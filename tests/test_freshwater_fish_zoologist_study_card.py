"""Freshwater fish Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_TWO_TOED_SLOTH,
    STUDY_SLOTS,
    TALK_ABOUT_FRESHWATER_FISH,
    TALK_ABOUT_LION,
    TALK_ABOUT_TWO_TOED_SLOTH,
    WIKI_FRESHWATER_FISH,
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
FISH = FP / "cards" / "freshwater-fish" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
SLOTH = FP / "cards" / "two-toed-sloth" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "What group do most familiar freshwater fish belong to?",
    "Within ray-finned fish, what are most living kinds?",
    "Is everyday “fish” one exclusive family tree?",
    "How do many freshwater fish take up salts from dilute pond water?",
    "How can a freshwater fish’s swim bladder be open or closed?",
    "How do anadromous and catadromous travelers differ when they breed?",
    "Can some freshwater fish handle a wide range of salt?",
    "Why can isolated lakes and river basins hold so many different fish kinds?",
    "What does comprehensive IUCN work find for assessed freshwater fish kinds (as a snapshot)?",
    "How do many freshwater fish pick up oxygen so well at the gills?",
)

ZOOLOGIST_IDS = (
    "ray-finned-majority-soft",
    "teleost-soft",
    "fish-grade-soft",
    "ionocytes-soft",
    "physostomous-physoclist-soft",
    "anadromy-catadromy-soft",
    "euryhaline-soft",
    "lake-islands-soft",
    "iucn-quarter-snapshot-soft",
    "countercurrent-gills-soft",
)

HARD_STEMS = (
    "How do most freshwater fish keep from swelling up in a pond?",
    "What does the lateral line along a freshwater fish’s side do?",
    "How do many bony freshwater fish stay at the right depth?",
    "What bony cover protects the gills of most bony freshwater fish?",
    "Do some kinds of freshwater fish travel between rivers and the sea?",
    "Can most kinds of freshwater fish live in both a pond and the ocean?",
    "Why do so many different kinds of fish live in fresh water?",
    "Is there one status letter for all freshwater fish?",
    "How can dams, dirty water, and water takeouts hurt freshwater fish?",
    "How can introduced fish and other invaders affect native freshwater fish?",
)

EASY_STEMS = (
    "Where do freshwater fish live?",
    "How is fresh water different from ocean water?",
    "How do freshwater fish get oxygen underwater?",
    "How do fins help freshwater fish move?",
    "How many kinds of fish live in fresh water?",
    "Do freshwater fish wear scales?",
    "How do most freshwater fish handle temperature?",
    "How do many freshwater fish begin life?",
    "What helps freshwater fish stay healthy in the wild?",
    "Do all fish need the ocean to live?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "41.24",
    "83%",
    "99%",
    "96%",
    "25%",
    "26%",
    "24%",
    "80%",
    "90%",
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
    "Rivers, lakes, ponds, and inland wetlands",
    "Fresh water has much less salt than the ocean",
    "Gills pull oxygen from the water",
    "Fins help push, steer, balance, and brake",
    "A huge share of all fish kinds live in fresh water",
    "Many wear protective scales, but not every kind",
    "Most follow the water’s temperature",
    "Many begin as eggs laid in the water",
    "Clean rivers and healthy wetlands",
    "plenty of fish spend their whole lives in fresh water",
    "Body salts stay higher than the water",
    "It feels water movement and nearby motion",
    "gas-filled swim bladder like a balloon",
    "A bony operculum",
    "Some kinds, such as salmon and eels, migrate between fresh and salt water at certain life stages",
    "most kinds are stenohaline",
    "Separate lakes and river systems help many different kinds evolve",
    "there is no single letter for the whole group; some thrive",
    "Barriers, dirty water, and water takeouts squeeze many kinds",
    "Introduced fish and other invaders can push native freshwater fish around",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class FreshwaterFishZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(
            shipped_levels_for("freshwater-fish"),
            ("easy", "hard", "zoologist"),
        )
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        self.assertIn("whale-shark", study_card_ids())
        self.assertIsNotNone(study_deck_for("whale-shark"))
        self.assertIsNotNone(study_deck_for("whale-shark", "hard"))
        self.assertIsNotNone(study_deck_for("whale-shark", "zoologist"))
        deck = study_deck_for("freshwater-fish", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_FRESHWATER_FISH)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Freshwater fish.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_FRESHWATER_FISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_FRESHWATER_FISH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("freshwater-fish", "zoologist")
        easy = study_deck_for("freshwater-fish", "easy")
        hard = study_deck_for("freshwater-fish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("freshwater-fish", "zoologist")
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
        self.assertIn("Actinopterygii", correct_choice_text(questions[0]))
        self.assertIn("ray-finned", correct_choice_text(questions[0]).lower())
        self.assertIn("bony rays", correct_choice_text(questions[0]).lower())
        self.assertIn("Teleosts", correct_choice_text(questions[1]))
        self.assertIn("advanced bony", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("grade", correct_choice_text(questions[2]).lower())
        self.assertIn("exclusive family tree", correct_choice_text(questions[2]).lower())
        self.assertIn("ionocytes", correct_choice_text(questions[3]).lower())
        self.assertIn("chloride cells", correct_choice_text(questions[3]).lower())
        self.assertIn("dilute", correct_choice_text(questions[3]).lower())
        self.assertIn("gulp", correct_choice_text(questions[4]).lower())
        self.assertIn("gas gland", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("anadromous", correct_choice_text(questions[5]).lower())
        self.assertIn("salmon", correct_choice_text(questions[5]).lower())
        self.assertIn("catadromous", correct_choice_text(questions[5]).lower())
        self.assertIn("eels", correct_choice_text(questions[5]).lower())
        self.assertIn("euryhaline", correct_choice_text(questions[6]).lower())
        self.assertIn("estuary", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("islands", correct_choice_text(questions[7]).lower())
        self.assertIn("speciation", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("quarter", correct_choice_text(questions[8]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[8]).lower())
        self.assertIn("not one letter", correct_choice_text(questions[8]).lower())
        self.assertIn("opposite", correct_choice_text(questions[9]).lower())
        self.assertIn("countercurrent", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Actinopterygii",
            "physostomous",
            "physoclist",
            "mitochondrion-rich",
            "biogeography",
            "stenohaline",
            "operculum",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_TWO_TOED_SLOTH + PUSH_FURTHER_TWO_TOED_SLOTH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_FRESHWATER_FISH + PUSH_FURTHER_FRESHWATER_FISH:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_FRESHWATER_FISH).lower()
        push = " ".join(PUSH_FURTHER_FRESHWATER_FISH).lower()
        self.assertIn("ray-finned", talk)
        self.assertIn("fish", talk)
        self.assertIn("ionocytes", talk)
        self.assertIn("salmon", talk)
        self.assertIn("eel", talk)
        self.assertIn("swim bladder", push)
        self.assertIn("lakes", push)
        self.assertIn("iucn", push)
        self.assertIn("kind", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("freshwater-fish", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "freshwater-fish", "packTemplate": "animals"})
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
        deck = study_deck_for("freshwater-fish", "zoologist")
        sheet = study_print_html(
            deck,
            name="River / lake fish",
            emoji="🐟",
            photo="/field-pack/photos/freshwater-fish.jpg?v=img2",
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
        for prompt in TALK_ABOUT_FRESHWATER_FISH + PUSH_FURTHER_FRESHWATER_FISH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_FRESHWATER_FISH, sheet)
        self.assertIn("Facts from Wikipedia, Freshwater fish.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("freshwater-fish", "zoologist"))
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
        self.assertEqual(shipped_levels_for("two-toed-sloth"), ("easy", "hard", "zoologist"))
        sloth_zoo = study_deck_for("two-toed-sloth", "zoologist")
        self.assertEqual(sloth_zoo["source"], WIKI_TWO_TOED_SLOTH)
        sloth_html = SLOTH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", sloth_html)
        self.assertEqual(sloth_zoo["talk_about"], list(TALK_ABOUT_TWO_TOED_SLOTH))
        self.assertEqual(sloth_zoo["push_further"], list(PUSH_FURTHER_TWO_TOED_SLOTH))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", jelly)
        self.assertNotIn("What do they eat?", jelly)
        self.assertNotIn("ray-finned-majority-soft", jelly)
        self.assertIsNotNone(study_deck_for("whale-shark"))
        self.assertIsNotNone(study_deck_for("whale-shark", "hard"))
        self.assertIsNotNone(study_deck_for("whale-shark", "zoologist"))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["freshwater-fish"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("ray-finned-majority-soft", data_js)
        self.assertIn("ionocytes-soft", data_js)
        self.assertIn("countercurrent-gills-soft", data_js)
        self.assertIn("iucn-quarter-snapshot-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = FISH.read_text(encoding="utf-8")
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
