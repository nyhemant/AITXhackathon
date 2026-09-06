"""First-time landing at /start/ — does not replace the live home."""

from pathlib import Path
import re
import unittest

from busyparent_agent.web import (
    ABOUT_PREFIX,
    FIELD_PACK_PREFIX,
    START_PREFIX,
    WebHandler,
    _safe_about_path,
    _safe_field_pack_path,
    _safe_start_path,
)


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
START = REPO / "static" / "start"
HOME = FP / "index.html"
START_HTML = START / "index.html"
GIRAFFE = FP / "cards" / "reticulated-giraffe" / "index.html"
DALLAS = FP / "dallas-zoo" / "index.html"


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


def _heading_text(html: str) -> str:
    h1 = re.search(r"<h1[^>]*id=\"start-heading\"[^>]*>([\s\S]*?)</h1>", html)
    assert h1, "missing #start-heading"
    return re.sub(r"\s+", " ", h1.group(1)).strip()


class StartLandingTests(unittest.TestCase):
    def setUp(self):
        self.html = START_HTML.read_text(encoding="utf-8")
        self.css = (START / "start.css").read_text(encoding="utf-8")
        self.js = (START / "start.js").read_text(encoding="utf-8")
        self.home = HOME.read_text(encoding="utf-8")
        self.pills = re.findall(r'<a class="start-pill"[^>]*>[\s\S]*?</a>', self.html)

    def test_route_is_start_not_home(self):
        root = _get("/")
        self.assertEqual(root._code, 302)
        self.assertEqual(root._headers.get("Location"), START_PREFIX + "/")

        home = _get("/field-pack/")
        self.assertEqual(home._code, 200)
        self.assertIn(b'id="us-map"', home.wfile.getvalue())
        self.assertIn(b"landing-hub", home.wfile.getvalue())
        self.assertNotIn(b"landing-pitch-t4b", home.wfile.getvalue())

        slashless = _get("/start")
        self.assertEqual(slashless._code, 301)
        self.assertEqual(slashless._headers.get("Location"), START_PREFIX + "/")

        start = _get("/start/")
        self.assertEqual(start._code, 200)
        body = start.wfile.getvalue().decode("utf-8")
        self.assertIn("Wildlife wonder, ready for curious kids.", body)
        self.assertIn('class="start-brand" href="/start/"', body)
        self.assertIn('aria-label="1less home"', body)
        self.assertIn('id="start-menu-btn"', body)
        self.assertIn("Print cutouts to hide", body)
        self.assertIn("Library", body)
        self.assertIn("/field-pack/virtual-zoo/?print=1", body)
        self.assertNotIn(">Field Trip Kit</span>", body)
        self.assertIn("Watch Live", body)
        self.assertNotIn("I need an activity for today", body)
        self.assertIsNotNone(_safe_start_path("/start/"))
        self.assertIsNotNone(_safe_start_path("/start/start.css"))
        self.assertIsNotNone(_safe_start_path("/start/home-print-table.jpg"))
        self.assertIsNotNone(_safe_start_path("/start/teasers/flamingo.mp4"))
        self.assertIsNotNone(_safe_start_path("/start/teasers/giraffe.mp4"))
        self.assertIsNotNone(_safe_start_path("/start/teasers/lion.mp4"))
        self.assertIsNotNone(_safe_start_path("/start/teasers/otter.mp4"))
        self.assertIsNotNone(_safe_start_path("/start/going-giraffe.jpg"))
        self.assertIsNotNone(_safe_start_path("/start/teach-card.jpg"))
        self.assertIsNotNone(_safe_start_path("/start/teach-lion.jpg"))
        self.assertIsNotNone(_safe_start_path("/start/teach-elephant.jpg"))
        self.assertIsNotNone(_safe_start_path("/start/teach-giraffe.jpg"))
        self.assertIsNone(_safe_start_path("/start/../field-pack/index.html"))
        self.assertIsNotNone(_safe_field_pack_path("/field-pack/"))

        about_slash = _get("/about")
        self.assertEqual(about_slash._code, 301)
        self.assertEqual(about_slash._headers.get("Location"), ABOUT_PREFIX + "/")
        about = _get("/about/")
        self.assertEqual(about._code, 200)
        self.assertIn("About · Field Trip Kit · 1Less", about.wfile.getvalue().decode("utf-8"))
        self.assertIsNotNone(_safe_about_path("/about/"))
        self.assertIsNotNone(_safe_about_path("/about/about.css"))
        self.assertIsNone(_safe_about_path("/about/../field-pack/index.html"))

        still = _get("/start/home-print-table.jpg")
        self.assertEqual(still._code, 200)
        self.assertTrue(still.wfile.getvalue().startswith(b"\xff\xd8"))

        teaser = _get("/start/teasers/flamingo.mp4")
        self.assertEqual(teaser._code, 200)
        self.assertTrue(teaser.wfile.getvalue()[4:8] == b"ftyp" or teaser.wfile.getvalue().startswith(b"\x00\x00"))

        going = _get("/start/going-giraffe.jpg")
        self.assertEqual(going._code, 200)
        self.assertTrue(going.wfile.getvalue().startswith(b"\xff\xd8"))

        teach = _get("/start/teach-card.jpg")
        self.assertEqual(teach._code, 200)
        self.assertTrue(teach.wfile.getvalue().startswith(b"\xff\xd8"))

        for panel in ("teach-lion.jpg", "teach-elephant.jpg", "teach-giraffe.jpg"):
            panel_res = _get(f"/start/{panel}")
            self.assertEqual(panel_res._code, 200, panel)
            self.assertTrue(panel_res.wfile.getvalue().startswith(b"\xff\xd8"), panel)

    def test_hero_is_local_giraffe_still(self):
        hero = re.search(r'<section class="start-hero"[\s\S]*?</section>', self.html)
        self.assertIsNotNone(hero)
        chapter = hero.group(0)
        self.assertLess(self.html.find('id="start-hero"'), self.html.find('id="start-home"'))
        self.assertIn('id="start-heading"', chapter)
        self.assertIn("Wildlife wonder, ready for curious kids.", chapter)
        self.assertIn('class="start-routes"', chapter)
        self.assertIn('href="#start-home"', chapter)
        self.assertIn('href="#start-going"', chapter)
        self.assertIn('href="#start-teach"', chapter)
        self.assertIn('class="start-hero-still"', chapter)
        self.assertIn('src="/start/hero-giraffe.jpg"', chapter)
        self.assertIn("srcset=", chapter)
        self.assertIn("/start/hero-giraffe-480.jpg 480w", chapter)
        self.assertIn("/start/hero-giraffe-640.jpg 640w", chapter)
        self.assertIn("/start/hero-giraffe.jpg 896w", chapter)
        self.assertIn('width="896"', chapter)
        self.assertIn('height="1136"', chapter)
        self.assertNotIn("http://", chapter)
        self.assertNotIn("https://", chapter)
        self.assertNotIn("I need an activity for today", chapter)
        self.assertNotIn("Free · No account · At home or on location", chapter)
        self.assertNotIn("At home or before you go.", chapter)
        self.assertNotIn("us-map", chapter)
        self.assertNotIn("start-door", chapter)
        self.assertTrue((START / "hero-giraffe.jpg").is_file())
        self.assertTrue((START / "hero-giraffe-640.jpg").is_file())
        self.assertTrue((START / "hero-giraffe-480.jpg").is_file())
        self.assertIn("object-fit: cover", self.css)
        self.assertIn("object-position: 52% 28%", self.css)
        self.assertIn("100svh", self.css)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertNotIn("webgl", self.css.lower())
        self.assertNotIn("parallax", self.css.lower())

    def test_hero_has_quiet_chapter_routes(self):
        hero = re.search(r'<section class="start-hero"[\s\S]*?</section>', self.html)
        self.assertIsNotNone(hero)
        chapter = hero.group(0)
        nav = re.search(r'<nav class="start-routes"[^>]*>([\s\S]*?)</nav>', chapter)
        self.assertIsNotNone(nav)
        self.assertIn('aria-label="Choose a path"', nav.group(0))
        routes = re.findall(r'<a class="start-route" href="([^"]+)">([^<]+)</a>', chapter)
        self.assertEqual(
            routes,
            [
                ("#start-home", "At home"),
                ("#start-going", "Going this week"),
                ("#start-teach", "Library"),
            ],
        )
        self.assertLess(chapter.find("start-heading"), chapter.find("start-routes"))
        self.assertEqual(self.html.count('class="start-route"'), 3)
        self.assertNotIn("start-pill", chapter)
        routes_html = nav.group(0)
        self.assertNotIn("Watch Live", routes_html)
        self.assertNotIn("Print cutouts to hide", routes_html)
        self.assertIn("Print cutouts to hide", chapter)
        self.assertIn('id="start-menu-btn"', chapter)
        self.assertIn(".start-routes", self.css)
        self.assertIn(".start-route", self.css)
        self.assertIn("scroll-margin-top", self.css)
        self.assertIn("min-height: 8vh", self.css)
        self.assertIn("min-height: 5vh", self.css)

    def test_home_chapter_is_local_print_table(self):
        home = re.search(r'<section class="start-chapter"[\s\S]*?</section>', self.html)
        self.assertIsNotNone(home)
        chapter = home.group(0)
        self.assertLess(self.html.find('id="start-hero"'), self.html.find('id="start-rest"'))
        self.assertLess(self.html.find('id="start-rest"'), self.html.find('id="start-home"'))
        self.assertLess(self.html.find('id="start-home"'), self.html.find('id="start-rest-2"'))
        self.assertLess(self.html.find('id="start-rest-2"'), self.html.find('id="start-going"'))
        self.assertLess(self.html.find('id="start-going"'), self.html.find('id="start-rest-3"'))
        self.assertLess(self.html.find('id="start-rest-3"'), self.html.find('id="start-teach"'))
        self.assertLess(self.html.find('id="start-teach"'), self.html.find('start-foot'))
        self.assertIn("At home this afternoon", chapter)
        self.assertIn("The cam is on. An hour at home.", chapter)
        self.assertIn("Watch live — or print, cut, hide.", chapter)
        self.assertIn('class="start-chapter-still"', chapter)
        self.assertIn('src="/start/home-print-table.jpg"', chapter)
        self.assertIn("srcset=", chapter)
        self.assertIn("/start/home-print-table-480.jpg 480w", chapter)
        self.assertIn("/start/home-print-table-640.jpg 640w", chapter)
        self.assertIn("/start/home-print-table.jpg 1024w", chapter)
        self.assertIn('width="1024"', chapter)
        self.assertIn('height="1536"', chapter)
        self.assertIn("animal cards", chapter.lower())
        self.assertNotIn("home-laptop-teaser", chapter)
        self.assertNotIn("print sheet", chapter.lower())
        self.assertNotIn("Open Dallas Zoo", chapter)
        self.assertNotIn('href="/field-pack/dallas-zoo/"', chapter)
        self.assertIn('class="start-chapter-hit"', chapter)
        self.assertIn('class="start-home-tease"', chapter)
        self.assertIn('class="start-home-screen"', chapter)
        self.assertIn('class="start-home-video"', chapter)
        self.assertIn('class="start-home-continue"', chapter)
        self.assertIn("muted", chapter)
        self.assertIn("playsinline", chapter)
        self.assertIn(">Continue<", chapter)
        hit = re.search(r'<a class="start-chapter-hit"[^>]*>[\s\S]*?</a>', chapter)
        self.assertIsNotNone(hit)
        self.assertIn('href="/field-pack/virtual-field-trip/"', hit.group(0))
        continue_link = re.search(r'<a class="start-home-continue"[^>]*>', chapter)
        self.assertIsNotNone(continue_link)
        self.assertIn('href="/field-pack/virtual-field-trip/"', continue_link.group(0))
        pills = re.findall(r'<a class="start-pill"[^>]*>[\s\S]*?</a>', chapter)
        self.assertEqual(len(pills), 2, pills)
        self.assertIn('href="/field-pack/virtual-field-trip/"', pills[0])
        self.assertIn("Watch Live", pills[0])
        self.assertIn('href="/field-pack/virtual-zoo/?print=1"', pills[1])
        self.assertIn("Print cutouts to hide", pills[1])
        self.assertNotIn("youtube.com", chapter)
        self.assertNotIn("target=\"_blank\"", chapter)
        self.assertNotIn("#mission", chapter)
        self.assertNotIn("#print", chapter)
        self.assertNotIn("http://", chapter)
        self.assertNotIn("https://", chapter)
        self.assertNotIn("I need an activity for today", chapter)
        self.assertNotIn("Free · No account · At home or on location", chapter)
        self.assertNotIn("At home or before you go.", chapter)
        self.assertNotIn("start-door", chapter)
        self.assertNotIn("us-map", chapter)
        self.assertTrue((START / "home-print-table.jpg").is_file())
        self.assertTrue((START / "home-print-table-640.jpg").is_file())
        self.assertTrue((START / "home-print-table-480.jpg").is_file())
        self.assertIn(".start-chapter", self.css)
        self.assertIn("object-position: 50% 38%", self.css)
        self.assertIn("#start-home .start-chapter-still", self.css)
        self.assertIn("object-position: 36% 24%", self.css)
        self.assertIn("object-position: 12% 22%", self.css)
        self.assertIn("framePlate", self.js)
        self.assertIn("fitHotboxPosition", self.js)
        self.assertIn("isMobilePortrait", self.js)
        self.assertIn(".start-home-screen", self.css)
        self.assertIn("8.20% 20.57%", self.css)
        self.assertIn("matrix3d", self.js)
        self.assertIn("fp-start-teaser-seen-v1", self.js)
        self.assertIn("/start/teasers/flamingo.mp4", self.js)
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertNotIn("webgl", self.css.lower())
        self.assertNotIn("parallax", self.css.lower())
        self.assertNotIn("youtube.com", chapter)
        self.assertNotIn("youtube-nocookie.com", chapter)
        self.assertNotIn("<iframe", chapter)

    def test_three_empty_cream_rests(self):
        rests = re.findall(r'<div class="start-rest"[^>]*>\s*</div>', self.html)
        self.assertEqual(len(rests), 3)
        self.assertIn('id="start-rest"', rests[0])
        self.assertIn('id="start-rest-2"', rests[1])
        self.assertIn('id="start-rest-3"', rests[2])
        for rest in rests:
            self.assertIn('aria-hidden="true"', rest)
            self.assertNotIn("At home this afternoon", rest)
            self.assertNotIn("Going this week", rest)
            self.assertNotIn("Teaching a group", rest)
            self.assertNotIn(">Teaching<", rest)
            self.assertNotIn("Open Dallas Zoo", rest)
            self.assertNotIn("start-door", rest)
            self.assertNotIn("<img", rest)
            self.assertNotIn("<a", rest)
        self.assertLess(self.html.find('id="start-hero"'), self.html.find('id="start-rest"'))
        self.assertLess(self.html.find('id="start-rest"'), self.html.find('id="start-home"'))
        self.assertLess(self.html.find('id="start-home"'), self.html.find('id="start-rest-2"'))
        self.assertLess(self.html.find('id="start-rest-2"'), self.html.find('id="start-going"'))
        self.assertLess(self.html.find('id="start-going"'), self.html.find('id="start-rest-3"'))
        self.assertLess(self.html.find('id="start-rest-3"'), self.html.find('id="start-teach"'))
        self.assertEqual(self.html.count('class="start-rest"'), 3)
        self.assertEqual(self.html.count('class="start-chapter"'), 3)
        self.assertIn("min-height: 8vh", self.css)
        self.assertIn("min-height: 5vh", self.css)
        self.assertNotIn("min-height: 16vh", self.css)
        self.assertNotIn("min-height: 42vh", self.css)
        self.assertIn("background: #f6f1ea", self.css)

    def test_going_chapter_is_local_jpeg(self):
        going = re.search(
            r'<section class="start-chapter" id="start-going"[\s\S]*?</section>',
            self.html,
        )
        self.assertIsNotNone(going)
        chapter = going.group(0)
        self.assertLess(self.html.find('id="start-home"'), self.html.find('id="start-rest-2"'))
        self.assertLess(self.html.find('id="start-rest-2"'), self.html.find('id="start-going"'))
        self.assertLess(self.html.find('id="start-going"'), self.html.find('id="start-rest-3"'))
        self.assertLess(self.html.find('id="start-rest-3"'), self.html.find('id="start-teach"'))
        self.assertIn("Going this week", chapter)
        self.assertIn("Same animal. Real place.", chapter)
        self.assertIn("Hunt page in hand.", chapter)
        self.assertNotIn("Giraffe already checked.", chapter)
        self.assertIn('class="start-chapter-still"', chapter)
        self.assertIn('src="/start/going-giraffe.jpg"', chapter)
        self.assertIn("srcset=", chapter)
        self.assertIn("/start/going-giraffe-480.jpg 480w", chapter)
        self.assertIn("/start/going-giraffe-640.jpg 640w", chapter)
        self.assertIn("/start/going-giraffe.jpg 1024w", chapter)
        self.assertIn('width="1024"', chapter)
        self.assertIn('height="1536"', chapter)
        self.assertIn("mission page", chapter.lower())
        self.assertIn("reticulated giraffe", chapter.lower())
        self.assertIn("start-going-hit", chapter)
        hit = re.search(r'<a class="start-chapter-hit start-going-hit"[^>]*>[\s\S]*?</a>', chapter)
        self.assertIsNotNone(hit)
        self.assertIn('href="/field-pack/dallas-zoo/"', hit.group(0))
        self.assertIn('src="/start/going-giraffe.jpg"', hit.group(0))
        self.assertNotIn("Explore zoos", hit.group(0))
        self.assertNotIn("Explore aquariums", hit.group(0))
        self.assertIn("Going this week", chapter)
        self.assertIn("Same animal. Real place.", chapter)
        self.assertIn("Hunt page in hand.", chapter)
        self.assertIn('href="/field-pack/dallas-zoo/"', chapter)
        pills = re.findall(r'<a class="start-pill"[^>]*>[\s\S]*?</a>', chapter)
        self.assertEqual(len(pills), 2, pills)
        self.assertIn('href="/field-pack/dallas-zoo/"', pills[0])
        self.assertIn("Sample visit", pills[0])
        self.assertIn('href="/field-pack/"', pills[1])
        self.assertIn("Explore Places Near You", pills[1])
        slides = re.findall(r'<a class="start-going-slide"[^>]*href="([^"]+)"', chapter)
        self.assertEqual(
            slides,
            [
                "/field-pack/georgia-aquarium/",
                "/field-pack/dallas-zoo/",
                "/field-pack/san-diego-zoo/",
            ],
        )
        self.assertIn('class="start-going-carousel"', chapter)
        self.assertIn('id="start-going-track"', chapter)
        self.assertIn('data-going-prev', chapter)
        self.assertIn('data-going-next', chapter)
        self.assertIn('aria-label="Previous place"', chapter)
        self.assertIn('aria-label="Next place"', chapter)
        self.assertIn('src="/start/going-georgia-aquarium.jpg?v=3"', chapter)
        self.assertIn("/start/going-georgia-aquarium-480.jpg?v=3 480w", chapter)
        self.assertIn("/start/going-georgia-aquarium-640.jpg?v=3 640w", chapter)
        self.assertIn('src="/start/going-san-diego-zoo.jpg?v=2"', chapter)
        self.assertIn("/start/going-san-diego-zoo-480.jpg?v=2 480w", chapter)
        self.assertIn("/start/going-san-diego-zoo-640.jpg?v=2 640w", chapter)
        self.assertIn(
            "child holding Georgia Aquarium hunt sheet with octopus behind",
            chapter,
        )
        self.assertNotIn("whale shark", chapter.lower())
        self.assertNotIn("Ocean Voyager", chapter)
        self.assertIn(
            "child holding San Diego Zoo hunt sheet with panda/bamboo behind",
            chapter,
        )
        self.assertIn("going-georgia-locked-octopus.jpg", chapter)
        self.assertIn("going-san-diego-locked-v2.jpg", chapter)
        self.assertNotIn("start-going-slide-name", chapter)
        self.assertNotIn('href="/field-pack/zoos/"', chapter)
        self.assertNotIn('href="/field-pack/aquariums/"', chapter)
        self.assertNotIn("Explore zoos", chapter)
        self.assertNotIn("Explore aquariums", chapter)
        self.assertNotIn("Open Dallas Zoo", chapter)
        self.assertNotIn('href="/field-pack/dallas-zoo/"', self.js)
        self.assertNotIn('href="/field-pack/georgia-aquarium/"', self.js)
        self.assertNotIn('href="/field-pack/san-diego-zoo/"', self.js)
        self.assertNotIn(".start-chapter-link", self.js)
        self.assertNotIn("#start-going", self.js)
        self.assertIn("start-going-track", self.js)
        self.assertIn("data-going-prev", self.js)
        self.assertIn("data-going-next", self.js)
        self.assertIn("startIndex = 1", self.js)
        self.assertIn("pinStart", self.js)
        self.assertIn("scrollTo", self.js)
        self.assertIn("window.location.href", self.js)
        self.assertIn("slideHref", self.js)
        reveal = re.search(r"function reveal\(\) \{([\s\S]*?)\n    \}", self.js)
        self.assertIsNotNone(reveal)
        self.assertLess(reveal.group(1).find("carousel.hidden = false"), reveal.group(1).find("pinStart"))
        self.assertNotIn("#mission", chapter)
        self.assertNotIn("#print", chapter)
        self.assertNotIn("http://", chapter)
        self.assertNotIn("https://", chapter)
        self.assertNotIn("I need an activity for today", chapter)
        self.assertNotIn("Free · No account · At home or on location", chapter)
        self.assertNotIn("At home or before you go.", chapter)
        self.assertNotIn("start-door", chapter)
        self.assertNotIn("us-map", chapter)
        self.assertTrue((FP / "zoos" / "index.html").is_file())
        self.assertTrue((FP / "aquariums" / "index.html").is_file())
        self.assertTrue((FP / "georgia-aquarium" / "index.html").is_file())
        self.assertTrue((FP / "san-diego-zoo" / "index.html").is_file())
        self.assertTrue((START / "going-giraffe.jpg").is_file())
        self.assertTrue((START / "going-giraffe-640.jpg").is_file())
        self.assertTrue((START / "going-giraffe-480.jpg").is_file())
        self.assertTrue((START / "going-giraffe.jpg").read_bytes().startswith(b"\xff\xd8"))
        self.assertTrue((START / "going-georgia-aquarium.jpg").is_file())
        self.assertTrue((START / "going-georgia-aquarium-480.jpg").is_file())
        self.assertTrue((START / "going-georgia-aquarium-640.jpg").is_file())
        self.assertTrue((START / "going-san-diego-zoo.jpg").is_file())
        self.assertTrue((START / "going-san-diego-zoo-480.jpg").is_file())
        self.assertTrue((START / "going-san-diego-zoo-640.jpg").is_file())
        self.assertIn(".start-chapter", self.css)
        self.assertIn(".start-chapter-quiet", self.css)
        self.assertIn(".start-going-hit", self.css)
        self.assertIn(".start-going-carousel", self.css)
        self.assertIn(".start-going-slide", self.css)
        self.assertIn(".start-going-arrow", self.css)
        self.assertIn(".start-going-prev", self.css)
        self.assertIn(".start-going-next", self.css)
        self.assertIn(".start-going-slide-fallback", self.css)
        self.assertIn(".start-chapter-pills", self.css)
        self.assertIn(".start-pill", self.css)
        self.assertNotIn("webgl", self.css.lower())
        self.assertNotIn("parallax", self.css.lower())

    def test_teach_chapter_is_local_jpeg(self):
        teach = re.search(
            r'<section class="start-chapter" id="start-teach"[\s\S]*?</section>',
            self.html,
        )
        self.assertIsNotNone(teach)
        chapter = teach.group(0)
        self.assertLess(self.html.find('id="start-going"'), self.html.find('id="start-rest-3"'))
        self.assertLess(self.html.find('id="start-rest-3"'), self.html.find('id="start-teach"'))
        self.assertLess(self.html.find('id="start-teach"'), self.html.find('start-foot'))
        self.assertIn("Library", chapter)
        self.assertIn("Look something up.", chapter)
        self.assertIn("Talk, photos, Q&amp;A — on the screen.", chapter)
        self.assertIn('class="start-chapter-still"', chapter)
        self.assertIn('src="/start/teach-card.jpg"', chapter)
        self.assertIn("srcset=", chapter)
        self.assertIn("/start/teach-card-480.jpg 480w", chapter)
        self.assertIn("/start/teach-card-640.jpg 640w", chapter)
        self.assertIn("/start/teach-card.jpg 1536w", chapter)
        self.assertIn('width="1536"', chapter)
        self.assertIn('height="1024"', chapter)
        self.assertIn("A4", chapter)
        self.assertIn("printouts", chapter.lower())
        self.assertNotIn("flashcard", chapter.lower())
        self.assertNotIn('alt="African lion"', chapter)
        self.assertNotIn("lion portrait", chapter.lower())
        pills = re.findall(r'<a class="start-pill"[^>]*>[\s\S]*?</a>', chapter)
        self.assertEqual(len(pills), 1, pills)
        self.assertIn('href="/field-pack/cards/#try-a-card"', pills[0])
        self.assertIn("Browse cards", pills[0])
        self.assertNotIn("Sample Animal", chapter)
        self.assertNotIn("start-teach-hit", chapter)
        self.assertIn("Open a card:", chapter)
        self.assertIn('href="/field-pack/cards/african-lion/"', chapter)
        self.assertIn(">Lion<", chapter)
        self.assertIn('href="/field-pack/cards/african-elephant/"', chapter)
        self.assertIn(">Elephant<", chapter)
        self.assertIn('href="/field-pack/cards/reticulated-giraffe/"', chapter)
        self.assertIn(">Giraffe<", chapter)
        slides = re.findall(
            r'<a class="start-teach-slide" href="([^"]+)">',
            chapter,
        )
        self.assertEqual(
            slides,
            [
                "/field-pack/cards/african-lion/",
                "/field-pack/cards/african-elephant/",
                "/field-pack/cards/reticulated-giraffe/",
            ],
        )
        self.assertIn('src="/start/teach-lion.jpg"', chapter)
        self.assertIn('src="/start/teach-elephant.jpg"', chapter)
        self.assertIn('src="/start/teach-giraffe.jpg"', chapter)
        self.assertIn("/start/teach-lion-480.jpg 480w", chapter)
        self.assertIn("/start/teach-elephant-480.jpg 480w", chapter)
        self.assertIn("/start/teach-giraffe-480.jpg 480w", chapter)
        self.assertIn('class="start-teach-carousel"', chapter)
        self.assertIn('class="start-chapter-still"', chapter)
        self.assertNotIn("start-teach-slide-name", chapter)
        self.assertIn('data-teach-prev', chapter)
        self.assertIn('data-teach-next', chapter)
        self.assertIn('aria-label="Previous card"', chapter)
        self.assertIn('aria-label="Next card"', chapter)
        self.assertLess(chapter.find("start-chapter-box"), chapter.find("start-open-cards"))
        self.assertLess(chapter.find("start-open-cards"), chapter.find("start-chapter-pills"))
        self.assertLess(chapter.find("start-teach-carousel"), chapter.find("start-open-cards"))
        self.assertNotIn("grid-template-columns: repeat(3", chapter)
        lion = FP / "cards" / "african-lion" / "index.html"
        elephant = FP / "cards" / "african-elephant" / "index.html"
        self.assertTrue(lion.is_file())
        self.assertTrue(elephant.is_file())
        self.assertTrue(GIRAFFE.is_file())
        self.assertNotIn("/field-pack/dallas-zoo/", chapter)
        self.assertNotIn("#mission", chapter)
        self.assertNotIn("#print", chapter)
        self.assertNotIn("http://", chapter)
        self.assertNotIn("https://", chapter)
        self.assertNotIn("I need an activity for today", chapter)
        self.assertNotIn("Free · No account · At home or on location", chapter)
        self.assertNotIn("At home or before you go.", chapter)
        self.assertNotIn("start-door", chapter)
        self.assertNotIn("us-map", chapter)
        self.assertTrue((START / "teach-card.jpg").is_file())
        self.assertTrue((START / "teach-card-640.jpg").is_file())
        self.assertTrue((START / "teach-card-480.jpg").is_file())
        self.assertTrue((START / "teach-card.jpg").read_bytes().startswith(b"\xff\xd8"))
        for name in (
            "teach-lion.jpg",
            "teach-lion-480.jpg",
            "teach-elephant.jpg",
            "teach-elephant-480.jpg",
            "teach-giraffe.jpg",
            "teach-giraffe-480.jpg",
        ):
            panel = START / name
            self.assertTrue(panel.is_file(), name)
            self.assertTrue(panel.read_bytes().startswith(b"\xff\xd8"), name)
        self.assertIn(".start-chapter", self.css)
        self.assertIn(".start-chapter-quiet", self.css)
        self.assertIn(".start-teach-carousel", self.css)
        self.assertIn(".start-teach-slide", self.css)
        self.assertIn(".start-teach-arrow", self.css)
        self.assertIn(".start-teach-prev", self.css)
        self.assertIn(".start-teach-next", self.css)
        self.assertNotIn(".start-teach-slide-name", self.css)
        self.assertIn("scroll-snap-type: x mandatory", self.css)
        self.assertIn("@media (max-width: 640px)", self.css)
        self.assertIn("@media (min-width: 641px)", self.css)
        self.assertNotIn("grid-template-columns: repeat(3", self.css)
        self.assertIn("start-teach-track", self.js)
        self.assertIn("data-teach-prev", self.js)
        self.assertIn("data-teach-next", self.js)
        self.assertIn("scrollTo", self.js)
        self.assertIn('href="/field-pack/cards/#try-a-card"', chapter)
        self.assertIn("Library", chapter)
        self.assertIn('.start-pill[href^="/field-pack/cards/"]', self.js)
        self.assertIn('exploreHref', self.js)
        self.assertIn("function openExplore()", self.js)
        self.assertIn("startedAt === \"start\"", self.js)
        self.assertIn("startedAt === \"end\"", self.js)
        self.assertIn("swipePx = 80", self.js)
        self.assertIn("AUTO_MS", self.js)
        self.assertIn("startAuto", self.js)
        self.assertIn("wheelPx = 120", self.js)
        self.assertIn("class=\"start-teach-spill start-teach-spill-prev\"", chapter)
        self.assertIn("class=\"start-teach-spill start-teach-spill-next\"", chapter)
        self.assertEqual(chapter.count(">Library<"), 3)
        self.assertIn(".start-teach-spill", self.css)
        self.assertIn(".is-teach-spill-prev", self.css)
        self.assertIn(".is-teach-spill-next", self.css)
        self.assertNotIn("webgl", self.css.lower())
        self.assertNotIn("parallax", self.css.lower())

    def test_locked_headline_and_no_marketing_stats(self):
        self.assertEqual(
            _heading_text(self.html),
            "Wildlife wonder, ready for curious kids.",
        )
        self.assertNotIn("I need an activity for today", self.html)
        self.assertNotIn("We’re visiting somewhere soon", self.html)
        self.assertNotIn("I’m teaching a group", self.html)
        self.assertNotIn("Ages 4–10", self.html)
        self.assertNotIn("Ages 4-10", self.html)
        self.assertNotIn("5–20 minutes", self.html)
        self.assertNotIn("5-20 minutes", self.html)
        self.assertNotIn("218 places", self.html)
        self.assertNotIn("10,000 families", self.html)
        self.assertNotIn("testimonial", self.html.lower())

    def test_page_is_hero_chapters_and_about_footer(self):
        hero = self.html.find('id="start-hero"')
        rest = self.html.find('id="start-rest"')
        home = self.html.find('id="start-home"')
        rest2 = self.html.find('id="start-rest-2"')
        going = self.html.find('id="start-going"')
        rest3 = self.html.find('id="start-rest-3"')
        teach = self.html.find('id="start-teach"')
        foot = self.html.find("start-foot")
        self.assertTrue(0 < hero < rest < home < rest2 < going < rest3 < teach < foot)
        self.assertEqual(self.html.count('class="start-chapter"'), 3)
        self.assertEqual(len(self.pills), 5)
        self.assertNotIn('id="start-outcome"', self.html)
        self.assertNotIn('id="start-doors"', self.html)
        self.assertNotIn('id="start-proof"', self.html)
        self.assertNotIn("start-door", self.html)
        self.assertNotIn('id="door-today"', self.html)
        self.assertNotIn('id="door-visiting"', self.html)
        self.assertNotIn('id="door-teaching"', self.html)
        self.assertNotIn("I need an activity for today", self.html)
        self.assertNotIn("We’re visiting somewhere soon", self.html)
        self.assertNotIn("I’m teaching a group", self.html)

    def test_no_intent_tiles_or_youtube(self):
        self.assertEqual(len(re.findall(r'class="start-door"', self.html)), 0)
        self.assertNotIn("/field-pack/dallas-zoo/#mission", self.html)
        self.assertNotIn("/field-pack/dallas-zoo/#print", self.html)
        self.assertNotIn("youtube.com", self.html)
        self.assertNotIn("youtube-nocookie.com", self.html)
        self.assertNotIn("us-map", self.html)
        self.assertNotIn("map-host", self.html)
        self.assertTrue(DALLAS.is_file())
        self.assertIsNotNone(_safe_field_pack_path("/field-pack/dallas-zoo/"))
        self.assertEqual(self.html.count('href="/field-pack/dallas-zoo/"'), 3)
        self.assertEqual(self.html.count('href="/field-pack/georgia-aquarium/"'), 1)
        self.assertEqual(self.html.count('href="/field-pack/san-diego-zoo/"'), 1)

    def test_chapter_pills_are_locked_and_under_the_box(self):
        chapters = {
            "start-home": re.search(
                r'<section class="start-chapter" id="start-home"[\s\S]*?</section>',
                self.html,
            ),
            "start-going": re.search(
                r'<section class="start-chapter" id="start-going"[\s\S]*?</section>',
                self.html,
            ),
            "start-teach": re.search(
                r'<section class="start-chapter" id="start-teach"[\s\S]*?</section>',
                self.html,
            ),
        }
        expected = {
            "start-home": [
                ("/field-pack/virtual-field-trip/", "Watch Live"),
                ("/field-pack/virtual-zoo/?print=1", "Print cutouts to hide"),
            ],
            "start-going": [
                ("/field-pack/dallas-zoo/", "Sample visit"),
                ("/field-pack/", "Explore Places Near You"),
            ],
            "start-teach": [
                ("/field-pack/cards/#try-a-card", "Browse cards"),
            ],
        }
        for chapter_id, match in chapters.items():
            self.assertIsNotNone(match, chapter_id)
            chapter = match.group(0)
            self.assertIn('class="start-chapter-box"', chapter)
            self.assertLess(chapter.find("start-chapter-box"), chapter.find("start-chapter-pills"))
            pills = re.findall(r'<a class="start-pill" href="([^"]+)">([^<]+)</a>', chapter)
            self.assertEqual(pills, expected[chapter_id], chapter_id)
            self.assertNotIn("start-chapter-link", chapter)
            self.assertNotIn("Open Dallas Zoo", chapter)
            self.assertNotIn("Sample Animal", chapter)
        home = chapters["start-home"].group(0)
        self.assertNotIn("/field-pack/dallas-zoo/", home)
        self.assertNotIn("youtube.com", home)
        self.assertNotIn("target=\"_blank\"", home)
        self.assertEqual(self.html.count('class="start-pill"'), 5)
        teach = chapters["start-teach"].group(0)
        open_cards = re.search(r'<p class="start-open-cards">([\s\S]*?)</p>', teach)
        self.assertIsNotNone(open_cards)
        row = re.sub(r"\s+", " ", open_cards.group(1))
        self.assertIn("Open a card:", row)
        self.assertEqual(
            re.findall(r'<a href="([^"]+)">([^<]+)</a>', open_cards.group(1)),
            [
                ("/field-pack/cards/african-lion/", "Lion"),
                ("/field-pack/cards/african-elephant/", "Elephant"),
                ("/field-pack/cards/reticulated-giraffe/", "Giraffe"),
            ],
        )
        self.assertNotIn("Open Dallas Zoo", self.html)
        self.assertIn("min-height: 44px", self.css)
        self.assertIn("font-size: 1.0625rem", self.css)
        self.assertIn(".start-chapter-pills", self.css)
        self.assertIn(".start-chapter-box", self.css)
        self.assertIn("flex-wrap: wrap", self.css)
        self.assertIn('class="start-open-label"', teach)
        self.assertIn("Open a card:", teach)

    def test_mobile_scrub_keeps_thumb_targets(self):
        mobile = re.search(
            r"@media \(max-width: 640px\) \{([\s\S]*?)\n\}",
            self.css,
        )
        self.assertIsNotNone(mobile)
        block = mobile.group(1)
        self.assertIn("flex-direction: column", block)
        self.assertIn("object-position: 12% 22%", block)
        self.assertIn("#start-home .start-chapter-still", block)
        self.assertIn("min-height: 48px", block)
        self.assertIn("font-size: 1.125rem", block)
        self.assertIn("width: 100%", block)
        self.assertIn(".start-open-label", block)
        self.assertIn("flex: 1 0 100%", block)
        self.assertIn("scroll-snap-type: x mandatory", block)
        self.assertIn("overflow-x: auto", block)
        self.assertIn("overflow-x: clip", self.css)
        self.assertIn(".start-chapter-pills {\n    flex-direction: column", self.css)
        self.assertIn('href="/start/"', self.html)
        self.assertIn('href="/field-pack/"', self.html)
        self.assertIn('href="/field-pack/cards/#try-a-card"', self.html)
        self.assertIn('href="/field-pack/virtual-field-trip/"', self.html)
        self.assertNotIn('href="/field-pack/"', self.js)

    def test_proof_block_is_gone_giraffe_card_still_exists(self):
        self.assertNotIn("start-proof", self.html)
        self.assertNotIn("What you get", self.html)
        self.assertTrue(GIRAFFE.is_file())
        self.assertTrue(DALLAS.is_file())
        giraffe = GIRAFFE.read_text(encoding="utf-8")
        dallas = DALLAS.read_text(encoding="utf-8")
        self.assertIn("reticulated-giraffe.jpg", giraffe)
        self.assertIn("Feed one from the Giraffe Ridge platform.", dallas)

    def test_no_dinner_age_picker_or_home_replacement(self):
        self.assertNotIn("/dinner", self.html)
        self.assertNotIn("seo-age-chip", self.html)
        self.assertNotIn("landing-pitch-t4b", self.html)
        self.assertNotIn("landing-pitch-t4b", self.home)
        self.assertIn("landing-hub", self.home)
        self.assertIn('id="us-map"', self.home)
        self.assertNotIn('id="door-today"', self.home)
        self.assertNotIn("Wildlife wonder, ready for curious kids.", self.home)
        self.assertIn("Zoo and aquarium first. Museums and parks are here when you want them.", self.html)
        foot = re.search(r'<footer class="start-foot">[\s\S]*?</footer>', self.html)
        self.assertIsNotNone(foot)
        self.assertIn('href="/about/"', foot.group(0))
        self.assertNotIn('class="start-door"', foot.group(0))
        self.assertEqual(len(re.findall(r'class="start-door"', self.html)), 0)
        self.assertNotIn("/field-pack/museums/", self.html)
        self.assertNotIn("/field-pack/national-parks/", self.html)
        self.assertIn("Talk, photos, Q&amp;A — on the screen.", self.html)
        self.assertNotIn("lesson plan", self.html.lower())
        self.assertNotIn("grade", self.html.lower())

    def test_motion_is_optional_and_tappable(self):
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn(":focus-visible", self.css)
        self.assertIn("start-home-video", self.html)
        self.assertIn("muted", self.html)
        self.assertIn("playsinline", self.html)
        self.assertIn("autoplay", self.html)
        self.assertIn('preload="auto"', self.html)
        self.assertNotIn('preload="none"', self.html)
        self.assertIn('start.js?v=25', self.html)
        self.assertIn("start.css?v=37", self.html)
        self.assertIn(" loop ", self.html)
        self.assertNotIn("youtube.com", self.html)
        self.assertNotIn("youtube-nocookie.com", self.html)
        self.assertNotIn("<iframe", self.html)
        self.assertIn("prefers-reduced-motion: reduce", self.css)
        self.assertIn(".start-home-video {\n    display: none", self.css)
        self.assertIn("IntersectionObserver", self.js)
        self.assertIn("min-width: 44px", self.css)
        self.assertIn("min-height: 44px", self.css)
        self.assertIn(".start-pill", self.js)
        self.assertIn(".start-route", self.js)
        self.assertNotIn(".start-door", self.js)
        self.assertEqual(len(self.pills), 5)
        for pill in self.pills:
            self.assertTrue(pill.startswith("<a"))

    def test_home_teaser_retries_play_instead_of_still(self):
        lock = self.js.find("function lockAutoplay()")
        src = self.js.find("video.src = teaser.src")
        play = self.js.find("function playTeaser()")
        still = self.js.find("function showStill()")
        hold = self.js.find("function holdPoster()")
        self.assertGreater(lock, 0)
        self.assertGreater(src, lock)
        self.assertGreater(play, src)
        self.assertGreater(hold, still)
        lock_fn = self.js[lock:src]
        self.assertIn("video.muted = true", lock_fn)
        self.assertIn("video.defaultMuted = true", lock_fn)
        self.assertIn("video.autoplay = true", lock_fn)
        self.assertIn("video.loop = true", lock_fn)
        self.assertIn("video.playsInline = true", lock_fn)
        self.assertIn('video.setAttribute("playsinline"', lock_fn)
        self.assertIn('video.setAttribute("autoplay"', lock_fn)
        self.assertIn('video.setAttribute("loop"', lock_fn)
        self.assertIn('video.setAttribute("muted"', lock_fn)
        self.assertIn('preload = "auto"', lock_fn)
        self.assertIn("video.load()", self.js)
        play_fn = re.search(r"function playTeaser\(\) \{([\s\S]*?)\n    \}", self.js)
        self.assertIsNotNone(play_fn)
        self.assertIn("if (reduceMotion)", play_fn.group(1))
        self.assertIn("holdPoster()", play_fn.group(1))
        self.assertIn("kick.catch(() => {\n          if (hardFail) return;\n          holdPoster();", self.js)
        self.assertNotIn("kick.catch(() => showStill())", self.js)
        show = re.search(r"function showContinue\(\) \{([\s\S]*?)\n    \}", self.js)
        self.assertIsNotNone(show)
        self.assertIn("continueEl.hidden = false", show.group(1))
        self.assertNotIn("video.pause()", show.group(1))
        self.assertNotIn("video.pause()", self.js)
        self.assertNotIn("ended = true", show.group(1))
        self.assertNotIn('video.addEventListener("timeupdate"', self.js)
        self.assertIn("ensureContinueTimer", self.js)
        self.assertIn("MAX_SEC * 1000", self.js)
        self.assertIn('home.addEventListener("pointerdown"', self.js)
        self.assertIn('home.addEventListener("touchstart"', self.js)
        self.assertIn('home.addEventListener("click"', self.js)
        self.assertIn("entry.isIntersecting", self.js)
        self.assertIn("playTeaser()", self.js)
        io = re.search(
            r"IntersectionObserver\(\s*\(entries\) => \{([\s\S]*?)\},\s*\{ threshold: \[0, 0.15, 0.35\] \}",
            self.js,
        )
        self.assertIsNotNone(io)
        self.assertIn("playTeaser()", io.group(1))
        self.assertIn("intersecting = true", io.group(1))
        self.assertIn("intersectionRatio > 0", io.group(1))
        self.assertNotIn("p.catch(() => {})", io.group(1))
        error = re.search(
            r'video.addEventListener\("error",\s*\(\) => \{([\s\S]*?)\n    \}\);',
            self.js,
        )
        self.assertIsNotNone(error)
        self.assertIn("showStill();", error.group(1))
        self.assertIn("hardFail = true", error.group(1))
        self.assertIn("prefers-reduced-motion: reduce", self.js)

    def test_home_teaser_files_are_local_mp4s(self):
        teasers = START / "teasers"
        for name in ("flamingo", "giraffe", "lion", "otter"):
            mp4 = teasers / f"{name}.mp4"
            still = teasers / f"{name}.jpg"
            self.assertTrue(mp4.is_file(), name)
            self.assertTrue(still.is_file(), name)
            data = mp4.read_bytes()
            self.assertLess(mp4.stat().st_size, 500_000, name)
            self.assertIn(b"ftyp", data[:32])
            self.assertTrue(still.read_bytes().startswith(b"\xff\xd8"), name)
            served = _get(f"/start/teasers/{name}.mp4")
            self.assertEqual(served._code, 200, name)
            self.assertEqual(served._headers.get("Content-Type"), "video/mp4", name)
        self.assertTrue((START / "home-print-table.jpg").is_file())
        self.assertTrue((START / "home-print-table-640.jpg").is_file())
        self.assertTrue((START / "home-print-table-480.jpg").is_file())
        self.assertFalse((START / "home-laptop-teaser.jpg").exists())
        self.assertIn("#habitat=", self.js)
        self.assertIn("caribbean-flamingo", self.js)
        self.assertIn("reticulated-giraffe", self.js)
        self.assertIn("african-lion", self.js)
        self.assertIn("asian-small-clawed-otter", self.js)


if __name__ == "__main__":
    unittest.main()
