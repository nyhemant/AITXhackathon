"""Galápagos tortoise Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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

ZOOLOGIST_STEMS = (
    "Which genus do Galápagos tortoises belong in today?",
    "How do scientists treat the named Galápagos tortoise island forms?",
    "Why are Galápagos tortoise shell differences a textbook evolutionary case?",
    "What physiological traits let a Galápagos tortoise tolerate a long fast?",
    "What is a Galápagos tortoise’s carapace largely built from?",
    "What is the status of the Pinta Island tortoise, C. abingdonii?",
    "What happened to the Fernandina Island tortoise, long presumed extinct?",
    "What ecological role do Galápagos tortoises play on their islands?",
    "What did genome studies of Lonesome George highlight?",
    "How is the sex of a Galápagos tortoise hatchling determined?",
)

ZOOLOGIST_IDS = (
    "genus",
    "species-complex",
    "adaptive-radiation",
    "low-metabolism",
    "carapace",
    "pinta-extinct",
    "fernandina",
    "megaherbivore",
    "genome",
    "tsd",
)

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
    "Least Concern",
    "least concern",
    "IUCN",
    "status LC",
    "Endangered",
    "Critically Endangered",
    "critically endangered",
    "Vulnerable",
    "500 years",
    "500-year",
    "Harriet",
    "177 years",
    "417 kg",
    "NEIL1",
    "RMI2",
    "XRCC6",
    "TP53",
    "2019",
    "12 subspecies",
    "13 subspecies",
    "14 subspecies",
    "15 subspecies",
    "exactly 12",
    "exactly 15",
)
REDO_THEMES = (
    "On islands near Ecuador",
    "Among the largest tortoises",
    "Over 100 years",
    "Plants such as grass, leaves, and cactus",
    "It moves slowly",
    "hatch from eggs buried",
    "Pull its head and legs inside",
    "long and can stretch upward",
    "shell is a coat",
    "Domed and saddleback",
    "raised front notch",
    "many months, or about a year",
    "bladder and other body tissues",
    "helped inspire Darwin",
    "Sailors took huge numbers",
    "Goats eat the plants",
    "The last known Pinta Island tortoise",
    "Diego fathered",
    "column-like feet",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class TortoiseZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("galapagos-tortoise"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("galapagos-tortoise", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_GALAPAGOS_TORTOISE)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Galápagos tortoise.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_TORTOISE))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_TORTOISE))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("galapagos-tortoise", "zoologist")
        easy = study_deck_for("galapagos-tortoise", "easy")
        hard = study_deck_for("galapagos-tortoise", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("galapagos-tortoise", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Chelonoidis", questions[0]["choices"][1])
        self.assertIn("Geochelone", questions[0]["choices"][1])
        self.assertIn("Testudo", questions[0]["choices"][1])
        self.assertIn("species complex", questions[1]["choices"][1].lower())
        self.assertIn("dozen-plus", questions[1]["choices"][1].lower())
        self.assertIn("debated", questions[1]["choices"][1].lower())
        self.assertIn("adaptive radiation", questions[2]["choices"][1].lower())
        self.assertIn("divergent shell", questions[2]["choices"][1].lower())
        self.assertIn("ectothermy", questions[3]["choices"][1].lower())
        self.assertIn("low metabolic", questions[3]["choices"][1].lower())
        self.assertIn("fused ribs", questions[4]["choices"][1].lower())
        self.assertIn("vertebrae", questions[4]["choices"][1].lower())
        self.assertIn("keratin scutes", questions[4]["choices"][1].lower())
        self.assertIn("C. abingdonii", questions[5]["choices"][1])
        self.assertIn("functionally extinct", questions[5]["choices"][1].lower())
        self.assertIn("2012", questions[5]["choices"][1])
        self.assertIn("living female", questions[6]["choices"][1].lower())
        self.assertIn("presumed extinct", questions[6]["choices"][1].lower())
        self.assertIn("megaherbivore", questions[7]["choices"][1].lower())
        self.assertIn("ecosystem engineer", questions[7]["choices"][1].lower())
        self.assertIn("seed", questions[7]["choices"][1].lower())
        self.assertIn("DNA-repair", questions[8]["choices"][1])
        self.assertIn("immune", questions[8]["choices"][1].lower())
        self.assertIn("tumour-suppression", questions[8]["choices"][1].lower())
        self.assertIn("incubation temperature", questions[9]["choices"][1].lower())
        self.assertIn("not sex chromosomes", questions[9]["choices"][1].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("galapagos-tortoise", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "galapagos-tortoise", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_zoologist_print_is_answer_light_duplex(self):
        deck = study_deck_for("galapagos-tortoise", "zoologist")
        sheet = study_print_html(
            deck,
            name="Galápagos tortoise",
            emoji="🐢",
            photo="/field-pack/photos/galapagos-tortoise.jpg?v=img2",
            photo_pos="50% 35%",
        )
        self.assertIn("Zoologist", sheet)
        self.assertNotIn("Junior Ranger", sheet)
        self.assertNotIn("Park Ranger", sheet)
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
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("galapagos-tortoise", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_lion_giraffe_elephant_penguin_and_flamingo_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_zoo = study_deck_for("african-lion", "zoologist")
        self.assertEqual(lion_zoo["source"], WIKI_LION)
        self.assertIn("hyoid", lion_zoo["questions"][0]["choices"][1])
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)
        self.assertEqual(lion_zoo["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion_zoo["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        giraffe_zoo = study_deck_for("reticulated-giraffe", "zoologist")
        self.assertEqual(giraffe_zoo["source"], WIKI_GIRAFFE)
        self.assertIn("Giraffa reticulata", giraffe_zoo["questions"][0]["choices"][1])
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giraffe_html)
        self.assertIn("Junior Ranger", giraffe_html)
        self.assertIn("Park Ranger", giraffe_html)
        self.assertEqual(giraffe_zoo["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_zoo["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_zoo = study_deck_for("african-elephant", "zoologist")
        self.assertEqual(elephant_zoo["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Loxodonta africana", elephant_zoo["questions"][0]["choices"][1])
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertIn("Junior Ranger", elephant_html)
        self.assertIn("Park Ranger", elephant_html)
        self.assertEqual(elephant_zoo["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_zoo["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        penguin_zoo = study_deck_for("african-penguin", "zoologist")
        self.assertEqual(penguin_zoo["source"], WIKI_AFRICAN_PENGUIN)
        self.assertIn("Spheniscus", penguin_zoo["questions"][0]["choices"][1])
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", penguin_html)
        self.assertIn("Junior Ranger", penguin_html)
        self.assertIn("Park Ranger", penguin_html)
        self.assertEqual(penguin_zoo["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin_zoo["push_further"], list(PUSH_FURTHER_PENGUIN))
        self.assertEqual(shipped_levels_for("caribbean-flamingo"), ("easy", "hard", "zoologist"))
        flamingo_zoo = study_deck_for("caribbean-flamingo", "zoologist")
        self.assertEqual(flamingo_zoo["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertIn("Mirandornithes", flamingo_zoo["questions"][0]["choices"][1])
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", flamingo_html)
        self.assertIn("Junior Ranger", flamingo_html)
        self.assertIn("Park Ranger", flamingo_html)
        self.assertEqual(flamingo_zoo["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(flamingo_zoo["push_further"], list(PUSH_FURTHER_FLAMINGO))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["galapagos-tortoise"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("Chelonoidis", data_js)
        self.assertIn("species-complex", data_js)
        self.assertIn("pinta-extinct", data_js)
        self.assertIn("megaherbivore", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = TORTOISE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=9", html)
        self.assertIn("study-cards-data.js?v=5", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Zoologist", print_tpl)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, print_tpl)


if __name__ == "__main__":
    unittest.main()
