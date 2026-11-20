"""KZK (kidzookit.com) 2026-11-18: a Kit "quarantined" reply is a robot check, not a signup.

Live: every signup forwarded from the server got {"status":"quarantined","url":".../forms/guards/<id>"}
and no confirmation email, while the site said "You're in! Check your inbox to confirm".
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from busyparent_agent.newsletter import (
    KitPostResult,
    NewsletterResult,
    handle_newsletter,
    interpret_kit_response,
    kit_guard_url,
    reset_newsletter_limits,
    response_for,
)

ROOT = Path(__file__).resolve().parents[1]
GUARD = "https://app.kit.com/forms/guards/3dd616f0-6a28-4932-a0c4-ddcb93974903"
FIELDS = {"email_address": "parent@example.com", "website": "", "placement": "printables_hub"}


class QuarantineIsNotSuccess(unittest.TestCase):
    def setUp(self):
        reset_newsletter_limits()

    def test_quarantined_json_carries_the_guard_url(self):
        body = ('{"consent":{"enabled":false},"status":"quarantined","url":"%s"}' % GUARD).encode()
        posted = interpret_kit_response(200, body)
        self.assertFalse(posted.ok)
        self.assertEqual(posted.verify_url, GUARD)

    def test_redirect_to_a_guard_page_is_not_success(self):
        posted = interpret_kit_response(302, b"", GUARD)
        self.assertFalse(posted.ok)
        self.assertEqual(posted.verify_url, GUARD)

    def test_only_an_exact_kit_guard_url_is_passed_on(self):
        for bad in (
            "javascript:alert(1)",
            "http://app.kit.com/forms/guards/3dd616f0-6a28",
            "https://app.kit.com.evil.example/forms/guards/3dd616f0-6a28",
            "https://evil.example/forms/guards/3dd616f0-6a28",
            GUARD + "?x=1",
            GUARD + "/../../x",
            "https://app.kit.com/forms/guards/<b>",
            "",
            None,
        ):
            with self.subTest(bad=bad):
                self.assertEqual(kit_guard_url(bad), "")
        body = b'{"status":"quarantined","url":"https://app.kit.com/guard"}'
        posted = interpret_kit_response(200, body)
        self.assertFalse(posted.ok)
        self.assertEqual(posted.verify_url, "")

    def test_handler_says_verify_never_ok(self):
        result = handle_newsletter(FIELDS, "203.0.113.70", poster=lambda _e: KitPostResult(ok=False, verify_url=GUARD))
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "verify")
        js = response_for(result, wants_json=True)
        self.assertEqual(js["status"], 200)
        self.assertEqual(js["body"], {"ok": False, "error": "verify", "verify_url": GUARD})
        page = response_for(result, wants_json=False)
        self.assertEqual(page["location"], "/newsletter/one-more-step/")
        self.assertNotIn("@", page["location"])

    def test_quarantine_without_a_usable_url_is_a_plain_error(self):
        result = handle_newsletter(FIELDS, "203.0.113.71", poster=lambda _e: KitPostResult(ok=False))
        self.assertEqual(result.error, "unavailable")
        self.assertEqual(response_for(result, wants_json=False)["location"], "/newsletter/try-again/")
        forged = NewsletterResult(ok=False, status=200, error="verify", verify_url="javascript:alert(1)")
        self.assertEqual(response_for(forged, wants_json=True)["body"], {"ok": False, "error": "unavailable"})

    def test_bad_address_keeps_its_old_url(self):
        bad = NewsletterResult(ok=False, status=400, error="invalid_email")
        self.assertEqual(response_for(bad, wants_json=False)["location"], "/newsletter/oops/?reason=email")


class PagesAndScriptSayOneTrueThing(unittest.TestCase):
    def _text(self, rel):
        html = (ROOT / rel).read_text(encoding="utf-8")
        return html, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))

    def test_error_pages_name_one_cause(self):
        oops_html, oops = self._text("static/newsletter/oops/index.html")
        self.assertIn("doesn't look quite right", oops)
        self.assertNotIn("went wrong", oops)
        again_html, again = self._text("static/newsletter/try-again/index.html")
        self.assertIn("Something went wrong. Please try again in a minute.", again)
        self.assertNotIn("look quite right", again)
        step_html, step = self._text("static/newsletter/one-more-step/index.html")
        self.assertIn("robot check", step)
        for html, text in ((oops_html, oops), (again_html, again), (step_html, step)):
            self.assertIn('content="noindex"', html)
            self.assertIn('href="/printables/"', html)
            self.assertNotRegex(text, r"(?i)\b(free|no-cost|we|our|us)\b")

    def test_script_handles_verify_without_claiming_a_signup(self):
        js = (ROOT / "static" / "field-pack" / "js" / "newsletter-v1.js").read_text(encoding="utf-8")
        self.assertIn('var SUB_KEY = "kz_nl_subscribed_v2";', js)
        self.assertIn(r"/^https:\/\/app\.kit\.com\/forms\/guards\/[A-Za-z0-9-]{8,80}$/", js)
        verify = js[js.index('if (code === "verify"'):]
        verify = verify[: verify.index("return;")]
        self.assertNotIn("storageSet", verify)
        self.assertNotIn('"sign_up"', verify)
        helper = js[js.index("function showVerify"): js.index("var sampleDialog")]
        self.assertNotIn("innerHTML", helper)
        self.assertIn('link.rel = "noopener noreferrer"', helper)
        self.assertNotIn("our end", js)
        self.assertIn("rate_limited", js)

    def test_every_page_with_the_box_loads_the_new_script(self):
        pages = [p for p in (ROOT / "static").rglob("*.html") if 'class="kz-nl ' in p.read_text(encoding="utf-8")]
        self.assertGreaterEqual(len(pages), 4)
        for page in pages:
            with self.subTest(page=str(page.relative_to(ROOT))):
                self.assertIn("newsletter-v1.js?v=5", page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
