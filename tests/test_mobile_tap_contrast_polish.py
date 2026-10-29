"""2026-10-29: tap targets, primary-button contrast and crawlable hidden anchor."""
import re
import unittest
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "static"


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


class MobilePolishTests(unittest.TestCase):
    def test_primary_button_contrast_at_least_4_5(self):
        css = (STATIC / "field-pack/css/styles.css").read_text(encoding="utf-8")
        last = re.findall(r"\n\.btn-primary \{\s*background: (#[0-9a-f]{6});", css)[-1]
        self.assertGreaterEqual(1.05 / (lum(last) + 0.05), 4.5, last)

    def test_tap_target_rules_present(self):
        css = (STATIC / "field-pack/css/styles.css").read_text(encoding="utf-8")
        for sel in (".seo-crumbs a", ".seo-map-ext-link", ".seo-home-card h3 a", ".vz-static-film"):
            self.assertIn(sel, css)
        about = (STATIC / "about/about.css").read_text(encoding="utf-8")
        self.assertIn("min-height: 44px", about)
        self.assertIn("about.css?v=12", (STATIC / "about/index.html").read_text(encoding="utf-8"))

    def test_hidden_learn_more_anchor_has_href(self):
        n = 0
        for p in (STATIC / "field-pack/cards").glob("*/index.html"):
            for a in re.findall(r'<a [^>]*card-learn-more[^>]*>', p.read_text(encoding="utf-8")):
                self.assertIn(" href=", a, p)
                n += 1
        self.assertGreater(n, 0)

    def test_arya_wording_kept(self):
        for page in ("start/index.html", "about/index.html"):
            s = (STATIC / page).read_text(encoding="utf-8")
            self.assertTrue("Arya’s Wildlife Project" in s or "Arya's Wildlife Project" in s, page)


if __name__ == "__main__":
    unittest.main()
