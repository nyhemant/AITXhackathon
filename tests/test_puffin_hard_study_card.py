"""Puffin Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_ELK,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PUFFIN,
    STUDY_SLOTS,
    TALK_ABOUT_ELK,
    TALK_ABOUT_LION,
    TALK_ABOUT_PUFFIN,
    WIKI_ATLANTIC_PUFFIN,
    WIKI_ELK,
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
PUFFIN = FP / "cards" / "puffin" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
ELK = FP / "cards" / "elk" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What is the Atlantic puffin’s scientific name, and what soft name story can Fratercula hold?",
    "Which bird family does the Atlantic puffin belong to?",
    "How many puffin species live in the Atlantic Ocean?",
    "What happens to an Atlantic puffin’s colorful outer bill after breeding season?",
    "How can an Atlantic puffin hold a row of fish while catching more?",
    "How does an Atlantic puffin dive for food, and where does it often hunt?",
    "Do Atlantic puffins often keep the same home and partner?",
    "How should we read the IUCN letter for Atlantic puffins?",
    "Why do Atlantic puffins prefer islands, and what still threatens chicks?",
    "Which Canadian province chose the Atlantic puffin as its official bird?",
)

HARD_IDS = (
    "fratercula-arctica-soft",
    "auk-family-soft",
    "three-puffins-soft",
    "bill-plates-soft",
    "spiny-tongue-soft",
    "wing-propelled-dive-soft",
    "site-fidelity-soft",
    "vu-snapshot-soft",
    "predator-islands-soft",
    "provincial-bird-soft",
)

EASY_STEMS = (
    "Where do Atlantic puffins spend their year?",
    "What does an Atlantic puffin’s bill look like in breeding season?",
    "Where does an Atlantic puffin usually put its nest?",
    "How many chicks do Atlantic puffins usually raise in a season?",
    "How can an Atlantic puffin carry food home?",
    "How does an Atlantic puffin swim after fish?",
    "How do Atlantic puffins often walk on land?",
    "How can people help wild puffins?",
    "How do Atlantic puffins usually nest?",
    "Is an Atlantic puffin a penguin?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "12–14 million",
    "12-14 million",
    "4,770,000",
    "650 g",
    "80 km/h",
    "100 km",
    "61 fish",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "12–14 million",
    "4,770,000",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class PuffinHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("puffin", study_card_ids())
        self.assertEqual(shipped_levels_for("puffin"), ("easy", "hard"))
        self.assertIsNone(study_deck_for("puffin", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("puffin", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_ATLANTIC_PUFFIN)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Atlantic puffin.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_PUFFIN))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_PUFFIN))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("puffin", "easy")
        hard = study_deck_for("puffin", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("puffin", "hard")
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
        self.assertIn("fratercula arctica", correct_choice_text(questions[0]).lower())
        self.assertIn("little brother", correct_choice_text(questions[0]).lower())
        self.assertIn("alcidae", correct_choice_text(questions[1]).lower())
        self.assertIn("auk", correct_choice_text(questions[1]).lower())
        self.assertIn("penguin", correct_choice_text(questions[1]).lower())
        self.assertIn("atlantic", correct_choice_text(questions[2]).lower())
        self.assertIn("horned", correct_choice_text(questions[2]).lower())
        self.assertIn("tufted", correct_choice_text(questions[2]).lower())
        self.assertIn("pacific", correct_choice_text(questions[2]).lower())
        self.assertIn("plates", correct_choice_text(questions[3]).lower())
        self.assertIn("shed", correct_choice_text(questions[3]).lower())
        self.assertIn("winter", correct_choice_text(questions[3]).lower())
        self.assertIn("spine", correct_choice_text(questions[4]).lower())
        self.assertIn("tongue", correct_choice_text(questions[4]).lower())
        self.assertIn("wings", correct_choice_text(questions[5]).lower())
        self.assertIn("shallower", correct_choice_text(questions[5]).lower())
        self.assertIn("burrow", correct_choice_text(questions[6]).lower())
        self.assertIn("year after year", correct_choice_text(questions[6]).lower())
        self.assertIn("vulnerable", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[7]).lower())
        self.assertIn("predator-free", correct_choice_text(questions[8]).lower())
        self.assertIn("gulls", correct_choice_text(questions[8]).lower())
        self.assertIn("skuas", correct_choice_text(questions[8]).lower())
        self.assertIn("newfoundland", correct_choice_text(questions[9]).lower())
        self.assertIn("labrador", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("puffin", "hard")
        easy = study_deck_for("puffin", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "puffin", "packTemplate": "animals"})
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
        deck = study_deck_for("puffin", "hard")
        sheet = study_print_html(
            deck,
            name="Puffin",
            emoji="🐦",
            photo="/field-pack/photos/puffin.jpg?v=img2",
            photo_pos="50% 22%",
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
        for prompt in TALK_ABOUT_PUFFIN + PUSH_FURTHER_PUFFIN:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_ATLANTIC_PUFFIN, sheet)
        self.assertIn("Facts from Wikipedia, Atlantic puffin.", sheet)
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
        self.assertEqual(shipped_levels_for("elk"), ("easy", "hard", "zoologist"))
        elk_hard = study_deck_for("elk", "hard")
        self.assertEqual(elk_hard["source"], WIKI_ELK)
        elk_html = ELK.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elk_html)
        self.assertEqual(elk_hard["talk_about"], list(TALK_ABOUT_ELK))
        self.assertEqual(elk_hard["push_further"], list(PUSH_FURTHER_ELK))
        jelly = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("fratercula-arctica-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["puffin"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertNotIn("zoologist", payload["puffin"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("puffin", data_js)
        self.assertIn("fratercula-arctica-soft", data_js)
        self.assertIn("provincial-bird-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = PUFFIN.read_text(encoding="utf-8")
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
        for stem in HARD_STEMS:
            self.assertNotIn(stem, print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        hard_html = study_talk_html(study_deck_for("puffin", "hard"))
        self.assertNotIn("study-teach", hard_html)
        self.assertIn('<details class="study-explore', hard_html)
        self.assertIn("Explore more", hard_html)
        self.assertLess(hard_html.find("study-foot"), hard_html.find("study-explore"))
        self.assertIn("Talk about it", hard_html)
        self.assertIn("Push further", hard_html)
        self.assertIn("Park Ranger", hard_html)
        self.assertIn("Junior Ranger", hard_html)
        self.assertNotIn("Zoologist", hard_html)


if __name__ == "__main__":
    unittest.main()
