"""American alligator Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger + Zoologist are sibling levels)."""

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
    LEVEL_DISPLAY_NAMES,
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
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_try_next_ids,
    target_letter_for_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
GATOR = FP / "cards" / "american-alligator" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
OTTER = FP / "cards" / "sea-otter" / "index.html"
PRINT_KIT = FP / "js" / "print-kit.js"
STUDY_JS = FP / "js" / "study-card.js"
STYLES = FP / "css" / "styles.css"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"

GENERIC_WORKSHEET = (
    "What do they eat?",
    "Where is home?",
    "What is their superpower?",
    "Baby or grown-up?",
    "I want to teach about…",
    "Food detective",
    "Meat eater or plant eater?",
    "What do you notice?",
)

TEACH = (
    "Live in freshwater wetlands of the Southeastern United States",
    "Powerful tails for swimming",
    "Bony armor plates (scutes) along the back",
    "Moms build nest mounds and watch over eggs and babies",
    "Healthy marshes and swamps help them thrive",
)

STEMS = (
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

QIDS = (
    "se-wetland-home",
    "tail-motor-soft",
    "armor-plates-soft",
    "big-bites-soft",
    "bellow-talk-soft",
    "nest-mounds-soft",
    "baby-bands-soft",
    "gator-holes-soft",
    "soft-wetland-care",
    "mom-does-care-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Endangered",
    "Vulnerable",
    "Critically",
    "Least Concern",
    "CITES",
    "ESA",
    "Endangered Species",
    "mississippiensis",
    "infrasound",
    "TSD",
    "temperature-dependent",
    "keystone",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "IUCN",
    "Least Concern",
    "CITES",
    "ESA",
    "infrasound",
    "TSD",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class AmericanAlligatorEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger(self):
        self.assertIn("american-alligator", study_card_ids())
        self.assertNotIn("jellyfish", study_card_ids())
        self.assertEqual(
            study_card_ids(),
            (
                "african-lion",
                "reticulated-giraffe",
                "african-elephant",
                "african-penguin",
                "caribbean-flamingo",
                "galapagos-tortoise",
                "zebra",
                "nile-hippo",
                "sumatran-tiger",
                "western-lowland-gorilla",
                "cheetah",
                "red-panda",
                "koala",
                "chimpanzee",
                "orangutan",
                "giant-panda",
                "ring-tailed-lemur",
                "ostrich",
                "warthog",
                "shark",
                "asian-small-clawed-otter",
                "two-toed-sloth",
                "freshwater-fish",
                "polar-bear",
                "sea-otter",
                "american-alligator",
                "american-bison",
                "elk",
                "puffin",
                "clownfish",
                "crab",
            ),
        )
        self.assertEqual(shipped_levels_for("american-alligator"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("american-alligator", "hard"))
        self.assertIsNotNone(study_deck_for("american-alligator", "zoologist"))
        self.assertIsNone(study_deck_for("jellyfish"))
        deck = study_deck_for("american-alligator")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "american-alligator")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_AMERICAN_ALLIGATOR)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, American alligator.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_AMERICAN_ALLIGATOR))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_AMERICAN_ALLIGATOR))
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)
        for q in deck["questions"]:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(str(q["why"]).strip())
        blob = " ".join(deck["teach"] + [q["stem"] + q["why"] for q in deck["questions"]])
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)
        self.assertIn("southeastern", blob.lower())
        self.assertIn("wetland", blob.lower())
        self.assertIn("tail", blob.lower())
        self.assertIn("scute", blob.lower())
        self.assertIn("fish", blob.lower())
        self.assertIn("bellow", blob.lower())
        self.assertIn("nest", blob.lower())
        self.assertIn("yellow", blob.lower())
        self.assertIn("gator hole", blob.lower())
        self.assertIn("guard", blob.lower())
        self.assertEqual(
            WIKI_AMERICAN_ALLIGATOR,
            "https://en.wikipedia.org/wiki/American_alligator",
        )

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        otter = study_deck_for("sea-otter")
        self.assertEqual(otter["source"], WIKI_SEA_OTTER)
        self.assertEqual(otter["talk_about"], list(TALK_ABOUT_SEA_OTTER))
        self.assertEqual(otter["push_further"], list(PUSH_FURTHER_SEA_OTTER))
        self.assertEqual(shipped_levels_for("sea-otter"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("sea-otter", "hard"))
        self.assertIsNotNone(study_deck_for("sea-otter", "zoologist"))
        self.assertEqual(shipped_levels_for("polar-bear"), ("easy", "hard", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "american-alligator", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("card-study-pack", html)
        self.assertIn("Learn first", html)
        self.assertIn('<details class="study-teach">', html)
        self.assertNotIn('<details class="study-teach" open', html)
        self.assertIn('<summary class="study-teach-kicker">', html)
        self.assertIn("tap to open", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        for prompt in TALK_ABOUT_AMERICAN_ALLIGATOR + PUSH_FURTHER_AMERICAN_ALLIGATOR:
            self.assertIn(prompt, html)
        self.assertIn("Show answers", html)
        self.assertIn("Score", html)
        for line in TEACH:
            self.assertIn(line, html)
        for stem in STEMS:
            self.assertIn(stem, html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, html)
        visible = _text(html)
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        self.assertIn('class="study-level-picker"', html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertNotIn('class="study-level-badge"', html)
        self.assertEqual(html.count('role="group"'), 2)
        self.assertIn("study-level-picker-bottom", html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, html)
        self.assertIn(
            "Freshwater wetlands of the Southeastern United States — marshes, swamps, lakes, and slow rivers",
            html,
        )
        self.assertIn(
            "No — alligator moms guard the nest and carry hatchlings to the water",
            html,
        )
        self.assertIn("Facts from Wikipedia, American alligator.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "jellyfish", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("Where do American alligators live in the wild?", html)
        jelly = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("Where do American alligators live in the wild?", jelly)

    def test_published_american_alligator_card_matches_easy_deck(self):
        html = GATOR.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("card-page-photo", main)
        self.assertIn("/field-pack/photos/american-alligator.jpg", main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "american-alligator"', html)
        self.assertNotIn('"id": "sea-otter"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=42", html)
        self.assertIn('<details class="study-teach">', main)
        self.assertNotIn('<details class="study-teach" open', main)
        self.assertNotIn('<div class="study-teach">', main)
        self.assertIn("Talk about it", main)
        self.assertIn("Push further", main)
        self.assertIn('<details class="study-explore', main)
        self.assertIn("Explore more", main)
        self.assertNotIn('<aside class="study-deepen"', main)
        self.assertLess(main.find("study-foot"), main.find("study-explore"))
        self.assertLess(main.find("study-explore"), main.find("card-try-next"))
        visible = _text(main)
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        self.assertIn('class="study-level-picker"', main)
        self.assertIn('data-study-pick="easy"', main)
        self.assertIn('data-study-pick="hard"', main)
        self.assertIn('data-study-pick="zoologist"', main)
        self.assertNotIn('class="study-level-badge"', main)
        self.assertIn("Learn first", main)
        self.assertIn(">Quiz</h2>", main)
        self.assertEqual(main.count("data-study-correct"), 2)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, main)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertNotIn(" · Easy ·", print_tpl)
        self.assertNotIn(" · Hard ·", print_tpl)
        self.assertNotIn("Explore more", print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertNotIn("Push further", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        self.assertIn("ps-study-deepen", back)
        for prompt in TALK_ABOUT_AMERICAN_ALLIGATOR + PUSH_FURTHER_AMERICAN_ALLIGATOR:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("american-alligator"),
            ["freshwater-fish", "galapagos-tortoise", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("american-alligator")
        sheet = study_print_html(
            deck,
            name="American alligator",
            emoji="🐊",
            photo="/field-pack/photos/american-alligator.jpg?v=img2",
            photo_pos="50% 35%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/american-alligator.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_AMERICAN_ALLIGATOR, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "Freshwater wetlands of the Southeastern United States — marshes, swamps, lakes, and slow rivers",
            sheet,
        )
        self.assertIn(
            "No — alligator moms guard the nest and carry hatchlings to the water",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_AMERICAN_ALLIGATOR + PUSH_FURTHER_AMERICAN_ALLIGATOR:
            self.assertIn(prompt, back)
        css = STYLES.read_text(encoding="utf-8")
        self.assertIn(".ps-study-front", css)
        self.assertIn(".ps-study-deepen", css)
        js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function buildStudyCardHtml", js)
        self.assertIn("function studyDeckFor", js)
        self.assertIn("Junior Ranger", js)
        study_js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("Show answers", study_js)
        self.assertIn('details class="study-teach"', study_js)
        self.assertIn("study-deepen", study_js)
        self.assertIn("is-wrong-pick", study_js)
        self.assertIn("FPStudyLevelName", study_js + STUDY_DATA_JS.read_text(encoding="utf-8"))

    def test_artifacts_include_american_alligator_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("american-alligator", payload)
        self.assertNotIn("jellyfish", payload)
        self.assertIn("sea-otter", payload)
        gator = payload["american-alligator"]
        self.assertEqual(gator["id"], "american-alligator")
        self.assertEqual(set(gator["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(gator["levels"]["hard"]["teach"], [])
        self.assertEqual(gator["levels"]["zoologist"]["teach"], [])
        easy = gator["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"american-alligator"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(
            set(payload["sea-otter"]["levels"]),
            {"easy", "hard", "zoologist"},
        )
        self.assertEqual(set(payload["african-lion"]["levels"]), {"easy", "hard", "zoologist"})

    def test_display_name_map_still_covers_future_tiers(self):
        self.assertEqual(
            LEVEL_DISPLAY_NAMES,
            {
                "easy": "Junior Ranger",
                "hard": "Park Ranger",
                "zoologist": "Zoologist",
            },
        )
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        gator_html = GATOR.read_text(encoding="utf-8")
        visible = _text(_main(gator_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        otter_html = OTTER.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(otter_html)))
        self.assertIn("Park Ranger", _text(_main(otter_html)))
        self.assertIn("Zoologist", _text(_main(otter_html)))


if __name__ == "__main__":
    unittest.main()
