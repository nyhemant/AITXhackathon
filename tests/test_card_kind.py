"""Card kind derivation — hub sections from kind, not hardcoded Wildlife/Parks lists."""

import re
from pathlib import Path
import sys
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from field_pack_card_kind import (  # noqa: E402
    attraction_venue_attribution,
    card_kind,
    card_may_feature,
    card_shows_venue_attribution,
    group_cards_by_hub_section,
)
from field_pack_catalog_kind import load_card_kinds  # noqa: E402

FP = REPO / "static" / "field-pack"
SEALIFE_MISFILED = (
    "whale-shark",
    "cuttlefish",
    "manta-ray",
    "sea-otter",
    "kelp-forest",
    "puffin",
)


class CardKindTests(unittest.TestCase):
    def test_explicit_kind_wins(self):
        self.assertEqual(card_kind({"id": "shark", "kind": "place_feature"}), "place_feature")

    def test_cm_and_sci_are_attractions(self):
        self.assertEqual(card_kind({"id": "cm-art-lab"}), "attraction")
        self.assertEqual(card_kind({"id": "sci-dinosaur", "pt": "exhibits"}), "attraction")

    def test_sea_life_id_is_kind_not_a_hub_list(self):
        self.assertEqual(card_kind({"id": "octopus", "pt": "animals"}), "sea_life")

    def test_tsv_sealife_ids_are_sea_life(self):
        for cid in SEALIFE_MISFILED:
            self.assertEqual(card_kind({"id": cid, "pt": "animals"}), "sea_life", cid)
        grouped = group_cards_by_hub_section(
            [{"id": cid, "pt": "animals"} for cid in SEALIFE_MISFILED]
        )
        self.assertEqual(sorted(c["id"] for c in grouped["sealife"]), sorted(SEALIFE_MISFILED))
        self.assertEqual(grouped["wildlife"], [])

    def test_cards_hub_html_matches_tsv_hub(self):
        hub = (FP / "cards" / "index.html").read_text(encoding="utf-8")
        kinds = load_card_kinds()
        items = re.findall(
            r'<li class="cards-hub-item"[^>]*data-card-id="([^"]+)"[^>]*>',
            hub,
        )
        self.assertTrue(items)
        for cid in items:
            row = kinds.get(cid)
            if not row:
                continue
            want_group = row["hub"]
            want_kind = {
                "wildlife": "animal",
                "sealife": "sea_life",
                "attractions": "attraction",
                "parks": "place_feature",
            }[want_group]
            li = [line for line in hub.splitlines() if f'data-card-id="{cid}"' in line and "cards-hub-item" in line][0]
            self.assertIn(f'data-card-group="{want_group}"', li, cid)
            self.assertIn(f'data-card-kind="{want_kind}"', li, cid)
        wildlife = hub.split('id="cards-wildlife"', 1)[1].split('id="cards-', 1)[0]
        sealife = hub.split('id="cards-sealife"', 1)[1].split('id="cards-', 1)[0]
        for cid in SEALIFE_MISFILED:
            self.assertNotIn(f'data-card-id="{cid}"', wildlife, cid)
            self.assertIn(f'data-card-id="{cid}"', sealife, cid)
        self.assertIn('Wildlife <span class="seo-dir-count">25</span>', hub)
        self.assertIn('Sea life <span class="seo-dir-count">17</span>', hub)
        self.assertNotIn('id="cards-parks"', hub)
        self.assertNotIn('data-card-id="cuyahoga-towpath"', hub)

    def test_landing_showcase_matches_tsv_primary_hub(self):
        landing = (FP / "index.html").read_text(encoding="utf-8")
        showcase = landing.split('id="cat-cards-showcase"', 1)[1].split(
            "<!-- SEO:CARDS-BODY:END -->", 1
        )[0]
        kinds = load_card_kinds()
        primary = {cid for cid, row in kinds.items() if row["hub"] in {"wildlife", "sealife"}}
        tiles = re.findall(
            r'<li class="cat-card-tile"[^>]*data-card-group="([^"]+)"[^>]*data-card-id="([^"]+)"',
            showcase,
        )
        self.assertTrue(tiles)
        seen: set[str] = set()
        for group, cid in tiles:
            row = kinds[cid]
            self.assertEqual(row["hub"], group, cid)
            self.assertIn(group, ("wildlife", "sealife"), cid)
            seen.add(cid)
        self.assertEqual(seen, primary)
        for cid in ("american-bison", "american-alligator", "elk"):
            li = [line for line in showcase.splitlines() if f'data-card-id="{cid}"' in line][0]
            self.assertIn('data-card-group="wildlife"', li, cid)
        for cid in SEALIFE_MISFILED:
            li = [line for line in showcase.splitlines() if f'data-card-id="{cid}"' in line][0]
            self.assertIn('data-card-group="sealife"', li, cid)
        self.assertNotIn('data-card-group="parks"', showcase)
        self.assertNotIn('data-card-filter="parks"', showcase)
        self.assertNotIn('data-card-filter="attractions"', showcase)
        self.assertNotIn("Parks & trails", showcase)
        self.assertNotIn(">Attractions<", showcase)
        self.assertIn("Browse cards", showcase)
        self.assertNotIn("All 58 cards", showcase)
        self.assertNotRegex(showcase, r"All \d+ cards")
        self.assertIn('data-card-count-build="42"', landing)
        self.assertNotIn("cuyahoga-towpath", showcase)
        gen = (REPO / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        self.assertIn("def _landing_primary_cards(", gen)
        self.assertIn("PRIMARY_HUB_SECTION_IDS", gen.split("def _landing_teaser_cards(", 1)[1])

    def test_animal_pack_stays_animal(self):
        self.assertEqual(
            card_kind({"id": "african-lion", "pt": "animals", "venue_type": "zoo"}),
            "animal",
        )

    def test_park_home_venue_is_place_feature_not_towpath_special_case(self):
        self.assertEqual(
            card_kind(
                {
                    "id": "cuyahoga-towpath",
                    "venue_type": "national_park",
                    "photoCredit": "Photo via Wikimedia Commons",
                }
            ),
            "place_feature",
        )
        self.assertEqual(
            card_kind({"id": "some-canal-path", "venue_type": "national_park"}),
            "place_feature",
        )

    def test_hub_sections_derived_from_kind(self):
        cards = [
            {"id": "african-lion", "pt": "animals", "venue_type": "zoo"},
            {"id": "octopus", "pt": "animals"},
            {"id": "cm-art-lab"},
            {"id": "cuyahoga-towpath", "venue_type": "national_park"},
        ]
        grouped = group_cards_by_hub_section(cards)
        self.assertEqual([c["id"] for c in grouped["wildlife"]], ["african-lion"])
        self.assertEqual([c["id"] for c in grouped["sealife"]], ["octopus"])
        self.assertEqual([c["id"] for c in grouped["attractions"]], ["cm-art-lab"])
        self.assertEqual([c["id"] for c in grouped["parks"]], ["cuyahoga-towpath"])

    def test_illustration_may_not_be_featured(self):
        card = {"id": "cm-art-lab", "photoCredit": "Illustration · Field Trip Kit"}
        self.assertFalse(card_may_feature(card))
        self.assertTrue(
            card_may_feature({"id": "african-lion", "photoCredit": "Enhanced for print · Field Trip Kit"})
        )

    def test_attraction_attribution_prefers_catalog_object(self):
        card = {
            "id": "cm-art-lab",
            "venue": "thinkery",
            "venue_attribution": {
                "venue_slug": "childrens-museum-perot",
                "venue_name": "Perot Museum",
            },
        }
        self.assertEqual(
            attraction_venue_attribution(card, {}),
            {"venue_slug": "childrens-museum-perot", "venue_name": "Perot Museum"},
        )

    def test_animal_and_sea_life_hide_venue_attribution(self):
        self.assertFalse(
            card_shows_venue_attribution(
                {"id": "western-lowland-gorilla", "pt": "animals", "venue_type": "zoo"}
            )
        )
        self.assertFalse(
            card_shows_venue_attribution({"id": "giant-panda", "pt": "animals", "venue_type": "zoo"})
        )
        self.assertFalse(card_shows_venue_attribution({"id": "octopus", "pt": "animals"}))
        self.assertTrue(card_shows_venue_attribution({"id": "cm-art-lab"}))
        self.assertTrue(
            card_shows_venue_attribution(
                {"id": "cuyahoga-towpath", "venue_type": "national_park"}
            )
        )
        self.assertTrue(
            card_shows_venue_attribution({"id": "sci-rocket", "pt": "exhibits"})
        )


if __name__ == "__main__":
    unittest.main()
