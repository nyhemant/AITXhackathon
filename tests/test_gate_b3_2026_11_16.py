"""Gate B3 (2026-11-16): no cam claim without a cam, no duplicate hunt list in the drawer."""
import glob
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from scav_test_2026_11 import COMPARISON_SLUGS, TEST_SLUGS  # noqa: E402

FROZEN = set(TEST_SLUGS) | set(COMPARISON_SLUGS)


def place_pages():
    for f in sorted(glob.glob(str(ROOT / "static/field-pack/*/index.html"))):
        slug = Path(f).parent.name
        t = Path(f).read_text(encoding="utf-8")
        if 'id="mission-drawer"' in t:
            yield slug, t


class GateB3(unittest.TestCase):
    def test_cam_disclaimer_only_with_a_cam(self):
        bad = []
        for slug, t in place_pages():
            if slug in FROZEN or "seo-cam-disclaimer" not in t:
                continue
            i = t.find('id="at-home"')
            sec = t[i : t.find("</details>", i)]
            links = re.findall(r'<a class="seo-watch-link"[^>]*>(.*?)</a>', sec, re.S)
            if not any("Live from" in l or re.search(r"\bcam\b", l, re.I) for l in links):
                bad.append(slug)
        self.assertEqual(bad, [])

    def test_helsinki_has_no_cam_claim(self):
        t = (ROOT / "static/field-pack/helsinki-zoo/index.html").read_text(encoding="utf-8")
        self.assertNotIn("doesn’t stream public cams", t)

    def test_drawer_lists_are_empty_on_non_frozen_pages(self):
        n = 0
        for slug, t in place_pages():
            if slug in FROZEN:
                continue
            n += 1
            self.assertIn('<ol class="mission-finds" id="mission-finds" aria-label="Finds"></ol>', t, slug)
            self.assertIn('<ul class="mission-challenges" id="mission-challenges" aria-label="Challenges"></ul>', t, slug)
            self.assertIn('class="seo-hunt-list"', t, slug)
        self.assertGreaterEqual(n, 190)

    def test_frozen_pages_keep_drawer_markup(self):
        for slug, t in place_pages():
            if slug in FROZEN:
                self.assertIn('<li class="mission-find">', t, slug)

    def test_generator_guards(self):
        src = (ROOT / "scripts/generate_bdo_seo.py").read_text(encoding="utf-8")
        self.assertIn("FROZEN_PLACE_SLUGS = frozenset(TEST_SLUGS | COMPARISON_SLUGS)", src)
        self.assertIn("if vid not in FROZEN_PLACE_SLUGS:", src)
        self.assertIn("venue_id in FROZEN_PLACE_SLUGS", src)


if __name__ == "__main__":
    unittest.main()
