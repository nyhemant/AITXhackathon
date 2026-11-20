"""Polish 2026-11-20: newsletter-v1.js no longer blocks the page ahead of mission-ui.js."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

TAG = re.compile(r"<script\b[^>]*newsletter-v1\.js[^>]*>")


class NewsletterDefer(unittest.TestCase):
    def test_every_page_defers_the_script(self):
        n = 0
        for page in sorted((ROOT / "static").rglob("index.html")):
            html = page.read_text(encoding="utf-8")
            tags = TAG.findall(html)
            if not tags:
                continue
            n += 1
            self.assertEqual(len(tags), 1, page)
            self.assertIn(" defer ", tags[0], page)
        self.assertGreaterEqual(n, 225)

    def test_script_starts_fine_after_parsing(self):
        js = (ROOT / "static" / "field-pack" / "js" / "newsletter-v1.js").read_text(encoding="utf-8")
        self.assertIn('document.readyState === "loading"', js)
        self.assertIn("DOMContentLoaded", js)

    def test_generator_emits_defer(self):
        import generate_bdo_seo as gen

        out = gen._ensure_newsletter_asset("<html><body><script src=\"/shell/shell.js?v=6\"></script></body></html>", "js", gen.NEWSLETTER_JS_HREF)
        self.assertIn(f'<script defer src="{gen.NEWSLETTER_JS_HREF}"></script>', out)
        again = gen._ensure_newsletter_asset(out, "js", gen.NEWSLETTER_JS_HREF)
        self.assertEqual(again, out)


if __name__ == "__main__":
    unittest.main()
