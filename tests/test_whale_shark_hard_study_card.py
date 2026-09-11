"""Whale shark Hard study-card: Park Ranger, no teach, 5 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_LION,
    PUSH_FURTHER_MANTA_RAY,
    PUSH_FURTHER_SHARK,
    PUSH_FURTHER_STINGRAY,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_SHARK,
    TALK_ABOUT_STINGRAY,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_SHARK,
    WIKI_STINGRAY,
    WIKI_WHALE_SHARK,
    correct_choice_text,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_talk_html,
    target_letter_for_deck_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
STINGRAY = FP / "cards" / "stingray" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
SHARK = FP / "cards" / "shark" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_SLOTS = 5

HARD_STEMS = (
    "Where does the whale shark sit in the shark family tree, if we keep names soft?",
    "How does a whale shark’s filter gear work beyond “open mouth and swim”?",
    "How has the IUCN listed the whale shark recently, if we treat the letter as a snapshot?",
    "Why do whale sharks sometimes gather in the same coastal spots year after year?",
    "What are a whale shark’s teeth like, compared with a great white’s big biting teeth?",
)

HARD_IDS = (
    "rhincodontidae-soft",
    "gill-pads-suction-soft",
    "endangered-soft",
    "migration-aggregations-soft",
    "tiny-tooth-rows-soft",
)

EASY_STEMS = (
    "What size record does the whale shark hold among living fish?",
    "Is a whale shark a whale?",
    "How does a whale shark mostly get its food?",
    "What is special about a whale shark’s pattern?",
    "Does a whale shark’s huge size mean it hunts people?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    " kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "CITES",
    "histotroph",
    "uterine milk",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class WhaleSharkHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("whale-shark", study_card_ids())
        self.assertEqual(shipped_levels_for("whale-shark"), ("easy", "hard"))
        self.assertIsNone(study_deck_for("whale-shark", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("whale-shark", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_WHALE_SHARK)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Whale shark.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], [])
        self.assertEqual(deck["push_further"], [])
        self.assertEqual(len(deck["questions"]), HARD_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(
            letters,
            [target_letter_for_deck_slot("whale-shark", "hard", i) for i in range(1, 6)],
        )
        self.assertEqual(letters, ["A", "B", "C", "A", "A"])
        self.assertEqual(letters.count("A"), 3)
        self.assertEqual(letters.count("B"), 1)
        self.assertEqual(letters.count("C"), 1)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("whale-shark", "easy")
        hard = study_deck_for("whale-shark", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("whale-shark", "hard")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 6)))
        self.assertEqual([q["id"] for q in questions], list(HARD_IDS))
        self.assertEqual([q["stem"] for q in questions], list(HARD_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("rhincodontidae", correct_choice_text(questions[0]).lower())
        self.assertIn("rhincodon", correct_choice_text(questions[0]).lower())
        self.assertIn("orectolobiformes", correct_choice_text(questions[0]).lower())
        self.assertIn("gill pads", correct_choice_text(questions[1]).lower())
        self.assertIn("suction", correct_choice_text(questions[1]).lower())
        self.assertIn("endangered", correct_choice_text(questions[2]).lower())
        self.assertIn("ningaloo", correct_choice_text(questions[3]).lower())
        self.assertIn("yucatán", correct_choice_text(questions[3]).lower())
        self.assertIn("tiny teeth", correct_choice_text(questions[4]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        self.assertIn("iucn", blob.lower())
        self.assertIn("filter pads", blob.lower())
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("whale-shark", "hard")
        easy = study_deck_for("whale-shark", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn('<details class="study-teach">', html)
        self.assertNotIn('<details class="study-teach" open', html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertNotIn("Zoologist", html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertNotIn('data-study-pick="zoologist"', html)
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
        deck = study_deck_for("whale-shark", "hard")
        sheet = study_print_html(
            deck,
            name="Whale shark",
            emoji="🦈",
            photo="/field-pack/photos/whale-shark.jpg?v=img2",
            photo_pos="50% 48%",
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
        self.assertNotIn("Talk about it", back)
        self.assertNotIn("Push further", back)
        self.assertNotIn("ps-study-deepen", back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_WHALE_SHARK, sheet)
        self.assertIn("Facts from Wikipedia, Whale shark.", sheet)
        for stem in HARD_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS:
            self.assertNotIn(stem, sheet)
        self.assertIn("rhincodontidae", sheet.lower())
        self.assertIn("gill pads", sheet.lower())

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
        self.assertEqual(shipped_levels_for("stingray"), ("easy", "hard", "zoologist"))
        ray_hard = study_deck_for("stingray", "hard")
        self.assertEqual(ray_hard["source"], WIKI_STINGRAY)
        ray_html = STINGRAY.read_text(encoding="utf-8")
        self.assertIn("Zoologist", ray_html)
        self.assertEqual(ray_hard["talk_about"], list(TALK_ABOUT_STINGRAY))
        self.assertEqual(ray_hard["push_further"], list(PUSH_FURTHER_STINGRAY))
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        manta_hard = study_deck_for("manta-ray", "hard")
        self.assertEqual(manta_hard["source"], WIKI_MANTA_RAY)
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", manta_html)
        self.assertEqual(manta_hard["talk_about"], list(TALK_ABOUT_MANTA_RAY))
        self.assertEqual(manta_hard["push_further"], list(PUSH_FURTHER_MANTA_RAY))
        self.assertEqual(shipped_levels_for("shark"), ("easy", "hard", "zoologist"))
        shark_hard = study_deck_for("shark", "hard")
        self.assertEqual(shark_hard["source"], WIKI_SHARK)
        shark_html = SHARK.read_text(encoding="utf-8")
        self.assertIn("Zoologist", shark_html)
        self.assertEqual(shark_hard["talk_about"], list(TALK_ABOUT_SHARK))
        self.assertEqual(shark_hard["push_further"], list(PUSH_FURTHER_SHARK))
        ray = STINGRAY.read_text(encoding="utf-8")
        self.assertNotIn("rhincodontidae-soft", ray)
        self.assertNotIn("tiny-tooth-rows-soft", ray)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["whale-shark"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), HARD_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertNotIn("zoologist", payload["whale-shark"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("whale-shark", data_js)
        self.assertIn("rhincodontidae-soft", data_js)
        self.assertIn("tiny-tooth-rows-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = WHALE_SHARK.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertNotIn("Zoologist", html)
        self.assertNotIn('data-study-pick="zoologist"', html)
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
        self.assertNotIn("Zoologist", print_tpl)
        for stem in HARD_STEMS:
            self.assertNotIn(stem, print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertNotIn("Talk about it", front)
        self.assertNotIn("Talk about it", back)
        self.assertNotIn("Push further", back)
        hard_html = study_talk_html(study_deck_for("whale-shark", "hard"))
        self.assertNotIn("study-teach", hard_html)
        self.assertNotIn('<details class="study-explore', hard_html)
        self.assertNotIn("Explore more", hard_html)
        self.assertNotIn("Talk about it", hard_html)
        self.assertNotIn("Push further", hard_html)
        self.assertIn("Park Ranger", hard_html)
        self.assertIn("Junior Ranger", hard_html)
        self.assertNotIn("Zoologist", hard_html)
        self.assertIn(">0</span>/5", hard_html)


if __name__ == "__main__":
    unittest.main()
