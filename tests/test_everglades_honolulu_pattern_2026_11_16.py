import json, pathlib, re, unittest
ROOT = pathlib.Path(__file__).resolve().parents[1]
class EvergladesHonoluluPattern20261116(unittest.TestCase):
    def setUp(self):
        self.v = json.loads((ROOT / "static/field-pack/data/venues/everglades.json").read_text())
        self.html = (ROOT / "static/field-pack/everglades/index.html").read_text()
    def test_animal_led_start_here(self):
        self.assertEqual(self.v["route_90m"][:3], ["np_wildlife_watch", "ev_anhinga", "ev_turtle"])
        self.assertIn("Starter list: American alligators on the Anhinga Trail", self.html)
    def test_new_items_sourced_to_nps(self):
        items = {i["id"]: i for i in self.v["items"]}
        for k in ["ev_anhinga", "ev_turtle", "ev_heron", "ev_gallinule"]:
            blob = json.dumps(items[k])
            self.assertIn("nps.gov", blob, k)
    def test_copy_rules(self):
        body = re.sub(r"<script.*?</script>", "", self.html, flags=re.S).lower()
        self.assertNotRegex(body, r"\bno-cost\b")
if __name__ == "__main__":
    unittest.main()
