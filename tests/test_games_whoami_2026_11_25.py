"""Who am I? animal clues (2026-11-25)."""
from __future__ import annotations

import json
import re
import unicodedata
import unittest
from pathlib import Path

from busyparent_agent.web import WebHandler

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / "static" / "games"
DATA = GAMES / "data" / "whoami-v1.json"
CARDS = ROOT / "static" / "field-pack" / "cards"


def _strip(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _name_forms(name: str) -> set[str]:
    forms = {_strip(name).lower()}
    for tok in re.findall(r"[A-Za-z]{3,}", _strip(name)):
        tl = tok.lower()
        forms.add(tl)
        if not tl.endswith("s"):
            forms.add(tl + "s")
        forms.add(tl + "'s")
        forms.add(tl + "’s")
    return forms


def _contains_name(text: str, forms: set[str]) -> bool:
    low = _strip(text).lower()
    for form in forms:
        if re.search(r"(?<![a-z])" + re.escape(form) + r"(?![a-z])", low):
            return True
    return False


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


class WhoAmIPages(unittest.TestCase):
    def test_page_and_assets_exist(self):
        self.assertTrue((GAMES / "who-am-i" / "index.html").is_file())
        self.assertTrue((GAMES / "css" / "whoami-v1.css").is_file())
        self.assertTrue((GAMES / "js" / "whoami-v1.js").is_file())
        self.assertTrue(DATA.is_file())

    def test_no_signup_and_six_rounds(self):
        html = (GAMES / "who-am-i" / "index.html").read_text(encoding="utf-8")
        self.assertNotRegex(html, r"type=[\"']password")
        self.assertNotIn("/api/newsletter", html)
        self.assertIn("/games/css/whoami-v1.css?v=1", html)
        self.assertIn("/games/js/whoami-v1.js?v=1", html)
        self.assertNotIn("fetchpriority", html)
        self.assertIn("Play 6 rounds", html)
        self.assertIn("Play again", html)
        css = (GAMES / "css" / "whoami-v1.css").read_text(encoding="utf-8")
        self.assertIn("min-height:var(--tap)", css)
        self.assertIn("prefers-reduced-motion", css)
        js = (GAMES / "js" / "whoami-v1.js").read_text(encoding="utf-8")
        self.assertIn("ROUNDS = 6", js)
        self.assertIn('gtag("event", "game_complete"', js)
        self.assertIn("who_am_i", js)
        self.assertNotIn("email", js)

    def test_clues_come_from_card_copy_and_omit_the_name(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["animals"]), 20)
        self.assertIn("dallas-zoo", data["places"])
        for animal in data["animals"]:
            clues = animal["clues"]
            self.assertGreaterEqual(len(clues), 2, animal["id"])
            self.assertLessEqual(len(clues), 3, animal["id"])
            html = (CARDS / animal["id"] / "index.html").read_text(encoding="utf-8")
            plain = re.sub(r"<[^>]+>", " ", html)
            forms = _name_forms(animal["name"])
            for clue in clues:
                self.assertIn(clue.rstrip(".!?"), re.sub(r"\s+", " ", plain), animal["id"])
                self.assertFalse(_contains_name(clue, forms), f"{animal['id']}: {clue}")

    def test_hub_links_who_am_i_and_has_no_coming_next(self):
        html = (GAMES / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/games/who-am-i/"', html)
        self.assertNotIn("Coming next", html)
        self.assertNotIn("Silhouette guess", html)
        self.assertNotIn("Habitat sort", html)
        self.assertNotIn("/games/silhouette/", html)

    def test_handler_serves_page_and_slashless_301(self):
        page = FakeHandler("/games/who-am-i/")
        page.do_GET()
        self.assertEqual(page._code, 200)
        self.assertIn(b"Who am I?", page.wfile.getvalue())
        data = FakeHandler("/games/data/whoami-v1.json")
        data.do_GET()
        self.assertEqual(data._code, 200)
        slash = FakeHandler("/games/who-am-i")
        slash.do_GET()
        self.assertEqual(slash._code, 301)
        self.assertTrue(slash._headers.get("Location", "").endswith("/games/who-am-i/"))
        head = FakeHandler("/games/who-am-i/")
        head.do_HEAD()
        self.assertEqual(head._code, 200)


if __name__ == "__main__":
    unittest.main()
