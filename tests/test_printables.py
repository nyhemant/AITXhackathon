"""Static /printables/ mount: hub page, PDFs, shell + GA4 loader."""

from pathlib import Path
import unittest

from busyparent_agent.web import PRINTABLES_ROOT, _safe_printables_path, _static_content_type

PDFS = ("scavenger-hunt", "animal-bingo", "carpool", "teacher-handout")
V2_SLUGS = (
    "scavenger-hunt",
    "park-scavenger-hunt",
    "animal-bingo",
    "carpool",
    "teacher-handout",
    "zoo-day-journal",
    "chaperone-card",
)


class PrintablesTests(unittest.TestCase):
    def test_hub_resolves(self):
        self.assertEqual(_safe_printables_path("/printables/"), (PRINTABLES_ROOT / "index.html").resolve())

    def test_pdfs_resolve_with_pdf_type(self):
        for name in PDFS:
            f = _safe_printables_path(f"/printables/pdf/{name}.pdf")
            self.assertIsNotNone(f)
            self.assertEqual(_static_content_type(f), "application/pdf")

    def test_v2_letter_and_a4_pdfs_resolve_and_are_pdfs(self):
        for slug in V2_SLUGS:
            for rel in (f"pdf/letter/{slug}.pdf", f"pdf/a4/{slug}-a4.pdf"):
                f = _safe_printables_path(f"/printables/{rel}")
                self.assertIsNotNone(f, rel)
                self.assertEqual(_static_content_type(f), "application/pdf")
                self.assertTrue(f.read_bytes().startswith(b"%PDF"), rel)

    def test_hub_links_every_v2_pdf_and_sections(self):
        html = (PRINTABLES_ROOT / "index.html").read_text()
        for slug in V2_SLUGS:
            self.assertIn(f'href="pdf/letter/{slug}.pdf"', html)
            self.assertIn(f'href="pdf/a4/{slug}-a4.pdf"', html)
            self.assertTrue(_safe_printables_path(f"/printables/img/{slug}.png"))
        self.assertEqual(html.count('class="card spot"'), 3)
        self.assertEqual(html.count("<li><div>"), 4)
        self.assertIn("More printables", html)

    def test_sitemap_lists_printables(self):
        sitemap = (PRINTABLES_ROOT.parent / "sitemap.xml").read_text()
        self.assertIn("<loc>https://kidzookit.com/printables/</loc>", sitemap)

    def test_traversal_blocked(self):
        self.assertIsNone(_safe_printables_path("/printables/../web.py"))

    def test_hub_uses_shell_for_ga4(self):
        html = (PRINTABLES_ROOT / "index.html").read_text()
        self.assertIn("/shell/shell.js", html)
        self.assertIn("oneless-shell", html)


if __name__ == "__main__":
    unittest.main()


class PrintablesIntegrationTests(unittest.TestCase):
    def test_printables_linked_from_start_and_hubs(self):
        root = Path(__file__).resolve().parents[1] / "static"
        start = (root / "start" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<a href="/printables/">Printables</a>', start)
        self.assertIn('class="start-printables" href="/printables/"', start)
        for rel in ("field-pack", "field-pack/zoos", "field-pack/aquariums", "field-pack/museums", "field-pack/national-parks"):
            html = (root / rel / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="/printables/"', html, rel)
        for rel in ("field-pack", "about"):
            html = (root / rel / "index.html").read_text(encoding="utf-8")
            self.assertIn('<a href="/printables/" role="menuitem">Printables</a>', html, rel)


class PrintablesWordingTests(unittest.TestCase):
    def test_no_free_wording_and_new_copy(self):
        html = (PRINTABLES_ROOT / "index.html").read_text()
        self.assertNotIn("free", html.lower())
        self.assertIn("<h1>Play &amp; Learn Printables for Kids</h1>", html)
        self.assertIn("For home and classroom use; please link rather than re-host.", html)
        start = (PRINTABLES_ROOT.parent / "start" / "index.html").read_text()
        self.assertNotIn("Free printables", start)
        self.assertIn("<strong>Play &amp; learn printables</strong>", start)
