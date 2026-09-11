"""Starfish Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY_ZOOLOGIST,
    TALK_ABOUT_OCTOPUS_ZOOLOGIST,
    TALK_ABOUT_SEA_TURTLE_ZOOLOGIST,
    TALK_ABOUT_SEAHORSE_ZOOLOGIST,
    TALK_ABOUT_STARFISH_ZOOLOGIST,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
    WIKI_SEAHORSE,
    WIKI_STARFISH,
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
STARFISH = FP / "cards" / "starfish" / "index.html"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
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

ZOOLOGIST_STEMS = (
    "How do living sea stars split at the order level, if we keep the count soft?",
    "What do scientists still debate about sea-star family trees?",
    "What lets a sea star shed an arm in seconds without using big muscles to tear it off?",
    "What experimental clue shows arm-shedding can be chemically triggered in sea stars?",
    "What helps pull an everted cardiac stomach back inside after feeding?",
    "What is sea star wasting disease, in soft kid-safe terms?",
    "How should we talk about IUCN status for the GROUP card “starfish”?",
    "Why is the Northern Pacific seastar (Asterias amurensis) famous in invasion biology?",
    "How do living sea stars relate to ancient Paleozoic star-shaped echinoderms?",
    "Can a sea star’s body wall only be “hard bone” or “floppy muscle”?",
)

ZOOLOGIST_IDS = (
    "seven-orders-soft",
    "phylogeny-soft",
    "catch-connective-soft",
    "autotomy-factor-soft",
    "stomach-neuropeptide-soft",
    "wasting-soft",
    "status-by-kind-soft",
    "northern-pacific-soft",
    "neoasteroidea-soft",
    "stiffness-myth",
)

HARD_STEMS = (
    "What scientific class do sea stars belong to, if we keep the family tree soft?",
    "What powers a sea star’s tube feet?",
    "What is the madreporite on a sea star?",
    "How does one tube foot extend and pull back?",
    "How do many predatory sea stars eat prey too big to swallow whole?",
    "Why do scientists call some sea stars “keystone” predators (example: ochre / purple sea star Pisaster)?",
    "What is special about the tropical crown-of-thorns sea star (Acanthaster)?",
    "What do most sea stars need to regrow a whole new body after an arm is lost?",
    "What are pedicellariae on many sea stars?",
    "Is a sea star’s “face” the colourful top side?",
)

EASY_STEMS = (
    "Are starfish a kind of fish?",
    "What does a sea star’s body look like, if we keep the arm count soft?",
    "How does a sea star walk?",
    "Where is a sea star’s mouth?",
    "Where do sea stars live?",
    "What is a sea star’s skin like?",
    "What do many sea stars hunt?",
    "What can many sea stars do if they lose an arm?",
    "How many kinds of sea star are there, if we keep the count soft?",
    "Does the name “starfish” mean they are fish?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
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
    "No — they have no gills, scales, or fins like fish. They are echinoderms, with urchins and sea cucumbers (names light)",
    "A central disc plus arms — five is common, but some kinds have far more (soft)",
    "Hundreds of tiny tube feet on the underside, powered by a water-pump system, help it move and grip",
    "On the bottom side, in the middle of the central disc",
    "In salt water, from shores to the deep sea — not in freshwater lakes",
    "Tough skin with plates and spines on top; colours run from bright orange or red to dull browns",
    "Slow seabed animals such as clams, snails, and other invertebrates",
    "They can grow a damaged or lost arm back over time; a few can rebuild more if part of the disc remains (soft)",
    "About two thousand known kinds worldwide (soft)",
    "No — the name sounds like a fish, but they are sea stars: invertebrates, not fish",
    "Asteroidea — star-shaped echinoderms in the same big phylum as urchins and sea cucumbers",
    "A water vascular system — fluid-filled canals that move, grip, feed, and help exchange gases",
    "A sieve-like plate on the top (aboral) surface where water can enter the water vascular system",
    "A bulb-like ampulla squeezes fluid into the foot to extend it; muscles pull it back",
    "They evert (push out) the cardiac stomach through the mouth, digest outside, then pull food back in",
    "Removing a few can let mussels take over and shrink tide-pool diversity — they punch above their numbers",
    "It is a coral-eating predator; dense outbreaks can leave large white coral scars (Indo-Pacific soft)",
    "At least part of the central disc still attached (a few tropical kinds can do more from an arm — soft)",
    "Tiny claw- or wrench-like ossicles that help keep the body surface clear of debris and settlers",
    "No — oral (mouth + tube feet) is the underside; aboral (often colourful, with madreporite) faces up",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class StarfishZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("starfish", study_card_ids())
        self.assertEqual(shipped_levels_for("starfish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("starfish", "hard"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("starfish", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_STARFISH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Starfish.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_STARFISH_ZOOLOGIST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_STARFISH_ZOOLOGIST))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("starfish", "zoologist")
        easy = study_deck_for("starfish", "easy")
        hard = study_deck_for("starfish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("starfish", "zoologist")
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
        self.assertIn("seven", correct_choice_text(questions[0]).lower())
        self.assertIn("forcipulatida", correct_choice_text(questions[0]).lower())
        self.assertIn("valvatida", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("base", correct_choice_text(questions[1]).lower())
        self.assertIn("asteroidea", correct_choice_text(questions[1]).lower())
        self.assertIn("morphology", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("catch connective", correct_choice_text(questions[2]).lower())
        self.assertIn("mutable collagenous", correct_choice_text(questions[2]).lower())
        self.assertIn("nervous", correct_choice_text(questions[2]).lower())
        self.assertIn("autotomy", correct_choice_text(questions[3]).lower())
        self.assertIn("injected", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("ngffyamide", correct_choice_text(questions[4]).lower())
        self.assertIn("cardiac", correct_choice_text(questions[4]).lower())
        self.assertIn("retraction", correct_choice_text(questions[4]).lower())
        self.assertIn("wasting", correct_choice_text(questions[5]).lower())
        self.assertIn("lesion", correct_choice_text(questions[5]).lower())
        self.assertIn("die-off", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("varies by kind", correct_choice_text(questions[6]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("invasive", correct_choice_text(questions[7]).lower())
        self.assertIn("ballast", correct_choice_text(questions[7]).lower())
        self.assertIn("australia", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("neoasteroidea", correct_choice_text(questions[8]).lower())
        self.assertIn("paleozoic", correct_choice_text(questions[8]).lower())
        self.assertIn("debated", correct_choice_text(questions[8]).lower())
        self.assertIn("catch connective", correct_choice_text(questions[9]).lower())
        self.assertIn("stiffen", correct_choice_text(questions[9]).lower())
        self.assertIn("soften", correct_choice_text(questions[9]).lower())
        self.assertIn("nervous", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Forcipulatida",
            "Valvatida",
            "Paxillosida",
            "Velatida",
            "NGFFYamide",
            "Neoasteroidea",
            "Asterias amurensis",
            "mutable collagenous",
            "Pisaster",
            "Brisingida",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_STARFISH_ZOOLOGIST + PUSH_FURTHER_STARFISH_ZOOLOGIST:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_STARFISH_ZOOLOGIST).lower()
        push = " ".join(PUSH_FURTHER_STARFISH_ZOOLOGIST).lower()
        self.assertIn("letter", talk)
        self.assertIn("stretchy", talk)
        self.assertIn("wasting", talk)
        self.assertIn("fossil", push)
        self.assertIn("ballast", push)
        self.assertIn("arm", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("starfish", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "starfish", "packTemplate": "animals"})
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
        deck = study_deck_for("starfish", "zoologist")
        sheet = study_print_html(
            deck,
            name="Sea star",
            emoji="⭐",
            photo="/field-pack/photos/starfish.jpg?v=img2",
            photo_pos="50% 45%",
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
        for prompt in TALK_ABOUT_STARFISH_ZOOLOGIST + PUSH_FURTHER_STARFISH_ZOOLOGIST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_STARFISH, sheet)
        self.assertIn("Facts from Wikipedia, Starfish.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("starfish", "zoologist"))
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
        ray = WHALE_SHARK.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", ray)
        self.assertNotIn("What do they eat?", ray)
        self.assertNotIn("seven-orders-soft", ray)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["starfish"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        self.assertIn("hard", payload["starfish"]["levels"])
        self.assertEqual(payload["starfish"]["levels"]["hard"]["teach"], [])
        self.assertEqual(payload["starfish"]["levels"]["easy"]["teach"], [
            "Star-shaped ocean animals — not fish (better called sea stars).",
            "Most have a central disc and about five arms (some kinds have many more).",
            "They walk with tiny tube feet on the underside.",
            "The mouth is in the middle of the bottom side.",
            "Many can regrow a lost arm over time.",
        ])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("seven-orders-soft", data_js)
        self.assertIn("catch-connective-soft", data_js)
        self.assertIn("wasting-soft", data_js)
        self.assertIn("stiffness-myth", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = STARFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="hard"', html)
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
