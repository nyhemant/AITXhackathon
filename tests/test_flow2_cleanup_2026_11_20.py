"""2026-11-20 round 2: unused files removed; the old sitemap copy URL forwards."""

from __future__ import annotations

import io
import unittest
from pathlib import Path

from busyparent_agent.web import WebHandler

ROOT = Path(__file__).resolve().parents[1]
START = ROOT / "static" / "start"


class _Handler(WebHandler):
    def __init__(self, path: str):
        self.path = path
        self.headers = {}
        self.code = None
        self.sent = {}
        self.wfile = io.BytesIO()

    def send_response(self, code, message=None):
        self.code = code

    def send_error(self, code, message=None):
        self.code = code

    def send_header(self, key, value):
        self.sent[key] = value

    def end_headers(self):
        return

    def log_message(self, format, *args):
        return


class Flow2Cleanup(unittest.TestCase):
    def test_old_sitemap_copy_301s_to_the_root_sitemap(self):
        for method in ("do_GET", "do_HEAD"):
            h = _Handler("/field-pack/sitemap.xml")
            getattr(h, method)()
            self.assertEqual(h.code, 301, method)
            self.assertEqual(h.sent["Location"], "/sitemap.xml", method)

    def test_root_sitemap_still_200(self):
        h = _Handler("/sitemap.xml")
        h.do_GET()
        self.assertEqual(h.code, 200)
        self.assertIn(b"<urlset", h.wfile.getvalue())

    def test_unused_start_files_are_gone(self):
        gone = ["home-map-v1.js", "home-map-v2.css", "map-v2-a-v1.css"]
        for name in ("koala", "tiger", "zebra"):
            gone += [f"playing-card-{name}.png", f"playing-card-{name}-240-v1.webp", f"playing-card-{name}-360-v1.webp"]
        for name in gone:
            self.assertFalse((START / name).exists(), name)
        html = (START / "index.html").read_text(encoding="utf-8")
        for name in gone:
            self.assertNotIn(name, html)
        self.assertIn("/start/home-map-v2.js", html)
        self.assertIn("/start/home-map-v2-a.css", html)


if __name__ == "__main__":
    unittest.main()
