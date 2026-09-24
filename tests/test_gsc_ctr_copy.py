"""Search snippet copy for pages that already earn impressions."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CARD_SEO,
    SEO_META_DESCRIPTIONS,
    SEO_TITLE_LABELS,
    TYPE_LANDINGS,
    VENUE_TITLE_TAIL,
    meta_for,
    quiet_hero_lead,
    seo_hunt_label,
    title_for,
    venue_streams_public_cams,
)

FP = REPO / "static" / "field-pack"


def _venue(slug: str, name: str, city: str = "Somewhere") -> dict:
    return {"id": slug, "name": name, "city": city, "location": city, "type": "zoo"}


class GscCtrCopyTests(unittest.TestCase):
    def test_shared_template_puts_parent_intent_early(self):
        label = seo_hunt_label(_venue("houston-zoo", "Houston Zoo", "Houston"))
        self.assertEqual(label, f"Houston Zoo for Kids — {VENUE_TITLE_TAIL}")
        self.assertLess(label.index("At-Home"), 60)
        self.assertIn("Printable Hunt", label)
        title = title_for(_venue("san-diego-zoo", "San Diego Zoo", "San Diego"))
        self.assertTrue(title.startswith("San Diego Zoo for Kids — At-Home"))
        self.assertTrue(title.endswith(" · KidZooKit"))
        self.assertLess(title.index("At-Home"), 60)

    def test_query_overrides_match_real_offers(self):
        field = title_for(_venue("field-museum", "Field Museum", "Chicago"))
        self.assertIn("Scavenger Hunt", field)
        self.assertLess(field.lower().index("scavenger hunt"), 60)
        dallas = title_for(_venue("dallas-zoo", "Dallas Zoo", "Dallas"))
        memphis = title_for(_venue("memphis-zoo", "Memphis Zoo", "Memphis"))
        self.assertIn("Field Trip", dallas)
        self.assertIn("Field Trip", memphis)
        self.assertNotIn("cam", dallas.lower())
        self.assertNotIn("webcam", dallas.lower())
        night = title_for(_venue("singapore-night-safari", "Night Safari", "Singapore"))
        self.assertTrue(night.startswith("Singapore Night Safari for Kids"))

    def test_descriptions_do_not_invent_cams(self):
        for slug in (
            "field-museum",
            "dallas-zoo",
            "memphis-zoo",
            "vancouver-aquarium",
            "singapore-night-safari",
            "copenhagen-zoo",
        ):
            desc = meta_for(_venue(slug, slug, "City"))
            self.assertNotIn("live cam", desc.lower(), slug)
            self.assertLessEqual(len(desc), 155, slug)
        field = meta_for(_venue("field-museum", "Field Museum", "Chicago"))
        self.assertIn("scavenger hunt", field.lower())
        dallas = meta_for(_venue("dallas-zoo", "Dallas Zoo", "Dallas"))
        self.assertIn("field trip", dallas.lower())
        self.assertIn("Penguin Cove", dallas)
        memphis = meta_for(_venue("memphis-zoo", "Memphis Zoo", "Memphis"))
        self.assertIn("field trip", memphis.lower())
        self.assertIn("Hippo Camp", memphis)
        self.assertNotIn("Simmons", memphis)
        sd = meta_for(_venue("san-diego-zoo", "San Diego Zoo", "San Diego"))
        self.assertIn("live cams", sd)
        self.assertLessEqual(len(sd), 155)

    def test_cam_flag_follows_venue_json(self):
        self.assertFalse(venue_streams_public_cams({"id": "dallas-zoo"}))
        self.assertFalse(venue_streams_public_cams({"id": "field-museum"}))
        self.assertFalse(venue_streams_public_cams({"id": "memphis-zoo"}))
        self.assertTrue(venue_streams_public_cams({"id": "san-diego-zoo"}))
        self.assertFalse(
            venue_streams_public_cams({"id": "dallas-zoo", "own_public_cams": False})
        )

    def test_field_museum_lead_keeps_t_rex(self):
        lead = quiet_hero_lead(
            {},
            {"tagline": "SUE the T. rex leads Chicago’s natural history hit list."},
        )
        self.assertIn("T. rex", lead)
        self.assertLessEqual(len(lead), 90)

    def test_hub_and_card_snippets(self):
        zoos = next(m for m in TYPE_LANDINGS if m["path"] == "zoos")
        self.assertIn("Zoos for Kids", zoos["title"])
        self.assertEqual(zoos["h1"], "Zoos")
        self.assertEqual(zoos["blurb"], "")
        self.assertIn("printable hunt", zoos["description"].lower())
        self.assertNotIn("live cam", zoos["description"].lower())
        card = CARD_SEO["sci-planet"]
        self.assertIn("for Kids", card["title"])
        self.assertLess(card["title"].index("for Kids"), 60)
        self.assertNotIn("live cam", card["description"].lower())
        self.assertNotIn("scavenger hunt", card["description"].lower())

    def test_override_keys_are_real_pages(self):
        for slug in set(SEO_TITLE_LABELS) | set(SEO_META_DESCRIPTIONS):
            self.assertTrue((FP / slug / "index.html").is_file(), slug)
        self.assertTrue((FP / "cards" / "sci-planet" / "index.html").is_file())


if __name__ == "__main__":
    unittest.main()
