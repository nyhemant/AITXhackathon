"""Elk Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_AMERICAN_BISON,
    PUSH_FURTHER_ELK,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_AMERICAN_BISON,
    TALK_ABOUT_ELK,
    TALK_ABOUT_LION,
    WIKI_AMERICAN_BISON,
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
ELK = FP / "cards" / "elk" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
BISON = FP / "cards" / "american-bison" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Which Cervus group does the elk sit with in mitochondrial DNA studies?",
    "Where did the Cervus family radiate, and how did wapiti ancestors reach North America?",
    "Is the elk a North-America-only species?",
    "How settled is the count of true elk subspecies?",
    "What is surprising about how high an elk bugle can sound?",
    "How do elk calls differ from a European red deer’s roar?",
    "What should we remember if elk and red deer meet in captivity or introductions?",
    "How does an elk’s four-chambered stomach help it eat through the year?",
    "Least Concern is one snapshot. What extra local care should we remember?",
    "What leftover can historic elk reintroductions leave in a herd’s genetics?",
)

ZOOLOGIST_IDS = (
    "eastern-cervus-clade-soft",
    "asian-origin-beringia-soft",
    "asian-wapiti-soft",
    "subspecies-flux-soft",
    "high-frequency-bugle-soft",
    "vocal-divergence-soft",
    "hybrid-caution-soft",
    "ruminant-deepen-soft",
    "lc-snapshot-nuance-soft",
    "translocation-mixing-soft",
)

HARD_STEMS = (
    "What is the elk’s scientific name, and what does “wapiti” mean?",
    "How do scientists now treat elk compared with European red deer?",
    "Which living North American elk kinds does Wikipedia still name?",
    "What covers a bull’s antlers while they are still growing?",
    "What helps steer the antler grow-and-shed cycle?",
    "What happens in the fall elk rut besides a bugle?",
    "Outside the fall rut, who usually stays with whom?",
    "How should we read the IUCN letter for elk?",
    "Which North American elk kinds are gone from the wild?",
    "Where do elk sit in the deer family, Cervidae?",
)

EASY_STEMS = (
    "Where do elk like to live in the wild?",
    "What pale mark helps an elk stand out from behind?",
    "What happens to a bull elk’s antlers each year?",
    "What do elk eat?",
    "How do elk herds usually work?",
    "What is an elk bugle?",
    "What do new elk calves often look like?",
    "How should people care around wild elk and their home?",
    "How big are elk among deer?",
    "Is a North American elk the same animal Europeans call “elk”?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "4000 Hz",
    "4000",
    "150 Hz",
    "2.5 cm",
    "10 million",
    "1 million",
    "25 million",
    "Oligocene",
    "kg",
    "cm",
    "mph",
    "km/h",
)
REDO_THEMES = (
    "Open forests, forest edges, and mountain meadows",
    "A light-colored rump patch against a darker body",
    "Males grow branched antlers, then shed them and grow a new set",
    "Grasses and also leaves, twigs, and bark",
    "Cows and calves often stay in groups; bulls are often apart except in breeding season",
    "A loud autumn bull call — a whistle and bellow that can carry far",
    "They start with spots, like many deer",
    "Give wild elk space and keep forest and meadow habitat healthy",
    "They are one of the largest deer — only moose is bigger",
    "No — in Europe “elk” often means moose; North American elk are also called wapiti",
    "Cervus canadensis — “wapiti” comes from a Shawnee and Cree-related word for “white rump”",
    "They were once lumped with European red deer (C. elaphus); genetics now treat elk/wapiti as their own species (soft)",
    "Living kinds include Rocky Mountain, Roosevelt, tule, and Manitoban (exact splits stay soft)",
    "Soft “velvet” skin — growing antlers are among the fastest-growing bones in mammals (daily length stays soft)",
    "A hormone called testosterone — it rises and drops through the year",
    "Bulls bugle, spar with antlers, and tend harems of cows",
    "Cows and calves often keep to their own groups, and bulls often keep to theirs",
    "Least Concern is a snapshot for the whole species — some local kinds, like tule elk, had tighter recoveries",
    "Eastern elk and Merriam’s elk are gone from the wild (soft history)",
    "They are the largest living deer after moose (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class ElkZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("elk", study_card_ids())
        self.assertEqual(shipped_levels_for("elk"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("elk", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_ELK)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Elk.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_ELK))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_ELK))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("elk", "zoologist")
        easy = study_deck_for("elk", "easy")
        hard = study_deck_for("elk", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("elk", "zoologist")
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
        self.assertIn("eastern", correct_choice_text(questions[0]).lower())
        self.assertIn("sika", correct_choice_text(questions[0]).lower())
        self.assertIn("thorold", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("asia", correct_choice_text(questions[1]).lower())
        self.assertIn("beringia", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("altai", correct_choice_text(questions[2]).lower())
        self.assertIn("tianshan", correct_choice_text(questions[2]).lower())
        self.assertIn("manchurian", correct_choice_text(questions[2]).lower())
        self.assertIn("alashan", correct_choice_text(questions[2]).lower())
        self.assertIn("ecotype", correct_choice_text(questions[3]).lower())
        self.assertIn("geist", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("high", correct_choice_text(questions[4]).lower())
        self.assertIn("nasal", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("red deer", correct_choice_text(questions[5]).lower())
        self.assertIn("high-pitched", correct_choice_text(questions[5]).lower())
        self.assertIn("sika", correct_choice_text(questions[5]).lower())
        self.assertIn("hybrid", correct_choice_text(questions[6]).lower())
        self.assertIn("new zealand", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("cud", correct_choice_text(questions[7]).lower())
        self.assertIn("graze", correct_choice_text(questions[7]).lower())
        self.assertIn("browse", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[8]).lower())
        self.assertIn("tule", correct_choice_text(questions[8]).lower())
        self.assertIn("asian", correct_choice_text(questions[8]).lower())
        self.assertIn("subspecies", correct_choice_text(questions[9]).lower())
        self.assertIn("conservation genetics", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "albirostris",
            "canadensis",
            "nippon",
            "introgression",
            "incomplete lineage sorting",
            "Fiordland",
            "4000",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_AMERICAN_BISON + PUSH_FURTHER_AMERICAN_BISON
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_ELK + PUSH_FURTHER_ELK:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_ELK).lower()
        push = " ".join(PUSH_FURTHER_ELK).lower()
        self.assertIn("cervus", talk)
        self.assertIn("beringia", talk)
        self.assertIn("bugle", talk)
        self.assertIn("sika", push)
        self.assertIn("thorold", push)
        self.assertIn("subspecies", push)
        self.assertIn("hybrid", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("elk", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "elk", "packTemplate": "animals"})
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
        deck = study_deck_for("elk", "zoologist")
        sheet = study_print_html(
            deck,
            name="Elk",
            emoji="🦌",
            photo="/field-pack/photos/elk.jpg?v=img2",
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
        for prompt in TALK_ABOUT_ELK + PUSH_FURTHER_ELK:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_ELK, sheet)
        self.assertIn("Facts from Wikipedia, Elk.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("elk", "zoologist"))
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
        self.assertEqual(shipped_levels_for("american-bison"), ("easy", "hard", "zoologist"))
        bison_zoo = study_deck_for("american-bison", "zoologist")
        self.assertEqual(bison_zoo["source"], WIKI_AMERICAN_BISON)
        bison_html = BISON.read_text(encoding="utf-8")
        self.assertIn("Zoologist", bison_html)
        self.assertEqual(bison_zoo["talk_about"], list(TALK_ABOUT_AMERICAN_BISON))
        self.assertEqual(bison_zoo["push_further"], list(PUSH_FURTHER_AMERICAN_BISON))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", jelly)
        self.assertNotIn("What do they eat?", jelly)
        self.assertNotIn("eastern-cervus-clade-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["elk"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("eastern-cervus-clade-soft", data_js)
        self.assertIn("asian-origin-beringia-soft", data_js)
        self.assertIn("translocation-mixing-soft", data_js)
        self.assertIn("hybrid-caution-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = ELK.read_text(encoding="utf-8")
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
