"""Server-side printable PDF download counter.

Counts a GET of a file under /printables/pdf/ only. Stores
{date: {"paper/stem": {"site"|"search"|"other": n}}} in
$KZK_COUNTS_DIR/pdf-counts-YYYY-MM.json. Never stores IP, UA, the full
Referer, or a query string. A write failure must not change the response.
"""
from __future__ import annotations

import http.client
import json
import os
import threading
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from busyparent_agent.rate_limit import RateLimiter, get_limiter, set_limiter
from busyparent_agent.web import KidZooKitServer, WebHandler, _pdf_canonical_link

REPO = Path(__file__).resolve().parents[1]
PDF_ROOT = REPO / "static" / "printables" / "pdf"
LETTER = "/printables/pdf/letter/scavenger-hunt.pdf"
LETTER_KEY = "letter/scavenger-hunt"
PNG = "/printables/img/scavenger-hunt.png"
PWA_PNG = "/pwa/icon-192.png"
BROWSER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


class PdfDownloadCounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._limiter = get_limiter()
        set_limiter(RateLimiter(enabled=False))
        cls.server = KidZooKitServer(("127.0.0.1", 0), WebHandler)
        cls.port = cls.server.server_address[1]
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        set_limiter(cls._limiter)

    def setUp(self):
        import tempfile

        self._tmp = tempfile.TemporaryDirectory()
        self.counts = Path(self._tmp.name)
        os.environ["KZK_COUNTS_DIR"] = str(self.counts)

    def tearDown(self):
        os.environ.pop("KZK_COUNTS_DIR", None)
        self._tmp.cleanup()

    def _req(self, method, path, headers=None):
        hdrs = {"User-Agent": BROWSER}
        if headers:
            hdrs.update(headers)
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=15)
        conn.request(method, path, headers=hdrs)
        response = conn.getresponse()
        body = response.read()
        status = response.status
        got = {k.lower(): v for k, v in response.getheaders()}
        conn.close()
        return status, got, body

    def _count_file(self):
        files = sorted(self.counts.glob("pdf-counts-*.json"))
        if not files:
            return None, None
        self.assertEqual(len(files), 1, [p.name for p in files])
        return files[0], json.loads(files[0].read_text(encoding="utf-8"))

    def _total(self, key, bucket=None):
        _path, data = self._count_file()
        if not data:
            return 0
        total = 0
        for day in data.values():
            row = (day or {}).get(key) or {}
            if bucket is None:
                total += sum(v for v in row.values() if isinstance(v, int))
            else:
                total += row.get(bucket, 0) or 0
        return total

    def test_get_increments_again_and_from_start_range_counts(self):
        status, _hdrs, body = self._req("GET", LETTER)
        self.assertEqual(status, 200)
        self.assertEqual(body, (PDF_ROOT / "letter" / "scavenger-hunt.pdf").read_bytes())
        self.assertEqual(self._total(LETTER_KEY), 1)
        status, _hdrs, _body = self._req("GET", LETTER)
        self.assertEqual(status, 200)
        self.assertEqual(self._total(LETTER_KEY), 2)
        status, _hdrs, _body = self._req("GET", LETTER, {"Range": "bytes=0-"})
        self.assertEqual(status, 200)
        self.assertEqual(self._total(LETTER_KEY), 3)
        status, _hdrs, _body = self._req("GET", LETTER, {"Range": "bytes=0-100"})
        self.assertEqual(status, 200)
        self.assertEqual(self._total(LETTER_KEY), 4)

        path, data = self._count_file()
        month = datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m")
        day = datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d")
        self.assertEqual(path.name, f"pdf-counts-{month}.json")
        self.assertEqual(set(data), {day})
        self.assertEqual(set(data[day]), {LETTER_KEY})
        self.assertEqual(set(data[day][LETTER_KEY]), {"other"})
        self.assertEqual(data[day][LETTER_KEY]["other"], 4)

    def test_head_notrack_opt_out_bots_and_mid_range_do_not_increment(self):
        cases = (
            ("HEAD", LETTER, None),
            ("GET", LETTER + "?notrack=1", None),
            ("GET", LETTER, {"Cookie": "one_less_analytics=off"}),
            ("GET", LETTER, {"User-Agent": "KidZooKitCheck"}),
            ("GET", LETTER, {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1)"}),
            ("GET", LETTER, {"Range": "bytes=500-"}),
        )
        for method, path, extra in cases:
            with self.subTest(method=method, path=path, extra=extra):
                status, hdrs, body = self._req(method, path, extra)
                self.assertEqual(status, 200)
                if method == "GET":
                    self.assertEqual(body, (PDF_ROOT / "letter" / "scavenger-hunt.pdf").read_bytes())
                self.assertIsNone(self._count_file()[0])
                self.assertEqual(hdrs.get("cache-control"), "no-cache")

    def test_file_holds_no_ip_ua_or_referrer(self):
        marker = "PdfCountUA-203.0.113.9-Unique"
        referer = "https://kidzookit.com/field-pack/amnh/?q=SECRET203.0.113.9"
        status, _hdrs, _body = self._req(
            "GET",
            LETTER,
            {"User-Agent": marker, "Referer": referer},
        )
        self.assertEqual(status, 200)
        self._req(
            "GET",
            "/printables/pdf/letter/animal-bingo.pdf",
            {"User-Agent": marker, "Referer": "https://www.google.com/search?q=zoo+hunt"},
        )
        self._req(
            "GET",
            "/printables/pdf/a4/scavenger-hunt-a4.pdf",
            {"User-Agent": marker, "Referer": "https://www.bing.com/search?q=1"},
        )
        self._req(
            "GET",
            "/printables/pdf/letter/carpool.pdf",
            {"User-Agent": marker, "Referer": "https://duckduckgo.com/?q=park"},
        )
        self._req(
            "GET",
            "/printables/pdf/letter/teacher-handout.pdf",
            {"User-Agent": marker, "Referer": "https://example.com/page?utm=1"},
        )
        path, data = self._count_file()
        text = path.read_text(encoding="utf-8")
        self.assertNotIn(marker, text)
        self.assertNotIn("203.0.113.9", text)
        self.assertNotIn("127.0.0.1", text)
        self.assertNotIn("kidzookit.com", text)
        self.assertNotIn("google.com", text)
        self.assertNotIn("bing.com", text)
        self.assertNotIn("duckduckgo.com", text)
        self.assertNotIn("example.com", text)
        self.assertNotIn("SECRET", text)
        self.assertNotIn("utm", text)
        self.assertNotIn("?", text)
        day = next(iter(data))
        self.assertEqual(data[day]["letter/scavenger-hunt"], {"site": 1})
        self.assertEqual(data[day]["letter/animal-bingo"], {"search": 1})
        self.assertEqual(data[day]["a4/scavenger-hunt"], {"search": 1})
        self.assertEqual(data[day]["letter/carpool"], {"search": 1})
        self.assertEqual(data[day]["letter/teacher-handout"], {"other": 1})
        for row in data[day].values():
            self.assertTrue(set(row) <= {"site", "search", "other"})

    def test_pdf_cache_control_no_cache_and_png_stays_public(self):
        status, hdrs, _body = self._req("GET", LETTER)
        self.assertEqual(status, 200)
        self.assertEqual(hdrs.get("cache-control"), "no-cache")
        status, hdrs, _body = self._req("HEAD", LETTER)
        self.assertEqual(status, 200)
        self.assertEqual(hdrs.get("cache-control"), "no-cache")
        for path in (PNG, PWA_PNG):
            status, hdrs, body = self._req("GET", path)
            self.assertEqual(status, 200, path)
            self.assertEqual(hdrs.get("cache-control"), "public, max-age=86400", path)
            self.assertGreater(len(body), 8, path)

    def test_readonly_counts_dir_still_serves_same_bytes(self):
        disk = (PDF_ROOT / "letter" / "scavenger-hunt.pdf").read_bytes()
        ro = self.counts / "ro"
        ro.mkdir()
        try:
            ro.chmod(0o555)
            os.environ["KZK_COUNTS_DIR"] = str(ro)
            status, hdrs, body = self._req("GET", LETTER)
            self.assertEqual(status, 200)
            self.assertEqual(body, disk)
            self.assertEqual(hdrs.get("cache-control"), "no-cache")
        finally:
            ro.chmod(0o755)

        blocker = self.counts / "not-a-directory"
        blocker.write_bytes(b"x")
        os.environ["KZK_COUNTS_DIR"] = str(blocker / "counts")
        status, hdrs, body = self._req("GET", LETTER)
        self.assertEqual(status, 200)
        self.assertEqual(body, disk)
        self.assertEqual(len(body), len(disk))
        self.assertFalse((blocker / "counts").exists())

    def test_every_pdf_stays_200_with_canonical_link(self):
        groups = (
            sorted(PDF_ROOT.glob("*.pdf")),
            sorted((PDF_ROOT / "letter").glob("*.pdf")),
            sorted((PDF_ROOT / "a4").glob("*-a4.pdf")),
        )
        seen = []
        for group in groups:
            self.assertTrue(group, group)
            for pdf in group:
                rel = pdf.relative_to(PDF_ROOT).as_posix()
                url = f"/printables/pdf/{rel}"
                seen.append(url)
                status, hdrs, body = self._req("GET", url)
                self.assertEqual(status, 200, url)
                self.assertEqual(body, pdf.read_bytes(), url)
                self.assertEqual(hdrs.get("link"), _pdf_canonical_link(url), url)
                self.assertIn('rel="canonical"', hdrs.get("link") or "", url)
                self.assertEqual(hdrs.get("cache-control"), "no-cache", url)
        self.assertGreaterEqual(len(seen), 18)
        self.assertEqual(len(seen), len(set(seen)))


if __name__ == "__main__":
    unittest.main()
