"""Citable-card pilot (2026-10-26): Sources & credits box on 3 traced cards only."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import card_sources as cs  # noqa: E402

CARDS = REPO / "static" / "field-pack" / "cards"
PILOT_IDS = ("whale-shark", "african-elephant", "manta-ray")
CITE_RE = re.compile(
    r'^KidZooKit\. "[A-Z][A-Za-z \'-]+ study card\." kidzookit\.com/field-pack/cards/[a-z0-9-]+/\. '
    r"Accessed (January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\.$"
)


def page(cid: str) -> str:
    return (CARDS / cid / "index.html").read_text(encoding="utf-8")


class CardSourcesPilotTests(unittest.TestCase):
    def test_pilot_set_is_exactly_the_traced_cards(self):
        self.assertEqual(tuple(cs.PILOT), PILOT_IDS)
        for cid in PILOT_IDS:
            self.assertTrue(cs.is_pilot(cid), cid)

    def test_block_on_pilot_pages_after_quiz_before_try_next(self):
        for cid in PILOT_IDS:
            html = page(cid)
            self.assertEqual(html.count('<section class="card-sources"'), 1, cid)
            self.assertIn(cs.render_html(cid), html, cid)
            self.assertIn(f"/field-pack/css/card-sources.css?v={cs.CARD_SOURCES_CSS_VER}", html)
            self.assertIn(f"/field-pack/js/card-sources.js?v={cs.CARD_SOURCES_JS_VER}", html)
            q, s, t = html.find('id="quiz"'), html.find('class="card-sources"'), html.find('class="card-try-next')
            self.assertTrue(0 < q < s < t, cid)
            self.assertIn(f'href="{cs.PILOT[cid]["wiki_url"]}"', html)

    def test_other_cards_untouched(self):
        for d in CARDS.iterdir():
            if d.name in PILOT_IDS or not (d / "index.html").is_file():
                continue
            html = (d / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("card-sources", html, d.name)

    def test_cite_text_format(self):
        for cid in PILOT_IDS:
            self.assertRegex(cs.cite_text(cid), CITE_RE)
            text = re.sub(r"<[^>]+>", "", re.search(r"data-cite-text>(.*?)</p>", page(cid)).group(1))
            text = text.replace("&quot;", '"')
            self.assertRegex(text, CITE_RE)

    def test_spot_checks_are_per_fact_and_never_whole_card(self):
        for cid in PILOT_IDS:
            block = cs.render_html(cid)
            n = len(cs.PILOT[cid]["checks"])
            self.assertGreater(n, 0)
            self.assertEqual(block.count("<li>Spot-checked: "), n)
            self.assertIn(f"{n} fact{'s' if n != 1 else ''} spot-checked", block)
            self.assertIn("Other facts were not separately checked.", block)
            for bad in ("Checked against", "Reviewed", "Verified", "Fact-checked", "approved"):
                self.assertNotIn(bad, block, f"{cid}: over-claiming wording {bad!r}")
            for ch in cs.PILOT[cid]["checks"]:
                self.assertTrue(ch["url"].startswith("https://"))

    def test_no_credit_without_author_and_licence(self):
        good = dict(cs.PILOT["whale-shark"]["photo"])
        self.assertTrue(cs.photo_credit_ok(good))
        for missing in ("author", "license", "license_url", "file_page"):
            bad = dict(good)
            bad[missing] = ""
            self.assertFalse(cs.photo_credit_ok(bad), missing)
        self.assertFalse(cs.photo_credit_ok(None))
        self.assertFalse(cs.photo_credit_ok(dict(good, file_page="https://example.com/x.jpg")))
        try:
            cs.PILOT["tmp-card"] = dict(cs.PILOT["manta-ray"], photo={"author": "", "license": "CC BY-SA 4.0"})
            self.assertFalse(cs.is_pilot("tmp-card"))
            self.assertEqual(cs.render_html("tmp-card"), "")
            self.assertEqual(cs.head_link("tmp-card"), "")
        finally:
            cs.PILOT.pop("tmp-card", None)
        for cid in PILOT_IDS:
            p = cs.PILOT[cid]["photo"]
            self.assertIn(f"Photo: {p['author']}, ", page(cid))
            self.assertIn(p["license"], page(cid))
            self.assertIn(p["file_page"].replace("&", "&amp;"), page(cid))

    def test_untraced_heroes_not_in_pilot(self):
        for cid in ("giant-panda", "african-lion", "american-bison"):
            self.assertFalse(cs.is_pilot(cid))
            self.assertNotIn("card-sources", page(cid))

    def test_js_events_and_copy_fallback(self):
        js = (REPO / "static" / "field-pack" / "js" / "card-sources.js").read_text(encoding="utf-8")
        self.assertIn('"cite_copy"', js)
        self.assertIn('"source_link_click"', js)
        self.assertIn("window.trackEvent", js)  # shell.js track: no-op when analytics is off
        self.assertNotIn("gtag(", js)
        self.assertIn("navigator.clipboard", js)
        self.assertIn("addRange", js)  # iOS Safari fallback selects the text
        self.assertIn("execCommand", js)

    def test_privacy_discloses_new_events(self):
        html = (REPO / "static" / "privacy" / "index.html").read_text(encoding="utf-8")
        self.assertIn("source link is opened", html)
        self.assertIn("Copy citation", html)
        self.assertIn("The copied text itself is not sent.", html)


if __name__ == "__main__":
    unittest.main()
