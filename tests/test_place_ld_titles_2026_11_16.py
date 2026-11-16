"""Place-page JSON-LD name/headline match the page title (2026-11-16), except the 24 test pages."""
from __future__ import annotations

import html
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELD = ROOT / "static" / "field-pack"
sys.path.insert(0, str(ROOT / "scripts"))

from scav_test_2026_11 import COMPARISON_SLUGS, TEST_SLUGS  # noqa: E402

LEGACY = " for Kids — Explore at Home or Print a Hunt"


def _ld(page: str) -> list[dict]:
    out = []
    for raw in re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', page, re.S):
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            pass
    return out


def _names(page: str) -> list[str]:
    vals = []
    for block in _ld(page):
        if block.get("@type") == "HowTo":
            vals.append(block["name"])
        if block.get("@type") == "Article":
            vals.append(block["headline"])
    return vals


class PlaceLdTitles(unittest.TestCase):
    def setUp(self):
        import generate_bdo_seo as gen

        self.gen = gen
        self.venues = {row["id"]: row for row in gen.load_venues()}

    def test_non_test_place_pages_match_title(self):
        checked = 0
        for slug in sorted(self.venues):
            if slug in TEST_SLUGS | COMPARISON_SLUGS:
                continue
            page = (FIELD / slug / "index.html").read_text(encoding="utf-8")
            names = _names(page)
            if not names:
                continue
            title = html.unescape(re.search(r"<title>(.*?)</title>", page).group(1))
            want = re.sub(r" [·|] KidZooKit$", "", title)
            with self.subTest(slug=slug):
                self.assertNotIn(LEGACY, page)
                self.assertEqual(set(names), {want})
                checked += 1
        self.assertGreaterEqual(checked, 190)

    def test_the_24_keep_legacy_ld(self):
        for slug in sorted(TEST_SLUGS | COMPARISON_SLUGS):
            page = (FIELD / slug / "index.html").read_text(encoding="utf-8")
            with self.subTest(slug=slug):
                if slug in ("air-and-space", "dallas-zoo"):
                    self.assertNotIn(LEGACY, page)
                else:
                    self.assertEqual(page.count(LEGACY), 2)

    def test_generator_hunt_name_matches(self):
        gen = self.gen
        self.assertEqual(gen.LEGACY_LD_SLUGS, (TEST_SLUGS | COMPARISON_SLUGS) - {"air-and-space", "dallas-zoo"})
        for slug in ("hogle-zoo", "dallas-zoo", "lincoln-park-zoo"):
            mission = gen.load_mission_venue(slug)
            v = self.venues[slug]
            rendered = gen.render_mission_venue_page(v, mission) if mission else gen.render_venue_page(v)
            page = (FIELD / slug / "index.html").read_text(encoding="utf-8")
            with self.subTest(slug=slug):
                self.assertEqual(_names(rendered), _names(page))


if __name__ == "__main__":
    unittest.main()
