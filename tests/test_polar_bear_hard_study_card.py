"""Polar bear Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_POLAR_BEAR,
    STUDY_SLOTS,
    TALK_ABOUT_FRESHWATER_FISH,
    TALK_ABOUT_LION,
    TALK_ABOUT_POLAR_BEAR,
    WIKI_FRESHWATER_FISH,
    WIKI_LION,
    WIKI_POLAR_BEAR,
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
BEAR = FP / "cards" / "polar-bear" / "index.html"
SEA_OTTER = FP / "cards" / "sea-otter" / "index.html"
FISH = FP / "cards" / "freshwater-fish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "Who are polar bears’ closest living relatives?",
    "Why are polar bears counted as marine mammals?",
    "How do polar bears often hunt seals at the ice?",
    "Which part of a seal do polar bears prefer to eat first?",
    "How do polar bear guard hairs help besides looking pale?",
    "Can a polar bear’s fur and fat keep it too warm?",
    "How should we read the IUCN letter for polar bears?",
    "What do international CITES trade rules say for polar bears?",
    "How can less summer sea ice change polar bear hunting?",
    "Can polar bears and brown bears have cubs together?",
)

HARD_IDS = (
    "brown-bear-kin-soft",
    "marine-mammal-soft",
    "still-hunt-soft",
    "blubber-first-soft",
    "hollow-hairs-deepen-soft",
    "warm-too-well-soft",
    "vu-snapshot-soft",
    "cites-ii-soft",
    "ice-platform-squeeze-soft",
    "hybrid-rare-soft",
)

EASY_STEMS = (
    "Where do polar bears live in the wild?",
    "Why does polar bear fur look white?",
    "What color is the skin under a polar bear’s fur?",
    "How do a polar bear’s huge paws help?",
    "What do polar bears specialize in hunting?",
    "How do polar bears swim?",
    "How does a polar bear stay warm in the cold?",
    "Where do polar bear moms have their cubs?",
    "Why does healthy sea ice matter for polar bears?",
    "Do polar bears live at the South Pole?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "22,000",
    "31,000",
    "2050",
    "climate change",
    "global warming",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "reniculate",
    "dichromat",
    "mitochondrial",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class PolarBearHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("polar-bear"), ("easy", "hard"))
        self.assertIsNone(study_deck_for("polar-bear", "zoologist"))
        self.assertNotIn("sea-otter", study_card_ids())
        self.assertIsNone(study_deck_for("sea-otter"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("polar-bear", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_POLAR_BEAR)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Polar bear.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_POLAR_BEAR))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_POLAR_BEAR))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("polar-bear", "easy")
        hard = study_deck_for("polar-bear", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("polar-bear", "hard")
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
        self.assertIn("Ursus arctos", correct_choice_text(questions[0]))
        self.assertIn("Ursus", correct_choice_text(questions[0]))
        self.assertIn("maritimus", correct_choice_text(questions[0]))
        self.assertIn("marine", correct_choice_text(questions[1]).lower())
        self.assertIn("sea-ice", correct_choice_text(questions[1]).lower())
        self.assertIn("breathing hole", correct_choice_text(questions[2]).lower())
        self.assertIn("ice edge", correct_choice_text(questions[2]).lower())
        self.assertIn("blubber", correct_choice_text(questions[3]).lower())
        self.assertIn("lean meat", correct_choice_text(questions[3]).lower())
        self.assertIn("hollow", correct_choice_text(questions[4]).lower())
        self.assertIn("oil", correct_choice_text(questions[4]).lower())
        self.assertIn("overheat", correct_choice_text(questions[5]).lower())
        self.assertIn("run hard", correct_choice_text(questions[5]).lower())
        self.assertIn("vulnerable", correct_choice_text(questions[6]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[6]).lower())
        self.assertIn("appendix ii", correct_choice_text(questions[7]).lower())
        self.assertIn("trade", correct_choice_text(questions[7]).lower())
        self.assertIn("less summer sea ice", correct_choice_text(questions[8]).lower())
        self.assertIn("land", correct_choice_text(questions[8]).lower())
        self.assertIn("pizzly", correct_choice_text(questions[9]).lower())
        self.assertIn("grolar", correct_choice_text(questions[9]).lower())
        self.assertIn("distinct species", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("polar-bear", "hard")
        easy = study_deck_for("polar-bear", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "polar-bear", "packTemplate": "animals"})
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
        deck = study_deck_for("polar-bear", "hard")
        sheet = study_print_html(
            deck,
            name="Polar bear",
            emoji="🐻‍❄️",
            photo="/field-pack/photos/polar-bear.jpg?v=img2",
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
        for prompt in TALK_ABOUT_POLAR_BEAR + PUSH_FURTHER_POLAR_BEAR:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_POLAR_BEAR, sheet)
        self.assertIn("Facts from Wikipedia, Polar bear.", sheet)
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
        self.assertEqual(shipped_levels_for("freshwater-fish"), ("easy", "hard", "zoologist"))
        fish_hard = study_deck_for("freshwater-fish", "hard")
        self.assertEqual(fish_hard["source"], WIKI_FRESHWATER_FISH)
        fish_html = FISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", fish_html)
        self.assertEqual(fish_hard["talk_about"], list(TALK_ABOUT_FRESHWATER_FISH))
        self.assertEqual(fish_hard["push_further"], list(PUSH_FURTHER_FRESHWATER_FISH))
        sea = SEA_OTTER.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", sea)
        self.assertNotIn("card-study-pack", sea)
        self.assertNotIn("brown-bear-kin-soft", sea)
        self.assertIsNone(study_deck_for("sea-otter"))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["polar-bear"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertNotIn("zoologist", payload["polar-bear"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("polar-bear", data_js)
        self.assertIn("brown-bear-kin-soft", data_js)
        self.assertIn("hybrid-rare-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = BEAR.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertNotIn("Zoologist", html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertNotIn('data-study-pick="zoologist"', html)
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
        hard_html = study_talk_html(study_deck_for("polar-bear", "hard"))
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
