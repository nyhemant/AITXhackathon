"""Map explorer chrome is sparse: map first, short title, no sales/FAQ essays."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

from busyparent_agent.web import START_PREFIX, WebHandler


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CTA_FIND,
    EXPLORER_H1,
    EXPLORER_TITLE,
    LANDING_CSS_VER,
    LANDING_HOOK_JS_VER,
    LANDING_MAP_JS_VER,
    TYPE_LANDINGS,
    TYPE_HUB_LEAD,
)

FP = REPO / "static" / "field-pack"
HOME = FP / "index.html"
MAP_JS = FP / "js" / "landing-map.js"
HOOK_JS = FP / "js" / "landing-hook.js"
GEN = REPO / "scripts" / "generate_bdo_seo.py"
WORDY = (
    "Explore a Zoo at Home or Print a Hunt",
    "explore a zoo, aquarium, museum, or park at home with cards",
    "Print a hunt if you’re going in person",
    "Print a hunt if you're going in person",
    "or print a hunt for the visit",
    "Explore a place at home",
    "Explore a place:",
    "Explore a place (no map needed)",
    "Map needs JavaScript",
    "Map didn’t load",
    "Explore a zoo at home",
    "Explore an aquarium at home",
    "Explore a museum at home",
    "Explore a park at home",
    "tap for places",
    "Common questions",
    "FAQPage",
    "Tabs above filter the map",
    "Each day type pairs places",
    "Catalog: wildlife cards",
    "Create and print your mission",
    "Create/print mission",
    "Print one-page hunt",
    "Sample Q&A card",
    "Tap to print this card",
    "Tap to print a one-page sample card",
    "Pick up where you left off",
    "Zoos & safaris",
    "Museums & science",
    "Places to visit",
    "Popular places",
)


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


class FakeHandler(WebHandler):
    def __init__(self, path):
        self.path = path
        self.headers = {}
        self._code = None
        self._headers = {}
        self.wfile = _Buf()

    def send_response(self, code, message=None):
        self._code = code

    def send_error(self, code, message=None):
        self._code = code

    def send_header(self, k, v):
        self._headers[k] = v

    def end_headers(self):
        return

    def log_message(self, format, *args):
        return


def _get(path: str) -> FakeHandler:
    h = FakeHandler(path)
    h.do_GET()
    return h


def _hero(html: str) -> str:
    return html.split('id="landing-hero"', 1)[1].split("</header>", 1)[0]


def _chrome(html: str) -> str:
    """Visible explorer chrome above the map + labels beside it."""
    head = html.split("<body", 1)[0]
    hero = html.split('id="landing-hero"', 1)[1].split('id="during"', 1)[0]
    beside = html.split('id="during"', 1)[1].split('id="after"', 1)[0]
    return head + hero + beside


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class MapExplorerSparseChromeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HOME.read_text(encoding="utf-8")
        cls.map_js = MAP_JS.read_text(encoding="utf-8")
        cls.hook = HOOK_JS.read_text(encoding="utf-8")
        cls.gen = GEN.read_text(encoding="utf-8")

    def test_constants_lock_short_explorer_voice(self):
        self.assertEqual(EXPLORER_H1, "Find a place")
        self.assertEqual(EXPLORER_TITLE, "Find a place · Field Trip Kit")
        self.assertEqual(CTA_FIND, "Find")
        self.assertLessEqual(len(EXPLORER_H1), 16)
        self.assertIn('EXPLORER_H1 = "Find a place"', self.gen)
        self.assertNotIn('CTA_READY = "Explore →"', self.gen)
        self.assertIn(f"LANDING_CSS_VER = \"{LANDING_CSS_VER}\"", self.gen)

    def test_title_is_short_and_meta_drops_sales_pitch(self):
        title = re.search(r"<title>(.*?)</title>", self.html, re.S)
        self.assertIsNotNone(title)
        self.assertEqual(_text(title.group(1)), EXPLORER_TITLE)
        desc = re.search(r'name="description"\s+content="([^"]+)"', self.html)
        self.assertIsNotNone(desc)
        self.assertLessEqual(len(desc.group(1)), 72)
        self.assertNotIn("print a hunt", desc.group(1).lower())
        self.assertNotIn("talk prompts", desc.group(1).lower())

    def test_hero_is_title_search_and_optional_one_line(self):
        hero = _hero(self.html)
        self.assertIn(f">{EXPLORER_H1}</h1>", hero)
        self.assertIn('id="hero-place-search"', hero)
        self.assertRegex(hero, rf">\s*{CTA_FIND}\s*</button>")
        leads = re.findall(r"<p[^>]*>(.*?)</p>", hero, re.S)
        for lead in leads:
            self.assertLessEqual(len(_text(lead)), 56)
        self.assertNotIn("class=\"pitch-cta\"", hero)
        self.assertNotIn("landing-pitch-t4b", self.html)

    def test_explorer_keeps_map_search_filters_and_place_list(self):
        self.assertIn("landing-hub", self.html)
        self.assertIn('id="us-map"', self.html)
        self.assertIn('id="hero-place-search"', self.html)
        self.assertIn('id="place-type-tabs"', self.html)
        self.assertIn('data-place-type="zoo"', self.html)
        self.assertIn('data-place-type="aquarium"', self.html)
        self.assertIn('data-place-type="museum"', self.html)
        self.assertIn('data-place-type="park"', self.html)
        self.assertNotIn('id="ready-grid"', self.html)
        self.assertNotIn('id="ready-heading"', self.html)
        self.assertIn('id="cat-places-compact"', self.html)
        self.assertIn('id="cat-popular"', self.html)
        self.assertIn("218 places worldwide", self.html)

    def test_chrome_drops_essays_faq_and_duplicate_pitch(self):
        chrome = _chrome(self.html)
        for phrase in WORDY:
            self.assertNotIn(phrase, chrome, phrase)
        self.assertNotIn('id="faq"', self.html)
        self.assertNotIn("FAQPage", self.html)
        self.assertNotIn("landing-pitch-t4b", self.html)
        self.assertNotIn("ready-now", chrome)
        self.assertNotIn("ready-card", chrome)
        self.assertNotIn("Explore →", chrome)
        for lead in re.findall(r'class="map-fallback-lead"[^>]*>(.*?)</p>', chrome, re.S):
            self.assertEqual(_text(lead), "Places")
        self.assertIn(">Places</h3>", chrome)
        self.assertIn(">Popular</p>", chrome)
        self.assertIn(">Zoos</span>", chrome)
        self.assertIn(">Museums</span>", chrome)
        self.assertIn(">Parks</span>", chrome)
        self.assertNotIn("Zoos &amp; safaris", chrome)
        self.assertNotIn("National parks", chrome)

    def test_type_tabs_filter_the_same_map_in_place(self):
        self.assertIn("function wirePlaceTypeTabs(", self.map_js)
        self.assertIn("function setPlaceType(", self.map_js)
        self.assertIn("ev.preventDefault()", self.map_js)
        self.assertIn('url.searchParams.set("type", k)', self.map_js)
        self.assertIn('href="/field-pack/zoos/"', self.html)
        self.assertIn('href="/field-pack/?type=zoo"', (FP / "zoos" / "index.html").read_text())
        self.assertIn("Left-click filters the map in place", self.map_js)

    def test_type_tab_copy_is_not_a_dual_mode_essay(self):
        self.assertIn("const TYPE_TAB_COPY", self.map_js)
        self.assertNotIn("print a hunt for the visit", self.map_js)
        self.assertNotIn("Explore a place at home", self.map_js)
        self.assertNotIn("Tabs above filter the map", self.map_js)
        self.assertNotIn("Catalog: wildlife cards", self.map_js)
        self.assertNotIn("function updateReadyChips(", self.map_js)
        self.assertNotIn("Create and print your mission", self.map_js)
        self.assertNotIn("Pick up where you left off", self.hook)

    def test_brand_stays_on_start_explorer_does_not_redirect(self):
        self.assertIn('class="shell-brand" href="/start/"', self.html)
        self.assertIn('class="shell-product" href="/start/"', self.html)
        self.assertIn('class="shell-start" href="/start/"', self.html)
        self.assertIn('href="/field-pack/" aria-current="page" role="menuitem">All places', self.html)
        explorer = _get("/field-pack/")
        self.assertEqual(explorer._code, 200)
        self.assertIsNone(explorer._headers.get("Location"))
        body = explorer.wfile.getvalue()
        self.assertIn(b"landing-hub", body)
        self.assertIn(b'id="us-map"', body)
        root = _get("/")
        self.assertEqual(root._code, 302)
        self.assertEqual(root._headers.get("Location"), START_PREFIX + "/")

    def test_cache_and_type_hubs_stay_sparse(self):
        self.assertIn(f"landing.css?v={LANDING_CSS_VER}", self.html)
        self.assertIn(f"landing-map.js?v={LANDING_MAP_JS_VER}", self.html)
        self.assertIn(f"landing-hook.js?v={LANDING_HOOK_JS_VER}", self.html)
        self.assertEqual(TYPE_HUB_LEAD, "Cards, photos, and a cam when we have one.")
        for meta in TYPE_LANDINGS:
            html = (FP / meta["path"] / "index.html").read_text(encoding="utf-8")
            with self.subTest(hub=meta["path"]):
                self.assertIn(f">{meta['h1']}</h1>", html)
                self.assertIn(f'href="/field-pack/?type={meta["map_type"]}">Map</a>', html)
                self.assertNotIn("print a hunt", html.lower())
                self.assertNotIn("Explore a zoo at home", html)
                self.assertNotIn("optional hunt", html.lower())
                leads = re.findall(r'class="type-lead"[^>]*>(.*?)</p>', html, re.S)
                if leads:
                    self.assertLessEqual(len(_text(leads[0])), 56)


if __name__ == "__main__":
    unittest.main()
