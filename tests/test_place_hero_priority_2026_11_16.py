"""Place hero photo (mobile LCP) has fetchpriority=high on non-test pages (2026-11-16)."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scav_test_2026_11 import COMPARISON_SLUGS, TEST_SLUGS  # noqa: E402

FIG = re.compile(r'<figure class="seo-place-photo">.*?</figure>', re.S)


class HeroPriority(unittest.TestCase):
    def test_hero_photo_priority(self):
        n = 0
        for p in sorted((ROOT / "static" / "field-pack").glob("*/index.html")):
            figs = FIG.findall(p.read_text(encoding="utf-8"))
            if not figs:
                continue
            with self.subTest(page=p.parent.name):
                self.assertEqual(len(figs), 1)
                if p.parent.name in TEST_SLUGS | COMPARISON_SLUGS:
                    self.assertNotIn("fetchpriority", figs[0])
                else:
                    self.assertIn('loading="eager" fetchpriority="high"', figs[0])
                    n += 1
        self.assertGreaterEqual(n, 110)
        page = (ROOT / "static/field-pack/hogle-zoo/index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('fetchpriority="high"'), 1)

    def test_generator(self):
        import generate_bdo_seo as gen

        html = gen.place_photo_figure({"rel": "photos/x.jpg", "alt": "X", "width": 1, "height": 1, "caption": "c"})
        self.assertIn('fetchpriority="high"', html)


if __name__ == "__main__":
    unittest.main()
