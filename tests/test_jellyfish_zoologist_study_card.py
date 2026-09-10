"""Jellyfish Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_EEL,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_LION,
    WIKI_CRAB,
    WIKI_CUTTLEFISH,
    WIKI_EEL,
    WIKI_JELLYFISH,
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
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
OCTOPUS = FP / "cards" / "stingray" / "index.html"
EEL = FP / "cards" / "eel" / "index.html"
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
CRAB = FP / "cards" / "crab" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "How are Scyphozoa, Cubozoa, and Staurozoa often grouped, if we keep that clade soft?",
    "What body plan do medusozoans typically show, if we keep that symmetry soft?",
    "What happens inside a nematocyst capsule when it fires, if we keep that discharge soft?",
    "What do rhopalia do besides hold sensors, if we keep those pacemakers soft?",
    "How should we read box-jelly eyes on the rhopalia, if we keep the count soft?",
    "How can elastic mesoglea make a jelly’s swim cheaper, if we keep that boost soft?",
    "What can Turritopsis dohrnii do under stress, if we keep the “immortal jelly” headline soft?",
    "How do corals and anemones differ from medusozoans, if we keep that phylogeny soft?",
    "Which human-linked changes can favor jelly dominance, if we keep those drivers soft?",
    "How should we read IUCN letters for “jellyfish,” if we keep that snapshot soft?",
)

ZOOLOGIST_IDS = (
    "acraspeda-soft",
    "tetramery-soft",
    "cnida-discharge-soft",
    "rhopalia-pacemakers-soft",
    "cubozoan-24-eye-soft",
    "passive-energy-swim-soft",
    "turritopsis-soft",
    "anthozoa-contrast-soft",
    "bloom-drivers-soft",
    "status-snapshot-soft",
)

HARD_STEMS = (
    "What are swimming “jellies,” if we keep the group soft?",
    "What main groups sit inside medusozoan jellies?",
    "How do stinging cells (nematocysts) grab prey, if we keep the mechanism soft?",
    "How do scyphozoan polyps make baby medusae?",
    "What happens after a jelly egg is fertilized, before a swimming medusa appears?",
    "Why can box jellyfish see space better than most other jellies?",
    "Why isn’t a Portuguese man o’ war a solitary true jelly?",
    "Why aren’t comb jellies the same as cnidarian jellies?",
    "When can huge jelly swarms form, if we keep the causes soft?",
    "Is there one IUCN letter for “jellyfish”?",
)

EASY_STEMS = (
    "Are jellyfish a kind of fish?",
    "What is the soft umbrella-shaped part of a jelly?",
    "What hang below a jelly’s bell?",
    "What do a jelly’s tentacles use to grab food?",
    "How does a jellyfish usually swim?",
    "How much of a jelly’s body is water, if we keep the share soft?",
    "What two stages do many jellies pass through?",
    "Where do jellyfish live?",
    "How can people help jellies and the shores they visit?",
    "Is a Portuguese man o’ war a true jellyfish?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "200 species",
    "1000",
    "1,000",
    " kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "No backbone — they’re cnidarians, the same big group as corals and anemones",
    "A soft umbrella-shaped body (the bell) made of jelly-like mesoglea",
    "Trailing tentacles hang below to catch food and sense the water",
    "Tiny stinging cells help grab plankton, small fish, or other jellies (many stings feel mild to people — soft)",
    "The bell squeezes and opens to push water and move",
    "Jelly tissue is about 95% water or more (exact share stays soft)",
    "Many start as a tiny polyp on the seafloor, then become a swimming medusa — the jelly we see",
    "Worldwide from shallow coasts to the deep sea; a few tiny kinds live in fresh water",
    "Keep coasts clean and seas balanced; big bloom swarms can bother beaches and fishing (soft)",
    "No — it’s a floating colony of many tiny animals working as one, not a true jellyfish",
    "The medusa stage of subphylum Medusozoa in phylum Cnidaria — not one clade of every gelatinous blob (soft)",
    "Scyphozoa (“true” jellies), Cubozoa (box jellies), Hydrozoa (many small jellies), and Staurozoa (stalked jellies)",
    "They fire tiny barbed threads that inject venom into prey (soft)",
    "They stack and pinch off baby medusae (ephyrae) in a process called strobilation",
    "Fertilized eggs become ciliated planula larvae that settle and grow into polyps before making medusae",
    "They have many eyes on sensory clubs (rhopalia) — better spatial vision than most other jellies (soft)",
    "It is a colonial hydrozoan (a siphonophore), not a solitary medusa — that deepens the JR myth buster (soft)",
    "Comb jellies look jelly-like but sit in a different phylum (Ctenophora) and have no nematocyst sting like cnidarians",
    "Huge swarms can form when currents, food, and warm or nutrient-rich water align; they can clog nets and intakes (soft)",
    "No — some invasive or bloom-forming kinds surge while habitats shift; watch species and places, not one group score (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class JellyfishZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("jellyfish", study_card_ids())
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("jellyfish", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_JELLYFISH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Jellyfish.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_JELLYFISH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("jellyfish", "zoologist")
        easy = study_deck_for("jellyfish", "easy")
        hard = study_deck_for("jellyfish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("jellyfish", "zoologist")
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
        self.assertIn("acraspeda", correct_choice_text(questions[0]).lower())
        self.assertIn("hydrozoa", correct_choice_text(questions[0]).lower())
        self.assertIn("sister", correct_choice_text(questions[0]).lower())
        self.assertIn("siphonophore", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("tetramer", correct_choice_text(questions[1]).lower())
        self.assertIn("oral arms", correct_choice_text(questions[1]).lower())
        self.assertIn("radial", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("inverted", correct_choice_text(questions[2]).lower())
        self.assertIn("tubule", correct_choice_text(questions[2]).lower())
        self.assertIn("pressure", correct_choice_text(questions[2]).lower())
        self.assertIn("weapon", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("pacemaker", correct_choice_text(questions[3]).lower())
        self.assertIn("rhopalia", correct_choice_text(questions[3]).lower())
        self.assertIn("pulse", correct_choice_text(questions[3]).lower())
        self.assertIn("nerve net", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("24", correct_choice_text(questions[4]))
        self.assertIn("four", correct_choice_text(questions[4]).lower())
        self.assertIn("morphological", correct_choice_text(questions[4]).lower())
        self.assertIn("obstacle", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("mesoglea", correct_choice_text(questions[5]).lower())
        self.assertIn("recoil", correct_choice_text(questions[5]).lower())
        self.assertIn("aurelia", correct_choice_text(questions[5]).lower())
        self.assertIn("efficient", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("turritopsis", correct_choice_text(questions[6]).lower())
        self.assertIn("dohrnii", correct_choice_text(questions[6]).lower())
        self.assertIn("polyp", correct_choice_text(questions[6]).lower())
        self.assertIn("immortal", correct_choice_text(questions[6]).lower())
        self.assertIn("lab", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("anthozoa", correct_choice_text(questions[7]).lower())
        self.assertIn("coral", correct_choice_text(questions[7]).lower())
        self.assertIn("anemone", correct_choice_text(questions[7]).lower())
        self.assertIn("medusa", correct_choice_text(questions[7]).lower())
        self.assertIn("polyp", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("eutrophication", correct_choice_text(questions[8]).lower())
        self.assertIn("warmer", correct_choice_text(questions[8]).lower())
        self.assertIn("overfishing", correct_choice_text(questions[8]).lower())
        self.assertIn("invasive", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("iucn", correct_choice_text(questions[9]).lower())
        self.assertIn("species", correct_choice_text(questions[9]).lower())
        self.assertIn("sea", correct_choice_text(questions[9]).lower())
        self.assertIn("score", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "dohrnii",
            "tetramerous",
            "nematocyst",
            "eutrophication",
            "Aurelia",
            "siphonophore",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_CUTTLEFISH + PUSH_FURTHER_CUTTLEFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_JELLYFISH).lower()
        push = " ".join(PUSH_FURTHER_JELLYFISH).lower()
        self.assertIn("acraspeda", talk)
        self.assertIn("hydrozoa", talk)
        self.assertIn("rhopalia", talk)
        self.assertIn("bloom", talk)
        self.assertIn("anthozoa", push)
        self.assertIn("turritopsis", push)
        self.assertIn("fish", push)
        self.assertIn("predator", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("jellyfish", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "jellyfish", "packTemplate": "animals"})
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
        deck = study_deck_for("jellyfish", "zoologist")
        sheet = study_print_html(
            deck,
            name="Jellyfish",
            emoji="🎐",
            photo="/field-pack/photos/jellyfish.jpg?v=img2",
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
        for prompt in TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_JELLYFISH, sheet)
        self.assertIn("Facts from Wikipedia, Jellyfish.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("jellyfish", "zoologist"))
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
        self.assertEqual(shipped_levels_for("crab"), ("easy", "hard", "zoologist"))
        crab_zoo = study_deck_for("crab", "zoologist")
        self.assertEqual(crab_zoo["source"], WIKI_CRAB)
        crab_html = CRAB.read_text(encoding="utf-8")
        self.assertIn("Zoologist", crab_html)
        self.assertEqual(crab_zoo["talk_about"], list(TALK_ABOUT_CRAB))
        self.assertEqual(crab_zoo["push_further"], list(PUSH_FURTHER_CRAB))
        octo = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", octo)
        self.assertNotIn("card-study-pack", octo)
        self.assertNotIn("acraspeda-soft", octo)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["jellyfish"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("acraspeda-soft", data_js)
        self.assertIn("rhopalia-pacemakers-soft", data_js)
        self.assertIn("turritopsis-soft", data_js)
        self.assertIn("status-snapshot-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = JELLYFISH.read_text(encoding="utf-8")
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
