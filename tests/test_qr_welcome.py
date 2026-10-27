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

    def test_version_bumped_everywhere(self):
        for rel in QR_PAGES + PRINT_PAGES:
            html = (STATIC / rel / "index.html").read_text(encoding="utf-8")
            self.assertIn("/shell/qr-welcome.js?v=3", html, rel)

    def test_scavenger_hunt_strip_reads_fine_mid_visit(self):
        js = JS.read_text(encoding="utf-8")
        m = re.search(r'"scavenger-hunt": \["([^"]+)", "([^"]+)", "([^"]+)"\]', js)
        self.assertIsNotNone(m)
        lead, button, href = m.groups()
        self.assertNotIn("Finished", lead)
        self.assertEqual(button, "Pick a zoo hunt for next time")
        self.assertEqual(href, "/printables/scavenger-hunt/#next")

    def test_generator_emits_tag_on_hubs_it_writes(self):
        import sys
        import tempfile
        from unittest import mock
        sys.path.insert(0, str(STATIC.parent / "scripts"))
        import generate_bdo_seo as g
        self.assertEqual(g.qr_welcome_tag(), '<script src="/shell/qr-welcome.js?v=3"></script>')
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(g, "FIELD", Path(tmp)):
            for meta in g.TYPE_LANDINGS:
                g.write_type_landing(meta, [])
                html = (Path(tmp) / meta["path"] / "index.html").read_text(encoding="utf-8")
                want = 1 if meta["path"] in g.QR_WELCOME_TYPE_LANDINGS else 0
                self.assertEqual(html.count("/shell/qr-welcome.js?v=3"), want, meta["path"])
                if want:
                    self.assertLess(html.index("/shell/shell.js"), html.index("/shell/qr-welcome.js"))
        src = (STATIC.parent / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        hub = src[src.index("def write_cards_hub("):]
        hub = hub[: hub.index("\ndef ")]
        self.assertIn("{qr_welcome_tag()}", hub)


if __name__ == "__main__":
    unittest.main()
