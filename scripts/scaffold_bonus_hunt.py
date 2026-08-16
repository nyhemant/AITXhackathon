#!/usr/bin/env python3
"""Scaffold or apply bonus_hunt packs for Field Trip Kit venues.

Usage:
  python3 scripts/scaffold_bonus_hunt.py --slug fort-worth-zoo --write
  python3 scripts/scaffold_bonus_hunt.py --all --write
  python3 scripts/scaffold_bonus_hunt.py --all --write --only-missing
  python3 scripts/scaffold_bonus_hunt.py --sync-file   # venues → bonus-hunts.json
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENUE_DIR = ROOT / "static/field-pack/data/venues"
BONUS_FILE = ROOT / "static/field-pack/data/bonus-hunts.json"
TODAY = date.today().isoformat()

PRESENCE_OK = {"verified", "high"}
# For partial/owner venues without presence, allow unset
PRESENCE_BLOCK = {"absent", "template", "medium"}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def save(p: Path, data: dict) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def item_ok(it: dict, venue: dict) -> bool:
    if not it or not it.get("id"):
        return False
    p = str(it.get("presence") or "").lower()
    if p in PRESENCE_BLOCK:
        return False
    if p in PRESENCE_OK:
        return True
    conf = venue.get("list_confidence") or ""
    if conf == "audited":
        return True
    if conf == "template":
        return False
    # partial: allow unless blocked
    return p not in PRESENCE_BLOCK


def safe_items(venue: dict) -> list[dict]:
    return [it for it in (venue.get("items") or []) if item_ok(it, venue)]


def venue_type(venue: dict) -> str:
    t = str(venue.get("type") or "zoo").lower()
    if "aquarium" in t:
        return "aquarium"
    if "safari" in t:
        return "safari_zoo"
    if "national_park" in t or t in ("park", "national park") or (
        "park" in t and "safari" not in t and "zoo" not in t
    ):
        return "national_park"
    if any(x in t for x in ("museum", "science", "history", "children", "space")):
        return "museum"
    return "zoo"


def pick_find_ids(venue: dict, safe: list[dict], n: int = 7) -> list[str]:
    route = list(venue.get("route_90m") or [])
    route_set = set(route)
    # Prefer non-route deep cuts first
    deep = [it for it in safe if it["id"] not in route_set]
    # De-prioritize pure kids reset for bonus (keep if needed to fill)
    def score(it: dict) -> tuple:
        tags = set(it.get("tags") or [])
        lab = str(it.get("label") or "").lower()
        s = 0
        if it["id"] in route_set:
            s -= 3
        if tags & {"wow", "big", "water"}:
            s += 2
        if any(k in lab for k in ("penguin", "hippo", "cheetah", "tiger", "gorilla", "shark", "jelly", "octopus", "dinosaur", "submarine", "storm")):
            s += 3
        if tags == {"kids"} or ("kids" in tags and "rest" in tags and "wow" not in tags):
            s -= 2
        if it.get("zone"):
            s += 1
        return (-s, it["id"])

    ordered = sorted(deep, key=score) + sorted(
        [it for it in safe if it["id"] in route_set], key=score
    )
    # Unique preserve order
    out: list[str] = []
    seen = set()
    for it in ordered:
        if it["id"] in seen:
            continue
        out.append(it["id"])
        seen.add(it["id"])
        if len(out) >= n:
            break
    return out


def challenge_templates(vtype: str) -> list[dict]:
    """Portable hard prompts; {label} {zone} filled when possible."""
    all_ages = ["2-3", "4-5", "6-8", "adult"]
    big = ["4-5", "6-8", "adult"]
    if vtype == "aquarium":
        return [
            {"id": "aq_dive", "text": "Watch one animal swim past you twice — same direction or different?", "age_fit": all_ages},
            {"id": "aq_camouflage", "text": "Find the best hider in a tank (camouflage or nook)", "age_fit": big},
            {"id": "aq_glow", "text": "Jellies or dark exhibit: stand still 15 seconds — what moves first?", "age_fit": all_ages},
            {"id": "aq_tiny_big", "text": "Find something tiny in the same hall as something huge", "age_fit": all_ages},
            {"id": "aq_tunnel", "text": "If there’s a tunnel or big window: name one animal above you and one beside you", "age_fit": big},
            {"id": "aq_quiet", "text": "Find the quietest tank corner — what’s the softest motion?", "age_fit": all_ages},
        ]
    if vtype == "museum":
        return [
            {"id": "mu_stop", "text": "What design at this stop makes kids freeze mid-walk?", "age_fit": big},
            {"id": "mu_compare", "text": "Compare two nearby exhibits — which would you show a friend first?", "age_fit": big},
            {"id": "mu_detail", "text": "Find a tiny label, button, or texture most people skip", "age_fit": all_ages},
            {"id": "mu_body", "text": "Use your body once: climb, reach, crouch, or tip-toe", "age_fit": ["2-3", "4-5", "6-8"]},
            {"id": "mu_teach", "text": "Explain this stop in one sentence a tired grown-up would remember", "age_fit": big},
            {"id": "mu_sound", "text": "Close eyes 10 seconds — what do you hear in this hall?", "age_fit": all_ages},
        ]
    if vtype == "safari_zoo":
        return [
            {"id": "sf_far", "text": "Spot an animal far away first — then one close to the path", "age_fit": all_ages},
            {"id": "sf_still", "text": "Find something almost camouflaged against grass or trees", "age_fit": big},
            {"id": "sf_pair", "text": "Two different patterns in one loop (stripes, spots, or horns)", "age_fit": big},
            {"id": "sf_quiet", "text": "Quiet 20 seconds — bird, insect, or vehicle: what wins?", "age_fit": all_ages},
            {"id": "sf_tall", "text": "Point to the tallest living thing you can see from here", "age_fit": all_ages},
        ]
    if vtype == "national_park":
        return [
            {"id": "np_still", "text": "Quiet 20 seconds on the trail — bird, wind, water, or people: what wins?", "age_fit": all_ages},
            {"id": "np_far_near", "text": "Name something far first — then something by your feet", "age_fit": all_ages},
            {"id": "np_camo", "text": "Best natural camouflage (rock, bark, shadow) you can spot", "age_fit": big},
            {"id": "np_map", "text": "Find a map or zone name you haven’t noticed — point it out", "age_fit": big},
            {"id": "np_tiny_huge", "text": "Something tiny next to something huge in this area", "age_fit": all_ages},
            {"id": "np_safe_edge", "text": "Stay on the path: find the edge marker, rail, or stay-back sign", "age_fit": all_ages},
            {"id": "np_little", "text": "Copy a nature move once (tiptoe, big stretch, quiet freeze)", "age_fit": ["2-3", "4-5"]},
        ]
    # zoo default
    return [
        {"id": "zoo_behavior", "text": "Watch one animal do something for 15 full seconds (eat, climb, pace, rest)", "age_fit": all_ages},
        {"id": "zoo_pattern", "text": "Match two patterns in different places (stripes, spots, shells)", "age_fit": big},
        {"id": "zoo_tiny_big", "text": "Find something tiny next to something huge", "age_fit": all_ages},
        {"id": "zoo_overlook", "text": "Find a cool detail most visitors walk past", "age_fit": big},
        {"id": "zoo_sound", "text": "Stand still 20 seconds — loudest sound that isn’t people?", "age_fit": all_ages},
        {"id": "zoo_water", "text": "Find water used by animals (pool, moat, splash, drink)", "age_fit": all_ages},
        {"id": "zoo_little", "text": "Copy an animal move once (stomp, stretch, tip-toe, roar soft)", "age_fit": ["2-3", "4-5"]},
    ]


def fill_challenges(venue: dict, safe: list[dict], find_ids: list[str], vtype: str) -> list[dict]:
    by_id = {it["id"]: it for it in safe}
    picks = [by_id[i] for i in find_ids if i in by_id]
    templates = challenge_templates(vtype)
    out: list[dict] = []
    # Zone-specific from top finds
    for it in picks[:5]:
        lab = it.get("display_label") or it.get("label") or it["id"]
        zone = (it.get("zone") or "").strip()
        slug = re.sub(r"[^a-z0-9]+", "_", str(venue.get("slug") or "v"))[:12]
        iid = re.sub(r"[^a-z0-9]+", "_", str(it["id"]))[:16]
        if zone:
            text = f"{zone}: take 15 seconds on the {lab} — what is it doing right now?"
        else:
            text = f"At the {lab}: watch 15 seconds — moving, eating, hiding, or resting?"
        out.append(
            {
                "id": f"{slug}_{iid}_watch",
                "text": text,
                "age_fit": ["2-3", "4-5", "6-8", "adult"],
            }
        )
    # Add type templates
    for t in templates:
        out.append(dict(t))
    # Dedupe by text
    seen = set()
    uniq = []
    for c in out:
        key = c["text"].lower()
        if key in seen:
            continue
        seen.add(key)
        uniq.append(c)
    return uniq[:10]


def easter_eggs(venue: dict, safe: list[dict], vtype: str) -> tuple[str, str]:
    name = venue.get("name") or "this place"
    kids = next(
        (
            it
            for it in safe
            if "kid" in str(it.get("label") or "").lower()
            or "children" in str(it.get("zone") or "").lower()
            or (it.get("tags") or []) == ["kids"]
            or "play" in (it.get("tags") or []) and "kids" in (it.get("tags") or [])
        ),
        None,
    )
    little = (
        f"★ Easter egg: {kids.get('display_label') or kids.get('label')} only after the hard list — one free play minute"
        if kids
        else "★ Easter egg: pick a favorite bench — sit 60 seconds and name three sounds"
    )
    if vtype == "museum":
        egg = f"★ Easter egg: find a map or hall name you’ve never noticed — point it out at {name}"
    elif vtype == "aquarium":
        egg = f"★ Easter egg: find the darkest or glowiest corner — whisper one thing that moved"
    else:
        egg = f"★ Easter egg: find a park map or zone sign — name one animal that lives that way"
    return egg, little


def build_pack(venue: dict, *, status: str = "solid") -> dict:
    safe = safe_items(venue)
    vtype = venue_type(venue)
    conf = venue.get("list_confidence") or "partial"
    if conf == "template" or len(safe) < 3:
        status = "thin"
        find_ids = [it["id"] for it in safe[:5]]
    else:
        find_ids = pick_find_ids(venue, safe, n=7 if status != "thin" else 4)
    challenges = fill_challenges(venue, safe, find_ids, vtype)
    egg, egg_l = easter_eggs(venue, safe, vtype)
    short = (venue.get("name") or venue.get("slug") or "Place").split("(")[0].strip()
    tag = {
        "zoo": f"{short} bonus · second-loop secrets",
        "aquarium": f"{short} bonus · deep tanks & hideouts",
        "museum": f"{short} bonus · halls worth a second look",
        "safari_zoo": f"{short} bonus · far sights & camouflage",
        "national_park": f"{short} bonus · second look on the trail",
    }.get(vtype, f"{short} bonus · curious explorers")
    pack = {
        "tagline": tag,
        "find_ids": find_ids,
        "challenges": challenges,
        "easter_egg": egg,
        "easter_egg_little": egg_l,
        "researched": TODAY,
        "status": status,
        "sources": [venue.get("official_url") or ""] if venue.get("official_url") else [],
    }
    if not pack["sources"] or pack["sources"] == [""]:
        pack.pop("sources", None)
    return pack


PACK_KEYS = (
    "tagline",
    "find_ids",
    "challenges",
    "easter_egg",
    "easter_egg_little",
    "researched",
    "status",
    "sources",
    "notes",
)


def sync_file_from_venues() -> int:
    data = load(BONUS_FILE) if BONUS_FILE.is_file() else {"version": 1, "generic": {}, "venues": {}}
    if "venues" not in data:
        data["venues"] = {}
    if "alpha" not in data or not isinstance(data["alpha"], dict):
        data["alpha"] = {"generic": {}, "venues": {}}
    if "venues" not in data["alpha"]:
        data["alpha"]["venues"] = {}
    if not data["alpha"].get("generic"):
        data["alpha"]["generic"] = {
            "tagline": "Extra-hard · cool deep cuts",
            "challenges": [
                {
                    "id": "ah_patience",
                    "text": "Pick one stop: full 30 silent seconds — write one verb for what happened",
                    "age_fit": ["4-5", "6-8", "adult"],
                },
                {
                    "id": "ah_overlook",
                    "text": "Find something cool most visitors walk past — point without talking",
                    "age_fit": ["2-3", "4-5", "6-8", "adult"],
                },
                {
                    "id": "ah_compare",
                    "text": "Compare two patterns or textures in different places — pick a winner",
                    "age_fit": ["4-5", "6-8", "adult"],
                },
                {
                    "id": "ah_map",
                    "text": "From a map only: name a zone you have not visited yet",
                    "age_fit": ["4-5", "6-8", "adult"],
                },
            ],
            "easter_egg": "★ Alpha egg: ask staff one question — write the answer on the back",
        }
    # ensure kits exist
    if "kits" not in data:
        data["kits"] = {
            "zoo": challenge_templates("zoo"),
            "aquarium": challenge_templates("aquarium"),
            "museum": challenge_templates("museum"),
            "safari_zoo": challenge_templates("safari_zoo"),
        }
    n = 0
    for p in sorted(VENUE_DIR.glob("*.json")):
        v = load(p)
        slug = v.get("slug") or p.stem
        bh = v.get("bonus_hunt")
        if bh:
            data["venues"][slug] = {k: bh[k] for k in PACK_KEYS if k in bh}
            n += 1
        ah = v.get("alpha_hunt")
        if ah:
            data["alpha"]["venues"][slug] = {k: ah[k] for k in PACK_KEYS if k in ah}
    save(BONUS_FILE, data)
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--only-missing", action="store_true")
    ap.add_argument("--sync-file", action="store_true")
    ap.add_argument("--force", action="store_true", help="Overwrite researched packs")
    args = ap.parse_args()

    if args.sync_file:
        n = sync_file_from_venues()
        print(f"synced {n} packs → {BONUS_FILE}")
        return

    slugs = []
    if args.slug:
        slugs = [args.slug]
    elif args.all:
        slugs = sorted(p.stem for p in VENUE_DIR.glob("*.json"))
    else:
        ap.error("Need --slug or --all (or --sync-file)")

    written = 0
    for slug in slugs:
        p = VENUE_DIR / f"{slug}.json"
        if not p.is_file():
            print("MISSING", slug)
            continue
        v = load(p)
        existing = v.get("bonus_hunt") or {}
        if args.only_missing and existing:
            continue
        if existing.get("status") == "researched" and not args.force:
            print("skip researched", slug)
            continue
        # Preserve researched content unless --force
        if existing.get("status") == "researched" and args.force:
            pass
        pack = build_pack(v, status="solid")
        # If was thin inventory
        if (v.get("list_confidence") or "") == "template":
            pack["status"] = "thin"
        if args.write:
            v["bonus_hunt"] = pack
            save(p, v)
            written += 1
            print(f"WRITE {slug} status={pack['status']} finds={len(pack['find_ids'])}")
        else:
            print(f"DRY {slug}", pack["tagline"], pack["find_ids"][:5])

    if args.write:
        n = sync_file_from_venues()
        print(f"done written={written} file_venues={n}")


if __name__ == "__main__":
    main()
