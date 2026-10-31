"""Same-origin Kit newsletter proxy and the two signup boxes."""

from __future__ import annotations

import io
import logging
import re
import unittest
import urllib.error
from email.message import Message
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs

from busyparent_agent.newsletter import (
    KIT_FORM_SUBSCRIBE_URL,
    KIT_TIMEOUT_SECONDS,
    KitPostResult,
    NewsletterResult,
    handle_newsletter,
    parse_form_body,
    post_kit_subscription,
    reset_newsletter_limits,
    response_for,
    valid_email,
)
from busyparent_agent.web import SECURITY_HEADERS, WebHandler

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "static" / "field-pack" / "cards"
START = ROOT / "static" / "start" / "index.html"
PRIVACY = ROOT / "static" / "privacy" / "index.html"
JS = ROOT / "static" / "field-pack" / "js" / "newsletter-v1.js"
CSS = ROOT / "static" / "field-pack" / "css" / "newsletter-v1.css"
EMAIL = "parent@example.com"


class _Headers(Message):
    def __init__(self, pairs: dict[str, str]):
        super().__init__()
        for key, value in pairs.items():
            self[key] = value


class NewsletterProxyTests(unittest.TestCase):
    def setUp(self):
        reset_newsletter_limits()

    def tearDown(self):
        reset_newsletter_limits()

    def test_rejects_bad_emails_without_forwarding(self):
        seen = []

        def poster(email: str) -> KitPostResult:
            seen.append(email)
            return KitPostResult(ok=True)

        for raw in ("", "not-an-email", "a@b", "a@b.c", "has space@example.com", "a@exam\nple.com", "x" * 250 + "@example.com"):
            result = handle_newsletter(
                {"email_address": raw, "website": "", "placement": "quiz_finish"},
                "203.0.113.10",
                poster=poster,
            )
            self.assertFalse(result.ok, raw)
            self.assertEqual(result.error, "invalid_email")
            self.assertEqual(result.status, 400)
        self.assertEqual(seen, [])
        self.assertTrue(valid_email(EMAIL))

    def test_honeypot_returns_ok_and_does_not_forward(self):
        def poster(email: str) -> KitPostResult:
            raise AssertionError("honeypot must not forward")

        result = handle_newsletter(
            {"email_address": EMAIL, "website": "https://spam.example", "placement": "cards_hub_aotd"},
            "203.0.113.11",
            poster=poster,
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.status, 200)
        self.assertFalse(result.already)

    def test_rate_limit_stops_the_sixth_forward(self):
        calls = []

        def poster(email: str) -> KitPostResult:
            calls.append(email)
            return KitPostResult(ok=True)

        fields = {"email_address": EMAIL, "website": "", "placement": "quiz_finish"}
        for _ in range(5):
            result = handle_newsletter(fields, "203.0.113.12", poster=poster)
            self.assertTrue(result.ok)
        blocked = handle_newsletter(fields, "203.0.113.12", poster=poster)
        self.assertFalse(blocked.ok)
        self.assertEqual(blocked.error, "rate_limited")
        self.assertEqual(blocked.status, 429)
        self.assertEqual(len(calls), 5)
        # A different IP is its own bucket.
        other = handle_newsletter(fields, "203.0.113.13", poster=poster)
        self.assertTrue(other.ok)
        self.assertEqual(len(calls), 6)

    def test_forwards_only_email_address_to_kit(self):
        captured = {}

        class Resp:
            status = 200

            def read(self, n):
                return b"Success! Now check your email to confirm your subscription."

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        def fake_urlopen(req, timeout=0):
            captured["url"] = req.full_url
            captured["data"] = req.data
            captured["timeout"] = timeout
            captured["headers"] = dict(req.header_items())
            return Resp()

        with patch("busyparent_agent.newsletter.urllib.request.urlopen", fake_urlopen):
            posted = post_kit_subscription(EMAIL)

        self.assertTrue(posted.ok)
        self.assertFalse(posted.already)
        self.assertEqual(captured["url"], KIT_FORM_SUBSCRIBE_URL)
        self.assertEqual(captured["url"], "https://app.kit.com/forms/10124095/subscriptions")
        self.assertEqual(captured["timeout"], KIT_TIMEOUT_SECONDS)
        body = parse_qs(captured["data"].decode("ascii"))
        self.assertEqual(body, {"email_address": [EMAIL]})
        self.assertNotIn("website", body)
        self.assertNotIn("placement", body)
        joined = " ".join(f"{k}:{v}" for k, v in captured["headers"].items())
        self.assertNotIn(EMAIL, joined)

    def test_already_subscribed_and_http_errors(self):
        class Resp:
            status = 200

            def read(self, n):
                return b"You are already subscribed"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        with patch("busyparent_agent.newsletter.urllib.request.urlopen", lambda *a, **k: Resp()):
            posted = post_kit_subscription(EMAIL)
        self.assertTrue(posted.ok)
        self.assertTrue(posted.already)

        err = urllib.error.HTTPError(
            KIT_FORM_SUBSCRIBE_URL, 422, "Unprocessable", Message(), io.BytesIO(b"nope")
        )
        with patch("busyparent_agent.newsletter.urllib.request.urlopen", side_effect=err):
            failed = post_kit_subscription(EMAIL)
        self.assertFalse(failed.ok)

        redirect = urllib.error.HTTPError(
            KIT_FORM_SUBSCRIBE_URL, 302, "Found", Message(), io.BytesIO(b"")
        )
        with patch("busyparent_agent.newsletter.urllib.request.urlopen", side_effect=redirect):
            moved = post_kit_subscription(EMAIL)
        self.assertTrue(moved.ok)

    def test_logs_omit_the_email(self):
        email = "unique-parent-9f3a@example.com"
        records: list[str] = []

        class Grab(logging.Handler):
            def emit(self, record):
                records.append(record.getMessage())

        log = logging.getLogger("busyparent_agent.newsletter")
        grab = Grab()
        log.addHandler(grab)
        log.setLevel(logging.INFO)
        try:
            def boom(address: str) -> KitPostResult:
                raise RuntimeError(address)

            handle_newsletter(
                {"email_address": email, "website": "", "placement": email},
                "203.0.113.14",
                poster=boom,
            )
            handle_newsletter(
                {"email_address": email, "website": "bot", "placement": "quiz_finish"},
                "203.0.113.14",
                poster=boom,
            )
        finally:
            log.removeHandler(grab)
        blob = "\n".join(records)
        self.assertNotIn(email, blob)
        self.assertNotIn("example.com", blob)
        self.assertIn("outcome=unavailable", blob)
        self.assertIn("placement=other", blob)
        self.assertIn("outcome=honeypot", blob)

    def test_json_and_no_js_responses(self):
        ok = response_for(NewsletterResult(ok=True, status=200), wants_json=True)
        self.assertEqual(ok, {"kind": "json", "status": 200, "body": {"ok": True}})
        already = response_for(NewsletterResult(ok=True, status=200, already=True), wants_json=True)
        self.assertEqual(already["body"], {"ok": True, "already": True})
        bad = response_for(NewsletterResult(ok=False, status=400, error="invalid_email"), wants_json=True)
        self.assertEqual(bad["body"], {"ok": False, "error": "invalid_email"})
        self.assertEqual(bad["status"], 400)
        page = response_for(NewsletterResult(ok=True, status=200), wants_json=False)
        self.assertEqual(page, {"kind": "redirect", "status": 303, "location": "/newsletter/thanks/"})
        oops = response_for(
            NewsletterResult(ok=False, status=400, error="invalid_email"), wants_json=False
        )
        self.assertEqual(oops["location"], "/newsletter/oops/?reason=email")
        down = response_for(
            NewsletterResult(ok=False, status=502, error="unavailable"), wants_json=False
        )
        self.assertEqual(down["location"], "/newsletter/oops/")

    def test_parses_urlencoded_and_multipart(self):
        raw = b"email_address=parent%40example.com&website=&placement=cards_hub_aotd"
        fields = parse_form_body(raw, "application/x-www-form-urlencoded")
        self.assertEqual(fields["email_address"], EMAIL)
        self.assertEqual(fields["website"], "")
        self.assertEqual(fields["placement"], "cards_hub_aotd")
        boundary = "----kzboundary"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="email_address"\r\n\r\n'
            f"{EMAIL}\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="website"\r\n\r\n'
            "\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="placement"\r\n\r\n'
            "quiz_finish\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        parsed = parse_form_body(body, f"multipart/form-data; boundary={boundary}")
        self.assertEqual(parsed["email_address"], EMAIL)
        self.assertEqual(parsed.get("website", ""), "")
        self.assertEqual(parsed["placement"], "quiz_finish")

    def test_handler_json_and_redirect_do_not_call_kit(self):
        def run(accept: str, body: bytes):
            handler = object.__new__(WebHandler)
            handler.headers = _Headers(
                {
                    "Accept": accept,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Content-Length": str(len(body)),
                }
            )
            handler.rfile = io.BytesIO(body)
            handler.client_address = ("203.0.113.20", 9)
            captured = {}
            handler._finish_newsletter = lambda spec: captured.setdefault("spec", spec)
            with patch("busyparent_agent.web.handle_newsletter", return_value=NewsletterResult(ok=True, status=200)) as mocked:
                WebHandler._handle_newsletter(handler)
            return captured["spec"], mocked.call_args

        body = b"email_address=parent%40example.com&website=&placement=quiz_finish"
        spec, args = run("application/json", body)
        self.assertEqual(spec["kind"], "json")
        self.assertEqual(spec["body"], {"ok": True})
        self.assertEqual(args[0][0]["email_address"], EMAIL)
        self.assertEqual(args[0][1], "203.0.113.20")
        spec, _args = run("text/html", body)
        self.assertEqual(spec, {"kind": "redirect", "status": 303, "location": "/newsletter/thanks/"})

    def test_post_route_and_csp_stay_on_self(self):
        handler = object.__new__(WebHandler)
        handler.path = "/api/newsletter"
        handler._reject_if_rate_limited = lambda: False
        called = {}
        handler._handle_newsletter = lambda: called.setdefault("yes", True)
        WebHandler.do_POST(handler)
        self.assertTrue(called.get("yes"))
        csp = SECURITY_HEADERS["Content-Security-Policy"]
        self.assertIn("form-action 'self'", csp)
        self.assertIn("connect-src 'self'", csp)
        self.assertNotIn("kit.com", csp)
        self.assertNotIn("convertkit.com", csp)


class NewsletterMarkupTests(unittest.TestCase):
    def test_box_on_card_pages_and_hub_not_on_start(self):
        js = JS.read_text(encoding="utf-8")
        hub = (CARDS / "index.html").read_text(encoding="utf-8")
        start = START.read_text(encoding="utf-8")
        card = (CARDS / "red-panda" / "index.html").read_text(encoding="utf-8")

        self.assertIn('src="/field-pack/js/newsletter-v1.js?v=1"', card)
        self.assertIn('href="/field-pack/css/newsletter-v1.css?v=1"', card)
        self.assertIn('value="quiz_finish"', js)
        self.assertIn('name="email_address"', js)
        self.assertIn('name="website"', js)
        self.assertIn("One animal + a quiz each week", js)
        self.assertIn("study-finish", js)
        self.assertIn("afterend", js)
        self.assertIn('class="kz-nl kz-nl--quiz no-print"', js)
        self.assertNotIn("gtag", js)
        self.assertIn("FPTrack", js)
        self.assertIn("OneLessAnalytics", js)
        self.assertIn('json.ok === true', js)
        self.assertIn('track("sign_up"', js)
        self.assertIn("newsletter_view", js)
        self.assertIn('localStorage.setItem(key, "1")', js)

        study_pages = [p for p in CARDS.glob("*/index.html") if "study-card.js" in p.read_text(encoding="utf-8")]
        self.assertGreaterEqual(len(study_pages), 42)
        for path in study_pages:
            html = path.read_text(encoding="utf-8")
            self.assertIn('src="/field-pack/js/newsletter-v1.js?v=1"', html, path.name)
            self.assertIn('href="/field-pack/css/newsletter-v1.css?v=1"', html, path.name)

        museum = (CARDS / "cm-art-lab" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("newsletter-v1", museum)

        self.assertIn('data-placement="cards_hub_aotd"', hub)
        self.assertIn('name="email_address"', hub)
        self.assertIn('name="website"', hub)
        self.assertIn('value="cards_hub_aotd"', hub)
        self.assertIn("Send me the weekly animal", hub)
        self.assertIn('href="/privacy/"', hub)
        self.assertIn('aria-live="polite"', hub)
        self.assertLess(hub.find("<!-- /kz-aotd -->"), hub.find('data-placement="cards_hub_aotd"'))
        self.assertLess(hub.find('data-placement="cards_hub_aotd"'), hub.find('id="cards-play"'))
        self.assertNotIn("No thanks", hub)

        self.assertNotIn("kz-nl", start)
        self.assertNotIn("newsletter-v1", start)
        self.assertNotIn("/api/newsletter", start)
        self.assertIn("Arya’s Wildlife Project", start)

        css = CSS.read_text(encoding="utf-8")
        self.assertIn("min-height: 44px", css)
        self.assertIn("font-size: 16px", css)
        self.assertIn("left: -9999px", css)
        self.assertNotIn("display: none", css.split(".kz-nl-hp")[1].split("}")[0])

    def test_privacy_names_kit_and_keeps_the_project_name(self):
        html = PRIVACY.read_text(encoding="utf-8")
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
        self.assertIn("Kit (ConvertKit)", text)
        self.assertIn("https://kit.com/privacy", html)
        self.assertIn("double opt-in", text)
        self.assertIn("unsubscribe any time", text.lower())
        self.assertIn("We never ask for or store anything about children", text)
        self.assertNotRegex(text, r"(?i)\bfree\b")
        about = (ROOT / "static" / "about" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Arya’s Wildlife Project", about)
        thanks = (ROOT / "static" / "newsletter" / "thanks" / "index.html").read_text(encoding="utf-8")
        oops = (ROOT / "static" / "newsletter" / "oops" / "index.html").read_text(encoding="utf-8")
        self.assertIn('content="noindex"', thanks)
        self.assertIn("Check your inbox to confirm", thanks)
        self.assertIn('content="noindex"', oops)
        self.assertIn("try again in a minute", oops.lower())


if __name__ == "__main__":
    unittest.main()
