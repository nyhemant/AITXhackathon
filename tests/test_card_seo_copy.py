"""2026-10-28: card titles/descriptions fit search snippets and never collide.

Fails the build if any card page description is over 155 characters, if any page title
on the site is duplicated, or if an animal / sea-life card drifts from the
"<Animal> Facts for Kids" pattern (og/twitter tags must match the title/description).
"""

from __future__ import annotations

import html
import re
import sys
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATIC = REPO / "static"
CARDS = STATIC / "field-pack" / "cards"
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import CARD_DESC_MAX, animal_card_seo, title_case_name  # noqa: E402

ANIMAL_KINDS = ("animal", "sea_life")


def _meta(h: str, attr: str, key: str) -> str | None:
    m = re.search(rf'<meta {attr}="{re.escape(key)}" content="([^"]*)"', h)
    return html.unescape(m.group(1)) if m else None


def _title(h: str) -> str:
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    return html.unescape(m.group(1).strip()) if m else ""


def _card_pages() -> dict[str, str]:
    return {
        p.parent.name: p.read_text(encoding="utf-8")
        for p in sorted(CARDS.glob("*/index.html"))
    }


def _animal_ids() -> set[str]:
    ids = set()
    for cid, h in _card_pages().items():
        if 'data-study-id="' in h and "Facts for Kids" in _title(h):
            ids.add(cid)
    return ids


class CardSeoCopyTest(unittest.TestCase):
    def test_every_card_description_fits_snippet(self):
        pages = _card_pages()
        self.assertGreaterEqual(len(pages), 50)
        too_long = {}
        for cid, h in pages.items():
            d = _meta(h, "name", "description")
            self.assertTrue(d, cid)
            if len(d) > CARD_DESC_MAX:
                too_long[cid] = len(d)
        self.assertEqual(too_long, {}, f"card descriptions over {CARD_DESC_MAX} chars")

    def test_no_duplicate_titles_on_site(self):
        sitemap = (STATIC / "sitemap.xml").read_text(encoding="utf-8")
        titles = []
        for loc in re.findall(r"<loc>https://kidzookit\.com(/[^<]*)</loc>", sitemap):
            f = STATIC / loc.strip("/") / "index.html" if loc.endswith("/") else STATIC / loc.lstrip("/")
            if f.is_file():
                titles.append(_title(f.read_text(encoding="utf-8")))
        self.assertGreater(len(titles), 250)
        dups = {t: n for t, n in Counter(titles).items() if n > 1}
        self.assertEqual(dups, {}, "duplicate <title> across sitemap pages")

    def test_animal_cards_use_facts_for_kids_pattern(self):
        pages = _card_pages()
        ids = _animal_ids()
        self.assertEqual(len(ids), 42, sorted(ids))
        for cid in ids:
            h = pages[cid]
            t = _title(h)
            d = _meta(h, "name", "description")
            self.assertTrue(t.endswith(" | KidZooKit"), cid)
            self.assertLessEqual(len(t), 60, cid)
            self.assertNotIn("Photo", t, cid)
            self.assertNotIn("free", (t + " " + d).lower(), cid)
            self.assertIn("quiz", d.lower(), cid)
            self.assertEqual(_meta(h, "property", "og:title"), t, cid)
            self.assertEqual(_meta(h, "name", "twitter:title"), t, cid)
            self.assertEqual(_meta(h, "property", "og:description"), d, cid)
            self.assertEqual(_meta(h, "name", "twitter:description"), d, cid)

    def test_generator_copy_is_built_from_card_text_only(self):
        long_name = "Western lowland gorilla"
        blurb = "Strong gentle ape in family groups."
        c = animal_card_seo(long_name, blurb)
        self.assertTrue(c["description"].startswith(blurb), c)
        self.assertLessEqual(len(c["title"]), 60)
        self.assertLessEqual(len(c["description"]), CARD_DESC_MAX)
        huge = animal_card_seo("Asian small-clawed otter", "x" * 140)
        self.assertLessEqual(len(huge["description"]), CARD_DESC_MAX)
        self.assertEqual(title_case_name("Two-toed sloth"), "Two-Toed Sloth")
        no_levels = animal_card_seo("Zebra", "Striped.", quiz_levels=1)
        self.assertNotIn("3 levels", no_levels["description"])


if __name__ == "__main__":
    unittest.main()
