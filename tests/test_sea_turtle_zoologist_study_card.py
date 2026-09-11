"""Sea-turtle Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_JELLYFISH,
    PUSH_FURTHER_KELP_FOREST,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_MANTA_RAY_ZOOLOGIST,
    PUSH_FURTHER_OCTOPUS_ZOOLOGIST,
    PUSH_FURTHER_SEA_TURTLE_ZOOLOGIST,
    STUDY_SLOTS,
    TALK_ABOUT_JELLYFISH,
    TALK_ABOUT_KELP_FOREST,
    TALK_ABOUT_LION,
    TALK_ABOUT_MANTA_RAY_ZOOLOGIST,
    TALK_ABOUT_OCTOPUS_ZOOLOGIST,
    TALK_ABOUT_SEA_TURTLE_ZOOLOGIST,
    WIKI_JELLYFISH,
    WIKI_KELP_FOREST,
    WIKI_LION,
    WIKI_MANTA_RAY,
    WIKI_OCTOPUS,
    WIKI_SEA_TURTLE,
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
SEA_TURTLE = FP / "cards" / "sea-turtle" / "index.html"
SEAHORSE = FP / "cards" / "whale-shark" / "index.html"
OCTOPUS = FP / "cards" / "octopus" / "index.html"
MANTA = FP / "cards" / "manta-ray" / "index.html"
KELP = FP / "cards" / "kelp-forest" / "index.html"
JELLYFISH = FP / "cards" / "jellyfish" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Where does crown Chelonioidea sit among living turtles, if we keep that tree soft?",
    "How can a leatherback keep a warmer core in cold water, if we keep that heat gap soft?",
    "How should we read IUCN letters for living sea turtles, if we keep those snapshots by kind?",
    "Why can one sea turtle species look recovered in one place and still struggle in another, if we keep those stocks soft?",
    "How does CITES treat sea turtles in international trade, if we keep that rule soft?",
    "How can a turtle excluder device (TED) help in a shrimp net, if we keep that cut soft?",
    "Why can floating plastic put sea turtles in danger, if we keep that trash story soft?",
    "How can beach lights send hatchlings inland, if we keep that glow story soft?",
    "What can a nesting beach’s magnetic signature tell us, if we keep that imprint story soft?",
    "How do green turtles help seagrass meadows, if we keep that gardening story soft?",
)

ZOOLOGIST_IDS = (
    "phylogeny-soft",
    "gigantothermy-soft",
    "status-by-kind-soft",
    "rmu-soft",
    "cites-i-soft",
    "ted-soft",
    "plastic-soft",
    "light-pollution-soft",
    "geomagnetic-imprint-soft",
    "seagrass-gardeners-soft",
)

HARD_STEMS = (
    "Where do true sea turtles sit in the family tree, if we keep that map soft?",
    "How can nest sand temperature steer hatchling sex, if we keep those thresholds soft?",
    "Where do many female sea turtles return to nest, if we keep that homing story soft?",
    "How can hatchlings and adults stay on long ocean routes, if we keep that sense soft?",
    "How do sea turtles dump extra salt, if we keep those glands soft?",
    "What makes a leatherback different from hard-shell sea turtles, if we keep that size soft?",
    "How do adult diets split among sea turtle kinds, if we keep those menus soft?",
    "How do some ridleys nest differently from most other sea turtles?",
    "Where do many young sea turtles spend their early years, if we keep that time soft?",
    "What human pressures can send hatchlings the wrong way or put wild turtles at risk, if we keep that care story soft?",
)

EASY_STEMS = (
    "How many kinds of sea turtle live in the world’s oceans, if we keep the list soft?",
    "What do a sea turtle’s flippers do?",
    "How is a sea turtle’s shell built for the ocean?",
    "How does a mom sea turtle make a nest?",
    "What are sea turtle eggs like — and does mom stay to guard them?",
    "What do baby sea turtles do after they hatch?",
    "How do sea turtles breathe, even though they live in the ocean?",
    "Where do sea turtles live?",
    "How far can many sea turtles travel, if we keep the miles soft?",
    "Can a sea turtle pull its head and flippers into its shell like many pet turtles?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "8 °C",
    "8°C",
    "14 °F",
    "97 percent",
    "97%",
    "Least Concern",
    "Critically Endangered",
    " kg",
    " cm",
    " mph",
    "km/h",
)
REDO_THEMES = (
    "About seven kinds — flatback, green, hawksbill, leatherback, loggerhead, Kemp’s ridley, and olive ridley (soft)",
    "Front flippers paddle; back flippers help steer — and dig the nest hole",
    "It is streamlined for swimming — flatter and smoother than many land turtles",
    "She hauls onto sand (usually at night), digs with hind flippers, buries eggs, then returns to the sea",
    "Soft-shelled eggs in a sand nest; mom does not stay to guard them",
    "They dig out together and race toward the brightest horizon — normally the ocean",
    "They have lungs and must surface to breathe — they can stay under a long time when resting (soft)",
    "In warm and temperate seas worldwide — none live only on land",
    "Many travel far between feeding waters and nesting beaches (soft)",
    "No — unlike many pet turtles, they cannot pull their head and flippers in. The body is built for swimming, not hiding inside",
    "Superfamily Chelonioidea — most kinds in hard-shelled Cheloniidae; the leatherback sits alone in Dermochelyidae with a leathery shell (soft)",
    "Warmer nests tend to make more females; cooler nests tend to make more males (exact degrees stay soft)",
    "Many return to nest near the beach where they hatched (philopatry); how tightly they match that beach varies by kind (soft)",
    "They use Earth’s magnetic field like a map plus a compass so they can hold a heading and know roughly where they are (soft)",
    "Special glands near the eyes make salty tears — reptile kidneys cannot make urine saltier than seawater (soft)",
    "It is the largest living sea turtle, with a soft leathery shell (no hard scutes), and it mainly eats jellyfish (soft)",
    "Green turtles shift toward seagrass and algae as adults; hawksbills lean on sponges; loggerheads and ridleys stay more mixed hunters (soft)",
    "Some ridleys nest in huge synchronized beach arrivals (arribadas); most other kinds nest more alone (soft)",
    "They spend early years offshore — often in floating seaweed mats — then move closer to shore as they grow (soft)",
    "Beach lights can send hatchlings the wrong way; fishing nets and trash also put pressure on wild turtles (soft)",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class SeaTurtleZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("sea-turtle", study_card_ids())
        self.assertEqual(shipped_levels_for("sea-turtle"), ("easy", "hard", "zoologist"))
        self.assertIsNotNone(study_deck_for("sea-turtle", "hard"))
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("sea-turtle", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_SEA_TURTLE)
        self.assertEqual(deck["source_note"], "Facts from Wikipedia, Sea turtle.")
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_SEA_TURTLE_ZOOLOGIST))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_SEA_TURTLE_ZOOLOGIST))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("sea-turtle", "zoologist")
        easy = study_deck_for("sea-turtle", "easy")
        hard = study_deck_for("sea-turtle", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("sea-turtle", "zoologist")
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
        self.assertIn("americhelydia", correct_choice_text(questions[0]).lower())
        self.assertIn("chelonioidea", correct_choice_text(questions[0]).lower())
        self.assertIn("protostegidae", correct_choice_text(questions[0]).lower())
        self.assertIn("archelon", correct_choice_text(questions[0]).lower())
        self.assertIn("soft", correct_choice_text(questions[0]).lower())
        self.assertIn("gigantothermy", correct_choice_text(questions[1]).lower())
        self.assertIn("leatherback", correct_choice_text(questions[1]).lower())
        self.assertIn("circulation", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("cr", correct_choice_text(questions[2]).lower())
        self.assertIn("vu", correct_choice_text(questions[2]).lower())
        self.assertIn("lc", correct_choice_text(questions[2]).lower())
        self.assertIn("dd", correct_choice_text(questions[2]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[2]).lower())
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("regional management", correct_choice_text(questions[3]).lower())
        self.assertIn("stock", correct_choice_text(questions[3]).lower())
        self.assertIn("recover", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("appendix i", correct_choice_text(questions[4]).lower())
        self.assertIn("trade", correct_choice_text(questions[4]).lower())
        self.assertIn("restricted", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("escape", correct_choice_text(questions[5]).lower())
        self.assertIn("bycatch", correct_choice_text(questions[5]).lower())
        self.assertIn("percent", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("jellyfish", correct_choice_text(questions[6]).lower())
        self.assertIn("blockage", correct_choice_text(questions[6]).lower())
        self.assertIn("entangle", correct_choice_text(questions[6]).lower())
        self.assertIn("soft", correct_choice_text(questions[6]).lower())
        self.assertIn("brightest horizon", correct_choice_text(questions[7]).lower())
        self.assertIn("inland", correct_choice_text(questions[7]).lower())
        self.assertIn("soft", correct_choice_text(questions[7]).lower())
        self.assertIn("isoline", correct_choice_text(questions[8]).lower())
        self.assertIn("genetic", correct_choice_text(questions[8]).lower())
        self.assertIn("distance", correct_choice_text(questions[8]).lower())
        self.assertIn("soft", correct_choice_text(questions[8]).lower())
        self.assertIn("seagrass", correct_choice_text(questions[9]).lower())
        self.assertIn("graz", correct_choice_text(questions[9]).lower())
        self.assertIn("meadow", correct_choice_text(questions[9]).lower())
        self.assertIn("soft", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Americhelydia",
            "Protostegidae",
            "Archelon",
            "gigantothermy",
            "Chelonioidea",
            "isoline",
            "Leviathanochelys",
            "fibropapillomatosis",
            "CITES",
            "RMU",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_JELLYFISH + PUSH_FURTHER_JELLYFISH
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_SEA_TURTLE_ZOOLOGIST + PUSH_FURTHER_SEA_TURTLE_ZOOLOGIST:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_SEA_TURTLE_ZOOLOGIST).lower()
        push = " ".join(PUSH_FURTHER_SEA_TURTLE_ZOOLOGIST).lower()
        self.assertIn("cr", talk)
        self.assertIn("lc", talk)
        self.assertIn("plastic", talk)
        self.assertIn("leatherback", talk)
        self.assertIn("fossil", push)
        self.assertIn("tumor", push)
        self.assertIn("female", push)
        self.assertIn("barnacle", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("sea-turtle", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "sea-turtle", "packTemplate": "animals"})
        self.assertIn(">Quiz</h2>", html)
        self.assertIn("Learn first", html)
        self.assertIn("Junior Ranger", html)
        self.assertIn("Park Ranger", html)
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="easy"', html)
        self.assertIn('data-study-pick="hard"', html)
        for stem in ZOOLOGIST_STEMS:
            self.assertNotIn(stem, html)
        for stem in EASY_STEMS:
            self.assertIn(stem, html)
        visible = _text(html)
        for badge in PLAIN_LEVEL_LABELS + AGE_BADGES:
            self.assertNotIn(badge, visible)

    def test_zoologist_print_is_answer_light_duplex(self):
        deck = study_deck_for("sea-turtle", "zoologist")
        sheet = study_print_html(
            deck,
            name="Sea turtle",
            emoji="🐢",
            photo="/field-pack/photos/sea-turtle.jpg?v=img2",
            photo_pos="50% 32%",
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
        for prompt in TALK_ABOUT_SEA_TURTLE_ZOOLOGIST + PUSH_FURTHER_SEA_TURTLE_ZOOLOGIST:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_SEA_TURTLE, sheet)
        self.assertIn("Facts from Wikipedia, Sea turtle.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("sea-turtle", "zoologist"))
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
        self.assertEqual(shipped_levels_for("octopus"), ("easy", "hard", "zoologist"))
        octo_zoo = study_deck_for("octopus", "zoologist")
        self.assertEqual(octo_zoo["source"], WIKI_OCTOPUS)
        octo_html = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("Zoologist", octo_html)
        self.assertEqual(octo_zoo["talk_about"], list(TALK_ABOUT_OCTOPUS_ZOOLOGIST))
        self.assertEqual(octo_zoo["push_further"], list(PUSH_FURTHER_OCTOPUS_ZOOLOGIST))
        self.assertEqual(shipped_levels_for("manta-ray"), ("easy", "hard", "zoologist"))
        manta_zoo = study_deck_for("manta-ray", "zoologist")
        self.assertEqual(manta_zoo["source"], WIKI_MANTA_RAY)
        manta_html = MANTA.read_text(encoding="utf-8")
        self.assertIn("Zoologist", manta_html)
        self.assertEqual(manta_zoo["talk_about"], list(TALK_ABOUT_MANTA_RAY_ZOOLOGIST))
        self.assertEqual(manta_zoo["push_further"], list(PUSH_FURTHER_MANTA_RAY_ZOOLOGIST))
        self.assertEqual(shipped_levels_for("jellyfish"), ("easy", "hard", "zoologist"))
        jelly_zoo = study_deck_for("jellyfish", "zoologist")
        self.assertEqual(jelly_zoo["source"], WIKI_JELLYFISH)
        jelly_html = JELLYFISH.read_text(encoding="utf-8")
        self.assertIn("Zoologist", jelly_html)
        self.assertEqual(jelly_zoo["talk_about"], list(TALK_ABOUT_JELLYFISH))
        self.assertEqual(jelly_zoo["push_further"], list(PUSH_FURTHER_JELLYFISH))
        self.assertEqual(shipped_levels_for("kelp-forest"), ("easy", "hard", "zoologist"))
        kelp_zoo = study_deck_for("kelp-forest", "zoologist")
        self.assertEqual(kelp_zoo["source"], WIKI_KELP_FOREST)
        kelp_html = KELP.read_text(encoding="utf-8")
        self.assertIn("Zoologist", kelp_html)
        self.assertEqual(kelp_zoo["talk_about"], list(TALK_ABOUT_KELP_FOREST))
        self.assertEqual(kelp_zoo["push_further"], list(PUSH_FURTHER_KELP_FOREST))
        horse = SEAHORSE.read_text(encoding="utf-8")
        self.assertIn("card-study-pack", horse)
        self.assertNotIn("What do they eat?", horse)
        self.assertNotIn("phylogeny-soft", horse)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["sea-turtle"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        self.assertIn("hard", payload["sea-turtle"]["levels"])
        self.assertEqual(payload["sea-turtle"]["levels"]["hard"]["teach"], [])
        self.assertEqual(payload["sea-turtle"]["levels"]["easy"]["teach"], [
            "Ocean reptiles with paddle flippers (not land-turtle feet)",
            "About seven kinds live in the world’s oceans (not the polar ice)",
            "Moms dig nests on sandy beaches and bury soft eggs",
            "Babies hatch and crawl to the sea (often at night)",
            "They breathe air — they surface, even though they live in the ocean",
        ])
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("phylogeny-soft", data_js)
        self.assertIn("gigantothermy-soft", data_js)
        self.assertIn("rmu-soft", data_js)
        self.assertIn("seagrass-gardeners-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = SEA_TURTLE.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
        self.assertIn('data-study-pick="hard"', html)
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
