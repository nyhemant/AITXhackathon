"""Status-letter talk stays on Zoologist, not Junior Ranger or Park Ranger."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from study_cards import (  # noqa: E402
    PUSH_FURTHER_FRESHWATER_FISH,
    PUSH_FURTHER_GORILLA,
    PUSH_FURTHER_KELP_FOREST,
    TALK_ABOUT_GIANT_PANDA,
    TALK_ABOUT_RING_TAILED_LEMUR,
    study_deck_for,
    study_talk_html,
)


class StudyPromptGateTests(unittest.TestCase):
    def test_gorilla_threat_letter_is_zoologist_only(self):
        easy = study_deck_for("western-lowland-gorilla", "easy")
        hard = study_deck_for("western-lowland-gorilla", "hard")
        zoo = study_deck_for("western-lowland-gorilla", "zoologist")
        self.assertTrue(any("threat letter" in line.lower() for line in PUSH_FURTHER_GORILLA))
        for deck in (easy, hard):
            blob = " ".join(deck["talk_about"] + deck["push_further"]).lower()
            self.assertNotIn("threat letter", blob)
        self.assertTrue(any("threat letter" in line.lower() for line in zoo["push_further"]))

    def test_named_status_lines_hide_below_zoologist(self):
        cases = (
            ("giant-panda", "easy", "threat letter"),
            ("ring-tailed-lemur", "easy", "status letter"),
            ("freshwater-fish", "hard", "iucn"),
            ("kelp-forest", "easy", "iucn"),
        )
        self.assertTrue(any("threat letter" in line.lower() for line in TALK_ABOUT_GIANT_PANDA))
        self.assertTrue(any("status letter" in line.lower() for line in TALK_ABOUT_RING_TAILED_LEMUR))
        self.assertTrue(any("iucn" in line.lower() for line in PUSH_FURTHER_FRESHWATER_FISH))
        self.assertTrue(any("iucn" in line.lower() for line in PUSH_FURTHER_KELP_FOREST))
        for cid, level, needle in cases:
            deck = study_deck_for(cid, level)
            blob = " ".join(deck["talk_about"] + deck["push_further"]).lower()
            self.assertNotIn(needle, blob, f"{cid} {level}")
            zoo = study_deck_for(cid, "zoologist")
            zoo_blob = " ".join(zoo["talk_about"] + zoo["push_further"]).lower()
            self.assertIn(needle, zoo_blob, f"{cid} zoologist")

    def test_young_tiers_do_not_advertise_an_ungated_jump(self):
        easy = study_talk_html(study_deck_for("galapagos-tortoise", "easy"))
        hard = study_talk_html(study_deck_for("galapagos-tortoise", "hard"))
        zoo = study_talk_html(study_deck_for("galapagos-tortoise", "zoologist"))
        self.assertIn("A grown-up can help you try a harder set.", easy)
        self.assertIn("Zoologist is a bigger step. A grown-up can help.", hard)
        self.assertNotIn("Jump to a harder set any time.", easy)
        self.assertNotIn("Jump to a harder set any time.", hard)
        self.assertNotIn("Jump to a harder set any time.", zoo)
        self.assertNotIn("study-level-note", zoo)
        self.assertIn('data-study-pick="zoologist"', easy)


if __name__ == "__main__":
    unittest.main()
