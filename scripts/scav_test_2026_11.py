#!/usr/bin/env python3
"""Printable scavenger-hunt block for the November 2026 test pages only.

Facts come from static/field-pack/data/venues/<slug>.json. Comparison pages
are not touched. Run ``python3 scripts/scav_test_2026_11.py`` to insert the
block into the committed test pages without rewriting any existing line.

A full ``generate_bdo_seo.py --only`` pass rebuilds the page and drops
hand-applied lines (link mesh, image alts, frozen JSON-LD). The generator
calls these helpers so a later regen still emits the block, and this script
is the post-step that keeps every current line.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "static" / "field-pack"
VENUES = FIELD / "data" / "venues"

TEST_SLUGS = frozenset({
    "amnh",
    "nashville-adventure-science",
    "air-and-space",
    "national-aquarium-baltimore",
    "shedd-aquarium",
    "lincoln-park-zoo",
    "toronto-zoo",
    "austin-zoo",
    "national-zoo",
    "bronx-zoo",
    "redwood",
    "joshua-tree",
})

COMPARISON_SLUGS = frozenset({
    "museum-of-science-industry-chi",
    "california-science-center",
    "discovery-place",
    "seattle-aquarium",
    "aquarium-of-the-pacific",
    "st-louis-zoo",
    "calgary-zoo",
    "fort-worth-zoo",
    "san-antonio-zoo",
    "dallas-zoo",
    "banff",
    "sequoia",
})

_ZOO_KINDS = frozenset({"zoo", "aquarium", "safari_zoo"})
_CSS_HREF = "/field-pack/css/scav-top-v1.css?v=1"
_JS_SRC = "/shell/qr-welcome.js?v=4"
E = lambda s: html.escape(str(s), quote=True)  # noqa: E731


def load_venue(slug: str) -> dict:
    return json.loads((VENUES / f"{slug}.json").read_text(encoding="utf-8"))


def _banned_catalog_ids(venue: dict) -> set[str]:
    banned = set()
    for row in venue.get("do_not_list") or []:
        cid = str(row.get("catalog_id") or "").strip()
        if cid:
            banned.add(cid)
    return banned


def hunt_items(venue: dict) -> list[dict]:
    banned = _banned_catalog_ids(venue)
    kept = []
    for item in venue.get("items") or []:
        cid = str(item.get("catalog_id") or "").strip()
        if cid and cid in banned:
            continue
        kept.append(item)
    return kept


def item_label(item: dict) -> str:
    label = str(item.get("display_label") or item.get("label") or "").strip()
    cid = str(item.get("catalog_id") or "")
    iid = str(item.get("id") or "")
    if iid == "cm_free_explore" or cid == "cm-free-explore":
        if label.lower() == "free explore":
            return "Explore on your own"
    return label


def item_line(item: dict) -> str:
    parts = [item_label(item)]
    one = str(item.get("one_liner") or "").strip()
    zone = str(item.get("zone") or "").strip()
    text = parts[0]
    if one:
        text = f"{text} — {one}" if text else one
    if zone:
        text = f"{text} · {zone}" if text else zone
    return text


def bonus_lines(venue: dict) -> list[str]:
    bonus = venue.get("bonus_hunt") or {}
    if not isinstance(bonus, dict):
        return []
    if str(bonus.get("status") or "") not in {"researched", "solid"}:
        return []
    lines = []
    for challenge in bonus.get("challenges") or []:
        text = str((challenge or {}).get("text") or "").strip()
        if text:
            lines.append(text)
    return lines


def intro_text(venue: dict, stop_count: int) -> str:
    name = str(venue.get("name") or "").strip()
    city = str(venue.get("city") or "").strip()
    duration = str((venue.get("practical") or {}).get("typical_duration") or "").strip()
    if city:
        first = f"A {stop_count}-stop hunt for {name} in {city}."
    else:
        first = f"A {stop_count}-stop hunt for {name}."
    if duration:
        second = (
            f"Plan on {duration}; print it before you go, then tick boxes as kids find each stop."
        )
    else:
        second = "Print it before you go, then tick boxes as kids find each stop."
    return f"{first} {second}"


def _pdf_links(pairs: tuple[tuple[str, str], ...]) -> str:
    anchors = []
    for href, label in pairs:
        anchors.append(
            f'<a class="kz-scav-pdf" href="{E(href)}" download data-kz-cta="scav-top">{E(label)}</a>'
        )
    return "".join(anchors)


def secondary_html(venue: dict) -> str:
    kind = str(venue.get("type") or "")
    if kind in _ZOO_KINDS:
        return _pdf_links((
            ("/printables/pdf/letter/scavenger-hunt.pdf", "Zoo & Park Scavenger Hunt (PDF)"),
            ("/printables/pdf/a4/scavenger-hunt-a4.pdf", "Zoo & Park Scavenger Hunt (PDF)"),
        ))
    if kind == "national_park":
        return _pdf_links((
            ("/printables/pdf/letter/park-scavenger-hunt.pdf", "Park & Backyard Hunt (PDF)"),
            ("/printables/pdf/a4/park-scavenger-hunt-a4.pdf", "Park & Backyard Hunt (PDF)"),
        ))
    if kind == "museum":
        return (
            '<a class="kz-scav-pdf" href="/printables/zoo-day-journal/" '
            'data-kz-cta="scav-top">Trip journal</a>'
        )
    return ""


def _list_html(lines: list[str]) -> str:
    items = "".join(
        '<li><span class="seo-hunt-box" aria-hidden="true">☐</span>'
        f"<span>{E(line)}</span></li>"
        for line in lines
    )
    return f'<ol class="kz-scav-list seo-hunt-list">{items}</ol>'


def scav_top_block(slug: str) -> str:
    """Hero block, or "" when slug is not one of the 12 test pages."""
    if slug not in TEST_SLUGS:
        return ""
    venue = load_venue(slug)
    items = hunt_items(venue)
    name = str(venue.get("name") or "").strip()
    bonus = bonus_lines(venue)
    bonus_html = ""
    if bonus:
        bonus_html = (
            '<h3 class="kz-scav-bonus-h">Bonus challenges</h3>'
            + _list_html(bonus)
        )
    return (
        '<section class="kz-scav-top no-print" id="printable-hunt" '
        'aria-labelledby="scav-top-h">'
        f'<h2 id="scav-top-h">Printable scavenger hunt for {E(name)}</h2>'
        f'<p class="kz-scav-intro">{E(intro_text(venue, len(items)))}</p>'
        '<p class="kz-scav-actions">'
        '<button type="button" class="kz-scav-print" data-how="print-hunt" '
        'data-kz-cta="scav-top">Build and print the hunt</button>'
        f"{secondary_html(venue)}"
        "</p>"
        '<p class="kz-scav-spec">US Letter or A4 · black &amp; white is fine</p>'
        f"{_list_html([item_line(item) for item in items])}"
        f"{bonus_html}"
        "</section>"
    )


def scav_top_css_tag(slug: str) -> str:
    if slug not in TEST_SLUGS:
        return ""
    return f'<link rel="stylesheet" href="{_CSS_HREF}" />'


def scav_top_script_tag(slug: str) -> str:
    if slug not in TEST_SLUGS:
        return ""
    return f'<script src="{_JS_SRC}" defer></script>'


def _insert_before(html: str, marker: str, snippet: str) -> str:
    idx = html.find(marker)
    if idx < 0:
        raise SystemExit(f"missing {marker}")
    return html[:idx] + snippet + "\n" + html[idx:]


def patch_html(html: str, slug: str) -> str:
    """Insert the block, stylesheet, and qr-welcome tag. Existing lines stay."""
    if slug not in TEST_SLUGS:
        return html
    block = scav_top_block(slug)
    if 'id="printable-hunt"' not in html:
        h1 = html.find("</h1>")
        if h1 < 0:
            raise SystemExit(f"{slug}: no h1")
        # Keep the h1 line intact. The block is the next line.
        line_end = html.find("\n", h1)
        if line_end < 0:
            raise SystemExit(f"{slug}: h1 line has no newline")
        html = html[: line_end + 1] + "        " + block + "\n" + html[line_end + 1 :]
    if _CSS_HREF not in html:
        html = _insert_before(html, "</head>", "  " + scav_top_css_tag(slug))
    if "qr-welcome.js" not in html:
        html = _insert_before(html, "</body>", "  " + scav_top_script_tag(slug))
    return html


def apply_test_pages() -> int:
    changed = 0
    for slug in sorted(TEST_SLUGS):
        path = FIELD / slug / "index.html"
        original = path.read_text(encoding="utf-8")
        updated = patch_html(original, slug)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1
            print(f"patched {slug}")
        else:
            print(f"unchanged {slug}")
    return changed


if __name__ == "__main__":
    raise SystemExit(0 if apply_test_pages() >= 0 else 1)
