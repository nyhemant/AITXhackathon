"""Starfish Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_OCTOPUS,
    PUSH_FURTHER_SEA_TURTLE,
    PUSH_FURTHER_SEAHORSE,
    PUSH_FURTHER_STARFISH,
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_OCTOPUS,
    TALK_ABOUT_SEA_TURTLE,
    TALK_ABOUT_SEAHORSE,
    TALK_ABOUT_STARFISH,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
    WIKI_SEAHORSE,
    WIKI_STARFISH,
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
STARFISH = FP / "cards" / "starfish" / "index.html"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
SEAHORSE = FP / "cards" / "seahorse" / "index.html"
SEA_TURTLE = FP / "cards" / "sea-turtle" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What scientific class do sea stars belong to, if we keep the family tree soft?",
    "What powers a sea star’s tube feet?",
    "What is the madreporite on a sea star?",
    "How does one tube foot extend and pull back?",
    "How do many predatory sea stars eat prey too big to swallow whole?",
    "Why do scientists call some sea stars “keystone” predators (example: ochre / purple sea star Pisaster)?",
    "What is special about the tropical crown-of-thorns sea star (Acanthaster)?",
    "What do most sea stars need to regrow a whole new body after an arm is lost?",
    "What are pedicellariae on many sea stars?",
    "Is a sea star’s “face” the colourful top side?",
)

HARD_IDS = (
    "asteroidea-soft",
    "water-vascular-soft",
    "madreporite-soft",
    "ampullae-soft",
    "stomach-eversion-soft",
    "keystone-soft",
    "crown-of-thorns-soft",
    "regrow-deepen-soft",
    "pedicellariae-soft",
    "top-vs-bottom-myth",
)

EASY_STEMS = (
    "Are starfish a kind of fish?",
    "What does a sea star’s body look like, if we keep the arm count soft?",
    "How does a sea star walk?",
    "Where is a sea star’s mouth?",
    "Where do sea stars live?",
    "What is a sea star’s skin like?",
    "What do many sea stars hunt?",
    "What can many sea stars do if they lose an arm?",
    "How many kinds of sea star are there, if we keep the count soft?",
    "Does the name “starfish” mean they are fish?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Endangered",
    "Vulnerable",
    "Critically",
    "Near Threatened",
    "Least Concern",
    "wasting",
    "neuropeptide",
    "Forcipulatida",
    "Valvatida",
    "Spinulosida",
    "Paxillosida",
    "Asterias amurensis",
    " kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "IUCN",
    "wasting",
    "neuropeptide",
    "Forcipulatida",
    "Valvatida",
    "Asterias amurensis",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class StarfishHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("starfish", study_card_ids())
        self.assertEqual(shipped_levels_for("starfish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("starfish", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("starfish", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_STARFISH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Starfish.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_STARFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_STARFISH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("starfish", "easy")
        hard = study_deck_for("starfish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("starfish", "hard")
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
        self.assertIn("asteroidea", correct_choice_text(questions[0]).lower())
        self.assertIn("echinoderm", correct_choice_text(questions[0]).lower())
        self.assertIn("urchin", correct_choice_text(questions[0]).lower())
        self.assertIn("water vascular", correct_choice_text(questions[1]).lower())
        self.assertIn("canal", correct_choice_text(questions[1]).lower())
        self.assertIn("madreporite", questions[2]["stem"].lower())
        self.assertIn("sieve", correct_choice_text(questions[2]).lower())
        self.assertIn("aboral", correct_choice_text(questions[2]).lower())
        self.assertIn("ampulla", correct_choice_text(questions[3]).lower())
        self.assertIn("evert", correct_choice_text(questions[4]).lower())
        self.assertNotIn("everth", correct_choice_text(questions[4]).lower())
        self.assertIn("cardiac", correct_choice_text(questions[4]).lower())
        self.assertIn("mussel", correct_choice_text(questions[5]).lower())
        self.assertIn("diversity", correct_choice_text(questions[5]).lower())
        self.assertIn("coral", correct_choice_text(questions[6]).lower())
        self.assertIn("indo-pacific", correct_choice_text(questions[6]).lower())
        self.assertIn("central disc", correct_choice_text(questions[7]).lower())
        self.assertIn("ossicle", correct_choice_text(questions[7]).lower() + correct_choice_text(questions[8]).lower())
        self.assertIn("claw", correct_choice_text(questions[8]).lower())
        self.assertIn("oral", correct_choice_text(questions[9]).lower())
        self.assertIn("aboral", correct_choice_text(questions[9]).lower())
        self.assertIn("underside", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        self.assertIn("evert", blob.lower())
        self.assertNotIn("everth", blob.lower())
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("starfish", "hard")
        easy = study_deck_for("starfish", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "starfish", "packTemplate": "animals"})
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
        deck = study_deck_for("starfish", "hard")
        sheet = study_print_html(
            deck,
            name="Sea star",
            emoji="⭐",
            photo="/field-pack/photos/starfish.jpg?v=img2",
            photo_pos="50% 45%",
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
        for prompt in TALK_ABOUT_STARFISH + PUSH_FURTHER_STARFISH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_STARFISH, sheet)
        self.assertIn("Facts from Wikipedia, Starfish.", sheet)
        for stem in HARD_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS:
            self.assertNotIn(stem, sheet)
        self.assertIn("evert", sheet.lower())
        self.assertNotIn("everth", sheet.lower())

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
        self.assertEqual(shipped_levels_for("sea-turtle"), ("easy", "hard", "zoologist"))
        turtle_hard = study_deck_for("sea-turtle", "hard")
        self.assertEqual(turtle_hard["source"], WIKI_SEA_TURTLE)
        turtle_html = SEA_TURTLE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", turtle_html)
        self.assertEqual(turtle_hard["talk_about"], list(TALK_ABOUT_SEA_TURTLE))
        self.assertEqual(turtle_hard["push_further"], list(PUSH_FURTHER_SEA_TURTLE))
        self.assertEqual(shipped_levels_for("seahorse"), ("easy", "hard", "zoologist"))
        horse_hard = study_deck_for("seahorse", "hard")
        self.assertEqual(horse_hard["source"], WIKI_SEAHORSE)
        horse_html = SEAHORSE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", horse_html)
        self.assertEqual(horse_hard["talk_about"], list(TALK_ABOUT_SEAHORSE))
        self.assertEqual(horse_hard["push_further"], list(PUSH_FURTHER_SEAHORSE))
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
        ray = WHALE_SHARK.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", ray)
        self.assertNotIn("card-study-pack", ray)
        self.assertNotIn("asteroidea-soft", ray)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["starfish"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["starfish"]["levels"])
        self.assertEqual(payload["starfish"]["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("starfish", data_js)
        self.assertIn("asteroidea-soft", data_js)
        self.assertIn("top-vs-bottom-myth", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = STARFISH.read_text(encoding="utf-8")
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
        hard_html = study_talk_html(study_deck_for("starfish", "hard"))
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
