"""Freshwater fish Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import outing_talk_html  # noqa: E402
from study_cards import (  # noqa: E402
    PUSH_FURTHER_FRESHWATER_FISH,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_TWO_TOED_SLOTH,
    STUDY_SLOTS,
    TALK_ABOUT_FRESHWATER_FISH,
    TALK_ABOUT_LION,
    TALK_ABOUT_TWO_TOED_SLOTH,
    WIKI_FRESHWATER_FISH,
    WIKI_LION,
    WIKI_TWO_TOED_SLOTH,
    correct_choice_text,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_talk_html,
    target_letter_for_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
FISH = FP / "cards" / "freshwater-fish" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
SLOTH = FP / "cards" / "two-toed-sloth" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "How do most freshwater fish keep from swelling up in a pond?",
    "What does the lateral line along a freshwater fish’s side do?",
    "How do many bony freshwater fish stay at the right depth?",
    "What bony cover protects the gills of most bony freshwater fish?",
    "Do some kinds of freshwater fish travel between rivers and the sea?",
    "Can most kinds of freshwater fish live in both a pond and the ocean?",
    "Why do so many different kinds of fish live in fresh water?",
    "Is there one status letter for all freshwater fish?",
    "How can dams, dirty water, and water takeouts hurt freshwater fish?",
    "How can introduced fish and other invaders affect native freshwater fish?",
)

HARD_IDS = (
    "salt-water-balance-soft",
    "lateral-line-soft",
    "swim-bladder-soft",
    "gill-cover-soft",
    "diadromy-soft",
    "stenohaline-soft",
    "scattered-homes-soft",
    "status-by-kind-soft",
    "dams-pollution-soft",
    "invasives-soft",
)

EASY_STEMS = (
    "Where do freshwater fish live?",
    "How is fresh water different from ocean water?",
    "How do freshwater fish get oxygen underwater?",
    "How do fins help freshwater fish move?",
    "How many kinds of fish live in fresh water?",
    "Do freshwater fish wear scales?",
    "How do most freshwater fish handle temperature?",
    "How do many freshwater fish begin life?",
    "What helps freshwater fish stay healthy in the wild?",
    "Do all fish need the ocean to live?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "41.24",
    "83%",
    "teleost",
    "Actinopterygii",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "teleost",
    "Actinopterygii",
    "ray-finned",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class FreshwaterFishHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("freshwater-fish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("freshwater-fish", "zoologist"))
        self.assertNotIn("jellyfish", study_card_ids())
        self.assertIsNone(study_deck_for("jellyfish"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("freshwater-fish", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_FRESHWATER_FISH)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Freshwater fish.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_FRESHWATER_FISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_FRESHWATER_FISH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("freshwater-fish", "easy")
        hard = study_deck_for("freshwater-fish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("freshwater-fish", "hard")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(HARD_IDS))
        self.assertEqual([q["stem"] for q in questions], list(HARD_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("salts", correct_choice_text(questions[0]).lower())
        self.assertIn("dilute", correct_choice_text(questions[0]).lower())
        self.assertIn("drink little", correct_choice_text(questions[0]).lower())
        self.assertIn("water movement", correct_choice_text(questions[1]).lower())
        self.assertIn("nearby motion", correct_choice_text(questions[1]).lower())
        self.assertIn("swim bladder", correct_choice_text(questions[2]).lower())
        self.assertIn("balloon", correct_choice_text(questions[2]).lower())
        self.assertIn("operculum", correct_choice_text(questions[3]).lower())
        self.assertIn("gill cover", correct_choice_text(questions[3]).lower())
        self.assertIn("salmon", correct_choice_text(questions[4]).lower())
        self.assertIn("eels", correct_choice_text(questions[4]).lower())
        self.assertIn("stenohaline", correct_choice_text(questions[5]).lower())
        self.assertIn("fresh or salt", correct_choice_text(questions[5]).lower())
        self.assertIn("lakes", correct_choice_text(questions[6]).lower())
        self.assertIn("river", correct_choice_text(questions[6]).lower())
        self.assertIn("no single letter", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[7]).lower())
        self.assertIn("barriers", correct_choice_text(questions[8]).lower())
        self.assertIn("takeouts", correct_choice_text(questions[8]).lower())
        self.assertIn("introduced", correct_choice_text(questions[9]).lower())
        self.assertIn("native", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("freshwater-fish", "hard")
        easy = study_deck_for("freshwater-fish", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "freshwater-fish", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn('<details class="study-teach">', html)
        self.assertNotIn('<details class="study-teach" open', html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertEqual(html.count('role="group"'), 2)
        self.assertIn("study-level-picker-bottom", html)
        self.assertIn('aria-label="Study level at the end"', html)
        for stem in HARD_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_hard_print_is_answer_light_duplex(self):
        deck = study_deck_for("freshwater-fish", "hard")
        sheet = study_print_html(
            deck,
            name="River / lake fish",
            emoji="🐟",
            photo="/field-pack/photos/freshwater-fish.jpg?v=img2",
            photo_pos="50% 35%",
        )
        self.assertIn("Park Ranger", sheet)
        self.assertNotIn("Junior Ranger", sheet)
        self.assertNotIn("Learn first", sheet)
        self.assertNotIn("ps-study-teach", sheet)
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        front, _, back = sheet.partition("ps-study-back")
        self.assertNotIn("Talk about it", front)
        self.assertNotIn("Push further", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        self.assertIn("ps-study-deepen", back)
        for prompt in TALK_ABOUT_FRESHWATER_FISH + PUSH_FURTHER_FRESHWATER_FISH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_FRESHWATER_FISH, sheet)
        self.assertIn("Facts from Wikipedia, Freshwater fish.", sheet)
        for stem in HARD_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS:
            self.assertNotIn(stem, sheet)

    def test_other_animal_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_hard = study_deck_for("african-lion", "hard")
        self.assertEqual(lion_hard["source"], WIKI_LION)
        self.assertIn("Panthera leo", correct_choice_text(lion_hard["questions"][0]))
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)
        self.assertEqual(lion_hard["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion_hard["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("two-toed-sloth"), ("easy", "hard", "zoologist"))
        sloth_hard = study_deck_for("two-toed-sloth", "hard")
        self.assertEqual(sloth_hard["source"], WIKI_TWO_TOED_SLOTH)
        sloth_html = SLOTH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", sloth_html)
        self.assertEqual(sloth_hard["talk_about"], list(TALK_ABOUT_TWO_TOED_SLOTH))
        self.assertEqual(sloth_hard["push_further"], list(PUSH_FURTHER_TWO_TOED_SLOTH))
        jelly = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("salt-water-balance-soft", jelly)
        self.assertIsNone(study_deck_for("jellyfish"))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["freshwater-fish"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["freshwater-fish"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("freshwater-fish", data_js)
        self.assertIn("salt-water-balance-soft", data_js)
        self.assertIn("invasives-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = FISH.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("Learn first", html)
        self.assertIn('class="card-hero-links no-print"', html)
        self.assertIn('class="card-try-next no-print"', html)
        self.assertIn("study-level-picker-bottom", html)
        self.assertNotIn("card-print-note", html)
        self.assertNotIn("One animal sheet — not the hide-and-seek cutouts", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Park Ranger", print_tpl)
        for stem in HARD_STEMS:
            self.assertNotIn(stem, print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        hard_html = study_talk_html(study_deck_for("freshwater-fish", "hard"))
        self.assertNotIn("study-teach", hard_html)
        self.assertIn('<details class="study-explore', hard_html)
        self.assertIn("Explore more", hard_html)
        self.assertLess(hard_html.find("study-foot"), hard_html.find("study-explore"))
        self.assertIn("Talk about it", hard_html)
        self.assertIn("Push further", hard_html)
        self.assertIn("Park Ranger", hard_html)
        self.assertIn("Junior Ranger", hard_html)
        self.assertIn("Zoologist", hard_html)


if __name__ == "__main__":
    unittest.main()
