"""Polish 2026-11-20: the post-print offer is a short strip that does not cover the page controls."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "static" / "field-pack"
sys.path.insert(0, str(ROOT / "scripts"))


class CompactPrintOffer(unittest.TestCase):
    def test_heading_is_true_whether_or_not_the_print_goes_through(self):
        import generate_bdo_seo as gen

        self.assertNotIn("printed", gen.PLACE_PRINT_HEADING.lower())
        self.assertTrue(gen.PLACE_PRINT_HEADING.startswith("Printing your hunt?"))
        for page in sorted(FP.glob("*/index.html")):
            html = page.read_text(encoding="utf-8")
            if 'data-placement="place_print"' in html:
                self.assertNotIn("Hunt printed", html, page.parent.name)

    def test_card_copy_rules_and_sample_link(self):
        import generate_bdo_seo as gen

        box = gen.place_print_newsletter_html()
        text = re.sub(r"<[^>]+>", " ", box)
        self.assertIn("See a sample email", text)
        self.assertNotRegex(text, r"(?i)\bfree\b")
        self.assertNotRegex(text, r"(?i)\b(we|our|us)\b")
        self.assertNotRegex(text, r"\bKit\b")
        self.assertIn('aria-label="No thanks"', box)

    def test_css_keeps_the_strip_short(self):
        css = (FP / "css" / "newsletter-v1.css").read_text(encoding="utf-8")
        rule = css.split(".kz-nl--print {", 1)[1].split("}", 1)[0]
        self.assertIn("max-height: 40vh", rule)
        self.assertNotIn("100vh", rule)

    def test_thanks_puts_the_strip_away(self):
        js = (FP / "js" / "newsletter-v1.js").read_text(encoding="utf-8")
        self.assertIn('form.getAttribute("data-reveal") === "print"', js)
        self.assertIn("form.hidden = true", js)


if __name__ == "__main__":
    unittest.main()
