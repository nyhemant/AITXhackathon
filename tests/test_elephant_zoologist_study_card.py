"""African elephant Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    WIKI_AFRICAN_ELEPHANT,
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
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "How do scientists treat living African elephants today?",
    "What is an elephant’s trunk, anatomically?",
    "How does an African elephant’s trunk tip differ from an Asian elephant’s?",
    "How can elephants pick up distant seismic signals?",
    "What happens when an adult bull elephant is in musth?",
    "Who besides the mother often helps care for an elephant calf?",
    "What can happen after an old elephant’s last molar set wears out?",
    "How do African elephants digest tough plants?",
    "What gene story is linked to elephants’ size and cancer resistance?",
    "Why are African elephants sometimes called megagardeners?",
)

ZOOLOGIST_IDS = (
    "species-split",
    "trunk-anatomy",
    "trunk-tip",
    "seismic",
    "musth",
    "allomothers",
    "last-molars",
    "hindgut",
    "tp53",
    "megagardener",
)

HARD_STEMS = (
    "How is an elephant’s trunk built, muscle-wise?",
    "How do elephants often talk across long distances?",
    "About how long is African elephant pregnancy?",
    "Why can an older matriarch be especially important in a drought?",
    "How do elephants replace worn chewing teeth?",
    "Why can such a heavy animal walk so quietly?",
    "How strong is an elephant’s sense of smell?",
    "What are the main threats to wild African elephants today?",
    "How can you usually tell an African elephant from an Asian elephant?",
    "Are elephants really afraid of mice?",
)

EASY_STEMS = (
    "What record does an African elephant hold among living land animals?",
    "What do African elephants eat?",
    "What does an elephant use its trunk for?",
    "Why does an African elephant have such big ears?",
    "What is a baby elephant called?",
    "Who usually leads an elephant herd?",
    "What are an elephant’s tusks?",
    "What sound is an elephant famous for?",
    "How can an African elephant swim?",
    "Can an elephant jump?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "20 copies",
    "twenty copies",
    "20 TP53",
    "Endangered",
    "Critically Endangered",
    "40,000",
    "40k",
    "60,000",
    "60k",
    "40 to 60",
    "40–60",
    "40-60",
)
REDO_THEMES = (
    "largest / heaviest living land animal",
    "grass, leaves, and bark",
    "grab, drink, spray",
    "to stay cool",
    "a baby elephant is a calf",
    "oldest female",
    "Very long teeth",
    "a trumpet",
    "snorkel",
    "cannot jump",
    "Tens of thousands",
    "low-frequency rumbles",
    "22 months",
    "memory of water",
    "like a conveyor",
    "Fatty cushion pads",
    "best senses of smell",
    "Ivory poaching",
    "larger ears",
    "afraid of mice",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class ElephantZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("african-elephant", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, African elephant / Elephant.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("african-elephant", "zoologist")
        easy = study_deck_for("african-elephant", "easy")
        hard = study_deck_for("african-elephant", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("african-elephant", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Loxodonta africana", questions[0]["choices"][1])
        self.assertIn("L. cyclotis", questions[0]["choices"][1])
        self.assertIn("IUCN", questions[0]["why"])
        self.assertIn("upper lip", questions[1]["choices"][1])
        self.assertIn("nose", questions[1]["choices"][1])
        self.assertIn("two finger-like", questions[2]["choices"][1])
        self.assertIn("Asian", questions[2]["choices"][1])
        self.assertIn("ground-borne", questions[3]["choices"][1])
        self.assertIn("feet", questions[3]["choices"][1])
        self.assertIn("trunk", questions[3]["choices"][1])
        self.assertIn("testosterone", questions[4]["choices"][1].lower())
        self.assertIn("temporal", questions[4]["choices"][1].lower())
        self.assertIn("allomother", questions[5]["choices"][1].lower())
        self.assertIn("starve", questions[6]["choices"][1].lower())
        self.assertIn("hindgut", questions[7]["choices"][1].lower())
        self.assertIn("TP53", questions[8]["choices"][1])
        self.assertIn("Peto", questions[8]["choices"][1])
        self.assertIn("seed", questions[9]["choices"][1].lower())
        self.assertIn("dung", questions[9]["choices"][1].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("african-elephant", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "african-elephant", "packTemplate": "animals"})
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
        deck = study_deck_for("african-elephant", "zoologist")
        sheet = study_print_html(
            deck,
            name="African elephant",
            emoji="🐘",
            photo="/field-pack/photos/african-elephant.jpg?v=img2",
            photo_pos="50% 28%",
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
        for prompt in TALK_ABOUT_ELEPHANT + PUSH_FURTHER_ELEPHANT:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_AFRICAN_ELEPHANT, sheet)
        self.assertIn("Facts from Wikipedia, African elephant / Elephant.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("african-elephant", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertNotIn("<details", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertRegex(html, r'<aside class="study-deepen"[^>]*\bhidden\b')
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_lion_and_giraffe_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_zoo = study_deck_for("african-lion", "zoologist")
        self.assertEqual(lion_zoo["source"], WIKI_LION)
        self.assertIn("hyoid", lion_zoo["questions"][0]["choices"][1])
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        giraffe_zoo = study_deck_for("reticulated-giraffe", "zoologist")
        self.assertEqual(giraffe_zoo["source"], WIKI_GIRAFFE)
        self.assertIn("Giraffa reticulata", giraffe_zoo["questions"][0]["choices"][1])
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giraffe_html)
        self.assertIn("Junior Ranger", giraffe_html)
        self.assertIn("Park Ranger", giraffe_html)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["african-elephant"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("Loxodonta africana", data_js)
        self.assertIn("allomother", data_js.lower())
        self.assertIn("TP53", data_js)
        self.assertIn("megagardener", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = ELEPHANT.read_text(encoding="utf-8")
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
