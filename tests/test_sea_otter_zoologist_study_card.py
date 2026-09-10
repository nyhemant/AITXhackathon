"""Sea otter Zoologist study-card: no teach, 10 Wikipedia-backed MCQs."""

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
    PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER,
    PUSH_FURTHER_LION,
    PUSH_FURTHER_SEA_OTTER,
    STUDY_SLOTS,
    TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER,
    TALK_ABOUT_LION,
    TALK_ABOUT_SEA_OTTER,
    WIKI_ASIAN_SMALL_CLAWED_OTTER,
    WIKI_LION,
    WIKI_SEA_OTTER,
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
OTTER = FP / "cards" / "sea-otter" / "index.html"
OCTOPUS = FP / "cards" / "stingray" / "index.html"
ASIAN = FP / "cards" / "asian-small-clawed-otter" / "index.html"
LION = FP / "cards" / "african-lion" / "index.html"
STUDY_JSON = FP / "data" / "study-cards.json"
STUDY_DATA_JS = FP / "js" / "study-cards-data.js"
STUDY_JS = FP / "js" / "study-card.js"
PRINT_KIT = FP / "js" / "print-kit.js"

ZOOLOGIST_STEMS = (
    "Which living otter is the only species in the genus Enhydra?",
    "How does a sea otter fit among living otters (Lutrinae) in the weasel family?",
    "How many living sea otter subspecies do scientists usually name?",
    "How are adult sea otter cheek teeth built?",
    "How “old” is the sea otter’s marine life compared with whales and seals?",
    "What can happen after sea otters mate, before the pup starts growing?",
    "How many pups does a sea otter mom usually raise at once?",
    "What classic cascade can sea otters start in a nearshore community?",
    "Does the global Endangered letter tell the same story on every sea otter coast?",
    "Where can sea otters give birth, compared with seals and sea lions?",
)

ZOOLOGIST_IDS = (
    "enhydra-only-soft",
    "lutrinae-marine-soft",
    "three-subspecies-soft",
    "bunodont-teeth-soft",
    "newcomer-to-sea-soft",
    "delayed-implantation-soft",
    "usually-one-pup-soft",
    "trophic-cascade-soft",
    "status-nuance-soft",
    "birth-in-water-soft",
)

HARD_STEMS = (
    "Unlike most marine mammals, how do sea otters stay warm?",
    "Why does grooming matter so much for a sea otter?",
    "How can sea otters help protect kelp forests?",
    "What do loose skin folds under a sea otter’s forearms do?",
    "Why do sea otters eat so much each day?",
    "How does a sea otter fit in the weasel family?",
    "What happened to sea otters during the historic fur trade?",
    "How should we read the IUCN letter for sea otters?",
    "What do international CITES trade rules say for sea otters?",
    "How do sea otters move when they come onto land?",
)

EASY_STEMS = (
    "Where do sea otters live in the wild?",
    "How do sea otters stay warm in cold ocean water?",
    "How do sea otters often rest and eat?",
    "How do sea otters open hard shells?",
    "What do sea otters love to eat?",
    "Why do sea otters wrap themselves in kelp?",
    "What is a group of resting sea otters called?",
    "How do sea otter moms carry their pups?",
    "Why do healthy kelp forests and clean coasts matter?",
    "Is a sea otter the same animal as a river otter or an Asian small-clawed otter?",
)

PLAIN_LEVEL_LABELS = ("Easy", "Hard")
AGE_BADGES = ("Ages", "Age 4", "age badge", "ages 4", "4–6", "4-6")
BRITTLE = (
    "150,000",
    "25%",
    "38%",
    "1741",
    "1911",
    "Exxon Valdez",
    "2 million",
    "5 million",
    "4 to 12",
    "four to twelve",
    "kg",
    "cm",
    "mph",
    "km/h",
)
REDO_THEMES = (
    "Nearshore North Pacific coasts — they can live almost entirely in the sea",
    "Super-thick fur — the densest of any animal",
    "use their belly like a picnic table",
    "They use rocks to bash open shells",
    "Sea urchins, clams, crabs, and other ocean invertebrates",
    "So they don’t drift while they rest",
    "A raft — they may hold paws so they stay together",
    "On their chests while floating",
    "Healthy kelp forests and clean coasts help sea otters and their food",
    "ocean specialists, different from river otters and Asian small-clawed otters",
    "They have little blubber — dense fur plus trapped air does the insulating",
    "Dirty or oiled fur loses its warm air layer",
    "help protect kelp forests from “urchin barrens”",
    "They stash rocks and prey while the otter dives",
    "A high metabolism means they eat a large share of their body weight each day",
    "Heaviest living mustelid (weasel family)",
    "Hunting nearly wiped them out; later bans and reintroductions helped a rebound",
    "IUCN lists them Endangered — the letter is a snapshot; recovery is real but uneven",
    "Species mostly Appendix II; the southern subspecies is Appendix I",
    "flipper-like hind feet make them awkward ashore",
)


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


class SeaOtterZoologistStudyCardTests(unittest.TestCase):
    def test_zoologist_deck_is_answer_light(self):
        self.assertIn("sea-otter", study_card_ids())
        self.assertEqual(
            shipped_levels_for("sea-otter"),
            ("easy", "hard", "zoologist"),
        )
        self.assertEqual(level_display_name("zoologist"), "Zoologist")
        deck = study_deck_for("sea-otter", "zoologist")
        self.assertIsNotNone(deck)
        self.assertEqual(deck["level"], "zoologist")
        self.assertEqual(deck["level_label"], "Zoologist")
        self.assertEqual(deck["source"], WIKI_SEA_OTTER)
        self.assertEqual(
            deck["source_note"],
            "Facts from Wikipedia, Sea otter.",
        )
        self.assertEqual(deck["teach"], [])
        self.assertEqual(deck["talk_about"], list(TALK_ABOUT_SEA_OTTER))
        self.assertEqual(deck["push_further"], list(PUSH_FURTHER_SEA_OTTER))
        self.assertEqual(len(deck["questions"]), STUDY_SLOTS)
        self.assertEqual(validate_deck(deck), [])
        letters = [q["correct"] for q in deck["questions"]]
        self.assertEqual(letters, [target_letter_for_slot(i) for i in range(1, 11)])
        self.assertEqual(letters.count("A"), 4)
        self.assertEqual(letters.count("B"), 3)
        self.assertEqual(letters.count("C"), 3)

    def test_validate_deck_allows_empty_teach_for_zoologist(self):
        zoo = study_deck_for("sea-otter", "zoologist")
        easy = study_deck_for("sea-otter", "easy")
        hard = study_deck_for("sea-otter", "hard")
        self.assertEqual(validate_deck(easy), [])
        self.assertEqual(validate_deck(hard), [])
        self.assertEqual(validate_deck(zoo), [])
        broken_zoo = dict(zoo)
        broken_zoo["teach"] = ["A leftover teach line."]
        self.assertIn("zoologist deck must not include a teach strip", validate_deck(broken_zoo))

    def test_zoologist_slots_and_copy_are_locked(self):
        deck = study_deck_for("sea-otter", "zoologist")
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
        self.assertIn("Enhydra lutris", correct_choice_text(questions[0]))
        self.assertIn("Aonyx", correct_choice_text(questions[0]))
        self.assertIn("Lutra", correct_choice_text(questions[0]))
        self.assertIn("Lutrinae", correct_choice_text(questions[1]))
        self.assertIn("Mustelidae", correct_choice_text(questions[1]))
        self.assertIn("marine", correct_choice_text(questions[1]).lower())
        self.assertIn("soft", correct_choice_text(questions[1]).lower())
        self.assertIn("lutris", correct_choice_text(questions[2]))
        self.assertIn("kenyoni", correct_choice_text(questions[2]))
        self.assertIn("nereis", correct_choice_text(questions[2]))
        self.assertIn("soft", correct_choice_text(questions[2]).lower())
        self.assertIn("bunodont", correct_choice_text(questions[3]).lower())
        self.assertIn("crush", correct_choice_text(questions[3]).lower())
        self.assertIn("soft", correct_choice_text(questions[3]).lower())
        self.assertIn("recent", correct_choice_text(questions[4]).lower())
        self.assertIn("whale", correct_choice_text(questions[4]).lower())
        self.assertIn("soft", correct_choice_text(questions[4]).lower())
        self.assertIn("embryo", correct_choice_text(questions[5]).lower())
        self.assertIn("pause", correct_choice_text(questions[5]).lower())
        self.assertIn("soft", correct_choice_text(questions[5]).lower())
        self.assertIn("single pup", correct_choice_text(questions[6]).lower())
        self.assertIn("twin", correct_choice_text(questions[6]).lower())
        self.assertIn("rare", correct_choice_text(questions[6]).lower())
        self.assertIn("urchin", correct_choice_text(questions[7]).lower())
        self.assertIn("kelp", correct_choice_text(questions[7]).lower())
        self.assertIn("cascade", correct_choice_text(questions[7]).lower())
        self.assertIn("snapshot", correct_choice_text(questions[8]).lower())
        self.assertIn("aleutian", correct_choice_text(questions[8]).lower())
        self.assertIn("california", correct_choice_text(questions[8]).lower())
        self.assertIn("water", correct_choice_text(questions[9]).lower())
        self.assertIn("pinniped", correct_choice_text(questions[9]).lower())
        self.assertIn("haul out", correct_choice_text(questions[9]).lower())
        blob = " ".join(q["why"] for q in questions) + " ".join(
            " ".join(q["choices"]) for q in questions
        )
        for phrase in BRITTLE:
            self.assertNotIn(phrase, blob)
        self.assertIn("Wikipedia", deck["source_note"])

    def test_explore_more_stays_kid_short(self):
        dense = (
            "Lutrinae",
            "Mustelidae",
            "pinniped",
            "trophic",
            "kenyoni",
            "nereis",
            "implantation",
        )
        peer = TALK_ABOUT_LION + PUSH_FURTHER_LION + TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER + PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER
        peer_max = max(len(line) for line in peer)
        for line in TALK_ABOUT_SEA_OTTER + PUSH_FURTHER_SEA_OTTER:
            for phrase in dense:
                self.assertNotIn(phrase, line)
            self.assertLessEqual(len(line), peer_max + 20, line)
        talk = " ".join(TALK_ABOUT_SEA_OTTER).lower()
        push = " ".join(PUSH_FURTHER_SEA_OTTER).lower()
        self.assertIn("enhydra", talk)
        self.assertIn("aonyx", talk)
        self.assertIn("subspecies", talk)
        self.assertIn("cascade", talk)
        self.assertIn("bunodont", push)
        self.assertIn("crush", push)
        self.assertIn("newcomer", push)
        self.assertIn("letter", push)
        self.assertIn("region", push)

    def test_zoologist_does_not_redo_easy_or_hard_stems(self):
        zoo = study_deck_for("sea-otter", "zoologist")
        zoo_stems = [q["stem"] for q in zoo["questions"]]
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, zoo_stems)
        zoo_blob = " ".join(
            q["stem"] + " " + " ".join(q["choices"]) + " " + q["why"] for q in zoo["questions"]
        ).lower()
        for phrase in REDO_THEMES:
            self.assertNotIn(phrase.lower(), zoo_blob)

    def test_default_screen_html_keeps_easy_and_adds_zoologist_picker(self):
        html = outing_talk_html({"id": "sea-otter", "packTemplate": "animals"})
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
        deck = study_deck_for("sea-otter", "zoologist")
        sheet = study_print_html(
            deck,
            name="Sea otter",
            emoji="🦦",
            photo="/field-pack/photos/sea-otter.jpg?v=img2",
            photo_pos="50% 38%",
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
        for prompt in TALK_ABOUT_SEA_OTTER + PUSH_FURTHER_SEA_OTTER:
            self.assertIn(prompt, back)
        self.assertIn("Flip for answers", sheet)
        self.assertIn(WIKI_SEA_OTTER, sheet)
        self.assertIn("Facts from Wikipedia, Sea otter.", sheet)
        for stem in ZOOLOGIST_STEMS:
            self.assertIn(stem, sheet)
        for stem in EASY_STEMS + HARD_STEMS:
            self.assertNotIn(stem, sheet)

    def test_zoologist_screen_hides_empty_teach_but_keeps_deepen(self):
        html = study_talk_html(study_deck_for("sea-otter", "zoologist"))
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
        self.assertEqual(
            shipped_levels_for("asian-small-clawed-otter"),
            ("easy", "hard", "zoologist"),
        )
        asian_zoo = study_deck_for("asian-small-clawed-otter", "zoologist")
        self.assertEqual(asian_zoo["source"], WIKI_ASIAN_SMALL_CLAWED_OTTER)
        asian_html = ASIAN.read_text(encoding="utf-8")
        self.assertIn("Zoologist", asian_html)
        self.assertEqual(
            asian_zoo["talk_about"],
            list(TALK_ABOUT_ASIAN_SMALL_CLAWED_OTTER),
        )
        self.assertEqual(
            asian_zoo["push_further"],
            list(PUSH_FURTHER_ASIAN_SMALL_CLAWED_OTTER),
        )
        sea = OCTOPUS.read_text(encoding="utf-8")
        self.assertIn("What do they eat?", sea)
        self.assertNotIn("card-study-pack", sea)
        self.assertNotIn("enhydra-only-soft", sea)

    def test_published_artifacts_and_plumbing(self):
        payload = json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        zoo = payload["sea-otter"]["levels"]["zoologist"]
        self.assertEqual(zoo["teach"], [])
        self.assertEqual(len(zoo["questions"]), STUDY_SLOTS)
        self.assertEqual([q["id"] for q in zoo["questions"]], list(ZOOLOGIST_IDS))
        data_js = STUDY_DATA_JS.read_text(encoding="utf-8")
        self.assertIn('"zoologist":{"teach":[]', data_js)
        self.assertIn("enhydra-only-soft", data_js)
        self.assertIn("lutrinae-marine-soft", data_js)
        self.assertIn("birth-in-water-soft", data_js)
        self.assertIn("status-nuance-soft", data_js)
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("zoologist", js)
        self.assertIn("data-study-pick", js)
        print_js = PRINT_KIT.read_text(encoding="utf-8")
        self.assertIn('fromDom === "zoologist"', print_js)
        html = OTTER.read_text(encoding="utf-8")
        self.assertIn("Zoologist", html)
        self.assertIn('data-study-pick="zoologist"', html)
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
