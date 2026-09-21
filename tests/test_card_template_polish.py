"""Card template polish: question count · tier, Back to place, Photos label."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    catalog_more_links_html,
    pictures_link_label,
    start_here_place_names,
    write_card_pages,
    load_all_catalog_cards,
)
from study_cards import study_deck_for, study_talk_html  # noqa: E402

FP = REPO / "static" / "field-pack"
SEO = REPO / "scripts" / "generate_bdo_seo.py"
STUDY_JS = FP / "js" / "study-card.js"


class CardTemplatePolishTests(unittest.TestCase):
    def test_score_states_question_count_with_tier(self):
        lion = study_talk_html(study_deck_for("african-lion"))
        self.assertIn("10 questions · Junior Ranger", lion)
        whale = study_talk_html(study_deck_for("whale-shark"))
        self.assertIn("5 questions · Junior Ranger", whale)
        hard = study_talk_html(study_deck_for("whale-shark", "hard"))
        self.assertIn("5 questions · Park Ranger", hard)

    def test_study_js_pending_score_includes_tier(self):
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("function pendingScoreLabel", js)
        self.assertIn("· ${tier}", js)

    def test_pictures_label_names_source(self):
        label = pictures_link_label(
            "https://kids.nationalgeographic.com/animals/mammals/facts/lion"
        )
        self.assertEqual(label, "More photos at National Geographic Kids")
        self.assertEqual(
            pictures_link_label("https://example.com/x", "Christmas Island photos"),
            "Christmas Island photos",
        )
        html = catalog_more_links_html(
            {
                "links": {
                    "pictures": "https://kids.nationalgeographic.com/animals/fish/facts/whale-sharks"
                }
            },
            shared=True,
            allow_cam=False,
        )
        self.assertIn("More photos at National Geographic Kids", html)
        self.assertNotIn(">Photos</a>", html)

    def test_generator_emits_back_to_place_chrome(self):
        gen = SEO.read_text(encoding="utf-8")
        self.assertIn("card-back-to-place", gen)
        self.assertIn("KIT_NAMES", gen)
        self.assertIn("Back to ", gen)
        self.assertIn("start_here_place_names", gen)
        names = start_here_place_names()
        self.assertEqual(names.get("dallas-zoo"), "Dallas Zoo")

    def test_card_pages_have_back_hook_and_named_photos(self):
        lion = (FP / "cards" / "african-lion" / "index.html").read_text(encoding="utf-8")
        self.assertIn("card-back-to-place", lion)
        self.assertIn("KIT_NAMES", lion)
        self.assertIn("More photos at National Geographic Kids", lion)
        self.assertNotIn(">Photos</a>", lion)
        self.assertIn("10 questions · Junior Ranger", lion)
        whale = (FP / "cards" / "whale-shark" / "index.html").read_text(encoding="utf-8")
        self.assertIn("5 questions · Junior Ranger", whale)
        self.assertIn("More photos at National Geographic Kids", whale)


if __name__ == "__main__":
    unittest.main()
