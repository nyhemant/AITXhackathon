"""Place-page photos, last-checked dates, and kit-aware Learn more labels."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATIC = REPO / "static"
FIELD = STATIC / "field-pack"
GEN = (REPO / "scripts" / "generate_bdo_seo.py").read_text(encoding="utf-8")

PLACES = {
    "sequoia": ("2026-08-09", "August 9, 2026", "np-hero-sequoia.jpg"),
    "taronga-zoo": ("2026-08-23", "August 23, 2026", "koala.jpg"),
    "calgary-zoo": ("2026-08-23", "August 23, 2026", "western-lowland-gorilla.jpg"),
    "amnh": ("2026-08-08", "August 8, 2026", "sci-dinosaur.jpg"),
}


class PlacePhotoDateTests(unittest.TestCase):
    def test_four_impression_pages_have_photo_and_last_checked(self):
        for slug, (iso, label, photo) in PLACES.items():
            html = (FIELD / slug / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("sample-mission-dallas-zoo", html, slug)
            self.assertIn(f"/field-pack/photos/{photo}", html, slug)
            self.assertIn(f"Last checked</span><span class=\"seo-fact-v\">{label}</span>", html, slug)
            article = None
            for m in re.finditer(r'<script type="application/ld\+json">', html):
                start = html.find("{", m.end())
                data, _end = json.JSONDecoder().raw_decode(html, start)
                if data.get("@type") == "Article":
                    article = data
                    break
            self.assertIsNotNone(article, slug)
            self.assertIn(photo, article.get("image") or "", slug)
            self.assertEqual(article.get("dateModified"), iso, slug)
            pub = article.get("publisher") or {}
            self.assertEqual(pub.get("url"), "https://kidzookit.com/start/", slug)
            self.assertIn("icon-512.png", (pub.get("logo") or {}).get("url") or "", slug)

    def test_air_and_space_mentions_udvar_hazy_in_title(self):
        html = (FIELD / "air-and-space" / "index.html").read_text(encoding="utf-8")
        self.assertIn("Udvar-Hazy", html)
        title = re.search(r"<title>(.*?)</title>", html).group(1)
        self.assertIn("Udvar-Hazy", title.replace("&amp;", "&"))
        self.assertLessEqual(len(title.replace("&amp;", "&")), 60)
        desc = re.search(r'<meta name="description" content="(.*?)" />', html).group(1)
        self.assertIn("Udvar-Hazy", desc.replace("&amp;", "&"))
        self.assertLessEqual(len(desc.replace("&amp;", "&")), 155)
        self.assertIsNone(re.search(r"\bfree\b|\bno-cost\b", desc, flags=re.I))

    def test_california_science_center_keeps_title_and_names_la(self):
        html = (FIELD / "california-science-center" / "index.html").read_text(encoding="utf-8")
        self.assertIn("<title>California Science Center Scavenger Hunt for Kids</title>", html)
        desc = re.search(r'<meta name="description" content="(.*?)" />', html).group(1)
        self.assertIn("Los Angeles", desc)
        self.assertIn("science museum", desc.lower())
        self.assertLessEqual(len(desc.replace("&amp;", "&")), 155)
        self.assertIsNone(re.search(r"\bfree\b|\bno-cost\b", desc, flags=re.I))

    def test_hidden_card_learn_more_says_all_places_and_js_names_the_place(self):
        n = 0
        for p in (FIELD / "cards").glob("*/index.html"):
            html = p.read_text(encoding="utf-8")
            if "card-learn-more" not in html:
                continue
            if 'href="/field-pack/" hidden' in html:
                self.assertIn(">All places</a>", html, p)
                self.assertNotIn(
                    'card-learn-more" href="/field-pack/" hidden target="_blank" rel="noopener noreferrer">Learn more</a>',
                    html,
                    p,
                )
                n += 1
            self.assertIn("if (KIT_NAMES[from]) more.textContent = KIT_NAMES[from];", html, p)
        self.assertGreaterEqual(n, 30)
        self.assertIn("All places</a>", GEN)
        self.assertIn("if (KIT_NAMES[from]) more.textContent = KIT_NAMES[from];", GEN)


if __name__ == "__main__":
    unittest.main()
