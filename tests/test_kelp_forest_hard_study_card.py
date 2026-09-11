"""Kelp-forest Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_CUTTLEFISH,
    PUSH_FURTHER_EEL,
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_KELP_FOREST,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_EEL,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    WIKI_CUTTLEFISH,
    WIKI_EEL,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
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
KELP = FP / "cards" / "kelp-forest" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
EEL = FP / "cards" / "eel" / "index.html"
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What are “kelps,” if we keep the group soft?",
    "What is a kelp’s body called, and how does it take up nutrients?",
    "How can a kelp forest make “stories” like a land forest, if we keep those layers soft?",
    "How fast can giant kelp (Macrocystis) lengthen in ideal water, if we keep the rate soft?",
    "Where do especially productive kelp forests often sit, if we keep that ocean story soft?",
    "How can predators shape a kelp forest in a trophic cascade, if we keep that chain soft?",
    "What can overgrazing do to a lush kelp forest, if we keep that flip soft?",
    "Who helps control urchins, if we keep the regional difference soft?",
    "How can warm spells and storms stress a kelp canopy, if we keep those threats soft?",
    "How can people help keep predator–urchin–kelp balance, if we keep that care soft?",
)

HARD_IDS = (
    "laminariales-soft",
    "thallus-parts-soft",
    "canopy-layers-soft",
    "giant-growth-soft",
    "upwelling-soft",
    "trophic-cascade-soft",
    "urchin-barrens-soft",
    "keystone-regional-soft",
    "warm-water-stress-soft",
    "mpa-care-soft",
)

EASY_STEMS = (
    "What is a kelp forest made of?",
    "Is kelp a land tree or plant?",
    "What does a kelp holdfast do?",
    "What are the stalk and leaf-like parts of kelp?",
    "How do many kinds of kelp lift their blades toward the sun?",
    "Where do kelp forests usually thrive?",
    "Who uses a kelp forest for food or shelter?",
    "How can sea otters help a kelp forest stay lush?",
    "How can people help kelp forests?",
    "Is a kelp forest a forest of trees?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "30–60",
    "30-60",
    "60 cm",
    "2 feet",
    "200 feet",
    "95%",
    " kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "30–60",
    "60 cm",
    "2 feet",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class KelpForestHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("kelp-forest", study_card_ids())
        self.assertEqual(shipped_levels_for("kelp-forest"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("kelp-forest", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("kelp-forest", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_KELP_FOREST)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Kelp forest.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_KELP_FOREST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_KELP_FOREST))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("kelp-forest", "easy")
        hard = study_deck_for("kelp-forest", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("kelp-forest", "hard")
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
        self.assertIn("laminariales", correct_choice_text(questions[0]).lower())
        self.assertIn("macrocystis", correct_choice_text(questions[0]).lower())
        self.assertIn("nereocystis", correct_choice_text(questions[0]).lower())
        self.assertIn("laminaria", correct_choice_text(questions[0]).lower())
        self.assertIn("ecklonia", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("thallus", correct_choice_text(questions[1]).lower())
        self.assertIn("holdfast", correct_choice_text(questions[1]).lower())
        self.assertIn("stipe", correct_choice_text(questions[1]).lower())
        self.assertIn("frond", correct_choice_text(questions[1]).lower())
        self.assertIn("blade", correct_choice_text(questions[1]).lower())
        self.assertIn("canopy", correct_choice_text(questions[2]).lower())
        self.assertIn("understory", correct_choice_text(questions[2]).lower())
        self.assertIn("prostrate", correct_choice_text(questions[2]).lower())
        self.assertIn("tens of centimeters", correct_choice_text(questions[3]).lower())
        self.assertIn("macrocystis", correct_choice_text(questions[3]).lower())
        self.assertIn("upwelling", correct_choice_text(questions[4]).lower())
        self.assertIn("nutrient", correct_choice_text(questions[4]).lower())
        self.assertIn("alaska", correct_choice_text(questions[5]).lower())
        self.assertIn("urchin", correct_choice_text(questions[5]).lower())
        self.assertIn("otter", correct_choice_text(questions[5]).lower())
        self.assertIn("barrens", correct_choice_text(questions[6]).lower())
        self.assertIn("alternate", correct_choice_text(questions[6]).lower())
        self.assertIn("keystone", correct_choice_text(questions[7]).lower())
        self.assertIn("lobster", correct_choice_text(questions[7]).lower())
        self.assertIn("el niño", correct_choice_text(questions[8]).lower())
        self.assertIn("storm", correct_choice_text(questions[8]).lower())
        self.assertIn("marine protected", correct_choice_text(questions[9]).lower())
        self.assertIn("place-by-place", correct_choice_text(questions[9]).lower())
        self.assertIn("letter", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("kelp-forest", "hard")
        easy = study_deck_for("kelp-forest", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "kelp-forest", "packTemplate": "animals"})
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
        deck = study_deck_for("kelp-forest", "hard")
        sheet = study_print_html(
            deck,
            name="Kelp forest",
            emoji="🌿",
            photo="/field-pack/photos/kelp-forest.jpg?v=img2",
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
        for prompt in TALK_ABOUT_KELP_FOREST + PUSH_FURTHER_KELP_FOREST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_KELP_FOREST, sheet)
        self.assertIn("Facts from Wikipedia, Kelp forest.", sheet)
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
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy", "hard", "zoologist"))
        jelly_hard = study_deck_for("jellyfish", "hard")
        self.assertEqual(jelly_hard["source"], WIKI_JELLYFISH)
        jelly_html = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", jelly_html)
        self.assertEqual(jelly_hard["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(jelly_hard["push_further"], list(PUSH_FURTHER_JELLYFISH))
        self.assertEqual(shipped_levels_for("eel"), ("easy", "hard", "zoologist"))
        eel_hard = study_deck_for("eel", "hard")
        self.assertEqual(eel_hard["source"], WIKI_EEL)
        eel_html = EEL.read_text(encoding="utf-8")
        self.assertIn("Zoologist", eel_html)
        self.assertEqual(eel_hard["talk_about"], list(TALK_ABOUT_EEL))
        self.assertEqual(eel_hard["push_further"], list(PUSH_FURTHER_EEL))
        self.assertEqual(shipped_levels_for("cuttlefish"), ("easy", "hard", "zoologist"))
        cuttle_hard = study_deck_for("cuttlefish", "hard")
        self.assertEqual(cuttle_hard["source"], WIKI_CUTTLEFISH)
        cuttle_html = CUTTLEFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", cuttle_html)
        self.assertEqual(cuttle_hard["talk_about"], list(TALK_ABOUT_CUTTLEFISH))
        self.assertEqual(cuttle_hard["push_further"], list(PUSH_FURTHER_CUTTLEFISH))
        octo = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", octo)
        self.assertNotIn("What do they eat?", octo)
        self.assertNotIn("laminariales-soft", octo)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["kelp-forest"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["kelp-forest"]["levels"])
        self.assertEqual(payload["kelp-forest"]["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("kelp-forest", data_js)
        self.assertIn("laminariales-soft", data_js)
        self.assertIn("mpa-care-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = KELP.read_text(encoding="utf-8")
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
        hard_html = study_talk_html(study_deck_for("kelp-forest", "hard"))
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
