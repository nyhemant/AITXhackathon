#!/usr/bin/env python3
"""Validate bonus_hunt packs + optional Node smoke for a few slugs."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENUE_DIR = ROOT / "static/field-pack/data/venues"
ENGINE = ROOT / "static/field-pack/js/mission/mission-engine.js"
CHALLENGES = ROOT / "static/field-pack/data/challenges.json"
WONDERS = ROOT / "static/field-pack/data/wonders.json"
BONUS = ROOT / "static/field-pack/data/bonus-hunts.json"

PRESENCE_BLOCK = {"absent", "template"}


def item_ok(it: dict, venue: dict) -> bool:
    p = str(it.get("presence") or "").lower()
    if p in PRESENCE_BLOCK:
        return False
    if p in ("verified", "high"):
        return True
    if (venue.get("list_confidence") or "") == "template":
        return False
    return p not in PRESENCE_BLOCK


def validate_pack(slug: str, pack: dict, by_id: dict, venue: dict, kind: str) -> list[str]:
    errs = []
    prefix = f"{slug} {kind}"
    for fid in pack.get("find_ids") or []:
        it = by_id.get(fid)
        if not it:
            errs.append(f"{prefix}: find_id unknown {fid}")
            continue
        if not item_ok(it, venue):
            errs.append(f"{prefix}: find_id not print-safe {fid} presence={it.get('presence')}")
    ch = pack.get("challenges") or []
    if len(ch) < 2:
        errs.append(f"{prefix}: need ≥2 challenges")
    if not (pack.get("easter_egg") or "").strip():
        errs.append(f"{prefix}: missing easter_egg")
    texts = [c.get("text") for c in ch if c.get("text")]
    if len(texts) != len(set(texts)):
        errs.append(f"{prefix}: duplicate challenge text")
    return errs


def validate_venue(path: Path) -> list[str]:
    errs = []
    v = json.loads(path.read_text(encoding="utf-8"))
    slug = v.get("slug") or path.stem
    bh = v.get("bonus_hunt")
    if not bh:
        errs.append(f"{slug}: missing bonus_hunt")
        return errs
    by_id = {it.get("id"): it for it in (v.get("items") or []) if it.get("id")}
    errs.extend(validate_pack(slug, bh, by_id, v, "bonus"))
    ah = v.get("alpha_hunt")
    if ah:
        errs.extend(validate_pack(slug, ah, by_id, v, "alpha"))
    return errs


def node_smoke(slug: str) -> str | None:
    venue = VENUE_DIR / f"{slug}.json"
    if not venue.is_file():
        return f"smoke {slug}: no venue"
    script = r"""
const fs=require('fs');const vm=require('vm');
const eng=fs.readFileSync(process.argv[1],'utf8');
const ctx={};vm.createContext(ctx);vm.runInContext(eng,ctx);
const ME=ctx.FPMission;
const v=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const ch=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const w=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
const b=JSON.parse(fs.readFileSync(process.argv[5],'utf8'));
const m=ME.selectMission(v,ch,{age:'4-5',time:'half',seed:1,hunt:'bonus'},w,b);
if(!m.finds||!m.finds.length) { console.error('no finds'); process.exit(2); }
if(m.hunt!=='bonus') { console.error('hunt not bonus'); process.exit(3); }
console.log(JSON.stringify({slug:v.slug,n:m.finds.length,egg:!!m.easterEgg,title:m.title,finds:m.finds.map(f=>f.id)}));
"""
    try:
        r = subprocess.run(
            ["node", "-e", script, str(ENGINE), str(venue), str(CHALLENGES), str(WONDERS), str(BONUS)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except Exception as e:
        return f"smoke {slug}: {e}"
    if r.returncode != 0:
        return f"smoke {slug}: {r.stderr or r.stdout}"
    return None


def main() -> int:
    errs: list[str] = []
    paths = sorted(VENUE_DIR.glob("*.json"))
    missing = 0
    for p in paths:
        v = json.loads(p.read_text(encoding="utf-8"))
        if not v.get("bonus_hunt"):
            missing += 1
            errs.append(f"{p.stem}: missing bonus_hunt")
            continue
        errs.extend(validate_venue(p))

    # Smoke a handful (classic path via bonus smoke)
    for slug in ["dallas-zoo", "detroit-zoo", "fort-worth-zoo", "georgia-aquarium", "perot-museum", "austin-zoo"]:
        if (VENUE_DIR / f"{slug}.json").is_file():
            e = node_smoke(slug)
            if e:
                errs.append(e)

    # Alpha smoke when pack exists
    for slug in ["dallas-zoo", "austin-zoo"]:
        if not (VENUE_DIR / f"{slug}.json").is_file():
            continue
        script = r"""
const fs=require('fs');const vm=require('vm');
const eng=fs.readFileSync(process.argv[1],'utf8');
const ctx={};vm.createContext(ctx);vm.runInContext(eng,ctx);
const ME=ctx.FPMission;
const v=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const ch=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));
const w=JSON.parse(fs.readFileSync(process.argv[4],'utf8'));
const b=JSON.parse(fs.readFileSync(process.argv[5],'utf8'));
const m=ME.selectMission(v,ch,{age:'6-8',time:'half',seed:2,hunt:'alpha'},w,b);
if(m.hunt!=='alpha') { console.error('hunt not alpha'); process.exit(3); }
if(!m.finds||!m.finds.length) { console.error('no alpha finds'); process.exit(2); }
console.log(JSON.stringify({slug:v.slug,n:m.finds.length,egg:!!m.easterEgg,title:m.title}));
"""
        try:
            r = subprocess.run(
                ["node", "-e", script, str(ENGINE), str(VENUE_DIR / f"{slug}.json"), str(CHALLENGES), str(WONDERS), str(BONUS)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except Exception as e:
            errs.append(f"alpha smoke {slug}: {e}")
            continue
        if r.returncode != 0:
            errs.append(f"alpha smoke {slug}: {r.stderr or r.stdout}")

    print(f"venues={len(paths)} missing_bonus={missing} errors={len(errs)}")
    for e in errs[:40]:
        print(" ", e)
    if len(errs) > 40:
        print(f"  … +{len(errs)-40} more")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
