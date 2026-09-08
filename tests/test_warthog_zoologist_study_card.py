"""Warthog Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    WIKI_SUMATRAN_TIGER,
    WIKI_WARTHOG,
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
    "What scientific name do scientists use for the common warthog, and which family and genus does it sit in?",
    "How did scientists once treat the common warthog’s name, and what does Phacochoerus aethiopicus mean now?",
    "How do many lists split living common warthogs across Africa?",
    "How should we read the usual IUCN letter for the common warthog?",
    "When do a warthog’s padded wrists start to form, and why does that matter?",
    "How long is a warthog pregnancy compared with many other pigs?",
    "What may a warthog sow do if she loses her own litter?",
    "Which two named facial glands do warthogs use for marking and social signals?",
    "Do common warthogs keep strict territories?",
    "How does a warthog’s life in the wild often compare with life in care?",
)

ZOOLOGIST_IDS = (
    "phacochoerus-africanus",
    "name-history-soft",
    "four-subspecies-soft",
    "least-concern-snapshot",
    "wrist-callosities",
    "long-gestation-soft",
    "allosucking-soft",
    "two-facial-glands",
    "home-range-not-territory",
    "lifespan-soft",
)

HARD_STEMS = (
    "When a warthog is scared, how fast can it sprint?",
    "How do warthogs often hold the tail when they run?",
    "How do warthogs stay comfortable when it is very hot or very cold?",
    "Is there more than one kind of warthog in Africa?",
    "What do facial scent marks help a warthog remember?",
    "How many piglets does a warthog mom often have at once?",
    "Who may hunt warthogs, and how do moms protect piglets?",
    "How does a warthog’s food change with the seasons?",
    "What can hurt local warthog groups today?",
    "Who sometimes helps a warthog by picking off ticks?",
)

EASY_STEMS = (
    "What do you call a group of warthogs, and who usually lives in one?",
    "Where do wild warthogs live?",
    "What kind of animal is a warthog?",
    "What are the bumps on a warthog’s face?",
    "How many pairs of tusks does a warthog have, and what are they for?",
    "How do warthogs often graze, and how do they dig?",
    "Where do warthogs often sleep?",
    "How does a warthog usually enter its den?",
    "How are wild warthogs doing today?",
    "Do warthogs dig holes with their tusks?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "175",
    "180 day",
    "7 to 11",
    "7–11",
    "7-11",
    "21 year",
    "250,000",
    "1999",
    "48 km",
    "30 mph",
)
REDO_THEMES = (
    "A sounder — moms and kids live together",
    "Grassland, savanna, and woodland in sub-Saharan Africa",
    "A wild African member of the pig family — not a farm pig",
    "Tough protective pads — not oozing disease sores",
    "Two pairs that curve up — used for fighting and defense",
    "They kneel on padded wrists; they dig and root with the snout and feet",
    "In empty aardvark burrows more often than digging every den themselves",
    "It usually backs in so the head and tusks face out",
    "They still live across many African grasslands and parks",
    "they dig with the snout and feet; tusks are for fighting and defense",
    "About as fast as a slow car",
    "thin tail held straight up",
    "wallow in mud to cool down, and huddle together",
    "a separate desert warthog lives in drier parts of East Africa",
    "Sleeping spots, feeding areas, and waterholes",
    "Often a few piglets — sometimes more",
    "lions, leopards, and hyenas may hunt them",
    "More grass in wet times; more roots and bulbs when it is dry",
    "Drought and hunting can hurt local groups",
    "mongooses or monkeys pick off ticks",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class WarthogZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("warthog"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("warthog", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_WARTHOG)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Common warthog.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_WARTHOG))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_WARTHOG))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("warthog", "zoologist")
        easy = study_deck_for("warthog", "easy")
        hard = study_deck_for("warthog", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("warthog", "zoologist")
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
        self.assertIn("Phacochoerus africanus", correct_choice_text(questions[0]))
        self.assertIn("Suidae", correct_choice_text(questions[0]))
        self.assertIn("desert warthog", correct_choice_text(questions[0]).lower())
        self.assertIn("lumped", correct_choice_text(questions[1]).lower())
        self.assertIn("aethiopicus", correct_choice_text(questions[1]))
        self.assertIn("desert warthog only", correct_choice_text(questions[1]).lower())
        self.assertIn("split maps stay soft", questions[1]["why"].lower())
        self.assertIn("four living subspecies", correct_choice_text(questions[2]).lower())
        self.assertIn("maps", correct_choice_text(questions[2]).lower())
        self.assertIn("contested", questions[2]["why"].lower())
        self.assertIn("Least Concern", correct_choice_text(questions[3]))
        self.assertIn("snapshot", correct_choice_text(questions[3]).lower())
        self.assertIn("wipeouts", correct_choice_text(questions[3]).lower())
        self.assertIn("before birth", correct_choice_text(questions[4]).lower())
        self.assertIn("kneeling", correct_choice_text(questions[4]).lower())
        self.assertIn("fetus", questions[4]["why"].lower())
        self.assertIn("five to six months", correct_choice_text(questions[5]).lower())
        self.assertIn("long for a pig", correct_choice_text(questions[5]).lower())
        self.assertIn("day counts stay soft", questions[5]["why"].lower())
        self.assertIn("foster", correct_choice_text(questions[6]).lower())
        self.assertIn("allosucking", correct_choice_text(questions[6]).lower())
        self.assertIn("cooperative", correct_choice_text(questions[6]).lower())
        self.assertIn("tusk gland", correct_choice_text(questions[7]).lower())
        self.assertIn("sebaceous", correct_choice_text(questions[7]).lower())
        self.assertIn("social signals", correct_choice_text(questions[7]).lower())
        self.assertIn("home ranges", correct_choice_text(questions[8]).lower())
        self.assertIn("not territorial", questions[8]["why"].lower())
        self.assertIn("fewer years", correct_choice_text(questions[9]).lower())
        self.assertIn("in care", correct_choice_text(questions[9]).lower())
        self.assertIn("ages stay soft", questions[9]["why"].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Phacochoerus",
            "aethiopicus",
            "sundevallii",
            "massaicus",
            "aeliani",
            "IUCN",
            "sebaceous",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_TORTOISE + PUSH_FURTHER_TORTOISE
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_WARTHOG + PUSH_FURTHER_WARTHOG:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_WARTHOG).lower()
        push = " ".join(PUSH_FURTHER_WARTHOG).lower()
        self.assertIn("two living", talk)
        self.assertIn("needs care", talk)
        self.assertIn("wrist", talk)
        self.assertIn("subspecies", push)
        self.assertIn("allosucking", push)
        self.assertIn("home range", push)
        self.assertIn("territor", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("warthog", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "warthog", "packTemplate": "animals"})
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
        deck = study_deck_for("warthog", "zoologist")
        sheet = study_print_html(
            deck,
            name="Warthog",
            emoji="🐗",
            photo="/field-pack/photos/warthog.jpg?v=img2",
            photo_pos="50% 28%",
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
        for prompt in TALK_ABOUT_WARTHOG + PUSH_FURTHER_WARTHOG:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_WARTHOG, sheet)
        self.assertIn("Facts from Wikipedia, Common warthog.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("warthog", "zoologist"))
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

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["warthog"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("phacochoerus-africanus", data_js)
        self.assertIn("name-history-soft", data_js)
        self.assertIn("lifespan-soft", data_js)
        self.assertIn("least-concern-snapshot", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = WARTHOG.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
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
