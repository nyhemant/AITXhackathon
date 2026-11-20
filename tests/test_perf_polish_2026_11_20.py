"""Polish 2026-11-20: map webp twins, longer cache on versioned assets."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "static" / "field-pack"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from busyparent_agent.web import VERSIONED_ASSET_CACHE, _static_cache_control  # noqa: E402

THUMB = re.compile(r'<img class="seo-map-thumb" src="([^"]+)"')
PREVIEW = re.compile(r'<img src="([^"]+)" alt="Enlarged visitor map"')


class MapWebp(unittest.TestCase):
    def test_big_maps_have_small_twins_and_pages_use_them(self):
        twins = left_on_jpg = 0
        for page in sorted(FP.glob("*/index.html")):
            html = page.read_text(encoding="utf-8")
            t, p = THUMB.search(html), PREVIEW.search(html)
            if not t or not p:
                continue
            src = t.group(1)
            if src.endswith("-640-v1.webp"):
                twins += 1
                slug = src.rsplit("/", 1)[1][: -len("-640-v1.webp")]
                big = FP / "media" / "maps" / f"{slug}-1400-v1.webp"
                want = f"/field-pack/media/maps/{slug}-1400-v1.webp" if big.is_file() else f"/field-pack/media/maps/{slug}.jpg"
                self.assertEqual(p.group(1), want, page.parent.name)
                jpg = FP / "media" / "maps" / f"{slug}.jpg"
                self.assertTrue(jpg.is_file(), slug)  # print keeps the jpg
                for u in (src, p.group(1)):
                    self.assertTrue((ROOT / "static" / u[1:]).is_file(), u)
                self.assertLess((ROOT / "static" / src[1:]).stat().st_size, jpg.stat().st_size * 0.7, slug)
            elif src.startswith("/field-pack/media/maps/") and src.endswith(".jpg"):
                left_on_jpg += 1
                self.assertLess((ROOT / "static" / src[1:]).stat().st_size, 150_000, page.parent.name)
        self.assertGreaterEqual(twins, 130)

    def test_dallas_map_numbers(self):
        maps = FP / "media" / "maps"
        self.assertLess((maps / "dallas-zoo-640-v1.webp").stat().st_size, 80_000)
        self.assertLess((maps / "dallas-zoo-1400-v1.webp").stat().st_size, 200_000)

    def test_page_patch_is_idempotent(self):
        import generate_bdo_seo as gen

        html = (FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(gen.add_map_webp(html), html)


class CacheLengths(unittest.TestCase):
    def test_versioned_assets_keep_thirty_days(self):
        thirty = "public, max-age=2592000"
        self.assertEqual(VERSIONED_ASSET_CACHE, thirty)
        p = Path
        self.assertEqual(_static_cache_control("/field-pack/css/landing.css?v=105", p("landing.css")), thirty)
        self.assertEqual(_static_cache_control("/field-pack/media/maps/dallas-zoo-640-v1.webp", p("dallas-zoo-640-v1.webp")), thirty)
        self.assertEqual(_static_cache_control("/field-pack/photos/zebra.jpg?v=img2", p("zebra.jpg")), thirty)

    def test_unversioned_things_keep_their_old_rules(self):
        p = Path
        self.assertEqual(_static_cache_control("/field-pack/media/maps/dallas-zoo.jpg", p("dallas-zoo.jpg")), "public, max-age=86400")
        self.assertEqual(_static_cache_control("/field-pack/css/landing.css", p("landing.css")), "no-cache")
        self.assertEqual(_static_cache_control("/field-pack/dallas-zoo/", p("index.html")), "no-cache")
        self.assertEqual(_static_cache_control("/printables/pdf/letter/x.pdf", p("x.pdf")), "no-cache")


if __name__ == "__main__":
    unittest.main()
