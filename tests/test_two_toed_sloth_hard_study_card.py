"""Two-toed sloth Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_TWO_TOED_SLOTH,
    STUDY_SLOTS,
    TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER,
    TALK_ABOUT_LION,
    TALK_ABOUT_TWO_TOED_SLOTH,
    WIKI_ASIAN_SMALL_CLAWED_OTTER,
    WIKI_LION,
    WIKI_TWO_TOED_SLOTH,
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
SLOTH = FP / "cards" / "two-toed-sloth" / "index.html"
OCTOPUS = FP / "cards" / "seahorse" / "index.html"
OTTER = FP / "cards" / "asian-small-clawed-otter" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "How many living kinds of two-toed sloth are there?",
    "How does a two-toed sloth’s big stomach help with tough leaves?",
    "About how long can food take to finish digesting?",
    "What can live in a two-toed sloth’s grooved fur?",
    "Is the famous “moth fertilizes algae” story equally proven for two-toed sloths?",
    "Why can’t two-toed sloths warm up by shivering like many mammals?",
    "How does the outer hair grow for a hanging life?",
    "Why do two-toed sloths come down to the ground so rarely?",
    "If two-toed sloths are poor on the ground, can they swim?",
    "How should we read Least Concern for both living kinds?",
)

HARD_IDS = (
    "two-living-kinds-soft",
    "ferment-tummy-soft",
    "slow-digest-soft",
    "living-fur-soft",
    "moth-algae-note-soft",
    "no-shiver-soft",
    "upside-down-fur-soft",
    "rare-ground-trips-soft",
    "swim-surprise-soft",
    "lc-snapshot-soft",
)

EASY_STEMS = (
    "How many big curved claws does a two-toed sloth have on each front foot?",
    "Where do two-toed sloths live in the wild?",
    "How do two-toed sloths spend most of their lives?",
    "Why do two-toed sloths move so slowly?",
    "Why can a two-toed sloth’s fur look a little green?",
    "What do two-toed sloths mostly eat?",
    "When are two-toed sloths mostly active?",
    "How do their long curved claws help them?",
    "Why do two-toed sloths need healthy rainforest trees?",
    "Are two-toed sloths just lazy?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "Xenarthra",
    "Megalonychidae",
    "Mylodontidae",
    "Choloepodidae",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "Xenarthra",
    "four-chambered",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class TwoToedSlothHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("two-toed-sloth"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("two-toed-sloth", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("two-toed-sloth", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_TWO_TOED_SLOTH)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Two-toed sloth.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_TWO_TOED_SLOTH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_TWO_TOED_SLOTH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("two-toed-sloth", "easy")
        hard = study_deck_for("two-toed-sloth", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("two-toed-sloth", "hard")
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
        self.assertIn("Linnaeus", correct_choice_text(questions[0]))
        self.assertIn("Hoffmann", correct_choice_text(questions[0]))
        self.assertIn("Choloepus", correct_choice_text(questions[0]))
        self.assertIn("multi-chambered", correct_choice_text(questions[1]).lower())
        self.assertIn("ferment", correct_choice_text(questions[1]).lower())
        self.assertIn("month", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("moths", correct_choice_text(questions[3]).lower())
        self.assertIn("beetles", correct_choice_text(questions[3]).lower())
        self.assertIn("ecosystem", correct_choice_text(questions[3]).lower())
        self.assertIn("three-toed", correct_choice_text(questions[4]).lower())
        self.assertIn("debated", correct_choice_text(questions[4]).lower())
        self.assertIn("metabolism", correct_choice_text(questions[5]).lower())
        self.assertIn("shiver", correct_choice_text(questions[5]).lower())
        self.assertIn("extremities", correct_choice_text(questions[6]).lower())
        self.assertIn("helpless", correct_choice_text(questions[7]).lower())
        self.assertIn("potty", correct_choice_text(questions[7]).lower())
        self.assertIn("swimmers", correct_choice_text(questions[8]).lower())
        self.assertIn("water", correct_choice_text(questions[8]).lower())
        self.assertIn("least concern", correct_choice_text(questions[9]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("two-toed-sloth", "hard")
        easy = study_deck_for("two-toed-sloth", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "two-toed-sloth", "packTemplate": "animals"})
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
        deck = study_deck_for("two-toed-sloth", "hard")
        sheet = study_print_html(
            deck,
            name="Two-toed sloth",
            emoji="🦥",
            photo="/field-pack/photos/two-toed-sloth.jpg?v=img2",
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
        for prompt in TALK_ABOUT_TWO_TOED_SLOTH + PUSH_FURTHER_TWO_TOED_SLOTH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_TWO_TOED_SLOTH, sheet)
        self.assertIn("Facts from Wikipedia, Two-toed sloth.", sheet)
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
        self.assertEqual(shipped_levels_for("asian-small-clawed-otter"), ("easy", "hard", "zoologist"))
        otter_hard = study_deck_for("asian-small-clawed-otter", "hard")
        self.assertEqual(otter_hard["source"], WIKI_ASIAN_SMALL_CLAWED_OTTER)
        otter_html = OTTER.read_text(encoding="utf-8")
        self.assertIn("Zoologist", otter_html)
        self.assertEqual(otter_hard["talk_about"], list(TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER))
        self.assertEqual(otter_hard["push_further"], list(PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER))
        sea = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", sea)
        self.assertNotIn("card-study-pack", sea)
        self.assertNotIn("two-living-kinds-soft", sea)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["two-toed-sloth"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["two-toed-sloth"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("two-toed-sloth", data_js)
        self.assertIn("two-living-kinds-soft", data_js)
        self.assertIn("lc-snapshot-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = SLOTH.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("Learn first", html)
        self.assertIn("Watch Live", html)
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
        hard_html = study_talk_html(study_deck_for("two-toed-sloth", "hard"))
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
