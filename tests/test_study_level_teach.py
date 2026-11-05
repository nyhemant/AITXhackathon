"""Learn-first tips on every study deck, copied from that deck's why text."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STUDY_JSON = REPO / "static" / "field-pack" / "data" / "study-cards.json"
STUDY_DATA_JS = REPO / "static" / "field-pack" / "js" / "study-cards-data.js"
CARDS = REPO / "static" / "field-pack" / "cards"
STUDY_JS = REPO / "static" / "field-pack" / "js" / "study-card.js"

LEVELS = ("easy", "hard", "zoologist")
SKIP_START = re.compile(r"^(correct|not quite|yes|no)\b", re.IGNORECASE)
BAD_REF = re.compile(
    r"\b(this answer|that choice|option)\b|\b(choice|letter|answer)\s+[ABC]\b",
    re.IGNORECASE,
)


def _cards_from_js() -> dict:
    js = STUDY_DATA_JS.read_text(encoding="utf-8")
    match = re.search(r"window\.FP_STUDY_CARDS = (\{.*?\});\n", js, re.S)
    if not match:
        raise AssertionError("FP_STUDY_CARDS missing from study-cards-data.js")
    return json.loads(match.group(1))


def _tip_key(text: str) -> str:
    cleaned = str(text or "").casefold().replace("’", "'")
    cleaned = re.sub(r"\s+", " ", cleaned).strip().rstrip(".!?\"'")
    return cleaned


class StudyLevelTeachTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = json.loads(STUDY_JSON.read_text(encoding="utf-8"))

    def test_json_and_data_js_match(self):
        self.assertEqual(self.cards, _cards_from_js())

    def test_every_deck_has_unique_teach_and_harder_tips_come_from_whys(self):
        self.assertGreaterEqual(len(self.cards), 42)
        for cid, card in self.cards.items():
            seen: set[str] = set()
            for level in LEVELS:
                pack = card["levels"][level]
                tips = list(pack.get("teach") or [])
                with self.subTest(card=cid, level=level):
                    self.assertGreaterEqual(len(tips), 2)
                    self.assertLessEqual(len(tips), 5)
                    whys = "\n".join(str(q.get("why") or "") for q in pack["questions"])
                    for tip in tips:
                        key = _tip_key(tip)
                        self.assertTrue(key)
                        self.assertNotIn(key, seen)
                        seen.add(key)
                        if level == "easy":
                            continue
                        self.assertIn(tip, whys)
                        self.assertLessEqual(len(re.findall(r"\S+", tip)), 30)
                        self.assertIsNone(SKIP_START.match(tip.strip()))
                        self.assertIsNone(BAD_REF.search(tip))

    def test_pages_open_tips_above_the_quiz_button(self):
        js = STUDY_JS.read_text(encoding="utf-8")
        self.assertIn("function placeTeachBeforeQuiz", js)
        self.assertIn("teachShouldOpen", js)
        self.assertIn("Quick tips (${esc(name)})", js)
        checked = 0
        for cid in self.cards:
            page = CARDS / cid / "index.html"
            html = page.read_text(encoding="utf-8")
            primary = html.split('class="card-page-actions-primary"', 1)[1].split(
                'class="card-page-actions-print"', 1
            )[0]
            teach_at = primary.find('class="study-teach" open')
            quiz_at = primary.find("card-quiz-peer")
            watch_at = primary.find("card-watch-live")
            with self.subTest(card=cid):
                self.assertGreaterEqual(teach_at, 0)
                self.assertLess(teach_at, quiz_at)
                if watch_at >= 0:
                    self.assertLess(watch_at, teach_at)
                self.assertIn("Quick tips (Junior Ranger)", primary)
                self.assertIn("study-cards-data.js?v=11", html)
                self.assertIn("study-card.js?v=22", html)
                self.assertIn("study-card.css?v=20", html)
                self.assertEqual(html.count('class="study-teach"'), 1)
                checked += 1
        self.assertGreaterEqual(checked, 42)


if __name__ == "__main__":
    unittest.main()
