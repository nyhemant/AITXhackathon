#!/usr/bin/env python3
"""Write Wave 3a international zoo venue JSONs + catalog.js kits (2026-08-23 official pass).

Does not rewrite card-kinds.tsv. Does not touch Wave 1, 2a, or 2b US zoo kits.
Does not touch aquariums, museums, parks, Madrid Zoo Aquarium, or Singapore Night Safari.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENUES = REPO / "static" / "field-pack" / "data" / "venues"
CATALOG = REPO / "static" / "field-pack" / "js" / "catalog.js"

AGE = ["2-3", "4-5", "6-8", "9+"]
QA = {"question": "What did you notice about the {label}?", "answer": "Tell a grown-up one thing you saw!"}

TITLES = {
    "african-elephant": "African elephant",
    "african-lion": "African lion",
    "cheetah": "Cheetah",
    "chimpanzee": "Chimpanzee",
    "galapagos-tortoise": "Galápagos tortoise",
    "giant-panda": "Giant panda",
    "koala": "Koala",
    "nile-hippo": "Nile hippo",
    "orangutan": "Orangutan",
    "ostrich": "Ostrich",
    "red-panda": "Red panda",
    "reticulated-giraffe": "Reticulated giraffe",
    "ring-tailed-lemur": "Ring-tailed lemur",
    "sumatran-tiger": "Sumatran tiger",
    "warthog": "Warthog",
    "western-lowland-gorilla": "Western lowland gorilla",
    "zebra": "Zebra",
    "african-penguin": "African penguin",
    "asian-small-clawed-otter": "Asian small-clawed otter",
    "caribbean-flamingo": "Caribbean flamingo",
    "two-toed-sloth": "Two-toed sloth",
    "freshwater-fish": "River / lake fish",
    "shark": "Shark",
    "cm-outdoor": "Outdoor Area",
}

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
    "african-elephant": ("🐘", ["big", "outdoor", "wow"], "Biggest land animal — look at that trunk."),
    "koala": ("🐨", ["climb", "outdoor"], "Sleepy eucalyptus eater — look twice."),
    "giant-panda": ("🐼", ["climb", "outdoor"], "Black-and-white bamboo eater."),
    "shark": ("🦈", ["water"], "Big fin in the water — watch the swim."),
    "freshwater-fish": ("🐟", ["water"], "River and lake fish — look for a flash of color."),
}


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


def js_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def js_str_array(values: list[str], indent: str = "      ") -> str:
    inner = ",\n".join(f'{indent}{js_str(v)}' for v in values)
    return "[\n" + inner + "\n    ]"


def js_display_names(names: dict[str, str]) -> str:
    if not names:
        return ""
    inner = ",\n".join(f'      {js_str(k)}: {js_str(v)}' for k, v in names.items())
    return "{\n" + inner + ",\n    }"


def js_treasure(lines: list[str]) -> str:
    rows = []
    for i, text in enumerate(lines, 1):
        rows.append(f'      {{ id: "th{i}", text: {js_str(text)} }}')
    return "[\n" + ",\n".join(rows) + "\n    ]"


def _venue_block_span(text: str, slug: str) -> tuple[int, int]:
    key = f'  "{slug}": {{'
    start = text.index(key)
    i = start + len(key) - 1
    depth = 0
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    raise ValueError(f"unclosed catalog block for {slug}")


_FIELD_END = r"(?=\n    [a-zA-Z]|\n  \})"


def _replace_or_insert_field(block: str, field: str, value: str) -> str:
    pattern = re.compile(rf"(    {re.escape(field)}: )[\s\S]*?{_FIELD_END}")
    if pattern.search(block):
        return pattern.sub(rf"\g<1>{value},", block, count=1)
    anchor = re.search(r"\n    (featuredAnimalIds|animalIds):", block)
    if not anchor:
        raise ValueError(f"cannot insert {field}")
    return block[: anchor.start()] + f"\n    {field}: {value}," + block[anchor.start() :]


def _drop_field(block: str, field: str) -> str:
    return re.sub(rf"\n    {re.escape(field)}: [\s\S]*?{_FIELD_END}", "", block, count=1)


def patch_catalog(
    slug: str,
    *,
    blurb: str,
    animal_ids: list[str],
    featured_ids: list[str],
    display_names: dict[str, str],
    treasure: list[str],
    last_verified: str | None,
) -> None:
    text = CATALOG.read_text(encoding="utf-8")
    start, end = _venue_block_span(text, slug)
    block = text[start:end]
    block = _replace_or_insert_field(block, "blurb", js_str(blurb))
    if last_verified:
        block = _replace_or_insert_field(block, "lastVerified", js_str(last_verified))
    else:
        block = _drop_field(block, "lastVerified")
    if display_names:
        block = _replace_or_insert_field(block, "itemDisplayNames", js_display_names(display_names))
    else:
        block = _drop_field(block, "itemDisplayNames")
    block = _replace_or_insert_field(block, "featuredAnimalIds", js_str_array(featured_ids))
    block = _replace_or_insert_field(block, "animalIds", js_str_array(animal_ids))
    block = _replace_or_insert_field(block, "treasureHunt", js_treasure(treasure))
    block = _replace_or_insert_field(block, "updated", js_str("2026-08-23"))
    CATALOG.write_text(text[:start] + block + text[end:], encoding="utf-8")


def patch_venue(slug: str, **fields) -> None:
    path = VENUES / f"{slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(fields)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mark_starter(slug: str) -> None:
    path = VENUES / f"{slug}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data.pop("last_verified", None)
    data.pop("last_presence_audit", None)
    data["status"] = "partial"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def apply_kit(
    slug: str,
    *,
    verified: bool,
    tagline: str,
    items: list[dict],
    bans: list[dict],
    sources: list[str],
    notes: str,
    hunt_tag: str,
    hunt_finds: list[str],
    hunt_challenges: list[tuple[str, str]],
    display_names: dict[str, str],
    treasure: list[str],
) -> None:
    cids = [it["catalog_id"] for it in items]
    route = [it["id"] for it in items[:3]]
    featured = cids[:6]
    fields = {
        "tagline": tagline,
        "items": items,
        "content_mode": "curated",
        "research_notes": notes,
        "list_confidence": "audited" if verified else "partial",
        "do_not_list": bans,
        "route_90m": route,
        "presence_sources": sources,
        "bonus_hunt": hunt(hunt_tag, hunt_finds, hunt_challenges, sources[:2]),
        "verified_by": "research",
    }
    if verified:
        fields["last_verified"] = "2026-08-23"
        fields["last_presence_audit"] = "2026-08-23"
        fields["status"] = "verified"
    else:
        fields["last_verified"] = None
    patch_venue(slug, **fields)
    if not verified:
        mark_starter(slug)
    patch_catalog(
        slug,
        blurb=tagline,
        animal_ids=cids,
        featured_ids=featured,
        display_names=display_names,
        treasure=treasure,
        last_verified="2026-08-23" if verified else None,
    )


def main() -> None:
    apply_kit(
        "london-zoo",
        verified=True,
        tagline="Gorilla Kingdom and Tiger Territory first, then a Rainforest Life sloth — Humboldt penguins, not African.",
        items=[
            item("western-lowland-gorilla", zone="Gorilla Kingdom", one="Gorilla Kingdom troop — who looks in charge?", core=True),
            item("sumatran-tiger", zone="Tiger Territory", one="Tiger Territory — orange stripes in the trees.", core=True),
            item("two-toed-sloth", zone="Rainforest Life", one="Linne's two-toed sloth — hang and look twice.", core=True),
            item("reticulated-giraffe", zone="Into Africa", one="Into Africa giraffe — look up from the path.", core=True, label="Giraffe", note="Official animals page: Giraffe (Giraffa camelopardalis). Soft Giraffe."),
            item("zebra", zone="Into Africa", one="Chapman's zebra — every stripe set is unique.", core=True, label="Zebra", note="Official: Chapman's zebra / plains zebra."),
            item("warthog", zone="Into Africa", one="Warthog — snout, tusks, and a trot.", core=True),
            item("galapagos-tortoise", zone="Giants of the Galápagos", one="Galápagos tortoise — mid-step or statue?", core=False),
            item("ring-tailed-lemur", zone="In with the Lemurs", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("asian-small-clawed-otter", zone="Animals", one="Asian short-clawed otter — smallest otter, biggest splash.", core=False, note="Official animals page: Asian short-clawed otter (Aonyx cinerea)."),
        ],
        bans=[
            ban("african-elephant", "Official animals index: elephants live at Whipsnade Zoo, not London."),
            ban("red-panda", "Official animals index: red pandas live at Whipsnade Zoo."),
            ban("chimpanzee", "Official gorilla page: chimps are at Whipsnade Zoo."),
            ban("african-lion", "Official: Asiatic lion (Panthera leo persica) at Land of the Lions."),
            ban("nile-hippo", "Official: pygmy hippo at Into Africa, not Nile / common hippo."),
            ban("african-penguin", "Official Penguin Beach: Humboldt penguin (Spheniscus humboldti)."),
            ban("caribbean-flamingo", "Official: Greater flamingo (Phoenicopterus roseus), not Caribbean/American."),
            ban("cheetah", "Not on the official animals / habitats pages reviewed."),
        ],
        sources=[
            "https://www.londonzoo.org/whats-here/animals",
            "https://www.londonzoo.org/whats-here/habitats",
            "https://www.londonzoo.org/whats-here/animals/western-lowland-gorilla",
            "https://www.londonzoo.org/whats-here/animals/sumatran-tiger",
            "https://www.londonzoo.org/whats-here/habitats/penguin-beach",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (londonzoo.org animals + habitats). Asiatic lion / Humboldt penguin / pygmy hippo dropped as false labels.",
        hunt_tag="London bonus · Gorilla Kingdom + Tiger Territory + Rainforest Life",
        hunt_finds=["reticulated_giraffe", "zebra", "warthog", "galapagos_tortoise", "ring_tailed_lemur", "asian_small_clawed_otter"],
        hunt_challenges=[
            ("lon_gorilla", "Gorilla Kingdom: who looks calmest?"),
            ("lon_tiger", "Tiger Territory: count stripe clusters on one shoulder."),
            ("lon_sloth", "Rainforest Life sloth: mid-reach or statue-still?"),
            ("lon_giraffe", "Into Africa giraffe: count the spots you can see on one neck."),
        ],
        display_names={
            "western-lowland-gorilla": "Gorilla Kingdom gorilla",
            "sumatran-tiger": "Tiger Territory tiger",
            "two-toed-sloth": "Rainforest Life sloth",
            "reticulated-giraffe": "Into Africa giraffe",
            "zebra": "Chapman's zebra",
            "warthog": "London warthog",
            "galapagos-tortoise": "Giants of the Galápagos tortoise",
            "ring-tailed-lemur": "In with the Lemurs lemur",
            "asian-small-clawed-otter": "London otter",
        },
        treasure=[
            "Find the Gorilla Kingdom troop",
            "Spot Sumatran tiger stripes in Tiger Territory",
            "Hang-and-look-twice at a Rainforest Life sloth",
            "Look up at an Into Africa giraffe",
            "Draw one Chapman's zebra stripe set in the air",
            "Find a warthog trot or a still stare",
            "Find a Galápagos tortoise mid-step or statue-still",
            "Pick a London Zoo favorite — draw it later",
        ],
    )

    apply_kit(
        "edinburgh-zoo",
        verified=True,
        tagline="Only UK Queensland koalas, then Budongo chimps and a Sumatran tiger — king/gentoo penguins, not African.",
        items=[
            item("koala", zone="Koala Territory", one="Queensland koala — only ones in the UK. Look twice in the trees.", core=True),
            item("chimpanzee", zone="Budongo Trail", one="Budongo Trail chimps — hands used like tools.", core=True),
            item("sumatran-tiger", zone="Tigers", one="Sumatran tiger — Dharma and Sialang in the trees.", core=True),
            item("reticulated-giraffe", zone="Giraffes", one="Nubian giraffe — look up from the path.", core=True, label="Giraffe", note="Official inhabitant page: Nubian giraffe. Soft Giraffe."),
            item("cheetah", zone="Animals", one="Cheetah Billy — tear marks, not a lion mane.", core=True),
            item("red-panda", zone="Animals", one="Red panda Bruce — rusty and tree-high.", core=True),
            item("asian-small-clawed-otter", zone="Animals", one="Asian small-clawed otter — smallest otter, biggest splash.", core=False),
            item("ring-tailed-lemur", zone="Animals", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("zebra", zone="Animals", one="Grevy's zebra — every stripe set is unique.", core=False, label="Zebra", note="Official: Grevy's zebra."),
            item("two-toed-sloth", zone="Animals", one="Linne's two-toed sloth — hang and look twice.", core=False),
        ],
        bans=[
            ban("african-penguin", "Official colony is gentoo, king, and Northern rockhopper — not African."),
            ban("african-lion", "Official inhabitant page: Asiatic lion (Jay and Bindee)."),
            ban("nile-hippo", "Official: pygmy hippo (Otto, Gloria, Piper), not Nile / common hippo."),
            ban("caribbean-flamingo", "Official: Chilean flamingo, not Caribbean/American."),
            ban("western-lowland-gorilla", "No official gorilla inhabitant page (gorilla slugs 404)."),
            ban("giant-panda", "Giant panda inhabitant page 404; current panda on site is the red panda."),
            ban("african-elephant", "Not on official inhabitant pages reviewed."),
        ],
        sources=[
            "https://www.edinburghzoo.org.uk/animals",
            "https://www.edinburghzoo.org.uk/animals/animal-inhabitants/queensland-koala",
            "https://www.edinburghzoo.org.uk/animals/animal-inhabitants/chimpanzee",
            "https://www.edinburghzoo.org.uk/animals/animal-inhabitants/sumatran-tiger",
            "https://www.edinburghzoo.org.uk/animals/webcams",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (edinburghzoo.org.uk inhabitant pages). Famous penguin parade is king/gentoo/rockhopper — no published penguin card fits.",
        hunt_tag="Edinburgh bonus · koalas + Budongo + tigers",
        hunt_finds=["reticulated_giraffe", "cheetah", "red_panda", "asian_small_clawed_otter", "ring_tailed_lemur", "zebra"],
        hunt_challenges=[
            ("edi_koala", "Queensland koala: eyes open or a daytime nap?"),
            ("edi_chimp", "Budongo Trail: spot hands used like tools."),
            ("edi_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
            ("edi_panda", "Red panda: climb or curl-up?"),
        ],
        display_names={
            "koala": "Queensland koala",
            "chimpanzee": "Budongo chimpanzee",
            "sumatran-tiger": "Edinburgh Sumatran tiger",
            "reticulated-giraffe": "Nubian giraffe",
            "cheetah": "Edinburgh cheetah",
            "red-panda": "Edinburgh red panda",
            "asian-small-clawed-otter": "Edinburgh otter",
            "ring-tailed-lemur": "Edinburgh lemur",
            "zebra": "Grevy's zebra",
            "two-toed-sloth": "Edinburgh sloth",
        },
        treasure=[
            "Find a Queensland koala in the trees",
            "Watch Budongo chimps use their hands",
            "Find Sumatran tiger stripes",
            "Look up at a Nubian giraffe",
            "Spot cheetah tear marks — not a mane",
            "Find a rusty red panda",
            "Watch Asian small-clawed otters splash",
            "Pick an Edinburgh favorite — draw it later",
        ],
    )

    apply_kit(
        "dublin-zoo",
        verified=True,
        tagline="Orangutan Forest first, then Gorilla Rainforest and a common hippo — Asian elephants and Amur tigers.",
        items=[
            item("orangutan", zone="Orangutan Forest", one="Northwest Bornean orangutan — long arms in the trees.", core=True),
            item("western-lowland-gorilla", zone="Gorilla Rainforest", one="Gorilla Rainforest family — who looks in charge?", core=True),
            item("nile-hippo", zone="African Plains", one="Common hippopotamus Imani — watch the water window.", core=True, label="Hippo", note="Official encyclopedia: Common hippopotamus (Hippopotamus amphibius). Soft Hippo."),
            item("chimpanzee", zone="African Plains", one="Western chimpanzee — beside Gorilla Rainforest.", core=True),
            item("reticulated-giraffe", zone="African Savanna", one="Nubian giraffe herd — look up from the path.", core=True, label="Giraffe", note="Official: Nubian giraffe. Soft Giraffe."),
            item("zebra", zone="African Savanna", one="Grant's zebra with the giraffes.", core=True, label="Zebra", note="Official: Grant's zebra."),
            item("ostrich", zone="African Savanna", one="Red-necked ostrich — look at those legs.", core=False),
            item("red-panda", zone="Himalayan Hills", one="Red panda — rusty and tree-high.", core=False),
            item("two-toed-sloth", zone="Rainforest House", one="Linne's two-toed sloth — hang and look twice.", core=False),
            item("cheetah", zone="African Plains", one="Northeast African cheetah — tear marks, not a mane.", core=False),
        ],
        bans=[
            ban("african-elephant", "Official encyclopedia: Asian elephant at Kaziranga Forest Trail."),
            ban("african-lion", "Official: Asian lion (Panthera leo persica) in Asian Forests."),
            ban("sumatran-tiger", "Official: Amur tiger (Panthera tigris altaica) in Asian Forests."),
            ban("african-penguin", "Official: Humboldt penguin beside Sea Lion Cove."),
            ban("caribbean-flamingo", "Official Flamingo Lagoon: Chilean flamingo."),
            ban("galapagos-tortoise", "Official tortoise is African spurred tortoise, not Galápagos."),
        ],
        sources=[
            "https://www.dublinzoo.ie/animals/",
            "https://www.dublinzoo.ie/plan-your-visit/zoo-habitats/",
            "https://www.dublinzoo.ie/animals/western-lowland-gorilla/",
            "https://www.dublinzoo.ie/animals/bornean-orangutan/",
            "https://www.dublinzoo.ie/animals/common-hippopotamus/",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (dublinzoo.ie Animal Encyclopedia + habitats).",
        hunt_tag="Dublin bonus · Orangutan Forest + Gorilla Rainforest + African Plains",
        hunt_finds=["chimpanzee", "reticulated_giraffe", "zebra", "ostrich", "red_panda", "two_toed_sloth"],
        hunt_challenges=[
            ("dub_orang", "Orangutan Forest: hands or feet doing the clever bit?"),
            ("dub_gorilla", "Gorilla Rainforest: who looks calmest?"),
            ("dub_hippo", "African Plains hippo: underwater, mud, or bank?"),
            ("dub_chimp", "Western chimps: spot hands used like tools."),
        ],
        display_names={
            "orangutan": "Orangutan Forest orangutan",
            "western-lowland-gorilla": "Gorilla Rainforest gorilla",
            "nile-hippo": "African Plains hippo",
            "chimpanzee": "Dublin chimpanzee",
            "reticulated-giraffe": "Nubian giraffe",
            "zebra": "Grant's zebra",
            "ostrich": "Red-necked ostrich",
            "red-panda": "Himalayan Hills red panda",
            "two-toed-sloth": "Rainforest House sloth",
            "cheetah": "Dublin cheetah",
        },
        treasure=[
            "Find orangutan long arms in Orangutan Forest",
            "Watch the Gorilla Rainforest family",
            "Watch the common hippo at the water window",
            "Watch chimps use their hands like tools",
            "Look up at a Nubian giraffe",
            "Draw one Grant's zebra stripe set in the air",
            "Find a rusty red panda at Himalayan Hills",
            "Pick a Dublin favorite — draw it later",
        ],
    )

    apply_kit(
        "toronto-zoo",
        verified=True,
        tagline="Rainforest gorillas first, then African penguins and American flamingos — Amur tigers, not Sumatran.",
        items=[
            item("western-lowland-gorilla", zone="African Rainforest Pavilion", one="Western lowland gorilla — who looks in charge?", core=True),
            item("african-penguin", zone="Africa Savanna", one="African penguin — waddle, then zoom in the water.", core=True),
            item("caribbean-flamingo", zone="Americas Outdoor", one="American flamingo flock at the Mayan Temple Ruins.", core=True, label="Flamingo", note="Official: American flamingo (Phoenicopterus ruber). Soft Flamingo."),
            item("reticulated-giraffe", zone="Africa Savanna", one="Masai giraffe — look up from the path.", core=True, label="Giraffe", note="Official fact sheet: Masai giraffe. Soft Giraffe."),
            item("nile-hippo", zone="Africa Savanna", one="River hippopotamus — watch the water.", core=True, label="Hippo", note="Official: River hippopotamus (Hippopotamus amphibius). Soft Hippo. Pygmy hippo is a separate Rainforest animal."),
            item("african-lion", zone="Africa Savanna", one="African lion pride — listen for a roar.", core=True),
            item("cheetah", zone="Africa Savanna", one="Cheetah — tear marks, not a lion mane.", core=False),
            item("orangutan", zone="Indo-Malaya Pavilion", one="Sumatran orangutan — long arms in the trees.", core=False),
            item("two-toed-sloth", zone="Americas Pavilion", one="Two-toed sloth — hang and look twice.", core=False),
            item("red-panda", zone="Africa Savanna", one="Red panda — rusty and tree-high.", core=False),
        ],
        bans=[
            ban("african-elephant", "No elephant on official region inventories; African elephant fact sheet 404."),
            ban("giant-panda", "Not on official region lists; giant panda fact sheet 404."),
            ban("sumatran-tiger", "Official Eurasia Wilds tiger is Amur tiger."),
            ban("chimpanzee", "Not on official region lists; chimpanzee fact sheet 404."),
            ban("koala", "Not on the Australasia list."),
            ban("galapagos-tortoise", "Official tortoise is Aldabra (Rainforest Pavilion), not Galápagos."),
            ban("asian-small-clawed-otter", "Official otter is North American river otter (Americas)."),
        ],
        sources=[
            "https://www.torontozoo.com/animals",
            "https://www.torontozoo.com/animals/africa",
            "https://www.torontozoo.com/animals/americas",
            "https://www.torontozoo.com/animals/indo-malaya",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (torontozoo.com region inventories). American flamingo maps to the Caribbean card.",
        hunt_tag="Toronto bonus · Rainforest Pavilion + Africa Savanna + Americas",
        hunt_finds=["reticulated_giraffe", "nile_hippo", "african_lion", "cheetah", "orangutan", "two_toed_sloth"],
        hunt_challenges=[
            ("tor_gorilla", "Rainforest Pavilion: who looks calmest in the gorilla family?"),
            ("tor_penguin", "African penguin: watch one bird enter or leave the water."),
            ("tor_flam", "American flamingos: more than half on one leg?"),
            ("tor_hippo", "River hippo: underwater, mud, or bank?"),
        ],
        display_names={
            "western-lowland-gorilla": "Rainforest Pavilion gorilla",
            "african-penguin": "Toronto African penguin",
            "caribbean-flamingo": "American flamingo",
            "reticulated-giraffe": "Masai giraffe",
            "nile-hippo": "River hippo",
            "african-lion": "Savanna lion",
            "cheetah": "Toronto cheetah",
            "orangutan": "Indo-Malaya orangutan",
            "two-toed-sloth": "Americas sloth",
            "red-panda": "Toronto red panda",
        },
        treasure=[
            "Find the Rainforest Pavilion gorilla family",
            "Watch an African penguin zoom underwater",
            "Count American flamingos on one leg",
            "Look up at a Masai giraffe",
            "Watch the river hippo in the water",
            "Hear an African lion — or wait quietly",
            "Find orangutan long arms in Indo-Malaya",
            "Pick a Toronto favorite — draw it later",
        ],
    )

    apply_kit(
        "calgary-zoo",
        verified=True,
        tagline="Destination Africa gorillas and hippos, then Exploration Asia red pandas — Humboldt penguins, not African.",
        items=[
            item("western-lowland-gorilla", zone="Destination Africa", one="Western lowland gorilla — who looks in charge?", core=True),
            item("nile-hippo", zone="Destination Africa", one="Hippopotamus — world's third-largest land mammal in the water.", core=True, label="Hippo", note="Official hippo page describes common/Nile hippo size and rivers, not pygmy."),
            item("red-panda", zone="Exploration Asia", one="Red panda — rusty and tree-high.", core=True),
            item("african-lion", zone="Destination Africa", one="African lion pride — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="Destination Africa", one="Giraffes Amani, Nabo, and Moshi — look up from the path.", core=True, label="Giraffe", note="Official Destination Africa: Giraffes. Soft Giraffe."),
            item("zebra", zone="Destination Africa", one="Hartmann's mountain zebra — every stripe set is unique.", core=True, label="Zebra", note="Official: Hartmann's mountain zebras."),
            item("ring-tailed-lemur", zone="Land of Lemurs", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("ostrich", zone="Destination Africa", one="Southern ostrich — look at those legs.", core=False),
        ],
        bans=[
            ban("sumatran-tiger", "Official mammals list: Amur tigers."),
            ban("african-penguin", "Penguin Plunge: Humboldt, gentoo, rockhopper, and king — not African."),
            ban("caribbean-flamingo", "Official birds list: Chilean flamingos."),
            ban("asian-small-clawed-otter", "Official otter is North American river otter."),
            ban("african-elephant", "Not on the official mammals directory."),
            ban("giant-panda", "Not on the official mammals directory (red pandas only)."),
            ban("galapagos-tortoise", "Destination Africa lists Egyptian / leopard tortoises, not Galápagos."),
        ],
        sources=[
            "https://www.calgaryzoo.com/care-conservation/our-animals/mammals/",
            "https://www.calgaryzoo.com/plan-your-visit/animal-zones/destination-africa/",
            "https://www.calgaryzoo.com/plan-your-visit/animal-zones/penguin-plunge/",
            "https://www.calgaryzoo.com/plan-your-visit/animal-zones/exploration-asia/red-pandas/",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (calgaryzoo.com mammals + Destination Africa + Penguin Plunge).",
        hunt_tag="Calgary bonus · Destination Africa + Exploration Asia",
        hunt_finds=["african_lion", "reticulated_giraffe", "zebra", "ring_tailed_lemur", "ostrich"],
        hunt_challenges=[
            ("cal_gorilla", "Destination Africa: who looks calmest in the gorilla family?"),
            ("cal_hippo", "Hippo: underwater, mud, or bank?"),
            ("cal_panda", "Red panda: climb or curl-up?"),
            ("cal_lion", "African lions: roar or a quiet pride?"),
        ],
        display_names={
            "western-lowland-gorilla": "Destination Africa gorilla",
            "nile-hippo": "Calgary hippo",
            "red-panda": "Exploration Asia red panda",
            "african-lion": "Calgary lion",
            "reticulated-giraffe": "Destination Africa giraffe",
            "zebra": "Hartmann's zebra",
            "ring-tailed-lemur": "Land of Lemurs lemur",
            "ostrich": "Southern ostrich",
        },
        treasure=[
            "Find the Destination Africa gorilla family",
            "Watch the hippo in the water",
            "Find a rusty red panda at Exploration Asia",
            "Hear an African lion — or wait quietly",
            "Look up at a Destination Africa giraffe",
            "Draw one Hartmann's zebra stripe set in the air",
            "Find a Land of Lemurs striped tail",
            "Pick a Calgary favorite — draw it later",
        ],
    )

    apply_kit(
        "melbourne-zoo",
        verified=False,
        tagline="Starter list: Australian Bush koalas, then Gorilla Rainforest and Forest of Wonder orangutans.",
        items=[
            item("koala", zone="Australian Bush", one="Southern koala — sleepy eucalyptus eater.", core=True),
            item("western-lowland-gorilla", zone="Gorilla Rainforest", one="Western lowland gorilla — who looks in charge?", core=True),
            item("orangutan", zone="Forest of Wonder", one="Orangutan — long arms in the Sumatran rainforest trail.", core=True),
            item("sumatran-tiger", zone="Forest of Wonder", one="Sumatran tiger — orange stripes in Lion Gorge / Forest of Wonder.", core=True),
            item("african-lion", zone="Lion Gorge", one="African lion — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="Main Trail", one="Main Trail giraffe — look up from the path.", core=True, label="Giraffe", note="Official habitat pages list Giraffe. Soft Giraffe."),
            item("red-panda", zone="Main Trail", one="Red panda — rusty and tree-high.", core=False),
            item("ring-tailed-lemur", zone="Gorilla Rainforest", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("asian-small-clawed-otter", zone="Forest of Wonder", one="Asian small-clawed otter — smallest otter, biggest splash.", core=False),
            item("shark", zone="Wild Sea", one="Port Jackson shark — watch the swim.", core=False, note="Official Wild Sea habitat names Port Jackson Shark."),
        ],
        bans=[
            ban("african-elephant", "Official Trail of the Elephants: Asian elephants."),
            ban("nile-hippo", "Official Gorilla Rainforest: pygmy hippopotamus."),
            ban("african-penguin", "Official Wild Sea: Little Penguin, not African."),
        ],
        sources=[
            "https://www.zoo.org.au/melbourne/animals-and-habitats/",
            "https://www.zoo.org.au/melbourne/animals-and-habitats/gorilla-rainforest/",
            "https://www.zoo.org.au/melbourne/animals-and-habitats/forest-of-wonder/",
            "https://www.zoo.org.au/melbourne/animals-and-habitats/australian-bush/",
            "https://www.zoo.org.au/melbourne/animals-and-habitats/wild-sea/",
        ],
        notes="[2026-08-23] Wave 3a: official habitat pages only; no complete species inventory. No invented verify date. Werribee Open Range animals omitted.",
        hunt_tag="Melbourne bonus · koalas + gorillas + Forest of Wonder",
        hunt_finds=["sumatran_tiger", "african_lion", "reticulated_giraffe", "red_panda", "ring_tailed_lemur", "asian_small_clawed_otter"],
        hunt_challenges=[
            ("mel_koala", "Australian Bush koala: eyes open or a daytime nap?"),
            ("mel_gorilla", "Gorilla Rainforest: who looks calmest?"),
            ("mel_orang", "Forest of Wonder orangutan: hands or feet doing the clever bit?"),
            ("mel_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
        ],
        display_names={
            "koala": "Australian Bush koala",
            "western-lowland-gorilla": "Gorilla Rainforest gorilla",
            "orangutan": "Forest of Wonder orangutan",
            "sumatran-tiger": "Melbourne Sumatran tiger",
            "african-lion": "Lion Gorge lion",
            "reticulated-giraffe": "Main Trail giraffe",
            "red-panda": "Main Trail red panda",
            "ring-tailed-lemur": "Melbourne lemur",
            "asian-small-clawed-otter": "Forest of Wonder otter",
            "shark": "Port Jackson shark",
        },
        treasure=[
            "Find a sleepy Australian Bush koala",
            "Watch the Gorilla Rainforest family",
            "Find orangutan long arms in Forest of Wonder",
            "Find Sumatran tiger stripes",
            "Hear a Lion Gorge roar — or wait quietly",
            "Look up at a Main Trail giraffe",
            "Watch Asian small-clawed otters splash",
            "Pick a Melbourne favorite — draw it later",
        ],
    )

    apply_kit(
        "taronga-zoo",
        verified=False,
        tagline="Starter Sydney list: koala country, Tiger Trek, then chimps — little penguins, not African.",
        items=[
            item("koala", zone="Nura Diya / Koala Country", one="Koala — look up in the eucalyptus.", core=True),
            item("sumatran-tiger", zone="Tiger Trek", one="Tiger Trek Sumatran tiger — orange stripes in the trees.", core=True),
            item("chimpanzee", zone="Our animals", one="Chimpanzee — hands used like tools.", core=True),
            item("western-lowland-gorilla", zone="Our animals", one="Western-lowland gorilla — who looks in charge?", core=True),
            item("african-lion", zone="African Savannah", one="African lion — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="African Savannah", one="African Savannah giraffe — look up from the path.", core=True, label="Giraffe", note="Official animals page: Giraffe. Soft Giraffe."),
            item("zebra", zone="African Savannah", one="Savannah zebra — pick one stripe set and draw it in the air.", core=False),
            item("red-panda", zone="Our animals", one="Red panda — rusty and tree-high.", core=False),
            item("ring-tailed-lemur", zone="Our animals", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
        ],
        bans=[
            ban("nile-hippo", "Official homepage / species page: pygmy hippopotamus on Rainforest Trail."),
            ban("african-penguin", "Great Southern Oceans: Little Penguin and Fiordland Penguin, not African."),
            ban("african-elephant", "No elephant on current Sydney featured / habitats pages (Western Plains is a different zoo)."),
        ],
        sources=[
            "https://www.taronga.org.au/sydney-zoo",
            "https://www.taronga.org.au/wildlife-and-conservation/animals/sydney",
            "https://www.taronga.org.au/sydney-zoo/habitats-and-trails",
            "https://www.taronga.org.au/sydney-zoo/habitats-and-trails/nura-diya-australia",
        ],
        notes="[2026-08-23] Wave 3a: official Sydney animals + habitats only (not Western Plains / Dubbo). Site says 350+ species; full inventory is JS-partial. No invented verify date.",
        hunt_tag="Taronga bonus · koala + Tiger Trek + savannah (Sydney)",
        hunt_finds=["western_lowland_gorilla", "african_lion", "reticulated_giraffe", "zebra", "red_panda", "ring_tailed_lemur"],
        hunt_challenges=[
            ("tar_koala", "Koala Country: eyes open or a daytime nap?"),
            ("tar_tiger", "Tiger Trek: how long until you spot stripes?"),
            ("tar_chimp", "Chimps: spot hands used like tools."),
            ("tar_giraffe", "Savannah giraffe: count the spots you can see on one neck."),
        ],
        display_names={
            "koala": "Taronga koala",
            "sumatran-tiger": "Tiger Trek tiger",
            "chimpanzee": "Taronga chimpanzee",
            "western-lowland-gorilla": "Taronga gorilla",
            "african-lion": "Savannah lion",
            "reticulated-giraffe": "Taronga giraffe",
            "zebra": "Savannah zebra",
            "red-panda": "Taronga red panda",
            "ring-tailed-lemur": "Taronga lemur",
        },
        treasure=[
            "Find a koala in Nura Diya / Koala Country",
            "Spot Sumatran tiger stripes on Tiger Trek",
            "Watch chimps use their hands like tools",
            "Find the western-lowland gorilla family",
            "Hear an African lion — or wait quietly",
            "Look up at an African Savannah giraffe",
            "Find a rusty red panda",
            "Pick a Taronga Sydney favorite — draw it later",
        ],
    )

    apply_kit(
        "perth-zoo",
        verified=False,
        tagline="Starter list: Australian Bushwalk koala, then a Sumatran orangutan and Galápagos tortoise.",
        items=[
            item("koala", zone="Australian Bushwalk", one="Koala — sleepy eucalyptus eater.", core=True),
            item("orangutan", zone="Animals", one="Sumatran orangutan — long arms in the trees.", core=True),
            item("galapagos-tortoise", zone="Animals", one="Galápagos tortoise — mid-step or statue?", core=True),
            item("african-lion", zone="African Savannah", one="African lion — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="Animals", one="Giraffe — look up from the path.", core=True, label="Giraffe", note="Official fact sheet: Giraffe (Giraffa camelopardalis). Soft Giraffe."),
            item("zebra", zone="Animals", one="Plains zebra — pick one stripe set and draw it in the air.", core=True, label="Zebra", note="Official animals index: Plains Zebra."),
            item("asian-small-clawed-otter", zone="Animals", one="Asian small-clawed otter — smallest otter, biggest splash.", core=False),
            item("sumatran-tiger", zone="Animals", one="Sumatran tiger — official FAQ names the species they keep.", core=False),
        ],
        bans=[
            ban("african-penguin", "Official Penguin Plunge page is Little Penguin, not African."),
            ban("nile-hippo", "Official FAQ: the collection does not include hippopotamus."),
            ban("african-elephant", "Official articles: former Asian elephants; Perth Zoo is no longer home to elephants."),
        ],
        sources=[
            "https://perthzoo.wa.gov.au/animals",
            "https://perthzoo.wa.gov.au/animal/koala",
            "https://perthzoo.wa.gov.au/animal/sumatran-orangutan",
            "https://perthzoo.wa.gov.au/animal/african-lion",
            "https://perthzoo.wa.gov.au/about-perth-zoo/frequently-asked-questions",
        ],
        notes="[2026-08-23] Wave 3a: official perthzoo.wa.gov.au animal fact sheets + FAQ. Full 156-species index was not fully downloaded here. No invented verify date.",
        hunt_tag="Perth bonus · koala + orangutan + tortoise",
        hunt_finds=["african_lion", "reticulated_giraffe", "zebra", "asian_small_clawed_otter", "sumatran_tiger"],
        hunt_challenges=[
            ("per_koala", "Australian Bushwalk koala: eyes open or a daytime nap?"),
            ("per_orang", "Sumatran orangutan: hands or feet doing the clever bit?"),
            ("per_tort", "Galápagos tortoise: mid-step or statue-still?"),
            ("per_lion", "African Savannah: roar or a quiet pride?"),
        ],
        display_names={
            "koala": "Bushwalk koala",
            "orangutan": "Sumatran orangutan",
            "galapagos-tortoise": "Perth Galápagos tortoise",
            "african-lion": "Savannah lion",
            "reticulated-giraffe": "Perth giraffe",
            "zebra": "Plains zebra",
            "asian-small-clawed-otter": "Perth otter",
            "sumatran-tiger": "Perth Sumatran tiger",
        },
        treasure=[
            "Find a koala on Australian Bushwalk",
            "Find orangutan long arms in the trees",
            "Find a Galápagos tortoise mid-step or statue-still",
            "Hear an African lion — or wait quietly",
            "Look up at a giraffe",
            "Draw one plains zebra stripe set in the air",
            "Watch Asian small-clawed otters splash",
            "Pick a Perth favorite — draw it later",
        ],
    )

    apply_kit(
        "adelaide-zoo",
        verified=True,
        tagline="Giant pandas Xing Qiu and Yi Lan first, then a southern koala and Sumatran orangutan.",
        items=[
            item("giant-panda", zone="Pandas", one="Giant pandas Xing Qiu and Yi Lan — bamboo first.", core=True),
            item("koala", zone="Animals", one="Southern koala — sleepy eucalyptus eater.", core=True),
            item("orangutan", zone="Animals", one="Sumatran orangutan — long arms in the trees.", core=True),
            item("sumatran-tiger", zone="Animals", one="Sumatran tiger — orange stripes in the trees.", core=True),
            item("red-panda", zone="Animals", one="Red panda — rusty and tree-high.", core=True),
            item("reticulated-giraffe", zone="Animals", one="Giraffe Kimya — look up from the path.", core=True, label="Giraffe", note="Official animals page: Giraffe. Soft Giraffe."),
            item("asian-small-clawed-otter", zone="Animals", one="Asian small-clawed otter — smallest otter, biggest splash.", core=False),
            item("ring-tailed-lemur", zone="Animals", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
        ],
        bans=[
            ban("nile-hippo", "Official animals directory: Pygmy Hippo."),
            ban("african-penguin", "Official animals directory: Little Penguin."),
            ban("galapagos-tortoise", "Official: Aldabra tortoise / Western swamp tortoise, not Galápagos."),
            ban("african-lion", "Not on the Adelaide Zoo animals list (lions are at Monarto Safari Park)."),
            ban("african-elephant", "Not on the Adelaide Zoo animals list."),
            ban("western-lowland-gorilla", "Not on the Adelaide Zoo animals list."),
            ban("chimpanzee", "Not on the Adelaide Zoo animals list."),
        ],
        sources=[
            "https://www.adelaidezoo.com.au/animals/",
            "https://www.adelaidezoo.com.au/",
            "https://www.adelaidezoo.com.au/animals/giraffe/",
            "https://www.adelaidezoo.com.au/animals/asian-small-clawed-otter/",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (adelaidezoo.com.au animals A–Z). Do not import Monarto Safari Park megafauna.",
        hunt_tag="Adelaide bonus · pandas + koala + orangutan",
        hunt_finds=["sumatran_tiger", "red_panda", "reticulated_giraffe", "asian_small_clawed_otter", "ring_tailed_lemur"],
        hunt_challenges=[
            ("adl_panda", "Giant panda: bamboo busy or a full rest?"),
            ("adl_koala", "Southern koala: eyes open or a daytime nap?"),
            ("adl_orang", "Sumatran orangutan: hands or feet doing the clever bit?"),
            ("adl_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
        ],
        display_names={
            "giant-panda": "Adelaide giant panda",
            "koala": "Southern koala",
            "orangutan": "Sumatran orangutan",
            "sumatran-tiger": "Adelaide Sumatran tiger",
            "red-panda": "Adelaide red panda",
            "reticulated-giraffe": "Adelaide giraffe",
            "asian-small-clawed-otter": "Adelaide otter",
            "ring-tailed-lemur": "Adelaide lemur",
        },
        treasure=[
            "Find giant pandas Xing Qiu or Yi Lan",
            "Find a sleepy southern koala",
            "Find orangutan long arms in the trees",
            "Find Sumatran tiger stripes",
            "Find a rusty red panda",
            "Look up at giraffe Kimya",
            "Watch Asian small-clawed otters splash",
            "Pick an Adelaide favorite — draw it later",
        ],
    )

    apply_kit(
        "auckland-zoo",
        verified=True,
        tagline="Sumatran tigers first, then a named Galápagos tortoise and Bornean orangutan — elephants have left.",
        items=[
            item("sumatran-tiger", zone="Mammals", one="Sumatran tiger — Ramah, Zayana, and Cahya.", core=True),
            item("galapagos-tortoise", zone="Ectotherms", one="Named Galápagos tortoise residents — mid-step or statue?", core=True),
            item("orangutan", zone="South East Asia", one="Bornean orangutan — long arms at High Canopy.", core=True),
            item("cheetah", zone="Mammals", one="Cheetah — tear marks, not a lion mane.", core=True),
            item("african-lion", zone="Mammals", one="African lion — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="Pridelands", one="Pridelands giraffe — look up from the path.", core=True, label="Giraffe", note="Official mammals page: Giraffe. Soft Giraffe."),
            item("zebra", zone="Pridelands", one="Pridelands zebra with ostrich and giraffe.", core=False),
            item("red-panda", zone="Mammals", one="Red panda — rusty and tree-high.", core=False),
            item("asian-small-clawed-otter", zone="Mammals", one="Asian small-clawed otter — smallest otter, biggest splash.", core=False),
            item("ostrich", zone="Pridelands", one="Common ostrich — four females on Pridelands.", core=False),
        ],
        bans=[
            ban("african-elephant", "Official: Asian elephants moved November 2024; none remain at Auckland Zoo."),
            ban("african-penguin", "Official birds list: Kororā / little penguin."),
            ban("caribbean-flamingo", "Official birds list: Greater Flamingo."),
            ban("nile-hippo", "Not on the official mammals directory."),
            ban("western-lowland-gorilla", "Not on the official mammals directory."),
            ban("chimpanzee", "Not on the official mammals directory."),
            ban("koala", "Not on the official mammals directory."),
        ],
        sources=[
            "https://www.aucklandzoo.co.nz/animals",
            "https://www.aucklandzoo.co.nz/animals/mammals",
            "https://www.aucklandzoo.co.nz/animals/birds",
            "https://www.aucklandzoo.co.nz/animals/ectotherms",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (aucklandzoo.co.nz mammals + birds + ectotherms).",
        hunt_tag="Auckland bonus · tiger + tortoise + High Canopy",
        hunt_finds=["cheetah", "african_lion", "reticulated_giraffe", "zebra", "red_panda", "asian_small_clawed_otter"],
        hunt_challenges=[
            ("auk_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
            ("auk_tort", "Galápagos tortoise: mid-step or statue-still?"),
            ("auk_orang", "Bornean orangutan: hands or feet doing the clever bit?"),
            ("auk_cheetah", "Cheetah: statue score 1–10 after 20 quiet seconds."),
        ],
        display_names={
            "sumatran-tiger": "Auckland Sumatran tiger",
            "galapagos-tortoise": "Auckland Galápagos tortoise",
            "orangutan": "Bornean orangutan",
            "cheetah": "Auckland cheetah",
            "african-lion": "Auckland lion",
            "reticulated-giraffe": "Pridelands giraffe",
            "zebra": "Pridelands zebra",
            "red-panda": "Auckland red panda",
            "asian-small-clawed-otter": "Auckland otter",
            "ostrich": "Pridelands ostrich",
        },
        treasure=[
            "Find Sumatran tiger stripes",
            "Find a Galápagos tortoise mid-step or statue-still",
            "Find orangutan long arms at High Canopy",
            "Spot a cheetah — tear marks, not a mane",
            "Hear an African lion — or wait quietly",
            "Look up at a Pridelands giraffe",
            "Watch Asian small-clawed otters splash",
            "Pick an Auckland favorite — draw it later",
        ],
    )

    apply_kit(
        "wellington-zoo",
        verified=True,
        tagline="Chimpanzee troop first, then Sumatran tiger Senja and red panda Ngima — kororā, not African penguins.",
        items=[
            item("chimpanzee", zone="Meet the animals", one="Chimpanzee troop of nine — daily Chimpanzee Talk.", core=True),
            item("sumatran-tiger", zone="Meet the animals", one="Sumatran tiger Senja — orange stripes and a Tiger Talk.", core=True),
            item("red-panda", zone="Meet the animals", one="Red panda Ngima — rusty and tree-high.", core=True),
            item("african-lion", zone="Lion habitat", one="Lion brothers — listen for a roar.", core=True, label="Lion", note="Official Meet the Animals title is Lion; copy is sub-Saharan. Soft Lion."),
            item("reticulated-giraffe", zone="African Savannah", one="Giraffe herd of four — Giraffe Talk on the savannah.", core=True, label="Giraffe", note="Official: Giraffe. Soft Giraffe."),
            item("asian-small-clawed-otter", zone="Meet the animals", one="Asian small-clawed otter — first habitat and Otter Talk.", core=True),
            item("ring-tailed-lemur", zone="Meet the animals", one="Ring-tailed lemur beside Australian Neighbours.", core=False),
            item("ostrich", zone="African Savannah", one="Two female ostriches with giraffe and nyala.", core=False),
        ],
        bans=[
            ban("african-penguin", "Official Penguin Point: Little Blue Penguin (Kororā)."),
            ban("african-elephant", "Not on the official 44-animal Meet the Animals list."),
            ban("nile-hippo", "Not on the official Meet the Animals list."),
            ban("western-lowland-gorilla", "Not on the official list (gibbon is listed)."),
            ban("koala", "Not on the official list."),
            ban("orangutan", "Not on the official list."),
            ban("zebra", "Not on the official Meet the Animals list."),
        ],
        sources=[
            "https://wellingtonzoo.com/animals/meet-the-animals/",
            "https://wellingtonzoo.com/visit/plan-your-day/",
            "https://wellingtonzoo.com/",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (wellingtonzoo.com Meet the Animals, 44 animals).",
        hunt_tag="Wellington bonus · chimps + tiger Senja + red panda",
        hunt_finds=["african_lion", "reticulated_giraffe", "asian_small_clawed_otter", "ring_tailed_lemur", "ostrich"],
        hunt_challenges=[
            ("wel_chimp", "Chimps: spot hands used like tools."),
            ("wel_tiger", "Tiger Senja: count stripe clusters on one shoulder."),
            ("wel_panda", "Red panda Ngima: climb or curl-up?"),
            ("wel_otter", "Asian small-clawed otter: find the splashiest 10 seconds."),
        ],
        display_names={
            "chimpanzee": "Wellington chimpanzee",
            "sumatran-tiger": "Tiger Senja",
            "red-panda": "Red panda Ngima",
            "african-lion": "Wellington lion",
            "reticulated-giraffe": "Savannah giraffe",
            "asian-small-clawed-otter": "Wellington otter",
            "ring-tailed-lemur": "Wellington lemur",
            "ostrich": "Savannah ostrich",
        },
        treasure=[
            "Watch the chimpanzee troop of nine",
            "Find Sumatran tiger Senja's stripes",
            "Find rusty red panda Ngima",
            "Hear a lion — or wait quietly",
            "Look up at a savannah giraffe",
            "Watch Asian small-clawed otters splash",
            "Find a ring-tailed lemur’s striped tail",
            "Pick a Wellington favorite — draw it later",
        ],
    )

    apply_kit(
        "singapore-zoo",
        verified=True,
        tagline="Orangutan Island first, then a two-toed sloth and a cheetah — Malayan tigers and Asian elephants.",
        items=[
            item("orangutan", zone="Orangutan Island", one="Bornean and Sumatran orangutans — free-ranging in the trees.", core=True),
            item("two-toed-sloth", zone="Animals", one="Two-toed sloth — hang and look twice.", core=True),
            item("cheetah", zone="Animals", one="Cheetah — tear marks from eye to mouth.", core=True),
            item("african-lion", zone="Wild Africa", one="African lion pride — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="Wild Africa", one="Rothschild's giraffes Adhil and Balaji — look up from the path.", core=True, label="Giraffe", note="Official: Rothschild’s giraffes Adhil and Balaji. Soft Giraffe."),
            item("zebra", zone="Wild Africa", one="Grevy's zebra — bullseye stripe pattern on the rump.", core=True, label="Zebra", note="Official zebra copy describes Grevy's zebra."),
            item("asian-small-clawed-otter", zone="Animals", one="Asian small-clawed otter — smallest of 13 otter species.", core=False),
            item("ring-tailed-lemur", zone="Animals", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("african-penguin", zone="African Penguin Exhibit", one="African Penguin Exhibit — closed 31 Aug–30 Nov 2026 for upgrades.", core=False, note="Official Singapore Zoo homepage names the African Penguin Exhibit (temporary upgrade closure)."),
        ],
        bans=[
            ban("african-elephant", "Official Elephants of Asia: Asian elephant — slighter than African cousins."),
            ban("sumatran-tiger", "Official animals directory: Malayan tiger."),
            ban("nile-hippo", "Official animals directory: pygmy hippo."),
            ban("galapagos-tortoise", "Tortoise Shell-ter lists Aldabra, African spurred, and others — not Galápagos."),
            ban("western-lowland-gorilla", "Not on the official Singapore Zoo animals directory."),
            ban("chimpanzee", "Not on the official Singapore Zoo animals directory."),
            ban("warthog", "Official list names red river hog, not warthog."),
            ban("red-panda", "Not on the official Singapore Zoo animals directory."),
            ban("giant-panda", "Not on the official Singapore Zoo animals directory."),
        ],
        sources=[
            "https://www.mandai.com/en/singapore-zoo.html",
            "https://www.mandai.com/en/singapore-zoo/animals-and-zones.html",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (mandai.com Singapore Zoo animals & zones). Night Safari / River Wonders / Bird Paradise omitted.",
        hunt_tag="Singapore Zoo bonus · Orangutan Island + sloth + Wild Africa",
        hunt_finds=["african_lion", "reticulated_giraffe", "zebra", "asian_small_clawed_otter", "ring_tailed_lemur", "african_penguin"],
        hunt_challenges=[
            ("sg_orang", "Orangutan Island: who is highest in the trees?"),
            ("sg_sloth", "Two-toed sloth: mid-reach or statue-still?"),
            ("sg_cheetah", "Cheetah: statue score 1–10 after 20 quiet seconds."),
            ("sg_giraffe", "Rothschild’s giraffe: count the spots you can see on one neck."),
        ],
        display_names={
            "orangutan": "Orangutan Island orangutan",
            "two-toed-sloth": "Singapore sloth",
            "cheetah": "Singapore cheetah",
            "african-lion": "Wild Africa lion",
            "reticulated-giraffe": "Wild Africa giraffe",
            "zebra": "Grevy's zebra",
            "asian-small-clawed-otter": "Singapore otter",
            "ring-tailed-lemur": "Singapore lemur",
            "african-penguin": "African Penguin Exhibit",
        },
        treasure=[
            "Find free-ranging orangutans on Orangutan Island",
            "Hang-and-look-twice at a two-toed sloth",
            "Spot cheetah tear marks — not a mane",
            "Hear a Wild Africa lion — or wait quietly",
            "Look up at Rothschild’s giraffes Adhil or Balaji",
            "Draw one Grevy's zebra stripe set in the air",
            "Watch Asian small-clawed otters splash",
            "Pick a Singapore Zoo favorite — draw it later",
        ],
    )

    apply_kit(
        "paris-zoo",
        verified=False,
        tagline="Starter Vincennes list: greenhouse sloth, then a ring-tailed lemur and West African giraffe.",
        items=[
            item("two-toed-sloth", zone="Great Greenhouse", one="Linnaeus's two-toed sloth in the Amazon-Guyana greenhouse.", core=True),
            item("ring-tailed-lemur", zone="Madagascar", one="Ring-tailed lemur — striped tail in the Great Greenhouse.", core=True),
            item("reticulated-giraffe", zone="Africa biozone", one="West African giraffe — look up from the path.", core=True, label="Giraffe", note="Official Africa biozone: West African giraffe (Giraffa camelopardalis). Soft Giraffe."),
            item("african-lion", zone="Africa biozone", one="West African lion — listen for a roar.", core=True, label="Lion", note="Official: West African / northern lion (Panthera leo). Soft Lion."),
            item("zebra", zone="Africa biozone", one="Grévy's zebra — every stripe set is unique.", core=False, label="Zebra", note="Official: Grévy’s zebra."),
            item("ostrich", zone="Africa biozone", one="Ostrich — look at those legs.", core=False),
            item("freshwater-fish", zone="Great Greenhouse", one="Arapaima and red-bellied piranha — look for a flash in the water.", core=False, note="Official greenhouse names arapaima and red-bellied piranha."),
        ],
        bans=[
            ban("african-penguin", "Official Patagonia names Humboldt penguin."),
            ban("caribbean-flamingo", "Official: greater flamingo (Phoenicopterus roseus), not Caribbean/American."),
            ban("galapagos-tortoise", "Official names radiated tortoise, not Galápagos."),
            ban("african-elephant", "Not named on official biozone / discover-the-animals pages opened."),
            ban("nile-hippo", "Not named on official biozone pages opened."),
            ban("western-lowland-gorilla", "Not named on official biozone pages opened."),
            ban("sumatran-tiger", "Not named on official biozone pages opened."),
        ],
        sources=[
            "https://www.parczoologiquedeparis.fr/en/discover-the-animals",
            "https://www.parczoologiquedeparis.fr/en/biozone-africa",
            "https://www.parczoologiquedeparis.fr/en/amazon-guyana-biozone",
            "https://www.parczoologiquedeparis.fr/en/visitor-map-routes",
        ],
        notes="[2026-08-23] Wave 3a: official biozones + visitor map. Site says “some of the 270 species.” Short published-card overlap. No invented verify date. Not Thoiry / Beauval / Jardin des Plantes.",
        hunt_tag="Paris Zoo bonus · greenhouse sloth + lemur + Africa giraffe",
        hunt_finds=["african_lion", "zebra", "ostrich", "freshwater_fish"],
        hunt_challenges=[
            ("par_sloth", "Greenhouse sloth: mid-reach or statue-still?"),
            ("par_lemur", "Ring-tailed lemur: striped tail up or a long sit?"),
            ("par_giraffe", "West African giraffe: count the spots you can see on one neck."),
            ("par_lion", "West African lion: roar or a quiet pride?"),
        ],
        display_names={
            "two-toed-sloth": "Greenhouse sloth",
            "ring-tailed-lemur": "Madagascar lemur",
            "reticulated-giraffe": "West African giraffe",
            "african-lion": "West African lion",
            "zebra": "Grévy's zebra",
            "ostrich": "Paris ostrich",
            "freshwater-fish": "Greenhouse fish",
        },
        treasure=[
            "Hang-and-look-twice at a greenhouse sloth",
            "Find a Madagascar ring-tailed lemur",
            "Look up at a West African giraffe",
            "Hear a West African lion — or wait quietly",
            "Draw one Grévy's zebra stripe set in the air",
            "Look at an ostrich’s legs — biggest bird",
            "Spot a flash of greenhouse fish",
            "Pick a Paris Zoo favorite — draw it later",
        ],
    )

    apply_kit(
        "berlin-zoo",
        verified=False,
        tagline="Starter list: Germany’s only giant pandas, then gorillas and a Sumatran orangutan — Asian elephants.",
        items=[
            item("giant-panda", zone="Panda Garden", one="Giant pandas — Germany’s only giant pandas.", core=True),
            item("western-lowland-gorilla", zone="Gorilla house", one="Western lowland gorilla — Fatou and Tilla’s house.", core=True),
            item("orangutan", zone="Great apes", one="Sumatran orangutan — long arms in the trees.", core=True),
            item("chimpanzee", zone="Great apes", one="Chimpanzee play and chatter.", core=True),
            item("african-lion", zone="Cats", one="Lion — listen for a roar.", core=True, label="Lion", note="Official species page: Lion (Panthera leo). Soft Lion."),
            item("nile-hippo", zone="Hippo house", one="Hippopotamus amphibius at the Hippo house.", core=True, label="Hippo", note="Official hippo page names Hippopotamus amphibius. Pygmy hippos are listed separately."),
            item("reticulated-giraffe", zone="Antelope House", one="Rothschild giraffes at the Antelope House.", core=False, label="Giraffe", note="Official Antelope House: Rothschild giraffes. Soft Giraffe."),
            item("zebra", zone="Grounds", one="Grévy's zebra — every stripe set is unique.", core=False, label="Zebra", note="Official: Grévy’s zebra."),
            item("two-toed-sloth", zone="Animals", one="Linné's two-toed sloth — hang and look twice.", core=False),
            item("asian-small-clawed-otter", zone="Seals & penguins", one="Oriental small-clawed otter — smallest otter, biggest splash.", core=False),
        ],
        bans=[
            ban("african-elephant", "Official elephant page is Asian elephant (Elephas maximus)."),
            ban("african-penguin", "Penguin World residents are king (and rockhopper) — not African."),
            ban("caribbean-flamingo", "Official names Chilean flamingo."),
            ban("sumatran-tiger", "Official facts highlight Amur / Siberian tiger; Sumatran CMS page mixes Tierpark copy."),
            ban("warthog", "Official names Visayan warty pig, not warthog."),
        ],
        sources=[
            "https://www.zoo-berlin.de/en/explore-the-zoo/giant-panda",
            "https://www.zoo-berlin.de/en/explore-the-zoo/western-lowland-gorilla",
            "https://www.zoo-berlin.de/en/explore-the-zoo/sumatran-orangutan",
            "https://www.zoo-berlin.de/en/explore-the-zoo/asian-elephant",
            "https://www.zoo-berlin.de/en/explore-the-zoo/seals-penguins",
        ],
        notes="[2026-08-23] Wave 3a: official Zoo Berlin species pages (not Tierpark). No complete public A–Z fetched. No invented verify date.",
        hunt_tag="Berlin bonus · Panda Garden + gorilla house + orangutan",
        hunt_finds=["chimpanzee", "african_lion", "nile_hippo", "reticulated_giraffe", "zebra", "two_toed_sloth"],
        hunt_challenges=[
            ("ber_panda", "Panda Garden: bamboo busy or a full rest?"),
            ("ber_gorilla", "Gorilla house: who looks calmest?"),
            ("ber_orang", "Sumatran orangutan: hands or feet doing the clever bit?"),
            ("ber_hippo", "Hippo house: underwater, mud, or bank?"),
        ],
        display_names={
            "giant-panda": "Panda Garden panda",
            "western-lowland-gorilla": "Berlin gorilla",
            "orangutan": "Sumatran orangutan",
            "chimpanzee": "Berlin chimpanzee",
            "african-lion": "Berlin lion",
            "nile-hippo": "Hippo house hippo",
            "reticulated-giraffe": "Antelope House giraffe",
            "zebra": "Grévy's zebra",
            "two-toed-sloth": "Berlin sloth",
            "asian-small-clawed-otter": "Berlin otter",
        },
        treasure=[
            "Find Germany’s only giant pandas",
            "Watch the gorilla house family",
            "Find orangutan long arms in the trees",
            "Watch chimps use their hands like tools",
            "Hear a lion — or wait quietly",
            "Watch the Hippo house from the water",
            "Look up at a Rothschild giraffe",
            "Pick a Berlin Zoo favorite — draw it later",
        ],
    )

    apply_kit(
        "artis-zoo",
        verified=True,
        tagline="African penguins first, then a reticulated giraffe and the Gorilla House — Asian elephants.",
        items=[
            item("african-penguin", zone="Penguins", one="African penguin — new home announced August 2026.", core=True),
            item("reticulated-giraffe", zone="Explorer", one="Official reticulated giraffe — look up from the path.", core=True),
            item("western-lowland-gorilla", zone="Gorilla House", one="Gorilla House family — who looks in charge?", core=True),
            item("chimpanzee", zone="Forest House", one="Forest House chimps — hands used like tools.", core=True),
            item("african-lion", zone="Animals", one="Lion — listen for a roar.", core=True, label="Lion", note="Official explorer page: Lion (Panthera leo), not Asiatic lion."),
            item("red-panda", zone="Animals", one="Red panda — rusty and tree-high.", core=True),
            item("ring-tailed-lemur", zone="Kerbertterras", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("asian-small-clawed-otter", zone="Kerbertterras", one="Asian small-clawed otter — smallest otter, biggest splash.", core=False),
            item("two-toed-sloth", zone="Animals", one="Linne's two-toed sloth — hang and look twice.", core=False),
            item("ostrich", zone="Animals", one="Common ostrich — look at those legs.", core=False),
        ],
        bans=[
            ban("african-elephant", "Official explorer page: Asian elephant (Sanuk / Thong Thai)."),
            ban("caribbean-flamingo", "Official: Chilean flamingo."),
            ban("galapagos-tortoise", "Official: Aldabra giant tortoise."),
            ban("sumatran-tiger", "Not named on the official What to explore directory."),
            ban("nile-hippo", "Not named on the official What to explore directory."),
            ban("zebra", "Not named on the official What to explore directory."),
        ],
        sources=[
            "https://www.artis.nl/en/artis-zoo/what-to-explore-in-artis-zoo",
            "https://www.artis.nl/en/artis-zoo/what-to-explore-in-artis-zoo/african-penguin",
            "https://www.artis.nl/en/artis-zoo/what-to-explore-in-artis-zoo/reticulated-giraffe",
            "https://www.artis.nl/en/artis-zoo/what-to-explore-in-artis-zoo/asian-elephant",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (artis.nl What to explore directory).",
        hunt_tag="ARTIS bonus · African penguin + reticulated giraffe + Gorilla House",
        hunt_finds=["chimpanzee", "african_lion", "red_panda", "ring_tailed_lemur", "asian_small_clawed_otter", "two_toed_sloth"],
        hunt_challenges=[
            ("art_penguin", "African penguin: watch one bird enter or leave the water."),
            ("art_giraffe", "Reticulated giraffe: count the spots you can see on one neck."),
            ("art_gorilla", "Gorilla House: who looks calmest?"),
            ("art_chimp", "Forest House chimps: spot hands used like tools."),
        ],
        display_names={
            "african-penguin": "ARTIS African penguin",
            "reticulated-giraffe": "ARTIS reticulated giraffe",
            "western-lowland-gorilla": "Gorilla House gorilla",
            "chimpanzee": "Forest House chimpanzee",
            "african-lion": "ARTIS lion",
            "red-panda": "ARTIS red panda",
            "ring-tailed-lemur": "Kerbertterras lemur",
            "asian-small-clawed-otter": "Kerbertterras otter",
            "two-toed-sloth": "ARTIS sloth",
            "ostrich": "ARTIS ostrich",
        },
        treasure=[
            "Watch an African penguin zoom underwater",
            "Look up at a reticulated giraffe",
            "Find the Gorilla House family",
            "Watch Forest House chimps use their hands",
            "Hear a lion — or wait quietly",
            "Find a rusty red panda",
            "Find a Kerbertterras ring-tailed lemur",
            "Pick an ARTIS favorite — draw it later",
        ],
    )

    apply_kit(
        "barcelona-zoo",
        verified=True,
        tagline="African bush elephant first, then a common hippo and American flamingos — Humboldt penguins, not African.",
        items=[
            item("african-elephant", zone="Animals", one="African bush elephant — look at that trunk.", core=True),
            item("nile-hippo", zone="Animals", one="Common hippopotamus — watch the water window.", core=True, label="Hippo", note="Official: Common hippopotamus (Hippopotamus amphibius). Soft Hippo."),
            item("caribbean-flamingo", zone="Birds", one="American flamingo flock — long legs in the shallows.", core=True, label="Flamingo", note="Official: American flamingo (Phoenicopterus ruber). Also keeps Chilean; American is named."),
            item("western-lowland-gorilla", zone="Animals", one="Western lowland gorilla — who looks in charge?", core=True),
            item("chimpanzee", zone="Animals", one="Chimpanzee play and chatter.", core=True),
            item("orangutan", zone="Animals", one="Bornean orangutan — long arms in the trees.", core=True),
            item("sumatran-tiger", zone="Animals", one="Sumatran tiger — the ones here are the Sumatra subspecies.", core=False),
            item("warthog", zone="Animals", one="Warthog — snout, tusks, and a keeper-talk favorite.", core=False),
            item("zebra", zone="Animals", one="Chapman's zebra — every stripe set is unique.", core=False, label="Zebra", note="Official: Chapman's zebra."),
            item("red-panda", zone="Animals", one="Red panda — rusty and tree-high.", core=False),
        ],
        bans=[
            ban("african-penguin", "Official animals page: Humboldt penguin."),
            ban("galapagos-tortoise", "Official: Aldabra giant tortoise (page contrasts it with Galápagos)."),
            ban("asian-small-clawed-otter", "Official: Eurasian otter."),
        ],
        sources=[
            "https://zoobarcelona.cat/en/animals",
            "https://zoobarcelona.cat/en/animals/common-hippopotamus",
            "https://zoobarcelona.cat/en/animals/american-flamingo",
            "https://zoobarcelona.cat/en/animals/sumatran-tiger",
            "https://zoobarcelona.cat/en/animals/humboldt-penguin",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (zoobarcelona.cat/en/animals).",
        hunt_tag="Barcelona bonus · African elephant + common hippo + American flamingo",
        hunt_finds=["western_lowland_gorilla", "chimpanzee", "orangutan", "sumatran_tiger", "warthog", "zebra"],
        hunt_challenges=[
            ("bcn_elephant", "African bush elephant: trunk busy or a full rest?"),
            ("bcn_hippo", "Common hippo: underwater, mud, or bank?"),
            ("bcn_flam", "American flamingos: more than half on one leg?"),
            ("bcn_gorilla", "Gorilla family: who looks calmest?"),
        ],
        display_names={
            "african-elephant": "Barcelona African elephant",
            "nile-hippo": "Barcelona hippo",
            "caribbean-flamingo": "American flamingo",
            "western-lowland-gorilla": "Barcelona gorilla",
            "chimpanzee": "Barcelona chimpanzee",
            "orangutan": "Bornean orangutan",
            "sumatran-tiger": "Barcelona Sumatran tiger",
            "warthog": "Barcelona warthog",
            "zebra": "Chapman's zebra",
            "red-panda": "Barcelona red panda",
        },
        treasure=[
            "Find the African bush elephant",
            "Watch the common hippo at the water window",
            "Count American flamingos on one leg",
            "Watch the western lowland gorilla family",
            "Watch chimps use their hands like tools",
            "Find orangutan long arms in the trees",
            "Find Sumatran tiger stripes",
            "Pick a Barcelona favorite — draw it later",
        ],
    )

    apply_kit(
        "prague-zoo",
        verified=False,
        tagline="Starter list: Dja Reserve gorillas, then a Rothschild’s giraffe and Lemur Island.",
        items=[
            item("western-lowland-gorilla", zone="Dja Reserve", one="Dja Reserve gorillas — who looks in charge?", core=True),
            item("reticulated-giraffe", zone="African Savanna", one="Rothschild’s giraffe at African House — look up from the path.", core=True, label="Giraffe", note="Official pavilion pages: Rothschild’s giraffe. Soft Giraffe."),
            item("ring-tailed-lemur", zone="Lemur Island", one="Lemur Island ring-tailed lemurs — striped tail.", core=True),
            item("zebra", zone="African Savanna", one="Grevy's zebra — every stripe set is unique.", core=True, label="Zebra", note="Official: Grevy’s zebra."),
            item("nile-hippo", zone="Hippo House", one="Hippo House — Slávek the hippopotamus at the water.", core=True, label="Hippo", note="Official Hippo House / adoption list: hippopotamus (not pygmy). Soft Hippo."),
            item("red-panda", zone="Sichuan", one="Pat the red panda near the main gate.", core=True),
            item("orangutan", zone="Animals", one="Sumatran orang-utan — long arms in the trees.", core=False, presence="high", note="Official adoption list names Sumatran orang-utan (list stamped 01.08.2020)."),
            item("sumatran-tiger", zone="Animals", one="Sumatran tiger — named on the official adoption list.", core=False, presence="high", note="Official adoption inventory names Sumatran tiger (also lists Malayan and Siberian). Confirm yard on arrival."),
            item("cheetah", zone="Animals", one="Cheetah on the official adoption list — tear marks, not a mane.", core=False, presence="high", note="Official adoption list names cheetah."),
            item("ostrich", zone="Animals", one="Ostrich on the official adoption list — look at those legs.", core=False, presence="high", note="Official adoption list names ostrich."),
        ],
        bans=[
            ban("african-elephant", "Official Elephant Valley is a herd of Indian / Asian elephants (Shanti)."),
            ban("african-lion", "Official adoption list names Asiatic lion, not African."),
            ban("african-penguin", "Official Penguin House is Humboldt’s penguin (Otylka)."),
            ban("asian-small-clawed-otter", "Official adoption names Canadian otter and smooth-coated otter, not Asian small-clawed."),
            ban("koala", "Darwin Crater mentions wombats as koala relatives — no koala on site."),
        ],
        sources=[
            "https://www.zoopraha.cz/en/animals",
            "https://www.zoopraha.cz/en/dja",
            "https://www.zoopraha.cz/en/animals/zoom-at-the-zoo/exhibit-compounds/7663-lemur-island",
            "https://www.zoopraha.cz/en/help-us/208-adoption-and-sponsorship/7559-list-of-animals-for-adoption",
        ],
        notes="[2026-08-23] Wave 3a: current pavilion pages plus official adoption inventory (stamped 01.08.2020). No English A–Z encyclopedia. No invented verify date.",
        hunt_tag="Prague bonus · Dja Reserve + African House + Lemur Island",
        hunt_finds=["zebra", "nile_hippo", "red_panda", "orangutan", "sumatran_tiger", "cheetah"],
        hunt_challenges=[
            ("prg_gorilla", "Dja Reserve: who looks calmest in the gorilla family?"),
            ("prg_giraffe", "Rothschild’s giraffe: count the spots you can see on one neck."),
            ("prg_lemur", "Lemur Island: striped tail up or a long sit?"),
            ("prg_hippo", "Hippo House: underwater, mud, or bank?"),
        ],
        display_names={
            "western-lowland-gorilla": "Dja Reserve gorilla",
            "reticulated-giraffe": "African House giraffe",
            "ring-tailed-lemur": "Lemur Island lemur",
            "zebra": "Grevy's zebra",
            "nile-hippo": "Hippo House hippo",
            "red-panda": "Pat the red panda",
            "orangutan": "Prague orangutan",
            "sumatran-tiger": "Prague Sumatran tiger",
            "cheetah": "Prague cheetah",
            "ostrich": "Prague ostrich",
        },
        treasure=[
            "Find the Dja Reserve gorilla family",
            "Look up at a Rothschild’s giraffe",
            "Find a Lemur Island striped tail",
            "Draw one Grevy's zebra stripe set in the air",
            "Watch Hippo House from the water",
            "Find Pat the red panda near the gate",
            "Find orangutan long arms in the trees",
            "Pick a Prague favorite — draw it later",
        ],
    )

    apply_kit(
        "vienna-zoo",
        verified=True,
        tagline="Giant pandas Lan Yun and He Feng first, then a Queensland koala and orangutan — Siberian tigers, not Sumatran.",
        items=[
            item("giant-panda", zone="Pandas", one="Giant pandas Lan Yun and He Feng — the pandas are back.", core=True),
            item("koala", zone="Animals", one="Queensland koala — sleepy eucalyptus eater.", core=True),
            item("orangutan", zone="Animals", one="Orangutan — long arms in the trees.", core=True),
            item("african-elephant", zone="Elephants", one="African savanna elephant — look at that trunk.", core=True),
            item("cheetah", zone="Animals", one="Cheetah — tear marks, not a lion mane.", core=True),
            item("nile-hippo", zone="Animals", one="Flusspferd — Hippopotamus amphibius at the water.", core=True, label="Hippo", note="Official DE lexicon: Flusspferd (Hippopotamus amphibius). Soft Hippo."),
            item("african-lion", zone="Lion rocks", one="African lion — listen for a roar.", core=False, note="Official DE lexicon copy calls it Afrikanischer Löwe."),
            item("reticulated-giraffe", zone="Animals", one="Giraffe / Netzgiraffe — look up from the path.", core=False, label="Giraffe", note="Official lexicon names Giraffe and Netzgiraffe (reticulated). Soft Giraffe."),
            item("red-panda", zone="Animals", one="Roter Panda — rusty and tree-high.", core=False),
            item("asian-small-clawed-otter", zone="Animals", one="Zwergotter Blanche and Squeak — smallest otter, biggest splash.", core=False),
        ],
        bans=[
            ban("sumatran-tiger", "Official DE lexicon: Sibirischer Tiger (Siberian / Amur)."),
            ban("african-penguin", "Official birds lexicon: Humboldt, king, and Northern rockhopper penguins."),
            ban("caribbean-flamingo", "Official: Rosa Flamingo (Phoenicopterus roseus, greater flamingo)."),
            ban("western-lowland-gorilla", "Complete mammal lexicon has no gorilla."),
            ban("chimpanzee", "Complete mammal lexicon has no chimpanzee."),
        ],
        sources=[
            "https://www.zoovienna.at/en/",
            "https://www.zoovienna.at/tiere/saeugetiere/",
            "https://www.zoovienna.at/tiere/voegel/",
            "https://www.zoovienna.at/tiere/saeugetiere/grosser-panda/",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (zoovienna.at German animal lexicon is the complete catalog; English homepage is marketing-thin).",
        hunt_tag="Schönbrunn bonus · pandas + koala + orangutan",
        hunt_finds=["african_elephant", "cheetah", "nile_hippo", "african_lion", "reticulated_giraffe", "red_panda"],
        hunt_challenges=[
            ("vie_panda", "Giant panda: bamboo busy or a full rest?"),
            ("vie_koala", "Queensland koala: eyes open or a daytime nap?"),
            ("vie_orang", "Orangutan: hands or feet doing the clever bit?"),
            ("vie_elephant", "African elephant: trunk busy or a full rest?"),
        ],
        display_names={
            "giant-panda": "Schönbrunn giant panda",
            "koala": "Queensland koala",
            "orangutan": "Schönbrunn orangutan",
            "african-elephant": "Schönbrunn African elephant",
            "cheetah": "Schönbrunn cheetah",
            "nile-hippo": "Schönbrunn hippo",
            "african-lion": "Lion rocks lion",
            "reticulated-giraffe": "Schönbrunn giraffe",
            "red-panda": "Roter Panda",
            "asian-small-clawed-otter": "Zwergotter",
        },
        treasure=[
            "Find giant pandas Lan Yun or He Feng",
            "Find a sleepy Queensland koala",
            "Find orangutan long arms in the trees",
            "Find the African savanna elephant",
            "Spot a cheetah — tear marks, not a mane",
            "Watch the hippo in the water",
            "Hear an African lion — or wait quietly",
            "Pick a Schönbrunn favorite — draw it later",
        ],
    )

    apply_kit(
        "zurich-zoo",
        verified=True,
        tagline="Koala, then a Sumatran orangutan and western lowland gorilla — Asiatic lions and Asian elephants.",
        items=[
            item("koala", zone="Australien", one="Koala — look twice in the Australian habitat.", core=True),
            item("orangutan", zone="Menschenaffenhaus", one="Sumatra orangutan — long arms in the great-ape house.", core=True),
            item("western-lowland-gorilla", zone="Menschenaffenhaus", one="Western lowland gorilla — who looks in charge?", core=True),
            item("reticulated-giraffe", zone="Lewa Savanna", one="Official reticulated giraffe since 2019 — look up from the path.", core=True),
            item("zebra", zone="Lewa Savanna", one="Grevy zebra — every stripe set is unique.", core=True, label="Zebra", note="Official DE lexicon: Grevyzebra."),
            item("red-panda", zone="Animals", one="Kleiner Panda — rusty and tree-high.", core=True),
            item("ostrich", zone="Lewa Savanna", one="South African blue-necked ostrich since 2020.", core=False),
        ],
        bans=[
            ban("african-elephant", "Official Kaeng Krachan Elephant Park: Asian elephant."),
            ban("african-lion", "Official encyclopedia: Asiatischer Löwe (Panthera leo persica)."),
            ban("sumatran-tiger", "Official lexicon lists Amurtiger."),
            ban("african-penguin", "Official: Königspinguin and Humboldtpinguin."),
            ban("caribbean-flamingo", "Official: Chileflamingo — the flamingo kept at Zoo Zürich."),
            ban("galapagos-tortoise", "Official lexicon: Aldabra-Riesenschildkröte."),
            ban("ring-tailed-lemur", "Masoala lemurs are red ruffed and black lemur, not ring-tailed."),
            ban("cm-outdoor", "kind=neither — not a zoo/both card. Masoala is a habitat, not a published animal card."),
        ],
        sources=[
            "https://www.zoo.ch/en",
            "https://www.zoo.ch/de/naturschutz-tiere/tier-pflanzenlexikon",
            "https://www.zoo.ch/en/reticulated-giraffe",
            "https://www.zoo.ch/en/asian-elephant",
            "https://www.zoo.ch/de/naturschutz-tiere/tier-pflanzenlexikon/asiatischer-loewe",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (zoo.ch German encyclopedia). English encyclopedia is intentionally incomplete. Dropped cloned cm-outdoor neither card.",
        hunt_tag="Zurich bonus · koala + Menschenaffenhaus + Lewa Savanna",
        hunt_finds=["reticulated_giraffe", "zebra", "red_panda", "ostrich"],
        hunt_challenges=[
            ("zur_koala", "Koala: eyes open or a daytime nap?"),
            ("zur_orang", "Sumatra orangutan: hands or feet doing the clever bit?"),
            ("zur_gorilla", "Gorilla: who looks calmest?"),
            ("zur_giraffe", "Reticulated giraffe: count the spots you can see on one neck."),
        ],
        display_names={
            "koala": "Zurich koala",
            "orangutan": "Sumatra orangutan",
            "western-lowland-gorilla": "Zurich gorilla",
            "reticulated-giraffe": "Lewa giraffe",
            "zebra": "Grevy zebra",
            "red-panda": "Kleiner Panda",
            "ostrich": "Lewa ostrich",
        },
        treasure=[
            "Find a koala in the Australian habitat",
            "Find orangutan long arms in the ape house",
            "Watch the western lowland gorilla family",
            "Look up at a Lewa Savanna reticulated giraffe",
            "Draw one Grevy zebra stripe set in the air",
            "Find a rusty Kleiner Panda",
            "Look at a Lewa ostrich’s legs",
            "Pick a Zurich favorite — draw it later",
        ],
    )

    apply_kit(
        "copenhagen-zoo",
        verified=True,
        tagline="Panda House first, then a reticulated giraffe and Hippo House — Asian elephants and Amur tigers.",
        items=[
            item("giant-panda", zone="Panda House", one="Giant panda — bamboo first at Panda House.", core=True),
            item("reticulated-giraffe", zone="Giraffe House", one="Official reticulated giraffe — look up from the path.", core=True),
            item("nile-hippo", zone="Hippo House", one="Hippopotamus amphibius at Hippo House.", core=True, label="Hippo", note="Official 2025 inventory: Hippopotamus (Hippopotamus amphibius). Soft Hippo."),
            item("african-lion", zone="Animals", one="Lion — listen for a roar.", core=True, label="Lion", note="Official inventory: Lion (Panthera leo). Soft Lion."),
            item("chimpanzee", zone="Animals", one="Chimpanzee — hands used like tools.", core=True),
            item("caribbean-flamingo", zone="Animals", one="American flamingo / Cariberflamingo flock.", core=True, label="Flamingo", note="Official inventory: American flamingo (Phoenicopterus ruber). Soft Flamingo."),
            item("red-panda", zone="Animals", one="Red panda — rusty and tree-high.", core=False),
            item("ring-tailed-lemur", zone="Animals", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("zebra", zone="Animals", one="Plains zebra — pick one stripe set and draw it in the air.", core=False, label="Zebra", note="Official inventory: Plains zebra (Equus quagga)."),
            item("asian-small-clawed-otter", zone="Animals", one="Asian small-clawed otter — smallest otter, biggest splash.", core=False),
        ],
        bans=[
            ban("african-elephant", "Official 31 Dec 2025 inventory: Asian elephant (Elephas maximus)."),
            ban("sumatran-tiger", "Official inventory: Amur tiger (Panthera tigris altaica)."),
            ban("african-penguin", "Official inventory: Humboldt penguin (Spheniscus humboldti)."),
            ban("western-lowland-gorilla", "Not on the official 2025 animal inventory."),
            ban("orangutan", "Not on the official 2025 animal inventory."),
            ban("koala", "Not on the official 2025 animal inventory."),
            ban("cheetah", "Not on the official 2025 animal inventory."),
            ban("galapagos-tortoise", "Inventory lists other tortoises, not Galápagos."),
        ],
        sources=[
            "https://www.zoo.dk/en",
            "https://content.zoo.dk/media/jfall0sx/dyrebestandsliste-2025.pdf",
            "https://www.zoo.dk/en/plan-your-visit/guides-to-your-visit",
        ],
        notes="[2026-08-23] Official-source Wave 3a public list pass (zoo.dk animal inventory as of 31 December 2025).",
        hunt_tag="Copenhagen bonus · Panda House + Giraffe House + Hippo House",
        hunt_finds=["african_lion", "chimpanzee", "caribbean_flamingo", "red_panda", "ring_tailed_lemur", "zebra"],
        hunt_challenges=[
            ("cph_panda", "Panda House: bamboo busy or a full rest?"),
            ("cph_giraffe", "Reticulated giraffe: count the spots you can see on one neck."),
            ("cph_hippo", "Hippo House: underwater, mud, or bank?"),
            ("cph_flam", "American flamingos: more than half on one leg?"),
        ],
        display_names={
            "giant-panda": "Panda House panda",
            "reticulated-giraffe": "Giraffe House giraffe",
            "nile-hippo": "Hippo House hippo",
            "african-lion": "Copenhagen lion",
            "chimpanzee": "Copenhagen chimpanzee",
            "caribbean-flamingo": "American flamingo",
            "red-panda": "Copenhagen red panda",
            "ring-tailed-lemur": "Copenhagen lemur",
            "zebra": "Plains zebra",
            "asian-small-clawed-otter": "Copenhagen otter",
        },
        treasure=[
            "Find a giant panda at Panda House",
            "Look up at a reticulated giraffe",
            "Watch Hippo House from the water",
            "Hear a lion — or wait quietly",
            "Watch chimps use their hands like tools",
            "Count American flamingos on one leg",
            "Find a rusty red panda",
            "Pick a Copenhagen favorite — draw it later",
        ],
    )


if __name__ == "__main__":
    main()
