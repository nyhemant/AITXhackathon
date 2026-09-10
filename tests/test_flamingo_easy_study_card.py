"""Caribbean flamingo Easy study-card: Junior Ranger, teach + 10 MCQs."""

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
    PUSH_FURTHER_FLAMINGO,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PENGUIN,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
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
FLAMINGO = FP / "cards" / "caribbean-flamingo" / "index.html"
PENGUIN = FP / "cards" / "african-penguin" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
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
    "Grown-up Caribbean flamingos are bright pink.",
    "They often stand on one leg.",
    "They find food in shallow water.",
    "A group of flamingos is a flock.",
    "Baby flamingos are grey and fluffy — not bright pink at first.",
)

STEMS = (
    "What colour are grown-up Caribbean flamingos?",
    "How do Caribbean flamingos often stand?",
    "Where do Caribbean flamingos find their food?",
    "What do you call a group of Caribbean flamingos?",
    "What do baby Caribbean flamingos look like at first?",
    "What is special about a Caribbean flamingo’s neck?",
    "What kind of nest does a Caribbean flamingo build?",
    "What is a Caribbean flamingo’s beak like?",
    "Why are grown-up Caribbean flamingos pink?",
    "Can Caribbean flamingos fly?",
)

QIDS = (
    "colour",
    "one-leg",
    "food-place",
    "flock",
    "chicks",
    "neck",
    "nest",
    "beak",
    "pink-food",
    "myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Endangered",
    "Critically Endangered",
    "Phoenicopterus",
    "flamboyance",
    "beta-carotene",
    "beta carotene",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class FlamingoEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_easy_only(self):
        self.assertIn("caribbean-flamingo", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("caribbean-flamingo"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("caribbean-flamingo", "hard"))
        self.assertIsNotNone(study_deck_for("caribbean-flamingo", "zoologist"))
        deck = study_deck_for("caribbean-flamingo")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "caribbean-flamingo")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, American flamingo / Caribbean flamingo.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_FLAMINGO))
        for q in deck["questions"]:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(str(q["why"]).strip())
        blob = " ".join(deck["teach"] + [q["stem"] + q["why"] for q in deck["questions"]])
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("flock", blob.lower())
        self.assertIn("mud mound", blob.lower())
        self.assertIn("capable flyers", blob.lower())

    def test_lion_giraffe_elephant_and_penguin_decks_untouched(self):
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
        elephant = study_deck_for("african-elephant")
        self.assertEqual(elephant["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertEqual(elephant["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("african-elephant", "hard"))
        self.assertIsNotNone(study_deck_for("african-elephant", "zoologist"))
        penguin = study_deck_for("african-penguin")
        self.assertEqual(penguin["source"], WIKI_AFRICAN_PENGUIN)
        self.assertEqual(penguin["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin["push_further"], list(PUSH_FURTHER_PENGUIN))
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("african-penguin", "hard"))
        self.assertIsNotNone(study_deck_for("african-penguin", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "caribbean-flamingo", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_FLAMINGO + PUSH_FURTHER_FLAMINGO:
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
        self.assertIn("Bright pink / reddish-pink", html)
        self.assertIn("Yes — they are strong fliers", html)
        self.assertIn("Facts from Wikipedia, American flamingo / Caribbean flamingo.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "jellyfish", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("What colour are grown-up Caribbean flamingos?", html)
        sea = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", sea)
        self.assertNotIn("card-study-pack", sea)

    def test_published_flamingo_card_matches_easy_deck(self):
        html = FLAMINGO.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("Watch Live", main)
        self.assertIn("/field-pack/virtual-zoo/?from=card#habitat=caribbean-flamingo", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "caribbean-flamingo"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=42", html)
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
        for prompt in TALK_ABOUT_FLAMINGO + PUSH_FURTHER_FLAMINGO:
            self.assertIn(prompt, back)

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("caribbean-flamingo")
        sheet = study_print_html(
            deck,
            name="Caribbean flamingo",
            emoji="🦩",
            photo="/field-pack/photos/caribbean-flamingo.jpg?v=img2",
            photo_pos="50% 18%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/caribbean-flamingo.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_AMERICAN_FLAMINGO, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("Bright pink / reddish-pink", sheet)
        self.assertIn("Yes — they are strong fliers", sheet)
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_FLAMINGO + PUSH_FURTHER_FLAMINGO:
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

    def test_artifacts_include_flamingo_easy_only(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("caribbean-flamingo", payload)
        self.assertIn("african-penguin", payload)
        self.assertIn("african-elephant", payload)
        self.assertIn("reticulated-giraffe", payload)
        self.assertIn("african-lion", payload)
        flamingo = payload["caribbean-flamingo"]
        self.assertEqual(flamingo["id"], "caribbean-flamingo")
        self.assertEqual(set(flamingo["levels"]), {"easy", "hard", "zoologist"})
        easy = flamingo["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        self.assertEqual(flamingo["levels"]["hard"]["teach"], [])
        self.assertEqual(flamingo["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("caribbean-flamingo", data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertIn('"hard":"Park Ranger"', data_js)
        self.assertEqual(set(payload["african-lion"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["reticulated-giraffe"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["african-elephant"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["african-penguin"]["levels"]), {"easy", "hard", "zoologist"})

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
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(elephant_html)))
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(penguin_html)))
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(flamingo_html)))
        self.assertIn("Zoologist", _text(_main(flamingo_html)))


if __name__ == "__main__":
    unittest.main()
