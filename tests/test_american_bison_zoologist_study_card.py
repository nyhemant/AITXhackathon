"""American bison Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_AMERICAN_ALLIGATOR,
    PUSH_FURTHER_AMERICAN_BISON,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_AMERICAN_ALLIGATOR,
    TALK_ABOUT_AMERICAN_BISON,
    TALK_ABOUT_LION,
    WIKI_AMERICAN_ALLIGATOR,
    WIKI_AMERICAN_BISON,
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
BISON = FP / "cards" / "american-bison" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
GATOR = FP / "cards" / "american-alligator" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "What is the scientific species name for the American bison, and how are the two main kinds often labeled?",
    "What does nuclear DNA say about where bison sit next to cattle and yaks?",
    "Where do American bison sit among even-toed ungulates?",
    "Where did American bison ancestors come from?",
    "What leftover do modern bison herds still show from the late-1800s crash?",
    "Why do many bison herds carry small amounts of domestic cattle DNA?",
    "How can European bison DNA tell two different family stories?",
    "Beyond simply eating grass, how can bison reshape a prairie?",
    "Near Threatened is one snapshot. What extra split should we remember about bison numbers?",
    "How do modern recovery programs try to keep bison genetic diversity from shrinking again?",
)

ZOOLOGIST_IDS = (
    "bison-bison-taxonomy-soft",
    "nested-in-bos-soft",
    "bovini-tribe-soft",
    "beringia-ancestry-soft",
    "bottleneck-genetics-soft",
    "cattle-dna-soft",
    "european-mtdna-soft",
    "keystone-ecology-soft",
    "nt-wild-vs-ranch-soft",
    "metapopulation-soft",
)

HARD_STEMS = (
    "What are the two main kinds of American bison, and how do they often look different?",
    "How many living bison species are there in the world?",
    "How can a bison reach grass under winter snow?",
    "Bison can look slow. What can they really do?",
    "Besides cooling off and shaking bugs, what can a bison wallow do for the prairie?",
    "What happens in late summer during the bison rut?",
    "How should we read the IUCN letter for American bison?",
    "What official U.S. honor do American bison hold?",
    "Why do American bison matter to many Plains Indigenous peoples?",
    "Why does it matter that bison and cattle can have calves together?",
)

EASY_STEMS = (
    "Where do American bison live in the wild?",
    "What makes the front of an American bison look so big?",
    "How does an American bison’s coat change with the seasons?",
    "Who has horns, and what are they for?",
    "What do American bison mostly eat?",
    "How do bison herds usually work?",
    "What color are new bison calves?",
    "Why do bison roll in dust or mud wallows?",
    "How should people care around wild bison and their home?",
    "Are American bison true buffalo?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "30 million",
    "60 million",
    "500,000",
    "541",
    "15,000",
    "20,500",
    "kg",
    "cm",
    "mph",
    "km/h",
)
REDO_THEMES = (
    "Open grasslands, plains, and river valleys of North America",
    "A massive front end with a tall shoulder hump",
    "A thick dark winter coat, then a lighter summer coat",
    "Both males and females have short curved horns for defense and herd status",
    "Mostly grasses and sedges — they graze and chew cud like cattle cousins",
    "Moms and calves live in groups; older bulls often stay apart except in breeding season",
    "They often start lighter / reddish-brown",
    "Rolling in a wallow can help with bugs and can be a kind of play",
    "Give wild bison space and keep prairie habitat healthy",
    "“buffalo” is a nickname; true buffalo live in Africa and Asia",
    "Plains bison are often smaller with a more rounded hump; wood bison are usually larger with a taller, squarer hump",
    "Only two living bison species — the American bison and the European bison, also called the wisent",
    "They sweep snow aside with the head, like a snow plow, to reach winter grass",
    "They can sprint about as fast as a slow highway car and jump surprisingly high fences",
    "Dust and mud wallows can help more prairie plants and bugs find a home",
    "Bulls bellow and tend cows during the late-summer breeding season",
    "Near Threatened is a snapshot — they were nearly wiped out in the late 1800s, then parks, tribes, and ranchers slowly helped them come back",
    "They are the official national mammal of the United States (named in 2016)",
    "They have deep cultural and spiritual importance for many Plains Indigenous peoples",
    "They belong to the same broad cattle family, and mixing can matter for keeping some conservation herds more purely bison",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class AmericanBisonZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("american-bison", study_card_ids())
        self.assertEqual(
            shipped_levels_for("american-bison"),
            ("easy", "hard", "zoologist"),
        )
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("american-bison", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_AMERICAN_BISON)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, American bison.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_AMERICAN_BISON))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_AMERICAN_BISON))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("american-bison", "zoologist")
        easy = study_deck_for("american-bison", "easy")
        hard = study_deck_for("american-bison", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("american-bison", "zoologist")
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
        self.assertIn("Bison bison", correct_choice_text(questions[0]))
        self.assertIn("athabascae", correct_choice_text(questions[0]))
        self.assertIn("ecotype", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("bos", correct_choice_text(questions[1]).lower())
        self.assertIn("yak", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("bovini", correct_choice_text(questions[2]).lower())
        self.assertIn("cattle", correct_choice_text(questions[2]).lower())
        self.assertIn("even-toed", correct_choice_text(questions[2]).lower())
        self.assertIn("priscus", correct_choice_text(questions[3]))
        self.assertIn("pleistocene", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("founding pool", correct_choice_text(questions[4]).lower())
        self.assertIn("genetic squeeze", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("cattle dna", correct_choice_text(questions[5]).lower())
        self.assertIn("pure", correct_choice_text(questions[5]).lower())
        self.assertIn("conservation herds", correct_choice_text(questions[5]).lower())
        self.assertIn("sister", correct_choice_text(questions[6]).lower())
        self.assertIn("mitochondrial", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("grazing", correct_choice_text(questions[7]).lower())
        self.assertIn("wallow", correct_choice_text(questions[7]).lower())
        self.assertIn("plant", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("wild", correct_choice_text(questions[8]).lower())
        self.assertIn("ranch", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("department of the interior", correct_choice_text(questions[9]).lower())
        self.assertIn("park herds", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "athabascae",
            "Bison bison",
            "introgression",
            "incomplete lineage sorting",
            "metapopulation",
            "Bovini",
            "priscus",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_AMERICAN_ALLIGATOR + PUSH_FURTHER_AMERICAN_ALLIGATOR
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_AMERICAN_BISON + PUSH_FURTHER_AMERICAN_BISON:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_AMERICAN_BISON).lower()
        push = " ".join(PUSH_FURTHER_AMERICAN_BISON).lower()
        self.assertIn("bos", talk)
        self.assertIn("nest", talk)
        self.assertIn("founding pool", talk)
        self.assertIn("wild", talk)
        self.assertIn("ranch", talk)
        self.assertIn("subspecies", push)
        self.assertIn("cattle dna", push)
        self.assertIn("mtdna", push)
        self.assertIn("puzzle", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("american-bison", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "american-bison", "packTemplate": "animals"})
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
        deck = study_deck_for("american-bison", "zoologist")
        sheet = study_print_html(
            deck,
            name="American bison",
            emoji="🦬",
            photo="/field-pack/photos/american-bison.jpg?v=img2",
            photo_pos="50% 25%",
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
        for prompt in TALK_ABOUT_AMERICAN_BISON + PUSH_FURTHER_AMERICAN_BISON:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_AMERICAN_BISON, sheet)
        self.assertIn("Facts from Wikipedia, American bison.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("american-bison", "zoologist"))
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
        self.assertEqual(shipped_levels_for("american-alligator"), ("easy", "hard", "zoologist"))
        gator_zoo = study_deck_for("american-alligator", "zoologist")
        self.assertEqual(gator_zoo["source"], WIKI_AMERICAN_ALLIGATOR)
        gator_html = GATOR.read_text(encoding="utf-8")
        self.assertIn("Zoologist", gator_html)
        self.assertEqual(gator_zoo["talk_about"], list(TALK_ABOUT_AMERICAN_ALLIGATOR))
        self.assertEqual(gator_zoo["push_further"], list(PUSH_FURTHER_AMERICAN_ALLIGATOR))
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", jelly)
        self.assertNotIn("What do they eat?", jelly)
        self.assertNotIn("bison-bison-taxonomy-soft", jelly)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["american-bison"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("bison-bison-taxonomy-soft", data_js)
        self.assertIn("nested-in-bos-soft", data_js)
        self.assertIn("metapopulation-soft", data_js)
        self.assertIn("european-mtdna-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = BISON.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
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
