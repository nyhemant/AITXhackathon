"""Reticulated giraffe Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_GIRAFFE,
    STUDY_SLOTS,
    TALK_ABOUT_GIRAFFE,
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
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "How do many scientists treat living giraffes today?",
    "Why must a giraffe’s heart work so hard to supply the brain?",
    "What helps protect a giraffe’s brain when the head drops to drink?",
    "How is a giraffe’s neck built, compared with most other mammals?",
    "How do male giraffes check whether a female is ready to mate?",
    "About how long is giraffe pregnancy, and how many calves are usual?",
    "What two main ideas does Wikipedia discuss for why giraffe necks became so long?",
    "What may the skin under a giraffe’s dark patches do besides camouflage?",
    "What is striking about a giraffe’s left recurrent laryngeal nerve?",
    "How do giraffe social groups actually work?",
)

ZOOLOGIST_IDS = (
    "species-split",
    "blood-pressure",
    "rete-mirabile",
    "cervical-length",
    "flehmen",
    "gestation",
    "neck-evolution",
    "spot-physiology",
    "laryngeal-nerve",
    "fission-fusion",
)

HARD_STEMS = (
    "What is the giraffe’s closest living relative?",
    "What does the old English name “camelopard” mean?",
    "What are a giraffe’s ossicones made of?",
    "How do male giraffes usually fight to establish dominance?",
    "How fast can a giraffe gallop in a short burst?",
    "How does a giraffe chew its food a second time?",
    "How do giraffes usually sleep?",
    "How tall is a newborn giraffe, and how soon can it run?",
    "What are the main threats to wild giraffes today?",
    "Why might a giraffe’s tongue be dark?",
)

EASY_STEMS = (
    "What record does a giraffe hold among living land animals?",
    "What do giraffes mostly eat?",
    "Why does a giraffe have such a long neck?",
    "What is special about a giraffe’s tongue?",
    "What is a baby giraffe called, and what can it do soon after birth?",
    "Where do wild giraffes mostly live?",
    "How does a giraffe drink water?",
    "What are the horn-like bumps on a giraffe’s head?",
    "What is special about a giraffe’s coat?",
    "Does a giraffe have extra neck bones compared with most mammals?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = ("mmHg", "280", "457", "2 m", "5 m", "150 beats", "11 kg", "7.5")
REDO_THEMES = (
    "tallest living land animal",
    "okapi",
    "camelopard",
    "sunburn",
    "as tall as a person",
    "30–37 mph",
    "four-chambered stomach",
    "few hours a day",
    "Habitat loss",
    "bushmeat",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class GiraffeZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("reticulated-giraffe", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_GIRAFFE)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Giraffe / Reticulated giraffe.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("reticulated-giraffe", "zoologist")
        easy = study_deck_for("reticulated-giraffe", "easy")
        hard = study_deck_for("reticulated-giraffe", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("reticulated-giraffe", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Giraffa reticulata", questions[0]["choices"][1])
        self.assertIn("often four", questions[0]["choices"][1])
        self.assertIn("roughly double", questions[1]["choices"][1])
        self.assertIn("rete mirabile", questions[2]["choices"][1])
        self.assertIn("jugular", questions[2]["choices"][1])
        self.assertIn("seven cervical vertebrae", questions[3]["choices"][1])
        self.assertIn("greatly lengthened", questions[3]["choices"][1])
        self.assertIn("vomeronasal", questions[4]["choices"][1])
        self.assertIn("flehmen", questions[4]["choices"][1])
        self.assertEqual(questions[5]["correct"], "A")
        self.assertIn("400–460", questions[5]["choices"][0])
        self.assertIn("usually one calf", questions[5]["choices"][0])
        self.assertIn("Competing browsers", questions[6]["choices"][1])
        self.assertIn("sexual selection", questions[6]["choices"][1])
        self.assertIn("sweat glands", questions[7]["choices"][1])
        self.assertIn("recurrent laryngeal", questions[8]["choices"][1].lower() + questions[8]["stem"].lower())
        self.assertIn("extraordinarily long", questions[8]["choices"][1])
        self.assertIn("Fission–fusion", questions[9]["choices"][1])
        self.assertIn("kinship", questions[9]["choices"][1])
        blob = " ".join(q["why"] for q in questions)
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("debate", questions[0]["why"])
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("reticulated-giraffe", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "reticulated-giraffe", "packTemplate": "animals"})
        self.assertIn(f">{CARD_TALK_H2}</h2>", html)
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
        deck = study_deck_for("reticulated-giraffe", "zoologist")
        sheet = study_print_html(
            deck,
            name="Reticulated giraffe",
            emoji="🦒",
            photo="/field-pack/photos/reticulated-giraffe.jpg?v=img2",
            photo_pos="50% 18%",
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
        for prompt in TALK_ABOUT_GIRAFFE + PUSH_FURTHER_GIRAFFE:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_GIRAFFE, sheet)
        self.assertIn("Facts from Wikipedia, Giraffe / Reticulated giraffe.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("reticulated-giraffe", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertNotIn("<details", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertRegex(html, r'<aside class="study-deepen"[^>]*\bhidden\b')
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_lion_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_zoo = study_deck_for("african-lion", "zoologist")
        self.assertEqual(lion_zoo["source"], WIKI_LION)
        self.assertIn("hyoid", lion_zoo["questions"][0]["choices"][1])
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["reticulated-giraffe"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("Giraffa reticulata", data_js)
        self.assertIn("rete mirabile", data_js)
        self.assertIn("vomeronasal", data_js)
        self.assertIn("fission", data_js.lower())
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=7", html)
        self.assertIn("study-cards-data.js?v=5", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Zoologist", print_tpl)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, print_tpl)


if __name__ == "__main__":
    unittest.main()
