"""First-time landing at /start/ — does not replace the live home."""

from pathlib import Path
import re
import unittest

from busyparent_agent.web import (
    FIELD_PACK_PREFIX,
    START_PREFIX,
    WebHandler,
    _safe_field_pack_path,
    _safe_start_path,
)


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
START = REPO / "static" / "start"
HOME = FP / "index.html"
START_HTML = START / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


class FakeHandler(WebHandler):
    def __init__(self, path):
        self.path = path
        self.headers = {}
        self._code = None
        self._headers = {}
        self.wfile = _Buf()

    def send_response(self, code, message=None):
        self._code = code

    def send_error(self, code, message=None):
        self._code = code

    def send_header(self, k, v):
        self._headers[k] = v

    def end_headers(self):
        return

    def log_message(self, format, *args):
        return


def _get(path: str) -> FakeHandler:
    h = FakeHandler(path)
    h.do_GET()
    return h


class StartLandingTests(unittest.TestCase):
    def setUp(self):
        self.html = START_HTML.read_text(encoding="utf-8")
        self.css = (START / "start.css").read_text(encoding="utf-8")
        self.js = (START / "start.js").read_text(encoding="utf-8")
        self.home = HOME.read_text(encoding="utf-8")
        self.card = re.search(
            r'<article\s+class="start-card"[\s\S]*?</article>',
            self.html,
        )
        self.assertIsNotNone(self.card)
        self.card_html = self.card.group(0)

    def test_route_is_start_not_home(self):
        root = _get("/")
        self.assertEqual(root._code, 302)
        self.assertEqual(root._headers.get("Location"), FIELD_PACK_PREFIX + "/")

        home = _get("/field-pack/")
        self.assertEqual(home._code, 200)
        self.assertIn(b'id="us-map"', home.wfile.getvalue())
        self.assertIn(b"landing-pitch-t4b", home.wfile.getvalue())

        slashless = _get("/start")
        self.assertEqual(slashless._code, 301)
        self.assertEqual(slashless._headers.get("Location"), START_PREFIX + "/")

        start = _get("/start/")
        self.assertEqual(start._code, 200)
        body = start.wfile.getvalue().decode("utf-8")
        self.assertIn("Giraffe first. Then elephant. Then you’re done.", body)
        self.assertIn('href="/field-pack/dallas-zoo/"', body)
        self.assertIsNotNone(_safe_start_path("/start/"))
        self.assertIsNotNone(_safe_start_path("/start/start.css"))
        self.assertIsNone(_safe_start_path("/start/../field-pack/index.html"))
        self.assertIsNotNone(_safe_field_pack_path("/field-pack/"))

    def test_locked_headline_and_sub(self):
        h1 = re.search(r"<h1[^>]*id=\"start-heading\"[^>]*>([\s\S]*?)</h1>", self.html)
        self.assertIsNotNone(h1)
        self.assertEqual(
            re.sub(r"\s+", " ", h1.group(1)).strip(),
            "Giraffe first. Then elephant. Then you’re done.",
        )
        self.assertIn("A short zoo or aquarium hour. At home, or before you go.", self.html)

    def test_teaches_in_locked_order(self):
        value = self.html.find('id="start-value"')
        jobs = self.html.find('id="start-jobs"')
        place = self.html.find('id="start-place"')
        card = self.html.find('id="start-giraffe-card"')
        close = self.html.find('id="start-close"')
        self.assertTrue(0 < value < jobs < place < card < close)
        self.assertIn("Going in person", self.html)
        self.assertIn("Staying in", self.html)
        self.assertIn("Print a hunt later", self.html)
        self.assertIn("Same cards on the couch", self.html)
        self.assertLess(place, self.html.find("Open Dallas Zoo"))
        self.assertLess(card, self.html.find('id="start-open-dallas-after"'))

    def test_primary_cta_opens_dallas_session(self):
        self.assertIn(">Open Dallas Zoo</a>", self.html)
        self.assertIn('id="start-open-dallas"', self.html)
        self.assertIn('href="/field-pack/dallas-zoo/"', self.html)
        self.assertNotIn("/field-pack/dallas-zoo/#mission", self.html)
        self.assertNotIn("/field-pack/dallas-zoo/#print", self.html)
        self.assertNotIn("youtube.com", self.html)
        self.assertNotIn("youtube-nocookie.com", self.html)
        self.assertNotIn("us-map", self.html)
        self.assertNotIn("map-host", self.html)

    def test_real_dallas_giraffe_card(self):
        giraffe = GIRAFFE.read_text(encoding="utf-8")
        dallas = (FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8")
        self.assertIn("/field-pack/photos/reticulated-giraffe.jpg?v=img2", self.card_html)
        self.assertIn("Reticulated giraffe", self.card_html)
        self.assertIn("Feed one from the Giraffe Ridge platform.", self.card_html)
        self.assertIn("How does a giraffe drink water?", self.card_html)
        self.assertIn("It spreads its front legs wide and bends way down.", self.card_html)
        self.assertIn("What do they eat?", self.card_html)
        self.assertIn("Feed one from the Giraffe Ridge platform.", dallas)
        self.assertIn("How does a giraffe drink water?", giraffe)
        self.assertNotIn("Dallas Zoo", self.card_html)
        self.assertNotIn("National Zoo", self.card_html)

    def test_verified_place_chrome_sits_by_cta(self):
        proof = self.html.split('id="start-open-dallas"', 1)[1].split("<article", 1)[0]
        self.assertIn("Verified", proof)
        self.assertIn("Dallas Zoo", proof)
        self.assertIn("checked Aug 2026", proof)
        self.assertIn("/field-pack/national-zoo/", self.html)
        self.assertIn("National Zoo", self.html)
        self.assertNotIn("Experimental", self.html)
        self.assertNotIn("10,000 families", self.html)

    def test_no_dinner_age_filter_or_home_replacement(self):
        self.assertNotIn("/dinner", self.html)
        self.assertNotIn("seo-age-chip", self.html)
        self.assertNotIn("landing-pitch-t4b", self.html)
        self.assertNotIn("hero-moment-link", self.html)
        self.assertIn("landing-pitch-t4b", self.home)
        self.assertIn('id="us-map"', self.home)
        self.assertNotIn('id="start-open-dallas"', self.home)
        self.assertNotIn("Giraffe first. Then elephant. Then you’re done.", self.home)
        self.assertIn("Museums and parks are here too — later.", self.html)
        self.assertNotIn("/field-pack/museums/", self.html)
        self.assertNotIn("/field-pack/national-parks/", self.html)

    def test_motion_respects_reduced_and_tap(self):
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn(":focus-within", self.css)
        self.assertIn("is-open", self.js)
        self.assertIn("prefers-reduced-motion", self.js)
        self.assertNotIn("autoplay", self.html)
        self.assertNotIn("youtube", self.js)


if __name__ == "__main__":
    unittest.main()
