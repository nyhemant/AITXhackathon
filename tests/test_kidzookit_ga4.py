"""KidZooKit GA4 property: live ID + Dinner exclusion."""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from busyparent_agent.web import (
    ANALYTICS_COOKIE,
    ANALYTICS_OFF_VALUE,
    CLOUDFLARE_BEACON_SCRIPT_HOST,
    GA4_MEASUREMENT_ID,
    HTML,
    SECURITY_HEADERS,
    _html_for_request,
    _security_headers_for,
)

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

    def test_ga4_config_turns_off_google_signals_and_ad_personalization(self):
        shell_js = SHELL_JS.read_text(encoding="utf-8")
        self.assertIn("allow_google_signals: false", shell_js)
        self.assertIn("allow_ad_personalization_signals: false", shell_js)
        self.assertNotIn("allow_google_signals: true", shell_js)
        self.assertNotIn("allow_ad_personalization_signals: true", shell_js)

    def test_site_analytics_never_sets_user_ids_or_user_properties(self):
        for rel in (
            "static/shell/shell.js",
            "static/shell/qr-welcome.js",
            "static/shell/related-links.js",
            "static/field-pack/js/fp-analytics.js",
            "static/start/start.js",
        ):
            text = (REPO / rel).read_text(encoding="utf-8")
            for banned in ("user_id", "user_properties", "setUserId", "setUserProperties"):
                self.assertNotIn(banned, text, f"{rel} must not use {banned}")


def _directives(csp: str) -> dict[str, list[str]]:
    out = {}
    for part in csp.split(";"):
        bits = part.split()
        if bits:
            out[bits[0]] = bits[1:]
    return out


class CloudflareBeaconCspTest(unittest.TestCase):
    """Cloudflare Web Analytics beacon: exactly one script host, nothing else loosened."""

    def test_script_src_allows_only_the_exact_beacon_host(self):
        self.assertEqual(CLOUDFLARE_BEACON_SCRIPT_HOST, "https://static.cloudflareinsights.com")
        d = _directives(SECURITY_HEADERS["Content-Security-Policy"])
        self.assertIn(CLOUDFLARE_BEACON_SCRIPT_HOST, d["script-src"])

    def test_no_cloudflare_wildcard_and_no_connect_src_host(self):
        # The beacon posts to /cdn-cgi/rum on our own origin, which connect-src 'self' covers.
        d = _directives(SECURITY_HEADERS["Content-Security-Policy"])
        for name, values in d.items():
            for v in values:
                if "cloudflare" in v:
                    self.assertEqual((name, v), ("script-src", CLOUDFLARE_BEACON_SCRIPT_HOST))
                    self.assertNotIn("*", v)
        self.assertIn("'self'", d["connect-src"])
        self.assertNotIn("cloudflareinsights", " ".join(d["connect-src"]))

    def test_other_directives_unchanged_by_the_beacon(self):
        d = _directives(SECURITY_HEADERS["Content-Security-Policy"])
        self.assertEqual(d["default-src"], ["'self'"])
        self.assertEqual(d["object-src"], ["'none'"])
        self.assertEqual(d["frame-ancestors"], ["'none'"])
        self.assertEqual(d["form-action"], ["'self'"])
        self.assertEqual(d["img-src"], ["'self'", "data:", "https:"])
        self.assertEqual(d["style-src"], ["'self'", "'unsafe-inline'"])
        self.assertEqual(d["font-src"], ["'self'"])

    def test_opted_out_visitors_do_not_get_the_beacon_host(self):
        off = f"a=b; {ANALYTICS_COOKIE}={ANALYTICS_OFF_VALUE}"
        opted_out = _security_headers_for(off)["Content-Security-Policy"]
        self.assertNotIn("cloudflareinsights", opted_out)
        self.assertIn("https://www.googletagmanager.com", opted_out)
        default = _directives(SECURITY_HEADERS["Content-Security-Policy"])
        out = _directives(opted_out)
        default["script-src"].remove(CLOUDFLARE_BEACON_SCRIPT_HOST)
        self.assertEqual(out, default)
        self.assertIs(_security_headers_for(None), SECURITY_HEADERS)
        self.assertIs(_security_headers_for("a=b"), SECURITY_HEADERS)


if __name__ == "__main__":
    unittest.main()
