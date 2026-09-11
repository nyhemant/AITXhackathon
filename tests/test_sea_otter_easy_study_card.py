"""Sea otter Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger is a sibling level)."""

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
    PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_SEA_OTTER,
    STUDY_SLOTS,
    TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER,
    TALK_ABOUT_LION,
    TALK_ABOUT_SEA_OTTER,
    WIKI_ASIAN_SMALL_CLAWED_OTTER,
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
OTTER = FP / "cards" / "sea-otter" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
ASIAN = FP / "cards" / "asian-small-clawed-otter" / "index.html"
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
    "Live in coastal North Pacific ocean waters — not rivers or Asian wetlands",
    "Warmth comes from super-thick fur (densest of any animal)",
    "Often float on their backs to rest and eat",
    "Crack hard shells with rocks — tool users",
    "Healthy kelp forests and clean coasts help them thrive",
)

STEMS = (
    "Where do sea otters live in the wild?",
    "How do sea otters stay warm in cold ocean water?",
    "How do sea otters often rest and eat?",
    "How do sea otters open hard shells?",
    "What do sea otters love to eat?",
    "Why do sea otters wrap themselves in kelp?",
    "What is a group of resting sea otters called?",
    "How do sea otter moms carry their pups?",
    "Why do healthy kelp forests and clean coasts matter?",
    "Is a sea otter the same animal as a river otter or an Asian small-clawed otter?",
)

QIDS = (
    "ocean-home",
    "densest-fur-soft",
    "belly-table-soft",
    "rock-tools-soft",
    "urchin-snacks-soft",
    "kelp-anchors-soft",
    "raft-pals-soft",
    "pup-on-tummy-soft",
    "soft-kelp-care",
    "not-a-river-otter-myth",
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
    "Enhydra",
    "blubber",
    "fur trade",
    "keystone",
    "kg",
    "cm",
    "mph",
    "km/h",
)
# Talk / push are Zoologist prompts (Enhydra vs Aonyx, three
# subspecies, kelp cascade, bunodont crushers, newcomer to the
# sea, regional status under one snapshot letter).
PAGE_BRITTLE = (
    "Vulnerable",
    "Critically",
    "Least Concern",
    "CITES",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "IUCN",
    "Endangered",
    "CITES",
    "Enhydra",
    "blubber",
    "fur trade",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class SeaOtterEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger(self):
        self.assertIn("sea-otter", study_card_ids())
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
        self.assertEqual(shipped_levels_for("sea-otter"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("sea-otter", "hard"))
        self.assertIsNotNone(study_deck_for("sea-otter", "zoologist"))
        self.assertIsNone(study_deck_for("whale-shark"))
        deck = study_deck_for("sea-otter")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "sea-otter")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_SEA_OTTER)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Sea otter.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_SEA_OTTER))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_SEA_OTTER))
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
        self.assertIn("north pacific", blob.lower())
        self.assertIn("fur", blob.lower())
        self.assertIn("densest", blob.lower())
        self.assertIn("float", blob.lower())
        self.assertIn("rock", blob.lower())
        self.assertIn("urchin", blob.lower())
        self.assertIn("kelp", blob.lower())
        self.assertIn("raft", blob.lower())
        self.assertIn("pup", blob.lower())
        self.assertIn("river otter", blob.lower())
        self.assertIn("asian small-clawed", blob.lower())
        self.assertEqual(
            WIKI_SEA_OTTER,
            "https://en.wikipedia.org/wiki/Sea_otter",
        )

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        asian = study_deck_for("asian-small-clawed-otter")
        self.assertEqual(asian["source"], WIKI_ASIAN_SMALL_CLAWED_OTTER)
        self.assertEqual(asian["talk_about"], list(TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER))
        self.assertEqual(asian["push_further"], list(PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER))
        self.assertEqual(
            shipped_levels_for("asian-small-clawed-otter"),
            ("easy", "hard", "zoologist"),
        )
        self.assertIsNotNone(study_deck_for("asian-small-clawed-otter", "hard"))
        self.assertIsNotNone(study_deck_for("asian-small-clawed-otter", "zoologist"))
        self.assertEqual(shipped_levels_for("polar-bear"), ("easy", "hard", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "sea-otter", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_SEA_OTTER + PUSH_FURTHER_SEA_OTTER:
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
            "Nearshore North Pacific coasts — they can live almost entirely in the sea",
            html,
        )
        self.assertIn(
            "No — sea otters are ocean specialists, different from river otters and Asian small-clawed otters",
            html,
        )
        self.assertIn("Facts from Wikipedia, Sea otter.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("Where do sea otters live in the wild?", html)
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("Where do sea otters live in the wild?", jelly)

    def test_published_sea_otter_card_matches_easy_deck(self):
        html = OTTER.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("card-page-photo", main)
        self.assertIn("/field-pack/photos/sea-otter.jpg", main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "sea-otter"', html)
        self.assertNotIn('"id": "asian-small-clawed-otter"', html)
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
        for prompt in TALK_ABOUT_SEA_OTTER + PUSH_FURTHER_SEA_OTTER:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("sea-otter"),
            ["asian-small-clawed-otter", "shark", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("sea-otter")
        sheet = study_print_html(
            deck,
            name="Sea otter",
            emoji="🦦",
            photo="/field-pack/photos/sea-otter.jpg?v=img2",
            photo_pos="50% 38%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/sea-otter.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_SEA_OTTER, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "Nearshore North Pacific coasts — they can live almost entirely in the sea",
            sheet,
        )
        self.assertIn(
            "No — sea otters are ocean specialists, different from river otters and Asian small-clawed otters",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_SEA_OTTER + PUSH_FURTHER_SEA_OTTER:
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

    def test_artifacts_include_sea_otter_easy_hard_and_zoologist(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("sea-otter", payload)
        self.assertNotIn("whale-shark", payload)
        self.assertIn("asian-small-clawed-otter", payload)
        otter = payload["sea-otter"]
        self.assertEqual(otter["id"], "sea-otter")
        self.assertEqual(set(otter["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(otter["levels"]["hard"]["teach"], [])
        self.assertEqual(otter["levels"]["zoologist"]["teach"], [])
        easy = otter["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"sea-otter"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(
            set(payload["asian-small-clawed-otter"]["levels"]),
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
        otter_html = OTTER.read_text(encoding="utf-8")
        visible = _text(_main(otter_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        asian_html = ASIAN.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(asian_html)))
        self.assertIn("Park Ranger", _text(_main(asian_html)))
        self.assertIn("Zoologist", _text(_main(asian_html)))


if __name__ == "__main__":
    unittest.main()
