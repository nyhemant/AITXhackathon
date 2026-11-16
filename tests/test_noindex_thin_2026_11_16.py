"""Two thin Starter pages are noindex,follow and out of the sitemap (2026-11-16); URLs still serve."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

NOINDEX = ("ecoparque-ba", "stockholm-skansen")
STAY_INDEXED = ("cairo-zoo", "mumbai-byculla-zoo")


class NoindexThin(unittest.TestCase):
    def test_robots_meta(self):
        for slug in NOINDEX:
            page = (ROOT / f"static/field-pack/{slug}/index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="noindex,follow" />', page)
            self.assertNotIn('content="index,follow"', page)
        for slug in STAY_INDEXED:
            page = (ROOT / f"static/field-pack/{slug}/index.html").read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="index,follow" />', page)

    def test_sitemaps_drop_only_the_two(self):
        for sm in ("static/sitemap.xml", "static/field-pack/sitemap.xml"):
            xml = (ROOT / sm).read_text(encoding="utf-8")
            self.assertEqual(xml.count("<url>"), 291, sm)
            for slug in NOINDEX:
                self.assertNotIn(f"/field-pack/{slug}/</loc>", xml)
            for slug in STAY_INDEXED:
                self.assertIn(f"/field-pack/{slug}/</loc>", xml)

    def test_generator(self):
        import generate_bdo_seo as gen

        self.assertEqual(gen.NOINDEX_PLACE_SLUGS, frozenset(NOINDEX))
        page = '<meta name="robots" content="index,follow" />'
        self.assertIn("noindex,follow", gen.apply_place_robots("ecoparque-ba", page))
        self.assertEqual(gen.apply_place_robots("cairo-zoo", page), page)

    def test_hub_still_links_them(self):
        hub = (ROOT / "static/field-pack/index.html").read_text(encoding="utf-8")
        for slug in NOINDEX:
            self.assertIn(f'href="/field-pack/{slug}/"', hub)


if __name__ == "__main__":
    unittest.main()
