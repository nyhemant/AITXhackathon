"""Places map leads /start/ without changing the frozen title block."""

from __future__ import annotations

import html
import json
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
START = REPO / "static" / "start"
FP = REPO / "static" / "field-pack"
HTML_PATH = START / "index.html"
ABOUT = REPO / "static" / "about" / "index.html"
VENUES = FP / "data" / "venues"

FEATURED = [
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
]

# Map v2: the detailed USA plate gives Baltimore, Bronx Zoo and AMNH their own tags.
GROUPS = [
    ("bronx-zoo", ["bronx-zoo"]),
    ("amnh", ["amnh"]),
    ("dc", ["air-and-space", "national-zoo"]),
    ("baltimore", ["national-aquarium-baltimore"]),
    ("chicago", ["shedd-aquarium", "lincoln-park-zoo"]),
    ("toronto", ["toronto-zoo"]),
    ("nashville", ["nashville-adventure-science"]),
    ("austin", ["austin-zoo"]),
    ("redwood", ["redwood"]),
    ("joshua-tree", ["joshua-tree"]),
    # 2026-11-12: map-only pins (not in the venue-card row or the scavenger test set).
    # Dallas Zoo pin was here 2026-11-12 to 2026-11-13; removed so comparison pair 10 is unpinned.
    # Fort Worth Zoo (pair 8) stays at Heymant's request.
    ("san-diego", ["san-diego-zoo"]),
    ("perot-museum", ["perot-museum"]),
    ("fort-worth-zoo", ["fort-worth-zoo"]),
    ("tampa", ["tampa-zoo"]),
    ("yellowstone", ["yellowstone"]),
    ("glacier", ["glacier"]),
]
MAP_ONLY = ["san-diego-zoo", "perot-museum", "fort-worth-zoo", "tampa-zoo", "yellowstone", "glacier"]

BANNED = re.compile(r"\b(?:free|we|our|us)\b|no-cost", re.I)
HREF = re.compile(r'href="([^"]+)"')
ZOO_PDF = "/printables/pdf/letter/scavenger-hunt.pdf"
PARK_PDF = "/printables/pdf/letter/park-scavenger-hunt.pdf"


def _git_show(path: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"origin/main:{path}"],
        cwd=REPO,
        text=True,
    )


def _meta(html: str, attr: str) -> str:
    match = re.search(rf'<meta {attr} content="([^"]*)"', html)
    assert match, attr
    return match.group(1)


def _print_href(vtype: str, slug: str) -> str:
    if vtype in ("zoo", "aquarium"):
        return ZOO_PDF
    if vtype == "national_park":
        return PARK_PDF
    return f"/field-pack/{slug}/#printable-hunt"


class HomeHuntsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.main = _git_show("static/start/index.html")
        cls.js = (START / "home-map-v2.js").read_text(encoding="utf-8")
        css = sorted(START.glob("home-map-v2-?.css"))
        assert len(css) == 1, css
        cls.css = css[0].read_text(encoding="utf-8")

    def test_title_meta_h1_and_canonical_match_main(self):
        for attr in (
            'name="description"',
            'property="og:title"',
            'property="og:description"',
            'property="og:url"',
            'property="og:image"',
            'property="og:type"',
            'property="og:site_name"',
            'name="twitter:card"',
            'name="twitter:title"',
            'name="twitter:description"',
            'name="twitter:image"',
        ):
            self.assertEqual(_meta(self.html, attr), _meta(self.main, attr), attr)
        title = re.search(r"<title>(.*?)</title>", self.html).group(1)
        self.assertEqual(title, re.search(r"<title>(.*?)</title>", self.main).group(1))
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', self.html).group(1)
        self.assertEqual(
            canon,
            re.search(r'<link rel="canonical" href="([^"]+)"', self.main).group(1),
        )
        self.assertEqual(canon, "https://kidzookit.com/start/")
        ld = re.search(
            r'<script type="application/ld\+json">(\{.*?\})</script>',
            self.html,
        ).group(1)
        main_ld = re.search(
            r'<script type="application/ld\+json">(\{.*?\})</script>',
            self.main,
        ).group(1)
        self.assertEqual(ld, main_ld)
        h1 = re.search(r'<h1 id="start-heading">(.*?)</h1>', self.html).group(1)
        self.assertEqual(
            h1,
            re.search(r'<h1 id="start-heading">(.*?)</h1>', self.main).group(1),
        )
        self.assertEqual(h1, "Virtual Zoo for Kids: Live Cams &amp; Animal Cards")
        self.assertEqual(self.html.count("<h1"), 1)

    def test_toggle_defaults_to_places_and_map_reuses_places_tile(self):
        animals = re.search(
            r'<button type="button" id="home-map-animals" aria-pressed="([^"]+)">Animals</button>',
            self.html,
        )
        places = re.search(
            r'<button type="button" id="home-map-places" aria-pressed="([^"]+)">Places</button>',
            self.html,
        )
        self.assertIsNotNone(animals)
        self.assertIsNotNone(places)
        self.assertEqual(animals.group(1), "false")
        self.assertEqual(places.group(1), "true")
        self.assertIn('role="group" aria-label="Map"', self.html)
        hero = re.search(r'<section class="start-hero"[^>]*>', self.html)
        self.assertIsNotNone(hero)
        self.assertIn("hidden", hero.group(0))
        self.assertLess(self.html.find('id="start-heading"'), self.html.find('id="home-hunts"'))
        self.assertLess(self.html.find('id="home-map-places"'), self.html.find('id="home-places-map"'))
        self.assertLess(self.html.find('id="home-places-map"'), self.html.find('id="start-hero"'))
        self.assertLess(self.html.find('id="start-hero"'), self.html.find('id="home-venue-row"'))
        self.assertLess(self.html.find('id="home-venue-row"'), self.html.find('id="start-home"'))
        self.assertRegex(self.html, r'data-kzm-svg="/start/map-v2/[ab]-usa-v1\.svg\?v=1"')
        self.assertIn("/start/home-map-v2.js?v=2", self.html)
        self.assertTrue((START / "home-map-v1.js").is_file())  # old URL keeps working
        self.assertIn('href="/field-pack/">See all places</a>', self.html)
        self.assertIn("/shell/qr-welcome.js?v=4", self.html)

    def test_metro_pins_and_valid_card_links(self):
        pins = re.findall(
            r'<button type="button" class="home-place-pin[^"]*" data-home-pin="([^"]+)" '
            r'data-members="([^"]+)"',
            self.html,
        )
        self.assertEqual([row[0] for row in pins], [row[0] for row in GROUPS])
        self.assertEqual(len(re.findall(r'class="home-place-pin[ "]', self.html)), len(GROUPS))
        member_slugs = []
        for gid, blob in pins:
            members = json.loads(html.unescape(blob))
            slugs = [row["slug"] for row in members]
            self.assertEqual(slugs, dict(GROUPS)[gid])
            member_slugs.extend(slugs)
            for row in members:
                venue = json.loads((VENUES / f"{row['slug']}.json").read_text(encoding="utf-8"))
                self.assertEqual(row["name"], venue["name"])
                self.assertEqual(row["city"], venue["city"])
                self.assertEqual(row["print"], _print_href(venue["type"], row["slug"]))
                self.assertEqual(row["page"], f"/field-pack/{row['slug']}/")
        self.assertEqual(sorted(member_slugs), sorted(FEATURED + MAP_ONLY))
        self.assertIn("inset: -8px -3px", self.css)  # 44px tap target
        self.assertIn("Print the scavenger hunt", self.js)
        self.assertIn("See the full page", self.js)
        cards = re.findall(
            r'<article class="home-venue-card" data-home-venue="([^"]+)">'
            r'<p class="home-venue-name">([^<]*)</p>'
            r'<p class="home-venue-city">([^<]*)</p>'
            r'<a class="home-venue-print" data-kz-cta="home-map" href="([^"]+)">Print the scavenger hunt</a>'
            r'<a class="home-venue-page" href="([^"]+)">See the full page</a>',
            self.html,
        )
        self.assertEqual([row[0] for row in cards], FEATURED)
        for slug, name, city, printed, page in cards:
            venue = json.loads((VENUES / f"{slug}.json").read_text(encoding="utf-8"))
            self.assertEqual(name, venue["name"])
            self.assertEqual(city, venue["city"])
            self.assertEqual(printed, _print_href(venue["type"], slug))
            self.assertEqual(page, f"/field-pack/{slug}/")
            self.assertTrue((FP / slug / "index.html").is_file(), slug)
            if printed.endswith(".pdf"):
                self.assertTrue((REPO / "static" / printed.lstrip("/")).is_file(), printed)
            else:
                self.assertTrue(printed.endswith("#printable-hunt"))
        self.assertIn('data-kz-cta="home-map"', self.html)
        self.assertIn('id="home-pin-list"', self.html)
        self.assertIn("scroll-snap-type: x mandatory", self.css)
        self.assertIn(
            '<a class="hx-mapprint" data-kz-cta="home-map" href="/field-pack/amnh/#printable-hunt">Print a scavenger hunt</a>',
            self.html,
        )
        self.assertIn('<p class="hx-maphint">Tap a pin to print</p>', self.html)
        hero = (START / "hero-common-v1.css").read_text(encoding="utf-8")
        self.assertIn(".hx-mapprint { display: none; }", hero)
        self.assertIn("@media (max-width: 640px)", hero)
        self.assertIn(".hx-maphint { display: none; }", hero)
        self.assertIn("min-height: 44px", hero)
        self.assertIn("/start/hero-common-v1.css?v=2", self.html)

    def test_places_map_is_full_width_without_start_here_box(self):
        """The Start here side panel is gone; sample venue cards stay under the map."""
        self.assertNotIn('class="hx-feature"', self.html)
        self.assertNotIn('aria-label="Start here"', self.html)
        self.assertNotIn("hx-feature-label", self.html)
        self.assertNotIn(">Start here<", self.html)
        self.assertIn('id="home-venue-row"', self.html)
        self.assertEqual(len(re.findall(r'<article class="home-venue-card"', self.html)), len(FEATURED))
        self.assertIn('id="kzm-usa-pan"', self.html)
        self.assertIn('id="kzm-usa-hint"', self.html)
        self.assertIn("Drag sideways to see more", self.html)
        self.assertIn("touch-action: pan-x pan-y", self.css)
        self.assertIn('id="home-pin-card"', self.html)
        self.assertIn('id="home-pin-close"', self.html)
        self.assertIn("keydown", self.js)
        self.assertIn("Escape", self.js)
        hero_a = (START / "hero-a-v1.css").read_text(encoding="utf-8")
        self.assertNotIn("minmax(0, 1.8fr) minmax(0, 1fr)", hero_a)
        self.assertNotIn(".hx-feature", hero_a)
        self.assertIn(".hx-mapcard .home-places-map,", hero_a)
        self.assertIn("width: 100%", hero_a)
        self.assertIn("/start/hero-a-v1.css?v=2", self.html)

    def test_previous_links_and_arya_name_stay(self):
        old = {href.split("?", 1)[0] for href in HREF.findall(self.main)}
        new = {href.split("?", 1)[0] for href in HREF.findall(self.html)}
        self.assertEqual(sorted(old - new), [])
        self.assertIn("Play &amp; learn printables", self.html)
        self.assertIn("Watch Live", self.html)
        self.assertEqual(
            self.html.count("Arya’s Wildlife Project"),
            self.main.count("Arya’s Wildlife Project"),
        )
        about = ABOUT.read_text(encoding="utf-8")
        main_about = _git_show("static/about/index.html")
        self.assertEqual(
            about.count("Arya’s Wildlife Project"),
            main_about.count("Arya’s Wildlife Project"),
        )

    def test_new_copy_skips_banned_words(self):
        section = re.search(
            r'<section id="home-hunts"[\s\S]*?</section>\s*<div class="start-rest"',
            self.html,
        )
        self.assertIsNotNone(section)
        for sample in (section.group(0), self.css, self.js):
            hit = BANNED.search(sample)
            self.assertIsNone(hit, hit.group(0) if hit else "")


if __name__ == "__main__":
    unittest.main()
