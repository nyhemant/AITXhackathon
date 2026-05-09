"""Inventory Confidence Engine for local demo planning.

The engine reconciles visible snapshots with mock order history and simple
household consumption heuristics. It intentionally stays deterministic.
"""

from __future__ import annotations

from datetime import date, datetime
import json
from pathlib import Path
from typing import Any, Callable

from busyparent_agent.adapters import costco_bulk
from busyparent_agent.adapters import mock_instacart
from busyparent_agent.adapters import mock_photo_scan


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
TraceFn = Callable[[str, dict[str, Any]], None] | None

KID_SNACK_ITEMS = {"berries", "blueberries", "carrots", "bananas", "mini cucumbers"}
FRESH_ITEMS = {
    "avocado",
    "berries",
    "blueberries",
    "carrots",
    "bagged salad",
    "salad kit",
    "plain yogurt",
    "eggs",
    "milk",
    "mini cucumbers",
    "bananas",
}
ITEM_ALIASES = {
    "eggs": "eggs",
    "egg": "eggs",
    "berry": "berries",
    "berries": "berries",
    "mini cucumber": "mini cucumbers",
    "mini cucumbers": "mini cucumbers",
}


def _read_json(filename: str) -> Any:
    with (DATA_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


def _trace(trace: TraceFn, name: str, payload: dict[str, Any]) -> None:
    if trace:
        trace(name, payload)


def build_confidence_inventory(now: datetime, trace: TraceFn = None) -> dict[str, Any]:
    fridge_snapshot = _read_json("fridge_snapshot.json")
    pantry_snapshot = _read_json("pantry_snapshot.json")
    costco_cadence = costco_bulk.get_cadence(trace)
    costco_receipts = costco_bulk.get_recent_receipts(now, trace)
    orders = mock_instacart.get_recent_orders(trace)
    mock_instacart.get_last_delivery(trace)
    frequently_bought = mock_instacart.get_frequently_bought_items(trace)

    evidence: dict[str, list[str]] = {}
    ordered_items: dict[str, dict[str, Any]] = {}
    costco_items: dict[str, dict[str, Any]] = {}
    photo_items: dict[str, dict[str, Any]] = {}
    photo_unknowns: list[dict[str, Any]] = []

    fridge_items = [_canonical(item) for item in fridge_snapshot.get("items", [])]
    pantry_items = [_canonical(item) for item in pantry_snapshot.get("pantry", [])]
    freezer_items = [_canonical(item) for item in pantry_snapshot.get("freezer", [])]

    for item in fridge_items:
        evidence.setdefault(item, []).append("seen in fridge snapshot")
    for item in pantry_items:
        evidence.setdefault(item, []).append("seen in pantry snapshot")
    for item in freezer_items:
        evidence.setdefault(item, []).append("seen in freezer snapshot")

    photo_scan_summary = _load_photo_scan_evidence(now, evidence, photo_items, photo_unknowns, trace)

    for order in orders:
        delivered_at = datetime.strptime(order["delivered_at"], "%Y-%m-%d %H:%M")
        for raw_item in order["items"]:
            item = _canonical(raw_item["name"])
            days = _days_ago(delivered_at.date(), now)
            prior = ordered_items.get(item)
            if prior is None or days < prior["days_ago"]:
                ordered_items[item] = {**raw_item, "name": item, "days_ago": days}
            if days <= 3:
                evidence.setdefault(item, []).append("bought recently")

    for receipt in costco_receipts:
        purchased_at = date.fromisoformat(receipt["purchased_at"])
        for raw_item in receipt["items"]:
            item = _canonical(raw_item["item"])
            days = _days_ago(purchased_at, now)
            prior = costco_items.get(item)
            if prior is None or days < prior["days_ago"]:
                costco_items[item] = {
                    **raw_item,
                    "item": item,
                    "days_ago": days,
                    "purchased_at": receipt["purchased_at"],
                    "source_type": receipt.get("source_type", "mock_fixture"),
                }
            evidence.setdefault(item, []).append("Costco bulk item")

    for item in frequently_bought:
        canonical = _canonical(item)
        evidence.setdefault(canonical, []).append("frequently bought")

    confidence: dict[str, dict[str, Any]] = {}
    all_items = sorted(set(evidence) | set(ordered_items) | set(costco_items) | set(photo_items))
    for item in all_items:
        entry = _classify_item(
            item,
            evidence.get(item, []),
            ordered_items.get(item),
            costco_items.get(item),
            photo_items.get(item),
        )
        confidence[item] = entry
        _trace(
            trace,
            "inventory_confidence",
            {
                "item": item,
                "bucket": entry["bucket"],
                "reason": entry["reason"],
            },
        )

    groups = {
        "high_confidence": _items_in_bucket(confidence, "high_confidence"),
        "medium_confidence": _items_in_bucket(confidence, "medium_confidence"),
        "low_confidence": _items_in_bucket(confidence, "low_confidence"),
        "likely_low": _items_in_bucket(confidence, "likely_low"),
        "needs_parent_check": _items_in_bucket(confidence, "needs_parent_check"),
    }

    return {
        "captured_at": fridge_snapshot["captured_at"],
        "fridge": fridge_items,
        "pantry": pantry_items,
        "freezer": freezer_items,
        "costco_cadence": {
            **costco_cadence,
            "days_until_next_run": costco_bulk.days_until_next_run(now, costco_cadence),
        },
        "confidence": confidence,
        "photo_scans": photo_scan_summary,
        "photo_unknowns": photo_unknowns,
        **groups,
        "needs_photo_hint": bool(groups["low_confidence"] or groups["needs_parent_check"]),
    }


def available_items(inventory: dict[str, Any], include_medium: bool = True) -> set[str]:
    items = set(inventory.get("high_confidence", []))
    if include_medium:
        items.update(inventory.get("medium_confidence", []))
    return items


def confidence_for_item(inventory: dict[str, Any], item: str) -> dict[str, Any]:
    canonical = _canonical(item)
    return inventory.get("confidence", {}).get(
        canonical,
        {"bucket": "needs_parent_check", "reason": "not visible or recently ordered"},
    )


def _classify_item(
    item: str,
    evidence: list[str],
    order_item: dict[str, Any] | None,
    costco_item: dict[str, Any] | None,
    photo_item: dict[str, Any] | None,
) -> dict[str, Any]:
    visible = any(reason.startswith("seen in") or reason.startswith("visible ") for reason in evidence)
    bought_recently = "bought recently" in evidence
    days_ago = order_item["days_ago"] if order_item else None
    kid_snack = bool(order_item and order_item.get("kid_snack")) or item in KID_SNACK_ITEMS

    if visible:
        if costco_item and costco_item["storage_type"] in {"shelf_stable", "freezer"}:
            return {"bucket": "high_confidence", "reason": _costco_reason(costco_item)}
        supporting = [reason for reason in evidence if reason != "frequently bought" and reason != "Costco bulk item"]
        if costco_item:
            supporting.append(_costco_reason(costco_item))
        reason = " + ".join(supporting)
        return {"bucket": "high_confidence", "reason": reason}

    if costco_item:
        return _classify_costco_item(costco_item)

    if photo_item:
        return _classify_photo_item(photo_item)

    if days_ago is not None:
        if kid_snack and days_ago >= 5:
            return {"bucket": "likely_low", "reason": f"bought {days_ago} days ago, kid snack item"}
        if item in FRESH_ITEMS and days_ago <= 3:
            return {"bucket": "medium_confidence", "reason": f"ordered {days_ago} days ago, not visible"}
        if item in FRESH_ITEMS and days_ago <= 5:
            return {"bucket": "low_confidence", "reason": f"ordered {days_ago} days ago, not visible"}
        if days_ago <= 10:
            return {"bucket": "low_confidence", "reason": f"ordered {days_ago} days ago, not visible"}

    return {"bucket": "needs_parent_check", "reason": "not visible or recently ordered"}


def _load_photo_scan_evidence(
    now: datetime,
    evidence: dict[str, list[str]],
    photo_items: dict[str, dict[str, Any]],
    photo_unknowns: list[dict[str, Any]],
    trace: TraceFn,
) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for source_type in ("fridge_photo", "pantry_photo", "grocery_haul_photo", "receipt_photo"):
        scan = mock_photo_scan.get_latest_scan(source_type, trace)
        if not scan:
            continue

        summaries.append(
            {
                "scan_id": scan["scan_id"],
                "source_type": source_type,
                "captured_at": scan["captured_at"],
                "items": len(scan.get("items", [])),
                "unknowns": len(scan.get("unknowns", [])),
            }
        )

        if source_type == "receipt_photo":
            _trace(
                trace,
                "vision_receipt",
                {"source_type": source_type, "items": len(scan.get("items", []))},
            )

        for raw_item in scan.get("items", []):
            item = _canonical(raw_item["name"])
            photo_item = {
                **raw_item,
                "name": item,
                "source_type": source_type,
                "scan_id": scan["scan_id"],
                "days_ago": _scan_days_ago(scan, now),
            }
            prior = photo_items.get(item)
            if prior is None or _photo_item_priority(photo_item) > _photo_item_priority(prior):
                photo_items[item] = photo_item

            if source_type in {"fridge_photo", "pantry_photo"}:
                evidence.setdefault(item, []).append(raw_item["evidence"])

            _trace_photo_item(trace, photo_item)

        for unknown in scan.get("unknowns", []):
            saved_unknown = {
                **unknown,
                "source_type": source_type,
                "scan_id": scan["scan_id"],
            }
            photo_unknowns.append(saved_unknown)
            _trace(
                trace,
                "vision_unknown",
                {
                    "description": unknown["description"],
                    "reason": unknown["reason"],
                    "storage": unknown.get("storage", "unknown"),
                },
            )

    return summaries


def _trace_photo_item(trace: TraceFn, item: dict[str, Any]) -> None:
    source_type = item["source_type"]
    confidence = float(item.get("confidence", 0))
    if source_type in {"fridge_photo", "pantry_photo"}:
        bucket = "high_confidence" if confidence >= 0.8 else "medium_confidence"
        reason = item["evidence"]
    elif source_type in {"grocery_haul_photo", "receipt_photo"}:
        classified = _classify_photo_item(item)
        bucket = classified["bucket"]
        reason = classified["reason"]
    else:
        bucket = "needs_parent_check"
        reason = "unsupported mock photo source"

    _trace(
        trace,
        "vision_item",
        {
            "item": item["name"],
            "bucket": bucket,
            "reason": reason,
        },
    )


def _classify_photo_item(item: dict[str, Any]) -> dict[str, Any]:
    source_type = item["source_type"]
    storage_type = _photo_storage_type(item)
    days_ago = item.get("days_ago")
    confidence = float(item.get("confidence", 0))

    if source_type in {"fridge_photo", "pantry_photo"}:
        bucket = "high_confidence" if confidence >= 0.8 else "medium_confidence"
        return {"bucket": bucket, "reason": item["evidence"]}

    if days_ago is None:
        return {"bucket": "needs_parent_check", "reason": "mock photo has no capture date"}

    reason = _photo_acquisition_reason(item, storage_type)
    shelf_life_days = int(item.get("shelf_life_days", 7 if storage_type == "fresh" else 30))

    if storage_type == "shelf_stable":
        return {"bucket": "high_confidence" if days_ago <= 30 else "medium_confidence", "reason": reason}
    if storage_type == "freezer":
        return {"bucket": "high_confidence" if days_ago <= 14 else "medium_confidence", "reason": reason}
    if storage_type == "fresh":
        if days_ago <= 3:
            return {"bucket": "medium_confidence", "reason": reason}
        if days_ago <= shelf_life_days:
            return {"bucket": "low_confidence", "reason": reason}
        return {"bucket": "likely_low", "reason": reason}

    return {"bucket": "low_confidence", "reason": reason}


def _photo_acquisition_reason(item: dict[str, Any], storage_type: str) -> str:
    days_ago = item["days_ago"]
    if item["source_type"] == "grocery_haul_photo":
        if storage_type == "fresh":
            return f"{item['evidence']}, fresh item, bought {days_ago} days ago"
        return f"{item['evidence']}, bought {days_ago} days ago"
    if item["source_type"] == "receipt_photo":
        return f"{item['evidence']}, {storage_type.replace('_', '-')}, bought {days_ago} days ago"
    return item["evidence"]


def _photo_storage_type(item: dict[str, Any]) -> str:
    storage = item.get("storage", "").lower()
    category = item.get("category", "").lower()
    if storage == "freezer" or category == "frozen":
        return "freezer"
    if storage in {"pantry", "shelf"} or category in {"grain", "canned_goods", "household"}:
        return "shelf_stable"
    if category == "produce" or storage in {"fridge", "counter"}:
        return "fresh"
    return storage or "unknown"


def _scan_days_ago(scan: dict[str, Any], now: datetime) -> int | None:
    captured_at = scan.get("captured_at")
    if not captured_at:
        return None
    return _days_ago(datetime.fromisoformat(captured_at).date(), now)


def _photo_item_priority(item: dict[str, Any]) -> tuple[int, float]:
    source_priority = {
        "fridge_photo": 4,
        "pantry_photo": 4,
        "grocery_haul_photo": 3,
        "receipt_photo": 2,
    }.get(item["source_type"], 1)
    return (source_priority, float(item.get("confidence", 0)))


def _classify_costco_item(item: dict[str, Any]) -> dict[str, Any]:
    storage_type = item["storage_type"]
    days_ago = item["days_ago"]

    if storage_type == "shelf_stable":
        if days_ago <= 45:
            return {"bucket": "high_confidence", "reason": _costco_reason(item)}
        if days_ago <= int(item["shelf_life_days"]):
            return {"bucket": "medium_confidence", "reason": _costco_reason(item)}

    if storage_type == "freezer":
        if days_ago <= 21:
            return {"bucket": "high_confidence", "reason": _costco_reason(item)}
        if days_ago <= int(item["shelf_life_days"]):
            return {"bucket": "medium_confidence", "reason": _costco_reason(item)}

    if storage_type == "fresh":
        if days_ago <= 3:
            return {"bucket": "medium_confidence", "reason": _costco_reason(item)}
        return {"bucket": "low_confidence", "reason": _costco_reason(item)}

    return {"bucket": "needs_parent_check", "reason": _costco_reason(item)}


def _costco_reason(item: dict[str, Any]) -> str:
    label = {
        "shelf_stable": "shelf-stable",
        "freezer": "freezer",
        "fresh": "fresh Costco item",
    }.get(item["storage_type"], item["storage_type"])
    if item["storage_type"] == "fresh":
        return f"{label}, bought {item['days_ago']} days ago"
    return f"Costco bulk item, {label}, bought {item['days_ago']} days ago"


def _items_in_bucket(confidence: dict[str, dict[str, Any]], bucket: str) -> list[str]:
    return sorted(item for item, entry in confidence.items() if entry["bucket"] == bucket)


def _canonical(item: str) -> str:
    return ITEM_ALIASES.get(item.lower(), item.lower())


def _days_ago(value: date, now: datetime) -> int:
    return max((now.date() - value).days, 0)
