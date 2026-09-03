"""Cards hub is a find-a-card explorer, twin of the place explorer."""

from pathlib import Path
import re
import unittest

from busyparent_agent.web import WebHandler


REPO = Path(__file__).resolve().parents[1]
CARDS = REPO / "static" / "field-pack" / "cards" / "index.html"
START = REPO / "static" / "start" / "index.html"
GIRAFFE = REPO / "static" / "field-pack" / "cards" / "reticulated-giraffe" / "index.html"


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


class CardsExplorerTests(unittest.TestCase):
    def setUp(self):
        self.html = CARDS.read_text(encoding="utf-8")
        self.start = START.read_text(encoding="utf-8")

    def test_cards_route_200_and_find_a_card(self):
        h = FakeHandler("/field-pack/cards/")
        h.do_GET()
        self.assertEqual(h._code, 200)
        body = h.wfile.getvalue().decode("utf-8")
        self.assertIn("cards-explorer", body)
        self.assertIn("Find a card", body)
        self.assertIn('id="cards-hub-search"', body)
        self.assertIn("Lion, shark, dinosaur", body)

    def test_explorer_is_samples_not_a_58_card_wall(self):
        self.assertIn("landing-hub", self.html)
        self.assertIn('id="try-a-card"', self.html)
        self.assertIn("Try a card", self.html)
        self.assertIn('href="/field-pack/cards/reticulated-giraffe/"', self.html)
        self.assertIn('href="/field-pack/cards/african-elephant/"', self.html)
        self.assertIn('href="/field-pack/cards/african-lion/"', self.html)
        self.assertIn('id="cards-all-wrap"', self.html)
        self.assertIn("All 58 cards", self.html)
        before_all, after_all = self.html.split('id="cards-all-wrap"', 1)
        self.assertNotIn("cards-hub-item", before_all)
        self.assertIn("cards-hub-item", after_all)
        self.assertEqual(self.html.count('class="cards-hub-item"'), 58)
        self.assertIn('data-card-filter="wildlife"', self.html)
        self.assertIn('data-card-filter="sealife"', self.html)
        self.assertIn('data-card-filter="attractions"', self.html)
        self.assertIn('data-card-filter="parks"', self.html)
        self.assertIn("58 cards · from Field Trip Kit place lists", self.html)

    def test_nav_pairs_with_places_and_start(self):
        self.assertIn('href="/start/"', self.html)
        self.assertIn('class="shell-start"', self.html)
        self.assertIn('href="/field-pack/"', self.html)
        self.assertIn(">Places<", self.html)
        self.assertIn('href="/about/"', self.html)
        self.assertNotIn("youtube.com", self.html)

    def test_existing_card_urls_and_return_crumb(self):
        self.assertTrue(GIRAFFE.is_file())
        giraffe = GIRAFFE.read_text(encoding="utf-8")
        self.assertIn('href="/field-pack/cards/"', giraffe)
        self.assertIn("/field-pack/cards/reticulated-giraffe/", self.html)

    def test_start_teaching_opens_cards(self):
        teach = re.search(
            r'<section class="start-chapter" id="start-teach"[\s\S]*?</section>',
            self.start,
        )
        self.assertIsNotNone(teach)
        chapter = teach.group(0)
        self.assertIn("Explore cards", chapter)
        self.assertIn('href="/field-pack/cards/"', chapter)
        self.assertIn('href="/field-pack/cards/reticulated-giraffe/"', chapter)
        self.assertNotIn("/field-pack/dallas-zoo/", chapter)
        door = re.search(r'<a[^>]*id="door-teaching"[^>]*>', self.start)
        self.assertIsNotNone(door)
        self.assertIn('href="/field-pack/cards/"', door.group(0))


if __name__ == "__main__":
    unittest.main()
