"""Clownfish Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_CLOWNFISH,
    PUSH_FURTHER_ELK,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PUFFIN,
    STUDY_SLOTS,
    TALK_ABOUT_CLOWNFISH,
    TALK_ABOUT_ELK,
    TALK_ABOUT_LION,
    TALK_ABOUT_PUFFIN,
    WIKI_ATLANTIC_PUFFIN,
    WIKI_CLOWNFISH,
    WIKI_ELK,
    WIKI_LION,
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
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
ELK = FP / "cards" / "elk" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
PUFFIN = FP / "cards" / "puffin" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "Clownfish are also called anemonefish. Which genus and family do they sit in?",
    "About how many living anemonefish species do scientists often name?",
    "How can the common “Nemo-like” pair of clownfish look different?",
    "How can a clownfish’s sex change if the breeding female is gone?",
    "How does size rank the fish that share one anemone?",
    "How does a clownfish settle into an anemone’s stinging tentacles?",
    "What do clownfish and sea anemones often give each other?",
    "Do all clownfish use the same kind of anemone host?",
    "Why does captive breeding matter for popular pet clownfish?",
    "How tightly are wild clownfish tied to reefs and anemones?",
)

HARD_IDS = (
    "amphiprion-soft",
    "two-dozen-species-soft",
    "ocellaris-vs-percula-soft",
    "protandry-soft",
    "size-hierarchy-soft",
    "mucus-acclimation-soft",
    "mutual-soft",
    "host-specialists-soft",
    "aquarium-trade-soft",
    "reef-tied-soft",
)

EASY_STEMS = (
    "Where do clownfish usually live?",
    "What do many clownfish look like?",
    "Where do clownfish find shelter?",
    "Why can a clownfish sit in stinging tentacles?",
    "What does a clownfish do when danger comes?",
    "How do clownfish usually live around an anemone?",
    "Where do clownfish put their eggs, and who helps?",
    "Where in the world do wild clownfish live?",
    "How can people help wild clownfish?",
    "Is there only one “Nemo” kind of clownfish?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "28 species",
    "29 species",
    "160 mm",
    "80 mm",
    "35 million",
    "10.5",
    "kg",
    " cm",
    " mph",
    "km/h",
)
RESERVED = (
    "28 species",
    "29 species",
    "160 mm",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class ClownfishHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertIn("clownfish", study_card_ids())
        self.assertEqual(shipped_levels_for("clownfish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("clownfish", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("clownfish", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_CLOWNFISH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Clownfish.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_CLOWNFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_CLOWNFISH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("clownfish", "easy")
        hard = study_deck_for("clownfish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("clownfish", "hard")
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
        self.assertIn("amphiprion", correct_choice_text(questions[0]).lower())
        self.assertIn("pomacentridae", correct_choice_text(questions[0]).lower())
        self.assertIn("damselfish", correct_choice_text(questions[0]).lower())
        self.assertIn("two dozen", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("ocellaris", correct_choice_text(questions[2]).lower())
        self.assertIn("percula", correct_choice_text(questions[2]).lower())
        self.assertIn("outline", correct_choice_text(questions[2]).lower())
        self.assertIn("born male", correct_choice_text(questions[3]).lower())
        self.assertIn("female", correct_choice_text(questions[3]).lower())
        self.assertIn("breeding female", correct_choice_text(questions[4]).lower())
        self.assertIn("breeding male", correct_choice_text(questions[4]).lower())
        self.assertIn("wait", correct_choice_text(questions[4]).lower())
        self.assertIn("mucus", correct_choice_text(questions[5]).lower())
        self.assertIn("not instant", correct_choice_text(questions[5]).lower())
        self.assertIn("shelter", correct_choice_text(questions[6]).lower())
        self.assertIn("mutual", correct_choice_text(questions[6]).lower())
        self.assertIn("ten", correct_choice_text(questions[7]).lower())
        self.assertIn("host", correct_choice_text(questions[7]).lower())
        self.assertIn("captive", correct_choice_text(questions[8]).lower())
        self.assertIn("wild reefs", correct_choice_text(questions[8]).lower())
        self.assertIn("depend", correct_choice_text(questions[9]).lower())
        self.assertIn("habitat health", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("clownfish", "hard")
        easy = study_deck_for("clownfish", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "clownfish", "packTemplate": "animals"})
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
        deck = study_deck_for("clownfish", "hard")
        sheet = study_print_html(
            deck,
            name="Clownfish",
            emoji="🐠",
            photo="/field-pack/photos/clownfish.jpg?v=img2",
            photo_pos="50% 35%",
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
        for prompt in TALK_ABOUT_CLOWNFISH + PUSH_FURTHER_CLOWNFISH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_CLOWNFISH, sheet)
        self.assertIn("Facts from Wikipedia, Clownfish.", sheet)
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
        self.assertEqual(shipped_levels_for("elk"), ("easy", "hard", "zoologist"))
        elk_hard = study_deck_for("elk", "hard")
        self.assertEqual(elk_hard["source"], WIKI_ELK)
        elk_html = ELK.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elk_html)
        self.assertEqual(elk_hard["talk_about"], list(TALK_ABOUT_ELK))
        self.assertEqual(elk_hard["push_further"], list(PUSH_FURTHER_ELK))
        self.assertEqual(shipped_levels_for("puffin"), ("easy", "hard", "zoologist"))
        puffin_hard = study_deck_for("puffin", "hard")
        self.assertEqual(puffin_hard["source"], WIKI_ATLANTIC_PUFFIN)
        puffin_html = PUFFIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", puffin_html)
        self.assertEqual(puffin_hard["talk_about"], list(TALK_ABOUT_PUFFIN))
        self.assertEqual(puffin_hard["push_further"], list(PUSH_FURTHER_PUFFIN))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", jelly)
        self.assertNotIn("What do they eat?", jelly)
        self.assertNotIn("amphiprion-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["clownfish"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["clownfish"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("clownfish", data_js)
        self.assertIn("amphiprion-soft", data_js)
        self.assertIn("reef-tied-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = CLOWNFISH.read_text(encoding="utf-8")
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
        for stem in HARD_STEMS:
            self.assertNotIn(stem, print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        hard_html = study_talk_html(study_deck_for("clownfish", "hard"))
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
