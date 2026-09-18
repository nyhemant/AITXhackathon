#!/usr/bin/env python3
"""Wave-1 unique cores + one-liners for eight home-facing packs. Dual-write JSON only."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENUE_DIR = ROOT / "static/field-pack/data/venues"

AGE = ["2-3", "4-5", "6-8", "9+"]


def item(
    *,
    iid: str,
    label: str,
    emoji: str,
    one_liner: str,
    catalog_id: str,
    zone: str,
    tags: list[str],
    core: bool,
    presence_note: str = "",
) -> dict:
    out = {
        "id": iid,
        "label": label,
        "emoji": emoji,
        "one_liner": one_liner,
        "tags": tags,
        "age_fit": AGE,
        "zone": zone,
        "qa_card": {
            "question": f"What did you notice about the {label.lower()}?",
            "answer": "Tell a grown-up one thing you saw!",
        },
        "catalog_id": catalog_id,
        "presence": "verified",
        "presence_checked": "2026-08-16",
        "presence_source": "official_animals_page",
        "display_label": label,
        "core": core,
    }
    if presence_note:
        out["presence_note"] = presence_note
    return out


def patch(slug: str, fn) -> None:
    path = VENUE_DIR / f"{slug}.json"
    v = json.loads(path.read_text(encoding="utf-8"))
    fn(v)
    v["last_verified"] = "2026-08-16"
    path.write_text(json.dumps(v, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {slug} items={len(v.get('items') or [])} cores={sum(1 for i in v['items'] if i.get('core'))}")


def by_cid(v: dict) -> dict:
    return {it.get("catalog_id"): it for it in v.get("items") or [] if it.get("catalog_id")}


def set_core_line(it: dict, core: bool, one_liner: str, zone: str | None = None) -> None:
    it["core"] = core
    it["one_liner"] = one_liner
    if zone:
        it["zone"] = zone


def dallas_zoo(v: dict) -> None:
    m = by_cid(v)
    cores = {
        "reticulated-giraffe": ("Feed one from the Giraffe Ridge platform.", "Giraffe Ridge"),
        "african-elephant": ("Baby elephant plus the Giants of the Savanna herd.", "Giants of the Savanna"),
        "african-penguin": ("Penguin Cove — waddle, then zoom in the water.", "Penguin Cove"),
        "nile-hippo": ("Simmons Hippo Outpost — watch the underwater window.", "Simmons Hippo Outpost"),
        "caribbean-flamingo": ("ZooNorth pink flock — long legs in the shallows.", "ZooNorth"),
        "cheetah": ("Savanna sprinter — spots, not stripes.", "Giants of the Savanna"),
        "galapagos-tortoise": ("ZooNorth giant — slow steps, huge shell.", "ZooNorth"),
        "sumatran-tiger": ("Endangered Tiger Habitat — orange stripes in the trees.", "Endangered Tiger Habitat"),
    }
    for cid, (line, zone) in cores.items():
        set_core_line(m[cid], True, line, zone)
    for cid, it in m.items():
        if cid not in cores:
            it["core"] = False
    # Children's Zoo stop has no catalog_id — leave, not core
    for it in v["items"]:
        if not it.get("catalog_id"):
            it["core"] = False
            it["one_liner"] = "Play yard after the savanna — goats and a breather."
    order = [
        "reticulated-giraffe",
        "african-elephant",
        "african-penguin",
        "nile-hippo",
        "caribbean-flamingo",
        "cheetah",
        "galapagos-tortoise",
        "sumatran-tiger",
        "african-lion",
        "western-lowland-gorilla",
        "zebra",
        None,
    ]
    rest = [it for it in v["items"] if not it.get("catalog_id")]
    mapped = [m[c] for c in order if c]
    v["items"] = mapped + rest
    v["tagline"] = "Giraffe Ridge feeding plus Penguin Cove and a hippo window."


def cad(v: dict) -> None:
    m = by_cid(v)
    cores = {
        "shark": "Fair Park shark tank — first big fish for little kids.",
        "stingray": "Touch pool rays — gentle hands if the pool is open.",
        "sea-turtle": "Turtle habitats — flippers, not feet.",
        "clownfish": "Small reef tank — orange stripes in the anemone.",
        "seahorse": "Upright swimmers holding on with a tail.",
        "crab": "Tide creatures — sideways walkers.",
        "starfish": "Touch-tank sea star — count the arms.",
        "eel": "Rocky hidey-hole — a long snaky fish.",
    }
    for cid, line in cores.items():
        set_core_line(m[cid], True, line)
    for cid, it in m.items():
        if cid not in cores:
            it["core"] = False
            if cid == "jellyfish":
                it["one_liner"] = "Soft drifters in the jellies gallery."
            elif cid == "octopus":
                it["one_liner"] = "Special-exhibit octopus — eight arms, one hide."
    v["tagline"] = "Fair Park first aquarium: sharks, rays, turtles, and a touch pool."


def perot_kids(v: dict) -> None:
    m = by_cid(v)
    cores = {
        "cm-imaginarium": "Multi-sensory pretend world on the kids floors.",
        "cm-woven": "Woven Wonders — climb the colorful net.",
        "cm-waterfall": "Water play if the pumps are on.",
        "cm-makery": "Make something with your hands, then take it or toss it.",
        "cm-toddler-garden": "Toddler Garden — the same path twice is the point.",
        "cm-outdoor": "Outdoor play when weather allows.",
        "cm-art-lab": "Come-and-go art — mess is allowed.",
        "cm-free-explore": "Let them pick the next zone for five minutes.",
    }
    for cid, line in cores.items():
        set_core_line(m[cid], True, line)
    for it in v["items"]:
        if not it.get("catalog_id"):
            it["core"] = False
            it["one_liner"] = "A quiet corner when the floors get loud."
    v["tagline"] = "Climb, make, splash, imagine — the Perot kids floors."


def dwa(v: dict) -> None:
    m = by_cid(v)
    cores = {
        "two-toed-sloth": "Rainforest canopy — sloths hanging in the greenery.",
        "ring-tailed-lemur": "Primates hall — ring tails and a long stare.",
        "shark": "Indoor sharks on the aquatic loop.",
        "stingray": "Rays gliding the indoor tanks.",
        "jellyfish": "Jellies gallery under the rainforest roof.",
        "freshwater-fish": "Orinoco / river fish — not a Fair Park touch pool.",
        "octopus": "Eight arms in a downtown hide.",
        "eel": "Long fish in the gallery rocks.",
    }
    for cid, line in cores.items():
        set_core_line(m[cid], True, line)
    for cid, it in m.items():
        if cid not in cores:
            it["core"] = False
    v["tagline"] = "Downtown rainforest under a roof — sloths, lemurs, then the tanks."


def perot_museum(v: dict) -> None:
    m = by_cid(v)
    cores = {
        "sci-dinosaur": "T. Boone Pickens Life Then and Now — look up at the giants.",
        "sci-hands-on": "Sports / being human — try one test with your body.",
        "sci-planet": "Earth and space hall — point to a planet or the Moon.",
        "sci-mammal-hall": "Life sciences halls — bones, bodies, and habitats.",
        "cm-makery": "Make floor — build, then try again.",
        "cm-imaginarium": "Kids explore rooms inside the big museum day.",
        "cm-free-explore": "One extra hall they pick.",
    }
    for cid, line in cores.items():
        set_core_line(m[cid], True, line)
    v["items"] = [it for it in v["items"] if it.get("catalog_id") != "sci-rainforest"]
    v["tagline"] = "Dinosaurs plus one sports or space hall — skip the rainforest dome."


def houston(v: dict) -> None:
    extras = [
        item(
            iid="red_panda",
            label="Red panda",
            emoji="🔴",
            one_liner="Hermann Park red panda — rusty coat, not a mini giant panda.",
            catalog_id="red-panda",
            zone="Asia / red pandas",
            tags=["climb", "outdoor"],
            core=True,
        ),
        item(
            iid="warthog",
            label="Warthog",
            emoji="🐗",
            one_liner="African forest warthog — snout, tusks, and a trot.",
            catalog_id="warthog",
            zone="Africa",
            tags=["outdoor", "africa"],
            core=True,
        ),
        item(
            iid="ostrich",
            label="Ostrich",
            emoji="🪶",
            one_liner="Biggest bird on the Africa loop — look at those legs.",
            catalog_id="ostrich",
            zone="Africa",
            tags=["birds", "outdoor"],
            core=True,
        ),
        item(
            iid="caribbean_flamingo",
            label="Caribbean flamingo",
            emoji="🦩",
            one_liner="Houston flamingo flock — pink on the water’s edge.",
            catalog_id="caribbean-flamingo",
            zone="Birds",
            tags=["birds", "outdoor"],
            core=False,
        ),
        item(
            iid="galapagos_tortoise",
            label="Galápagos tortoise",
            emoji="🐢",
            one_liner="Island giant — slow walk, huge shell.",
            catalog_id="galapagos-tortoise",
            zone="Reptiles",
            tags=["outdoor", "slow"],
            core=False,
        ),
        item(
            iid="cheetah",
            label="Cheetah",
            emoji="🐆",
            one_liner="Fast cat on the Africa side — tear marks, not a lion mane.",
            catalog_id="cheetah",
            zone="Big cats",
            tags=["big-cats", "outdoor"],
            core=False,
        ),
    ]
    m = by_cid(v)
    cores = {
        "western-lowland-gorilla": ("McGovern gorillas — who looks calmest?", "Gorillas"),
        "chimpanzee": ("Chimp play and chatter on the ape side.", "Chimps / apes"),
        "zebra": ("Africa zebra — pick one stripe set and draw it in the air.", "Africa"),
        "african-lion": ("Houston lion pride — listen for a roar, then wait.", "Big cats"),
        "sumatran-tiger": ("Tiger water’s edge — why put a pool in the habitat?", "Big cats"),
        "reticulated-giraffe": ("Giraffe tongue watch — 15 seconds at the feeding rail.", "Giraffes"),
    }
    for cid, (line, zone) in cores.items():
        set_core_line(m[cid], True, line, zone)
    v["items"] = list(v["items"]) + extras
    v["tagline"] = "Hermann Park apes, Africa loop, and a red panda — not the Dallas savanna kit."


def sdz(v: dict) -> None:
    m = by_cid(v)
    cores = {
        "giant-panda": "Panda Ridge — bamboo breakfast if the line allows.",
        "koala": "Outback koalas — sleepy in the eucalyptus.",
        "two-toed-sloth": "Rainforest sloth — hang and look twice.",
        "african-elephant": "Elephant Odyssey — a real walking giant.",
        "reticulated-giraffe": "Africa giraffe — tall against the canyon.",
        "orangutan": "Lost Forest orangutan — long arms in the trees.",
        "western-lowland-gorilla": "Lost Forest gorilla family.",
        "sumatran-tiger": "Asian Passage tiger — stripes in the shade.",
    }
    for cid, line in cores.items():
        set_core_line(m[cid], True, line)
    for cid, it in m.items():
        if cid not in cores:
            it["core"] = False
    v["tagline"] = "Pandas and koalas first, then Elephant Odyssey — not a Texas savanna clone."


def national(v: dict) -> None:
    m = by_cid(v)
    cores = {
        "giant-panda": "Asia Trail pandas — the Smithsonian pair.",
        "asian-small-clawed-otter": "Asia Trail otters — smallest otter, biggest splash.",
        "red-panda": "Asia Trail red panda — rusty and tree-high.",
        "caribbean-flamingo": "Bird House flamingo flock on the National Mall side.",
        "orangutan": "O Line orangutans — watch them travel above the path.",
        "african-lion": "Great Cats lion — DC roar, not a Dallas savanna.",
        "sumatran-tiger": "Great Cats tiger next door to the lions.",
        "western-lowland-gorilla": "Great Ape House gorilla family.",
    }
    for cid, line in cores.items():
        set_core_line(m[cid], True, line)
    v["tagline"] = "Asia Trail pandas and otters, then the O Line — no African elephants here."


def main() -> None:
    patch("dallas-zoo", dallas_zoo)
    patch("childrens-aquarium-dallas", cad)
    patch("childrens-museum-perot", perot_kids)
    patch("dallas-world-aquarium", dwa)
    patch("perot-museum", perot_museum)
    patch("houston-zoo", houston)
    patch("san-diego-zoo", sdz)
    patch("national-zoo", national)


if __name__ == "__main__":
    main()
