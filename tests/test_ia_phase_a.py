"""Phase A IA: one Watch Live home, named print path, parks/app.html aliases."""

from __future__ import annotations

import unittest
from pathlib import Path

from busyparent_agent.url_aliases import (
    CARD_SLUG_ALIASES,
    NATIONAL_PARKS_PATH,
    PATH_REDIRECTS,
    PLACES_PATH,
    PRINT_PATH,
    PRINT_TARGET,
    VFT_PATH,
    card_alias_redirects,
    redirect_location,
)
from busyparent_agent.web import CARD_ALIAS_REDIRECTS, WebHandler


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
START = REPO / "static" / "start" / "index.html"
ABOUT = REPO / "static" / "about" / "index.html"
LANDING = FP / "index.html"
CARDS = FP / "cards" / "index.html"
VFT = FP / "virtual-field-trip" / "index.html"


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


def _head(path: str) -> FakeHandler:
    h = FakeHandler(path)
    h.do_HEAD()
    return h


class IaPhaseATests(unittest.TestCase):
    def test_shared_table_matches_web_export(self):
        self.assertEqual(CARD_ALIAS_REDIRECTS, card_alias_redirects())
        self.assertIn("giraffe", CARD_SLUG_ALIASES)
        self.assertEqual(CARD_SLUG_ALIASES["giraffe"], "reticulated-giraffe")
        self.assertEqual(CARD_SLUG_ALIASES["panda"], "giant-panda")
        self.assertEqual(CARD_SLUG_ALIASES["sea-star"], "starfish")
        self.assertNotIn("okapi", CARD_SLUG_ALIASES)

    def test_virtual_zoo_301_to_vft_preserves_query(self):
        for path in ("/field-pack/virtual-zoo", "/field-pack/virtual-zoo/"):
            h = _get(path)
            self.assertEqual(h._code, 301, path)
            self.assertEqual(h._headers.get("Location"), VFT_PATH, path)
            self.assertEqual(_head(path)._code, 301, path)
        q = _get("/field-pack/virtual-zoo/?from=card")
        self.assertEqual(q._code, 301)
        self.assertEqual(q._headers.get("Location"), VFT_PATH + "?from=card")
        print_q = _get("/field-pack/virtual-zoo/?print=1")
        self.assertEqual(print_q._code, 301)
        self.assertEqual(print_q._headers.get("Location"), PRINT_TARGET)
        stub = (FP / "virtual-zoo" / "index.html").read_text(encoding="utf-8")
        self.assertIn('content="0;url=/field-pack/virtual-field-trip/"', stub)
        self.assertNotIn("data-virtual-venue", stub)

    def test_print_path_301s_to_vft_print_mode(self):
        self.assertEqual(redirect_location("/field-pack/print/"), PRINT_TARGET)
        for path in ("/field-pack/print", "/field-pack/print/"):
            h = _get(path)
            self.assertEqual(h._code, 301, path)
            self.assertEqual(h._headers.get("Location"), PRINT_TARGET, path)
        stub = (FP / "print" / "index.html").read_text(encoding="utf-8")
        self.assertIn("print=1", stub)

    def test_parks_stub_301s_to_national_parks(self):
        for path in ("/field-pack/parks", "/field-pack/parks/"):
            h = _get(path)
            self.assertEqual(h._code, 301, path)
            self.assertEqual(h._headers.get("Location"), NATIONAL_PARKS_PATH, path)
        stub = (FP / "parks" / "index.html").read_text(encoding="utf-8")
        self.assertIn(NATIONAL_PARKS_PATH, stub)
        self.assertNotIn("card-page", stub)

    def test_app_html_301s_to_places_and_stays_unlisted(self):
        h = _get("/field-pack/app.html")
        self.assertEqual(h._code, 301)
        self.assertEqual(h._headers.get("Location"), PLACES_PATH)
        self.assertEqual(_head("/field-pack/app.html")._code, 301)
        for html in (
            START.read_text(encoding="utf-8"),
            ABOUT.read_text(encoding="utf-8"),
            LANDING.read_text(encoding="utf-8"),
            CARDS.read_text(encoding="utf-8"),
            VFT.read_text(encoding="utf-8"),
        ):
            self.assertNotIn("/field-pack/app.html", html)

    def test_short_card_slugs_301(self):
        for src, dest in CARD_SLUG_ALIASES.items():
            dest_url = f"/field-pack/cards/{dest}/"
            for path in (f"/field-pack/cards/{src}", f"/field-pack/cards/{src}/"):
                h = _get(path)
                self.assertEqual(h._code, 301, path)
                self.assertEqual(h._headers.get("Location"), dest_url, path)
            stub = (FP / "cards" / src / "index.html").read_text(encoding="utf-8")
            self.assertIn(dest_url, stub)
            self.assertNotIn("card-page", stub)

    def test_start_about_cards_use_canonical_doors(self):
        start = START.read_text(encoding="utf-8")
        about = ABOUT.read_text(encoding="utf-8")
        cards = CARDS.read_text(encoding="utf-8")
        self.assertIn('href="/field-pack/virtual-field-trip/"', start)
        self.assertIn('href="/field-pack/print/"', start)
        self.assertNotIn("/field-pack/virtual-zoo/", start)
        self.assertIn('href="/field-pack/virtual-field-trip/"', about)
        self.assertIn('href="/field-pack/print/"', about)
        self.assertIn('href="/start/"', about)
        self.assertIn('href="/field-pack/cards/"', about)
        self.assertIn('href="/field-pack/"', about)
        self.assertIn(">Cards</a>", about)
        self.assertIn(">Watch Live</a>", about)
        self.assertIn(">Places</a>", about)
        self.assertIn('href="/field-pack/print/"', cards)
        self.assertNotIn("/field-pack/virtual-zoo/", cards)

    def test_about_experimental_wording_and_doors(self):
        about = ABOUT.read_text(encoding="utf-8")
        before_exp, rest = about.split('id="experimental"', 1)
        exp = rest.split("</section>", 1)[0]
        self.assertIn("How it fits together", before_exp)
        self.assertIn(">Cards</a>", before_exp)
        self.assertIn(">Watch Live</a>", before_exp)
        self.assertIn(">Places</a>", before_exp)
        self.assertIn("Those three doors start from", before_exp)
        self.assertIn("print cutouts to hide", before_exp)
        self.assertIn("Experimental", exp)
        self.assertIn(
            "Not part of the three doors — quiet extras if you already know you want them.",
            exp,
        )
        self.assertIn("Museum stops &amp; extras", exp)
        self.assertIn('href="/field-pack/cards/#cards-attractions"', exp)
        self.assertIn('href="/dinner"', exp)
        self.assertIn("tonight", exp)
        self.assertNotIn("national-parks", exp)
        self.assertNotIn("Yellowstone", exp)
        self.assertNotIn('href="/field-pack/parks/"', exp)
        self.assertNotIn("Dinner", before_exp)
        self.assertNotIn('href="/dinner"', before_exp)

    def test_museum_sci_hidden_from_primary_cards_hub(self):
        cards = CARDS.read_text(encoding="utf-8")
        start = START.read_text(encoding="utf-8")
        landing = LANDING.read_text(encoding="utf-8")
        primary, experimental = cards.split('id="cards-attractions"', 1)
        self.assertNotIn('data-card-filter="attractions"', cards)
        self.assertIn('data-card-filter="wildlife"', primary)
        self.assertIn('data-card-filter="sealife"', primary)
        self.assertNotIn('data-card-filter="parks"', cards)
        self.assertIn("42 cards", primary)
        self.assertIn("All cards", primary)
        self.assertNotIn("All 42 cards", primary)
        self.assertIn('data-card-id="american-alligator"', primary)
        self.assertIn('data-card-id="american-bison"', primary)
        self.assertIn('data-card-id="elk"', primary)
        self.assertNotIn('data-card-group="parks"', primary)
        self.assertIn('data-card-group="wildlife"', primary)
        self.assertNotIn('data-card-id="sci-dinosaur"', primary)
        self.assertNotIn('data-card-id="cm-art-lab"', primary)
        self.assertIn("Experimental", experimental)
        self.assertIn("Museum stops &amp; extras", experimental)
        self.assertNotIn("Museum &amp; science cards", experimental)
        self.assertIn('data-card-id="sci-dinosaur"', experimental)
        self.assertIn('data-card-id="cm-art-lab"', experimental)
        self.assertIn('data-card-group="attractions"', experimental)
        self.assertTrue((FP / "cards" / "sci-dinosaur" / "index.html").is_file())
        self.assertTrue((FP / "cards" / "cm-art-lab" / "index.html").is_file())
        self.assertNotIn("/field-pack/cards/sci-", start)
        self.assertNotIn("/field-pack/cards/cm-", start)
        self.assertNotIn("sci-dinosaur", start)
        self.assertIn('href="/field-pack/national-parks/"', landing)
        self.assertNotIn('href="/field-pack/parks/"', landing)

    def test_fp_chrome_does_not_promote_dinner(self):
        for path in (LANDING, CARDS, VFT, START):
            html = path.read_text(encoding="utf-8")
            self.assertNotIn('href="/dinner"', html, path.name)
            self.assertNotIn("Dinner<small>", html, path.name)
        about = ABOUT.read_text(encoding="utf-8")
        intro = about.split('id="experimental"', 1)[0]
        self.assertNotIn('href="/dinner"', intro)
        self.assertIn('href="/dinner"', about.split('id="experimental"', 1)[1])

    def test_zoo_watch_live_uses_vft_tab(self):
        lion = (FP / "cards" / "african-lion" / "index.html").read_text(encoding="utf-8")
        manta = (FP / "cards" / "manta-ray" / "index.html").read_text(encoding="utf-8")
        whale = (FP / "cards" / "whale-shark" / "index.html").read_text(encoding="utf-8")
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=zoo&from=card#habitat=african-lion",
            lion,
        )
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&from=card#habitat=manta-ray",
            manta.replace("&amp;", "&"),
        )
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&from=card#habitat=whale-shark",
            whale.replace("&amp;", "&"),
        )
        self.assertNotIn("/field-pack/virtual-zoo/", lion)
        self.assertNotIn("/field-pack/virtual-zoo/", manta)
        self.assertNotIn("/field-pack/virtual-zoo/", whale)

    def test_path_redirect_table_covers_phase_a(self):
        self.assertEqual(PATH_REDIRECTS["/field-pack/virtual-zoo/"], VFT_PATH)
        self.assertEqual(PATH_REDIRECTS["/field-pack/parks/"], NATIONAL_PARKS_PATH)
        self.assertEqual(PATH_REDIRECTS["/field-pack/app.html"], PLACES_PATH)
        self.assertEqual(PATH_REDIRECTS[PRINT_PATH.rstrip("/") + "/"], PRINT_TARGET)


if __name__ == "__main__":
    unittest.main()
