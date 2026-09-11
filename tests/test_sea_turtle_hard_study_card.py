"""Sea-turtle Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_KELP_FOREST,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_MANTA_RAY,
    PUSH_FURTHER_OCTOPUS,
    PUSH_FURTHER_SEA_TURTLE,
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_OCTOPUS,
    TALK_ABOUT_SEA_TURTLE,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
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
SEA_TURTLE = FP / "cards" / "sea-turtle" / "index.html"
SEAHORSE = FP / "cards" / "whale-shark" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "Where do true sea turtles sit in the family tree, if we keep that map soft?",
    "How can nest sand temperature steer hatchling sex, if we keep those thresholds soft?",
    "Where do many female sea turtles return to nest, if we keep that homing story soft?",
    "How can hatchlings and adults stay on long ocean routes, if we keep that sense soft?",
    "How do sea turtles dump extra salt, if we keep those glands soft?",
    "What makes a leatherback different from hard-shell sea turtles, if we keep that size soft?",
    "How do adult diets split among sea turtle kinds, if we keep those menus soft?",
    "How do some ridleys nest differently from most other sea turtles?",
    "Where do many young sea turtles spend their early years, if we keep that time soft?",
    "What human pressures can send hatchlings the wrong way or put wild turtles at risk, if we keep that care story soft?",
)

HARD_IDS = (
    "chelonioidea-soft",
    "tsd-soft",
    "natal-beach-soft",
    "magnetic-sense-soft",
    "salt-tears-soft",
    "leatherback-soft",
    "diet-split-soft",
    "arribada-soft",
    "lost-years-soft",
    "threats-soft",
)

EASY_STEMS = (
    "How many kinds of sea turtle live in the world’s oceans, if we keep the list soft?",
    "What do a sea turtle’s flippers do?",
    "How is a sea turtle’s shell built for the ocean?",
    "How does a mom sea turtle make a nest?",
    "What are sea turtle eggs like — and does mom stay to guard them?",
    "What do baby sea turtles do after they hatch?",
    "How do sea turtles breathe, even though they live in the ocean?",
    "Where do sea turtles live?",
    "How far can many sea turtles travel, if we keep the miles soft?",
    "Can a sea turtle pull its head and flippers into its shell like many pet turtles?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Endangered",
    "Vulnerable",
    "Critically",
    "Least Concern",
    "°C",
    "27°",
    "29°",
    "gigantothermy",
    "Archelon",
    "Protostega",
    "110 million",
    "97 percent",
    "70–95",
    "70-95",
    " kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "IUCN",
    "gigantothermy",
    "Archelon",
    "Protostega",
    "°C",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class SeaTurtleHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("sea-turtle", study_card_ids())
        self.assertEqual(shipped_levels_for("sea-turtle"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("sea-turtle", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("sea-turtle", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_SEA_TURTLE)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Sea turtle.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_SEA_TURTLE))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_SEA_TURTLE))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("sea-turtle", "easy")
        hard = study_deck_for("sea-turtle", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("sea-turtle", "hard")
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
        self.assertIn("chelonioidea", correct_choice_text(questions[0]).lower())
        self.assertIn("cheloniidae", correct_choice_text(questions[0]).lower())
        self.assertIn("dermochelyidae", correct_choice_text(questions[0]).lower())
        self.assertIn("leatherback", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("warmer", correct_choice_text(questions[1]).lower())
        self.assertIn("female", correct_choice_text(questions[1]).lower())
        self.assertIn("cooler", correct_choice_text(questions[1]).lower())
        self.assertIn("male", correct_choice_text(questions[1]).lower())
        self.assertIn("hatched", correct_choice_text(questions[2]).lower())
        self.assertIn("philopatry", correct_choice_text(questions[2]).lower())
        self.assertIn("magnetic", correct_choice_text(questions[3]).lower())
        self.assertIn("map", correct_choice_text(questions[3]).lower())
        self.assertIn("compass", correct_choice_text(questions[3]).lower())
        self.assertIn("gland", correct_choice_text(questions[4]).lower())
        self.assertIn("eyes", correct_choice_text(questions[4]).lower())
        self.assertIn("salt", correct_choice_text(questions[4]).lower())
        self.assertIn("kidney", correct_choice_text(questions[4]).lower())
        self.assertIn("largest", correct_choice_text(questions[5]).lower())
        self.assertIn("leathery", correct_choice_text(questions[5]).lower())
        self.assertIn("jellyfish", correct_choice_text(questions[5]).lower())
        self.assertIn("scute", correct_choice_text(questions[5]).lower())
        self.assertIn("seagrass", correct_choice_text(questions[6]).lower())
        self.assertIn("algae", correct_choice_text(questions[6]).lower())
        self.assertIn("sponge", correct_choice_text(questions[6]).lower())
        self.assertIn("loggerhead", correct_choice_text(questions[6]).lower())
        self.assertIn("arribada", correct_choice_text(questions[7]).lower())
        self.assertIn("ridley", correct_choice_text(questions[7]).lower())
        self.assertIn("alone", correct_choice_text(questions[7]).lower())
        self.assertIn("offshore", correct_choice_text(questions[8]).lower())
        self.assertIn("seaweed", correct_choice_text(questions[8]).lower())
        self.assertIn("shore", correct_choice_text(questions[8]).lower())
        self.assertIn("light", correct_choice_text(questions[9]).lower())
        self.assertIn("net", correct_choice_text(questions[9]).lower())
        self.assertIn("trash", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("sea-turtle", "hard")
        easy = study_deck_for("sea-turtle", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "sea-turtle", "packTemplate": "animals"})
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
        deck = study_deck_for("sea-turtle", "hard")
        sheet = study_print_html(
            deck,
            name="Sea turtle",
            emoji="🐢",
            photo="/field-pack/photos/sea-turtle.jpg?v=img2",
            photo_pos="50% 32%",
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
        for prompt in TALK_ABOUT_SEA_TURTLE + PUSH_FURTHER_SEA_TURTLE:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_SEA_TURTLE, sheet)
        self.assertIn("Facts from Wikipedia, Sea turtle.", sheet)
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
        self.assertEqual(shipped_levels_for("octopus"), ("easy", "hard", "zoologist"))
        octo_hard = study_deck_for("octopus", "hard")
        self.assertEqual(octo_hard["source"], WIKI_OCTOPUS)
        octo_html = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("Zoologist", octo_html)
        self.assertEqual(octo_hard["talk_about"], list(TALK_ABOUT_OCTOPUS))
        self.assertEqual(octo_hard["push_further"], list(PUSH_FURTHER_OCTOPUS))
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        manta_hard = study_deck_for("manta-ray", "hard")
        self.assertEqual(manta_hard["source"], WIKI_MANTA_RAY)
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", manta_html)
        self.assertEqual(manta_hard["talk_about"], list(TALK_ABOUT_MANTA_RAY))
        self.assertEqual(manta_hard["push_further"], list(PUSH_FURTHER_MANTA_RAY))
        self.assertEqual(shipped_levels_for("kelp-forest"), ("easy", "hard", "zoologist"))
        kelp_hard = study_deck_for("kelp-forest", "hard")
        self.assertEqual(kelp_hard["source"], WIKI_KELP_FOREST)
        kelp_html = KELP.read_text(encoding="utf-8")
        self.assertIn("Zoologist", kelp_html)
        self.assertEqual(kelp_hard["talk_about"], list(TALK_ABOUT_KELP_FOREST))
        self.assertEqual(kelp_hard["push_further"], list(PUSH_FURTHER_KELP_FOREST))
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy", "hard", "zoologist"))
        jelly_hard = study_deck_for("jellyfish", "hard")
        self.assertEqual(jelly_hard["source"], WIKI_JELLYFISH)
        jelly_html = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", jelly_html)
        self.assertEqual(jelly_hard["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(jelly_hard["push_further"], list(PUSH_FURTHER_JELLYFISH))
        horse = SEAHORSE.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", horse)
        self.assertNotIn("What do they eat?", horse)
        self.assertNotIn("chelonioidea-soft", horse)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["sea-turtle"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["sea-turtle"]["levels"])
        self.assertEqual(payload["sea-turtle"]["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("sea-turtle", data_js)
        self.assertIn("chelonioidea-soft", data_js)
        self.assertIn("threats-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = SEA_TURTLE.read_text(encoding="utf-8")
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
        self.assertNotIn("Zoologist", print_tpl)
        for stem in HARD_STEMS:
            self.assertNotIn(stem, print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        hard_html = study_talk_html(study_deck_for("sea-turtle", "hard"))
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
