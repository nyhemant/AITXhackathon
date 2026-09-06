"""Root static allowlist: robots, sitemap, and Google Search Console tags."""

from pathlib import Path
import unittest

from busyparent_agent.web import (
    STATIC_ROOT,
    WebHandler,
    _is_allowed_static_root_name,
    _root_static_content_type,
    _safe_static_root_file,
)


GSC_NAME = "google271ca6586619f22f.html"
GSC_PATH = f"/{GSC_NAME}"
REPO = Path(__file__).resolve().parents[1]


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


class FakeHandler(WebHandler):
    def __init__(self, path, command="GET"):
        self.path = path
        self.command = command
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


class StaticRootFileTests(unittest.TestCase):
    def test_allows_google_search_console_html(self):
        self.assertTrue(_is_allowed_static_root_name(GSC_NAME))
        resolved = _safe_static_root_file(GSC_PATH)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved, (STATIC_ROOT / GSC_NAME).resolve())
        self.assertTrue(resolved.is_file())
        self.assertEqual(
            _root_static_content_type(resolved),
            "text/html; charset=utf-8",
        )

    def test_allows_robots_and_sitemap(self):
        self.assertEqual(
            _safe_static_root_file("/robots.txt"),
            (STATIC_ROOT / "robots.txt").resolve(),
        )
        self.assertEqual(
            _safe_static_root_file("/sitemap.xml"),
            (STATIC_ROOT / "sitemap.xml").resolve(),
        )

    def test_rejects_other_html_and_unknown_names(self):
        self.assertFalse(_is_allowed_static_root_name("index.html"))
        self.assertFalse(_is_allowed_static_root_name("google271ca6586619f22f.txt"))
        self.assertIsNone(_safe_static_root_file("/index.html"))
        self.assertIsNone(_safe_static_root_file("/not-google.html"))

    def test_rejects_path_traversal(self):
        traversal_paths = (
            f"/../{GSC_NAME}",
            f"/foo/../{GSC_NAME}",
            f"/{GSC_NAME}/../../{GSC_NAME}",
            f"/field-pack/../{GSC_NAME}",
            "/../etc/passwd",
            f"/..%2F{GSC_NAME}",
            f"/%2e%2e/{GSC_NAME}",
            f"/{GSC_NAME}/../../../src/busyparent_agent/web.py",
            f"/static/../{GSC_NAME}",
        )
        for path in traversal_paths:
            with self.subTest(path=path):
                self.assertFalse(
                    _is_allowed_static_root_name(path.lstrip("/")),
                    f"raw name should be rejected: {path}",
                )
                self.assertIsNone(
                    _safe_static_root_file(path),
                    f"traversal must not resolve: {path}",
                )

    def test_rejects_nested_google_html(self):
        self.assertIsNone(_safe_static_root_file(f"/pwa/{GSC_NAME}"))
        self.assertIsNone(_safe_static_root_file(f"/field-pack/{GSC_NAME}"))

    def test_get_and_head_serve_gsc_html(self):
        expected = (REPO / "static" / GSC_NAME).read_bytes()
        get_handler = FakeHandler(GSC_PATH)
        get_handler.do_GET()
        self.assertEqual(get_handler._code, 200)
        self.assertEqual(
            get_handler._headers.get("Content-Type"),
            "text/html; charset=utf-8",
        )
        self.assertEqual(get_handler.wfile.getvalue(), expected)

        head_handler = FakeHandler(GSC_PATH, command="HEAD")
        head_handler.do_HEAD()
        self.assertEqual(head_handler._code, 200)
        self.assertEqual(
            head_handler._headers.get("Content-Type"),
            "text/html; charset=utf-8",
        )
        self.assertEqual(
            int(head_handler._headers.get("Content-Length")),
            len(expected),
        )
        self.assertEqual(head_handler.wfile.getvalue(), b"")


if __name__ == "__main__":
    unittest.main()
