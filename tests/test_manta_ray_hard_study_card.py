"""Manta-ray Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
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
MANTA = FP / "cards" / "manta-ray" / "index.html"
OCTOPUS = FP / "cards" / "stingray" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "Where do mantas sit in the genus tree now, if we keep that rename soft?",
    "What three kinds of manta do people name now, if we keep sizes and lives soft?",
    "What family do mantas share with other eagle and devil rays, if we keep that map soft?",
    "How do spongy gill-raker plates help a manta eat?",
    "How do cephalic fins and filter tissue work together, if we keep that feeding path soft?",
    "Why must mantas keep swimming to breathe, if we keep those spiracles soft?",
    "Why do manta populations recover slowly, if we keep that breeding story soft?",
    "How should we read IUCN letters for reef and giant oceanic mantas, if we keep those snapshots soft?",
    "Why can demand for dried gill rakers threaten mantas, if we keep that trade story kid-safe and soft?",
    "How do international agreements protect mantas — and what still matters near shore?",
)

HARD_IDS = (
    "mobula-soft",
    "three-kinds-soft",
    "eagle-ray-family-soft",
    "gill-rakers-soft",
    "filter-deepen-soft",
    "must-keep-swimming-soft",
    "slow-breeders-soft",
    "vu-en-soft",
    "gill-plate-trade-soft",
    "cms-care-soft",
)

EASY_STEMS = (
    "What do a manta’s broad fins work like?",
    "What sit beside a manta’s wide forward mouth?",
    "How do mantas gather their food?",
    "How big can a manta get, if we keep the size soft?",
    "How do reef mantas and giant oceanic mantas use the sea?",
    "How are baby mantas born?",
    "Why do mantas visit coral cleaning stations?",
    "What do mantas sometimes do at the surface — and do we know why?",
    "How can people help mantas?",
    "Do a manta’s horns mean it is dangerous?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "7 m",
    "23 ft",
    "5.5 m",
    "18 ft",
    "6 m",
    "20 ft",
    "12–13",
    "12-13",
    "372",
    "$73",
    "$40",
    "$500",
    "$1 million",
    " kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "7 m",
    "23 ft",
    "5.5 m",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class MantaRayHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("manta-ray", study_card_ids())
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("manta-ray", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("manta-ray", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_MANTA_RAY)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Manta ray.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_MANTA_RAY))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_MANTA_RAY))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("manta-ray", "easy")
        hard = study_deck_for("manta-ray", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("manta-ray", "hard")
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
        self.assertIn("mobula", correct_choice_text(questions[0]).lower())
        self.assertIn("junior synonym", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("alfredi", correct_choice_text(questions[1]).lower())
        self.assertIn("birostris", correct_choice_text(questions[1]).lower())
        self.assertIn("yarae", correct_choice_text(questions[1]).lower())
        self.assertIn("myliobatidae", correct_choice_text(questions[2]).lower())
        self.assertIn("mobulinae", correct_choice_text(questions[2]).lower())
        self.assertIn("gill-raker", correct_choice_text(questions[3]).lower())
        self.assertIn("plankton", correct_choice_text(questions[3]).lower())
        self.assertIn("cephalic", correct_choice_text(questions[4]).lower())
        self.assertIn("filter", correct_choice_text(questions[4]).lower())
        self.assertIn("spiracles", correct_choice_text(questions[5]).lower())
        self.assertIn("vestigial", correct_choice_text(questions[5]).lower())
        self.assertIn("one pup", correct_choice_text(questions[6]).lower())
        self.assertIn("over a year", correct_choice_text(questions[6]).lower())
        self.assertIn("vulnerable", correct_choice_text(questions[7]).lower())
        self.assertIn("endangered", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[7]).lower())
        self.assertIn("gill rakers", correct_choice_text(questions[8]).lower())
        self.assertIn("traditional", correct_choice_text(questions[8]).lower())
        self.assertIn("cms", correct_choice_text(questions[9]).lower())
        self.assertIn("bycatch", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("manta-ray", "hard")
        easy = study_deck_for("manta-ray", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "manta-ray", "packTemplate": "animals"})
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
        deck = study_deck_for("manta-ray", "hard")
        sheet = study_print_html(
            deck,
            name="Manta ray",
            emoji="🐟",
            photo="/field-pack/photos/manta-ray.jpg?v=img2",
            photo_pos="50% 48%",
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
        for prompt in TALK_ABOUT_MANTA_RAY + PUSH_FURTHER_MANTA_RAY:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_MANTA_RAY, sheet)
        self.assertIn("Facts from Wikipedia, Manta ray.", sheet)
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
        octo = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", octo)
        self.assertNotIn("card-study-pack", octo)
        self.assertNotIn("mobula-soft", octo)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["manta-ray"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["manta-ray"]["levels"])
        self.assertEqual(payload["manta-ray"]["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("manta-ray", data_js)
        self.assertIn("mobula-soft", data_js)
        self.assertIn("cms-care-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = MANTA.read_text(encoding="utf-8")
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
        hard_html = study_talk_html(study_deck_for("manta-ray", "hard"))
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
