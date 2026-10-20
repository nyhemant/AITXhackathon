"""QR-scan next step strip (/shell/qr-welcome.js) and printable_download events."""

from pathlib import Path
import re
import unittest

from busyparent_agent.web import _safe_printables_path

STATIC = Path(__file__).resolve().parents[1] / "static"
JS = STATIC / "shell" / "qr-welcome.js"
QR_PAGES = ("start", "field-pack", "field-pack/zoos", "field-pack/cards", "field-pack/virtual-field-trip")
PRINT_PAGES = ("printables", "printables/scavenger-hunt", "printables/animal-bingo", "printables/zoo-day-journal")
CAMPAIGNS = ("scavenger-hunt", "park-scavenger-hunt", "animal-bingo", "carpool",
             "teacher-handout", "zoo-day-journal", "chaperone-card")


class QrWelcomeTests(unittest.TestCase):
    def test_script_loaded_after_shell_on_qr_and_printable_pages(self):
        for rel in QR_PAGES + PRINT_PAGES:
            html = (STATIC / rel / "index.html").read_text(encoding="utf-8")
            self.assertEqual(html.count("/shell/qr-welcome.js?v="), 1, rel)
            self.assertLess(html.index("/shell/shell.js"), html.index("/shell/qr-welcome.js"), rel)

    def test_every_qr_campaign_has_one_real_next_step(self):
        js = JS.read_text(encoding="utf-8")
        for c in CAMPAIGNS:
            m = re.search(r'"%s": \[[^\]]*"(/[^"]+)"\]' % re.escape(c), js)
            self.assertIsNotNone(m, c)
            path = m.group(1).split("#")[0]
            if path.startswith("/printables/"):
                self.assertIsNotNone(_safe_printables_path(path), path)
            else:
                self.assertTrue((STATIC / path.strip("/") / "index.html").is_file(), path)

    def test_quiet_and_private(self):
        js = JS.read_text(encoding="utf-8")
        self.assertIn('utm_medium") !== "qr"', js)
        self.assertIn("sessionStorage", js)
        self.assertIn(">= 2", js)  # stop after two dismissals
        for ev in ("qr_welcome_shown", "qr_welcome_click", "printable_download"):
            self.assertIn(ev, js)
        self.assertNotIn("replaceState", js)  # UTMs stay in the URL
        self.assertNotIn("free", js.lower())


if __name__ == "__main__":
    unittest.main()
