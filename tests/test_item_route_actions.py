"""Dead Live cam / Photos / Learn more links must not appear on item routes."""

from pathlib import Path
import json
import re
import subprocess
import unittest

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
APP_JS = FP / "js" / "app.js"
CATALOG_JS = FP / "js" / "catalog.js"
STYLES = FP / "css" / "styles.css"
APP_HTML = FP / "app.html"

ACTION_NAMES = ("Live cam", "Photos", "Learn more")

# Node walks every #/venue/:venueId/item/:itemId from catalog data and applies
# the production setExternalAction helper to the same three links the SPA shows.
_AUDIT_JS = r"""
const fs = require("fs");
const vm = require("vm");
const catalogPath = process.argv[1];
const appPath = process.argv[2];
const window = {};
vm.runInNewContext(fs.readFileSync(catalogPath, "utf8"), { window });
const appSrc = fs.readFileSync(appPath, "utf8");
const fnMatch = appSrc.match(/function setExternalAction\(link, url\) \{[\s\S]*?\n  \}\n/);
if (!fnMatch) {
  throw new Error("setExternalAction not found in app.js");
}
const setExternalAction = vm.runInNewContext(fnMatch[0] + "\nsetExternalAction;");
function makeLink(name) {
  const attrs = { href: "#", target: "_blank", rel: "noopener", hidden: false };
  return {
    textContent: name,
    get hidden() { return attrs.hidden; },
    set hidden(v) { attrs.hidden = Boolean(v); },
    get href() { return attrs.href == null ? "" : String(attrs.href); },
    set href(v) { attrs.href = String(v); },
    get target() { return attrs.target || ""; },
    set target(v) { attrs.target = String(v); },
    get rel() { return attrs.rel || ""; },
    set rel(v) { attrs.rel = String(v); },
    removeAttribute(name) {
      if (name === "href") attrs.href = null;
      if (name === "aria-disabled") delete attrs["aria-disabled"];
    },
    setAttribute(name, value) { attrs[name] = String(value); },
    getAttribute(name) {
      if (name === "href") return attrs.href;
      return attrs[name] == null ? null : String(attrs[name]);
    },
    snapshot() { return { ...attrs, text: this.textContent }; },
  };
}
const routes = [];
for (const [venueId, venue] of Object.entries(window.FIELD_PACK_VENUES || {})) {
  for (const itemId of venue.animalIds || []) {
    const item = window.FIELD_PACK_CATALOG[itemId] || null;
    const links = (item && item.links) || {};
    const moreLabel = venue.packTemplate === "exhibits" ? "Museum site" : "Learn more";
    const buttons = [
      ["Live cam", links.cam || ""],
      ["Photos", links.pictures || ""],
      [moreLabel, links.more || ""],
    ].map(([name, url]) => {
      const link = makeLink(name);
      setExternalAction(link, url);
      return { name, url, ...link.snapshot() };
    });
    routes.push({
      route: `#/venue/${venueId}/item/${itemId}`,
      venueId,
      itemId,
      itemFound: Boolean(item),
      actions: buttons,
    });
  }
}
process.stdout.write(JSON.stringify(routes));
"""


def _load_routes():
    proc = subprocess.run(
        ["node", "-e", _AUDIT_JS, str(CATALOG_JS), str(APP_JS)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def _is_dead_visible_href(href: str) -> bool:
    raw = "" if href is None else str(href).strip()
    if not raw or raw == "#":
        return True
    if raw.startswith("#"):
        return True
    lower = raw.lower()
    if "/field-pack/#" in lower:
        return True
    if re.search(r"https?://[^/]*1less\.app/field-pack/?#", lower):
        return True
    if not re.match(r"^https?://", raw):
        return True
    return False


class ItemRouteActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = _load_routes()

    def test_renderer_uses_set_external_action_and_validates_item(self):
        js = APP_JS.read_text(encoding="utf-8")
        self.assertIn("function setExternalAction(link, url)", js)
        self.assertIn("setExternalAction(els.btnCam, camUrl)", js)
        self.assertIn("setExternalAction(els.btnPictures, picUrl)", js)
        self.assertIn("setExternalAction(els.btnMore, moreUrl)", js)
        self.assertIn("!/^https?:\\/\\//.test(url)", js)
        self.assertIn("itemOnVenue", js)
        self.assertIn("venue.items", js)
        html = APP_HTML.read_text(encoding="utf-8")
        self.assertNotIn('id="btn-cam" class="btn btn-ghost" href="#"', html)

    def test_hidden_action_links_are_display_none(self):
        css = STYLES.read_text(encoding="utf-8")
        self.assertIn(".btn[hidden]", css)
        self.assertIn(".detail-links .btn[hidden]", css)
        block = css.split(".btn[hidden]", 1)[1].split("}", 1)[0]
        self.assertIn("display: none", block)

    def test_every_item_route_visible_actions_are_real_http(self):
        self.assertGreater(len(self.routes), 200)
        meadow = next(
            (r for r in self.routes if r["route"] == "#/venue/white-sands/item/np-meadow"),
            None,
        )
        self.assertIsNotNone(meadow, "white-sands / np-meadow must be in the route list")
        self.assertTrue(meadow["itemFound"])

        failures = []
        meadow_visible = []
        for row in self.routes:
            if not row["itemFound"]:
                failures.append(f"{row['route']} — item id missing from catalog")
                continue
            for action in row["actions"]:
                name = action["name"]
                visible = not action["hidden"]
                href = action.get("href")
                if name == "Museum site":
                    check_name = "Learn more"
                else:
                    check_name = name
                if check_name not in ACTION_NAMES and name != "Museum site":
                    continue
                if not visible:
                    if href not in (None, ""):
                        failures.append(
                            f"{row['route']} {name} is hidden but still has href={href!r}"
                        )
                    continue
                if _is_dead_visible_href(href):
                    failures.append(
                        f"{row['route']} visible {name} has dead href={href!r}"
                    )
                if row["route"] == "#/venue/white-sands/item/np-meadow":
                    meadow_visible.append(name)

        self.assertEqual(
            meadow_visible,
            [],
            "White Sands meadow has no cam/photos/learn-more URLs — actions must stay hidden",
        )
        self.assertEqual(failures, [], "\n".join(failures[:40]))

    def test_african_lion_photos_uses_live_natgeo_slug(self):
        """ParentTest: Photos on african-lion must be the working NatGeo Kids page."""
        lion_pictures = (
            "https://kids.nationalgeographic.com/animals/mammals/facts/lion"
        )
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        self.assertIn(f'pictures: "{lion_pictures}"', catalog)
        self.assertNotIn(
            "https://kids.nationalgeographic.com/animals/mammals/facts/african-lion",
            catalog,
        )
        card = (FP / "cards" / "african-lion" / "index.html").read_text(encoding="utf-8")
        self.assertIn(f'href="{lion_pictures}"', card)
        self.assertNotIn("/facts/african-lion", card)

        lion_routes = [r for r in self.routes if r["itemId"] == "african-lion"]
        self.assertGreater(len(lion_routes), 0)
        for row in lion_routes:
            photos = next(a for a in row["actions"] if a["name"] == "Photos")
            self.assertFalse(photos["hidden"], row["route"])
            self.assertEqual(photos["href"], lion_pictures, row["route"])

    def test_catalog_avoids_known_dead_natgeo_slugs(self):
        """Static denylist — no live crawl. Same class as /facts/african-lion 404."""
        dead_slugs = (
            "/animals/mammals/facts/african-lion",
            "/animals/mammals/facts/bengal-tiger",
            "/animals/birds/facts/caribbean-flamingo",
            "/animals/mammals/facts/three-toed-sloth",
            "/animals/fish/facts/southern-stingray",
            "/animals/mammals/facts/plains-zebra",
            "/animals/mammals/facts/red-kangaroo",
            "/animals/mammals/facts/black-rhinoceros",
        )
        hits = []
        for row in self.routes:
            for action in row["actions"]:
                href = str(action.get("href") or "")
                for slug in dead_slugs:
                    if slug in href:
                        hits.append(f"{row['route']} {action['name']} {href}")
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        for slug in dead_slugs:
            if slug in catalog:
                hits.append(f"catalog.js still has {slug}")
        self.assertEqual(hits, [], "\n".join(hits[:20]))


if __name__ == "__main__":
    unittest.main()
