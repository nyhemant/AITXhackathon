"""Eel Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_CUTTLEFISH,
    PUSH_FURTHER_EEL,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CLOWNFISH,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_EEL,
    TALK_ABOUT_LION,
    WIKI_CLOWNFISH,
    WIKI_CRAB,
    WIKI_CUTTLEFISH,
    WIKI_EEL,
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
EEL = FP / "cards" / "eel" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
CRAB = FP / "cards" / "crab" / "index.html"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What order do true eels belong to, if we keep the counts soft?",
    "Which familiar families sit inside true eels?",
    "How do freshwater eels (Anguilla) use rivers and the ocean to spawn?",
    "Where do European and American freshwater eels spawn, if we keep that map soft?",
    "What life-stage names can a freshwater eel pass through before the ocean return?",
    "How can elvers reach habitat upstream of weirs and dams?",
    "Is there one IUCN letter for all eels?",
    "What extra stress sits on freshwater eels besides fishing and farms?",
    "Why aren’t swamp eels and electric eels true eels?",
    "How marine are true eels, if we keep the freshwater exception soft?",
)

HARD_IDS = (
    "anguilliformes-soft",
    "big-families-soft",
    "catadromy-soft",
    "sargasso-soft",
    "life-stages-soft",
    "climb-soft",
    "status-by-kind-soft",
    "fisheries-pressure-soft",
    "look-alikes-soft",
    "mostly-marine-soft",
)

EASY_STEMS = (
    "What is special about an eel’s body?",
    "Which fins do true eels usually skip?",
    "How do eels usually swim?",
    "How many kinds of true eels are there, if we keep the count soft?",
    "Where do most true eels live?",
    "What is an eel’s first baby stage?",
    "What do eel larvae become as they grow?",
    "Where do many eels hide, and when are they active?",
    "How can people help young eels?",
    "Are electric “eels” true eels?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "164",
    "1000 species",
    "1,000",
    "8 suborders",
    "20 families",
    " kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "164",
    "1000 species",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class EelHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("eel", study_card_ids())
        self.assertEqual(shipped_levels_for("eel"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("eel", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("eel", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_EEL)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Eel.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_EEL))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_EEL))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("eel", "easy")
        hard = study_deck_for("eel", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("eel", "hard")
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
        self.assertIn("anguilliformes", correct_choice_text(questions[0]).lower())
        self.assertIn("eight", correct_choice_text(questions[0]).lower())
        self.assertIn("twenty", correct_choice_text(questions[0]).lower())
        self.assertIn("thousand", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("muraenidae", correct_choice_text(questions[1]).lower())
        self.assertIn("congridae", correct_choice_text(questions[1]).lower())
        self.assertIn("ophichthidae", correct_choice_text(questions[1]).lower())
        self.assertIn("anguillidae", correct_choice_text(questions[1]).lower())
        self.assertIn("rivers", correct_choice_text(questions[2]).lower())
        self.assertIn("ocean", correct_choice_text(questions[2]).lower())
        self.assertIn("salmon", correct_choice_text(questions[2]).lower())
        self.assertIn("catadromy", correct_choice_text(questions[2]).lower())
        self.assertIn("sargasso", correct_choice_text(questions[3]).lower())
        self.assertIn("larvae", correct_choice_text(questions[3]).lower())
        self.assertIn("currents", correct_choice_text(questions[3]).lower())
        self.assertIn("leptocephalus", correct_choice_text(questions[4]).lower())
        self.assertIn("glass eel", correct_choice_text(questions[4]).lower())
        self.assertIn("elver", correct_choice_text(questions[4]).lower())
        self.assertIn("yellow", correct_choice_text(questions[4]).lower())
        self.assertIn("silver", correct_choice_text(questions[4]).lower())
        self.assertIn("climb", correct_choice_text(questions[5]).lower())
        self.assertIn("weirs", correct_choice_text(questions[5]).lower())
        self.assertIn("waterfall", correct_choice_text(questions[5]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[6]).lower())
        self.assertIn("european", correct_choice_text(questions[6]).lower())
        self.assertIn("cr", correct_choice_text(questions[6]).lower())
        self.assertIn("american", correct_choice_text(questions[6]).lower())
        self.assertIn("en", correct_choice_text(questions[6]).lower())
        self.assertIn("fished", correct_choice_text(questions[7]).lower())
        self.assertIn("farmed", correct_choice_text(questions[7]).lower())
        self.assertIn("asia", correct_choice_text(questions[7]).lower())
        self.assertIn("europe", correct_choice_text(questions[7]).lower())
        self.assertIn("swamp", correct_choice_text(questions[8]).lower())
        self.assertIn("electric", correct_choice_text(questions[8]).lower())
        self.assertIn("anguilliformes", correct_choice_text(questions[8]).lower())
        self.assertIn("ocean-only", correct_choice_text(questions[9]).lower())
        self.assertIn("anguilla", correct_choice_text(questions[9]).lower())
        self.assertIn("exception", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("eel", "hard")
        easy = study_deck_for("eel", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "eel", "packTemplate": "animals"})
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
        deck = study_deck_for("eel", "hard")
        sheet = study_print_html(
            deck,
            name="Eel",
            emoji="🐍",
            photo="/field-pack/photos/eel.jpg?v=img2",
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
        for prompt in TALK_ABOUT_EEL + PUSH_FURTHER_EEL:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_EEL, sheet)
        self.assertIn("Facts from Wikipedia, Eel.", sheet)
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
        self.assertEqual(shipped_levels_for("cuttlefish"), ("easy", "hard", "zoologist"))
        cuttle_hard = study_deck_for("cuttlefish", "hard")
        self.assertEqual(cuttle_hard["source"], WIKI_CUTTLEFISH)
        cuttle_html = CUTTLEFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", cuttle_html)
        self.assertEqual(cuttle_hard["talk_about"], list(TALK_ABOUT_CUTTLEFISH))
        self.assertEqual(cuttle_hard["push_further"], list(PUSH_FURTHER_CUTTLEFISH))
        self.assertEqual(shipped_levels_for("crab"), ("easy", "hard", "zoologist"))
        crab_hard = study_deck_for("crab", "hard")
        self.assertEqual(crab_hard["source"], WIKI_CRAB)
        crab_html = CRAB.read_text(encoding="utf-8")
        self.assertIn("Zoologist", crab_html)
        self.assertEqual(crab_hard["talk_about"], list(TALK_ABOUT_CRAB))
        self.assertEqual(crab_hard["push_further"], list(PUSH_FURTHER_CRAB))
        self.assertEqual(shipped_levels_for("clownfish"), ("easy", "hard", "zoologist"))
        clown_hard = study_deck_for("clownfish", "hard")
        self.assertEqual(clown_hard["source"], WIKI_CLOWNFISH)
        clown_html = CLOWNFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", clown_html)
        self.assertEqual(clown_hard["talk_about"], list(TALK_ABOUT_CLOWNFISH))
        self.assertEqual(clown_hard["push_further"], list(PUSH_FURTHER_CLOWNFISH))
        jelly = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("anguilliformes-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["eel"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["eel"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("eel", data_js)
        self.assertIn("anguilliformes-soft", data_js)
        self.assertIn("mostly-marine-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = EEL.read_text(encoding="utf-8")
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
        hard_html = study_talk_html(study_deck_for("eel", "hard"))
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
