"""Two thin Starter pages are noindex,follow and out of the sitemap (2026-11-16); URLs still serve."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

NOINDEX = (
    "ecoparque-ba", "stockholm-skansen",
    # gate B2 (2026-11-16)
    "cairo-zoo", "nairobi-safari-walk", "bogota-zoo", "beijing-zoo", "lotte-aquarium-seoul",
)
STAY_INDEXED = ("mumbai-byculla-zoo", "helsinki-zoo")


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
            self.assertEqual(xml.count("<url>"), 286, sm)
            for slug in NOINDEX:
                self.assertNotIn(f"/field-pack/{slug}/</loc>", xml)
            for slug in STAY_INDEXED:
                self.assertIn(f"/field-pack/{slug}/</loc>", xml)

    def test_generator(self):
        import generate_bdo_seo as gen

        self.assertEqual(gen.NOINDEX_PLACE_SLUGS, frozenset(NOINDEX))
        page = '<meta name="robots" content="index,follow" />'
        self.assertIn("noindex,follow", gen.apply_place_robots("ecoparque-ba", page))
        self.assertEqual(gen.apply_place_robots("mumbai-byculla-zoo", page), page)

    def test_cairo_closure_notice(self):
        import generate_bdo_seo as gen

        page = (ROOT / "static/field-pack/cairo-zoo/index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('class="seo-place-notice"'), 1)
        self.assertIn("closed for redevelopment since July 2023", page)
        self.assertIn(gen.PLACE_NOTICES["cairo-zoo"], page)
        lead = '<p class="lead">x</p>\n'
        self.assertEqual(gen.apply_place_notice("cairo-zoo", gen.apply_place_notice("cairo-zoo", lead)).count("seo-place-notice"), 1)
        self.assertEqual(gen.apply_place_notice("mumbai-byculla-zoo", lead), lead)

    def test_hub_still_links_them(self):
        hub = (ROOT / "static/field-pack/index.html").read_text(encoding="utf-8")
        for slug in NOINDEX:
            self.assertIn(f'href="/field-pack/{slug}/"', hub)


if __name__ == "__main__":
    unittest.main()
