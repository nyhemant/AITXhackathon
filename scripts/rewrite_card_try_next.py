#!/usr/bin/env python3
"""Rewrite baked card Try-next grids from card-kinds.tsv hubs + neighbors.

ParentTest: sealife first paint must stay sealife (no african-lion / wildlife).
``generate_bdo_seo.py --cards-only`` already calls study_try_next_html(); this
script is the surgical path so a leftover grid can be fixed without a full
card regen, and ``--check`` fails CI if HTML drifts.

Usage:
  python3 scripts/rewrite_card_try_next.py --check
  python3 scripts/rewrite_card_try_next.py --write
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from field_pack_catalog_kind import load_card_kinds  # noqa: E402
from study_cards import (  # noqa: E402
    STUDY_CARDS,
    study_try_next_hub,
    study_try_next_html,
    study_try_next_ids,
)

FP = ROOT / "static" / "field-pack"
CARDS = FP / "cards"
TRY_NEXT_NAV = re.compile(
    r'<nav class="card-try-next no-print" aria-label="Try next">.*?</nav>',
    re.DOTALL,
)
BAKED_ID = re.compile(r"/cards/([^/]+)/")


def baked_try_next_ids(html: str) -> list[str]:
    match = TRY_NEXT_NAV.search(html)
    if not match:
        return []
    return BAKED_ID.findall(match.group(0))


def published_study_ids() -> list[str]:
    out: list[str] = []
    for cid in STUDY_CARDS:
        if (CARDS / cid / "index.html").is_file():
            out.append(cid)
    return out


def sealife_ids(kinds: dict | None = None) -> list[str]:
    table = kinds if kinds is not None else load_card_kinds()
    return [cid for cid in published_study_ids() if study_try_next_hub(cid, table) == "sealife"]


def wildlife_chip_ids(baked: list[str], kinds: dict) -> list[str]:
    return [cid for cid in baked if study_try_next_hub(cid, kinds) != "sealife"]


def check_grids() -> list[str]:
    """Return human-readable issues. Empty means HTML matches the generator."""
    kinds = load_card_kinds()
    issues: list[str] = []
    tsv_sea = [cid for cid, row in kinds.items() if row.get("hub") == "sealife"]
    missing_html = [cid for cid in tsv_sea if not (CARDS / cid / "index.html").is_file()]
    if missing_html:
        issues.append("TSV sealife missing HTML: " + ", ".join(missing_html))
    for cid in published_study_ids():
        path = CARDS / cid / "index.html"
        html = path.read_text(encoding="utf-8")
        want = study_try_next_ids(cid)
        baked = baked_try_next_ids(html)
        hub = study_try_next_hub(cid, kinds)
        if hub == "sealife":
            wild = wildlife_chip_ids(baked, kinds)
            if wild:
                issues.append(f"{cid}: wildlife chips {wild} in {baked}")
            if "african-lion" in baked:
                issues.append(f"{cid}: african-lion still baked")
        if baked != want:
            issues.append(f"{cid}: baked {baked} != generator {want}")
    return issues


def write_grids() -> tuple[int, int]:
    """Replace animal Try-next navs. Returns (rewritten, unchanged)."""
    rewritten = 0
    unchanged = 0
    for cid in published_study_ids():
        path = CARDS / cid / "index.html"
        html = path.read_text(encoding="utf-8")
        block = study_try_next_html(cid)
        if not block:
            continue
        if not TRY_NEXT_NAV.search(html):
            raise SystemExit(f"{cid}: missing Try next nav to rewrite")
        next_html, n = TRY_NEXT_NAV.subn(block, html, count=1)
        if n != 1:
            raise SystemExit(f"{cid}: expected one Try next nav, replaced {n}")
        if next_html == html:
            unchanged += 1
            continue
        path.write_text(next_html, encoding="utf-8")
        rewritten += 1
    return rewritten, unchanged


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Exit 1 if any grid drifts")
    mode.add_argument("--write", action="store_true", help="Rewrite baked grids from TSV hubs")
    args = ap.parse_args()

    kinds = load_card_kinds()
    sea = sealife_ids(kinds)
    print(f"Try-next rewrite ({'check' if args.check else 'write'})")
    print(f"  published study cards: {len(published_study_ids())}")
    print(f"  TSV sealife with HTML: {len(sea)}")

    if args.write:
        rewritten, unchanged = write_grids()
        print(f"  rewritten: {rewritten}")
        print(f"  unchanged: {unchanged}")

    issues = check_grids()
    if issues:
        print(f"  issues: {len(issues)}")
        for line in issues:
            print(f"  - {line}")
        return 1
    print("  issues: 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
