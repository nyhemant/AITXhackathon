"""African lion card talk is a lion-specific conversation, not the generic worksheet."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CARD_TALK_OVERRIDE,
    CARD_TALK_QA_OVERRIDE,
    OUTING_TALK_ANIMAL,
    outing_missions_for,
    outing_talk_html,
)

FP = REPO / "static" / "field-pack"
LION = FP / "cards" / "african-lion" / "index.html"
GENERIC_QS = (
    "What do they eat?",
    "Where is home?",
    "What is their superpower?",
    "Baby or grown-up?",
    "I want to teach about…",
)
LION_QS = (
    "Does this lion have a big fluffy mane?",
    "What do you notice?",
    "Lions often live in a group called a pride. How many do you see?",
    "Meat eater or plant eater?",
    "Did we see a lion — and what would you tell a grown-up?",
)


class LionCardTalkTests(unittest.TestCase):
    def test_override_is_lion_only(self):
        self.assertEqual(tuple(CARD_TALK_OVERRIDE), ("african-lion",))
        lion = outing_missions_for({"id": "african-lion", "packTemplate": "animals"})
        elephant = outing_missions_for({"id": "african-elephant", "packTemplate": "animals"})
        self.assertEqual(lion, CARD_TALK_OVERRIDE["african-lion"])
        self.assertEqual(elephant, OUTING_TALK_ANIMAL)
        self.assertNotEqual(lion, elephant)

    def test_generator_html_is_not_generic_worksheet(self):
        html = outing_talk_html(
            {
                "id": "african-lion",
                "packTemplate": "animals",
                "key": {"food": ["Meat"], "home": ["Grassland"]},
            }
        )
        for q in GENERIC_QS:
            self.assertNotIn(q, html)
        for q in LION_QS:
            self.assertIn(q, html)
        self.assertIn("Meat eater", html)
        self.assertIn('aria-pressed="true"', html)
        self.assertIn("More talk", html)
        self.assertIn(CARD_TALK_QA_OVERRIDE["african-lion"]["question"], html)
        self.assertIn("data-count=\"3\"", html)

    def test_other_animal_html_stays_generic(self):
        html = outing_talk_html({"id": "koala", "packTemplate": "animals"})
        self.assertIn("What do they eat?", html)
        self.assertNotIn("Does this lion have a big fluffy mane?", html)
        self.assertNotIn("More talk", html)

    def test_published_lion_card_matches_override(self):
        html = LION.read_text(encoding="utf-8")
        for q in GENERIC_QS:
            self.assertNotIn(q, html)
        for q in LION_QS:
            self.assertIn(q, html)
        self.assertIn("Watch Live", html)
        self.assertIn("/field-pack/virtual-zoo/?from=card#habitat=african-lion", html)
        self.assertIn(CARD_TALK_QA_OVERRIDE["african-lion"]["question"], html)
        self.assertIn("Look close — mane, whiskers, a tuft on the tail.", html)
        self.assertNotIn("mighty roar", html)


if __name__ == "__main__":
    unittest.main()
