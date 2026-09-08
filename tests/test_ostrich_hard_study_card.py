"""Ostrich Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_CHEETAH,
    PUSH_FURTHER_CHIMPANZEE,
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_GIANT_PANDA,
    PUSH_FURTHER_GORILLA,
    PUSH_FURTHER_KOALA,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_ORANGUTAN,
    PUSH_FURTHER_OSTRICH,
    PUSH_FURTHER_RED_PANDA,
    PUSH_FURTHER_RING_TAILED_LEMUR,
    STUDY_SLOTS,
    TALK_ABOUT_CHEETAH,
    TALK_ABOUT_CHIMPANZEE,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_GIANT_PANDA,
    TALK_ABOUT_GORILLA,
    TALK_ABOUT_KOALA,
    TALK_ABOUT_LION,
    TALK_ABOUT_ORANGUTAN,
    TALK_ABOUT_OSTRICH,
    TALK_ABOUT_RED_PANDA,
    TALK_ABOUT_RING_TAILED_LEMUR,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_CHEETAH,
    WIKI_CHIMPANZEE,
    WIKI_GIRAFFE,
    WIKI_GIANT_PANDA,
    WIKI_KOALA,
    WIKI_LION,
    WIKI_ORANGUTAN,
    WIKI_OSTRICH,
    WIKI_RED_PANDA,
    WIKI_RING_TAILED_LEMUR,
    WIKI_WESTERN_LOWLAND_GORILLA,
    correct_choice_text,
    level_display_name,
    shipped_levels_for,
    study_deck_for,
    study_print_html,
    study_talk_html,
    target_letter_for_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
OSTRICH = FP / "cards" / "ostrich" / "index.html"
LEMUR = FP / "cards" / "ring-tailed-lemur" / "index.html"
GIANT_PANDA = FP / "cards" / "giant-panda" / "index.html"
ORANGUTAN = FP / "cards" / "orangutan" / "index.html"
CHIMPANZEE = FP / "cards" / "chimpanzee" / "index.html"
KOALA = FP / "cards" / "koala" / "index.html"
RED_PANDA = FP / "cards" / "red-panda" / "index.html"
CHEETAH = FP / "cards" / "cheetah" / "index.html"
GORILLA = FP / "cards" / "western-lowland-gorilla" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

HARD_STEMS = (
    "How many toes does an ostrich have on each foot, and why does that help?",
    "How fast can an ostrich sprint, and can it keep a strong pace?",
    "If an ostrich is cornered, how can its strong legs help it defend itself?",
    "How does a territorial male ostrich show off to attract mates?",
    "Where do ostrich eggs go, and who may add eggs to the nest?",
    "Who usually sits on the nest by day and by night, and why do those colors help?",
    "Why are ostrich feathers soft, and what do the wings help with?",
    "Why do ostriches swallow pebbles?",
    "How have wild ostrich numbers changed, and where do many ostriches live now?",
    "Who might ostriches travel with on the grassland?",
)

HARD_IDS = (
    "two-toe-runners",
    "burst-speed-soft",
    "forward-kick",
    "boom-show",
    "shared-pit-nest",
    "day-night-sit",
    "fluffy-not-flight",
    "pebble-grinders",
    "need-our-help-soft",
    "travel-buddies-soft",
)

EASY_STEMS = (
    "What kind of living bird is the ostrich?",
    "Can ostriches fly?",
    "Where do wild ostriches live?",
    "How do a long neck and long legs help an ostrich?",
    "How can you often tell a male ostrich from a female?",
    "What do ostriches eat first?",
    "What is special about an ostrich egg?",
    "What is a baby ostrich called, and what does it look like?",
    "How are wild ostriches doing today?",
    "Do ostriches bury their heads in the sand?",
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
    "Struthio",
    "camelus",
    "Somali",
    "Arabian",
    "ratite",
    "keel",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "Somali",
    "Arabian",
    "ratite",
    "keel",
    "Least Concern",
    "IUCN",
    "CITES",
    "eye mm",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class OstrichHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("ostrich"), ("easy", "hard"))
        self.assertIsNone(study_deck_for("ostrich", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("ostrich", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_OSTRICH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Ostrich.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_OSTRICH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_OSTRICH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("ostrich", "easy")
        hard = study_deck_for("ostrich", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("ostrich", "hard")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(HARD_IDS))
        self.assertEqual([q["stem"] for q in questions], list(HARD_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("two toes", correct_choice_text(questions[0]).lower())
        self.assertIn("running", correct_choice_text(questions[0]).lower())
        self.assertIn("four", questions[0]["why"].lower())
        self.assertIn("car in town", correct_choice_text(questions[1]).lower())
        self.assertIn("steady pace", correct_choice_text(questions[1]).lower())
        self.assertIn("speed numbers stay soft", questions[1]["why"].lower())
        self.assertIn("kick forward", correct_choice_text(questions[2]).lower())
        self.assertIn("defense", correct_choice_text(questions[2]).lower())
        self.assertIn("boom", correct_choice_text(questions[3]).lower())
        self.assertIn("wings", correct_choice_text(questions[3]).lower())
        self.assertIn("shallow ground pit", correct_choice_text(questions[4]).lower())
        self.assertIn("more than one hen", correct_choice_text(questions[4]).lower())
        self.assertIn("females often sit by day", correct_choice_text(questions[5]).lower())
        self.assertIn("males by night", correct_choice_text(questions[5]).lower())
        self.assertIn("tiny hooks", correct_choice_text(questions[6]).lower())
        self.assertIn("balance", correct_choice_text(questions[6]).lower())
        self.assertIn("pebbles", correct_choice_text(questions[7]).lower())
        self.assertIn("gizzard", correct_choice_text(questions[7]).lower())
        self.assertIn("200 years", correct_choice_text(questions[8]))
        self.assertIn("farms", correct_choice_text(questions[8]).lower())
        self.assertIn("reserves", correct_choice_text(questions[8]).lower())
        self.assertIn("status letter", questions[8]["why"].lower())
        self.assertIn("zebras", correct_choice_text(questions[9]).lower())
        self.assertIn("antelope", correct_choice_text(questions[9]).lower())
        self.assertIn("group sizes soft", questions[9]["why"].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("ostrich", "hard")
        easy = study_deck_for("ostrich", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "ostrich", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn('<details class="study-teach">', html)
        self.assertNotIn('<details class="study-teach" open', html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertNotIn("Zoologist", html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertNotIn('data-study-pick="zoologist"', html)
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
        deck = study_deck_for("ostrich", "hard")
        sheet = study_print_html(
            deck,
            name="Ostrich",
            emoji="🪶",
            photo="/field-pack/photos/ostrich.jpg?v=img2",
            photo_pos="50% 15%",
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
        for prompt in TALK_ABOUT_OSTRICH + PUSH_FURTHER_OSTRICH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_OSTRICH, sheet)
        self.assertIn("Facts from Wikipedia, Ostrich.", sheet)
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
        self.assertEqual(giraffe_hard["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_hard["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_hard = study_deck_for("african-elephant", "hard")
        self.assertEqual(elephant_hard["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Tens of thousands", correct_choice_text(elephant_hard["questions"][0]))
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertEqual(elephant_hard["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_hard["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("western-lowland-gorilla"), ("easy", "hard", "zoologist"))
        gorilla_hard = study_deck_for("western-lowland-gorilla", "hard")
        self.assertEqual(gorilla_hard["source"], WIKI_WESTERN_LOWLAND_GORILLA)
        gorilla_html = GORILLA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", gorilla_html)
        self.assertEqual(gorilla_hard["talk_about"], list(TALK_ABOUT_GORILLA))
        self.assertEqual(gorilla_hard["push_further"], list(PUSH_FURTHER_GORILLA))
        self.assertEqual(shipped_levels_for("cheetah"), ("easy", "hard", "zoologist"))
        cheetah_hard = study_deck_for("cheetah", "hard")
        self.assertEqual(cheetah_hard["source"], WIKI_CHEETAH)
        cheetah_html = CHEETAH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", cheetah_html)
        self.assertEqual(cheetah_hard["talk_about"], list(TALK_ABOUT_CHEETAH))
        self.assertEqual(cheetah_hard["push_further"], list(PUSH_FURTHER_CHEETAH))
        self.assertEqual(shipped_levels_for("red-panda"), ("easy", "hard", "zoologist"))
        panda_hard = study_deck_for("red-panda", "hard")
        self.assertEqual(panda_hard["source"], WIKI_RED_PANDA)
        panda_html = RED_PANDA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", panda_html)
        self.assertEqual(panda_hard["talk_about"], list(TALK_ABOUT_RED_PANDA))
        self.assertEqual(panda_hard["push_further"], list(PUSH_FURTHER_RED_PANDA))
        self.assertEqual(shipped_levels_for("koala"), ("easy", "hard", "zoologist"))
        koala_hard = study_deck_for("koala", "hard")
        self.assertEqual(koala_hard["source"], WIKI_KOALA)
        koala_html = KOALA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", koala_html)
        self.assertEqual(koala_hard["talk_about"], list(TALK_ABOUT_KOALA))
        self.assertEqual(koala_hard["push_further"], list(PUSH_FURTHER_KOALA))
        self.assertEqual(shipped_levels_for("chimpanzee"), ("easy", "hard", "zoologist"))
        chimp_hard = study_deck_for("chimpanzee", "hard")
        self.assertEqual(chimp_hard["source"], WIKI_CHIMPANZEE)
        chimp_html = CHIMPANZEE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", chimp_html)
        self.assertEqual(chimp_hard["talk_about"], list(TALK_ABOUT_CHIMPANZEE))
        self.assertEqual(chimp_hard["push_further"], list(PUSH_FURTHER_CHIMPANZEE))
        self.assertEqual(shipped_levels_for("orangutan"), ("easy", "hard", "zoologist"))
        orang_hard = study_deck_for("orangutan", "hard")
        self.assertEqual(orang_hard["source"], WIKI_ORANGUTAN)
        orang_html = ORANGUTAN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", orang_html)
        self.assertEqual(orang_hard["talk_about"], list(TALK_ABOUT_ORANGUTAN))
        self.assertEqual(orang_hard["push_further"], list(PUSH_FURTHER_ORANGUTAN))
        self.assertEqual(shipped_levels_for("giant-panda"), ("easy", "hard", "zoologist"))
        giant_hard = study_deck_for("giant-panda", "hard")
        self.assertEqual(giant_hard["source"], WIKI_GIANT_PANDA)
        giant_html = GIANT_PANDA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giant_html)
        self.assertEqual(giant_hard["talk_about"], list(TALK_ABOUT_GIANT_PANDA))
        self.assertEqual(giant_hard["push_further"], list(PUSH_FURTHER_GIANT_PANDA))
        self.assertEqual(shipped_levels_for("ring-tailed-lemur"), ("easy", "hard", "zoologist"))
        lemur_hard = study_deck_for("ring-tailed-lemur", "hard")
        self.assertEqual(lemur_hard["source"], WIKI_RING_TAILED_LEMUR)
        lemur_html = LEMUR.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lemur_html)
        self.assertEqual(lemur_hard["talk_about"], list(TALK_ABOUT_RING_TAILED_LEMUR))
        self.assertEqual(lemur_hard["push_further"], list(PUSH_FURTHER_RING_TAILED_LEMUR))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["ostrich"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertNotIn("zoologist", payload["ostrich"]["levels"])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("ostrich", data_js)
        self.assertIn("two-toe-runners", data_js)
        self.assertIn("travel-buddies-soft", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = OSTRICH.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertNotIn("Zoologist", html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertNotIn('data-study-pick="zoologist"', html)
        self.assertIn("Learn first", html)
        self.assertNotIn("Watch Live", html)
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
        hard_html = study_talk_html(study_deck_for("ostrich", "hard"))
        self.assertNotIn("study-teach", hard_html)
        self.assertIn('<details class="study-explore', hard_html)
        self.assertIn("Explore more", hard_html)
        self.assertLess(hard_html.find("study-foot"), hard_html.find("study-explore"))
        self.assertIn("Talk about it", hard_html)
        self.assertIn("Push further", hard_html)
        self.assertIn("Park Ranger", hard_html)
        self.assertIn("Junior Ranger", hard_html)
        self.assertNotIn("Zoologist", hard_html)


if __name__ == "__main__":
    unittest.main()
