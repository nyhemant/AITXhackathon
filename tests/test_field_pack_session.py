"""Flagship at-home session: honest start-here, 6-Q cards, no notice-stubs."""

from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"


class FlagshipSessionTests(unittest.TestCase):
    def test_map_count_never_places_loading(self):
        html = (FP / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("Places loading", html)
        self.assertIn("218 places worldwide", html)
        self.assertIn("<noscript><p class=\"map-count-quiet\">218 places worldwide</p></noscript>", html)

    def _visible(self, html: str) -> str:
        return html.split('id="venue-data"', 1)[0]

    def test_dallas_start_here_is_dual_cta(self):
        html = (FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8")
        visible = self._visible(html)
        self.assertIn("Talk at home", visible)
        self.assertIn("Add to hunt", visible)
        self.assertIn('href="/field-pack/cards/reticulated-giraffe/"', visible)
        self.assertIn('href="/field-pack/cards/african-elephant/"', visible)
        self.assertIn('href="/field-pack/cards/african-lion/"', visible)
        self.assertIn('data-how="print-hunt"', visible)
        self.assertIn("This zoo's cards", visible)
        self.assertIn('href="#at-home"', visible)
        start = visible.split('id="route90-heading"', 1)[1].split("</section>", 1)[0]
        self.assertNotIn('class="seo-start-card" href="#mission"', start)
        self.assertNotIn("What did you notice about", visible)

    def test_san_diego_start_here_is_dual_cta(self):
        html = (FP / "san-diego-zoo" / "index.html").read_text(encoding="utf-8")
        visible = self._visible(html)
        self.assertIn("Talk at home", visible)
        self.assertIn("Add to hunt", visible)
        self.assertIn('href="/field-pack/cards/giant-panda/"', visible)
        self.assertIn('href="/field-pack/cards/koala/"', visible)
        self.assertIn("This zoo's cards", visible)
        self.assertNotIn("What did you notice about the Koala?", visible)

    def test_lion_card_has_outing_six_and_cam(self):
        html = (FP / "cards" / "african-lion" / "index.html").read_text(encoding="utf-8")
        for q in (
            "What do they eat?",
            "Where is home?",
            "What is their superpower?",
            "Baby or grown-up?",
            "Did we see one live?",
            "I want to teach about…",
        ):
            self.assertIn(q, html)
        self.assertIn("nationalzoo.si.edu/webcams/lion-cam", html)
        self.assertIn("Print this card", html)
        self.assertNotIn("Open in outing view", html)
        self.assertNotIn("What did you notice about", html)

    def test_flagship_cards_reuse_vft_cams_when_present(self):
        expect = {
            "reticulated-giraffe": "houstonzoo.org/explore/webcams/giraffe-feeding-platform",
            "african-elephant": "nationalzoo.si.edu/webcams/elephants",
            "african-lion": "nationalzoo.si.edu/webcams/lion-cam",
            "giant-panda": "nationalzoo.si.edu/webcams/panda-cam",
            "african-penguin": "zoo.sandiegozoo.org/cams/penguin-cam",
        }
        for cid, needle in expect.items():
            html = (FP / "cards" / cid / "index.html").read_text(encoding="utf-8")
            self.assertIn(needle, html, cid)
            self.assertIn("What do they eat?", html)
        koala = (FP / "cards" / "koala" / "index.html").read_text(encoding="utf-8")
        self.assertIn("What do they eat?", koala)
        self.assertNotIn("What did you notice about the Koala?", koala)

    def test_dallas_real_qa_kept_generic_notice_not_shipped(self):
        dallas = self._visible((FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8"))
        giraffe = (FP / "cards" / "reticulated-giraffe" / "index.html").read_text(encoding="utf-8")
        self.assertIn("How does a giraffe drink water?", giraffe)
        self.assertIn("What does an elephant use its trunk for?", (FP / "cards" / "african-elephant" / "index.html").read_text(encoding="utf-8"))
        self.assertNotIn("What did you notice about", dallas)

    def test_dinner_route_still_defined(self):
        web = (REPO / "src" / "busyparent_agent" / "web.py").read_text(encoding="utf-8")
        self.assertIn('DINNER_PATH = "/dinner"', web)


if __name__ == "__main__":
    unittest.main()
