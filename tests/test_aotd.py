"""Animal of the day tile on the cards hub (static fallback + day rotation)."""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HUB = REPO / "static" / "field-pack" / "cards" / "index.html"
JS = REPO / "static" / "field-pack" / "js" / "aotd.js"
PHOTOS = REPO / "static" / "field-pack" / "photos"
CARDS = REPO / "static" / "field-pack" / "cards"


class AnimalOfTheDayTests(unittest.TestCase):
    def test_cards_hub_fallback_tile_links_with_aotd_hash(self):
        html = HUB.read_text(encoding="utf-8")
        tile = re.search(r'<section class="aotd"[\s\S]*?</section>', html)
        self.assertIsNotNone(tile, "cards hub is missing the Animal of the day tile")
        block = tile.group(0)
        self.assertIn("Animal of the day", block)
        self.assertNotRegex(block, r"\bFree\b")
        href = re.search(r'href="(/field-pack/cards/([a-z0-9-]+)/#from=aotd)"', block)
        self.assertIsNotNone(href, block)
        cid = href.group(2)
        self.assertTrue((CARDS / cid / "index.html").is_file(), cid)
        img = re.search(r"<img\b[^>]*class=\"aotd-photo\"[^>]*>", block)
        self.assertIsNotNone(img)
        tag = img.group(0)
        self.assertIn('width="', tag)
        self.assertIn('height="', tag)
        self.assertIn("-320-v1.webp", tag)
        self.assertTrue((PHOTOS / f"{cid}-320-v1.webp").is_file())
        self.assertIn('<script src="/field-pack/js/aotd.js?v=1" defer></script>', html)

    def test_script_lists_forty_two_existing_animals(self):
        js = JS.read_text(encoding="utf-8")
        ids = re.findall(r'\bid:"([a-z0-9-]+)"', js)
        self.assertEqual(len(ids), 42)
        self.assertEqual(len(set(ids)), 42)
        self.assertNotIn("Free", js)
        for cid in ids:
            self.assertTrue((CARDS / cid / "index.html").is_file(), cid)
            self.assertTrue((PHOTOS / f"{cid}-320-v1.webp").is_file(), cid)

    def test_generator_keeps_the_tile(self):
        src = (REPO / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        hub = src[src.index("def write_cards_hub(") : src.index("\ndef write_card_pages(")]
        self.assertIn("{aotd_tile_html()}", hub)
        self.assertIn("{AOTD_JS_TAG}", hub)
        self.assertIn("ensure_aotd_on_landing", src)
