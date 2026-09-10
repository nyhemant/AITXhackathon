"""American bison Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger + Zoologist are sibling levels)."""

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
    PUSH_FURTHER_AMERICAN_BISON,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_AMERICAN_ALLIGATOR,
    TALK_ABOUT_AMERICAN_BISON,
    TALK_ABOUT_LION,
    WIKI_AMERICAN_ALLIGATOR,
    WIKI_AMERICAN_BISON,
    WIKI_LION,
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
BISON = FP / "cards" / "american-bison" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
GATOR = FP / "cards" / "american-alligator" / "index.html"
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
    "Big grassland grazers of North America",
    "Tall shoulder hump + shaggy coat",
    "Both males and females have horns",
    "Live in herds on the prairie",
    "Often nicknamed “buffalo,” but they’re bison",
)

STEMS = (
    "Where do American bison live in the wild?",
    "What makes the front of an American bison look so big?",
    "How does an American bison’s coat change with the seasons?",
    "Who has horns, and what are they for?",
    "What do American bison mostly eat?",
    "How do bison herds usually work?",
    "What color are new bison calves?",
    "Why do bison roll in dust or mud wallows?",
    "How should people care around wild bison and their home?",
    "Are American bison true buffalo?",
)

QIDS = (
    "prairie-home-soft",
    "shoulder-hump-soft",
    "coat-change-soft",
    "horns-soft",
    "graze-cud-soft",
    "herd-life-soft",
    "reddish-calves-soft",
    "wallow-soft",
    "soft-prairie-care",
    "not-a-true-buffalo-myth",
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
    "athabascae",
    "Bison bison",
    "plains bison",
    "wood bison",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "IUCN",
    "Near Threatened",
    "CITES",
    "athabascae",
    "plains bison",
    "wood bison",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class AmericanBisonEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger(self):
        self.assertIn("american-bison", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("american-bison"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("american-bison", "hard"))
        self.assertIsNotNone(study_deck_for("american-bison", "zoologist"))
        self.assertIsNone(study_deck_for("jellyfish"))
        deck = study_deck_for("american-bison")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "american-bison")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_AMERICAN_BISON)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, American bison.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_AMERICAN_BISON))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_AMERICAN_BISON))
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
        self.assertIn("grassland", blob.lower())
        self.assertIn("hump", blob.lower())
        self.assertIn("coat", blob.lower())
        self.assertIn("horn", blob.lower())
        self.assertIn("grass", blob.lower())
        self.assertIn("herd", blob.lower())
        self.assertIn("reddish", blob.lower())
        self.assertIn("wallow", blob.lower())
        self.assertIn("space", blob.lower())
        self.assertIn("buffalo", blob.lower())
        self.assertEqual(
            WIKI_AMERICAN_BISON,
            "https://en.wikipedia.org/wiki/American_bison",
        )

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        gator = study_deck_for("american-alligator")
        self.assertEqual(gator["source"], WIKI_AMERICAN_ALLIGATOR)
        self.assertEqual(gator["talk_about"], list(TALK_ABOUT_AMERICAN_ALLIGATOR))
        self.assertEqual(gator["push_further"], list(PUSH_FURTHER_AMERICAN_ALLIGATOR))
        self.assertEqual(shipped_levels_for("american-alligator"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("american-alligator", "hard"))
        self.assertIsNotNone(study_deck_for("american-alligator", "zoologist"))
        self.assertEqual(shipped_levels_for("sea-otter"), ("easy", "hard", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "american-bison", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_AMERICAN_BISON + PUSH_FURTHER_AMERICAN_BISON:
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
            "Open grasslands, plains, and river valleys of North America",
            html,
        )
        self.assertIn(
            "No — “buffalo” is a nickname; true buffalo live in Africa and Asia",
            html,
        )
        self.assertIn("Facts from Wikipedia, American bison.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "jellyfish", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("Where do American bison live in the wild?", html)
        jelly = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("Where do American bison live in the wild?", jelly)

    def test_published_american_bison_card_matches_easy_deck(self):
        html = BISON.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("card-page-photo", main)
        self.assertIn("/field-pack/photos/american-bison.jpg", main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "american-bison"', html)
        self.assertNotIn('"id": "american-alligator"', html)
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
        for prompt in TALK_ABOUT_AMERICAN_BISON + PUSH_FURTHER_AMERICAN_BISON:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("american-bison"),
            ["zebra", "warthog", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("american-bison")
        sheet = study_print_html(
            deck,
            name="American bison",
            emoji="🦬",
            photo="/field-pack/photos/american-bison.jpg?v=img2",
            photo_pos="50% 25%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/american-bison.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_AMERICAN_BISON, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "Open grasslands, plains, and river valleys of North America",
            sheet,
        )
        self.assertIn(
            "No — “buffalo” is a nickname; true buffalo live in Africa and Asia",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_AMERICAN_BISON + PUSH_FURTHER_AMERICAN_BISON:
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

    def test_artifacts_include_american_bison_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("american-bison", payload)
        self.assertNotIn("jellyfish", payload)
        self.assertIn("american-alligator", payload)
        bison = payload["american-bison"]
        self.assertEqual(bison["id"], "american-bison")
        self.assertEqual(set(bison["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(bison["levels"]["hard"]["teach"], [])
        self.assertEqual(bison["levels"]["zoologist"]["teach"], [])
        easy = bison["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"american-bison"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(
            set(payload["american-alligator"]["levels"]),
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
        bison_html = BISON.read_text(encoding="utf-8")
        visible = _text(_main(bison_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        gator_html = GATOR.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(gator_html)))
        self.assertIn("Park Ranger", _text(_main(gator_html)))
        self.assertIn("Zoologist", _text(_main(gator_html)))


if __name__ == "__main__":
    unittest.main()
