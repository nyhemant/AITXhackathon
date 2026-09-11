"""Warthog Easy study-card: Junior Ranger teach + 10 MCQs (first deck)."""

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
    LEVEL_DISPLAY_NAMES,
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
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_try_next_ids,
    target_letter_for_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
WARTHOG = FP / "cards" / "warthog" / "index.html"
OSTRICH = FP / "cards" / "ostrich" / "index.html"
LEMUR = FP / "cards" / "ring-tailed-lemur" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
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
    "A group of warthogs is a sounder.",
    "They are wild African savanna pigs, not farm pigs.",
    "They kneel on padded wrists and dig with a strong snout — not with tusks.",
    "They often sleep in old aardvark burrows, backing in with tusks ready.",
    "Face “warts” are tough pads, not disease sores.",
)

STEMS = (
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

QIDS = (
    "sounder",
    "africa-grassland",
    "wild-pig-kin",
    "wart-pads",
    "curved-tusks",
    "kneel-to-graze",
    "borrowed-dens",
    "back-in-first",
    "soft-care",
    "tusk-dig-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Vulnerable",
    "Endangered",
    "Critically",
    "Least Concern",
    "Phacochoerus",
    "africanus",
    "aethiopicus",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "desert warthog",
    "gland",
    "litter",
    "mph",
    "km/h",
    "IUCN",
    "Least Concern",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class WarthogEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_with_park_ranger_and_zoologist(self):
        self.assertIn("warthog", study_card_ids())
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
                "puffin",
                "clownfish",
                "crab",
                "cuttlefish",
                "eel",
                "jellyfish",
                "kelp-forest",
                "manta-ray",
                "octopus",
                "sea-turtle",
                "seahorse",
                "starfish",
                "stingray",
                "whale-shark",
            ),
        )
        self.assertEqual(shipped_levels_for("warthog"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("warthog", "hard"))
        self.assertIsNotNone(study_deck_for("warthog", "zoologist"))
        deck = study_deck_for("warthog")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "warthog")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_WARTHOG)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Common warthog.")
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_WARTHOG))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_WARTHOG))
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)
        for q in deck["questions"]:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(str(q["why"]).strip())
        blob = " ".join(deck["teach"] + [q["stem"] + q["why"] for q in deck["questions"]])
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)
        self.assertIn("sounder", blob.lower())
        self.assertIn("africa", blob.lower())
        self.assertIn("grassland", blob.lower())
        self.assertIn("savanna", blob.lower())
        self.assertIn("pig family", blob.lower())
        self.assertIn("pads", blob.lower())
        self.assertIn("tusk", blob.lower())
        self.assertIn("kneel", blob.lower())
        self.assertIn("aardvark", blob.lower())
        self.assertIn("snout", blob.lower())
        self.assertEqual(WIKI_WARTHOG, "https://en.wikipedia.org/wiki/Common_warthog")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        giraffe = study_deck_for("reticulated-giraffe")
        self.assertEqual(giraffe["source"], WIKI_GIRAFFE)
        self.assertEqual(giraffe["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe["push_further"], list(PUSH_FURTHER_GIRAFFE))
        elephant = study_deck_for("african-elephant")
        self.assertEqual(elephant["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertEqual(elephant["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant["push_further"], list(PUSH_FURTHER_ELEPHANT))
        penguin = study_deck_for("african-penguin")
        self.assertEqual(penguin["source"], WIKI_AFRICAN_PENGUIN)
        self.assertEqual(penguin["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin["push_further"], list(PUSH_FURTHER_PENGUIN))
        flamingo = study_deck_for("caribbean-flamingo")
        self.assertEqual(flamingo["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertEqual(flamingo["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(flamingo["push_further"], list(PUSH_FURTHER_FLAMINGO))
        tortoise = study_deck_for("galapagos-tortoise")
        self.assertEqual(tortoise["source"], WIKI_GALAPAGOS_TORTOISE)
        self.assertEqual(tortoise["talk_about"], list(TALK_ABOUT_TORTOISE))
        self.assertEqual(tortoise["push_further"], list(PUSH_FURTHER_TORTOISE))
        zebra = study_deck_for("zebra")
        self.assertEqual(zebra["source"], WIKI_PLAINS_ZEBRA)
        self.assertEqual(zebra["talk_about"], list(TALK_ABOUT_ZEBRA))
        self.assertEqual(zebra["push_further"], list(PUSH_FURTHER_ZEBRA))
        hippo = study_deck_for("nile-hippo")
        self.assertEqual(hippo["source"], WIKI_HIPPOPOTAMUS)
        self.assertEqual(hippo["talk_about"], list(TALK_ABOUT_HIPPO))
        self.assertEqual(hippo["push_further"], list(PUSH_FURTHER_HIPPO))
        tiger = study_deck_for("sumatran-tiger")
        self.assertEqual(tiger["source"], WIKI_SUMATRAN_TIGER)
        self.assertEqual(tiger["talk_about"], list(TALK_ABOUT_TIGER))
        self.assertEqual(tiger["push_further"], list(PUSH_FURTHER_TIGER))
        gorilla = study_deck_for("western-lowland-gorilla")
        self.assertEqual(gorilla["source"], WIKI_WESTERN_LOWLAND_GORILLA)
        self.assertEqual(gorilla["talk_about"], list(TALK_ABOUT_GORILLA))
        self.assertEqual(gorilla["push_further"], list(PUSH_FURTHER_GORILLA))
        cheetah = study_deck_for("cheetah")
        self.assertEqual(cheetah["source"], WIKI_CHEETAH)
        self.assertEqual(cheetah["talk_about"], list(TALK_ABOUT_CHEETAH))
        self.assertEqual(cheetah["push_further"], list(PUSH_FURTHER_CHEETAH))
        panda = study_deck_for("red-panda")
        self.assertEqual(panda["source"], WIKI_RED_PANDA)
        self.assertEqual(panda["talk_about"], list(TALK_ABOUT_RED_PANDA))
        self.assertEqual(panda["push_further"], list(PUSH_FURTHER_RED_PANDA))
        koala = study_deck_for("koala")
        self.assertEqual(koala["source"], WIKI_KOALA)
        self.assertEqual(koala["talk_about"], list(TALK_ABOUT_KOALA))
        self.assertEqual(koala["push_further"], list(PUSH_FURTHER_KOALA))
        chimp = study_deck_for("chimpanzee")
        self.assertEqual(chimp["source"], WIKI_CHIMPANZEE)
        self.assertEqual(chimp["talk_about"], list(TALK_ABOUT_CHIMPANZEE))
        self.assertEqual(chimp["push_further"], list(PUSH_FURTHER_CHIMPANZEE))
        orang = study_deck_for("orangutan")
        self.assertEqual(orang["source"], WIKI_ORANGUTAN)
        self.assertEqual(orang["talk_about"], list(TALK_ABOUT_ORANGUTAN))
        self.assertEqual(orang["push_further"], list(PUSH_FURTHER_ORANGUTAN))
        giant = study_deck_for("giant-panda")
        self.assertEqual(giant["source"], WIKI_GIANT_PANDA)
        self.assertEqual(giant["talk_about"], list(TALK_ABOUT_GIANT_PANDA))
        self.assertEqual(giant["push_further"], list(PUSH_FURTHER_GIANT_PANDA))
        lemur = study_deck_for("ring-tailed-lemur")
        self.assertEqual(lemur["source"], WIKI_RING_TAILED_LEMUR)
        self.assertEqual(lemur["talk_about"], list(TALK_ABOUT_RING_TAILED_LEMUR))
        self.assertEqual(lemur["push_further"], list(PUSH_FURTHER_RING_TAILED_LEMUR))
        self.assertEqual(shipped_levels_for("ring-tailed-lemur"), ("easy", "hard", "zoologist"))
        ostrich = study_deck_for("ostrich")
        self.assertEqual(ostrich["source"], WIKI_OSTRICH)
        self.assertEqual(ostrich["talk_about"], list(TALK_ABOUT_OSTRICH))
        self.assertEqual(ostrich["push_further"], list(PUSH_FURTHER_OSTRICH))
        self.assertEqual(shipped_levels_for("ostrich"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("ostrich", "hard"))
        self.assertIsNotNone(study_deck_for("ostrich", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "warthog", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("card-study-pack", html)
        self.assertIn("Learn first", html)
        self.assertIn('<details class="study-teach">', html)
        self.assertNotIn('<details class="study-teach" open', html)
        self.assertIn('<summary class="study-teach-kicker">', html)
        self.assertIn("tap to open", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        for prompt in TALK_ABOUT_WARTHOG + PUSH_FURTHER_WARTHOG:
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
        self.assertEqual(html.count('role="group"'), 2)
        self.assertIn("study-level-picker-bottom", html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, html)
        self.assertIn(
            "A sounder — moms and kids live together; grown males often roam alone",
            html,
        )
        self.assertIn(
            "No — they dig with the snout and feet; tusks are for fighting and defense",
            html,
        )
        self.assertIn("Facts from Wikipedia, Common warthog.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn("card-study-pack", html)
        self.assertNotIn("What do they eat?", html)
        self.assertNotIn("What do you call a group of warthogs", html)
        sea = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", sea)
        self.assertNotIn("What do they eat?", sea)

    def test_published_warthog_card_matches_easy_deck(self):
        html = WARTHOG.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertNotIn("Watch Live", main)
        self.assertNotIn("card-watch-live", main)
        self.assertNotIn("card-page-photo-link", main)
        self.assertIn('class="card-hero-links no-print"', main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=7", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "warthog"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=42", html)
        self.assertIn('<details class="study-teach">', main)
        self.assertNotIn('<details class="study-teach" open', main)
        self.assertNotIn('<div class="study-teach">', main)
        self.assertIn("Talk about it", main)
        self.assertIn("Push further", main)
        self.assertIn('<details class="study-explore', main)
        self.assertIn("Explore more", main)
        self.assertNotIn('<aside class="study-deepen"', main)
        self.assertLess(main.find("study-foot"), main.find("study-explore"))
        self.assertLess(main.find("study-explore"), main.find("card-try-next"))
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
        self.assertIn(">Quiz</h2>", main)
        self.assertEqual(main.count("data-study-correct"), 2)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, main)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertNotIn(" · Easy ·", print_tpl)
        self.assertNotIn(" · Hard ·", print_tpl)
        self.assertNotIn("Explore more", print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertNotIn("Push further", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        self.assertIn("ps-study-deepen", back)
        for prompt in TALK_ABOUT_WARTHOG + PUSH_FURTHER_WARTHOG:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("warthog"),
            ["zebra", "ostrich", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("warthog")
        sheet = study_print_html(
            deck,
            name="Warthog",
            emoji="🐗",
            photo="/field-pack/photos/warthog.jpg?v=img2",
            photo_pos="50% 28%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/warthog.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_WARTHOG, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "A sounder — moms and kids live together; grown males often roam alone",
            sheet,
        )
        self.assertIn(
            "No — they dig with the snout and feet; tusks are for fighting and defense",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_WARTHOG + PUSH_FURTHER_WARTHOG:
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
        self.assertIn('details class="study-teach"', study_js)
        self.assertIn("study-deepen", study_js)
        self.assertIn("is-wrong-pick", study_js)
        self.assertIn("FPStudyLevelName", study_js + STUDY_DATA_JS.read_text(encoding="utf-8"))

    def test_artifacts_include_warthog_easy_hard_and_zoologist(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("warthog", payload)
        self.assertIn("ostrich", payload)
        self.assertIn("ring-tailed-lemur", payload)
        hog = payload["warthog"]
        self.assertEqual(hog["id"], "warthog")
        self.assertEqual(set(hog["levels"]), {"easy", "hard", "zoologist"})
        easy = hog["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        hard = hog["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        zoo = hog["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("warthog", data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertIn('"hard":"Park Ranger"', data_js)
        self.assertEqual(set(payload["ostrich"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["ring-tailed-lemur"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["african-lion"]["levels"]), {"easy", "hard", "zoologist"})

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
        hog_html = WARTHOG.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(hog_html)))
        self.assertIn("Park Ranger", _text(_main(hog_html)))
        self.assertIn("Zoologist", _text(_main(hog_html)))
        ostrich_html = OSTRICH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(ostrich_html)))
        self.assertIn("Park Ranger", _text(_main(ostrich_html)))
        self.assertIn("Zoologist", _text(_main(ostrich_html)))
        lemur_html = LEMUR.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(lemur_html)))
        self.assertIn("Park Ranger", _text(_main(lemur_html)))
        self.assertIn("Zoologist", _text(_main(lemur_html)))


if __name__ == "__main__":
    unittest.main()
