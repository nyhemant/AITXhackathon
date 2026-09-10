"""Study-card answer keys must not monopolize one letter."""

from __future__ import annotations

import json
import sys
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from study_cards import (  # noqa: E402
    LETTERS,
    MAX_OVERALL_B_SHARE,
    MAX_SAME_LETTER_PER_DECK,
    PUSH_FURTHER_CHEETAH,
    PUSH_FURTHER_CHIMPANZEE,
    PUSH_FURTHER_GIANT_PANDA,
    PUSH_FURTHER_GORILLA,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_KOALA,
    PUSH_FURTHER_ORANGUTAN,
    PUSH_FURTHER_OSTRICH,
    PUSH_FURTHER_RED_PANDA,
    PUSH_FURTHER_RING_TAILED_LEMUR,
    PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER,
    PUSH_FURTHER_SHARK,
    PUSH_FURTHER_TWO_TOED_SLOTH,
    PUSH_FURTHER_FRESHWATER_FISH,
    PUSH_FURTHER_AMERICAN_ALLIGATOR,
    PUSH_FURTHER_AMERICAN_BISON,
    PUSH_FURTHER_ELK,
    PUSH_FURTHER_PUFFIN,
    PUSH_FURTHER_POLAR_BEAR,
    PUSH_FURTHER_SEA_OTTER,
    PUSH_FURTHER_WARTHOG,
    PUSH_FURTHER_TIGER,
    PUSH_FURTHER_TORTOISE,
    STUDY_SLOTS,
    TALK_ABOUT_CHEETAH,
    TALK_ABOUT_CHIMPANZEE,
    TALK_ABOUT_GIANT_PANDA,
    TALK_ABOUT_GORILLA,
    TALK_ABOUT_KOALA,
    TALK_ABOUT_LION,
    TALK_ABOUT_ORANGUTAN,
    TALK_ABOUT_OSTRICH,
    TALK_ABOUT_RED_PANDA,
    TALK_ABOUT_RING_TAILED_LEMUR,
    TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER,
    TALK_ABOUT_SHARK,
    TALK_ABOUT_TWO_TOED_SLOTH,
    TALK_ABOUT_FRESHWATER_FISH,
    TALK_ABOUT_AMERICAN_ALLIGATOR,
    TALK_ABOUT_AMERICAN_BISON,
    TALK_ABOUT_ELK,
    TALK_ABOUT_PUFFIN,
    TALK_ABOUT_POLAR_BEAR,
    TALK_ABOUT_SEA_OTTER,
    TALK_ABOUT_WARTHOG,
    TALK_ABOUT_TIGER,
    TALK_ABOUT_TORTOISE,
    correct_choice_text,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    target_letter_for_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
STUDY_JSON = FP / "data" / "study-cards.json"
TRAFFIC_IDS = (
    "african-lion",
    "reticulated-giraffe",
    "african-elephant",
    "african-penguin",
    "caribbean-flamingo",
    "galapagos-tortoise",
    "zebra",
    "nile-hippo",
    "sumatran-tiger",
    "western-lowland-gorilla",
    "cheetah",
    "red-panda",
    "koala",
    "chimpanzee",
    "orangutan",
    "giant-panda",
    "ring-tailed-lemur",
    "ostrich",
    "warthog",
    "shark",
    "asian-small-clawed-otter",
    "two-toed-sloth",
    "freshwater-fish",
    "polar-bear",
    "sea-otter",
    "american-alligator",
    "american-bison",
    "elk",
    "puffin",
)


def _decks():
    for card_id in TRAFFIC_IDS:
        for level in shipped_levels_for(card_id):
            deck = study_deck_for(card_id, level)
            yield card_id, level, deck


class StudyCardAnswerKeyTests(unittest.TestCase):
    def test_traffic_set_is_twenty_nine_animals(self):
        self.assertEqual(tuple(study_card_ids()), TRAFFIC_IDS)
        self.assertEqual(shipped_levels_for("cheetah"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("cheetah", "zoologist"))
        self.assertEqual(shipped_levels_for("red-panda"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("red-panda", "hard"))
        self.assertIsNotNone(study_deck_for("red-panda", "zoologist"))
        self.assertEqual(shipped_levels_for("koala"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("koala", "hard"))
        self.assertIsNotNone(study_deck_for("koala", "zoologist"))
        self.assertEqual(shipped_levels_for("chimpanzee"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("chimpanzee", "hard"))
        self.assertIsNotNone(study_deck_for("chimpanzee", "zoologist"))
        self.assertEqual(shipped_levels_for("orangutan"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("orangutan", "hard"))
        self.assertIsNotNone(study_deck_for("orangutan", "zoologist"))
        self.assertEqual(shipped_levels_for("giant-panda"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("giant-panda", "hard"))
        self.assertIsNotNone(study_deck_for("giant-panda", "zoologist"))
        self.assertEqual(shipped_levels_for("ring-tailed-lemur"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("ring-tailed-lemur", "hard"))
        self.assertIsNotNone(study_deck_for("ring-tailed-lemur", "zoologist"))
        self.assertEqual(shipped_levels_for("ostrich"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("ostrich", "hard"))
        self.assertIsNotNone(study_deck_for("ostrich", "zoologist"))
        self.assertEqual(shipped_levels_for("warthog"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("warthog", "hard"))
        self.assertIsNotNone(study_deck_for("warthog", "zoologist"))
        self.assertEqual(shipped_levels_for("shark"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("shark", "hard"))
        self.assertIsNotNone(study_deck_for("shark", "zoologist"))
        self.assertEqual(shipped_levels_for("asian-small-clawed-otter"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("asian-small-clawed-otter", "hard"))
        self.assertIsNotNone(study_deck_for("asian-small-clawed-otter", "zoologist"))
        self.assertEqual(shipped_levels_for("two-toed-sloth"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("two-toed-sloth", "hard"))
        self.assertIsNotNone(study_deck_for("two-toed-sloth", "zoologist"))
        self.assertEqual(shipped_levels_for("freshwater-fish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("freshwater-fish", "hard"))
        self.assertIsNotNone(study_deck_for("freshwater-fish", "zoologist"))
        self.assertEqual(shipped_levels_for("polar-bear"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("polar-bear", "hard"))
        self.assertIsNotNone(study_deck_for("polar-bear", "zoologist"))
        self.assertEqual(shipped_levels_for("sea-otter"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("sea-otter", "hard"))
        self.assertIsNotNone(study_deck_for("sea-otter", "zoologist"))
        self.assertEqual(shipped_levels_for("american-alligator"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("american-alligator", "hard"))
        self.assertIsNotNone(study_deck_for("american-alligator", "zoologist"))
        self.assertEqual(shipped_levels_for("american-bison"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("american-bison", "hard"))
        self.assertIsNotNone(study_deck_for("american-bison", "zoologist"))
        self.assertEqual(shipped_levels_for("elk"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("elk", "hard"))
        self.assertIsNotNone(study_deck_for("elk", "zoologist"))
        self.assertEqual(shipped_levels_for("puffin"), ("easy",))
        self.assertIsNone(study_deck_for("puffin", "hard"))
        self.assertIsNone(study_deck_for("puffin", "zoologist"))
        decks = list(_decks())
        self.assertEqual(len(decks), 85)
        for card_id, level, deck in decks:
            self.assertIsNotNone(deck, f"{card_id}/{level}")
            self.assertEqual(validate_deck(deck), [])
            self.assertEqual(len(deck["questions"]), STUDY_SLOTS)

    def test_slot_rotation_maps_correct_letter_without_dropping_texts(self):
        for card_id, level, deck in _decks():
            for q in deck["questions"]:
                self.assertEqual(
                    q["correct"],
                    target_letter_for_slot(q["slot"]),
                    f"{card_id}/{level} slot {q['slot']}",
                )
                self.assertEqual(len(q["choices"]), 3)
                self.assertEqual(len(set(q["choices"])), 3)
                self.assertTrue(correct_choice_text(q).strip())

    def test_no_deck_has_more_than_six_of_the_same_letter(self):
        for card_id, level, deck in _decks():
            counts = Counter(q["correct"] for q in deck["questions"])
            for letter in LETTERS:
                self.assertLessEqual(
                    counts[letter],
                    MAX_SAME_LETTER_PER_DECK,
                    f"{card_id}/{level} has {counts[letter]} {letter}s: {counts}",
                )
            self.assertTrue(all(counts[letter] >= 3 for letter in LETTERS), counts)

    def test_overall_correct_b_is_not_a_majority(self):
        letters = [q["correct"] for _, _, deck in _decks() for q in deck["questions"]]
        self.assertEqual(len(letters), 850)
        share_b = letters.count("B") / len(letters)
        self.assertLessEqual(
            share_b,
            MAX_OVERALL_B_SHARE,
            f"correct==B is {share_b:.1%} ({letters.count('B')}/850)",
        )
        for letter in LETTERS:
            share = letters.count(letter) / len(letters)
            self.assertGreaterEqual(share, 0.25, f"{letter} is only {share:.1%}")

    def test_tiger_gorilla_cheetah_red_panda_koala_chimpanzee_orangutan_giant_panda_lemur_and_ostrich_explore_more_stay_kid_short(self):
        dense = (
            "Laverania",
            "incomplete lineage sorting",
            "sondaica",
            "studbook",
            "vestibular",
            "Ice Age",
            "microsatellite",
            "MHC",
            "Miracinonyx",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_TORTOISE + PUSH_FURTHER_TORTOISE
        peer_max = max(len(line) for line in peer)
        lines = (
            TALK_ABOUT_TIGER
            + PUSH_FURTHER_TIGER
            + TALK_ABOUT_GORILLA
            + PUSH_FURTHER_GORILLA
            + TALK_ABOUT_CHEETAH
            + PUSH_FURTHER_CHEETAH
            + TALK_ABOUT_RED_PANDA
            + PUSH_FURTHER_RED_PANDA
            + TALK_ABOUT_KOALA
            + PUSH_FURTHER_KOALA
            + TALK_ABOUT_CHIMPANZEE
            + PUSH_FURTHER_CHIMPANZEE
            + TALK_ABOUT_ORANGUTAN
            + PUSH_FURTHER_ORANGUTAN
            + TALK_ABOUT_GIANT_PANDA
            + PUSH_FURTHER_GIANT_PANDA
            + TALK_ABOUT_RING_TAILED_LEMUR
            + PUSH_FURTHER_RING_TAILED_LEMUR
            + TALK_ABOUT_OSTRICH
            + PUSH_FURTHER_OSTRICH
            + TALK_ABOUT_WARTHOG
            + PUSH_FURTHER_WARTHOG
            + TALK_ABOUT_SHARK
            + PUSH_FURTHER_SHARK
            + TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER
            + PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER
            + TALK_ABOUT_TWO_TOED_SLOTH
            + PUSH_FURTHER_TWO_TOED_SLOTH
            + TALK_ABOUT_FRESHWATER_FISH
            + PUSH_FURTHER_FRESHWATER_FISH
            + TALK_ABOUT_POLAR_BEAR
            + PUSH_FURTHER_POLAR_BEAR
            + TALK_ABOUT_SEA_OTTER
            + PUSH_FURTHER_SEA_OTTER
            + TALK_ABOUT_AMERICAN_ALLIGATOR
            + PUSH_FURTHER_AMERICAN_ALLIGATOR
            + TALK_ABOUT_AMERICAN_BISON
            + PUSH_FURTHER_AMERICAN_BISON
            + TALK_ABOUT_ELK
            + PUSH_FURTHER_ELK
            + TALK_ABOUT_PUFFIN
            + PUSH_FURTHER_PUFFIN
        )
        for line in lines:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)

    def test_published_json_matches_rotated_decks(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        for card_id, level, deck in _decks():
            published = payload[card_id]["levels"][level]["questions"]
            self.assertEqual(
                [q["correct"] for q in published],
                [q["correct"] for q in deck["questions"]],
            )
            self.assertEqual(
                [q["choices"] for q in published],
                [q["choices"] for q in deck["questions"]],
            )


if __name__ == "__main__":
    unittest.main()
