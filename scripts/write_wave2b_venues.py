#!/usr/bin/env python3
"""Write Wave 2b venue JSONs + matching catalog.js kits from the 2026-08-23 official pass.

Does not rewrite card-kinds.tsv. Does not touch Wave 1 or Wave 2a venue lists.
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
    # Insert before featuredAnimalIds (or animalIds).
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
        "albuquerque-biopark",
        verified=True,
        tagline="Gorillas and chimps first, then a reticulated giraffe — Asian elephants, not African.",
        items=[
            item("western-lowland-gorilla", zone="Primates", one="Western lowland gorilla — who looks in charge?", core=True),
            item("chimpanzee", zone="Primates", one="Chimp play and chatter on the primate side.", core=True),
            item("reticulated-giraffe", zone="Africa", one="Official reticulated giraffe — look up from the path.", core=True),
            item("cheetah", zone="Cats", one="Southeast African cheetah — tear marks, not a lion mane.", core=True),
            item("orangutan", zone="Primates", one="Sumatran orangutan — long arms in the trees.", core=True),
            item("nile-hippo", zone="Hippos", one="Official Hippo — watch the water window.", core=True, label="Hippo", note="Official city animals page: Hippo. Soft Hippo."),
            item("zebra", zone="Africa", one="Hartmann's mountain zebra — every stripe set is unique.", core=False, label="Zebra", note="Official: Hartmann's Mountain Zebra."),
            item("warthog", zone="Africa", one="Southern warthog — snout, tusks, and a trot.", core=False),
            item("caribbean-flamingo", zone="Birds", one="American flamingo flock — long legs in the shallows.", core=False, label="Flamingo", note="Official: American Flamingo (Caribbean form). Soft Flamingo."),
        ],
        bans=[
            ban("african-elephant", "Official city animals page lists Asian Elephant."),
            ban("sumatran-tiger", "Official list: Malayan Tiger, not Sumatran."),
            ban("african-penguin", "Official: Gentoo, King, and Macaroni penguins — not African."),
            ban("african-lion", "Not on the current official city animals page or June 2026 zoo map."),
            ban("galapagos-tortoise", "Official list does not name Galápagos tortoise."),
        ],
        sources=[
            "https://www.cabq.gov/artsculture/biopark/zoo/zoo-animals",
            "https://www.cabq.gov/artsculture/biopark/zoo",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (cabq.gov zoo-animals). Lion omitted — not on the current city animals page.",
        hunt_tag="ABQ BioPark bonus · primates + giraffe + cheetah",
        hunt_finds=["cheetah", "orangutan", "nile_hippo", "zebra", "warthog", "caribbean_flamingo"],
        hunt_challenges=[
            ("abq_gorilla", "Gorilla yard: who looks calmest?"),
            ("abq_chimp", "Chimps: spot hands used like tools."),
            ("abq_giraffe", "Reticulated giraffe: count the spots you can see on one neck."),
            ("abq_cheetah", "Cheetah: statue score 1–10 after 20 quiet seconds."),
        ],
        display_names={
            "western-lowland-gorilla": "BioPark gorilla",
            "chimpanzee": "BioPark chimpanzee",
            "reticulated-giraffe": "BioPark giraffe",
            "cheetah": "Southeast African cheetah",
            "orangutan": "Sumatran orangutan",
            "nile-hippo": "BioPark hippo",
            "zebra": "Hartmann's zebra",
            "warthog": "Southern warthog",
            "caribbean-flamingo": "American flamingo",
        },
        treasure=[
            "Find the western lowland gorilla family",
            "Watch chimps use their hands like tools",
            "Look up at a reticulated giraffe neck",
            "Spot cheetah tear marks — not a lion mane",
            "Find orangutan long arms in the trees",
            "Watch the hippo in the water",
            "Draw one Hartmann's zebra stripe set in the air",
            "Pick a BioPark favorite — draw it later",
        ],
    )

    apply_kit(
        "audubon-zoo",
        verified=True,
        tagline="African lions and Caribbean flamingos, then World of Primates gorillas — zoo-side cards only.",
        items=[
            item("african-lion", zone="African Savanna", one="African Savanna lions — listen for a roar.", core=True),
            item("caribbean-flamingo", zone="Entrance flock", one="Caribbean flamingo lagoon — the unofficial welcome committee.", core=True),
            item("western-lowland-gorilla", zone="World of Primates", one="World of Primates gorilla troop — who looks in charge?", core=True),
            item("reticulated-giraffe", zone="Twiga Terrace", one="Twiga Terrace giraffe — look up from the path.", core=True, label="Giraffe", note="Official animals list: Giraffe. Soft Giraffe."),
            item("zebra", zone="Twiga Terrace", one="Hartmann's mountain zebra back on Twiga Terrace.", core=True, label="Zebra", note="Official: Hartmann's Mountain Zebra."),
            item("orangutan", zone="Asia", one="Sumatran orangutan — long arms in the trees.", core=True),
            item("two-toed-sloth", zone="Animals", one="Linne's two-toed sloth — hang and look twice.", core=False),
        ],
        bans=[
            ban("african-elephant", "Official Zoo list: Asian Elephant."),
            ban("sumatran-tiger", "Official Zoo list: Malayan Tiger."),
            ban("african-penguin", "Official: African Penguin is at Audubon Aquarium, not the Zoo."),
            ban("galapagos-tortoise", "Official Zoo list: Aldabra Tortoise, not Galápagos."),
            ban("nile-hippo", "Not on the official Zoo animals list."),
            ban("ring-tailed-lemur", "Official Zoo list: Black and White Ruffed Lemur, not ring-tailed."),
        ],
        sources=[
            "https://audubonnatureinstitute.org/animals-of-audubon",
            "https://audubonnatureinstitute.org/zoo-exhibits-and-experiences",
            "https://audubonnatureinstitute.org/zoo/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass. Zoo location only; Aquarium African penguin dropped.",
        hunt_tag="Audubon bonus · Savanna + flamingos + primates",
        hunt_finds=["reticulated_giraffe", "zebra", "orangutan", "two_toed_sloth"],
        hunt_challenges=[
            ("au_lion", "African Savanna: roar or a quiet pride?"),
            ("au_flam", "Caribbean flamingos: more than half on one leg?"),
            ("au_gorilla", "World of Primates: who looks calmest?"),
            ("au_zebra", "Twiga Terrace: draw one Hartmann's stripe set in the air."),
        ],
        display_names={
            "african-lion": "Savanna lion",
            "caribbean-flamingo": "Caribbean flamingo",
            "western-lowland-gorilla": "World of Primates gorilla",
            "reticulated-giraffe": "Twiga Terrace giraffe",
            "zebra": "Hartmann's zebra",
            "orangutan": "Sumatran orangutan",
            "two-toed-sloth": "Linne sloth",
        },
        treasure=[
            "Hear an African Savanna lion — or wait quietly",
            "Count Caribbean flamingos standing on one leg",
            "Find the World of Primates gorilla family",
            "Look up at a Twiga Terrace giraffe",
            "Draw one Hartmann's zebra stripe set in the air",
            "Find orangutan long arms in the trees",
            "Hang-and-look-twice at a two-toed sloth",
            "Pick an Audubon Zoo favorite — draw it later",
        ],
    )

    apply_kit(
        "cincinnati-zoo",
        verified=True,
        tagline="Hippo Cove first, then Gorilla World and a cheetah sprint — Asian elephants, not African.",
        items=[
            item("nile-hippo", zone="Hippo Cove", one="Hippo Cove — Fiona and the bloat at the underwater window.", core=True),
            item("western-lowland-gorilla", zone="Gorilla World", one="Gorilla World family — who looks in charge?", core=True),
            item("cheetah", zone="Cheetah Encounter", one="Cheetah Encounter — tear marks, then a sprint if the run is on.", core=True),
            item("african-penguin", zone="African Penguin Point", one="African Penguin Point — waddle, then zoom in the water.", core=True),
            item("african-lion", zone="Africa", one="Africa lion pride — listen for a roar.", core=True),
            item("galapagos-tortoise", zone="Galapagos Tortoise Yard", one="Galápagos tortoise yard — mid-step or statue?", core=True),
            item("red-panda", zone="Red Panda", one="Red panda — rusty and tree-high.", core=False),
            item("orangutan", zone="Jungle Trails", one="Jungle Trails orangutan — long arms in the trees.", core=False),
            item("ring-tailed-lemur", zone="Lemur Lookout", one="Lemur Lookout — striped tail and a long stare.", core=False),
            item("two-toed-sloth", zone="P&G Discovery Forest", one="Discovery Forest sloth — hang and look twice.", core=False),
        ],
        bans=[
            ban("african-elephant", "Official: Asian elephant at Elephant Trek."),
            ban("sumatran-tiger", "Official Cat Canyon: Malayan Tiger, not Sumatran."),
            ban("caribbean-flamingo", "Official birds list: Greater Flamingo, not Caribbean."),
        ],
        sources=[
            "https://cincinnatizoo.org/animals/",
            "https://cincinnatizoo.org/animals/habitats/",
            "https://cincinnatizoo.org/animals-archive/hippopotamus/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (cincinnatizoo.org/animals + habitats).",
        hunt_tag="Cincinnati bonus · Hippo Cove + Gorilla World + cheetahs",
        hunt_finds=["african_penguin", "african_lion", "galapagos_tortoise", "red_panda", "orangutan", "ring_tailed_lemur"],
        hunt_challenges=[
            ("cin_hippo", "Hippo Cove: more underwater, mud, or bank?"),
            ("cin_gorilla", "Gorilla World: who looks calmest?"),
            ("cin_cheetah", "Cheetah Encounter: statue score 1–10 after 20 quiet seconds."),
            ("cin_penguin", "Penguin Point: watch one bird enter or leave the water."),
        ],
        display_names={
            "nile-hippo": "Hippo Cove hippo",
            "western-lowland-gorilla": "Gorilla World gorilla",
            "cheetah": "Cheetah Encounter cheetah",
            "african-penguin": "Penguin Point penguin",
            "african-lion": "Cincinnati lion",
            "galapagos-tortoise": "Tortoise Yard tortoise",
            "red-panda": "Cincinnati red panda",
            "orangutan": "Jungle Trails orangutan",
            "ring-tailed-lemur": "Lemur Lookout lemur",
            "two-toed-sloth": "Discovery Forest sloth",
        },
        treasure=[
            "Watch Fiona’s bloat at the Hippo Cove window",
            "Find the Gorilla World family",
            "Spot cheetah tear marks — not a mane",
            "Watch an African penguin zoom underwater",
            "Hear an Africa lion — or wait quietly",
            "Find a Galápagos tortoise mid-step or statue-still",
            "Find a rusty red panda in the trees",
            "Pick a Cincinnati favorite — draw it later",
        ],
    )

    apply_kit(
        "cleveland-metroparks-zoo",
        verified=False,
        tagline="Starter list: African Elephant Crossing, gorillas, then cheetahs on the savanna path.",
        items=[
            item("african-elephant", zone="African Elephant Crossing", one="Four African elephants at Elephant Crossing.", core=True),
            item("western-lowland-gorilla", zone="Primate, Cat & Aquatics", one="Western lowland gorilla — who looks in charge?", core=True),
            item("cheetah", zone="African Savanna", one="Savanna cheetahs — the zoo’s speediest animals.", core=True),
            item("african-lion", zone="African Savanna", one="African Lion habitat — listen for a roar.", core=True),
            item("zebra", zone="African Savanna", one="Savanna zebra — pick one stripe set and draw it in the air.", core=True),
            item("reticulated-giraffe", zone="Ben Gogolick Giraffe Encounter", one="Giraffe Encounter — look up from the path.", core=True, label="Giraffe", note="Official habitat pages list giraffes; soft Giraffe."),
            item("koala", zone="Australian Adventure", one="Official location pages: visit koalas year-round.", core=False),
        ],
        bans=[
            ban("sumatran-tiger", "Official: Amur tigers at Rosebrough Tiger Passage."),
            ban("galapagos-tortoise", "Official habitat pages: Aldabra tortoises, not Galápagos."),
            ban("nile-hippo", "No current official Nile hippo habitat page."),
            ban("two-toed-sloth", "RainForest (sloths) is closed for Primate Forest construction."),
            ban("orangutan", "RainForest (orangutans) is closed for Primate Forest construction."),
        ],
        sources=[
            "https://www.clevelandmetroparks.com/zoo",
            "https://www.clevelandmetroparks.com/zoo/zoo-locations/african-elephant-crossing",
            "https://www.clevelandmetroparks.com/zoo/zoo-locations/african-savanna",
            "https://www.clevelandmetroparks.com/zoo/zoo-locations/primate-cat-and-aquatics",
        ],
        notes="[2026-08-23] Wave 2b: habitat pages only; no complete current A–Z. Resource library is historical. RainForest sloth/orangutan omitted (closed). No invented verify date.",
        hunt_tag="Cleveland bonus · Elephant Crossing + gorillas + savanna",
        hunt_finds=["african_lion", "zebra", "reticulated_giraffe", "koala"],
        hunt_challenges=[
            ("cle_elephant", "Elephant Crossing: trunk busy or a full rest?"),
            ("cle_gorilla", "Gorilla: who looks in charge?"),
            ("cle_cheetah", "Cheetah: statue score 1–10 after 20 quiet seconds."),
            ("cle_koala", "Koala: eyes open or a daytime nap?"),
        ],
        display_names={
            "african-elephant": "Elephant Crossing elephant",
            "western-lowland-gorilla": "Cleveland gorilla",
            "cheetah": "Savanna cheetah",
            "african-lion": "Savanna lion",
            "zebra": "Savanna zebra",
            "reticulated-giraffe": "Giraffe Encounter giraffe",
            "koala": "Australian Adventure koala",
        },
        treasure=[
            "Find the African Elephant Crossing herd",
            "Watch the gorilla family — who looks in charge?",
            "Spot a cheetah — tear marks, not a mane",
            "Hear an African lion — or wait quietly",
            "Draw one zebra stripe set in the air",
            "Look up at a Giraffe Encounter neck",
            "Find a koala at Australian Adventure",
            "Pick a Cleveland favorite — draw it later",
        ],
    )

    apply_kit(
        "detroit-zoo",
        verified=True,
        tagline="Great Apes first — gorilla, then chimpanzee, then the African lion pride.",
        items=[
            item("western-lowland-gorilla", zone="Great Apes of Harambee", one="Harambee gorilla family — who looks in charge?", core=True, label="Gorilla", note="Official animal page: Gorilla (Gorilla gorilla gorilla)."),
            item("chimpanzee", zone="Great Apes of Harambee", one="Harambee chimp play and chatter.", core=True),
            item("african-lion", zone="African Grasslands", one="African Grasslands pride — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="African Grasslands", one="African Grasslands giraffe — look up from the path.", core=True, label="Giraffe", note="Official animal page: Giraffe. Soft Giraffe."),
            item("zebra", zone="African Grasslands", one="Grevy's zebra — every stripe set is unique.", core=True, label="Zebra", note="Official: Grevy's Zebra."),
            item("warthog", zone="African Grasslands", one="Warthog family — snout, tusks, and a trot.", core=True),
            item("red-panda", zone="Holtzman Wildlife Foundation Red Panda Forest", one="Red panda — rusty and tree-high.", core=False),
        ],
        bans=[
            ban("african-penguin", "Penguin Conservation Center features macaroni and other cold-climate penguins — not African."),
            ban("sumatran-tiger", "Official animal page is Amur tiger, not Sumatran."),
            ban("african-elephant", "Detroit Zoo ended its elephant program in 2005."),
            ban("nile-hippo", "No official hippo animal page."),
            ban("cheetah", "No official cheetah animal page."),
            ban("two-toed-sloth", "Official listing is sloth bear, not a two-toed sloth."),
        ],
        sources=[
            "https://detroitzoo.org/animals/",
            "https://detroitzoo.org/animal/gorilla/",
            "https://detroitzoo.org/animal/chimpanzee/",
            "https://detroitzoo.org/animal/african-lion/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (detroitzoo.org/animals + species pages).",
        hunt_tag="Detroit bonus · Harambee apes + African Grasslands",
        hunt_finds=["reticulated_giraffe", "zebra", "warthog", "red_panda"],
        hunt_challenges=[
            ("det_gorilla", "Harambee: gorilla hands busy or full rest?"),
            ("det_chimp", "Chimps: spot hands used like tools."),
            ("det_lion", "Lions: roar or a quiet pride?"),
            ("det_warthog", "Warthog: trot, mud, or a still stare?"),
        ],
        display_names={
            "western-lowland-gorilla": "Harambee gorilla",
            "chimpanzee": "Harambee chimpanzee",
            "african-lion": "Grasslands lion",
            "reticulated-giraffe": "Grasslands giraffe",
            "zebra": "Grevy's zebra",
            "warthog": "Grasslands warthog",
            "red-panda": "Red Panda Forest panda",
        },
        treasure=[
            "Find the Harambee gorilla family",
            "Watch chimps use their hands like tools",
            "Hear an African lion — or wait quietly",
            "Look up at a Grasslands giraffe",
            "Draw one Grevy's zebra stripe set in the air",
            "Find a warthog trot or a still stare",
            "Find a rusty red panda in the trees",
            "Pick a Detroit favorite — draw it later",
        ],
    )

    apply_kit(
        "hogle-zoo",
        verified=False,
        tagline="Starter list: Great Apes gorillas and orangutans, then the African lion pride.",
        items=[
            item("western-lowland-gorilla", zone="Great Apes", one="Great Apes gorilla troop — who looks in charge?", core=True),
            item("orangutan", zone="Great Apes", one="Bornean orangutan — long arms in the trees.", core=True),
            item("african-lion", zone="African Savanna", one="African lion pride — listen for a roar.", core=True),
            item("reticulated-giraffe", zone="Twiga Terrace", one="Twiga Terrace giraffe — look up from the path.", core=True, label="Giraffe", note="Official exhibit pages list Giraffe. Soft Giraffe."),
            item("zebra", zone="African Savanna", one="Hartmann's mountain zebra — every stripe set is unique.", core=True, label="Zebra", note="Official: Hartmann's mountain zebras."),
            item("ostrich", zone="African Savanna", one="Savanna ostrich — look at those legs.", core=False),
            item("warthog", zone="African Savanna", one="Southern warthog — snout, tusks, and a trot.", core=False),
            item("red-panda", zone="Asian Highlands", one="Chinese red panda — rusty and tree-high.", core=False),
        ],
        bans=[
            ban("sumatran-tiger", "Official Asian Highlands: Amur Tiger, not Sumatran."),
            ban("asian-small-clawed-otter", "Official: North American River Otter, not Asian small-clawed."),
            ban("galapagos-tortoise", "Official: Aldabra tortoises, not Galápagos."),
            ban("african-elephant", "Not on the official habitat resident lists reviewed."),
            ban("african-penguin", "Not on the official habitat resident lists reviewed."),
        ],
        sources=[
            "https://www.hoglezoo.org/",
            "https://www.hoglezoo.org/exhibits/",
            "https://www.hoglezoo.org/great-apes/",
            "https://www.hoglezoo.org/african-savanna/",
        ],
        notes="[2026-08-23] Wave 2b: official habitat resident lists, no complete animals index. No invented verify date.",
        hunt_tag="Hogle bonus · Great Apes + savanna",
        hunt_finds=["reticulated_giraffe", "zebra", "ostrich", "warthog", "red_panda"],
        hunt_challenges=[
            ("hg_gorilla", "Great Apes: who looks calmest in the gorilla troop?"),
            ("hg_orang", "Orangutan: hands or feet doing the clever bit?"),
            ("hg_lion", "Lions: roar or a quiet pride?"),
            ("hg_zebra", "Mountain zebra: draw one stripe set in the air."),
        ],
        display_names={
            "western-lowland-gorilla": "Great Apes gorilla",
            "orangutan": "Bornean orangutan",
            "african-lion": "Hogle lion",
            "reticulated-giraffe": "Twiga Terrace giraffe",
            "zebra": "Mountain zebra",
            "ostrich": "Savanna ostrich",
            "warthog": "Southern warthog",
            "red-panda": "Asian Highlands red panda",
        },
        treasure=[
            "Find the Great Apes gorilla troop",
            "Find orangutan long arms in the trees",
            "Hear an African lion — or wait quietly",
            "Look up at a Twiga Terrace giraffe",
            "Draw one mountain zebra stripe set in the air",
            "Look at an ostrich’s legs — biggest bird",
            "Find a rusty red panda at Asian Highlands",
            "Pick a Hogle favorite — draw it later",
        ],
    )

    apply_kit(
        "honolulu-zoo",
        verified=False,
        tagline="Starter list: African penguins, then a Sumatran tiger and reticulated giraffe.",
        items=[
            item("african-penguin", zone="Africa", one="African penguin — waddle, then zoom in the water.", core=True),
            item("sumatran-tiger", zone="Sumatra", one="Sumatran tiger — orange stripes in the trees.", core=True),
            item("reticulated-giraffe", zone="Africa", one="Official reticulated giraffe — look up from the path.", core=True),
            item("cheetah", zone="Africa", one="Cheetah — tear marks, not a lion mane.", core=True),
            item("african-lion", zone="Africa", one="Lion yard — listen for a roar.", core=True, label="Lion", note="Official archive: Lion. Soft Lion."),
            item("nile-hippo", zone="Africa", one="Official Hippopotamus — watch the water.", core=True, label="Hippo", note="Official: Hippopotamus. Soft Hippo."),
            item("ring-tailed-lemur", zone="Madagascar", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("orangutan", zone="Indonesia", one="Orangutan — long arms in the trees.", core=False),
            item("two-toed-sloth", zone="South America", one="Linne's two-toed sloth — hang and look twice.", core=False),
            item("galapagos-tortoise", zone="Galapagos", one="Galápagos tortoise — mid-step or statue?", core=False),
        ],
        bans=[
            ban("african-elephant", "Official list: Asian Elephant."),
            ban("western-lowland-gorilla", "Not named on the official animal archives reviewed."),
            ban("zebra", "Not named on the official animal archives reviewed."),
        ],
        sources=[
            "https://www.honoluluzoo.org/",
            "https://www.honoluluzoo.org/all-animals/africa/",
            "https://www.honoluluzoo.org/all-animals/mammals/",
            "https://www.honoluluzoo.org/all-animals/sumatra/",
        ],
        notes="[2026-08-23] Wave 2b: official all-animals archives (paginated). No invented verify date.",
        hunt_tag="Honolulu bonus · penguins + Sumatra + Africa",
        hunt_finds=["cheetah", "african_lion", "nile_hippo", "ring_tailed_lemur", "orangutan", "galapagos_tortoise"],
        hunt_challenges=[
            ("hnl_penguin", "African penguin: watch one bird enter or leave the water."),
            ("hnl_tiger", "Sumatran tiger: count stripe clusters on one shoulder (best guess)."),
            ("hnl_giraffe", "Reticulated giraffe: count the spots you can see on one neck."),
            ("hnl_lemur", "Ring-tailed lemur: striped tail up or a long sit?"),
        ],
        display_names={
            "african-penguin": "Honolulu African penguin",
            "sumatran-tiger": "Sumatra tiger",
            "reticulated-giraffe": "Honolulu giraffe",
            "cheetah": "Honolulu cheetah",
            "african-lion": "Honolulu lion",
            "nile-hippo": "Honolulu hippo",
            "ring-tailed-lemur": "Madagascar lemur",
            "orangutan": "Honolulu orangutan",
            "two-toed-sloth": "Linne sloth",
            "galapagos-tortoise": "Galapagos tortoise",
        },
        treasure=[
            "Watch an African penguin zoom underwater",
            "Find Sumatran tiger stripes in the trees",
            "Look up at a reticulated giraffe",
            "Spot cheetah tear marks — not a mane",
            "Hear a lion — or wait quietly",
            "Watch the hippo in the water",
            "Find a ring-tailed lemur’s striped tail",
            "Pick a Honolulu favorite — draw it later",
        ],
    )

    apply_kit(
        "kansas-city-zoo",
        verified=False,
        tagline="Starter list: chimpanzee troop, western lowland gorillas, then a Sumatran tiger.",
        items=[
            item("chimpanzee", zone="Chimpanzee habitat", one="Chimpanzee troop — hands used like tools.", core=True),
            item("western-lowland-gorilla", zone="Gorillas", one="Western lowland gorillas — who looks in charge?", core=True),
            item("sumatran-tiger", zone="Asia", one="Sumatran tiger Phoebe — orange stripes in the trees.", core=True),
            item("orangutan", zone="Orangutan Canopy", one="Orangutan Canopy — long arms in the trees.", core=True),
            item("cheetah", zone="Africa", one="Cheetah exhibit — tear marks, not a lion mane.", core=True),
            item("red-panda", zone="Asia", one="Red panda near the Asian cats — rusty and tree-high.", core=True),
            item("reticulated-giraffe", zone="Giraffe Crossing", one="Giraffe Crossing — look up from the path.", core=False, label="Giraffe", note="Official chats/habitat: giraffes; conservation copy names Masai. Soft Giraffe."),
            item("african-lion", zone="Africa", one="Lion family / Lion Chat — listen for a roar.", core=False, label="Lion", note="Official chats: lion family. Soft Lion."),
            item("nile-hippo", zone="Hippo", one="Hippo Chat — Liberty and Cairo at the water.", core=False, label="Hippo", note="Official Hippo Chat names Liberty and Cairo (not pygmy). Soft Hippo."),
            item("zebra", zone="African Sky Safari", one="African Sky Safari zebras — every pattern is unique.", core=False),
        ],
        bans=[
            ban("african-penguin", "Official Helzberg Penguin Plaza: King, Gentoo, Macaroni, Chinstrap, and Humboldt — not African."),
            ban("african-elephant", "Official pages say elephants / Elephant Expedition but do not name African vs Asian."),
            ban("koala", "Not confirmed on the official chats / exhibit pages reviewed."),
        ],
        sources=[
            "https://kansascityzoo.org/animals",
            "https://kansascityzoo.org/activity/animal-chats",
            "https://kansascityzoo.org/animals/orangutan-canopy",
            "https://kansascityzoo.org/featured-exhibits",
        ],
        notes="[2026-08-23] Wave 2b: official chats + exhibit pages (animals index is JS-only). Zoo-side cards only; Sobela Ocean Aquarium omitted. No invented verify date.",
        hunt_tag="Kansas City bonus · apes + Sumatran tiger + Africa",
        hunt_finds=["orangutan", "cheetah", "red_panda", "reticulated_giraffe", "african_lion", "nile_hippo"],
        hunt_challenges=[
            ("kc_chimp", "Chimps: spot hands used like tools."),
            ("kc_gorilla", "Gorillas: who looks calmest?"),
            ("kc_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
            ("kc_hippo", "Hippo: underwater, mud, or bank?"),
        ],
        display_names={
            "chimpanzee": "KC chimpanzee",
            "western-lowland-gorilla": "KC gorilla",
            "sumatran-tiger": "Sumatran tiger Phoebe",
            "orangutan": "Orangutan Canopy orangutan",
            "cheetah": "KC cheetah",
            "red-panda": "Asia red panda",
            "reticulated-giraffe": "Giraffe Crossing giraffe",
            "african-lion": "KC lion",
            "nile-hippo": "KC hippo",
            "zebra": "Sky Safari zebra",
        },
        treasure=[
            "Watch the chimpanzee troop use their hands",
            "Find the western lowland gorilla family",
            "Find Sumatran tiger stripes in the trees",
            "Find orangutan long arms at Orangutan Canopy",
            "Spot a cheetah — tear marks, not a mane",
            "Find a rusty red panda on the Asia side",
            "Look up at Giraffe Crossing",
            "Pick a Kansas City zoo-side favorite — draw it later",
        ],
    )

    apply_kit(
        "memphis-zoo",
        verified=True,
        tagline="African Veldt elephants, then a giraffe and Cat Country Sumatran tigers — pandas left in 2023.",
        items=[
            item("african-elephant", zone="African Veldt", one="African Veldt elephant herd — look at that trunk.", core=True),
            item("reticulated-giraffe", zone="African Veldt", one="African Veldt giraffe — look up from the path.", core=True, label="Giraffe", note="Official Veldt lists Giraffe / reticulated giraffes. Soft Giraffe."),
            item("sumatran-tiger", zone="Cat Country", one="Cat Country Sumatran tigers — orange stripes in the trees.", core=True),
            item("western-lowland-gorilla", zone="Primate Canyon", one="Primate Canyon lowland gorillas — who looks in charge?", core=True, label="Gorilla", note="Official: Lowland Gorillas."),
            item("african-lion", zone="Cat Country", one="Cat Country African lions — listen for a roar.", core=True),
            item("african-penguin", zone="Penguin Rock", one="Penguin Rock — African black-footed penguins in the water.", core=True),
            item("cheetah", zone="Cat Country", one="Cat Country cheetah — tear marks, not a lion mane.", core=False),
            item("nile-hippo", zone="Zambezi River Hippo Camp", one="Hippo Camp — Hippopotamus amphibius at the water window.", core=False, label="Hippo", note="Official: Hippos / Hippopotamus amphibius. Soft Hippo."),
            item("two-toed-sloth", zone="Animals of the Night", one="Animals of the Night two-toed sloth — hang and look twice.", core=False),
            item("galapagos-tortoise", zone="Herpetarium", one="Herpetarium Galápagos tortoise — mid-step or statue?", core=False),
        ],
        bans=[
            ban("giant-panda", "China exhibit no longer lists giant pandas (Ya Ya returned to China in 2023)."),
            ban("caribbean-flamingo", "Hippo Camp flamingos are Chilean and lesser, not Caribbean."),
        ],
        sources=[
            "https://www.memphiszoo.org/animals",
            "https://www.memphiszoo.org/african-veldt",
            "https://www.memphiszoo.org/cat-country",
            "https://www.memphiszoo.org/primate-canyon",
            "https://www.memphiszoo.org/penguin-rock",
            "https://www.memphiszoo.org/zambezi-river-hippo-camp",
            "https://www.memphiszoo.org/herpetarium",
            "https://www.memphiszoo.org/china",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (memphiszoo.org habitat pages). Giant panda dropped.",
        hunt_tag="Memphis bonus · Veldt + Cat Country + Primate Canyon",
        hunt_finds=["western_lowland_gorilla", "african_lion", "african_penguin", "cheetah", "nile_hippo", "two_toed_sloth"],
        hunt_challenges=[
            ("mem_elephant", "African Veldt: trunk busy or a full rest?"),
            ("mem_tiger", "Cat Country: count stripe clusters on one tiger shoulder."),
            ("mem_penguin", "Penguin Rock: watch one bird enter or leave the water."),
            ("mem_hippo", "Hippo Camp: underwater, mud, or bank?"),
        ],
        display_names={
            "african-elephant": "Veldt elephant",
            "reticulated-giraffe": "Veldt giraffe",
            "sumatran-tiger": "Cat Country tiger",
            "western-lowland-gorilla": "Primate Canyon gorilla",
            "african-lion": "Cat Country lion",
            "african-penguin": "Penguin Rock penguin",
            "cheetah": "Cat Country cheetah",
            "nile-hippo": "Hippo Camp hippo",
            "two-toed-sloth": "Animals of the Night sloth",
            "galapagos-tortoise": "Herpetarium tortoise",
        },
        treasure=[
            "Find the African Veldt elephant herd",
            "Look up at a Veldt giraffe",
            "Find Cat Country Sumatran tiger stripes",
            "Watch the Primate Canyon gorilla family",
            "Hear a Cat Country lion — or wait quietly",
            "Watch a Penguin Rock bird zoom underwater",
            "Find a two-toed sloth after dark-house eyes adjust",
            "Pick a Memphis favorite — draw it later",
        ],
    )

    apply_kit(
        "miami-zoo",
        verified=False,
        tagline="Starter list: African elephants, then a Sumatran tiger and Bornean orangutan.",
        items=[
            item("african-elephant", zone="Africa", one="Official African elephants — look at that trunk.", core=True),
            item("sumatran-tiger", zone="Asia", one="Sumatran tiger — orange stripes in the trees.", core=True),
            item("orangutan", zone="Asia", one="Bornean orangutan — long arms in the trees.", core=True),
            item("western-lowland-gorilla", zone="Africa", one="Lowland gorilla family — who looks in charge?", core=True, label="Gorilla", note="Official: Lowland Gorilla / Western lowland gorillas."),
            item("chimpanzee", zone="Africa", one="Chimpanzee play and chatter.", core=True),
            item("koala", zone="Australia", one="Official koala — sleepy eucalyptus eater.", core=True),
            item("warthog", zone="Africa", one="Warthog — snout, tusks, and a trot.", core=False),
            item("galapagos-tortoise", zone="Reptiles", one="Galápagos tortoise — mid-step or statue?", core=False),
            item("caribbean-flamingo", zone="Florida", one="American flamingo flock — long legs in the shallows.", core=False, label="Flamingo", note="Official: American Flamingos (Phoenicopterus ruber). Soft Flamingo."),
            item("reticulated-giraffe", zone="Africa", one="Official reticulated giraffe — look up from the path.", core=False),
        ],
        bans=[
            ban("nile-hippo", "Official listing: pygmy hippopotamus, not Nile hippo."),
            ban("asian-small-clawed-otter", "Official map/adopt lists giant otter and North American river otter."),
        ],
        sources=[
            "https://www.zoomiami.org/animals",
            "https://www.zoomiami.org/zoo-map",
            "https://www.zoomiami.org/wildlife-guardians",
        ],
        notes="[2026-08-23] Wave 2b: official zoo-map + adopt/animals pages. Also keeps Asian elephants — do not fold into the African card. No invented verify date.",
        hunt_tag="Zoo Miami bonus · elephants + tiger + orangutan",
        hunt_finds=["western_lowland_gorilla", "chimpanzee", "koala", "warthog", "galapagos_tortoise", "caribbean_flamingo"],
        hunt_challenges=[
            ("mia_elephant", "African elephants: trunk busy or a full rest?"),
            ("mia_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
            ("mia_orang", "Orangutan: hands or feet doing the clever bit?"),
            ("mia_koala", "Koala: eyes open or a daytime nap?"),
        ],
        display_names={
            "african-elephant": "Zoo Miami African elephant",
            "sumatran-tiger": "Zoo Miami Sumatran tiger",
            "orangutan": "Bornean orangutan",
            "western-lowland-gorilla": "Zoo Miami gorilla",
            "chimpanzee": "Zoo Miami chimpanzee",
            "koala": "Zoo Miami koala",
            "warthog": "Zoo Miami warthog",
            "galapagos-tortoise": "Zoo Miami Galápagos tortoise",
            "caribbean-flamingo": "American flamingo",
            "reticulated-giraffe": "Zoo Miami giraffe",
        },
        treasure=[
            "Find the African elephant herd",
            "Find Sumatran tiger stripes in the trees",
            "Find orangutan long arms in the trees",
            "Watch the lowland gorilla family",
            "Watch chimps use their hands like tools",
            "Find a sleepy koala",
            "Count American flamingos on one leg",
            "Pick a Zoo Miami favorite — draw it later",
        ],
    )

    apply_kit(
        "milwaukee-zoo",
        verified=True,
        tagline="African savanna elephant, then a reticulated giraffe and Apes of Africa gorillas.",
        items=[
            item("african-elephant", zone="Adventure Africa", one="African savanna elephant — look at that trunk.", core=True),
            item("reticulated-giraffe", zone="Adventure Africa", one="Official reticulated giraffe — look up from the path.", core=True),
            item("western-lowland-gorilla", zone="Stearns Family Apes of Africa", one="Apes of Africa gorilla — who looks in charge?", core=True),
            item("african-lion", zone="Africa", one="African lion pride — listen for a roar.", core=True),
            item("cheetah", zone="Africa", one="Cheetah — tear marks, not a lion mane.", core=True),
            item("orangutan", zone="Primates", one="Orangutan — long arms in the trees.", core=True),
            item("nile-hippo", zone="Dohmen Hippo Haven", one="Hippo Haven — Hippopotamus at the water window.", core=False, label="Hippo", note="Official: Hippopotamus (common hippo, not pygmy). Soft Hippo."),
            item("zebra", zone="Africa", one="Plains zebra — pick one stripe set and draw it in the air.", core=False, label="Zebra", note="Official: Plains Zebra."),
            item("ostrich", zone="Africa", one="Ostrich — look at those legs.", core=False),
            item("red-panda", zone="Asia", one="Red panda — rusty and tree-high.", core=False),
        ],
        bans=[
            ban("african-penguin", "Official Meet Our Animals: Humboldt, rockhopper, and gentoo penguins — not African."),
            ban("sumatran-tiger", "Official: Amur Tiger, not Sumatran."),
            ban("chimpanzee", "Official Apes of Africa lists bonobos, not chimpanzees."),
            ban("ring-tailed-lemur", "Official list: red-ruffed lemur, not ring-tailed."),
            ban("galapagos-tortoise", "Official tortoises are African spurred / yellow-footed, not Galápagos."),
            ban("asian-small-clawed-otter", "Official: North American River Otter."),
        ],
        sources=[
            "https://milwaukeezoo.org/visit/meet-our-animals/",
            "https://milwaukeezoo.org/visit/meet-our-animals/african-savanna-elephant/",
            "https://milwaukeezoo.org/visit/meet-our-animals/reticulated-giraffe/",
            "https://milwaukeezoo.org/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (milwaukeezoo.org Meet Our Animals).",
        hunt_tag="Milwaukee bonus · Adventure Africa + Apes of Africa",
        hunt_finds=["african_lion", "cheetah", "orangutan", "nile_hippo", "zebra", "red_panda"],
        hunt_challenges=[
            ("mke_elephant", "Adventure Africa: trunk busy or a full rest?"),
            ("mke_giraffe", "Reticulated giraffe: count the spots you can see on one neck."),
            ("mke_gorilla", "Apes of Africa: who looks calmest?"),
            ("mke_hippo", "Hippo Haven: underwater, mud, or bank?"),
        ],
        display_names={
            "african-elephant": "Adventure Africa elephant",
            "reticulated-giraffe": "Milwaukee reticulated giraffe",
            "western-lowland-gorilla": "Apes of Africa gorilla",
            "african-lion": "Milwaukee lion",
            "cheetah": "Milwaukee cheetah",
            "orangutan": "Milwaukee orangutan",
            "nile-hippo": "Hippo Haven hippo",
            "zebra": "Plains zebra",
            "ostrich": "Milwaukee ostrich",
            "red-panda": "Milwaukee red panda",
        },
        treasure=[
            "Find the African savanna elephant",
            "Look up at a reticulated giraffe",
            "Watch the Apes of Africa gorilla family",
            "Hear an African lion — or wait quietly",
            "Spot a cheetah — tear marks, not a mane",
            "Find orangutan long arms in the trees",
            "Watch Hippo Haven from the water window",
            "Pick a Milwaukee favorite — draw it later",
        ],
    )

    apply_kit(
        "minnesota-zoo",
        verified=True,
        tagline="African penguins first, then a Northern Trail red panda and Tropics Trail lemurs — no giraffes or lions.",
        items=[
            item("african-penguin", zone="South Entry", one="3M Penguins of the African Coast — waddle, then zoom.", core=True),
            item("red-panda", zone="Northern Trail", one="Northern Trail red panda — rusty and tree-high.", core=True),
            item("ring-tailed-lemur", zone="Tropics Trail", one="Tropics Trail ring-tailed lemur — striped tail and a long stare.", core=True),
            item("two-toed-sloth", zone="Tropics Trail", one="Linne's two-toed sloth — hang and look twice.", core=True),
            item("shark", zone="Discovery Bay", one="Discovery Bay sand tiger and leopard sharks — watch the swim.", core=False),
        ],
        bans=[
            ban("sumatran-tiger", "Official animals list: Amur tiger on Northern Trail."),
            ban("reticulated-giraffe", "Minnesota Zoo does not list giraffes."),
            ban("african-elephant", "Minnesota Zoo does not list elephants."),
            ban("african-lion", "Minnesota Zoo does not list lions."),
            ban("zebra", "Minnesota Zoo does not list zebras."),
            ban("nile-hippo", "Not on the official animals list."),
            ban("western-lowland-gorilla", "Not on the official animals list."),
            ban("caribbean-flamingo", "Official list: Lesser Flamingo, not Caribbean."),
            ban("asian-small-clawed-otter", "Official: North American river otter (and a separate sea otter)."),
        ],
        sources=[
            "https://mnzoo.org/animals/",
            "https://mnzoo.org/blog/animals/african-penguin/",
            "https://mnzoo.org/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (mnzoo.org/animals complete directory). Shark is on the official zoo animals index (Discovery Bay).",
        hunt_tag="Minnesota bonus · penguins + red panda + Tropics Trail",
        hunt_finds=["two_toed_sloth", "shark"],
        hunt_challenges=[
            ("mn_penguin", "African penguin: watch one bird enter or leave the water."),
            ("mn_panda", "Red panda: climb or curl-up?"),
            ("mn_lemur", "Ring-tailed lemur: striped tail up or a long sit?"),
            ("mn_sloth", "Tropics Trail sloth: mid-reach or statue-still?"),
        ],
        display_names={
            "african-penguin": "African Coast penguin",
            "red-panda": "Northern Trail red panda",
            "ring-tailed-lemur": "Tropics Trail lemur",
            "two-toed-sloth": "Tropics Trail sloth",
            "shark": "Discovery Bay shark",
        },
        treasure=[
            "Watch an African penguin zoom underwater",
            "Find a rusty red panda on Northern Trail",
            "Find a Tropics Trail ring-tailed lemur",
            "Hang-and-look-twice at a two-toed sloth",
            "Watch a Discovery Bay shark swim past",
            "Point to a sleep spot on Tropics Trail",
            "Find a bright bird on the way to the penguins",
            "Pick a Minnesota Zoo favorite — draw it later",
        ],
    )

    apply_kit(
        "nashville-zoo",
        verified=True,
        tagline="Sumatran tigers first, then a two-toed sloth and Caribbean flamingos — the elephant herd has left.",
        items=[
            item("sumatran-tiger", zone="Our animals", one="Sumatran tiger — orange stripes and a keeper-chat favorite.", core=True),
            item("two-toed-sloth", zone="Our animals", one="Two-toed sloth — hang and look twice.", core=True),
            item("caribbean-flamingo", zone="Our animals", one="Caribbean flamingo flock — long legs in the shallows.", core=True),
            item("reticulated-giraffe", zone="Leopard Forest", one="Leopard Forest Masai giraffes — look up from the path.", core=True, label="Giraffe", note="Official Our Animals + Leopard Forest: Masai Giraffe. Soft Giraffe."),
            item("ring-tailed-lemur", zone="Our animals", one="Ring-tailed lemur — striped tail and a long stare.", core=True),
            item("galapagos-tortoise", zone="Our animals", one="Galápagos tortoise — mid-step or statue?", core=True),
            item("zebra", zone="Our animals", one="Plains zebra — pick one stripe set and draw it in the air.", core=False, label="Zebra", note="Official: Plains Zebra."),
            item("ostrich", zone="Our animals", one="Ostrich — look at those legs.", core=False),
            item("red-panda", zone="Our animals", one="Red panda (returns in fall) — rusty and tree-high.", core=False, note="Official Our Animals: Red Panda (Returns in Fall)."),
        ],
        bans=[
            ban("african-elephant", "Official Our Animals does not list elephants; herd left and the former exhibit holds white rhinos."),
            ban("african-penguin", "Official: the zoo does not have African penguins now."),
            ban("cheetah", "Somaliland conservation mentions only — not on Our Animals."),
            ban("nile-hippo", "Not on the official Our Animals list."),
            ban("african-lion", "Not on the official Our Animals list."),
            ban("western-lowland-gorilla", "Not on the official Our Animals list."),
        ],
        sources=[
            "https://www.nashvillezoo.org/our-animals",
            "https://www.nashvillezoo.org/leopard-forest",
            "https://www.nashvillezoo.org/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (nashvillezoo.org/our-animals).",
        hunt_tag="Nashville bonus · tiger + sloth + flamingo",
        hunt_finds=["reticulated_giraffe", "ring_tailed_lemur", "galapagos_tortoise", "zebra", "ostrich", "red_panda"],
        hunt_challenges=[
            ("nsh_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
            ("nsh_sloth", "Two-toed sloth: mid-reach or statue-still?"),
            ("nsh_flam", "Caribbean flamingos: more than half on one leg?"),
            ("nsh_giraffe", "Masai giraffe: count the spots you can see on one neck."),
        ],
        display_names={
            "sumatran-tiger": "Nashville Sumatran tiger",
            "two-toed-sloth": "Nashville sloth",
            "caribbean-flamingo": "Nashville Caribbean flamingo",
            "reticulated-giraffe": "Leopard Forest giraffe",
            "ring-tailed-lemur": "Nashville lemur",
            "galapagos-tortoise": "Nashville Galápagos tortoise",
            "zebra": "Plains zebra",
            "ostrich": "Nashville ostrich",
            "red-panda": "Nashville red panda",
        },
        treasure=[
            "Find Sumatran tiger stripes",
            "Hang-and-look-twice at a two-toed sloth",
            "Count Caribbean flamingos on one leg",
            "Look up at a Leopard Forest giraffe",
            "Find a ring-tailed lemur’s striped tail",
            "Find a Galápagos tortoise mid-step or statue-still",
            "Draw one plains zebra stripe set in the air",
            "Pick a Nashville favorite — draw it later",
        ],
    )

    apply_kit(
        "north-carolina-zoo",
        verified=True,
        tagline="African elephants, then western lowland gorillas and African lions — Asia continent is not open yet.",
        items=[
            item("african-elephant", zone="Africa", one="African elephant habitat — look at that trunk.", core=True),
            item("western-lowland-gorilla", zone="Africa", one="Western lowland gorilla family — who looks in charge?", core=True),
            item("african-lion", zone="Africa", one="African lion — listen for a roar.", core=True),
            item("chimpanzee", zone="Africa", one="Chimp play and chatter on the Africa loop.", core=True),
            item("reticulated-giraffe", zone="Africa", one="Africa giraffe — look up from the path.", core=True, label="Giraffe", note="Official animals list: Giraffe. Soft Giraffe."),
            item("zebra", zone="Africa", one="Africa zebra — pick one stripe set and draw it in the air.", core=True),
            item("ostrich", zone="Africa", one="Africa ostrich — look at those legs.", core=False),
        ],
        bans=[
            ban("sumatran-tiger", "Asia continent is not open yet; tigers are not on the current official animals list."),
            ban("nile-hippo", "Not on the official animals list."),
            ban("african-penguin", "Not on the official animals list."),
            ban("cheetah", "Not on the official animals list."),
            ban("ring-tailed-lemur", "Official list: red-ruffed lemur, not ring-tailed."),
            ban("galapagos-tortoise", "Not on the official animals list."),
        ],
        sources=[
            "https://www.nczoo.org/wildlife/animals",
            "https://www.nczoo.org/experiences",
            "https://www.nczoo.org/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (nczoo.org/wildlife/animals).",
        hunt_tag="North Carolina bonus · Africa loop",
        hunt_finds=["chimpanzee", "reticulated_giraffe", "zebra", "ostrich"],
        hunt_challenges=[
            ("nc_elephant", "African elephant: trunk busy or a full rest?"),
            ("nc_gorilla", "Gorilla family: who looks calmest?"),
            ("nc_lion", "Lions: roar or a quiet pride?"),
            ("nc_chimp", "Chimps: spot hands used like tools."),
        ],
        display_names={
            "african-elephant": "NC Zoo elephant",
            "western-lowland-gorilla": "NC Zoo gorilla",
            "african-lion": "NC Zoo lion",
            "chimpanzee": "NC Zoo chimpanzee",
            "reticulated-giraffe": "NC Zoo giraffe",
            "zebra": "NC Zoo zebra",
            "ostrich": "NC Zoo ostrich",
        },
        treasure=[
            "Find the African elephant habitat",
            "Watch the western lowland gorilla family",
            "Hear an African lion — or wait quietly",
            "Watch chimps use their hands like tools",
            "Look up at an Africa giraffe",
            "Draw one zebra stripe set in the air",
            "Look at an ostrich’s legs — biggest bird",
            "Pick an NC Zoo favorite — draw it later",
        ],
    )

    apply_kit(
        "omaha-henry-doorly",
        verified=False,
        tagline="Starter zoo-side list: African elephants, Hubbard gorillas, then orangutans — no aquarium cards.",
        items=[
            item("african-elephant", zone="Scott African Grasslands", one="African elephant herd — look at that trunk.", core=True),
            item("western-lowland-gorilla", zone="Hubbard Gorilla Valley", one="Hubbard gorillas — who looks in charge?", core=True),
            item("orangutan", zone="Hubbard Orangutan Forest", one="Hubbard orangutans — long arms in the trees.", core=True),
            item("cheetah", zone="African Grasslands", one="Cheetah exhibit — tear marks, not a lion mane.", core=True),
            item("african-lion", zone="Hawks Foundation Lion's Pride", one="Lion's Pride — listen for a roar.", core=True, label="Lion", note="Official: African lions. Soft Lion."),
            item("reticulated-giraffe", zone="Hawkins Giraffe Encounter", one="Giraffe Encounter — look up from the path.", core=True, label="Giraffe", note="Official grasslands: giraffes. Soft Giraffe."),
            item("zebra", zone="Grewcock Elephant and Zebra Habitat", one="Plains zebra beside the elephant habitat.", core=False, label="Zebra", note="Official: plains zebra."),
            item("ostrich", zone="African Grasslands", one="Grasslands ostrich roaming with giraffes.", core=False),
            item("ring-tailed-lemur", zone="Hubbard Expedition Madagascar", one="Madagascar ring-tailed lemur — striped tail.", core=False),
            item("two-toed-sloth", zone="Kingdoms of the Night", one="Hoffmann's two-toed sloth — hang and look twice.", core=False, note="Official adopt list: Hoffmann's Two-toed Sloth in Kingdoms of the Night (zoo-side nocturnal)."),
        ],
        bans=[
            ban("sumatran-tiger", "Official Asian Highlands: Amur tigers."),
            ban("nile-hippo", "Official Lied Jungle: pygmy hippos, not Nile hippo."),
            ban("african-penguin", "King, gentoo, and rockhopper penguins are in Scott Aquarium — not a zoo-side card."),
            ban("shark", "Shark Tunnel is Scott Aquarium — not a zoo-side card for this kit."),
            ban("asian-small-clawed-otter", "Adopt copy places Asian small-clawed otter in the Aquarium."),
        ],
        sources=[
            "https://www.omahazoo.com/",
            "https://www.omahazoo.com/scott-african-grasslands",
            "https://www.omahazoo.com/hubbard-gorilla-valley",
            "https://www.omahazoo.com/hubbard-orangutan-forest",
            "https://www.omahazoo.com/plan-your-visit",
        ],
        notes="[2026-08-23] Wave 2b: zoo-side exhibit pages only. Scott Aquarium shark/penguin/stingray dropped. No invented verify date.",
        hunt_tag="Omaha bonus · Grasslands + Hubbard apes (zoo-side)",
        hunt_finds=["cheetah", "african_lion", "reticulated_giraffe", "zebra", "ostrich", "ring_tailed_lemur"],
        hunt_challenges=[
            ("oma_elephant", "African Grasslands: trunk busy or a full rest?"),
            ("oma_gorilla", "Hubbard Gorilla Valley: who looks calmest?"),
            ("oma_orang", "Orangutan Forest: hands or feet doing the clever bit?"),
            ("oma_lion", "Lion's Pride: roar or a quiet pride?"),
        ],
        display_names={
            "african-elephant": "Grasslands elephant",
            "western-lowland-gorilla": "Hubbard gorilla",
            "orangutan": "Hubbard orangutan",
            "cheetah": "Grasslands cheetah",
            "african-lion": "Lion's Pride lion",
            "reticulated-giraffe": "Giraffe Encounter giraffe",
            "zebra": "Grewcock zebra",
            "ostrich": "Grasslands ostrich",
            "ring-tailed-lemur": "Madagascar lemur",
            "two-toed-sloth": "Kingdoms of the Night sloth",
        },
        treasure=[
            "Find the African elephant herd",
            "Watch the Hubbard gorilla family",
            "Find orangutan long arms in Hubbard Forest",
            "Spot a cheetah — tear marks, not a mane",
            "Hear Lion's Pride — or wait quietly",
            "Look up at Giraffe Encounter",
            "Find a Madagascar ring-tailed lemur",
            "Pick an Omaha zoo-side favorite — draw it later",
        ],
    )

    apply_kit(
        "philadelphia-zoo",
        verified=False,
        tagline="Starter list: Big Cat Falls lions, PECO gorillas, then a reticulated giraffe.",
        items=[
            item("african-lion", zone="Big Cat Falls", one="Big Cat Falls African lion — listen for a roar.", core=True),
            item("western-lowland-gorilla", zone="PECO Primate Reserve", one="PECO gorilla family — who looks in charge?", core=True),
            item("reticulated-giraffe", zone="African Plains", one="Official reticulated giraffe — look up from the path.", core=True),
            item("nile-hippo", zone="Hippo", one="Hippopotamus amphibius — watch the water window.", core=True, label="Hippo", note="Official: Hippopotamus / Hippopotamus amphibius. Soft Hippo."),
            item("orangutan", zone="PECO Primate Reserve", one="PECO orangutan — long arms in the trees.", core=True),
            item("caribbean-flamingo", zone="Flamingo Cove", one="Flamingo Cove — Caribbean and African greater flamingos.", core=True),
            item("ring-tailed-lemur", zone="Lemur Island", one="Lemur Island ring-tailed lemurs — striped tail.", core=False),
            item("galapagos-tortoise", zone="Reptile and Amphibian House", one="Galápagos tortoise — mid-step or statue?", core=False),
            item("cheetah", zone="Animals", one="Cheetah on the official adopt list — tear marks, not a mane.", core=False, presence="high", note="Official adopt list names Cheetah."),
            item("red-panda", zone="Water is Life", one="Exhibits page still lists inquisitive red pandas.", core=False, presence="high", note="Official exhibits page lists red pandas; confirm yard on arrival."),
        ],
        bans=[
            ban("sumatran-tiger", "Official listing: Amur Tiger."),
            ban("african-elephant", "Philadelphia Zoo ended elephants in 2009."),
            ban("african-penguin", "Official exhibits: Humboldt / Magellanic penguins, not African."),
            ban("asian-small-clawed-otter", "Official: giant river otters, not Asian small-clawed."),
        ],
        sources=[
            "https://philadelphiazoo.org/animals/",
            "https://www.philadelphiazoo.org/animals/african-lion/",
            "https://www.philadelphiazoo.org/animals/western-lowland-gorilla/",
            "https://www.philadelphiazoo.org/animals/reticulated-giraffe/",
            "https://www.philadelphiazoo.org/exhibits/",
        ],
        notes="[2026-08-23] Wave 2b: official species + exhibits/adopt pages; no complete A–Z. No invented verify date.",
        hunt_tag="Philadelphia bonus · Big Cat Falls + PECO + African Plains",
        hunt_finds=["nile_hippo", "orangutan", "caribbean_flamingo", "ring_tailed_lemur", "galapagos_tortoise", "red_panda"],
        hunt_challenges=[
            ("phl_lion", "Big Cat Falls: roar or a quiet pride?"),
            ("phl_gorilla", "PECO: who looks calmest in the gorilla family?"),
            ("phl_giraffe", "Reticulated giraffe: count the spots you can see on one neck."),
            ("phl_flam", "Flamingo Cove: more than half on one leg?"),
        ],
        display_names={
            "african-lion": "Big Cat Falls lion",
            "western-lowland-gorilla": "PECO gorilla",
            "reticulated-giraffe": "African Plains giraffe",
            "nile-hippo": "Philadelphia hippo",
            "orangutan": "PECO orangutan",
            "caribbean-flamingo": "Flamingo Cove flamingo",
            "ring-tailed-lemur": "Lemur Island lemur",
            "galapagos-tortoise": "Reptile House tortoise",
            "cheetah": "Philadelphia cheetah",
            "red-panda": "Philadelphia red panda",
        },
        treasure=[
            "Hear a Big Cat Falls lion — or wait quietly",
            "Watch the PECO gorilla family",
            "Look up at a reticulated giraffe",
            "Watch the hippo at the water window",
            "Find orangutan long arms at PECO",
            "Count Flamingo Cove birds on one leg",
            "Find a Lemur Island striped tail",
            "Pick a Philadelphia favorite — draw it later",
        ],
    )

    apply_kit(
        "phoenix-zoo",
        verified=False,
        tagline="Starter list: Sumatran tiger, Bornean orangutan, then African penguins — Asian elephants, not African.",
        items=[
            item("sumatran-tiger", zone="Animals", one="Sumatran tiger — orange stripes in the trees.", core=True),
            item("orangutan", zone="Animals", one="Bornean orangutan — long arms in the trees.", core=True),
            item("african-penguin", zone="Animals", one="African penguin — waddle, then zoom in the water.", core=True),
            item("cheetah", zone="Animals", one="Cheetah — tear marks, not a lion mane.", core=True),
            item("african-lion", zone="Animals", one="African lion pride — listen for a roar.", core=True),
            item("two-toed-sloth", zone="Animals", one="Linne's two-toed sloth — hang and look twice.", core=True),
            item("zebra", zone="Animals", one="Grevy's zebra — every stripe set is unique.", core=False, label="Zebra", note="Official: Grevy's Zebra."),
            item("reticulated-giraffe", zone="Animals", one="Masai giraffe — look up from the path.", core=False, label="Giraffe", note="Official animals page: Masai Giraffe. Soft Giraffe."),
        ],
        bans=[
            ban("african-elephant", "Official: Asian Elephant (currently not on view)."),
            ban("western-lowland-gorilla", "No gorillas on the official animals pages reviewed."),
            ban("nile-hippo", "Not on the official animals pages reviewed."),
            ban("galapagos-tortoise", "Wrong tortoise species vs official list."),
            ban("caribbean-flamingo", "Official flamingo page names Chilean and greater flamingos, not Caribbean."),
            ban("ring-tailed-lemur", "Official: ruffed lemurs, not ring-tailed."),
            ban("ostrich", "Official ostrich page: not currently on view."),
        ],
        sources=[
            "https://www.phoenixzoo.org/explore/animals/",
            "https://www.phoenixzoo.org/explore/animals/sumatran-tiger-2/",
            "https://www.phoenixzoo.org/explore/animals/african-penguin/",
            "https://www.phoenixzoo.org/explore/animals/bornean-orangutan/",
        ],
        notes="[2026-08-23] Wave 2b: official per-species pages; index says not all animals are shown. No invented verify date.",
        hunt_tag="Phoenix bonus · tiger + orangutan + African penguin",
        hunt_finds=["cheetah", "african_lion", "two_toed_sloth", "zebra", "reticulated_giraffe"],
        hunt_challenges=[
            ("phx_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
            ("phx_orang", "Orangutan: hands or feet doing the clever bit?"),
            ("phx_penguin", "African penguin: watch one bird enter or leave the water."),
            ("phx_sloth", "Linne sloth: mid-reach or statue-still?"),
        ],
        display_names={
            "sumatran-tiger": "Phoenix Sumatran tiger",
            "orangutan": "Bornean orangutan",
            "african-penguin": "Phoenix African penguin",
            "cheetah": "Phoenix cheetah",
            "african-lion": "Phoenix lion",
            "two-toed-sloth": "Linne sloth",
            "zebra": "Grevy's zebra",
            "reticulated-giraffe": "Masai giraffe",
        },
        treasure=[
            "Find Sumatran tiger stripes",
            "Find orangutan long arms in the trees",
            "Watch an African penguin zoom underwater",
            "Spot a cheetah — tear marks, not a mane",
            "Hear an African lion — or wait quietly",
            "Hang-and-look-twice at a two-toed sloth",
            "Draw one Grevy's zebra stripe set in the air",
            "Pick a Phoenix favorite — draw it later",
        ],
    )

    apply_kit(
        "pittsburgh-zoo",
        verified=False,
        tagline="Starter zoo-side list: African elephants, then African lions and a red panda — no PPG Aquarium cards.",
        items=[
            item("african-elephant", zone="Africa", one="African elephant — look at that trunk.", core=True),
            item("african-lion", zone="Africa", one="African lion pride — listen for a roar.", core=True),
            item("red-panda", zone="Asia", one="Red panda — rusty and tree-high.", core=True),
            item("cheetah", zone="Africa", one="Cheetah — tear marks, not a lion mane.", core=True),
            item("western-lowland-gorilla", zone="Forest", one="Western lowland gorillas — who looks in charge?", core=True, note="Official 2026 news names western lowland gorillas Moka and Ibo."),
            item("reticulated-giraffe", zone="Africa", one="Masai giraffe — look up from the path.", core=True, label="Giraffe", note="Official animals list: Masai Giraffe. Soft Giraffe."),
            item("zebra", zone="Africa", one="Grant's zebra — pick one stripe set and draw it in the air.", core=False, label="Zebra", note="Official: Grant's Zebra."),
            item("ostrich", zone="Africa", one="Ostrich — look at those legs.", core=False),
            item("caribbean-flamingo", zone="Birds", one="Flamingo flock — long legs in the shallows.", core=False, label="Flamingo", note="Official animals list: Flamingo (species not named). Soft Flamingo."),
        ],
        bans=[
            ban("sumatran-tiger", "Official animals list: Amur Tiger."),
            ban("nile-hippo", "Official animals list: Pygmy Hippo, not Nile hippo."),
            ban("galapagos-tortoise", "Official animals list: Aldabra Tortoise."),
            ban("african-penguin", "Official: Gentoo and Macaroni penguins, not African."),
            ban("shark", "Blacktip reef shark is listed under PPG Aquarium — not a zoo-side card."),
            ban("asian-small-clawed-otter", "Official: North American River Otter."),
        ],
        sources=[
            "https://www.pittsburghzoo.org/our-animals/",
            "https://www.pittsburghzoo.org/animals/",
            "https://www.pittsburghzoo.org/animal/elephant-african/",
            "https://www.pittsburghzoo.org/animal/red-panda/",
        ],
        notes="[2026-08-23] Wave 2b: zoo-side official animals pages (list still incomplete). PPG Aquarium shark/jelly/turtle/ray dropped. No invented verify date.",
        hunt_tag="Pittsburgh bonus · Africa + red panda (zoo-side)",
        hunt_finds=["cheetah", "western_lowland_gorilla", "reticulated_giraffe", "zebra", "ostrich", "caribbean_flamingo"],
        hunt_challenges=[
            ("pit_elephant", "African elephant: trunk busy or a full rest?"),
            ("pit_lion", "Lions: roar or a quiet pride?"),
            ("pit_panda", "Red panda: climb or curl-up?"),
            ("pit_giraffe", "Masai giraffe: count the spots you can see on one neck."),
        ],
        display_names={
            "african-elephant": "Pittsburgh African elephant",
            "african-lion": "Pittsburgh lion",
            "red-panda": "Pittsburgh red panda",
            "cheetah": "Pittsburgh cheetah",
            "western-lowland-gorilla": "Pittsburgh gorilla",
            "reticulated-giraffe": "Masai giraffe",
            "zebra": "Grant's zebra",
            "ostrich": "Pittsburgh ostrich",
            "caribbean-flamingo": "Pittsburgh flamingo",
        },
        treasure=[
            "Find the African elephant",
            "Hear an African lion — or wait quietly",
            "Find a rusty red panda",
            "Spot a cheetah — tear marks, not a mane",
            "Watch the gorilla family",
            "Look up at a Masai giraffe",
            "Draw one Grant's zebra stripe set in the air",
            "Pick a Pittsburgh zoo-side favorite — draw it later",
        ],
    )

    apply_kit(
        "point-defiance-zoo",
        verified=False,
        tagline="Starter zoo-side list: Sumatran tiger, Asian small-clawed otter, then ring-tailed lemurs — no aquarium cards.",
        items=[
            item("sumatran-tiger", zone="Asian Forest Sanctuary", one="Asian Forest Sumatran tiger (Bintang) — orange stripes in the trees.", core=True),
            item("asian-small-clawed-otter", zone="Asian Forest Sanctuary", one="Asian Forest otters — smallest otter, biggest splash.", core=True),
            item("ring-tailed-lemur", zone="Kids' Zone", one="Kids' Zone ring-tailed lemurs — striped tail and a long stare.", core=True, note="Official story names ring-tailed lemurs Bobbi and Freedom; Kids' Zone also has ruffed lemurs."),
        ],
        bans=[
            ban("african-penguin", "Official Penguin Point: Magellanic penguins, not African."),
            ban("african-elephant", "Former elephant barn is being converted; historical elephant was Asian."),
            ban("reticulated-giraffe", "Not on official habitat animal lists."),
            ban("zebra", "Not on official habitat animal lists."),
            ban("shark", "Sharks are Pacific Seas / Tropical Reef aquarium habitats — not a zoo-side card."),
            ban("red-panda", "Not on the official Asian Forest animal list."),
        ],
        sources=[
            "https://www.pdza.org/animals/",
            "https://www.pdza.org/animals/asian-forest-sanctuary/",
            "https://www.pdza.org/animals/rocky-shores/penguin-point/",
            "https://www.pdza.org/animals/kids-zone/",
        ],
        notes="[2026-08-23] Wave 2b: zoo-side habitat pages only. Aquarium shark/jelly/turtle/ray dropped. Short published-card list. No invented verify date.",
        hunt_tag="Point Defiance bonus · Asian Forest + Kids' Zone (zoo-side)",
        hunt_finds=[],
        hunt_challenges=[
            ("pdza_tiger", "Sumatran tiger: count stripe clusters on one shoulder."),
            ("pdza_otter", "Asian small-clawed otter: find the splashiest 10 seconds."),
            ("pdza_lemur", "Ring-tailed lemur: striped tail up or a long sit?"),
            ("pdza_map", "Point to Asian Forest on a map, then Kids' Zone."),
        ],
        display_names={
            "sumatran-tiger": "Asian Forest tiger",
            "asian-small-clawed-otter": "Asian Forest otter",
            "ring-tailed-lemur": "Kids' Zone lemur",
        },
        treasure=[
            "Find Sumatran tiger stripes in Asian Forest",
            "Watch Asian small-clawed otters splash",
            "Find a Kids' Zone ring-tailed lemur",
            "Point to Asian Forest on a zoo map",
            "Find a sleep spot in Asian Forest",
            "Listen for a tiger or otter sound",
            "Compare a striped tail to tiger stripes",
            "Pick a Point Defiance zoo-side favorite — draw it later",
        ],
    )

    apply_kit(
        "san-diego-safari-park",
        verified=True,
        tagline="Elephant Valley first, then a giraffe and Tiger Trail — not the Zoo’s panda path.",
        items=[
            item("african-elephant", zone="Elephant Valley", one="African elephant herd — two large habitat areas to roam.", core=True),
            item("reticulated-giraffe", zone="Africa field", one="Safari Park giraffe — look up from the tram or walk.", core=True, label="Giraffe", note="Official animals-gardens card: GIRAFFE. Soft Giraffe."),
            item("sumatran-tiger", zone="Tiger Trail", one="Tiger Trail Sumatran tiger — the toughest to spot.", core=True),
            item("cheetah", zone="Africa", one="Cheetah — built to sprint across short distances.", core=True),
            item("western-lowland-gorilla", zone="Gorilla Forest", one="Gorilla Forest — largest of all primates.", core=True, label="Gorilla", note="Official animals-gardens card: GORILLA. Soft Gorilla."),
            item("african-lion", zone="Lion camp", one="Lion camp — short bursts of action, then a long rest.", core=True, label="Lion", note="Official animals-gardens card: LION. Soft Lion."),
            item("zebra", zone="Africa field", one="Grevy's zebra — every stripe set is unique.", core=False, label="Zebra", note="Official: GREVY'S ZEBRA."),
            item("caribbean-flamingo", zone="Flamingo", one="Largest greater-flamingo flock in North America — long legs in the shallows.", core=False, label="Flamingo", note="Official animals-gardens card: FLAMINGO. Soft Flamingo."),
        ],
        bans=[
            ban("giant-panda", "Giant pandas are at San Diego Zoo, not Safari Park."),
            ban("koala", "Walkabout Australia does not list koala as a park animal; koalas are at the Zoo."),
            ban("nile-hippo", "Not on the official animals-gardens list."),
            ban("ostrich", "Not on the current official animals-gardens cards."),
            ban("warthog", "Official list names red river hog, not warthog."),
        ],
        sources=[
            "https://sdzsafaripark.org/animals-gardens",
            "https://sdzsafaripark.org/animals/elephant",
            "https://sdzsafaripark.org/animals/sumatran-tiger",
            "https://sdzsafaripark.org/elephant-valley",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (sdzsafaripark.org/animals-gardens). safari_zoo — do not copy San Diego Zoo panda→koala→elephant.",
        hunt_tag="Safari Park bonus · Elephant Valley + Tiger Trail + Africa field",
        hunt_finds=["cheetah", "western_lowland_gorilla", "african_lion", "zebra", "caribbean_flamingo"],
        hunt_challenges=[
            ("ssp_elephant", "Elephant Valley: trunk busy or a full rest?"),
            ("ssp_giraffe", "Giraffe: count the spots you can see on one neck."),
            ("ssp_tiger", "Tiger Trail: how long until you spot stripes?"),
            ("ssp_cheetah", "Cheetah: statue score 1–10 after 20 quiet seconds."),
        ],
        display_names={
            "african-elephant": "Elephant Valley elephant",
            "reticulated-giraffe": "Safari Park giraffe",
            "sumatran-tiger": "Tiger Trail tiger",
            "cheetah": "Safari Park cheetah",
            "western-lowland-gorilla": "Gorilla Forest gorilla",
            "african-lion": "Safari Park lion",
            "zebra": "Grevy's zebra",
            "caribbean-flamingo": "Safari Park flamingo",
        },
        treasure=[
            "Find the Elephant Valley African elephant herd",
            "Look up at a Safari Park giraffe",
            "Spot Sumatran tiger stripes on Tiger Trail",
            "Find a cheetah — built to sprint",
            "Watch the Gorilla Forest family",
            "Hear a lion — or wait through a long rest",
            "Draw one Grevy's zebra stripe set in the air",
            "Pick a Safari Park favorite — draw it later",
        ],
    )

    apply_kit(
        "tampa-zoo",
        verified=True,
        tagline="African elephants, then African penguins and a Queensland koala — pygmy hippos, not Nile.",
        items=[
            item("african-elephant", zone="Africa", one="Official African elephant — look at that trunk.", core=True),
            item("african-penguin", zone="Africa", one="African penguin — waddle, then zoom in the water.", core=True),
            item("koala", zone="Australia", one="Queensland koala — sleepy eucalyptus eater.", core=True),
            item("orangutan", zone="Asia", one="Bornean orangutans — long arms in the trees.", core=True),
            item("caribbean-flamingo", zone="Birds", one="Caribbean flamingo flock — long legs in the shallows.", core=True),
            item("galapagos-tortoise", zone="Reptiles", one="Galápagos giant tortoise — mid-step or statue?", core=True),
            item("ring-tailed-lemur", zone="Madagascar", one="Ring-tailed lemur — striped tail and a long stare.", core=False),
            item("reticulated-giraffe", zone="Africa", one="Masai giraffe — look up from the path.", core=False, label="Giraffe", note="Official animals list: Masai Giraffe. Soft Giraffe."),
        ],
        bans=[
            ban("nile-hippo", "Official animals list: Pygmy Hippopotamus, not Nile hippo."),
            ban("sumatran-tiger", "Official animals list: Malayan Tiger, not Sumatran."),
            ban("asian-small-clawed-otter", "Official: North American River Otter."),
            ban("african-lion", "Not on the official animals list."),
            ban("western-lowland-gorilla", "Not on the official animals list."),
            ban("zebra", "Not on the official animals list."),
        ],
        sources=[
            "https://zootampa.org/visit/animals/",
            "https://zootampa.org/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (zootampa.org/visit/animals). Manatee/Florida panther omitted — no published cards.",
        hunt_tag="ZooTampa bonus · elephant + penguin + koala",
        hunt_finds=["orangutan", "caribbean_flamingo", "galapagos_tortoise", "ring_tailed_lemur", "reticulated_giraffe"],
        hunt_challenges=[
            ("tpa_elephant", "African elephant: trunk busy or a full rest?"),
            ("tpa_penguin", "African penguin: watch one bird enter or leave the water."),
            ("tpa_koala", "Queensland koala: eyes open or a daytime nap?"),
            ("tpa_flam", "Caribbean flamingos: more than half on one leg?"),
        ],
        display_names={
            "african-elephant": "ZooTampa African elephant",
            "african-penguin": "ZooTampa African penguin",
            "koala": "Queensland koala",
            "orangutan": "Bornean orangutan",
            "caribbean-flamingo": "Caribbean flamingo",
            "galapagos-tortoise": "Galápagos tortoise",
            "ring-tailed-lemur": "ZooTampa lemur",
            "reticulated-giraffe": "Masai giraffe",
        },
        treasure=[
            "Find the African elephant",
            "Watch an African penguin zoom underwater",
            "Find a sleepy Queensland koala",
            "Find orangutan long arms in the trees",
            "Count Caribbean flamingos on one leg",
            "Find a Galápagos tortoise mid-step or statue-still",
            "Find a ring-tailed lemur’s striped tail",
            "Pick a ZooTampa favorite — draw it later",
        ],
    )

    apply_kit(
        "woodland-park-zoo",
        verified=True,
        tagline="Gorillas first, then Asian small-clawed otters and ring-tailed lemurs — Humboldt penguins, not African.",
        items=[
            item("western-lowland-gorilla", zone="Tropical Rain Forest", one="Two gorilla troops — who looks in charge?", core=True, label="Gorilla", note="Official animals map: Gorilla. Soft Gorilla."),
            item("asian-small-clawed-otter", zone="Tropical Asia", one="Asian small-clawed otter — smallest otter, biggest splash.", core=True),
            item("ring-tailed-lemur", zone="Tropics", one="Ring-tailed lemur — striped tail and a long stare.", core=True),
            item("african-lion", zone="African Savanna", one="African lions — listen for a roar.", core=True),
            item("orangutan", zone="Tropical Asia", one="Orangutan — long arms in the trees.", core=True),
            item("red-panda", zone="Temperate Forest", one="Red panda — rusty and tree-high.", core=True),
            item("reticulated-giraffe", zone="African Savanna", one="Savanna giraffe — look up from the path.", core=False, label="Giraffe", note="Official animals map: Giraffe. Soft Giraffe."),
            item("zebra", zone="African Savanna", one="Savanna zebra — pick one stripe set and draw it in the air.", core=False),
            item("ostrich", zone="African Savanna", one="Savanna ostrich — look at those legs.", core=False),
        ],
        bans=[
            ban("african-penguin", "Official: Humboldt Penguin, not African."),
            ban("sumatran-tiger", "Official: Malayan Tiger, not Sumatran."),
            ban("galapagos-tortoise", "Official: Aldabra Tortoise, not Galápagos."),
            ban("caribbean-flamingo", "Official exhibit: Chilean Flamingo, not Caribbean."),
            ban("african-elephant", "Not on the official animals map."),
            ban("nile-hippo", "Not on the official animals map."),
            ban("cheetah", "Not on the official animals map."),
            ban("two-toed-sloth", "Official listing is sloth bear, not a two-toed sloth."),
        ],
        sources=[
            "https://zoo.org/animals/",
            "https://map.zoo.org/place-types/150-animals",
            "https://zoo.org/rainforest/",
            "https://www.zoo.org/",
        ],
        notes="[2026-08-23] Official-source Wave 2b public list pass (zoo.org/animals + map.zoo.org).",
        hunt_tag="Woodland Park bonus · gorillas + otters + lemurs",
        hunt_finds=["african_lion", "orangutan", "red_panda", "reticulated_giraffe", "zebra", "ostrich"],
        hunt_challenges=[
            ("wpz_gorilla", "Gorilla troop: who looks in charge?"),
            ("wpz_otter", "Asian small-clawed otter: find the splashiest 10 seconds."),
            ("wpz_lemur", "Ring-tailed lemur: striped tail up or a long sit?"),
            ("wpz_lion", "African lions: roar or a quiet pride?"),
        ],
        display_names={
            "western-lowland-gorilla": "Rain Forest gorilla",
            "asian-small-clawed-otter": "Tropical Asia otter",
            "ring-tailed-lemur": "Woodland Park lemur",
            "african-lion": "Savanna lion",
            "orangutan": "Tropical Asia orangutan",
            "red-panda": "Temperate Forest red panda",
            "reticulated-giraffe": "Savanna giraffe",
            "zebra": "Savanna zebra",
            "ostrich": "Savanna ostrich",
        },
        treasure=[
            "Find a gorilla troop in the Rain Forest",
            "Watch Asian small-clawed otters splash",
            "Find a ring-tailed lemur’s striped tail",
            "Hear an African lion — or wait quietly",
            "Find orangutan long arms in Tropical Asia",
            "Find a rusty red panda in Temperate Forest",
            "Look up at a Savanna giraffe",
            "Pick a Woodland Park favorite — draw it later",
        ],
    )


if __name__ == "__main__":
    main()
