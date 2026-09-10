"""Eel Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_CRAB,
    PUSH_FURTHER_CUTTLEFISH,
    PUSH_FURTHER_EEL,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_EEL,
    TALK_ABOUT_LION,
    WIKI_CRAB,
    WIKI_CUTTLEFISH,
    WIKI_EEL,
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
EEL = FP / "cards" / "eel" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
CRAB = FP / "cards" / "crab" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Where do true eels sit among bony fishes, if we keep the superorder soft?",
    "Which major living clades sit inside Anguilliformes, if we keep the names soft?",
    "Where might freshwater Anguilla have come from, if we keep that origin soft?",
    "What did Johannes Schmidt show about eel spawning, if we keep that history soft?",
    "How do European and American eels behave as breeding pools, if we keep that mix soft?",
    "How often do silver eels spawn, if we keep that life-history soft?",
    "Which group is the sister clade to true eels, and which “eels” are only look-alikes?",
    "Where does the electric eel (Electrophorus) sit, if we keep that tree soft?",
    "How should we read Anguilla IUCN letters next to marine eel families?",
    "How do barriers and trade stack pressure on threatened Anguilla, if we keep that story soft?",
)

ZOOLOGIST_IDS = (
    "elopomorpha-soft",
    "suborder-tree-soft",
    "deep-sea-origin-soft",
    "schmidt-sargasso-soft",
    "panmixia-soft",
    "semelparity-soft",
    "sister-notacanth-soft",
    "gymnotiformes-soft",
    "status-snapshots-soft",
    "barriers-trade-soft",
)

HARD_STEMS = (
    "What order do true eels belong to, if we keep the counts soft?",
    "Which familiar families sit inside true eels?",
    "How do freshwater eels (Anguilla) use rivers and the ocean to spawn?",
    "Where do European and American freshwater eels spawn, if we keep that map soft?",
    "What life-stage names can a freshwater eel pass through before the ocean return?",
    "How can elvers reach habitat upstream of weirs and dams?",
    "Is there one IUCN letter for all eels?",
    "What extra stress sits on freshwater eels besides fishing and farms?",
    "Why aren’t swamp eels and electric eels true eels?",
    "How marine are true eels, if we keep the freshwater exception soft?",
)

EASY_STEMS = (
    "What is special about an eel’s body?",
    "Which fins do true eels usually skip?",
    "How do eels usually swim?",
    "How many kinds of true eels are there, if we keep the count soft?",
    "Where do most true eels live?",
    "What is an eel’s first baby stage?",
    "What do eel larvae become as they grow?",
    "Where do many eels hide, and when are they active?",
    "How can people help young eels?",
    "Are electric “eels” true eels?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "164",
    "1000 species",
    "1,000",
    "8 suborders",
    "20 families",
    "1920",
    "1921",
    "1922",
    " kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "A stretchy, ribbon-like body with an almost continuous fin along the back and belly",
    "No pelvic fins; many also lack pectoral fins",
    "They send waves down the body — and can reverse the wave to go backward",
    "Morays, congers, garden eels, freshwater eels — about a thousand species (soft)",
    "Most are marine; a few (genus Anguilla) spend years in rivers, then return to the sea",
    "A flat, transparent “leaf” larva that drifts in the open ocean",
    "Clear glass eels, then little elvers",
    "Many are night-active and tuck into sand, mud, or rock holes",
    "Keep coasts healthy and river paths open so young eels can reach growing places",
    "No — they’re South American knifefish, not Anguilliformes",
    "Order Anguilliformes — about eight suborders, about twenty families, and about a thousand species (soft)",
    "Muraenidae (morays), Congridae (congers and garden eels), Ophichthidae (snake eels), and Anguillidae (freshwater eels)",
    "They grow in rivers and lakes, then migrate to the ocean to spawn — the opposite of salmon (catadromy, soft)",
    "They spawn in the Sargasso Sea; larvae then drift on currents toward the continents (soft)",
    "Leptocephalus → glass eel → elver → yellow eel → silver eel, then the ocean return (soft names)",
    "They may climb weirs, dam walls, and waterfalls to reach upstream habitat (soft)",
    "No — letters are species-specific: European eel is a CR snapshot, American and Japanese EN, short-finned NT (soft)",
    "They are heavily fished and farmed in Asia and Europe; barriers and habitat loss add stress (soft)",
    "They evolved long bodies separately — swamp eels and electric eels are not Anguilliformes (soft)",
    "The vast majority stay ocean-only; genus Anguilla is the famous freshwater exception (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class EelZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("eel", study_card_ids())
        self.assertEqual(shipped_levels_for("eel"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("eel", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_EEL)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Eel.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_EEL))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_EEL))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("eel", "zoologist")
        easy = study_deck_for("eel", "easy")
        hard = study_deck_for("eel", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("eel", "zoologist")
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
        self.assertIn("elopomorpha", correct_choice_text(questions[0]).lower())
        self.assertIn("tarpon", correct_choice_text(questions[0]).lower())
        self.assertIn("bonefish", correct_choice_text(questions[0]).lower())
        self.assertIn("leptocephalus", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("anguilloidei", correct_choice_text(questions[1]).lower())
        self.assertIn("congroidei", correct_choice_text(questions[1]).lower())
        self.assertIn("muraenoidei", correct_choice_text(questions[1]).lower())
        self.assertIn("saccopharyngoidei", correct_choice_text(questions[1]).lower())
        self.assertIn("gulper", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("inoue", correct_choice_text(questions[2]).lower())
        self.assertIn("deep-ocean", correct_choice_text(questions[2]).lower())
        self.assertIn("ancestor", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("schmidt", correct_choice_text(questions[3]).lower())
        self.assertIn("smaller", correct_choice_text(questions[3]).lower())
        self.assertIn("sargasso", correct_choice_text(questions[3]).lower())
        self.assertIn("spawn", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("panmixia", correct_choice_text(questions[4]).lower())
        self.assertIn("mixed", correct_choice_text(questions[4]).lower())
        self.assertIn("overlapping", correct_choice_text(questions[4]).lower())
        self.assertIn("sargasso", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("once", correct_choice_text(questions[5]).lower())
        self.assertIn("die", correct_choice_text(questions[5]).lower())
        self.assertIn("semelparity", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("notacanthiformes", correct_choice_text(questions[6]).lower())
        self.assertIn("sister", correct_choice_text(questions[6]).lower())
        self.assertIn("swamp", correct_choice_text(questions[6]).lower())
        self.assertIn("electric", correct_choice_text(questions[6]).lower())
        self.assertIn("look-alike", correct_choice_text(questions[6]).lower())
        self.assertIn("electrophorus", correct_choice_text(questions[7]).lower())
        self.assertIn("gymnotiformes", correct_choice_text(questions[7]).lower())
        self.assertIn("knifefish", correct_choice_text(questions[7]).lower())
        self.assertIn("catfish", correct_choice_text(questions[7]).lower())
        self.assertIn("carp", correct_choice_text(questions[7]).lower())
        self.assertIn("anguilliformes", correct_choice_text(questions[7]).lower())
        self.assertIn("anguilla", correct_choice_text(questions[8]).lower())
        self.assertIn("cr", correct_choice_text(questions[8]).lower())
        self.assertIn("rostrata", correct_choice_text(questions[8]).lower())
        self.assertIn("japonica", correct_choice_text(questions[8]).lower())
        self.assertIn("en", correct_choice_text(questions[8]).lower())
        self.assertIn("australis", correct_choice_text(questions[8]).lower())
        self.assertIn("nt", correct_choice_text(questions[8]).lower())
        self.assertIn("marine", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("dam", correct_choice_text(questions[9]).lower())
        self.assertIn("weir", correct_choice_text(questions[9]).lower())
        self.assertIn("glass-eel", correct_choice_text(questions[9]).lower())
        self.assertIn("aquaculture", correct_choice_text(questions[9]).lower())
        self.assertIn("anguilla", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Notacanthiformes",
            "Electrophorus",
            "Saccopharyngoidei",
            "Anguilloidei",
            "Congroidei",
            "Muraenoidei",
            "Inoue",
            "rostrata",
            "japonica",
            "australis",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_CUTTLEFISH + PUSH_FURTHER_CUTTLEFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_EEL + PUSH_FURTHER_EEL:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_EEL).lower()
        push = " ".join(PUSH_FURTHER_EEL).lower()
        self.assertIn("elopomorpha", talk)
        self.assertIn("leptocephalus", talk)
        self.assertIn("sargasso", talk)
        self.assertIn("panmixia", talk)
        self.assertIn("cr", talk)
        self.assertIn("en", talk)
        self.assertIn("anguilla", talk)
        self.assertIn("deep-ocean", push)
        self.assertIn("once", push)
        self.assertIn("die", push)
        self.assertIn("gymnotiformes", push)
        self.assertIn("anguilliformes", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("eel", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "eel", "packTemplate": "animals"})
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
        deck = study_deck_for("eel", "zoologist")
        sheet = study_print_html(
            deck,
            name="Eel",
            emoji="🐍",
            photo="/field-pack/photos/eel.jpg?v=img2",
            photo_pos="50% 35%",
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
        for prompt in TALK_ABOUT_EEL + PUSH_FURTHER_EEL:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_EEL, sheet)
        self.assertIn("Facts from Wikipedia, Eel.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("eel", "zoologist"))
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
        self.assertEqual(shipped_levels_for("cuttlefish"), ("easy", "hard", "zoologist"))
        cuttle_zoo = study_deck_for("cuttlefish", "zoologist")
        self.assertEqual(cuttle_zoo["source"], WIKI_CUTTLEFISH)
        cuttle_html = CUTTLEFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", cuttle_html)
        self.assertEqual(cuttle_zoo["talk_about"], list(TALK_ABOUT_CUTTLEFISH))
        self.assertEqual(cuttle_zoo["push_further"], list(PUSH_FURTHER_CUTTLEFISH))
        self.assertEqual(shipped_levels_for("crab"), ("easy", "hard", "zoologist"))
        crab_zoo = study_deck_for("crab", "zoologist")
        self.assertEqual(crab_zoo["source"], WIKI_CRAB)
        crab_html = CRAB.read_text(encoding="utf-8")
        self.assertIn("Zoologist", crab_html)
        self.assertEqual(crab_zoo["talk_about"], list(TALK_ABOUT_CRAB))
        self.assertEqual(crab_zoo["push_further"], list(PUSH_FURTHER_CRAB))
        jelly = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("elopomorpha-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["eel"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("elopomorpha-soft", data_js)
        self.assertIn("schmidt-sargasso-soft", data_js)
        self.assertIn("barriers-trade-soft", data_js)
        self.assertIn("gymnotiformes-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = EEL.read_text(encoding="utf-8")
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
