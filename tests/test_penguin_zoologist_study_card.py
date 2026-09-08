"""African penguin Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PENGUIN,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_GIRAFFE,
    WIKI_LION,
    level_display_name,
    shipped_levels_for,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
PENGUIN = FP / "cards" / "african-penguin" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Which genus do African penguins belong to, and who are their closest banded-penguin relatives?",
    "What makes the African penguin unique among living penguins?",
    "How does an African penguin’s supraorbital salt gland keep the body in osmotic balance?",
    "What named camouflage strategy is an African penguin’s dark back and pale belly?",
    "What actually makes the pink facial patch above an African penguin’s eye look pinker when the bird is warmer?",
    "What combination of pressures has driven the sharp drop in wild African penguins?",
    "How do commercial fisheries compete with African penguins near colonies?",
    "Why can no-take fishing closures around African penguin colonies help breeding birds?",
    "How do African penguins usually catch their prey underwater?",
    "What are penguins’ closest living relatives as an order?",
)

ZOOLOGIST_IDS = (
    "genus",
    "old-world",
    "supraorbital",
    "countershading",
    "vasodilation",
    "decline-drivers",
    "fishery",
    "no-take",
    "pursuit-dive",
    "tubenoses",
)

HARD_STEMS = (
    "What does the bare pink skin above an African penguin’s eye help it do?",
    "What is special about an African penguin’s chest spots?",
    "What happens in an African penguin’s catastrophic moult?",
    "How does an African penguin get rid of extra salt from seawater and sea food?",
    "What is the biggest problem facing wild African penguins today?",
    "How did old guano harvesting hurt African penguin nests?",
    "How do African penguin pairs often behave from year to year?",
    "Where do African penguins breed in the wild?",
    "Why are African penguins called banded penguins?",
    "Do wild penguins and polar bears ever meet?",
)

EASY_STEMS = (
    "Where do wild African penguins live?",
    "Can an African penguin fly in the air?",
    "What do African penguins mostly eat?",
    "Why is the African penguin sometimes called a “jackass penguin”?",
    "What do you call a large group of African penguins living together?",
    "How do African penguins have babies?",
    "How does an African penguin’s black-and-white coat help it hide?",
    "What are an African penguin’s wings like?",
    "Where do African penguins usually nest?",
    "Do all penguins live on cold ice?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "Critically Endangered",
    "critically endangered",
    "IUCN",
    "status CR",
    "Endangered",
    "95%",
    "95 percent",
    "10,000",
    "10000",
    "19,800",
    "19800",
    "20,850",
    "20850",
    "130 m",
    "130m",
    "430 ft",
    "275 second",
    "25 m",
    "25m",
    "69 second",
)
REDO_THEMES = (
    "jackass penguin",
    "cannot fly in the air",
    "donkey-like",
    "catastrophic moult",
    "like a fingerprint",
    "guano harvesting",
    "polar bears",
    "live in Africa, not Antarctica",
    "Lose heat — the patch flushes pinker",
    "A salt gland near the eye helps dump",
    "Not enough prey fish, after commercial fishing",
    "dark band(s) across the chest",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class PenguinZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("african-penguin", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_AFRICAN_PENGUIN)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, African penguin.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_PENGUIN))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("african-penguin", "zoologist")
        easy = study_deck_for("african-penguin", "easy")
        hard = study_deck_for("african-penguin", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("african-penguin", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Spheniscus", questions[0]["choices"][1])
        self.assertIn("Humboldt", questions[0]["choices"][1])
        self.assertIn("Magellanic", questions[0]["choices"][1])
        self.assertIn("Galápagos", questions[0]["choices"][1])
        self.assertIn("African continent", questions[1]["choices"][1])
        self.assertIn("Old World", questions[1]["choices"][1])
        self.assertIn("excretes concentrated salt", questions[2]["choices"][1])
        self.assertIn("supraorbital", questions[2]["stem"].lower())
        self.assertIn("osmotic", questions[2]["stem"].lower() + questions[2]["why"].lower())
        self.assertIn("Classic countershading", questions[3]["choices"][1])
        self.assertIn("vasodilation", questions[4]["choices"][1])
        self.assertIn("vasoconstriction", questions[4]["choices"][1])
        self.assertIn("Prey shortage", questions[5]["choices"][1])
        self.assertIn("habitat loss", questions[5]["choices"][1])
        self.assertIn("Purse-seine", questions[6]["choices"][1])
        self.assertIn("sardines and anchovies", questions[6]["choices"][1])
        self.assertIn("foraging range", questions[7]["choices"][1])
        self.assertIn("pursuit diving", questions[8]["choices"][1])
        self.assertIn("relatively shallow", questions[8]["choices"][1])
        self.assertIn("Tubenoses", questions[9]["choices"][1])
        self.assertIn("albatrosses", questions[9]["choices"][1])
        self.assertIn("petrels", questions[9]["choices"][1])
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("african-penguin", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "african-penguin", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_zoologist_print_is_answer_light_duplex(self):
        deck = study_deck_for("african-penguin", "zoologist")
        sheet = study_print_html(
            deck,
            name="African penguin",
            emoji="🐧",
            photo="/field-pack/photos/african-penguin.jpg?v=img2",
            photo_pos="50% 20%",
        )
        self.assertIn("Zoologist", sheet)
        self.assertNotIn("Junior Ranger", sheet)
        self.assertNotIn("Park Ranger", sheet)
        self.assertNotIn("Learn first", sheet)
        self.assertNotIn("ps-study-teach", sheet)
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        front, _, back = sheet.partition("ps-study-back")
        self.assertNotIn("Talk about it", front)
        self.assertNotIn("Push further", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        self.assertIn("ps-study-deepen", back)
        for prompt in TALK_ABOUT_PENGUIN + PUSH_FURTHER_PENGUIN:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_AFRICAN_PENGUIN, sheet)
        self.assertIn("Facts from Wikipedia, African penguin.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("african-penguin", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_lion_giraffe_and_elephant_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_zoo = study_deck_for("african-lion", "zoologist")
        self.assertEqual(lion_zoo["source"], WIKI_LION)
        self.assertIn("hyoid", lion_zoo["questions"][0]["choices"][1])
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)
        self.assertEqual(lion_zoo["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion_zoo["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        giraffe_zoo = study_deck_for("reticulated-giraffe", "zoologist")
        self.assertEqual(giraffe_zoo["source"], WIKI_GIRAFFE)
        self.assertIn("Giraffa reticulata", giraffe_zoo["questions"][0]["choices"][1])
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giraffe_html)
        self.assertIn("Junior Ranger", giraffe_html)
        self.assertIn("Park Ranger", giraffe_html)
        self.assertEqual(giraffe_zoo["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_zoo["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_zoo = study_deck_for("african-elephant", "zoologist")
        self.assertEqual(elephant_zoo["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Loxodonta africana", elephant_zoo["questions"][0]["choices"][1])
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertIn("Junior Ranger", elephant_html)
        self.assertIn("Park Ranger", elephant_html)
        self.assertEqual(elephant_zoo["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_zoo["push_further"], list(PUSH_FURTHER_ELEPHANT))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["african-penguin"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("Spheniscus", data_js)
        self.assertIn("supraorbital", data_js)
        self.assertIn("vasodilation", data_js)
        self.assertIn("tubenoses", data_js.lower())
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=8", html)
        self.assertIn("study-cards-data.js?v=5", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Zoologist", print_tpl)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, print_tpl)


if __name__ == "__main__":
    unittest.main()
