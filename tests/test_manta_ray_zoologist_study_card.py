"""Manta-ray Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_MANTA_RAY,
    PUSH_FURTHER_MANTA_RAY_ZOOLOGIST,
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_MANTA_RAY_ZOOLOGIST,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
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
MANTA = FP / "cards" / "manta-ray" / "index.html"
OCTOPUS = FP / "cards" / "seahorse" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Why did researchers sink the old genus Manta into Mobula, if we keep that 2017–18 tree soft?",
    "What third living manta was formally named in 2025, if we keep that discovery soft?",
    "How can gill-raker lobes catch food without clogging, if we keep that “ricochet” story soft?",
    "Where might much of a giant manta’s food come from, if we keep that isotope story soft?",
    "What is special about a manta’s brain, if we keep those warm-blood hints soft?",
    "What have captive giant mantas done at mirrors, if we keep that awareness hint debated?",
    "How do manta embryos get food inside the mother, if we keep that “milk” story soft?",
    "Why doesn’t overfishing one manta site refill quickly from elsewhere, if we keep that mix soft?",
    "How should we read IUCN letters for living mantas, if we keep those snapshots soft?",
    "Why might live manta tourism out-earn a dead manta’s gill plates, if we keep that trade-off soft?",
)

ZOOLOGIST_IDS = (
    "paraphyly-soft",
    "yarae-soft",
    "ricochet-filter-soft",
    "mesopelagic-diet-soft",
    "brain-retia-soft",
    "mirror-check-soft",
    "histotroph-soft",
    "fragmented-stocks-soft",
    "status-snapshots-soft",
    "trade-tourism-soft",
)

HARD_STEMS = (
    "Where do mantas sit in the genus tree now, if we keep that rename soft?",
    "What three kinds of manta do people name now, if we keep sizes and lives soft?",
    "What family do mantas share with other eagle and devil rays, if we keep that map soft?",
    "How do spongy gill-raker plates help a manta eat?",
    "How do cephalic fins and filter tissue work together, if we keep that feeding path soft?",
    "Why must mantas keep swimming to breathe, if we keep those spiracles soft?",
    "Why do manta populations recover slowly, if we keep that breeding story soft?",
    "How should we read IUCN letters for reef and giant oceanic mantas, if we keep those snapshots soft?",
    "Why can demand for dried gill rakers threaten mantas, if we keep that trade story kid-safe and soft?",
    "How do international agreements protect mantas — and what still matters near shore?",
)

EASY_STEMS = (
    "What do a manta’s broad fins work like?",
    "What sit beside a manta’s wide forward mouth?",
    "How do mantas gather their food?",
    "How big can a manta get, if we keep the size soft?",
    "How do reef mantas and giant oceanic mantas use the sea?",
    "How are baby mantas born?",
    "Why do mantas visit coral cleaning stations?",
    "What do mantas sometimes do at the surface — and do we know why?",
    "How can people help mantas?",
    "Do a manta’s horns mean it is dangerous?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "73%",
    "200 g",
    "$40",
    "$500",
    "$1 million",
    " kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "Broad triangular pectoral fins work like underwater wings",
    "Cephalic fins by the mouth look like horns — an old “devilfish” nickname",
    "They swim with mouths open; horn fins funnel plankton toward the gills",
    "Among the largest rays — disc width can reach several meters (soft)",
    "Reef mantas stay nearer coasts; giant oceanic mantas roam farther offshore (soft)",
    "Mothers carry pups inside and give birth to live young after a long pregnancy (soft)",
    "So little fish can pick off parasites",
    "They sometimes leap clear of the water — the reasons are still debated (soft)",
    "Keep warm seas healthy; fishing nets and demand for gill plates put pressure on slow-breeding mantas (soft)",
    "No — horns don’t mean danger. Mantas are gentle plankton-eaters, not man-eaters",
    "They now sit in genus Mobula with devil rays — the old genus Manta is treated as a junior synonym (soft)",
    "Reef (M. alfredi), giant oceanic (M. birostris), and Atlantic (M. yarae, newly named) — sizes and lifestyles differ (soft)",
    "They sit in Myliobatidae / Mobulinae with other eagle and devil rays (soft)",
    "Spongy gill-raker plates strain plankton from water as it exits the gill slots",
    "Cephalic fins unfurl as funnels; particles bounce or collect on filter tissue so the ray can keep swimming and feeding (soft)",
    "Spiracles are tiny or vestigial, so they need forward motion to push oxygenated water over the gills (soft)",
    "Pregnancy lasts over a year; usually one pup; years can pass between births — populations recover slowly (soft)",
    "Reef manta: Vulnerable snapshot; giant oceanic: Endangered snapshot — letters can change; Atlantic status is still settling (soft)",
    "Demand for dried gill rakers in some traditional markets drives targeted fishing — a top human threat (soft)",
    "Migratory-route agreements (CMS) protect them in international waters, but nearshore nets and bycatch still matter (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class MantaRayZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("manta-ray", study_card_ids())
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("manta-ray", "hard"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("manta-ray", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_MANTA_RAY)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Manta ray.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_MANTA_RAY_ZOOLOGIST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_MANTA_RAY_ZOOLOGIST))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("manta-ray", "zoologist")
        easy = study_deck_for("manta-ray", "easy")
        hard = study_deck_for("manta-ray", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("manta-ray", "zoologist")
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
        self.assertIn("mobula", correct_choice_text(questions[0]).lower())
        self.assertIn("paraphyletic", correct_choice_text(questions[0]).lower())
        self.assertIn("nested", correct_choice_text(questions[0]).lower())
        self.assertIn("2017", correct_choice_text(questions[0]))
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("yarae", correct_choice_text(questions[1]).lower())
        self.assertIn("atlantic", correct_choice_text(questions[1]).lower())
        self.assertIn("reef", correct_choice_text(questions[1]).lower())
        self.assertIn("oceanic", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("ricochet", correct_choice_text(questions[2]).lower())
        self.assertIn("gill-raker", correct_choice_text(questions[2]).lower())
        self.assertIn("pore", correct_choice_text(questions[2]).lower())
        self.assertIn("throat", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("isotope", correct_choice_text(questions[3]).lower())
        self.assertIn("mesopelagic", correct_choice_text(questions[3]).lower())
        self.assertIn("surface", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("brain", correct_choice_text(questions[4]).lower())
        self.assertIn("retia", correct_choice_text(questions[4]).lower())
        self.assertIn("warm", correct_choice_text(questions[4]).lower())
        self.assertIn("fish", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("mirror", correct_choice_text(questions[5]).lower())
        self.assertIn("contingency", correct_choice_text(questions[5]).lower())
        self.assertIn("debated", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("histotroph", correct_choice_text(questions[6]).lower())
        self.assertIn("egg", correct_choice_text(questions[6]).lower())
        self.assertIn("milk", correct_choice_text(questions[6]).lower())
        self.assertIn("placenta", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("aggregat", correct_choice_text(questions[7]).lower())
        self.assertIn("mix", correct_choice_text(questions[7]).lower())
        self.assertIn("overfish", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("alfredi", correct_choice_text(questions[8]).lower())
        self.assertIn("birostris", correct_choice_text(questions[8]).lower())
        self.assertIn("yarae", correct_choice_text(questions[8]).lower())
        self.assertIn("vu", correct_choice_text(questions[8]).lower())
        self.assertIn("en", correct_choice_text(questions[8]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("gill plate", correct_choice_text(questions[9]).lower())
        self.assertIn("tourism", correct_choice_text(questions[9]).lower())
        self.assertIn("lifetime", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "paraphyletic",
            "histotroph",
            "mesopelagic",
            "contingency",
            "retia",
            "yarae",
            "alfredi",
            "birostris",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_MANTA_RAY_ZOOLOGIST + PUSH_FURTHER_MANTA_RAY_ZOOLOGIST:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_MANTA_RAY_ZOOLOGIST).lower()
        push = " ".join(PUSH_FURTHER_MANTA_RAY_ZOOLOGIST).lower()
        self.assertIn("mobula", talk)
        self.assertIn("ricochet", talk)
        self.assertIn("vu", talk)
        self.assertIn("en", talk)
        self.assertIn("deeper", push)
        self.assertIn("mirror", push)
        self.assertIn("tourism", push)
        self.assertIn("gill plate", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("manta-ray", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "manta-ray", "packTemplate": "animals"})
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
        deck = study_deck_for("manta-ray", "zoologist")
        sheet = study_print_html(
            deck,
            name="Manta ray",
            emoji="🐟",
            photo="/field-pack/photos/manta-ray.jpg?v=img2",
            photo_pos="50% 48%",
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
        for prompt in TALK_ABOUT_MANTA_RAY_ZOOLOGIST + PUSH_FURTHER_MANTA_RAY_ZOOLOGIST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_MANTA_RAY, sheet)
        self.assertIn("Facts from Wikipedia, Manta ray.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("manta-ray", "zoologist"))
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
        self.assertEqual(shipped_levels_for("kelp-forest"), ("easy", "hard", "zoologist"))
        kelp_zoo = study_deck_for("kelp-forest", "zoologist")
        self.assertEqual(kelp_zoo["source"], WIKI_KELP_FOREST)
        kelp_html = KELP.read_text(encoding="utf-8")
        self.assertIn("Zoologist", kelp_html)
        self.assertEqual(kelp_zoo["talk_about"], list(TALK_ABOUT_KELP_FOREST))
        self.assertEqual(kelp_zoo["push_further"], list(PUSH_FURTHER_KELP_FOREST))
        octo = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", octo)
        self.assertNotIn("card-study-pack", octo)
        self.assertNotIn("paraphyly-soft", octo)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["manta-ray"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        self.assertIn("hard", payload["manta-ray"]["levels"])
        self.assertEqual(payload["manta-ray"]["levels"]["hard"]["teach"], [])
        self.assertEqual(payload["manta-ray"]["levels"]["easy"]["teach"], [
            "Huge flat rays with wing-like fins",
            "Horn-shaped fins beside a wide forward mouth",
            "Filter-feed on tiny drifting animals (plankton)",
            "Swim by flapping their “wings”",
            "Live in warm tropical and subtropical seas",
        ])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("paraphyly-soft", data_js)
        self.assertIn("ricochet-filter-soft", data_js)
        self.assertIn("histotroph-soft", data_js)
        self.assertIn("trade-tourism-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = MANTA.read_text(encoding="utf-8")
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
