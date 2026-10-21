"""Internal link mesh (2026-10-21): place "Explore more", card "Where to see", breadcrumbs."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
FIELD = STATIC / "field-pack"


def _place_pages():
    for f in sorted(FIELD.glob("*/index.html")):
        s = f.read_text(encoding="utf-8")
        if 'id="venue-data"' in s:
            yield f, s


def _block(s, name):
    return re.findall(rf"<!-- kz-mesh:{name} -->(.*?)<!-- /kz-mesh:{name} -->", s, re.S)


def _exists(href):
    path = href.split("#")[0].split("?")[0]
    target = STATIC / path.lstrip("/")
    return (target / "index.html").exists() if path.endswith("/") else target.exists()


class LinkMeshTests(unittest.TestCase):
    def test_place_pages_have_in_body_explore_block(self):
        sets = {}
        for f, s in _place_pages():
            blocks = _block(s, "explore")
            self.assertEqual(len(blocks), 1, f)
            b = blocks[0]
            self.assertLess(s.index("kz-mesh:explore"), s.index('class="site-footer'), f)
            places = re.findall(r'href="(/field-pack/[a-z0-9-]+/)" data-related-link="place"', b)
            cards = re.findall(r'href="(/field-pack/cards/[a-z0-9-]+/)" data-related-link="card"', b)
            prints = re.findall(r'href="(/printables/[a-z0-9-/]*)" data-related-link="printable"', b)
            self.assertTrue(4 <= len(places) <= 6, (f, places))
            self.assertLessEqual(len(cards), 4, f)
            self.assertEqual(len(prints), 1, f)
            own = "/field-pack/" + f.parent.name + "/"
            hrefs = re.findall(r'href="([^"]+)"', b)
            self.assertNotIn(own, hrefs, f)
            self.assertEqual(len(hrefs), len(set(hrefs)), f)
            for h in hrefs:
                self.assertTrue(_exists(h), (f, h))
            for c in cards:  # only animals the page already features elsewhere
                rest = s.replace(b, "")
                self.assertIn('href="' + c, rest, (f, c))
            self.assertNotIn(">Related<", b)
            sets.setdefault(frozenset(hrefs), []).append(f.parent.name)
        dupes = [v for v in sets.values() if len(v) > 1]
        self.assertEqual(dupes, [])

    def test_place_breadcrumbs_visible_and_structured(self):
        for f, s in _place_pages():
            nav = re.search(r'<nav class="seo-crumbs no-print" aria-label="Breadcrumb">(.*?)</nav>', s, re.S).group(1)
            self.assertIn('href="/start/"', nav, f)
            self.assertIn('<a href="/field-pack/">All places</a>', nav, f)
            self.assertIn('aria-current="page"', nav, f)
            ld = _block(s, "crumb-ld")
            self.assertEqual(len(ld), 1, f)
            data = json.loads(re.search(r">(\{.*\})</script>", ld[0]).group(1))
            self.assertEqual(data["@type"], "BreadcrumbList")
            self.assertEqual(data["itemListElement"][-1]["item"], f"https://kidzookit.com/field-pack/{f.parent.name}/")

    def test_card_pages_link_places_capped_with_see_all(self):
        for f in sorted((FIELD / "cards").glob("*/index.html")):
            s = f.read_text(encoding="utf-8")
            self.assertEqual(len(_block(s, "crumb-ld")), 1, f)
            self.assertIn('aria-current="page"', s.split('class="card-page-crumbs"')[1].split("</p>")[0], f)
            where = _block(s, "where")
            main = s[: s.rfind("</main>")]
            related = set(re.findall(r'href="/field-pack/cards/([a-z0-9-]+)/"', main)) - {f.parent.name}
            self.assertGreaterEqual(len(related), 3, f)
            if not where:
                continue
            places = re.findall(r'data-related-link="place"', where[0])
            self.assertTrue(1 <= len(places) <= 8, f)
            self.assertIn('data-related-link="see_all"', where[0], f)
            for h in re.findall(r'href="([^"]+)"', where[0]):
                self.assertTrue(_exists(h), (f, h))

    def test_tracking_script_and_css_present(self):
        js = (STATIC / "shell" / "related-links.js").read_text(encoding="utf-8")
        self.assertIn("related_link_click", js)
        self.assertIn("window.trackEvent", js)
        self.assertNotIn("href", js.split("trackEvent(")[1].split(")")[0])
        for f, s in _place_pages():
            self.assertIn("/shell/related-links.js?v=1", s, f)
            self.assertIn("/field-pack/css/link-mesh.css?v=1", s, f)
        start = (STATIC / "start" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(len(_block(start, "start-trips")), 1)
        self.assertIn("/shell/related-links.js?v=1", start)


if __name__ == "__main__":
    unittest.main()
