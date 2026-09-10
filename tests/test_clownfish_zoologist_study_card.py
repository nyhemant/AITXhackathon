"""Clownfish Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PUFFIN,
    STUDY_SLOTS,
    TALK_ABOUT_CLOWNFISH,
    TALK_ABOUT_LION,
    TALK_ABOUT_PUFFIN,
    WIKI_ATLANTIC_PUFFIN,
    WIKI_CLOWNFISH,
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
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
PUFFIN = FP / "cards" / "puffin" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Where have anemonefish traditionally sat inside the damselfish family?",
    "How do scientists treat the maroon clownfish (Premnas biaculeatus)?",
    "Which classic species complexes do scientists often name for anemonefish?",
    "How does Amphiprion clarkii compare with many other clownfish as a host user?",
    "How do smaller clownfish keep from being evicted by the fish above them?",
    "How can sound help a clownfish group keep its rank?",
    "What mucus chemistry idea may help clownfish avoid triggering anemone stings?",
    "Is sting protection only learned, or is some of it already there?",
    "What happens after clownfish eggs hatch, before a young fish can live in an anemone?",
    "Beyond a simple hideout, how might the fish–anemone partnership go both ways?",
)

ZOOLOGIST_IDS = (
    "amphiprioninae-soft",
    "premnas-flux-soft",
    "species-complexes-soft",
    "clarkii-generalist-soft",
    "growth-suppression-soft",
    "sound-hierarchy-soft",
    "mucus-chemistry-soft",
    "acclimation-innate-soft",
    "larval-ocean-soft",
    "mutualism-deepen-soft",
)

HARD_STEMS = (
    "Clownfish are also called anemonefish. Which genus and family do they sit in?",
    "About how many living anemonefish species do scientists often name?",
    "How can the common “Nemo-like” pair of clownfish look different?",
    "How can a clownfish’s sex change if the breeding female is gone?",
    "How does size rank the fish that share one anemone?",
    "How does a clownfish settle into an anemone’s stinging tentacles?",
    "What do clownfish and sea anemones often give each other?",
    "Do all clownfish use the same kind of anemone host?",
    "Why does captive breeding matter for popular pet clownfish?",
    "How tightly are wild clownfish tied to reefs and anemones?",
)

EASY_STEMS = (
    "Where do clownfish usually live?",
    "What do many clownfish look like?",
    "Where do clownfish find shelter?",
    "Why can a clownfish sit in stinging tentacles?",
    "What does a clownfish do when danger comes?",
    "How do clownfish usually live around an anemone?",
    "Where do clownfish put their eggs, and who helps?",
    "Where in the world do wild clownfish live?",
    "How can people help wild clownfish?",
    "Is there only one “Nemo” kind of clownfish?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "28 species",
    "29 species",
    "160 mm",
    "80 mm",
    "35 million",
    "10.5",
    "kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "On shallow coral reefs and in nearby calm lagoons",
    "An orange to reddish body with white bands — some kinds look darker",
    "Among sea-anemone tentacles on the reef",
    "Special skin mucus helps them not get stung",
    "It ducks into the anemone tentacles",
    "They live in a small group around one anemone",
    "They lay eggs near the anemone, and parents help guard them",
    "Warm waters of the Indian Ocean and the western Pacific",
    "Keep reefs and anemones healthy so clownfish still have homes",
    "No — many kinds of anemonefish share the clownfish nickname",
    "Genus Amphiprion, in the damselfish family Pomacentridae",
    "Roughly two dozen living anemonefish species — the exact count stays soft",
    "A. ocellaris (false percula) vs A. percula (true orange clownfish) — black outline thickness often differs (soft)",
    "They are born male; the largest fish can become female if the breeding female is gone",
    "Biggest = breeding female; next = breeding male; smaller fish wait in line",
    "Special mucus plus careful touching of tentacles helps them settle — protection is not instant",
    "The fish get shelter; the anemone may get cleaning and defense help (soft mutualism)",
    "Different clownfish prefer different anemone hosts — about ten host anemone kinds (soft)",
    "Clownfish are very popular pets; captive breeding can help take pressure off wild reefs (soft)",
    "They completely depend on anemones and reefs — habitat health is clownfish health",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class ClownfishZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("clownfish", study_card_ids())
        self.assertEqual(shipped_levels_for("clownfish"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("clownfish", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_CLOWNFISH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Clownfish.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_CLOWNFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_CLOWNFISH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("clownfish", "zoologist")
        easy = study_deck_for("clownfish", "easy")
        hard = study_deck_for("clownfish", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("clownfish", "zoologist")
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
        self.assertIn("amphiprioninae", correct_choice_text(questions[0]).lower())
        self.assertIn("pomacentridae", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("premnas", correct_choice_text(questions[1]).lower())
        self.assertIn("amphiprion", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("percula", correct_choice_text(questions[2]).lower())
        self.assertIn("clarkii", correct_choice_text(questions[2]).lower())
        self.assertIn("ephippium", correct_choice_text(questions[2]).lower())
        self.assertIn("akallopisos", correct_choice_text(questions[2]).lower())
        self.assertIn("polymnus", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("clarkii", correct_choice_text(questions[3]).lower())
        self.assertIn("many host", correct_choice_text(questions[3]).lower())
        self.assertIn("specialist", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("growth", correct_choice_text(questions[4]).lower())
        self.assertIn("size", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("clicks", correct_choice_text(questions[5]).lower())
        self.assertIn("pops", correct_choice_text(questions[5]).lower())
        self.assertIn("chirps", correct_choice_text(questions[5]).lower())
        self.assertIn("rank", correct_choice_text(questions[5]).lower())
        self.assertIn("sialic", correct_choice_text(questions[6]).lower())
        self.assertIn("neu5ac", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("innate", correct_choice_text(questions[7]).lower())
        self.assertIn("tentacle", correct_choice_text(questions[7]).lower())
        self.assertIn("species", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("larvae", correct_choice_text(questions[8]).lower())
        self.assertIn("settle", correct_choice_text(questions[8]).lower())
        self.assertIn("anemone", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("fan", correct_choice_text(questions[9]).lower())
        self.assertIn("clean", correct_choice_text(questions[9]).lower())
        self.assertIn("grow", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "biaculeatus",
            "Amphiprioninae",
            "Neu5Ac",
            "nematocyst",
            "akallopisos",
            "ephippium",
            "polymnus",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_PUFFIN + PUSH_FURTHER_PUFFIN
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_CLOWNFISH + PUSH_FURTHER_CLOWNFISH:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_CLOWNFISH).lower()
        push = " ".join(PUSH_FURTHER_CLOWNFISH).lower()
        self.assertIn("premnas", talk)
        self.assertIn("growth", talk)
        self.assertIn("mucus", talk)
        self.assertIn("specialist", push)
        self.assertIn("generalist", push)
        self.assertIn("clicks", push)
        self.assertIn("larvae", push)
        self.assertIn("settlement", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("clownfish", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "clownfish", "packTemplate": "animals"})
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
        deck = study_deck_for("clownfish", "zoologist")
        sheet = study_print_html(
            deck,
            name="Clownfish",
            emoji="🐠",
            photo="/field-pack/photos/clownfish.jpg?v=img2",
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
        for prompt in TALK_ABOUT_CLOWNFISH + PUSH_FURTHER_CLOWNFISH:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_CLOWNFISH, sheet)
        self.assertIn("Facts from Wikipedia, Clownfish.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("clownfish", "zoologist"))
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
        self.assertEqual(shipped_levels_for("puffin"), ("easy", "hard", "zoologist"))
        puffin_zoo = study_deck_for("puffin", "zoologist")
        self.assertEqual(puffin_zoo["source"], WIKI_ATLANTIC_PUFFIN)
        puffin_html = PUFFIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", puffin_html)
        self.assertEqual(puffin_zoo["talk_about"], list(TALK_ABOUT_PUFFIN))
        self.assertEqual(puffin_zoo["push_further"], list(PUSH_FURTHER_PUFFIN))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("amphiprioninae-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["clownfish"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("amphiprioninae-soft", data_js)
        self.assertIn("premnas-flux-soft", data_js)
        self.assertIn("mutualism-deepen-soft", data_js)
        self.assertIn("mucus-chemistry-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = CLOWNFISH.read_text(encoding="utf-8")
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
