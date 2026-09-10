"""Crab Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_CLOWNFISH,
    PUSH_FURTHER_CRAB,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CLOWNFISH,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_LION,
    WIKI_CLOWNFISH,
    WIKI_CRAB,
    WIKI_LION,
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
CRAB = FP / "cards" / "crab" / "index.html"
OCTOPUS = FP / "cards" / "stingray" / "index.html"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What are “true crabs,” and what body plan do they share?",
    "Which look-alike crabs sit in sister group Anomura, not Brachyura?",
    "What does carcinisation say about crab-like bodies?",
    "Why might king crabs look like true crabs but not be Brachyura?",
    "What are porcelain crabs, and how can they escape?",
    "How is a hermit crab’s rear different from a true crab’s?",
    "Why aren’t horseshoe “crabs” decapod crabs at all?",
    "How wide can crab diets and freshwater homes spread?",
    "How far can crab sizes stretch if we keep exact records soft?",
    "Is there one IUCN letter for “crabs” as a group?",
)

HARD_IDS = (
    "brachyura-soft",
    "anomura-soft",
    "carcinisation-soft",
    "king-from-hermit-soft",
    "porcelain-soft",
    "hermit-shell-soft",
    "chelicerata-deepen-soft",
    "niche-spread-soft",
    "size-extremes-soft",
    "status-by-kind-soft",
)

EASY_STEMS = (
    "What covers a crab’s body?",
    "What do a crab’s front legs often end in?",
    "How do many crabs move?",
    "Where do many crabs like to hide?",
    "How does a crab grow bigger?",
    "Do all crabs look the same size and shape?",
    "Where can crabs live?",
    "What do many crabs eat?",
    "How can people help crabs?",
    "Are horseshoe crabs true crabs?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "6,793",
    "6793",
    "3.7 m",
    "3.8 m",
    "12.5",
    "12 ft",
    "kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "6,793",
    "3.7 m",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class CrabHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("crab", study_card_ids())
        self.assertEqual(shipped_levels_for("crab"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("crab", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("crab", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_CRAB)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Crab.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_CRAB))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_CRAB))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("crab", "easy")
        hard = study_deck_for("crab", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("crab", "hard")
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
        self.assertIn("brachyura", correct_choice_text(questions[0]).lower())
        self.assertIn("7,000", correct_choice_text(questions[0]))
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("carapace", correct_choice_text(questions[0]).lower())
        self.assertIn("anomura", correct_choice_text(questions[1]).lower())
        self.assertIn("hermit", correct_choice_text(questions[1]).lower())
        self.assertIn("king", correct_choice_text(questions[1]).lower())
        self.assertIn("porcelain", correct_choice_text(questions[1]).lower())
        self.assertIn("more than once", correct_choice_text(questions[2]).lower())
        self.assertIn("tucked", correct_choice_text(questions[2]).lower())
        self.assertIn("hermit-crab", correct_choice_text(questions[3]).lower())
        self.assertIn("abdomen", correct_choice_text(questions[3]).lower())
        self.assertIn("anomura", correct_choice_text(questions[4]).lower())
        self.assertIn("squat lobster", correct_choice_text(questions[4]).lower())
        self.assertIn("limb", correct_choice_text(questions[4]).lower())
        self.assertIn("soft rear", correct_choice_text(questions[5]).lower())
        self.assertIn("snail", correct_choice_text(questions[5]).lower())
        self.assertIn("chelicerata", correct_choice_text(questions[6]).lower())
        self.assertIn("mouthparts", correct_choice_text(questions[6]).lower())
        self.assertIn("1,300", correct_choice_text(questions[7]))
        self.assertIn("filter", correct_choice_text(questions[7]).lower())
        self.assertIn("millimeters", correct_choice_text(questions[8]).lower())
        self.assertIn("several meters", correct_choice_text(questions[8]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[9]).lower())
        self.assertIn("horseshoe", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("crab", "hard")
        easy = study_deck_for("crab", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "crab", "packTemplate": "animals"})
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
        deck = study_deck_for("crab", "hard")
        sheet = study_print_html(
            deck,
            name="Crab",
            emoji="🦀",
            photo="/field-pack/photos/crab.jpg?v=img2",
            photo_pos="50% 40%",
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
        for prompt in TALK_ABOUT_CRAB + PUSH_FURTHER_CRAB:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_CRAB, sheet)
        self.assertIn("Facts from Wikipedia, Crab.", sheet)
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
        self.assertEqual(shipped_levels_for("clownfish"), ("easy", "hard", "zoologist"))
        clown_hard = study_deck_for("clownfish", "hard")
        self.assertEqual(clown_hard["source"], WIKI_CLOWNFISH)
        clown_html = CLOWNFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", clown_html)
        self.assertEqual(clown_hard["talk_about"], list(TALK_ABOUT_CLOWNFISH))
        self.assertEqual(clown_hard["push_further"], list(PUSH_FURTHER_CLOWNFISH))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("brachyura-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["crab"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["crab"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("crab", data_js)
        self.assertIn("brachyura-soft", data_js)
        self.assertIn("status-by-kind-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = CRAB.read_text(encoding="utf-8")
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
        hard_html = study_talk_html(study_deck_for("crab", "hard"))
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
