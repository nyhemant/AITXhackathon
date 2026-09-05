"""Field Trip Kit PWA: manifest, icons, service worker, quiet install."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from busyparent_agent.web import (
    PWA_ROOT,
    SECURITY_HEADERS,
    WebHandler,
    _safe_pwa_path,
    _safe_pwa_root_file,
    _static_content_type,
)


REPO = Path(__file__).resolve().parents[1]
START_HTML = REPO / "static" / "start" / "index.html"
VFT_PAGES = (
    REPO / "static" / "field-pack" / "virtual-field-trip" / "index.html",
    REPO / "static" / "field-pack" / "virtual-zoo" / "index.html",
)
MANIFEST = PWA_ROOT / "manifest.webmanifest"
SW = PWA_ROOT / "sw.js"
REGISTER = PWA_ROOT / "register.js"
ICON_NAMES = (
    "icon-192.png",
    "icon-512.png",
    "icon-192-maskable.png",
    "icon-512-maskable.png",
    "apple-touch-icon.png",
)


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


class FakeHandler(WebHandler):
    def __init__(self, path):
        self.path = path
        self.headers = {}
        self._code = None
        self._headers = {}
        self.wfile = _Buf()

    def send_response(self, code, message=None):
        self._code = code

    def send_error(self, code, message=None):
        self._code = code

    def send_header(self, k, v):
        self._headers[k] = v

    def end_headers(self):
        return

    def log_message(self, format, *args):
        return


def _get(path: str) -> FakeHandler:
    h = FakeHandler(path)
    h.do_GET()
    return h


class PwaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.start = START_HTML.read_text(encoding="utf-8")
        cls.vft = {p: p.read_text(encoding="utf-8") for p in VFT_PAGES}
        cls.sw = SW.read_text(encoding="utf-8")
        cls.register = REGISTER.read_text(encoding="utf-8")
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_is_served_with_correct_type(self):
        self.assertTrue(MANIFEST.is_file())
        self.assertEqual(
            _static_content_type(MANIFEST),
            "application/manifest+json",
        )
        self.assertIsNotNone(_safe_pwa_root_file("/manifest.webmanifest"))
        self.assertIsNone(_safe_pwa_root_file("/pwa/../sw.js"))
        served = _get("/manifest.webmanifest")
        self.assertEqual(served._code, 200)
        self.assertEqual(served._headers.get("Content-Type"), "application/manifest+json")
        self.assertEqual(served._headers.get("Cache-Control"), "no-cache")
        body = json.loads(served.wfile.getvalue().decode("utf-8"))
        self.assertEqual(body["id"], "https://1less.app/field-trip-kit")
        self.assertEqual(body["name"], "Field Trip Kit")
        self.assertLessEqual(len(body["short_name"]), 12)
        self.assertEqual(body["short_name"], "1less")
        self.assertEqual(body["start_url"], "/start/?source=pwa")
        self.assertEqual(body["scope"], "/")
        self.assertEqual(body["display"], "standalone")
        self.assertEqual(body["background_color"], "#f6f3ec")
        self.assertEqual(body["theme_color"], "#0a4545")
        self.assertIn("/field-pack/virtual-field-trip/", json.dumps(body["shortcuts"]))
        self.assertIn("/field-pack/", json.dumps(body["shortcuts"]))
        self.assertIn("Watch Live", json.dumps(body["shortcuts"]))

    def test_icons_are_pngs_from_the_brand_mark(self):
        sizes = {}
        for name in ICON_NAMES:
            path = PWA_ROOT / name
            self.assertTrue(path.is_file(), name)
            data = path.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"), name)
            self.assertIsNotNone(_safe_pwa_path(f"/pwa/{name}"), name)
            served = _get(f"/pwa/{name}")
            self.assertEqual(served._code, 200, name)
            self.assertEqual(served._headers.get("Content-Type"), "image/png", name)
            sizes[name] = (data[16:20], data[20:24])
        self.assertEqual(sizes["icon-192.png"], (b"\x00\x00\x00\xc0", b"\x00\x00\x00\xc0"))
        self.assertEqual(sizes["icon-512.png"], (b"\x00\x00\x02\x00", b"\x00\x00\x02\x00"))
        self.assertEqual(sizes["apple-touch-icon.png"], (b"\x00\x00\x00\xb4", b"\x00\x00\x00\xb4"))
        srcs = {icon["src"] for icon in self.manifest["icons"]}
        self.assertIn("/pwa/icon-192.png", srcs)
        self.assertIn("/pwa/icon-512.png", srcs)
        purposes = {icon["src"]: icon.get("purpose") for icon in self.manifest["icons"]}
        self.assertEqual(purposes["/pwa/icon-192-maskable.png"], "maskable")
        self.assertEqual(purposes["/pwa/icon-512-maskable.png"], "maskable")

    def test_service_worker_is_same_origin_and_careful(self):
        self.assertTrue(SW.is_file())
        self.assertIsNotNone(_safe_pwa_root_file("/sw.js"))
        served = _get("/sw.js")
        self.assertEqual(served._code, 200)
        self.assertEqual(served._headers.get("Content-Type"), "application/javascript; charset=utf-8")
        self.assertEqual(served._headers.get("Cache-Control"), "no-cache")
        self.assertEqual(served._headers.get("Service-Worker-Allowed"), "/")
        self.assertIn('FTK_SHELL_CACHE = "ftk-shell-v1"', self.sw)
        self.assertIn("skipWaiting()", self.sw)
        self.assertIn("clients.claim()", self.sw)
        self.assertIn("networkFirst", self.sw)
        self.assertIn("cacheFirst", self.sw)
        self.assertIn("/start", self.sw)
        self.assertIn("/field-pack/virtual-zoo", self.sw)
        self.assertIn("/field-pack/virtual-field-trip", self.sw)
        self.assertIn("youtube", self.sw.lower())
        self.assertIn("antmedia", self.sw.lower())
        self.assertIn("shouldBypass", self.sw)
        self.assertNotIn("eval(", self.sw)
        self.assertNotIn("importScripts", self.sw)
        self.assertIn('register("/sw.js"', self.register)
        self.assertIn('scope: "/"', self.register)
        self.assertNotIn("beforeinstallprompt", self.register)
        self.assertIn("ftk-pwa-ios-tip-dismissed-v1", self.register)
        self.assertIn("Add to Home Screen", self.register)

    def test_start_and_vft_link_manifest_and_register(self):
        pages = [self.start, *self.vft.values()]
        for html in pages:
            self.assertIn('rel="manifest" href="/manifest.webmanifest"', html)
            self.assertIn('rel="apple-touch-icon" href="/pwa/apple-touch-icon.png"', html)
            self.assertIn('name="theme-color" content="#0a4545"', html)
            self.assertIn('name="apple-mobile-web-app-capable" content="yes"', html)
            self.assertIn('name="apple-mobile-web-app-status-bar-style" content="default"', html)
            self.assertIn('name="apple-mobile-web-app-title" content="1less"', html)
            self.assertIn('src="/pwa/register.js?v=1"', html)
            self.assertIn("viewport-fit=cover", html)
        self.assertIn("start.css?v=21", self.start)
        self.assertIn(".start-pwa-tip", (REPO / "static" / "start" / "start.css").read_text(encoding="utf-8"))
        for html in self.vft.values():
            self.assertIn('href="/pwa/pwa.css?v=1"', html)
            self.assertIn("virtual-venue.css?v=56", html)
            self.assertIn("virtual-venue.js?v=96", html)

    def test_register_is_served_and_csp_allows_worker(self):
        js = _get("/pwa/register.js")
        self.assertEqual(js._code, 200)
        self.assertEqual(js._headers.get("Content-Type"), "application/javascript; charset=utf-8")
        css = _get("/pwa/pwa.css")
        self.assertEqual(css._code, 200)
        self.assertEqual(css._headers.get("Content-Type"), "text/css; charset=utf-8")
        csp = SECURITY_HEADERS["Content-Security-Policy"]
        self.assertIn("default-src 'self'", csp)
        self.assertIn("worker-src 'self'", csp)
        self.assertIn("https://www.youtube-nocookie.com", csp)
        self.assertIn("https://ams-28635.antmedia.cloud:5443", csp)

    def test_start_and_vft_routes_still_200(self):
        start = _get("/start/")
        self.assertEqual(start._code, 200)
        body = start.wfile.getvalue().decode("utf-8")
        self.assertIn("A ready-to-use field trip for curious kids.", body)
        self.assertIn('rel="manifest"', body)
        self.assertNotIn("beforeinstallprompt", body)
        vft = _get("/field-pack/virtual-field-trip/")
        self.assertEqual(vft._code, 200)
        self.assertIn(b'rel="manifest"', vft.wfile.getvalue())
        zoo = _get("/field-pack/virtual-zoo/")
        self.assertEqual(zoo._code, 200)
        self.assertIn(b"A zoo day at home", zoo.wfile.getvalue())
        self.assertIn(b'rel="manifest"', zoo.wfile.getvalue())

    def test_quiet_install_is_not_in_start_markup(self):
        self.assertNotIn("start-pwa-tip", self.start)
        self.assertNotIn("Add to Home Screen", self.start)
        self.assertNotIn("beforeinstallprompt", self.start)
        self.assertIsNone(re.search(r"install now", self.start, re.I))


if __name__ == "__main__":
    unittest.main()
