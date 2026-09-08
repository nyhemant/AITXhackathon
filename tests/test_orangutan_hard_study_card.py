"""Orangutan Hard study-card: Park Ranger, no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_GORILLA,
    PUSH_FURTHER_KOALA,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_ORANGUTAN,
    PUSH_FURTHER_RED_PANDA,
    STUDY_SLOTS,
    TALK_ABOUT_CHEETAH,
    TALK_ABOUT_CHIMPANZEE,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_GORILLA,
    TALK_ABOUT_KOALA,
    TALK_ABOUT_LION,
    TALK_ABOUT_ORANGUTAN,
    TALK_ABOUT_RED_PANDA,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_CHEETAH,
    WIKI_CHIMPANZEE,
    WIKI_GIRAFFE,
    WIKI_KOALA,
    WIKI_LION,
    WIKI_ORANGUTAN,
    WIKI_RED_PANDA,
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
    "What do big adult males use booming long calls for?",
    "How do orangutans make their nests, and how do young ones learn?",
    "How long do orangutan moms and babies stay close?",
    "How much of the day do orangutans spend in the trees?",
    "What puts wild orangutans under pressure today?",
    "What may orangutans do with leafy branches in the rain?",
    "How do an orangutan’s fingers and feet help it hang in the trees?",
    "How do orangutan home ranges work, even though they live mostly alone?",
    "What extra nest do orangutans often build besides the night nest?",
    "How do adult males compare in size with adult females?",
)

HARD_IDS = (
    "long-call-boom",
    "nest-craft",
    "long-childhood",
    "canopy-specialist",
    "threats-soft",
    "rain-leaf-cover",
    "hook-grip",
    "overlapping-homes",
    "day-rest-nest",
    "bigger-males",
)

EASY_STEMS = (
    "What does the name “orangutan” mean?",
    "Where do wild orangutans live?",
    "What does an orangutan’s coat look like?",
    "How are an orangutan’s arms built for tree life?",
    "What is the most important food for wild orangutans?",
    "How do orangutans usually live, compared with other great apes?",
    "Where does an orangutan usually sleep at night?",
    "What is a quick clue that an orangutan is a great ape, not a monkey?",
    "What extra face feature do many big adult males grow?",
    "Are orangutans African apes?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Vulnerable",
    "Endangered",
    "Critically",
    "Tapanuli",
    "Pongo",
    "pygmaeus",
    "abelii",
    "bimaturism",
    "throat-sac",
    "throat sac",
    "palm oil",
    "palm-oil",
    "kg",
    "cm",
)
RESERVED = (
    "Tapanuli",
    "Critically Endangered",
    "bimaturism",
    "three-species",
    "three species",
    "subspecies",
    "tool-culture",
    "tool culture",
    "palm oil",
    "palm-oil",
    "Endangered",
    "throat pouch",
    "resonance",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class OrangutanHardStudyCardTests(unittest.TestCase):
    def test_hard_deck_is_park_ranger_without_teach(self):
        self.assertEqual(shipped_levels_for("orangutan"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("orangutan", "zoologist"))
        self.assertEqual(level_display_name("hard"), "Park Ranger")
        deck = study_deck_for("orangutan", "hard")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "hard")
        self.assertEqual(deck["level_label"], "Park Ranger")
        self.assertEqual(deck["source"], WIKI_ORANGUTAN)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Orangutan.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_ORANGUTAN))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_ORANGUTAN))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_only_for_hard(self):
        easy = study_deck_for("orangutan", "easy")
        hard = study_deck_for("orangutan", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        broken_easy = dict(easy)
        broken_easy["teach"] = []
        self.assertIn("teach strip empty", validate_deck(broken_easy))
        broken_hard = dict(hard)
        broken_hard["teach"] = ["A leftover teach line."]
        self.assertIn("hard deck must not include a teach strip", validate_deck(broken_hard))

    def test_hard_slots_and_copy_are_locked(self):
        deck = study_deck_for("orangutan", "hard")
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
        self.assertIn("attract females", correct_choice_text(questions[0]).lower())
        self.assertIn("warn rival", correct_choice_text(questions[0]).lower())
        self.assertIn("later", questions[0]["why"].lower())
        self.assertIn("watching mom", correct_choice_text(questions[1]).lower())
        self.assertIn("branches and leaves", correct_choice_text(questions[1]).lower())
        self.assertIn("longest mother", correct_choice_text(questions[2]).lower())
        self.assertIn("ages soft", questions[2]["why"].lower())
        self.assertIn("arboreal", correct_choice_text(questions[3]).lower())
        self.assertIn("percent", questions[3]["why"].lower())
        self.assertIn("Habitat loss", correct_choice_text(questions[4]))
        self.assertIn("pet trade", correct_choice_text(questions[4]).lower())
        self.assertIn("status letter", questions[4]["why"].lower())
        self.assertIn("umbrella", correct_choice_text(questions[5]).lower())
        self.assertIn("later", questions[5]["why"].lower())
        self.assertIn("hooks", correct_choice_text(questions[6]).lower())
        self.assertIn("overlap", correct_choice_text(questions[7]).lower())
        self.assertIn("day nest", correct_choice_text(questions[8]).lower())
        self.assertIn("larger and heavier", correct_choice_text(questions[9]).lower())
        self.assertIn("exact weights", questions[9]["why"].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)

    def test_hard_does_not_redo_easy_stems(self):
        hard = study_deck_for("orangutan", "hard")
        easy = study_deck_for("orangutan", "easy")
        hard_stems = [q["stem"] for q in hard["questions"]]
        easy_stems = [q["stem"] for q in easy["questions"]]
        self.assertEqual(easy_stems, list(EASY_STEMS))
        for stem in EASY_STEMS:
            self.assertNotIn(stem, hard_stems)

    def test_default_screen_html_keeps_easy_and_adds_picker(self):
        html = outing_talk_html({"id": "orangutan", "packTemplate": "animals"})
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
        deck = study_deck_for("orangutan", "hard")
        sheet = study_print_html(
            deck,
            name="Orangutan",
            emoji="🦧",
            photo="/field-pack/photos/orangutan.jpg?v=img2",
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
        for prompt in TALK_ABOUT_ORANGUTAN + PUSH_FURTHER_ORANGUTAN:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_ORANGUTAN, sheet)
        self.assertIn("Facts from Wikipedia, Orangutan.", sheet)
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

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        hard = payload["orangutan"]["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in hard["questions"]], list(HARD_IDS))
        self.assertIn("zoologist", payload["orangutan"]["levels"])
        self.assertEqual(payload["orangutan"]["levels"]["zoologist"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("orangutan", data_js)
        self.assertIn("long-call-boom", data_js)
        self.assertIn("bigger-males", data_js)
        self.assertIn("talk_about", data_js)
        self.assertIn("push_further", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("data-study-pick", js)
        self.assertIn("levelFromQuery", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function selectedStudyLevel", print_js)
        html = ORANGUTAN.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-pick="zoologist"', html)
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
        hard_html = study_talk_html(study_deck_for("orangutan", "hard"))
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
