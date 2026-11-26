"""2026-11-26 Gemini SEO consult (ChiefGrok plan item 1): Aquarium of the Pacific title says Los Angeles."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "static/field-pack/aquarium-of-the-pacific/index.html"
TITLE = "Los Angeles Aquarium Scavenger Hunt: Aquarium of the Pacific"


class AopLosAngelesTitle(unittest.TestCase):
    def setUp(self):
        self.html = PAGE.read_text(encoding="utf-8")

    def test_title_og_and_twitter_say_los_angeles(self):
        self.assertIn(f"<title>{TITLE}</title>", self.html)
        self.assertIn(f'<meta property="og:title" content="{TITLE}" />', self.html)
        self.assertIn(f'<meta name="twitter:title" content="{TITLE}" />', self.html)
        self.assertNotIn("LA-Area", self.html)
        self.assertLessEqual(len(TITLE), 60)

    def test_meta_description_names_los_angeles_and_long_beach(self):
        desc = re.search(r'<meta name="description" content="([^"]*)"', self.html).group(1)
        self.assertTrue(desc.startswith("Aquarium scavenger hunt in Los Angeles:"), desc)
        self.assertIn("(Long Beach)", desc)
        self.assertLessEqual(len(desc), 155)

    def test_generator_matches_page(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        import generate_bdo_seo as g
        self.assertEqual(g.SEO_TITLE_LABELS["aquarium-of-the-pacific"], TITLE)
        self.assertIn(g.SEO_META_DESCRIPTIONS["aquarium-of-the-pacific"], self.html)


if __name__ == "__main__":
    unittest.main()
