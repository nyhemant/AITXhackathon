"""Follow-up 2026-11-16: no live-cam promise in LD/meta on place pages without a live cam row."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_bdo_seo as gen  # noqa: E402

FP = ROOT / "static" / "field-pack"
LIVE = '<span class="seo-watch-source">Live'
FILM = '<span class="seo-watch-source">Film'


def _claims(page: str) -> list[str]:
    out = [m.group(1) for m in re.finditer(r'"description": "([^"]*)"', page)]
    out += [m.group(1) for m in re.finditer(r'<meta (?:name|property)="[^"]*description" content="([^"]*)"', page)]
    out += re.findall(r'"name": "(Phone or laptop[^"]*)"', page)
    return out


class CamHonesty(unittest.TestCase):
    def test_no_cam_claim_without_live_row(self):
        checked = 0
        for d in sorted(FP.iterdir()):
            f = d / "index.html"
            if not f.is_file() or d.name in gen.FROZEN_PLACE_SLUGS:
                continue
            page = f.read_text(encoding="utf-8")
            if 'id="venue-data"' not in page and "seo-home-session" not in page:
                continue
            if LIVE in page:
                continue
            checked += 1
            for c in _claims(page):
                self.assertNotRegex(c, r"(?i)\bcams?\b|webcam", f"{d.name}: {c}")
        self.assertGreater(checked, 50)

    def test_films_named_when_shown(self):
        page = (FP / "arizona-science-center" / "index.html").read_text(encoding="utf-8")
        self.assertIn(FILM, page)
        self.assertNotIn(LIVE, page)
        self.assertIn("talk prompts, photos, and films at home", page)
        self.assertIn('"Phone or laptop (cards, photos, films)"', page)

    def test_generator_guard(self):
        ld = '"description": "X in Y: animal cards, talk prompts, photos, and live cams at home." "name": "Phone or laptop (cards, photos, cams)"'
        none = gen.apply_cam_honesty("acadia", ld)
        self.assertIn("talk prompts, and photos at home", none)
        self.assertIn("(cards and photos)", none)
        films = gen.apply_cam_honesty("acadia", ld + FILM)
        self.assertIn("photos, and films at home", films)
        live = ld + LIVE
        self.assertEqual(gen.apply_cam_honesty("acadia", live), live)
        self.assertEqual(gen.apply_cam_honesty("bronx-zoo", ld), ld)  # frozen page: untouched
        self.assertEqual(gen.apply_cam_honesty("acadia", none), none)  # idempotent


if __name__ == "__main__":
    unittest.main()
