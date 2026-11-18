"""2026-11-18: caveats dropped by #460's taglines are back in the visible lead (KZK, kidzookit.com)."""
import json, pathlib, sys, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
FP = ROOT / "static/field-pack"
sys.path.insert(0, str(ROOT / "scripts"))
WANT = {
    "calgary-zoo": "Starter list: western lowland gorillas, then hippos and red pandas — Humboldt penguins, not African",
    "toronto-zoo": "Starter list: western lowland gorillas, then African penguins and American flamingos — Amur tigers, not Sumatran",
    "joshua-tree": "Starter list: desert spiny lizards on the rocks, then roadrunners and Gambel's quail — sightings aren't promised",
}
class Caveats20261118(unittest.TestCase):
    def test_lead_shows_caveat(self):
        for s, lead in WANT.items():
            self.assertIn(f'<p class="lead">{lead}</p>', (FP / f"{s}/index.html").read_text(), s)
    def test_generator_keeps_caveat(self):
        import generate_bdo_seo as g
        for s, lead in WANT.items():
            v = json.loads((FP / f"data/venues/{s}.json").read_text())
            self.assertEqual(g.quiet_hero_lead({}, v), lead, s)
    def test_caveat_facts_already_on_page(self):
        self.assertIn("Humboldt, gentoo, rockhopper, and king — not African", (FP / "calgary-zoo/index.html").read_text())
        self.assertIn("Official Eurasia Wilds tiger is Amur tiger", (FP / "toronto-zoo/index.html").read_text())
if __name__ == "__main__":
    unittest.main()
