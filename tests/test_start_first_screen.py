"""/start/ first-screen diet (2026-10-22): only the hero map loads eagerly."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

START = Path(__file__).resolve().parents[1] / "static" / "start"


class StartFirstScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (START / "index.html").read_text(encoding="utf-8")
        cls.js = (START / "start.js").read_text(encoding="utf-8")

    def test_hero_map_is_the_only_high_priority_image(self):
        self.assertEqual(self.html.count('fetchpriority="high"'), 1)
        hero = re.search(r'<img\s+class="start-hero-still"[^>]*>', self.html).group(0)
        self.assertIn('fetchpriority="high"', hero)
        self.assertNotIn('loading="lazy"', hero)

    def test_hero_cards_yield_to_the_map(self):
        cards = re.findall(r'<img\s+src="/start/playing-card-[a-z]+\.png"[^>]*>', self.html)
        self.assertEqual(len(cards), 3)
        for c in cards:
            self.assertIn('fetchpriority="low"', c)

    def test_sample_cards_and_hunt_preview_have_alt(self):
        expected = {
            "/start/playing-card-koala.png": "Sleepy eucalyptus climber — naps most of the day.",
            "/start/playing-card-tiger.png": "Quiet striped hunter — built for the forest edge.",
            "/start/playing-card-zebra.png": "Striped grassland runner — every pattern is unique.",
            "/printables/img/scavenger-hunt.png": "Zoo &amp; Park Scavenger Hunt",
        }
        for src, needle in expected.items():
            tag = re.search(rf'<img\b[^>]*\bsrc="{re.escape(src)}"[^>]*>', self.html)
            self.assertIsNotNone(tag, src)
            alt = re.search(r'\balt="([^"]*)"', tag.group(0))
            self.assertIsNotNone(alt, src)
            self.assertTrue(alt.group(1).strip(), src)
            self.assertIn(needle, alt.group(1), src)
        fallback = re.search(r'<img class="start-home-fallback"[^>]*>', self.html)
        self.assertIsNotNone(fallback)
        self.assertIn('alt=""', fallback.group(0))

    def test_below_fold_home_plate_is_lazy(self):
        plate = re.search(r'<img\s+class="start-chapter-still"\s+src="/start/home-print-table\.jpg"[^>]*>', self.html)
        self.assertIsNotNone(plate)
        self.assertIn('loading="lazy"', plate.group(0))

    def test_slides_and_video_wait_until_near(self):
        self.assertIn("function nearGate(", self.js)
        self.assertIn("const teachNear = nearGate(section)", self.js)
        self.assertIn("const goingNear = nearGate(section)", self.js)
        self.assertIn("if (teaserNear) armTeaser();", self.js)
        self.assertIn('rootMargin: "400px 0px"', self.js)


if __name__ == "__main__":
    unittest.main()
