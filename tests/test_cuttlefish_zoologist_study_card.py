"""Cuttlefish Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_LION,
    WIKI_CRAB,
    WIKI_CUTTLEFISH,
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
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
CRAB = FP / "cards" / "crab" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "What did Lupše and colleagues do to classic Sepia in 2023, if we keep the tree soft?",
    "What kind of shell is a cuttlebone, and how does gas move through it?",
    "How can cuttlefish eyes judge depth when they strike prey?",
    "Besides evening shallow-water glare, what debated idea links the W-shaped pupil to color-blind eyes?",
    "How does each chromatophore sac change size so quickly?",
    "How can a small male sneak past a guarding male to mate?",
    "Why do cephalopods need a closed blood system, unlike most molluscs?",
    "How should we read tetrodotoxin in flamboyant cuttlefish muscle?",
    "Why might the family have never reached the Americas, if we keep that map soft?",
    "How should we read the common cuttlefish IUCN letter next to local fishing and acid seas?",
)

ZOOLOGIST_IDS = (
    "2023-genera-soft",
    "phragmocone-soft",
    "dual-foveae-soft",
    "w-chromatic-soft",
    "neural-chromatophores-soft",
    "sexual-mimicry-soft",
    "closed-circulation-soft",
    "flamboyant-ttx-soft",
    "americas-cold-gate-soft",
    "officinalis-lc-soft",
)

HARD_STEMS = (
    "What family and order do living cuttlefish sit in?",
    "What internal shell sets cuttlefish apart from squid?",
    "How are the color-change cells stacked in cuttlefish skin?",
    "How can cuttlefish match backgrounds if they are mostly color-blind?",
    "Why do cuttlefish have three hearts?",
    "Why can cuttlefish blood look blue-green?",
    "Where are wild cuttlefish missing, if we keep the map soft?",
    "How deep do most cuttlefish live, if we keep the depth soft?",
    "What IUCN snapshot does the common cuttlefish (Sepia officinalis) carry?",
    "Why might acidifying seas matter for cuttlefish later?",
)

EASY_STEMS = (
    "What kind of animal is a cuttlefish?",
    "What does the cuttlebone help a cuttlefish do?",
    "How many arms and tentacles does a cuttlefish have?",
    "Why are cuttlefish nicknamed “chameleons of the sea”?",
    "How can a cuttlefish use ink when a predator comes?",
    "What do cuttlefish eyes look like in bright light?",
    "What do cuttlefish eat?",
    "About how long do cuttlefish usually live?",
    "How can people help cuttlefish?",
    "Are cuttlefish a kind of fish?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "120 species",
    "133",
    "114",
    "200 m",
    "400 m",
    "600 m",
    "1,000",
    " kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "A cephalopod — the same big group as squid, octopus, and nautilus",
    "A porous internal “bone” lets them float up or sink by adjusting gas and liquid",
    "Eight arms plus two longer tentacles with suckers to grab prey",
    "They can shift color and pattern in about a second",
    "A dark ink cloud or a look-alike decoy helps them escape",
    "Big eyes with a W-shaped pupil",
    "Crabs, shrimp, fish, and sometimes other cuttlefish",
    "Typical lifespan about 1–2 years",
    "Keep shallow coastal waters healthy so they have places to hunt and lay eggs",
    "No — they’re molluscs (soft bodies + a shell inside), closer to octopus than to tuna",
    "Family Sepiidae, order Sepiida — more than 100 living species (soft); taxonomy is being reshuffled",
    "A chambered cuttlebone made of aragonite; squid keep a thin gladius instead",
    "Pigment chromatophores sit over reflective iridophores over white leucophores",
    "They sense polarized light for contrast, which can help them match a scene even without full color vision (soft)",
    "Two branchial hearts push blood to the gills; one systemic heart serves the body",
    "It uses copper-based hemocyanin to carry oxygen, not iron hemoglobin",
    "They live around Africa, Europe, Asia, and Australia — and are totally absent from the Americas (soft)",
    "Mostly tropical and temperate shallow seas; some kinds reach roughly hundreds of meters (soft)",
    "Least Concern — fisheries pressure can be local, but the range is wide (soft snapshot)",
    "More acidic water is cited as a possible future stress on shells and eggs — still under study (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class CuttlefishZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("cuttlefish", study_card_ids())
        self.assertEqual(shipped_levels_for("cuttlefish"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("cuttlefish", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_CUTTLEFISH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Cuttlefish.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_CUTTLEFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_CUTTLEFISH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("cuttlefish", "zoologist")
        easy = study_deck_for("cuttlefish", "easy")
        hard = study_deck_for("cuttlefish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("cuttlefish", "zoologist")
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
        self.assertIn("acanthosepion", correct_choice_text(questions[0]).lower())
        self.assertIn("ascarosepion", correct_choice_text(questions[0]).lower())
        self.assertIn("rhombosepion", correct_choice_text(questions[0]).lower())
        self.assertIn("metasepia", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("phragmocone", correct_choice_text(questions[1]).lower())
        self.assertIn("siphuncle", correct_choice_text(questions[1]).lower())
        self.assertIn("spirula", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("foveae", correct_choice_text(questions[2]).lower())
        self.assertIn("forward", correct_choice_text(questions[2]).lower())
        self.assertIn("rearward", correct_choice_text(questions[2]).lower())
        self.assertIn("stereopsis", correct_choice_text(questions[2]).lower())
        self.assertIn("chromatic", correct_choice_text(questions[3]).lower())
        self.assertIn("wavelength", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("neural", correct_choice_text(questions[4]).lower())
        self.assertIn("500%", correct_choice_text(questions[4]))
        self.assertIn("iridophore", correct_choice_text(questions[4]).lower())
        self.assertIn("leucophore", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("mottle", correct_choice_text(questions[5]).lower())
        self.assertIn("egg", correct_choice_text(questions[5]).lower())
        self.assertIn("one side", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("hemocyanin", correct_choice_text(questions[6]).lower())
        self.assertIn("closed", correct_choice_text(questions[6]).lower())
        self.assertIn("hemoglobin", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("tetrodotoxin", correct_choice_text(questions[7]).lower())
        self.assertIn("poisonous", correct_choice_text(questions[7]).lower())
        self.assertIn("venom", correct_choice_text(questions[7]).lower())
        self.assertIn("species-by-species", correct_choice_text(questions[7]).lower())
        self.assertIn("old world", correct_choice_text(questions[8]).lower())
        self.assertIn("north atlantic", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("lc", correct_choice_text(questions[9]).lower())
        self.assertIn("overfishing", correct_choice_text(questions[9]).lower())
        self.assertIn("acidification", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Acanthosepion",
            "Ascarosepion",
            "Rhombosepion",
            "phragmocone",
            "siphuncle",
            "tetrodotoxin",
            "Lupše",
            "stereopsis",
            "foveae",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_CRAB + PUSH_FURTHER_CRAB
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_CUTTLEFISH + PUSH_FURTHER_CUTTLEFISH:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_CUTTLEFISH).lower()
        push = " ".join(PUSH_FURTHER_CUTTLEFISH).lower()
        self.assertIn("2023", talk)
        self.assertIn("sepia", talk)
        self.assertIn("sneak", talk)
        self.assertIn("closed", talk)
        self.assertIn("hemocyanin", talk)
        self.assertIn("metasepia", push)
        self.assertIn("one side", push)
        self.assertIn("poison", push)
        self.assertIn("venom", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("cuttlefish", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "cuttlefish", "packTemplate": "animals"})
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
        deck = study_deck_for("cuttlefish", "zoologist")
        sheet = study_print_html(
            deck,
            name="Cuttlefish",
            emoji="🦑",
            photo="/field-pack/photos/cuttlefish.jpg?v=img2",
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
        for prompt in TALK_ABOUT_CUTTLEFISH + PUSH_FURTHER_CUTTLEFISH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_CUTTLEFISH, sheet)
        self.assertIn("Facts from Wikipedia, Cuttlefish.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("cuttlefish", "zoologist"))
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
        self.assertEqual(shipped_levels_for("crab"), ("easy", "hard", "zoologist"))
        crab_zoo = study_deck_for("crab", "zoologist")
        self.assertEqual(crab_zoo["source"], WIKI_CRAB)
        crab_html = CRAB.read_text(encoding="utf-8")
        self.assertIn("Zoologist", crab_html)
        self.assertEqual(crab_zoo["talk_about"], list(TALK_ABOUT_CRAB))
        self.assertEqual(crab_zoo["push_further"], list(PUSH_FURTHER_CRAB))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("2023-genera-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["cuttlefish"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("2023-genera-soft", data_js)
        self.assertIn("phragmocone-soft", data_js)
        self.assertIn("officinalis-lc-soft", data_js)
        self.assertIn("flamboyant-ttx-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = CUTTLEFISH.read_text(encoding="utf-8")
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
