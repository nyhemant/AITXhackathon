"""Printable activity pages pilot (/printables/<slug>/): pages, hub links, sitemap."""

import json
import re
import unittest

from busyparent_agent.web import PRINTABLES_ROOT, _safe_printables_path

PILOT = ("scavenger-hunt", "animal-bingo", "zoo-day-journal")
SITE = "https://kidzookit.com"


class PrintablePagesTests(unittest.TestCase):
    def _html(self, slug):
        f = _safe_printables_path(f"/printables/{slug}/")
        self.assertIsNotNone(f, slug)
        return f.read_text(encoding="utf-8")

    def test_pages_resolve_with_own_seo(self):
        titles = set()
        for slug in PILOT:
            html = self._html(slug)
            self.assertIn(f'<link rel="canonical" href="{SITE}/printables/{slug}/" />', html)
            self.assertIn(f'<meta property="og:image" content="{SITE}/printables/img/{slug}.png" />', html)
            self.assertIn('name="twitter:card" content="summary_large_image"', html)
            self.assertEqual(html.count("<h1>"), 1)
            titles.add(re.search(r"<title>(.*?)</title>", html).group(1))
            ld = re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', html, re.S).group(1)
            json.loads(ld)
        self.assertEqual(len(titles), 3)

    def test_pages_link_existing_pdfs_and_next_step(self):
        for slug in PILOT:
            html = self._html(slug)
            for rel in (f"pdf/letter/{slug}.pdf", f"pdf/a4/{slug}-a4.pdf"):
                self.assertIn(f'href="/printables/{rel}"', html)
                self.assertIsNotNone(_safe_printables_path(f"/printables/{rel}"), rel)
            self.assertIn('id="next"', html)
            self.assertIn("Just finished? Next step", html)
            for href in re.findall(r'href="(/printables/[^"#]+)"', html):
                self.assertIsNotNone(_safe_printables_path(href), f"{slug}: {href}")

    def test_print_buttons_come_before_preview(self):
        """Print buttons sit above the preview image so phones see them on the first screen."""
        for slug in PILOT:
            html = self._html(slug)
            h1 = html.index("</h1>")
            bar = html.index('class="printbar"')
            letter = html.index(f'href="/printables/pdf/letter/{slug}.pdf"')
            a4 = html.index(f'href="/printables/pdf/a4/{slug}-a4.pdf"')
            img = html.index('<div class="hero">')
            self.assertTrue(h1 < bar < letter < a4 < img, slug)
            # exactly one Letter and one A4 print button (no duplicates that would double-count)
            self.assertEqual(html.count('class="btn" href="/printables/pdf/letter/'), 1, slug)
            self.assertEqual(html.count('class="btn alt" href="/printables/pdf/a4/'), 1, slug)

    def test_before_you_print_qa_is_sheet_specific(self):
        """'Before you print' Q&A: natural questions, own answers per sheet, honest about pre-readers."""
        answers = {}
        for slug in PILOT:
            html = self._html(slug)
            m = re.search(r'<section class="box faq" id="before-you-print".*?</section>', html, re.S)
            self.assertIsNotNone(m, slug)
            sec = m.group(0)
            self.assertIn('<h2 id="faq-h">Before you print</h2>', sec)
            qs = re.findall(r"<h3>(.*?)</h3>", sec)
            self.assertGreaterEqual(len(qs), 4, slug)
            for q in qs:
                self.assertTrue(q.endswith("?"), q)
            ps = re.findall(r"<p>(.*?)</p>", sec, re.S)
            self.assertEqual(len(ps), len(qs), slug)
            answers[slug] = set(ps)
            self.assertNotIn("free", sec.lower(), slug)
            # Q&A comes before the Next step box
            self.assertLess(html.index('id="before-you-print"'), html.index('id="next"'), slug)
        a, b, c = (answers[s] for s in PILOT)
        self.assertFalse(a & b or a & c or b & c, "an answer is pasted on more than one sheet page")

    def test_pages_use_shell_and_no_free_hook(self):
        for slug in PILOT:
            html = self._html(slug)
            self.assertIn("/shell/shell.js", html)
            self.assertIn("oneless-shell", html)
            self.assertNotIn("free", html.lower(), slug)

    def test_hub_links_pilot_pages_and_has_social_preview(self):
        html = (PRINTABLES_ROOT / "index.html").read_text(encoding="utf-8")
        for slug in PILOT:
            self.assertIn(f'href="/printables/{slug}/"', html)
        self.assertIn('property="og:image"', html)
        self.assertIn('name="twitter:card"', html)

    def test_sitemap_lists_pilot_pages(self):
        root = PRINTABLES_ROOT.parent
        for name in ("sitemap.xml", "field-pack/sitemap.xml"):
            sm = (root / name).read_text(encoding="utf-8")
            for slug in PILOT:
                self.assertIn(f"<loc>{SITE}/printables/{slug}/</loc>", sm, name)


if __name__ == "__main__":
    unittest.main()
