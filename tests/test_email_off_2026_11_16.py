"""mailto anchors sit inside <!--email_off--> so Cloudflare does not swap in a 404 link (2026-11-16)."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scav_test_2026_11 import COMPARISON_SLUGS, TEST_SLUGS  # noqa: E402

ANCHOR = re.compile(r'<a [^>]*href="mailto:[^"]*"[^>]*>[^<]*</a>')


class EmailOff(unittest.TestCase):
    def test_every_mailto_anchor_is_wrapped_outside_the_24(self):
        frozen = {f"static/field-pack/{s}/index.html" for s in TEST_SLUGS | COMPARISON_SLUGS}
        wrapped = 0
        for p in sorted((ROOT / "static").glob("**/*.html")):
            rel = p.relative_to(ROOT).as_posix()
            s = p.read_text(encoding="utf-8")
            for m in ANCHOR.finditer(s):
                with self.subTest(page=rel):
                    before = s[max(0, m.start() - 16): m.start()]
                    after = s[m.end(): m.end() + 17]
                    if rel in frozen:
                        self.assertNotIn("email_off", before)
                        continue
                    self.assertEqual(before, "<!--email_off-->")
                    self.assertEqual(after, "<!--/email_off-->")
                    wrapped += 1
        self.assertGreaterEqual(wrapped, 200)

    def test_generator_wraps_contact_link(self):
        gen = (ROOT / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        self.assertEqual(
            gen.count('<!--email_off--><a href="mailto:{CONTACT_MAIL}">Contact</a><!--/email_off-->'), 2
        )


if __name__ == "__main__":
    unittest.main()
