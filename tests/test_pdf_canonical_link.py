"""Printable PDFs carry an HTTP Link rel=canonical (2026-10-30).

Legacy root PDFs (/printables/pdf/X.pdf) are byte-identical to /printables/pdf/letter/X.pdf.
Both keep answering 200 (printed QR codes, old links); the header names the letter copy.
"""
from __future__ import annotations

import http.client
import threading
import unittest
from pathlib import Path

from busyparent_agent.web import KidZooKitServer, WebHandler, _pdf_canonical_link

REPO = Path(__file__).resolve().parents[1]
PDF = REPO / "static" / "printables" / "pdf"


class PdfCanonicalLinkTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = KidZooKitServer(("127.0.0.1", 0), WebHandler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _req(self, method, path):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request(method, path, headers={"User-Agent": "Mozilla/5.0"})
        r = conn.getresponse()
        r.read()
        conn.close()
        return r

    def test_legacy_root_pdfs_point_at_letter_copy(self):
        for name in ("animal-bingo.pdf", "carpool.pdf", "scavenger-hunt.pdf", "teacher-handout.pdf"):
            self.assertEqual((PDF / name).read_bytes(), (PDF / "letter" / name).read_bytes(), name)
            r = self._req("GET", f"/printables/pdf/{name}?utm_source=qr")
            self.assertEqual(r.status, 200, name)
            self.assertEqual(
                r.getheader("Link"),
                f'<https://kidzookit.com/printables/pdf/letter/{name}>; rel="canonical"',
            )

    def test_letter_and_a4_are_self_canonical(self):
        r = self._req("GET", "/printables/pdf/a4/zoo-day-journal-a4.pdf")
        self.assertEqual(r.status, 200)
        self.assertEqual(
            r.getheader("Link"),
            '<https://kidzookit.com/printables/pdf/a4/zoo-day-journal-a4.pdf>; rel="canonical"',
        )
        r = self._req("HEAD", "/printables/pdf/letter/zoo-day-journal.pdf")
        self.assertIn("letter/zoo-day-journal.pdf", r.getheader("Link") or "")

    def test_html_gets_no_link_header(self):
        r = self._req("GET", "/printables/")
        self.assertIsNone(r.getheader("Link"))

    def test_rejects_odd_paths(self):
        self.assertIsNone(_pdf_canonical_link("/printables/pdf/../x.pdf"))
        self.assertIsNone(_pdf_canonical_link("/printables/x.pdf"))
        self.assertIsNone(_pdf_canonical_link(None))


if __name__ == "__main__":
    unittest.main()
