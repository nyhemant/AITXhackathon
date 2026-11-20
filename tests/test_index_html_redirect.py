"""A directory's /index.html used to be a second 200 for the same page. It now 301s to the directory URL."""

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
PAIRS = {
    "/field-pack/index.html": "/field-pack/",
    "/field-pack/zoos/index.html": "/field-pack/zoos/",
    "/field-pack/bronx-zoo/index.html": "/field-pack/bronx-zoo/",
    "/field-pack/cards/index.html": "/field-pack/cards/",
    "/field-pack/cards/african-lion/index.html": "/field-pack/cards/african-lion/",
    "/printables/index.html": "/printables/",
    "/printables/scavenger-hunt/index.html": "/printables/scavenger-hunt/",
    "/start/index.html": "/start/",
    "/about/index.html": "/about/",
    "/privacy/index.html": "/privacy/",
}


class IndexHtmlRedirectTests(unittest.TestCase):
    def test_index_html_301s_to_directory_on_get_and_head_keeping_query(self):
        for src, dest in PAIRS.items():
            for method in ("do_GET", "do_HEAD"):
                for query in ("", "?" + QS):
                    with self.subTest(path=src, method=method, query=query):
                        h = _Handler(src + query)
                        getattr(h, method)()
                        self.assertEqual(h.code, 301)
                        self.assertEqual(h.sent["Location"], dest + query)

    def test_directory_url_still_serves_200(self):
        for dest in PAIRS.values():
            with self.subTest(path=dest):
                h = _Handler(dest)
                h.do_GET()
                self.assertEqual(h.code, 200)

    def test_root_index_html_keeps_its_own_redirect_to_start(self):
        h = _Handler("/index.html")
        h.do_GET()
        self.assertEqual(h.code, 301)
        self.assertTrue(h.sent["Location"].endswith("/start/"))

    def test_unknown_index_html_is_not_redirected(self):
        h = _Handler("/field-pack/no-such-place-xyz/index.html")
        h.do_GET()
        self.assertEqual(h.code, 404)


if __name__ == "__main__":
    unittest.main()
