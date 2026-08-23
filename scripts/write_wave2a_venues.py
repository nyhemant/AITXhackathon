#!/usr/bin/env python3
"""Write Wave 2a venue JSONs + card-kinds.tsv from the 2026-08-23 official pass."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENUES = REPO / "static" / "field-pack" / "data" / "venues"
TSV = REPO / "static" / "field-pack" / "data" / "card-kinds.tsv"

AGE = ["2-3", "4-5", "6-8", "9+"]
QA = {"question": "What did you notice about the {label}?", "answer": "Tell a grown-up one thing you saw!"}

# slug, title, hub, kind
CARD_KINDS = [
    ("african-elephant", "African elephant", "wildlife", "zoo"),
    ("african-lion", "African lion", "wildlife", "zoo"),
    ("cheetah", "Cheetah", "wildlife", "zoo"),
    ("chimpanzee", "Chimpanzee", "wildlife", "zoo"),
    ("galapagos-tortoise", "Galápagos tortoise", "wildlife", "zoo"),
    ("giant-panda", "Giant panda", "wildlife", "zoo"),
    ("koala", "Koala", "wildlife", "zoo"),
    ("nile-hippo", "Nile hippo", "wildlife", "zoo"),
    ("orangutan", "Orangutan", "wildlife", "zoo"),
    ("ostrich", "Ostrich", "wildlife", "zoo"),
    ("red-panda", "Red panda", "wildlife", "zoo"),
    ("reticulated-giraffe", "Reticulated giraffe", "wildlife", "zoo"),
    ("ring-tailed-lemur", "Ring-tailed lemur", "wildlife", "zoo"),
    ("sumatran-tiger", "Sumatran tiger", "wildlife", "zoo"),
    ("warthog", "Warthog", "wildlife", "zoo"),
    ("western-lowland-gorilla", "Western lowland gorilla", "wildlife", "zoo"),
    ("zebra", "Zebra", "wildlife", "zoo"),
    ("african-penguin", "African penguin", "wildlife", "both"),
    ("asian-small-clawed-otter", "Asian small-clawed otter", "wildlife", "both"),
    ("caribbean-flamingo", "Caribbean flamingo", "wildlife", "both"),
    ("two-toed-sloth", "Two-toed sloth", "wildlife", "both"),
    ("freshwater-fish", "River / lake fish", "sealife", "both"),
    ("shark", "Shark", "sealife", "both"),
    ("clownfish", "Clownfish", "sealife", "aquarium"),
    ("crab", "Crab", "sealife", "aquarium"),
    ("eel", "Eel", "sealife", "aquarium"),
    ("jellyfish", "Jellyfish", "sealife", "aquarium"),
    ("octopus", "Octopus", "sealife", "aquarium"),
    ("starfish", "Sea star", "sealife", "aquarium"),
    ("sea-turtle", "Sea turtle", "sealife", "aquarium"),
    ("seahorse", "Seahorse", "sealife", "aquarium"),
    ("stingray", "Stingray", "sealife", "aquarium"),
    ("puffin", "Puffin", "sealife", "aquarium"),
    ("sea-otter", "Sea otter", "sealife", "aquarium"),
    ("manta-ray", "Manta ray", "sealife", "aquarium"),
    ("kelp-forest", "Kelp forest", "sealife", "aquarium"),
    ("cuttlefish", "Cuttlefish", "sealife", "aquarium"),
    ("whale-shark", "Whale shark", "sealife", "aquarium"),
    ("cm-outdoor", "Outdoor Area", "attractions", "neither"),
    ("cm-toddler-garden", "Toddler Garden", "attractions", "neither"),
    ("cm-imaginarium", "Imaginarium", "attractions", "neither"),
    ("cm-woven", "Woven Wonders", "attractions", "neither"),
    ("cm-makery", "Makery", "attractions", "neither"),
    ("cm-art-lab", "Art Lab", "attractions", "neither"),
    ("cm-free-explore", "Free explore", "attractions", "neither"),
    ("sci-dinosaur", "Dinosaur hall", "attractions", "neither"),
    ("sci-mammal-hall", "Animal / mammal hall", "attractions", "neither"),
    ("sci-planet", "Planet / space hall", "attractions", "neither"),
    ("sci-hands-on", "Hands-on lab", "attractions", "neither"),
    ("sci-rainforest", "Rainforest dome", "attractions", "neither"),
    ("sci-aquarium-zone", "Aquarium zone", "attractions", "neither"),
    ("sci-rocket", "Rockets & launch", "attractions", "neither"),
    ("sci-astronaut", "Astronaut training", "attractions", "neither"),
    ("american-alligator", "American alligator", "parks", "neither"),
    ("american-bison", "American bison", "parks", "neither"),
    ("elk", "Elk", "parks", "neither"),
    ("cuyahoga-towpath", "Towpath trail", "parks", "neither"),
]

META = {
    "reticulated-giraffe": ("🦒", ["tall", "outdoor", "wow"], "Giraffe Ridge feeding plus a long neck."),
    "african-lion": ("🦁", ["big-cats", "outdoor", "sound"], "Big cat of the grassland pride — mighty roar!"),
    "sumatran-tiger": ("🐯", ["big-cats", "pattern", "outdoor"], "Orange stripes built for stealth."),
    "cheetah": ("🐆", ["big-cats", "outdoor"], "Fastest land animal — built to sprint."),
    "western-lowland-gorilla": ("🦍", ["primates", "outdoor"], "Strong gentle ape in family groups."),
    "orangutan": ("🦧", ["primates", "climb", "outdoor"], "Tree ape with long arms — watches from the canopy."),
    "chimpanzee": ("🐵", ["primates", "play"], "Smart forest ape — climbs and tools."),
    "nile-hippo": ("🦛", ["big", "water", "outdoor"], "Huge river giant that loves the water."),
    "ostrich": ("🪶", ["birds", "outdoor"], "Biggest bird — can’t fly, runs fast."),
    "zebra": ("🦓", ["pattern", "outdoor", "savanna"], "Striped grassland runner — every pattern is unique."),
    "caribbean-flamingo": ("🦩", ["birds", "color", "water"], "Bright pink wader — long legs for shallow water."),
    "two-toed-sloth": ("🦥", ["climb", "outdoor"], "Slow forest climber — hangs upside down."),
    "galapagos-tortoise": ("🐢", ["outdoor", "slow"], "Giant tortoise — slow and steady."),
    "asian-small-clawed-otter": ("🦦", ["play", "water"], "Playful swimmer — smallest otter."),
    "african-penguin": ("🐧", ["birds", "water", "outdoor"], "Waddle on land, zoom in water."),
    "red-panda": ("🦊", ["climb", "outdoor"], "Rusty tree-climber with a ringed tail — not a giant panda!"),
    "ring-tailed-lemur": ("🐒", ["primates", "pattern", "climb"], "Stripy tail from Madagascar."),
    "warthog": ("🐗", ["outdoor", "africa"], "Savanna pig with tusks."),
}

TITLES = {s: t for s, t, _h, _k in CARD_KINDS}


def item(cid: str, *, zone: str, one: str, core: bool, presence: str = "verified",
         label: str | None = None, note: str | None = None) -> dict:
    emoji, tags, default_one = META[cid]
    title = label or TITLES[cid]
    out = {
        "id": cid.replace("-", "_"),
        "label": title,
        "emoji": emoji,
        "one_liner": one or default_one,
        "tags": tags,
        "age_fit": AGE,
        "zone": zone,
        "qa_card": {
            "question": QA["question"].format(label=title),
            "answer": QA["answer"],
        },
        "catalog_id": cid,
        "presence": presence,
        "presence_checked": "2026-08-23",
        "presence_source": "official_animals_page",
        "display_label": title,
        "core": core,
    }
    if note:
        out["presence_note"] = note
    return out


def ban(cid: str, reason: str) -> dict:
    return {"catalog_id": cid, "name": TITLES.get(cid, cid), "reason": reason, "as_of": "2026-08-23"}


def hunt(tagline: str, find_ids: list[str], challenges: list[tuple[str, str]], sources: list[str]) -> dict:
    return {
        "tagline": tagline,
        "find_ids": find_ids,
        "challenges": [
            {"id": hid, "text": text, "age_fit": ["2-3", "4-5", "6-8", "adult"]}
            for hid, text in challenges
        ],
        "easter_egg": "★ Easter egg: find this zoo on a map/sign and point to a habitat you have not visited yet",
        "easter_egg_little": "★ Easter egg: pick a favorite stop and tell a grown-up why",
        "sources": sources,
        "researched": "2026-08-23",
        "status": "researched",
    }


def patch(slug: str, **fields) -> None:
    path = VENUES / f"{slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(fields)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_tsv() -> None:
    lines = ["slug\ttitle\thub\tkind"]
    lines.extend(f"{s}\t{t}\t{h}\t{k}" for s, t, h, k in CARD_KINDS)
    TSV.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_tsv()

    patch(
        "fort-worth-zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Predators of Asia & Africa, then the Savanna hippo river.",
        items=[
            item("african-lion", zone="Predators of Asia & Africa", one="Predators habitat — listen for a roar.", core=True),
            item("sumatran-tiger", zone="Predators of Asia & Africa", one="Predators of Asia — orange stripes in the trees.", core=True),
            item("nile-hippo", zone="African Savanna", one="Savanna hippo river — watch the underwater window.", core=True),
            item("cheetah", zone="Predators of Asia & Africa", one="Fast cat on the Predators path — tear marks, not a lion mane.", core=True),
            item("reticulated-giraffe", zone="African Savanna", one="Savanna giraffe — look up from the feeding deck.", core=True, label="Giraffe", note="Official habitats list giraffes; soft Giraffe."),
            item("western-lowland-gorilla", zone="World of Primates", one="World of Primates gorilla troop in the forest yard.", core=True, label="Gorilla"),
            item("orangutan", zone="World of Primates", one="World of Primates orangutan — long arms in the trees.", core=True),
            item("ostrich", zone="African Savanna", one="Savanna ostrich — look at those legs.", core=False),
            item("caribbean-flamingo", zone="Flamingo flock / entrance", one="Pink flock near the entrance — long legs in the shallows.", core=False),
            item("two-toed-sloth", zone="World of Primates", one="Olive the two-toed sloth — hang and look twice.", core=False),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass (habitats + Predators + construction updates).",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("african-elephant", "Official: Asian elephants at Elephant Springs."),
            ban("african-penguin", "Official: African penguins moved to Waco; remaining penguins are southern rockhopper."),
            ban("galapagos-tortoise", "Official herpetarium / chats list Aldabra tortoise, not Galápagos."),
            ban("asian-small-clawed-otter", "Official: North American river otter, not Asian small-clawed."),
            ban("chimpanzee", "Official World of Primates lists bonobos, not chimpanzees."),
        ],
        route_90m=["african_lion", "sumatran_tiger", "nile_hippo"],
        presence_sources=[
            "https://www.fortworthzoo.org/",
            "https://www.fortworthzoo.org/habitats",
            "https://www.fortworthzoo.org/predators",
            "https://www.fortworthzoo.org/construction-updates",
        ],
        bonus_hunt=hunt(
            "Fort Worth bonus · Predators + Savanna + Primates",
            ["cheetah", "reticulated_giraffe", "western_lowland_gorilla", "orangutan", "caribbean_flamingo", "two_toed_sloth"],
            [
                ("fw_lion", "Predators: watch a lion for 20 seconds — roar, rest, or pace?"),
                ("fw_tiger", "Tiger yard: count stripe clusters on one shoulder (best guess)."),
                ("fw_hippo", "Hippo river: more underwater, mud, or bank?"),
                ("fw_sloth", "World of Primates sloth: mid-reach or statue-still?"),
            ],
            ["https://www.fortworthzoo.org/habitats", "https://www.fortworthzoo.org/predators"],
        ),
    )

    patch(
        "san-antonio-zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Congo Falls gorillas, then Pride Plaza flamingos and Big Cat Valley.",
        items=[
            item("western-lowland-gorilla", zone="Congo Falls", one="Congo Falls gorillas — face to face in the tall habitat.", core=True),
            item("caribbean-flamingo", zone="Pride Plaza", one="Pride Plaza pink flock — the unofficial welcome committee.", core=True),
            item("african-lion", zone="Big Cat Valley", one="Big Cat Valley lions — face-to-face viewing.", core=True),
            item("zebra", zone="Naylor Savanna", one="Savanna zebra — pick one stripe set and draw it in the air.", core=True),
            item("reticulated-giraffe", zone="Naylor Savanna", one="Savanna giraffe — feed one if the line allows.", core=True, label="Giraffe", note="Official Naylor Savanna lists giraffes; soft Giraffe."),
            item("nile-hippo", zone="Africa Live!", one="Africa Live hippos Timothy and Uma — watch the underwater window.", core=True, label="Hippo", note="Official: world-famous hippos Timothy and Uma. Soft Hippo."),
            item("asian-small-clawed-otter", zone="Asian Forest", one="Asian Forest otters — smallest otter, biggest splash.", core=False),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass (sazoo.org/animals habitats).",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("african-elephant", "Not on the official animals / habitats list."),
            ban("african-penguin", "Not on the official animals / habitats list."),
            ban("sumatran-tiger", "Not on the official animals / habitats list."),
            ban("galapagos-tortoise", "Official VIP list: Aldabra tortoises, not Galápagos."),
            ban("ring-tailed-lemur", "Official Pride Plaza: red ruffed and black-and-white lemurs, not ring-tailed."),
        ],
        route_90m=["western_lowland_gorilla", "caribbean_flamingo", "african_lion"],
        presence_sources=[
            "https://sazoo.org/",
            "https://sazoo.org/animals/",
            "https://sazoo.org/congo-falls/",
        ],
        bonus_hunt=hunt(
            "San Antonio bonus · Congo Falls + Pride Plaza + Savanna",
            ["zebra", "reticulated_giraffe", "nile_hippo", "asian_small_clawed_otter"],
            [
                ("sa_gorilla", "Congo Falls: who looks calmest in the gorilla family?"),
                ("sa_flam", "Pride Plaza flamingos: more than half on one leg?"),
                ("sa_lion", "Big Cat Valley: listen for a roar, then wait."),
                ("sa_hippo", "Africa Live: Timothy or Uma — underwater or bank?"),
            ],
            ["https://sazoo.org/animals/"],
        ),
    )

    patch(
        "austin-zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Hill Country rescue zoo — lions, cheetahs, tortoises; not a megafauna safari.",
        items=[
            item("african-lion", zone="Big cats", one="Rescue lions — shorter campus, big presence.", core=True),
            item("cheetah", zone="Big cats", one="Cheetah chats on the rescue schedule — often still.", core=True),
            item("galapagos-tortoise", zone="Reptiles", one="Giant tortoises + private encounters marketed.", core=True),
            item("zebra", zone="Hoofstock", one="Zebra/ostrich chats on the schedule.", core=True),
            item("ostrich", zone="Hoofstock", one="Big flightless bird with zebra yard energy.", core=False),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass (austinzoo.org plan-a-visit + sponsors). Rescue collection; published zoo/both cards only.",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("sumatran-tiger", "Official: white tiger / tiger habitats — not Sumatran."),
            ban("reticulated-giraffe", "Rescue zoo; giraffes not a featured species."),
            ban("african-elephant", "No elephant program."),
            ban("nile-hippo", "No hippo program."),
            ban("red-panda", "Not on the official visit / sponsor list."),
            ban("ring-tailed-lemur", "Official schedule lists brown lemur feeding, not ring-tailed."),
        ],
        route_90m=["african_lion", "cheetah", "galapagos_tortoise"],
        presence_sources=[
            "https://austinzoo.org/",
            "https://austinzoo.org/plan-a-visit/",
            "https://austinzoo.org/sponsors/",
        ],
        bonus_hunt=hunt(
            "Austin bonus · rescue cats + tortoise barn + hoofstock",
            ["zebra", "ostrich"],
            [
                ("az_lion", "Lions: mane fluff or sleek face — who looks more awake?"),
                ("az_cheetah", "Cheetah: statue score 1–10 after 20 quiet seconds."),
                ("az_tort", "Galápagos tortoise barn: mid-step or statue?"),
                ("az_zebra", "Zebra/ostrich yard: stripes vs feathers — which is busier?"),
            ],
            ["https://austinzoo.org/plan-a-visit/", "https://austinzoo.org/sponsors/"],
        ),
    )

    patch(
        "lincoln-park-zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Free lakefront apes, Penguin Cove, then a small-clawed otter splash.",
        items=[
            item("western-lowland-gorilla", zone="Regenstein Center for African Apes", one="Lakefront gorilla family — who looks in charge?", core=True),
            item("african-penguin", zone="Pritzker Penguin Cove", one="Penguin Cove — waddle, then zoom in the water.", core=True),
            item("asian-small-clawed-otter", zone="Animals & exhibits", one="Smallest otter, biggest splash.", core=True),
            item("chimpanzee", zone="Regenstein Center for African Apes", one="Chimp play and chatter on the ape side.", core=True),
            item("african-lion", zone="Kovler Lion House", one="Lion House pride — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="Regenstein African Journey", one="African Journey giraffe — look up from the path.", core=True, label="Giraffe", note="Official giraffe training at African Journey; soft Giraffe."),
            item("zebra", zone="Camel & Zebra", one="Park zebra — pick one stripe set and draw it in the air.", core=False),
            item("caribbean-flamingo", zone="Waterfowl Lagoon", one="Lagoon flamingos — long legs in the shallows.", core=False, label="Flamingo", note="Official waterfowl lagoon lists flamingos; soft Flamingo."),
            item("two-toed-sloth", zone="Small Mammal-Reptile House", one="Small-mammal sloth — hang and look twice.", core=False, label="Sloth", note="Official welcome guide: sloths in the Small Mammal-Reptile House. Soft Sloth."),
            item("red-panda", zone="Animals & gardens", one="Red panda — rusty and tree-high.", core=False, presence="high", note="Official animals & gardens features red pandas; confirm yard on arrival."),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass (lpzoo.org animals-exhibits + visit guide).",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("african-elephant", "Official African Journey lists giraffes, rhinos, and pygmy hippos — no elephants."),
            ban("nile-hippo", "Official: pygmy hippos, not Nile hippo."),
            ban("sumatran-tiger", "Not on the official animals / exhibits list."),
        ],
        route_90m=["western_lowland_gorilla", "african_penguin", "asian_small_clawed_otter"],
        presence_sources=[
            "https://www.lpzoo.org/",
            "https://www.lpzoo.org/animals-gardens/animals-exhibits/",
            "https://www.lpzoo.org/visit/things-to-do/",
        ],
        bonus_hunt=hunt(
            "Lincoln Park bonus · apes + Penguin Cove + Lion House",
            ["chimpanzee", "african_lion", "reticulated_giraffe", "zebra", "caribbean_flamingo", "two_toed_sloth"],
            [
                ("lp_gorilla", "Ape house: gorilla hands busy or full rest?"),
                ("lp_penguin", "Penguin Cove: watch one bird enter or leave the water."),
                ("lp_otter", "Otters: find the splashiest 10 seconds."),
                ("lp_lion", "Lion House: roar or a quiet pride?"),
            ],
            ["https://www.lpzoo.org/animals-gardens/animals-exhibits/"],
        ),
    )

    patch(
        "bronx-zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Congo Gorilla Forest, then a Himalayan red panda and flamingo flock.",
        items=[
            item("western-lowland-gorilla", zone="Congo Gorilla Forest", one="Congo gorillas — each has a unique personality.", core=True, label="Gorilla"),
            item("red-panda", zone="Himalayan Highlands", one="Himalayan Highlands red panda — rusty and tree-high.", core=True),
            item("caribbean-flamingo", zone="Aquatic Bird House", one="Sea Bird Aviary flamingo flock — long legs in the shallows.", core=True),
            item("reticulated-giraffe", zone="Carter Giraffe Building", one="Carter giraffe — indoor or African Plains outdoor yard.", core=True, label="Giraffe", note="Official Our Animals lists Giraffe; soft Giraffe."),
            item("zebra", zone="African Plains", one="Grevy's zebra on African Plains — every pattern is unique.", core=True, label="Zebra", note="Official: Grevy's zebra."),
            item("two-toed-sloth", zone="Children's Zoo", one="Linne's two-toed sloth — hang and look twice.", core=False),
            item("asian-small-clawed-otter", zone="JungleWorld", one="JungleWorld otters — smallest otter, biggest splash.", core=False),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass (bronxzoo.com/animals/our-animals).",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("african-elephant", "Official: Asian Elephant on the Wild Asia Monorail."),
            ban("sumatran-tiger", "Official: Amur tiger and Malayan tiger at Tiger Mountain."),
            ban("african-penguin", "Official: little penguin and Magellanic penguin, not African."),
            ban("galapagos-tortoise", "Official: Aldabra tortoise at Zoo Center."),
            ban("ring-tailed-lemur", "Official Madagascar list: red ruffed lemur, not ring-tailed."),
            ban("african-lion", "Not on the current official Our Animals list."),
            ban("nile-hippo", "Not on the current official Our Animals list."),
        ],
        route_90m=["western_lowland_gorilla", "red_panda", "caribbean_flamingo"],
        presence_sources=[
            "https://bronxzoo.com/",
            "https://bronxzoo.com/animals/our-animals",
            "https://bronxzoo.com/things-to-do/exhibits",
        ],
        bonus_hunt=hunt(
            "Bronx bonus · Congo + Highlands + African Plains",
            ["reticulated_giraffe", "zebra", "two_toed_sloth", "asian_small_clawed_otter"],
            [
                ("bx_gorilla", "Congo Gorilla Forest: cautious, playful, or nurturing today?"),
                ("bx_panda", "Red panda: climb or curl-up?"),
                ("bx_flam", "Flamingos: pinkest bird in the flock — point once."),
                ("bx_zebra", "African Plains: Grevy's stripes — shoulder vs rump."),
            ],
            ["https://bronxzoo.com/animals/our-animals"],
        ),
    )

    patch(
        "la-zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Chimps, gorillas, and orangutans — the elephant program is paused.",
        items=[
            item("chimpanzee", zone="Chimpanzees of the Mahale Mountains", one="One of the largest chimp troops in a U.S. zoo.", core=True),
            item("western-lowland-gorilla", zone="Campo Gorilla Reserve", one="Campo gorillas — gentle giants in the reserve.", core=True),
            item("orangutan", zone="Red Ape Rainforest", one="Bornean orangutan — long arms in the trees.", core=True),
            item("sumatran-tiger", zone="Mammals", one="Sumatran tiger — orange stripes in the trees.", core=True),
            item("zebra", zone="Africa", one="Grevy's zebra — every stripe set is unique.", core=True, label="Zebra", note="Official mammals list: Grevy's zebra."),
            item("two-toed-sloth", zone="Mammals", one="Linné's two-toed sloth — hang and look twice.", core=False),
            item("ring-tailed-lemur", zone="Mammals", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("caribbean-flamingo", zone="Birds", one="Flamingo Mingle flock — long legs in the shallows.", core=False, label="Flamingo", note="Official calendar lists Flamingo Mingle; soft Flamingo."),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass (lazoo.org mammals + elephant relocation news).",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("african-elephant", "Official Apr 2025: remaining Asian elephants moved to Tulsa; elephant program paused."),
            ban("reticulated-giraffe", "Official mammals list: Masai giraffe, not reticulated."),
            ban("nile-hippo", "Not on the current official mammals list."),
            ban("african-lion", "Not on the current official mammals list."),
            ban("african-penguin", "Not on the current official animals list."),
            ban("koala", "Not on the current official mammals list."),
        ],
        route_90m=["chimpanzee", "western_lowland_gorilla", "orangutan"],
        presence_sources=[
            "https://www.lazoo.org/",
            "https://lazoo.org/explore-your-zoo/our-animals/mammals/",
            "https://lazoo.org/2025/04/elephantnews/",
            "https://lazoo.org/plan-your-visit/shows-activities/",
        ],
        bonus_hunt=hunt(
            "LA Zoo bonus · great apes + tiger + flamingo mingle",
            ["sumatran_tiger", "zebra", "two_toed_sloth", "ring_tailed_lemur", "caribbean_flamingo"],
            [
                ("la_chimp", "Chimp Chat yard: hands used like tools (hold, climb, poke)?"),
                ("la_gorilla", "Gorilla Talk: who looks calmest?"),
                ("la_orang", "Orangutan: hands or feet doing the clever bit?"),
                ("la_flam", "Flamingo Mingle: more than half on one leg?"),
            ],
            ["https://lazoo.org/explore-your-zoo/our-animals/mammals/"],
        ),
    )

    patch(
        "oregon-zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Red pandas and chimps first — Asian elephants, not African.",
        items=[
            item("red-panda", zone="Discovery Zone", one="Discovery Zone red panda — rusty and tree-high.", core=True),
            item("chimpanzee", zone="Primate Forest", one="Primate Forest chimp play and chatter.", core=True),
            item("african-lion", zone="Africa", one="Oregon lion pride — listen for a roar, then wait.", core=True, label="Lion", note="Official map lists Lions; news names the African lion pride."),
            item("orangutan", zone="Primate Forest", one="Primate Forest orangutan — long arms in the trees.", core=True),
            item("ring-tailed-lemur", zone="Animals", one="Ring-tailed lemur — striped tail on the primate side.", core=True),
            item("reticulated-giraffe", zone="Africa", one="Africa giraffe — look up from the path.", core=False, label="Giraffe", note="Official map lists Giraffe; soft Giraffe."),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass (map.oregonzoo.org animals + oregonzoo.org news).",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("african-elephant", "Official: Asian elephant at Elephant Lands."),
            ban("sumatran-tiger", "Official: Amur tiger in Discovery Zone."),
            ban("african-penguin", "Official: Humboldt penguin at Pacific Shores."),
            ban("caribbean-flamingo", "Official: lesser flamingo, not Caribbean."),
            ban("western-lowland-gorilla", "Not on the official animals map."),
            ban("nile-hippo", "Not on the official animals map."),
        ],
        route_90m=["red_panda", "chimpanzee", "african_lion"],
        presence_sources=[
            "https://www.oregonzoo.org/",
            "https://map.oregonzoo.org/place-types/169-animals",
            "https://www.oregonzoo.org/news",
        ],
        bonus_hunt=hunt(
            "Oregon bonus · red panda + Primate Forest + lions",
            ["orangutan", "ring_tailed_lemur", "reticulated_giraffe"],
            [
                ("or_panda", "Red panda: climb or curl-up?"),
                ("or_chimp", "Chimps: spot hands used like tools."),
                ("or_lion", "Lions: roar or a quiet pride?"),
                ("or_orang", "Orangutan: hands or feet doing the clever bit?"),
            ],
            ["https://map.oregonzoo.org/place-types/169-animals"],
        ),
    )

    patch(
        "columbus-zoo",
        type="zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Congo gorillas, then Heart of Africa lions and cheetahs — zoo-side cards only.",
        items=[
            item("western-lowland-gorilla", zone="Congo Expedition", one="Congo Expedition gorillas — who looks in charge?", core=True),
            item("african-lion", zone="Heart of Africa", one="Heart of Africa lion pride — listen for a roar.", core=True),
            item("cheetah", zone="Heart of Africa", one="Heart of Africa cheetah — tear marks, not a lion mane.", core=True),
            item("orangutan", zone="Animals", one="Bornean orangutan — long arms in the trees.", core=True),
            item("red-panda", zone="Asia Quest", one="Asia Quest red panda — rusty and tree-high.", core=True),
            item("zebra", zone="Heart of Africa", one="Grant's zebra — pick one stripe set and draw it in the air.", core=True, label="Zebra", note="Official: Grant's zebra."),
            item("ostrich", zone="Heart of Africa", one="Heart of Africa ostrich — look at those legs.", core=False),
            item("warthog", zone="Heart of Africa", one="Common warthog — snout, tusks, and a trot.", core=False),
            item("reticulated-giraffe", zone="Heart of Africa", one="Heart of Africa giraffe — feedings seasonally.", core=False, label="Giraffe", note="Official animals list: Giraffe; soft Giraffe."),
            item("caribbean-flamingo", zone="Shores", one="Shores flamingo flock — long legs in the shallows.", core=False),
            item("asian-small-clawed-otter", zone="Animals", one="Asian small-clawed otter — smallest otter, biggest splash.", core=False),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass. Zoo-side only; Discovery Reef aquarium-only cards dropped.",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("african-elephant", "Official animals list: Asian Elephant."),
            ban("sumatran-tiger", "Official animals list: Amur Tiger."),
            ban("african-penguin", "Official: Humboldt penguin at Shores, not African."),
            ban("nile-hippo", "Not on the current official animals list."),
            ban("chimpanzee", "Official Congo list: bonobos, not chimpanzees."),
            ban("galapagos-tortoise", "Official: Aldabra tortoise at Shores."),
            ban("shark", "Discovery Reef aquarium-side; not a zoo-side card for this kit."),
        ],
        route_90m=["western_lowland_gorilla", "african_lion", "cheetah"],
        presence_sources=[
            "https://www.columbuszoo.org/",
            "https://www.columbuszoo.org/animals",
        ],
        bonus_hunt=hunt(
            "Columbus bonus · Congo + Heart of Africa (zoo-side)",
            ["orangutan", "red_panda", "zebra", "ostrich", "warthog", "caribbean_flamingo"],
            [
                ("cz_gorilla", "Congo: gorilla family — who looks calmest?"),
                ("cz_lion", "Heart of Africa: roar or a quiet pride?"),
                ("cz_cheetah", "Cheetah: statue score 1–10 after 20 quiet seconds."),
                ("cz_zebra", "Grant's zebra: draw one stripe set in the air."),
            ],
            ["https://www.columbuszoo.org/animals"],
        ),
    )

    patch(
        "denver-zoo",
        last_verified=None,
        verified_by="research",
        tagline="Starter list from published zoo cards still honest on official Denver pages.",
        items=[
            item("western-lowland-gorilla", zone="Gorillas", one="Lowland gorilla viewing — who looks calmest?", core=True),
            item("orangutan", zone="Asia", one="Sumatran orangutan — long arms in the trees.", core=True),
            item("african-penguin", zone="African Penguin Point", one="Penguin Point — waddle, then zoom in the water.", core=True),
            item("zebra", zone="Africa", one="Grevy's zebra — every stripe set is unique.", core=True, label="Zebra", note="Official animals page: Grevy's zebra."),
            item("two-toed-sloth", zone="Animals", one="Linne's two-toed sloth — hang and look twice.", core=False, presence="high", note="Official 2024 report lists Linne's two-toed sloth young."),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Wave 2a: official animals index is incomplete (“not all animals represented”). Short Starter list from published zoo/both cards named on official Denver pages. No invented verify date.",
        list_confidence="partial",
        do_not_list=[
            ban("african-elephant", "Official / sensory materials: Asian elephants at Elephant Passage."),
            ban("ring-tailed-lemur", "Official animals page lists red-ruffed lemur, not ring-tailed."),
        ],
        route_90m=["western_lowland_gorilla", "orangutan", "african_penguin"],
        presence_sources=[
            "https://denverzoo.org/",
            "https://denverzoo.org/animals/",
            "https://denverzoo.org/annual-report/",
        ],
        bonus_hunt=hunt(
            "Denver bonus · gorillas + orangutans + Penguin Point",
            ["zebra", "two_toed_sloth"],
            [
                ("dv_gorilla", "Gorilla yard: who looks in charge?"),
                ("dv_orang", "Orangutan: hands or feet doing the clever bit?"),
                ("dv_penguin", "Penguin Point: watch one bird enter or leave the water."),
                ("dv_zebra", "Grevy's zebra: shoulder stripes vs rump."),
            ],
            ["https://denverzoo.org/animals/"],
        ),
    )
    # Drop last_verified / last_presence_audit on the Denver Starter kit.
    denver = json.loads((VENUES / "denver-zoo.json").read_text(encoding="utf-8"))
    denver.pop("last_verified", None)
    denver.pop("last_presence_audit", None)
    denver["status"] = "partial"
    (VENUES / "denver-zoo.json").write_text(json.dumps(denver, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    patch(
        "st-louis-zoo",
        last_verified="2026-08-23",
        verified_by="research",
        tagline="Ape house first, then a reticulated giraffe — penguins here are not African.",
        items=[
            item("western-lowland-gorilla", zone="Apes", one="Western lowland gorilla family — who looks calmest?", core=True),
            item("chimpanzee", zone="Apes", one="Chimp play and chatter on the ape side.", core=True),
            item("reticulated-giraffe", zone="Hoofed mammals", one="Official reticulated giraffe — look up from the path.", core=True),
            item("orangutan", zone="Apes", one="Sumatran orangutan — long arms in the trees.", core=True),
            item("nile-hippo", zone="Hoofed mammals", one="River hippo — watch the underwater window.", core=True, label="Hippo", note="Official mammals list: Hippopotamus. Soft Hippo."),
            item("cheetah", zone="Mammals", one="Cheetah — tear marks, not a lion mane.", core=True),
            item("zebra", zone="Hoofed mammals", one="Grevy's zebra — every stripe set is unique.", core=False, label="Zebra", note="Official: Grevy's zebra."),
            item("ring-tailed-lemur", zone="Lemurs, monkeys and apes", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("two-toed-sloth", zone="Mammals", one="Hoffman's two-toed sloth — hang and look twice.", core=False),
            item("red-panda", zone="Mammals", one="Red panda — rusty and tree-high.", core=False),
        ],
        content_mode="curated",
        research_notes="[2026-08-23] Official-source Wave 2a public list pass (stlzoo.org/animals/mammals).",
        list_confidence="audited",
        last_presence_audit="2026-08-23",
        do_not_list=[
            ban("african-elephant", "Official mammals list: Asian Elephant."),
            ban("sumatran-tiger", "Official mammals list: Amur tiger."),
            ban("african-penguin", "Official penguin page: rockhopper, king, Humboldt, and gentoo — not African."),
            ban("african-lion", "Lion is not on the current official mammals list."),
        ],
        route_90m=["western_lowland_gorilla", "chimpanzee", "reticulated_giraffe"],
        presence_sources=[
            "https://www.stlzoo.org/",
            "https://stlzoo.org/animals/mammals",
            "https://stlzoo.org/animals/mammals/lemurs-monkeys-apes",
            "https://stlzoo.org/animals/birds/penguins",
        ],
        bonus_hunt=hunt(
            "Saint Louis bonus · apes + giraffe + hippo",
            ["orangutan", "nile_hippo", "cheetah", "zebra", "ring_tailed_lemur", "red_panda"],
            [
                ("stl_gorilla", "Gorilla family: who looks in charge?"),
                ("stl_chimp", "Chimps: spot hands used like tools."),
                ("stl_giraffe", "Reticulated giraffe: count the spots you can see on one neck."),
                ("stl_hippo", "Hippo: underwater, mud, or bank?"),
            ],
            ["https://stlzoo.org/animals/mammals"],
        ),
    )


if __name__ == "__main__":
    main()
