#!/usr/bin/env python3
"""Build-time uniqueness lint for Field Trip Kit venue items.

Reports issues. Exit 1 only with --enforce-top10 / --strict when:
  - same item description (one_liner) appears in >3 venues
  - a venue core list has >2 generic-prefix catalog ids (np-*)
  - two same-type venues share >50% of core shortlist catalog ids

Core list = items with core=True, else first 8 items / featured-equivalent.
Writes docs/item-uniqueness-report.md (and legacy scripts/data copy)
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
VENUE_DIR = ROOT / "static/field-pack/data/venues"
OUT = ROOT / "docs" / "item-uniqueness-report.md"
OUT_LEGACY = ROOT / "scripts/data/item-uniqueness-report.md"
GENERIC_PREFIXES = ("np-",)
MAX_DESC_VENUES = 3
MAX_GENERIC_CORE = 2
MAX_SHARE = 0.50

def load_venues():
    out = []
    for p in sorted(VENUE_DIR.glob("*.json")):
        v = json.loads(p.read_text(encoding="utf-8"))
        v["_path"] = str(p)
        out.append(v)
    return out

def core_items(v):
    items = v.get("items") or []
    marked = [it for it in items if it.get("core") is True]
    if marked:
        return marked
    # fallback: first 8 non-bonus-tagged
    return [it for it in items if it.get("core") is not False][:8]

def core_ids(v):
    ids = []
    for it in core_items(v):
        cid = (it.get("catalog_id") or it.get("id") or "").strip()
        if cid and cid not in ids:
            ids.append(cid)
    return ids

def main():
    venues = load_venues()
    issues = []
    lines = ["# Item uniqueness report\n", f"Venues scanned: **{len(venues)}**\n"]

    # 1) description reuse
    desc_map = defaultdict(list)
    for v in venues:
        slug = v.get("slug") or Path(v["_path"]).stem
        for it in core_items(v):
            d = (it.get("one_liner") or "").strip().lower()
            if len(d) < 12:
                continue
            desc_map[d].append(slug)
    desc_off = {d: sorted(set(sl)) for d, sl in desc_map.items() if len(set(sl)) > MAX_DESC_VENUES}
    lines.append(f"\n## Descriptions in >{MAX_DESC_VENUES} venues ({len(desc_off)})\n")
    for d, sl in sorted(desc_off.items(), key=lambda x: -len(x[1]))[:80]:
        lines.append(f"- ({len(sl)}) `{d[:90]}` → {', '.join(sl[:12])}{'…' if len(sl)>12 else ''}\n")
        issues.append(("desc", d[:60], sl))

    # 2) generic core density
    lines.append(f"\n## Core lists with >{MAX_GENERIC_CORE} generic (`np-*`) ids\n")
    gen_off = []
    for v in venues:
        slug = v.get("slug") or Path(v["_path"]).stem
        ids = core_ids(v)
        if not ids:
            continue
        gen = [i for i in ids if any(i.startswith(p) for p in GENERIC_PREFIXES)]
        if len(gen) > MAX_GENERIC_CORE:
            gen_off.append((slug, v.get("type"), len(gen), len(ids), gen))
            issues.append(("generic_core", slug, gen))
    for slug, typ, ng, n, gen in sorted(gen_off, key=lambda x: -x[2]):
        lines.append(f"- **{slug}** ({typ}): {ng}/{n} generic → {', '.join(gen)}\n")

    # 3) pairwise share >50% same type
    lines.append(f"\n## Same-type pairs sharing >{int(MAX_SHARE*100)}% core catalog ids\n")
    by_type = defaultdict(list)
    for v in venues:
        by_type[v.get("type") or "?"].append(v)
    pair_off = []
    for typ, vs in by_type.items():
        cores = [(v.get("slug") or Path(v["_path"]).stem, set(core_ids(v))) for v in vs]
        cores = [(s, ids) for s, ids in cores if len(ids) >= 4]
        for i in range(len(cores)):
            for j in range(i+1, len(cores)):
                a, A = cores[i]
                b, B = cores[j]
                inter = A & B
                base = min(len(A), len(B)) or 1
                share = len(inter) / base
                if share > MAX_SHARE and len(inter) >= 3:
                    pair_off.append((typ, a, b, share, sorted(inter)))
                    issues.append(("pair", f"{a}|{b}", sorted(inter)))
    for typ, a, b, share, inter in sorted(pair_off, key=lambda x: -x[3])[:100]:
        lines.append(f"- **{typ}** `{a}` ↔ `{b}`: {share:.0%} shared ({', '.join(inter[:8])})\n")

    # Top-10 special focus
    TOP10 = [
        "great-smoky-mountains","zion","yellowstone","grand-canyon","yosemite",
        "rocky-mountain","acadia","glacier","arches","olympic",
    ]
    lines.append("\n## Top-10 depth parks (expect clean)\n")
    top_ok = True
    for slug in TOP10:
        v = next((x for x in venues if (x.get("slug") or Path(x["_path"]).stem) == slug), None)
        if not v:
            lines.append(f"- **{slug}**: MISSING\n"); top_ok=False; continue
        ids = core_ids(v)
        gen = [i for i in ids if i.startswith("np-")]
        lines.append(f"- **{slug}**: core={len(ids)} generic_np={len(gen)} slice={((v.get('practical') or {}).get('slice_name') or v.get('slice_label') or '')}\n")
        if len(gen) > MAX_GENERIC_CORE:
            top_ok = False

    lines.append(f"\n## Summary\n")
    lines.append(f"- Description offenders: {len(desc_off)}\n")
    lines.append(f"- Generic-core offenders: {len(gen_off)}\n")
    lines.append(f"- Pairwise share offenders: {len(pair_off)}\n")
    lines.append(f"- Top-10 clean: {'YES' if top_ok else 'NO'}\n")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(lines)
    OUT.write_text(text, encoding="utf-8")
    try:
        OUT_LEGACY.parent.mkdir(parents=True, exist_ok=True)
        OUT_LEGACY.write_text(text, encoding="utf-8")
    except Exception:
        pass
    print("".join(lines[-20:]))
    print("Wrote", OUT)

    # Default: report-only (exit 0). T11: --enforce-top10 fails on top-10 regressions.
    # --strict fails on any long-tail issue too.
    strict = "--strict" in sys.argv
    enforce_top10 = "--enforce-top10" in sys.argv or strict
    top10_pair = any(a in TOP10 and b in TOP10 for typ, a, b, share, inter in pair_off)
    fail = False
    if enforce_top10:
        fail = (not top_ok) or top10_pair
    if strict:
        fail = fail or bool(desc_off) or bool(gen_off) or bool(pair_off)
    print(
        "STATUS",
        "FAIL" if fail else "OK",
        "| top10_clean",
        top_ok,
        "| enforce_top10",
        enforce_top10,
        "| strict",
        strict,
        "| warn-only",
        not enforce_top10,
    )
    return 1 if fail else 0

if __name__ == "__main__":
    sys.exit(main())
