"""Sumatran tiger Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    correct_choice_text,
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_FLAMINGO,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_HIPPO,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PENGUIN,
    PUSH_FURTHER_TIGER,
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_ZEBRA,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_HIPPO,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_TIGER,
    TALK_ABOUT_TORTOISE,
    TALK_ABOUT_ZEBRA,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
    WIKI_GALAPAGOS_TORTOISE,
    WIKI_GIRAFFE,
    WIKI_HIPPOPOTAMUS,
    WIKI_LION,
    WIKI_PLAINS_ZEBRA,
    WIKI_SUMATRAN_TIGER,
    level_display_name,
    shipped_levels_for,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
TIGER = FP / "cards" / "sumatran-tiger" / "index.html"
HIPPO = FP / "cards" / "nile-hippo" / "index.html"
ZEBRA = FP / "cards" / "zebra" / "index.html"
TORTOISE = FP / "cards" / "galapagos-tortoise" / "index.html"
FLAMINGO = FP / "cards" / "caribbean-flamingo" / "index.html"
PENGUIN = FP / "cards" / "african-penguin" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "What did the 2017 Cat Specialist Group review do with living Sumatran tigers and the extinct Bali and Java tigers?",
    "How should we read a Critically Endangered letter for the Sumatran tiger?",
    "About how many Sumatran tigers are thought to remain in the wild?",
    "What is a major driver of Sumatran tiger forest loss?",
    "How did Sumatran tigers become cut off from mainland tigers?",
    "What do mitochondrial DNA and microsatellite studies say about Sumatran tigers versus mainland tigers?",
    "What is a genetics worry in captive Sumatran tigers?",
    "How does international law treat trade in tigers, including the Sumatran tiger?",
    "How do wire snares harm Sumatran tigers even when a hunter is not targeting a tiger?",
    "Where do people and Sumatran tigers most often come into conflict?",
)

ZOOLOGIST_IDS = (
    "sondaica",
    "cr-snapshot",
    "population-soft",
    "palm-acacia",
    "island-isolation",
    "mtdna-isolation",
    "studbook",
    "cites",
    "snares",
    "conflict-edges",
)

HARD_STEMS = (
    "Why do Sumatran tigers need thick cover on the forest floor?",
    "Which kind of land do Sumatran tigers use most?",
    "What kinds of animals do Sumatran tigers usually hunt in the forest?",
    "How is Sumatran tiger habitat spread across the island?",
    "What puts wild Sumatran tigers under pressure today?",
    "Across what kinds of forest can wild Sumatran tigers live?",
    "How does a tiger usually catch its prey?",
    "What kind of forest do Sumatran tigers need to thrive?",
    "What happens near the ends of a Sumatran tiger’s stripes?",
    "Where do the largest groups of wild Sumatran tigers live?",
)

EASY_STEMS = (
    "Where do wild Sumatran tigers live?",
    "How does a Sumatran tiger’s size compare with other living tigers?",
    "What is special about a Sumatran tiger’s stripes?",
    "What kind of place do Sumatran tigers prefer?",
    "What do wild Sumatran tigers hunt?",
    "How do Sumatran tigers usually live?",
    "What do you call a baby Sumatran tiger?",
    "What extra fur can a male Sumatran tiger show?",
    "Why is the Sumatran tiger called the last Sunda island tiger?",
    "Are Sumatran tigers scared of water, like a cartoon house cat?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "618",
    "1,000",
    "1000",
    "12,000",
    "12000",
    "6,000",
    "6000",
    "kyr",
    "15 founder",
    "375",
    "220 lb",
    "310 lb",
    "100 kg",
    "140 kg",
    "3,200",
    "3200",
)
REDO_THEMES = (
    "only on the island of Sumatra",
    "among the smallest living tigers",
    "denser, with little spots between the stripes",
    "Forest with cover, not open grassland",
    "Deer, wild pigs, and other forest prey",
    "Mostly alone, not in a lion-style pride",
    "cheek and neck ruff",
    "last Sunda island tiger",
    "tigers are strong swimmers",
    "Thick understory cover hides them",
    "uncultivated forest and make little use of plantations",
    "mid-sized forest mammals",
    "small, scattered habitat patches",
    "Habitat loss, fewer prey animals, and hunting or snares",
    "coastal lowland forest up into high mountain forest",
    "ambush, not a long open chase",
    "Large connected forest blocks",
    "dissolve into spots",
    "major national parks, which hold the biggest remaining groups",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class TigerZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("sumatran-tiger"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("sumatran-tiger", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_SUMATRAN_TIGER)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Sumatran tiger.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_TIGER))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_TIGER))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("sumatran-tiger", "zoologist")
        easy = study_deck_for("sumatran-tiger", "easy")
        hard = study_deck_for("sumatran-tiger", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("sumatran-tiger", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("sondaica", correct_choice_text(questions[0]))
        self.assertIn("sumatrae", correct_choice_text(questions[0]))
        self.assertIn("2017", questions[0]["stem"])
        self.assertIn("Cat Specialist Group", questions[0]["stem"])
        self.assertIn("P. t. sondaica", questions[0]["why"])
        self.assertIn("sumatrae", questions[0]["why"])
        self.assertIn("Critically Endangered", correct_choice_text(questions[1]))
        self.assertIn("snapshot", correct_choice_text(questions[1]).lower() + questions[1]["why"].lower())
        self.assertIn("hundreds", correct_choice_text(questions[2]).lower())
        self.assertIn("fragmented", correct_choice_text(questions[2]).lower())
        self.assertIn("oil palm", correct_choice_text(questions[3]).lower())
        self.assertIn("acacia", correct_choice_text(questions[3]).lower())
        self.assertIn("Ice Age", correct_choice_text(questions[4]))
        self.assertIn("approximate", correct_choice_text(questions[4]).lower())
        self.assertIn("land bridge", questions[4]["why"].lower())
        self.assertIn("mtdna", correct_choice_text(questions[5]).lower())
        self.assertIn("microsatellite", correct_choice_text(questions[5]).lower())
        self.assertIn("mainland", correct_choice_text(questions[5]).lower())
        self.assertIn("studbook", correct_choice_text(questions[6]).lower())
        self.assertIn("founders", correct_choice_text(questions[6]).lower())
        self.assertIn("vestibular", correct_choice_text(questions[6]).lower())
        self.assertIn("CITES Appendix I", correct_choice_text(questions[7]))
        self.assertIn("tightly controlled", correct_choice_text(questions[7]).lower())
        self.assertIn("wire snares", correct_choice_text(questions[8]).lower())
        self.assertIn("accident", correct_choice_text(questions[8]).lower())
        self.assertIn("farms", correct_choice_text(questions[9]).lower())
        self.assertIn("settlements", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("sumatran-tiger", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "sumatran-tiger", "packTemplate": "animals"})
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
        deck = study_deck_for("sumatran-tiger", "zoologist")
        sheet = study_print_html(
            deck,
            name="Sumatran tiger",
            emoji="🐯",
            photo="/field-pack/photos/sumatran-tiger.jpg?v=img2",
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
        for prompt in TALK_ABOUT_TIGER + PUSH_FURTHER_TIGER:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_SUMATRAN_TIGER, sheet)
        self.assertIn("Facts from Wikipedia, Sumatran tiger.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("sumatran-tiger", "zoologist"))
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
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        giraffe_zoo = study_deck_for("reticulated-giraffe", "zoologist")
        self.assertEqual(giraffe_zoo["source"], WIKI_GIRAFFE)
        self.assertIn("Giraffa reticulata", correct_choice_text(giraffe_zoo["questions"][0]))
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giraffe_html)
        self.assertIn("Junior Ranger", giraffe_html)
        self.assertIn("Park Ranger", giraffe_html)
        self.assertEqual(giraffe_zoo["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_zoo["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_zoo = study_deck_for("african-elephant", "zoologist")
        self.assertEqual(elephant_zoo["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Loxodonta africana", correct_choice_text(elephant_zoo["questions"][0]))
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertIn("Junior Ranger", elephant_html)
        self.assertIn("Park Ranger", elephant_html)
        self.assertEqual(elephant_zoo["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_zoo["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        penguin_zoo = study_deck_for("african-penguin", "zoologist")
        self.assertEqual(penguin_zoo["source"], WIKI_AFRICAN_PENGUIN)
        self.assertIn("Spheniscus", correct_choice_text(penguin_zoo["questions"][0]))
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", penguin_html)
        self.assertIn("Junior Ranger", penguin_html)
        self.assertIn("Park Ranger", penguin_html)
        self.assertEqual(penguin_zoo["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin_zoo["push_further"], list(PUSH_FURTHER_PENGUIN))
        self.assertEqual(shipped_levels_for("caribbean-flamingo"), ("easy", "hard", "zoologist"))
        flamingo_zoo = study_deck_for("caribbean-flamingo", "zoologist")
        self.assertEqual(flamingo_zoo["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertIn("Mirandornithes", correct_choice_text(flamingo_zoo["questions"][0]))
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", flamingo_html)
        self.assertIn("Junior Ranger", flamingo_html)
        self.assertIn("Park Ranger", flamingo_html)
        self.assertEqual(flamingo_zoo["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(flamingo_zoo["push_further"], list(PUSH_FURTHER_FLAMINGO))
        self.assertEqual(shipped_levels_for("galapagos-tortoise"), ("easy", "hard", "zoologist"))
        tortoise_zoo = study_deck_for("galapagos-tortoise", "zoologist")
        self.assertEqual(tortoise_zoo["source"], WIKI_GALAPAGOS_TORTOISE)
        self.assertIn("Chelonoidis", correct_choice_text(tortoise_zoo["questions"][0]))
        tortoise_html = TORTOISE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", tortoise_html)
        self.assertIn("Junior Ranger", tortoise_html)
        self.assertIn("Park Ranger", tortoise_html)
        self.assertEqual(tortoise_zoo["talk_about"], list(TALK_ABOUT_TORTOISE))
        self.assertEqual(tortoise_zoo["push_further"], list(PUSH_FURTHER_TORTOISE))
        self.assertEqual(shipped_levels_for("zebra"), ("easy", "hard", "zoologist"))
        zebra_zoo = study_deck_for("zebra", "zoologist")
        self.assertEqual(zebra_zoo["source"], WIKI_PLAINS_ZEBRA)
        self.assertIn("Equus quagga", correct_choice_text(zebra_zoo["questions"][0]))
        zebra_html = ZEBRA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", zebra_html)
        self.assertIn("Junior Ranger", zebra_html)
        self.assertIn("Park Ranger", zebra_html)
        self.assertEqual(zebra_zoo["talk_about"], list(TALK_ABOUT_ZEBRA))
        self.assertEqual(zebra_zoo["push_further"], list(PUSH_FURTHER_ZEBRA))
        self.assertEqual(shipped_levels_for("nile-hippo"), ("easy", "hard", "zoologist"))
        hippo_zoo = study_deck_for("nile-hippo", "zoologist")
        self.assertEqual(hippo_zoo["source"], WIKI_HIPPOPOTAMUS)
        self.assertIn("Hipposudoric acids", correct_choice_text(hippo_zoo["questions"][0]))
        hippo_html = HIPPO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", hippo_html)
        self.assertIn("Junior Ranger", hippo_html)
        self.assertIn("Park Ranger", hippo_html)
        self.assertEqual(hippo_zoo["talk_about"], list(TALK_ABOUT_HIPPO))
        self.assertEqual(hippo_zoo["push_further"], list(PUSH_FURTHER_HIPPO))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["sumatran-tiger"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("sondaica", data_js)
        self.assertIn("cr-snapshot", data_js)
        self.assertIn("palm-acacia", data_js)
        self.assertIn("conflict-edges", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = TIGER.read_text(encoding="utf-8")
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
