#!/usr/bin/env python3
"""Image-first place hubs (2026-10-23). Idempotent post-process of the 4 type hubs
(static/field-pack/{zoos,aquariums,museums,national-parks}/index.html):
  * 'Start here' tiles get a lazy photo the place page already uses (canonical
    card-page URL when the photo is a card photo); no photo repeats inside a hub;
    tiles with no distinct photo keep the emoji/text tile.
  * a hand-curated card strip per hub (only animals/stops that fit the place type).
  * museums hub H1 'Museums for Kids' + one intro line (also in generator TYPE_LANDINGS).
  * related_link_click link_type hub_tile / hub_card via /shell/related-links.js.
Re-run after any generate_bdo_seo.py run that rewrites the hubs:
    python3 scripts/hub_photos.py
tests/test_hub_images.py fails if the photos or strips disappear."""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"

TILE_PHOTOS = {
    "zoos": {
        "dallas-zoo": "reticulated-giraffe", "san-diego-zoo": "giant-panda",
        "bronx-zoo": "western-lowland-gorilla", "national-zoo": "asian-small-clawed-otter",
        "houston-zoo": "chimpanzee", "fort-worth-zoo": "sumatran-tiger"},
    "aquariums": {
        "georgia-aquarium": "whale-shark", "monterey-bay-aquarium": "jellyfish",
        "childrens-aquarium-dallas": "stingray", "shedd-aquarium": "sea-otter",
        "aquarium-of-the-pacific": "puffin", "seattle-aquarium": "octopus"},
    "museums": {
        "amnh": "sci-planet", "childrens-museum-perot": "cm-makery",
        "california-science-center": "sci-shuttle", "air-and-space": "sci-rocket",
        "please-touch-museum": "cm-water"},  # field-museum keeps its text tile (only dinosaur/mammal photos, both in the strip)
    "national-parks": {},  # already has place-specific park hero photos
}
STRIPS = {
    "zoos": ("Animals you might meet at a zoo",
             ["african-lion", "zebra", "african-elephant", "caribbean-flamingo", "red-panda", "ring-tailed-lemur", "african-penguin"]),
    "aquariums": ("Animals you might meet at an aquarium",
                  ["shark", "sea-turtle", "seahorse", "clownfish", "starfish", "eel", "crab"]),
    "museums": ("Museum stops to look for",
                ["sci-dinosaur", "sci-mammal-hall", "sci-astronaut", "sci-hands-on", "sci-aquarium-zone", "sci-rainforest"]),
    "national-parks": ("Wild animals and trails for park days",
                       ["american-bison", "elk", "american-alligator", "cuyahoga-towpath"]),
}
MUSEUM_H1 = "Museums for Kids"
MUSEUM_INTRO = ("Pick a museum for a kid-sized plan: dinosaur halls, space and rockets, hands-on science "
                "and children's museums, each with talk prompts and a printable sheet for your visit.")
S0, S1 = "<!-- kz-hub:strip -->", "<!-- /kz-hub:strip -->"


def card_photo(cid):
    page = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
    m = re.search(r'class="card-page-photo" src="([^"]+)"', page)
    hub = (FP / "cards" / "index.html").read_text(encoding="utf-8")
    hn = re.search(r'data-card-id="' + re.escape(cid) + r'".*?class="cards-hub-name">([^<]+)<', hub)
    if hn:
        return m.group(1), hn.group(1).strip()
    name = re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S).group(1))
    name = re.sub(r"^[^A-Za-z]+", "", name).split(" Animal Card")[0].strip()
    return m.group(1), name


def place_photo(slug, stem):
    """URL for photo `stem` as used on the place page; prefer the card-page URL."""
    page = (FP / slug / "index.html").read_text(encoding="utf-8")
    on_page = re.search(r'src="/?(?:field-pack/)?(photos/' + re.escape(stem) + r'\.jpg[^"]*)"', page)
    assert on_page, (slug, stem)
    card = FP / "cards" / stem / "index.html"
    if card.exists():
        url, _ = card_photo(stem)
        if url.split("?")[0].endswith("/" + stem + ".jpg"):
            return url
    return "/field-pack/" + on_page.group(1)


def strip_html(hub):
    title, ids = STRIPS[hub]
    tiles = []
    for cid in ids:
        url, name = card_photo(cid)
        tiles.append(f'<li><a href="/field-pack/cards/{cid}/" data-related-link="hub_card">'
                     f'<img src="{url}" alt="" width="640" height="640" loading="lazy" decoding="async" />'
                     f'<span>{name}</span></a></li>')
    return (f'{S0}<section class="kz-hub-strip" aria-labelledby="kz-hub-strip-h"><h2 id="kz-hub-strip-h">{title}</h2>'
            f'<ul>{"".join(tiles)}</ul>'
            f'<p class="kz-hub-strip-all"><a href="/field-pack/cards/" data-related-link="hub_card">See all animal cards</a></p></section>{S1}')


def process(hub):
    path = FP / hub / "index.html"
    html = path.read_text(encoding="utf-8")
    orig = html
    for slug, stem in TILE_PHOTOS[hub].items():
        pat = re.compile(r'<a class="type-feat-card" href="/field-pack/' + re.escape(slug) + r'/"><span class="type-feat-emoji" aria-hidden="true">[^<]*</span>')
        url = place_photo(slug, stem)
        html, n = pat.subn(
            f'<a class="type-feat-card type-feat-has-hero" href="/field-pack/{slug}/" data-related-link="hub_tile">'
            f'<span class="type-feat-thumb"><img src="{url}" alt="" width="640" height="640" loading="lazy" decoding="async" /></span>', html)
        assert n <= 1
    # tiles without a photo (and park tiles) still get click tracking
    html = re.sub(r'<a class="(type-feat-card[^"]*)" href="(/field-pack/[^"]+)">', r'<a class="\1" href="\2" data-related-link="hub_tile">', html)
    # strip: after the Start here grid
    html = re.sub(r"\s*" + re.escape(S0) + r".*?" + re.escape(S1), "", html, flags=re.S)
    i = html.index('<div class="type-feat-grid">')
    j = html.index("</div>", i) + len("</div>")
    html = html[:j] + "\n      " + strip_html(hub) + html[j:]
    if hub == "museums":
        html = html.replace("<h1>Museums</h1>", f"<h1>{MUSEUM_H1}</h1>", 1)
        if 'class="type-lead"' not in html:
            html = html.replace(f"<h1>{MUSEUM_H1}</h1>", f'<h1>{MUSEUM_H1}</h1>\n      <p class="type-lead">{MUSEUM_INTRO}</p>', 1)
    if "hub-strip.css" not in html:
        html = re.sub(r'(<link rel="stylesheet" href="/field-pack/css/seo-venue.css\?v=\d+" />)',
                      r'\1\n  <link rel="stylesheet" href="/field-pack/css/hub-strip.css?v=1" />', html, count=1)
    if "related-links.js" not in html:
        html = html.replace('<script src="/shell/shell.js?v=6" defer></script>',
                            '<script src="/shell/shell.js?v=6" defer></script>\n  <script src="/shell/related-links.js?v=1" defer></script>', 1)
    if html != orig:
        path.write_text(html, encoding="utf-8")
        print("updated", path.relative_to(REPO))


def main():
    for hub in TILE_PHOTOS:
        process(hub)


if __name__ == "__main__":
    main()
