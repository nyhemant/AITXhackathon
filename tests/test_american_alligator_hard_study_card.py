"""American alligator Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_AMERICAN_ALLIGATOR,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_SEA_OTTER,
    STUDY_SLOTS,
    TALK_ABOUT_AMERICAN_ALLIGATOR,
    TALK_ABOUT_LION,
    TALK_ABOUT_SEA_OTTER,
    WIKI_AMERICAN_ALLIGATOR,
    WIKI_LION,
    WIKI_SEA_OTTER,
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
GATOR = FP / "cards" / "american-alligator" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
OTTER = FP / "cards" / "sea-otter" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "How can snout shape help you tell an American alligator from an American crocodile?",
    "Why do American alligators stick to fresher water more than American crocodiles?",
    "How do American alligators handle cooler weather compared with American crocodiles?",
    "What can nest temperature help decide for baby alligators?",
    "What extra kind of sound can a male alligator send during courtship?",
    "Besides bellows, what is another loud social display?",
    "How can alligator holes reshape a wetland in a drought?",
    "How should we read the IUCN letter for American alligators?",
    "How many living alligator species are there?",
    "What do international CITES trade rules say for American alligators?",
)

HARD_IDS = (
    "u-snout-vs-crocs-soft",
    "fresher-water-soft",
    "cooler-ok-soft",
    "temperature-sex-soft",
    "infrasound-soft",
    "head-slap-soft",
    "engineer-deepen-soft",
    "lc-recovery-soft",
    "two-living-alligators-soft",
    "cites-ii-soft",
)

EASY_STEMS = (
    "Where do American alligators live in the wild?",
    "How do American alligators power their swimming?",
    "What covers an American alligator’s back?",
    "What do American alligators use their strong jaws for?",
    "Why do American alligators bellow?",
    "How do alligator moms make a nest?",
    "What do baby alligators often look like when they hatch?",
    "What can a gator hole do in dry times?",
    "Why do healthy freshwater wetlands matter?",
    "Do alligator moms leave their eggs like many reptiles?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "88.7",
    "90.5",
    "94.1",
    "31.5",
    "32.5",
    "33.5",
    "34.5",
    "mississippiensis",
    "sinensis",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "mississippiensis",
    "sinensis",
    "Alligatoridae",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class AmericanAlligatorHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("american-alligator", study_card_ids())
        self.assertEqual(shipped_levels_for("american-alligator"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("american-alligator", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("american-alligator", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_AMERICAN_ALLIGATOR)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, American alligator.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_AMERICAN_ALLIGATOR))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_AMERICAN_ALLIGATOR))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("american-alligator", "easy")
        hard = study_deck_for("american-alligator", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("american-alligator", "hard")
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
        self.assertIn("u-shaped", correct_choice_text(questions[0]).lower())
        self.assertIn("narrower v", correct_choice_text(questions[0]).lower())
        self.assertIn("freshwater", correct_choice_text(questions[1]).lower())
        self.assertIn("salt", correct_choice_text(questions[1]).lower())
        self.assertIn("cooler", correct_choice_text(questions[2]).lower())
        self.assertIn("crocodile", correct_choice_text(questions[2]).lower())
        self.assertIn("male or female", correct_choice_text(questions[3]).lower())
        self.assertIn("infrasound", correct_choice_text(questions[4]).lower())
        self.assertIn("ripple", correct_choice_text(questions[4]).lower())
        self.assertIn("head-slap", correct_choice_text(questions[5]).lower())
        self.assertIn("reshape", correct_choice_text(questions[6]).lower())
        self.assertIn("drought", correct_choice_text(questions[6]).lower())
        self.assertIn("least concern", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[7]).lower())
        self.assertIn("two living", correct_choice_text(questions[8]).lower())
        self.assertIn("chinese", correct_choice_text(questions[8]).lower())
        self.assertIn("appendix ii", correct_choice_text(questions[9]).lower())
        self.assertIn("trade", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("american-alligator", "hard")
        easy = study_deck_for("american-alligator", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "american-alligator", "packTemplate": "animals"})
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
        deck = study_deck_for("american-alligator", "hard")
        sheet = study_print_html(
            deck,
            name="American alligator",
            emoji="🐊",
            photo="/field-pack/photos/american-alligator.jpg?v=img2",
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
        for prompt in TALK_ABOUT_AMERICAN_ALLIGATOR + PUSH_FURTHER_AMERICAN_ALLIGATOR:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_AMERICAN_ALLIGATOR, sheet)
        self.assertIn("Facts from Wikipedia, American alligator.", sheet)
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
        self.assertEqual(shipped_levels_for("sea-otter"), ("easy", "hard", "zoologist"))
        otter_hard = study_deck_for("sea-otter", "hard")
        self.assertEqual(otter_hard["source"], WIKI_SEA_OTTER)
        otter_html = OTTER.read_text(encoding="utf-8")
        self.assertIn("Zoologist", otter_html)
        self.assertEqual(otter_hard["talk_about"], list(TALK_ABOUT_SEA_OTTER))
        self.assertEqual(otter_hard["push_further"], list(PUSH_FURTHER_SEA_OTTER))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", jelly)
        self.assertNotIn("What do they eat?", jelly)
        self.assertNotIn("u-snout-vs-crocs-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["american-alligator"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["american-alligator"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("american-alligator", data_js)
        self.assertIn("u-snout-vs-crocs-soft", data_js)
        self.assertIn("cites-ii-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = GATOR.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="hard"', html)
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
        hard_html = study_talk_html(study_deck_for("american-alligator", "hard"))
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
