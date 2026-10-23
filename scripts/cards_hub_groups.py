#!/usr/bin/env python3
"""Cards hub 'Browse by group' (2026-10-23). Idempotent post-process of
static/field-pack/cards/index.html:
  * chip nav (plain anchors, works with JS off) under the hero intro
  * Wildlife panel split into Mammals / Birds / Reptiles sub-lists (static, crawlable)
  * anchor targets for Ocean & water and Museum stops
  * hub tile photos use the same ?v=img2 URL the card page uses (one URL per photo)
Re-run after any generate_bdo_seo.py run that rewrites the cards hub:
    python3 scripts/cards_hub_groups.py
tests/test_cards_groups.py fails if the chips or groups disappear."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HUB = REPO / "static" / "field-pack" / "cards" / "index.html"
CARDS = REPO / "static" / "field-pack" / "cards"

# Every hub card in exactly one group. Wildlife panel is split by animal class.
WILDLIFE_GROUPS = [
    ("mammals", "Mammals", [
        "african-elephant", "african-lion", "american-bison", "asian-small-clawed-otter",
        "cheetah", "chimpanzee", "elk", "giant-panda", "koala", "nile-hippo", "orangutan",
        "polar-bear", "red-panda", "reticulated-giraffe", "ring-tailed-lemur",
        "sumatran-tiger", "two-toed-sloth", "warthog", "western-lowland-gorilla", "zebra"]),
    ("birds", "Birds", ["african-penguin", "caribbean-flamingo", "ostrich"]),
    ("reptiles", "Reptiles", ["american-alligator", "galapagos-tortoise"]),
]
CHIPS = [
    ("mammals", "Mammals", "\U0001F418"),
    ("birds", "Birds", "\U0001F426"),
    ("reptiles", "Reptiles", "\U0001F422"),
    ("ocean", "Ocean &amp; water", "\U0001F419"),
    ("museum", "Museum stops", "\U0001F996"),
]
START, END = "<!-- kz-groups:chips -->", "<!-- /kz-groups:chips -->"


def chips_html():
    links = "".join(
        f'<a class="cards-group-chip" href="/field-pack/cards/#g-{gid}" data-group="{gid}" '
        f'data-related-link="group"><span aria-hidden="true">{emo}</span> {label}</a>'
        for gid, label, emo in CHIPS)
    return (f'{START}<nav class="cards-groups" aria-label="Browse cards by group">'
            f'<p class="cards-groups-label">Browse by group</p>'
            f'<div class="cards-groups-row">{links}</div></nav>{END}')


def canonical_src(html):
    def fix(m):
        cid, src = m.group(1), m.group(2)
        page = CARDS / cid / "index.html"
        if not page.exists():
            return m.group(0)
        hero = re.search(r'class="card-page-photo" src="([^"]+)"', page.read_text(encoding="utf-8"))
        if hero and hero.group(1).split("?")[0] == src.split("?")[0] and hero.group(1) != src:
            return m.group(0).replace(f'src="{src}"', f'src="{hero.group(1)}"')
        return m.group(0)
    return re.sub(r'<li class="cards-hub-item" data-card-id="([^"]+)".*?<img class="cards-hub-thumb" src="([^"]+)"', fix, html)


def main():
    html = HUB.read_text(encoding="utf-8")
    orig = html
    # 1) chips after the hero intro paragraph
    html = re.sub(r"\n\s*" + re.escape(START) + r".*?" + re.escape(END), "", html, flags=re.S)
    intro_end = html.index("</p>", html.index('class="cards-play-intro')) + len("</p>")
    html = html[:intro_end] + "\n        " + chips_html() + html[intro_end:]
    # 2) split the wildlife list into class groups (skip if already split)
    if 'id="g-mammals"' not in html:
        sec = re.search(r'(<section class="cards-hub-section" id="cards-wildlife"[^>]*>\s*)<ul class="cards-hub-list">(.*?)</ul>', html, re.S)
        items = {m.group(1): m.group(0) for m in re.finditer(r'<li class="cards-hub-item" data-card-id="([^"]+)".*?</li>', sec.group(2), re.S)}
        used = [c for _, _, ids in WILDLIFE_GROUPS for c in ids]
        assert sorted(used) == sorted(items), (set(used) ^ set(items))
        parts = []
        for gid, label, ids in WILDLIFE_GROUPS:
            lis = "\n".join("    " + items[c] for c in ids)
            parts.append(f'  <h3 class="cards-group-h" id="g-{gid}">{label} <span class="seo-dir-count">{len(ids)}</span></h3>\n  <ul class="cards-hub-list">\n{lis}\n  </ul>')
        html = html[:sec.start()] + sec.group(1) + "\n".join(parts) + html[sec.end():]
    # 3) anchor targets on the other two panels
    if 'id="g-ocean"' not in html:
        html = html.replace('<section class="cards-hub-section" id="cards-sealife" aria-labelledby="h-sealife">',
                            '<section class="cards-hub-section" id="cards-sealife" aria-labelledby="h-sealife">\n  <span class="cards-group-anchor" id="g-ocean"></span>', 1)
    if 'id="g-museum"' not in html:
        html = html.replace('<section class="cards-hub-section" id="cards-attractions-list" aria-labelledby="h-attractions">',
                            '<section class="cards-hub-section" id="cards-attractions-list" aria-labelledby="h-attractions">\n  <span class="cards-group-anchor" id="g-museum"></span>', 1)
    # 4) one URL per photo
    html = canonical_src(html)
    # 5) assets (new versioned files)
    if "cards-groups.css" not in html:
        html = html.replace('<link rel="stylesheet" href="/field-pack/css/seo-venue.css?v=38" />',
                            '<link rel="stylesheet" href="/field-pack/css/seo-venue.css?v=38" />\n  <link rel="stylesheet" href="/field-pack/css/cards-groups.css?v=1" />', 1)
    if "cards-groups.js" not in html:
        html = html.replace('<script src="/field-pack/js/cards-explorer.js?v=9"></script>',
                            '<script src="/field-pack/js/cards-explorer.js?v=9"></script>\n  <script src="/field-pack/js/cards-groups.js?v=1"></script>\n  <script src="/shell/related-links.js?v=1"></script>', 1)
    if html != orig:
        HUB.write_text(html, encoding="utf-8")
        print("updated", HUB.relative_to(REPO))
    else:
        print("unchanged")


if __name__ == "__main__":
    main()
