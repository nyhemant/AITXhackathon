"""2026-11-16: "An 8-stop" / "An 11-stop" in the shared printable block intro."""
import re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import scav_test_2026_11 as sc  # noqa: E402
class ScavArticle20261116(unittest.TestCase):
    def test_intro_article(self):
        v = {"name": "X", "city": "Y"}
        for n, art in [(5, "A"), (7, "A"), (8, "An"), (10, "A"), (11, "An"), (12, "A"), (18, "An")]:
            self.assertTrue(sc.intro_text(v, n).startswith(f"{art} {n}-stop hunt"), n)
    def test_no_page_says_a_8_or_a_11(self):
        for p in (ROOT / "static/field-pack").glob("*/index.html"):
            self.assertIsNone(re.search(r"\bA (8|11|18)-stop", p.read_text()), p.parent.name)
if __name__ == "__main__":
    unittest.main()
