"""Printable hunts lead /start/ without changing the frozen title block."""

from __future__ import annotations

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

BANNED = re.compile(r"\b(?:free|we|our|us)\b|no-cost", re.I)
HREF = re.compile(r'href="([^"]+)"')


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


class HomeHuntsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML_PATH.read_text(encoding="utf-8")
        cls.main = _git_show("static/start/index.html")
        cls.js = (START / "home-hunts-v1.js").read_text(encoding="utf-8")
        cls.css = (START / "home-hunts-v1.css").read_text(encoding="utf-8")

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

    def test_hunt_hero_leads_and_map_is_second(self):
        hunts = self.html.find('id="home-hunts"')
        heading = self.html.find('id="start-heading"')
        at_home = self.html.find('id="start-at-home-heading"')
        hero = self.html.find('id="start-hero"')
        cams = self.html.find('id="start-home"')
        self.assertTrue(0 < heading < hunts < at_home < hero < cams)
        self.assertIn(
            "Printable scavenger hunts for your next zoo, aquarium or museum trip",
            self.html,
        )
        self.assertIn("Not going anywhere today? Explore from home", self.html)
        self.assertIn('id="home-hunts-q"', self.html)
        self.assertIn('href="/printables/"', self.html)
        self.assertIn('href="/printables/scavenger-hunt/"', self.html)
        self.assertIn(">All printables<", self.html)
        self.assertIn(">Scavenger hunt printable<", self.html)

    def test_previous_links_and_arya_name_stay(self):
        old = set(HREF.findall(self.main))
        new = set(HREF.findall(self.html))
        missing = sorted(old - new)
        self.assertEqual(missing, [])
        self.assertIn("Play &amp; learn printables", self.html)
        self.assertEqual(self.html.count("Arya’s Wildlife Project"), self.main.count("Arya’s Wildlife Project"))
        self.assertGreaterEqual(self.html.count("Arya’s Wildlife Project"), 1)
        about = ABOUT.read_text(encoding="utf-8")
        main_about = _git_show("static/about/index.html")
        self.assertEqual(
            about.count("Arya’s Wildlife Project"),
            main_about.count("Arya’s Wildlife Project"),
        )
        self.assertIn("Arya’s Wildlife Project", about)

    def test_featured_cards_link_to_existing_place_pages(self):
        cards = re.findall(
            r'<a class="home-hunts-card" href="([^"]+)" data-home-hunt-slug="([^"]+)" '
            r'data-home-hunt-name="([^"]+)" data-home-hunt-city="([^"]*)">',
            self.html,
        )
        self.assertEqual([slug for _href, slug, _name, _city in cards], FEATURED)
        for href, slug, name, city in cards:
            self.assertEqual(href, f"/field-pack/{slug}/#printable-hunt")
            self.assertTrue((FP / slug / "index.html").is_file(), slug)
            venue = json.loads((VENUES / f"{slug}.json").read_text(encoding="utf-8"))
            self.assertEqual(name, venue["name"])
            self.assertEqual(city, venue["city"])
            self.assertNotIn('fetchpriority="high"', href)

        blob = self.js.split("var places = ", 1)[1].split(";", 1)[0]
        places = json.loads(blob)
        slugs = {row["slug"] for row in places}
        self.assertTrue(set(FEATURED) <= slugs)
        for row in places:
            self.assertTrue((FP / row["slug"] / "index.html").is_file(), row["slug"])
            venue = json.loads((VENUES / f"{row['slug']}.json").read_text(encoding="utf-8"))
            self.assertEqual(row["name"], venue["name"])
            self.assertEqual(row["city"], venue["city"])
        self.assertIn("home_hunt_card_click", self.js)
        self.assertIn("FPTrack", self.js)
        self.assertIn('href="/start/home-hunts-v1.css?v=1"', self.html)
        self.assertIn('src="/start/home-hunts-v1.js?v=1"', self.html)
        eager = re.findall(r'<img class="home-hunts-photo"[^>]*>', self.html)
        self.assertGreaterEqual(len(eager), 2)
        lazy = [tag for tag in eager if 'loading="lazy"' in tag]
        not_lazy = [tag for tag in eager if 'loading="lazy"' not in tag]
        self.assertEqual(len(not_lazy), 2)
        self.assertGreater(len(lazy), 0)
        for tag in eager:
            self.assertNotIn('fetchpriority="high"', tag)
            self.assertIn("width=", tag)
            self.assertIn("height=", tag)

    def test_new_copy_skips_banned_words(self):
        section = re.search(
            r'<section id="home-hunts"[\s\S]*?</section>\s*'
            r'<section id="start-at-home"[\s\S]*?<h2 id="start-at-home-heading">.*?</h2>',
            self.html,
        )
        self.assertIsNotNone(section)
        samples = [
            section.group(0),
            self.css,
            self.js,
        ]
        for sample in samples:
            hit = BANNED.search(sample)
            self.assertIsNone(hit, hit.group(0) if hit else "")


if __name__ == "__main__":
    unittest.main()
