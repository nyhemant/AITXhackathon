"""Shared Field Trip Kit print geometry — one letter page with visible slack.

Chrome 100% preview hairline-paginates when sheet height + @page margins + leftover
in-flow chrome exceed the printable page. These constants are the universal contract
(mission.css, styles.css, print-kit.js). Do not invent per-venue print CSS.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
MISSION_CSS = (FP / "css" / "mission.css").read_text(encoding="utf-8")
STYLES_CSS = (FP / "css" / "styles.css").read_text(encoding="utf-8")
PRINT_KIT_JS = (FP / "js" / "print-kit.js").read_text(encoding="utf-8")
MISSION_UI_JS = (FP / "js" / "mission" / "mission-ui.js").read_text(encoding="utf-8")

# Letter portrait 11in; landscape short side 8.5in.
LETTER_PORTRAIT_IN = 11.0
LETTER_LANDSCAPE_SHORT_IN = 8.5
PAGE_MARGIN_IN = 0.4
SHEET_HEIGHT_IN = 9.4
LANDSCAPE_SHEET_HEIGHT_IN = 7.3
MIN_SLACK_IN = 0.6


def _first_print_block(css: str) -> str:
    m = re.search(r"@media print\s*\{", css)
    if not m:
        return ""
    start = m.start()
    return css[start : start + 9000]


class PrintCssSlackTest(unittest.TestCase):
    def test_portrait_sheet_plus_margins_leave_visible_slack(self):
        used = SHEET_HEIGHT_IN + 2 * PAGE_MARGIN_IN
        slack = LETTER_PORTRAIT_IN - used
        self.assertGreaterEqual(slack, MIN_SLACK_IN)
        self.assertAlmostEqual(used, 10.2)
        self.assertAlmostEqual(slack, 0.8)

    def test_landscape_cutout_sheet_plus_margins_leave_slack(self):
        used = LANDSCAPE_SHEET_HEIGHT_IN + 2 * PAGE_MARGIN_IN
        slack = LETTER_LANDSCAPE_SHORT_IN - used
        self.assertGreaterEqual(slack, 0.4)
        self.assertAlmostEqual(used, 8.1)

    def test_shared_files_use_the_same_page_margin(self):
        page = re.compile(r"@page\s*\{[^}]*margin:\s*0\.4in", re.S)
        self.assertRegex(MISSION_CSS, page)
        self.assertRegex(STYLES_CSS, page)
        self.assertIn("@page { size: letter landscape; margin: 0.4in; }", PRINT_KIT_JS)
        self.assertNotIn("margin: 0.35in", MISSION_CSS)
        self.assertNotIn("margin: 0.35in", STYLES_CSS)
        self.assertNotIn("margin: 0.35in", PRINT_KIT_JS)

    def test_shared_files_use_the_same_sheet_height(self):
        for css in (MISSION_CSS, STYLES_CSS):
            self.assertIn("height: 9.4in", css)
            self.assertIn("max-height: 9.4in", css)
            self.assertNotIn("height: 9.7in", css)
            self.assertNotIn("max-height: 9.7in", css)
        self.assertIn("FP_PRINT_SHEET_HEIGHT", MISSION_CSS)
        self.assertIn("FP_PRINT_SHEET_HEIGHT", STYLES_CSS)

    def test_mission_print_hides_body_siblings_and_keeps_sheet_in_flow(self):
        self.assertIn("body.printing-mission > *:not(.mission-overlay)", MISSION_CSS)
        self.assertRegex(
            MISSION_CSS,
            r"body\.printing-mission \.mission-sheet\s*\{[^}]*position:\s*relative",
        )
        self.assertNotRegex(
            MISSION_CSS,
            r"body\.printing-mission \.mission-sheet\s*\{[^}]*position:\s*absolute",
        )
        self.assertIn("body.printing-mission .mission-overlay.no-print", MISSION_CSS)
        self.assertNotIn("body.printing-mission * {\n    visibility: hidden;", MISSION_CSS)

    def test_mission_map_can_flex_shrink(self):
        self.assertIn("body.printing-mission .ms-map-print-frame", MISSION_CSS)
        frame = MISSION_CSS.split("body.printing-mission .ms-map-print-frame", 1)[1][:400]
        self.assertIn("min-height: 1.15in", frame)
        self.assertNotIn("min-height: 1.6in", MISSION_CSS)
        # Floor is small enough that 1.15in + 8.25in of text still fits 9.4in.

    def test_treasure_and_qa_hide_non_sheet_chrome(self):
        block = _first_print_block(STYLES_CSS)
        self.assertIn("body.printing-treasure > *:not(#treasure-sheet)", block)
        self.assertIn("body.printing-qa > *:not(#print-sheet)", block)
        self.assertIn("body.printing-safari > *:not(#print-sheet)", block)
        self.assertIn(".no-print:not(.mission-overlay)", STYLES_CSS)
        self.assertIn("height: 7.3in", STYLES_CSS)
        self.assertNotIn("height: 7.55in", STYLES_CSS)

    def test_print_js_sets_mode_classes_on_html_and_body(self):
        self.assertIn('classList.toggle("printing-qa"', PRINT_KIT_JS)
        self.assertIn("document.documentElement.classList.toggle", PRINT_KIT_JS)
        self.assertIn("document.documentElement.classList.add(\"printing-mission\")", MISSION_UI_JS)
        self.assertIn("waitForPrintImages", MISSION_UI_JS)
        self.assertIn("waitForPrintImages,", PRINT_KIT_JS)


if __name__ == "__main__":
    unittest.main()
