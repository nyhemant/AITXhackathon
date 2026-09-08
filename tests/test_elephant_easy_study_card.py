"""African elephant Easy study-card: Junior Ranger only, teach + 10 MCQs."""

from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import CARD_TALK_H2, outing_talk_html  # noqa: E402
from study_cards import (  # noqa: E402
    LEVEL_DISPLAY_NAMES,
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_LION,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_GIRAFFE,
    WIKI_LION,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
OTTER = FP / "cards" / "asian-small-clawed-otter" / "index.html"
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
    "The African elephant is the largest living land animal.",
    "It eats plants — grass, leaves, and bark — not meat.",
    "Its trunk can grab, drink, spray, and smell.",
    "A baby elephant is a calf.",
    "A herd is led by the oldest female.",
)

STEMS = (
    "What record does an African elephant hold among living land animals?",
    "What do African elephants eat?",
    "What does an elephant use its trunk for?",
    "Why does an African elephant have such big ears?",
    "What is a baby elephant called?",
    "Who usually leads an elephant herd?",
    "What are an elephant’s tusks?",
    "What sound is an elephant famous for?",
    "How can an African elephant swim?",
    "Can an elephant jump?",
)

QIDS = (
    "biggest",
    "food",
    "trunk",
    "ears",
    "young",
    "family",
    "tusks",
    "voice",
    "water",
    "myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "only mammal on Earth",
    "only mammal",
    "Loxodonta",
    "bush elephant",
    "forest elephant",
    "Loxodonta africana",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class ElephantEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_easy_only(self):
        self.assertIn("african-elephant", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("african-elephant", "hard"))
        self.assertIsNotNone(study_deck_for("african-elephant", "zoologist"))
        deck = study_deck_for("african-elephant")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "african-elephant")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, African elephant / Elephant.")
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_ELEPHANT))
        for q in deck["questions"]:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(str(q["why"]).strip())
        blob = " ".join(deck["teach"] + [q["stem"] + q["why"] for q in deck["questions"]])
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("cannot jump", blob.lower())
        young = next(q for q in deck["questions"] if q["id"] == "young")
        tusks = next(q for q in deck["questions"] if q["id"] == "tusks")
        self.assertIn("calf", young["why"].lower())
        self.assertGreaterEqual(len(young["why"].split()), 12)
        self.assertIn("teeth", tusks["why"].lower())
        self.assertGreaterEqual(len(tusks["why"].split()), 12)

    def test_lion_and_giraffe_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("african-lion", "hard"))
        self.assertIsNotNone(study_deck_for("african-lion", "zoologist"))
        giraffe = study_deck_for("reticulated-giraffe")
        self.assertEqual(giraffe["source"], WIKI_GIRAFFE)
        self.assertEqual(giraffe["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("reticulated-giraffe", "hard"))
        self.assertIsNotNone(study_deck_for("reticulated-giraffe", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "african-elephant", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("card-study-pack", html)
        self.assertIn("Learn first", html)
        self.assertIn("<details class=\"study-teach\">", html)
        self.assertNotIn("<details class=\"study-teach\" open", html)
        self.assertIn("<summary class=\"study-teach-kicker\">", html)
        self.assertIn("tap to open", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        for prompt in TALK_ABOUT_ELEPHANT + PUSH_FURTHER_ELEPHANT:
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
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        for phrase in BRITTLE:
            self.assertNotIn(phrase, html)
        self.assertIn("Very long teeth", html)
        self.assertIn("elephants cannot jump", html)
        self.assertIn("Facts from Wikipedia, African elephant / Elephant.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "asian-small-clawed-otter", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("What record does an African elephant hold", html)
        otter = OTTER.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", otter)
        self.assertNotIn("card-study-pack", otter)

    def test_published_elephant_card_matches_easy_deck(self):
        html = ELEPHANT.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("Watch Live", main)
        self.assertIn("/field-pack/virtual-zoo/?from=card#habitat=african-elephant", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "african-elephant"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=41", html)
        self.assertIn("<details class=\"study-teach\">", main)
        self.assertNotIn("<details class=\"study-teach\" open", main)
        self.assertNotIn("<div class=\"study-teach\">", main)
        self.assertIn("Talk about it", main)
        self.assertIn("Push further", main)
        self.assertIn('<details class="study-explore', main)
        self.assertIn("Explore more", main)
        self.assertNotIn('<aside class="study-deepen"', main)
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
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        for phrase in BRITTLE:
            self.assertNotIn(phrase, main)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertNotIn(" · Easy ·", print_tpl)
        self.assertNotIn(" · Hard ·", print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertNotIn("Push further", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        self.assertIn("ps-study-deepen", back)
        for prompt in TALK_ABOUT_ELEPHANT + PUSH_FURTHER_ELEPHANT:
            self.assertIn(prompt, back)

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("african-elephant")
        sheet = study_print_html(
            deck,
            name="African elephant",
            emoji="🐘",
            photo="/field-pack/photos/african-elephant.jpg?v=img2",
            photo_pos="50% 28%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/african-elephant.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_AFRICAN_ELEPHANT, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("Very long teeth", sheet)
        self.assertIn("elephants cannot jump", sheet)
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_ELEPHANT + PUSH_FURTHER_ELEPHANT:
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
        self.assertIn("details class=\"study-teach\"", study_js)
        self.assertIn("study-deepen", study_js)
        self.assertIn("is-wrong-pick", study_js)
        self.assertIn("FPStudyLevelName", study_js + STUDY_DATA_JS.read_text(encoding="utf-8"))

    def test_artifacts_include_elephant_easy_only(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("african-elephant", payload)
        self.assertIn("reticulated-giraffe", payload)
        self.assertIn("african-lion", payload)
        elephant = payload["african-elephant"]
        self.assertEqual(elephant["id"], "african-elephant")
        self.assertEqual(set(elephant["levels"]), {"easy", "hard", "zoologist"})
        easy = elephant["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        self.assertEqual(elephant["levels"]["hard"]["teach"], [])
        self.assertEqual(elephant["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("african-elephant", data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertIn('"hard":"Park Ranger"', data_js)
        lion_levels = payload["african-lion"]["levels"]
        self.assertEqual(set(lion_levels), {"easy", "hard", "zoologist"})
        giraffe_levels = payload["reticulated-giraffe"]["levels"]
        self.assertEqual(set(giraffe_levels), {"easy", "hard", "zoologist"})

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
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(lion_html)))
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(giraffe_html)))


if __name__ == "__main__":
    unittest.main()
