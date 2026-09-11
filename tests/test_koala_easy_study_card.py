"""Koala Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger + Zoologist sibling levels)."""

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
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_FLAMINGO,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_GORILLA,
    PUSH_FURTHER_HIPPO,
    PUSH_FURTHER_KOALA,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PENGUIN,
    PUSH_FURTHER_RED_PANDA,
    PUSH_FURTHER_TIGER,
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_ZEBRA,
    STUDY_SLOTS,
    TALK_ABOUT_CHEETAH,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_GORILLA,
    TALK_ABOUT_HIPPO,
    TALK_ABOUT_KOALA,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_RED_PANDA,
    TALK_ABOUT_TIGER,
    TALK_ABOUT_TORTOISE,
    TALK_ABOUT_ZEBRA,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
    WIKI_CHEETAH,
    WIKI_GALAPAGOS_TORTOISE,
    WIKI_GIRAFFE,
    WIKI_HIPPOPOTAMUS,
    WIKI_KOALA,
    WIKI_LION,
    WIKI_PLAINS_ZEBRA,
    WIKI_RED_PANDA,
    WIKI_SUMATRAN_TIGER,
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
    "Not a bear — a marsupial with a pouch.",
    "Lives in eucalyptus forests in Australia.",
    "Eats eucalyptus leaves.",
    "A baby is a joey (grows in mom’s pouch).",
    "Sleeps most of the day to save energy.",
)

STEMS = (
    "Where do wild koalas live?",
    "What do koalas almost always eat?",
    "Where does a koala spend almost all of its time?",
    "Why do koalas sleep most of the day?",
    "What is a baby koala called, and where does it keep growing?",
    "How do a koala’s front paws help it climb?",
    "What makes the classic koala face?",
    "How do adult koalas usually live?",
    "How do koalas usually get the water they need?",
    "People sometimes say “koala bear.” Is a koala a bear?",
)

QIDS = (
    "australia-home",
    "eucalyptus-leaves",
    "tree-life",
    "sleepy-saver",
    "joey",
    "climb-grip",
    "fluffy-look",
    "mostly-alone",
    "leaf-water",
    "koala-bear-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Vulnerable",
    "Endangered",
    "Phascolarctos",
    "cinereus",
    "caecum",
    "cecum",
    "pap",
    "fingerprint",
    "20 hours",
    "twenty hours",
    "400 gram",
    "400 g",
    "kg",
    "cm",
)
# Explore more may name pap, fingerprints, status letters, and caecum.
PAGE_BRITTLE = (
    "IUCN",
    "Phascolarctos",
    "cinereus",
    "20 hours",
    "twenty hours",
    "400 gram",
    "400 g",
    "kg",
    "cm",
)
RESERVED = (
    "Phascolarctos",
    "caecum",
    "pap",
    "fingerprint",
    "Vulnerable",
    "Endangered",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class KoalaEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_with_park_ranger_and_zoologist(self):
        self.assertIn("koala", study_card_ids())
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
        self.assertEqual(shipped_levels_for("koala"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("koala", "hard"))
        self.assertIsNotNone(study_deck_for("koala", "zoologist"))
        deck = study_deck_for("koala")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "koala")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_KOALA)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Koala.")
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_KOALA))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_KOALA))
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
        self.assertIn("not a bear", blob.lower())
        self.assertIn("marsupial", blob.lower())
        self.assertIn("australia", blob.lower())
        self.assertIn("eucalyptus", blob.lower())
        self.assertIn("joey", blob.lower())
        self.assertIn("pouch", blob.lower())
        self.assertIn("sleep", blob.lower())
        self.assertIn("thumb", blob.lower())
        self.assertIn("solitary", blob.lower())
        self.assertIn("drink", blob.lower())
        self.assertEqual(WIKI_KOALA, "https://en.wikipedia.org/wiki/Koala")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("african-lion", "hard"))
        self.assertIsNotNone(study_deck_for("african-lion", "zoologist"))
        giraffe = study_deck_for("reticulated-giraffe")
        self.assertEqual(giraffe["source"], WIKI_GIRAFFE)
        self.assertEqual(giraffe["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
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
        self.assertEqual(shipped_levels_for("zebra"), ("easy", "hard", "zoologist"))
        hippo = study_deck_for("nile-hippo")
        self.assertEqual(hippo["source"], WIKI_HIPPOPOTAMUS)
        self.assertEqual(hippo["talk_about"], list(TALK_ABOUT_HIPPO))
        self.assertEqual(hippo["push_further"], list(PUSH_FURTHER_HIPPO))
        self.assertEqual(shipped_levels_for("nile-hippo"), ("easy", "hard", "zoologist"))
        tiger = study_deck_for("sumatran-tiger")
        self.assertEqual(tiger["source"], WIKI_SUMATRAN_TIGER)
        self.assertEqual(tiger["talk_about"], list(TALK_ABOUT_TIGER))
        self.assertEqual(tiger["push_further"], list(PUSH_FURTHER_TIGER))
        self.assertEqual(shipped_levels_for("sumatran-tiger"), ("easy", "hard", "zoologist"))
        gorilla = study_deck_for("western-lowland-gorilla")
        self.assertEqual(gorilla["source"], WIKI_WESTERN_LOWLAND_GORILLA)
        self.assertEqual(gorilla["talk_about"], list(TALK_ABOUT_GORILLA))
        self.assertEqual(gorilla["push_further"], list(PUSH_FURTHER_GORILLA))
        self.assertEqual(shipped_levels_for("western-lowland-gorilla"), ("easy", "hard", "zoologist"))
        cheetah = study_deck_for("cheetah")
        self.assertEqual(cheetah["source"], WIKI_CHEETAH)
        self.assertEqual(cheetah["talk_about"], list(TALK_ABOUT_CHEETAH))
        self.assertEqual(cheetah["push_further"], list(PUSH_FURTHER_CHEETAH))
        self.assertEqual(shipped_levels_for("cheetah"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("cheetah", "hard"))
        self.assertIsNotNone(study_deck_for("cheetah", "zoologist"))
        panda = study_deck_for("red-panda")
        self.assertEqual(panda["source"], WIKI_RED_PANDA)
        self.assertEqual(panda["talk_about"], list(TALK_ABOUT_RED_PANDA))
        self.assertEqual(panda["push_further"], list(PUSH_FURTHER_RED_PANDA))
        self.assertEqual(shipped_levels_for("red-panda"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("red-panda", "hard"))
        self.assertIsNotNone(study_deck_for("red-panda", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "koala", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("card-study-pack", html)
        self.assertIn("Learn first", html)
        self.assertIn("<details class=\"study-teach\">", html)
        self.assertNotIn("<details class=\"study-teach\" open", html)
        self.assertIn("<summary class=\"study-teach-kicker\">", html)
        self.assertIn("tap to open", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        for prompt in TALK_ABOUT_KOALA + PUSH_FURTHER_KOALA:
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
        self.assertIn("Eucalyptus forests of eastern and southeastern Australia", html)
        self.assertIn("No — it is a marsupial (a pouch mammal), not a bear", html)
        self.assertIn("Facts from Wikipedia, Koala.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn("card-study-pack", html)
        self.assertNotIn("What do they eat?", html)
        self.assertNotIn("Where do wild koalas live?", html)
        sea = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", sea)
        self.assertNotIn("What do they eat?", sea)

    def test_published_koala_card_matches_easy_deck(self):
        html = KOALA.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertNotIn("Watch Live", main)
        self.assertNotIn("/field-pack/virtual-zoo/?from=card#habitat=koala", main)
        self.assertIn('class="card-hero-links no-print"', main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertNotIn('class="card-page-photo-link"', main)
        self.assertNotIn('aria-label="Watch Live: Koala"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=7", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "koala"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=42", html)
        self.assertIn("<details class=\"study-teach\">", main)
        self.assertNotIn("<details class=\"study-teach\" open", main)
        self.assertNotIn("<div class=\"study-teach\">", main)
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
        for prompt in TALK_ABOUT_KOALA + PUSH_FURTHER_KOALA:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("koala"),
            ["red-panda", "sumatran-tiger", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("koala")
        sheet = study_print_html(
            deck,
            name="Koala",
            emoji="🐨",
            photo="/field-pack/photos/koala.jpg?v=img2",
            photo_pos="50% 28%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/koala.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_KOALA, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("Eucalyptus forests of eastern and southeastern Australia", sheet)
        self.assertIn("No — it is a marsupial (a pouch mammal), not a bear", sheet)
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_KOALA + PUSH_FURTHER_KOALA:
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
        self.assertIn("details class=\"study-teach\"", study_js)
        self.assertIn("study-deepen", study_js)
        self.assertIn("is-wrong-pick", study_js)
        self.assertIn("FPStudyLevelName", study_js + STUDY_DATA_JS.read_text(encoding="utf-8"))

    def test_artifacts_include_koala_easy_hard_and_zoologist(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("koala", payload)
        self.assertIn("red-panda", payload)
        self.assertIn("cheetah", payload)
        self.assertIn("western-lowland-gorilla", payload)
        self.assertIn("sumatran-tiger", payload)
        self.assertIn("nile-hippo", payload)
        self.assertIn("zebra", payload)
        self.assertIn("galapagos-tortoise", payload)
        self.assertIn("caribbean-flamingo", payload)
        self.assertIn("african-penguin", payload)
        self.assertIn("african-elephant", payload)
        self.assertIn("reticulated-giraffe", payload)
        self.assertIn("african-lion", payload)
        koala = payload["koala"]
        self.assertEqual(koala["id"], "koala")
        self.assertEqual(set(koala["levels"]), {"easy", "hard", "zoologist"})
        easy = koala["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        hard = koala["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        zoo = koala["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("koala", data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertIn('"hard":"Park Ranger"', data_js)
        self.assertIn('"zoologist":"Zoologist"', data_js)
        self.assertEqual(set(payload["african-lion"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["reticulated-giraffe"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["african-elephant"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["african-penguin"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["caribbean-flamingo"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["galapagos-tortoise"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["zebra"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["nile-hippo"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["sumatran-tiger"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["western-lowland-gorilla"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["cheetah"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["red-panda"]["levels"]), {"easy", "hard", "zoologist"})

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
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(lion_html)))
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(giraffe_html)))
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(elephant_html)))
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(penguin_html)))
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(flamingo_html)))
        self.assertIn("Zoologist", _text(_main(flamingo_html)))
        tortoise_html = TORTOISE.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(tortoise_html)))
        self.assertIn("Zoologist", _text(_main(tortoise_html)))
        zebra_html = ZEBRA.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(zebra_html)))
        self.assertIn("Zoologist", _text(_main(zebra_html)))
        hippo_html = HIPPO.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(hippo_html)))
        self.assertIn("Zoologist", _text(_main(hippo_html)))
        tiger_html = TIGER.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(tiger_html)))
        self.assertIn("Park Ranger", _text(_main(tiger_html)))
        self.assertIn("Zoologist", _text(_main(tiger_html)))
        gorilla_html = GORILLA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(gorilla_html)))
        self.assertIn("Park Ranger", _text(_main(gorilla_html)))
        self.assertIn("Zoologist", _text(_main(gorilla_html)))
        cheetah_html = CHEETAH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(cheetah_html)))
        self.assertIn("Park Ranger", _text(_main(cheetah_html)))
        self.assertIn("Zoologist", _text(_main(cheetah_html)))
        panda_html = RED_PANDA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(panda_html)))
        self.assertIn("Park Ranger", _text(_main(panda_html)))
        self.assertIn("Zoologist", _text(_main(panda_html)))
        koala_html = KOALA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(koala_html)))
        self.assertIn("Park Ranger", _text(_main(koala_html)))
        self.assertIn("Zoologist", _text(_main(koala_html)))


if __name__ == "__main__":
    unittest.main()
