"""Hub links in the shared menu (2026-10-23, scripts/shell_menu_hubs.py).
If this fails after a generator run: python3 scripts/shell_menu_hubs.py"""
import re
import unittest
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "static"
HUBS = ["/field-pack/zoos/", "/field-pack/aquariums/", "/field-pack/museums/", "/field-pack/national-parks/"]


class ShellMenuHubsTest(unittest.TestCase):
    def test_every_shell_menu_has_hub_links_under_places(self):
        n = 0
        for p in STATIC.rglob("*.html"):
            s = p.read_text(encoding="utf-8")
            if 'id="shell-menu"' not in s:
                continue
            n += 1
            menu = re.search(r'id="shell-menu"[\s\S]*?About</a>', s).group(0)
            hrefs = re.findall(r'href="([^"]+)"', menu)
            i = hrefs.index("/field-pack/")
            self.assertEqual(hrefs[i + 1:i + 5], HUBS, p)
            self.assertEqual(menu.count('data-related-link="menu_hub"'), 4, p)
            self.assertIn("/shell/shell.css?v=13", s, p)
        self.assertGreaterEqual(n, 280)

    def test_hub_targets_exist_and_css_present(self):
        for h in HUBS:
            self.assertTrue((STATIC / h.strip("/") / "index.html").exists(), h)
        self.assertIn("a.shell-menu-sub", (STATIC / "shell" / "shell.css").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
