"""KidZooKit GA4 property: live ID + Dinner exclusion."""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from busyparent_agent.web import GA4_MEASUREMENT_ID, HTML, _html_for_request

REPO = Path(__file__).resolve().parents[1]
SHELL_JS = REPO / "static" / "shell" / "shell.js"
OLD_1LESS_ID = "G-X6V6PNY9ZV"
KIDZOOKIT_ID = "G-XB8HKLF4XY"

NODE_HARNESS = r"""
const fs = require("fs");
const vm = require("vm");
const code = fs.readFileSync(process.argv[1], "utf8");
const pathname = process.argv[2];
const scripts = [];
const created = [];
const document = {
  querySelectorAll: () => [],
  querySelector: (sel) => {
    if (String(sel).includes("googletagmanager.com/gtag/js")) {
      return scripts.length ? { src: scripts[0] } : null;
    }
    return null;
  },
  createElement: (tag) => {
    const el = { tagName: String(tag).toUpperCase(), async: false, src: "" };
    created.push(el);
    return el;
  },
  head: { appendChild: (el) => { if (el && el.src) scripts.push(el.src); } },
  addEventListener: () => {},
  cookie: "",
};
const location = {
  hostname: "kidzookit.com",
  pathname,
  search: "",
  hash: "",
  href: "https://kidzookit.com" + pathname,
  protocol: "https:",
};
const windowObj = {
  document,
  location,
  dataLayer: undefined,
  addEventListener: () => {},
};
windowObj.window = windowObj;
const localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
const history = { pushState: function () {}, replaceState: function () {} };
const context = {
  window: windowObj,
  document,
  location,
  localStorage,
  history,
  console,
  URLSearchParams,
  encodeURIComponent,
  Date,
};
vm.runInNewContext(code, context);
console.log(JSON.stringify({
  scripts,
  ready: !!windowObj.__1LESS_GA4_READY__,
  measurementId: windowObj.OneLessAnalytics && windowObj.OneLessAnalytics.measurementId,
  dinner: windowObj.OneLessAnalytics && windowObj.OneLessAnalytics.isDinnerPath(),
  disabled: windowObj.OneLessAnalytics && windowObj.OneLessAnalytics.isDisabled(),
}));
"""


def _live_id_assignments(text: str, measurement_id: str) -> list[str]:
    return [
        line
        for line in text.splitlines()
        if measurement_id in line and not line.lstrip().startswith(("#", "//"))
    ]


class KidZooKitGa4Test(unittest.TestCase):
    def test_live_measurement_id_is_kidzookit_property(self):
        shell_js = SHELL_JS.read_text(encoding="utf-8")
        web_py = (REPO / "src" / "busyparent_agent" / "web.py").read_text(encoding="utf-8")

        self.assertEqual(GA4_MEASUREMENT_ID, KIDZOOKIT_ID)
        self.assertIn(f'GA4_MEASUREMENT_ID = "{KIDZOOKIT_ID}"', shell_js)
        self.assertIn(f'GA4_MEASUREMENT_ID = "{KIDZOOKIT_ID}"', web_py)
        self.assertTrue(_live_id_assignments(shell_js, KIDZOOKIT_ID))
        self.assertTrue(_live_id_assignments(web_py, KIDZOOKIT_ID))

        # Historical 1Less ID stays in comments / docs only — never as the live tag.
        self.assertIn(OLD_1LESS_ID, shell_js)
        self.assertIn(OLD_1LESS_ID, web_py)
        self.assertEqual(_live_id_assignments(shell_js, OLD_1LESS_ID), [])
        self.assertEqual(_live_id_assignments(web_py, OLD_1LESS_ID), [])

    def test_dinner_html_loads_shell_but_does_not_embed_gtag(self):
        html = _html_for_request(None)
        self.assertIn("/shell/shell.js?v=6", html)
        self.assertIn("/shell/shell.js?v=6", HTML)
        self.assertNotIn("googletagmanager.com/gtag/js", html)
        self.assertNotIn(KIDZOOKIT_ID, html)
        self.assertNotIn(OLD_1LESS_ID, html)

    def test_tracked_pages_pin_bumped_shell_cache(self):
        for rel in (
            "static/start/index.html",
            "static/about/index.html",
            "static/field-pack/index.html",
            "static/field-pack/app.html",
        ):
            text = (REPO / rel).read_text(encoding="utf-8")
            self.assertIn("/shell/shell.js?v=6", text, rel)
            self.assertNotIn("/shell/shell.js?v=4", text, rel)
            self.assertNotIn("/shell/shell.js?v=5", text, rel)

    @unittest.skipUnless(shutil.which("node"), "node required to simulate gtag init")
    def test_shell_skips_gtag_on_dinner_and_loads_on_zoo_paths(self):
        cases = {
            "/dinner": {"ready": False, "scripts": [], "dinner": True, "disabled": True},
            "/dinner/": {"ready": False, "scripts": [], "dinner": True, "disabled": True},
            "/field-pack/": {"ready": True, "dinner": False, "disabled": False},
            "/start/": {"ready": True, "dinner": False, "disabled": False},
            "/about/": {"ready": True, "dinner": False, "disabled": False},
        }
        for path, expect in cases.items():
            result = subprocess.run(
                ["node", "-e", NODE_HARNESS, str(SHELL_JS), path],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["dinner"], expect["dinner"], path)
            self.assertEqual(payload["disabled"], expect["disabled"], path)
            self.assertEqual(payload["ready"], expect["ready"], path)
            self.assertEqual(payload["measurementId"], KIDZOOKIT_ID, path)
            if expect["ready"]:
                self.assertTrue(
                    any(KIDZOOKIT_ID in src for src in payload["scripts"]),
                    f"{path} should load KidZooKit gtag, got {payload['scripts']}",
                )
                self.assertFalse(any(OLD_1LESS_ID in src for src in payload["scripts"]), path)
            else:
                self.assertEqual(payload["scripts"], [])


if __name__ == "__main__":
    unittest.main()
