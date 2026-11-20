"""Round 2 item 4b (2026-11-20): /start/ has one obvious first job.

GA4 (Nov 20): 34% of /start/ landers engage and 4 of 47 tapped a map pin. The first screen now leads
with one button, "Pick your zoo or aquarium" (the place search on /field-pack/), and the map is the
second way in. Title, meta and H1 do not change. Arya's Wildlife Project stays.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "static" / "start" / "index.html"
FP_INDEX = ROOT / "static" / "field-pack" / "index.html"
HOOK = ROOT / "static" / "field-pack" / "js" / "landing-hook.js"


class StartFirstJob(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = START.read_text(encoding="utf-8")

    def test_one_primary_action_right_under_the_headline(self):
        head = re.search(r'<div class="hx-head">([\s\S]*?)</div>', self.html).group(1)
        self.assertIn('<h1 id="start-heading">Printable scavenger hunts for your next zoo, aquarium or museum trip</h1>', head)
        self.assertEqual(head.count('class="hx-pick"'), 1)
        self.assertLess(head.find("</h1>"), head.find('class="hx-pick"'))
        self.assertEqual(self.html.count('class="hx-pick"'), 1)
        self.assertIn('<span class="hx-or">or tap a pin on the map</span>', head)
        text = re.sub(r"<[^>]+>", " ", head).lower()
        self.assertNotRegex(text, r"\bfree\b|\bwe\b|\bour\b")

    def test_target_is_the_place_search(self):
        self.assertIn('id="hero-place-search"', FP_INDEX.read_text(encoding="utf-8"))
        self.assertIn('get("find") === "1"', HOOK.read_text(encoding="utf-8"))

    def test_identity_and_head_tags_unchanged(self):
        self.assertIn("Arya’s Wildlife Project", self.html)
        self.assertIn("<title>Virtual Zoo for Kids: Animal Cards &amp; Quizzes | KidZooKit</title>", self.html)
        about = (ROOT / "static" / "about" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Arya", about)


if __name__ == "__main__":
    unittest.main()
