"""Reticulated giraffe Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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

HARD_IDS = (
    "relative",
    "name",
    "ossicones-deeper",
    "necking",
    "speed",
    "ruminate",
    "sleep",
    "calf-size",
    "threats",
    "tongue-why",
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
BRITTLE = ("4.6", "1.7", "5 ft 7", "45 cm", "45cm", "18 in", "Vulnerable", "Endangered")


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class GiraffeHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("reticulated-giraffe", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("reticulated-giraffe", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_GIRAFFE)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Giraffe / Reticulated giraffe.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("reticulated-giraffe", "easy")
        hard = study_deck_for("reticulated-giraffe", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("reticulated-giraffe", "hard")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(HARD_IDS))
        self.assertEqual([q["stem"] for q in questions], list(HARD_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("okapi", correct_choice_text(questions[0]))
        self.assertIn("Giraffidae", correct_choice_text(questions[0]))
        self.assertIn("leopard-like spots", correct_choice_text(questions[1]))
        self.assertIn("Ossified cartilage", correct_choice_text(questions[2]))
        self.assertIn("fused to the skull", correct_choice_text(questions[2]))
        self.assertIn("swing their necks", correct_choice_text(questions[3]))
        self.assertIn("30–37 mph", correct_choice_text(questions[4]))
        self.assertIn("four-chambered stomach", correct_choice_text(questions[5]))
        self.assertIn("few hours a day", correct_choice_text(questions[6]))
        self.assertIn("as tall as a person", correct_choice_text(questions[7]))
        self.assertIn("run within hours", correct_choice_text(questions[7]))
        self.assertIn("Habitat loss", correct_choice_text(questions[8]))
        self.assertIn("bushmeat", correct_choice_text(questions[8]))
        self.assertIn("sunburn", correct_choice_text(questions[9]))
        blob = " ".join(q["why"] for q in questions)
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("reticulated-giraffe", "hard")
        easy = study_deck_for("reticulated-giraffe", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "reticulated-giraffe", "packTemplate": "animals"})
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
        deck = study_deck_for("reticulated-giraffe", "hard")
        sheet = study_print_html(
            deck,
            name="Reticulated giraffe",
            emoji="🦒",
            photo="/field-pack/photos/reticulated-giraffe.jpg?v=img2",
            photo_pos="50% 18%",
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
        for prompt in TALK_ABOUT_GIRAFFE + PUSH_FURTHER_GIRAFFE:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_GIRAFFE, sheet)
        self.assertIn("Facts from Wikipedia, Giraffe / Reticulated giraffe.", sheet)
        for stem in HARD_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS:
            self.assertNotIn(stem, sheet)

    def test_lion_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_hard = study_deck_for("african-lion", "hard")
        self.assertEqual(lion_hard["source"], WIKI_LION)
        self.assertIn("Panthera leo", correct_choice_text(lion_hard["questions"][0]))
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["reticulated-giraffe"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["reticulated-giraffe"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("reticulated-giraffe", data_js)
        self.assertIn("okapi", data_js)
        self.assertIn("camelopard", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn("Learn first", html)
        self.assertIn("Watch Live", html)
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
        hard_html = study_talk_html(study_deck_for("reticulated-giraffe", "hard"))
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
