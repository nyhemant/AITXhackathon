"""Whale-shark Zoologist study-card: no teach, 5 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_LION,
    PUSH_FURTHER_STINGRAY_ZOOLOGIST,
    PUSH_FURTHER_WHALE_SHARK_ZOOLOGIST,
    TALK_ABOUT_LION,
    TALK_ABOUT_STINGRAY_ZOOLOGIST,
    TALK_ABOUT_WHALE_SHARK_ZOOLOGIST,
    WIKI_STINGRAY,
    WIKI_WHALE_SHARK,
    correct_choice_text,
    default_study_deck_for,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_talk_html,
    target_letter_for_deck_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
STINGRAY = FP / "cards" / "stingray" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_SLOTS = 5
SIGNED_LETTERS = ("A", "B", "A", "B", "C")

ZOOLOGIST_STEMS = (
    "How do scientists place the living whale shark, and what extinct relative does Wikipedia note?",
    "What is unusual about whale-shark life history for a fish, if we keep numbers soft?",
    "What tooth-like skin structures do whale sharks have beyond the tiny mouth teeth?",
    "How do researchers tell one whale shark from another without tagging every animal?",
    "Beyond the IUCN Endangered letter, what human pressures does Wikipedia emphasize for whale sharks?",
)

ZOOLOGIST_IDS = (
    "elasmobranchii-fossil-soft",
    "longevity-maturity-soft",
    "denticles-soft",
    "photo-id-soft",
    "ship-strike-bycatch-soft",
)

HARD_STEMS = (
    "Where does the whale shark sit in the shark family tree, if we keep names soft?",
    "How does a whale shark’s filter gear work beyond “open mouth and swim”?",
    "How has the IUCN listed the whale shark recently, if we treat the letter as a snapshot?",
    "Why do whale sharks sometimes gather in the same coastal spots year after year?",
    "What are a whale shark’s teeth like, compared with a great white’s big biting teeth?",
)

EASY_STEMS = (
    "What size record does the whale shark hold among living fish?",
    "Is a whale shark a whale?",
    "How does a whale shark mostly get its food?",
    "What is special about a whale shark’s pattern?",
    "Does a whale shark’s huge size mean it hunts people?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    " kg",
    " cm",
    " mph",
    "km/h",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class WhaleSharkZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("whale-shark", study_card_ids())
        self.assertEqual(shipped_levels_for("whale-shark"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("whale-shark", "easy"))
        self.assertIsNotNone(study_deck_for("whale-shark", "hard"))
        self.assertEqual(study_deck_for("whale-shark")["level"], "easy")
        default = default_study_deck_for("whale-shark")
        self.assertIsNotNone(default)
        self.assertEqual(default["level"], "easy")
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("whale-shark", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_WHALE_SHARK)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Whale shark.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_WHALE_SHARK_ZOOLOGIST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_WHALE_SHARK_ZOOLOGIST))
        self.assertEqual(len(deck["questions"]), ZOOLOGIST_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, list(SIGNED_LETTERS))
        self.assertEqual(
            letters,
            [target_letter_for_deck_slot("whale-shark", "zoologist", i) for i in range(1, 6)],
        )
        self.assertEqual(letters.count("A"), 2)
        self.assertEqual(letters.count("B"), 2)
        self.assertEqual(letters.count("C"), 1)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("whale-shark", "zoologist")
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("whale-shark", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 6)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("chondrichthyes", correct_choice_text(questions[0]).lower())
        self.assertIn("elasmobranchii", correct_choice_text(questions[0]).lower())
        self.assertIn("carpet shark", correct_choice_text(questions[0]).lower())
        self.assertIn("ferriolensis", correct_choice_text(questions[0]).lower())
        self.assertNotIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("late maturity", correct_choice_text(questions[1]).lower())
        self.assertIn("decades", correct_choice_text(questions[1]).lower())
        self.assertNotIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("dermal denticles", correct_choice_text(questions[2]).lower())
        self.assertIn("eyeball", correct_choice_text(questions[2]).lower())
        self.assertNotIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("spot", correct_choice_text(questions[3]).lower())
        self.assertIn("photo", correct_choice_text(questions[3]).lower())
        self.assertNotIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("bycatch", correct_choice_text(questions[4]).lower())
        self.assertIn("ship", correct_choice_text(questions[4]).lower())
        self.assertNotIn("soft", correct_choice_text(questions[4]).lower())
        for q in questions:
            for choice in q["choices"]:
                self.assertNotIn("(soft)", choice)
                self.assertNotIn("— soft", choice)
                self.assertNotIn("(exact years soft)", choice)
        why_blob = " ".join(q["why"] for q in questions)
        self.assertIn("soft", why_blob.lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])
        self.assertIn("rhincodon", blob.lower())
        self.assertIn("miocene", blob.lower())

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Elasmobranchii",
            "Chondrichthyes",
            "Rhincodon",
            "ferriolensis",
            "Burdigalian",
            "Miocene",
            "IUCN",
            "placoid",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_WHALE_SHARK_ZOOLOGIST + PUSH_FURTHER_WHALE_SHARK_ZOOLOGIST:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_WHALE_SHARK_ZOOLOGIST).lower()
        push = " ".join(PUSH_FURTHER_WHALE_SHARK_ZOOLOGIST).lower()
        self.assertIn("carpet shark", talk)
        self.assertIn("years", talk)
        self.assertIn("denticles", talk)
        self.assertIn("spot", push)
        self.assertIn("boats", push)
        self.assertIn("fossil", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("whale-shark", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        easy = study_deck_for("whale-shark", "easy")
        hard = study_deck_for("whale-shark", "hard")
        self.assertEqual([q["stem"] for q in easy["questions"]], list(EASY_STEMS))
        self.assertEqual([q["stem"] for q in hard["questions"]], list(HARD_STEMS))
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_zoologist_print_is_answer_light_duplex(self):
        deck = study_deck_for("whale-shark", "zoologist")
        sheet = study_print_html(
            deck,
            name="Whale shark",
            emoji="🦈",
            photo="/field-pack/photos/whale-shark.jpg?v=img2",
            photo_pos="50% 48%",
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
        for prompt in TALK_ABOUT_WHALE_SHARK_ZOOLOGIST + PUSH_FURTHER_WHALE_SHARK_ZOOLOGIST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_WHALE_SHARK, sheet)
        self.assertIn("Facts from Wikipedia, Whale shark.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("whale-shark", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        self.assertLess(html.find("study-foot"), html.find("study-explore"))
        self.assertIn(">0</span>/5", html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_stingray_decks_untouched(self):
        self.assertEqual(shipped_levels_for("stingray"), ("easy", "hard", "zoologist"))
        ray_zoo = study_deck_for("stingray", "zoologist")
        self.assertEqual(ray_zoo["source"], WIKI_STINGRAY)
        self.assertEqual(ray_zoo["talk_about"], list(TALK_ABOUT_STINGRAY_ZOOLOGIST))
        self.assertEqual(ray_zoo["push_further"], list(PUSH_FURTHER_STINGRAY_ZOOLOGIST))
        ray_html = STINGRAY.read_text(encoding="utf-8")
        self.assertIn("Zoologist", ray_html)
        self.assertIn("Junior Ranger", ray_html)
        self.assertIn("Park Ranger", ray_html)
        self.assertNotIn("elasmobranchii-fossil-soft", ray_html)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("whale-shark", payload)
        self.assertEqual(set(payload["whale-shark"]["levels"]), {"easy", "hard", "zoologist"})
        zoo = payload["whale-shark"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), ZOOLOGIST_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        self.assertEqual([q["correct"] for q in zoo["questions"]], list(SIGNED_LETTERS))
        self.assertEqual(payload["whale-shark"]["levels"]["hard"]["teach"], [])
        self.assertEqual(
            [q["stem"] for q in payload["whale-shark"]["levels"]["easy"]["questions"]],
            list(EASY_STEMS),
        )
        self.assertEqual(
            [q["stem"] for q in payload["whale-shark"]["levels"]["hard"]["questions"]],
            list(HARD_STEMS),
        )
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"whale-shark"', data_js)
        self.assertIn("elasmobranchii-fossil-soft", data_js)
        self.assertIn("longevity-maturity-soft", data_js)
        self.assertIn("denticles-soft", data_js)
        self.assertIn("photo-id-soft", data_js)
        self.assertIn("ship-strike-bycatch-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = WHALE_SHARK.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-id="whale-shark"', html)
        self.assertIn('data-study-level="easy"', html)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-cards-data.js?v=7", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Zoologist", print_tpl)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, print_tpl)
        main = _main(html)
        self.assertNotIn('<details class="study-explore', main)
        self.assertLess(main.find("study-foot"), main.find("card-try-next"))
        self.assertNotIn(">Talk</h2>", main)
        self.assertIn(">Quiz</h2>", main)


if __name__ == "__main__":
    unittest.main()
