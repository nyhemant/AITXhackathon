"""Static /printables/ mount: hub page, PDFs, shell + GA4 loader."""

from pathlib import Path
import unittest

from busyparent_agent.web import PRINTABLES_ROOT, _safe_printables_path, _static_content_type

PDFS = ("scavenger-hunt", "animal-bingo", "carpool", "teacher-handout")


class PrintablesTests(unittest.TestCase):
    def test_hub_resolves(self):
        self.assertEqual(_safe_printables_path("/printables/"), (PRINTABLES_ROOT / "index.html").resolve())

    def test_pdfs_resolve_with_pdf_type(self):
        for name in PDFS:
            f = _safe_printables_path(f"/printables/pdf/{name}.pdf")
            self.assertIsNotNone(f)
            self.assertEqual(_static_content_type(f), "application/pdf")

    def test_traversal_blocked(self):
        self.assertIsNone(_safe_printables_path("/printables/../web.py"))

    def test_hub_uses_shell_for_ga4(self):
        html = (PRINTABLES_ROOT / "index.html").read_text()
        self.assertIn("/shell/shell.js", html)
        self.assertIn("oneless-shell", html)


if __name__ == "__main__":
    unittest.main()
