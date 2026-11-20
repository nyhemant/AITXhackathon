"""KZK (kidzookit.com) 2026-11-19: newsletter sign-ups go through Kit's v4 API, not the public form."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from busyparent_agent import newsletter
from busyparent_agent.newsletter import (
    KIT_API_SUBSCRIBERS_URL,
    KIT_FORM_ID,
    KIT_SIGNUP_REFERRER,
    KitPostResult,
    api_subscribe,
    deliver_signup,
    form_subscribers_url,
    handle_newsletter,
    kit_api_key,
    kit_form_id,
    reset_newsletter_limits,
    response_for,
)

FIELDS = {"email_address": "parent@example.com", "website": "", "placement": "printables_hub"}
JS = Path(__file__).resolve().parents[1] / "static" / "field-pack" / "js" / "newsletter-v1.js"
THANKS = Path(__file__).resolve().parents[1] / "static" / "newsletter" / "thanks" / "index.html"
SUCCESS_LINE = (
    "You're in! Check your inbox for “Confirm your KidZooKit weekly animal card” "
    "from KidZooKit. (Confirmed before? Nothing more to do.) The next animal arrives soon."
)


class KitApiSubscribeTests(unittest.TestCase):
    def setUp(self):
        reset_newsletter_limits()
        self._env = {k: os.environ.get(k) for k in ("KZK_KIT_API_KEY", "KZK_KIT_FORM_ID", "KZK_KIT_CONFIG")}
        for key in self._env:
            os.environ.pop(key, None)
        # Never read the real ~/.kidzookit-data/kit.json (it exists on the production box).
        self._empty = tempfile.TemporaryDirectory()
        os.environ["KZK_KIT_CONFIG"] = str(Path(self._empty.name) / "no-kit.json")

    def tearDown(self):
        self._empty.cleanup()
        for key, value in self._env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_api_subscribe_creates_inactive_then_adds_to_the_kzk_form(self):
        calls = []

        def fake_post(url, body, api_key, timeout):
            self.assertEqual(api_key, "kit-test-key")
            calls.append((url, body))
            if url == KIT_API_SUBSCRIBERS_URL:
                self.assertEqual(body, {"email_address": "parent@example.com", "state": "inactive"})
                return 201
            self.assertEqual(url, form_subscribers_url(KIT_FORM_ID))
            self.assertEqual(body, {"email_address": "parent@example.com", "referrer": KIT_SIGNUP_REFERRER})
            return 201

        with patch.object(newsletter, "_post_kit_api", side_effect=fake_post):
            result = api_subscribe("parent@example.com", KIT_FORM_ID, "kit-test-key")
        self.assertEqual(result, KitPostResult(ok=True, already=False))
        self.assertEqual(len(calls), 2)

    def test_a_200_on_the_form_means_already_on_the_list(self):
        def fake_post(url, body, api_key, timeout):
            return 200

        with patch.object(newsletter, "_post_kit_api", side_effect=fake_post):
            result = api_subscribe("parent@example.com", KIT_FORM_ID, "kit-test-key")
        self.assertEqual(result, KitPostResult(ok=True, already=True))

    def test_create_or_form_failure_is_not_ok(self):
        with patch.object(newsletter, "_post_kit_api", return_value=401):
            self.assertFalse(api_subscribe("parent@example.com", KIT_FORM_ID, "kit-test-key").ok)

        def create_ok_form_fail(url, body, api_key, timeout):
            return 201 if url == KIT_API_SUBSCRIBERS_URL else 500

        with patch.object(newsletter, "_post_kit_api", side_effect=create_ok_form_fail):
            self.assertFalse(api_subscribe("parent@example.com", KIT_FORM_ID, "kit-test-key").ok)

    def test_missing_key_does_not_call_kit_or_the_public_form(self):
        with patch.object(newsletter, "_post_kit_api") as api, patch.object(newsletter, "post_kit_subscription") as public:
            result = deliver_signup("parent@example.com")
        self.assertFalse(result.ok)
        api.assert_not_called()
        public.assert_not_called()

    def test_handler_uses_the_api_path_and_keeps_honest_errors(self):
        with patch.object(newsletter, "deliver_signup", return_value=KitPostResult(ok=True)) as deliver:
            result = handle_newsletter(FIELDS, "203.0.113.80")
        deliver.assert_called_once_with("parent@example.com")
        self.assertTrue(result.ok)
        self.assertEqual(response_for(result, wants_json=True)["body"], {"ok": True})
        self.assertEqual(response_for(result, wants_json=False)["location"], "/newsletter/thanks/")

        with patch.object(newsletter, "deliver_signup", return_value=KitPostResult(ok=False)):
            failed = handle_newsletter(FIELDS, "203.0.113.81")
        self.assertEqual(failed.error, "unavailable")
        self.assertEqual(response_for(failed, wants_json=False)["location"], "/newsletter/try-again/")

        bad = handle_newsletter({"email_address": "not-an-email", "website": ""}, "203.0.113.82")
        self.assertEqual(bad.error, "invalid_email")

        honey = handle_newsletter({**FIELDS, "website": "http://spam.example"}, "203.0.113.83")
        self.assertTrue(honey.ok)

    def test_key_comes_from_env_or_config_file_and_is_not_the_form_id(self):
        os.environ["KZK_KIT_API_KEY"] = "kit-env-key"
        self.assertEqual(kit_api_key(), "kit-env-key")
        self.assertEqual(kit_form_id(), KIT_FORM_ID)
        os.environ.pop("KZK_KIT_API_KEY")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "kit.json"
            path.write_text(json.dumps({"form_id": "10124095", "api_key": "kit-file-key"}), encoding="utf-8")
            os.environ["KZK_KIT_CONFIG"] = str(path)
            self.assertEqual(kit_api_key(), "kit-file-key")
            self.assertEqual(kit_form_id(), "10124095")
        # The production module must never fall back to posting the public form on its own.
        source = Path(newsletter.__file__).read_text(encoding="utf-8")
        self.assertIn("poster or deliver_signup", source)
        self.assertNotIn("poster or post_kit_subscription", source)

    def test_success_copy_names_the_subject_and_sender(self):
        js = JS.read_text(encoding="utf-8")
        thanks = THANKS.read_text(encoding="utf-8")
        self.assertIn(
            "You're in! Check your inbox for \\u201CConfirm your KidZooKit weekly animal card\\u201D from KidZooKit.",
            js,
        )
        self.assertIn(
            "Check your inbox for “Confirm your KidZooKit weekly animal card” from KidZooKit.",
            thanks,
        )
        self.assertIn("<h1>You're in!</h1>", thanks)
        for blob in (SUCCESS_LINE, thanks):
            self.assertNotRegex(blob, r"(?i)\bfree\b")
            self.assertNotIn("email service", blob.lower())
        # The notice names the KidZooKit sender, not the email service.
        self.assertNotIn("Kit,", SUCCESS_LINE)
        self.assertNotIn("ConvertKit", SUCCESS_LINE)


if __name__ == "__main__":
    unittest.main()
