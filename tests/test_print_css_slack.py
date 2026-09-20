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
        self.assertIn("body.printing-study > *:not(#print-sheet)", block)
        self.assertIn("body.printing-safari > *:not(#print-sheet)", block)
        self.assertIn(".no-print:not(.mission-overlay)", STYLES_CSS)
        self.assertIn("height: 7.3in", STYLES_CSS)
        self.assertNotIn("height: 7.55in", STYLES_CSS)

    def test_study_print_answers_are_italic_dark_grey(self):
        block = STYLES_CSS.split(".ps-study-answers {", 1)[1]
        answers = block.split(".ps-study-deepen {", 1)[0]
        self.assertIn("font-style: italic", answers)
        self.assertIn("color: #3a3f48", answers)
        self.assertIn("color: #2a2e36", answers)
        self.assertNotIn("color: #0a4545", answers)

    def test_print_js_sets_mode_classes_on_html_and_body(self):
        self.assertIn('classList.toggle("printing-qa"', PRINT_KIT_JS)
        self.assertIn('classList.toggle("printing-study"', PRINT_KIT_JS)
        self.assertIn("document.documentElement.classList.toggle", PRINT_KIT_JS)
        self.assertIn("document.documentElement.classList.add(\"printing-mission\")", MISSION_UI_JS)
        self.assertIn("waitForPrintImages", MISSION_UI_JS)
        self.assertIn("waitForPrintImages,", PRINT_KIT_JS)

    # ---- Unified print-pack assertions (brand + tokens) ----

    def test_all_print_banners_use_kidzookit_brand(self):
        """Every JS-generated print banner should have <h2>KIDZOOKIT</h2> (not page H1)."""
        self.assertIn('<h2>KIDZOOKIT</h2>', PRINT_KIT_JS)
        for label in ("buildQaCardHtml", "buildStudyCardHtml",
                       "buildTreasureHtml", "buildCutPageHtml",
                       "buildAnswerPageHtml"):
            block_start = PRINT_KIT_JS.find(f"function {label}")
            self.assertNotEqual(block_start, -1, f"{label} not found")
            next_fn = PRINT_KIT_JS.find("\n  function ", block_start + 1)
            if next_fn == -1:
                next_fn = len(PRINT_KIT_JS)
            block = PRINT_KIT_JS[block_start:next_fn]
            self.assertIn("<h2>KIDZOOKIT</h2>", block,
                          f"{label} should have KIDZOOKIT in banner h2")

    def test_shared_print_tokens_declared(self):
        """styles.css should declare FP_PRINT_TOKENS custom properties."""
        self.assertIn("FP_PRINT_TOKENS", STYLES_CSS)
        for token in ("--fp-print-font", "--fp-print-ink",
                       "--fp-print-footer-size", "--fp-print-footer-color",
                       "--fp-print-brand-bg"):
            self.assertIn(token, STYLES_CSS,
                          f"Token {token} should be declared in styles.css")

    def test_print_tokens_consumed_by_mission_css(self):
        """mission.css print rules should reference shared tokens."""
        self.assertIn("--fp-print-font", MISSION_CSS)
        self.assertIn("--fp-print-footer-size", MISSION_CSS)

    def test_no_hardcoded_6pt_or_8pt_print_footer(self):
        """Footer sizes should use the shared 7pt token, not stale 6pt/8pt."""
        block = _first_print_block(STYLES_CSS)
        for selector in (".ps-footer", ".th-footer", ".hs-footer"):
            after = block.split(selector, 1)
            if len(after) < 2:
                continue
            rule = after[1][:200]
            self.assertNotIn("font-size: 6pt", rule,
                             f"{selector} should not use hardcoded 6pt")
            self.assertNotIn("font-size: 8pt", rule,
                             f"{selector} should not use hardcoded 8pt")

    def test_duplex_guidance_is_consistent(self):
        """Study card and cutout answers should use the same two-sided wording."""
        self.assertIn("Print two-sided (flip on long edge)", PRINT_KIT_JS)
        self.assertNotIn("Duplex:", PRINT_KIT_JS)

    def test_th_safety_not_duplicated_in_seo_venue(self):
        """th-safety should only be defined in styles.css, not duplicated."""
        seo_css = (FP / "css" / "seo-venue.css").read_text(encoding="utf-8")
        self.assertNotIn(".th-safety {", seo_css)

    def test_footer_includes_kidzookit_com(self):
        """All print footer strings should mention kidzookit.com."""
        self.assertIn("kidzookit.com", PRINT_KIT_JS)


if __name__ == "__main__":
    unittest.main()
