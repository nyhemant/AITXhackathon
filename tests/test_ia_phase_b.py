"""Phase B IA: print is a side door; More menu is four doors only."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from busyparent_agent.url_aliases import PRINT_PATH, PRINT_TARGET, VFT_PATH, redirect_location
from busyparent_agent.web import WebHandler


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
START = REPO / "static" / "start" / "index.html"
ABOUT = REPO / "static" / "about" / "index.html"
LANDING = FP / "index.html"
CARDS = FP / "cards" / "index.html"
VFT = FP / "virtual-field-trip" / "index.html"
DALLAS = FP / "dallas-zoo" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
LANDING_MAP = FP / "js" / "landing-map.js"
LANDING_HOOK = FP / "js" / "landing-hook.js"
GENERATOR = REPO / "scripts" / "generate_bdo_seo.py"

FEATURED_HTML = (START, ABOUT, LANDING, CARDS, VFT)
SHELL_HTML = (START, LANDING, CARDS, VFT, DALLAS, LION)

LEGACY_HREFS = (
    "/field-pack/app.html",
    "/field-pack/parks/",
    "/field-pack/places/",
    "/field-pack/virtual-zoo/",
)

PRIMARY_MENU = (
    ("/field-pack/cards/", "Cards"),
    ("/field-pack/virtual-field-trip/", "Watch Live"),
    ("/field-pack/", "Places"),
    ("/about/", "About"),
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

    def send_header(self, key, value):
        self._headers[key] = value

    def end_headers(self):
        return

    def log_message(self, format, *args):
        return


def _get(path: str) -> FakeHandler:
    h = FakeHandler(path)
    h.do_GET()
    return h


def _menu_items(html: str, menu_id: str) -> list[tuple[str, str]]:
    block = re.search(
        rf'<(?:div|nav) id="{menu_id}"[^>]*>([\s\S]*?)</(?:div|nav)>',
        html,
    )
    assert block, f"missing #{menu_id}"
    return [
        (href, re.sub(r"<small>[\s\S]*?</small>", "", label).strip())
        for href, label in re.findall(
            r'<a\s+[^>]*href="([^"]+)"[^>]*>([\s\S]*?)</a>',
            block.group(1),
        )
    ]


class IaPhaseBTests(unittest.TestCase):
    def test_print_stays_named_side_door_not_a_start_hero(self):
        self.assertEqual(redirect_location(PRINT_PATH), PRINT_TARGET)
        h = _get(PRINT_PATH)
        self.assertEqual(h._code, 301)
        self.assertEqual(h._headers.get("Location"), PRINT_TARGET)
        start = START.read_text(encoding="utf-8")
        hero = re.search(r'<section class="start-hero"[\s\S]*?</section>', start)
        self.assertIsNotNone(hero)
        routes = re.findall(
            r'<a class="start-route" href="([^"]+)">([^<]+)</a>',
            hero.group(0),
        )
        self.assertEqual(
            routes,
            [
                ("/field-pack/cards/", "Cards"),
                ("/field-pack/virtual-field-trip/", "Watch Live"),
                ("/field-pack/", "Places"),
            ],
        )
        self.assertNotIn("/field-pack/print/", "".join(href for href, _ in routes))
        menu = _menu_items(start, "start-menu")
        self.assertEqual(menu[:4], list(PRIMARY_MENU))
        self.assertEqual(menu[4], ("/field-pack/print/", "Print cutouts"))
        self.assertIn('class="start-menu-grownup"', start)
        self.assertIn("Cut · hide · seek", start)
        about = ABOUT.read_text(encoding="utf-8")
        before_exp = about.split('id="experimental"', 1)[0]
        self.assertIn("Side door:", before_exp)
        self.assertNotIn("grown-ups", before_exp)
        self.assertIn('href="/field-pack/print/"', before_exp)
        self.assertIn("print cutouts to cut · hide · seek", before_exp)

    def test_featured_surfaces_do_not_link_legacy_destinations(self):
        for path in FEATURED_HTML:
            html = path.read_text(encoding="utf-8")
            for banned in LEGACY_HREFS:
                self.assertNotIn(banned, html, f"{path.name} still features {banned}")
        for js in (LANDING_MAP, LANDING_HOOK):
            text = js.read_text(encoding="utf-8")
            self.assertNotIn("/field-pack/app.html", text, js.name)
            self.assertNotIn("/field-pack/parks/", text, js.name)
            self.assertNotIn("/field-pack/places/", text, js.name)
            self.assertNotIn("/field-pack/virtual-zoo/", text, js.name)
            self.assertNotIn(".appHref", text, js.name)

    def test_shell_more_is_four_doors_only(self):
        for path in SHELL_HTML:
            html = path.read_text(encoding="utf-8")
            items = _menu_items(html, "shell-menu") if 'id="shell-menu"' in html else _menu_items(html, "start-menu")
            if path == START:
                self.assertEqual(items[:4], list(PRIMARY_MENU), path.name)
                self.assertEqual(items[4], ("/field-pack/print/", "Print cutouts"))
            else:
                self.assertEqual(
                    [(href, label) for href, label in items],
                    list(PRIMARY_MENU),
                    path.name,
                )
            self.assertNotIn('href="/dinner"', html, path.name)

    def test_cards_hub_keeps_primary_filters_and_experimental_museum(self):
        cards = CARDS.read_text(encoding="utf-8")
        primary, experimental = cards.split('id="cards-attractions"', 1)
        self.assertIn('data-card-filter="wildlife"', primary)
        self.assertIn('data-card-filter="sealife"', primary)
        self.assertIn('data-card-filter="parks"', primary)
        self.assertNotIn('data-card-filter="attractions"', cards)
        self.assertNotIn('data-card-id="sci-dinosaur"', primary)
        self.assertIn("Museum &amp; science cards", experimental)
        self.assertIn("Experimental · Quiet", experimental)
        self.assertIn('data-card-id="sci-dinosaur"', experimental)
        self.assertIn('id="cards-accordion"', cards)
        self.assertIn('data-card-accordion="wildlife" open', cards)
        self.assertIn(">All cards</button>", cards)
        about = ABOUT.read_text(encoding="utf-8")
        exp = about.split('id="experimental"', 1)[1]
        self.assertIn('href="/field-pack/cards/#cards-attractions"', exp)
        self.assertIn('href="/dinner"', exp)

    def test_virtual_zoo_stays_301_alias_not_a_featured_href(self):
        self.assertEqual(_get("/field-pack/virtual-zoo/")._code, 301)
        self.assertEqual(_get("/field-pack/virtual-zoo/")._headers.get("Location"), VFT_PATH)
        start = START.read_text(encoding="utf-8")
        self.assertNotIn('href="/field-pack/virtual-zoo/', start)
        self.assertNotIn('href="/virtual-zoo/', start)
        gen = GENERATOR.read_text(encoding="utf-8")
        self.assertIn('NAV_CARDS_LABEL = "Cards"', gen)
        self.assertIn('NAV_WATCH_LABEL = "Watch Live"', gen)
        self.assertIn('NAV_PLACES_LABEL = "Places"', gen)
        self.assertIn('NAV_ABOUT_HREF = "/about/"', gen)
        self.assertIn("No Dinner, no print", gen)

    def test_places_legacy_files_stay_301_unlinked(self):
        h = _get("/field-pack/places/dallas-zoo.html")
        self.assertEqual(h._code, 301)
        self.assertEqual(h._headers.get("Location"), "/field-pack/dallas-zoo/")
        self.assertTrue((FP / "places" / "dallas-zoo.html").is_file())
        for path in FEATURED_HTML:
            html = path.read_text(encoding="utf-8")
            self.assertNotIn("/field-pack/places/", html, path.name)


if __name__ == "__main__":
    unittest.main()
