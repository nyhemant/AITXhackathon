"""2026-10-29 (reviewer-adopted): every quiz card shows a visible in-page "Take the quiz" jump right under
the intro, and the outside "More photos at ..." link sits below Print. No new tracking, no URL changes."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

CARDS = Path(__file__).resolve().parents[1] / "static" / "field-pack" / "cards"


class CardQuizJumpTests(unittest.TestCase):
    def test_quiz_cards_show_jump_and_photos_below_print(self):
        n = 0
        for f in sorted(CARDS.glob("*/index.html")):
            html = f.read_text(encoding="utf-8")
            if 'id="quiz"' not in html or "card-study-pack" not in html:
                continue
            n += 1
            with self.subTest(card=f.parent.name):
                self.assertNotIn('card-quiz-peer" href="#quiz" hidden', html)
                jump = html.find('<a class="btn btn-primary card-quiz-peer" href="#quiz">Take the quiz</a>')
                self.assertGreater(jump, 0)
                self.assertLess(html.find('class="card-page-blurb"'), jump)
                self.assertLess(jump, html.find('id="quiz"'))
                if "card-page-photos" in html:
                    self.assertLess(html.find('id="print-this-card"'), html.find("card-page-photos"))
                    self.assertLess(html.find("card-page-photos"), html.find('id="quiz"'))
                self.assertIsNone(re.search(r"card-quiz-peer[^>]*data-ga|data-event[^>]*card-quiz-peer", html))
        self.assertGreaterEqual(n, 42)


if __name__ == "__main__":
    unittest.main()
