"""Mock Costco bulk-restock adapter backed by local fixtures.

This is a demo-only read model. It does not log in to Costco, scrape receipts,
or access an account.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
import json
from pathlib import Path
from typing import Any, Callable


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
TraceFn = Callable[[str, dict[str, Any]], None] | None


def _read_fixture() -> dict[str, Any]:
    with (DATA_DIR / "costco_bulk_purchases.json").open(encoding="utf-8") as file:
        return json.load(file)


def _trace(trace: TraceFn, name: str, payload: dict[str, Any]) -> None:
    if trace:
        trace(name, payload)


def get_cadence(trace: TraceFn = None) -> dict[str, Any]:
    cadence = dict(_read_fixture()["cadence"])
    _trace(
        trace,
        "costco_bulk.get_cadence",
        {
            "frequency_days": cadence["frequency_days"],
            "usual_day": cadence["usual_day"],
            "usual_time": cadence["usual_time"],
        },
    )
    return cadence


def get_recent_receipts(now: datetime, trace: TraceFn = None) -> list[dict[str, Any]]:
    receipts = _read_fixture()["receipts"]
    last_run = _last_run_date(receipts)
    _trace(
        trace,
        "costco_bulk.get_recent_receipts",
        {
            "receipts": len(receipts),
            "last_run_days_ago": (now.date() - last_run).days if last_run else None,
        },
    )
    return receipts


def expected_next_run_date(cadence: dict[str, Any] | None = None) -> date:
    cadence = cadence or get_cadence()
    if cadence.get("expected_next_run_date"):
        return date.fromisoformat(cadence["expected_next_run_date"])
    last_run = date.fromisoformat(cadence["last_bulk_run_date"])
    return last_run + timedelta(days=int(cadence["frequency_days"]))


def days_until_next_run(now: datetime, cadence: dict[str, Any] | None = None) -> int:
    return (expected_next_run_date(cadence) - now.date()).days


def _last_run_date(receipts: list[dict[str, Any]]) -> date | None:
    if not receipts:
        return None
    return max(date.fromisoformat(receipt["purchased_at"]) for receipt in receipts)
