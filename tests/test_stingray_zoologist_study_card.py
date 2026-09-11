"""Stingray Zoologist study-card: no teach, 5 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_KELP_FOREST,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_MANTA_RAY_ZOOLOGIST,
    PUSH_FURTHER_OCTOPUS_ZOOLOGIST,
    PUSH_FURTHER_SEA_TURTLE_ZOOLOGIST,
    PUSH_FURTHER_SEAHORSE_ZOOLOGIST,
    PUSH_FURTHER_STARFISH_ZOOLOGIST,
    PUSH_FURTHER_STINGRAY_ZOOLOGIST,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY_ZOOLOGIST,
    TALK_ABOUT_OCTOPUS_ZOOLOGIST,
    TALK_ABOUT_SEA_TURTLE_ZOOLOGIST,
    TALK_ABOUT_SEAHORSE_ZOOLOGIST,
    TALK_ABOUT_STARFISH_ZOOLOGIST,
    TALK_ABOUT_STINGRAY_ZOOLOGIST,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
    WIKI_SEAHORSE,
    WIKI_STARFISH,
    WIKI_STINGRAY,
    correct_choice_text,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_talk_html,
    target_letter_for_deck_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
STINGRAY = FP / "cards" / "stingray" / "index.html"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
STARFISH = FP / "cards" / "starfish" / "index.html"
SEAHORSE = FP / "cards" / "seahorse" / "index.html"
SEA_TURTLE = FP / "cards" / "sea-turtle" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_SLOTS = 5
SIGNED_LETTERS = ("A", "B", "C", "A", "A")

ZOOLOGIST_STEMS = (
    "How broad is the stingray group Myliobatoidei, if we keep the family list soft?",
    "What is unusual about how a stingray stores its venom, compared with many other venomous animals?",
    "How should we talk about IUCN status for the GROUP card “stingray”?",
    "After the yolk sac is used up, how can a mother stingray keep feeding embryos inside her?",
    "How can a male stingray’s teeth differ from a female’s during the mating season?",
)

ZOOLOGIST_IDS = (
    "families-manta-soft",
    "venom-tissue-soft",
    "status-by-kind-soft",
    "uterine-milk-soft",
    "tooth-dimorphism-soft",
)

HARD_STEMS = (
    "Where do scientists place stingrays in the fish family tree, if we keep names soft?",
    "How can a stingray find prey it cannot see under its disc?",
    "How do stingrays power swimming with their pectoral “wings”?",
    "Do all stingrays live only in the ocean?",
    "When a stingray is buried and hunting, which breathing path keeps sand out of the mouth route?",
)

EASY_STEMS = (
    "What is a stingray’s skeleton mostly made of?",
    "What shape helps many stingrays hug the seafloor?",
    "Where are a stingray’s eyes and mouth?",
    "How do many bottom-living stingrays hide?",
    "What is the famous “sting” on many stingrays?",
    "What do many stingrays eat on the seafloor?",
    "How can a buried stingray keep breathing without gulping sandy water through its mouth?",
    "How do stingray babies usually arrive?",
    "About how many kinds of stingray are there, if we keep the count soft?",
    "Do stingrays usually chase and hunt people?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    " kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "Cartilage — tough and flexible, like a shark’s skeleton (soft)",
    "A flattened body with wide pectoral “wings” fused into a disc",
    "Eyes on top; mouth (and gill slots) on the underside",
    "They stir sand and settle under it, often leaving mainly eyes and tail showing",
    "A venomous spine (stinger / spinal blade) on the tail used for defense",
    "Mollusks, crustaceans, and sometimes small fish — many crush hard shells with strong jaws",
    "Openings called spiracles behind the eyes can draw clearer water in",
    "Born live after developing inside the mother (ovoviviparous soft) — litter size soft",
    "About two hundred known kinds worldwide (soft)",
    "No — they are not usually aggressive; stings happen mainly when a ray is stepped on or threatened",
    "Order Myliobatiformes (suborder Myliobatoidei) — cartilaginous rays related to sharks, not bony fish",
    "Smell plus electroreceptors (ampullae of Lorenzini) that sense tiny electrical signals, similar to sharks",
    "Two main styles — undulatory waves along thicker fins (often slower, bottom-living) or oscillatory wing-like flaps (often faster, open-water soft)",
    "No — river stingrays (and some whiptail kinds) live in fresh water; most others are marine (soft)",
    "Spiracles behind the eyes can draw clearer water in while the mouth stays out of the sediment path",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class StingrayZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("stingray", study_card_ids())
        self.assertEqual(shipped_levels_for("stingray"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("stingray", "hard"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("stingray", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_STINGRAY)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Stingray.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_STINGRAY_ZOOLOGIST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_STINGRAY_ZOOLOGIST))
        self.assertEqual(len(deck["questions"]), ZOOLOGIST_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, list(SIGNED_LETTERS))
        self.assertEqual(
            letters,
            [target_letter_for_deck_slot("stingray", "zoologist", i) for i in range(1, 6)],
        )
        self.assertEqual(letters.count("A"), 3)
        self.assertEqual(letters.count("B"), 1)
        self.assertEqual(letters.count("C"), 1)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("stingray", "zoologist")
        easy = study_deck_for("stingray", "easy")
        hard = study_deck_for("stingray", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("stingray", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 6)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("several families", correct_choice_text(questions[0]).lower())
        self.assertIn("mobulidae", correct_choice_text(questions[0]).lower())
        self.assertIn("manta", correct_choice_text(questions[0]).lower())
        self.assertIn("devil", correct_choice_text(questions[0]).lower())
        self.assertIn("tissue cells", correct_choice_text(questions[1]).lower())
        self.assertIn("gland", correct_choice_text(questions[1]).lower())
        self.assertIn("mucus", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("varies by kind", correct_choice_text(questions[2]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("uterine", correct_choice_text(questions[3]).lower())
        self.assertIn("milk", correct_choice_text(questions[3]).lower())
        self.assertIn("histotroph", correct_choice_text(questions[3]).lower())
        self.assertIn("placenta", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("pointed", correct_choice_text(questions[4]).lower())
        self.assertIn("cusp", correct_choice_text(questions[4]).lower())
        self.assertIn("dimorphism", correct_choice_text(questions[4]).lower())
        self.assertIn("season", correct_choice_text(questions[4]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])
        self.assertIn("myliobatoidei", blob.lower())
        self.assertIn("dasyatidae", blob.lower())
        self.assertIn("mobulidae", blob.lower())

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Myliobatoidei",
            "Mobulidae",
            "Dasyatidae",
            "Potamotrygonidae",
            "Myliobatidae",
            "histotroph",
            "cystatins",
            "galectin",
            "IUCN",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_STINGRAY_ZOOLOGIST + PUSH_FURTHER_STINGRAY_ZOOLOGIST:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_STINGRAY_ZOOLOGIST).lower()
        push = " ".join(PUSH_FURTHER_STINGRAY_ZOOLOGIST).lower()
        self.assertIn("letter", talk)
        self.assertIn("venom", talk)
        self.assertIn("yolk", talk)
        self.assertIn("manta", push)
        self.assertIn("teeth", push)
        self.assertIn("family", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("stingray", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "stingray", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_zoologist_print_is_answer_light_duplex(self):
        deck = study_deck_for("stingray", "zoologist")
        sheet = study_print_html(
            deck,
            name="Stingray",
            emoji="🐟",
            photo="/field-pack/photos/stingray.jpg?v=img2",
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
        for prompt in TALK_ABOUT_STINGRAY_ZOOLOGIST + PUSH_FURTHER_STINGRAY_ZOOLOGIST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_STINGRAY, sheet)
        self.assertIn("Facts from Wikipedia, Stingray.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("stingray", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        self.assertLess(html.find("study-foot"), html.find("study-explore"))
        self.assertIn(">0</span>/5", html)
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
        self.assertEqual(shipped_levels_for("octopus"), ("easy", "hard", "zoologist"))
        octo_zoo = study_deck_for("octopus", "zoologist")
        self.assertEqual(octo_zoo["source"], WIKI_OCTOPUS)
        octo_html = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("Zoologist", octo_html)
        self.assertEqual(octo_zoo["talk_about"], list(TALK_ABOUT_OCTOPUS_ZOOLOGIST))
        self.assertEqual(octo_zoo["push_further"], list(PUSH_FURTHER_OCTOPUS_ZOOLOGIST))
        self.assertEqual(shipped_levels_for("sea-turtle"), ("easy", "hard", "zoologist"))
        turtle_zoo = study_deck_for("sea-turtle", "zoologist")
        self.assertEqual(turtle_zoo["source"], WIKI_SEA_TURTLE)
        turtle_html = SEA_TURTLE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", turtle_html)
        self.assertEqual(turtle_zoo["talk_about"], list(TALK_ABOUT_SEA_TURTLE_ZOOLOGIST))
        self.assertEqual(turtle_zoo["push_further"], list(PUSH_FURTHER_SEA_TURTLE_ZOOLOGIST))
        self.assertEqual(shipped_levels_for("seahorse"), ("easy", "hard", "zoologist"))
        horse_zoo = study_deck_for("seahorse", "zoologist")
        self.assertEqual(horse_zoo["source"], WIKI_SEAHORSE)
        horse_html = SEAHORSE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", horse_html)
        self.assertEqual(horse_zoo["talk_about"], list(TALK_ABOUT_SEAHORSE_ZOOLOGIST))
        self.assertEqual(horse_zoo["push_further"], list(PUSH_FURTHER_SEAHORSE_ZOOLOGIST))
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        manta_zoo = study_deck_for("manta-ray", "zoologist")
        self.assertEqual(manta_zoo["source"], WIKI_MANTA_RAY)
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", manta_html)
        self.assertEqual(manta_zoo["talk_about"], list(TALK_ABOUT_MANTA_RAY_ZOOLOGIST))
        self.assertEqual(manta_zoo["push_further"], list(PUSH_FURTHER_MANTA_RAY_ZOOLOGIST))
        self.assertEqual(shipped_levels_for("starfish"), ("easy", "hard", "zoologist"))
        star_zoo = study_deck_for("starfish", "zoologist")
        self.assertEqual(star_zoo["source"], WIKI_STARFISH)
        star_html = STARFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", star_html)
        self.assertEqual(star_zoo["talk_about"], list(TALK_ABOUT_STARFISH_ZOOLOGIST))
        self.assertEqual(star_zoo["push_further"], list(PUSH_FURTHER_STARFISH_ZOOLOGIST))
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy", "hard", "zoologist"))
        jelly_zoo = study_deck_for("jellyfish", "zoologist")
        self.assertEqual(jelly_zoo["source"], WIKI_JELLYFISH)
        jelly_html = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", jelly_html)
        self.assertEqual(jelly_zoo["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(jelly_zoo["push_further"], list(PUSH_FURTHER_JELLYFISH))
        self.assertEqual(shipped_levels_for("kelp-forest"), ("easy", "hard", "zoologist"))
        kelp_zoo = study_deck_for("kelp-forest", "zoologist")
        self.assertEqual(kelp_zoo["source"], WIKI_KELP_FOREST)
        kelp_html = KELP.read_text(encoding="utf-8")
        self.assertIn("Zoologist", kelp_html)
        self.assertEqual(kelp_zoo["talk_about"], list(TALK_ABOUT_KELP_FOREST))
        self.assertEqual(kelp_zoo["push_further"], list(PUSH_FURTHER_KELP_FOREST))
        whale = WHALE_SHARK.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", whale)
        self.assertNotIn("What do they eat?", whale)
        self.assertNotIn("families-manta-soft", whale)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["stingray"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), ZOOLOGIST_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        self.assertEqual([q["correct"] for q in zoo["questions"]], list(SIGNED_LETTERS))
        self.assertIn("hard", payload["stingray"]["levels"])
        self.assertEqual(payload["stingray"]["levels"]["hard"]["teach"], [])
        self.assertEqual(payload["stingray"]["levels"]["easy"]["teach"], [
            "Flattened ocean fish with a skeleton of cartilage (related to sharks — soft)",
            "Eyes on top; mouth and gills on the underside",
            "Many hide under sand on the seafloor",
            "The tail can carry a venomous stinger used for defense",
            "Usually shy — they sting when threatened or stepped on, not when chasing people",
        ])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("families-manta-soft", data_js)
        self.assertIn("venom-tissue-soft", data_js)
        self.assertIn("uterine-milk-soft", data_js)
        self.assertIn("tooth-dimorphism-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = STINGRAY.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="hard"', html)
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
