"""Freshwater fish Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger and Zoologist are sibling levels)."""

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
FISH = FP / "cards" / "freshwater-fish" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
SLOTH = FP / "cards" / "two-toed-sloth" / "index.html"
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
    "Live in rivers, lakes, ponds, and wetlands — not salty ocean water",
    "Breathe underwater with gills",
    "Use fins to swim, steer, and stop",
    "Come in many shapes and sizes (catfish, trout, perch, and more)",
    "Need clean fresh water to stay healthy",
)

STEMS = (
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

QIDS = (
    "fresh-homes",
    "low-salt-water-soft",
    "gill-breathers",
    "fin-toolkit",
    "many-kinds-soft",
    "scaly-coats-soft",
    "water-temp-soft",
    "egg-starts-soft",
    "soft-water-care",
    "not-only-ocean-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Vulnerable",
    "Endangered",
    "Critically",
    "Least Concern",
    "teleost",
    "Actinopterygii",
    "osmoregulation",
    "diadrom",
    "anadrom",
    "catadrom",
    "lateral line",
    "swim bladder",
    "41.24",
    "kg",
    "cm",
    "mph",
    "km/h",
)
# Talk / push are Zoologist prompts (ray-finned vs “fish”, ionocytes, salmon up / eel down).
PAGE_BRITTLE = (
    "Vulnerable",
    "Endangered",
    "Critically",
    "Least Concern",
    "teleost",
    "Actinopterygii",
    "osmoregulation",
    "diadrom",
    "anadrom",
    "catadrom",
    "41.24",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "IUCN",
    "teleost",
    "ray-finned",
    "osmoregulation",
    "lateral line",
    "swim bladder",
    "diadromy",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class FreshwaterFishEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger(self):
        self.assertIn("freshwater-fish", study_card_ids())
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
                "cuttlefish",
            ),
        )
        self.assertEqual(shipped_levels_for("freshwater-fish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("freshwater-fish", "hard"))
        self.assertIsNotNone(study_deck_for("freshwater-fish", "zoologist"))
        self.assertIsNone(study_deck_for("jellyfish"))
        deck = study_deck_for("freshwater-fish")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "freshwater-fish")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_FRESHWATER_FISH)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Freshwater fish.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_FRESHWATER_FISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_FRESHWATER_FISH))
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
        self.assertIn("rivers", blob.lower())
        self.assertIn("lakes", blob.lower())
        self.assertIn("salt", blob.lower())
        self.assertIn("gill", blob.lower())
        self.assertIn("fin", blob.lower())
        self.assertIn("huge share", blob.lower())
        self.assertIn("scale", blob.lower())
        self.assertIn("cold-blooded", blob.lower())
        self.assertIn("egg", blob.lower())
        self.assertIn("clean", blob.lower())
        self.assertIn("ocean", blob.lower())
        self.assertEqual(
            WIKI_FRESHWATER_FISH,
            "https://en.wikipedia.org/wiki/Freshwater_fish",
        )

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        sloth = study_deck_for("two-toed-sloth")
        self.assertEqual(sloth["source"], WIKI_TWO_TOED_SLOTH)
        self.assertEqual(sloth["talk_about"], list(TALK_ABOUT_TWO_TOED_SLOTH))
        self.assertEqual(sloth["push_further"], list(PUSH_FURTHER_TWO_TOED_SLOTH))
        self.assertEqual(shipped_levels_for("two-toed-sloth"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("two-toed-sloth", "hard"))
        self.assertIsNotNone(study_deck_for("two-toed-sloth", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "freshwater-fish", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_FRESHWATER_FISH + PUSH_FURTHER_FRESHWATER_FISH:
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
        self.assertIn("Rivers, lakes, ponds, and inland wetlands", html)
        self.assertIn(
            "No — plenty of fish spend their whole lives in fresh water, with no ocean required",
            html,
        )
        self.assertIn("Facts from Wikipedia, Freshwater fish.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "jellyfish", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("Where do freshwater fish live?", html)
        jelly = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("Where do freshwater fish live?", jelly)

    def test_published_fish_card_matches_easy_deck(self):
        html = FISH.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("card-page-photo", main)
        self.assertIn("/field-pack/photos/freshwater-fish.jpg", main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "freshwater-fish"', html)
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
        for prompt in TALK_ABOUT_FRESHWATER_FISH + PUSH_FURTHER_FRESHWATER_FISH:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("freshwater-fish"),
            ["shark", "asian-small-clawed-otter", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("freshwater-fish")
        sheet = study_print_html(
            deck,
            name="River / lake fish",
            emoji="🐟",
            photo="/field-pack/photos/freshwater-fish.jpg?v=img2",
            photo_pos="50% 35%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/freshwater-fish.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_FRESHWATER_FISH, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("Rivers, lakes, ponds, and inland wetlands", sheet)
        self.assertIn(
            "No — plenty of fish spend their whole lives in fresh water, with no ocean required",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_FRESHWATER_FISH + PUSH_FURTHER_FRESHWATER_FISH:
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

    def test_artifacts_include_fish_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("freshwater-fish", payload)
        self.assertNotIn("jellyfish", payload)
        self.assertIn("two-toed-sloth", payload)
        fish = payload["freshwater-fish"]
        self.assertEqual(fish["id"], "freshwater-fish")
        self.assertEqual(set(fish["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(fish["levels"]["hard"]["teach"], [])
        self.assertEqual(fish["levels"]["zoologist"]["teach"], [])
        self.assertIn("zoologist", fish["levels"])
        easy = fish["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"freshwater-fish"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(
            set(payload["two-toed-sloth"]["levels"]),
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
        fish_html = FISH.read_text(encoding="utf-8")
        visible = _text(_main(fish_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        sloth_html = SLOTH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(sloth_html)))
        self.assertIn("Park Ranger", _text(_main(sloth_html)))
        self.assertIn("Zoologist", _text(_main(sloth_html)))


if __name__ == "__main__":
    unittest.main()
