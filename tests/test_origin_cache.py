"""Origin reliability (2026-10-22): listen backlog + edge-cacheable ?v= assets.

Cloudflare re-fetched every CSS/JS file on every page view because they were
sent ``no-cache``; with the stdlib listen backlog of 5 that burst could make
Cloudflare answer 502. Versioned CSS/JS are now cacheable for a day; HTML,
unversioned files and the service worker must keep revalidating.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from busyparent_agent.web import (
    VERSIONED_ASSET_CACHE,
    KidZooKitServer,
    WebHandler,
    _is_versioned_asset,
)

REPO = Path(__file__).resolve().parents[1]
STATIC = REPO / "static"


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)


class FakeHandler(WebHandler):
    def __init__(self, path):
        self.path = path
        self.headers = {}
        self._code = None
        self._headers = {}
        self.wfile = _Buf()

    def send_response(self, code, message=None):
        self._code = code

    def send_error(self, code, message=None):
        self._code = code

    def send_header(self, k, v):
        self._headers[k] = v

    def end_headers(self):
        return

    def log_message(self, format, *args):
        return


def _get(path: str) -> FakeHandler:
    h = FakeHandler(path)
    h.do_GET()
    return h


ASSET_REF = re.compile(r"""<(?:link[^>]+href|script[^>]+src)=["']([^"']+\.(?:css|js)(?:\?[^"']*)?)["']""")


class OriginCacheTests(unittest.TestCase):
    def test_server_has_real_backlog_and_daemon_threads(self):
        self.assertGreaterEqual(KidZooKitServer.request_queue_size, 128)
        self.assertTrue(KidZooKitServer.daemon_threads)

    def test_versioned_css_js_are_edge_cacheable(self):
        for path in (
            "/field-pack/css/landing.css?v=104",
            "/shell/shell.js?v=6",
            "/start/start.css?v=79",
            "/start/start.js?v=39",
            "/field-pack/js/fp-analytics.js?v=1",
        ):
            with self.subTest(path):
                served = _get(path)
                self.assertEqual(served._code, 200, path)
                self.assertEqual(served._headers.get("Cache-Control"), VERSIONED_ASSET_CACHE)

    def test_unversioned_assets_html_and_sw_still_revalidate(self):
        for path in (
            "/field-pack/css/landing.css",
            "/field-pack/css/landing.css?cb=1",
            "/field-pack/css/landing.css?v=",
            "/shell/shell.js",
            "/field-pack/",
            "/start/",
            "/printables/",
        ):
            with self.subTest(path):
                served = _get(path)
                self.assertEqual(served._code, 200, path)
                self.assertEqual(served._headers.get("Cache-Control"), "no-cache", path)
        served = _get("/sw.js?v=5")
        self.assertEqual(served._headers.get("Cache-Control"), "no-cache")

    def test_images_keep_one_day_cache(self):
        served = _get("/pwa/icon-192.png")
        self.assertEqual(served._headers.get("Cache-Control"), "public, max-age=86400")

    def test_is_versioned_asset(self):
        p = Path("x.css")
        self.assertTrue(_is_versioned_asset("/a/x.css?v=3", p))
        self.assertTrue(_is_versioned_asset("/a/x.css?utm=1&v=3", p))
        self.assertFalse(_is_versioned_asset("/a/x.css", p))
        self.assertFalse(_is_versioned_asset("/a/x.css?v", p))
        self.assertFalse(_is_versioned_asset("/a/x.css?vv=3", p))
        self.assertFalse(_is_versioned_asset("/a/x.html?v=3", Path("x.html")))
        self.assertFalse(_is_versioned_asset("/sw.js?v=3", Path("sw.js")))

    def test_every_local_css_js_reference_is_versioned(self):
        """A missing ?v= would be served no-cache (safe but slow); a changed
        file must also bump its ?v= or visitors keep the old copy up to 1 day."""
        missing = []
        for html in STATIC.rglob("*.html"):
            text = html.read_text(encoding="utf-8", errors="ignore")
            for url in ASSET_REF.findall(text):
                if url.startswith(("http:", "https:", "//", "data:")):
                    continue
                if not re.search(r"[?&]v=[^&]+", url):
                    missing.append(f"{html.relative_to(REPO)}: {url}")
        self.assertEqual(missing, [], "CSS/JS refs without ?v=:\n" + "\n".join(missing[:20]))


if __name__ == "__main__":
    unittest.main()
