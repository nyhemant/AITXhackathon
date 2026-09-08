"""Zebra Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_ZEBRA,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_TORTOISE,
    TALK_ABOUT_ZEBRA,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
    WIKI_GALAPAGOS_TORTOISE,
    WIKI_GIRAFFE,
    WIKI_LION,
    WIKI_PLAINS_ZEBRA,
    level_display_name,
    shipped_levels_for,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
ZEBRA = FP / "cards" / "zebra" / "index.html"
TORTOISE = FP / "cards" / "galapagos-tortoise" / "index.html"
FLAMINGO = FP / "cards" / "caribbean-flamingo" / "index.html"
PENGUIN = FP / "cards" / "african-penguin" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "What is a leading idea today for why plains zebras have stripes?",
    "What is a plains zebra harem?",
    "What do young male plains zebras often do before starting a harem?",
    "Why are plains zebras often called pioneer grazers?",
    "How does a plains zebra digest grass compared with a cow-like ruminant?",
    "How tied are plains zebras to drinking water?",
    "What do plains zebras often do when they spot a predator?",
    "What colour are a newborn plains zebra’s stripes at first?",
    "What extra marking do some southern plains zebras show between the black and white?",
    "What puts wild plains zebras under pressure today?",
)

HARD_IDS = (
    "fly-stripe",
    "harem",
    "bachelors",
    "pioneer",
    "hindgut",
    "water",
    "alarm",
    "foal-coat",
    "shadow-stripes",
    "threats",
)

EASY_STEMS = (
    "What is special about a plains zebra’s coat?",
    "What do plains zebras mostly eat?",
    "Where do wild plains zebras live?",
    "How do plains zebras live together?",
    "What do you call a baby plains zebra?",
    "How do plains zebras escape danger?",
    "What animal is a plains zebra a wild relative of?",
    "What is a plains zebra’s mane like?",
    "What contact call is a plains zebra known for?",
    "Are plains zebras just striped farm horses you can ride?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Near Threatened",
    "near threatened",
    "quagga",
    "Quagga",
    "subspecies",
    "cline",
    "flehmen",
    "Equus",
    "mph",
    "km/h",
    "37",
    "43",
    "60 km",
    "70 km",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class ZebraHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("zebra"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("zebra", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("zebra", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_PLAINS_ZEBRA)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Plains zebra.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_ZEBRA))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_ZEBRA))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("zebra", "easy")
        hard = study_deck_for("zebra", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("zebra", "hard")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(HARD_IDS))
        self.assertEqual([q["stem"] for q in questions], list(HARD_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("deter biting flies", correct_choice_text(questions[0]))
        self.assertIn("leading", questions[0]["stem"].lower() + " " + questions[0]["why"].lower())
        self.assertIn("hypothesis", questions[0]["why"].lower())
        self.assertIn("One stallion, several mares, and their young", correct_choice_text(questions[1]))
        self.assertIn("bachelor groups", correct_choice_text(questions[2]))
        self.assertIn("tall, tough grass", correct_choice_text(questions[3]))
        self.assertIn("hindgut fermenter", correct_choice_text(questions[4]))
        self.assertIn("water-dependent", correct_choice_text(questions[5]))
        self.assertIn("seldom wander far", correct_choice_text(questions[5]))
        self.assertIn("bark or snort", correct_choice_text(questions[6]))
        self.assertIn("Brownish", correct_choice_text(questions[7]))
        self.assertIn("darken", correct_choice_text(questions[7]))
        self.assertIn("shadow", correct_choice_text(questions[8]).lower())
        self.assertIn("southern", correct_choice_text(questions[8]).lower())
        self.assertIn("Hunting and habitat loss", correct_choice_text(questions[9]))
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("zebra", "hard")
        easy = study_deck_for("zebra", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "zebra", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("<details class=\"study-teach\">", html)
        self.assertNotIn("<details class=\"study-teach\" open", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertEqual(html.count('role="group"'), 2)
        self.assertIn("study-level-picker-bottom", html)
        self.assertIn('aria-label="Study level at the end"', html)
        for stem in HARD_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_hard_print_is_answer_light_duplex(self):
        deck = study_deck_for("zebra", "hard")
        sheet = study_print_html(
            deck,
            name="Zebra",
            emoji="🦓",
            photo="/field-pack/photos/zebra.jpg?v=img2",
            photo_pos="50% 22%",
        )
        self.assertIn("Park Ranger", sheet)
        self.assertNotIn("Junior Ranger", sheet)
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
        for prompt in TALK_ABOUT_ZEBRA + PUSH_FURTHER_ZEBRA:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_PLAINS_ZEBRA, sheet)
        self.assertIn("Facts from Wikipedia, Plains zebra.", sheet)
        for stem in HARD_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS:
            self.assertNotIn(stem, sheet)

    def test_other_animal_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_hard = study_deck_for("african-lion", "hard")
        self.assertEqual(lion_hard["source"], WIKI_LION)
        self.assertIn("Panthera leo", correct_choice_text(lion_hard["questions"][0]))
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)
        self.assertEqual(lion_hard["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion_hard["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        giraffe_hard = study_deck_for("reticulated-giraffe", "hard")
        self.assertEqual(giraffe_hard["source"], WIKI_GIRAFFE)
        self.assertIn("okapi", correct_choice_text(giraffe_hard["questions"][0]))
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giraffe_html)
        self.assertIn("Junior Ranger", giraffe_html)
        self.assertIn("Park Ranger", giraffe_html)
        self.assertEqual(giraffe_hard["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_hard["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_hard = study_deck_for("african-elephant", "hard")
        self.assertEqual(elephant_hard["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Tens of thousands", correct_choice_text(elephant_hard["questions"][0]))
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertIn("Junior Ranger", elephant_html)
        self.assertIn("Park Ranger", elephant_html)
        self.assertEqual(elephant_hard["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_hard["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        penguin_hard = study_deck_for("african-penguin", "hard")
        self.assertEqual(penguin_hard["source"], WIKI_AFRICAN_PENGUIN)
        self.assertIn("Lose heat", correct_choice_text(penguin_hard["questions"][0]))
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", penguin_html)
        self.assertIn("Junior Ranger", penguin_html)
        self.assertIn("Park Ranger", penguin_html)
        self.assertEqual(penguin_hard["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin_hard["push_further"], list(PUSH_FURTHER_PENGUIN))
        self.assertEqual(shipped_levels_for("caribbean-flamingo"), ("easy", "hard", "zoologist"))
        flamingo_hard = study_deck_for("caribbean-flamingo", "hard")
        self.assertEqual(flamingo_hard["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertIn("Carotenoid pigments", correct_choice_text(flamingo_hard["questions"][0]))
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", flamingo_html)
        self.assertIn("Junior Ranger", flamingo_html)
        self.assertIn("Park Ranger", flamingo_html)
        self.assertEqual(flamingo_hard["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(flamingo_hard["push_further"], list(PUSH_FURTHER_FLAMINGO))
        self.assertEqual(shipped_levels_for("galapagos-tortoise"), ("easy", "hard", "zoologist"))
        tortoise_hard = study_deck_for("galapagos-tortoise", "hard")
        self.assertEqual(tortoise_hard["source"], WIKI_GALAPAGOS_TORTOISE)
        self.assertIn("Domed and saddleback", correct_choice_text(tortoise_hard["questions"][0]))
        tortoise_html = TORTOISE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", tortoise_html)
        self.assertIn("Junior Ranger", tortoise_html)
        self.assertIn("Park Ranger", tortoise_html)
        self.assertEqual(tortoise_hard["talk_about"], list(TALK_ABOUT_TORTOISE))
        self.assertEqual(tortoise_hard["push_further"], list(PUSH_FURTHER_TORTOISE))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["zebra"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["zebra"]["levels"])
        self.assertEqual(payload["zebra"]["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("zebra", data_js)
        self.assertIn("fly-stripe", data_js)
        self.assertIn("shadow-stripes", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = ZEBRA.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn("Learn first", html)
        self.assertIn("Watch Live", html)
        self.assertIn('class="card-hero-links no-print"', html)
        self.assertIn('class="card-try-next no-print"', html)
        self.assertIn("study-level-picker-bottom", html)
        self.assertNotIn("card-print-note", html)
        self.assertNotIn("One animal sheet — not the hide-and-seek cutouts", html)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertIn("Learn first", print_tpl)
        self.assertNotIn("Park Ranger", print_tpl)
        for stem in HARD_STEMS:
            self.assertNotIn(stem, print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        hard_html = study_talk_html(study_deck_for("zebra", "hard"))
        self.assertNotIn("study-teach", hard_html)
        self.assertIn('<details class="study-explore', hard_html)
        self.assertIn("Explore more", hard_html)
        self.assertIn("Talk about it", hard_html)
        self.assertIn("Push further", hard_html)
        self.assertIn("Park Ranger", hard_html)
        self.assertIn("Junior Ranger", hard_html)
        self.assertIn("Zoologist", hard_html)


if __name__ == "__main__":
    unittest.main()
