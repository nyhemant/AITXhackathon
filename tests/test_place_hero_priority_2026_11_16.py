"""Place hero photo (mobile LCP) has fetchpriority=high on every place page that has one.

Held off the 2026-11-16 test/comparison pages until after the Nov 26 hero
judging. This test now expects the hint on those pages too; merge only after
that judging.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

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
                self.assertIn('loading="eager" fetchpriority="high"', figs[0])
                n += 1
        self.assertGreaterEqual(n, 130)
        page = (ROOT / "static/field-pack/hogle-zoo/index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('fetchpriority="high"'), 1)
        dallas = (ROOT / "static/field-pack/dallas-zoo/index.html").read_text(encoding="utf-8")
        figs = FIG.findall(dallas)
        self.assertEqual(len(figs), 1)
        self.assertIn("reticulated-giraffe", figs[0])
        self.assertIn('loading="eager" fetchpriority="high"', figs[0])

    def test_generator(self):
        import generate_bdo_seo as gen

        html = gen.place_photo_figure({"rel": "photos/x.jpg", "alt": "X", "width": 1, "height": 1, "caption": "c"})
        self.assertIn('fetchpriority="high"', html)


if __name__ == "__main__":
    unittest.main()
