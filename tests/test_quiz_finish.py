"""Quiz finish moment + quiz events (2026-10-24).

Guards: the reviewed one-printable-per-card map covers every quiz card and only
points at existing printable pages; JS and data file agree; event names and
honest copy are present; card pages and the generator carry the same asset
versions so a regen keeps the new JS/CSS.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "static" / "field-pack"
JS = FP / "js" / "study-card.js"
CSS = FP / "css" / "study-card.css"
DATA = ROOT / "data" / "quiz_printables.json"
GEN = ROOT / "scripts" / "generate_bdo_seo.py"


def quiz_card_ids():
    out = set()
    for page in (FP / "cards").glob("*/index.html"):
        m = re.search(r'data-study-id="([a-z0-9-]+)"', page.read_text(encoding="utf-8"))
        if m:
            out.add(m.group(1))
    return out


class QuizPrintableMapTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(DATA.read_text(encoding="utf-8"))
        self.js = JS.read_text(encoding="utf-8")

    def test_every_quiz_card_has_exactly_one_reviewed_sheet(self):
        ids = quiz_card_ids()
        self.assertEqual(len(ids), 42)
        self.assertEqual(set(self.data["cards"]), ids)
        for cid, row in self.data["cards"].items():
            self.assertIn(row["sheet"], self.data["pages"], cid)
            self.assertTrue(row.get("why", "").strip(), cid)

    def test_sheets_are_existing_printable_pages(self):
        for slug, page in self.data["pages"].items():
            self.assertEqual(page["href"], f"/printables/{slug}/")
            self.assertTrue((ROOT / "static" / "printables" / slug / "index.html").is_file(), slug)
            self.assertNotIn("free", page["label"].lower())

    def test_js_map_matches_data_file(self):
        block = self.js.split("const FP_QUIZ_PRINTABLES = {", 1)[1].split("};", 1)[0]
        js_map = dict(re.findall(r'"([a-z0-9-]+)": "([a-z0-9-]+)"', block))
        self.assertEqual(js_map, {k: v["sheet"] for k, v in self.data["cards"].items()})
        pages = self.js.split("const FP_QUIZ_PRINTABLE_PAGES = {", 1)[1].split("};", 1)[0]
        for slug, page in self.data["pages"].items():
            self.assertIn(f'"{slug}": {{ href: "{page["href"]}", label: "{page["label"]}" }}', pages)


class QuizFinishCopyAndEventsTest(unittest.TestCase):
    def setUp(self):
        self.js = JS.read_text(encoding="utf-8")
        self.css = CSS.read_text(encoding="utf-8")

    def test_events_use_shell_track_event(self):
        for name in ("quiz_start", "quiz_complete", "quiz_tier_pick", "quiz_next_click"):
            self.assertIn(f'"{name}"', self.js)
        self.assertIn("window.trackEvent", self.js)
        self.assertIn("first_try_correct", self.js)
        for link_type in ("next_tier", "next_card", "printable", "watch"):
            self.assertIn(f'"{link_type}"', self.js)

    def test_honest_copy(self):
        self.assertIn("Not quite, try another!", self.js)
        self.assertIn("complete!", self.js)
        self.assertIn("right on the first try", self.js)
        self.assertIn("Skip ahead to", self.js)
        self.assertNotIn("Got them all", self.js)
        self.assertIn("of ${total} done", self.js)

    def test_no_completion_claim_before_answers_in_static_pages(self):
        for page in (FP / "cards").glob("*/index.html"):
            html = page.read_text(encoding="utf-8")
            self.assertNotIn("Got them all", html, page.parent.name)
            self.assertNotIn("study-finish", html, page.parent.name)

    def test_celebration_respects_reduced_motion(self):
        self.assertIn("@keyframes study-finish-pop", self.css)
        tail = self.css.split("@media (prefers-reduced-motion: reduce)")[-1]
        self.assertIn(".study-finish", tail)
        self.assertIn("animation: none", tail)


class AnswerCueVisibleTest(unittest.TestCase):
    """The wrong-answer cue and the 'why' line must not hide under the sticky pill."""

    def test_js_scrolls_cue_clear_of_pill(self):
        js = (FP / "js" / "study-card.js").read_text(encoding="utf-8")
        self.assertIn("function revealFeedback(qEl, isRight)", js)
        self.assertIn(".study-progress", js.split("function revealFeedback", 1)[1][:900])
        self.assertIn("prefers-reduced-motion: reduce", js.split("function revealFeedback", 1)[1][:1200])
        self.assertIn("revealFeedback(qEl, isRight);", js)

    def test_css_leaves_room_for_pill(self):
        css = (FP / "css" / "study-card.css").read_text(encoding="utf-8")
        block = css.split(".card-page .card-study-pack .study-why {\n  scroll-margin-bottom", 1)
        self.assertEqual(len(block), 2)
        self.assertIn(".card-page .card-study-pack .study-nudge,", css)


class QuizAssetVersionGuardTest(unittest.TestCase):
    def test_card_pages_match_generator_versions(self):
        gen = GEN.read_text(encoding="utf-8")
        js_ver = re.search(r'STUDY_CARD_JS_VER = "(\d+)"', gen).group(1)
        css_ver = re.search(r'STUDY_CARD_CSS_VER = "(\d+)"', gen).group(1)
        self.assertGreaterEqual(int(js_ver), 19)
        self.assertGreaterEqual(int(css_ver), 16)
        n = 0
        for page in (FP / "cards").glob("*/index.html"):
            html = page.read_text(encoding="utf-8")
            if "study-card.js" not in html:
                continue
            n += 1
            self.assertIn(f"/field-pack/js/study-card.js?v={js_ver}", html, page.parent.name)
            self.assertIn(f"/field-pack/css/study-card.css?v={css_ver}", html, page.parent.name)
        self.assertEqual(n, 42)


if __name__ == "__main__":
    unittest.main()
