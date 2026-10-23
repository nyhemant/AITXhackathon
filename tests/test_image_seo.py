"""Image sitemap + descriptive card hero alts (2026-10-23, scripts/image_seo.py).
If this fails after a generator run: python3 scripts/image_seo.py && python3 scripts/sitemap_lastmod_from_git.py"""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
SM = REPO / "static" / "sitemap.xml"
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "i": "http://www.google.com/schemas/sitemap-image/1.1"}
GENERIC = ("np-visitor-center", "np-scenic-overlook", "np-trailhead-sign")


class ImageSeoTest(unittest.TestCase):
    def test_sitemap_has_image_entries_and_is_valid(self):
        raw = SM.read_text(encoding="utf-8")
        self.assertEqual(raw, (FP / "sitemap.xml").read_text(encoding="utf-8"))
        root = ET.fromstring(raw.encode("utf-8"))
        urls = root.findall("s:url", NS)
        self.assertEqual(len(urls), 292)
        imgs = {u.find("s:loc", NS).text: [i.find("i:loc", NS).text for i in u.findall("i:image", NS)] for u in urls}
        cards = [k for k in imgs if re.search(r"/field-pack/cards/[^/]+/$", k)]
        self.assertGreaterEqual(len(cards), 58)
        for k in cards:
            self.assertEqual(len(imgs[k]), 1, k)
        n = sum(len(v) for v in imgs.values())
        self.assertGreaterEqual(n, 130)
        for k, v in imgs.items():
            for src in v:
                self.assertTrue(src.startswith("https://kidzookit.com/field-pack/photos/"), src)
                self.assertFalse(any(g in src for g in GENERIC), src)
                local = FP / "photos" / src.split("/photos/")[1].split("?")[0]
                self.assertTrue(local.exists(), src)

    def test_card_hero_alts_describe_the_photo(self):
        for p in sorted((FP / "cards").glob("*/index.html")):
            s = p.read_text(encoding="utf-8")
            m = re.search(r'<img class="card-page-photo" src="[^"]+" data-card-name="([^"]+)" alt="([^"]+)"', s)
            self.assertIsNotNone(m, p.parent.name)
            self.assertNotEqual(m.group(1), m.group(2), p.parent.name)
            self.assertGreaterEqual(len(m.group(2).split()), 3, p.parent.name)

    def test_no_park_park_day_alts(self):
        for p in FP.glob("*/index.html"):
            self.assertNotRegex(p.read_text(encoding="utf-8"), r'alt="[^"]*[Pp]ark park day"', p.parent.name)


if __name__ == "__main__":
    unittest.main()
