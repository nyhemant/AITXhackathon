"""301s on /, /zoo and legacy /field-pack/places/ keep the query (QR utm tags)."""

import unittest

from tests.test_start_landing import _get, _head


class RedirectKeepsQueryTests(unittest.TestCase):
    CASES = {
        "/?utm_source=qr&utm_medium=print": "/start/?utm_source=qr&utm_medium=print",
        "/index.html?utm_source=qr": "/start/?utm_source=qr",
        "/zoo?utm_source=qr": "/start/?utm_source=qr",
        "/zoo/?utm_campaign=flyer": "/start/?utm_campaign=flyer",
        "/field-pack/places/dallas-zoo.html?utm_source=qr": "/field-pack/dallas-zoo/?utm_source=qr",
        "/field-pack/places/dallas-zoo?utm_source=qr": "/field-pack/dallas-zoo/?utm_source=qr",
    }

    def test_get_and_head_keep_query(self):
        for fn in (_get, _head):
            for src, dest in self.CASES.items():
                with self.subTest(fn=fn.__name__, src=src):
                    h = fn(src)
                    self.assertEqual(h._code, 301)
                    self.assertEqual(h._headers.get("Location"), dest)

    def test_no_query_unchanged(self):
        for src, dest in {"/": "/start/", "/zoo": "/start/", "/field-pack/places/dallas-zoo.html": "/field-pack/dallas-zoo/"}.items():
            with self.subTest(src=src):
                h = _get(src)
                self.assertEqual((h._code, h._headers.get("Location")), (301, dest))


if __name__ == "__main__":
    unittest.main()
