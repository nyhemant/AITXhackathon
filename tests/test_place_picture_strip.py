"""Picture-first animal photo strip on place pages and /field-pack/."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"

TILE_RE = re.compile(
    r'<a class="seo-pic-tile" href="([^"]+)">\s*(<img\b[^>]*>)\s*</a>',
    re.S,
)
IMG_ATTR = re.compile(r'\b(alt|width|height)="([^"]*)"')


def _hero(html: str) -> str:
    return html.split('class="seo-hero"', 1)[1].split("</header>", 1)[0]


def _strip_after_h1(hero: str) -> str:
    after = hero.split("</h1>", 1)[1]
    if not after.lstrip().startswith('<div class="seo-pic-strip">'):
        raise AssertionError("photo strip is not the first element under the H1")
    return after.lstrip().split("</div>", 1)[0]


def _tiles(strip_inner: str) -> list[tuple[str, str]]:
    return TILE_RE.findall(strip_inner if strip_inner.startswith("<") else "<x>" + strip_inner)


class PlacePictureStripTests(unittest.TestCase):
    def _assert_place_strip(self, slug: str) -> None:
        html = (FP / slug / "index.html").read_text(encoding="utf-8")
        hero = _hero(html)
        inner = _strip_after_h1(hero)
        tiles = TILE_RE.findall(inner)
        self.assertGreaterEqual(len(tiles), 1, slug)
        eager = 0
        for href, img in tiles:
            self.assertRegex(href, rf"^/field-pack/cards/[a-z0-9-]+/#from={re.escape(slug)}$")
            attrs = dict(IMG_ATTR.findall(img))
            self.assertTrue(attrs.get("alt", "").strip(), img)
            self.assertRegex(attrs.get("width", ""), r"^[1-9]\d*$")
            self.assertRegex(attrs.get("height", ""), r"^[1-9]\d*$")
            if 'loading="eager"' in img:
                eager += 1
            else:
                self.assertIn('loading="lazy"', img)
                self.assertIn('decoding="async"', img)
        self.assertGreaterEqual(eager, 1)
        self.assertLessEqual(eager, 3)
        if "seo-fact-chips" in hero:
            rest = hero.split("</h1>", 1)[1].lstrip()
            rest = rest.split("</div>", 1)[1].lstrip()
            self.assertTrue(
                rest.startswith('<ul class="seo-fact-chips seo-fact-row"'),
                "Time/Tickets/Get there row should sit directly under the strip",
            )

    def test_dallas_zoo_strip_follows_h1(self):
        self._assert_place_strip("dallas-zoo")

    def test_generated_houston_zoo_strip_follows_h1(self):
        self._assert_place_strip("houston-zoo")

    def test_field_pack_photo_row_before_map(self):
        html = (FP / "index.html").read_text(encoding="utf-8")
        map_at = html.find('id="us-map"')
        self.assertGreater(map_at, 0)
        before = html[:map_at]
        strip_at = before.rfind('<div class="seo-pic-strip">')
        self.assertGreater(strip_at, 0)
        strip = before[strip_at:]
        tiles = TILE_RE.findall(strip)
        self.assertGreaterEqual(len(tiles), 4)
        self.assertLessEqual(len(tiles), 6)
        for href, img in tiles:
            self.assertRegex(href, r"^/field-pack/cards/[a-z0-9-]+/$")
            attrs = dict(IMG_ATTR.findall(img))
            self.assertTrue(attrs.get("alt", "").strip(), img)
            self.assertRegex(attrs.get("width", ""), r"^[1-9]\d*$")
            self.assertRegex(attrs.get("height", ""), r"^[1-9]\d*$")
            self.assertIn('decoding="async"', img)
