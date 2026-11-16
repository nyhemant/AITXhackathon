"""Follow-up 2026-11-16: 'N animals with talk cards' counts animals only."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_bdo_seo as gen  # noqa: E402

FP = ROOT / "static" / "field-pack"


def _label(slug: str) -> str:
    page = (FP / slug / "index.html").read_text(encoding="utf-8")
    return re.search(r'<span class="seo-home-summary-count">([^<]*)</span>', page).group(1)


class TalkCount(unittest.TestCase):
    def test_classifier(self):
        self.assertTrue(gen.home_card_is_animal({"id": "african-lion"}))
        self.assertTrue(gen.home_card_is_animal({"id": "shark"}))
        self.assertFalse(gen.home_card_is_animal({"id": "sci-dinosaur"}))
        self.assertFalse(gen.home_card_is_animal({"id": "np-visitor-center"}))
        self.assertFalse(gen.home_card_is_animal({"id": "fm-maximo"}))
        self.assertTrue(gen.home_card_is_animal({"id": "nzp-tiger", "find_kind": "animal"}))

    def test_labels(self):
        self.assertEqual(_label("field-museum"), "Talk cards for this place")  # halls and fossils only
        self.assertEqual(_label("acadia"), "Talk cards for this place")  # park stops only
        self.assertEqual(_label("delhi-zoo"), "9 animals with talk cards")
        self.assertEqual(_label("audubon-aquarium"), "5 animals with talk cards")  # 3 exhibits not counted

    def test_every_nonfrozen_label_matches_rule(self):
        for d in sorted(FP.iterdir()):
            f = d / "index.html"
            if d.name in gen.FROZEN_PLACE_SLUGS or not f.is_file():
                continue
            page = f.read_text(encoding="utf-8")
            m = re.search(r'<span class="seo-home-summary-count">([^<]*)</span>', page)
            if not m:
                continue
            ids = re.findall(r'<article class="seo-home-card" id="home-([^"]+)">', page)
            m2 = re.match(r"(\d+) animals? with talk cards$", m.group(1))
            if m2:
                self.assertGreater(int(m2.group(1)), 0, d.name)
                self.assertLessEqual(int(m2.group(1)), len(ids), d.name)
            else:
                self.assertEqual(m.group(1), "Talk cards for this place", d.name)


if __name__ == "__main__":
    unittest.main()
