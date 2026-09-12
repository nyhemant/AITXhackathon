"""Legacy 1less.app Host headers 301 to https://kidzookit.com."""

from __future__ import annotations

import unittest

from busyparent_agent.site import PUBLIC_SITE, host_redirect_location
from busyparent_agent.web import WebHandler


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


class FakeHandler(WebHandler):
    def __init__(self, path, host=None, command="GET"):
        self.path = path
        self.command = command
        self.headers = {} if host is None else {"Host": host}
        self._code = None
        self._headers = {}
        self.wfile = _Buf()

    def send_response(self, code, message=None):
        self._code = code

    def send_error(self, code, message=None):
        self._code = code

    def send_header(self, key, value):
        self._headers[key] = value

    def end_headers(self):
        return

    def log_message(self, format, *args):
        return


def _get(path: str, host: str | None) -> FakeHandler:
    h = FakeHandler(path, host=host)
    h.do_GET()
    return h


def _head(path: str, host: str | None) -> FakeHandler:
    h = FakeHandler(path, host=host, command="HEAD")
    h.do_HEAD()
    return h


class PublicHostRedirectTests(unittest.TestCase):
    def test_public_site_default_is_kidzookit(self):
        self.assertEqual(PUBLIC_SITE, "https://kidzookit.com")

    def test_1less_host_301s_to_kidzookit_same_path_query(self):
        for host in ("1less.app", "www.1less.app", "1less.app:443"):
            h = _get("/field-pack/dallas-zoo/?from=chip", host)
            self.assertEqual(h._code, 301, host)
            self.assertEqual(
                h._headers.get("Location"),
                "https://kidzookit.com/field-pack/dallas-zoo/?from=chip",
                host,
            )
            self.assertEqual(h.wfile.getvalue(), b"")
            head = _head("/field-pack/dallas-zoo/?from=chip", host)
            self.assertEqual(head._code, 301, host)
            self.assertEqual(
                head._headers.get("Location"),
                "https://kidzookit.com/field-pack/dallas-zoo/?from=chip",
                host,
            )

    def test_www_kidzookit_301s_to_apex(self):
        h = _get("/start/?utm=1", "www.kidzookit.com")
        self.assertEqual(h._code, 301)
        self.assertEqual(h._headers.get("Location"), "https://kidzookit.com/start/?utm=1")

    def test_canonical_and_local_hosts_do_not_redirect(self):
        for host in (None, "kidzookit.com", "127.0.0.1", "localhost:8000"):
            h = _get("/field-pack/", host)
            self.assertEqual(h._code, 200, host)
            self.assertIsNone(h._headers.get("Location"), host)

    def test_legacy_path_on_1less_is_one_hop_or_host_first(self):
        # Host redirect first (same path). Path alias then runs on kidzookit.
        h = _get("/field-pack/virtual-zoo/?from=card", "1less.app")
        self.assertEqual(h._code, 301)
        self.assertEqual(
            h._headers.get("Location"),
            "https://kidzookit.com/field-pack/virtual-zoo/?from=card",
        )
        # Same alias on the canonical host still 301s to the VFT path.
        canonical = _get("/field-pack/virtual-zoo/?from=card", "kidzookit.com")
        self.assertEqual(canonical._code, 301)
        self.assertEqual(
            canonical._headers.get("Location"),
            "/field-pack/virtual-field-trip/?from=card",
        )

    def test_health_on_legacy_host_is_not_redirected(self):
        self.assertIsNone(host_redirect_location("1less.app", "/health"))
        h = _get("/health", "1less.app")
        self.assertNotEqual(h._code, 301)
        self.assertIsNone(h._headers.get("Location"))


if __name__ == "__main__":
    unittest.main()
