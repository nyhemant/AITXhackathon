"""2026-11-17: public contact address is ask@kidzookit.com everywhere but the 10 still-clean scav pages."""
import re, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
NEW, OLD = "ask@kidzookit.com", "kidzookit@agentmail.to"
SKIP = {"bronx-zoo", "austin-zoo", "national-zoo", "lincoln-park-zoo", "shedd-aquarium",
        "seattle-aquarium", "st-louis-zoo", "fort-worth-zoo", "san-antonio-zoo", "dallas-zoo"}
STATIC = ROOT / "static"
def skipped(p):
    r = p.relative_to(STATIC).parts
    return len(r) == 3 and r[0] == "field-pack" and r[1] in SKIP
class ContactAsk20261117(unittest.TestCase):
    def test_no_stale_address_outside_skipped_pages(self):
        bad = []
        for p in list(STATIC.rglob("*.html")) + list(STATIC.rglob("*.js")) + list(STATIC.rglob("*.txt")):
            if not skipped(p) and OLD in p.read_text(encoding="utf-8", errors="ignore"):
                bad.append(str(p.relative_to(ROOT)))
        self.assertEqual(bad, [])
    def test_key_pages_use_ask(self):
        for rel in ["privacy/index.html", "about/index.html", "start/index.html", "field-pack/index.html", "field-pack/cairo-zoo/index.html", "field-pack/amnh/index.html"]:
            t = (STATIC / rel).read_text()
            self.assertIn(f'<!--email_off--><a href="mailto:{NEW}"', t, rel)
        self.assertIn(NEW, (STATIC / "field-pack/js/print-kit.js").read_text())
    def test_every_mailto_is_inside_email_off(self):
        for p in STATIC.rglob("*.html"):
            if skipped(p):
                continue
            t = p.read_text(encoding="utf-8")
            for m in re.finditer(r'<a href="mailto:', t):
                self.assertEqual(t[max(0, m.start() - 16):m.start()], "<!--email_off-->", str(p.relative_to(ROOT)))
    def test_skipped_pages_untouched_and_generator_guard(self):
        import generate_bdo_seo as gen
        import field_pack_kit_tier as kt
        self.assertEqual(gen.CONTACT_MAIL, NEW); self.assertEqual(kt.FRESHNESS_MAIL, NEW)
        for s in SKIP:
            self.assertIn(OLD, (STATIC / "field-pack" / s / "index.html").read_text())
            self.assertEqual(gen.apply_contact_guard(s, f"mailto:{NEW}"), f"mailto:{OLD}")
        self.assertEqual(gen.apply_contact_guard("amnh", f"mailto:{NEW}"), f"mailto:{NEW}")
if __name__ == "__main__":
    unittest.main()
