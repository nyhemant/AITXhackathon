"""Card kind derivation — hub sections from kind, not hardcoded Wildlife/Parks lists."""

from pathlib import Path
import sys
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from field_pack_card_kind import (  # noqa: E402
    attraction_venue_attribution,
    card_kind,
    card_may_feature,
    group_cards_by_hub_section,
)


class CardKindTests(unittest.TestCase):
    def test_explicit_kind_wins(self):
        self.assertEqual(card_kind({"id": "shark", "kind": "place_feature"}), "place_feature")

    def test_cm_and_sci_are_attractions(self):
        self.assertEqual(card_kind({"id": "cm-art-lab"}), "attraction")
        self.assertEqual(card_kind({"id": "sci-dinosaur", "pt": "exhibits"}), "attraction")

    def test_sea_life_id_is_kind_not_a_hub_list(self):
        self.assertEqual(card_kind({"id": "octopus", "pt": "animals"}), "sea_life")

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


if __name__ == "__main__":
    unittest.main()
