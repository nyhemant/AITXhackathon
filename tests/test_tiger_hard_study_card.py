"""Sumatran tiger Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    correct_choice_text,
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_FLAMINGO,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_HIPPO,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PENGUIN,
    PUSH_FURTHER_TIGER,
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_ZEBRA,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_HIPPO,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_TIGER,
    TALK_ABOUT_TORTOISE,
    TALK_ABOUT_ZEBRA,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
    WIKI_GALAPAGOS_TORTOISE,
    WIKI_GIRAFFE,
    WIKI_HIPPOPOTAMUS,
    WIKI_LION,
    WIKI_PLAINS_ZEBRA,
    WIKI_SUMATRAN_TIGER,
    level_display_name,
    shipped_levels_for,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
TIGER = FP / "cards" / "sumatran-tiger" / "index.html"
HIPPO = FP / "cards" / "nile-hippo" / "index.html"
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
    "Why do Sumatran tigers need thick cover on the forest floor?",
    "Which kind of land do Sumatran tigers use most?",
    "What kinds of animals do Sumatran tigers usually hunt in the forest?",
    "How is Sumatran tiger habitat spread across the island?",
    "What puts wild Sumatran tigers under pressure today?",
    "Across what kinds of forest can wild Sumatran tigers live?",
    "How does a tiger usually catch its prey?",
    "What kind of forest do Sumatran tigers need to thrive?",
    "What happens near the ends of a Sumatran tiger’s stripes?",
    "Where do the largest groups of wild Sumatran tigers live?",
)

HARD_IDS = (
    "understory",
    "natural-forest",
    "forest-prey",
    "fragments",
    "threats",
    "sea-to-mountains",
    "ambush",
    "forest-blocks",
    "stripe-tips",
    "park-strongholds",
)

EASY_STEMS = (
    "Where do wild Sumatran tigers live?",
    "How does a Sumatran tiger’s size compare with other living tigers?",
    "What is special about a Sumatran tiger’s stripes?",
    "What kind of place do Sumatran tigers prefer?",
    "What do wild Sumatran tigers hunt?",
    "How do Sumatran tigers usually live?",
    "What do you call a baby Sumatran tiger?",
    "What extra fur can a male Sumatran tiger show?",
    "Why is the Sumatran tiger called the last Sunda island tiger?",
    "Are Sumatran tigers scared of water, like a cartoon house cat?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Critically Endangered",
    "Endangered",
    "sondaica",
    "Sondaica",
    "palm oil",
    "Palm oil",
    "oil palm",
    "studbook",
    "inbreeding",
    "618",
    "1,000",
    "1000",
    "kg",
    "kilogram",
    "220",
    "310",
    "CITES",
    "Appendix",
    "webbing",
    "3,200",
    "3200",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class TigerHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("sumatran-tiger"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("sumatran-tiger", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("sumatran-tiger", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_SUMATRAN_TIGER)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Sumatran tiger.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_TIGER))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_TIGER))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("sumatran-tiger", "easy")
        hard = study_deck_for("sumatran-tiger", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("sumatran-tiger", "hard")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(HARD_IDS))
        self.assertEqual([q["stem"] for q in questions], list(HARD_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("understory cover", correct_choice_text(questions[0]))
        self.assertIn("more exposed", correct_choice_text(questions[0]))
        self.assertIn("uncultivated forest", correct_choice_text(questions[1]))
        self.assertIn("little use of plantations", correct_choice_text(questions[1]))
        self.assertIn("mid-sized forest mammals", correct_choice_text(questions[2]))
        self.assertIn("scattered habitat patches", correct_choice_text(questions[3]))
        self.assertIn("Habitat loss", correct_choice_text(questions[4]))
        self.assertIn("snares", correct_choice_text(questions[4]))
        self.assertIn("coastal lowland", correct_choice_text(questions[5]))
        self.assertIn("high mountain forest", correct_choice_text(questions[5]))
        self.assertIn("ambush", correct_choice_text(questions[6]))
        self.assertIn("long open chase", correct_choice_text(questions[6]))
        self.assertIn("Large connected forest", correct_choice_text(questions[7]))
        self.assertIn("edges", correct_choice_text(questions[7]))
        self.assertIn("dissolve into spots", correct_choice_text(questions[8]))
        self.assertIn("small dark spots", correct_choice_text(questions[8]))
        self.assertIn("major national parks", correct_choice_text(questions[9]))
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("sumatran-tiger", "hard")
        easy = study_deck_for("sumatran-tiger", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "sumatran-tiger", "packTemplate": "animals"})
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
        deck = study_deck_for("sumatran-tiger", "hard")
        sheet = study_print_html(
            deck,
            name="Sumatran tiger",
            emoji="🐯",
            photo="/field-pack/photos/sumatran-tiger.jpg?v=img2",
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
        for prompt in TALK_ABOUT_TIGER + PUSH_FURTHER_TIGER:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_SUMATRAN_TIGER, sheet)
        self.assertIn("Facts from Wikipedia, Sumatran tiger.", sheet)
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
        self.assertEqual(shipped_levels_for("zebra"), ("easy", "hard", "zoologist"))
        zebra_hard = study_deck_for("zebra", "hard")
        self.assertEqual(zebra_hard["source"], WIKI_PLAINS_ZEBRA)
        self.assertIn("deter biting flies", correct_choice_text(zebra_hard["questions"][0]))
        zebra_html = ZEBRA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", zebra_html)
        self.assertIn("Junior Ranger", zebra_html)
        self.assertIn("Park Ranger", zebra_html)
        self.assertEqual(zebra_hard["talk_about"], list(TALK_ABOUT_ZEBRA))
        self.assertEqual(zebra_hard["push_further"], list(PUSH_FURTHER_ZEBRA))
        self.assertEqual(shipped_levels_for("nile-hippo"), ("easy", "hard", "zoologist"))
        hippo_hard = study_deck_for("nile-hippo", "hard")
        self.assertEqual(hippo_hard["source"], WIKI_HIPPOPOTAMUS)
        self.assertIn("walk or bounce", correct_choice_text(hippo_hard["questions"][0]))
        hippo_html = HIPPO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", hippo_html)
        self.assertIn("Junior Ranger", hippo_html)
        self.assertIn("Park Ranger", hippo_html)
        self.assertEqual(hippo_hard["talk_about"], list(TALK_ABOUT_HIPPO))
        self.assertEqual(hippo_hard["push_further"], list(PUSH_FURTHER_HIPPO))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["sumatran-tiger"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["sumatran-tiger"]["levels"])
        self.assertEqual(payload["sumatran-tiger"]["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("sumatran-tiger", data_js)
        self.assertIn("understory", data_js)
        self.assertIn("park-strongholds", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = TIGER.read_text(encoding="utf-8")
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
        hard_html = study_talk_html(study_deck_for("sumatran-tiger", "hard"))
        self.assertNotIn("study-teach", hard_html)
        self.assertIn('<details class="study-explore', hard_html)
        self.assertIn("Explore more", hard_html)
        self.assertLess(hard_html.find("study-foot"), hard_html.find("study-explore"))
        self.assertIn("Talk about it", hard_html)
        self.assertIn("Push further", hard_html)
        self.assertIn("Park Ranger", hard_html)
        self.assertIn("Junior Ranger", hard_html)
        self.assertIn("Zoologist", hard_html)


if __name__ == "__main__":
    unittest.main()
