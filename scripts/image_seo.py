#!/usr/bin/env python3
"""Image discovery (2026-10-23). Idempotent post-process:
  1. Card hero alt text: short factual description of what each photo shows
     (checked by eye on 2026-10-23; illustrations are called illustrations).
     The plain card name moves to data-card-name (scripts/add_link_mesh.py reads it).
  2. Park hero alt "X National Park park day" -> "X National Park".
  3. <image:image> entries in static/sitemap.xml for the 58 card hero photos and the
     place-specific park hero photos (np-hero-<slug>), never the generic stock
     (np-visitor-center / np-scenic-overlook / np-trailhead-sign). URL list and order are
     unchanged; /field-pack/sitemap.xml is written byte-identical.
Re-run after ANY generate_bdo_seo.py run (it rewrites the sitemap and pages), then
scripts/sitemap_lastmod_from_git.py:   python3 scripts/image_seo.py
tests/test_image_seo.py fails if the image entries or alts disappear."""
import html as H
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
SITEMAPS = [REPO / "static" / "sitemap.xml", FP / "sitemap.xml"]
BASE = "https://kidzookit.com"
GENERIC = ("np-visitor-center", "np-scenic-overlook", "np-trailhead-sign")

CARD_ALTS = {
    "african-elephant": "African elephant with tusks standing on grass",
    "african-lion": "Male African lion with a big mane in tall grass",
    "african-penguin": "African penguin standing by the water",
    "american-alligator": "American alligator resting in a marsh",
    "american-bison": "American bison with curved horns in a grassy field",
    "asian-small-clawed-otter": "Asian small-clawed otter on rocks by the water",
    "caribbean-flamingo": "Pink Caribbean flamingo standing in water",
    "cheetah": "Close-up of a spotted cheetah",
    "chimpanzee": "Chimpanzee sitting in a green forest",
    "clownfish": "Orange and white clownfish by a sea anemone",
    "cm-art-lab": "Illustration of children painting at an easel",
    "cm-free-explore": "Illustration of a child exploring a colorful museum room",
    "cm-imaginarium": "Illustration of a toddler reaching for a glowing ball",
    "cm-makery": "Illustration of hands building with wood and craft pieces",
    "cm-outdoor": "Illustration of families at an outdoor play area",
    "cm-toddler-garden": "Illustration of a toddler planting in a garden",
    "cm-woven": "Illustration of children climbing a woven rope structure",
    "crab": "Crab on wet rocks",
    "cuttlefish": "Cuttlefish on the sea floor",
    "cuyahoga-towpath": "Flat wetland marsh under a cloudy sky",
    "eel": "Spotted moray eel peeking out from rocks",
    "elk": "Bull elk with large antlers in a mountain meadow",
    "freshwater-fish": "Spotted trout swimming over river stones",
    "galapagos-tortoise": "Giant Galápagos tortoise walking on dirt",
    "giant-panda": "Giant panda sitting among bamboo",
    "jellyfish": "Orange jellyfish drifting in blue water",
    "kelp-forest": "Sunlight shining through an underwater kelp forest",
    "koala": "Koala holding onto a tree branch",
    "manta-ray": "Manta ray gliding through deep blue water",
    "nile-hippo": "Hippo standing in shallow water",
    "octopus": "Octopus resting on the sea floor",
    "orangutan": "Orangutan with orange fur in a forest",
    "ostrich": "Ostrich head and long neck above a grassy field",
    "polar-bear": "Polar bear on snow and ice",
    "puffin": "Puffin with an orange beak standing on a mossy rock",
    "red-panda": "Red panda in a forest",
    "reticulated-giraffe": "Reticulated giraffe showing its patterned coat",
    "ring-tailed-lemur": "Ring-tailed lemur with a striped tail on a branch",
    "sci-aquarium-zone": "Illustration of a sea turtle swimming over a reef",
    "sci-astronaut": "Illustration of an astronaut helmet and gloves",
    "sci-dinosaur": "Illustration of a dinosaur skeleton in a museum hall",
    "sci-hands-on": "Illustration of hands playing with gears on a table",
    "sci-mammal-hall": "Illustration of a child pointing at an elephant display in a museum",
    "sci-planet": "Illustration of a family looking at a planetarium dome under the stars",
    "sci-rainforest": "Illustration of a macaw in a rainforest exhibit",
    "sci-rocket": "Illustration of a family looking at tall rockets",
    "sea-otter": "Sea otter floating on its back in the water",
    "sea-turtle": "Sea turtle swimming over sea grass",
    "seahorse": "Seahorse holding onto seaweed with its tail",
    "shark": "Shark swimming near the water surface",
    "starfish": "Orange sea star on pebbles",
    "stingray": "Stingray resting on a sandy sea floor",
    "sumatran-tiger": "Striped tiger looking at the camera",
    "two-toed-sloth": "Sloth hanging among green leaves",
    "warthog": "Warthog with curved tusks on red dirt",
    "western-lowland-gorilla": "Gorilla sitting among green leaves",
    "whale-shark": "Whale shark swimming in dark blue water",
    "zebra": "Zebra with black and white stripes in tall grass",
}


def fix_card(cid):
    p = FP / "cards" / cid / "index.html"
    s = p.read_text(encoding="utf-8")
    m = re.search(r'<img class="card-page-photo" src="([^"]+)"( data-card-name="[^"]*")? alt="([^"]*)"', s)
    assert m, cid
    name = H.unescape(m.group(2)[len(' data-card-name="'):-1]) if m.group(2) else H.unescape(m.group(3))
    new = f'<img class="card-page-photo" src="{m.group(1)}" data-card-name="{H.escape(name, quote=True)}" alt="{H.escape(CARD_ALTS[cid], quote=True)}"'
    if m.group(0) != new:
        s = s.replace(m.group(0), new, 1)
        p.write_text(s, encoding="utf-8")
    return m.group(1)


def fix_park(p):
    s = p.read_text(encoding="utf-8")
    t = re.sub(r'alt="([^"]*[Pp]ark) park day"', r'alt="\1"', s)
    if t != s:
        p.write_text(t, encoding="utf-8")
    m = re.search(r'<img src="((?:/field-pack/)?photos/np-hero-([a-z0-9-]+)\.jpg[^"]*)"[^>]*loading="eager"', t)
    if m and m.group(2) == p.parent.name and not any(g in m.group(1) for g in GENERIC):
        src = m.group(1)
        return src if src.startswith("/") else "/field-pack/" + src
    return None


def main():
    images = {}
    for cid in CARD_ALTS:
        images[f"{BASE}/field-pack/cards/{cid}/"] = BASE + fix_card(cid)
    for p in sorted(FP.glob("*/index.html")):
        if p.parent.name == "cards":
            continue
        src = fix_park(p)
        if src:
            images[f"{BASE}/field-pack/{p.parent.name}/"] = BASE + src
    sm = SITEMAPS[0].read_text(encoding="utf-8")
    sm = re.sub(r"\n\s*<image:image>.*?</image:image>", "", sm, flags=re.S)
    if "xmlns:image=" not in sm:
        sm = sm.replace('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">', 1)

    def add(m):
        img = images.get(m.group(2))
        if not img:
            return m.group(0)
        return m.group(0).replace("</url>", f"  <image:image>\n      <image:loc>{H.escape(img)}</image:loc>\n    </image:image>\n  </url>")
    sm = re.sub(r"(<url>\s*<loc>)([^<]+)(</loc>.*?</url>)", add, sm, flags=re.S)
    for f in SITEMAPS:
        if f.read_text(encoding="utf-8") != sm:
            f.write_text(sm, encoding="utf-8")
    print("image entries:", sm.count("<image:image>"), "urls:", len(re.findall(r"<loc>", sm)))


if __name__ == "__main__":
    main()
