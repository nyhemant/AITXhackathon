"""Cuttlefish Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger is a sibling level)."""

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
    PUSH_FURTHER_CLOWNFISH,
    PUSH_FURTHER_CRAB,
    PUSH_FURTHER_CUTTLEFISH,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_SHARK,
    STUDY_SLOTS,
    TALK_ABOUT_CLOWNFISH,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_LION,
    TALK_ABOUT_SHARK,
    WIKI_CLOWNFISH,
    WIKI_CRAB,
    WIKI_CUTTLEFISH,
    WIKI_LION,
    WIKI_SHARK,
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
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
OCTOPUS = FP / "cards" / "whale-shark" / "index.html"
CRAB = FP / "cards" / "crab" / "index.html"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
SHARK = FP / "cards" / "shark" / "index.html"
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
    "Marine molluscs related to squid and octopus",
    "Unique internal shell (cuttlebone) for buoyancy",
    "Eight arms plus two longer hunting tentacles",
    "Change skin color and pattern very fast",
    "Squirt ink to hide or confuse predators",
)

STEMS = (
    "What kind of animal is a cuttlefish?",
    "What does the cuttlebone help a cuttlefish do?",
    "How many arms and tentacles does a cuttlefish have?",
    "Why are cuttlefish nicknamed “chameleons of the sea”?",
    "How can a cuttlefish use ink when a predator comes?",
    "What do cuttlefish eyes look like in bright light?",
    "What do cuttlefish eat?",
    "About how long do cuttlefish usually live?",
    "How can people help cuttlefish?",
    "Are cuttlefish a kind of fish?",
)

QIDS = (
    "cephalopod-soft",
    "cuttlebone-soft",
    "arms-tentacles-soft",
    "camouflage-soft",
    "ink-soft",
    "w-eyes-soft",
    "hunt-soft",
    "short-life-soft",
    "soft-coastal-care",
    "not-a-fish-myth",
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
    "Sepiidae",
    "Sepiida",
    "chromatophore",
    "iridophore",
    "leucophore",
    "hemocyanin",
    "polarization",
    "Americas",
    "2023",
    "kg",
    "cm",
    "mph",
    "km/h",
)
# Explore more now uses Zoologist talk/push, so 2023 and hemocyanin
# may appear on the Junior Ranger page without leaking into JR questions.
PAGE_BRITTLE = tuple(p for p in BRITTLE if p not in ("2023", "hemocyanin"))
RESERVED = (
    "IUCN",
    "Sepiidae",
    "chromatophore",
    "hemocyanin",
    "polarization",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class CuttlefishEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_only(self):
        self.assertIn("cuttlefish", study_card_ids())
        self.assertNotIn("whale-shark", study_card_ids())
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
                "starfish",
                "stingray",
            ),
        )
        self.assertEqual(shipped_levels_for("cuttlefish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("cuttlefish", "hard"))
        self.assertIsNotNone(study_deck_for("cuttlefish", "zoologist"))
        self.assertIsNone(study_deck_for("whale-shark"))
        deck = study_deck_for("cuttlefish")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "cuttlefish")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_CUTTLEFISH)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Cuttlefish.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_CUTTLEFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_CUTTLEFISH))
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
        self.assertIn("cephalopod", blob.lower())
        self.assertIn("cuttlebone", blob.lower())
        self.assertIn("tentacle", blob.lower())
        self.assertIn("chameleon", blob.lower())
        self.assertIn("ink", blob.lower())
        self.assertIn("w-shaped", blob.lower())
        self.assertIn("crab", blob.lower())
        self.assertIn("1–2", blob)
        self.assertIn("coastal", blob.lower())
        self.assertIn("mollusc", blob.lower())
        self.assertEqual(WIKI_CUTTLEFISH, "https://en.wikipedia.org/wiki/Cuttlefish")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        shark = study_deck_for("shark")
        self.assertEqual(shark["source"], WIKI_SHARK)
        self.assertEqual(shark["talk_about"], list(TALK_ABOUT_SHARK))
        self.assertEqual(shark["push_further"], list(PUSH_FURTHER_SHARK))
        self.assertEqual(shipped_levels_for("shark"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("shark", "hard"))
        self.assertIsNotNone(study_deck_for("shark", "zoologist"))
        crab = study_deck_for("crab")
        self.assertEqual(crab["source"], WIKI_CRAB)
        self.assertEqual(crab["talk_about"], list(TALK_ABOUT_CRAB))
        self.assertEqual(crab["push_further"], list(PUSH_FURTHER_CRAB))
        self.assertEqual(shipped_levels_for("crab"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("crab", "hard"))
        self.assertIsNotNone(study_deck_for("crab", "zoologist"))
        clown = study_deck_for("clownfish")
        self.assertEqual(clown["source"], WIKI_CLOWNFISH)
        self.assertEqual(clown["talk_about"], list(TALK_ABOUT_CLOWNFISH))
        self.assertEqual(clown["push_further"], list(PUSH_FURTHER_CLOWNFISH))
        self.assertEqual(shipped_levels_for("clownfish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("clownfish", "hard"))
        self.assertIsNotNone(study_deck_for("clownfish", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "cuttlefish", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_CUTTLEFISH + PUSH_FURTHER_CUTTLEFISH:
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
            "A cephalopod — the same big group as squid, octopus, and nautilus",
            html,
        )
        self.assertIn(
            "No — they’re molluscs (soft bodies + a shell inside), closer to octopus than to tuna",
            html,
        )
        self.assertIn("Facts from Wikipedia, Cuttlefish.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("What kind of animal is a cuttlefish", html)
        jelly = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", jelly)
        self.assertNotIn("card-study-pack", jelly)
        self.assertNotIn("What kind of animal is a cuttlefish", jelly)

    def test_published_cuttlefish_card_matches_easy_deck(self):
        html = CUTTLEFISH.read_text(encoding="utf-8")
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
        self.assertIn("/field-pack/photos/cuttlefish.jpg", main)
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=cuttlefish",
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
        self.assertIn('"id": "cuttlefish"', html)
        self.assertNotIn('"id": "crab"', html)
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
        for prompt in TALK_ABOUT_CUTTLEFISH + PUSH_FURTHER_CUTTLEFISH:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("cuttlefish"),
            ["crab", "clownfish", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("cuttlefish")
        sheet = study_print_html(
            deck,
            name="Cuttlefish",
            emoji="🦑",
            photo="/field-pack/photos/cuttlefish.jpg?v=img2",
            photo_pos="50% 28%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/cuttlefish.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_CUTTLEFISH, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "A cephalopod — the same big group as squid, octopus, and nautilus",
            sheet,
        )
        self.assertIn(
            "No — they’re molluscs (soft bodies + a shell inside), closer to octopus than to tuna",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_CUTTLEFISH + PUSH_FURTHER_CUTTLEFISH:
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

    def test_artifacts_include_cuttlefish_easy_and_hard(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("cuttlefish", payload)
        self.assertNotIn("whale-shark", payload)
        self.assertIn("crab", payload)
        self.assertIn("clownfish", payload)
        self.assertIn("shark", payload)
        fish = payload["cuttlefish"]
        self.assertEqual(fish["id"], "cuttlefish")
        self.assertEqual(set(fish["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(fish["levels"]["hard"]["teach"], [])
        self.assertEqual(fish["levels"]["zoologist"]["teach"], [])
        easy = fish["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"cuttlefish"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(set(payload["crab"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["clownfish"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["shark"]["levels"]), {"easy", "hard", "zoologist"})
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
        cuttle_html = CUTTLEFISH.read_text(encoding="utf-8")
        visible = _text(_main(cuttle_html))
        self.assertIn("Junior Ranger", visible)
        self.assertIn("Park Ranger", visible)
        self.assertIn("Zoologist", visible)
        crab_html = CRAB.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(crab_html)))
        self.assertIn("Park Ranger", _text(_main(crab_html)))
        self.assertIn("Zoologist", _text(_main(crab_html)))
        clown_html = CLOWNFISH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(clown_html)))
        self.assertIn("Park Ranger", _text(_main(clown_html)))
        self.assertIn("Zoologist", _text(_main(clown_html)))
        shark_html = SHARK.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(shark_html)))
        self.assertIn("Park Ranger", _text(_main(shark_html)))
        self.assertIn("Zoologist", _text(_main(shark_html)))


if __name__ == "__main__":
    unittest.main()
