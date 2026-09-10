"""Sea-turtle Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger is a sibling level)."""

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
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_OCTOPUS,
    TALK_ABOUT_SEA_TURTLE,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
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
SEA_TURTLE = FP / "cards" / "sea-turtle" / "index.html"
SEAHORSE = FP / "cards" / "seahorse" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
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
    "Ocean reptiles with paddle flippers (not land-turtle feet)",
    "About seven kinds live in the world’s oceans (not the polar ice)",
    "Moms dig nests on sandy beaches and bury soft eggs",
    "Babies hatch and crawl to the sea (often at night)",
    "They breathe air — they surface, even though they live in the ocean",
)

STEMS = (
    "How many kinds of sea turtle live in the world’s oceans, if we keep the list soft?",
    "What do a sea turtle’s flippers do?",
    "How is a sea turtle’s shell built for the ocean?",
    "How does a mom sea turtle make a nest?",
    "What are sea turtle eggs like — and does mom stay to guard them?",
    "What do baby sea turtles do after they hatch?",
    "How do sea turtles breathe, even though they live in the ocean?",
    "Where do sea turtles live?",
    "How far can many sea turtles travel, if we keep the miles soft?",
    "Can a sea turtle pull its head and flippers into its shell like many pet turtles?",
)

QIDS = (
    "seven-kinds-soft",
    "flippers-soft",
    "streamlined-shell-soft",
    "beach-nest-soft",
    "eggs-soft",
    "hatchling-run-soft",
    "air-breathers-soft",
    "ocean-homes-soft",
    "long-trips-soft",
    "cannot-hide-myth",
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
    "Chelonioidea",
    "Cheloniidae",
    "Dermochelyidae",
    "Cryptodira",
    "Testudines",
    "magnetoreception",
    "natal homing",
    "gigantothermy",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "IUCN",
    "Chelonioidea",
    "Cheloniidae",
    "Dermochelyidae",
    "Cryptodira",
    "magnetoreception",
    "natal homing",
    "gigantothermy",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class SeaTurtleEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_only(self):
        self.assertIn("sea-turtle", study_card_ids())
        self.assertNotIn("seahorse", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("sea-turtle"), ("easy", "hard"))
        self.assertIsNotNone(study_deck_for("sea-turtle", "hard"))
        self.assertIsNone(study_deck_for("sea-turtle", "zoologist"))
        self.assertIsNone(study_deck_for("seahorse"))
        deck = study_deck_for("sea-turtle")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "sea-turtle")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_SEA_TURTLE)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Sea turtle.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_SEA_TURTLE))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_SEA_TURTLE))
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
        self.assertIn("flipper", blob.lower())
        self.assertIn("seven", blob.lower())
        self.assertIn("ridley", blob.lower())
        self.assertIn("leatherback", blob.lower())
        self.assertIn("nest", blob.lower())
        self.assertIn("soft-shelled", blob.lower())
        self.assertIn("horizon", blob.lower())
        self.assertIn("lung", blob.lower())
        self.assertIn("polar", blob.lower())
        self.assertIn("feeding", blob.lower())
        self.assertIn("retract", blob.lower())
        self.assertEqual(WIKI_SEA_TURTLE, "https://en.wikipedia.org/wiki/Sea_turtle")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
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
        html = outing_talk_html({"id": "sea-turtle", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_SEA_TURTLE + PUSH_FURTHER_SEA_TURTLE:
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
        self.assertNotIn("Zoologist", visible)
        self.assertIn('class="study-level-picker"', html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertNotIn('data-study-pick="zoologist"', html)
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
            "About seven kinds — flatback, green, hawksbill, leatherback, loggerhead, Kemp’s ridley, and olive ridley (soft)",
            html,
        )
        self.assertIn(
            "No — unlike many pet turtles, they cannot pull their head and flippers in. The body is built for swimming, not hiding inside",
            html,
        )
        self.assertIn("Facts from Wikipedia, Sea turtle.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "seahorse", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("How many kinds of sea turtle", html)
        horse = SEAHORSE.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", horse)
        self.assertNotIn("card-study-pack", horse)
        self.assertNotIn("How many kinds of sea turtle", horse)

    def test_published_sea_turtle_card_matches_easy_deck(self):
        html = SEA_TURTLE.read_text(encoding="utf-8")
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
        self.assertIn("/field-pack/photos/sea-turtle.jpg", main)
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=sea-turtle",
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
        self.assertIn('"id": "sea-turtle"', html)
        self.assertNotIn('"id": "octopus"', html)
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
        self.assertNotIn("Zoologist", visible)
        self.assertIn('class="study-level-picker"', main)
        self.assertIn('data-study-pick="easy"', main)
        self.assertIn('data-study-pick="hard"', main)
        self.assertNotIn('data-study-pick="zoologist"', main)
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
        for prompt in TALK_ABOUT_SEA_TURTLE + PUSH_FURTHER_SEA_TURTLE:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("sea-turtle"),
            ["octopus", "manta-ray", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("sea-turtle")
        sheet = study_print_html(
            deck,
            name="Sea turtle",
            emoji="🐢",
            photo="/field-pack/photos/sea-turtle.jpg?v=img2",
            photo_pos="50% 32%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/sea-turtle.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_SEA_TURTLE, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "About seven kinds — flatback, green, hawksbill, leatherback, loggerhead, Kemp’s ridley, and olive ridley (soft)",
            sheet,
        )
        self.assertIn(
            "No — unlike many pet turtles, they cannot pull their head and flippers in. The body is built for swimming, not hiding inside",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_SEA_TURTLE + PUSH_FURTHER_SEA_TURTLE:
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

    def test_artifacts_include_sea_turtle_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("sea-turtle", payload)
        self.assertNotIn("seahorse", payload)
        self.assertIn("octopus", payload)
        self.assertIn("manta-ray", payload)
        self.assertIn("kelp-forest", payload)
        turtle = payload["sea-turtle"]
        self.assertEqual(turtle["id"], "sea-turtle")
        self.assertEqual(set(turtle["levels"]), {"easy", "hard"})
        self.assertNotIn("zoologist", turtle["levels"])
        easy = turtle["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"sea-turtle"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(set(payload["octopus"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["manta-ray"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["kelp-forest"]["levels"]), {"easy", "hard", "zoologist"})
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
        turtle_html = SEA_TURTLE.read_text(encoding="utf-8")
        visible = _text(_main(turtle_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertNotIn("Zoologist", visible)
        octo_html = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(octo_html)))
        self.assertIn("Park Ranger", _text(_main(octo_html)))
        self.assertIn("Zoologist", _text(_main(octo_html)))
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(manta_html)))
        self.assertIn("Park Ranger", _text(_main(manta_html)))
        self.assertIn("Zoologist", _text(_main(manta_html)))
        kelp_html = KELP.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(kelp_html)))
        self.assertIn("Park Ranger", _text(_main(kelp_html)))
        self.assertIn("Zoologist", _text(_main(kelp_html)))


if __name__ == "__main__":
    unittest.main()
