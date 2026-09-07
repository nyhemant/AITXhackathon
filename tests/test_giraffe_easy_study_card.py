"""Reticulated giraffe Easy study-card: Junior Ranger only, teach + 10 MCQs."""

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
    PUSH_FURTHER_GIRAFFE,
    STUDY_SLOTS,
    TALK_ABOUT_GIRAFFE,
    WIKI_GIRAFFE,
    WIKI_LION,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
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
    "The giraffe is the tallest living land animal.",
    "It eats leaves and shoots from tall trees.",
    "A very long neck helps it reach high foliage.",
    "A baby giraffe is a calf.",
    "Wild giraffes live on African savannah and open woodland.",
)

STEMS = (
    "What record does a giraffe hold among living land animals?",
    "What do giraffes mostly eat?",
    "Why does a giraffe have such a long neck?",
    "What is special about a giraffe’s tongue?",
    "What is a baby giraffe called, and what can it do soon after birth?",
    "Where do wild giraffes mostly live?",
    "How does a giraffe drink water?",
    "What are the horn-like bumps on a giraffe’s head?",
    "What is special about a giraffe’s coat?",
    "Does a giraffe have extra neck bones compared with most mammals?",
)

QIDS = (
    "tallest",
    "food",
    "neck",
    "tongue",
    "young",
    "home",
    "drink",
    "ossicones",
    "coat",
    "myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
INVENTED_TONGUE_CM = ("45 cm", "45cm", "18 in", "18in", "30 cm", "30cm", "12 in", "12in")


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class GiraffeEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_easy_only(self):
        self.assertIn("reticulated-giraffe", study_card_ids())
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy",))
        self.assertIsNone(study_deck_for("reticulated-giraffe", "hard"))
        self.assertIsNone(study_deck_for("reticulated-giraffe", "zoologist"))
        deck = study_deck_for("reticulated-giraffe")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "reticulated-giraffe")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_GIRAFFE)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Giraffe / Reticulated giraffe.")
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_GIRAFFE))
        for q in deck["questions"]:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(str(q["why"]).strip())
        blob = " ".join(deck["teach"] + [q["stem"] + q["why"] for q in deck["questions"]])
        for phrase in INVENTED_TONGUE_CM:
            self.assertNotIn(phrase, blob)
        self.assertNotIn("Kenya only", blob)
        self.assertNotIn("only in Kenya", blob.lower())

    def test_lion_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("african-lion", "hard"))
        self.assertIsNotNone(study_deck_for("african-lion", "zoologist"))
        self.assertIsNone(study_deck_for("african-elephant"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "reticulated-giraffe", "packTemplate": "animals"})
        self.assertIn(f">{CARD_TALK_H2}</h2>", html)
        self.assertIn("card-study-pack", html)
        self.assertIn("Learn first", html)
        self.assertIn("<details class=\"study-teach\">", html)
        self.assertNotIn("<details class=\"study-teach\" open", html)
        self.assertIn("<summary class=\"study-teach-kicker\">", html)
        self.assertIn("tap to open", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertRegex(html, r'<aside class="study-deepen"[^>]*\bhidden\b')
        for prompt in TALK_ABOUT_GIRAFFE + PUSH_FURTHER_GIRAFFE:
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
        self.assertNotIn("Park Ranger", visible)
        self.assertNotIn("Zoologist", visible)
        self.assertIn('class="study-level-badge"', html)
        self.assertNotIn('class="study-level-picker"', html)
        self.assertNotIn("data-study-pick", html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        self.assertIn("Skin-covered ossicones", html)
        self.assertIn("still seven vertebrae, just much longer", html)
        self.assertIn("Facts from Wikipedia, Giraffe / Reticulated giraffe.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "koala", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("What record does a giraffe hold", html)
        elephant = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", elephant)
        self.assertNotIn("card-study-pack", elephant)

    def test_published_giraffe_card_matches_easy_deck(self):
        html = GIRAFFE.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("Watch Live", main)
        self.assertIn("/field-pack/virtual-zoo/?from=card#habitat=reticulated-giraffe", main)
        self.assertIn("study-card.js?v=6", html)
        self.assertIn("study-card.css?v=7", html)
        self.assertIn("study-cards-data.js?v=5", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "reticulated-giraffe"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=41", html)
        self.assertIn("<details class=\"study-teach\">", main)
        self.assertNotIn("<details class=\"study-teach\" open", main)
        self.assertNotIn("<div class=\"study-teach\">", main)
        self.assertIn("Talk about it", main)
        self.assertIn("Push further", main)
        self.assertRegex(main, r'<aside class="study-deepen"[^>]*\bhidden\b')
        visible = _text(main)
        self.assertIn("Junior Ranger", visible)
        self.assertNotIn("Park Ranger", visible)
        self.assertNotIn("Zoologist", visible)
        self.assertIn('class="study-level-badge"', main)
        self.assertNotIn('class="study-level-picker"', main)
        self.assertNotIn("data-study-pick", main)
        self.assertIn("Learn first", main)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        for phrase in INVENTED_TONGUE_CM:
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
        for prompt in TALK_ABOUT_GIRAFFE + PUSH_FURTHER_GIRAFFE:
            self.assertIn(prompt, back)

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("reticulated-giraffe")
        sheet = study_print_html(
            deck,
            name="Reticulated giraffe",
            emoji="🦒",
            photo="/field-pack/photos/reticulated-giraffe.jpg?v=img2",
            photo_pos="50% 18%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/reticulated-giraffe.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_GIRAFFE, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("Skin-covered ossicones", sheet)
        self.assertIn("still seven vertebrae, just much longer", sheet)
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_GIRAFFE + PUSH_FURTHER_GIRAFFE:
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

    def test_artifacts_include_giraffe_easy_only(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("reticulated-giraffe", payload)
        self.assertIn("african-lion", payload)
        giraffe = payload["reticulated-giraffe"]
        self.assertEqual(giraffe["id"], "reticulated-giraffe")
        self.assertEqual(set(giraffe["levels"]), {"easy"})
        easy = giraffe["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("reticulated-giraffe", data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        lion_levels = payload["african-lion"]["levels"]
        self.assertEqual(set(lion_levels), {"easy", "hard", "zoologist"})

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


if __name__ == "__main__":
    unittest.main()
