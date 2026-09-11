"""Starfish Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger is a sibling level)."""

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
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_KELP_FOREST,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_MANTA_RAY,
    PUSH_FURTHER_OCTOPUS,
    PUSH_FURTHER_SEA_TURTLE,
    PUSH_FURTHER_STARFISH,
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_OCTOPUS,
    TALK_ABOUT_SEA_TURTLE,
    TALK_ABOUT_STARFISH,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
    WIKI_STARFISH,
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
STARFISH = FP / "cards" / "starfish" / "index.html"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
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
    "Star-shaped ocean animals — not fish (better called sea stars).",
    "Most have a central disc and about five arms (some kinds have many more).",
    "They walk with tiny tube feet on the underside.",
    "The mouth is in the middle of the bottom side.",
    "Many can regrow a lost arm over time.",
)

STEMS = (
    "Are starfish a kind of fish?",
    "What does a sea star’s body look like, if we keep the arm count soft?",
    "How does a sea star walk?",
    "Where is a sea star’s mouth?",
    "Where do sea stars live?",
    "What is a sea star’s skin like?",
    "What do many sea stars hunt?",
    "What can many sea stars do if they lose an arm?",
    "How many kinds of sea star are there, if we keep the count soft?",
    "Does the name “starfish” mean they are fish?",
)

QIDS = (
    "not-fish-soft",
    "star-body-soft",
    "tube-feet-soft",
    "mouth-underneath-soft",
    "ocean-only-soft",
    "armour-soft",
    "predators-soft",
    "regrow-soft",
    "many-kinds-soft",
    "starfish-name-myth",
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
    "Asteroidea",
    "madreporite",
    "ossicle",
    "pedicellaria",
    "pyloric",
    "cardiac",
    "eversion",
    "keystone",
    "Acanthaster",
    "wasting",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "IUCN",
    "Asteroidea",
    "madreporite",
    "ossicle",
    "pedicellaria",
    "pyloric",
    "cardiac",
    "eversion",
    "keystone",
    "Acanthaster",
    "wasting",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class StarfishEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_only(self):
        self.assertIn("starfish", study_card_ids())
        self.assertNotIn("whale-shark", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("starfish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("starfish", "hard"))
        self.assertIsNotNone(study_deck_for("starfish", "zoologist"))
        self.assertIsNone(study_deck_for("whale-shark"))
        deck = study_deck_for("starfish")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "starfish")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_STARFISH)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Starfish.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_STARFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_STARFISH))
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
        self.assertIn("echinoderm", blob.lower())
        self.assertIn("urchin", blob.lower())
        self.assertIn("sea cucumber", blob.lower())
        self.assertIn("tube feet", blob.lower())
        self.assertIn("disc", blob.lower())
        self.assertIn("mouth", blob.lower())
        self.assertIn("salt", blob.lower())
        self.assertIn("freshwater", blob.lower())
        self.assertIn("plates", blob.lower())
        self.assertIn("clam", blob.lower())
        self.assertIn("regenerat", blob.lower())
        self.assertIn("two thousand", blob.lower())
        self.assertIn("invertebrate", blob.lower())
        self.assertIn("sea star", blob.lower())
        self.assertEqual(WIKI_STARFISH, "https://en.wikipedia.org/wiki/Starfish")

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
        manta = study_deck_for("manta-ray")
        self.assertEqual(manta["source"], WIKI_MANTA_RAY)
        self.assertEqual(manta["talk_about"], list(TALK_ABOUT_MANTA_RAY))
        self.assertEqual(manta["push_further"], list(PUSH_FURTHER_MANTA_RAY))
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("manta-ray", "hard"))
        self.assertIsNotNone(study_deck_for("manta-ray", "zoologist"))
        kelp = study_deck_for("kelp-forest")
        self.assertEqual(kelp["source"], WIKI_KELP_FOREST)
        self.assertEqual(kelp["talk_about"], list(TALK_ABOUT_KELP_FOREST))
        self.assertEqual(kelp["push_further"], list(PUSH_FURTHER_KELP_FOREST))
        self.assertEqual(shipped_levels_for("kelp-forest"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("kelp-forest", "hard"))
        self.assertIsNotNone(study_deck_for("kelp-forest", "zoologist"))
        jelly = study_deck_for("jellyfish")
        self.assertEqual(jelly["source"], WIKI_JELLYFISH)
        self.assertEqual(jelly["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(jelly["push_further"], list(PUSH_FURTHER_JELLYFISH))
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("jellyfish", "hard"))
        self.assertIsNotNone(study_deck_for("jellyfish", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "starfish", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_STARFISH + PUSH_FURTHER_STARFISH:
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
            "No — they have no gills, scales, or fins like fish. They are echinoderms, with urchins and sea cucumbers (names light)",
            html,
        )
        self.assertIn(
            "No — the name sounds like a fish, but they are sea stars: invertebrates, not fish",
            html,
        )
        self.assertIn("Facts from Wikipedia, Starfish.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("Are starfish a kind of fish", html)
        ray = WHALE_SHARK.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", ray)
        self.assertNotIn("card-study-pack", ray)
        self.assertNotIn("Are starfish a kind of fish", ray)

    def test_published_starfish_card_matches_easy_deck(self):
        html = STARFISH.read_text(encoding="utf-8")
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
        self.assertIn("/field-pack/photos/starfish.jpg", main)
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=starfish",
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
        self.assertIn('"id": "starfish"', html)
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
        for prompt in TALK_ABOUT_STARFISH + PUSH_FURTHER_STARFISH:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("starfish"),
            ["sea-turtle", "octopus", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("starfish")
        sheet = study_print_html(
            deck,
            name="Sea star",
            emoji="⭐",
            photo="/field-pack/photos/starfish.jpg?v=img2",
            photo_pos="50% 45%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/starfish.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_STARFISH, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "No — they have no gills, scales, or fins like fish. They are echinoderms, with urchins and sea cucumbers (names light)",
            sheet,
        )
        self.assertIn(
            "No — the name sounds like a fish, but they are sea stars: invertebrates, not fish",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_STARFISH + PUSH_FURTHER_STARFISH:
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

    def test_artifacts_include_starfish_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("starfish", payload)
        self.assertNotIn("whale-shark", payload)
        self.assertIn("seahorse", payload)
        self.assertIn("sea-turtle", payload)
        self.assertIn("octopus", payload)
        self.assertIn("manta-ray", payload)
        star = payload["starfish"]
        self.assertEqual(star["id"], "starfish")
        self.assertEqual(set(star["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(star["levels"]["zoologist"]["teach"], [])
        easy = star["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"starfish"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(set(payload["sea-turtle"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["octopus"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["manta-ray"]["levels"]), {"easy", "hard", "zoologist"})
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
        star_html = STARFISH.read_text(encoding="utf-8")
        visible = _text(_main(star_html))
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
