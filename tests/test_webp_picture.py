"""2026-10-29: right-sized WebP via <picture>; originals stay as fallback (never overwritten)."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
sys.path.insert(0, str(ROOT / "scripts"))
import webp_picture  # noqa: E402

PIC = re.compile(r'<picture style="display:contents"><source type="image/webp" (?:data-)?srcset="([^"]+)"[^>]*/>(<img\b[^>]*>)</picture>', re.S)


class WebpPictureTests(unittest.TestCase):
    def pages(self):
        return webp_picture.targets()

    def test_every_webp_source_exists_and_is_versioned_new_file(self):
        n = 0
        for p in self.pages():
            s = p.read_text(encoding="utf-8")
            for srcset in re.findall(r'type="image/webp" (?:data-)?srcset="([^"]+)"', s):
                for part in srcset.split(","):
                    url = part.strip().split()[0]
                    self.assertRegex(url, r"-\d+-v\d+\.webp$", url)
                    self.assertTrue((STATIC / url.lstrip("/")).is_file(), (p, url))
                    n += 1
        self.assertGreater(n, 300)

    def test_fallback_img_keeps_original_jpeg_or_png(self):
        for p in self.pages():
            for _srcset, img in PIC.findall(p.read_text(encoding="utf-8")):
                src = re.search(r'\s(?:data-)?src="([^"]+)"', img).group(1)
                self.assertRegex(src.split("?")[0], r"\.(jpe?g|png)$", (p, img))
                self.assertTrue((STATIC / src.split("?")[0].lstrip("/")).is_file(), (p, src))
                self.assertIn(" alt=", img)

    def test_hub_and_cards_use_picture(self):
        hub = (STATIC / "field-pack/cards/index.html").read_text(encoding="utf-8")
        self.assertGreaterEqual(hub.count('class="cards-hub-thumb"'), 55)
        self.assertEqual(hub.count('class="cards-hub-thumb"'), len(re.findall(r'image/webp[^>]*/><img class="cards-hub-thumb"', hub)))
        ws = (STATIC / "field-pack/cards/whale-shark/index.html").read_text(encoding="utf-8")
        self.assertRegex(ws, r'image/webp[^>]*/><img class="card-page-photo"')
        self.assertRegex(ws, r'image/webp[^>]*/><img class="card-try-next-thumb"')

    def test_lcp_images_have_high_priority_and_are_not_lazy(self):
        hub = (STATIC / "field-pack/cards/index.html").read_text(encoding="utf-8")
        still = re.search(r'<img\s+class="cards-play-still"[^>]*>', hub).group(0)
        self.assertIn('fetchpriority="high"', still)
        self.assertNotIn('loading="lazy"', still)
        for p in (STATIC / "field-pack/cards").glob("*/index.html"):
            m = re.search(r'<img class="card-page-photo"[^>]*>', p.read_text(encoding="utf-8"))
            if m:
                self.assertIn('fetchpriority="high"', m.group(0), p)
                self.assertNotIn('loading="lazy"', m.group(0), p)
        start = (STATIC / "start/index.html").read_text(encoding="utf-8")
        self.assertIn("/start/hero-world-map-1280-v1.webp", start)
        self.assertIn('src="/start/hero-world-map.jpg"', start)

    def test_pass_is_idempotent(self):
        for p in self.pages()[:6]:
            s = p.read_text(encoding="utf-8")
            self.assertEqual(webp_picture.wrap_html(s, {}, is_hub=(p.parent.name == "cards")), s, p)

    def test_lazy_start_panels_arm_webp_sources(self):
        js = (STATIC / "start/start.js").read_text(encoding="utf-8")
        self.assertIn('source[data-srcset]', js)


if __name__ == "__main__":
    unittest.main()
