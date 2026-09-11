"""Seahorse Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY_ZOOLOGIST,
    TALK_ABOUT_OCTOPUS_ZOOLOGIST,
    TALK_ABOUT_SEA_TURTLE_ZOOLOGIST,
    TALK_ABOUT_SEAHORSE_ZOOLOGIST,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
    WIKI_SEAHORSE,
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
SEAHORSE = FP / "cards" / "seahorse" / "index.html"
STINGRAY = FP / "cards" / "stingray" / "index.html"
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

ZOOLOGIST_STEMS = (
    "How fast did the tiger-tail seahorse (H. comes) genome change, if we keep that speed story soft?",
    "What tooth-gene loss is linked to the seahorse’s tube snout, if we keep those gene names soft?",
    "How is the loss of tbx4 linked to the “no hind fins” seahorse look, if we keep that gene story soft?",
    "How should we read IUCN letters for “seahorse,” if we keep those snapshots by kind?",
    "How does CITES treat Hippocampus trade, if we keep that rulebook soft?",
    "How big is the dried-seahorse trade, if we keep that count soft?",
    "Where do tiny pygmy seahorses sit on the family tree, if we keep that split soft?",
    "What do the oldest known seahorse fossils show, if we keep that timing soft?",
    "How does the pouch lining change during pregnancy, if we keep that nursery story soft?",
    "How is a seahorse’s prehensile tail built as armour, if we keep that materials story soft?",
)

ZOOLOGIST_IDS = (
    "rapid-genome-soft",
    "tooth-loss-scpp-soft",
    "tbx4-soft",
    "status-by-kind-soft",
    "cites-ii-soft",
    "trade-volume-soft",
    "pygmy-clade-soft",
    "miocene-stem-soft",
    "pseudoplacenta-soft",
    "square-tail-armour-soft",
)

HARD_STEMS = (
    "What family do seahorses sit in with pipefishes and seadragons, if we keep that tree soft?",
    "What jobs can a closed brood pouch do besides hold eggs, if we keep that nursery story kid-simple?",
    "Where do seahorse eggs meet sperm, if we keep that fertilization story soft?",
    "Why do seahorse pairs dance and greet for days before eggs move, if we keep those dance names soft?",
    "Do seahorses stay with one mate for life, if we keep that bond story soft?",
    "Why must a seahorse eat almost constantly, if we keep that gut story soft?",
    "How can a slow seahorse still ambush a copepod, if we keep that strike story soft?",
    "Why are seahorses such weak swimmers, if we keep that speed story soft?",
    "What homes do seahorses need — and what can hurt those places?",
    "How is the huge dried-seahorse trade handled, if we keep those rules soft?",
)

EASY_STEMS = (
    "Are seahorses a kind of fish?",
    "How does a seahorse swim, if we keep the fins simple?",
    "What does a seahorse’s tail do?",
    "Why does a seahorse’s head look horse-like, and how does it eat?",
    "What covers a seahorse’s body, if we keep the armour story soft?",
    "Who carries seahorse babies, and how?",
    "How can a seahorse hide in seagrass or coral?",
    "Where do seahorses usually live?",
    "Which animals are seahorses closely related to?",
    "Do seahorse moms always carry the babies?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "20 million",
    "20M",
    "20,000,000",
    "Least Concern",
    "Endangered",
    "Vulnerable",
    "Critically",
    " kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "Yes — small bony fish in genus Hippocampus, with many kinds (soft)",
    "A small dorsal fin pushes it along; pectoral fins help steer; it has no typical tail fin",
    "A square-ringed gripping tail holds seagrass, coral, or seaweed so they aren’t swept away",
    "A bent neck and tubular snout suck in tiny shrimp and other plankton",
    "Thin skin stretched over bony plate rings that help protect them",
    "The female places eggs in the male’s front pouch; he carries them until tiny fry are born",
    "It can change colour, and sometimes grow or shrink skin frills, to blend in",
    "In shallow seas — seagrass beds, reefs, mangroves, and some brackish lagoons",
    "Closely related to pipefish and seadragons (same family) — names stay light",
    "No — people think moms always carry babies, but in seahorses the father does the pouch care",
    "Family Syngnathidae — seahorses (Hippocampus) sit with pipefishes and seadragons; seahorses are highly modified pipefish that swim upright (soft)",
    "It can supply oxygen, control salt and water, remove waste, and add extra nutrients such as lipids and calcium beyond the egg yolk — a bit like a living nursery (soft)",
    "Inside the pouch after seawater briefly enters; then the pouch closes — physically inside, but more like outside-the-body chemistry (soft)",
    "Multi-day greetings and colour-bright dances help sync the pair before the female places eggs in the pouch (soft)",
    "Many species stay with one mate through a breeding season — not always for life — and some switch more readily (soft)",
    "Its gut is extremely simple and has no true stomach, so it must eat tiny crustaceans by suction almost all day (soft)",
    "A rapid snout pivot plus suction lets it ambush copepods at a surprising range for a slow fish (soft)",
    "They swim poorly, so they cling with a prehensile tail; the dwarf seahorse is often cited among the slowest fish (exact speed stays soft)",
    "They need seagrass, mangroves, reefs, and estuaries; coastal damage and destructive fishing can wipe those homes (soft)",
    "A huge dried-seahorse trade (medicine and curios) plus bycatch is controlled in international trade under CITES since 2002 (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class SeahorseZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("seahorse", study_card_ids())
        self.assertEqual(shipped_levels_for("seahorse"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("seahorse", "hard"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("seahorse", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_SEAHORSE)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Seahorse.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_SEAHORSE_ZOOLOGIST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_SEAHORSE_ZOOLOGIST))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("seahorse", "zoologist")
        easy = study_deck_for("seahorse", "easy")
        hard = study_deck_for("seahorse", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("seahorse", "zoologist")
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
        self.assertIn("comes", correct_choice_text(questions[0]).lower())
        self.assertIn("fastest-evolving", correct_choice_text(questions[0]).lower())
        self.assertIn("nature", correct_choice_text(questions[0]).lower())
        self.assertIn("2016", correct_choice_text(questions[0]))
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("scpp", correct_choice_text(questions[1]).lower())
        self.assertIn("enamel", correct_choice_text(questions[1]).lower())
        self.assertIn("teeth", correct_choice_text(questions[1]).lower())
        self.assertIn("snout", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("tbx4", correct_choice_text(questions[2]).lower())
        self.assertIn("zebrafish", correct_choice_text(questions[2]).lower())
        self.assertIn("pelvic", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("iucn", correct_choice_text(questions[3]).lower())
        self.assertIn("vu", correct_choice_text(questions[3]).lower())
        self.assertIn("en", correct_choice_text(questions[3]).lower())
        self.assertIn("dd", correct_choice_text(questions[3]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("cites", correct_choice_text(questions[4]).lower())
        self.assertIn("appendix ii", correct_choice_text(questions[4]).lower())
        self.assertIn("2002", correct_choice_text(questions[4]))
        self.assertIn("permit", correct_choice_text(questions[4]).lower())
        self.assertIn("appendix i", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("tens of millions", correct_choice_text(questions[5]).lower())
        self.assertIn("pill", correct_choice_text(questions[5]).lower())
        self.assertIn("juvenile", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("bargibanti", correct_choice_text(questions[6]).lower())
        self.assertIn("clade", correct_choice_text(questions[6]).lower())
        self.assertIn("gorgonian", correct_choice_text(questions[6]).lower())
        self.assertIn("hydroid", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("slovenia", correct_choice_text(questions[7]).lower())
        self.assertIn("13", correct_choice_text(questions[7]))
        self.assertIn("miocene", correct_choice_text(questions[7]).lower())
        self.assertIn("seagrass", correct_choice_text(questions[7]).lower())
        self.assertIn("oligocene", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("pseudoplacenta", correct_choice_text(questions[8]).lower())
        self.assertIn("remodel", correct_choice_text(questions[8]).lower())
        self.assertIn("immune", correct_choice_text(questions[8]).lower())
        self.assertIn("nutrient", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("square", correct_choice_text(questions[9]).lower())
        self.assertIn("bony", correct_choice_text(questions[9]).lower())
        self.assertIn("crush", correct_choice_text(questions[9]).lower())
        self.assertIn("grip", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "SCPP",
            "tbx4",
            "bargibanti",
            "Hippocampus comes",
            "pseudoplacenta",
            "Miocene",
            "Oligocene",
            "CITES",
            "Bateman",
            "phylogeography",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_SEAHORSE_ZOOLOGIST + PUSH_FURTHER_SEAHORSE_ZOOLOGIST:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_SEAHORSE_ZOOLOGIST).lower()
        push = " ".join(PUSH_FURTHER_SEAHORSE_ZOOLOGIST).lower()
        self.assertIn("appendix ii", talk)
        self.assertIn("safe forever", talk)
        self.assertIn("tooth", talk)
        self.assertIn("snout", talk)
        self.assertIn("pygmy", talk)
        self.assertIn("energy", push)
        self.assertIn("atlantic", push)
        self.assertIn("robot", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("seahorse", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "seahorse", "packTemplate": "animals"})
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
        deck = study_deck_for("seahorse", "zoologist")
        sheet = study_print_html(
            deck,
            name="Seahorse",
            emoji="🌊",
            photo="/field-pack/photos/seahorse.jpg?v=img2",
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
        for prompt in TALK_ABOUT_SEAHORSE_ZOOLOGIST + PUSH_FURTHER_SEAHORSE_ZOOLOGIST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_SEAHORSE, sheet)
        self.assertIn("Facts from Wikipedia, Seahorse.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("seahorse", "zoologist"))
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
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        manta_zoo = study_deck_for("manta-ray", "zoologist")
        self.assertEqual(manta_zoo["source"], WIKI_MANTA_RAY)
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", manta_html)
        self.assertEqual(manta_zoo["talk_about"], list(TALK_ABOUT_MANTA_RAY_ZOOLOGIST))
        self.assertEqual(manta_zoo["push_further"], list(PUSH_FURTHER_MANTA_RAY_ZOOLOGIST))
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
        ray = STINGRAY.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", ray)
        self.assertNotIn("card-study-pack", ray)
        self.assertNotIn("rapid-genome-soft", ray)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["seahorse"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        self.assertIn("hard", payload["seahorse"]["levels"])
        self.assertEqual(payload["seahorse"]["levels"]["hard"]["teach"], [])
        self.assertEqual(payload["seahorse"]["levels"]["easy"]["teach"], [
            "Small bony fish that swim upright (not mammals)",
            "Horse-like head and long snout for sucking tiny food",
            "A curled gripping tail holds seagrass, coral, or seaweed",
            "Dad carries the babies in a front pouch until they are born",
            "Thin skin over bony plates (not fish scales) — great at camouflage",
        ])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("rapid-genome-soft", data_js)
        self.assertIn("tooth-loss-scpp-soft", data_js)
        self.assertIn("pseudoplacenta-soft", data_js)
        self.assertIn("square-tail-armour-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = SEAHORSE.read_text(encoding="utf-8")
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
