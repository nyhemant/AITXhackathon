"""Venue SEO pages ship the mission drawer without catalog / print-kit dead weight."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import MISSION_UI_JS_VER  # noqa: E402

FP = REPO / "static" / "field-pack"
GENERATOR = REPO / "scripts" / "generate_bdo_seo.py"
MISSION_UI = FP / "js" / "mission" / "mission-ui.js"
VENUE_DATA = FP / "data" / "venues"

# One page per type — regenerated HTML must match the slim generator path.
SAMPLE = (
    "dallas-zoo",
    "georgia-aquarium",
    "amnh",
    "yellowstone",
)

DEAD_WEIGHT = (
    "/field-pack/js/catalog.js",
    "/field-pack/js/print-kit.js",
    'id="print-sheet"',
    'id="treasure-sheet"',
    'id="challenges-data"',
    'id="wonders-data"',
)

KEEP = (
    'id="venue-data"',
    'id="bonus-hunts-data"',
    "/field-pack/js/print-maps.js",
    "/field-pack/js/mission/mission-engine.js",
    "/field-pack/js/mission/mission-ui.js",
    'id="mission-drawer"',
)


def _fn_src(src: str, name: str, nxt: str) -> str:
    start = src.index(f"def {name}")
    end = src.index(f"def {nxt}")
    return src[start:end]


class VenueSeoPayloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = GENERATOR.read_text(encoding="utf-8")
        cls.ui = MISSION_UI.read_text(encoding="utf-8")
        cls.mission_tpl = _fn_src(cls.gen, "render_mission_venue_page", "render_venue_page")
        cls.legacy_tpl = _fn_src(cls.gen, "render_venue_page", "write_type_landing")

    def test_mission_template_drops_dead_weight(self):
        for needle in DEAD_WEIGHT:
            self.assertNotIn(needle, self.mission_tpl, needle)
        for needle in KEEP:
            self.assertIn(needle, self.mission_tpl, needle)
        self.assertIn("MISSION_UI_JS_VER", self.mission_tpl)
        self.assertEqual(MISSION_UI_JS_VER, "19")

    def test_legacy_fallback_also_drops_catalog_and_print_kit(self):
        for needle in (
            "/field-pack/js/catalog.js",
            "/field-pack/js/print-kit.js",
            'id="print-sheet"',
            'id="treasure-sheet"',
        ):
            self.assertNotIn(needle, self.legacy_tpl, needle)

    def test_mission_ui_fetches_shared_hunt_json(self):
        self.assertIn("/field-pack/data/challenges.json", self.ui)
        self.assertIn("/field-pack/data/wonders.json", self.ui)
        self.assertIn("function waitForPrintImages", self.ui)
        self.assertNotIn("window.FPPrint && typeof window.FPPrint.waitForPrintImages", self.ui)

    def test_shared_hunt_json_still_exists(self):
        challenges = json.loads((FP / "data" / "challenges.json").read_text(encoding="utf-8"))
        wonders = json.loads((FP / "data" / "wonders.json").read_text(encoding="utf-8"))
        self.assertIn("challenges", challenges)
        self.assertGreater(len(challenges["challenges"]), 3)
        self.assertIn("wonders", wonders)
        self.assertGreater(len(wonders["wonders"]), 3)

    def test_sample_pages_match_slim_payload(self):
        for slug in SAMPLE:
            html = (FP / slug / "index.html").read_text(encoding="utf-8")
            with self.subTest(slug=slug):
                for needle in DEAD_WEIGHT:
                    self.assertNotIn(needle, html, needle)
                for needle in KEEP:
                    self.assertIn(needle, html, needle)
                self.assertIn(f"mission-ui.js?v={MISSION_UI_JS_VER}", html)

    def test_every_generated_venue_page_is_slim(self):
        missing = []
        fat = []
        for path in sorted(VENUE_DATA.glob("*.json")):
            slug = path.stem
            page = FP / slug / "index.html"
            if not page.is_file():
                missing.append(slug)
                continue
            html = page.read_text(encoding="utf-8")
            if any(n in html for n in DEAD_WEIGHT):
                fat.append(slug)
        self.assertFalse(missing, f"venue pages missing: {missing[:8]}")
        self.assertFalse(fat, f"venue pages still ship dead weight: {fat[:8]}")


if __name__ == "__main__":
    unittest.main()
