"""African lion Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_LION,
    WIKI_LION,
    level_display_name,
    shipped_levels_for,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "What helps a lion roar, unlike a house cat’s continuous purr?",
    "When a lion curls its lips in a flehmen grimace, where does the scent go?",
    "What are a lion’s carnassial teeth built to do?",
    "Which two living lion subspecies do scientists recognize today?",
    "What can hide inside a lion’s dark tail tuft?",
    "Why do new males often kill young cubs after taking over a pride?",
    "How do lions compare with other wild cats?",
    "What are the greatest causes for concern in the lion’s decline?",
    "Why do lions hunt with short rushes instead of long chases?",
    "How do lions and spotted hyenas treat each other’s kills?",
)

ZOOLOGIST_IDS = (
    "roar-anatomy",
    "flehmen",
    "carnassials",
    "subspecies",
    "tail-spur",
    "takeover-estrus",
    "most-social",
    "decline-drivers",
    "burst-muscle",
    "hyena-contest",
)

HARD_STEMS = (
    "What is the lion’s scientific name?",
    "In a typical pride, who forms the stable core?",
    "What do wild lions mostly hunt?",
    "How do lions usually chase prey?",
    "How does the IUCN list wild lions today?",
    "Where do wild Asiatic lions live today?",
    "When can a newborn lion cub see?",
    "About how long is a lioness’s pregnancy, and how many cubs are usual?",
    "What often happens to young cubs when new males take over a pride?",
    "What makes a white lion white?",
)

EASY_STEMS = (
    "What do you call a group of lions?",
    "What do lions mostly eat?",
    "What sound is a lion famous for?",
    "Which lion usually grows a big fluffy mane?",
    "What is a baby lion called?",
    "Where do wild lions mostly live?",
    "How much of the day do lions often spend resting?",
    "In a pride, who usually does most of the hunting?",
    "What special tip does a lion’s tail have?",
    "Do lions really live in a jungle like in some cartoons?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class LionZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("african-lion", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_LION)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Lion.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("african-lion", "zoologist")
        easy = study_deck_for("african-lion", "easy")
        hard = study_deck_for("african-lion", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("african-lion", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("hyoid", questions[0]["choices"][1])
        self.assertIn("vomeronasal", questions[1]["choices"][1])
        self.assertIn("P4", questions[2]["choices"][1])
        self.assertIn("melanochaita", questions[3]["choices"][1])
        self.assertIn("function is unknown", questions[4]["choices"][1])
        self.assertEqual(questions[5]["correct"], "A")
        self.assertIn("estrus", questions[5]["choices"][0])
        self.assertEqual(questions[6]["correct"], "A")
        self.assertIn("most social", questions[6]["choices"][0])
        self.assertIn("Habitat loss", questions[7]["choices"][1])
        self.assertEqual(questions[8]["correct"], "A")
        self.assertIn("fast-twitch", questions[8]["choices"][0])
        self.assertIn("kleptoparasitism", questions[9]["choices"][1])
        blob = " ".join(q["why"] for q in questions)
        self.assertNotIn("43%", blob)
        self.assertNotIn("74.1", blob)
        self.assertNotIn("58.6", blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("african-lion", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "african-lion", "packTemplate": "animals"})
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
        deck = study_deck_for("african-lion", "zoologist")
        sheet = study_print_html(
            deck,
            name="African lion",
            emoji="🦁",
            photo="/field-pack/photos/african-lion.jpg?v=img2",
            photo_pos="50% 22%",
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
        for prompt in TALK_ABOUT_LION + PUSH_FURTHER_LION:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_LION, sheet)
        self.assertIn("Facts from Wikipedia, Lion.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("african-lion", "zoologist"))
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

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["african-lion"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("melanochaita", data_js)
        self.assertIn("vomeronasal", data_js)
        self.assertIn("kleptoparasitism", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=8", html)
        self.assertIn("study-cards-data.js?v=5", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Zoologist", print_tpl)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, print_tpl)


if __name__ == "__main__":
    unittest.main()
