"""First-time homepage: giraffe card first, Dallas session, no twin hub."""

from pathlib import Path
import re
import unittest

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
HOME = FP / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"


class HomepageFirstTests(unittest.TestCase):
    def setUp(self):
        self.html = HOME.read_text(encoding="utf-8")
        first = self.html.split('id="during"', 1)[0]
        start = first.find('id="landing-hero"')
        self.assertNotEqual(start, -1)
        self.hero = first[start:]
        self.card = re.search(
            r'<article class="home-giraffe-card"[^>]*>[\s\S]*?</article>',
            self.hero,
        )
        self.assertIsNotNone(self.card)
        self.card_html = self.card.group(0)

    def test_locked_headline_and_sub(self):
        self.assertIn("Giraffe first. Then elephant. Then you’re done.", self.hero)
        self.assertIn("A short zoo or aquarium hour. At home, or before you go.", self.hero)
        h1 = re.search(r'<h1[^>]*id="pitch-heading"[^>]*>([\s\S]*?)</h1>', self.hero)
        self.assertIsNotNone(h1)
        self.assertEqual(
            re.sub(r"\s+", " ", h1.group(1)).strip(),
            "Giraffe first. Then elephant. Then you’re done.",
        )

    def test_primary_cta_opens_dallas_session(self):
        self.assertIn(">Open Dallas Zoo</a>", self.hero)
        self.assertIn('id="home-open-dallas"', self.hero)
        self.assertIn('href="/field-pack/dallas-zoo/"', self.hero)
        self.assertNotIn('href="/field-pack/dallas-zoo/#mission"', self.html)
        self.assertNotIn('href="/field-pack/dallas-zoo/#print"', self.html)
        self.assertNotIn("youtube.com", self.hero)
        self.assertNotIn("youtube-nocookie.com", self.hero)
        self.assertLess(self.hero.find("Open Dallas Zoo"), self.html.find('id="us-map"'))
        self.assertLess(self.hero.find("Open Dallas Zoo"), self.html.find('id="map-host"'))

    def test_real_giraffe_card_from_existing_copy(self):
        giraffe = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn("/field-pack/photos/reticulated-giraffe.jpg?v=img2", self.card_html)
        self.assertIn("Reticulated giraffe", self.card_html)
        self.assertIn("Tallest animal on long legs — look up!", self.card_html)
        self.assertIn("How does a giraffe drink water?", self.card_html)
        self.assertIn("It spreads its front legs wide and bends way down.", self.card_html)
        self.assertIn("What do they eat?", self.card_html)
        self.assertIn("Tallest animal on long legs — look up!", giraffe)
        self.assertIn("How does a giraffe drink water?", giraffe)
        self.assertNotIn("Dallas Zoo", self.card_html)

    def test_verified_place_named_next_to_cta(self):
        proof = self.hero.split('id="home-open-dallas"', 1)[1].split("<article", 1)[0]
        self.assertIn("Verified", proof)
        self.assertIn("Dallas Zoo", proof)
        self.assertIn("checked Aug 2026", proof)
        self.assertNotIn("Experimental", self.hero)

    def test_no_dinner_age_picker_or_lead_phrases(self):
        self.assertNotIn("/dinner", self.html)
        self.assertNotIn("seo-age-chip", self.hero)
        self.assertNotIn("hero-moment-link", self.hero)
        self.assertNotIn("one less thing", self.hero.lower())
        self.assertNotIn("virtual field trip", self.hero.lower())
        self.assertNotIn("a better hour", self.hero.lower())
        self.assertNotIn("10,000 families", self.html)
        self.assertNotIn("Explore a zoo, aquarium, or park at home", self.hero)

    def test_second_beat_after_cta_not_print_first(self):
        self.assertIn('id="home-second"', self.hero)
        self.assertIn("Going in person", self.hero)
        self.assertIn("Staying in", self.hero)
        self.assertIn("Print a hunt later", self.hero)
        self.assertIn("Same cards, plus live cams", self.hero)
        self.assertLess(self.hero.find("Open Dallas Zoo"), self.hero.find("Going in person"))
        self.assertLess(self.hero.find("Open Dallas Zoo"), self.hero.find("museums"))

    def test_no_classic_twin_first_screen(self):
        self.assertNotIn("landing-pitch-t4b", self.html)
        self.assertNotIn("hero-moment-strip", self.html)
        self.assertIn("home-first.css", self.html)
        self.assertIn("home-first.js", self.html)
        self.assertIn("prefers-reduced-motion", (FP / "css" / "home-first.css").read_text(encoding="utf-8"))

    def test_catalog_and_faq_stay_below(self):
        self.assertIn('id="cat-card-grid"', self.html)
        self.assertIn("218 places worldwide", self.html)
        self.assertIn('id="faq"', self.html)
        self.assertLess(self.html.find('id="landing-hero"'), self.html.find('id="during"'))
        self.assertLess(self.html.find('id="home-open-dallas"'), self.html.find('id="cat-card-grid"'))


if __name__ == "__main__":
    unittest.main()
