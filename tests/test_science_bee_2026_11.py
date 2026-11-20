"""KZK Science Bee practice section (2026-11-18).

Covers the question bank schema and balance, generated pages staying in sync
with the bank, no outbound links or media on the game pages, copy rules, no
overlap with the reference competition packets used only for calibration,
routing, and the sitemap.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import struct
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from busyparent_agent.web import WebHandler

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "static" / "science-bee"
BANK = ROOT / "data" / "questions-v1.json"
REF_6GRAMS = REPO / "tests" / "data" / "science_bee_ref_6gram_v1.bin"
TOPIC_SLUGS = {
    "life": "life-science",
    "earth": "earth-and-space",
    "physical": "physical-science",
    "body": "human-body",
    "weather": "weather",
    "plants": "plants-and-animals",
}
INDEXED = ["/science-bee/"] + [f"/science-bee/questions/{s}/" for s in TOPIC_SLUGS.values()]


def _load_build():
    spec = importlib.util.spec_from_file_location("sb_build", REPO / "scripts" / "science_bee_build_v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _bank():
    return json.loads(BANK.read_text(encoding="utf-8"))["questions"]


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs, self.srcs, self.tags, self.text = [], [], [], []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        if "src" in a:
            self.srcs.append(a["src"])
        if tag in ("script", "style"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def _parse(path: Path) -> _Links:
    p = _Links()
    p.feed(path.read_text(encoding="utf-8"))
    return p


def _norm_words(s: str) -> list[str]:
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).split()


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)


class _Fake(WebHandler):
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


def _req(path, method="GET"):
    h = _Fake(path)
    getattr(h, "do_" + method)()
    return h


class QuestionBankTests(unittest.TestCase):
    def setUp(self):
        self.qs = _bank()

    def test_schema(self):
        build = _load_build()
        ids = [q["id"] for q in self.qs]
        self.assertEqual(len(ids), len(set(ids)))
        for q in self.qs:
            with self.subTest(q=q["id"]):
                self.assertIn(q["topic"], TOPIC_SLUGS)
                self.assertIn(q["band"], ("little", "big"))
                for k in ("q", "a", "hint", "fix"):
                    self.assertIsInstance(q[k], str)
                    self.assertGreater(len(q[k].strip()), 1)
                self.assertNotIn(q["a"], q["wrong"])
                self.assertEqual(len(set(q["wrong"])), len(q["wrong"]))
                if q["band"] == "little":
                    self.assertIn(len(q["wrong"]), (1, 2), "Little questions offer 2 or 3 choices")
                else:
                    self.assertEqual(len(q["wrong"]), 2, "Big questions keep 3 choices for Give choices")
                pic = q.get("pic")
                if pic:
                    self.assertEqual(len(pic), 1)
                    if "svg" in pic:
                        self.assertIn(pic["svg"], build.SVGS)
                    if "photo" in pic:
                        self.assertIn(pic["photo"], build.PHOTOS)
                        self.assertTrue((REPO / "static" / "field-pack" / "photos" / f"{pic['photo']}.jpg").is_file())

    def test_size_and_balance(self):
        self.assertGreaterEqual(len(self.qs), 200)
        cell = Counter((q["topic"], q["band"]) for q in self.qs)
        for t in TOPIC_SLUGS:
            for b in ("little", "big"):
                self.assertGreaterEqual(cell[(t, b)], 15, (t, b))
        bands = Counter(q["band"] for q in self.qs)
        self.assertLess(abs(bands["little"] - bands["big"]), len(self.qs) * 0.15)
        topics = Counter(q["topic"] for q in self.qs)
        for t, n in topics.items():
            self.assertGreater(n / len(self.qs), 0.12, t)
            self.assertLess(n / len(self.qs), 0.22, t)
        pics = Counter(q["band"] for q in self.qs if q.get("pic"))
        self.assertGreaterEqual(pics["little"], 12)
        self.assertGreaterEqual(pics["big"], 12)

    def test_easy_win_pool(self):
        for b in ("little", "big"):
            easy = [q for q in self.qs if q["band"] == b and q.get("easy")]
            self.assertGreaterEqual(len(easy), 3, b)
        little_easy = [q for q in self.qs if q["band"] == "little" and q.get("easy")]
        self.assertGreaterEqual(len(little_easy), 30)
        self.assertEqual({q["topic"] for q in little_easy}, set(TOPIC_SLUGS))

    def test_no_overlap_with_reference_packets(self):
        """No 6-word run from the calibration packets (stored only as hashes)."""
        raw = REF_6GRAMS.read_bytes()
        ref = set(struct.unpack(f">{len(raw) // 4}I", raw))
        self.assertGreater(len(ref), 50000)
        hits = []
        for q in self.qs:
            for field in ("q", "a", "hint", "fix"):
                w = _norm_words(q[field])
                for i in range(len(w) - 5):
                    g = " ".join(w[i : i + 6])
                    h = int.from_bytes(hashlib.sha256(g.encode()).digest()[:4], "big")
                    if h in ref:
                        hits.append((q["id"], field, g))
        self.assertEqual(hits, [])


class GeneratedPagesTests(unittest.TestCase):
    def test_generated_files_match_the_bank(self):
        build = _load_build()
        bank = build.load_bank()
        self.assertEqual((ROOT / "sb-questions-v1.js").read_text(encoding="utf-8"), build.build_bank_js(bank))
        self.assertEqual((ROOT / "index.html").read_text(encoding="utf-8"), build.build_hub(bank))
        self.assertEqual((ROOT / "play" / "index.html").read_text(encoding="utf-8"), build.build_play())
        for t in build.TOPICS:
            path = ROOT / "questions" / t[1] / "index.html"
            self.assertEqual(path.read_text(encoding="utf-8"), build.build_topic(bank, t), t[1])

    def test_every_question_is_on_a_topic_page(self):
        qs = _bank()
        for q in qs:
            html = (ROOT / "questions" / TOPIC_SLUGS[q["topic"]] / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'id="{q["id"]}"', html)

    def test_game_pages_have_no_outbound_links_or_media(self):
        pages = [ROOT / "play" / "index.html"] + [ROOT / "questions" / s / "index.html" for s in TOPIC_SLUGS.values()]
        for page in pages:
            p = _parse(page)
            with self.subTest(page=str(page.relative_to(REPO))):
                for href in p.hrefs:
                    self.assertTrue(href.startswith("/") or href.startswith("#"), href)
                for src in p.srcs:
                    self.assertTrue(src.startswith("/"), src)
                tags = {t for t, _ in p.tags}
                for bad in ("audio", "video", "iframe", "embed", "object", "form", "input"):
                    self.assertNotIn(bad, tags)
                self.assertNotIn("autoplay", page.read_text(encoding="utf-8"))
        for js in ("sb-game-v1.js", "sb-questions-v1.js"):
            body = (ROOT / js).read_text(encoding="utf-8")
            self.assertNotRegex(body, r"https?://")
            for bad in ("fetch(", "XMLHttpRequest", "sendBeacon", "new Audio", "AudioContext", ".play("):
                self.assertNotIn(bad, body, (js, bad))

    def test_hub_outbound_links_are_photo_credits_only(self):
        p = _parse(ROOT / "index.html")
        outbound = [h for h in p.hrefs if not (h.startswith("/") or h.startswith("#"))]
        self.assertTrue(outbound)
        for h in outbound:
            self.assertTrue(h.startswith("https://creativecommons.org/") or h.startswith("https://commons.wikimedia.org/"), h)

    def test_game_stores_settings_only(self):
        body = (ROOT / "sb-game-v1.js").read_text(encoding="utf-8")
        self.assertEqual(body.count("localStorage.setItem("), 1)
        self.assertIn('var KEY = "kzk-sb-settings-v1"', body)
        self.assertNotIn("sessionStorage", body)
        self.assertNotIn("document.cookie", body)
        self.assertNotIn("indexedDB", body)
        self.assertNotRegex(body, r"<input|prompt\(")

    def test_copy_rules(self):
        files = [ROOT / "index.html", ROOT / "play" / "index.html"] + [ROOT / "questions" / s / "index.html" for s in TOPIC_SLUGS.values()]
        words = re.compile(r"\b(we|our|us|We|Our|Us|free|Free|FREE|no-cost|No-cost)\b")
        for f in files:
            text = " ".join(_parse(f).text)
            with self.subTest(page=str(f.relative_to(REPO))):
                self.assertIsNone(words.search(text), words.search(text) and words.search(text).group(0))
                self.assertNotIn("IAC", text)
                self.assertNotIn("International Academic", text)
                self.assertNotIn("National Science Bee", text)
                self.assertIn("not connected to or endorsed by any competition", text)
        game = (ROOT / "sb-game-v1.js").read_text(encoding="utf-8")
        for q in _bank():
            blob = " ".join([q["q"], q["a"], q["hint"], q["fix"]] + q["wrong"])
            self.assertIsNone(words.search(blob), q["id"])
        self.assertIsNone(re.search(r"\b(free|Free|IAC)\b", game))

    def test_play_is_noindex_and_topic_pages_are_indexed(self):
        play = (ROOT / "play" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<meta name="robots" content="noindex,follow" />', play)
        for u in INDEXED:
            path = REPO / "static" / u.strip("/") / "index.html"
            html = path.read_text(encoding="utf-8")
            self.assertIn('<meta name="robots" content="index,follow" />', html)
            self.assertIn(f'<link rel="canonical" href="https://kidzookit.com{u}" />', html)

    def test_pdf_is_versioned_and_present(self):
        pdf = ROOT / "pdf" / "science-bee-practice-sheet-v1.pdf"
        self.assertTrue(pdf.read_bytes().startswith(b"%PDF"))
        self.assertIn("/science-bee/pdf/science-bee-practice-sheet-v1.pdf", (ROOT / "index.html").read_text(encoding="utf-8"))


class RoutingAndSitemapTests(unittest.TestCase):
    def test_routes(self):
        for u in INDEXED + ["/science-bee/play/"]:
            r = _req(u)
            self.assertEqual(r._code, 200, u)
            self.assertEqual(r._headers.get("Content-Type"), "text/html; charset=utf-8")
            self.assertEqual(r._headers.get("Cache-Control"), "no-cache")
        r = _req("/science-bee")
        self.assertEqual(r._code, 301)
        self.assertEqual(r._headers.get("Location"), "/science-bee/")
        r = _req("/science-bee/play?x=1")
        self.assertEqual(r._code, 301)
        self.assertEqual(r._headers.get("Location"), "/science-bee/play/?x=1")
        r = _req("/science-bee/pdf/science-bee-practice-sheet-v1.pdf")
        self.assertEqual(r._code, 200)
        self.assertEqual(r._headers.get("Content-Type"), "application/pdf")
        r = _req("/science-bee/sb-game-v1.js?v=1")
        self.assertEqual(r._headers.get("Cache-Control"), "public, max-age=2592000")  # versioned: 30 days (2026-11-20)
        self.assertEqual(_req("/science-bee/../web.py")._code, 404)
        self.assertEqual(_req("/science-bee/nope/")._code, 404)
        h = _req("/science-bee/", "HEAD")
        self.assertEqual(h._code, 200)

    def test_sitemap_lists_hub_and_topics_not_play(self):
        for sm in (REPO / "static" / "sitemap.xml",):
            body = sm.read_text(encoding="utf-8")
            for u in INDEXED:
                self.assertEqual(body.count(f"<loc>https://kidzookit.com{u}</loc>"), 1, (sm, u))
            self.assertNotIn("/science-bee/play/", body)

    def test_generator_keeps_science_bee_in_sitemap(self):
        src = (REPO / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        self.assertIn("extras.extend(published_science_bee_paths())", src)

    def test_entry_links(self):
        start = (REPO / "static" / "start" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/science-bee/"', start)
        printables = (REPO / "static" / "printables" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/science-bee/"', printables)

    def test_offline_shell(self):
        sw = (REPO / "static" / "pwa" / "sw.js").read_text(encoding="utf-8")
        self.assertIn('"/science-bee/play",', sw)
        play = (ROOT / "play" / "index.html").read_text(encoding="utf-8")
        self.assertIn('src="/pwa/register.js?v=1"', play)


if __name__ == "__main__":
    unittest.main()
