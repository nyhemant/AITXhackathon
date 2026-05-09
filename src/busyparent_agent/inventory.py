"""Inventory Confidence Engine for local demo planning.

The engine reconciles visible snapshots with mock order history and simple
household consumption heuristics. It intentionally stays deterministic.
"""

from __future__ import annotations

from datetime import date, datetime
import json
from pathlib import Path
from typing import Any, Callable

from busyparent_agent.adapters import mock_instacart


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
TraceFn = Callable[[str, dict[str, Any]], None] | None

KID_SNACK_ITEMS = {"berries", "carrots"}
FRESH_ITEMS = {"avocado", "berries", "carrots", "bagged salad", "plain yogurt", "eggs", "milk"}
ITEM_ALIASES = {
    "eggs": "eggs",
    "egg": "eggs",
    "berry": "berries",
    "berries": "berries",
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
    bulk_purchases = _read_json("costco_bulk_purchases.json")
    orders = mock_instacart.get_recent_orders(trace)
    mock_instacart.get_last_delivery(trace)
    frequently_bought = mock_instacart.get_frequently_bought_items(trace)

    evidence: dict[str, list[str]] = {}
    ordered_items: dict[str, dict[str, Any]] = {}

    fridge_items = [_canonical(item) for item in fridge_snapshot.get("items", [])]
    pantry_items = [_canonical(item) for item in pantry_snapshot.get("pantry", [])]
    freezer_items = [_canonical(item) for item in pantry_snapshot.get("freezer", [])]

    for item in fridge_items:
        evidence.setdefault(item, []).append("seen in fridge snapshot")
    for item in pantry_items:
        evidence.setdefault(item, []).append("seen in pantry snapshot")
    for item in freezer_items:
        evidence.setdefault(item, []).append("seen in freezer snapshot")

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

    for purchase in bulk_purchases:
        item = _canonical(purchase["item"])
        days = _days_ago(date.fromisoformat(purchase["purchased_at"]), now)
        if days <= int(purchase["shelf_life_days"]):
            evidence.setdefault(item, []).append("bulk purchase likely on hand")

    for item in frequently_bought:
        canonical = _canonical(item)
        evidence.setdefault(canonical, []).append("frequently bought")

    confidence: dict[str, dict[str, Any]] = {}
    all_items = sorted(set(evidence) | set(ordered_items))
    for item in all_items:
        entry = _classify_item(item, evidence.get(item, []), ordered_items.get(item))
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
        "confidence": confidence,
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


def _classify_item(item: str, evidence: list[str], order_item: dict[str, Any] | None) -> dict[str, Any]:
    visible = any(reason.startswith("seen in") for reason in evidence)
    bought_recently = "bought recently" in evidence
    bulk = "bulk purchase likely on hand" in evidence
    days_ago = order_item["days_ago"] if order_item else None
    kid_snack = bool(order_item and order_item.get("kid_snack")) or item in KID_SNACK_ITEMS

    if visible:
        supporting = [reason for reason in evidence if reason != "frequently bought"]
        reason = " + ".join(supporting)
        return {"bucket": "high_confidence", "reason": reason}

    if bulk:
        return {"bucket": "high_confidence", "reason": "bulk purchase likely on hand"}

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


def _items_in_bucket(confidence: dict[str, dict[str, Any]], bucket: str) -> list[str]:
    return sorted(item for item, entry in confidence.items() if entry["bucket"] == bucket)


def _canonical(item: str) -> str:
    return ITEM_ALIASES.get(item.lower(), item.lower())


def _days_ago(value: date, now: datetime) -> int:
    return max((now.date() - value).days, 0)
