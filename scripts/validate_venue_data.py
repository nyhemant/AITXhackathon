#!/usr/bin/env python3
"""Validate pilot venue mission data. Exit 1 on failure."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENUE_DIR = REPO / "static" / "field-pack" / "data" / "venues"
CHALLENGES = REPO / "static" / "field-pack" / "data" / "challenges.json"
PLACES = REPO / "static" / "field-pack" / "js" / "places-data.js"

REQUIRED_ITEM = ("id", "label", "emoji", "one_liner", "tags", "age_fit")
VALID_STATUS = {"verified", "unverified", "needs_review"}
AGES = {"2-3", "4-5", "6-8", "9+"}


def cities_from_places() -> set[str]:
    text = PLACES.read_text(encoding="utf-8")
    cities = set(re.findall(r'city:\s*"([^"]+)"', text))
    # common extras
    cities.update({"Dallas", "Tokyo", "London", "Houston", "Chicago", "Paris", "Berlin"})
    return {c for c in cities if c}


def validate_venue(path: Path, all_cities: set[str]) -> list[str]:
    errs = []
    data = json.loads(path.read_text(encoding="utf-8"))
    slug = data.get("slug") or path.stem
    for key in ("slug", "name", "type", "city", "country", "last_verified", "status", "items"):
        if key not in data or data[key] in (None, ""):
            errs.append(f"{slug}: missing {key}")
    if data.get("status") not in VALID_STATUS:
        errs.append(f"{slug}: bad status {data.get('status')}")
    items = data.get("items") or []
    if data.get("status") == "verified" and len(items) < 8:
        errs.append(f"{slug}: verified venues need ≥8 items (has {len(items)})")
    ids = set()
    own_city = (data.get("city") or "").lower()
    own_name = (data.get("name") or "").lower()
    for it in items:
        for k in REQUIRED_ITEM:
            if k not in it or it[k] in (None, "", []):
                errs.append(f"{slug}: item {it.get('id')} missing {k}")
        iid = it.get("id")
        if iid in ids:
            errs.append(f"{slug}: duplicate item id {iid}")
        ids.add(iid)
        for band in it.get("age_fit") or []:
            if band not in AGES:
                errs.append(f"{slug}: bad age_fit {band} on {iid}")
        blob = " ".join(
            [
                str(it.get("one_liner") or ""),
                str((it.get("qa_card") or {}).get("question") or ""),
                str((it.get("qa_card") or {}).get("answer") or ""),
            ]
        )
        for city in all_cities:
            if city.lower() == own_city:
                continue
            if len(city) < 4:
                continue
            if re.search(rf"\b{re.escape(city)}\b", blob, re.I):
                # allow if city appears inside own venue name somehow
                if city.lower() not in own_name:
                    errs.append(f"{slug}: item {iid} leaks city '{city}' in text")
        # foreign venue name fragments
        for other in ("Dallas Zoo", "Ueno Zoo", "London Zoo", "feeding platform"):
            if other.lower() in blob.lower() and other.lower() not in own_name:
                if other == "feeding platform" and slug == "dallas-zoo":
                    continue
                if "feeding platform" in other and slug != "dallas-zoo" and "feeding platform" in blob.lower():
                    if slug != "dallas-zoo":
                        errs.append(f"{slug}: item {iid} may leak venue-specific phrase '{other}'")
    return errs


def main() -> int:
    if not VENUE_DIR.is_dir():
        print("No venues dir")
        return 1
    all_cities = cities_from_places()
    errs: list[str] = []
    if not CHALLENGES.is_file():
        errs.append("missing challenges.json")
    else:
        ch = json.loads(CHALLENGES.read_text())
        if len(ch.get("challenges") or []) < 8:
            errs.append("challenges.json too small")
    for path in sorted(VENUE_DIR.glob("*.json")):
        errs.extend(validate_venue(path, all_cities))
    if errs:
        print("VALIDATION FAILED:")
        for e in errs:
            print(" -", e)
        return 1
    print(f"OK: {len(list(VENUE_DIR.glob('*.json')))} venues validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
