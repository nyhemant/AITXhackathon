"""Polar bear Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger and Zoologist are sibling levels)."""

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
    PUSH_FURTHER_POLAR_BEAR,
    STUDY_SLOTS,
    TALK_ABOUT_FRESHWATER_FISH,
    TALK_ABOUT_LION,
    TALK_ABOUT_POLAR_BEAR,
    WIKI_FRESHWATER_FISH,
    WIKI_LION,
    WIKI_POLAR_BEAR,
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
BEAR = FP / "cards" / "polar-bear" / "index.html"
OCTOPUS = FP / "cards" / "stingray" / "index.html"
FISH = FP / "cards" / "freshwater-fish" / "index.html"
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
    "Live in the Arctic on sea ice and nearby coasts",
    "Fur looks white; skin underneath is black",
    "Huge paws for walking on ice and paddling",
    "Hunt seals from the ice",
    "Need healthy sea ice to find food",
)

STEMS = (
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

QIDS = (
    "arctic-home",
    "looks-white-fur-soft",
    "black-skin-soft",
    "ice-and-paddle-paws",
    "seal-snacks-soft",
    "strong-swimmers-soft",
    "fat-jacket-soft",
    "cub-dens-soft",
    "soft-ice-care",
    "not-south-pole-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Vulnerable",
    "Endangered",
    "Critically",
    "Least Concern",
    "CITES",
    "Ursus",
    "climate change",
    "global warming",
    "brown bear",
    "blubber",
    "kg",
    "cm",
    "mph",
    "km/h",
)
# Talk / push are Zoologist prompts (delayed implantation, Ursus vs
# Thalarctos, subpopulations, stored-fat den, regional status, skull).
PAGE_BRITTLE = (
    "Endangered",
    "Critically",
    "Least Concern",
    "climate change",
    "global warming",
    "blubber",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "IUCN",
    "Vulnerable",
    "CITES",
    "Ursus",
    "climate change",
    "brown bear",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class PolarBearEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger(self):
        self.assertIn("polar-bear", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("polar-bear"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("polar-bear", "hard"))
        self.assertIsNotNone(study_deck_for("polar-bear", "zoologist"))
        deck = study_deck_for("polar-bear")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "polar-bear")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_POLAR_BEAR)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Polar bear.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_POLAR_BEAR))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_POLAR_BEAR))
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
        self.assertIn("arctic", blob.lower())
        self.assertIn("sea ice", blob.lower())
        self.assertIn("antarctic", blob.lower())
        self.assertIn("see-through", blob.lower())
        self.assertIn("scatter", blob.lower())
        self.assertIn("black", blob.lower())
        self.assertIn("paw", blob.lower())
        self.assertIn("paddle", blob.lower())
        self.assertIn("ringed seal", blob.lower())
        self.assertIn("swim", blob.lower())
        self.assertIn("fat", blob.lower())
        self.assertIn("den", blob.lower())
        self.assertIn("penguin", blob.lower())
        self.assertEqual(
            WIKI_POLAR_BEAR,
            "https://en.wikipedia.org/wiki/Polar_bear",
        )

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        fish = study_deck_for("freshwater-fish")
        self.assertEqual(fish["source"], WIKI_FRESHWATER_FISH)
        self.assertEqual(fish["talk_about"], list(TALK_ABOUT_FRESHWATER_FISH))
        self.assertEqual(fish["push_further"], list(PUSH_FURTHER_FRESHWATER_FISH))
        self.assertEqual(shipped_levels_for("freshwater-fish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("freshwater-fish", "hard"))
        self.assertIsNotNone(study_deck_for("freshwater-fish", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "polar-bear", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_POLAR_BEAR + PUSH_FURTHER_POLAR_BEAR:
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
        self.assertIn("On Arctic sea ice and nearby coasts — not the Antarctic", html)
        self.assertIn(
            "No — polar bears are Arctic animals; penguins, not polar bears, live in Antarctica",
            html,
        )
        self.assertIn("Facts from Wikipedia, Polar bear.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "stingray", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("Where do polar bears live in the wild?", html)
        otter = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", otter)
        self.assertNotIn("card-study-pack", otter)
        self.assertNotIn("Where do polar bears live in the wild?", otter)

    def test_published_polar_bear_card_matches_easy_deck(self):
        html = BEAR.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("card-page-photo", main)
        self.assertIn("/field-pack/photos/polar-bear.jpg", main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "polar-bear"', html)
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
        for prompt in TALK_ABOUT_POLAR_BEAR + PUSH_FURTHER_POLAR_BEAR:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("polar-bear"),
            ["african-penguin", "asian-small-clawed-otter", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("polar-bear")
        sheet = study_print_html(
            deck,
            name="Polar bear",
            emoji="🐻‍❄️",
            photo="/field-pack/photos/polar-bear.jpg?v=img2",
            photo_pos="50% 22%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/polar-bear.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_POLAR_BEAR, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("On Arctic sea ice and nearby coasts — not the Antarctic", sheet)
        self.assertIn(
            "No — polar bears are Arctic animals; penguins, not polar bears, live in Antarctica",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_POLAR_BEAR + PUSH_FURTHER_POLAR_BEAR:
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

    def test_artifacts_include_polar_bear_easy_hard_and_zoologist(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("polar-bear", payload)
        self.assertNotIn("stingray", payload)
        self.assertIn("freshwater-fish", payload)
        bear = payload["polar-bear"]
        self.assertEqual(bear["id"], "polar-bear")
        self.assertEqual(set(bear["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(bear["levels"]["hard"]["teach"], [])
        self.assertEqual(bear["levels"]["zoologist"]["teach"], [])
        easy = bear["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"polar-bear"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(
            set(payload["freshwater-fish"]["levels"]),
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
        bear_html = BEAR.read_text(encoding="utf-8")
        visible = _text(_main(bear_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        fish_html = FISH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(fish_html)))
        self.assertIn("Park Ranger", _text(_main(fish_html)))
        self.assertIn("Zoologist", _text(_main(fish_html)))


if __name__ == "__main__":
    unittest.main()
