"""Image-first place hubs + curated card strips (2026-10-23, scripts/hub_photos.py)."""
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
HUBS = ["zoos", "aquariums", "museums", "national-parks"]
GENERIC = ("np-visitor-center", "np-scenic-overlook", "np-trailhead-sign")


class HubImagesTest(unittest.TestCase):
    def html(self, hub):
        return (FP / hub / "index.html").read_text(encoding="utf-8")

    def test_tiles_have_distinct_lazy_photos_with_dims(self):
        for hub in HUBS:
            h = self.html(hub)
            grid = re.search(r'<div class="type-feat-grid">(.*?)</div>', h, re.S).group(1)
            imgs = re.findall(r"<img [^>]*>", grid)
            self.assertGreaterEqual(len(imgs), 5, hub)
            srcs = [re.search(r'src="([^"]+)"', i).group(1).split("?")[0] for i in imgs]
            self.assertEqual(len(srcs), len(set(srcs)), hub)
            for i in imgs:
                self.assertIn('loading="lazy"', i)
                self.assertIn("width=", i)
                self.assertIn("height=", i)
                self.assertFalse(any(g in i for g in GENERIC), i)
            self.assertEqual(grid.count("type-feat-card"), grid.count('data-related-link="hub_tile"'), hub)

    def test_tile_photo_is_used_on_the_place_page(self):
        for hub in HUBS:
            for slug, src in re.findall(r'href="/field-pack/([^/"]+)/" data-related-link="hub_tile"><span class="type-feat-thumb"><img src="([^"?]+)', self.html(hub)):
                page = (FP / slug / "index.html").read_text(encoding="utf-8")
                self.assertIn(src.replace("/field-pack/", "").split("/")[-1], page, (hub, slug))

    def test_curated_strip(self):
        for hub in HUBS:
            h = self.html(hub)
            strip = re.search(r"<!-- kz-hub:strip -->(.*?)<!-- /kz-hub:strip -->", h, re.S)
            self.assertIsNotNone(strip, hub)
            cards = re.findall(r'href="/field-pack/cards/([^/"]+)/" data-related-link="hub_card"', strip.group(1))
            self.assertGreaterEqual(len(cards), 4, hub)
            self.assertLessEqual(len(cards), 8, hub)
            self.assertEqual(len(cards), len(set(cards)))
            for c in cards:
                self.assertTrue((FP / "cards" / c / "index.html").exists(), c)
            for i in re.findall(r"<img [^>]*>", strip.group(1)):
                self.assertIn('loading="lazy"', i)
                self.assertIn('width="640" height="640"', i)
            self.assertIn("/field-pack/css/hub-strip.css?v=1", h)
            self.assertIn("/shell/related-links.js?v=1", h)
            self.assertIn("qr-welcome.js", h) if hub == "zoos" else None
        # only fitting animals: no sea life at the zoo strip, no land mammals in the aquarium strip
        zoo = self.html("zoos")
        self.assertNotIn("/field-pack/cards/shark/", zoo.split("kz-hub:strip")[1])
        aq = self.html("aquariums").split("kz-hub:strip")[1]
        self.assertNotIn("/field-pack/cards/african-lion/", aq)

    def test_museums_h1_and_intro(self):
        h = self.html("museums")
        self.assertIn("<h1>Museums for Kids</h1>", h)
        self.assertRegex(h, r'<h1>Museums for Kids</h1>\s*<p class="type-lead">[^<]{40,}</p>')
        copy = (REPO / "scripts" / "seo_page_copy.py").read_text(encoding="utf-8")
        self.assertIn('"h1": "Museums for Kids"', copy)


if __name__ == "__main__":
    unittest.main()
