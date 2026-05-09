"""Mock Instacart-like adapter backed by local JSON fixtures.

No network calls, credentials, scraping, or real purchasing happen here.
"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Callable


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
TraceFn = Callable[[str, dict[str, Any]], None] | None
ORDER_RULES = {
    "minimum_order_amount": 35.00,
    "small_order_fee_threshold": 35.00,
    "cart_target_amount": 40.00,
}
SMART_ADDON_CANDIDATES = [
    ("rice", "Costco bulk staple check"),
    ("eggs", "visible fridge staple check"),
    ("mini cucumbers", "recurring kid side + low confidence"),
    ("bananas", "kid snack staple + low waste"),
    ("salad kit", "useful for next dinner side"),
    ("applesauce pouches", "lunchbox backup + low waste"),
    ("granola bars", "kid snack staple + low waste"),
    ("crackers", "kid side + pantry snack"),
    ("strawberries", "kid snack fruit + flexible side"),
]
MAX_SMART_FRESH_ITEMS = 3


def _read_orders() -> list[dict[str, Any]]:
    with (DATA_DIR / "instacart_orders.json").open(encoding="utf-8") as file:
        return json.load(file)


def _read_catalog() -> list[dict[str, Any]]:
    with (DATA_DIR / "mock_grocery_catalog.json").open(encoding="utf-8") as file:
        return json.load(file)


def _trace(trace: TraceFn, name: str, payload: dict[str, Any]) -> None:
    if trace:
        trace(name, payload)


def get_recent_orders(trace: TraceFn = None) -> list[dict[str, Any]]:
    orders = _read_orders()
    _trace(trace, "mock_instacart.get_recent_orders", {"orders": len(orders)})
    return orders


def get_last_delivery(trace: TraceFn = None) -> dict[str, Any] | None:
    orders = sorted(_read_orders(), key=lambda order: order["delivered_at"], reverse=True)
    last_delivery = orders[0] if orders else None
    _trace(
        trace,
        "mock_instacart.get_last_delivery",
        {"delivered_at": last_delivery["delivered_at"] if last_delivery else None},
    )
    return last_delivery


def get_frequently_bought_items(trace: TraceFn = None) -> list[str]:
    counts: dict[str, int] = {}
    for order in _read_orders():
        for item in order["items"]:
            name = item["name"]
            counts[name] = counts.get(name, 0) + 1
    items = [name for name, count in sorted(counts.items()) if count >= 1]
    _trace(trace, "mock_instacart.get_frequently_bought_items", {"items": len(items)})
    return items


def get_catalog_items(trace: TraceFn = None) -> list[dict[str, Any]]:
    catalog = _read_catalog()
    _trace(trace, "mock_instacart.get_catalog_items", {"items": len(catalog)})
    return catalog


def search_catalog(query: str, trace: TraceFn = None) -> list[dict[str, Any]]:
    normalized = _normalize(query)
    results = [
        item
        for item in _read_catalog()
        if normalized in _normalize(item["name"]) or normalized in {_normalize(tag) for tag in item.get("tags", [])}
    ]
    _trace(trace, "mock_instacart.search_catalog", {"query": query, "matches": len(results)})
    return results


def get_item(item_id: str, trace: TraceFn = None) -> dict[str, Any] | None:
    item = next((item for item in _read_catalog() if item["id"] == item_id), None)
    _trace(trace, "mock_instacart.get_item", {"item_id": item_id, "found": item is not None})
    return item


def check_availability(items: list[str], trace: TraceFn = None) -> dict[str, Any]:
    catalog = _read_catalog()
    available = []
    unavailable = []
    for requested in _unique(items):
        item = _find_catalog_item(requested, catalog)
        if item and item["in_stock"]:
            available.append(item)
        else:
            unavailable.append(requested)
    _trace(trace, "mock_instacart.check_availability", {"available": len(available), "unavailable": len(unavailable)})
    return {"available": available, "unavailable": unavailable}


def catalog_item_available(name: str) -> bool:
    item = _find_catalog_item(name, _read_catalog())
    if item and item["in_stock"]:
        return True
    return _find_substitute(item, _read_catalog()) is not None


def check_delivery_window(now: datetime, trace: TraceFn = None) -> dict[str, Any]:
    minutes = now.hour * 60 + now.minute
    can_deliver = minutes < 16 * 60 + 30
    result = {
        "can_deliver": can_deliver,
        "estimated_minutes": 90 if can_deliver else None,
        "message": "Mock delivery window available." if can_deliver else "Mock delivery window closed for tonight.",
    }
    _trace(trace, "mock_instacart.check_delivery_window", result)
    return result


def get_order_rules(trace: TraceFn = None) -> dict[str, float]:
    _trace(trace, "mock_instacart.get_order_rules", ORDER_RULES)
    return dict(ORDER_RULES)


def build_reviewable_cart(
    items: list[str],
    trace: TraceFn = None,
    inventory: dict[str, Any] | None = None,
    meal_options: list[dict[str, Any]] | None = None,
    current_meal: dict[str, Any] | None = None,
) -> dict[str, Any]:
    catalog = _read_catalog()
    required_line_items = []
    unavailable_items = []
    substitutions = []

    for requested in _unique(items):
        item = _find_catalog_item(requested, catalog)
        if item and item["in_stock"]:
            required_line_items.append(_cart_line(requested, item, "required_for_tonight"))
            continue

        substitute = _find_substitute(item, catalog) if item else None
        if substitute:
            required_line_items.append(_cart_line(requested, substitute, "required_for_tonight"))
            substitutions.append({"requested": requested, "substitute": substitute["name"]})
        else:
            unavailable_items.append(requested)

    required_subtotal = _subtotal(required_line_items)
    _trace(trace, "cart_required_subtotal", {"subtotal": required_subtotal})

    smart_addons: list[dict[str, Any]] = []
    rules = get_order_rules()
    if required_line_items and required_subtotal < rules["minimum_order_amount"]:
        _trace(trace, "cart_below_minimum", {"minimum_order_amount": rules["minimum_order_amount"]})
        smart_addons = _build_smart_addons(
            catalog,
            required_line_items,
            inventory or {},
            trace,
            rules["cart_target_amount"],
            meal_options or [],
            current_meal or {},
        )

    line_items = required_line_items + smart_addons
    subtotal = _subtotal(line_items)
    status = "meets minimum" if subtotal >= rules["minimum_order_amount"] else "below minimum"
    cart = {
        "items": [line["name"] for line in line_items],
        "line_items": line_items,
        "required_items": required_line_items,
        "smart_addons": smart_addons,
        "unavailable_items": unavailable_items,
        "substitutions": substitutions,
        "subtotal": subtotal,
        "required_subtotal": required_subtotal,
        "minimum_order_amount": rules["minimum_order_amount"],
        "small_order_fee_threshold": rules["small_order_fee_threshold"],
        "cart_target_amount": rules["cart_target_amount"],
        "status": status,
        "note": "Review before buying. This mock adapter never places orders.",
    }
    _trace(trace, "cart_final_subtotal", {"subtotal": subtotal, "status": status})
    _trace(
        trace,
        "mock_instacart.build_reviewable_cart",
        {"items": cart["items"], "subtotal": subtotal, "unavailable": unavailable_items},
    )
    return cart


def _build_smart_addons(
    catalog: list[dict[str, Any]],
    required_line_items: list[dict[str, Any]],
    inventory: dict[str, Any],
    trace: TraceFn,
    target_amount: float,
    meal_options: list[dict[str, Any]],
    current_meal: dict[str, Any],
) -> list[dict[str, Any]]:
    selected = []
    selected_names = {line["name"] for line in required_line_items}
    future_names = _future_candidate_names(meal_options, current_meal)
    fresh_count = 0

    for candidate_name, default_reason in SMART_ADDON_CANDIDATES:
        item = _find_catalog_item(candidate_name, catalog)
        if not item or not item["in_stock"]:
            continue
        if item["name"] in selected_names:
            continue

        skip_reason = _skip_reason(item, inventory)
        if skip_reason:
            _trace(trace, "cart_skipped_item", {"item": item["name"], "reason": skip_reason})
            continue

        if "fresh" in item.get("tags", []) and fresh_count >= MAX_SMART_FRESH_ITEMS:
            _trace(trace, "cart_skipped_item", {"item": item["name"], "reason": "fresh add-on limit"})
            continue

        reason = _smart_reason(item["name"], default_reason, future_names)
        selected.append(_cart_line(item["name"], item, "smart_addon", reason))
        selected_names.add(item["name"])
        if "fresh" in item.get("tags", []):
            fresh_count += 1
        _trace(trace, "cart_added_smart_addon", {"item": item["name"], "reason": reason})

        if _subtotal(required_line_items + selected) >= target_amount:
            break

    return selected


def _future_candidate_names(meal_options: list[dict[str, Any]], current_meal: dict[str, Any]) -> set[str]:
    current_name = current_meal.get("name")
    names = set()
    for meal in [meal for meal in meal_options if meal.get("name") != current_name][:4]:
        names.update(item.lower() for item in meal.get("optional", []))
        names.update(item.lower() for item in meal.get("delivery_add_ons", []))
    return names


def _smart_reason(item_name: str, default_reason: str, future_names: set[str]) -> str:
    if item_name in future_names:
        return f"{default_reason} + useful for upcoming meals"
    return default_reason


def _skip_reason(item: dict[str, Any], inventory: dict[str, Any]) -> str | None:
    confidence = inventory.get("confidence", {}).get(item["name"])
    if confidence and confidence["bucket"] == "high_confidence":
        reason = confidence["reason"]
        if "Costco bulk item" in reason:
            return "Costco bulk item is high confidence"
        return "already high confidence at home"
    tags = set(item.get("tags", []))
    if "allergen_peanut" in tags:
        return "peanut allergen risk"
    if "spicy" in tags:
        return "spicy item"
    return None


def _find_catalog_item(name: str, catalog: list[dict[str, Any]]) -> dict[str, Any] | None:
    normalized = _normalize(name)
    return next((item for item in catalog if _normalize(item["name"]) == normalized), None)


def _find_substitute(item: dict[str, Any] | None, catalog: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not item:
        return None
    for substitute_name in item.get("substitutes", []):
        substitute = _find_catalog_item(substitute_name, catalog)
        if substitute and substitute["in_stock"]:
            return substitute
    return None


def _cart_line(
    requested: str,
    item: dict[str, Any],
    section: str,
    reason: str | None = None,
) -> dict[str, Any]:
    return {
        "id": item["id"],
        "requested": requested,
        "name": item["name"],
        "brand": item["brand"],
        "size": item["size"],
        "price": item["price"],
        "section": section,
        "reason": reason,
    }


def _subtotal(line_items: list[dict[str, Any]]) -> float:
    return round(sum(line["price"] for line in line_items), 2)


def _unique(items: list[str]) -> list[str]:
    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items


def _normalize(value: str) -> str:
    return value.strip().lower().replace("-", " ")
