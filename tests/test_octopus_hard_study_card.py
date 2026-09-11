"""Octopus Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_OCTOPUS,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
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
OCTOPUS = FP / "cards" / "octopus" / "index.html"
SEAHORSE = FP / "cards" / "whale-shark" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What order do octopuses sit in, if we keep that group map soft?",
    "How is octopus skin stacked for colour and shine, if we keep those cell names soft?",
    "What happens to an octopus’s hearts during a hard jet swim?",
    "Why can octopus blood look blue, if we keep the chemistry soft?",
    "Where do most octopus nerve cells sit, if we keep that count soft?",
    "What clues show octopus intelligence, if we keep those stories soft?",
    "Are octopuses venomous — and which kinds are known to be deadly to people?",
    "What happens after an octopus lays eggs, if we keep that life story soft?",
    "How can an octopus open a crab or clam, if we keep the timing soft?",
    "How can some octopuses warn or fool a threat, if we keep those displays soft?",
)

HARD_IDS = (
    "octopoda-soft",
    "chromatophore-stack-soft",
    "gill-hearts-soft",
    "haemocyanin-soft",
    "arm-brains-soft",
    "intelligence-soft",
    "blue-ring-soft",
    "egg-guard-fade-soft",
    "shell-drill-soft",
    "mimic-warning-soft",
)

EASY_STEMS = (
    "How many arms does an octopus have?",
    "Why can an octopus squeeze through a tiny gap?",
    "How can an octopus hide in plain sight?",
    "What can many octopuses do when a predator comes?",
    "What does an octopus use to eat, and what does it hunt?",
    "Where do many octopuses hide, and what clue might sit outside?",
    "What is special about octopus blood and hearts, if we keep it kid-simple?",
    "Where do octopuses live?",
    "How many kinds of octopus are there, if we keep the count soft?",
    "Do octopuses have tentacles?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "500 million",
    "71 kg",
    "157 lb",
    "180,000",
    "500,000",
    "75 mmHg",
    "tetrodotoxin",
    "TTX",
    "IUCN",
    "Endangered",
    "Vulnerable",
    " kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "tetrodotoxin",
    "TTX",
    "500 million",
    "IUCN",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class OctopusHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("octopus", study_card_ids())
        self.assertEqual(shipped_levels_for("octopus"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("octopus", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("octopus", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_OCTOPUS)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Octopus.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_OCTOPUS))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_OCTOPUS))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("octopus", "easy")
        hard = study_deck_for("octopus", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("octopus", "hard")
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
        self.assertIn("octopoda", correct_choice_text(questions[0]).lower())
        self.assertIn("cirrina", correct_choice_text(questions[0]).lower())
        self.assertIn("incirrina", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("chromatophore", correct_choice_text(questions[1]).lower())
        self.assertIn("iridophore", correct_choice_text(questions[1]).lower())
        self.assertIn("leucophore", correct_choice_text(questions[1]).lower())
        self.assertIn("gill", correct_choice_text(questions[2]).lower())
        self.assertIn("systemic", correct_choice_text(questions[2]).lower())
        self.assertIn("haemocyanin", correct_choice_text(questions[3]).lower())
        self.assertIn("copper", correct_choice_text(questions[3]).lower())
        self.assertIn("plasma", correct_choice_text(questions[3]).lower())
        self.assertIn("two-thirds", correct_choice_text(questions[4]).lower())
        self.assertIn("neuron", correct_choice_text(questions[4]).lower())
        self.assertIn("maze", correct_choice_text(questions[5]).lower())
        self.assertIn("coconut", correct_choice_text(questions[5]).lower())
        self.assertIn("veined", correct_choice_text(questions[5]).lower())
        self.assertIn("venomous", correct_choice_text(questions[6]).lower())
        self.assertIn("blue-ring", correct_choice_text(questions[6]).lower())
        self.assertIn("guards", correct_choice_text(questions[7]).lower())
        self.assertIn("mating", correct_choice_text(questions[7]).lower())
        self.assertIn("drill", correct_choice_text(questions[8]).lower())
        self.assertIn("saliva", correct_choice_text(questions[8]).lower())
        self.assertIn("lionfish", correct_choice_text(questions[9]).lower())
        self.assertIn("sea snake", correct_choice_text(questions[9]).lower())
        self.assertIn("warning", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("octopus", "hard")
        easy = study_deck_for("octopus", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "octopus", "packTemplate": "animals"})
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
        deck = study_deck_for("octopus", "hard")
        sheet = study_print_html(
            deck,
            name="Octopus",
            emoji="🐙",
            photo="/field-pack/photos/octopus.jpg?v=img2",
            photo_pos="50% 30%",
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
        for prompt in TALK_ABOUT_OCTOPUS + PUSH_FURTHER_OCTOPUS:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_OCTOPUS, sheet)
        self.assertIn("Facts from Wikipedia, Octopus.", sheet)
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
        self.assertIn("What do they eat?", horse)
        self.assertNotIn("card-study-pack", horse)
        self.assertNotIn("octopoda-soft", horse)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["octopus"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["octopus"]["levels"])
        self.assertEqual(payload["octopus"]["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("octopus", data_js)
        self.assertIn("octopoda-soft", data_js)
        self.assertIn("mimic-warning-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = OCTOPUS.read_text(encoding="utf-8")
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
        hard_html = study_talk_html(study_deck_for("octopus", "hard"))
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
