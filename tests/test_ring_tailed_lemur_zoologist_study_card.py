"""Ring-tailed lemur Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_PENGUIN,
    PUSH_FURTHER_RED_PANDA,
    PUSH_FURTHER_RING_TAILED_LEMUR,
    PUSH_FURTHER_TIGER,
    PUSH_FURTHER_TORTOISE,
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
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_RED_PANDA,
    TALK_ABOUT_RING_TAILED_LEMUR,
    TALK_ABOUT_TIGER,
    TALK_ABOUT_TORTOISE,
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
    WIKI_PLAINS_ZEBRA,
    WIKI_RED_PANDA,
    WIKI_RING_TAILED_LEMUR,
    WIKI_SUMATRAN_TIGER,
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
    "How does the ring-tailed lemur sit in its genus and family?",
    "What kind of primate is a ring-tailed lemur, by its nose?",
    "How do male ring-tailed lemurs mix the scent used in a stink fight?",
    "What is the horny spur over a male’s forearm gland used for?",
    "What special grooming claw do ring-tailed lemurs have?",
    "Why can a ring-tailed lemur’s eyes shine even though it is mostly day-active?",
    "How should we read the usual threat listing for ring-tailed lemurs?",
    "How long are female ring-tailed lemurs receptive during the breeding season?",
    "Which native predators do wild ring-tailed lemurs have to watch for?",
    "How did lemurs likely reach Madagascar and then become so many kinds?",
)

ZOOLOGIST_IDS = (
    "lemur-catta",
    "strepsirrhine",
    "stink-fight-glands",
    "wrist-spur",
    "toilet-claw",
    "eye-shine",
    "endangered-snapshot",
    "short-window",
    "fossa-watch",
    "island-radiation",
)

HARD_STEMS = (
    "How do male ring-tailed lemurs settle many fights without punching?",
    "How does a baby ring-tailed lemur ride with its mother as it grows?",
    "When are ring-tailed lemurs mostly active?",
    "Why does a ring-tailed lemur troop use so many different calls?",
    "What special job do a ring-tailed lemur’s lower front teeth do?",
    "Which plant treat do ring-tailed lemurs especially like?",
    "What kind of wild home do ring-tailed lemurs use in southern Madagascar?",
    "What do young male ring-tailed lemurs usually do when they grow up?",
    "What puts wild ring-tailed lemurs under pressure today?",
    "How do ring-tailed lemurs get around in trees and on rocky ground?",
)

EASY_STEMS = (
    "Where do wild ring-tailed lemurs live?",
    "Why are they called ring-tailed lemurs?",
    "Who leads a ring-tailed lemur troop?",
    "How do ring-tailed lemurs warm up in the morning?",
    "What do ring-tailed lemurs mostly eat?",
    "Why do ring-tailed lemurs hold their tails high?",
    "How do ring-tailed lemurs spend a lot of their day, unlike many other lemurs?",
    "How do ring-tailed lemurs share “our place” with the troop?",
    "What do wild ring-tailed lemur forests need?",
    "Is a ring-tailed lemur a monkey?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "6–24",
    "6-24",
    "24 hours",
    "50 Ma",
    "60 Ma",
    "54 Ma",
    "million years ago",
    "2,000",
    "2000",
    "Cryptoprocta",
)
REDO_THEMES = (
    "Only on the island of Madagascar",
    "long black-and-white ringed tail",
    "Females lead the troop and eat first",
    "sunbathe with their bellies toward the sun",
    "Plants — fruit, leaves, and flowers",
    "the tail is not for grabbing",
    "spend a lot of time on the ground",
    "leave scent on trees and rocks",
    "wild forests in Madagascar need looking after",
    "a lemur, a different Madagascar primate",
    "Males rub scent on their tails and wave them at rivals",
    "Infants cling to mom’s belly first, then ride on her back",
    "Mostly in the daytime",
    "Many different calls help the troop stay together and warn of danger",
    "They work like a comb for grooming fur",
    "Tamarind fruit and leaves",
    "Dry forests, riverside gallery forests, and rocky areas",
    "Young males usually leave their birth group and join another",
    "Forests are shrinking, and some lemurs are hunted or kept as pets",
    "They leap well through trees and across rocky ground",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class RingTailedLemurZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("ring-tailed-lemur"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("ring-tailed-lemur", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_RING_TAILED_LEMUR)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Ring-tailed lemur.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_RING_TAILED_LEMUR))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_RING_TAILED_LEMUR))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("ring-tailed-lemur", "zoologist")
        easy = study_deck_for("ring-tailed-lemur", "easy")
        hard = study_deck_for("ring-tailed-lemur", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("ring-tailed-lemur", "zoologist")
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
        self.assertIn("Lemur catta", correct_choice_text(questions[0]))
        self.assertIn("Lemuridae", correct_choice_text(questions[0]))
        self.assertIn("bamboo", correct_choice_text(questions[0]).lower())
        self.assertIn("splits stay soft", questions[0]["why"].lower())
        self.assertIn("strepsirrhine", correct_choice_text(questions[1]).lower())
        self.assertIn("rhinarium", correct_choice_text(questions[1]).lower())
        self.assertIn("wet-nosed", correct_choice_text(questions[1]).lower())
        self.assertIn("antebrachial", correct_choice_text(questions[2]).lower())
        self.assertIn("brachial", correct_choice_text(questions[2]).lower())
        self.assertIn("forearm", correct_choice_text(questions[2]).lower())
        self.assertIn("shoulder", correct_choice_text(questions[2]).lower())
        self.assertIn("spur-marking", correct_choice_text(questions[3]).lower())
        self.assertIn("forearm gland", correct_choice_text(questions[3]).lower())
        self.assertIn("toilet claw", correct_choice_text(questions[4]).lower())
        self.assertIn("second toe", correct_choice_text(questions[4]).lower())
        self.assertIn("tapetum lucidum", correct_choice_text(questions[5]).lower())
        self.assertIn("diurnal", questions[5]["why"].lower())
        self.assertIn("Endangered", correct_choice_text(questions[6]))
        self.assertIn("snapshot", correct_choice_text(questions[6]).lower())
        self.assertIn("headcounts", questions[6]["why"].lower())
        self.assertIn("few hours", correct_choice_text(questions[7]).lower())
        self.assertIn("hour counts stay soft", questions[7]["why"].lower())
        self.assertIn("fossa", correct_choice_text(questions[8]).lower())
        self.assertIn("birds", correct_choice_text(questions[8]).lower())
        self.assertIn("snakes", correct_choice_text(questions[8]).lower())
        self.assertIn("lists stay soft", questions[8]["why"].lower())
        self.assertIn("rafted", correct_choice_text(questions[9]).lower())
        self.assertIn("dates stay soft", questions[9]["why"].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Laverania",
            "incomplete lineage sorting",
            "microsatellite",
            "MHC",
            "antebrachial",
            "brachial",
            "tapetum",
            "rhinarium",
            "Hapalemur",
            "Lemuridae",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_TORTOISE + PUSH_FURTHER_TORTOISE
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_RING_TAILED_LEMUR + PUSH_FURTHER_RING_TAILED_LEMUR:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_RING_TAILED_LEMUR).lower()
        push = " ".join(PUSH_FURTHER_RING_TAILED_LEMUR).lower()
        self.assertIn("wet nose", talk)
        self.assertIn("dry", talk)
        self.assertIn("two glands", talk)
        self.assertIn("stink fight", talk)
        self.assertIn("status letter", talk)
        self.assertIn("snapshot", talk)
        self.assertIn("toilet claw", push)
        self.assertIn("shine", push)
        self.assertIn("raft", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("ring-tailed-lemur", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "ring-tailed-lemur", "packTemplate": "animals"})
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
        deck = study_deck_for("ring-tailed-lemur", "zoologist")
        sheet = study_print_html(
            deck,
            name="Ring-tailed lemur",
            emoji="🐒",
            photo="/field-pack/photos/ring-tailed-lemur.jpg?v=img2",
            photo_pos="50% 22%",
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
        for prompt in TALK_ABOUT_RING_TAILED_LEMUR + PUSH_FURTHER_RING_TAILED_LEMUR:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_RING_TAILED_LEMUR, sheet)
        self.assertIn("Facts from Wikipedia, Ring-tailed lemur.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("ring-tailed-lemur", "zoologist"))
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

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["ring-tailed-lemur"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("lemur-catta", data_js)
        self.assertIn("stink-fight-glands", data_js)
        self.assertIn("island-radiation", data_js)
        self.assertIn("endangered-snapshot", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = LEMUR.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=9", html)
        self.assertIn("study-cards-data.js?v=5", html)
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
