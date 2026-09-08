"""African lion Easy study-card: Junior Ranger labels, teach + 10 MCQs."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import CARD_TALK_H2, STUDY_CARD_CSS_VER, outing_talk_html  # noqa: E402
from study_cards import (  # noqa: E402
    LEVEL_DISPLAY_NAMES,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_LION,
    WIKI_LION,
    level_display_name,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
LION = FP / "cards" / "african-lion" / "index.html"
PRINT_KIT = FP / "js" / "print-kit.js"
STUDY_JS = FP / "js" / "study-card.js"
STYLES = FP / "css" / "styles.css"

GENERIC_WORKSHEET = (
    "What do they eat?",
    "Where is home?",
    "What is their superpower?",
    "Baby or grown-up?",
    "I want to teach about…",
    "Food detective",
    "Does this lion have a big fluffy mane?",
    "Meat eater or plant eater?",
    "What do you notice?",
)

TEACH = (
    "A group of lions is a pride.",
    "A baby is a cub.",
    "They live on grasslands / savannah, not jungle.",
    "Their famous sound is a roar.",
    "Male lions often grow a big mane.",
)

STEMS = (
    "What do you call a group of lions?",
    "What do lions mostly eat?",
    "What sound is a lion famous for?",
    "Which lion usually grows a big fluffy mane?",
    "What is a baby lion called?",
    "Where do wild lions mostly live?",
    "How much of the day do lions often spend resting?",
    "In a pride, who usually does most of the hunting?",
    "What special tip does a lion’s tail have?",
    "Do lions really live in a jungle like in some cartoons?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class LionEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_locked_easy_only(self):
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
            ),
        )
        deck = study_deck_for("african-lion")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_LION)
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(study_deck_for("african-elephant")["level"], "easy")
        self.assertIsNotNone(study_deck_for("african-elephant", "hard"))
        self.assertIsNotNone(study_deck_for("african-elephant", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "african-lion", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_LION + PUSH_FURTHER_LION:
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
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        self.assertIn("A pride", html)
        self.assertIn("The moms (lionesses)", html)
        self.assertIn("about 8 km / 5 miles (Wikipedia)", html)
        self.assertIn("Facts from Wikipedia, Lion.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "koala", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("What do you call a group of lions?", html)

    def test_published_lion_card_matches_easy_deck(self):
        html = LION.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("Watch Live", main)
        self.assertIn("/field-pack/virtual-zoo/?from=card#habitat=african-lion", main)
        self.assertNotIn("nationalzoo.si.edu/webcams", main)
        self.assertIn("Look close — mane, whiskers, a tuft on the tail.", html)
        self.assertNotIn("mighty roar", html)
        self.assertIn("study-card.js?v=6", html)
        self.assertIn("study-card.css?v=7", html)
        self.assertIn("study-cards-data.js?v=5", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
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
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        self.assertIn('class="study-level-picker"', main)
        self.assertIn('data-study-pick="easy"', main)
        self.assertIn('data-study-pick="hard"', main)
        self.assertIn('data-study-pick="zoologist"', main)
        self.assertIn("Learn first", main)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
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
        for prompt in TALK_ABOUT_LION + PUSH_FURTHER_LION:
            self.assertIn(prompt, back)

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("african-lion")
        sheet = study_print_html(
            deck,
            name="African lion",
            emoji="🦁",
            photo="/field-pack/photos/african-lion.jpg?v=img2",
            photo_pos="50% 22%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/african-lion.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_LION, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("A dark hairy tuft", sheet)
        self.assertIn("The moms (lionesses)", sheet)
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_LION + PUSH_FURTHER_LION:
            self.assertIn(prompt, back)
        css = STYLES.read_text(encoding="utf-8")
        self.assertIn(".ps-study-front", css)
        self.assertIn(".ps-study-deepen", css)
        self.assertIn("height: 9.4in", css)
        self.assertIn("body.printing-study > *:not(#print-sheet)", css)
        self.assertIn(":not(.printing-study)", css)
        js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function buildStudyCardHtml", js)
        self.assertIn('classList.toggle("printing-study"', js)
        self.assertIn("size: A4 portrait", js)
        self.assertIn("function studyDeckFor", js)
        self.assertIn("function studyLevelName", js)
        self.assertIn("Junior Ranger", js)
        self.assertTrue(STUDY_JS.is_file())
        study_js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("Show answers", study_js)
        self.assertIn("details class=\"study-teach\"", study_js)
        self.assertIn("study-deepen", study_js)
        self.assertIn("Talk about it", study_js)
        self.assertIn("FPStudyLevelName", study_js + STUDY_DATA_JS.read_text(encoding="utf-8"))

    def test_hard_screen_hides_empty_teach_but_keeps_deepen(self):
        hard = study_deck_for("african-lion", "hard")
        html = study_talk_html(hard)
        self.assertNotIn("study-teach", html)
        self.assertNotIn("<details", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertRegex(html, r'<aside class="study-deepen"[^>]*\bhidden\b')

    def test_display_name_map_covers_future_tiers(self):
        self.assertEqual(
            LEVEL_DISPLAY_NAMES,
            {
                "easy": "Junior Ranger",
                "hard": "Park Ranger",
                "zoologist": "Zoologist",
            },
        )
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        self.assertEqual(level_display_name("unknown"), "Junior Ranger")
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("window.FP_STUDY_LEVEL_NAMES", data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertIn('"hard":"Park Ranger"', data_js)
        self.assertIn('"zoologist":"Zoologist"', data_js)
        self.assertIn("window.FPStudyLevelName", data_js)

    def test_desktop_widens_study_card_page_only(self):
        css = (FP / "css" / "study-card.css").read_text(encoding="utf-8")
        seo = (FP / "css" / "seo-venue.css").read_text(encoding="utf-8")
        self.assertEqual(STUDY_CARD_CSS_VER, "7")
        self.assertIn("max-width: 34rem;", seo)
        self.assertIn("@media screen and (min-width: 960px)", css)
        self.assertIn("max-width: 48rem;", css)
        self.assertIn(".study-choice.is-wrong-pick", css)
        self.assertNotIn("@media print", css)
        koala = (FP / "cards" / "koala" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("study-card.css", koala)


if __name__ == "__main__":
    unittest.main()
