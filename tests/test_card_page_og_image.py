"""Study card pages use the animal photo for social preview, not Dallas mission art."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    OG_SHARE_IMAGE,
    SITE,
    published_card_ids,
    FIELD,
)

FP = REPO / "static" / "field-pack"
WHALE = FP / "cards" / "whale-shark" / "index.html"
GENERATOR = REPO / "scripts" / "generate_bdo_seo.py"

OG_RE = re.compile(
    r'<meta\s+property="og:image"\s+content="([^"]+)"\s*/?>',
    re.I,
)
TW_RE = re.compile(
    r'<meta\s+name="twitter:image"\s+content="([^"]+)"\s*/?>',
    re.I,
)
DALLAS = "sample-mission-dallas-zoo"


class CardPageOgImageTests(unittest.TestCase):
    def test_whale_shark_og_is_animal_photo_not_dallas(self):
        html = WHALE.read_text(encoding="utf-8")
        og = OG_RE.search(html)
        self.assertIsNotNone(og, "whale-shark missing og:image")
        self.assertEqual(
            og.group(1),
            f"{SITE}/field-pack/photos/whale-shark.jpg",
        )
        self.assertNotIn(DALLAS, og.group(1))
        tw = TW_RE.search(html)
        self.assertIsNotNone(tw, "whale-shark missing twitter:image")
        self.assertEqual(tw.group(1), og.group(1))

    def test_published_cards_with_photo_skip_dallas_og(self):
        pub = published_card_ids()
        missing_photo: list[str] = []
        still_dallas: list[str] = []
        for cid in sorted(pub):
            page = FP / "cards" / cid / "index.html"
            if not page.is_file():
                continue
            has_file = (FIELD / "photos" / f"{cid}.jpg").is_file()
            html = page.read_text(encoding="utf-8")
            og = OG_RE.search(html)
            self.assertIsNotNone(og, f"{cid} missing og:image")
            url = og.group(1)
            if not has_file:
                # Catalog may still supply photos/<id>; flag if og fell back.
                if DALLAS in url or url == OG_SHARE_IMAGE:
                    missing_photo.append(cid)
                continue
            expected = f"{SITE}/field-pack/photos/{cid}.jpg"
            if DALLAS in url or url == OG_SHARE_IMAGE:
                still_dallas.append(cid)
            else:
                self.assertEqual(url, expected, cid)
            tw = TW_RE.search(html)
            self.assertIsNotNone(tw, f"{cid} missing twitter:image")
            self.assertEqual(tw.group(1), url, cid)
        self.assertEqual(
            still_dallas,
            [],
            f"cards still using Dallas/fallback og:image: {still_dallas}",
        )
        # Informational: cards without a photo file that still fall back.
        if missing_photo:
            # Fail soft only if any published card truly has no photo path.
            self.fail(f"published cards missing photo (og fallback): {missing_photo}")

    def test_generator_derives_og_from_card_photo(self):
        src = GENERATOR.read_text(encoding="utf-8")
        self.assertIn("Social preview: each card's own animal photo", src)
        self.assertIn('WARN card missing photo for og:image', src)
        self.assertNotIn(
            '<meta property="og:image" content="{OG_SHARE_IMAGE}" />',
            src.split("def write_card_pages", 1)[1].split("def ", 1)[0],
        )


if __name__ == "__main__":
    unittest.main()
