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

    def test_hidden_animals_plate_waits_and_nothing_jumps_the_queue(self):
        # Map v2: Places leads, so the hidden Animals world plate is lazy and no image is high priority.
        self.assertEqual(self.html.count('fetchpriority="high"'), 0)
        hero = re.search(r'<img\s+class="kzm-base start-hero-still"[^>]*>', self.html).group(0)
        self.assertIn('loading="lazy"', hero)
        self.assertIn('src="/start/map-v2/a-world-v1.svg"', hero)

    def test_hero_cards_yield_to_the_map(self):
        # Map v2 drops the playing-card stack from the Animals view; the files stay for old links.
        self.assertEqual(re.findall(r'<img\s+src="/start/playing-card-[a-z]+\.png"[^>]*>', self.html), [])
        for name in ("koala", "tiger", "zebra"):
            self.assertTrue((START / f"playing-card-{name}.png").is_file(), name)

    def test_sample_cards_and_hunt_preview_have_alt(self):
        expected = {
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
