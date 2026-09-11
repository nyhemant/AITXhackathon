"""Caribbean flamingo Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    correct_choice_text,
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
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
FLAMINGO = FP / "cards" / "caribbean-flamingo" / "index.html"
PENGUIN = FP / "cards" / "african-penguin" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "What do molecular studies place flamingos closest to among living birds?",
    "What kind of pigment gives a Caribbean flamingo’s feathers their main pink colour?",
    "Where does flamingo “crop milk” actually come from, and is it like mammalian milk?",
    "How does a Caribbean flamingo’s tongue help it filter-feed?",
    "What is unusual about a flamingo’s bill compared with most birds?",
    "How do Caribbean flamingos handle the extra salt in hypersaline lakes?",
    "What biomechanical trick lets a flamingo hold a one-leg pose with almost no muscle work?",
    "How have scientists treated the American / Caribbean flamingo (Phoenicopterus ruber) next to the greater flamingo?",
    "How does a Caribbean flamingo chick’s bill change as it grows?",
    "How does the wild status of the American / Caribbean flamingo compare with many other zoo-card animals?",
)

ZOOLOGIST_IDS = (
    "grebes",
    "feather-pigment",
    "crop-milk-glands",
    "tongue-piston",
    "bill-mechanics",
    "salt-glands",
    "gravity-stay",
    "lump-split",
    "chick-bill",
    "status-soft",
)

HARD_STEMS = (
    "What actually makes a Caribbean flamingo’s feathers pink?",
    "How does a Caribbean flamingo hold its bill when it feeds?",
    "What do the comb-like lamellae in a Caribbean flamingo’s bill do?",
    "How do Caribbean flamingo parents feed a newly hatched chick?",
    "How many eggs does a Caribbean flamingo usually lay in a clutch?",
    "Why can standing on one leg take almost no muscle effort for a flamingo?",
    "Why can Caribbean flamingos thrive in very salty shallow water?",
    "How does a Caribbean / American flamingo’s colour compare with other flamingo species?",
    "What do Caribbean flamingo groups often do when they court?",
    "If a zoo flamingo looks pale, what is the usual reason?",
)

EASY_STEMS = (
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

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "Least Concern",
    "least concern",
    "IUCN",
    "status LC",
    "Endangered",
    "Critically Endangered",
    "critically endangered",
    "beta-carotene",
    "beta carotene",
    "flamboyance",
)
REDO_THEMES = (
    "Bright pink / reddish-pink",
    "On one leg",
    "In shallow water",
    "A flock",
    "Grey and fluffy",
    "long and bendy",
    "little mound of mud",
    "Bent in the middle",
    "The pink colour comes from the food they eat",
    "Yes — they are strong fliers",
    "Carotenoid pigments in algae, shrimp",
    "Upside down — the head is inverted",
    "Strain tiny food from the water",
    "Both parents can feed a nutrient-rich “crop milk”",
    "Typically one egg",
    "A passive joint lock lets the pose hold",
    "Few other birds compete there",
    "most vividly coloured",
    "head-flagging and wing salutes",
    "needs more carotenoids in its diet",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class FlamingoZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("caribbean-flamingo"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("caribbean-flamingo", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, American flamingo / Caribbean flamingo.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_FLAMINGO))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("caribbean-flamingo", "zoologist")
        easy = study_deck_for("caribbean-flamingo", "easy")
        hard = study_deck_for("caribbean-flamingo", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("caribbean-flamingo", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Grebes", correct_choice_text(questions[0]))
        self.assertIn("Mirandornithes", correct_choice_text(questions[0]))
        self.assertIn("herons", correct_choice_text(questions[0]).lower())
        self.assertIn("carotenoid", correct_choice_text(questions[1]).lower())
        self.assertIn("canthaxanthin", correct_choice_text(questions[1]).lower())
        self.assertIn("such as", correct_choice_text(questions[1]).lower() + questions[1]["why"].lower())
        self.assertIn("upper digestive tract", correct_choice_text(questions[2]).lower())
        self.assertIn("both sexes", correct_choice_text(questions[2]).lower())
        self.assertIn("not mammalian milk", correct_choice_text(questions[2]).lower())
        self.assertIn("piston", correct_choice_text(questions[3]).lower())
        self.assertIn("lamellae", correct_choice_text(questions[3]).lower())
        self.assertIn("lower mandible", correct_choice_text(questions[4]).lower())
        self.assertIn("upper mandible", correct_choice_text(questions[4]).lower())
        self.assertIn("Nasal salt glands", correct_choice_text(questions[5]))
        self.assertIn("concentrated salt", correct_choice_text(questions[5]).lower())
        self.assertIn("Gravity", correct_choice_text(questions[6]))
        self.assertIn("passive stay", correct_choice_text(questions[6]).lower())
        self.assertIn("P. ruber", correct_choice_text(questions[7]))
        self.assertIn("lumped", correct_choice_text(questions[7]).lower())
        self.assertIn("greater flamingo", correct_choice_text(questions[7]).lower())
        self.assertIn("relatively straight", correct_choice_text(questions[8]).lower())
        self.assertIn("filter-feeding", correct_choice_text(questions[8]).lower())
        self.assertIn("relatively secure", correct_choice_text(questions[9]).lower())
        self.assertIn("lower-risk", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("caribbean-flamingo", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "caribbean-flamingo", "packTemplate": "animals"})
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
        deck = study_deck_for("caribbean-flamingo", "zoologist")
        sheet = study_print_html(
            deck,
            name="Caribbean flamingo",
            emoji="🦩",
            photo="/field-pack/photos/caribbean-flamingo.jpg?v=img2",
            photo_pos="50% 18%",
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
        for prompt in TALK_ABOUT_FLAMINGO + PUSH_FURTHER_FLAMINGO:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_AMERICAN_FLAMINGO, sheet)
        self.assertIn("Facts from Wikipedia, American flamingo / Caribbean flamingo.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("caribbean-flamingo", "zoologist"))
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

    def test_lion_giraffe_elephant_and_penguin_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_zoo = study_deck_for("african-lion", "zoologist")
        self.assertEqual(lion_zoo["source"], WIKI_LION)
        self.assertIn("hyoid", correct_choice_text(lion_zoo["questions"][0]))
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)
        self.assertEqual(lion_zoo["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion_zoo["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        giraffe_zoo = study_deck_for("reticulated-giraffe", "zoologist")
        self.assertEqual(giraffe_zoo["source"], WIKI_GIRAFFE)
        self.assertIn("Giraffa reticulata", correct_choice_text(giraffe_zoo["questions"][0]))
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giraffe_html)
        self.assertIn("Junior Ranger", giraffe_html)
        self.assertIn("Park Ranger", giraffe_html)
        self.assertEqual(giraffe_zoo["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_zoo["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_zoo = study_deck_for("african-elephant", "zoologist")
        self.assertEqual(elephant_zoo["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Loxodonta africana", correct_choice_text(elephant_zoo["questions"][0]))
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertIn("Junior Ranger", elephant_html)
        self.assertIn("Park Ranger", elephant_html)
        self.assertEqual(elephant_zoo["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_zoo["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        penguin_zoo = study_deck_for("african-penguin", "zoologist")
        self.assertEqual(penguin_zoo["source"], WIKI_AFRICAN_PENGUIN)
        self.assertIn("Spheniscus", correct_choice_text(penguin_zoo["questions"][0]))
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", penguin_html)
        self.assertIn("Junior Ranger", penguin_html)
        self.assertIn("Park Ranger", penguin_html)
        self.assertEqual(penguin_zoo["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin_zoo["push_further"], list(PUSH_FURTHER_PENGUIN))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["caribbean-flamingo"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("Mirandornithes", data_js)
        self.assertIn("tongue-piston", data_js)
        self.assertIn("gravity-stay", data_js)
        self.assertIn("lump-split", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-cards-data.js?v=7", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Zoologist", print_tpl)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, print_tpl)


if __name__ == "__main__":
    unittest.main()
