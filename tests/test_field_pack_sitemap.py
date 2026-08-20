"""Sitemap must stay a static 200 at the robots.txt URL."""

from pathlib import Path
import unittest

from busyparent_agent.web import WebHandler, _sitemap_bytes, _SITEMAP_URLS, _static_content_type


REPO = Path(__file__).resolve().parents[1]


class SitemapTests(unittest.TestCase):
    def test_static_sitemap_bytes_are_xml(self):
        body = _sitemap_bytes()
        self.assertTrue(body.startswith(b"<?xml"))
        self.assertIn(b"<urlset", body)
        self.assertIn(b"https://1less.app/field-pack/", body)

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


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


if __name__ == "__main__":
    unittest.main()
