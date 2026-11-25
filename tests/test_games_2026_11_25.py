"""Games hub + animal memory match (2026-11-25)."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from busyparent_agent.web import WebHandler

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / "static" / "games"
DATA = GAMES / "data" / "memory-v1.json"
CARDS = ROOT / "static" / "field-pack" / "cards"


class GamesPages(unittest.TestCase):
    def test_hub_and_memory_pages_exist(self):
        self.assertTrue((GAMES / "index.html").is_file())
        self.assertTrue((GAMES / "memory" / "index.html").is_file())
        self.assertTrue((GAMES / "css" / "games-v1.css").is_file())
        self.assertTrue((GAMES / "js" / "memory-v1.js").is_file())
        self.assertTrue(DATA.is_file())

    def test_no_signup_and_self_contained_assets(self):
        for rel in ("index.html", "memory/index.html"):
            html = (GAMES / rel).read_text(encoding="utf-8")
            self.assertNotRegex(html, r"type=[\"']password")
            self.assertNotIn("/api/newsletter", html)
            self.assertIn("/games/css/games-v1.css?v=1", html)
            self.assertNotIn("fetchpriority", html)

    def test_memory_has_modes_and_reduced_motion(self):
        html = (GAMES / "memory" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Easy · 6 pairs", html)
        self.assertIn("A bit harder · 8 pairs", html)
        self.assertIn("Play again", html)
        css = (GAMES / "css" / "games-v1.css").read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("min-height:var(--tap)", css)
        self.assertIn("--tap:3rem", css)
        js = (GAMES / "js" / "memory-v1.js").read_text(encoding="utf-8")
        self.assertIn('gtag("event", "game_complete"', js)
        self.assertIn("game_name", js)
        self.assertNotIn("email", js)

    def test_memory_facts_match_card_blurbs(self):
        data = json.loads(DATA.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(data["animals"]), 20)
        self.assertIn("dallas-zoo", data["places"])
        self.assertGreaterEqual(len(data["places"]["dallas-zoo"]["ids"]), 6)
        sample = {a["id"]: a for a in data["animals"]}
        for cid in ("african-lion", "reticulated-giraffe", "zebra"):
            self.assertIn(cid, sample)
            html = (CARDS / cid / "index.html").read_text(encoding="utf-8")
            m = re.search(r'class="card-page-blurb"[^>]*>(.*?)</p>', html, re.S)
            self.assertIsNotNone(m, cid)
            blurb = " ".join(re.sub(r"<[^>]+>", "", m.group(1)).split())
            self.assertEqual(sample[cid]["fact"], blurb)

    def test_start_has_a_games_link(self):
        html = (ROOT / "static" / "start" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/games/"', html)
        self.assertIn("Arya", html)
        self.assertIn("Wildlife Project", html)
        self.assertIn("Printable scavenger hunts for your next zoo, aquarium or museum trip", html)


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


class GamesHandler(unittest.TestCase):
    def test_hub_and_memory_are_200_slashless_301(self):
        hub = FakeHandler("/games/")
        hub.do_GET()
        self.assertEqual(hub._code, 200)
        body = hub.wfile.getvalue().decode("utf-8")
        self.assertIn("Games for a zoo day", body)
        self.assertIn("/games/memory/", body)
        mem = FakeHandler("/games/memory/")
        mem.do_GET()
        self.assertEqual(mem._code, 200)
        self.assertIn(b"Animal memory match", mem.wfile.getvalue())
        data = FakeHandler("/games/data/memory-v1.json")
        data.do_GET()
        self.assertEqual(data._code, 200)
        self.assertIn("application/json", data._headers.get("Content-Type", ""))
        slash = FakeHandler("/games")
        slash.do_GET()
        self.assertEqual(slash._code, 301)
        self.assertTrue(slash._headers.get("Location", "").endswith("/games/"))
        mem_slash = FakeHandler("/games/memory")
        mem_slash.do_GET()
        self.assertEqual(mem_slash._code, 301)
        self.assertTrue(mem_slash._headers.get("Location", "").endswith("/games/memory/"))
        head = FakeHandler("/games/")
        head.do_HEAD()
        self.assertEqual(head._code, 200)


if __name__ == "__main__":
    unittest.main()
