"""2026-11-18: /privacy/ tells parents about Kit's robot check and today's confirmation sender."""
import re
import unittest
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / "static" / "privacy" / "index.html"


class PrivacyKitCheck(unittest.TestCase):
    def setUp(self):
        self.html = PAGE.read_text(encoding="utf-8")
        self.text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>|<!--.*?-->", " ", self.html, flags=re.S))

    def test_names_recaptcha_and_sender(self):
        self.assertIn("Kit may show a quick robot check (Google reCAPTCHA)", self.text)
        self.assertIn("The confirmation email currently comes from “1Less” at ask@1less.app", self.text)

    def test_sender_marked_temporary_and_not_a_link(self):
        self.assertIn("kz-temp:kit-sender TEMPORARY", self.html)
        self.assertIn('data-kz-temp="kit-sender"', self.html)
        self.assertNotIn("mailto:ask@1less.app", self.html)
        self.assertIn("<!--email_off-->ask@1less.app<!--/email_off-->", self.html)

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
