"""Kelp-forest Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_CUTTLEFISH,
    PUSH_FURTHER_EEL,
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_KELP_FOREST,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_EEL,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    WIKI_CUTTLEFISH,
    WIKI_EEL,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
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
KELP = FP / "cards" / "kelp-forest" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
EEL = FP / "cards" / "eel" / "index.html"
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Where do kelps sit on the tree of life, if we keep that nest soft?",
    "How do kelp growth forms stack like a rainforest, if we keep those guilds soft?",
    "How fast can giant kelp add length in ideal light and nutrients, if we keep that rate soft?",
    "Where is kelp species richness often highest, if we keep that count soft?",
    "Why can a kelp forest and an urchin barren both last, if we keep that flip soft?",
    "Why doesn’t removing one kelp-forest predator mean the same outcome everywhere?",
    "When do urchins switch from drift kelp to live holdfasts, if we keep that buffer soft?",
    "How can El Niño–type events stress a kelp canopy, if we keep that climate link soft?",
    "What happened to some Northern California kelp in the 2010s, if we keep that snapshot local?",
    "How might kelp and other macroalgae store carbon, if we keep those amounts soft?",
)

ZOOLOGIST_IDS = (
    "ochrophyta-soft",
    "guild-architecture-soft",
    "macrocystis-rate-soft",
    "ne-pacific-richness-soft",
    "alternate-states-soft",
    "cascade-redundancy-soft",
    "drift-subsidy-soft",
    "enso-stress-soft",
    "heatwave-snapshot-soft",
    "blue-carbon-soft",
)

HARD_STEMS = (
    "What are “kelps,” if we keep the group soft?",
    "What is a kelp’s body called, and how does it take up nutrients?",
    "How can a kelp forest make “stories” like a land forest, if we keep those layers soft?",
    "How fast can giant kelp (Macrocystis) lengthen in ideal water, if we keep the rate soft?",
    "Where do especially productive kelp forests often sit, if we keep that ocean story soft?",
    "How can predators shape a kelp forest in a trophic cascade, if we keep that chain soft?",
    "What can overgrazing do to a lush kelp forest, if we keep that flip soft?",
    "Who helps control urchins, if we keep the regional difference soft?",
    "How can warm spells and storms stress a kelp canopy, if we keep those threats soft?",
    "How can people help keep predator–urchin–kelp balance, if we keep that care soft?",
)

EASY_STEMS = (
    "What is a kelp forest made of?",
    "Is kelp a land tree or plant?",
    "What does a kelp holdfast do?",
    "What are the stalk and leaf-like parts of kelp?",
    "How do many kinds of kelp lift their blades toward the sun?",
    "Where do kelp forests usually thrive?",
    "Who uses a kelp forest for food or shelter?",
    "How can sea otters help a kelp forest stay lush?",
    "How can people help kelp forests?",
    "Is a kelp forest a forest of trees?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "90%",
    "93%",
    "2 feet",
    "60 cm",
    "30 cm",
    " cm",
    " kg",
    " mph",
    "km/h",
    "20 species",
    "27 species",
)
REDO_THEMES = (
    "Dense stands of tall kelp form layered homes from a sunny surface canopy to a shaded seafloor",
    "No — kelp is brown algae that uses sunlight to make food, but it isn’t a true land plant",
    "A root-like holdfast grips rock so the kelp stays put — it does not drink nutrients like plant roots",
    "A flexible stalk (the stipe) holds up leaf-like blades that catch light",
    "Many kinds have gas-filled bladders that help the blades float toward sunlight",
    "Along cool, nutrient-rich coasts — often where deeper water rises and feeds the kelp (soft)",
    "Rockfish, snails, crabs, seals, otters, and seabirds can use the forest for food or shelter",
    "Sea otters eat urchins that chew kelp — when predators keep urchins in check, forests stay lush (soft)",
    "Protect cool coasts and the animals that stop urchins from mowing the kelp down (soft)",
    "No — it’s a forest of seaweed, even when giant kelp looks tree-tall",
    "Large brown algae in order Laminariales — genera like Macrocystis, Nereocystis, Laminaria, and Ecklonia (soft list)",
    "The body is a thallus — holdfast + stipe + fronds — and nutrients are taken across the blades, not through roots",
    "Surface canopy, mid understory, and seafloor prostrate kelps create sunny-to-shaded stories (soft)",
    "In cool, nutrient-rich water, giant kelp (Macrocystis) can lengthen tens of centimeters a day (exact rate stays soft)",
    "Where deep, cool, nutrient-rich water rises to the surface (upwelling) (soft)",
    "Predators (for example sea otters in Alaska) eat urchins → fewer urchins → kelp can recover; remove predators and urchins can boom (soft)",
    "It can flip the forest into rocky “urchin barrens” with little kelp — an alternate ecosystem state (soft)",
    "In some Pacific forests otters act as a keystone; elsewhere lobsters or large fishes help control urchins instead (soft)",
    "Heat waves, El Niño-type warm spells, and storms can weaken canopies and tip systems toward barrens (soft)",
    "Marine protected areas and careful fishing can help; forest status is place-by-place, not one letter (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class KelpForestZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("kelp-forest", study_card_ids())
        self.assertEqual(shipped_levels_for("kelp-forest"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("kelp-forest", "hard"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("kelp-forest", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_KELP_FOREST)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Kelp forest.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_KELP_FOREST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_KELP_FOREST))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("kelp-forest", "zoologist")
        easy = study_deck_for("kelp-forest", "easy")
        hard = study_deck_for("kelp-forest", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("kelp-forest", "zoologist")
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
        self.assertIn("ochrophyta", correct_choice_text(questions[0]).lower())
        self.assertIn("laminariales", correct_choice_text(questions[0]).lower())
        self.assertIn("stramenopile", correct_choice_text(questions[0]).lower())
        self.assertIn("plantae", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("macrocystis", correct_choice_text(questions[1]).lower())
        self.assertIn("alaria", correct_choice_text(questions[1]).lower())
        self.assertIn("eisenia", correct_choice_text(questions[1]).lower())
        self.assertIn("ecklonia", correct_choice_text(questions[1]).lower())
        self.assertIn("laminaria", correct_choice_text(questions[1]).lower())
        self.assertIn("rainforest", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("30", correct_choice_text(questions[2]))
        self.assertIn("60", correct_choice_text(questions[2]))
        self.assertIn("centimeter", correct_choice_text(questions[2]).lower())
        self.assertIn("year-round", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("northeastern pacific", correct_choice_text(questions[3]).lower())
        self.assertIn("california", correct_choice_text(questions[3]).lower())
        self.assertIn("aleutian", correct_choice_text(questions[3]).lower())
        self.assertIn("dozens", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("barren", correct_choice_text(questions[4]).lower())
        self.assertIn("persist", correct_choice_text(questions[4]).lower())
        self.assertIn("disease", correct_choice_text(questions[4]).lower())
        self.assertIn("predator", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("alaska", correct_choice_text(questions[5]).lower())
        self.assertIn("otter", correct_choice_text(questions[5]).lower())
        self.assertIn("southern california", correct_choice_text(questions[5]).lower())
        self.assertIn("lobster", correct_choice_text(questions[5]).lower())
        self.assertIn("sheephead", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("drift", correct_choice_text(questions[6]).lower())
        self.assertIn("holdfast", correct_choice_text(questions[6]).lower())
        self.assertIn("subsidy", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("el niño", correct_choice_text(questions[7]).lower())
        self.assertIn("nutrient-poor", correct_choice_text(questions[7]).lower())
        self.assertIn("storm", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("northern california", correct_choice_text(questions[8]).lower())
        self.assertIn("heatwave", correct_choice_text(questions[8]).lower())
        self.assertIn("urchin", correct_choice_text(questions[8]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("carbon", correct_choice_text(questions[9]).lower())
        self.assertIn("sink", correct_choice_text(questions[9]).lower())
        self.assertIn("offshore", correct_choice_text(questions[9]).lower())
        self.assertIn("estimate", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertNotIn("Least Concern", blob)
        self.assertNotIn("Endangered", blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Laminariales",
            "Macrocystis",
            "Eisenia",
            "Ecklonia",
            "stramenopile",
            "Aleutians",
            "sheephead",
            "macroalgae",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_KELP_FOREST + PUSH_FURTHER_KELP_FOREST:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_KELP_FOREST).lower()
        push = " ".join(PUSH_FURTHER_KELP_FOREST).lower()
        self.assertIn("ochrophyta", talk)
        self.assertIn("plant", talk)
        self.assertIn("barren", talk)
        self.assertIn("alaska", talk)
        self.assertIn("southern california", talk)
        self.assertIn("drift", push)
        self.assertIn("el niño", push)
        self.assertIn("heatwave", push)
        self.assertIn("iucn", push)
        self.assertIn("habitat", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("kelp-forest", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "kelp-forest", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="hard"', html)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_zoologist_print_is_answer_light_duplex(self):
        deck = study_deck_for("kelp-forest", "zoologist")
        sheet = study_print_html(
            deck,
            name="Kelp forest",
            emoji="🌿",
            photo="/field-pack/photos/kelp-forest.jpg?v=img2",
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
        for prompt in TALK_ABOUT_KELP_FOREST + PUSH_FURTHER_KELP_FOREST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_KELP_FOREST, sheet)
        self.assertIn("Facts from Wikipedia, Kelp forest.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("kelp-forest", "zoologist"))
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
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy", "hard", "zoologist"))
        jelly_zoo = study_deck_for("jellyfish", "zoologist")
        self.assertEqual(jelly_zoo["source"], WIKI_JELLYFISH)
        jelly_html = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", jelly_html)
        self.assertEqual(jelly_zoo["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(jelly_zoo["push_further"], list(PUSH_FURTHER_JELLYFISH))
        self.assertEqual(shipped_levels_for("eel"), ("easy", "hard", "zoologist"))
        eel_zoo = study_deck_for("eel", "zoologist")
        self.assertEqual(eel_zoo["source"], WIKI_EEL)
        eel_html = EEL.read_text(encoding="utf-8")
        self.assertIn("Zoologist", eel_html)
        self.assertEqual(eel_zoo["talk_about"], list(TALK_ABOUT_EEL))
        self.assertEqual(eel_zoo["push_further"], list(PUSH_FURTHER_EEL))
        self.assertEqual(shipped_levels_for("cuttlefish"), ("easy", "hard", "zoologist"))
        cuttle_zoo = study_deck_for("cuttlefish", "zoologist")
        self.assertEqual(cuttle_zoo["source"], WIKI_CUTTLEFISH)
        cuttle_html = CUTTLEFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", cuttle_html)
        self.assertEqual(cuttle_zoo["talk_about"], list(TALK_ABOUT_CUTTLEFISH))
        self.assertEqual(cuttle_zoo["push_further"], list(PUSH_FURTHER_CUTTLEFISH))
        octo = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", octo)
        self.assertNotIn("card-study-pack", octo)
        self.assertNotIn("ochrophyta-soft", octo)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["kelp-forest"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        self.assertIn("hard", payload["kelp-forest"]["levels"])
        self.assertEqual(payload["kelp-forest"]["levels"]["hard"]["teach"], [])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("ochrophyta-soft", data_js)
        self.assertIn("guild-architecture-soft", data_js)
        self.assertIn("drift-subsidy-soft", data_js)
        self.assertIn("blue-carbon-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = KELP.read_text(encoding="utf-8")
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
