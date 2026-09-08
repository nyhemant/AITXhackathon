"""African lion Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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

HARD_IDS = (
    "name",
    "pride-core",
    "prey",
    "speed",
    "status",
    "asia",
    "cub-senses",
    "gestation",
    "takeover",
    "white-lion",
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


class LionHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("african-lion", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_LION)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Lion.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("african-lion", "easy")
        hard = study_deck_for("african-lion", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("african-lion", "hard")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(HARD_IDS))
        self.assertEqual([q["stem"] for q in questions], list(HARD_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Panthera leo", correct_choice_text(questions[0]))
        self.assertIn("Related females", correct_choice_text(questions[1]))
        self.assertIn("hooved mammals", correct_choice_text(questions[2]))
        self.assertIn("30–37 mph", correct_choice_text(questions[3]))
        self.assertIn("Vulnerable", correct_choice_text(questions[4]))
        self.assertIn("snapshot", correct_choice_text(questions[4]).lower())
        self.assertIn("snapshot", questions[4]["why"].lower())
        self.assertNotIn("still listed as Vulnerable", questions[4]["why"])
        self.assertIn("Gir National Park", correct_choice_text(questions[5]))
        self.assertIn("around a week", correct_choice_text(questions[6]))
        self.assertIn("110 days", correct_choice_text(questions[7]))
        self.assertIn("kill existing young cubs", correct_choice_text(questions[8]))
        self.assertIn("leucism", correct_choice_text(questions[9]))
        blob = " ".join(q["why"] for q in questions)
        self.assertNotIn("43%", blob)
        self.assertNotIn("74.1", blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("african-lion", "hard")
        easy = study_deck_for("african-lion", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "african-lion", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("<details class=\"study-teach\">", html)
        self.assertNotIn("<details class=\"study-teach\" open", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
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
        deck = study_deck_for("african-lion", "hard")
        sheet = study_print_html(
            deck,
            name="African lion",
            emoji="🦁",
            photo="/field-pack/photos/african-lion.jpg?v=img2",
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
        for prompt in TALK_ABOUT_LION + PUSH_FURTHER_LION:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_LION, sheet)
        self.assertIn("Facts from Wikipedia, Lion.", sheet)
        for stem in HARD_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS:
            self.assertNotIn(stem, sheet)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["african-lion"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"hard":{"teach":[]', data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        self.assertIn("Panthera leo", data_js)
        self.assertIn("Gir National Park", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = LION.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn("Learn first", html)
        self.assertIn("Watch Live", html)
        self.assertIn("Zoologist", html.split("<main", 1)[1].split("</main>", 1)[0])
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
        hard_html = study_talk_html(study_deck_for("african-lion", "hard"))
        self.assertNotIn("study-teach", hard_html)
        self.assertIn('<details class="study-explore', hard_html)
        self.assertIn("Explore more", hard_html)
        self.assertIn("Talk about it", hard_html)
        self.assertIn("Push further", hard_html)


if __name__ == "__main__":
    unittest.main()
