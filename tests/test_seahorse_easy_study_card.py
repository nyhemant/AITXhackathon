"""Seahorse Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger is a sibling level)."""

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
    PUSH_FURTHER_LION,
    PUSH_FURTHER_OCTOPUS,
    PUSH_FURTHER_SEA_TURTLE,
    PUSH_FURTHER_SEAHORSE,
    STUDY_SLOTS,
    TALK_ABOUT_LION,
    TALK_ABOUT_OCTOPUS,
    TALK_ABOUT_SEA_TURTLE,
    TALK_ABOUT_SEAHORSE,
    WIKI_LION,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
    WIKI_SEAHORSE,
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
SEAHORSE = FP / "cards" / "seahorse" / "index.html"
STINGRAY = FP / "cards" / "whale-shark" / "index.html"
SEA_TURTLE = FP / "cards" / "sea-turtle" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
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
    "Small bony fish that swim upright (not mammals)",
    "Horse-like head and long snout for sucking tiny food",
    "A curled gripping tail holds seagrass, coral, or seaweed",
    "Dad carries the babies in a front pouch until they are born",
    "Thin skin over bony plates (not fish scales) — great at camouflage",
)

STEMS = (
    "Are seahorses a kind of fish?",
    "How does a seahorse swim, if we keep the fins simple?",
    "What does a seahorse’s tail do?",
    "Why does a seahorse’s head look horse-like, and how does it eat?",
    "What covers a seahorse’s body, if we keep the armour story soft?",
    "Who carries seahorse babies, and how?",
    "How can a seahorse hide in seagrass or coral?",
    "Where do seahorses usually live?",
    "Which animals are seahorses closely related to?",
    "Do seahorse moms always carry the babies?",
)

QIDS = (
    "true-fish-soft",
    "upright-swim-soft",
    "gripping-tail-soft",
    "horse-snout-soft",
    "bony-armour-soft",
    "dads-pouch-soft",
    "camouflage-soft",
    "clingy-homes-soft",
    "pipefish-cousins-soft",
    "dad-not-mom-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Endangered",
    "Vulnerable",
    "Critically",
    "Near Threatened",
    "Least Concern",
    "CITES",
    "Syngnathidae",
    "Phycodurus",
    "Phyllopteryx",
    "bargibanti",
    "zosterae",
    "histotroph",
    "osmoregulation",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "IUCN",
    "CITES",
    "Syngnathidae",
    "Phycodurus",
    "Phyllopteryx",
    "bargibanti",
    "zosterae",
    "histotroph",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class SeahorseEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_only(self):
        self.assertIn("seahorse", study_card_ids())
        self.assertIn("whale-shark", study_card_ids())
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
                "cuttlefish",
                "eel",
                "jellyfish",
                "kelp-forest",
                "manta-ray",
                "octopus",
                "sea-turtle",
                "seahorse",
                "starfish",
                "stingray",
                "whale-shark",
            ),
        )
        self.assertEqual(shipped_levels_for("seahorse"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("seahorse", "hard"))
        self.assertIsNotNone(study_deck_for("seahorse", "zoologist"))
        self.assertIsNotNone(study_deck_for("whale-shark"))
        self.assertIsNone(study_deck_for("whale-shark", "hard"))
        self.assertIsNone(study_deck_for("whale-shark", "zoologist"))
        deck = study_deck_for("seahorse")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "seahorse")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_SEAHORSE)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Seahorse.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_SEAHORSE))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_SEAHORSE))
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
        blob = " ".join(
            deck["teach"]
            + [
                q["stem"] + q["why"] + " ".join(q["choices"])
                for q in deck["questions"]
            ]
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)
        self.assertIn("hippocampus", blob.lower())
        self.assertIn("bony fish", blob.lower())
        self.assertIn("dorsal", blob.lower())
        self.assertIn("pectoral", blob.lower())
        self.assertIn("square", blob.lower())
        self.assertIn("snout", blob.lower())
        self.assertIn("pouch", blob.lower())
        self.assertIn("colour", blob.lower())
        self.assertIn("seagrass", blob.lower())
        self.assertIn("pipefish", blob.lower())
        self.assertIn("seadragon", blob.lower())
        self.assertIn("father", blob.lower())
        self.assertEqual(WIKI_SEAHORSE, "https://en.wikipedia.org/wiki/Seahorse")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        turtle = study_deck_for("sea-turtle")
        self.assertEqual(turtle["source"], WIKI_SEA_TURTLE)
        self.assertEqual(turtle["talk_about"], list(TALK_ABOUT_SEA_TURTLE))
        self.assertEqual(turtle["push_further"], list(PUSH_FURTHER_SEA_TURTLE))
        self.assertEqual(shipped_levels_for("sea-turtle"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("sea-turtle", "hard"))
        self.assertIsNotNone(study_deck_for("sea-turtle", "zoologist"))
        octo = study_deck_for("octopus")
        self.assertEqual(octo["source"], WIKI_OCTOPUS)
        self.assertEqual(octo["talk_about"], list(TALK_ABOUT_OCTOPUS))
        self.assertEqual(octo["push_further"], list(PUSH_FURTHER_OCTOPUS))
        self.assertEqual(shipped_levels_for("octopus"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("octopus", "hard"))
        self.assertIsNotNone(study_deck_for("octopus", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "seahorse", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_SEAHORSE + PUSH_FURTHER_SEAHORSE:
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
        self.assertNotIn(" · Easy ·", html)
        self.assertNotIn(" · Hard ·", html)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, html)
        self.assertIn(
            "Yes — small bony fish in genus Hippocampus, with many kinds (soft)",
            html,
        )
        self.assertIn(
            "No — people think moms always carry babies, but in seahorses the father does the pouch care",
            html,
        )
        self.assertIn("Facts from Wikipedia, Seahorse.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn("card-study-pack", html)
        self.assertNotIn("What do they eat?", html)
        self.assertNotIn("Are seahorses a kind of fish", html)
        ray = STINGRAY.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", ray)
        self.assertNotIn("What do they eat?", ray)
        self.assertNotIn("Are seahorses a kind of fish", ray)

    def test_published_seahorse_card_matches_easy_deck(self):
        html = SEAHORSE.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("Watch Live", main)
        self.assertIn("card-watch-live", main)
        self.assertIn("card-page-photo", main)
        self.assertIn("/field-pack/photos/seahorse.jpg", main)
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=seahorse",
            main,
        )
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "seahorse"', html)
        self.assertNotIn('"id": "sea-turtle"', html)
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
        self.assertNotIn(" · Easy ·", main)
        self.assertNotIn(" · Hard ·", main)
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
        for prompt in TALK_ABOUT_SEAHORSE + PUSH_FURTHER_SEAHORSE:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("seahorse"),
            ["octopus", "sea-turtle", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("seahorse")
        sheet = study_print_html(
            deck,
            name="Seahorse",
            emoji="🌊",
            photo="/field-pack/photos/seahorse.jpg?v=img2",
            photo_pos="50% 30%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/seahorse.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_SEAHORSE, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "Yes — small bony fish in genus Hippocampus, with many kinds (soft)",
            sheet,
        )
        self.assertIn(
            "No — people think moms always carry babies, but in seahorses the father does the pouch care",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_SEAHORSE + PUSH_FURTHER_SEAHORSE:
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

    def test_artifacts_include_seahorse_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("seahorse", payload)
        self.assertIn("whale-shark", payload)
        self.assertEqual(set(payload["whale-shark"]["levels"]), {"easy"})
        self.assertIn("sea-turtle", payload)
        self.assertIn("octopus", payload)
        horse = payload["seahorse"]
        self.assertEqual(horse["id"], "seahorse")
        self.assertEqual(set(horse["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(horse["levels"]["zoologist"]["teach"], [])
        easy = horse["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"seahorse"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(set(payload["sea-turtle"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["octopus"]["levels"]), {"easy", "hard", "zoologist"})
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
        horse_html = SEAHORSE.read_text(encoding="utf-8")
        visible = _text(_main(horse_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        turtle_html = SEA_TURTLE.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(turtle_html)))
        self.assertIn("Park Ranger", _text(_main(turtle_html)))
        self.assertIn("Zoologist", _text(_main(turtle_html)))
        octo_html = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(octo_html)))
        self.assertIn("Park Ranger", _text(_main(octo_html)))
        self.assertIn("Zoologist", _text(_main(octo_html)))


if __name__ == "__main__":
    unittest.main()
