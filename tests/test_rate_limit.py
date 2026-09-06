"""In-app scrape/bot rate limits — no accounts, no email, no CAPTCHA."""

from __future__ import annotations

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import os
import threading
import unittest
from unittest import mock

from busyparent_agent.rate_limit import (
    BOT_UA_NEEDLES,
    DEFAULT_LIMITS,
    FRIENDLY_UA_NEEDLES,
    RateLimiter,
    classify_path,
    env_flag,
    evaluate_request,
    limits_from_env,
    peer_is_trusted,
    reset_limiter,
    resolve_client_ip,
    set_limiter,
    ua_looks_like_bot,
)
from busyparent_agent.web import WebHandler


class ClassifyPathTests(unittest.TestCase):
    def test_pages(self):
        for path in (
            "/",
            "/field-pack/",
            "/field-pack/dallas-zoo/",
            "/field-pack/dallas-zoo/index.html",
            "/start/",
            "/about/",
            "/dinner",
        ):
            self.assertEqual(classify_path(path), "pages", path)

    def test_catalog(self):
        for path in (
            "/field-pack/js/catalog.js",
            "/field-pack/js/places-data.js",
            "/field-pack/seo-venues.json",
            "/field-pack/data/venues/dallas-zoo.json",
            "/field-pack/data/virtual-venues/zoos.json",
        ):
            self.assertEqual(classify_path(path), "catalog", path)

    def test_images(self):
        for path in (
            "/field-pack/photos/np-hero-yellowstone.jpg",
            "/1LessMark.png",
            "/field-pack/photos/sample.webp",
        ):
            self.assertEqual(classify_path(path), "images", path)

    def test_print(self):
        for path in (
            "/field-pack/js/print-kit.js",
            "/field-pack/js/print-maps.js",
            "/field-pack/css/print.css",
            "/field-pack/media/maps/yellowstone.jpg",
        ):
            self.assertEqual(classify_path(path), "print", path)

    def test_api_and_other_and_exempt(self):
        self.assertEqual(classify_path("/api/chat"), "api")
        self.assertEqual(classify_path("/api/preview"), "api")
        self.assertEqual(classify_path("/field-pack/css/landing.css"), "other")
        self.assertEqual(classify_path("/robots.txt"), "exempt")
        self.assertEqual(classify_path("/analytics/off"), "exempt")


class UserAgentTests(unittest.TestCase):
    def test_empty_and_scrapers_are_bots(self):
        self.assertTrue(ua_looks_like_bot(""))
        self.assertTrue(ua_looks_like_bot("Wget/1.21"))
        self.assertTrue(ua_looks_like_bot("python-requests/2.32.0"))
        self.assertTrue(ua_looks_like_bot("curl/8.7.1"))
        self.assertTrue(ua_looks_like_bot("Scrapy/2.11"))
        self.assertTrue(ua_looks_like_bot("Mozilla/5.0 (compatible; Bytespider; +https://zhanzhang.toutiao.com/)"))

    def test_ai_fetch_crawlers_are_on_family_allowlist(self):
        for needle in (
            "gptbot",
            "claudebot",
            "claude-web",
            "anthropic-ai",
            "perplexitybot",
            "chatgpt-user",
            "google-extended",
        ):
            self.assertIn(needle, FRIENDLY_UA_NEEDLES)
            self.assertNotIn(needle, BOT_UA_NEEDLES)
        self.assertNotIn("anthropic", BOT_UA_NEEDLES)
        self.assertIn("bytespider", BOT_UA_NEEDLES)

        for ua in (
            "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
            "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
            "Claude-Web",
            "anthropic-ai",
            "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
            "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot",
            "Google-Extended",
        ):
            self.assertFalse(ua_looks_like_bot(ua), ua)

    def test_browsers_and_googlebot_are_not_tightened(self):
        self.assertFalse(
            ua_looks_like_bot(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            )
        )
        self.assertFalse(
            ua_looks_like_bot("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")
        )


class ClientIpTests(unittest.TestCase):
    def test_trusts_cf_connecting_ip_from_loopback(self):
        ip = resolve_client_ip(
            "127.0.0.1",
            {"CF-Connecting-IP": "203.0.113.9", "User-Agent": "Safari"},
            trust_proxy=True,
        )
        self.assertEqual(ip, "203.0.113.9")

    def test_trusts_xff_first_hop_from_private_peer(self):
        ip = resolve_client_ip(
            "192.168.1.4",
            {"X-Forwarded-For": "198.51.100.10, 172.16.0.2"},
            trust_proxy=True,
        )
        self.assertEqual(ip, "198.51.100.10")

    def test_ignores_spoofed_forwarded_headers_from_public_peer(self):
        ip = resolve_client_ip(
            "203.0.113.50",
            {"CF-Connecting-IP": "198.51.100.1", "X-Forwarded-For": "198.51.100.1"},
            trust_proxy=True,
        )
        self.assertEqual(ip, "203.0.113.50")

    def test_ipv6_mapped_loopback_is_trusted(self):
        self.assertTrue(peer_is_trusted("::ffff:127.0.0.1"))
        ip = resolve_client_ip(
            "::ffff:127.0.0.1",
            {"cf-connecting-ip": "2001:db8::1"},
            trust_proxy=True,
        )
        self.assertEqual(ip, "2001:db8::1")


class SlidingWindowTests(unittest.TestCase):
    def test_allows_then_denies_with_retry_after(self):
        clock = {"now": 1000.0}
        limiter = RateLimiter(
            enabled=True,
            limits={**DEFAULT_LIMITS, "pages": 3, "overall": 100},
            window_seconds=60,
            bot_ua=False,
            clock=lambda: clock["now"],
        )
        for _ in range(3):
            decision = limiter.check(ip="203.0.113.2", path="/field-pack/", user_agent="Safari")
            self.assertTrue(decision.allowed)
        denied = limiter.check(ip="203.0.113.2", path="/field-pack/dallas-zoo/", user_agent="Safari")
        self.assertFalse(denied.allowed)
        self.assertEqual(denied.bucket, "pages")
        self.assertGreaterEqual(denied.retry_after, 1)
        self.assertEqual(limiter.stats.limited, 1)

        clock["now"] = 1061.0
        later = limiter.check(ip="203.0.113.2", path="/field-pack/", user_agent="Safari")
        self.assertTrue(later.allowed)

    def test_buckets_are_independent(self):
        limiter = RateLimiter(
            enabled=True,
            limits={**DEFAULT_LIMITS, "pages": 1, "images": 2, "overall": 50},
            window_seconds=60,
            bot_ua=False,
        )
        self.assertTrue(limiter.check(ip="10.0.0.2", path="/field-pack/").allowed)
        self.assertFalse(limiter.check(ip="10.0.0.2", path="/start/").allowed)
        self.assertTrue(
            limiter.check(ip="10.0.0.2", path="/field-pack/photos/np-hero-yellowstone.jpg").allowed
        )

    def test_other_ips_do_not_share_budget(self):
        limiter = RateLimiter(
            enabled=True,
            limits={**DEFAULT_LIMITS, "pages": 1, "overall": 50},
            window_seconds=60,
            bot_ua=False,
        )
        self.assertTrue(limiter.check(ip="10.0.0.3", path="/field-pack/").allowed)
        self.assertTrue(limiter.check(ip="10.0.0.4", path="/field-pack/").allowed)

    def test_disabled_never_rejects(self):
        limiter = RateLimiter(enabled=False, limits={**DEFAULT_LIMITS, "pages": 1})
        for _ in range(8):
            decision = limiter.check(ip="10.0.0.5", path="/field-pack/")
            self.assertTrue(decision.allowed)
            self.assertTrue(decision.skipped)

    def test_missing_ip_is_skipped_for_fake_handlers(self):
        limiter = RateLimiter(enabled=True, limits={**DEFAULT_LIMITS, "pages": 1})
        for _ in range(5):
            decision = limiter.check(ip=None, path="/field-pack/")
            self.assertTrue(decision.allowed)
            self.assertTrue(decision.skipped)

    def test_exempt_robots_never_counts(self):
        limiter = RateLimiter(enabled=True, limits={**DEFAULT_LIMITS, "other": 1, "overall": 1})
        for _ in range(6):
            self.assertTrue(limiter.check(ip="10.0.0.6", path="/robots.txt").allowed)
        self.assertEqual(limiter.stats.limited, 0)

    def test_bot_ua_gets_tighter_budget(self):
        limiter = RateLimiter(
            enabled=True,
            limits={**DEFAULT_LIMITS, "pages": 40, "overall": 400},
            window_seconds=60,
            bot_ua=True,
            bot_factor=0.25,
        )
        # 40 * 0.25 = 10, floor is 8 → 10 page hits for wget
        allowed = 0
        denied = 0
        for _ in range(12):
            decision = limiter.check(ip="10.0.0.7", path="/field-pack/", user_agent="Wget/1.21")
            if decision.allowed:
                allowed += 1
            else:
                denied += 1
        self.assertEqual(allowed, 10)
        self.assertEqual(denied, 2)

        browser = RateLimiter(
            enabled=True,
            limits={**DEFAULT_LIMITS, "pages": 40, "overall": 400},
            window_seconds=60,
            bot_ua=True,
            bot_factor=0.25,
        )
        for _ in range(12):
            self.assertTrue(
                browser.check(
                    ip="10.0.0.8",
                    path="/field-pack/",
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15",
                ).allowed
            )

    def test_googlebot_and_ai_crawlers_keep_family_budget(self):
        agents = (
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)",
            "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)",
            "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)",
        )
        for index, ua in enumerate(agents):
            limiter = RateLimiter(
                enabled=True,
                limits={**DEFAULT_LIMITS, "pages": 12, "overall": 100},
                window_seconds=60,
                bot_ua=True,
                bot_factor=0.25,
            )
            for _ in range(12):
                self.assertTrue(
                    limiter.check(
                        ip=f"10.0.0.{10 + index}",
                        path="/field-pack/",
                        user_agent=ua,
                    ).allowed,
                    ua,
                )

    def test_classroom_default_pages_budget(self):
        limiter = RateLimiter.from_env()
        # 30 kids × 4 HTML pages in a minute stays under the 180 default.
        for i in range(120):
            decision = limiter.check(
                ip="10.20.30.40",
                path="/field-pack/dallas-zoo/" if i % 2 == 0 else "/field-pack/",
                user_agent="Mozilla/5.0 ClassroomSafari",
            )
            self.assertTrue(decision.allowed, f"classroom hit {i} was limited")

    def test_include_ua_splits_keys(self):
        limiter = RateLimiter(
            enabled=True,
            limits={**DEFAULT_LIMITS, "pages": 1, "overall": 50},
            window_seconds=60,
            bot_ua=False,
            include_ua=True,
        )
        self.assertTrue(limiter.check(ip="10.0.0.11", path="/field-pack/", user_agent="Safari").allowed)
        self.assertTrue(limiter.check(ip="10.0.0.11", path="/field-pack/", user_agent="Chrome").allowed)
        self.assertFalse(limiter.check(ip="10.0.0.11", path="/field-pack/", user_agent="Safari").allowed)


class EnvConfigTests(unittest.TestCase):
    def test_disable_flag(self):
        self.assertTrue(env_flag("ONELESS_RATE_LIMIT_MISSING", True))
        with mock.patch.dict(os.environ, {"ONELESS_RATE_LIMIT": "0"}):
            self.assertFalse(env_flag("ONELESS_RATE_LIMIT", True))
        with mock.patch.dict(os.environ, {"ONELESS_RATE_LIMIT": "off"}):
            self.assertFalse(env_flag("ONELESS_RATE_LIMIT", True))

    def test_limit_overrides(self):
        with mock.patch.dict(os.environ, {"ONELESS_RATE_LIMIT_PAGES": "12"}):
            limits = limits_from_env()
        self.assertEqual(limits["pages"], 12)
        self.assertEqual(limits["images"], DEFAULT_LIMITS["images"])

    def test_from_env_respects_disable(self):
        with mock.patch.dict(os.environ, {"ONELESS_RATE_LIMIT": "0"}):
            limiter = RateLimiter.from_env()
        self.assertFalse(limiter.enabled)


class ProcessLimiterTests(unittest.TestCase):
    def tearDown(self):
        reset_limiter()

    def test_evaluate_request_uses_cf_ip(self):
        set_limiter(
            RateLimiter(
                enabled=True,
                limits={**DEFAULT_LIMITS, "pages": 1, "overall": 50},
                window_seconds=60,
                bot_ua=False,
            )
        )
        first = evaluate_request(
            peer="127.0.0.1",
            headers={"CF-Connecting-IP": "198.51.100.20", "User-Agent": "Safari"},
            path="/field-pack/",
        )
        second = evaluate_request(
            peer="127.0.0.1",
            headers={"CF-Connecting-IP": "198.51.100.20", "User-Agent": "Safari"},
            path="/field-pack/",
        )
        other = evaluate_request(
            peer="127.0.0.1",
            headers={"CF-Connecting-IP": "198.51.100.21", "User-Agent": "Safari"},
            path="/field-pack/",
        )
        self.assertTrue(first.allowed)
        self.assertTrue(second.rejected)
        self.assertEqual(second.retry_after, 60)
        self.assertTrue(other.allowed)


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


class FakeHandler(WebHandler):
    def __init__(self, path, *, headers=None, client_address=None, command="GET"):
        self.path = path
        self.headers = headers or {}
        self.client_address = client_address
        self.command = command
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


class HandlerHookTests(unittest.TestCase):
    def tearDown(self):
        reset_limiter()

    def test_fake_handler_without_client_is_not_limited(self):
        set_limiter(
            RateLimiter(
                enabled=True,
                limits={**DEFAULT_LIMITS, "pages": 1, "overall": 1},
                window_seconds=60,
                bot_ua=False,
            )
        )
        for _ in range(4):
            handler = FakeHandler("/field-pack/")
            handler.do_GET()
            self.assertEqual(handler._code, 200)

    def test_fake_handler_with_client_returns_429(self):
        set_limiter(
            RateLimiter(
                enabled=True,
                limits={**DEFAULT_LIMITS, "pages": 1, "overall": 50},
                window_seconds=60,
                bot_ua=False,
            )
        )
        first = FakeHandler("/field-pack/", client_address=("203.0.113.40", 1234))
        first.do_GET()
        self.assertEqual(first._code, 200)
        second = FakeHandler("/field-pack/houston-zoo/", client_address=("203.0.113.40", 1235))
        second.do_GET()
        self.assertEqual(second._code, 429)
        self.assertEqual(second._headers.get("Retry-After"), "60")
        self.assertIn(b"Too many requests", second.wfile.getvalue())
        self.assertNotIn(b"sign up", second.wfile.getvalue().lower())
        self.assertNotIn(b"email", second.wfile.getvalue().lower())


class LiveOriginTests(unittest.TestCase):
    def setUp(self):
        set_limiter(
            RateLimiter(
                enabled=True,
                limits={**DEFAULT_LIMITS, "pages": 5, "overall": 80, "other": 80, "images": 80},
                window_seconds=60,
                bot_ua=False,
            )
        )
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), WebHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.host, self.port = self.server.server_address

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        reset_limiter()

    def _request(self, path: str, method: str = "GET", ua: str = "Mozilla/5.0 TestFamily"):
        conn = HTTPConnection(self.host, self.port, timeout=5)
        try:
            conn.request(method, path, headers={"User-Agent": ua})
            response = conn.getresponse()
            body = response.read()
            return response.status, dict(response.headers), body
        finally:
            conn.close()

    def test_family_burst_then_429_with_retry_after(self):
        codes = []
        retry_after = None
        body = b""
        for _ in range(7):
            status, headers, payload = self._request("/field-pack/")
            codes.append(status)
            if status == 429:
                retry_after = headers.get("Retry-After")
                body = payload
        self.assertEqual(codes[:5], [200, 200, 200, 200, 200])
        self.assertIn(429, codes)
        self.assertIsNotNone(retry_after)
        self.assertGreaterEqual(int(retry_after), 1)
        self.assertIn(b"Too many requests", body)
        self.assertEqual(codes.count(200), 5)

    def test_robots_stays_200_during_page_limit(self):
        for _ in range(5):
            self.assertEqual(self._request("/field-pack/")[0], 200)
        self.assertEqual(self._request("/field-pack/")[0], 429)
        self.assertEqual(self._request("/robots.txt")[0], 200)

    def test_head_429_has_no_body(self):
        for _ in range(5):
            self.assertEqual(self._request("/start/", method="HEAD")[0], 200)
        status, headers, body = self._request("/start/", method="HEAD")
        self.assertEqual(status, 429)
        self.assertTrue(headers.get("Retry-After"))
        self.assertEqual(body, b"")


class HelpFlagTests(unittest.TestCase):
    def test_help_mentions_disable_switch(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-m", "busyparent_agent.web", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("--no-rate-limit", result.stdout)
        self.assertIn("ONELESS_RATE_LIMIT", result.stdout)


if __name__ == "__main__":
    unittest.main()
