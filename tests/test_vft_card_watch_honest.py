"""Watch-from-card state honesty (2026-10-24).

A card-launched single-stop view (?from=card) must not claim
"1 of 1 stops · Path complete" on arrival. It names what is playing
("Watching: <animal>") and only counts the stop as seen after a real
interaction (play, cam, map tap, or focus moving into the player). It also
links back to the card's quiz.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "static" / "field-pack"
JS = FP / "js" / "virtual-venue.js"
VFT = FP / "virtual-field-trip" / "index.html"


class VftCardWatchHonestTest(unittest.TestCase):
    def setUp(self):
        self.js = JS.read_text(encoding="utf-8")
        self.html = VFT.read_text(encoding="utf-8")

    def test_card_mode_label_and_deferred_stamp(self):
        self.assertIn("Watching: ${watchName(habs[0])", self.js)
        self.assertIn("Seen ✓", self.js)
        self.assertIn("function stampHabitat(h)", self.js)
        self.assertIn("if (fromCard() && fromHash) {", self.js)
        self.assertIn("pendingStamp = stamps.includes(h.id) ? null : h;", self.js)
        # Real interactions stamp: film, cam, and focus moving into the player iframe.
        self.assertGreaterEqual(self.js.count("stampHabitat(h);"), 3)
        self.assertIn('window.addEventListener("blur"', self.js)
        self.assertIn('a.tagName !== "IFRAME"', self.js)

    def test_quiz_link_back_to_card(self):
        self.assertIn('id="vz-card-quiz"', self.html)
        self.assertIn('return cardHrefFor(h) + "#quiz";', self.js)
        self.assertIn("Try the ${name} quiz →", self.js)
        self.assertIn('link_type: "watch_quiz"', self.js)
        self.assertNotIn("free", "Try the quiz".lower())

    def test_every_card_watch_link_lands_on_a_quiz_card_tab(self):
        n = 0
        for page in (FP / "cards").glob("*/index.html"):
            html = page.read_text(encoding="utf-8")
            m = re.search(r'<a[^>]*card-watch-live[^>]*href="([^"]+)"', html)
            if not m:
                continue
            n += 1
            tab = re.search(r"tab=([a-z_-]+)", m.group(1)).group(1)
            self.assertIn(tab, ("zoo", "aquarium"), page.parent.name)
            self.assertIn("data-study-id=", html, page.parent.name)
            self.assertIn('id="quiz"', html, page.parent.name)
        self.assertGreaterEqual(n, 41)

    def test_asset_version_bumped(self):
        self.assertIn("/field-pack/js/virtual-venue.js?v=111", self.html)


if __name__ == "__main__":
    unittest.main()
