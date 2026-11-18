"""2026-11-18: no indexed KZK (kidzookit.com) page links to the 7 noindex places; the places stay live."""
import pathlib, re, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
S = ROOT / "static"
NOI = ["ecoparque-ba", "stockholm-skansen", "cairo-zoo", "beijing-zoo",
       "nairobi-safari-walk", "bogota-zoo", "lotte-aquarium-seoul"]
ALT = "|".join(NOI)
# Any attribute or JSON-LD URL that lands on a noindex place page (absolute, root-relative or base-relative).
PLACE_LINK = re.compile(r'(?:href|content|src)="(?:https://kidzookit\.com)?(?:/field-pack/)?(?:' + ALT + r')/?(?:[?#][^"]*)?"|kidzookit\.com/field-pack/(?:' + ALT + r')/')
CARD_QUERY = re.compile(r'href="[^"]*/cards/[a-z0-9-]+/\?from=(?:' + ALT + r')')
class NoindexLinks20261118(unittest.TestCase):
    def indexed_pages(self):
        for p in S.rglob("*.html"):
            rel = p.relative_to(S).as_posix()
            if any(rel.startswith(f"field-pack/{n}/") for n in NOI):
                continue
            t = p.read_text(encoding="utf-8", errors="ignore")
            if re.search(r'<meta name="robots" content="noindex', t):
                continue
            yield rel, t
    def test_no_indexed_page_links_to_a_noindex_place(self):
        bad = [(rel, m.group(0)) for rel, t in self.indexed_pages() for m in [PLACE_LINK.search(t) or CARD_QUERY.search(t)] if m]
        self.assertEqual(bad, [])
    def test_noindex_places_stay_live_and_unlisted(self):
        pd = (S / "field-pack/js/places-data.js").read_text()
        for n in NOI:
            self.assertTrue((S / f"field-pack/{n}/index.html").is_file(), n)
            self.assertRegex(pd, r'id: "' + n + r'",\s*\n\s*listed: false', n)
        sys.path.insert(0, str(ROOT / "scripts"))
        import generate_bdo_seo as g
        self.assertEqual(set(NOI), set(g.NOINDEX_PLACE_SLUGS))
if __name__ == "__main__":
    unittest.main()
