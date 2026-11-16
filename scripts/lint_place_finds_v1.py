"""Place-specific finds linter (v1, 2026-11-16).

A find in the page's hunt list (ol.seo-hunt-list) counts as place-specific when:
- it has a zone and the zone is not "Wonder";
- its label is not a generic hall/activity label (ALWAYS_GENERIC);
- if its label is a reused template name (TEMPLATE_NAMES), the venue item behind it
  carries an http presence_url (the name is then the venue's own, e.g. Perot's Imaginarium).
"""
import re, html, glob, sys, json, os
ALWAYS_GENERIC = re.compile(r"""^(?:
 free\ explore|explore\ on\ your\ own|kids?\ explore|kid\ (?:pick|choice)|
 hands-on(?:\ (?:lab|labs|exhibits?|galleries|play|zone|science))?(?:\ \(optional\))?|hands-on\ /\ discovery|science\ /\ hands-on\ galleries|
 outdoor(?:\ area|\ play)?|water\ play|make(?:\ /\ design)?|pretend\ play|climb|toddler\ zone|quiet\ corner|art\ /\ nature\ create|
 space(?:\ exhibits)?|planetarium|planet\ /\ space\ hall|earth\ /\ planet\ earth|earth\ /\ space\ content|rockets?\ (?:&|and)\ launch|space\ shuttle\ /\ orbiter|
 dinosaurs?|dinosaur\ hall|animal\ /\ mammal\ hall|mammals?(?:\ halls?)?|mammals\ /\ whale\ hall|life\ sciences|live\ animals(?:\ \(verify\))?|
 rainforest(?:\ dome|\ ecosystem)?|aquarium\ zone|marine\ /\ gulf\ zone|forest\ /\ botany\ halls|river\ /\ lake\ fish
)$""", re.I | re.X)
TEMPLATE_NAMES = re.compile(r"^(?:imaginarium|(?:creative\ )?makery|woven\ wonders|toddler\ garden|art\ lab|waterfall\ play|astronaut\ training)$", re.I | re.X)
FROZEN = set("amnh nashville-adventure-science air-and-space national-aquarium-baltimore shedd-aquarium lincoln-park-zoo toronto-zoo austin-zoo national-zoo bronx-zoo redwood joshua-tree museum-of-science-industry-chi california-science-center discovery-place seattle-aquarium aquarium-of-the-pacific st-louis-zoo calgary-zoo fort-worth-zoo san-antonio-zoo dallas-zoo banff sequoia".split())
FLOOR = 5

def finds(t):
    m = re.search(r'<ol class="seo-hunt-list">(.*?)</ol>', t, re.S)
    return [html.unescape(x) for x in re.findall(r"<span>(.*?)</span></li>", m.group(1))] if m else []

def venue_items(root, slug):
    p = f"{root}/data/venues/{slug}.json"
    if not os.path.exists(p): return {}
    m = {}
    for it in json.load(open(p, encoding="utf-8")).get("items", []):
        for k in (it.get("display_label"), it.get("label")):
            if k: m.setdefault(k.strip(), it)
    return m

def specific(t, items=None):
    out = []
    for l in finds(t):
        if " · " not in l: continue
        label, zone = l.split(" — ")[0].strip(), l.rsplit(" · ", 1)[1].strip()
        if zone.lower() == "wonder" or ALWAYS_GENERIC.match(label): continue
        if TEMPLATE_NAMES.match(label):
            it = (items or {}).get(label) or {}
            if not str(it.get("presence_url") or "").startswith("http"): continue
        out.append(label)
    return out

def indexed_place_pages(root):
    for f in sorted(glob.glob(f"{root}/*/index.html")):
        s = f.split("/")[-2]; t = open(f, encoding="utf-8").read()
        if s in FROZEN or 'id="venue-data"' not in t or 'content="noindex' in t: continue
        yield s, t

def counts(root="static/field-pack"):
    return {s: specific(t, venue_items(root, s)) for s, t in indexed_place_pages(root)}

if __name__ == "__main__":
    res = counts(sys.argv[1] if len(sys.argv) > 1 else "static/field-pack")
    bad = {k: v for k, v in res.items() if len(v) < FLOOR}
    print("indexed non-frozen place pages", len(res), "under", FLOOR, ":", len(bad))
    for k, v in sorted(bad.items(), key=lambda x: len(x[1])): print(f"  {k}: {len(v)} {v}")
    json.dump({k: len(v) for k, v in res.items()}, open(sys.argv[2] if len(sys.argv) > 2 else "/tmp/lint_counts.json", "w"), indent=0)
