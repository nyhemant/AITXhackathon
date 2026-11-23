"""Scavenger-hunt test: "Printable" title on the 12 TEST pages (2026-11-16).

Pulled forward from Nov 24 after the title freeze was lifted on Nov 15. Only the
<title>, og:title and twitter:title change on test pages. H1, meta descriptions,
LD and every comparison page stay as they were. Judge date ~2026-12-10.
"""
from __future__ import annotations

import hashlib
import html
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scav_test_2026_11 import COMPARISON_SLUGS, FREEZE_ENDED_SLUGS, TEST_SLUGS, UNFROZEN_CHANGED_SLUGS  # noqa: E402

FIELD = ROOT / "static" / "field-pack"

TEST_TITLES = {
    "amnh": "AMNH Printable Scavenger Hunt: Museum of Natural History",  # query page 2026-11-16
    "nashville-adventure-science": "Adventure Science Center Printable Scavenger Hunt for Kids",
    "air-and-space": "Air and Space & Udvar-Hazy Printable Scavenger Hunt for Kids",
    "national-aquarium-baltimore": "Washington DC Aquarium Printable Scavenger Hunt · KidZooKit",  # query page 2026-11-23
    "shedd-aquarium": "Shedd Aquarium Printable Scavenger Hunt for Kids · KidZooKit",
    "lincoln-park-zoo": "Lincoln Park Zoo Printable Scavenger Hunt · KidZooKit",
    "toronto-zoo": "Toronto Zoo Printable Scavenger Hunt for Kids · KidZooKit",
    "austin-zoo": "Austin Zoo Printable Scavenger Hunt for Kids · KidZooKit",
    "national-zoo": "Smithsonian National Zoo Printable Scavenger Hunt for Kids",
    "bronx-zoo": "Bronx Zoo Printable Scavenger Hunt for Kids · KidZooKit",
    "redwood": "Redwood National and State Parks Printable Scavenger Hunt",
    "joshua-tree": "Joshua Tree National Park Printable Scavenger Hunt for Kids",
}

# Comparison pages are the control: byte-for-byte as shipped on 2026-11-13 (main f51946a9).
COMPARISON_SHA256 = {
    "museum-of-science-industry-chi": "c970e745dcd8f69e1a451057b653c7aa5fe297e1424a2f311ee206c9c39631ab",
    "california-science-center": "e904bea5726f69bfbc90e79d65823197cc006338aad9f7aebfbe10f0ce974d53",
    "discovery-place": "3f8fea4b0828234b5a91d861f28936394b69b879db7fcdb5ab5ce47175f53d0d",
    "seattle-aquarium": "42d17470f5ee435f955b83d3d33046429292a1b692041aa1957900f8384eb61b",
    "aquarium-of-the-pacific": "064827ebf38669236d1fa37990caae4aa18c40ccd9edc14c9ab1998743cc2411",
    "st-louis-zoo": "dbcf13943e5e17c1b9f4b4f4ae4ef296a636b6ff6fd5fc8dd187136e6eb05608",
    "calgary-zoo": "59fd8542eebd0bb643f66df7232547b10581aecac5ca5e4c21c5e1174f634174",
    "fort-worth-zoo": "7936df3faccc36fd38957fddd929c52a30daf300163a124de089d2612f921901",
    "san-antonio-zoo": "d67fcea9ca4698d9234dac4ae2730ef99b02bef430a21a2bf6e9cdc484fe7e9e",
    "dallas-zoo": "1f357982e3efc16a8fe3776dbe519dca7357988027aa0954358f9605202f0026",
    "banff": "30b1bfc7a7a4b6e4d061ca90d0296d2004e63c7e37f363510c83ea4008076cd3",
    "sequoia": "298da361664a6626a71048c54ba79c6ddd96ba9a7dd3d9449993261c991668cf",
}

FREE_RE = re.compile(r"\b(free|no-cost)\b", re.IGNORECASE)
WE_RE = re.compile(r"\b(we|our|us)\b", re.IGNORECASE)


def _page(slug: str) -> str:
    return (FIELD / slug / "index.html").read_text(encoding="utf-8")


def _one(page: str, pattern: str) -> str:
    found = re.findall(pattern, page)
    if len(found) != 1:
        raise AssertionError(f"{pattern}: {len(found)} matches")
    return html.unescape(found[0])


class ScavPrintableTitles(unittest.TestCase):
    def test_pins_cover_the_twelve_test_pages(self):
        self.assertEqual(set(TEST_TITLES), set(TEST_SLUGS))
        self.assertEqual(set(COMPARISON_SHA256), set(COMPARISON_SLUGS))

    def test_test_page_titles(self):
        for slug, want in sorted(TEST_TITLES.items()):
            with self.subTest(slug=slug):
                page = _page(slug)
                self.assertEqual(_one(page, r"<title>(.*?)</title>"), want)
                self.assertEqual(_one(page, r'<meta property="og:title" content="([^"]*)"'), want)
                self.assertEqual(_one(page, r'<meta name="twitter:title" content="([^"]*)"'), want)
                self.assertLessEqual(len(want), 60)
                self.assertIn("Printable Scavenger Hunt", want)
                self.assertIsNone(FREE_RE.search(want))
                self.assertIsNone(WE_RE.search(want))
                self.assertNotIn("Printable", _one(page, r"<h1[^>]*>(.*?)</h1>"))

    def test_generator_title_matches_pages(self):
        import generate_bdo_seo as gen

        venues = {row["id"]: row for row in gen.load_venues()}
        for slug, want in TEST_TITLES.items():
            self.assertEqual(gen.title_for(venues[slug]), want, slug)
        for slug in COMPARISON_SLUGS:
            title = gen.title_for(venues[slug])
            self.assertNotIn("Printable Scavenger", title, slug)

    def test_comparison_pages_untouched(self):
        for slug, digest in sorted(COMPARISON_SHA256.items()):
            if slug in UNFROZEN_CHANGED_SLUGS or slug in FREEZE_ENDED_SLUGS:  # freeze ended 2026-11-20; freeze lifted 2026-11-15 (Heymant); changed pages are listed in UNFROZEN_CHANGED_SLUGS
                continue
            with self.subTest(slug=slug):
                raw = (FIELD / slug / "index.html").read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
                self.assertIn(b"/shell/shell.js?v=6", raw)
                self.assertNotIn(b"Printable Scavenger Hunt", raw)


if __name__ == "__main__":
    unittest.main()
