"""Zoo place pages show a listed-animal photo; the virtual field trip has a next step."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
DALLAS = FP / "dallas-zoo" / "index.html"
VFT = FP / "virtual-field-trip" / "index.html"
YELLOWSTONE = FP / "yellowstone" / "index.html"

NEXT = (
    ("/field-pack/cards/", "Meet the animals"),
    ("/field-pack/zoos/", "Plan a real zoo trip"),
    ("/printables/scavenger-hunt/", "Print a scavenger hunt"),
)


class PlaceListedPhotoTests(unittest.TestCase):
    def test_dallas_zoo_photo_caption_and_og_image(self):
        html = DALLAS.read_text(encoding="utf-8")
        figure = re.search(
            r'<figure class="seo-place-photo">(.*?)</figure>',
            html,
            re.S,
        )
        self.assertIsNotNone(figure)
        block = figure.group(0)
        self.assertIn('alt="Reticulated giraffe"', block)
        self.assertIn("Reticulated giraffe — one of the animals on this hunt", block)
        self.assertIn('loading="eager"', block)
        self.assertIn('width="', block)
        self.assertIn('height="', block)
        self.assertIsNone(re.search(r"\bfree\b", block, re.I))
        og = re.search(r'<meta property="og:image" content="([^"]+)"', html)
        self.assertIsNotNone(og)
        url = og.group(1)
        self.assertTrue(url.startswith("https://kidzookit.com/field-pack/photos/"))
        self.assertNotIn("sample-mission-dallas-zoo", url)
        rel = url.split("https://kidzookit.com/field-pack/", 1)[1]
        self.assertTrue((FP / rel).is_file(), rel)
        tw = re.search(r'<meta name="twitter:image" content="([^"]+)"', html)
        self.assertIsNotNone(tw)
        self.assertEqual(tw.group(1), url)
        park = YELLOWSTONE.read_text(encoding="utf-8")
        self.assertNotIn('class="seo-place-photo"', park)
        self.assertIn('class="seo-park-hero', park)

    def test_virtual_field_trip_explore_next_cards(self):
        html = VFT.read_text(encoding="utf-8")
        start = html.find("<!-- VFT:NEXT:START -->")
        end = html.find("<!-- VFT:NEXT:END -->")
        self.assertGreater(start, 0)
        self.assertGreater(end, start)
        self.assertLess(end, html.find("</main>"))
        block = html[start:end]
        self.assertIn(">Explore next</h2>", block)
        self.assertEqual(block.count('loading="lazy"'), 3)
        self.assertIsNone(re.search(r"\bfree\b", block, re.I))
        for href, label in NEXT:
            card = re.search(
                rf'<a class="vz-next-card [^"]+" href="{re.escape(href)}">(.*?)</a>',
                block,
                re.S,
            )
            self.assertIsNotNone(card, href)
            inner = card.group(1)
            self.assertIn(f'alt="{label}"', inner)
            self.assertIn(f"<span>{label}</span>", inner)
            src = re.search(r'<img src="([^"]+)"', inner)
            self.assertIsNotNone(src, href)
            path = src.group(1)
            self.assertTrue(path.startswith("/"))
            self.assertTrue((REPO / "static" / path.lstrip("/")).is_file(), path)


if __name__ == "__main__":
    unittest.main()
