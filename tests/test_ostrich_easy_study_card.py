"""Ostrich Easy study-card: Junior Ranger teach + 10 MCQs (first deck)."""

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
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
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
    "The ostrich is the world’s largest living bird.",
    "Ostriches cannot fly — they run on strong legs.",
    "Wild ostriches live in Africa on open grassland / savanna.",
    "A baby ostrich is a chick.",
    "Males are mostly black-and-white; females are brownish-grey.",
)

STEMS = (
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

QIDS = (
    "biggest-bird",
    "run-dont-fly",
    "africa-home",
    "long-lookout",
    "boy-girl-look",
    "plant-first-snacks",
    "giant-eggs-soft",
    "chick",
    "soft-care",
    "head-in-sand-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Vulnerable",
    "Endangered",
    "Critically",
    "Least Concern",
    "Struthio",
    "camelus",
    "kg",
    "cm",
    "mph",
    "km/h",
)
# Explore more may name a later prompt; page HTML must stay JR-soft.
PAGE_BRITTLE = (
    "IUCN",
    "Vulnerable",
    "Endangered",
    "Critically",
    "Least Concern",
    "Struthio",
    "camelus",
    "kg",
    "cm",
    "mph",
    "km/h",
)
RESERVED = (
    "boom",
    "toes",
    "km/h",
    "mph",
    "IUCN",
    "Least Concern",
    "egg kg",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class OstrichEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_with_park_ranger_and_zoologist(self):
        self.assertIn("ostrich", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("ostrich"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("ostrich", "hard"))
        self.assertIsNotNone(study_deck_for("ostrich", "zoologist"))
        deck = study_deck_for("ostrich")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "ostrich")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_OSTRICH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Ostrich.")
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_OSTRICH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_OSTRICH))
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
        self.assertIn("largest", blob.lower())
        self.assertIn("fly", blob.lower())
        self.assertIn("africa", blob.lower())
        self.assertIn("grassland", blob.lower())
        self.assertIn("savanna", blob.lower())
        self.assertIn("neck", blob.lower())
        self.assertIn("black", blob.lower())
        self.assertIn("seeds", blob.lower())
        self.assertIn("egg", blob.lower())
        self.assertIn("chick", blob.lower())
        self.assertIn("sand", blob.lower())
        self.assertEqual(WIKI_OSTRICH, "https://en.wikipedia.org/wiki/Ostrich")

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
        koala = study_deck_for("koala")
        self.assertEqual(koala["source"], WIKI_KOALA)
        self.assertEqual(koala["talk_about"], list(TALK_ABOUT_KOALA))
        self.assertEqual(koala["push_further"], list(PUSH_FURTHER_KOALA))
        self.assertEqual(shipped_levels_for("koala"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("koala", "hard"))
        self.assertIsNotNone(study_deck_for("koala", "zoologist"))
        chimp = study_deck_for("chimpanzee")
        self.assertEqual(chimp["source"], WIKI_CHIMPANZEE)
        self.assertEqual(chimp["talk_about"], list(TALK_ABOUT_CHIMPANZEE))
        self.assertEqual(chimp["push_further"], list(PUSH_FURTHER_CHIMPANZEE))
        self.assertEqual(shipped_levels_for("chimpanzee"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("chimpanzee", "hard"))
        self.assertIsNotNone(study_deck_for("chimpanzee", "zoologist"))
        orang = study_deck_for("orangutan")
        self.assertEqual(orang["source"], WIKI_ORANGUTAN)
        self.assertEqual(orang["talk_about"], list(TALK_ABOUT_ORANGUTAN))
        self.assertEqual(orang["push_further"], list(PUSH_FURTHER_ORANGUTAN))
        self.assertEqual(shipped_levels_for("orangutan"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("orangutan", "hard"))
        self.assertIsNotNone(study_deck_for("orangutan", "zoologist"))
        giant = study_deck_for("giant-panda")
        self.assertEqual(giant["source"], WIKI_GIANT_PANDA)
        self.assertEqual(giant["talk_about"], list(TALK_ABOUT_GIANT_PANDA))
        self.assertEqual(giant["push_further"], list(PUSH_FURTHER_GIANT_PANDA))
        self.assertEqual(shipped_levels_for("giant-panda"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("giant-panda", "hard"))
        self.assertIsNotNone(study_deck_for("giant-panda", "zoologist"))
        lemur = study_deck_for("ring-tailed-lemur")
        self.assertEqual(lemur["source"], WIKI_RING_TAILED_LEMUR)
        self.assertEqual(lemur["talk_about"], list(TALK_ABOUT_RING_TAILED_LEMUR))
        self.assertEqual(lemur["push_further"], list(PUSH_FURTHER_RING_TAILED_LEMUR))
        self.assertEqual(shipped_levels_for("ring-tailed-lemur"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("ring-tailed-lemur", "hard"))
        self.assertIsNotNone(study_deck_for("ring-tailed-lemur", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "ostrich", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_OSTRICH + PUSH_FURTHER_OSTRICH:
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
        self.assertIn("The tallest and heaviest living bird", html)
        self.assertIn(
            "No — they do not bury their heads; when hiding they may press head and neck flat so they look like a mound",
            html,
        )
        self.assertIn("Facts from Wikipedia, Ostrich.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "jellyfish", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("What kind of living bird is the ostrich?", html)
        sea = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", sea)
        self.assertNotIn("card-study-pack", sea)

    def test_published_ostrich_card_matches_easy_deck(self):
        html = OSTRICH.read_text(encoding="utf-8")
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
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "ostrich"', html)
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
        for prompt in TALK_ABOUT_OSTRICH + PUSH_FURTHER_OSTRICH:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("ostrich"),
            ["caribbean-flamingo", "african-penguin", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("ostrich")
        sheet = study_print_html(
            deck,
            name="Ostrich",
            emoji="🪶",
            photo="/field-pack/photos/ostrich.jpg?v=img2",
            photo_pos="50% 15%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/ostrich.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_OSTRICH, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("The tallest and heaviest living bird", sheet)
        self.assertIn(
            "No — they do not bury their heads; when hiding they may press head and neck flat so they look like a mound",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_OSTRICH + PUSH_FURTHER_OSTRICH:
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

    def test_artifacts_include_ostrich_easy_hard_and_zoologist(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("ostrich", payload)
        self.assertIn("ring-tailed-lemur", payload)
        self.assertIn("giant-panda", payload)
        self.assertIn("orangutan", payload)
        self.assertIn("chimpanzee", payload)
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
        bird = payload["ostrich"]
        self.assertEqual(bird["id"], "ostrich")
        self.assertEqual(set(bird["levels"]), {"easy", "hard", "zoologist"})
        easy = bird["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        hard = bird["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        zoo = bird["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("ostrich", data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertIn('"hard":"Park Ranger"', data_js)
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
        self.assertEqual(set(payload["koala"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["chimpanzee"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["orangutan"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["giant-panda"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["ring-tailed-lemur"]["levels"]), {"easy", "hard", "zoologist"})

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
        red_html = RED_PANDA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(red_html)))
        self.assertIn("Park Ranger", _text(_main(red_html)))
        self.assertIn("Zoologist", _text(_main(red_html)))
        koala_html = KOALA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(koala_html)))
        self.assertIn("Park Ranger", _text(_main(koala_html)))
        self.assertIn("Zoologist", _text(_main(koala_html)))
        chimp_html = CHIMPANZEE.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(chimp_html)))
        self.assertIn("Park Ranger", _text(_main(chimp_html)))
        self.assertIn("Zoologist", _text(_main(chimp_html)))
        orang_html = ORANGUTAN.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(orang_html)))
        self.assertIn("Park Ranger", _text(_main(orang_html)))
        self.assertIn("Zoologist", _text(_main(orang_html)))
        panda_html = GIANT_PANDA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(panda_html)))
        self.assertIn("Park Ranger", _text(_main(panda_html)))
        self.assertIn("Zoologist", _text(_main(panda_html)))
        lemur_html = LEMUR.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(lemur_html)))
        self.assertIn("Park Ranger", _text(_main(lemur_html)))
        self.assertIn("Zoologist", _text(_main(lemur_html)))
        ostrich_html = OSTRICH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(ostrich_html)))
        self.assertIn("Park Ranger", _text(_main(ostrich_html)))
        self.assertIn("Zoologist", _text(_main(ostrich_html)))


if __name__ == "__main__":
    unittest.main()
