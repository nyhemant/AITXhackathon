"""Octopus Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger is a sibling level)."""

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
    LEVEL_DISPLAY_NAMES,
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_KELP_FOREST,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_MANTA_RAY,
    PUSH_FURTHER_OCTOPUS,
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_OCTOPUS,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
    level_display_name,
    shipped_levels_for,
    study_card_ids,
    study_deck_for,
    study_print_html,
    study_try_next_ids,
    target_letter_for_slot,
    validate_deck,
)

FP = REPO / "static" / "field-pack"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
SEAHORSE = FP / "cards" / "stingray" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
PRINT_KIT = FP / "js" / "print-kit.js"
STUDY_JS = FP / "js" / "study-card.js"
STYLES = FP / "css" / "styles.css"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"

GENERIC_WORKSHEET = (
    "What do they eat?",
    "Where is home?",
    "What is their superpower?",
    "Baby or grown-up?",
    "I want to teach about…",
    "Food detective",
    "Meat eater or plant eater?",
    "What do you notice?",
)

TEACH = (
    "Soft-bodied sea animals with eight arms (molluscs, not fish)",
    "Arms have suckers that grip and help feel/taste what they touch",
    "They can change colour (and skin texture) to hide",
    "When scared, many squirt dark ink and jet away",
    "Almost no hard parts — they squeeze through tiny gaps (the beak is the hard bit)",
)

STEMS = (
    "How many arms does an octopus have?",
    "Why can an octopus squeeze through a tiny gap?",
    "How can an octopus hide in plain sight?",
    "What can many octopuses do when a predator comes?",
    "What does an octopus use to eat, and what does it hunt?",
    "Where do many octopuses hide, and what clue might sit outside?",
    "What is special about octopus blood and hearts, if we keep it kid-simple?",
    "Where do octopuses live?",
    "How many kinds of octopus are there, if we keep the count soft?",
    "Do octopuses have tentacles?",
)

QIDS = (
    "eight-arms-soft",
    "soft-squeeze-soft",
    "colour-change-soft",
    "ink-escape-soft",
    "beak-hunt-soft",
    "den-home-soft",
    "blue-blood-hearts-soft",
    "ocean-homes-soft",
    "many-kinds-soft",
    "arms-not-tentacles-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Endangered",
    "Vulnerable",
    "Critically",
    "Near Threatened",
    "Least Concern",
    "CITES",
    "Cirrina",
    "Incirrina",
    "chromatophore",
    "hemocyanin",
    "haemocyanin",
    "tetrodotoxin",
    "TTX",
    "RNA",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "IUCN",
    "Cirrina",
    "Incirrina",
    "chromatophore",
    "hemocyanin",
    "haemocyanin",
    "tetrodotoxin",
    "TTX",
    "RNA",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class OctopusEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_only(self):
        self.assertIn("octopus", study_card_ids())
        self.assertNotIn("stingray", study_card_ids())
        self.assertEqual(
            study_card_ids(),
            (
                "african-lion",
                "reticulated-giraffe",
                "african-elephant",
                "african-penguin",
                "caribbean-flamingo",
                "galapagos-tortoise",
                "zebra",
                "nile-hippo",
                "sumatran-tiger",
                "western-lowland-gorilla",
                "cheetah",
                "red-panda",
                "koala",
                "chimpanzee",
                "orangutan",
                "giant-panda",
                "ring-tailed-lemur",
                "ostrich",
                "warthog",
                "shark",
                "asian-small-clawed-otter",
                "two-toed-sloth",
                "freshwater-fish",
                "polar-bear",
                "sea-otter",
                "american-alligator",
                "american-bison",
                "elk",
                "puffin",
                "clownfish",
                "crab",
                "cuttlefish",
                "eel",
                "jellyfish",
                "kelp-forest",
                "manta-ray",
                "octopus",
                "sea-turtle",
                "seahorse",
            ),
        )
        self.assertEqual(shipped_levels_for("octopus"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("octopus", "hard"))
        self.assertIsNotNone(study_deck_for("octopus", "zoologist"))
        self.assertIsNone(study_deck_for("stingray"))
        deck = study_deck_for("octopus")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "octopus")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_OCTOPUS)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Octopus.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_OCTOPUS))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_OCTOPUS))
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)
        for q in deck["questions"]:
            self.assertEqual(len(q["choices"]), 3)
            self.assertEqual(len(set(q["choices"])), 3)
            self.assertIn(q["correct"], ("A", "B", "C"))
            self.assertTrue(str(q["why"]).strip())
        blob = " ".join(
            deck["teach"]
            + [
                q["stem"] + q["why"] + " ".join(q["choices"])
                for q in deck["questions"]
            ]
        )
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)
        self.assertIn("mollusc", blob.lower())
        self.assertIn("sucker", blob.lower())
        self.assertIn("colour", blob.lower())
        self.assertIn("ink", blob.lower())
        self.assertIn("beak", blob.lower())
        self.assertIn("midden", blob.lower())
        self.assertIn("blue", blob.lower())
        self.assertIn("three hearts", blob.lower())
        self.assertIn("fresh", blob.lower())
        self.assertIn("300", blob)
        self.assertIn("giant pacific", blob.lower())
        self.assertIn("tentacle", blob.lower())
        self.assertEqual(WIKI_OCTOPUS, "https://en.wikipedia.org/wiki/Octopus")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        manta = study_deck_for("manta-ray")
        self.assertEqual(manta["source"], WIKI_MANTA_RAY)
        self.assertEqual(manta["talk_about"], list(TALK_ABOUT_MANTA_RAY))
        self.assertEqual(manta["push_further"], list(PUSH_FURTHER_MANTA_RAY))
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("manta-ray", "hard"))
        self.assertIsNotNone(study_deck_for("manta-ray", "zoologist"))
        kelp = study_deck_for("kelp-forest")
        self.assertEqual(kelp["source"], WIKI_KELP_FOREST)
        self.assertEqual(kelp["talk_about"], list(TALK_ABOUT_KELP_FOREST))
        self.assertEqual(kelp["push_further"], list(PUSH_FURTHER_KELP_FOREST))
        self.assertEqual(shipped_levels_for("kelp-forest"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("kelp-forest", "hard"))
        self.assertIsNotNone(study_deck_for("kelp-forest", "zoologist"))
        jelly = study_deck_for("jellyfish")
        self.assertEqual(jelly["source"], WIKI_JELLYFISH)
        self.assertEqual(jelly["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(jelly["push_further"], list(PUSH_FURTHER_JELLYFISH))
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("jellyfish", "hard"))
        self.assertIsNotNone(study_deck_for("jellyfish", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "octopus", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("card-study-pack", html)
        self.assertIn("Learn first", html)
        self.assertIn('<details class="study-teach">', html)
        self.assertNotIn('<details class="study-teach" open', html)
        self.assertIn('<summary class="study-teach-kicker">', html)
        self.assertIn("tap to open", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        for prompt in TALK_ABOUT_OCTOPUS + PUSH_FURTHER_OCTOPUS:
            self.assertIn(prompt, html)
        self.assertIn("Show answers", html)
        self.assertIn("Score", html)
        for line in TEACH:
            self.assertIn(line, html)
        for stem in STEMS:
            self.assertIn(stem, html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, html)
        visible = _text(html)
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        self.assertIn('class="study-level-picker"', html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertNotIn('class="study-level-badge"', html)
        self.assertEqual(html.count('role="group"'), 2)
        self.assertIn("study-level-picker-bottom", html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        self.assertNotIn(" · Easy ·", html)
        self.assertNotIn(" · Hard ·", html)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, html)
        self.assertIn(
            "Eight sucker-lined arms — not the long clubbed tentacles of squid or cuttlefish",
            html,
        )
        self.assertIn(
            "No — people say “tentacles,” but octopuses have arms with suckers all along. Squid and cuttlefish add two longer tentacles",
            html,
        )
        self.assertIn("Facts from Wikipedia, Octopus.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "stingray", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("How many arms does an octopus", html)
        horse = SEAHORSE.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", horse)
        self.assertNotIn("card-study-pack", horse)
        self.assertNotIn("How many arms does an octopus", horse)

    def test_published_octopus_card_matches_easy_deck(self):
        html = OCTOPUS.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("Watch Live", main)
        self.assertIn("card-watch-live", main)
        self.assertIn("card-page-photo", main)
        self.assertIn("/field-pack/photos/octopus.jpg", main)
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=octopus",
            main,
        )
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "octopus"', html)
        self.assertNotIn('"id": "manta-ray"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=42", html)
        self.assertIn('<details class="study-teach">', main)
        self.assertNotIn('<details class="study-teach" open', main)
        self.assertNotIn('<div class="study-teach">', main)
        self.assertIn("Talk about it", main)
        self.assertIn("Push further", main)
        self.assertIn('<details class="study-explore', main)
        self.assertIn("Explore more", main)
        self.assertNotIn('<aside class="study-deepen"', main)
        self.assertLess(main.find("study-foot"), main.find("study-explore"))
        self.assertLess(main.find("study-explore"), main.find("card-try-next"))
        visible = _text(main)
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        self.assertIn('class="study-level-picker"', main)
        self.assertIn('data-study-pick="easy"', main)
        self.assertIn('data-study-pick="hard"', main)
        self.assertIn('data-study-pick="zoologist"', main)
        self.assertNotIn('class="study-level-badge"', main)
        self.assertIn("Learn first", main)
        self.assertIn(">Quiz</h2>", main)
        self.assertEqual(main.count("data-study-correct"), 2)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        self.assertNotIn(" · Easy ·", main)
        self.assertNotIn(" · Hard ·", main)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, main)
        print_tpl = html.split('id="study-print-template">', 1)[1].split("</template>", 1)[0]
        self.assertIn("Junior Ranger", print_tpl)
        self.assertNotIn(" · Easy ·", print_tpl)
        self.assertNotIn(" · Hard ·", print_tpl)
        self.assertNotIn("Explore more", print_tpl)
        front, _, back = print_tpl.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertNotIn("Push further", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        self.assertIn("ps-study-deepen", back)
        for prompt in TALK_ABOUT_OCTOPUS + PUSH_FURTHER_OCTOPUS:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("octopus"),
            ["cuttlefish", "jellyfish", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("octopus")
        sheet = study_print_html(
            deck,
            name="Octopus",
            emoji="🐙",
            photo="/field-pack/photos/octopus.jpg?v=img2",
            photo_pos="50% 30%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/octopus.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_OCTOPUS, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "Eight sucker-lined arms — not the long clubbed tentacles of squid or cuttlefish",
            sheet,
        )
        self.assertIn(
            "No — people say “tentacles,” but octopuses have arms with suckers all along. Squid and cuttlefish add two longer tentacles",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_OCTOPUS + PUSH_FURTHER_OCTOPUS:
            self.assertIn(prompt, back)
        css = STYLES.read_text(encoding="utf-8")
        self.assertIn(".ps-study-front", css)
        self.assertIn(".ps-study-deepen", css)
        js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn("function buildStudyCardHtml", js)
        self.assertIn("function studyDeckFor", js)
        self.assertIn("Junior Ranger", js)
        study_js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("Show answers", study_js)
        self.assertIn('details class="study-teach"', study_js)
        self.assertIn("study-deepen", study_js)
        self.assertIn("is-wrong-pick", study_js)
        self.assertIn("FPStudyLevelName", study_js + STUDY_DATA_JS.read_text(encoding="utf-8"))

    def test_artifacts_include_octopus_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("octopus", payload)
        self.assertNotIn("stingray", payload)
        self.assertIn("manta-ray", payload)
        self.assertIn("kelp-forest", payload)
        self.assertIn("jellyfish", payload)
        octo = payload["octopus"]
        self.assertEqual(octo["id"], "octopus")
        self.assertEqual(set(octo["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(octo["levels"]["zoologist"]["teach"], [])
        easy = octo["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"octopus"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(set(payload["manta-ray"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["kelp-forest"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["jellyfish"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["african-lion"]["levels"]), {"easy", "hard", "zoologist"})

    def test_display_name_map_still_covers_future_tiers(self):
        self.assertEqual(
            LEVEL_DISPLAY_NAMES,
            {
                "easy": "Junior Ranger",
                "hard": "Park Ranger",
                "zoologist": "Zoologist",
            },
        )
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        octo_html = OCTOPUS.read_text(encoding="utf-8")
        visible = _text(_main(octo_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(manta_html)))
        self.assertIn("Park Ranger", _text(_main(manta_html)))
        self.assertIn("Zoologist", _text(_main(manta_html)))
        kelp_html = KELP.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(kelp_html)))
        self.assertIn("Park Ranger", _text(_main(kelp_html)))
        self.assertIn("Zoologist", _text(_main(kelp_html)))
        jelly_html = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(jelly_html)))
        self.assertIn("Park Ranger", _text(_main(jelly_html)))
        self.assertIn("Zoologist", _text(_main(jelly_html)))


if __name__ == "__main__":
    unittest.main()
