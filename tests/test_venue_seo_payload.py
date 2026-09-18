"""Venue SEO pages ship the mission drawer without catalog / print-kit dead weight."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    MISSION_UI_JS_VER,
    PUBLIC_VENUE_DROP_KEYS,
    load_bonus_hunts,
    load_mission_venue,
    load_venues,
    public_bonus_hunts_embed,
    public_mission_venue,
    render_mission_venue_page,
)

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
TEMPLATE_KEEP = (
    'id="venue-data"',
    'id="bonus-hunts-data"',
    "/field-pack/js/print-maps.js",
    "/field-pack/js/mission/mission-engine.js",
    "/field-pack/js/mission/mission-ui.js",
    "{drawer}",
    "public_mission_venue",
    "public_bonus_hunts_embed",
)

# Shared type-kit challenge ids shipped in bonus-hunts.json["kits"].
SHARED_KIT_IDS = (
    "zoo_behavior",
    "aq_dive",
    "mu_stop",
    "np_still",
    "sf_far",
)
# Shared bonus / alpha pools — identical on every page if embedded.
SHARED_GENERIC_IDS = (
    "bh_overlook",
    "ah_patience",
)


def _embed_json(html: str, el_id: str) -> dict:
    marker = f'id="{el_id}"'
    start = html.index(marker)
    open_gt = html.index(">", start)
    close = html.index("</script>", open_gt)
    return json.loads(html[open_gt + 1 : close])


def _assert_public_embeds_are_slim(test: unittest.TestCase, html: str, slug: str) -> None:
    venue = _embed_json(html, "venue-data")
    for key in PUBLIC_VENUE_DROP_KEYS:
        test.assertNotIn(key, venue, f"{slug} #venue-data still has {key}")
    bonus = _embed_json(html, "bonus-hunts-data")
    test.assertNotIn("kits", bonus, f"{slug} still embeds shared kits")
    test.assertNotIn("generic", bonus, f"{slug} still embeds shared generic")
    test.assertNotIn("description", bonus)
    alpha = bonus.get("alpha") or {}
    test.assertNotIn("generic", alpha, f"{slug} still embeds shared alpha.generic")
    test.assertLessEqual(len(bonus.get("venues") or {}), 1)
    dumped = json.dumps(bonus)
    for kid in SHARED_KIT_IDS:
        test.assertNotIn(kid, dumped, f"{slug} embed still has kit id {kid}")
    for gid in SHARED_GENERIC_IDS:
        test.assertNotIn(gid, dumped, f"{slug} embed still has shared generic id {gid}")


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
        for needle in TEMPLATE_KEEP:
            self.assertIn(needle, self.mission_tpl, needle)
        self.assertIn("MISSION_UI_JS_VER", self.mission_tpl)
        self.assertEqual(MISSION_UI_JS_VER, "19")
        self.assertNotIn('_bh_slim["kits"]', self.mission_tpl)
        self.assertNotIn('json.dumps(mission_venue, ensure_ascii=False)', self.mission_tpl)

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

    def test_generator_render_is_slim(self):
        venues = {row["id"]: row for row in load_venues()}
        v = venues["dallas-zoo"]
        mission = load_mission_venue("dallas-zoo")
        html = render_mission_venue_page(v, mission)
        for needle in DEAD_WEIGHT:
            self.assertNotIn(needle, html, needle)
        for needle in KEEP:
            self.assertIn(needle, html, needle)
        self.assertIn(f"mission-ui.js?v={MISSION_UI_JS_VER}", html)
        _assert_public_embeds_are_slim(self, html, "dallas-zoo")
        self.assertIn("dallas-zoo", (_embed_json(html, "bonus-hunts-data").get("venues") or {}))

    def test_public_helpers_drop_authoring_and_shared_kits(self):
        raw = load_mission_venue("dallas-zoo")
        self.assertIsNotNone(raw)
        self.assertIn("research_notes", raw)
        self.assertIn("presence_sources", raw)
        pub = public_mission_venue(raw)
        for key in PUBLIC_VENUE_DROP_KEYS:
            self.assertNotIn(key, pub)
        self.assertEqual(pub["slug"], "dallas-zoo")
        self.assertIn("bonus_hunt", pub)
        self.assertIn("items", pub)

        bonus_all = load_bonus_hunts()
        self.assertIn("kits", bonus_all)
        self.assertIn("generic", bonus_all)
        slim = public_bonus_hunts_embed(bonus_all, "dallas-zoo", raw)
        self.assertNotIn("kits", slim)
        self.assertNotIn("generic", slim)
        self.assertEqual(set(slim["venues"]), {"dallas-zoo"})
        dumped = json.dumps(slim)
        for kid in SHARED_KIT_IDS:
            self.assertNotIn(kid, dumped)

    def test_authoring_json_stays_on_disk(self):
        disk = json.loads((VENUE_DATA / "dallas-zoo.json").read_text(encoding="utf-8"))
        self.assertIn("research_notes", disk)
        self.assertIn("presence_sources", disk)
        bonus = json.loads((FP / "data" / "bonus-hunts.json").read_text(encoding="utf-8"))
        self.assertIn("kits", bonus)
        self.assertIn("zoo", bonus["kits"])
        self.assertIn("generic", bonus)

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
                _assert_public_embeds_are_slim(self, html, slug)

    def test_every_generated_venue_page_is_slim(self):
        missing = []
        fat = []
        authoring = []
        shared_kits = []
        for path in sorted(VENUE_DATA.glob("*.json")):
            slug = path.stem
            page = FP / slug / "index.html"
            if not page.is_file():
                missing.append(slug)
                continue
            html = page.read_text(encoding="utf-8")
            if any(n in html for n in DEAD_WEIGHT):
                fat.append(slug)
            try:
                venue = _embed_json(html, "venue-data")
                bonus = _embed_json(html, "bonus-hunts-data")
            except (ValueError, json.JSONDecodeError):
                fat.append(slug)
                continue
            if any(k in venue for k in PUBLIC_VENUE_DROP_KEYS):
                authoring.append(slug)
            if "kits" in bonus or "generic" in bonus or "generic" in (bonus.get("alpha") or {}):
                shared_kits.append(slug)
        self.assertFalse(missing, f"venue pages missing: {missing[:8]}")
        self.assertFalse(fat, f"venue pages still ship dead weight: {fat[:8]}")
        self.assertFalse(authoring, f"venue pages still embed authoring fields: {authoring[:8]}")
        self.assertFalse(shared_kits, f"venue pages still embed shared kits: {shared_kits[:8]}")


if __name__ == "__main__":
    unittest.main()
