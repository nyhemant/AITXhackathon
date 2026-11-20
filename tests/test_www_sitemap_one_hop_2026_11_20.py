"""Polish 2026-11-20: www.kidzookit.com/field-pack/sitemap.xml reaches /sitemap.xml in one 301; 1less.app unchanged."""

from __future__ import annotations

import itertools
import unittest

from busyparent_agent.site import host_redirect_location, https_upgrade_location

try:
    from test_public_host_redirect import _get, _head
except ImportError:  # run as tests.<module>
    from tests.test_public_host_redirect import _get, _head

OLD = "/field-pack/sitemap.xml"
LESS_HOSTS = ("1less.app", "www.1less.app", "1less.app:443", "WWW.1LESS.APP")


class WwwSitemapOneHop(unittest.TestCase):
    def test_www_goes_straight_to_the_sitemap(self):
        for host in ("www.kidzookit.com", "www.kidzookit.com:443"):
            for path in (OLD, OLD + "?x=1"):
                with self.subTest(host=host, path=path):
                    self.assertEqual(host_redirect_location(host, path), "https://kidzookit.com/sitemap.xml")
                    for fn in (_get, _head):
                        h = fn(path, host)
                        self.assertEqual(h._code, 301)
                        self.assertEqual(h._headers.get("Location"), "https://kidzookit.com/sitemap.xml")

    def test_http_apex_goes_straight_to_the_sitemap(self):
        class H(dict):
            pass

        headers = H({"X-Forwarded-Proto": "http"})
        self.assertEqual(https_upgrade_location("kidzookit.com", OLD, headers), "https://kidzookit.com/sitemap.xml")

    def test_apex_https_still_301s_to_the_sitemap(self):
        h = _get(OLD, "kidzookit.com")
        self.assertEqual(h._code, 301)
        self.assertEqual(h._headers.get("Location"), "/sitemap.xml")

    def test_1less_hosts_keep_the_old_two_step_behavior(self):
        for host, path in itertools.product(LESS_HOSTS, (OLD, "/", "/sitemap.xml", "/field-pack/dallas-zoo/")):
            with self.subTest(host=host, path=path):
                self.assertEqual(host_redirect_location(host, path), "https://kidzookit.com" + path)


if __name__ == "__main__":
    unittest.main()
