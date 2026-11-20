"""K4: a quick double tap on Print opens one print dialog, not two."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FP = ROOT / "static" / "field-pack"
GUARD = FP / "js" / "print-guard-v1.js"
TAG = '<script src="/field-pack/js/print-guard-v1.js?v=1"></script>'
# Round 2 (2026-11-20): the freeze ended, so no mission page skips the tag any more.
SKIPPED: set[str] = set()
FORMERLY_SKIPPED = {
    "bronx-zoo", "austin-zoo", "national-zoo", "lincoln-park-zoo", "shedd-aquarium",
    "seattle-aquarium", "st-louis-zoo", "fort-worth-zoo", "san-antonio-zoo", "dallas-zoo",
}
UI_TAG = re.compile(r'<script src="/field-pack/js/mission/mission-ui\.js\?v=[0-9a-z-]+"></script>')


class PrintGuardPages(unittest.TestCase):
    def test_every_other_mission_page_loads_the_guard_before_mission_ui(self):
        seen = 0
        for page in sorted(FP.glob("*/index.html")):
            html = page.read_text(encoding="utf-8")
            ui = UI_TAG.search(html)
            if not ui:
                continue
            slug = page.parent.name
            if slug in SKIPPED:
                self.assertNotIn("print-guard", html, slug)
                continue
            seen += 1
            self.assertEqual(html.count(TAG), 1, slug)
            self.assertLess(html.index(TAG), ui.start(), slug)
        self.assertGreaterEqual(seen, 221)

    def test_formerly_skipped_pages_now_load_the_guard(self):
        for slug in sorted(FORMERLY_SKIPPED):
            with self.subTest(slug=slug):
                html = (FP / slug / "index.html").read_text(encoding="utf-8")
                ui = UI_TAG.search(html)
                self.assertIsNotNone(ui, slug)
                self.assertEqual(html.count(TAG), 1, slug)
                self.assertLess(html.index(TAG), ui.start(), slug)

    def test_generator_skip_list_is_empty(self):
        src = (ROOT / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")
        self.assertIn("PRINT_GUARD_SKIP: frozenset[str] = frozenset()", src)

    def test_guard_script_is_small_and_has_no_tracking(self):
        src = GUARD.read_text(encoding="utf-8")
        self.assertLess(len(src), 1500)
        for word in ("fetch(", "XMLHttpRequest", "localStorage", "document.cookie", "gtag"):
            self.assertNotIn(word, src)


@unittest.skipUnless(shutil.which("node"), "node not installed")
class PrintGuardBehavior(unittest.TestCase):
    def run_js(self, calls_ms: list[int]) -> int:
        script = f"""
        let t = 0, n = 0;
        const realNow = Date.now;
        Date.now = () => t;
        global.window = {{ print() {{ n += 1; }} }};
        require({json.dumps(str(GUARD))});
        for (const at of {json.dumps(calls_ms)}) {{ t = at; window.print(); }}
        console.log(n);
        """
        out = subprocess.run(["node", "-e", script], capture_output=True, text=True, check=True, timeout=20)
        return int(out.stdout.strip())

    def test_single_tap_prints_once(self):
        self.assertEqual(self.run_js([1000]), 1)

    def test_double_tap_prints_once(self):
        self.assertEqual(self.run_js([1000, 1040, 1500]), 1)

    def test_later_print_after_the_window_still_works(self):
        self.assertEqual(self.run_js([1000, 1040, 3500]), 2)


if __name__ == "__main__":
    unittest.main()
