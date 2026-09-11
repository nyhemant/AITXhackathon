"""American alligator Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_AMERICAN_ALLIGATOR,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_SEA_OTTER,
    STUDY_SLOTS,
    TALK_ABOUT_AMERICAN_ALLIGATOR,
    TALK_ABOUT_LION,
    TALK_ABOUT_SEA_OTTER,
    WIKI_AMERICAN_ALLIGATOR,
    WIKI_LION,
    WIKI_SEA_OTTER,
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
GATOR = FP / "cards" / "american-alligator" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
OTTER = FP / "cards" / "sea-otter" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "What living groups sit inside the family Alligatoridae?",
    "Where does the scientific name Alligator mississippiensis come from?",
    "Who is the American alligator’s closest living relative, and how long ago did the lineages split?",
    "How do caimans fit with American alligators?",
    "How does air move through an American alligator’s lungs?",
    "Do American alligators keep growing for their whole lives?",
    "How does nest temperature tend to steer hatchling sex?",
    "When an American alligator shuts its jaws, where does the large lower fourth tooth go?",
    "Why might an American alligator balance sticks on its head?",
    "Besides hunting animals, what unexpected food can American alligators take?",
)

ZOOLOGIST_IDS = (
    "alligatoridae-family-soft",
    "mississippiensis-name-soft",
    "chinese-sister-split-soft",
    "caiman-cousins-soft",
    "one-way-lungs-soft",
    "growth-slows-soft",
    "tsd-pattern-soft",
    "fourth-tooth-pocket-soft",
    "stick-lure-debate-soft",
    "fruit-seed-soft",
)

HARD_STEMS = (
    "How can snout shape help you tell an American alligator from an American crocodile?",
    "Why do American alligators stick to fresher water more than American crocodiles?",
    "How do American alligators handle cooler weather compared with American crocodiles?",
    "What can nest temperature help decide for baby alligators?",
    "What extra kind of sound can a male alligator send during courtship?",
    "Besides bellows, what is another loud social display?",
    "How can alligator holes reshape a wetland in a drought?",
    "How should we read the IUCN letter for American alligators?",
    "How many living alligator species are there?",
    "What do international CITES trade rules say for American alligators?",
)

EASY_STEMS = (
    "Where do American alligators live in the wild?",
    "How do American alligators power their swimming?",
    "What covers an American alligator’s back?",
    "What do American alligators use their strong jaws for?",
    "Why do American alligators bellow?",
    "How do alligator moms make a nest?",
    "What do baby alligators often look like when they hatch?",
    "What can a gator hole do in dry times?",
    "Why do healthy freshwater wetlands matter?",
    "Do alligator moms leave their eggs like many reptiles?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "88.7",
    "90.5",
    "94.1",
    "31.5",
    "32.5",
    "33.5",
    "34.5",
    "33 million",
    "43 years",
    "31 years",
    "kg",
    "cm",
    "mph",
    "km/h",
)
REDO_THEMES = (
    "Freshwater wetlands of the Southeastern United States — marshes, swamps, lakes, and slow rivers",
    "A strong muscular tail moves side to side and powers swimming",
    "Bony armor plates called scutes that help protect the back",
    "Catching fish, turtles, birds, and other wetland prey",
    "Loud bellows help claim space and find mates",
    "Females pile vegetation, sticks, and mud into a nest mound for the eggs",
    "They often have yellow bands, and moms help them to the water",
    "Digging holes can hold water in dry times for other wildlife too",
    "Healthy freshwater wetlands give food, nest sites, and shelter",
    "alligator moms guard the nest and carry hatchlings to the water",
    "American alligators have a broader U-shaped snout; American crocodiles tend toward a narrower V — a soft field tip",
    "tongue salt glands don’t work the same way as in American crocodiles",
    "They handle cooler climates better than tropical-leaning American crocodiles",
    "Nest temperature helps decide whether hatchlings are male or female",
    "Very low “felt” sounds (infrasound) that can ripple the water",
    "A loud head-slap is another social display",
    "Digging holes reshapes wetlands and helps other species find water and drier nest spots in a drought",
    "Least Concern is a snapshot — they were once listed as endangered from overhunting and later recovered enough to be delisted",
    "Only two living alligator species — the American alligator and a much smaller Chinese alligator",
    "Appendix II — international trade is allowed only with rules, not a free-for-all",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class AmericanAlligatorZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("american-alligator", study_card_ids())
        self.assertEqual(
            shipped_levels_for("american-alligator"),
            ("easy", "hard", "zoologist"),
        )
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("american-alligator", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_AMERICAN_ALLIGATOR)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, American alligator.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_AMERICAN_ALLIGATOR))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_AMERICAN_ALLIGATOR))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("american-alligator", "zoologist")
        easy = study_deck_for("american-alligator", "easy")
        hard = study_deck_for("american-alligator", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("american-alligator", "zoologist")
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
        self.assertIn("Alligatorinae", correct_choice_text(questions[0]))
        self.assertIn("Caimaninae", correct_choice_text(questions[0]))
        self.assertIn("eight", correct_choice_text(questions[0]).lower())
        self.assertIn("mississippiensis", correct_choice_text(questions[1]))
        self.assertIn("el lagarto", correct_choice_text(questions[1]).lower())
        self.assertIn("chinese", correct_choice_text(questions[2]).lower())
        self.assertIn("tens of millions", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("neotropical", correct_choice_text(questions[3]).lower())
        self.assertIn("not true alligator", correct_choice_text(questions[3]).lower())
        self.assertIn("one way", correct_choice_text(questions[4]).lower())
        self.assertIn("bird", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("slows", correct_choice_text(questions[5]).lower())
        self.assertIn("not forever", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("mid-range", correct_choice_text(questions[6]).lower())
        self.assertIn("male", correct_choice_text(questions[6]).lower())
        self.assertIn("female", correct_choice_text(questions[6]).lower())
        self.assertIn("pocket", correct_choice_text(questions[7]).lower())
        self.assertIn("fourth", correct_choice_text(questions[7]).lower())
        self.assertIn("stick", correct_choice_text(questions[8]).lower())
        self.assertIn("debated", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("fruit", correct_choice_text(questions[9]).lower())
        self.assertIn("seed", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Alligatorinae",
            "Caimaninae",
            "unidirectional",
            "determinate",
            "TSD",
            "frugivory",
            "mississippiensis",
            "archosaur",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_SEA_OTTER + PUSH_FURTHER_SEA_OTTER
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_AMERICAN_ALLIGATOR + PUSH_FURTHER_AMERICAN_ALLIGATOR:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_AMERICAN_ALLIGATOR).lower()
        push = " ".join(PUSH_FURTHER_AMERICAN_ALLIGATOR).lower()
        self.assertIn("alligatorid", talk)
        self.assertIn("croc", talk)
        self.assertIn("lung", talk)
        self.assertIn("bird", talk)
        self.assertIn("grow", talk)
        self.assertIn("chinese", push)
        self.assertIn("nest", push)
        self.assertIn("male", push)
        self.assertIn("stick", push)
        self.assertIn("debate", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("american-alligator", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "american-alligator", "packTemplate": "animals"})
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
        deck = study_deck_for("american-alligator", "zoologist")
        sheet = study_print_html(
            deck,
            name="American alligator",
            emoji="🐊",
            photo="/field-pack/photos/american-alligator.jpg?v=img2",
            photo_pos="50% 35%",
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
        for prompt in TALK_ABOUT_AMERICAN_ALLIGATOR + PUSH_FURTHER_AMERICAN_ALLIGATOR:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_AMERICAN_ALLIGATOR, sheet)
        self.assertIn("Facts from Wikipedia, American alligator.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("american-alligator", "zoologist"))
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
        self.assertEqual(shipped_levels_for("sea-otter"), ("easy", "hard", "zoologist"))
        otter_zoo = study_deck_for("sea-otter", "zoologist")
        self.assertEqual(otter_zoo["source"], WIKI_SEA_OTTER)
        otter_html = OTTER.read_text(encoding="utf-8")
        self.assertIn("Zoologist", otter_html)
        self.assertEqual(otter_zoo["talk_about"], list(TALK_ABOUT_SEA_OTTER))
        self.assertEqual(otter_zoo["push_further"], list(PUSH_FURTHER_SEA_OTTER))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", jelly)
        self.assertNotIn("What do they eat?", jelly)
        self.assertNotIn("alligatoridae-family-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["american-alligator"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("alligatoridae-family-soft", data_js)
        self.assertIn("mississippiensis-name-soft", data_js)
        self.assertIn("fruit-seed-soft", data_js)
        self.assertIn("stick-lure-debate-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = GATOR.read_text(encoding="utf-8")
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
