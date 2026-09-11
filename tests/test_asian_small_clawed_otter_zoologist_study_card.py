"""Asian small-clawed otter Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_SHARK,
    PUSH_FURTHER_TORTOISE,
    STUDY_SLOTS,
    TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER,
    TALK_ABOUT_LION,
    TALK_ABOUT_SHARK,
    TALK_ABOUT_TORTOISE,
    WIKI_ASIAN_SMALL_CLAWED_OTTER,
    WIKI_LION,
    WIKI_SHARK,
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
OTTER = FP / "cards" / "asian-small-clawed-otter" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
SHARK = FP / "cards" / "shark" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "What scientific name do scientists often use for the Asian small-clawed otter?",
    "Which living otter sits closest on the family tree, according to molecular work?",
    "Which other otters group with this species in a clade next to Lutra?",
    "How are this otter’s upper cheek teeth built?",
    "How far does the webbing go on their digits?",
    "What rare mixing has been documented in Singapore?",
    "Where do otters sit in the mammal family tree?",
    "What is a holt, and who gathers nest material?",
    "How do newborn pups start life?",
    "What have keepers seen captive otters do with shellfish?",
)

ZOOLOGIST_IDS = (
    "naming-flux-soft",
    "sister-lutrogale-soft",
    "clawless-cousins-soft",
    "crushing-teeth-soft",
    "incomplete-webbing-soft",
    "hybrid-singapore-soft",
    "mustelidae-lutrinae",
    "holt-nest-soft",
    "altricial-pups-soft",
    "sun-open-shells-soft",
)

HARD_STEMS = (
    "How do long whiskers help Asian small-clawed otters hunt?",
    "How do their paws help them find food?",
    "When are they often more active if they live near people?",
    "Why do family groups smear droppings at special spots?",
    "Who may help raise younger otter pups?",
    "How should we read the IUCN letter for this otter?",
    "How did international trade rules change for this otter in 2019?",
    "Why is keeping these otters as pets a problem?",
    "Do Asian small-clawed otters sleep by holding hands in the water like sea otters?",
    "What is shrinking or getting polluted for these otters?",
)

EASY_STEMS = (
    "What kind of otter is the Asian small-clawed otter?",
    "Where do Asian small-clawed otters live in the wild?",
    "What do Asian small-clawed otters often eat?",
    "What is special about their claws?",
    "How do Asian small-clawed otters usually live?",
    "What sounds do they make?",
    "What is a baby otter called?",
    "How do they stay warm in the water?",
    "How do their feet help them move?",
    "Is an otter the same animal as a beaver?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "60 hybrid",
    "at least 60",
    "2016",
    "1.33",
    "1.5 mya",
    "million years exactly",
    "40 days",
    "62 day",
    "86 day",
    "Vulnerable",
    "Endangered",
    "Critically",
    "CITES",
)
REDO_THEMES = (
    "The world’s smallest otter",
    "Rivers, wetlands, mangroves, and rice fields",
    "Crabs, shellfish, and small fish",
    "Short claws that often don’t stick past the toe pads",
    "In pairs and family groups",
    "Lots of squeaks, chirps, and yelps",
    "Dense fur helps them stay warm in water",
    "Webbed feet help them swim",
    "otters eat meaty snacks; beavers eat plants",
    "murky water",
    "feel for crabs and shellfish under mud and stones",
    "dusk and night",
    "spraint posts",
    "Older siblings may help",
    "IUCN lists them Vulnerable",
    "Appendix I",
    "Illegal pet trade",
    "hand-holding",
    "Wetlands, mangroves, and clean water",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class AsianSmallClawedOtterZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(
            shipped_levels_for("asian-small-clawed-otter"),
            ("easy", "hard", "zoologist"),
        )
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("asian-small-clawed-otter", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_ASIAN_SMALL_CLAWED_OTTER)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Asian small-clawed otter.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("asian-small-clawed-otter", "zoologist")
        easy = study_deck_for("asian-small-clawed-otter", "easy")
        hard = study_deck_for("asian-small-clawed-otter", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("asian-small-clawed-otter", "zoologist")
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
        self.assertIn("Aonyx cinereus", correct_choice_text(questions[0]))
        self.assertIn("Amblonyx", correct_choice_text(questions[0]))
        self.assertIn("Lutra cinerea", correct_choice_text(questions[0]))
        self.assertIn("still move", correct_choice_text(questions[0]))
        self.assertIn("Lutrogale", correct_choice_text(questions[1]))
        self.assertIn("1.5 million", correct_choice_text(questions[1]))
        self.assertIn("stays soft", correct_choice_text(questions[1]).lower())
        self.assertIn("African clawless", correct_choice_text(questions[2]))
        self.assertIn("Aonyx", correct_choice_text(questions[2]))
        self.assertIn("Lutra", correct_choice_text(questions[2]))
        self.assertIn("premolars", correct_choice_text(questions[3]).lower())
        self.assertIn("four cheek teeth", correct_choice_text(questions[3]).lower())
        self.assertIn("crushing", correct_choice_text(questions[3]).lower())
        self.assertIn("last joint", correct_choice_text(questions[4]).lower())
        self.assertIn("hand-foraging", correct_choice_text(questions[4]).lower())
        self.assertIn("Singapore", questions[5]["stem"])
        self.assertIn("hybrid", correct_choice_text(questions[5]).lower())
        self.assertIn("smooth-coated", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("Lutrinae", correct_choice_text(questions[6]))
        self.assertIn("Mustelidae", correct_choice_text(questions[6]))
        self.assertIn("weasel", correct_choice_text(questions[6]).lower())
        self.assertIn("bank den", correct_choice_text(questions[7]).lower())
        self.assertIn("both parents", correct_choice_text(questions[7]).lower())
        self.assertIn("eyes closed", correct_choice_text(questions[8]).lower())
        self.assertIn("week five", correct_choice_text(questions[8]).lower())
        self.assertIn("three months", correct_choice_text(questions[8]).lower())
        self.assertIn("exact days vary", correct_choice_text(questions[8]).lower())
        self.assertIn("sun", correct_choice_text(questions[9]).lower())
        self.assertIn("shellfish", correct_choice_text(questions[9]).lower())
        self.assertIn("captive", questions[9]["stem"].lower() + questions[9]["why"].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Aonyx",
            "Amblonyx",
            "Lutra",
            "cinereus",
            "cinerea",
            "Lutrogale",
            "cladogram",
            "paraphyly",
            "mtDNA",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_TORTOISE + PUSH_FURTHER_TORTOISE
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER + PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER).lower()
        push = " ".join(PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER).lower()
        self.assertIn("scientific name", talk)
        self.assertIn("crushing teeth", talk)
        self.assertIn("holt", talk)
        self.assertIn("sister", push)
        self.assertIn("family tree", push)
        self.assertIn("singapore", push)
        self.assertIn("mustelidae", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("asian-small-clawed-otter", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "asian-small-clawed-otter", "packTemplate": "animals"})
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
        deck = study_deck_for("asian-small-clawed-otter", "zoologist")
        sheet = study_print_html(
            deck,
            name="Asian small-clawed otter",
            emoji="🦦",
            photo="/field-pack/photos/asian-small-clawed-otter.jpg?v=img2",
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
        for prompt in TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER + PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_ASIAN_SMALL_CLAWED_OTTER, sheet)
        self.assertIn("Facts from Wikipedia, Asian small-clawed otter.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("asian-small-clawed-otter", "zoologist"))
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
        self.assertEqual(shipped_levels_for("shark"), ("easy", "hard", "zoologist"))
        shark_zoo = study_deck_for("shark", "zoologist")
        self.assertEqual(shark_zoo["source"], WIKI_SHARK)
        self.assertIn("Selachii", correct_choice_text(shark_zoo["questions"][0]))
        shark_html = SHARK.read_text(encoding="utf-8")
        self.assertIn("Zoologist", shark_html)
        self.assertEqual(shark_zoo["talk_about"], list(TALK_ABOUT_SHARK))
        self.assertEqual(shark_zoo["push_further"], list(PUSH_FURTHER_SHARK))
        sea = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", sea)
        self.assertNotIn("What do they eat?", sea)
        self.assertNotIn("naming-flux-soft", sea)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["asian-small-clawed-otter"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("naming-flux-soft", data_js)
        self.assertIn("sister-lutrogale-soft", data_js)
        self.assertIn("sun-open-shells-soft", data_js)
        self.assertIn("mustelidae-lutrinae", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = OTTER.read_text(encoding="utf-8")
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
