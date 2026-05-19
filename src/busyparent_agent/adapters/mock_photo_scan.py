"""Deterministic photo scan adapter for local 1Less validation.

This module never reads image pixels and never calls a camera, OCR, or vision
API. It returns local fixture outputs that model what a future adapter could
produce from fridge, pantry, haul, or receipt images.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
TraceFn = Callable[[str, dict[str, Any]], None] | None


def _read_scan_results() -> dict[str, Any]:
    with (DATA_DIR / "photo_scan_results.json").open(encoding="utf-8") as file:
        return json.load(file)


def _trace(trace: TraceFn, name: str, payload: dict[str, Any]) -> None:
    if trace:
        trace(name, payload)


def list_available_scans(trace: TraceFn = None) -> list[dict[str, Any]]:
    scans = deepcopy(_read_scan_results()["scans"])
    _trace(trace, "mock_photo_scan.list_available_scans", {"scans": len(scans)})
    return scans


def get_scan(scan_id: str, trace: TraceFn = None) -> dict[str, Any] | None:
    scan = next((scan for scan in _read_scan_results()["scans"] if scan["scan_id"] == scan_id), None)
    _trace(
        trace,
        "mock_photo_scan.get_scan",
        {"scan_id": scan_id, "found": scan is not None},
    )
    return deepcopy(scan) if scan else None


def get_latest_scan(source_type: str, trace: TraceFn = None) -> dict[str, Any] | None:
    scans = [scan for scan in _read_scan_results()["scans"] if scan["source_type"] == source_type]
    scans.sort(key=lambda scan: scan["captured_at"], reverse=True)
    scan = scans[0] if scans else None
    _trace(
        trace,
        "mock_photo_scan.get_latest_scan",
        {
            "source_type": source_type,
            "scan_id": scan["scan_id"] if scan else None,
        },
    )
    return deepcopy(scan) if scan else None


def scan_photo(image_path: str, source_type: str, trace: TraceFn = None) -> dict[str, Any]:
    """Return a deterministic fixture scan for a requested image/source pair."""

    scans = _read_scan_results()["scans"]
    scan = next(
        (
            scan
            for scan in scans
            if scan["source_type"] == source_type and scan["image_path"] == image_path
        ),
        None,
    )
    if scan is None:
        scan = next((scan for scan in scans if scan["source_type"] == source_type), None)
    if scan is None:
        scan = _empty_scan(image_path, source_type)

    _trace(
        trace,
        "mock_photo_scan.scan_photo",
        {
            "source_type": source_type,
            "scan_id": scan["scan_id"],
            "items": len(scan.get("items", [])),
            "unknowns": len(scan.get("unknowns", [])),
        },
    )
    return deepcopy(scan)


def _empty_scan(image_path: str, source_type: str) -> dict[str, Any]:
    return {
        "scan_id": f"empty-{source_type}",
        "source_type": source_type,
        "image_path": image_path,
        "captured_at": None,
        "items": [],
        "unknowns": [
            {
                "description": "unrecognized photo",
                "storage": "unknown",
                "reason": "no matching mock fixture",
            }
        ],
        "notes": [
            "No real camera, OCR, or vision API was used.",
        ],
    }
