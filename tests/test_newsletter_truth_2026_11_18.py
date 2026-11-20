"""KZK (kidzookit.com) newsletter truth rules.

2026-11-18: a Kit "quarantined" reply was a robot check, not a signup. 2026-11-20: sign-ups use Kit's
API (#477), so the robot-check branch, its page and the public-form code are gone. These tests keep the
honest outcomes: success only on a real API success, one plain no-JS error page, and no leftover
robot-check path.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from busyparent_agent import newsletter
from busyparent_agent.newsletter import (
    KitPostResult,
    NewsletterResult,
    handle_newsletter,
    reset_newsletter_limits,
    response_for,
)

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"email_address": "parent@example.com", "website": "", "placement": "printables_hub"}


class OnlyRealSuccessIsSuccess(unittest.TestCase):
    def setUp(self):
        reset_newsletter_limits()

    def test_no_robot_check_path_is_left(self):
        for name in ("interpret_kit_response", "kit_guard_url", "post_kit_subscription", "KIT_GUARD_RE"):
            self.assertFalse(hasattr(newsletter, name), name)
        self.assertNotIn("verify_url", NewsletterResult.__dataclass_fields__)

    def test_a_failed_post_is_a_plain_error(self):
        result = handle_newsletter(FIELDS, "203.0.113.71", poster=lambda _e: KitPostResult(ok=False))
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "unavailable")
        self.assertEqual(response_for(result, wants_json=True)["body"], {"ok": False, "error": "unavailable"})
        self.assertEqual(response_for(result, wants_json=False)["location"], "/newsletter/try-again/")

    def test_bad_address_goes_to_the_one_error_page_with_a_reason(self):
        bad = NewsletterResult(ok=False, status=400, error="invalid_email")
        self.assertEqual(response_for(bad, wants_json=False)["location"], "/newsletter/try-again/?reason=email")
        self.assertEqual(response_for(bad, wants_json=True)["body"], {"ok": False, "error": "invalid_email"})


class PagesAndScriptSayOneTrueThing(unittest.TestCase):
    def _text(self, rel):
        html = (ROOT / rel).read_text(encoding="utf-8")
        return html, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))

    def test_one_error_page_names_both_causes(self):
        html, text = self._text("static/newsletter/try-again/index.html")
        self.assertIn("didn't go through", text)
        self.assertIn("email address looks right", text)
        self.assertIn('content="noindex"', html)
        self.assertIn('href="/printables/"', html)
        self.assertNotRegex(text, r"(?i)\b(free|no-cost|we|our|us)\b")
        for gone in ("oops", "one-more-step"):
            self.assertFalse((ROOT / "static" / "newsletter" / gone).exists(), gone)

    def test_script_has_no_robot_check_branch(self):
        js = (ROOT / "static" / "field-pack" / "js" / "newsletter-v1.js").read_text(encoding="utf-8")
        self.assertIn('var SUB_KEY = "kz_nl_subscribed_v2";', js)
        for gone in ("showVerify", "GUARD_RE", "verify_url", "kz-nl-verify", "robot check"):
            self.assertNotIn(gone, js)
        self.assertNotIn("our end", js)
        self.assertIn("rate_limited", js)

    def test_every_page_with_the_box_loads_the_new_script(self):
        pages = [p for p in (ROOT / "static").rglob("*.html") if 'class="kz-nl ' in p.read_text(encoding="utf-8")]
        self.assertGreaterEqual(len(pages), 4)
        for page in pages:
            with self.subTest(page=str(page.relative_to(ROOT))):
                self.assertIn("newsletter-v1.js?v=6", page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
