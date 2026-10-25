"""The /privacy/ page exists, is routed, is in the sitemap and only states audited facts."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from busyparent_agent.web import _safe_privacy_path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "static" / "privacy" / "index.html"


class PrivacyPageTests(unittest.TestCase):
    def test_routed(self):
        self.assertEqual(_safe_privacy_path("/privacy/"), PAGE)
        self.assertEqual(_safe_privacy_path("/privacy/index.html"), PAGE)
        self.assertIsNone(_safe_privacy_path("/privacy/../web.py"))

    def test_in_both_sitemaps(self):
        for p in ("static/sitemap.xml", "static/field-pack/sitemap.xml"):
            self.assertIn("<loc>https://kidzookit.com/privacy/</loc>", (ROOT / p).read_text())

    def test_page_copy_rules(self):
        html = PAGE.read_text(encoding="utf-8")
        text = re.sub(r"<[^>]+>", " ", html)
        self.assertNotRegex(text, r"(?i)\bfree\b")
        self.assertIn("mailto:kidzookit@agentmail.to", html)
        self.assertIn("Google Analytics", text)
        for bad in ("guarantee", "COPPA compliant", "GDPR compliant"):
            self.assertNotIn(bad.lower(), text.lower())

    def test_lists_quiz_counts_and_purpose(self):
        """Quiz events (#368) and the purpose/safeguards notice stay described."""
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", PAGE.read_text(encoding="utf-8")))
        self.assertIn("right on the first try", text)
        self.assertIn("the answers a child picks are not sent", text)
        self.assertIn("What the counting is for", text)
        self.assertIn("We don’t use them for ads", text)
        js = (ROOT / "static" / "field-pack" / "js" / "study-card.js").read_text(encoding="utf-8")
        payload = js.split('"quiz_complete", {', 1)[1].split("}", 1)[0]
        self.assertNotIn("letter", payload)
        self.assertNotIn("answer", payload)

    def test_describes_cloudflare_web_analytics_as_cloudflares_claim(self):
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", PAGE.read_text(encoding="utf-8")))
        self.assertIn("Cloudflare Web Analytics", text)
        self.assertIn("Cloudflare describes this service as cookieless", text)
        self.assertIn("That is Cloudflare’s description, not a promise from us", text)
        self.assertIn("Cloudflare also delivers this site", text)
        self.assertIn("stop Google Analytics and the Cloudflare Web Analytics script", text)
        for bad in ("anonymous", "no tracking", "no personal information", "uses no cookies"):
            self.assertNotIn(bad, text.lower())

    def test_footers_link_to_privacy(self):
        for p in ("static/about/index.html", "static/start/index.html"):
            self.assertIn('href="/privacy/"', (ROOT / p).read_text(), p)


if __name__ == "__main__":
    unittest.main()
