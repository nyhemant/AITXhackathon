"""Crab Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_CLOWNFISH,
    PUSH_FURTHER_CRAB,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CLOWNFISH,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_LION,
    WIKI_CLOWNFISH,
    WIKI_CRAB,
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
CRAB = FP / "cards" / "crab" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Which clade groups Anomura and Brachyura as sister taxa inside Decapoda?",
    "What does calling everyday “crab” a polyphyletic word mean?",
    "What traits did Keiler and colleagues use for a carcinised crab body plan?",
    "About how many living decapod lines has carcinisation hit, if we keep the list soft?",
    "Where do king crabs (Lithodidae) sit on molecular trees of hermit crabs?",
    "How do galatheoid squat lobsters sit next to porcelain crabs?",
    "What does decarcinisation mean for some crab lineages?",
    "Where do horseshoe crabs sit, and how should we read their IUCN letters?",
    "About how much of the marine crustacean catch do crabs make up?",
    "What makes the coconut crab (Birgus latro) unusual among hermit lineages?",
)

ZOOLOGIST_IDS = (
    "meiura-soft",
    "polyphyletic-soft",
    "keiler-body-plan-soft",
    "five-origins-soft",
    "lithodidae-nest-soft",
    "half-carcinized-soft",
    "decarcinisation-soft",
    "xiphosura-snapshot-soft",
    "fisheries-soft",
    "birgus-terrestrial-soft",
)

HARD_STEMS = (
    "What are “true crabs,” and what body plan do they share?",
    "Which look-alike crabs sit in sister group Anomura, not Brachyura?",
    "What does carcinisation say about crab-like bodies?",
    "Why might king crabs look like true crabs but not be Brachyura?",
    "What are porcelain crabs, and how can they escape?",
    "How is a hermit crab’s rear different from a true crab’s?",
    "Why aren’t horseshoe “crabs” decapod crabs at all?",
    "How wide can crab diets and freshwater homes spread?",
    "How far can crab sizes stretch if we keep exact records soft?",
    "Is there one IUCN letter for “crabs” as a group?",
)

EASY_STEMS = (
    "What covers a crab’s body?",
    "What do a crab’s front legs often end in?",
    "How do many crabs move?",
    "Where do many crabs like to hide?",
    "How does a crab grow bigger?",
    "Do all crabs look the same size and shape?",
    "Where can crabs live?",
    "What do many crabs eat?",
    "How can people help crabs?",
    "Are horseshoe crabs true crabs?",
)

PLAIN_LEVEL_LABELS = ("Easy",)
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "6,793",
    "6793",
    "3.7 m",
    "3.8 m",
    "4 m",
    "4.1 kg",
    "40 cm",
    "7,000",
    "7000",
    "1,300",
    "kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "A thick armored shell (exoskeleton) that protects the body",
    "Pincers (claws) they use for eating and defense",
    "Many scuttle sideways into rock crevices",
    "Rocky cracks, sand, and tide pools",
    "They shed the old shell so a bigger soft one can harden",
    "From tiny pea crabs to giant spider crabs — lots of shapes and sizes",
    "Most live in the ocean; some live in rivers or even on land",
    "Many are omnivores — algae, scraps, and small animals",
    "Keep shores and reefs healthy so crabs have places to hide and grow",
    "No — horseshoe “crabs” are a different kind of animal, closer to spiders than to true crabs",
    "Infraorder Brachyura — about 7,000 species (soft) — thick armored carapace, tail tucked under",
    "Hermit crabs, king crabs, porcelain crabs, and mole crabs sit in Anomura — they look crabby but aren’t Brachyura",
    "A crab-like body — flat shell, tucked abdomen, sideways scuttle — evolved more than once",
    "Evidence says they evolved from hermit-crab ancestors — an uneven abdomen is a soft clue",
    "Small, flattened Anomura near squat lobsters; they often drop a limb to escape (soft)",
    "Hermit crabs keep a soft rear and borrow empty snail shells — not the same body plan as true crabs",
    "They sit in Chelicerata with spiders and scorpions — different mouthparts and body layout",
    "Omnivores, herbivores, carnivores, filter-feeders, even some parasites; about 1,300 freshwater kinds (soft)",
    "Pea crabs may be only millimeters across; Japanese spider crab leg spans can reach several meters (soft)",
    "No — some common or fished kinds do fine; others (and horseshoe crabs as separate animals) face habitat or harvest pressure (soft snapshot)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class CrabZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("crab", study_card_ids())
        self.assertEqual(shipped_levels_for("crab"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("crab", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_CRAB)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Crab.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_CRAB))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_CRAB))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("crab", "zoologist")
        easy = study_deck_for("crab", "easy")
        hard = study_deck_for("crab", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("crab", "zoologist")
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
        self.assertIn("meiura", correct_choice_text(questions[0]).lower())
        self.assertIn("anomura", correct_choice_text(questions[0]).lower())
        self.assertIn("brachyura", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("polyphyletic", correct_choice_text(questions[1]).lower())
        self.assertIn("independently", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("carapace", correct_choice_text(questions[2]).lower())
        self.assertIn("plastron", correct_choice_text(questions[2]).lower())
        self.assertIn("pleon", correct_choice_text(questions[2]).lower())
        self.assertIn("keiler", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("five", correct_choice_text(questions[3]).lower())
        self.assertIn("king", correct_choice_text(questions[3]).lower())
        self.assertIn("porcelain", correct_choice_text(questions[3]).lower())
        self.assertIn("hairy stone", correct_choice_text(questions[3]).lower())
        self.assertIn("patagurus", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("lithodidae", correct_choice_text(questions[4]).lower())
        self.assertIn("paguridae", correct_choice_text(questions[4]).lower())
        self.assertIn("asymmetrical", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("half-carcinized", correct_choice_text(questions[5]).lower())
        self.assertIn("porcellanidae", correct_choice_text(questions[5]).lower())
        self.assertIn("squat", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("raninid", correct_choice_text(questions[6]).lower())
        self.assertIn("callichimaera", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("xiphosura", correct_choice_text(questions[7]).lower())
        self.assertIn("limulus", correct_choice_text(questions[7]).lower())
        self.assertIn("vu", correct_choice_text(questions[7]).lower())
        self.assertIn("tachypleus", correct_choice_text(questions[7]).lower())
        self.assertIn("en", correct_choice_text(questions[7]).lower())
        self.assertIn("20%", correct_choice_text(questions[8]))
        self.assertIn("1.5 million", correct_choice_text(questions[8]))
        self.assertIn("species-by-species", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("birgus", correct_choice_text(questions[9]).lower())
        self.assertIn("largest land", correct_choice_text(questions[9]).lower())
        self.assertIn("hermit", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Lithodidae",
            "Paguridae",
            "Porcellanidae",
            "Callichimaera",
            "Tachypleus",
            "tridentatus",
            "Birgus",
            "latro",
            "Patagurus",
            "Keiler",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_CLOWNFISH + PUSH_FURTHER_CLOWNFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_CRAB + PUSH_FURTHER_CRAB:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_CRAB).lower()
        push = " ".join(PUSH_FURTHER_CRAB).lower()
        self.assertIn("meiura", talk)
        self.assertIn("mixed family", talk)
        self.assertIn("fused", talk)
        self.assertIn("king crabs", talk)
        self.assertIn("hermit", talk)
        self.assertIn("squat lobster", push)
        self.assertIn("halfway", push)
        self.assertIn("porcelain", push)
        self.assertIn("reverse", push)
        self.assertIn("vu", push)
        self.assertIn("en", push)
        self.assertIn("species-by-species", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("crab", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "crab", "packTemplate": "animals"})
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
        deck = study_deck_for("crab", "zoologist")
        sheet = study_print_html(
            deck,
            name="Crab",
            emoji="🦀",
            photo="/field-pack/photos/crab.jpg?v=img2",
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
        for prompt in TALK_ABOUT_CRAB + PUSH_FURTHER_CRAB:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_CRAB, sheet)
        self.assertIn("Facts from Wikipedia, Crab.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("crab", "zoologist"))
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
        self.assertEqual(shipped_levels_for("clownfish"), ("easy", "hard", "zoologist"))
        clown_zoo = study_deck_for("clownfish", "zoologist")
        self.assertEqual(clown_zoo["source"], WIKI_CLOWNFISH)
        clown_html = CLOWNFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", clown_html)
        self.assertEqual(clown_zoo["talk_about"], list(TALK_ABOUT_CLOWNFISH))
        self.assertEqual(clown_zoo["push_further"], list(PUSH_FURTHER_CLOWNFISH))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", jelly)
        self.assertNotIn("What do they eat?", jelly)
        self.assertNotIn("meiura-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["crab"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("meiura-soft", data_js)
        self.assertIn("keiler-body-plan-soft", data_js)
        self.assertIn("birgus-terrestrial-soft", data_js)
        self.assertIn("xiphosura-snapshot-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = CRAB.read_text(encoding="utf-8")
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
