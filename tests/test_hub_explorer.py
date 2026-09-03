"""Field Trip Kit hub is a place explorer. Root still points at /field-pack/."""

from pathlib import Path
import re
import unittest

from busyparent_agent.web import ABOUT_PREFIX, FIELD_PACK_PREFIX, START_PREFIX, WebHandler


REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
START = REPO / "static" / "start"
HOME = FP / "index.html"
START_HTML = START / "index.html"


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


COMPAT_PATHS = (
    "/field-pack/",
    "/field-pack/zoos/",
    "/field-pack/aquariums/",
    "/field-pack/museums/",
    "/field-pack/national-parks/",
    "/field-pack/cards/",
    "/field-pack/cards/reticulated-giraffe/",
    "/field-pack/virtual-field-trip/",
    "/field-pack/virtual-zoo/",
    "/field-pack/dallas-zoo/",
    "/start/",
    "/about/",
    "/dinner",
)


class HubExplorerTests(unittest.TestCase):
    def setUp(self):
        self.html = HOME.read_text(encoding="utf-8")
        self.start = START_HTML.read_text(encoding="utf-8")

    def test_root_redirect_is_unchanged(self):
        root = _get("/")
        self.assertEqual(root._code, 302)
        self.assertEqual(root._headers.get("Location"), FIELD_PACK_PREFIX + "/")
        self.assertNotEqual(root._headers.get("Location"), START_PREFIX + "/")

    def test_start_has_one_explore_places_cta(self):
        going = re.search(
            r'<section class="start-chapter" id="start-going"[\s\S]*?</section>',
            self.start,
        )
        self.assertIsNotNone(going)
        chapter = going.group(0)
        links = re.findall(r'<a class="start-chapter-link"[^>]*>[\s\S]*?</a>', chapter)
        self.assertEqual(len(links), 1, links)
        self.assertIn('href="/field-pack/"', links[0])
        self.assertIn("Explore places near you", links[0])
        self.assertNotIn("Explore zoos", chapter)
        self.assertNotIn("Explore aquariums", chapter)
        self.assertIn('href="/field-pack/dallas-zoo/"', chapter)
        self.assertIn('class="start-going-hit"', chapter)
        self.assertIn("Open Dallas Zoo", self.start)
        self.assertEqual(self.start.count('href="/field-pack/dallas-zoo/"'), 4)

    def test_hub_is_map_first_place_explorer(self):
        self.assertIn("landing-hub", self.html)
        self.assertIn('class="hub-find"', self.html)
        self.assertIn('id="pitch-heading"', self.html)
        self.assertIn("Find a place", self.html)
        self.assertIn('id="hero-place-search"', self.html)
        self.assertIn('id="place-type-tabs"', self.html)
        self.assertIn('data-place-type="zoo"', self.html)
        self.assertIn('data-place-type="aquarium"', self.html)
        self.assertIn('data-place-type="museum"', self.html)
        self.assertIn('data-place-type="park"', self.html)
        self.assertIn('id="scope-top"', self.html)
        self.assertIn('id="scope-more"', self.html)
        self.assertIn('id="scope-intl"', self.html)
        self.assertIn('id="us-map"', self.html)
        self.assertIn('id="ready-grid"', self.html)
        self.assertIn("218 places worldwide", self.html)
        self.assertIn('href="/field-pack/zoos/"', self.html)
        self.assertIn('href="/field-pack/aquariums/"', self.html)
        self.assertIn('href="/field-pack/museums/"', self.html)
        self.assertIn('href="/field-pack/national-parks/"', self.html)
        self.assertIn("location.replace(\"/field-pack/\" + encodeURIComponent(id) + \"/\")", self.html)

    def test_hub_has_start_path_and_no_primary_pitch(self):
        self.assertIn('href="/start/"', self.html)
        self.assertIn('class="shell-start"', self.html)
        self.assertNotIn("landing-pitch-t4b", self.html)
        self.assertNotIn("hero-moment-strip", self.html)
        self.assertNotIn("hero-moment-before", self.html)
        self.assertNotIn(">Before<", self.html)
        self.assertNotIn(">During<", self.html)
        self.assertNotIn(">After<", self.html)
        self.assertIn('id="after"', self.html)
        self.assertIn('id="about"', self.html)
        self.assertNotIn('id="faq"', self.html)
        self.assertNotIn("Common questions", self.html)
        self.assertNotIn("FAQPage", self.html)
        self.assertIn('href="/about/"', self.html)
        self.assertIn("hub-secondary", self.html)
        self.assertIn('id="cat-card-grid"', self.html)
        self.assertIn('href="/field-pack/cards/"', self.html)
        self.assertIn('href="/field-pack/virtual-field-trip/"', self.html)

    def test_compatibility_routes_still_200(self):
        for path in COMPAT_PATHS:
            h = _get(path)
            self.assertEqual(h._code, 200, path)

        zoos = _get("/field-pack/zoos/")
        self.assertIn(b"Zoos", zoos.wfile.getvalue())
        parks = _get("/field-pack/national-parks/")
        self.assertEqual(parks._code, 200)
        vft = _get("/field-pack/virtual-field-trip/")
        self.assertIn(b"Virtual Field Trip", vft.wfile.getvalue())
        vz = _get("/field-pack/virtual-zoo/")
        self.assertIn(vz._code, {200, 301, 302}, vz._code)

    def test_about_is_seek_out_not_a_landing(self):
        slash = _get("/about")
        self.assertEqual(slash._code, 301)
        self.assertEqual(slash._headers.get("Location"), ABOUT_PREFIX + "/")
        page = _get("/about/")
        self.assertEqual(page._code, 200)
        body = page.wfile.getvalue().decode("utf-8")
        self.assertIn("<title>About · Field Trip Kit · 1Less</title>", body)
        self.assertIn("Field Trip Kit is an at-home virtual zoo", body)
        self.assertIn("Use the at-home cards and session together; print is optional for a group visit.", body)
        self.assertIn("What should I see at the zoo with a toddler?", body)
        self.assertIn("Can teachers or homeschool groups use this?", body)
        self.assertNotIn('class="start-hero"', body)
        self.assertNotIn('id="door-today"', body)
        heading = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", body)
        self.assertIsNotNone(heading)
        self.assertEqual(heading.group(1).strip(), "About")
        self.assertIn('href="/start/"', body)
        foot = re.search(r'<footer class="start-foot">[\s\S]*?</footer>', self.start)
        self.assertIsNotNone(foot)
        self.assertIn('href="/about/"', foot.group(0))
        self.assertNotIn('id="door-about"', self.start)
        doors = re.findall(r'class="start-door"', self.start)
        self.assertEqual(len(doors), 3)


if __name__ == "__main__":
    unittest.main()
