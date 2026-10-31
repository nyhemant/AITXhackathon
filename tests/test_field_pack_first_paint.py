"""2026-10-29: /field-pack/ scripts are deferred (order kept) and the Dallas enlarged map has size hints."""
import re
import unittest
from pathlib import Path

FP = Path(__file__).resolve().parents[1] / "static" / "field-pack"
ORDER = ["shell.js", "qr-welcome.js", "fp-analytics.js", "places-data.js", "catalog.js",
         "print-maps.js", "print-kit.js", "mission-pilots.js", "landing-map.js", "landing-hook.js",
         "aotd.js"]


class FieldPackFirstPaintTests(unittest.TestCase):
    def test_external_scripts_deferred_in_original_order(self):
        s = (FP / "index.html").read_text(encoding="utf-8")
        tags = re.findall(r"<script\s+src=\"([^\"]+)\"([^>]*)>", s)
        names = [t[0].split("/")[-1].split("?")[0] for t in tags]
        self.assertEqual(names, ORDER)
        for src, rest in tags:
            self.assertIn("defer", rest, src)
            self.assertNotIn("async", rest, src)

    def test_no_inline_script_runs_after_head_that_needs_them(self):
        s = (FP / "index.html").read_text(encoding="utf-8")
        body = s.split("<body", 1)[1]
        self.assertEqual(re.findall(r"<script>(.*?)</script>", body, re.S), [])

    def test_dallas_enlarged_map_has_dimensions(self):
        s = (FP / "dallas-zoo" / "index.html").read_text(encoding="utf-8")
        img = re.search(r'<img [^>]*alt="Enlarged visitor map"[^>]*>', s).group(0)
        self.assertIn('width="1400"', img)
        self.assertIn('height="894"', img)


if __name__ == "__main__":
    unittest.main()
