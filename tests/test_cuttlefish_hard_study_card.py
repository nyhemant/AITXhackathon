"""Cuttlefish Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CLOWNFISH,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_LION,
    WIKI_CLOWNFISH,
    WIKI_CRAB,
    WIKI_CUTTLEFISH,
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
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
OCTOPUS = FP / "cards" / "starfish" / "index.html"
CRAB = FP / "cards" / "crab" / "index.html"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What family and order do living cuttlefish sit in?",
    "What internal shell sets cuttlefish apart from squid?",
    "How are the color-change cells stacked in cuttlefish skin?",
    "How can cuttlefish match backgrounds if they are mostly color-blind?",
    "Why do cuttlefish have three hearts?",
    "Why can cuttlefish blood look blue-green?",
    "Where are wild cuttlefish missing, if we keep the map soft?",
    "How deep do most cuttlefish live, if we keep the depth soft?",
    "What IUCN snapshot does the common cuttlefish (Sepia officinalis) carry?",
    "Why might acidifying seas matter for cuttlefish later?",
)

HARD_IDS = (
    "sepiidae-soft",
    "sepia-vs-squid-soft",
    "chromatophore-stack-soft",
    "polarization-paradox-soft",
    "three-hearts-soft",
    "hemocyanin-soft",
    "americas-absence-soft",
    "shallow-range-soft",
    "common-lc-soft",
    "ocean-acid-soft",
)

EASY_STEMS = (
    "What kind of animal is a cuttlefish?",
    "What does the cuttlebone help a cuttlefish do?",
    "How many arms and tentacles does a cuttlefish have?",
    "Why are cuttlefish nicknamed “chameleons of the sea”?",
    "How can a cuttlefish use ink when a predator comes?",
    "What do cuttlefish eyes look like in bright light?",
    "What do cuttlefish eat?",
    "About how long do cuttlefish usually live?",
    "How can people help cuttlefish?",
    "Are cuttlefish a kind of fish?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "120 species",
    "133",
    "114",
    "200 m",
    "400 m",
    "600 m",
    "1,000",
    "2023",
    " kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "120 species",
    "200 m",
    "2023",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class CuttlefishHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("cuttlefish", study_card_ids())
        self.assertEqual(shipped_levels_for("cuttlefish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("cuttlefish", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("cuttlefish", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_CUTTLEFISH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Cuttlefish.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_CUTTLEFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_CUTTLEFISH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("cuttlefish", "easy")
        hard = study_deck_for("cuttlefish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("cuttlefish", "hard")
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
        self.assertIn("sepiidae", correct_choice_text(questions[0]).lower())
        self.assertIn("sepiida", correct_choice_text(questions[0]).lower())
        self.assertIn("100", correct_choice_text(questions[0]))
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("cuttlebone", correct_choice_text(questions[1]).lower())
        self.assertIn("aragonite", correct_choice_text(questions[1]).lower())
        self.assertIn("gladius", correct_choice_text(questions[1]).lower())
        self.assertIn("chromatophore", correct_choice_text(questions[2]).lower())
        self.assertIn("iridophore", correct_choice_text(questions[2]).lower())
        self.assertIn("leucophore", correct_choice_text(questions[2]).lower())
        self.assertIn("polarized", correct_choice_text(questions[3]).lower())
        self.assertIn("color-blind", questions[3]["stem"].lower())
        self.assertIn("branchial", correct_choice_text(questions[4]).lower())
        self.assertIn("systemic", correct_choice_text(questions[4]).lower())
        self.assertIn("hemocyanin", correct_choice_text(questions[5]).lower())
        self.assertIn("copper", correct_choice_text(questions[5]).lower())
        self.assertIn("americas", correct_choice_text(questions[6]).lower())
        self.assertIn("africa", correct_choice_text(questions[6]).lower())
        self.assertIn("shallow", correct_choice_text(questions[7]).lower())
        self.assertIn("hundreds", correct_choice_text(questions[7]).lower())
        self.assertIn("least concern", correct_choice_text(questions[8]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[8]).lower())
        self.assertIn("acid", correct_choice_text(questions[9]).lower())
        self.assertIn("shells", correct_choice_text(questions[9]).lower())
        self.assertIn("study", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("cuttlefish", "hard")
        easy = study_deck_for("cuttlefish", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "cuttlefish", "packTemplate": "animals"})
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
        deck = study_deck_for("cuttlefish", "hard")
        sheet = study_print_html(
            deck,
            name="Cuttlefish",
            emoji="🦑",
            photo="/field-pack/photos/cuttlefish.jpg?v=img2",
            photo_pos="50% 28%",
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
        for prompt in TALK_ABOUT_CUTTLEFISH + PUSH_FURTHER_CUTTLEFISH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_CUTTLEFISH, sheet)
        self.assertIn("Facts from Wikipedia, Cuttlefish.", sheet)
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
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("sepiidae-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["cuttlefish"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["cuttlefish"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("cuttlefish", data_js)
        self.assertIn("sepiidae-soft", data_js)
        self.assertIn("ocean-acid-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = CUTTLEFISH.read_text(encoding="utf-8")
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
        hard_html = study_talk_html(study_deck_for("cuttlefish", "hard"))
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
