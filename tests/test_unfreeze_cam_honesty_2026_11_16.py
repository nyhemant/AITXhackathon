"""2026-11-16 unfreeze (C): no cam claim on a test/comparison page without a "Live from" cam row."""
import re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from scav_test_2026_11 import COMPARISON_SLUGS, TEST_SLUGS  # noqa: E402
FP = ROOT / "static/field-pack"
LIVE = '<span class="seo-watch-source">Live'
class UnfreezeCamHonesty20261116(unittest.TestCase):
    def test_no_cam_claims_without_cam_row(self):
        for slug in sorted(TEST_SLUGS | COMPARISON_SLUGS):
            t = (FP / slug / "index.html").read_text()
            if LIVE in t:
                continue
            with self.subTest(slug=slug):
                self.assertNotIn("live cams", t)
                self.assertNotIn("(cards, photos, cams)", t)
    def test_generator_rule_covers_unfrozen_pages(self):
        import generate_bdo_seo as gen
        ld = '"description": "X: animal cards, talk prompts, photos, and live cams at home."'
        self.assertNotIn("live cams", gen.apply_cam_honesty("banff", ld))
        self.assertIn("live cams", gen.apply_cam_honesty("st-louis-zoo", ld))  # not changed since the lift
if __name__ == "__main__":
    unittest.main()
