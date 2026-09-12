"""Galápagos tortoise Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import CARD_TALK_H2, outing_talk_html  # noqa: E402
from study_cards import (  # noqa: E402
    correct_choice_text,
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_FLAMINGO,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PENGUIN,
    PUSH_FURTHER_TORTOISE,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_TORTOISE,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
    WIKI_GALAPAGOS_TORTOISE,
    WIKI_GIRAFFE,
    WIKI_LION,
    level_display_name,
    shipped_levels_for,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
TORTOISE = FP / "cards" / "galapagos-tortoise" / "index.html"
FLAMINGO = FP / "cards" / "caribbean-flamingo" / "index.html"
PENGUIN = FP / "cards" / "african-penguin" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What are the two main Galápagos tortoise shell shapes?",
    "Why does a saddleback Galápagos tortoise have a raised front notch on its shell?",
    "How long can a Galápagos tortoise go without food or water?",
    "Where can a Galápagos tortoise store water?",
    "Why are Galápagos tortoises famous in the story of evolution?",
    "Why did Galápagos tortoise numbers crash in the 1800s?",
    "How do introduced goats, rats, and pigs harm Galápagos tortoises?",
    "Who was Lonesome George?",
    "How has captive breeding helped Galápagos tortoises?",
    "How is a tortoise different from a sea turtle?",
)

HARD_IDS = (
    "shell-shapes",
    "saddleback-why",
    "fasting",
    "water-store",
    "darwin",
    "sailors",
    "pests",
    "lonesome-george",
    "breeding",
    "tortoise-vs-turtle",
)

EASY_STEMS = (
    "Where do wild Galápagos tortoises live?",
    "How big is a Galápagos tortoise?",
    "How long can a Galápagos tortoise live?",
    "What do Galápagos tortoises eat?",
    "What is the hard covering on a Galápagos tortoise’s back?",
    "How does a Galápagos tortoise usually move?",
    "How do baby Galápagos tortoises start life?",
    "What can a Galápagos tortoise do when it is frightened?",
    "What is special about a Galápagos tortoise’s neck?",
    "Can a Galápagos tortoise leave its shell?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Endangered",
    "Critically Endangered",
    "critically endangered",
    "Chelonoidis",
    "500 years",
    "500-year",
    "Harriet",
    "417 kg",
    "177 years",
    "ten years",
    "10 years",
    "350–800",
    "350-800",
    "800 progeny",
    "800 offspring",
    "1,200",
    "1200",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class TortoiseHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("galapagos-tortoise"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("galapagos-tortoise", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("galapagos-tortoise", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_GALAPAGOS_TORTOISE)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Galápagos tortoise.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_TORTOISE))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_TORTOISE))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("galapagos-tortoise", "easy")
        hard = study_deck_for("galapagos-tortoise", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("galapagos-tortoise", "hard")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(HARD_IDS))
        self.assertEqual([q["stem"] for q in questions], list(HARD_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Domed and saddleback", correct_choice_text(questions[0]))
        self.assertIn("raised front notch", correct_choice_text(questions[1]))
        self.assertIn("high plants", correct_choice_text(questions[1]))
        self.assertIn("drier islands", correct_choice_text(questions[1]))
        self.assertIn("many months", correct_choice_text(questions[2]))
        self.assertIn("about a year", correct_choice_text(questions[2]))
        self.assertIn("bladder", correct_choice_text(questions[3]))
        self.assertIn("body tissues", correct_choice_text(questions[3]))
        self.assertIn("Darwin", correct_choice_text(questions[4]))
        self.assertIn("evolution", correct_choice_text(questions[4]))
        self.assertIn("Sailors", correct_choice_text(questions[5]))
        self.assertIn("shipboard food", correct_choice_text(questions[5]))
        self.assertIn("Goats eat the plants", correct_choice_text(questions[6]))
        self.assertIn("rats and pigs", correct_choice_text(questions[6]))
        self.assertIn("Pinta Island", correct_choice_text(questions[7]))
        self.assertIn("2012", correct_choice_text(questions[7]))
        self.assertIn("Diego", correct_choice_text(questions[8]))
        self.assertIn("many young", correct_choice_text(questions[8]))
        self.assertIn("column-like feet", correct_choice_text(questions[9]))
        self.assertIn("not flippers", correct_choice_text(questions[9]))
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("galapagos-tortoise", "hard")
        easy = study_deck_for("galapagos-tortoise", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "galapagos-tortoise", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("<details class=\"study-teach\">", html)
        self.assertNotIn("<details class=\"study-teach\" open", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-pick="zoologist"', html)
        for stem in HARD_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_hard_print_is_answer_light_duplex(self):
        deck = study_deck_for("galapagos-tortoise", "hard")
        sheet = study_print_html(
            deck,
            name="Galápagos tortoise",
            emoji="🐢",
            photo="/field-pack/photos/galapagos-tortoise.jpg?v=img2",
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
        for prompt in TALK_ABOUT_TORTOISE + PUSH_FURTHER_TORTOISE:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_GALAPAGOS_TORTOISE, sheet)
        self.assertIn("Facts from Wikipedia, Galápagos tortoise.", sheet)
        for stem in HARD_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS:
            self.assertNotIn(stem, sheet)

    def test_lion_giraffe_elephant_penguin_and_flamingo_decks_untouched(self):
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
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        giraffe_hard = study_deck_for("reticulated-giraffe", "hard")
        self.assertEqual(giraffe_hard["source"], WIKI_GIRAFFE)
        self.assertIn("okapi", correct_choice_text(giraffe_hard["questions"][0]))
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giraffe_html)
        self.assertIn("Junior Ranger", giraffe_html)
        self.assertIn("Park Ranger", giraffe_html)
        self.assertEqual(giraffe_hard["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_hard["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_hard = study_deck_for("african-elephant", "hard")
        self.assertEqual(elephant_hard["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Tens of thousands", correct_choice_text(elephant_hard["questions"][0]))
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertIn("Junior Ranger", elephant_html)
        self.assertIn("Park Ranger", elephant_html)
        self.assertEqual(elephant_hard["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_hard["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        penguin_hard = study_deck_for("african-penguin", "hard")
        self.assertEqual(penguin_hard["source"], WIKI_AFRICAN_PENGUIN)
        self.assertIn("Lose heat", correct_choice_text(penguin_hard["questions"][0]))
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", penguin_html)
        self.assertIn("Junior Ranger", penguin_html)
        self.assertIn("Park Ranger", penguin_html)
        self.assertEqual(penguin_hard["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin_hard["push_further"], list(PUSH_FURTHER_PENGUIN))
        self.assertEqual(shipped_levels_for("caribbean-flamingo"), ("easy", "hard", "zoologist"))
        flamingo_hard = study_deck_for("caribbean-flamingo", "hard")
        self.assertEqual(flamingo_hard["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertIn("Carotenoid pigments", correct_choice_text(flamingo_hard["questions"][0]))
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", flamingo_html)
        self.assertIn("Junior Ranger", flamingo_html)
        self.assertIn("Park Ranger", flamingo_html)
        self.assertEqual(flamingo_hard["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(flamingo_hard["push_further"], list(PUSH_FURTHER_FLAMINGO))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["galapagos-tortoise"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["galapagos-tortoise"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("galapagos-tortoise", data_js)
        self.assertIn("shell-shapes", data_js)
        self.assertIn("tortoise-vs-turtle", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = TORTOISE.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn("Learn first", html)
        self.assertIn("Watch Live", html)
        self.assertIn("card-watch-live", html)
        self.assertIn("#habitat=galapagos-tortoise", html)
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
        hard_html = study_talk_html(study_deck_for("galapagos-tortoise", "hard"))
        self.assertNotIn("study-teach", hard_html)
        self.assertIn('<details class="study-explore', hard_html)
        self.assertIn("Explore more", hard_html)
        self.assertIn("Talk about it", hard_html)
        self.assertIn("Push further", hard_html)
        self.assertIn("Park Ranger", hard_html)
        self.assertIn("Junior Ranger", hard_html)
        self.assertIn("Zoologist", hard_html)


if __name__ == "__main__":
    unittest.main()
