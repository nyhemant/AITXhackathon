"""First-time landing at /start/ — does not replace the live home."""

from pathlib import Path
import hashlib
import re
import subprocess
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
DALLAS = FP / "dallas-zoo" / "index.html"
MAIN_HOME_SHA = "5b527c1b3407794627f60b57882e2ad466708ddbfffeb52ebb25eb4d124f0cb4"


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
        self.doors = re.findall(
            r'<a\s+class="start-door"[\s\S]*?</a>',
            self.html,
        )

    def test_home_file_is_unchanged_from_starting_main(self):
        digest = hashlib.sha256(HOME.read_bytes()).hexdigest()
        self.assertEqual(digest, MAIN_HOME_SHA)
        try:
            tracked = subprocess.check_output(
                ["git", "diff", "--name-only", "--", "static/field-pack/index.html"],
                cwd=REPO,
                text=True,
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            tracked = ""
        self.assertEqual(tracked, "")

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
        self.assertIn("A ready-to-use field trip for curious kids.", body)
        self.assertIn("I need an activity for today", body)
        self.assertIsNotNone(_safe_start_path("/start/"))
        self.assertIsNotNone(_safe_start_path("/start/start.css"))
        self.assertIsNone(_safe_start_path("/start/../field-pack/index.html"))
        self.assertIsNotNone(_safe_field_pack_path("/field-pack/"))

    def test_locked_headline_sub_and_trust(self):
        self.assertEqual(
            _heading_text(self.html),
            "A ready-to-use field trip for curious kids.",
        )
        self.assertIn(
            "At home or before you go. Pick a place or an animal. Get a short activity with real photos, questions to ask, and an optional mission to print.",
            self.html,
        )
        self.assertIn("Free · No account · At home or on location", self.html)
        self.assertNotIn("Ages 4–10", self.html)
        self.assertNotIn("Ages 4-10", self.html)
        self.assertNotIn("5–20 minutes", self.html)
        self.assertNotIn("5-20 minutes", self.html)
        self.assertNotIn("218 places", self.html)
        self.assertNotIn("10,000 families", self.html)
        self.assertNotIn("testimonial", self.html.lower())

    def test_outcome_then_three_equal_doors(self):
        outcome = self.html.find('id="start-outcome"')
        doors = self.html.find('id="start-doors"')
        proof = self.html.find('id="start-proof"')
        self.assertTrue(0 < outcome < doors < proof)
        self.assertEqual(len(self.doors), 3)
        self.assertIn("I need an activity for today", self.html)
        self.assertIn("Pick an animal or a place. Start now.", self.html)
        self.assertIn("We’re visiting somewhere soon", self.html)
        self.assertIn("Make the outing easier to finish. Same cards, optional print later.", self.html)
        self.assertIn("I’m teaching a group", self.html)
        self.assertIn(
            "For classrooms and homeschool: open a place, show the visuals, ask the prompts, optional printable follow-up.",
            self.html,
        )
        self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr))", self.css)
        self.assertNotIn("Before", "".join(self.doors))
        self.assertNotIn("During", "".join(self.doors))
        self.assertNotIn("After", "".join(self.doors))

    def test_each_door_opens_dallas_session_not_print(self):
        self.assertEqual(len(self.doors), 3)
        for door in self.doors:
            href = re.search(r'href="([^"]+)"', door)
            self.assertIsNotNone(href)
            self.assertEqual(href.group(1), "/field-pack/dallas-zoo/")
            self.assertNotIn("#mission", door)
            self.assertNotIn("#print", door)
            self.assertNotIn("youtube", door.lower())
        self.assertIn('id="door-today"', self.html)
        self.assertIn('id="door-visiting"', self.html)
        self.assertIn('id="door-teaching"', self.html)
        self.assertNotIn("/field-pack/dallas-zoo/#mission", self.html)
        self.assertNotIn("/field-pack/dallas-zoo/#print", self.html)
        self.assertNotIn("youtube.com", self.html)
        self.assertNotIn("youtube-nocookie.com", self.html)
        self.assertNotIn("us-map", self.html)
        self.assertNotIn("map-host", self.html)
        self.assertTrue(DALLAS.is_file())
        self.assertIsNotNone(_safe_field_pack_path("/field-pack/dallas-zoo/"))

    def test_proof_is_existing_dallas_giraffe(self):
        proof = re.search(r'<figure class="start-proof-card">[\s\S]*?</figure>', self.html)
        self.assertIsNotNone(proof)
        card = proof.group(0)
        giraffe = GIRAFFE.read_text(encoding="utf-8")
        dallas = DALLAS.read_text(encoding="utf-8")
        self.assertIn("/field-pack/photos/reticulated-giraffe.jpg?v=img2", card)
        self.assertIn("Reticulated giraffe", card)
        self.assertIn("Feed one from the Giraffe Ridge platform.", card)
        self.assertIn("Feed one from the Giraffe Ridge platform.", dallas)
        self.assertIn("reticulated-giraffe.jpg", giraffe)
        self.assertNotIn("Dallas Zoo", card)
        self.assertNotIn("/field-pack/cards/", card)

    def test_no_dinner_age_picker_or_home_replacement(self):
        self.assertNotIn("/dinner", self.html)
        self.assertNotIn("seo-age-chip", self.html)
        self.assertNotIn("landing-pitch-t4b", self.html)
        self.assertIn("landing-pitch-t4b", self.home)
        self.assertIn('id="us-map"', self.home)
        self.assertNotIn('id="door-today"', self.home)
        self.assertNotIn("A ready-to-use field trip for curious kids.", self.home)
        self.assertIn("Zoo and aquarium first. Museums and parks are here when you want them.", self.html)
        self.assertNotIn("/field-pack/museums/", self.html)
        self.assertNotIn("/field-pack/national-parks/", self.html)
        self.assertNotIn("lesson", self.html.lower())
        self.assertNotIn("grade", self.html.lower())

    def test_motion_is_optional_and_tappable(self):
        self.assertIn("prefers-reduced-motion", self.css)
        self.assertIn(":focus-visible", self.css)
        self.assertNotIn("autoplay", self.html)
        self.assertNotIn("<video", self.html)
        self.assertIn(".start-door", self.js)
        for door in self.doors:
            self.assertTrue(door.startswith("<a"))


if __name__ == "__main__":
    unittest.main()
