"""Cheetah Easy study-card: Junior Ranger teach + 10 MCQs (Park Ranger is a sibling level)."""

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
    PUSH_FURTHER_CHEETAH,
    PUSH_FURTHER_ELEPHANT,
    PUSH_FURTHER_FLAMINGO,
    PUSH_FURTHER_GIRAFFE,
    PUSH_FURTHER_GORILLA,
    PUSH_FURTHER_HIPPO,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_PENGUIN,
    PUSH_FURTHER_TIGER,
    PUSH_FURTHER_TORTOISE,
    PUSH_FURTHER_ZEBRA,
    STUDY_SLOTS,
    TALK_ABOUT_CHEETAH,
    TALK_ABOUT_ELEPHANT,
    TALK_ABOUT_FLAMINGO,
    TALK_ABOUT_GIRAFFE,
    TALK_ABOUT_GORILLA,
    TALK_ABOUT_HIPPO,
    TALK_ABOUT_LION,
    TALK_ABOUT_PENGUIN,
    TALK_ABOUT_TIGER,
    TALK_ABOUT_TORTOISE,
    TALK_ABOUT_ZEBRA,
    WIKI_AFRICAN_ELEPHANT,
    WIKI_AFRICAN_PENGUIN,
    WIKI_AMERICAN_FLAMINGO,
    WIKI_CHEETAH,
    WIKI_GALAPAGOS_TORTOISE,
    WIKI_GIRAFFE,
    WIKI_HIPPOPOTAMUS,
    WIKI_LION,
    WIKI_PLAINS_ZEBRA,
    WIKI_SUMATRAN_TIGER,
    WIKI_WESTERN_LOWLAND_GORILLA,
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
CHEETAH = FP / "cards" / "cheetah" / "index.html"
GORILLA = FP / "cards" / "western-lowland-gorilla" / "index.html"
TIGER = FP / "cards" / "sumatran-tiger" / "index.html"
HIPPO = FP / "cards" / "nile-hippo" / "index.html"
ZEBRA = FP / "cards" / "zebra" / "index.html"
TORTOISE = FP / "cards" / "galapagos-tortoise" / "index.html"
FLAMINGO = FP / "cards" / "caribbean-flamingo" / "index.html"
PENGUIN = FP / "cards" / "african-penguin" / "index.html"
ELEPHANT = FP / "cards" / "african-elephant" / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
GIANT_PANDA = FP / "cards" / "giant-panda" / "index.html"
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
    "They are the fastest animal on land — built for short sprints.",
    "They have solid black spots, not the rosettes a leopard has.",
    "Black tear marks run from each eye toward the nose.",
    "They chirp and purr — they do not roar like a lion.",
    "They live mostly on African grassland / savannah.",
)

STEMS = (
    "What is a cheetah famous for?",
    "What kind of marks does a cheetah’s coat have?",
    "What are the black lines on a cheetah’s face?",
    "What sounds is a cheetah known for?",
    "Where do most wild cheetahs live?",
    "How is a cheetah’s body built for a chase?",
    "How does a cheetah’s long tail help in a chase?",
    "What do wild cheetahs mostly hunt?",
    "What special fur do cheetah cubs have on their backs?",
    "Do cheetahs run fast for a long time, like a marathon?",
)

QIDS = (
    "fastest",
    "spots",
    "tear-marks",
    "no-roar",
    "savannah",
    "sprint-body",
    "steering-tail",
    "meat-hunter",
    "cub-cape",
    "marathon-myth",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "IUCN",
    "Vulnerable",
    "mph",
    "km/h",
    "58",
    "65",
    "71",
    "93",
    "104",
    "114",
    "Acinonyx",
    "king cheetah",
    "King cheetah",
    "Asiatic",
    "bottleneck",
    "coalition",
    "retract",
)
RESERVED = (
    "genetic",
    "taxonomy",
    "Iran",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


class CheetahEasyStudyCardTests(unittest.TestCase):
    def test_deck_is_junior_ranger_with_park_ranger_and_zoologist(self):
        self.assertIn("cheetah", study_card_ids())
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
            ),
        )
        self.assertEqual(shipped_levels_for("cheetah"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("cheetah", "hard"))
        self.assertIsNotNone(study_deck_for("cheetah", "zoologist"))
        deck = study_deck_for("cheetah")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["id"], "cheetah")
        self.assertEqual(deck["level"], "easy")
        self.assertEqual(deck["level_label"], "Junior Ranger")
        self.assertEqual(level_display_name("easy"), "Junior Ranger")
        self.assertEqual(deck["source"], WIKI_CHEETAH)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Cheetah.")
        self.assertEqual(validate_deck(deck), [])
        self.assertEqual(len(deck["teach"]), 5)
        self.assertEqual(deck["teach"], list(TEACH))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual([q["stem"] for q in deck["questions"]], list(STEMS))
        self.assertEqual([q["id"] for q in deck["questions"]], list(QIDS))
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_CHEETAH))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_CHEETAH))
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
        blob = " ".join(deck["teach"] + [q["stem"] + q["why"] for q in deck["questions"]])
        for phrase in BRITTLE + RESERVED:
            self.assertNotIn(phrase, blob)
        self.assertIn("fastest", blob.lower())
        self.assertIn("solid black spots", blob.lower())
        self.assertIn("rosette", blob.lower())
        self.assertIn("tear", blob.lower())
        self.assertIn("chirp", blob.lower())
        self.assertIn("purr", blob.lower())
        self.assertIn("savannah", blob.lower())
        self.assertIn("flexible spine", blob.lower())
        self.assertIn("rudder", blob.lower())
        self.assertIn("gazelle", blob.lower())
        self.assertIn("cape", blob.lower())
        self.assertIn("short", blob.lower())
        self.assertEqual(WIKI_CHEETAH, "https://en.wikipedia.org/wiki/Cheetah")

    def test_other_study_decks_untouched(self):
        lion = study_deck_for("african-lion")
        self.assertEqual(lion["source"], WIKI_LION)
        self.assertEqual(lion["level_label"], "Junior Ranger")
        self.assertEqual(len(lion["questions"]), STUDY_SLOTS)
        self.assertEqual(lion["talk_about"], list(TALK_ABOUT_LION))
        self.assertEqual(lion["push_further"], list(PUSH_FURTHER_LION))
        self.assertEqual(shipped_levels_for("african-lion"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("african-lion", "hard"))
        self.assertIsNotNone(study_deck_for("african-lion", "zoologist"))
        giraffe = study_deck_for("reticulated-giraffe")
        self.assertEqual(giraffe["source"], WIKI_GIRAFFE)
        self.assertEqual(giraffe["talk_about"], list(TALK_ABOUT_GIRAFFE))
        self.assertEqual(giraffe["push_further"], list(PUSH_FURTHER_GIRAFFE))
        self.assertEqual(shipped_levels_for("reticulated-giraffe"), ("easy", "hard", "zoologist"))
        elephant = study_deck_for("african-elephant")
        self.assertEqual(elephant["source"], WIKI_AFRICAN_ELEPHANT)
        self.assertEqual(elephant["talk_about"], list(TALK_ABOUT_ELEPHANT))
        self.assertEqual(elephant["push_further"], list(PUSH_FURTHER_ELEPHANT))
        penguin = study_deck_for("african-penguin")
        self.assertEqual(penguin["source"], WIKI_AFRICAN_PENGUIN)
        self.assertEqual(penguin["talk_about"], list(TALK_ABOUT_PENGUIN))
        self.assertEqual(penguin["push_further"], list(PUSH_FURTHER_PENGUIN))
        flamingo = study_deck_for("caribbean-flamingo")
        self.assertEqual(flamingo["source"], WIKI_AMERICAN_FLAMINGO)
        self.assertEqual(flamingo["talk_about"], list(TALK_ABOUT_FLAMINGO))
        self.assertEqual(flamingo["push_further"], list(PUSH_FURTHER_FLAMINGO))
        tortoise = study_deck_for("galapagos-tortoise")
        self.assertEqual(tortoise["source"], WIKI_GALAPAGOS_TORTOISE)
        self.assertEqual(tortoise["talk_about"], list(TALK_ABOUT_TORTOISE))
        self.assertEqual(tortoise["push_further"], list(PUSH_FURTHER_TORTOISE))
        zebra = study_deck_for("zebra")
        self.assertEqual(zebra["source"], WIKI_PLAINS_ZEBRA)
        self.assertEqual(zebra["talk_about"], list(TALK_ABOUT_ZEBRA))
        self.assertEqual(zebra["push_further"], list(PUSH_FURTHER_ZEBRA))
        self.assertEqual(shipped_levels_for("zebra"), ("easy", "hard", "zoologist"))
        hippo = study_deck_for("nile-hippo")
        self.assertEqual(hippo["source"], WIKI_HIPPOPOTAMUS)
        self.assertEqual(hippo["talk_about"], list(TALK_ABOUT_HIPPO))
        self.assertEqual(hippo["push_further"], list(PUSH_FURTHER_HIPPO))
        self.assertEqual(shipped_levels_for("nile-hippo"), ("easy", "hard", "zoologist"))
        tiger = study_deck_for("sumatran-tiger")
        self.assertEqual(tiger["source"], WIKI_SUMATRAN_TIGER)
        self.assertEqual(tiger["talk_about"], list(TALK_ABOUT_TIGER))
        self.assertEqual(tiger["push_further"], list(PUSH_FURTHER_TIGER))
        self.assertEqual(shipped_levels_for("sumatran-tiger"), ("easy", "hard", "zoologist"))
        gorilla = study_deck_for("western-lowland-gorilla")
        self.assertEqual(gorilla["source"], WIKI_WESTERN_LOWLAND_GORILLA)
        self.assertEqual(gorilla["talk_about"], list(TALK_ABOUT_GORILLA))
        self.assertEqual(gorilla["push_further"], list(PUSH_FURTHER_GORILLA))
        self.assertEqual(shipped_levels_for("western-lowland-gorilla"), ("easy", "hard", "zoologist"))

    def test_generator_html_is_study_not_worksheet(self):
        html = outing_talk_html({"id": "cheetah", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("card-study-pack", html)
        self.assertIn("Learn first", html)
        self.assertIn("<details class=\"study-teach\">", html)
        self.assertNotIn("<details class=\"study-teach\" open", html)
        self.assertIn("<summary class=\"study-teach-kicker\">", html)
        self.assertIn("tap to open", html)
        self.assertIn("Talk about it", html)
        self.assertIn("Push further", html)
        self.assertIn('<details class="study-explore', html)
        self.assertIn("Explore more", html)
        self.assertNotIn('<aside class="study-deepen"', html)
        for prompt in TALK_ABOUT_CHEETAH + PUSH_FURTHER_CHEETAH:
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
        for phrase in BRITTLE:
            self.assertNotIn(phrase, html)
        self.assertIn("Being the fastest animal on land", html)
        self.assertIn("No — they sprint in short bursts, not long runs", html)
        self.assertIn("Facts from Wikipedia, Cheetah.", html)

    def test_other_animal_stays_generic_worksheet(self):
        html = outing_talk_html({"id": "giant-panda", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("card-study-pack", html)
        self.assertNotIn("What is a cheetah famous for?", html)
        panda = GIANT_PANDA.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", panda)
        self.assertNotIn("card-study-pack", panda)

    def test_published_cheetah_card_matches_easy_deck(self):
        html = CHEETAH.read_text(encoding="utf-8")
        main = _main(html)
        for phrase in GENERIC_WORKSHEET:
            self.assertNotIn(phrase, main)
        for stem in STEMS:
            self.assertIn(stem, main)
        for line in TEACH:
            self.assertIn(line, main)
        self.assertIn("Watch Live", main)
        self.assertIn("/field-pack/virtual-zoo/?from=card#habitat=cheetah", main)
        self.assertIn('class="card-hero-links no-print"', main)
        self.assertIn('class="card-try-next no-print"', main)
        self.assertIn('class="card-page-photo-link"', main)
        self.assertIn('aria-label="Watch Live: Cheetah"', main)
        self.assertIn("study-level-picker-bottom", main)
        self.assertNotIn("card-print-note", main)
        self.assertIn("study-card.js?v=9", html)
        self.assertIn("study-card.css?v=9", html)
        self.assertIn("study-cards-data.js?v=5", html)
        self.assertIn('id="study-card-data"', html)
        self.assertIn('"level_label": "Junior Ranger"', html)
        self.assertIn('"id": "cheetah"', html)
        self.assertIn('id="study-print-template"', html)
        self.assertIn("print-kit.js?v=20", html)
        self.assertIn("styles.css?v=41", html)
        self.assertIn("<details class=\"study-teach\">", main)
        self.assertNotIn("<details class=\"study-teach\" open", main)
        self.assertNotIn("<div class=\"study-teach\">", main)
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
        for phrase in BRITTLE:
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
        for prompt in TALK_ABOUT_CHEETAH + PUSH_FURTHER_CHEETAH:
            self.assertIn(prompt, back)
        self.assertEqual(
            study_try_next_ids("cheetah"),
            ["african-lion", "zebra", "reticulated-giraffe"],
        )

    def test_print_faces_are_duplex_and_clamped(self):
        deck = study_deck_for("cheetah")
        sheet = study_print_html(
            deck,
            name="Cheetah",
            emoji="🐆",
            photo="/field-pack/photos/cheetah.jpg?v=img2",
            photo_pos="50% 22%",
        )
        self.assertIn("ps-study-front", sheet)
        self.assertIn("ps-study-back", sheet)
        self.assertIn("ps-study-photo", sheet)
        self.assertIn("/field-pack/photos/cheetah.jpg", sheet)
        self.assertIn("Flip for answers", sheet)
        self.assertIn("Junior Ranger", sheet)
        self.assertNotIn(" · Easy ·", sheet)
        self.assertIn(WIKI_CHEETAH, sheet)
        for stem in STEMS:
            self.assertIn(stem, sheet)
        self.assertIn("Being the fastest animal on land", sheet)
        self.assertIn("No — they sprint in short bursts, not long runs", sheet)
        front, _, back = sheet.partition("ps-study-back")
        self.assertIn("Learn first", front)
        self.assertNotIn("Talk about it", front)
        self.assertIn("Talk about it", back)
        self.assertIn("Push further", back)
        for prompt in TALK_ABOUT_CHEETAH + PUSH_FURTHER_CHEETAH:
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
        self.assertIn("details class=\"study-teach\"", study_js)
        self.assertIn("study-deepen", study_js)
        self.assertIn("is-wrong-pick", study_js)
        self.assertIn("FPStudyLevelName", study_js + STUDY_DATA_JS.read_text(encoding="utf-8"))

    def test_artifacts_include_cheetah_easy_hard_and_zoologist(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        self.assertIn("cheetah", payload)
        self.assertIn("western-lowland-gorilla", payload)
        self.assertIn("sumatran-tiger", payload)
        self.assertIn("nile-hippo", payload)
        self.assertIn("zebra", payload)
        self.assertIn("galapagos-tortoise", payload)
        self.assertIn("caribbean-flamingo", payload)
        self.assertIn("african-penguin", payload)
        self.assertIn("african-elephant", payload)
        self.assertIn("reticulated-giraffe", payload)
        self.assertIn("african-lion", payload)
        cheetah = payload["cheetah"]
        self.assertEqual(cheetah["id"], "cheetah")
        self.assertEqual(set(cheetah["levels"]), {"easy", "hard", "zoologist"})
        easy = cheetah["levels"]["easy"]
        self.assertEqual(len(easy["teach"]), 5)
        self.assertEqual(len(easy["questions"]), STUDY_SLOTS)
        self.assertEqual(
            [q["correct"] for q in easy["questions"]],
            [target_letter_for_slot(i) for i in range(1, 11)],
        )
        for q in easy["questions"]:
            self.assertEqual(len(q["choices"]), 3)
        hard = cheetah["levels"]["hard"]
        self.assertEqual(hard["teach"], [])
        self.assertEqual(len(hard["questions"]), STUDY_SLOTS)
        zoo = cheetah["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn("cheetah", data_js)
        self.assertIn('"easy":"Junior Ranger"', data_js)
        self.assertIn('"hard":"Park Ranger"', data_js)
        self.assertEqual(set(payload["african-lion"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["reticulated-giraffe"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["african-elephant"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["african-penguin"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["caribbean-flamingo"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["galapagos-tortoise"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["zebra"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["nile-hippo"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["sumatran-tiger"]["levels"]), {"easy", "hard", "zoologist"})
        self.assertEqual(set(payload["western-lowland-gorilla"]["levels"]), {"easy", "hard", "zoologist"})

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
        lion_html = LION.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(lion_html)))
        giraffe_html = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(giraffe_html)))
        elephant_html = ELEPHANT.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(elephant_html)))
        penguin_html = PENGUIN.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(penguin_html)))
        flamingo_html = FLAMINGO.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(flamingo_html)))
        self.assertIn("Zoologist", _text(_main(flamingo_html)))
        tortoise_html = TORTOISE.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(tortoise_html)))
        self.assertIn("Zoologist", _text(_main(tortoise_html)))
        zebra_html = ZEBRA.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(zebra_html)))
        self.assertIn("Zoologist", _text(_main(zebra_html)))
        hippo_html = HIPPO.read_text(encoding="utf-8")
        self.assertIn("Park Ranger", _text(_main(hippo_html)))
        self.assertIn("Zoologist", _text(_main(hippo_html)))
        tiger_html = TIGER.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(tiger_html)))
        self.assertIn("Park Ranger", _text(_main(tiger_html)))
        self.assertIn("Zoologist", _text(_main(tiger_html)))
        gorilla_html = GORILLA.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(gorilla_html)))
        self.assertIn("Park Ranger", _text(_main(gorilla_html)))
        self.assertIn("Zoologist", _text(_main(gorilla_html)))
        cheetah_html = CHEETAH.read_text(encoding="utf-8")
        self.assertIn("Junior Ranger", _text(_main(cheetah_html)))
        self.assertIn("Park Ranger", _text(_main(cheetah_html)))
        self.assertIn("Zoologist", _text(_main(cheetah_html)))


if __name__ == "__main__":
    unittest.main()
