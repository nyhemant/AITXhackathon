"""Brand/home links go to /start/. Explorer CTAs stay on /field-pack/.

Locked IA:
  / → 302 /start/
  /start/ = first screen
  /field-pack/ = map explorer (must stay 200; never redirect to /start/)
"""

from pathlib import Path
import re
import unittest

from busyparent_agent.web import FIELD_PACK_PREFIX, START_PREFIX, WebHandler


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
START = REPO / "static" / "start" / "index.html"
ABOUT = REPO / "static" / "about" / "index.html"
HOUSTON = FP / "houston-zoo" / "index.html"
HUB = FP / "index.html"
CARDS = FP / "cards" / "index.html"
VFT = FP / "virtual-field-trip" / "index.html"
GENERATOR = REPO / "scripts" / "generate_bdo_seo.py"


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


def _attr(html: str, cls: str, attr: str = "href") -> str:
    m = re.search(rf'<a class="{cls}"[^>]*{attr}="([^"]+)"', html)
    assert m, f"missing a.{cls} {attr}"
    return m.group(1)


class BrandHomeTests(unittest.TestCase):
    def test_root_redirects_to_start_not_explorer(self):
        root = _get("/")
        self.assertEqual(root._code, 302)
        self.assertEqual(root._headers.get("Location"), START_PREFIX + "/")
        self.assertNotEqual(root._headers.get("Location"), FIELD_PACK_PREFIX + "/")

    def test_field_pack_explorer_stays_200_no_start_redirect(self):
        explorer = _get("/field-pack/")
        self.assertEqual(explorer._code, 200)
        self.assertIsNone(explorer._headers.get("Location"))
        body = explorer.wfile.getvalue()
        self.assertIn(b"landing-hub", body)
        self.assertIn(b'id="us-map"', body)
        self.assertIn(b"Find a place", body)

    def test_place_page_logo_and_title_go_to_start(self):
        html = HOUSTON.read_text(encoding="utf-8")
        self.assertEqual(_attr(html, "shell-brand"), "/start/")
        self.assertEqual(_attr(html, "shell-product"), "/start/")
        self.assertEqual(_attr(html, "mission-home"), "/start/")
        self.assertIn('aria-label="Field Trip Kit home"', html)
        self.assertIn('<base href="/field-pack/" />', html)
        self.assertIn('rel="canonical" href="https://1less.app/field-pack/houston-zoo/"', html)

    def test_place_page_explorer_ctas_stay_on_field_pack(self):
        html = HOUSTON.read_text(encoding="utf-8")
        self.assertIn('href="/field-pack/">All places</a>', html)
        self.assertIn('href="/field-pack/" role="menuitem">All places', html)
        self.assertEqual(_attr(html, "mission-change-place"), "/field-pack/?find=1")
        self.assertIn("Different place?", html)

    def test_start_brand_stays_on_start_explore_pill_hits_explorer(self):
        html = START.read_text(encoding="utf-8")
        self.assertEqual(_attr(html, "start-brand"), "/start/")
        pills = re.findall(r'<a class="start-pill" href="([^"]+)">([^<]+)</a>', html)
        self.assertIn(("/field-pack/", "Explore Places Near You"), pills)

    def test_about_brand_goes_to_start_find_a_place_hits_explorer(self):
        html = ABOUT.read_text(encoding="utf-8")
        self.assertEqual(_attr(html, "about-brand"), "/start/")
        self.assertIn('href="/field-pack/">Find a place</a>', html)

    def test_explorer_hub_brand_goes_to_start_all_places_stays(self):
        html = HUB.read_text(encoding="utf-8")
        self.assertEqual(_attr(html, "shell-brand"), "/start/")
        self.assertEqual(_attr(html, "shell-product"), "/start/")
        self.assertIn('href="/field-pack/" aria-current="page" role="menuitem">All places', html)
        self.assertIn("Find a place", html)

    def test_cards_and_vft_shells_match_the_same_split(self):
        cards = CARDS.read_text(encoding="utf-8")
        vft = VFT.read_text(encoding="utf-8")
        self.assertEqual(_attr(cards, "shell-brand"), "/start/")
        self.assertEqual(_attr(cards, "shell-product"), "/start/")
        self.assertIn('href="/field-pack/">Places</a>', cards)
        self.assertIn('href="/field-pack/" role="menuitem">All places', cards)
        self.assertEqual(_attr(vft, "shell-brand"), "/start/")
        self.assertEqual(_attr(vft, "shell-product"), "/start/")
        self.assertIn('href="/field-pack/" role="menuitem">All places', vft)

    def test_generator_keeps_brand_on_start_and_explorer_on_field_pack(self):
        src = GENERATOR.read_text(encoding="utf-8")
        self.assertIn('HOME_HREF = "/start/"', src)
        self.assertIn('class="shell-brand" href="{HOME_HREF}"', src)
        self.assertIn('class="shell-product" href="{HOME_HREF}"', src)
        self.assertIn('class="mission-home" href="{HOME_HREF}"', src)
        self.assertNotIn('class="shell-brand" href="/field-pack/"', src)
        self.assertNotIn('class="shell-product" href="/field-pack/"', src)
        self.assertNotIn('class="mission-home" href="/field-pack/"', src)
        self.assertIn('href="/field-pack/">All places</a>', src)
        self.assertIn('class="mission-change-place" href="/field-pack/?find=1"', src)
        self.assertIn("<base href=\"/field-pack/\" />", src)


if __name__ == "__main__":
    unittest.main()
