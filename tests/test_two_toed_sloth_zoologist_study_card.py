"""Two-toed sloth Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_TWO_TOED_SLOTH,
    STUDY_SLOTS,
    TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER,
    TALK_ABOUT_LION,
    TALK_ABOUT_TORTOISE,
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
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
OTTER = FP / "cards" / "asian-small-clawed-otter" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Which bigger mammal group do two-toed sloths belong with?",
    "How do scientists place two-toed sloths next to anteaters?",
    "Two-toed (Choloepus) and three-toed (Bradypus) sloths look alike. Are they close cousins?",
    "Which sloth family do two-toed sloths sit in now?",
    "What bigger sloth story are living tree sloths leftover from?",
    "About how long ago did Linnaeus’s and Hoffmann’s two-toed sloths split?",
    "How do two-toed sloth necks break the mammal “rule of seven”?",
    "What does the name “two-toed sloth” actually count?",
    "How do two-toed sloths often come down a tree compared with three-toed sloths?",
    "How does a two-toed sloth’s menu compare with a specialist three-toed leaf-browser?",
)

ZOOLOGIST_IDS = (
    "xenarthra-soft",
    "pilosa-folivora-soft",
    "convergence-star-soft",
    "family-flux-soft",
    "ground-sloth-cousins-soft",
    "species-split-soft",
    "neck-count-exception-soft",
    "two-fingered-naming-soft",
    "head-first-down-soft",
    "broader-menu-soft",
)

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
    "exactly five",
    "exactly 5",
    "exactly six",
    "exactly 6",
    "exactly seven",
    "6.0 million",
    "7.0 million",
    "Vulnerable",
    "Endangered",
    "Critically",
    "Least Concern",
    "kg",
    "cm",
    "mph",
    "km/h",
)
REDO_THEMES = (
    "Two big curved claws (sometimes called two-fingered)",
    "Tropical rainforest trees of Central and South America",
    "Hanging upside down from tree branches",
    "Moving slowly helps them save energy",
    "Greenish algae in the fur help them blend",
    "Mostly leaves, plus shoots, fruit, and other plant bits",
    "Mostly at night, with quiet rest in the day",
    "The claws lock onto branches like hooks",
    "Healthy rainforest trees give them food and hiding spots",
    "slow is an energy plan and a way to stay hard to spot",
    "How many living kinds of two-toed sloth are there?",
    "multi-chambered",
    "ferment the tough leaves",
    "about a month",
    "moths, beetles, and algae",
    "moth fertilizes algae",
    "cannot shiver",
    "grows toward the extremities",
    "almost helpless on the ground",
    "good enough swimmers",
    "Least Concern — a snapshot",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class TwoToedSlothZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(
            shipped_levels_for("two-toed-sloth"),
            ("easy", "hard", "zoologist"),
        )
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("two-toed-sloth", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
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

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("two-toed-sloth", "zoologist")
        easy = study_deck_for("two-toed-sloth", "easy")
        hard = study_deck_for("two-toed-sloth", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("two-toed-sloth", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Xenarthra", correct_choice_text(questions[0]))
        self.assertIn("strange joints", correct_choice_text(questions[0]))
        self.assertIn("anteaters", correct_choice_text(questions[0]).lower())
        self.assertIn("armadillos", correct_choice_text(questions[0]).lower())
        self.assertIn("Pilosa", correct_choice_text(questions[1]))
        self.assertIn("Folivora", correct_choice_text(questions[1]))
        self.assertIn("leaf eaters", correct_choice_text(questions[1]).lower())
        self.assertIn("convergent", correct_choice_text(questions[2]).lower())
        self.assertIn("close cousins", correct_choice_text(questions[2]).lower())
        self.assertIn("Choloepodidae", correct_choice_text(questions[3]))
        self.assertIn("mylodontid", correct_choice_text(questions[3]).lower())
        self.assertIn("Megalonychidae", correct_choice_text(questions[3]))
        self.assertIn("ground sloths", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("6–7", correct_choice_text(questions[5]))
        self.assertIn("Andes", correct_choice_text(questions[5]))
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("fewer than seven", correct_choice_text(questions[6]).lower())
        self.assertIn("three-toed", correct_choice_text(questions[6]).lower())
        self.assertIn("front claws", correct_choice_text(questions[7]).lower())
        self.assertIn("hind feet still have three", correct_choice_text(questions[7]).lower())
        self.assertIn("head-first", correct_choice_text(questions[8]).lower())
        self.assertIn("three-toed", correct_choice_text(questions[8]).lower())
        self.assertIn("fruit", correct_choice_text(questions[9]).lower())
        self.assertIn("shoots", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Choloepodidae",
            "Megalonychidae",
            "Mylodontidae",
            "mylodontid",
            "Bradypus",
            "didactylus",
            "hoffmanni",
            "cladogram",
            "mtDNA",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_TORTOISE + PUSH_FURTHER_TORTOISE
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_TWO_TOED_SLOTH + PUSH_FURTHER_TWO_TOED_SLOTH:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_TWO_TOED_SLOTH).lower()
        push = " ".join(PUSH_FURTHER_TWO_TOED_SLOTH).lower()
        self.assertIn("xenarthra", talk)
        self.assertIn("family reunion", talk)
        self.assertIn("fool", talk)
        self.assertIn("rule of seven", talk)
        self.assertIn("ground sloth", push)
        self.assertIn("andes", push)
        self.assertIn("two-toed", push)
        self.assertIn("three-toed", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("two-toed-sloth", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "two-toed-sloth", "packTemplate": "animals"})
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
        deck = study_deck_for("two-toed-sloth", "zoologist")
        sheet = study_print_html(
            deck,
            name="Two-toed sloth",
            emoji="🦥",
            photo="/field-pack/photos/two-toed-sloth.jpg?v=img2",
            photo_pos="50% 45%",
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
        for prompt in TALK_ABOUT_TWO_TOED_SLOTH + PUSH_FURTHER_TWO_TOED_SLOTH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_TWO_TOED_SLOTH, sheet)
        self.assertIn("Facts from Wikipedia, Two-toed sloth.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("two-toed-sloth", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        self.assertLess(html.find("study-foot"), html.find("study-explore"))
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_other_animal_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_zoo = study_deck_for("african-lion", "zoologist")
        self.assertEqual(lion_zoo["source"], WIKI_LION)
        self.assertIn("hyoid", correct_choice_text(lion_zoo["questions"][0]))
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)
        self.assertEqual(lion_zoo["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion_zoo["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("asian-small-clawed-otter"), ("easy", "hard", "zoologist"))
        otter_zoo = study_deck_for("asian-small-clawed-otter", "zoologist")
        self.assertEqual(otter_zoo["source"], WIKI_ASIAN_SMALL_CLAWED_OTTER)
        otter_html = OTTER.read_text(encoding="utf-8")
        self.assertIn("Zoologist", otter_html)
        self.assertEqual(otter_zoo["talk_about"], list(TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER))
        self.assertEqual(otter_zoo["push_further"], list(PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER))
        sea = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", sea)
        self.assertNotIn("What do they eat?", sea)
        self.assertNotIn("xenarthra-soft", sea)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["two-toed-sloth"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("xenarthra-soft", data_js)
        self.assertIn("convergence-star-soft", data_js)
        self.assertIn("broader-menu-soft", data_js)
        self.assertIn("neck-count-exception-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = SLOTH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-cards-data.js?v=7", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Zoologist", print_tpl)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, print_tpl)
        main = html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]
        self.assertLess(main.find("study-foot"), main.find("study-explore"))
        self.assertLess(main.find("study-explore"), main.find("card-try-next"))


if __name__ == "__main__":
    unittest.main()
