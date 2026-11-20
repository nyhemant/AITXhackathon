"""Favicon on every page (2026-11-16), except the 24 scavenger test/comparison pages.

Those 24 stay byte-identical until the ~2026-12-10 judge date; the root /favicon.ico
covers them without an HTML change.
"""
from __future__ import annotations

import hashlib
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

from scav_test_2026_11 import COMPARISON_SLUGS, FREEZE_ENDED_SLUGS, TEST_SLUGS, UNFROZEN_CHANGED_SLUGS  # noqa: E402

ICON = '<link rel="icon" href="/favicon.ico?v=1" sizes="48x48" />'
PNG = '<link rel="icon" type="image/png" href="/pwa/favicon-96-v1.png" sizes="96x96" />'
APPLE = '<link rel="apple-touch-icon" href="/pwa/apple-touch-icon.png" />'

# The 24 frozen pages as of 2026-11-16 (test titles from #437; comparison unchanged since Nov 12).
FROZEN_SHA256 = {
    "amnh": "4c1f8eae15f0cb53697508daa9a609a5ce66e4643d55badc39f923b27d9a7259",
    "nashville-adventure-science": "1858998ca7e15aeba0b0cb9bff098d4806872a732aa8199c1246fdbdc30829bd",
    "air-and-space": "78b4ac7c17b274dced498d88e6f0dbe658aea8f6f54e0173fc4059c1a52a1eaf",
    "national-aquarium-baltimore": "2c375c7b906290b78c61890e9fafec7302eeb679c8f1f4ef54bcc6f340f2dc77",
    "shedd-aquarium": "4a157761bd8db963f88f395bfae76fb4e57db3743e50589808f3e9ed8926e8d5",
    "lincoln-park-zoo": "2d3186c8f4bd096e775531e8ed50ee4303c01e565f1163ce7494196b0cb262b9",
    "toronto-zoo": "ffae07f80a39b61587aa51a6cf40a6eb94f53251e14cbd860b90a88baae2bd81",
    "austin-zoo": "dde498694f625c6caada29dbc29566ba5294dbc257dbf75b850d2179822d7640",
    "national-zoo": "225abeae58a6d1358a05c3b36a60a84914162e1347c69b5c27f129e1b68c509a",
    "bronx-zoo": "0c48ec2080183b8ed8f279cf9e6e140b9e0629ab2bb4d734a96d1adc342b8d76",
    "redwood": "7ae70db4f2e1a48c9d7899e76e077da1290cd281de26e13cd00c9b1090f550ed",
    "joshua-tree": "dc5efed4ad0b646c793c2c4c79ed8f11b53ed3dc4f3c16482509b6d8ab7675dc",
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


def _frozen_rel() -> set[str]:
    return {f"static/field-pack/{s}/index.html" for s in TEST_SLUGS | COMPARISON_SLUGS}


class Favicon(unittest.TestCase):
    def test_icon_files_exist(self):
        ico = (STATIC / "favicon.ico").read_bytes()
        self.assertEqual(ico[:4], b"\x00\x00\x01\x00")
        png = (STATIC / "pwa" / "favicon-96-v1.png").read_bytes()
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        self.assertTrue((STATIC / "pwa" / "apple-touch-icon.png").is_file())

    def test_every_page_but_the_24_links_the_icons(self):
        frozen = _frozen_rel()
        pages = 0
        for p in sorted(STATIC.glob("**/*.html")):
            rel = p.relative_to(ROOT).as_posix()
            if p.name.startswith("google"):
                continue
            s = p.read_text(encoding="utf-8")
            head = s.split("</head>", 1)[0]
            with self.subTest(page=rel):
                if rel in frozen:
                    self.assertNotIn('rel="icon"', s)
                    continue
                pages += 1
                self.assertEqual(head.count(ICON), 1)
                self.assertEqual(head.count(PNG), 1)
                self.assertEqual(head.count('rel="apple-touch-icon"'), 1)
        self.assertGreaterEqual(pages, 270)

    def test_the_24_frozen_pages_are_byte_identical(self):
        self.assertEqual(set(FROZEN_SHA256), TEST_SLUGS | COMPARISON_SLUGS)
        for slug, digest in sorted(FROZEN_SHA256.items()):
            if slug in UNFROZEN_CHANGED_SLUGS or slug in FREEZE_ENDED_SLUGS:  # freeze ended 2026-11-20; freeze lifted 2026-11-15 (Heymant); changed pages are listed in UNFROZEN_CHANGED_SLUGS
                continue
            with self.subTest(slug=slug):
                raw = (STATIC / "field-pack" / slug / "index.html").read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)

    def test_generator_templates_emit_the_icons(self):
        gen = (ROOT / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        self.assertEqual(gen.count(f"  {ICON}\n  {PNG}\n  {APPLE}\n"), 5)

    def test_server_serves_root_favicon(self):
        from busyparent_agent.web import (
            _is_allowed_static_root_name,
            _root_static_content_type,
            _safe_static_root_file,
        )

        self.assertTrue(_is_allowed_static_root_name("favicon.ico"))
        path = _safe_static_root_file("/favicon.ico")
        self.assertIsNotNone(path)
        self.assertEqual(_root_static_content_type(path), "image/x-icon")
        self.assertIsNone(_safe_static_root_file("/favicon.png"))


if __name__ == "__main__":
    unittest.main()
