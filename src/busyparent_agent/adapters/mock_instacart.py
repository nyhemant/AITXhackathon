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


def build_reviewable_cart(items: list[str], trace: TraceFn = None) -> dict[str, Any]:
    catalog = _read_catalog()
    line_items = []
    unavailable_items = []
    substitutions = []

    for requested in _unique(items):
        item = _find_catalog_item(requested, catalog)
        if item and item["in_stock"]:
            line_items.append(_cart_line(requested, item))
            continue

        substitute = _find_substitute(item, catalog) if item else None
        if substitute:
            line_items.append(_cart_line(requested, substitute))
            substitutions.append({"requested": requested, "substitute": substitute["name"]})
        else:
            unavailable_items.append(requested)

    subtotal = round(sum(line["price"] for line in line_items), 2)
    cart = {
        "items": [line["name"] for line in line_items],
        "line_items": line_items,
        "unavailable_items": unavailable_items,
        "substitutions": substitutions,
        "subtotal": subtotal,
        "note": "Review before buying. This mock adapter never places orders.",
    }
    _trace(
        trace,
        "mock_instacart.build_reviewable_cart",
        {"items": cart["items"], "subtotal": subtotal, "unavailable": unavailable_items},
    )
    return cart


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


def _cart_line(requested: str, item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item["id"],
        "requested": requested,
        "name": item["name"],
        "brand": item["brand"],
        "size": item["size"],
        "price": item["price"],
    }


def _unique(items: list[str]) -> list[str]:
    unique_items = []
    for item in items:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items


def _normalize(value: str) -> str:
    return value.strip().lower().replace("-", " ")
