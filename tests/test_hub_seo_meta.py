"""2026-10-28 search-visibility guard for hub pages: titles, social tags, JSON-LD."""
from __future__ import annotations

import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"


def _read(rel: str) -> str:
    return (STATIC / rel).read_text(encoding="utf-8")


def _meta(h: str, key: str) -> str | None:
    m = re.search(rf'<meta (?:name|property)="{re.escape(key)}" content="([^"]*)"', h)
    return html.unescape(m.group(1)) if m else None


def _title(h: str) -> str:
    return html.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1))


def _ld_blocks(h: str) -> list:
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)]


HUBS = [
    "start/index.html",
    "field-pack/cards/index.html",
    "field-pack/zoos/index.html",
    "field-pack/aquariums/index.html",
    "field-pack/museums/index.html",
    "field-pack/national-parks/index.html",
    "printables/scavenger-hunt/index.html",
    "printables/animal-bingo/index.html",
    "printables/zoo-day-journal/index.html",
    "privacy/index.html",
]


class HubSeoMeta(unittest.TestCase):
    def test_social_tags_present_and_in_sync(self):
        for rel in HUBS:
            h = _read(rel)
            with self.subTest(page=rel):
                self.assertIsNotNone(_meta(h, "og:image"))
                # Printable sheets keep a shorter social title on purpose; twitter mirrors og.
                self.assertTrue(_meta(h, "og:title"))
                self.assertEqual(_meta(h, "twitter:title"), _meta(h, "og:title"))
                self.assertEqual(_meta(h, "og:description"), _meta(h, "description"))
                self.assertEqual(_meta(h, "twitter:description"), _meta(h, "description"))
                self.assertIsNotNone(_meta(h, "twitter:card"))

    def test_hub_titles_descriptive_and_short(self):
        for rel in ["start/index.html", "field-pack/museums/index.html"]:
            t = _title(_read(rel))
            with self.subTest(page=rel):
                self.assertLessEqual(len(t), 60)
                self.assertIn("for Kids", t)
                self.assertTrue(t.endswith("| KidZooKit"))

    def test_start_keeps_project_wordmark(self):
        h = _read("start/index.html")
        self.assertIn('<p class="start-wordmark">Arya’s Wildlife Project</p>', h)

    def test_start_website_org_json_ld(self):
        blocks = _ld_blocks(_read("start/index.html"))
        types = {n["@type"] for b in blocks for n in b.get("@graph", [b])}
        self.assertIn("WebSite", types)
        self.assertIn("Organization", types)

    def test_cards_hub_item_list_matches_links(self):
        h = _read("field-pack/cards/index.html")
        blocks = [b for b in _ld_blocks(h) if b.get("@type") == "CollectionPage"]
        self.assertEqual(len(blocks), 1)
        items = blocks[0]["mainEntity"]["itemListElement"]
        links = set(re.findall(r'<a class="cards-hub-link" href="(/field-pack/cards/[a-z0-9-]+/)"', h))
        self.assertEqual({i["url"].replace("https://kidzookit.com", "") for i in items}, links)
        self.assertEqual(blocks[0]["mainEntity"]["numberOfItems"], len(items))

    def test_all_hub_json_ld_parses(self):
        for rel in HUBS:
            with self.subTest(page=rel):
                for b in _ld_blocks(_read(rel)):
                    self.assertIn("@context", b)

    def test_printable_descriptions(self):
        want = {
            "printables/scavenger-hunt/index.html": "zoo scavenger hunt printable",
            "printables/animal-bingo/index.html": "animal bingo printable",
            "printables/zoo-day-journal/index.html": "zoo field trip worksheet",
        }
        for rel, phrase in want.items():
            d = _meta(_read(rel), "description")
            with self.subTest(page=rel):
                self.assertLessEqual(len(d), 155)
                self.assertIn(phrase, d.lower())
                self.assertNotIn("free", d.lower())


if __name__ == "__main__":
    unittest.main()
