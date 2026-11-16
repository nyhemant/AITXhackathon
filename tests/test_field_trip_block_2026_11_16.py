"""Hogle Zoo school field-trip printables block (2026-11-16)."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from field_trip_blocks_v1 import FIELD_TRIP_BLOCKS, field_trip_block_html, with_field_trip_block  # noqa: E402
from scav_test_2026_11 import COMPARISON_SLUGS, TEST_SLUGS  # noqa: E402

FREE_RE = re.compile(r"\b(free|no-cost)\b", re.IGNORECASE)
WE_RE = re.compile(r"\b(we|our|us|We|Our|Us)\b")  # "US Letter" is fine


class FieldTripBlock(unittest.TestCase):
    def test_only_hogle_and_never_the_24(self):
        self.assertEqual(set(FIELD_TRIP_BLOCKS), {"hogle-zoo"})
        self.assertFalse(set(FIELD_TRIP_BLOCKS) & (TEST_SLUGS | COMPARISON_SLUGS))

    def test_hogle_page_has_block_once_after_hunt(self):
        page = (ROOT / "static/field-pack/hogle-zoo/index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('id="field-trip"'), 1)
        self.assertIn(field_trip_block_html("hogle-zoo").strip(), page)
        self.assertLess(page.find('class="seo-list-block seo-hunt-block"'), page.find('id="field-trip"'))
        self.assertLess(page.find('id="field-trip"'), page.find('id="explore-more"'))
        self.assertIn("Hogle Zoo field trip printables", page)
        self.assertIn('href="https://www.hoglezoo.org/field-trips/"', page)
        self.assertEqual(with_field_trip_block("hogle-zoo", page), page)

    def test_block_links_existing_pdfs_and_copy_rules(self):
        block = field_trip_block_html("hogle-zoo")
        hrefs = re.findall(r'href="(/printables/pdf/[^"]+)"', block)
        self.assertEqual(len(hrefs), 6)
        for href in hrefs:
            self.assertTrue((ROOT / "static" / href.lstrip("/")).is_file(), href)
        text = re.sub(r"<[^>]+>", " ", block)
        self.assertIsNone(FREE_RE.search(text))
        self.assertIsNone(WE_RE.search(text))

    def test_other_pages_unchanged_by_helper(self):
        self.assertEqual(with_field_trip_block("banff", "<x>"), "<x>")

    def test_generator_applies_block(self):
        gen = (ROOT / "scripts/generate_bdo_seo.py").read_text(encoding="utf-8")
        self.assertIn('html = with_field_trip_block(v["id"], html)', gen)


if __name__ == "__main__":
    unittest.main()
