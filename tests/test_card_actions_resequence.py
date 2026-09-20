"""Card action controls: Watch | Photos on row 1; Print alone on row 2."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    CARD_SEO_CSS_VER,
    card_pictures_link_html,
    pictures_link_label,
)

FP = REPO / "static" / "field-pack"


def _main(html: str) -> str:
    return html.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]


def _actions(main: str) -> str:
    return main.split('class="card-page-actions"', 1)[1]


class CardActionsResequenceTests(unittest.TestCase):
    def test_css_ver_bumped(self):
        self.assertEqual(CARD_SEO_CSS_VER, "38")
        css = (FP / "css" / "seo-venue.css").read_text(encoding="utf-8")
        self.assertIn(".card-page-actions-primary", css)
        self.assertIn(".card-page-actions-print", css)

    def test_pictures_helper_for_action_row(self):
        html = card_pictures_link_html(
            {
                "links": {
                    "pictures": "https://kids.nationalgeographic.com/animals/mammals/facts/lion"
                }
            }
        )
        self.assertIn("card-page-photos", html)
        self.assertIn("More photos at National Geographic Kids", html)
        self.assertEqual(card_pictures_link_html({"links": {}}), "")

    def test_cam_and_photos_row_order(self):
        main = _main((FP / "cards" / "whale-shark" / "index.html").read_text(encoding="utf-8"))
        actions = _actions(main)
        primary = actions.split("card-page-actions-primary", 1)[1].split(
            "card-page-actions-print", 1
        )[0]
        print_row = actions.split("card-page-actions-print", 1)[1]
        self.assertIn("Watch live at Georgia Aquarium", primary)
        self.assertLess(primary.find("card-watch-live"), primary.find("card-page-photos"))
        self.assertIn("print-this-card", print_row)
        self.assertIn("US Letter or A4", print_row)
        self.assertNotIn("card-watch-live", print_row)
        self.assertNotIn("card-page-photos", print_row)

    def test_photos_only_row(self):
        main = _main((FP / "cards" / "freshwater-fish" / "index.html").read_text(encoding="utf-8"))
        actions = _actions(main)
        primary = actions.split("card-page-actions-primary", 1)[1].split(
            "card-page-actions-print", 1
        )[0]
        self.assertIn("card-page-photos", primary)
        self.assertNotIn("card-watch-live", actions)

    def test_neither_print_row(self):
        main = _main((FP / "cards" / "cuyahoga-towpath" / "index.html").read_text(encoding="utf-8"))
        actions = _actions(main)
        self.assertIn("print-this-card", actions)
        self.assertNotIn("card-watch-live", actions)
        self.assertNotIn("card-page-photos", actions)

    def test_explicit_photos_label_preserved(self):
        main = _main((FP / "cards" / "crab" / "index.html").read_text(encoding="utf-8"))
        actions = _actions(main)
        self.assertIn("Christmas Island photos", actions)
        self.assertIn("card-watch-live", actions)


if __name__ == "__main__":
    unittest.main()
