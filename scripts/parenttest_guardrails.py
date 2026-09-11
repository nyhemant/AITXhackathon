#!/usr/bin/env python3
"""ParentTest production guardrails for Field Trip Kit cards.

Read-only checks. Fail the build when Sep 2026 Layer A/B regressions return:
  A) baked Try-next thumbs leave the card's kingdom
  B) visible Watch Live CTA with no tour habitat
  C) empty catalog `pictures` on animal / sea_life cards

Kingdom mapping (do not invent a new ontology)
----------------------------------------------
Source: static/field-pack/data/card-kinds.tsv via load_card_kinds().
Try-next kingdom is study_try_next_hub() — the same helper the SPA picker
and rewrite_card_try_next.py already use.

  TSV hub        card_kind()      Try-next kingdom     In scope for A/C
  -------------  ---------------  -------------------  ----------------
  wildlife       animal           wildlife             yes
  sealife        sea_life         sealife              yes
  attractions    attraction       (n/a)                no
  parks          place_feature    (n/a)                no

study_try_next_hub(id) returns "sealife" only when TSV hub is sealife;
every other id groups as "wildlife". Thumb ids use that same helper, so a
wildlife card may recommend a parks study card (bison) — that is in-kingdom
under the existing helper.

Usage:
  python3 scripts/parenttest_guardrails.py --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from field_pack_catalog_kind import load_card_kinds  # noqa: E402
from generate_bdo_seo import load_catalog_depth, load_vft_by_card, vft_can_watch_live  # noqa: E402
from rewrite_card_try_next import baked_try_next_ids  # noqa: E402
from study_cards import study_try_next_hub  # noqa: E402

FP = ROOT / "static" / "field-pack"
CARDS = FP / "cards"
VDIR = FP / "data" / "virtual-venues"

# TSV hubs that are animal | sea_life. Attractions + parks stay out.
ANIMAL_SEA_LIFE_HUBS = frozenset({"wildlife", "sealife"})

# Tiny documented exceptions only. Each entry is (card_id, reason).
TRY_NEXT_CROSS_KINGDOM_ALLOW: tuple[tuple[str, str], ...] = ()
WATCH_LIVE_WITHOUT_HABITAT_ALLOW: tuple[tuple[str, str], ...] = ()
EMPTY_PICTURES_ALLOW: tuple[tuple[str, str], ...] = ()

# Film-library overlays that already have video/cam, but baked cards still hide
# Watch Live (PR #207). A separate PR is restoring those CTAs — do not block
# this suite on that restore. Drop an id here when its card gains Watch Live.
# Reason: CTA restore is a sibling PR; aquarium/zoo film libraries already have media.
LIBRARY_WATCH_LIVE_PENDING_RESTORE = frozenset(
    {
        "cheetah",
        "chimpanzee",
        "cuttlefish",
        "galapagos-tortoise",
        "kelp-forest",
        "koala",
        "manta-ray",
        "orangutan",
        "polar-bear",
        "puffin",
        "red-panda",
        "ring-tailed-lemur",
        "sea-otter",
        "two-toed-sloth",
        "whale-shark",
        "zebra",
    }
)

# Short slugs that 404; hub / card links must use the canonical card id.
CANONICAL_SHORT_SLUGS = {
    "giraffe": "reticulated-giraffe",
}

WATCH_TAG_RE = re.compile(
    r'<a[^>]+class="[^"]*(?:card-watch-live|card-page-photo-link)[^"]*"[^>]*>',
    re.I,
)
HREF_RE = re.compile(r"""\bhref\s*=\s*(['"])(.*?)\1""", re.I)
HABITAT_RE = re.compile(r"#habitat=([^&\"'\s]+)")


def _allow_ids(rows: tuple[tuple[str, str], ...]) -> set[str]:
    return {cid for cid, _reason in rows}


def published_animal_sea_life_ids(kinds: dict | None = None) -> list[str]:
    """Published animal + sea_life slugs from card-kinds.tsv (not attractions/parks)."""
    table = kinds if kinds is not None else load_card_kinds()
    return sorted(
        cid for cid, row in table.items() if row.get("hub") in ANIMAL_SEA_LIFE_HUBS
    )


def card_kingdom(card_id: str, kinds: dict | None = None) -> str:
    """sealife | wildlife — existing study_try_next_hub mapping."""
    return study_try_next_hub(card_id, kinds)


def load_card_html(card_id: str) -> str:
    path = CARDS / card_id / "index.html"
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def tour_habitat_ids(vdir: Path | None = None) -> set[str]:
    """Real virtual-zoo / virtual-aquarium tour habitats (not film-library overlays)."""
    root = vdir if vdir is not None else VDIR
    ids: set[str] = set()
    for name in ("virtual-zoo.json", "virtual-aquarium.json"):
        path = root / name
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for h in data.get("habitats") or []:
            hid = str(h.get("id") or "").strip()
            cid = str(h.get("cardId") or "").strip()
            if hid:
                ids.add(hid)
            if cid:
                ids.add(cid)
    return ids


def _library_entry_playable(card: dict) -> bool:
    video = card.get("video") if isinstance(card.get("video"), dict) else {}
    cam = card.get("cam") if isinstance(card.get("cam"), dict) else {}
    return bool(
        str(video.get("url") or "").strip()
        or str(cam.get("url") or "").strip()
        or str(cam.get("embed") or "").strip()
    )


def film_library_playable_ids(vdir: Path | None = None) -> set[str]:
    """cardIds in aquarium/zoo film libraries that already have video or cam."""
    root = vdir if vdir is not None else VDIR
    ids: set[str] = set()
    for name in ("aquarium-film-library.json", "zoo-film-library.json"):
        path = root / name
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for card in data.get("cards") or []:
            cid = str(card.get("cardId") or "").strip()
            if cid and _library_entry_playable(card):
                ids.add(cid)
    return ids


def _main(html: str) -> str:
    if '<main class="card-page">' not in html:
        return html
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


def visible_watch_live_hrefs(html: str) -> list[str]:
    """hrefs of visible card-watch-live / hero photo Watch Live links in <main>."""
    hrefs: list[str] = []
    for tag in WATCH_TAG_RE.findall(_main(html)):
        match = HREF_RE.search(tag)
        if match:
            hrefs.append(unescape(match.group(2)))
    return hrefs


def cross_kingdom_try_next_issues(
    *,
    html_by_id: dict[str, str] | None = None,
    kinds: dict | None = None,
    ids: list[str] | None = None,
) -> list[str]:
    """A: baked Try-next thumbs must stay in the same TSV kingdom as the card."""
    table = kinds if kinds is not None else load_card_kinds()
    want = ids if ids is not None else published_animal_sea_life_ids(table)
    skip = _allow_ids(TRY_NEXT_CROSS_KINGDOM_ALLOW)
    issues: list[str] = []
    for cid in want:
        if cid in skip:
            continue
        html = (html_by_id or {}).get(cid) if html_by_id is not None else load_card_html(cid)
        if html_by_id is not None and cid not in html_by_id:
            continue
        if not html:
            issues.append(f"{cid}: missing cards/{cid}/index.html")
            continue
        hub = card_kingdom(cid, table)
        baked = baked_try_next_ids(html)
        if not baked:
            issues.append(f"{cid}: no baked Try-next thumbs")
            continue
        crossed = [
            nxt for nxt in baked if card_kingdom(nxt, table) != hub
        ]
        if crossed:
            issues.append(
                f"{cid}: Try-next {crossed} left kingdom {hub} (baked {baked})"
            )
    return issues


def dead_watch_live_issues(
    *,
    html_by_id: dict[str, str] | None = None,
    kinds: dict | None = None,
    ids: list[str] | None = None,
    habitats: set[str] | None = None,
    library_playable: set[str] | None = None,
    vft_by_card: dict | None = None,
) -> list[str]:
    """B: visible Watch Live needs a tour habitat or playable film-library media."""
    table = kinds if kinds is not None else load_card_kinds()
    want = ids if ids is not None else published_animal_sea_life_ids(table)
    skip = _allow_ids(WATCH_LIVE_WITHOUT_HABITAT_ALLOW)
    real = habitats if habitats is not None else tour_habitat_ids()
    library = (
        library_playable if library_playable is not None else film_library_playable_ids()
    )
    vft = vft_by_card if vft_by_card is not None else load_vft_by_card()
    issues: list[str] = []
    for cid in want:
        if cid in skip:
            continue
        html = (html_by_id or {}).get(cid) if html_by_id is not None else load_card_html(cid)
        if html_by_id is not None and cid not in html_by_id:
            continue
        if not html:
            continue
        hrefs = visible_watch_live_hrefs(html)
        if not hrefs:
            continue
        rec = vft.get(cid) or {}
        library_ok = cid in library
        for href in hrefs:
            hid_m = HABITAT_RE.search(href)
            hid = hid_m.group(1) if hid_m else ""
            if not hid:
                issues.append(f"{cid}: Watch Live {href} has no #habitat=")
                continue
            tour_ok = hid in real and vft_can_watch_live(rec)
            if not tour_ok and not library_ok:
                issues.append(
                    f"{cid}: Watch Live #{hid} has no tour habitat and no film-library video/cam"
                )
    return issues


def missing_library_watch_live_issues(
    *,
    html_by_id: dict[str, str] | None = None,
    kinds: dict | None = None,
    ids: list[str] | None = None,
    library_playable: set[str] | None = None,
    pending: set[str] | None = None,
) -> list[str]:
    """Film-library video/cam cards should show Watch Live (hide must see the libraries)."""
    table = kinds if kinds is not None else load_card_kinds()
    want = ids if ids is not None else published_animal_sea_life_ids(table)
    library = (
        library_playable if library_playable is not None else film_library_playable_ids()
    )
    skip = LIBRARY_WATCH_LIVE_PENDING_RESTORE if pending is None else set(pending)
    issues: list[str] = []
    for cid in want:
        if cid not in library or cid in skip:
            continue
        html = (html_by_id or {}).get(cid) if html_by_id is not None else load_card_html(cid)
        if html_by_id is not None and cid not in html_by_id:
            continue
        if not html:
            issues.append(f"{cid}: film library has video/cam but cards/{cid}/index.html is missing")
            continue
        if not visible_watch_live_hrefs(html):
            issues.append(
                f"{cid}: film library has video/cam but baked HTML has no Watch Live CTA"
            )
    return issues


def short_slug_hub_issues(*, hub_html: str | None = None) -> list[str]:
    """Hub must not point animal/sea_life at a 404 short slug (giraffe → reticulated-giraffe)."""
    html = hub_html if hub_html is not None else (CARDS / "index.html").read_text(encoding="utf-8")
    issues: list[str] = []
    for short, canonical in CANONICAL_SHORT_SLUGS.items():
        if re.search(rf"/field-pack/cards/{re.escape(short)}/?", html):
            issues.append(
                f"cards hub links to /cards/{short}/ (404); canonical is {canonical}"
            )
    for slug in re.findall(r"/field-pack/cards/([a-z0-9-]+)/", html):
        if slug in CANONICAL_SHORT_SLUGS:
            continue
        if not (CARDS / slug / "index.html").is_file():
            issues.append(f"cards hub links to missing cards/{slug}/")
    return issues


def empty_pictures_issues(
    *,
    catalog: dict | None = None,
    html_by_id: dict[str, str] | None = None,
    kinds: dict | None = None,
    ids: list[str] | None = None,
) -> list[str]:
    """C: catalog.js pictures must be non-empty for animal / sea_life; bake keeps the URL."""
    table = kinds if kinds is not None else load_card_kinds()
    want = ids if ids is not None else published_animal_sea_life_ids(table)
    skip = _allow_ids(EMPTY_PICTURES_ALLOW)
    cat = catalog if catalog is not None else load_catalog_depth()
    issues: list[str] = []
    for cid in want:
        if cid in skip:
            continue
        item = cat.get(cid)
        if item is None:
            if catalog is not None:
                continue
            issues.append(f"{cid}: missing from catalog.js")
            continue
        pics = str((item.get("links") or {}).get("pictures") or "").strip()
        if not pics:
            issues.append(f"{cid}: catalog.js links.pictures is empty")
            continue
        html = (html_by_id or {}).get(cid) if html_by_id is not None else load_card_html(cid)
        if html_by_id is not None and cid not in html_by_id:
            continue
        if html and pics not in html:
            issues.append(f"{cid}: catalog pictures URL missing from baked card HTML")
    return issues


def all_issues(**kwargs) -> dict[str, list[str]]:
    shared = {k: kwargs[k] for k in ("html_by_id", "kinds", "ids") if k in kwargs}
    return {
        "try_next_kingdom": cross_kingdom_try_next_issues(**shared),
        "watch_live_habitat": dead_watch_live_issues(**shared),
        "empty_pictures": empty_pictures_issues(**shared),
        "library_watch_live": missing_library_watch_live_issues(**shared),
        "short_slug_hub": short_slug_hub_issues(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="Exit 1 if any guardrail fails")
    args = ap.parse_args()
    if not args.check:
        ap.error("use --check")

    kinds = load_card_kinds()
    published = published_animal_sea_life_ids(kinds)
    print("ParentTest production guardrails")
    print(f"  published animal/sea_life: {len(published)}")
    print("  kingdom: TSV hub wildlife→animal / sealife→sea_life (study_try_next_hub)")

    found = all_issues(kinds=kinds)
    failed = 0
    for name, rows in found.items():
        print(f"  {name}: {len(rows)}")
        for line in rows:
            print(f"    - {line}")
        failed += len(rows)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
