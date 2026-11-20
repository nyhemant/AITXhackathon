"""2026-11-18/19: /privacy/ names the KidZooKit confirmation sender; the old reCAPTCHA line is gone."""
import re
import unittest
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "static" / "privacy" / "index.html"


class PrivacyKitCheck(unittest.TestCase):
    def setUp(self):
        self.html = PAGE.read_text(encoding="utf-8")
        self.text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|<!--.*?-->", " ", self.html, flags=re.S))

    def test_names_sender_and_drops_the_old_recaptcha_line(self):
        # 2026-11-19: sign-ups go through Kit's API, so the #471 reCAPTCHA line is no longer true.
        self.assertNotIn("reCAPTCHA", self.html)
        self.assertNotIn("robot check", self.text)
        self.assertIn("The confirmation email comes from “KidZooKit” at ask@kidzookit.com", self.text)
        self.assertIn("Kit emails you a confirmation first. That is double opt-in", self.text)

    def test_sender_permanent_shielded_and_not_a_link(self):
        # 2026-11-18 10:03 PM CT: Kit sender set to KidZooKit <ask@kidzookit.com>; the temporary 1Less line is gone.
        self.assertNotIn("1less.app", self.html)
        self.assertNotIn("kz-temp:kit-sender", self.html)
        self.assertIn("<!--email_off-->ask@kidzookit.com<!--/email_off-->, so look for that name", self.html)
        self.assertNotIn('mailto:ask@kidzookit.com">ask@kidzookit.com</a>, so look', self.html)

    def test_existing_lines_and_freeze_kept(self):
        self.assertIn("Kit emails you a confirmation first. That is double opt-in", self.text)
        self.assertIn("<title>Privacy — KidZooKit</title>", self.html)
        self.assertIn('<h1 id="privacy-heading">Privacy</h1>', self.html)
        self.assertIn('content="What KidZooKit collects: visit counts via Google Analytics and Cloudflare Web Analytics, no accounts, child names stay on the page, email only if you join."', self.html)

    def test_new_lines_avoid_we_and_free(self):
        block = self.html.split("double opt-in", 1)[1].split("You can unsubscribe", 1)[0]
        words = re.sub(r"<[^>]+>|<!--.*?-->", " ", block, flags=re.S)
        self.assertNotRegex(words, r"(?i)\b(we|our|us|free|no-cost)\b")


if __name__ == "__main__":
    unittest.main()
