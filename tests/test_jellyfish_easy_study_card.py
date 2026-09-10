"""Jellyfish Easy study-card: Junior Ranger teach + 10 MCQs (later tiers reserved)."""

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
    PUSH_FURTHER_EEL,
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_LION,
    STUDY_SLOTS,
    TALK_ABOUT_CLOWNFISH,
    TALK_ABOUT_CRAB,
    TALK_ABOUT_CUTTLEFISH,
    TALK_ABOUT_EEL,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_LION,
    WIKI_CLOWNFISH,
    WIKI_CRAB,
    WIKI_CUTTLEFISH,
    WIKI_EEL,
    WIKI_JELLYFISH,
    WIKI_LION,
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
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
EEL = FP / "cards" / "eel" / "index.html"
CUTTLEFISH = FP / "cards" / "cuttlefish" / "index.html"
CRAB = FP / "cards" / "crab" / "index.html"
CLOWNFISH = FP / "cards" / "clownfish" / "index.html"
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
    "Soft, jelly-bodied sea animals — not fish",
    "Umbrella-shaped bell plus trailing tentacles",
    "Tentacles carry stinging cells",
    "Swim by pulsing the bell",
    "Body is mostly water",
)

STEMS = (
    "Are jellyfish a kind of fish?",
    "What is the soft umbrella-shaped part of a jelly?",
    "What hang below a jelly’s bell?",
    "What do a jelly’s tentacles use to grab food?",
    "How does a jellyfish usually swim?",
    "How much of a jelly’s body is water, if we keep the share soft?",
    "What two stages do many jellies pass through?",
    "Where do jellyfish live?",
    "How can people help jellies and the shores they visit?",
    "Is a Portuguese man o’ war a true jellyfish?",
)

QIDS = (
    "not-fish-soft",
    "bell-soft",
    "tentacles-soft",
    "sting-soft",
    "pulse-swim-soft",
    "mostly-water-soft",
    "two-stages-soft",
    "everywhere-soft",
    "soft-coast-bloom-care",
    "man-o-war-not-jelly-myth",
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
    "Scyphozoa",
    "Cubozoa",
    "Hydrozoa",
    "Medusozoa",
    "nematocyst",
    "strobilation",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "IUCN",
    "Scyphozoa",
    "Cubozoa",
    "Hydrozoa",
    "Medusozoa",
    "nematocyst",
    "strobilation",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class JellyfishEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_only(self):
        self.assertIn("jellyfish", study_card_ids())
        self.assertNotIn("octopus", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy",))
        self.assertIsNone(study_deck_for("jellyfish", "hard"))
        self.assertIsNone(study_deck_for("jellyfish", "zoologist"))
        self.assertIsNone(study_deck_for("octopus"))
        deck = study_deck_for("jellyfish")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "jellyfish")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_JELLYFISH)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Jellyfish.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_JELLYFISH))
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
        self.assertIn("cnidarian", blob.lower())
        self.assertIn("coral", blob.lower())
        self.assertIn("anemone", blob.lower())
        self.assertIn("bell", blob.lower())
        self.assertIn("mesoglea", blob.lower())
        self.assertIn("tentacle", blob.lower())
        self.assertIn("sting", blob.lower())
        self.assertIn("plankton", blob.lower())
        self.assertIn("pulse", blob.lower() + " ".join(deck["teach"]).lower())
        self.assertIn("squeez", blob.lower())
        self.assertIn("95", blob)
        self.assertIn("polyp", blob.lower())
        self.assertIn("medusa", blob.lower())
        self.assertIn("fresh", blob.lower())
        self.assertIn("bloom", blob.lower())
        self.assertIn("man o", blob.lower())
        self.assertIn("colony", blob.lower())
        self.assertEqual(WIKI_JELLYFISH, "https://en.wikipedia.org/wiki/Jellyfish")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        eel = study_deck_for("eel")
        self.assertEqual(eel["source"], WIKI_EEL)
        self.assertEqual(eel["talk_about"], list(TALK_ABOUT_EEL))
        self.assertEqual(eel["push_further"], list(PUSH_FURTHER_EEL))
        self.assertEqual(shipped_levels_for("eel"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("eel", "hard"))
        self.assertIsNotNone(study_deck_for("eel", "zoologist"))
        cuttle = study_deck_for("cuttlefish")
        self.assertEqual(cuttle["source"], WIKI_CUTTLEFISH)
        self.assertEqual(cuttle["talk_about"], list(TALK_ABOUT_CUTTLEFISH))
        self.assertEqual(cuttle["push_further"], list(PUSH_FURTHER_CUTTLEFISH))
        self.assertEqual(shipped_levels_for("cuttlefish"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("cuttlefish", "hard"))
        self.assertIsNotNone(study_deck_for("cuttlefish", "zoologist"))
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
        html = outing_talk_html({"id": "jellyfish", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH:
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
        self.assertNotIn("Park Ranger", visible)
        self.assertNotIn("Zoologist", visible)
        self.assertIn('class="study-level-badge"', html)
        self.assertNotIn('class="study-level-picker"', html)
        self.assertNotIn('data-study-pick="easy"', html)
        self.assertNotIn('data-study-pick="hard"', html)
        self.assertNotIn('data-study-pick="zoologist"', html)
        self.assertNotIn("study-level-picker-bottom", html)
        self.assertEqual(html.count('role="group"'), 0)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        self.assertNotIn(" · Easy ·", html)
        self.assertNotIn(" · Hard ·", html)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, html)
        self.assertIn(
            "No backbone — they’re cnidarians, the same big group as corals and anemones",
            html,
        )
        self.assertIn(
            "No — it’s a floating colony of many tiny animals working as one, not a true jellyfish",
            html,
        )
        self.assertIn("Facts from Wikipedia, Jellyfish.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "octopus", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("Are jellyfish a kind of fish", html)
        octo = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", octo)
        self.assertNotIn("card-study-pack", octo)
        self.assertNotIn("Are jellyfish a kind of fish", octo)

    def test_published_jellyfish_card_matches_easy_deck(self):
        html = JELLYFISH.read_text(encoding="utf-8")
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
        self.assertIn("/field-pack/photos/jellyfish.jpg", main)
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=jellyfish",
            main,
        )
        self.assertIn('class="card-try-next no-print"', main)
        self.assertNotIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=10", html)
        self.assertIn("study-cards-data.js?v=6", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "jellyfish"', html)
        self.assertNotIn('"id": "eel"', html)
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
        self.assertNotIn("Park Ranger", visible)
        self.assertNotIn("Zoologist", visible)
        self.assertIn('class="study-level-badge"', main)
        self.assertNotIn('class="study-level-picker"', main)
        self.assertNotIn('data-study-pick="easy"', main)
        self.assertNotIn('data-study-pick="hard"', main)
        self.assertNotIn('data-study-pick="zoologist"', main)
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
        for prompt in TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("jellyfish"),
            ["eel", "cuttlefish", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("jellyfish")
        sheet = study_print_html(
            deck,
            name="Jellyfish",
            emoji="🎐",
            photo="/field-pack/photos/jellyfish.jpg?v=img2",
            photo_pos="50% 35%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/jellyfish.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_JELLYFISH, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "No backbone — they’re cnidarians, the same big group as corals and anemones",
            sheet,
        )
        self.assertIn(
            "No — it’s a floating colony of many tiny animals working as one, not a true jellyfish",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH:
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

    def test_artifacts_include_jellyfish_easy_only(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("jellyfish", payload)
        self.assertNotIn("octopus", payload)
        self.assertIn("eel", payload)
        self.assertIn("cuttlefish", payload)
        self.assertIn("crab", payload)
        self.assertIn("clownfish", payload)
        fish = payload["jellyfish"]
        self.assertEqual(fish["id"], "jellyfish")
        self.assertEqual(set(fish["levels"]), {"easy"})
        self.assertNotIn("hard", fish["levels"])
        self.assertNotIn("zoologist", fish["levels"])
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
        self.assertIn('"jellyfish"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(set(payload["eel"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["cuttlefish"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["crab"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["clownfish"]["levels"]), {"easy", "hard", "zoologist"})
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
        jelly_html = JELLYFISH.read_text(encoding="utf-8")
        visible = _text(_main(jelly_html))
        self.assertIn("Junior Ranger", visible)
        self.assertNotIn("Park Ranger", visible)
        self.assertNotIn("Zoologist", visible)
        eel_html = EEL.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(eel_html)))
        self.assertIn("Park Ranger", _text(_main(eel_html)))
        self.assertIn("Zoologist", _text(_main(eel_html)))
        cuttle_html = CUTTLEFISH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(cuttle_html)))
        self.assertIn("Park Ranger", _text(_main(cuttle_html)))
        self.assertIn("Zoologist", _text(_main(cuttle_html)))
        crab_html = CRAB.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(crab_html)))
        self.assertIn("Park Ranger", _text(_main(crab_html)))
        self.assertIn("Zoologist", _text(_main(crab_html)))
        clown_html = CLOWNFISH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(clown_html)))
        self.assertIn("Park Ranger", _text(_main(clown_html)))
        self.assertIn("Zoologist", _text(_main(clown_html)))


if __name__ == "__main__":
    unittest.main()
