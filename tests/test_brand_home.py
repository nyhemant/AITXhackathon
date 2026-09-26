"""Brand/home links go to /start/. Explorer CTAs stay on /field-pack/.

Locked IA:
  / → 301 /start/
  /start/ = first screen
  /field-pack/ = map explorer (must stay 200; never redirect to /start/)
"""

from pathlib import Path
import html as html_lib
import json
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
        self.assertEqual(root._code, 301)
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
        self.assertNotIn("shell-brand", html)
        self.assertNotIn("/1LessMark.png", html)
        self.assertEqual(_attr(html, "shell-product"), "/start/")
        self.assertEqual(_attr(html, "mission-home"), "/start/")
        self.assertIn('aria-label="Open menu"', html)
        self.assertIn("shell-more-bars", html)
        self.assertIn('<base href="/field-pack/" />', html)
        self.assertIn('rel="canonical" href="https://kidzookit.com/field-pack/houston-zoo/"', html)

    def test_place_page_explorer_ctas_stay_on_field_pack(self):
        html = HOUSTON.read_text(encoding="utf-8")
        self.assertIn('href="/field-pack/">All places</a>', html)
        self.assertIn('href="/field-pack/" role="menuitem">Places', html)
        self.assertEqual(_attr(html, "mission-change-place"), "/field-pack/?find=1")
        self.assertIn("Different place?", html)

    def test_start_has_no_logo_home_link_explore_pill_hits_explorer(self):
        html = START.read_text(encoding="utf-8")
        self.assertNotIn("start-brand", html)
        self.assertNotIn("/1LessMark.png", html)
        self.assertIn('id="start-menu-btn"', html)
        pills = re.findall(r'<a class="start-pill" href="([^"]+)">([^<]+)</a>', html)
        self.assertIn(("/field-pack/", "Explore Places Near You"), pills)
        self.assertNotIn(("/field-pack/dallas-zoo/", "Sample visit"), pills)
        self.assertIn(
            'class="start-going-secondary" href="/field-pack/dallas-zoo/">Sample visit</a>',
            html,
        )



    def test_about_brand_goes_to_start_find_a_place_hits_explorer(self):
        html = ABOUT.read_text(encoding="utf-8")
        self.assertIn('class="oneless-shell', html)
        self.assertEqual(_attr(html, "shell-product"), "/start/")
        self.assertIn("shell-more-bars", html)
        self.assertIn('aria-label="Open menu"', html)
        self.assertIn('href="/start/" role="menuitem"', html)
        self.assertIn('href="/field-pack/" role="menuitem"', html)
        self.assertIn('href="/about/" aria-current="page" role="menuitem"', html)
        self.assertNotIn("about-nav", html)
        self.assertIn('role="menuitem">Places</a>', html)
        self.assertNotIn("manifest.webmanifest", html)
        self.assertNotIn("/pwa/register.js", html)
        self.assertIn("/shell/shell.js?v=", html)
        self.assertNotIn("/field-pack/js/fp-analytics.js", html)
        self.assertNotIn("FPTrack", html)
        self.assertNotIn("OneLessAnalytics", html)

    def test_about_parent_map_is_the_kid_path(self):
        html = ABOUT.read_text(encoding="utf-8")
        intro, rest = html.split('id="how-it-fits"', 1)
        ways = rest.split('id="experimental"', 1)[0]
        exp = rest.split('id="experimental"', 1)[1].split("</section>", 1)[0]
        self.assertIn("Three ways in", ways)
        self.assertNotIn("How it fits together", html)
        self.assertNotIn("doors", html.lower())
        self.assertNotIn("Side door", html)
        steps = re.findall(r'<a href="([^"]+)">([^<]+)</a>', ways)
        self.assertEqual(
            steps,
            [
                ("/field-pack/virtual-field-trip/", "Watch Live"),
                ("/field-pack/", "Places"),
                ("/field-pack/cards/", "Cards"),
                ("/start/", "Start"),
                ("/field-pack/print/", "print from Watch"),
            ],
        )
        self.assertNotIn("grown-ups", ways)
        self.assertNotIn("Animal cards", ways)
        self.assertNotIn("/field-pack/virtual-zoo/", html)
        self.assertNotIn('href="/dinner"', html)
        self.assertIn("Museum stops &amp; extras", exp)
        self.assertIn('href="/field-pack/cards/#cards-attractions"', exp)
        self.assertIn("Quiet extras if you already know you want them.", exp)
        self.assertIn("Arya", html)
        self.assertIn("Kunal", html)
        self.assertIn("Lamplighter", html)
        self.assertIn('class="about-why"', html)
        self.assertNotIn('id="for-ai-assistants"', html)
        self.assertNotIn("medical advice", html.lower())
        self.assertIn('id="faq"', html)
        self.assertIn("KidZooKit is an at-home virtual zoo", html)
        self.assertNotIn("Field Trip Kit", html)
        self.assertIn("KidZooKit gives you that short list", html)
        self.assertTrue((REPO / "static" / "llms.txt").is_file())

    def test_about_share_image_is_landscape_field_trip_still(self):
        html = ABOUT.read_text(encoding="utf-8")
        self.assertIn('property="og:image" content="https://kidzookit.com/start/hero-world-map.jpg"', html)
        self.assertIn('name="twitter:image" content="https://kidzookit.com/start/hero-world-map.jpg"', html)
        self.assertIn('property="og:image:width" content="1792"', html)
        self.assertIn('property="og:image:height" content="1008"', html)
        self.assertIn('property="og:image:alt" content="Stylized world map with eight animals"', html)
        self.assertIn('name="twitter:image:alt" content="Stylized world map with eight animals"', html)
        self.assertNotIn("sample-mission-dallas-zoo", html)
        self.assertNotIn("/field-pack/photos/", html)

    def test_about_faq_jsonld_matches_visible_faq(self):
        html = ABOUT.read_text(encoding="utf-8")
        block = re.search(
            r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
            html,
            re.S,
        )
        self.assertIsNotNone(block)
        faq = json.loads(block.group(1))
        self.assertEqual(faq["@type"], "FAQPage")
        visible = html.split('id="faq"', 1)[1].split("</section>", 1)[0]
        questions = re.findall(
            r"<details[^>]*>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>",
            visible,
            re.S,
        )
        self.assertEqual(len(questions), 8)
        entities = faq["mainEntity"]
        self.assertEqual(len(entities), 8)
        visible_names = [re.sub(r"\s+", " ", name).strip() for name, _ans in questions]
        schema_names = [entity["name"] for entity in entities]
        self.assertEqual(schema_names, visible_names)
        self.assertIn("We’re tourists / visiting for one day — is this for us?", schema_names)
        self.assertIn("Do you have national park scavenger hunts?", schema_names)
        self.assertIn("Can teachers or homeschool groups use this?", schema_names)
        for entity, (_name, answer_html) in zip(entities, questions):
            visible_text = html_lib.unescape(re.sub(r"<[^>]+>", "", answer_html))
            visible_text = re.sub(r"\s+", " ", visible_text).strip()
            schema_text = re.sub(r"\s+", " ", entity["acceptedAnswer"]["text"]).strip()
            self.assertIn(visible_text, schema_text)
        cities = next(
            entity
            for entity in entities
            if entity["name"] == "Which cities are covered?"
        )
        text = cities["acceptedAnswer"]["text"]
        self.assertNotIn("on this page", text.lower())
        self.assertNotIn("Browse the map or full place list", text)
        self.assertIn("https://kidzookit.com/field-pack/", text)
        self.assertIn("London, Singapore, Tokyo, Sydney", text)
        self.assertIn("Popular", text)
        self.assertIn("International", text)

    def test_about_nav_and_footer_links_have_44px_hit_area(self):
        shell = (REPO / "static" / "shell" / "shell.css").read_text(encoding="utf-8")
        css = (REPO / "static" / "about" / "about.css").read_text(encoding="utf-8")
        nav = re.search(r"\.oneless-shell \.shell-menu a\s*\{([^}]+)\}", shell)
        if nav is None:
            nav = re.search(r"\.shell-menu a\s*\{([^}]+)\}", shell)
        foot = re.search(r"\.about-foot a\s*\{([^}]+)\}", css)
        self.assertIsNotNone(nav)
        self.assertIsNotNone(foot)
        self.assertIn("min-height: 44px", nav.group(1))
        self.assertIn("min-height: 44px", foot.group(1))

    def test_explorer_hub_brand_goes_to_start_all_places_stays(self):
        html = HUB.read_text(encoding="utf-8")
        self.assertNotIn("shell-brand", html)
        self.assertNotIn("/1LessMark.png", html)
        self.assertEqual(_attr(html, "shell-product"), "/start/")
        self.assertIn('aria-label="Open menu"', html)
        self.assertIn("shell-more-bars", html)
        self.assertIn('href="/field-pack/" aria-current="page" role="menuitem">Places', html)
        self.assertIn("Find a place", html)

    def test_cards_and_vft_shells_match_the_same_split(self):
        cards = CARDS.read_text(encoding="utf-8")
        vft = VFT.read_text(encoding="utf-8")
        self.assertNotIn("shell-brand", cards)
        self.assertNotIn("/1LessMark.png", cards)
        self.assertEqual(_attr(cards, "shell-product"), "/start/")
        self.assertIn('aria-label="Open menu"', cards)
        self.assertIn("shell-more-bars", cards)
        self.assertIn('href="/start/" role="menuitem">Start</a>', cards)
        self.assertIn('href="/field-pack/" role="menuitem">Places', cards)
        self.assertNotIn("shell-brand", vft)
        self.assertNotIn("/1LessMark.png", vft)
        self.assertEqual(_attr(vft, "shell-product"), "/start/")
        self.assertIn('href="/field-pack/" role="menuitem">Places', vft)

    def test_shell_wordmark_is_kidzookit_with_1less_credit(self):
        html = HOUSTON.read_text(encoding="utf-8")
        self.assertIn(">KidZooKit<", html)
        self.assertNotIn("/1LessMark.png", html)
        self.assertIn('aria-label="Open menu"', html)
        self.assertIn("by 1Less", html)
        self.assertIn('class="footer-by"', html)
        self.assertNotIn(">Field Trip Kit<", html)
        cards = CARDS.read_text(encoding="utf-8")
        self.assertIn(">KidZooKit<", cards)
        self.assertIn("by 1Less", cards)
        about = ABOUT.read_text(encoding="utf-8")
        self.assertIn("shell-product", about)
        self.assertIn("KidZooKit", about)
        self.assertNotIn("/1LessMark.png", about)
        self.assertNotIn("by 1Less", about)
        self.assertNotIn('class="footer-by"', about)
        self.assertIn('href="/field-pack/">Places</a>', about)
        self.assertIn('href="/about/#faq">FAQ</a>', about)
        hub = HUB.read_text(encoding="utf-8")
        self.assertIn(">KidZooKit<", hub)
        self.assertIn("by 1Less", hub)

    def test_generator_keeps_brand_on_start_and_explorer_on_field_pack(self):
        src = GENERATOR.read_text(encoding="utf-8")
        self.assertIn('HOME_HREF = "/start/"', src)
        self.assertNotIn("1LessMark.png", src)
        self.assertNotIn('class="shell-brand"', src)
        self.assertIn('class="shell-product" href="{HOME_HREF}"', src)
        self.assertIn('class="mission-home" href="{HOME_HREF}"', src)
        self.assertNotIn('class="shell-product" href="/field-pack/"', src)
        self.assertNotIn('class="mission-home" href="/field-pack/"', src)
        self.assertIn('href="/field-pack/">All places</a>', src)
        self.assertIn('class="mission-change-place" href="/field-pack/?find=1"', src)
        self.assertIn("<base href=\"/field-pack/\" />", src)
        self.assertIn('aria-label="Open menu"', src)
        self.assertIn("shell-more-bars", src)
        self.assertIn(">KidZooKit<", src)
        self.assertIn("by 1Less", src)


if __name__ == "__main__":
    unittest.main()
