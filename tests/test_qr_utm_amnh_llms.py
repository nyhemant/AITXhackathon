"""QR utm backtick normalization, /start/ museum links, and llms.txt."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from tests.test_start_landing import _get, _head

REPO = Path(__file__).resolve().parents[1]
STATIC = REPO / "static"
TICK = chr(96)
TEXT_SUFFIXES = {".py", ".js", ".html", ".css", ".md", ".txt", ".json", ".svg", ".xml"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
ANSWER = (
    "KidZooKit is a printable zoo, aquarium, and museum field trip kit "
    "and animal study cards with quizzes, for kids about 4–8."
)
KEY_LLMS = (
    "https://kidzookit.com/start/",
    "https://kidzookit.com/field-pack/",
    "https://kidzookit.com/printables/",
    "https://kidzookit.com/field-pack/cards/",
    "https://kidzookit.com/printables/scavenger-hunt/",
    "https://kidzookit.com/field-pack/amnh/",
)
UTM_VALUE = re.compile(r"utm_[A-Za-z0-9_]+=([^&\s\"'<>]*)")


def _bad_source(extra: str = "") -> str:
    """utm_source value qr plus a trailing backtick, built without that byte in source."""
    return "utm_source=qr" + TICK + extra


class QrUtmNormalizeTests(unittest.TestCase):
    def test_backtick_source_becomes_printable_qr(self):
        src = "/start/?" + _bad_source("&utm_campaign=carpool")
        for fn in (_get, _head):
            h = fn(src)
            self.assertEqual(h._code, 301, fn.__name__)
            self.assertEqual(
                h._headers.get("Location"),
                "/start/?utm_source=printable&utm_medium=qr&utm_campaign=carpool",
            )

    def test_percent_encoded_backtick_and_other_params(self):
        h = _get("/field-pack/zoos/?utm_source=qr" + "%60" + "&utm_content=sheet&utm_campaign=scavenger-hunt")
        self.assertEqual(h._code, 301)
        self.assertEqual(
            h._headers.get("Location"),
            "/field-pack/zoos/?utm_source=printable&utm_medium=qr&utm_content=sheet&utm_campaign=scavenger-hunt",
        )

    def test_existing_medium_is_replaced_when_source_was_malformed(self):
        h = _get("/printables/?" + _bad_source("&utm_medium=print"))
        self.assertEqual(h._code, 301)
        self.assertEqual(
            h._headers.get("Location"),
            "/printables/?utm_source=printable&utm_medium=qr",
        )

    def test_backtick_on_another_utm_is_stripped_without_rewriting_source(self):
        h = _get("/start/?utm_source=printable&utm_medium=qr&utm_campaign=carpool" + TICK)
        self.assertEqual(h._code, 301)
        self.assertEqual(
            h._headers.get("Location"),
            "/start/?utm_source=printable&utm_medium=qr&utm_campaign=carpool",
        )

    def test_clean_printable_qr_is_not_redirected(self):
        h = _get("/start/?utm_source=printable&utm_medium=qr&utm_campaign=carpool")
        self.assertEqual(h._code, 200)

    def test_plain_utm_source_qr_is_not_rewritten(self):
        h = _get("/?utm_source=qr&utm_medium=print")
        self.assertEqual(h._code, 301)
        self.assertEqual(h._headers.get("Location"), "/start/?utm_source=qr&utm_medium=print")

    def test_no_backtick_in_utm_values_in_repo(self):
        bad = []
        for path in REPO.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in UTM_VALUE.finditer(text):
                value = match.group(1)
                if TICK in value or "%60" in value.lower():
                    bad.append(f"{path.relative_to(REPO)}:{value}")
        self.assertEqual(bad, [])


class AmnhAndLlmsTests(unittest.TestCase):
    def test_start_links_amnh_and_other_museums(self):
        html = (STATIC / "start" / "index.html").read_text(encoding="utf-8")
        block = re.search(r"<!-- kz-mesh:start-trips -->(.*)<!-- /kz-mesh:start-trips -->", html, re.S)
        self.assertIsNotNone(block)
        body = block.group(1)
        self.assertIn('href="/field-pack/amnh/"', body)
        self.assertIn("American Museum of Natural History", body)
        self.assertIn('href="/field-pack/field-museum/"', body)
        self.assertIn('href="/field-pack/smithsonian-natural-history/"', body)
        self.assertNotIn("Arya", html[html.find("start-popular-trips"): html.find("start-popular-trips") + 800])

    def test_science_cards_that_list_amnh_link_it_up_top(self):
        for slug in ("sci-dinosaur", "sci-hands-on", "sci-mammal-hall", "sci-planet"):
            html = (STATIC / "field-pack" / "cards" / slug / "index.html").read_text(encoding="utf-8")
            where = html.split("<!-- kz-mesh:where -->", 1)[1].split("<!-- /kz-mesh:where -->", 1)[0]
            self.assertIn('href="/field-pack/amnh/"', where, slug)
            actions = html.split('class="card-page-actions-primary"', 1)[1].split("</div>", 1)[0]
            self.assertIn('href="/field-pack/amnh/"', actions, slug)

    def test_plain_answer_opens_chatgpt_landing_pages(self):
        pages = {
            "start/index.html": "<h1",
            "field-pack/index.html": 'id="pitch-heading"',
            "printables/index.html": "<h1>",
            "field-pack/cards/index.html": 'id="cards-play-heading"',
            "printables/scavenger-hunt/index.html": "<h1>",
        }
        for rel, heading in pages.items():
            html = (STATIC / rel).read_text(encoding="utf-8")
            self.assertIn(heading, html, rel)
            self.assertIn(ANSWER, html, rel)
            self.assertLess(html.index(heading), html.index(ANSWER), rel)
            self.assertNotIn(" we ", ANSWER.lower())
            self.assertNotIn(" our ", ANSWER.lower())

    def test_llms_txt_lists_key_pages_and_is_plain_text(self):
        text = (STATIC / "llms.txt").read_text(encoding="utf-8")
        for url in KEY_LLMS:
            self.assertIn(url, text)
        robots = (STATIC / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Allow: /llms.txt", robots)
        self.assertNotIn("Disallow: /llms.txt", robots)
        h = _get("/llms.txt")
        self.assertEqual(h._code, 200)
        self.assertTrue(h._headers.get("Content-Type", "").startswith("text/plain"))


if __name__ == "__main__":
    unittest.main()
