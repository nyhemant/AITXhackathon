#!/usr/bin/env python3
"""Every venue page must be reachable within 2 static clicks from /field-pack/.

Click 0: landing
Click 1: type hub (/zoos/, /aquariums/, …) or popular chip / direct landing link
Click 2: venue page

Also accepts venue links present directly on landing (popular chips).
Exit 0 if all reachable; 1 otherwise. Writes docs/venue-reachability-report.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "static" / "field-pack"
OUT = ROOT / "docs" / "venue-reachability-report.md"

HUBS = [
    "zoos/index.html",
    "aquariums/index.html",
    "museums/index.html",
    "national-parks/index.html",
]


def venue_ids() -> set[str]:
    return {p.stem for p in (FIELD / "data" / "venues").glob("*.json")}


def links_in(html: str) -> set[str]:
    found = set()
    for m in re.finditer(r'href="(/field-pack/([^"#?]+)/?)"', html):
        slug = m.group(2).strip("/")
        if not slug or "/" in slug:
            # nested path — take first segment if venue-like
            first = slug.split("/")[0]
            found.add(first)
        else:
            found.add(slug)
    return found


def main() -> int:
    ids = venue_ids()
    landing = (FIELD / "index.html").read_text(encoding="utf-8", errors="ignore")
    click1 = links_in(landing)
    # hubs
    hub_links: set[str] = set()
    for h in HUBS:
        p = FIELD / h
        if p.is_file():
            hub_links |= links_in(p.read_text(encoding="utf-8", errors="ignore"))

    reachable = set()
    via = {}
    for vid in ids:
        if vid in click1:
            reachable.add(vid)
            via[vid] = "landing (≤1 click)"
        elif vid in hub_links:
            reachable.add(vid)
            via[vid] = "type hub (2 clicks)"
    missing = sorted(ids - reachable)

    lines = [
        "# Venue reachability report\n\n",
        f"Venues: **{len(ids)}** · reachable ≤2 clicks: **{len(reachable)}** · missing: **{len(missing)}**\n\n",
    ]
    if missing:
        lines.append("## Missing\n")
        for m in missing:
            lines.append(f"- `{m}`\n")
    else:
        lines.append("All venues reachable within two static clicks of `/field-pack/`.\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(lines), encoding="utf-8")
    print("".join(lines))
    print("Wrote", OUT)
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
