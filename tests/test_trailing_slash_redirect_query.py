"""Bare hub paths 301 to the trailing-slash URL and keep the query string.

Printed QR codes and shared links carry utm_* params; a redirect must not drop them.
"""

from __future__ import annotations

import io
import unittest

from busyparent_agent.web import WebHandler


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


QS = "utm_source=printable&utm_medium=qr&utm_campaign=chaperone-card"


class TrailingSlashRedirectQueryTests(unittest.TestCase):
    def test_bare_hub_paths_keep_query_on_get_and_head(self):
        for bare in ("/printables", "/field-pack", "/start", "/about"):
            for method in ("do_GET", "do_HEAD"):
                with self.subTest(path=bare, method=method):
                    h = _Handler(f"{bare}?{QS}")
                    getattr(h, method)()
                    self.assertEqual(h.code, 301)
                    self.assertEqual(h.sent["Location"], f"{bare}/?{QS}")

    def test_bare_hub_paths_without_query_stay_clean(self):
        for bare in ("/printables", "/field-pack", "/start", "/about"):
            for method in ("do_GET", "do_HEAD"):
                with self.subTest(path=bare, method=method):
                    h = _Handler(bare)
                    getattr(h, method)()
                    self.assertEqual(h.code, 301)
                    self.assertEqual(h.sent["Location"], f"{bare}/")

    def test_redirect_target_is_never_a_loop(self):
        for bare in ("/printables", "/field-pack", "/start", "/about"):
            h = _Handler(f"{bare}/?{QS}")
            h.do_GET()
            self.assertEqual(h.code, 200, bare)


if __name__ == "__main__":
    unittest.main()
