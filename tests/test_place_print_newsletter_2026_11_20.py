"""Round 2 item 2 (2026-11-20): the weekly email offer on the print path of every place page."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "static" / "field-pack"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

UI_TAG = re.compile(r'<script src="/field-pack/js/mission/mission-ui\.js\?v=[0-9a-z-]+"></script>')
FORM_RE = re.compile(r'<form class="kz-nl kz-nl--print no-print".*?</form>', re.S)


def _mission_pages():
    for page in sorted(FP.glob("*/index.html")):
        html = page.read_text(encoding="utf-8")
        if UI_TAG.search(html):
            yield page.parent.name, html


class PlacePrintBox(unittest.TestCase):
    def test_every_place_page_has_one_hidden_box_after_the_sticky_bar(self):
        n = 0
        for slug, html in _mission_pages():
            n += 1
            with self.subTest(slug=slug):
                forms = FORM_RE.findall(html)
                self.assertEqual(len(forms), 1, slug)
                form = forms[0]
                self.assertIn('data-placement="place_print" hidden data-reveal="print"', form)
                self.assertIn('action="/api/newsletter" method="post"', form)
                self.assertIn('<input type="hidden" name="placement" value="place_print">', form)
                self.assertIn('<a class="kz-nl-sample" href="/newsletter/sample/">See a sample email</a>', form)
                self.assertIn('name="website"', form)
                self.assertLess(html.find('id="seo-hunt-sticky"'), html.find(form))
                self.assertLess(html.find('id="mission-drawer"'), html.find(form))
                self.assertEqual(html.count('href="/field-pack/css/newsletter-v1.css?v=6"'), 1, slug)
                self.assertEqual(html.count('src="/field-pack/js/newsletter-v1.js?v=8"'), 1, slug)
                text = re.sub(r"<[^>]+>", " ", form)
                self.assertNotRegex(text, r"(?i)\bfree\b")
                self.assertNotRegex(text, r"(?i)\b(we|our|us)\b")
                self.assertNotRegex(text, r"\bKit\b")
        self.assertGreaterEqual(n, 221)

    def test_generator_template_and_patch_agree(self):
        import generate_bdo_seo as gen

        box = gen.place_print_newsletter_html()
        for slug, html in _mission_pages():
            self.assertIn(box, html, slug)
        src = (ROOT / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        tpl = src.split("def render_mission_venue_page(", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("{place_print_newsletter_html()}", tpl)
        self.assertIn('<script defer src="{NEWSLETTER_JS_HREF}"></script>', tpl)
        self.assertIn('<link rel="stylesheet" href="{NEWSLETTER_CSS_HREF}" />', tpl)
        # Patch is idempotent.
        slug, html = next(_mission_pages())
        self.assertEqual(gen.add_place_print_newsletter(html), html)

    def test_script_reveals_only_on_print_and_respects_opt_outs(self):
        js = (FP / "js" / "newsletter-v1.js").read_text(encoding="utf-8")
        self.assertIn('getAttribute("data-reveal") === "print"', js)
        self.assertIn('window.addEventListener("beforeprint", reveal)', js)
        self.assertIn('window.addEventListener("afterprint", reveal)', js)
        self.assertIn('value === "place_print"', js)
        reveal = js.split("function reveal()", 1)[1].split("window.addEventListener", 1)[0]
        self.assertIn("SUB_KEY", reveal)
        self.assertIn("DISMISS_KEY", reveal)

    def test_card_never_prints(self):
        css = (FP / "css" / "newsletter-v1.css").read_text(encoding="utf-8")
        tail = css.split("/* place_print:", 1)[1]
        self.assertIn("@media print", tail)
        self.assertIn(".kz-nl--print {\n    display: none !important;", tail)

    def test_server_logs_the_new_placement(self):
        from busyparent_agent.newsletter import placement_label

        self.assertEqual(placement_label("place_print"), "place_print")
        self.assertEqual(placement_label("someone@example.com"), "other")


if __name__ == "__main__":
    unittest.main()
