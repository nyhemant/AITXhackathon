"""Sitemap must stay a static 200 at the robots.txt URL."""

from __future__ import annotations

import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

from busyparent_agent.web import WebHandler, _sitemap_bytes, _SITEMAP_URLS, _static_content_type


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from generate_bdo_seo import (  # noqa: E402
    SITE,
    collect_sitemap_extra_urls,
    is_redirect_only_url,
    lastmod_for_paths,
    lastmod_for_url,
    source_paths_for_url,
    write_sitemap,
)


_LASTMOD_RE = re.compile(r"<lastmod>([^<]+)</lastmod>")
_LOC_RE = re.compile(r"<loc>([^<]+)</loc>")
_REDIRECT_LOCS = (
    "https://1less.app/field-pack/print/",
    "https://1less.app/field-pack/virtual-zoo/",
    "https://1less.app/field-pack/parks/",
    "https://1less.app/field-pack/app.html",
    "https://1less.app/field-pack/cards/giraffe/",
    "https://1less.app/field-pack/cards/lion/",
)


class SitemapTests(unittest.TestCase):
    def test_static_sitemap_bytes_are_xml(self):
        body = _sitemap_bytes()
        self.assertTrue(body.startswith(b"<?xml"))
        self.assertIn(b"<urlset", body)
        self.assertIn(b"https://1less.app/field-pack/", body)
        self.assertIn(b"https://1less.app/about/", body)

    def test_sitemap_paths_are_the_robots_and_alias_urls(self):
        self.assertEqual(_SITEMAP_URLS, ("/sitemap.xml", "/field-pack/sitemap.xml"))

    def test_xml_content_type(self):
        self.assertEqual(
            _static_content_type(Path("sitemap.xml")),
            "application/xml; charset=utf-8",
        )

    def test_static_files_exist(self):
        self.assertTrue((REPO / "static" / "sitemap.xml").is_file())
        self.assertTrue((REPO / "static" / "field-pack" / "sitemap.xml").is_file())

    def test_both_sitemaps_include_live_card_urls(self):
        expected_locs = (
            "https://1less.app/field-pack/cards/cuttlefish/",
            "https://1less.app/field-pack/cards/kelp-forest/",
            "https://1less.app/field-pack/cards/manta-ray/",
            "https://1less.app/field-pack/cards/puffin/",
            "https://1less.app/field-pack/cards/sea-otter/",
            "https://1less.app/field-pack/cards/whale-shark/",
            "https://1less.app/about/",
        )
        sitemap_paths = (
            REPO / "static" / "sitemap.xml",
            REPO / "static" / "field-pack" / "sitemap.xml",
        )

        for sitemap_path in sitemap_paths:
            sitemap_text = sitemap_path.read_text(encoding="utf-8")
            for loc in expected_locs:
                self.assertIn(f"<loc>{loc}</loc>", sitemap_text)

    def test_handler_serves_sitemap_200(self):
        class FakeHandler(WebHandler):
            def __init__(self):
                self.path = "/sitemap.xml"
                self.headers = {}
                self._code = None
                self._headers = {}
                self.wfile = _Buf()

            def send_response(self, code, message=None):
                self._code = code

            def send_header(self, k, v):
                self._headers[k] = v

            def end_headers(self):
                return

            def log_message(self, format, *args):
                return

        h = FakeHandler()
        h.do_GET()
        self.assertEqual(h._code, 200)
        self.assertEqual(h._headers.get("Content-Type"), "application/xml; charset=utf-8")
        self.assertTrue(h.wfile.getvalue().startswith(b"<?xml"))

    def test_robots_still_points_at_root_sitemap(self):
        robots = (REPO / "static" / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://1less.app/sitemap.xml", robots)

    def test_canonical_ia_urls_present_redirects_omitted(self):
        extras = collect_sitemap_extra_urls()
        self.assertIn("/field-pack/virtual-field-trip/", extras)
        self.assertIn("/field-pack/national-parks/", extras)
        self.assertIn("/start/", extras)
        self.assertIn("/about/", extras)
        self.assertIn("/field-pack/cards/", extras)
        self.assertNotIn("/field-pack/print/", extras)
        self.assertNotIn("/field-pack/virtual-zoo/", extras)
        self.assertNotIn("/field-pack/parks/", extras)
        self.assertTrue(is_redirect_only_url("/field-pack/print/"))
        self.assertTrue(is_redirect_only_url("/field-pack/virtual-zoo/"))
        self.assertTrue(is_redirect_only_url("/field-pack/parks/"))
        self.assertTrue(is_redirect_only_url("/field-pack/app.html"))
        self.assertTrue(is_redirect_only_url("/field-pack/cards/giraffe/"))
        self.assertFalse(is_redirect_only_url("/field-pack/virtual-field-trip/"))
        self.assertFalse(is_redirect_only_url("/field-pack/cards/reticulated-giraffe/"))

        sitemap_paths = (
            REPO / "static" / "sitemap.xml",
            REPO / "static" / "field-pack" / "sitemap.xml",
        )
        for sitemap_path in sitemap_paths:
            text = sitemap_path.read_text(encoding="utf-8")
            self.assertIn("<loc>https://1less.app/field-pack/virtual-field-trip/</loc>", text)
            self.assertIn("<loc>https://1less.app/field-pack/national-parks/</loc>", text)
            self.assertIn("<loc>https://1less.app/start/</loc>", text)
            for loc in _REDIRECT_LOCS:
                self.assertNotIn(f"<loc>{loc}</loc>", text)

    def test_lastmod_uses_file_mtime_when_git_is_silent(self):
        with tempfile.TemporaryDirectory() as raw:
            older = Path(raw) / "older.txt"
            newer = Path(raw) / "newer.txt"
            older.write_text("old", encoding="utf-8")
            newer.write_text("new", encoding="utf-8")
            # Midday UTC so local-calendar mtime stays on the intended day.
            os.utime(older, (1_724_068_800, 1_724_068_800))  # 2024-08-19
            os.utime(newer, (1_756_987_200, 1_756_987_200))  # 2025-09-04
            silent = lambda path: None  # noqa: E731
            old_stamp = lastmod_for_paths([older], git_lookup=silent, today="1999-01-01")
            new_stamp = lastmod_for_paths([newer], git_lookup=silent, today="1999-01-01")
            both = lastmod_for_paths([older, newer], git_lookup=silent, today="1999-01-01")
            self.assertEqual(old_stamp, "2024-08-19")
            self.assertEqual(new_stamp, "2025-09-04")
            self.assertEqual(both, new_stamp)
            # A constant today fallback would ignore mtimes — refuse that.
            self.assertNotEqual(old_stamp, "1999-01-01")

    def test_source_paths_prefer_venue_json_over_generated_html(self):
        yellowstone = source_paths_for_url("https://1less.app/field-pack/yellowstone/")
        self.assertEqual(
            [p.name for p in yellowstone],
            ["yellowstone.json"],
        )
        start = source_paths_for_url("https://1less.app/start/")
        self.assertTrue(any(p.name == "index.html" for p in start))
        vft = source_paths_for_url("/field-pack/virtual-field-trip/")
        self.assertTrue(any(p.name == "virtual-venue.js" for p in vft))

    def test_generator_lastmods_are_not_one_constant(self):
        start = lastmod_for_url(f"{SITE}/start/")
        about = lastmod_for_url(f"{SITE}/about/")
        yellowstone = lastmod_for_url(f"{SITE}/field-pack/yellowstone/")
        cards = lastmod_for_url(f"{SITE}/field-pack/cards/")
        self.assertGreaterEqual(start, "2026-09-01")
        self.assertGreaterEqual(about, "2026-09-01")
        self.assertGreaterEqual(cards, "2026-09-01")
        self.assertLess(yellowstone, start)
        self.assertNotEqual({start, about, yellowstone, cards}, {start})

    def test_committed_sitemap_lastmods_are_not_stuck(self):
        root = (REPO / "static" / "sitemap.xml").read_text(encoding="utf-8")
        copy = (REPO / "static" / "field-pack" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(root, copy)
        lastmods = _LASTMOD_RE.findall(root)
        locs = _LOC_RE.findall(root)
        self.assertGreaterEqual(len(locs), 200)
        self.assertEqual(len(locs), len(lastmods))
        unique = set(lastmods)
        self.assertGreaterEqual(
            len(unique),
            3,
            f"sitemap lastmods collapsed to {unique}",
        )
        self.assertTrue(
            any(d >= "2026-09-01" for d in lastmods),
            "expected September lastmods on recently touched surfaces",
        )
        # A regen that stamps TODAY or 2026-08-23 on every URL fails here.
        self.assertLess(min(lastmods), max(lastmods))
        loc_to_mod = dict(zip(locs, lastmods))
        for loc in (
            "https://1less.app/start/",
            "https://1less.app/about/",
            "https://1less.app/field-pack/cards/",
            "https://1less.app/field-pack/virtual-field-trip/",
        ):
            self.assertGreaterEqual(loc_to_mod[loc], "2026-09-01", loc)

    def test_write_sitemap_respects_per_url_lastmod(self):
        stamps = {
            f"{SITE}/field-pack/": "2026-09-10",
            f"{SITE}/start/": "2026-09-12",
            f"{SITE}/field-pack/dallas-zoo/": "2026-08-08",
        }

        def fake_lastmod(url: str) -> str:
            return stamps.get(url, "2026-01-01")

        root = REPO / "static" / "sitemap.xml"
        copy = REPO / "static" / "field-pack" / "sitemap.xml"
        before_root = root.read_text(encoding="utf-8")
        before_copy = copy.read_text(encoding="utf-8")
        try:
            write_sitemap(
                [{"id": "dallas-zoo"}],
                extra_urls=["/start/", "/field-pack/print/"],
                lastmod_fn=fake_lastmod,
            )
            text = root.read_text(encoding="utf-8")
            self.assertIn("<lastmod>2026-09-12</lastmod>", text)
            self.assertIn("<lastmod>2026-08-08</lastmod>", text)
            self.assertNotIn("<loc>https://1less.app/field-pack/print/</loc>", text)
            self.assertNotEqual(text.count("<lastmod>2026-09-12</lastmod>"), text.count("<lastmod>"))
        finally:
            root.write_text(before_root, encoding="utf-8")
            copy.write_text(before_copy, encoding="utf-8")


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


if __name__ == "__main__":
    unittest.main()
