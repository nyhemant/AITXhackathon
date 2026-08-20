#!/usr/bin/env python3
"""Cheap card-kind lint — does not replace lint_item_uniqueness.py.

Report-only by default. Exit 1 only with --strict.

Checks:
  - kind=attraction cards missing catalog venue_attribution {venue_slug, venue_name}
  - write_cards_hub still hand-assigns Wildlife/Parks lists (or special-cases Towpath)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from field_pack_card_kind import (  # noqa: E402
    card_kind,
    catalog_has_venue_attribution,
)

CATALOG_JS = ROOT / "static" / "field-pack" / "js" / "catalog.js"
GENERATOR = ROOT / "scripts" / "generate_bdo_seo.py"


def _load_catalog_cards() -> list[dict]:
    script = r"""
const fs = require('fs');
const vm = require('vm');
const ctx = { window: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
const cat = ctx.window.FIELD_PACK_CATALOG || {};
const out = [];
for (const [id, it] of Object.entries(cat)) {
  if (!it || !it.name) continue;
  out.push({
    id,
    name: it.name,
    kind: it.kind || '',
    packTemplate: it.packTemplate || '',
    photoCredit: String(it.photoCredit || ''),
    status: String(it.status || ''),
    venue_attribution: it.venue_attribution && typeof it.venue_attribution === 'object'
      ? it.venue_attribution
      : null,
  });
}
process.stdout.write(JSON.stringify(out));
"""
    raw = subprocess.check_output(["node", "-e", script, str(CATALOG_JS)], text=True)
    return json.loads(raw)


def _write_cards_hub_source() -> str:
    src = GENERATOR.read_text(encoding="utf-8")
    start = src.find("def write_cards_hub(")
    if start < 0:
        return ""
    nxt = src.find("\ndef ", start + 1)
    return src[start:nxt] if nxt > 0 else src[start:]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true", help="Exit 1 when issues are found")
    args = ap.parse_args()

    issues: list[str] = []
    notes: list[str] = []

    cards = _load_catalog_cards()
    missing_attr = [
        c["id"]
        for c in cards
        if card_kind(c) == "attraction" and not catalog_has_venue_attribution(c)
    ]
    if missing_attr:
        preview = ", ".join(f"`{i}`" for i in missing_attr[:12])
        extra = f" (+{len(missing_attr) - 12} more)" if len(missing_attr) > 12 else ""
        issues.append(
            f"attraction missing venue_attribution ({len(missing_attr)}): {preview}{extra}"
        )

    hub_src = _write_cards_hub_source()
    if not hub_src:
        issues.append("generate_bdo_seo.py write_cards_hub not found")
    else:
        if "_split_creature_cards" in hub_src:
            issues.append("write_cards_hub hand-assigns Wildlife/Sea life via _split_creature_cards")
        if "cuyahoga-towpath" in hub_src:
            issues.append("write_cards_hub special-cases cuyahoga-towpath (use kind=place_feature)")
        if "group_cards_by_hub_section" not in hub_src and "card_kind" not in hub_src and "_card_group_key" not in hub_src:
            issues.append("write_cards_hub does not derive sections from kind")

    print("Card-kind lint (report-only unless --strict)")
    print(f"  catalog cards scanned: {len(cards)}")
    if issues:
        print(f"  issues: {len(issues)}")
        for line in issues:
            print(f"  - {line}")
    else:
        print("  issues: 0")
    for line in notes:
        print(f"  note: {line}")

    if args.strict and issues:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
