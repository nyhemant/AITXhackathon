"""Shark Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_FLAMINGO,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_GIANT_PANDA,
    PUSH_FURTHER_GORILLA,
    PUSH_FURTHER_HIPPO,
    PUSH_FURTHER_KOALA,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_ORANGUTAN,
    PUSH_FURTHER_OSTRICH,
    PUSH_FURTHER_PENGUIN,
    PUSH_FURTHER_RED_PANDA,
    PUSH_FURTHER_RING_TAILED_LEMUR,
    PUSH_FURTHER_SHARK,
    PUSH_FURTHER_TIGER,
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_WARTHOG,
    PUSH_FURTHER_ZEBRA,
    STUDY_SLOTS,
    TALK_ABOUT_CHEETAH,
    TALK_ABOUT_CHIMPANZEE,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_GIANT_PANDA,
    TALK_ABOUT_GORILLA,
    TALK_ABOUT_HIPPO,
    TALK_ABOUT_KOALA,
    TALK_ABOUT_LION,
    TALK_ABOUT_ORANGUTAN,
    TALK_ABOUT_OSTRICH,
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_RED_PANDA,
    TALK_ABOUT_RING_TAILED_LEMUR,
    TALK_ABOUT_SHARK,
    TALK_ABOUT_TIGER,
    TALK_ABOUT_TORTOISE,
    TALK_ABOUT_WARTHOG,
    TALK_ABOUT_ZEBRA,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
    WIKI_CHEETAH,
    WIKI_CHIMPANZEE,
    WIKI_GALAPAGOS_TORTOISE,
    WIKI_GIANT_PANDA,
    WIKI_GIRAFFE,
    WIKI_HIPPOPOTAMUS,
    WIKI_KOALA,
    WIKI_LION,
    WIKI_ORANGUTAN,
    WIKI_OSTRICH,
    WIKI_PLAINS_ZEBRA,
    WIKI_RED_PANDA,
    WIKI_RING_TAILED_LEMUR,
    WIKI_SHARK,
    WIKI_SUMATRAN_TIGER,
    WIKI_WARTHOG,
    WIKI_WESTERN_LOWLAND_GORILLA,
    correct_choice_text,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_talk_html,
    target_letter_for_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
SHARK = FP / "cards" / "shark" / "index.html"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
WARTHOG = FP / "cards" / "warthog" / "index.html"
OSTRICH = FP / "cards" / "ostrich" / "index.html"
LEMUR = FP / "cards" / "ring-tailed-lemur" / "index.html"
GIANT_PANDA = FP / "cards" / "giant-panda" / "index.html"
ORANGUTAN = FP / "cards" / "orangutan" / "index.html"
CHIMPANZEE = FP / "cards" / "chimpanzee" / "index.html"
KOALA = FP / "cards" / "koala" / "index.html"
RED_PANDA = FP / "cards" / "red-panda" / "index.html"
CHEETAH = FP / "cards" / "cheetah" / "index.html"
GORILLA = FP / "cards" / "western-lowland-gorilla" / "index.html"
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

ZOOLOGIST_STEMS = (
    "Where do modern sharks sit among cartilaginous fishes?",
    "What living group is the sister group to modern sharks?",
    "How far back do shark-like fishes go in the fossil record?",
    "About how many living kinds of shark are there?",
    "Can we give every shark the same Red List letter?",
    "What have studies reported about some oceanic sharks and rays since about 1970?",
    "How do finning and trade rules like CITES affect sharks?",
    "In some live-bearing sharks, what may pups do inside the mother?",
    "How do many sharks keep their body fluids in balance with salty seawater?",
    "An oily liver helps sharks with buoyancy. Why do many still need to keep moving?",
)

ZOOLOGIST_IDS = (
    "selachii-soft",
    "sister-to-batoids",
    "deep-time-soft",
    "hundreds-of-kinds-soft",
    "status-by-kind",
    "ocean-declines-soft",
    "finning-cites-soft",
    "oophagy-soft",
    "urea-salt-soft",
    "dynamic-lift-soft",
)

HARD_STEMS = (
    "How do jelly-filled pores on a shark’s snout help it find other animals?",
    "Sharks have no gas swim bladder like many bony fish. What helps them with buoyancy?",
    "How do many sharks get water over their gills?",
    "Do most kinds of shark have to keep swimming, or they cannot breathe?",
    "How do sharks have their young?",
    "Why do shark teeth come in different shapes?",
    "What is the small opening some sharks have just behind the eye?",
    "Which animals are sharks most closely related to?",
    "Why do many kinds of shark need our help today?",
    "Where should you learn about huge filter-feeders like the whale shark?",
)

EASY_STEMS = (
    "What are a shark’s “bones” made of?",
    "Why can shark skin feel rough, like sandpaper?",
    "Where do most sharks live?",
    "What do most sharks eat?",
    "How do sharks breathe?",
    "How is a shark’s body built for moving?",
    "What happens to a shark’s teeth over time?",
    "What extra sense can sharks use to find other animals?",
    "How are sharks doing in the wild today?",
    "Are most sharks the movie “man-eaters” people imagine?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "71%",
    "71 percent",
    "100 million",
    "100million",
    "470",
    "500 species",
    "419",
    "359",
    "2.5%",
    "30%",
    "squalene",
    "Vulnerable",
    "Endangered",
    "Critically",
    "Least Concern",
    "Carcharodon",
)
REDO_THEMES = (
    "Soft cartilage, not hard bone",
    "dermal denticles",
    "most kinds do not live in fresh water",
    "Meat or fish — though diets differ by kind",
    "often about five to seven",
    "A strong swishy body and fins for swimming",
    "get replaced again and again",
    "weak electric fields from other animals",
    "Fishing and finning can hurt many kinds",
    "most are not dangerous to people",
    "ampullae of Lorenzini",
    "A big oily liver helps them stay buoyant",
    "ram ventilation",
    "only a small number of kinds must keep swimming",
    "Some lay egg cases; others give live birth",
    "cutters, grippers, or crushers",
    "A spiracle that helps take in water",
    "they are cartilage fishes together",
    "Overfishing and finning put many kinds at risk",
    "whale-shark card",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class SharkZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("shark"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        self.assertIn("whale-shark", study_card_ids())
        self.assertIsNotNone(study_deck_for("whale-shark", "hard"))
        self.assertIsNotNone(study_deck_for("whale-shark", "zoologist"))
        deck = study_deck_for("shark", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_SHARK)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Shark.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_SHARK))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_SHARK))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("shark", "zoologist")
        easy = study_deck_for("shark", "easy")
        hard = study_deck_for("shark", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("shark", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Selachii", correct_choice_text(questions[0]))
        self.assertIn("Chondrichthyes", correct_choice_text(questions[0]))
        self.assertIn("division", correct_choice_text(questions[0]).lower())
        self.assertIn("Batomorphi", correct_choice_text(questions[1]))
        self.assertIn("sister", correct_choice_text(questions[1]).lower())
        self.assertIn("Selachii", correct_choice_text(questions[1]))
        self.assertIn("Devonian", correct_choice_text(questions[2]))
        self.assertIn("fossil", questions[2]["stem"].lower() + questions[2]["why"].lower())
        self.assertIn("stay soft", questions[2]["why"].lower())
        self.assertIn("Hundreds", correct_choice_text(questions[3]))
        self.assertIn("families", correct_choice_text(questions[3]).lower())
        self.assertIn("keep the number soft", questions[3]["why"].lower())
        self.assertIn("each kind", correct_choice_text(questions[4]).lower())
        self.assertIn("group card", correct_choice_text(questions[4]).lower())
        self.assertIn("snapshot", questions[4]["why"].lower())
        self.assertNotIn("Vulnerable", correct_choice_text(questions[4]))
        self.assertNotIn("Endangered", correct_choice_text(questions[4]))
        self.assertIn("big drops", correct_choice_text(questions[5]).lower())
        self.assertIn("1970", questions[5]["stem"])
        self.assertIn("percents stay soft", questions[5]["why"].lower())
        self.assertIn("CITES", questions[6]["stem"])
        self.assertIn("CITES", questions[6]["why"])
        self.assertIn("many kinds", correct_choice_text(questions[6]).lower())
        self.assertIn("snapshot", questions[6]["why"].lower())
        self.assertIn("eggs", correct_choice_text(questions[7]).lower())
        self.assertIn("oophagy", questions[7]["why"].lower())
        self.assertIn("not true of every", questions[7]["why"].lower())
        self.assertIn("urea", correct_choice_text(questions[8]).lower())
        self.assertIn("seawater", correct_choice_text(questions[8]).lower())
        self.assertIn("percents stay soft", questions[8]["why"].lower())
        self.assertIn("forward motion", correct_choice_text(questions[9]).lower())
        self.assertIn("fin lift", correct_choice_text(questions[9]).lower())
        self.assertIn("dynamic lift", questions[9]["why"].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Chondrichthyes",
            "Batomorphi",
            "oophagy",
            "IUCN",
            "squalene",
            "trimethylamine",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_TORTOISE + PUSH_FURTHER_TORTOISE
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_SHARK + PUSH_FURTHER_SHARK:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_SHARK).lower()
        push = " ".join(PUSH_FURTHER_SHARK).lower()
        self.assertIn("red list", talk)
        self.assertIn("selachii", talk)
        self.assertIn("deep time", talk)
        self.assertIn("cites", push)
        self.assertIn("live-bearing", push)
        self.assertIn("threatened sharks", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("shark", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "shark", "packTemplate": "animals"})
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
        deck = study_deck_for("shark", "zoologist")
        sheet = study_print_html(
            deck,
            name="Shark",
            emoji="🦈",
            photo="/field-pack/photos/shark.jpg?v=img2",
            photo_pos="50% 40%",
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
        for prompt in TALK_ABOUT_SHARK + PUSH_FURTHER_SHARK:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_SHARK, sheet)
        self.assertIn("Facts from Wikipedia, Shark.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("shark", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        self.assertLess(html.find("study-foot"), html.find("study-explore"))
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_other_animal_decks_untouched(self):
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
        self.assertEqual(giraffe_zoo["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_zoo["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_zoo = study_deck_for("african-elephant", "zoologist")
        self.assertEqual(elephant_zoo["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Loxodonta africana", correct_choice_text(elephant_zoo["questions"][0]))
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertEqual(elephant_zoo["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_zoo["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        penguin_zoo = study_deck_for("african-penguin", "zoologist")
        self.assertEqual(penguin_zoo["source"], WIKI_AFRICAN_PENGUIN)
        self.assertIn("Spheniscus", correct_choice_text(penguin_zoo["questions"][0]))
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", penguin_html)
        self.assertEqual(penguin_zoo["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin_zoo["push_further"], list(PUSH_FURTHER_PENGUIN))
        self.assertEqual(shipped_levels_for("caribbean-flamingo"), ("easy", "hard", "zoologist"))
        flamingo_zoo = study_deck_for("caribbean-flamingo", "zoologist")
        self.assertEqual(flamingo_zoo["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertIn("Mirandornithes", correct_choice_text(flamingo_zoo["questions"][0]))
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", flamingo_html)
        self.assertEqual(flamingo_zoo["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(flamingo_zoo["push_further"], list(PUSH_FURTHER_FLAMINGO))
        self.assertEqual(shipped_levels_for("galapagos-tortoise"), ("easy", "hard", "zoologist"))
        tortoise_zoo = study_deck_for("galapagos-tortoise", "zoologist")
        self.assertEqual(tortoise_zoo["source"], WIKI_GALAPAGOS_TORTOISE)
        self.assertIn("Chelonoidis", correct_choice_text(tortoise_zoo["questions"][0]))
        tortoise_html = TORTOISE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", tortoise_html)
        self.assertEqual(tortoise_zoo["talk_about"], list(TALK_ABOUT_TORTOISE))
        self.assertEqual(tortoise_zoo["push_further"], list(PUSH_FURTHER_TORTOISE))
        self.assertEqual(shipped_levels_for("zebra"), ("easy", "hard", "zoologist"))
        zebra_zoo = study_deck_for("zebra", "zoologist")
        self.assertEqual(zebra_zoo["source"], WIKI_PLAINS_ZEBRA)
        self.assertIn("Equus quagga", correct_choice_text(zebra_zoo["questions"][0]))
        zebra_html = ZEBRA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", zebra_html)
        self.assertEqual(zebra_zoo["talk_about"], list(TALK_ABOUT_ZEBRA))
        self.assertEqual(zebra_zoo["push_further"], list(PUSH_FURTHER_ZEBRA))
        self.assertEqual(shipped_levels_for("nile-hippo"), ("easy", "hard", "zoologist"))
        hippo_zoo = study_deck_for("nile-hippo", "zoologist")
        self.assertEqual(hippo_zoo["source"], WIKI_HIPPOPOTAMUS)
        self.assertIn("Hipposudoric acids", correct_choice_text(hippo_zoo["questions"][0]))
        hippo_html = HIPPO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", hippo_html)
        self.assertEqual(hippo_zoo["talk_about"], list(TALK_ABOUT_HIPPO))
        self.assertEqual(hippo_zoo["push_further"], list(PUSH_FURTHER_HIPPO))
        self.assertEqual(shipped_levels_for("sumatran-tiger"), ("easy", "hard", "zoologist"))
        tiger_zoo = study_deck_for("sumatran-tiger", "zoologist")
        self.assertEqual(tiger_zoo["source"], WIKI_SUMATRAN_TIGER)
        self.assertIn("sondaica", correct_choice_text(tiger_zoo["questions"][0]))
        tiger_html = TIGER.read_text(encoding="utf-8")
        self.assertIn("Zoologist", tiger_html)
        self.assertEqual(tiger_zoo["talk_about"], list(TALK_ABOUT_TIGER))
        self.assertEqual(tiger_zoo["push_further"], list(PUSH_FURTHER_TIGER))
        self.assertEqual(shipped_levels_for("western-lowland-gorilla"), ("easy", "hard", "zoologist"))
        gorilla_zoo = study_deck_for("western-lowland-gorilla", "zoologist")
        self.assertEqual(gorilla_zoo["source"], WIKI_WESTERN_LOWLAND_GORILLA)
        self.assertIn("Critically Endangered", correct_choice_text(gorilla_zoo["questions"][0]))
        gorilla_html = GORILLA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", gorilla_html)
        self.assertEqual(gorilla_zoo["talk_about"], list(TALK_ABOUT_GORILLA))
        self.assertEqual(gorilla_zoo["push_further"], list(PUSH_FURTHER_GORILLA))
        self.assertEqual(shipped_levels_for("cheetah"), ("easy", "hard", "zoologist"))
        cheetah_zoo = study_deck_for("cheetah", "zoologist")
        self.assertEqual(cheetah_zoo["source"], WIKI_CHEETAH)
        self.assertIn("Acinonyx", correct_choice_text(cheetah_zoo["questions"][0]))
        cheetah_html = CHEETAH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", cheetah_html)
        self.assertEqual(cheetah_zoo["talk_about"], list(TALK_ABOUT_CHEETAH))
        self.assertEqual(cheetah_zoo["push_further"], list(PUSH_FURTHER_CHEETAH))
        self.assertEqual(shipped_levels_for("red-panda"), ("easy", "hard", "zoologist"))
        panda_zoo = study_deck_for("red-panda", "zoologist")
        self.assertEqual(panda_zoo["source"], WIKI_RED_PANDA)
        self.assertIn("Ailuridae", correct_choice_text(panda_zoo["questions"][0]))
        panda_html = RED_PANDA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", panda_html)
        self.assertEqual(panda_zoo["talk_about"], list(TALK_ABOUT_RED_PANDA))
        self.assertEqual(panda_zoo["push_further"], list(PUSH_FURTHER_RED_PANDA))
        self.assertEqual(shipped_levels_for("koala"), ("easy", "hard", "zoologist"))
        koala_zoo = study_deck_for("koala", "zoologist")
        self.assertEqual(koala_zoo["source"], WIKI_KOALA)
        self.assertIn("Phascolarctos cinereus", correct_choice_text(koala_zoo["questions"][0]))
        koala_html = KOALA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", koala_html)
        self.assertEqual(koala_zoo["talk_about"], list(TALK_ABOUT_KOALA))
        self.assertEqual(koala_zoo["push_further"], list(PUSH_FURTHER_KOALA))
        self.assertEqual(shipped_levels_for("chimpanzee"), ("easy", "hard", "zoologist"))
        chimp_zoo = study_deck_for("chimpanzee", "zoologist")
        self.assertEqual(chimp_zoo["source"], WIKI_CHIMPANZEE)
        self.assertIn("one or two percent", correct_choice_text(chimp_zoo["questions"][0]).lower())
        chimp_html = CHIMPANZEE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", chimp_html)
        self.assertEqual(chimp_zoo["talk_about"], list(TALK_ABOUT_CHIMPANZEE))
        self.assertEqual(chimp_zoo["push_further"], list(PUSH_FURTHER_CHIMPANZEE))
        self.assertEqual(shipped_levels_for("orangutan"), ("easy", "hard", "zoologist"))
        orang_zoo = study_deck_for("orangutan", "zoologist")
        self.assertEqual(orang_zoo["source"], WIKI_ORANGUTAN)
        self.assertIn("Pongo", correct_choice_text(orang_zoo["questions"][0]))
        orang_html = ORANGUTAN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", orang_html)
        self.assertEqual(orang_zoo["talk_about"], list(TALK_ABOUT_ORANGUTAN))
        self.assertEqual(orang_zoo["push_further"], list(PUSH_FURTHER_ORANGUTAN))
        self.assertEqual(shipped_levels_for("giant-panda"), ("easy", "hard", "zoologist"))
        giant_zoo = study_deck_for("giant-panda", "zoologist")
        self.assertEqual(giant_zoo["source"], WIKI_GIANT_PANDA)
        self.assertIn("Ailuropoda", correct_choice_text(giant_zoo["questions"][0]))
        giant_html = GIANT_PANDA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giant_html)
        self.assertEqual(giant_zoo["talk_about"], list(TALK_ABOUT_GIANT_PANDA))
        self.assertEqual(giant_zoo["push_further"], list(PUSH_FURTHER_GIANT_PANDA))
        self.assertEqual(shipped_levels_for("ring-tailed-lemur"), ("easy", "hard", "zoologist"))
        lemur_zoo = study_deck_for("ring-tailed-lemur", "zoologist")
        self.assertEqual(lemur_zoo["source"], WIKI_RING_TAILED_LEMUR)
        self.assertIn("Lemur catta", correct_choice_text(lemur_zoo["questions"][0]))
        lemur_html = LEMUR.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lemur_html)
        self.assertEqual(lemur_zoo["talk_about"], list(TALK_ABOUT_RING_TAILED_LEMUR))
        self.assertEqual(lemur_zoo["push_further"], list(PUSH_FURTHER_RING_TAILED_LEMUR))
        self.assertEqual(shipped_levels_for("ostrich"), ("easy", "hard", "zoologist"))
        ostrich_zoo = study_deck_for("ostrich", "zoologist")
        self.assertEqual(ostrich_zoo["source"], WIKI_OSTRICH)
        self.assertIn("Struthio camelus", correct_choice_text(ostrich_zoo["questions"][0]))
        ostrich_html = OSTRICH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", ostrich_html)
        self.assertEqual(ostrich_zoo["talk_about"], list(TALK_ABOUT_OSTRICH))
        self.assertEqual(ostrich_zoo["push_further"], list(PUSH_FURTHER_OSTRICH))
        self.assertEqual(shipped_levels_for("warthog"), ("easy", "hard", "zoologist"))
        hog_zoo = study_deck_for("warthog", "zoologist")
        self.assertEqual(hog_zoo["source"], WIKI_WARTHOG)
        self.assertIn("Phacochoerus africanus", correct_choice_text(hog_zoo["questions"][0]))
        hog_html = WARTHOG.read_text(encoding="utf-8")
        self.assertIn("Zoologist", hog_html)
        self.assertEqual(hog_zoo["talk_about"], list(TALK_ABOUT_WARTHOG))
        self.assertEqual(hog_zoo["push_further"], list(PUSH_FURTHER_WARTHOG))
        whale = WHALE_SHARK.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", whale)
        self.assertNotIn("selachii-soft", whale)
        self.assertIsNotNone(study_deck_for("whale-shark", "zoologist"))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["shark"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("selachii-soft", data_js)
        self.assertIn("sister-to-batoids", data_js)
        self.assertIn("dynamic-lift-soft", data_js)
        self.assertIn("oophagy-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = SHARK.read_text(encoding="utf-8")
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
        main = html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]
        self.assertLess(main.find("study-foot"), main.find("study-explore"))
        self.assertLess(main.find("study-explore"), main.find("card-try-next"))


if __name__ == "__main__":
    unittest.main()
