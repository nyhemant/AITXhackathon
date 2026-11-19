"""Device-only animal stars on the card quiz finish panel."""

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / "static" / "field-pack" / "js" / "study-card.js"
GEN = ROOT / "scripts" / "generate_bdo_seo.py"
CARDS = ROOT / "static" / "field-pack" / "cards"
PRIVACY = ROOT / "static" / "privacy" / "index.html"
PRIVACY_SENTENCE = (
    "Animal stars from finished card quizzes are saved only in this browser "
    "(local storage) and are never sent anywhere; the Clear stars button removes them."
)


class StudyCardStarsTests(unittest.TestCase):
    def setUp(self):
        self.js = JS.read_text(encoding="utf-8")
        self.region = self.js.split("/* kzk-stars-start */", 1)[1].split("/* kzk-stars-end */", 1)[0]

    def test_storage_key_and_copy(self):
        self.assertIn("kzk_stars_v1", self.region)
        self.assertIn("Animal stars saved on this browser", self.region)
        self.assertIn('n === 1 ? "animal" : "animals"', self.region)
        self.assertIn("Clear stars", self.region)
        self.assertIn("confirm(", self.region)
        self.assertIn("removeItem", self.region)
        self.assertIn(".slice(-3)", self.region)
        self.assertIn("You earned a star on this animal before", self.region)
        self.assertIn("See all animal cards", self.region)
        self.assertIn('href="/field-pack/cards/"', self.region)

    def test_storage_is_try_catch_and_offline(self):
        for needle in (
            "localStorage.getItem",
            "localStorage.setItem",
            "localStorage.removeItem",
            "JSON.parse",
        ):
            idx = self.region.find(needle)
            self.assertGreater(idx, -1, needle)
            self.assertGreater(self.region.rfind("try", 0, idx), -1, needle)
            self.assertGreater(self.region.find("catch", idx), idx, needle)
        self.assertNotIn("fetch(", self.region)
        self.assertNotIn("sendBeacon", self.region)
        self.assertNotIn("gtag", self.region)
        lowered = self.region.lower()
        self.assertNotIn("we ", lowered)
        self.assertNotIn("our ", lowered)
        self.assertNotRegex(lowered, r"\bfree\b")

    def test_shelf_follows_what_next_list(self):
        finish = self.js.split("function paintFinish", 1)[1].split("function afterAnswer", 1)[0]
        next_at = finish.find('class="study-finish-next"')
        stars_at = finish.find("starsShelfHtml(")
        self.assertGreater(next_at, -1)
        self.assertGreater(stars_at, next_at)
        self.assertIn("What next?", finish)
        self.assertLess(finish.find("What next?"), stars_at)
        answered = self.js.split("function afterAnswer", 1)[1].split("function markChoice", 1)[0]
        self.assertLess(answered.find("recordAnimalStar("), answered.find("paintFinish("))
        self.assertIn('quizTrack("quiz_complete"', answered)

    def test_card_pages_use_study_card_v23(self):
        gen = GEN.read_text(encoding="utf-8")
        self.assertIn('STUDY_CARD_JS_VER = "23"', gen)
        pages = list(CARDS.glob("*/index.html"))
        linked = []
        for page in pages:
            html = page.read_text(encoding="utf-8")
            self.assertNotIn("/field-pack/js/study-card.js?v=22", html, page.parent.name)
            if "study-card.js" in html:
                self.assertIn("/field-pack/js/study-card.js?v=23", html, page.parent.name)
                linked.append(page.parent.name)
        self.assertEqual(len(linked), 42)

    def test_privacy_sentence_added(self):
        html = PRIVACY.read_text(encoding="utf-8")
        self.assertEqual(html.count(PRIVACY_SENTENCE), 1)
        self.assertIn("<title>Privacy — KidZooKit</title>", html)
        self.assertIn('<h1 id="privacy-heading">Privacy</h1>', html)


if __name__ == "__main__":
    unittest.main()
