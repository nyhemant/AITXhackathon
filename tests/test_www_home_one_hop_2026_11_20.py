"""Round 2 item 3 (2026-11-20): www.kidzookit.com home lands on /start/ in one 301; 1less.app hosts unchanged."""

from __future__ import annotations

import itertools
import unittest

from busyparent_agent.site import host_redirect_location

try:
    from test_public_host_redirect import _get, _head
except ImportError:  # run as tests.<module>
    from tests.test_public_host_redirect import _get, _head

LESS_HOSTS = ("1less.app", "www.1less.app", "1less.app:443", "WWW.1LESS.APP")
PATHS = ("/", "/?utm_source=qr", "/index.html", "/start", "/start/", "/field-pack/dallas-zoo/?from=chip",
         "/field-pack/virtual-zoo/", "/printables/", "/sitemap.xml", "/about/")


class WwwHomeOneHop(unittest.TestCase):
    def test_www_home_goes_straight_to_start(self):
        for host in ("www.kidzookit.com", "www.kidzookit.com:443"):
            for path, want in (
                ("/", "https://kidzookit.com/start/"),
                ("/?utm_source=qr", "https://kidzookit.com/start/?utm_source=qr"),
                ("/index.html", "https://kidzookit.com/start/"),
                ("/start", "https://kidzookit.com/start/"),
                ("/start?x=1", "https://kidzookit.com/start/?x=1"),
            ):
                with self.subTest(host=host, path=path):
                    h = _get(path, host)
                    self.assertEqual(h._code, 301)
                    self.assertEqual(h._headers.get("Location"), want)
                    self.assertEqual(_head(path, host)._headers.get("Location"), want)

    def test_other_www_paths_keep_path_and_query(self):
        self.assertEqual(host_redirect_location("www.kidzookit.com", "/start/?utm=1"), "https://kidzookit.com/start/?utm=1")
        self.assertEqual(host_redirect_location("www.kidzookit.com", "/printables/"), "https://kidzookit.com/printables/")
        self.assertIsNone(host_redirect_location("www.kidzookit.com", "/health"))

    def test_1less_hosts_keep_same_path_redirects(self):
        for host, path in itertools.product(LESS_HOSTS, PATHS):
            with self.subTest(host=host, path=path):
                self.assertEqual(host_redirect_location(host, path), "https://kidzookit.com" + path)
        self.assertIsNone(host_redirect_location("1less.app", "/health"))


if __name__ == "__main__":
    unittest.main()
