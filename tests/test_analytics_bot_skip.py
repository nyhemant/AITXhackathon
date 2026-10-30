"""Bot / self-traffic skip (2026-10-30).

- shell.js skips GA4 for navigator.webdriver, headless/automation/crawler UAs and
  ?notrack=1 (which also persists the opt-out like ?analytics=off).
- The server answers ?notrack=1 HTML with the same one_less_analytics=off cookie as
  /analytics/off, and gives skipped-tracking HTML (cookie off, ?notrack=1, headless
  UA) Cache-Control no-transform so Cloudflare does not inject its beacon, plus a
  CSP without the beacon host. Normal visitors and search crawlers are unchanged.
"""
from __future__ import annotations

import http.client
import threading
import unittest
from pathlib import Path

from busyparent_agent.web import (
    CLOUDFLARE_BEACON_SCRIPT_HOST,
    KidZooKitServer,
    WebHandler,
    _is_automation_ua,
    _query_wants_notrack,
    _tracking_skipped,
)

REPO = Path(__file__).resolve().parents[1]
SHELL_JS = (REPO / "static" / "shell" / "shell.js").read_text(encoding="utf-8")

CHROME = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
)
HEADLESS = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "HeadlessChrome/141.0.0.0 Safari/537.36"
)
GOOGLEBOT = (
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0 Mobile Safari/537.36 "
    "(compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
)


class ShellJsSkipTest(unittest.TestCase):
    def test_webdriver_and_ua_skip(self):
        self.assertIn("navigator.webdriver === true", SHELL_JS)
        self.assertIn("HeadlessChrome", SHELL_JS)
        self.assertIn("Googlebot", SHELL_JS)
        self.assertIn("if (isAutomatedVisitor()) return true;", SHELL_JS)

    def test_notrack_param_persists_opt_out(self):
        self.assertIn('q.get("notrack") === "1"', SHELL_JS)

    def test_page_print_event_is_enum_only(self):
        self.assertIn('track("page_print", { page_kind: pageKind() });', SHELL_JS)
        self.assertIn('addEventListener("beforeprint", sendPagePrint)', SHELL_JS)


class HelperTest(unittest.TestCase):
    def test_helpers(self):
        self.assertTrue(_query_wants_notrack("/start/?notrack=1"))
        self.assertTrue(_query_wants_notrack("/start/?utm_source=printable&notrack=1"))
        self.assertFalse(_query_wants_notrack("/start/?notrack=0"))
        self.assertFalse(_query_wants_notrack("/start/"))
        self.assertTrue(_is_automation_ua(HEADLESS))
        self.assertFalse(_is_automation_ua(CHROME))
        self.assertFalse(_is_automation_ua(GOOGLEBOT))
        self.assertTrue(_tracking_skipped("one_less_analytics=off", CHROME, "/start/"))
        self.assertFalse(_tracking_skipped(None, CHROME, "/start/"))


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = KidZooKitServer(("127.0.0.1", 0), WebHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path, ua=CHROME, cookie=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        headers = {"User-Agent": ua}
        if cookie:
            headers["Cookie"] = cookie
        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()
        resp.read()
        conn.close()
        return resp

    def test_normal_visitor_unchanged(self):
        r = self._get("/start/")
        self.assertEqual(r.status, 200)
        self.assertNotIn("no-transform", r.getheader("Cache-Control") or "")
        self.assertIsNone(r.getheader("Set-Cookie"))
        self.assertIn(CLOUDFLARE_BEACON_SCRIPT_HOST, r.getheader("Content-Security-Policy"))

    def test_search_crawler_unchanged(self):
        r = self._get("/field-pack/cards/whale-shark/", ua=GOOGLEBOT)
        self.assertEqual(r.status, 200)
        self.assertNotIn("no-transform", r.getheader("Cache-Control") or "")
        self.assertIn(CLOUDFLARE_BEACON_SCRIPT_HOST, r.getheader("Content-Security-Policy"))

    def test_notrack_sets_opt_out_cookie_and_no_transform(self):
        r = self._get("/start/?notrack=1")
        self.assertEqual(r.status, 200)
        self.assertIn("one_less_analytics=off", r.getheader("Set-Cookie") or "")
        self.assertIn("no-transform", r.getheader("Cache-Control") or "")
        self.assertNotIn(CLOUDFLARE_BEACON_SCRIPT_HOST, r.getheader("Content-Security-Policy"))

    def test_headless_html_no_transform_but_assets_untouched(self):
        r = self._get("/field-pack/cards/whale-shark/", ua=HEADLESS)
        self.assertIn("no-transform", r.getheader("Cache-Control") or "")
        self.assertIsNone(r.getheader("Set-Cookie"))
        a = self._get("/shell/shell.js?v=6", ua=HEADLESS)
        self.assertEqual(a.status, 200)
        self.assertNotIn("no-transform", a.getheader("Cache-Control") or "")

    def test_cookie_opt_out_no_transform_without_new_cookie(self):
        r = self._get("/about/", cookie="one_less_analytics=off")
        self.assertIn("no-transform", r.getheader("Cache-Control") or "")
        self.assertIsNone(r.getheader("Set-Cookie"))

    def test_notrack_redirect_keeps_query(self):
        r = self._get("/start?notrack=1&utm_source=printable")
        self.assertEqual(r.status, 301)
        self.assertEqual(r.getheader("Location"), "/start/?notrack=1&utm_source=printable")


if __name__ == "__main__":
    unittest.main()
