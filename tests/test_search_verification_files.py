"""Bing Webmaster ownership + IndexNow key (2026-10-30). Both must stay forever."""
from __future__ import annotations

import http.client
import re
import threading
import unittest
from pathlib import Path

from busyparent_agent.web import INDEXNOW_KEY, KidZooKitServer, WebHandler

REPO = Path(__file__).resolve().parents[1]
BING = '<?xml version="1.0"?>\n<users>\n\t<user>E63AEF0E1192E12B426013FB51D3B60B</user>\n</users>\n'


class SearchVerificationFilesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = KidZooKitServer(("127.0.0.1", 0), WebHandler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        conn.request("GET", path, headers={"User-Agent": "Mozilla/5.0"})
        r = conn.getresponse()
        body = r.read()
        conn.close()
        return r, body

    def test_bing_site_auth(self):
        r, body = self._get("/BingSiteAuth.xml")
        self.assertEqual(r.status, 200)
        self.assertIn("xml", r.getheader("Content-Type"))
        self.assertEqual(body.decode("utf-8"), BING)

    def test_indexnow_key_file(self):
        self.assertRegex(INDEXNOW_KEY, r"^[0-9a-f]{32}$")
        r, body = self._get(f"/{INDEXNOW_KEY}.txt")
        self.assertEqual(r.status, 200)
        self.assertTrue(r.getheader("Content-Type").startswith("text/plain"))
        self.assertEqual(body.decode("utf-8").strip(), INDEXNOW_KEY)

    def test_other_root_txt_not_served(self):
        r, _ = self._get("/00000000000000000000000000000000.txt")
        self.assertEqual(r.status, 404)

    def test_msvalidate_meta_on_start(self):
        html = (REPO / "static" / "start" / "index.html").read_text(encoding="utf-8")
        head = html.split("</head>", 1)[0]
        self.assertIn('<meta name="msvalidate.01" content="E63AEF0E1192E12B426013FB51D3B60B" />', head)

    def test_ping_script_reads_key(self):
        src = (REPO / "scripts" / "indexnow_ping.py").read_text(encoding="utf-8")
        self.assertIn("api.indexnow.org/indexnow", src)


if __name__ == "__main__":
    unittest.main()
