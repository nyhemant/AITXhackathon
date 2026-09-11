"""Stingray Easy study-card: Junior Ranger teach + 10 MCQs (no Park Ranger yet)."""

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
    PUSH_FURTHER_LION,
    PUSH_FURTHER_MANTA_RAY,
    PUSH_FURTHER_SEAHORSE,
    PUSH_FURTHER_STINGRAY,
    STUDY_SLOTS,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY,
    TALK_ABOUT_SEAHORSE,
    TALK_ABOUT_STINGRAY,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_SEAHORSE,
    WIKI_STINGRAY,
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
STINGRAY = FP / "cards" / "stingray" / "index.html"
WHALE_SHARK = FP / "cards" / "whale-shark" / "index.html"
SEAHORSE = FP / "cards" / "seahorse" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
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
    "Flattened ocean fish with a skeleton of cartilage (related to sharks — soft)",
    "Eyes on top; mouth and gills on the underside",
    "Many hide under sand on the seafloor",
    "The tail can carry a venomous stinger used for defense",
    "Usually shy — they sting when threatened or stepped on, not when chasing people",
)

STEMS = (
    "What is a stingray’s skeleton mostly made of?",
    "What shape helps many stingrays hug the seafloor?",
    "Where are a stingray’s eyes and mouth?",
    "How do many bottom-living stingrays hide?",
    "What is the famous “sting” on many stingrays?",
    "What do many stingrays eat on the seafloor?",
    "How can a buried stingray keep breathing without gulping sandy water through its mouth?",
    "How do stingray babies usually arrive?",
    "About how many kinds of stingray are there, if we keep the count soft?",
    "Do stingrays usually chase and hunt people?",
)

QIDS = (
    "cartilage-soft",
    "flat-disc-soft",
    "eyes-up-mouth-down-soft",
    "sand-hide-soft",
    "stinger-soft",
    "crush-food-soft",
    "spiracles-soft",
    "live-young-soft",
    "many-kinds-soft",
    "not-hunters-myth",
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
    "Myliobatiformes",
    "ampullae",
    "undulatory",
    "oscillatory",
    "histotroph",
    "uterine milk",
    "Mobula",
    "devil-ray",
    "kg",
    "cm",
    "mph",
    "km/h",
)
PAGE_BRITTLE = BRITTLE
RESERVED = (
    "IUCN",
    "CITES",
    "Myliobatiformes",
    "ampullae",
    "undulatory",
    "oscillatory",
    "histotroph",
    "uterine milk",
    "Mobula",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class StingrayEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_only(self):
        self.assertIn("stingray", study_card_ids())
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
        self.assertEqual(shipped_levels_for("stingray"), ("easy",))
        self.assertIsNone(study_deck_for("stingray", "hard"))
        self.assertIsNone(study_deck_for("stingray", "zoologist"))
        self.assertIsNone(study_deck_for("whale-shark"))
        deck = study_deck_for("stingray")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "stingray")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_STINGRAY)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Stingray.",
        )
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_STINGRAY))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_STINGRAY))
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
        self.assertIn("cartilage", blob.lower())
        self.assertIn("shark", blob.lower())
        self.assertIn("pectoral", blob.lower())
        self.assertIn("disc", blob.lower())
        self.assertIn("underside", blob.lower())
        self.assertIn("sand", blob.lower())
        self.assertIn("stinger", blob.lower())
        self.assertIn("venom", blob.lower())
        self.assertIn("mollusks", blob.lower())
        self.assertIn("spiracles", blob.lower())
        self.assertIn("ovoviviparous", blob.lower())
        self.assertIn("two hundred", blob.lower())
        self.assertIn("stepped", blob.lower())
        self.assertEqual(WIKI_STINGRAY, "https://en.wikipedia.org/wiki/Stingray")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        horse = study_deck_for("seahorse")
        self.assertEqual(horse["source"], WIKI_SEAHORSE)
        self.assertEqual(horse["talk_about"], list(TALK_ABOUT_SEAHORSE))
        self.assertEqual(horse["push_further"], list(PUSH_FURTHER_SEAHORSE))
        self.assertEqual(shipped_levels_for("seahorse"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("seahorse", "hard"))
        self.assertIsNotNone(study_deck_for("seahorse", "zoologist"))
        manta = study_deck_for("manta-ray")
        self.assertEqual(manta["source"], WIKI_MANTA_RAY)
        self.assertEqual(manta["talk_about"], list(TALK_ABOUT_MANTA_RAY))
        self.assertEqual(manta["push_further"], list(PUSH_FURTHER_MANTA_RAY))
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("manta-ray", "hard"))
        self.assertIsNotNone(study_deck_for("manta-ray", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "stingray", "packTemplate": "animals"})
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
        for prompt in TALK_ABOUT_STINGRAY + PUSH_FURTHER_STINGRAY:
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
        self.assertNotIn("data-study-pick", html)
        self.assertNotIn("study-level-picker-bottom", html)
        self.assertEqual(html.count('role="group"'), 0)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)
        self.assertNotIn(" · Easy ·", html)
        self.assertNotIn(" · Hard ·", html)
        for phrase in PAGE_BRITTLE:
            self.assertNotIn(phrase, html)
        self.assertIn(
            "Cartilage — tough and flexible, like a shark’s skeleton (soft)",
            html,
        )
        self.assertIn(
            "No — they are not usually aggressive; stings happen mainly when a ray is stepped on or threatened",
            html,
        )
        self.assertIn("Facts from Wikipedia, Stingray.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "whale-shark", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("What is a stingray", html)
        star = WHALE_SHARK.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", star)
        self.assertNotIn("card-study-pack", star)
        self.assertNotIn("What is a stingray", star)

    def test_published_stingray_card_matches_easy_deck(self):
        html = STINGRAY.read_text(encoding="utf-8")
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
        self.assertIn("/field-pack/photos/stingray.jpg", main)
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=stingray",
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
        self.assertIn('"id": "stingray"', html)
        self.assertNotIn('"id": "seahorse"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=42", html)
        self.assertIn('<details class="study-teach">', html)
        self.assertNotIn('<details class="study-teach" open', html)
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
        self.assertNotIn("data-study-pick", main)
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
        for prompt in TALK_ABOUT_STINGRAY + PUSH_FURTHER_STINGRAY:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("stingray"),
            ["manta-ray", "seahorse", "african-lion"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("stingray")
        sheet = study_print_html(
            deck,
            name="Stingray",
            emoji="🐟",
            photo="/field-pack/photos/stingray.jpg?v=img2",
            photo_pos="50% 40%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/stingray.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_STINGRAY, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn(
            "Cartilage — tough and flexible, like a shark’s skeleton (soft)",
            sheet,
        )
        self.assertIn(
            "No — they are not usually aggressive; stings happen mainly when a ray is stepped on or threatened",
            sheet,
        )
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_STINGRAY + PUSH_FURTHER_STINGRAY:
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

    def test_artifacts_include_stingray_easy_only(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("stingray", payload)
        self.assertNotIn("whale-shark", payload)
        self.assertIn("seahorse", payload)
        self.assertIn("manta-ray", payload)
        ray = payload["stingray"]
        self.assertEqual(ray["id"], "stingray")
        self.assertEqual(set(ray["levels"]), {"easy"})
        self.assertNotIn("hard", ray["levels"])
        self.assertNotIn("zoologist", ray["levels"])
        easy = ray["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"stingray"', data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertEqual(set(payload["seahorse"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["manta-ray"]["levels"]), {"easy", "hard", "zoologist"})
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
        ray_html = STINGRAY.read_text(encoding="utf-8")
        visible = _text(_main(ray_html))
        self.assertIn("Junior Ranger", visible)
        self.assertNotIn("Park Ranger", visible)
        self.assertNotIn("Zoologist", visible)
        horse_html = SEAHORSE.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(horse_html)))
        self.assertIn("Park Ranger", _text(_main(horse_html)))
        self.assertIn("Zoologist", _text(_main(horse_html)))
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(manta_html)))
        self.assertIn("Park Ranger", _text(_main(manta_html)))
        self.assertIn("Zoologist", _text(_main(manta_html)))


if __name__ == "__main__":
    unittest.main()
