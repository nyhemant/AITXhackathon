"""Whale shark Easy study-card: Junior Ranger teach + 5 signed MCQs (Park Ranger is a sibling level)."""

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
    PUSH_FURTHER_MANTA_RAY,
    PUSH_FURTHER_SHARK,
    STUDY_SLOTS_SHORT,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_SHARK,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_SHARK,
    WIKI_WHALE_SHARK,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_try_next_ids,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
STINGRAY = FP / "cards" / "stingray" / "index.html"
SHARK = FP / "cards" / "shark" / "index.html"
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
    "The biggest living fish in the ocean (size soft).",
    "A shark — not a whale — that filter-feeds with a huge mouth.",
    "Dark back with light spots and stripes in a checkerboard pattern.",
    "Eats tiny plankton and small schooling fish — not people.",
    "Usually gentle and slow-moving in warm seas.",
)

STEMS = (
    "What size record does the whale shark hold among living fish?",
    "Is a whale shark a whale?",
    "How does a whale shark mostly get its food?",
    "What is special about a whale shark’s pattern?",
    "Does a whale shark’s huge size mean it hunts people?",
)

QIDS = (
    "biggest-soft",
    "shark-not-whale",
    "filter-soft",
    "spots-soft",
    "gentle-giant-myth",
)

LETTERS = ("B", "A", "C", "A", "B")

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Endangered",
    "Vulnerable",
    "Critically",
    "Near Threatened",
    "Least Concern",
    "CITES",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class WhaleSharkEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_only(self):
        self.assertIn("whale-shark", study_card_ids())
        self.assertIn("stingray", study_card_ids())
        self.assertEqual(study_card_ids()[-1], "whale-shark")
        self.assertEqual(shipped_levels_for("whale-shark"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("whale-shark", "hard"))
        self.assertIsNotNone(study_deck_for("whale-shark", "zoologist"))
        self.assertIsNotNone(study_deck_for("stingray"))
        self.assertEqual(shipped_levels_for("stingray"), ("easy", "hard", "zoologist"))
        deck = study_deck_for("whale-shark")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "whale-shark")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_WHALE_SHARK)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Whale shark.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS_SHORT)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], [])
        self.assertEqual(deck["push_further"], [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, list(LETTERS))
        self.assertEqual(letters.count("A"), 2)
        self.assertEqual(letters.count("B"), 2)
        self.assertEqual(letters.count("C"), 1)
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
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("largest known living fish", blob.lower())
        self.assertIn("carpet shark", blob.lower())
        self.assertIn("filter-feeding", blob.lower())
        self.assertIn("checkerboard", blob.lower())
        self.assertIn("docile", blob.lower())
        self.assertEqual(WIKI_WHALE_SHARK, "https://en.wikipedia.org/wiki/Whale_shark")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        shark = study_deck_for("shark")
        self.assertEqual(shark["source"], WIKI_SHARK)
        self.assertEqual(shark["talk_about"], list(TALK_ABOUT_SHARK))
        self.assertEqual(shark["push_further"], list(PUSH_FURTHER_SHARK))
        self.assertEqual(shipped_levels_for("shark"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("shark", "hard"))
        self.assertIsNotNone(study_deck_for("shark", "zoologist"))
        manta = study_deck_for("manta-ray")
        self.assertEqual(manta["source"], WIKI_MANTA_RAY)
        self.assertEqual(manta["talk_about"], list(TALK_ABOUT_MANTA_RAY))
        self.assertEqual(manta["push_further"], list(PUSH_FURTHER_MANTA_RAY))
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("manta-ray", "hard"))
        self.assertIsNotNone(study_deck_for("manta-ray", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("card-study-pack", html)
        self.assertIn("Learn first", html)
        self.assertIn('<details class="study-teach">', html)
        self.assertNotIn('<details class="study-teach" open', html)
        self.assertIn('<summary class="study-teach-kicker">', html)
        self.assertIn("tap to open", html)
        self.assertNotIn("Talk about it", html)
        self.assertNotIn("Push further", html)
        self.assertNotIn('<details class="study-explore', html)
        self.assertNotIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        self.assertIn("Show answers", html)
        self.assertIn("Score", html)
        self.assertIn(">0</span>/5", html)
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
        self.assertIn("Largest living fish", html)
        self.assertNotIn("Largest living fish (exact length soft)", html)
        self.assertIn(
            "A checkerboard of light spots and stripes on a dark back — each shark’s pattern is unique",
            html,
        )
        self.assertNotIn("unique (soft)", html)
        self.assertIn(
            "No — it is a shark (a fish with a cartilage skeleton), even though the name says “whale”",
            html,
        )
        self.assertIn("Facts from Wikipedia, Whale shark.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "stingray", "packTemplate": "animals"})
        self.assertIn("card-study-pack", html)
        self.assertNotIn("Is a whale shark a whale", html)
        ray = STINGRAY.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", ray)
        self.assertNotIn("Is a whale shark a whale", ray)

    def test_published_whale_shark_card_matches_easy_deck(self):
        html = WHALE_SHARK.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertNotIn("Watch Live", main)
        self.assertNotIn("card-watch-live", main)
        self.assertNotIn("card-page-photo-link", main)
        self.assertIn("card-page-photo", main)
        self.assertIn("/field-pack/photos/whale-shark.jpg", main)
        self.assertNotIn("#habitat=whale-shark", main)
        self.assertIn("https://kids.nationalgeographic.com/animals/fish/facts/whale-sharks", main)
        self.assertNotIn("https://kids.nationalgeographic.com/animals/fish/facts/whale-shark\"", main)
        self.assertIn("Largest living fish", main)
        self.assertNotIn("Largest living fish (exact length soft)", main)
        self.assertIn(
            "A checkerboard of light spots and stripes on a dark back — each shark’s pattern is unique",
            main,
        )
        self.assertNotIn("unique (soft)", main)
        self.assertIn('href="/field-pack/cards/"', main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=7", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "whale-shark"', html)
        self.assertNotIn('"id": "shark"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=42", html)
        self.assertIn('<details class="study-teach">', main)
        self.assertNotIn('<details class="study-teach" open', main)
        self.assertNotIn('<div class="study-teach">', main)
        self.assertNotIn("Talk about it", main)
        self.assertNotIn("Push further", main)
        self.assertNotIn('<details class="study-explore', main)
        self.assertNotIn("Explore more", main)
        self.assertNotIn('<aside class="study-deepen"', main)
        self.assertLess(main.find("study-foot"), main.find("card-try-next"))
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
        self.assertIn(">0</span>/5", main)
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
        self.assertNotIn("Talk about it", back)
        self.assertNotIn("Push further", back)
        self.assertNotIn("ps-study-deepen", back)
        self.assertEqual(
            study_try_next_ids("whale-shark"),
            ["shark", "manta-ray", "clownfish"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("whale-shark")
        sheet = study_print_html(
            deck,
            name="Whale shark",
            emoji="🦈",
            photo="/field-pack/photos/whale-shark.jpg?v=img2",
            photo_pos="50% 48%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/whale-shark.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_WHALE_SHARK, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("Largest living fish", sheet)
        self.assertNotIn("Largest living fish (exact length soft)", sheet)
        self.assertIn(
            "A checkerboard of light spots and stripes on a dark back — each shark’s pattern is unique",
            sheet,
        )
        self.assertNotIn("unique (soft)", sheet)
        self.assertIn(
            "No — it is docile and poses no significant threat to people; it filters tiny food, not humans",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertNotIn("Talk about it", back)
        css = STYLES.read_text(encoding="utf-8")
        self.assertIn(".ps-study-front", css)
        js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function buildStudyCardHtml", js)
        self.assertIn("function studyDeckFor", js)
        self.assertIn("Junior Ranger", js)
        study_js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("Show answers", study_js)
        self.assertIn('details class="study-teach"', study_js)
        self.assertIn("questions.length !== 5", study_js)
        self.assertIn("paintScoreTotal", study_js)
        self.assertIn("FPStudyLevelName", study_js + STUDY_DATA_JS.read_text(encoding="utf-8"))

    def test_artifacts_include_whale_shark_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("whale-shark", payload)
        self.assertIn("stingray", payload)
        self.assertEqual(set(payload["stingray"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertIn("shark", payload)
        self.assertIn("manta-ray", payload)
        fish = payload["whale-shark"]
        self.assertEqual(fish["id"], "whale-shark")
        self.assertEqual(set(fish["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(fish["levels"]["zoologist"]["teach"], [])
        self.assertEqual(fish["levels"]["hard"]["teach"], [])
        easy = fish["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS_SHORT)
        self.assertEqual([q["correct"] for q in easy["questions"]], list(LETTERS))
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"whale-shark"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(set(payload["shark"]["levels"]), {"easy", "hard", "zoologist"})
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
        whale_html = WHALE_SHARK.read_text(encoding="utf-8")
        visible = _text(_main(whale_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        shark_html = SHARK.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(shark_html)))
        self.assertIn("Park Ranger", _text(_main(shark_html)))
        self.assertIn("Zoologist", _text(_main(shark_html)))


if __name__ == "__main__":
    unittest.main()
