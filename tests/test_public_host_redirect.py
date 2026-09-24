"""Legacy 1less.app Host headers 301 to https://kidzookit.com."""

from __future__ import annotations

import unittest

from busyparent_agent.site import (
    PUBLIC_SITE,
    host_redirect_location,
    https_upgrade_location,
    visitor_scheme,
)
from busyparent_agent.web import WebHandler


class _Buf:
    def __init__(self):
        self._b = bytearray()

    def write(self, data):
        self._b.extend(data)

    def getvalue(self):
        return bytes(self._b)


class FakeHandler(WebHandler):
    def __init__(self, path, host=None, command="GET", extra_headers=None):
        self.path = path
        self.command = command
        self.headers = {} if host is None else {"Host": host}
        if extra_headers:
            self.headers.update(extra_headers)
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


def _get(path: str, host: str | None, extra_headers=None) -> FakeHandler:
    h = FakeHandler(path, host=host, extra_headers=extra_headers)
    h.do_GET()
    return h


def _head(path: str, host: str | None, extra_headers=None) -> FakeHandler:
    h = FakeHandler(path, host=host, command="HEAD", extra_headers=extra_headers)
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

    def test_apex_home_301s_to_absolute_start(self):
        for path in ("/", "/index.html"):
            h = _get(path, "kidzookit.com")
            self.assertEqual(h._code, 301, path)
            self.assertEqual(h._headers.get("Location"), "https://kidzookit.com/start/", path)
            head = _head(path, "kidzookit.com")
            self.assertEqual(head._code, 301, path)
            self.assertEqual(head._headers.get("Location"), "https://kidzookit.com/start/", path)

    def test_local_home_stays_relative_301(self):
        h = _get("/", None)
        self.assertEqual(h._code, 301)
        self.assertEqual(h._headers.get("Location"), "/start/")

    def test_plain_http_on_apex_301s_to_https(self):
        headers = {"X-Forwarded-Proto": "http"}
        start = _get("/start/", "kidzookit.com", headers)
        self.assertEqual(start._code, 301)
        self.assertEqual(start._headers.get("Location"), "https://kidzookit.com/start/")
        head = _head("/start/", "kidzookit.com", headers)
        self.assertEqual(head._code, 301)
        self.assertEqual(head._headers.get("Location"), "https://kidzookit.com/start/")

        home = _get("/?utm=1", "kidzookit.com", headers)
        self.assertEqual(home._code, 301)
        self.assertEqual(home._headers.get("Location"), "https://kidzookit.com/start/")

        slashless = _get("/start", "kidzookit.com", headers)
        self.assertEqual(slashless._code, 301)
        self.assertEqual(slashless._headers.get("Location"), "https://kidzookit.com/start/")

        place = _get("/field-pack/dallas-zoo/?from=chip", "kidzookit.com", headers)
        self.assertEqual(place._code, 301)
        self.assertEqual(
            place._headers.get("Location"),
            "https://kidzookit.com/field-pack/dallas-zoo/?from=chip",
        )

    def test_cf_visitor_http_upgrades_and_https_does_not(self):
        http_headers = {"CF-Visitor": '{"scheme":"http"}'}
        h = _get("/start/", "kidzookit.com", http_headers)
        self.assertEqual(h._code, 301)
        self.assertEqual(h._headers.get("Location"), "https://kidzookit.com/start/")

        # Visitor scheme wins over a conflicting forwarded proto (Flexible SSL).
        mixed = {
            "CF-Visitor": '{"scheme":"https"}',
            "X-Forwarded-Proto": "http",
        }
        self.assertEqual(visitor_scheme(mixed), "https")
        stay = _get("/start/", "kidzookit.com", mixed)
        self.assertEqual(stay._code, 200)
        self.assertIsNone(stay._headers.get("Location"))

    def test_https_and_local_do_not_upgrade(self):
        https_headers = {"X-Forwarded-Proto": "https"}
        h = _get("/start/", "kidzookit.com", https_headers)
        self.assertEqual(h._code, 200)
        self.assertIsNone(h._headers.get("Location"))

        local = _get("/start/", "127.0.0.1", {"X-Forwarded-Proto": "http"})
        self.assertEqual(local._code, 200)
        self.assertIsNone(https_upgrade_location("127.0.0.1", "/start/", {"X-Forwarded-Proto": "http"}))

    def test_plain_http_health_is_not_upgraded(self):
        headers = {"X-Forwarded-Proto": "http"}
        self.assertIsNone(https_upgrade_location("kidzookit.com", "/health", headers))
        h = _get("/health", "kidzookit.com", headers)
        self.assertNotEqual(h._code, 301)
        self.assertIsNone(h._headers.get("Location"))


if __name__ == "__main__":
    unittest.main()
