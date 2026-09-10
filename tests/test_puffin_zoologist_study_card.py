"""Puffin Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_ELK,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PUFFIN,
    STUDY_SLOTS,
    TALK_ABOUT_ELK,
    TALK_ABOUT_LION,
    TALK_ABOUT_PUFFIN,
    WIKI_ATLANTIC_PUFFIN,
    WIKI_ELK,
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
PUFFIN = FP / "cards" / "puffin" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
ELK = FP / "cards" / "elk" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Which auk tribe do puffins sit with, along with the rhinoceros auklet?",
    "Which larger bird order do Atlantic puffins sit in?",
    "How many Atlantic puffin subspecies do scientists often name?",
    "Which living puffin is the closest relative of the Atlantic puffin?",
    "Where is living Fraterculini diversity highest?",
    "What are the bright breeding bill plates made of, and what happens after the season?",
    "How do Atlantic puffins usually invest in the next generation?",
    "How can chick success track the fish puffins catch?",
    "Does the Vulnerable letter tell the same story on every Atlantic puffin coast?",
    "What does the extinct great auk show about auk lineages?",
)

ZOOLOGIST_IDS = (
    "fraterculini-soft",
    "charadriiformes-soft",
    "three-subspecies-soft",
    "horned-closest-soft",
    "pacific-origin-soft",
    "keratin-bill-molt-soft",
    "k-selected-soft",
    "sandeel-link-soft",
    "vu-regional-nuance-soft",
    "great-auk-contrast-soft",
)

HARD_STEMS = (
    "What is the Atlantic puffin’s scientific name, and what soft name story can Fratercula hold?",
    "Which bird family does the Atlantic puffin belong to?",
    "How many puffin species live in the Atlantic Ocean?",
    "What happens to an Atlantic puffin’s colorful outer bill after breeding season?",
    "How can an Atlantic puffin hold a row of fish while catching more?",
    "How does an Atlantic puffin dive for food, and where does it often hunt?",
    "Do Atlantic puffins often keep the same home and partner?",
    "How should we read the IUCN letter for Atlantic puffins?",
    "Why do Atlantic puffins prefer islands, and what still threatens chicks?",
    "Which Canadian province chose the Atlantic puffin as its official bird?",
)

EASY_STEMS = (
    "Where do Atlantic puffins spend their year?",
    "What does an Atlantic puffin’s bill look like in breeding season?",
    "Where does an Atlantic puffin usually put its nest?",
    "How many chicks do Atlantic puffins usually raise in a season?",
    "How can an Atlantic puffin carry food home?",
    "How does an Atlantic puffin swim after fish?",
    "How do Atlantic puffins often walk on land?",
    "How can people help wild puffins?",
    "How do Atlantic puffins usually nest?",
    "Is an Atlantic puffin a penguin?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "12–14 million",
    "12-14 million",
    "4,770,000",
    "4-5 years",
    "4–5 years",
    "2–3 years",
    "2-3 years",
    "650 g",
    "80 km/h",
    "50–79%",
    "50-79%",
    "kg",
    "cm",
    "mph",
    "km/h",
)
REDO_THEMES = (
    "They breed on cold northern coasts and islands, then winter on the open ocean",
    "A bright orange-yellow-red bill",
    "It digs a burrow — or uses a rock crevice — for the nest",
    "Usually one chick from one egg",
    "It can hold several small fish side-by-side in the bill at once",
    "It “flies” underwater with its wings, and its feet steer",
    "With a funny side-to-side waddle",
    "Protect nesting islands and keep oceans healthy for fish",
    "They nest close together in busy cliff-top colonies",
    "No — puffins can fly in the air; penguins are different birds that don’t",
    "Fratercula arctica — a soft “little brother of the north” name story",
    "The auk family, Alcidae — with murres, auklets, and razorbills, not penguins",
    "Only the Atlantic puffin; horned and tufted puffins live in the North Pacific",
    "The colorful outer plates and face ornaments grow for breeding, then shed — the winter bill looks duller and smaller",
    "Spines on the tongue and the roof of the mouth help pin fish in a row",
    "It dives using its wings for thrust, and it usually feeds in shallower water near colonies",
    "They often return to the same burrow and mate year after year",
    "Vulnerable is a snapshot — some colonies still struggle with food and climate shifts",
    "They prefer predator-free islands; gulls and skuas still threaten chicks from the air",
    "Newfoundland and Labrador",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class PuffinZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("puffin", study_card_ids())
        self.assertEqual(shipped_levels_for("puffin"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("puffin", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_ATLANTIC_PUFFIN)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Atlantic puffin.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_PUFFIN))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_PUFFIN))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("puffin", "zoologist")
        easy = study_deck_for("puffin", "easy")
        hard = study_deck_for("puffin", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("puffin", "zoologist")
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
        self.assertIn("fraterculini", correct_choice_text(questions[0]).lower())
        self.assertIn("rhinoceros auklet", correct_choice_text(questions[0]).lower())
        self.assertIn("alcidae", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("charadriiformes", correct_choice_text(questions[1]).lower())
        self.assertIn("gull", correct_choice_text(questions[1]).lower())
        self.assertIn("auk", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("arctica", correct_choice_text(questions[2]).lower())
        self.assertIn("grabae", correct_choice_text(questions[2]).lower())
        self.assertIn("naumanni", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("horned", correct_choice_text(questions[3]).lower())
        self.assertIn("corniculata", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("pacific", correct_choice_text(questions[4]).lower())
        self.assertIn("atlantic", correct_choice_text(questions[4]).lower())
        self.assertIn("one living", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("keratin", correct_choice_text(questions[5]).lower())
        self.assertIn("sheath", correct_choice_text(questions[5]).lower())
        self.assertIn("paint", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("long-lived", correct_choice_text(questions[6]).lower())
        self.assertIn("one chick", correct_choice_text(questions[6]).lower())
        self.assertIn("several years", correct_choice_text(questions[6]).lower())
        self.assertIn("sandeel", correct_choice_text(questions[7]).lower())
        self.assertIn("warm", correct_choice_text(questions[7]).lower())
        self.assertIn("prey", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[8]).lower())
        self.assertIn("east atlantic", correct_choice_text(questions[8]).lower())
        self.assertIn("west atlantic", correct_choice_text(questions[8]).lower())
        self.assertIn("great auk", correct_choice_text(questions[9]).lower())
        self.assertIn("flightless", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "arctica",
            "grabae",
            "naumanni",
            "corniculata",
            "Cerorhinca",
            "Charadriiformes",
            "Alcidae",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_ELK + PUSH_FURTHER_ELK
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_PUFFIN + PUSH_FURTHER_PUFFIN:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_PUFFIN).lower()
        push = " ".join(PUSH_FURTHER_PUFFIN).lower()
        self.assertIn("fraterculini", talk)
        self.assertIn("auk", talk)
        self.assertIn("keratin", talk)
        self.assertIn("sandeel", talk)
        self.assertIn("named kinds", push)
        self.assertIn("rhinoceros auklet", push)
        self.assertIn("east atlantic", push)
        self.assertIn("west atlantic", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("puffin", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "puffin", "packTemplate": "animals"})
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
        deck = study_deck_for("puffin", "zoologist")
        sheet = study_print_html(
            deck,
            name="Puffin",
            emoji="🐦",
            photo="/field-pack/photos/puffin.jpg?v=img2",
            photo_pos="50% 22%",
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
        for prompt in TALK_ABOUT_PUFFIN + PUSH_FURTHER_PUFFIN:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_ATLANTIC_PUFFIN, sheet)
        self.assertIn("Facts from Wikipedia, Atlantic puffin.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("puffin", "zoologist"))
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
        self.assertEqual(shipped_levels_for("elk"), ("easy", "hard", "zoologist"))
        elk_zoo = study_deck_for("elk", "zoologist")
        self.assertEqual(elk_zoo["source"], WIKI_ELK)
        elk_html = ELK.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elk_html)
        self.assertEqual(elk_zoo["talk_about"], list(TALK_ABOUT_ELK))
        self.assertEqual(elk_zoo["push_further"], list(PUSH_FURTHER_ELK))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("fraterculini-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["puffin"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("fraterculini-soft", data_js)
        self.assertIn("charadriiformes-soft", data_js)
        self.assertIn("great-auk-contrast-soft", data_js)
        self.assertIn("vu-regional-nuance-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = PUFFIN.read_text(encoding="utf-8")
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
