"""Nile hippo Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_ZEBRA,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_HIPPO,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
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
    level_display_name,
    shipped_levels_for,
    study_deck_for,
    study_print_html,
    study_talk_html,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
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
    "What are the red and orange chemicals in a hippo’s skin goo?",
    "What do scientists say hippos share with living whales and dolphins?",
    "How useful are the named Nile hippo subspecies to people who study them in the field?",
    "Where did a wild hippo population start from animals that escaped a private collection?",
    "How does a Nile hippo’s stomach compare with a cow that chews cud?",
    "How do scientists usually describe the wild status of the common / Nile hippo today?",
    "What is unusual about how a Nile hippo can send a call?",
    "What is special about a Nile hippo’s big canines and incisors?",
    "How does a Nile hippo’s skeleton help it move in water?",
    "How many living hippo species do scientists recognise today?",
)

ZOOLOGIST_IDS = (
    "hipposudoric",
    "whale-clade",
    "subspecies",
    "colombia",
    "gut",
    "status-soft",
    "amphibious-call",
    "combat-teeth",
    "dense-bones",
    "two-living",
)

HARD_STEMS = (
    "How do Nile hippos usually move when they are underwater?",
    "Where does a bull Nile hippo usually hold territory?",
    "How do Nile hippos usually group up in water versus on land?",
    "What is a Nile hippo’s best-known long-carrying contact call?",
    "Where does a Nile hippo sit among the largest land mammals?",
    "Besides showing it is not blood, what jobs can a hippo’s reddish skin goo do?",
    "What must a Nile hippo still do even when it rests under water?",
    "Where do wild Nile hippos live?",
    "What puts wild Nile hippos under pressure today?",
    "How can a Nile hippo calf travel with its mother in deep water?",
)

EASY_STEMS = (
    "What does the name hippopotamus mean?",
    "What do Nile hippos usually do by day and at dusk?",
    "What do wild Nile hippos mostly eat?",
    "Why are a Nile hippo’s eyes, ears, and nostrils high on its head?",
    "What is the reddish liquid people call a hippo’s “blood sweat”?",
    "Who are a hippo’s closest living relatives?",
    "What does a hippo’s huge “yawn” usually mean?",
    "Why do people treat wild hippos with extra care?",
    "Where do Nile hippos often have babies, and how can calves drink milk?",
    "Can a Nile hippo stay dry on land all day like a horse?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "55 million",
    "60 million",
    "54 million",
    "52 million",
    "35 million",
    "115,000",
    "130,000",
    "115000",
    "1.5 t",
    "1.3 t",
    "40 cm",
    "50 cm",
    "100–110",
    "100 degrees",
    "Least Concern",
    "Endangered",
    "Critically Endangered",
    "CITES",
    "Appendix",
    " km/h",
)
REDO_THEMES = (
    "Horse of the river",
    "Stay cool in water or mud by day, then graze on land at dusk",
    "Almost all grass",
    "rest in water with most of its body hidden",
    "A sunscreen goo — not blood and not sweat",
    "Whales and dolphins — a surprise for many people",
    "The wide-open mouth is a threat",
    "dangerous when surprised",
    "calves can nurse underwater",
    "thick skin can crack if it stays dry",
    "walk or bounce along the bottom",
    "stretch of water — they show little territoriality",
    "rest in pods in the water, then typically graze alone",
    "wheeze-honk that can travel a long way",
    "among the next-largest land mammals",
    "works as a sunscreen and can help fight microbes",
    "Come up to breathe regularly",
    "Rivers, lakes, and mangrove swamps",
    "Habitat loss, plus hunting for meat and teeth",
    "rides on her back",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class HippoZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("nile-hippo"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("nile-hippo", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_HIPPOPOTAMUS)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Hippopotamus.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_HIPPO))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_HIPPO))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("nile-hippo", "zoologist")
        easy = study_deck_for("nile-hippo", "easy")
        hard = study_deck_for("nile-hippo", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("nile-hippo", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Hipposudoric acids", correct_choice_text(questions[0]))
        self.assertIn("norhipposudoric", questions[0]["why"].lower())
        self.assertIn("ultraviolet", questions[0]["why"].lower())
        self.assertIn("cetaceans", correct_choice_text(questions[1]).lower())
        self.assertIn("clade", correct_choice_text(questions[1]).lower())
        self.assertIn("anthracothere", questions[1]["why"].lower())
        self.assertIn("tens of millions", questions[1]["why"].lower())
        self.assertIn("subspecies have been described", correct_choice_text(questions[2]).lower())
        self.assertIn("rarely used", correct_choice_text(questions[2]).lower())
        self.assertIn("mitochondrial", correct_choice_text(questions[2]).lower())
        self.assertIn("Colombia", correct_choice_text(questions[3]))
        self.assertIn("Escobar", correct_choice_text(questions[3]))
        self.assertIn("feral", correct_choice_text(questions[3]).lower())
        self.assertIn("pseudoruminant", correct_choice_text(questions[4]).lower())
        self.assertIn("three-chambered", correct_choice_text(questions[4]).lower())
        self.assertIn("does not chew cud", correct_choice_text(questions[4]).lower())
        self.assertIn("Vulnerable", correct_choice_text(questions[5]))
        self.assertIn("snapshot", correct_choice_text(questions[5]).lower() + questions[5]["why"].lower())
        self.assertIn("air and water", correct_choice_text(questions[6]).lower())
        self.assertIn("clicks", correct_choice_text(questions[6]).lower())
        self.assertIn("keep growing", correct_choice_text(questions[7]).lower())
        self.assertIn("fighting", correct_choice_text(questions[7]).lower())
        self.assertIn("graviportal", correct_choice_text(questions[8]).lower())
        self.assertIn("sink", correct_choice_text(questions[8]).lower())
        self.assertIn("Hippopotamus amphibius", correct_choice_text(questions[9]))
        self.assertIn("pygmy", correct_choice_text(questions[9]).lower())
        self.assertIn("Choeropsis", questions[9]["why"])
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("nile-hippo", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "nile-hippo", "packTemplate": "animals"})
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
        deck = study_deck_for("nile-hippo", "zoologist")
        sheet = study_print_html(
            deck,
            name="Nile hippo",
            emoji="🦛",
            photo="/field-pack/photos/nile-hippo.jpg?v=img2",
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
        for prompt in TALK_ABOUT_HIPPO + PUSH_FURTHER_HIPPO:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_HIPPOPOTAMUS, sheet)
        self.assertIn("Facts from Wikipedia, Hippopotamus.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("nile-hippo", "zoologist"))
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

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["nile-hippo"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("hipposudoric", data_js)
        self.assertIn("whale-clade", data_js)
        self.assertIn("colombia", data_js)
        self.assertIn("two-living", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = HIPPO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn("study-card.js?v=9", html)
        self.assertIn("study-cards-data.js?v=5", html)
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
