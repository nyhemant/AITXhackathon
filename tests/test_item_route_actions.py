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
        self.assertIn("item.links.picturesLabel", js)
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

    def test_western_lowland_gorilla_photos_is_not_mountain_gorilla(self):
        """ParentTest Layer B: western-lowland Photos must not use mountain-gorilla."""
        gorilla_pictures = (
            "https://www.nationalgeographic.com/animals/mammals/facts/"
            "western-lowland-gorilla"
        )
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        self.assertIn(f'pictures: "{gorilla_pictures}"', catalog)
        self.assertNotIn(
            "https://kids.nationalgeographic.com/animals/mammals/facts/mountain-gorilla",
            catalog,
        )
        card = (FP / "cards" / "western-lowland-gorilla" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn(f'href="{gorilla_pictures}"', card)
        self.assertNotIn("/facts/mountain-gorilla", card)

        gorilla_routes = [r for r in self.routes if r["itemId"] == "western-lowland-gorilla"]
        self.assertGreater(len(gorilla_routes), 0)
        for row in gorilla_routes:
            photos = next(a for a in row["actions"] if a["name"] == "Photos")
            self.assertFalse(photos["hidden"], row["route"])
            self.assertEqual(photos["href"], gorilla_pictures, row["route"])

    def test_asian_small_clawed_otter_photos_uses_live_otter_hub(self):
        """ParentTest Layer B: restore otter Photos; not a 404 or cousin slug."""
        otter_pictures = (
            "https://www.nationalgeographic.com/animals/mammals/facts/otters-1"
        )
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        self.assertIn(f'pictures: "{otter_pictures}"', catalog)
        self.assertNotIn(
            "kids.nationalgeographic.com/animals/mammals/facts/asian-small-clawed-otter",
            catalog,
        )
        card = (FP / "cards" / "asian-small-clawed-otter" / "index.html").read_text(
            encoding="utf-8"
        )
        main = card.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]
        self.assertIn(f'href="{otter_pictures}"', main)
        self.assertIn(">Photos</a>", main)
        self.assertIn(
            "/field-pack/virtual-zoo/?from=card#habitat=asian-small-clawed-otter",
            main,
        )
        self.assertNotIn("/facts/sea-otter", main)
        self.assertNotIn("/facts/river-otter", main)

        otter_routes = [r for r in self.routes if r["itemId"] == "asian-small-clawed-otter"]
        self.assertGreater(len(otter_routes), 0)
        for row in otter_routes:
            photos = next(a for a in row["actions"] if a["name"] == "Photos")
            self.assertFalse(photos["hidden"], row["route"])
            self.assertEqual(photos["href"], otter_pictures, row["route"])

    def test_shark_photos_uses_generic_shark_hub(self):
        """ParentTest Layer B soft: generic shark card must not open great-white."""
        shark_pictures = (
            "https://www.nationalgeographic.com/animals/fish/facts/sharks-1"
        )
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        self.assertIn(f'pictures: "{shark_pictures}"', catalog)
        shark_block = catalog.split("shark: {", 1)[1].split("stingray:", 1)[0]
        self.assertNotIn("/facts/great-white-shark", shark_block)
        card = (FP / "cards" / "shark" / "index.html").read_text(encoding="utf-8")
        main = card.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]
        self.assertIn(f'href="{shark_pictures}"', main)
        self.assertIn(">Photos</a>", main)
        self.assertNotIn("/facts/great-white-shark", main)

        shark_routes = [r for r in self.routes if r["itemId"] == "shark"]
        self.assertGreater(len(shark_routes), 0)
        for row in shark_routes:
            photos = next(a for a in row["actions"] if a["name"] == "Photos")
            self.assertFalse(photos["hidden"], row["route"])
            self.assertEqual(photos["href"], shark_pictures, row["route"])

    def test_weedy_sea_dragon_photos_is_not_leafy_cousin(self):
        """Same cousin-species class: weedy must not open leafy sea dragon."""
        weedy_pictures = (
            "https://www.nationalgeographic.com/animals/fish/facts/weedy-sea-dragon"
        )
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        self.assertIn(f'pictures: "{weedy_pictures}"', catalog)
        self.assertNotIn(
            'pictures: "https://www.nationalgeographic.com/animals/fish/facts/leafy-sea-dragon"',
            catalog,
        )

    def test_whale_shark_photos_uses_live_kids_natgeo_slug(self):
        """ParentTest: whale-shark Photos must not use the 404 singular Kids slug."""
        whale_pictures = (
            "https://kids.nationalgeographic.com/animals/fish/facts/whale-sharks"
        )
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        self.assertIn(f'pictures: "{whale_pictures}"', catalog)
        self.assertNotIn(
            'pictures: "https://kids.nationalgeographic.com/animals/fish/facts/whale-shark"',
            catalog,
        )
        card = (FP / "cards" / "whale-shark" / "index.html").read_text(encoding="utf-8")
        self.assertIn(f'href="{whale_pictures}"', card)
        self.assertNotIn("/facts/whale-shark\"", card)

        whale_routes = [r for r in self.routes if r["itemId"] == "whale-shark"]
        self.assertGreater(len(whale_routes), 0)
        for row in whale_routes:
            photos = next(a for a in row["actions"] if a["name"] == "Photos")
            self.assertFalse(photos["hidden"], row["route"])
            self.assertEqual(photos["href"], whale_pictures, row["route"])

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
            "kids.nationalgeographic.com/animals/fish/facts/manta-ray",
            "kids.nationalgeographic.com/animals/fish/facts/moray-eel",
            "kids.nationalgeographic.com/animals/fish/facts/ocean-sunfish",
            "kids.nationalgeographic.com/animals/fish/facts/leafy-sea-dragon",
            "kids.nationalgeographic.com/animals/birds/facts/african-penguin",
            "kids.nationalgeographic.com/animals/mammals/facts/asian-small-clawed-otter",
            "kids.nationalgeographic.com/animals/invertebrates/facts/crab",
            "kids.nationalgeographic.com/animals/invertebrates/facts/cuttlefish",
            "kids.nationalgeographic.com/animals/mammals/facts/elk",
            "kids.nationalgeographic.com/nature/article/rain-forest",
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

    def test_eel_photos_uses_live_true_eel_page(self):
        """ParentTest Layer B: restore eel Photos; not a 404 or electric-eel cousin."""
        eel_pictures = (
            "https://www.nationalgeographic.com/animals/fish/facts/european-eel"
        )
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        self.assertIn(f'pictures: "{eel_pictures}"', catalog)
        eel_block = catalog.split("eel: {", 1)[1].split("crab:", 1)[0]
        self.assertNotIn("/facts/electric-eel", eel_block)
        self.assertNotIn("/facts/moray-eel", eel_block)
        card = (FP / "cards" / "eel" / "index.html").read_text(encoding="utf-8")
        main = card.split('<main class="card-page">', 1)[1].split("</main>", 1)[0]
        self.assertIn(f'href="{eel_pictures}"', main)
        self.assertIn(">Photos</a>", main)
        self.assertIn(
            "/field-pack/virtual-field-trip/?tab=aquarium&amp;from=card#habitat=eel",
            main,
        )
        self.assertNotIn("/facts/electric-eel", main)
        self.assertNotIn("/facts/moray-eel", main)

        eel_routes = [r for r in self.routes if r["itemId"] == "eel"]
        self.assertGreater(len(eel_routes), 0)
        for row in eel_routes:
            photos = next(a for a in row["actions"] if a["name"] == "Photos")
            self.assertFalse(photos["hidden"], row["route"])
            self.assertEqual(photos["href"], eel_pictures, row["route"])

    def test_remaining_layer_a_photos_use_live_or_hide(self):
        """Layer A leftovers: penguin/crab/cuttlefish/elk stay on their live slugs."""
        catalog = CATALOG_JS.read_text(encoding="utf-8")
        penguin = "https://kids.nationalgeographic.com/animals/birds/topic/penguin-facts"
        crab = (
            "https://kids.nationalgeographic.com/animals/invertebrates/facts/"
            "christmas-island-red-crab"
        )
        cuttle = "https://www.nationalgeographic.com/animals/invertebrates/facts/cuttlefish"
        elk = "https://www.nationalgeographic.com/animals/mammals/facts/elk"
        self.assertIn(f'pictures: "{penguin}"', catalog)
        self.assertIn(f'pictures: "{crab}"', catalog)
        self.assertIn('picturesLabel: "Christmas Island photos"', catalog)
        self.assertIn(f'pictures: "{cuttle}"', catalog)
        self.assertIn(f'pictures: "{elk}"', catalog)

        penguin_card = (FP / "cards" / "african-penguin" / "index.html").read_text(
            encoding="utf-8"
        )
        crab_card = (FP / "cards" / "crab" / "index.html").read_text(encoding="utf-8")
        cuttle_card = (FP / "cards" / "cuttlefish" / "index.html").read_text(
            encoding="utf-8"
        )
        self.assertIn(f'href="{penguin}"', penguin_card)
        self.assertIn(f'href="{crab}"', crab_card)
        crab_main = crab_card.split('<main class="card-page">', 1)[1].split(
            "</main>", 1
        )[0]
        self.assertIn(">Christmas Island photos</a>", crab_main)
        self.assertNotIn(">Photos</a>", crab_main)
        self.assertIn(f'href="{cuttle}"', cuttle_card)

        expect = {
            "african-penguin": penguin,
            "crab": crab,
            "cuttlefish": cuttle,
            "elk": elk,
        }
        for item_id, url in expect.items():
            routes = [r for r in self.routes if r["itemId"] == item_id]
            self.assertGreater(len(routes), 0, item_id)
            for row in routes:
                photos = next(a for a in row["actions"] if a["name"] == "Photos")
                self.assertFalse(photos["hidden"], row["route"])
                self.assertEqual(photos["href"], url, row["route"])


if __name__ == "__main__":
    unittest.main()
