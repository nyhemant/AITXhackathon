"""Animal word search (2026-11-25)."""
from __future__ import annotations

import json
import re
import unicodedata
import unittest
from pathlib import Path

from busyparent_agent.web import WebHandler

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / "static" / "games"
DATA = GAMES / "data" / "memory-v1.json"
CARDS = ROOT / "static" / "field-pack" / "cards"

MOD = set(
    "AFRICAN AMERICAN ASIAN CARIBBEAN GIANT RED SEA NILE RING TAILED TWO TOED "
    "WESTERN LOWLAND SUMATRAN RETICULATED GALAPAGOS SMALL CLAWED RIVER LAKE FRESHWATER".split()
)


def _strip(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _tokens(name: str) -> list[str]:
    return re.findall(r"[A-Z]+", _strip(name).upper())


def grid_word(name: str, max_len: int) -> str | None:
    compact = "".join(_tokens(name))
    if 3 <= len(compact) <= max_len:
        return compact
    animal = [t for t in _tokens(name) if t not in MOD and 3 <= len(t) <= max_len]
    if not animal:
        return None
    last = animal[-1]
    if len(last) >= 4:
        return last
    return sorted(animal, key=len, reverse=True)[0]


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


class WordSearchPages(unittest.TestCase):
    def test_page_and_assets_exist(self):
        self.assertTrue((GAMES / "word-search" / "index.html").is_file())
        self.assertTrue((GAMES / "css" / "wordsearch-v1.css").is_file())
        self.assertTrue((GAMES / "js" / "wordsearch-v1.js").is_file())

    def test_no_signup_and_versioned_assets(self):
        html = (GAMES / "word-search" / "index.html").read_text(encoding="utf-8")
        self.assertNotRegex(html, r"type=[\"']password")
        self.assertNotIn("/api/newsletter", html)
        self.assertIn("/games/css/wordsearch-v1.css?v=1", html)
        self.assertIn("/games/js/wordsearch-v1.js?v=2", html)
        self.assertNotIn("fetchpriority", html)
        self.assertIn("Easy · 6×6", html)
        self.assertIn("A bit harder · 8×8", html)
        self.assertIn("Play again", html)

    def test_swipe_and_reduced_motion(self):
        css = (GAMES / "css" / "wordsearch-v1.css").read_text(encoding="utf-8")
        self.assertIn("touch-action:none", css)
        self.assertIn("min-height:var(--tap)", css)
        self.assertIn("prefers-reduced-motion", css)
        js = (GAMES / "js" / "wordsearch-v1.js").read_text(encoding="utf-8")
        self.assertIn("pointerdown", js)
        self.assertIn("Now tap the last letter", js)
        self.assertIn("tiny pointer wobble still counts as a tap", js)
        self.assertIn('gtag("event", "game_complete"', js)
        self.assertIn("word_search", js)
        self.assertNotIn("email", js)

    def test_grid_words_come_from_official_names(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        sample = {a["id"]: a["name"] for a in data["animals"]}
        self.assertEqual(grid_word("African lion", 6), "LION")
        self.assertEqual(grid_word("Zebra", 6), "ZEBRA")
        self.assertEqual(grid_word("Reticulated giraffe", 8), "GIRAFFE")
        self.assertEqual(grid_word("Manta ray", 8), "MANTARAY")
        self.assertIsNone(grid_word("American alligator", 8))
        for a in data["animals"]:
            for size in (6, 8):
                word = grid_word(a["name"], size)
                if not word:
                    continue
                letters = "".join(_tokens(a["name"]))
                self.assertIn(word, letters, a["name"])
        dallas = data["places"]["dallas-zoo"]["ids"]
        easy = [grid_word(sample[i], 6) for i in dallas if i in sample]
        easy = [w for w in easy if w]
        self.assertGreaterEqual(len(set(easy)), 4)

    def test_hub_links_word_search_and_has_no_coming_next(self):
        html = (GAMES / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/games/word-search/"', html)
        self.assertNotIn("Coming next", html)

    def test_handler_serves_page_and_slashless_301(self):
        page = FakeHandler("/games/word-search/")
        page.do_GET()
        self.assertEqual(page._code, 200)
        self.assertIn(b"Animal word search", page.wfile.getvalue())
        slash = FakeHandler("/games/word-search")
        slash.do_GET()
        self.assertEqual(slash._code, 301)
        self.assertTrue(slash._headers.get("Location", "").endswith("/games/word-search/"))
        css = FakeHandler("/games/css/wordsearch-v1.css")
        css.do_GET()
        self.assertEqual(css._code, 200)
        head = FakeHandler("/games/word-search/")
        head.do_HEAD()
        self.assertEqual(head._code, 200)


if __name__ == "__main__":
    unittest.main()
