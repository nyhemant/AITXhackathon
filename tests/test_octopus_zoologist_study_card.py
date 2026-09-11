"""Octopus Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY_ZOOLOGIST,
    TALK_ABOUT_OCTOPUS_ZOOLOGIST,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
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
OCTOPUS = FP / "cards" / "octopus" / "index.html"
SEAHORSE = FP / "cards" / "starfish" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "How do coleoid octopuses rewrite gene copies after they are written, if we keep that editing story soft?",
    "What makes blue-ringed octopuses (Hapalochlaena) the human danger outlier, if we keep that clinical story soft?",
    "What did the California two-spot octopus genome show, if we keep those gene families soft?",
    "How do modern octopod chromosomes compare with the vampire squid’s, if we keep that karyotype story soft?",
    "How should we read the old Cirrina (Cirromorphida) and Argonautoidea boxes, if we keep those names soft?",
    "Where do octopods arise in the fossil tree, if we keep that Jurassic timing soft?",
    "What do the optic glands do after breeding, if we keep that fade story soft?",
    "How should we read status for “octopus,” if we keep those snapshots by kind and fishery?",
    "What is unusual about octopus blood vessels, if we keep that circulation story soft?",
    "How did lab-welfare rules treat the common octopus, if we keep that legal story soft?",
)

ZOOLOGIST_IDS = (
    "rna-edit-soft",
    "ttx-blue-ring-soft",
    "genome-soft",
    "karyotype-soft",
    "cirrate-phylogeny-soft",
    "jurassic-stem-soft",
    "optic-gland-soft",
    "status-by-kind-soft",
    "closed-circulation-soft",
    "research-care-soft",
)

HARD_STEMS = (
    "What order do octopuses sit in, if we keep that group map soft?",
    "How is octopus skin stacked for colour and shine, if we keep those cell names soft?",
    "What happens to an octopus’s hearts during a hard jet swim?",
    "Why can octopus blood look blue, if we keep the chemistry soft?",
    "Where do most octopus nerve cells sit, if we keep that count soft?",
    "What clues show octopus intelligence, if we keep those stories soft?",
    "Are octopuses venomous — and which kinds are known to be deadly to people?",
    "What happens after an octopus lays eggs, if we keep that life story soft?",
    "How can an octopus open a crab or clam, if we keep the timing soft?",
    "How can some octopuses warn or fool a threat, if we keep those displays soft?",
)

EASY_STEMS = (
    "How many arms does an octopus have?",
    "Why can an octopus squeeze through a tiny gap?",
    "How can an octopus hide in plain sight?",
    "What can many octopuses do when a predator comes?",
    "What does an octopus use to eat, and what does it hunt?",
    "Where do many octopuses hide, and what clue might sit outside?",
    "What is special about octopus blood and hearts, if we keep it kid-simple?",
    "Where do octopuses live?",
    "How many kinds of octopus are there, if we keep the count soft?",
    "Do octopuses have tentacles?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "75 mmHg",
    "500 million",
    "71 kg",
    "157 lb",
    "380,000",
    "24 hour",
    "6,957",
    "276 million",
    "155 mya",
    "Least Concern",
    "Endangered",
    "Vulnerable",
    " kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "Eight sucker-lined arms — not the long clubbed tentacles of squid or cuttlefish",
    "Its soft body can pass through an opening only a little bigger than its hard beak",
    "Tiny colour cells (and friends) shift colour and pattern to match the scene",
    "Squirt a dark ink cloud and jet away",
    "A sharp beak at the centre of the arms; they hunt crabs, clams, snails, and fish",
    "In rock crevices, shells, and dens — leftovers often pile up outside as a midden",
    "Copper-based blue blood, and three hearts — two for the gills and one for the body",
    "In seas worldwide — reefs, seafloor, tide pools, and even deep water (not freshwater)",
    "About 300 known species, from tiny kinds to the giant Pacific octopus (soft)",
    "No — people say “tentacles,” but octopuses have arms with suckers all along. Squid and cuttlefish add two longer tentacles",
    "Order Octopoda — about 300 species; a traditional split is finned deep-sea Cirrina (cirri + fins) and typical Incirrina (most aquarium kinds) (soft)",
    "Colour cells (chromatophores) sit with reflective iridophores and white leucophores; skin muscles can also change texture (soft)",
    "Two gill hearts keep pushing blood through the gills, but the main (systemic) heart pauses — so long jet swims tire them fast",
    "A copper-based oxygen carrier (haemocyanin) is dissolved in the plasma — it works well in cold, low-oxygen water (soft)",
    "Roughly two-thirds of the neurons sit in the arms, so an arm can act with some independence from the central brain (soft)",
    "Maze and problem-solving tests show short- and long-term memory; the veined octopus uses coconut shells as portable shelters (tool use) (soft)",
    "All octopuses are venomous; only blue-ringed kinds are known to be deadly to humans if bitten (soft)",
    "The female guards the eggs in a den until they hatch, then typically stops eating and dies; males often fade after mating (soft)",
    "It can drill a shell and use toxic saliva to open crabs or clams (exact timing stays soft)",
    "Some mimic dangerous animals such as lionfish or sea snakes; blue-rings flash warning colours when threatened (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class OctopusZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("octopus", study_card_ids())
        self.assertEqual(shipped_levels_for("octopus"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("octopus", "hard"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("octopus", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_OCTOPUS)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Octopus.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_OCTOPUS_ZOOLOGIST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_OCTOPUS_ZOOLOGIST))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("octopus", "zoologist")
        easy = study_deck_for("octopus", "easy")
        hard = study_deck_for("octopus", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("octopus", "zoologist")
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
        self.assertIn("rna", correct_choice_text(questions[0]).lower())
        self.assertIn("adar", correct_choice_text(questions[0]).lower())
        self.assertIn("nervous", correct_choice_text(questions[0]).lower())
        self.assertIn("dna", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("hapalochlaena", correct_choice_text(questions[1]).lower())
        self.assertIn("tetrodotoxin", correct_choice_text(questions[1]).lower())
        self.assertIn("breath", correct_choice_text(questions[1]).lower())
        self.assertIn("antidote", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("protocadherin", correct_choice_text(questions[2]).lower())
        self.assertIn("c2h2", correct_choice_text(questions[2]).lower())
        self.assertIn("zinc-finger", correct_choice_text(questions[2]).lower())
        self.assertIn("sucker", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("fusion", correct_choice_text(questions[3]).lower())
        self.assertIn("vampire squid", correct_choice_text(questions[3]).lower())
        self.assertIn("basal", correct_choice_text(questions[3]).lower())
        self.assertIn("karyotype", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("cirrina", correct_choice_text(questions[4]).lower())
        self.assertIn("cirromorphida", correct_choice_text(questions[4]).lower())
        self.assertIn("argonautoidea", correct_choice_text(questions[4]).lower())
        self.assertIn("paraphyletic", correct_choice_text(questions[4]).lower())
        self.assertIn("basal", correct_choice_text(questions[4]).lower())
        self.assertIn("muensterelloidea", correct_choice_text(questions[5]).lower())
        self.assertIn("jurassic", correct_choice_text(questions[5]).lower())
        self.assertIn("vampyropoda", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("optic", correct_choice_text(questions[6]).lower())
        self.assertIn("maturation", correct_choice_text(questions[6]).lower())
        self.assertIn("spawning", correct_choice_text(questions[6]).lower())
        self.assertIn("extend", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("iucn", correct_choice_text(questions[7]).lower())
        self.assertIn("fished", correct_choice_text(questions[7]).lower())
        self.assertIn("farming", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("endothelium", correct_choice_text(questions[8]).lower())
        self.assertIn("haemocyanin", correct_choice_text(questions[8]).lower())
        self.assertIn("pressure", correct_choice_text(questions[8]).lower())
        self.assertIn("invertebrate", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("common octopus", correct_choice_text(questions[9]).lower())
        self.assertIn("cephalopod", correct_choice_text(questions[9]).lower())
        self.assertIn("welfare", correct_choice_text(questions[9]).lower())
        self.assertIn("intelligence", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertNotIn("Least Concern", blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "ADAR",
            "Hapalochlaena",
            "protocadherin",
            "C2H2",
            "Muensterelloidea",
            "Vampyropoda",
            "Cirromorphida",
            "Argonautoidea",
            "Grimpoteuthis",
            "endothelium",
            "tetrodotoxin",
            "TTX",
            "dsRNA",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_OCTOPUS_ZOOLOGIST + PUSH_FURTHER_OCTOPUS_ZOOLOGIST:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_OCTOPUS_ZOOLOGIST).lower()
        push = " ".join(PUSH_FURTHER_OCTOPUS_ZOOLOGIST).lower()
        self.assertIn("rna", talk)
        self.assertIn("dna", talk)
        self.assertIn("blue-ring", talk)
        self.assertIn("cirrina", talk)
        self.assertIn("paired rna", push)
        self.assertIn("dumbo", push)
        self.assertIn("catch", push)
        self.assertIn("robot", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("octopus", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "octopus", "packTemplate": "animals"})
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
        deck = study_deck_for("octopus", "zoologist")
        sheet = study_print_html(
            deck,
            name="Octopus",
            emoji="🐙",
            photo="/field-pack/photos/octopus.jpg?v=img2",
            photo_pos="50% 30%",
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
        for prompt in TALK_ABOUT_OCTOPUS_ZOOLOGIST + PUSH_FURTHER_OCTOPUS_ZOOLOGIST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_OCTOPUS, sheet)
        self.assertIn("Facts from Wikipedia, Octopus.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("octopus", "zoologist"))
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
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        manta_zoo = study_deck_for("manta-ray", "zoologist")
        self.assertEqual(manta_zoo["source"], WIKI_MANTA_RAY)
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", manta_html)
        self.assertEqual(manta_zoo["talk_about"], list(TALK_ABOUT_MANTA_RAY_ZOOLOGIST))
        self.assertEqual(manta_zoo["push_further"], list(PUSH_FURTHER_MANTA_RAY_ZOOLOGIST))
        horse = SEAHORSE.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", horse)
        self.assertNotIn("card-study-pack", horse)
        self.assertNotIn("rna-edit-soft", horse)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["octopus"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        self.assertIn("hard", payload["octopus"]["levels"])
        self.assertEqual(payload["octopus"]["levels"]["hard"]["teach"], [])
        self.assertEqual(payload["octopus"]["levels"]["easy"]["teach"], [
            "Soft-bodied sea animals with eight arms (molluscs, not fish)",
            "Arms have suckers that grip and help feel/taste what they touch",
            "They can change colour (and skin texture) to hide",
            "When scared, many squirt dark ink and jet away",
            "Almost no hard parts — they squeeze through tiny gaps (the beak is the hard bit)",
        ])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("rna-edit-soft", data_js)
        self.assertIn("ttx-blue-ring-soft", data_js)
        self.assertIn("optic-gland-soft", data_js)
        self.assertIn("research-care-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = OCTOPUS.read_text(encoding="utf-8")
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
