"""Friendly 404 page and slashless directory 301s that keep the query string."""

from __future__ import annotations

import io
import unittest

from busyparent_agent.web import WebHandler, _index_dir_slash_redirect


class _Handler(WebHandler):
    def __init__(self, path: str, command: str = "GET"):
        self.path = path
        self.command = command
        self.headers = {}
        self.code = None
        self.sent = {}
        self.wfile = io.BytesIO()

    def send_response(self, code, message=None):
        self.code = code

    def send_header(self, key, value):
        self.sent[key] = value

    def end_headers(self):
        return

    def log_message(self, format, *args):
        return


QS = "utm_source=printable&utm_medium=qr&utm_campaign=chaperone-card"

SLASHLESS_INDEXES = (
    "/field-pack/sequoia",
    "/field-pack/taronga-zoo",
    "/field-pack/cards",
    "/field-pack/zoos",
    "/field-pack/aquariums",
    "/field-pack/museums",
    "/field-pack/amnh",
)


class DirSlashAndFriendly404Tests(unittest.TestCase):
    def test_slashless_place_and_hub_paths_301_and_keep_query(self):
        for bare in SLASHLESS_INDEXES:
            for method, command in (("do_GET", "GET"), ("do_HEAD", "HEAD")):
                with self.subTest(path=bare, method=method):
                    h = _Handler(f"{bare}?{QS}", command=command)
                    getattr(h, method)()
                    self.assertEqual(h.code, 301, bare)
                    self.assertEqual(h.sent["Location"], f"{bare}/?{QS}")

    def test_slashless_paths_without_query_stay_clean(self):
        for bare in SLASHLESS_INDEXES:
            h = _Handler(bare)
            h.do_GET()
            self.assertEqual(h.code, 301, bare)
            self.assertEqual(h.sent["Location"], f"{bare}/")

    def test_slashed_targets_still_200(self):
        for bare in SLASHLESS_INDEXES:
            h = _Handler(f"{bare}/?{QS}")
            h.do_GET()
            self.assertEqual(h.code, 200, bare)

    def test_suffixed_assets_are_not_redirected(self):
        for path in (
            "/field-pack/js/virtual-venue.js",
            "/llms.txt",
            "/sitemap.xml",
        ):
            self.assertIsNone(_index_dir_slash_redirect(path), path)
        h = _Handler("/llms.txt")
        h.do_GET()
        self.assertEqual(h.code, 200)
        self.assertNotIn("Location", h.sent)

    def test_existing_hub_slash_redirects_still_work(self):
        h = _Handler(f"/about?{QS}")
        h.do_GET()
        self.assertEqual(h.code, 301)
        self.assertEqual(h.sent["Location"], f"/about/?{QS}")

    def test_friendly_404_keeps_status_and_links_home(self):
        h = _Handler("/this-page-does-not-exist-kz-seo")
        h.do_GET()
        self.assertEqual(h.code, 404)
        body = h.wfile.getvalue().decode("utf-8")
        self.assertNotIn("Error response", body)
        self.assertIn("Page not found | KidZooKit", body)
        self.assertIn('href="/start/"', body)
        self.assertIn('href="/field-pack/cards/"', body)
        self.assertIn('href="/printables/"', body)
        self.assertIn('href="/field-pack/"', body)
        self.assertIn("noindex", body)
        self.assertNotRegex(body, r"\bfree\b|\bno-cost\b")
        self.assertEqual(h.sent.get("X-Robots-Tag"), "noindex")

    def test_head_404_has_no_body(self):
        h = _Handler("/this-page-does-not-exist-kz-seo", command="HEAD")
        h.do_HEAD()
        self.assertEqual(h.code, 404)
        self.assertEqual(h.wfile.getvalue(), b"")

    def test_non_404_errors_stay_stock(self):
        h = _Handler("/api/chat")
        # Real send_error for 400 should not use the friendly HTML page.
        # Call it directly with a 400 so we do not have to POST.
        try:
            h.send_error(400, "Invalid JSON")
        except Exception:
            # Stock handler may try to flush a log line; body still matters.
            pass
        body = h.wfile.getvalue().decode("utf-8", "replace")
        self.assertEqual(h.code, 400)
        self.assertNotIn("This page isn’t here", body)


if __name__ == "__main__":
    unittest.main()
