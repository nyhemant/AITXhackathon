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
import re
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

# 2026-11-15: Heymant lifted the freeze ("lifting freeze unless you have critical
# reasons to freeze. We are not waiting and watching."). At ChiefGrok's direction the
# pages below changed from 2026-11-16 evening CT, so the controlled scavenger-hunt
# comparison is confounded from then (TEST NOTE in kidzookit-loop/LOG.md and baseline.md).
# Byte-identity guards now skip these slugs and still hold for the rest of the 24.
FREEZE_LIFTED_ON = "2026-11-15"
UNFROZEN_CHANGED_SLUGS = frozenset({
    # weekly 2026-11-16 (A): query pages
    "museum-of-science-industry-chi",
    "national-aquarium-baltimore",
    "aquarium-of-the-pacific",
    "amnh",
    "california-science-center",
    # unfreeze 2026-11-16 (B): Honolulu pattern
    "calgary-zoo",
    "toronto-zoo",
    "joshua-tree",
    # unfreeze 2026-11-16 (C): no cam row, so no cam claims (matches #446 / #450)
    "banff",
    "discovery-place",
    "nashville-adventure-science",
    "redwood",
    "sequoia",
    "air-and-space",  # HowTo tool said "cams" with films only
})

# 2026-11-20 round 2: Heymant ended the freeze ("The freeze is gone"). The last 10 pages that were still
# byte-identical to the 2026-11-16 freeze now change too (K4 print guard tag, then one-tap print). Byte-identity
# guards skip them from here. This set is separate from UNFROZEN_CHANGED_SLUGS on purpose: the generator still uses
# that set for the contact address and legacy JSON-LD, and those lines on these 10 pages do not change.
FREEZE_ENDED_ON = "2026-11-20"
FREEZE_ENDED_SLUGS = frozenset({
    "bronx-zoo", "austin-zoo", "national-zoo", "lincoln-park-zoo", "shedd-aquarium",
    "seattle-aquarium", "st-louis-zoo", "fort-worth-zoo", "san-antonio-zoo", "dallas-zoo",
})
assert FREEZE_ENDED_SLUGS == (TEST_SLUGS | COMPARISON_SLUGS) - UNFROZEN_CHANGED_SLUGS

# Homepage-map venues outside the test set that get the same printable block
# (2026-11-12). Not test pages and not comparison pages, so the pairs stay as set.
PIN_SLUGS = frozenset({
    "perot-museum",
    # 2026-11-16 weekly: page for "science museum scavenger hunt san francisco".
    "cal-academy",
    # 2026-11-16 unfreeze (A): comparison pages that now answer a big query.
    "museum-of-science-industry-chi",
    "aquarium-of-the-pacific",
    "california-science-center",
    # 2026-11-23 weekly: printable sheet up top on the St. Louis Zoo query page.
    "st-louis-zoo",
})
BLOCK_SLUGS = TEST_SLUGS | PIN_SLUGS

_ZOO_KINDS = frozenset({"zoo", "aquarium", "safari_zoo"})
_CSS_HREF = "/field-pack/css/scav-top-v1.css?v=3"
_JS_SRC = "/shell/qr-welcome.js?v=5"
# Test pages get their own cache key for mission-ui.js so the sticky bar code
# (data-kz-scav-print) is not served from a cached older copy. Comparison pages
# keep the generator's MISSION_UI_JS_VER.
MISSION_UI_TEST_VER = "23-scav4"
# Round 2 (2026-11-20): the top button and the sticky bar print in one tap (mission-ui.js v22).
# The drawer is still there for options: the "Change" button under the print button opens it.
PRINT_ACTION = "Print the hunt"
DEFAULT_LINE = (
    '<p class="kz-scav-default">Ready for <span id="kz-scav-default-now">ages 5–8, half day</span>. '
    '<button type="button" class="kz-scav-change" data-how="open-customize" aria-haspopup="dialog" '
    'aria-controls="mission-drawer">Change</button></p>'
)
E = lambda s: html.escape(str(s), quote=True)  # noqa: E731
_SECTION_RE = re.compile(
    r'[ \t]*<section class="kz-scav-top no-print" id="printable-hunt".*?</section>',
    re.S,
)
_OLD_STICKY = """  <div class="seo-hunt-sticky no-print" id="seo-hunt-sticky" hidden>
    <p class="seo-hunt-sticky-copy" id="seo-hunt-sticky-label"><span id="seo-hunt-count"></span>Suggested stops · Print (1 page)</p>
    <button type="button" class="btn btn-primary seo-sticky-print" id="seo-sticky-print" data-how="print-hunt">Print</button>
    <p class="print-spec seo-sticky-print-spec">US Letter or A4 · black &amp; white is fine</p>
  </div>"""


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
    # "An 8-stop", "An 11-stop", "An 18-stop" (2026-11-16 grammar fix).
    art = "An" if str(stop_count).startswith("8") or stop_count in (11, 18) else "A"
    if city:
        first = f"{art} {stop_count}-stop hunt for {name} in {city}."
    else:
        first = f"{art} {stop_count}-stop hunt for {name}."
    if duration:
        second = (
            f"Plan on {duration}; print it before you go, then tick boxes as kids find each stop."
        )
    else:
        second = "Print it before you go, then tick boxes as kids find each stop."
    return f"{first} {second}"


def _pdf_pair(name: str, letter_href: str, a4_href: str) -> str:
    """One sheet name, two paper-size buttons. Labels differ."""
    return (
        '<span class="kz-scav-pdfs">'
        f'<span class="kz-scav-pdf-name">{E(name)}</span>'
        f'<a class="kz-scav-pdf" href="{E(letter_href)}" download data-kz-cta="scav-top">PDF, US Letter</a>'
        f'<a class="kz-scav-pdf" href="{E(a4_href)}" download data-kz-cta="scav-top">PDF, A4</a>'
        "</span>"
    )


def secondary_html(venue: dict) -> str:
    kind = str(venue.get("type") or "")
    if kind in _ZOO_KINDS:
        return _pdf_pair(
            "Zoo & Park Scavenger Hunt",
            "/printables/pdf/letter/scavenger-hunt.pdf",
            "/printables/pdf/a4/scavenger-hunt-a4.pdf",
        )
    if kind == "national_park":
        return _pdf_pair(
            "Park & Backyard Hunt",
            "/printables/pdf/letter/park-scavenger-hunt.pdf",
            "/printables/pdf/a4/park-scavenger-hunt-a4.pdf",
        )
    if kind == "museum":
        return (
            '<a class="kz-scav-pdf" href="/printables/zoo-day-journal/" '
            'data-kz-cta="scav-top">Trip journal</a>'
        )
    return ""


def spec_html(venue: dict) -> str:
    """Paper size stays in the link labels, so the spec line keeps the ink note."""
    kind = str(venue.get("type") or "")
    if kind in _ZOO_KINDS or kind == "national_park":
        return '<p class="kz-scav-spec">black &amp; white is fine</p>'
    return '<p class="kz-scav-spec">US Letter or A4 · black &amp; white is fine</p>'


def _list_html(lines: list[str]) -> str:
    items = "".join(
        '<li><span class="seo-hunt-box" aria-hidden="true">☐</span>'
        f"<span>{E(line)}</span></li>"
        for line in lines
    )
    return f'<ol class="kz-scav-list seo-hunt-list">{items}</ol>'


def scav_top_block(slug: str) -> str:
    """Hero block, or "" when slug is not a test page or a PIN_SLUGS page."""
    if slug not in BLOCK_SLUGS:
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
        f'data-kz-cta="scav-top">{PRINT_ACTION}</button>'
        f"{secondary_html(venue)}"
        "</p>"
        f"{DEFAULT_LINE}"
        f"{spec_html(venue)}"
        f"{_list_html([item_line(item) for item in items])}"
        f"{bonus_html}"
        "</section>"
    )


def scav_top_css_tag(slug: str) -> str:
    if slug not in BLOCK_SLUGS:
        return ""
    return f'<link rel="stylesheet" href="{_CSS_HREF}" />'


def scav_top_script_tag(slug: str) -> str:
    if slug not in BLOCK_SLUGS:
        return ""
    return f'<script src="{_JS_SRC}" defer></script>'


def sticky_single_print_html() -> str:
    """Sticky bar for test pages: same label and drawer as the hunt button.

    Leading newline matches the generator's previous sticky snippet.
    """
    return (
        "\n"
        '  <div class="seo-hunt-sticky no-print" id="seo-hunt-sticky" '
        'data-kz-scav-print="1" hidden>\n'
        '    <button type="button" class="btn btn-primary seo-sticky-print" '
        'id="seo-sticky-print" data-how="print-hunt" data-kz-cta="scav-top">'
        f"{PRINT_ACTION}</button>\n"
        "  </div>"
    )


def _insert_before(html: str, marker: str, snippet: str) -> str:
    idx = html.find(marker)
    if idx < 0:
        raise SystemExit(f"missing {marker}")
    return html[:idx] + snippet + "\n" + html[idx:]


def patch_html(html: str, slug: str) -> str:
    """Refresh the hunt block and fold the sticky Print bar into it.

    Frozen head lines and every other existing line stay. The block and the
    sticky bar are replaced in place; the page is not regenerated.
    """
    if slug not in BLOCK_SLUGS:
        return html
    block = "        " + scav_top_block(slug)
    if _SECTION_RE.search(html):
        html = _SECTION_RE.sub(block, html, count=1)
    else:
        h1 = html.find("</h1>")
        if h1 < 0:
            raise SystemExit(f"{slug}: no h1")
        line_end = html.find("\n", h1)
        if line_end < 0:
            raise SystemExit(f"{slug}: h1 line has no newline")
        html = html[: line_end + 1] + block + "\n" + html[line_end + 1 :]
    sticky = sticky_single_print_html().lstrip("\n")
    if _OLD_STICKY in html:
        html = html.replace(_OLD_STICKY, sticky, 1)
    elif 'data-kz-scav-print="1"' not in html:
        raise SystemExit(f"{slug}: sticky bar not found")
    else:
        html = re.sub(
            r'  <div class="seo-hunt-sticky no-print" id="seo-hunt-sticky" data-kz-scav-print="1" hidden>\n.*?\n  </div>',
            sticky,
            html,
            count=1,
            flags=re.S,
        )
    html = html.replace('href="/field-pack/css/scav-top-v1.css?v=1"', f'href="{_CSS_HREF}"')
    html = re.sub(r'src="/shell/qr-welcome\.js\?v=[^"]*"', f'src="{_JS_SRC}"', html)
    html = re.sub(
        r'src="/field-pack/js/mission/mission-ui\.js\?v=[^"]*"',
        f'src="/field-pack/js/mission/mission-ui.js?v={MISSION_UI_TEST_VER}"',
        html,
    )
    if _CSS_HREF not in html:
        html = _insert_before(html, "</head>", "  " + scav_top_css_tag(slug))
    if "qr-welcome.js" not in html:
        html = _insert_before(html, "</body>", "  " + scav_top_script_tag(slug))
    return html


def apply_test_pages() -> int:
    changed = 0
    for slug in sorted(BLOCK_SLUGS):
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
