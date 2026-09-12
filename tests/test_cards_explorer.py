"""Cards hub is the cutout-play door, then a find-a-card explorer."""

from pathlib import Path
import re
import unittest

from busyparent_agent.web import CARD_ALIAS_REDIRECTS, WebHandler


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
        self.assertIn("Print cutouts to play", body)
        self.assertIn("Find a card", body)
        self.assertIn('id="cards-hub-search"', body)
        self.assertIn("Lion, shark, bison", body)

    def test_play_door_is_first_and_teaches_print_cut_hide(self):
        play = re.search(r'<section class="cards-play"[\s\S]*?</section>', self.html)
        self.assertIsNotNone(play)
        door = play.group(0)
        self.assertLess(self.html.find('id="cards-play"'), self.html.find('id="cards-find"'))
        self.assertLess(self.html.find('id="cards-play"'), self.html.find('id="try-a-card"'))
        self.assertIn('id="cards-play-heading"', door)
        self.assertIn("Print cutouts to play", door)
        self.assertIn("Hide-and-seek at home", door)
        self.assertIn('src="/start/home-print-table.jpg"', door)
        self.assertIn("/start/home-print-table-480.jpg 480w", door)
        self.assertIn('class="cards-play-steps"', door)
        self.assertIn(">Print</span>", door)
        self.assertIn(">Cut</span>", door)
        self.assertIn(">Hide</span>", door)
        self.assertIn('href="/field-pack/print/"', door)
        self.assertIn("Print the cutouts", door)
        self.assertIn('href="/field-pack/cards/#try-a-card"', door)
        self.assertIn("Browse cards on the screen", door)
        self.assertNotIn("youtube.com", door)
        title = re.search(r"<title>(.*?)</title>", self.html)
        self.assertIsNotNone(title)
        self.assertIn("Print cutouts to play", title.group(1))
        self.assertIn("landing.css?v=102", self.html)
        self.assertIn("cards-explorer.js?v=5", self.html)

    def test_explorer_is_samples_not_a_58_card_wall(self):
        self.assertIn("landing-hub", self.html)
        self.assertIn('id="try-a-card"', self.html)
        self.assertIn("Try a card", self.html)
        try_row = re.search(
            r'<section class="ready-now ready-slim try-card-row"[\s\S]*?</section>',
            self.html,
        )
        self.assertIsNotNone(try_row)
        teasers = try_row.group(0)
        self.assertIn('href="/field-pack/cards/red-panda/"', teasers)
        self.assertIn('href="/field-pack/cards/whale-shark/"', teasers)
        self.assertIn('href="/field-pack/cards/octopus/"', teasers)
        self.assertNotIn('href="/field-pack/cards/reticulated-giraffe/"', teasers)
        self.assertNotIn('href="/field-pack/cards/african-elephant/"', teasers)
        self.assertNotIn('href="/field-pack/cards/african-lion/"', teasers)
        self.assertIn("Rusty tree-climber with a ringed tail — not a giant panda!", teasers)
        self.assertIn("Biggest fish in the sea — a gentle giant with a wide, filtering mouth.", teasers)
        self.assertIn("Eight arms and a big brain — master of hide-and-seek.", teasers)
        self.assertIn('id="cards-all-wrap"', self.html)
        self.assertIn(">All cards</button>", self.html)
        self.assertNotIn("All 43 cards", self.html)
        before_all, after_all = self.html.split('id="cards-all-wrap"', 1)
        self.assertNotIn("cards-hub-item", before_all)
        self.assertIn("cards-hub-item", after_all)
        self.assertEqual(self.html.count('class="cards-hub-item"'), 58)
        self.assertIn('data-card-filter="wildlife"', self.html)
        self.assertIn('data-card-filter="sealife"', self.html)
        self.assertNotIn('data-card-filter="attractions"', self.html)
        self.assertIn('data-card-filter="parks"', self.html)
        self.assertIn("43 cards", self.html)
        self.assertIn('id="cards-attractions"', self.html)
        self.assertIn("Museum &amp; science cards", self.html)
        self.assertIn("Experimental · Quiet", self.html)
        self.assertIn('id="cards-accordion"', self.html)
        self.assertIn("cards-theme-wildlife", self.html)
        self.assertIn("cards-theme-sealife", self.html)
        self.assertIn("cards-theme-parks", self.html)
        self.assertIn("cards-theme-attractions", self.html)
        self.assertNotIn("<h2 id=\"h-wildlife\">", self.html)
        self.assertNotIn("<h2 id=\"h-sealife\">", self.html)
        self.assertNotIn("<h2 id=\"h-parks\">", self.html)
        self.assertNotIn("<h2 id=\"h-attractions\">", self.html)
        self.assertIn('id="h-wildlife"', self.html)
        self.assertEqual(self.html.count('Wildlife <span class="seo-dir-count">22</span>'), 1)
        self.assertIn('data-card-accordion="wildlife" open', self.html)
        self.assertIn('data-card-accordion="sealife"', self.html)
        self.assertIn('data-card-accordion="parks"', self.html)
        self.assertIn('data-card-accordion="attractions"', self.html)
        self.assertNotIn('data-card-accordion="sealife" open', self.html)
        self.assertNotIn('data-card-accordion="parks" open', self.html)
        self.assertNotIn('data-card-accordion="attractions" open', self.html)
        self.assertNotIn('class="place-type-tabs-cards"', self.html)
        primary, experimental = self.html.split('id="cards-attractions"', 1)
        self.assertIn('data-card-id="american-bison"', primary)
        self.assertIn('data-card-id="american-alligator"', primary)
        self.assertIn('data-card-id="elk"', primary)
        self.assertNotIn('data-card-id="sci-dinosaur"', primary)
        self.assertIn('data-card-id="sci-dinosaur"', experimental)
        self.assertIn('data-card-id="cm-art-lab"', experimental)
        self.assertNotIn("from Field Trip Kit place lists", self.html)
        gen = (REPO / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        self.assertIn('TRY_CARD_IDS = ("red-panda", "whale-shark", "octopus")', gen)
        self.assertIn("cards-accordion-panel", gen)
        self.assertIn("cards-theme-", gen)
        explorer_js = (REPO / "static" / "field-pack" / "js" / "cards-explorer.js").read_text(encoding="utf-8")
        self.assertIn("openPrimaryAll", explorer_js)
        self.assertIn("requestAnimationFrame", explorer_js)
        self.assertIn('aria-pressed") === "true"', explorer_js)

    def test_nav_pairs_with_places_and_start(self):
        self.assertIn('href="/start/"', self.html)
        self.assertIn('class="shell-start"', self.html)
        self.assertIn('class="shell-brand" href="/start/"', self.html)
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
        self.assertIn("Look something up.", chapter)
        self.assertNotIn("Sample Animal", chapter)
        self.assertIn("Open a card:", chapter)
        self.assertIn('href="/field-pack/cards/"', chapter)
        self.assertIn(">All cards</a>", chapter)
        self.assertNotIn('class="start-pill" href="/field-pack/cards/">Cards</a>', chapter)
        self.assertIn('href="/field-pack/cards/african-lion/"', chapter)
        self.assertIn('href="/field-pack/cards/african-elephant/"', chapter)
        self.assertIn('href="/field-pack/cards/reticulated-giraffe/"', chapter)
        self.assertNotIn("/field-pack/dallas-zoo/", chapter)
        self.assertNotIn('id="door-teaching"', self.start)

    def test_giraffe_short_path_redirects_to_reticulated(self):
        dest = "/field-pack/cards/reticulated-giraffe/"
        self.assertEqual(CARD_ALIAS_REDIRECTS["/field-pack/cards/giraffe/"], dest)
        self.assertEqual(CARD_ALIAS_REDIRECTS["/field-pack/cards/giraffe"], dest)
        for path in ("/field-pack/cards/giraffe/", "/field-pack/cards/giraffe"):
            h = FakeHandler(path)
            h.do_GET()
            self.assertEqual(h._code, 301, path)
            self.assertEqual(h._headers.get("Location"), dest, path)
        alias = Path(GIRAFFE).parent.parent / "giraffe" / "index.html"
        self.assertTrue(alias.is_file())
        html = alias.read_text(encoding="utf-8")
        self.assertIn('rel="canonical" href="https://kidzookit.com/field-pack/cards/reticulated-giraffe/"', html)
        self.assertIn('content="0;url=/field-pack/cards/reticulated-giraffe/"', html)
        self.assertIn("location.replace(", html)
        self.assertIn("/field-pack/cards/reticulated-giraffe/", html)
        self.assertNotIn("card-page", html)
        self.assertNotIn('data-card-id="giraffe"', self.html)


if __name__ == "__main__":
    unittest.main()
