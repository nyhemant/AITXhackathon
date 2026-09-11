"""Polar bear Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_FRESHWATER_FISH,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_POLAR_BEAR,
    STUDY_SLOTS,
    TALK_ABOUT_FRESHWATER_FISH,
    TALK_ABOUT_LION,
    TALK_ABOUT_POLAR_BEAR,
    WIKI_FRESHWATER_FISH,
    WIKI_LION,
    WIKI_POLAR_BEAR,
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
BEAR = FP / "cards" / "polar-bear" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
FISH = FP / "cards" / "freshwater-fish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Which mammal family and order do polar bears belong to?",
    "Why did scientists keep polar bears in Ursus instead of Thalarctos?",
    "How do a polar bear’s skull and teeth compare with a typical brown bear’s?",
    "What happens after polar bears mate in spring?",
    "How does a pregnant polar bear fuel the maternity-den months?",
    "How do adult male and female polar bears compare in size?",
    "How are wild polar bears grouped for study and care?",
    "What kind of ice do polar bears prefer to live on?",
    "Does the global Vulnerable letter tell the same story for every polar bear group?",
    "How do polar bears often find seals across the ice?",
)

ZOOLOGIST_IDS = (
    "ursidae-soft",
    "thalarctos-flux-soft",
    "hypercarnivore-soft",
    "delayed-implantation-soft",
    "capital-denning-soft",
    "sexual-dimorphism-soft",
    "subpopulations-soft",
    "pagophily-soft",
    "status-nuance-soft",
    "smell-hunters-soft",
)

HARD_STEMS = (
    "Who are polar bears’ closest living relatives?",
    "Why are polar bears counted as marine mammals?",
    "How do polar bears often hunt seals at the ice?",
    "Which part of a seal do polar bears prefer to eat first?",
    "How do polar bear guard hairs help besides looking pale?",
    "Can a polar bear’s fur and fat keep it too warm?",
    "How should we read the IUCN letter for polar bears?",
    "What do international CITES trade rules say for polar bears?",
    "How can less summer sea ice change polar bear hunting?",
    "Can polar bears and brown bears have cubs together?",
)

EASY_STEMS = (
    "Where do polar bears live in the wild?",
    "Why does polar bear fur look white?",
    "What color is the skin under a polar bear’s fur?",
    "How do a polar bear’s huge paws help?",
    "What do polar bears specialize in hunting?",
    "How do polar bears swim?",
    "How does a polar bear stay warm in the cold?",
    "Where do polar bear moms have their cubs?",
    "Why does healthy sea ice matter for polar bears?",
    "Do polar bears live at the South Pole?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "22,000",
    "31,000",
    "2050",
    "climate change",
    "global warming",
    "kg",
    "cm",
    "mph",
    "km/h",
)
REDO_THEMES = (
    "On Arctic sea ice and nearby coasts — not the Antarctic",
    "Guard hairs are see-through and scatter light",
    "Black — you can see it on the nose and foot pads",
    "They spread weight on ice and paddle when the bear swims",
    "Seals (especially ringed seals) hunted from the ice",
    "They are strong swimmers that paddle with their front paws",
    "A thick layer of fat under the skin helps keep them warm",
    "In a winter den; cubs stay with mom a long time",
    "Healthy sea ice helps them reach seal hunting spots",
    "penguins, not polar bears, live in Antarctica",
    "Brown bears (Ursus arctos) — same genus Ursus (U. maritimus)",
    "They depend on sea-ice marine food webs",
    "They often wait at a seal breathing hole or ice edge",
    "The energy-rich blubber, more than the lean meat",
    "Translucent hollow guard hairs scatter light",
    "they can overheat if they run hard",
    "IUCN lists them Vulnerable — the letter is a snapshot, driven mainly by a sea-ice loss outlook",
    "They are on Appendix II, so international trade is allowed but regulated",
    "Less summer sea ice makes seal hunting harder and means more time on land",
    "“pizzly” or “grolar” hybrids can happen",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class PolarBearZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(
            shipped_levels_for("polar-bear"),
            ("easy", "hard", "zoologist"),
        )
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("polar-bear", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_POLAR_BEAR)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Polar bear.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_POLAR_BEAR))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_POLAR_BEAR))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("polar-bear", "zoologist")
        easy = study_deck_for("polar-bear", "easy")
        hard = study_deck_for("polar-bear", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("polar-bear", "zoologist")
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
        self.assertIn("Ursidae", correct_choice_text(questions[0]))
        self.assertIn("Carnivora", correct_choice_text(questions[0]))
        self.assertIn("Ursus", correct_choice_text(questions[0]))
        self.assertIn("fossils", correct_choice_text(questions[1]).lower())
        self.assertIn("hybrid", correct_choice_text(questions[1]).lower())
        self.assertIn("ursus", correct_choice_text(questions[1]).lower())
        self.assertIn("cutting meat", correct_choice_text(questions[2]).lower())
        self.assertIn("seal predator", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("embryo", correct_choice_text(questions[3]).lower())
        self.assertIn("pause", correct_choice_text(questions[3]).lower())
        self.assertIn("fall", correct_choice_text(questions[3]).lower())
        self.assertIn("stored fat", correct_choice_text(questions[4]).lower())
        self.assertIn("capital", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("males", correct_choice_text(questions[5]).lower())
        self.assertIn("larger", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("19", correct_choice_text(questions[6]))
        self.assertIn("subpopulation", correct_choice_text(questions[6]).lower())
        self.assertIn("region", correct_choice_text(questions[6]).lower())
        self.assertIn("pagophilic", correct_choice_text(questions[7]).lower())
        self.assertIn("annual sea ice", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[8]).lower())
        self.assertIn("subpopulation", correct_choice_text(questions[8]).lower())
        self.assertIn("ice outlook", correct_choice_text(questions[8]).lower())
        self.assertIn("smell", correct_choice_text(questions[9]).lower())
        self.assertIn("breathing hole", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "hypercarnivore",
            "pagophilic",
            "Carnivora",
            "dimorphism",
            "circumpolar",
            "capital-breeding",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_FRESHWATER_FISH + PUSH_FURTHER_FRESHWATER_FISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_POLAR_BEAR + PUSH_FURTHER_POLAR_BEAR:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_POLAR_BEAR).lower()
        push = " ".join(PUSH_FURTHER_POLAR_BEAR).lower()
        self.assertIn("delayed implantation", talk)
        self.assertIn("ursus", talk)
        self.assertIn("thalarctos", talk)
        self.assertIn("subpopulation", talk)
        self.assertIn("fat", push)
        self.assertIn("region", push)
        self.assertIn("skull", push)
        self.assertIn("meat", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("polar-bear", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "polar-bear", "packTemplate": "animals"})
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
        deck = study_deck_for("polar-bear", "zoologist")
        sheet = study_print_html(
            deck,
            name="Polar bear",
            emoji="🐻‍❄️",
            photo="/field-pack/photos/polar-bear.jpg?v=img2",
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
        for prompt in TALK_ABOUT_POLAR_BEAR + PUSH_FURTHER_POLAR_BEAR:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_POLAR_BEAR, sheet)
        self.assertIn("Facts from Wikipedia, Polar bear.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("polar-bear", "zoologist"))
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
        self.assertEqual(shipped_levels_for("freshwater-fish"), ("easy", "hard", "zoologist"))
        fish_zoo = study_deck_for("freshwater-fish", "zoologist")
        self.assertEqual(fish_zoo["source"], WIKI_FRESHWATER_FISH)
        fish_html = FISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", fish_html)
        self.assertEqual(fish_zoo["talk_about"], list(TALK_ABOUT_FRESHWATER_FISH))
        self.assertEqual(fish_zoo["push_further"], list(PUSH_FURTHER_FRESHWATER_FISH))
        sea = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", sea)
        self.assertNotIn("card-study-pack", sea)
        self.assertNotIn("ursidae-soft", sea)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["polar-bear"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("ursidae-soft", data_js)
        self.assertIn("thalarctos-flux-soft", data_js)
        self.assertIn("smell-hunters-soft", data_js)
        self.assertIn("status-nuance-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = BEAR.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
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
