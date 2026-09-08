"""Zebra Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_FLAMINGO,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PENGUIN,
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_ZEBRA,
    STUDY_SLOTS,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_TORTOISE,
    TALK_ABOUT_ZEBRA,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
    WIKI_GALAPAGOS_TORTOISE,
    WIKI_GIRAFFE,
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
    "What scientific name do scientists use for the plains zebra today?",
    "The plains zebra is one of how many living zebra species?",
    "What do DNA studies say about the extinct quagga and today’s plains zebra?",
    "How does plains-zebra striping tend to change from north to south?",
    "What does experimental and comparative research currently favor as a leading job of zebra stripes?",
    "How does a stallion check whether a mare is ready to mate?",
    "What often happens to a plains zebra harem when a new stallion takes over?",
    "What does a mother plains zebra do with her newborn at first?",
    "What do studies suggest migratory plains-zebra herds use to find good grazing?",
    "What do scientists emphasize about wild plains-zebra numbers today?",
)

ZOOLOGIST_IDS = (
    "species-name",
    "three-species",
    "quagga",
    "stripe-cline",
    "fly-deeper",
    "flehmen",
    "harem-takeover",
    "foal-guard",
    "migration-memory",
    "status-soft",
)

HARD_STEMS = (
    "What is a leading idea today for why plains zebras have stripes?",
    "What is a plains zebra harem?",
    "What do young male plains zebras often do before starting a harem?",
    "Why are plains zebras often called pioneer grazers?",
    "How does a plains zebra digest grass compared with a cow-like ruminant?",
    "How tied are plains zebras to drinking water?",
    "What do plains zebras often do when they spot a predator?",
    "What colour are a newborn plains zebra’s stripes at first?",
    "What extra marking do some southern plains zebras show between the black and white?",
    "What puts wild plains zebras under pressure today?",
)

EASY_STEMS = (
    "What is special about a plains zebra’s coat?",
    "What do plains zebras mostly eat?",
    "Where do wild plains zebras live?",
    "How do plains zebras live together?",
    "What do you call a baby plains zebra?",
    "How do plains zebras escape danger?",
    "What animal is a plains zebra a wild relative of?",
    "What is a plains zebra’s mane like?",
    "What contact call is a plains zebra known for?",
    "Are plains zebras just striped farm horses you can ride?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "500,000",
    "500 000",
    " km/h",
    "60 km",
    "70 km",
    "120,000",
    "290,000",
    "370,000",
    "Least Concern",
    "least concern",
    "Endangered",
    "Critically Endangered",
    "critically endangered",
)
REDO_THEMES = (
    "each zebra’s pattern is unique",
    "Bold black-and-white stripes",
    "Grass (plants, not meat)",
    "African grassland / savanna",
    "family groups (a stallion with mares",
    "They can run fast",
    "The horse (same horse family)",
    "Short and upright along the neck",
    "kwaha",
    "not domesticated like horses",
    "Stripes help deter biting flies",
    "One stallion, several mares, and their young",
    "bachelor groups of other young males",
    "tall, tough grass",
    "hindgut fermenter — food moves through faster",
    "seldom wander far from drinking water",
    "They bark or snort, and the group stays alert",
    "Brownish — they darken with age",
    "Brown “shadow” stripes — commoner in some southern populations",
    "Hunting and habitat loss / farming encroachment",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class ZebraZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertEqual(shipped_levels_for("zebra"), ("easy", "hard", "zoologist"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("zebra", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_PLAINS_ZEBRA)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Plains zebra.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_ZEBRA))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_ZEBRA))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("zebra", "zoologist")
        easy = study_deck_for("zebra", "easy")
        hard = study_deck_for("zebra", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("zebra", "zoologist")
        questions = deck["questions"]
        self.assertEqual([q["slot"] for q in questions], list(range(1, 11)))
        self.assertEqual([q["id"] for q in questions], list(ZOOLOGIST_IDS))
        self.assertEqual([q["stem"] for q in questions], list(ZOOLOGIST_STEMS))
        for q in questions:
            self.assertEqual(len(q["choices"]), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(q["why"].strip())
            self.assertTrue(q["title"].strip())
        self.assertIn("Equus quagga", questions[0]["choices"][1])
        self.assertIn("burchellii", questions[0]["choices"][1])
        self.assertIn("three living", questions[1]["choices"][1].lower())
        self.assertIn("Grévy", questions[1]["choices"][1])
        self.assertIn("mountain zebra", questions[1]["choices"][1].lower())
        self.assertIn("close relationship", questions[2]["choices"][1].lower())
        self.assertIn("species complex", questions[2]["choices"][1].lower())
        self.assertIn("subspecies forever", questions[2]["why"].lower())
        self.assertIn("lessen toward the south", questions[3]["choices"][1].lower())
        self.assertIn("shadow", questions[3]["choices"][1].lower())
        self.assertIn("cline", questions[3]["why"].lower())
        self.assertIn("experimental", questions[4]["stem"].lower())
        self.assertIn("fly deterrence", questions[4]["choices"][1].lower())
        self.assertIn("debated", questions[4]["choices"][1].lower())
        self.assertIn("camouflage", questions[4]["choices"][1].lower())
        self.assertIn("flehmen", questions[5]["choices"][1].lower())
        self.assertIn("vomeronasal", questions[5]["choices"][1].lower())
        self.assertIn("gradually", questions[6]["choices"][1].lower())
        self.assertIn("mare membership", questions[6]["choices"][1].lower())
        self.assertIn("even the stallion", questions[7]["choices"][1].lower())
        self.assertIn("Memory of places", questions[8]["choices"][1])
        self.assertIn("not only day-to-day", questions[8]["choices"][1].lower())
        self.assertIn("Hunting and habitat", questions[9]["choices"][1])
        self.assertIn("Near Threatened", questions[9]["choices"][1])
        self.assertIn("snapshot", questions[9]["choices"][1].lower() + questions[9]["why"].lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("zebra", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "zebra", "packTemplate": "animals"})
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
        deck = study_deck_for("zebra", "zoologist")
        sheet = study_print_html(
            deck,
            name="Zebra",
            emoji="🦓",
            photo="/field-pack/photos/zebra.jpg?v=img2",
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
        for prompt in TALK_ABOUT_ZEBRA + PUSH_FURTHER_ZEBRA:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_PLAINS_ZEBRA, sheet)
        self.assertIn("Facts from Wikipedia, Plains zebra.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("zebra", "zoologist"))
        self.assertNotIn("study-teach", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn("Zoologist", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_other_animal_decks_untouched(self):
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        lion_zoo = study_deck_for("african-lion", "zoologist")
        self.assertEqual(lion_zoo["source"], WIKI_LION)
        self.assertIn("hyoid", lion_zoo["questions"][0]["choices"][1])
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Zoologist", lion_html)
        self.assertIn("Junior Ranger", lion_html)
        self.assertIn("Park Ranger", lion_html)
        self.assertEqual(lion_zoo["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion_zoo["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        giraffe_zoo = study_deck_for("reticulated-giraffe", "zoologist")
        self.assertEqual(giraffe_zoo["source"], WIKI_GIRAFFE)
        self.assertIn("Giraffa reticulata", giraffe_zoo["questions"][0]["choices"][1])
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", giraffe_html)
        self.assertIn("Junior Ranger", giraffe_html)
        self.assertIn("Park Ranger", giraffe_html)
        self.assertEqual(giraffe_zoo["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe_zoo["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("african-elephant"), ("easy", "hard", "zoologist"))
        elephant_zoo = study_deck_for("african-elephant", "zoologist")
        self.assertEqual(elephant_zoo["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertIn("Loxodonta africana", elephant_zoo["questions"][0]["choices"][1])
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Zoologist", elephant_html)
        self.assertIn("Junior Ranger", elephant_html)
        self.assertIn("Park Ranger", elephant_html)
        self.assertEqual(elephant_zoo["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant_zoo["push_further"], list(PUSH_FURTHER_ELEPHANT))
        self.assertEqual(shipped_levels_for("african-penguin"), ("easy", "hard", "zoologist"))
        penguin_zoo = study_deck_for("african-penguin", "zoologist")
        self.assertEqual(penguin_zoo["source"], WIKI_AFRICAN_PENGUIN)
        self.assertIn("Spheniscus", penguin_zoo["questions"][0]["choices"][1])
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", penguin_html)
        self.assertIn("Junior Ranger", penguin_html)
        self.assertIn("Park Ranger", penguin_html)
        self.assertEqual(penguin_zoo["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin_zoo["push_further"], list(PUSH_FURTHER_PENGUIN))
        self.assertEqual(shipped_levels_for("caribbean-flamingo"), ("easy", "hard", "zoologist"))
        flamingo_zoo = study_deck_for("caribbean-flamingo", "zoologist")
        self.assertEqual(flamingo_zoo["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertIn("Mirandornithes", flamingo_zoo["questions"][0]["choices"][1])
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Zoologist", flamingo_html)
        self.assertIn("Junior Ranger", flamingo_html)
        self.assertIn("Park Ranger", flamingo_html)
        self.assertEqual(flamingo_zoo["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(flamingo_zoo["push_further"], list(PUSH_FURTHER_FLAMINGO))
        self.assertEqual(shipped_levels_for("galapagos-tortoise"), ("easy", "hard", "zoologist"))
        tortoise_zoo = study_deck_for("galapagos-tortoise", "zoologist")
        self.assertEqual(tortoise_zoo["source"], WIKI_GALAPAGOS_TORTOISE)
        self.assertIn("Chelonoidis", tortoise_zoo["questions"][0]["choices"][1])
        tortoise_html = TORTOISE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", tortoise_html)
        self.assertIn("Junior Ranger", tortoise_html)
        self.assertIn("Park Ranger", tortoise_html)
        self.assertEqual(tortoise_zoo["talk_about"], list(TALK_ABOUT_TORTOISE))
        self.assertEqual(tortoise_zoo["push_further"], list(PUSH_FURTHER_TORTOISE))

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["zebra"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("Equus quagga", data_js)
        self.assertIn("stripe-cline", data_js)
        self.assertIn("flehmen", data_js)
        self.assertIn("migration-memory", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = ZEBRA.read_text(encoding="utf-8")
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


if __name__ == "__main__":
    unittest.main()
