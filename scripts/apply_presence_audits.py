#!/usr/bin/env python3
"""Apply presence audit JSON → data/venues/*.json.

Safety:
- Only updates items that exist on the venue (matched by id).
- Marks presence; strips items with presence=absent from print list (moved to do_not_list).
- Does not invent new exhibit ids (museum rebuilds are hand-done).
- Skips slug denylist (known bad audits / needs hand rewrite).

Usage:
  python3 scripts/apply_presence_audits.py
  python3 scripts/apply_presence_audits.py --slug lincoln-park-zoo
  python3 scripts/apply_presence_audits.py --dry-run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENUE_DIR = ROOT / "static/field-pack/data/venues"
AUDIT_DIR = ROOT / "static/field-pack/data/audits/results"

# Audits that confused venues or need full item rewrite — skip auto-apply
SKIP_SLUGS = {
    "childrens-museum-perot",  # audit confused with Perot science museum
    "museum-of-science-industry-chi",  # needs new real exhibit ids
    "nashville-adventure-science",  # needs real ASC exhibit names
}

PRACTICAL_FIELDS = {
    "ticket_note",
    "transit_note",
    "energy_note",
    "best_start",
    "typical_duration",
}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def save(p: Path, data: dict) -> None:
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def apply_one(venue: dict, audit: dict) -> list[str]:
    notes: list[str] = []
    slug = venue.get("slug") or ""

    # Merge do_not_list
    dnl = list(venue.get("do_not_list") or [])
    seen = {
        (str(x.get("catalog_id") or x.get("name") or "").lower() if isinstance(x, dict) else str(x).lower())
        for x in dnl
    }
    for row in audit.get("do_not_list") or []:
        if not isinstance(row, dict):
            continue
        key = str(row.get("catalog_id") or row.get("name") or "").lower()
        if key and key not in seen:
            dnl.append(
                {
                    "catalog_id": row.get("catalog_id") or "",
                    "name": row.get("name") or "",
                    "reason": row.get("reason") or "",
                    "as_of": audit.get("audited_at") or "2026-08-08",
                }
            )
            seen.add(key)
            notes.append(f"do_not_list +{key}")
    venue["do_not_list"] = dnl

    # Index audit items by id
    by_id = {str(it.get("id") or ""): it for it in (audit.get("items") or []) if it.get("id")}

    kept = []
    for it in venue.get("items") or []:
        iid = str(it.get("id") or "")
        a = by_id.get(iid)
        if not a:
            kept.append(it)
            continue
        pres = str(a.get("presence") or "").lower()
        if pres == "absent":
            # drop from print list; ensure do_not_list
            cid = it.get("catalog_id") or ""
            name = it.get("label") or a.get("label") or iid
            key = str(cid or name).lower()
            if key not in seen:
                dnl.append(
                    {
                        "catalog_id": cid,
                        "name": name,
                        "reason": a.get("notes") or "Absent per presence audit",
                        "as_of": audit.get("audited_at") or "2026-08-08",
                    }
                )
                seen.add(key)
            notes.append(f"removed absent {iid}")
            continue
        if pres in ("verified", "high", "medium", "template", "unclear"):
            # map unclear → medium for engine (engine blocks medium on template venues)
            it["presence"] = "medium" if pres == "unclear" else pres
            it["presence_checked"] = audit.get("audited_at") or "2026-08-08"
            if a.get("source_url"):
                it["presence_source"] = "official_animals_page"
            if a.get("display_label"):
                it["display_label"] = a["display_label"]
                # Prefer soft label on sheet
                if a["display_label"] and a["display_label"] != it.get("label"):
                    it["label"] = a["display_label"]
            if a.get("notes"):
                it["presence_note"] = str(a["notes"])[:240]
        kept.append(it)

    venue["items"] = kept
    venue["do_not_list"] = dnl

    # route_90m: only keep ids that still exist and are print-safe
    ok_ids = {
        it["id"]
        for it in kept
        if str(it.get("presence") or "") in ("verified", "high", "", "none")
        or (
            str(it.get("presence") or "") in ("verified", "high")
        )
        or it.get("presence") in (None, "")
        or str(it.get("presence")) in ("verified", "high")
    }
    # stricter: verified/high only for new route; if empty keep filtered old
    strong = {
        it["id"]
        for it in kept
        if str(it.get("presence") or "").lower() in ("verified", "high")
    }
    rec = [rid for rid in (audit.get("route_90m_recommended") or []) if rid in {it["id"] for it in kept}]
    rec_strong = [rid for rid in rec if rid in strong]
    if rec_strong:
        venue["route_90m"] = rec_strong[:3]
        notes.append(f"route_90m {venue['route_90m']}")
    elif rec:
        venue["route_90m"] = rec[:3]
        notes.append(f"route_90m soft {venue['route_90m']}")
    else:
        # strip absent from existing route
        old = [rid for rid in (venue.get("route_90m") or []) if rid in {it["id"] for it in kept}]
        if old != (venue.get("route_90m") or []):
            venue["route_90m"] = old
            notes.append("route_90m pruned")

    # list_confidence
    rec_conf = audit.get("list_confidence_recommended")
    if rec_conf in ("audited", "partial", "template"):
        # Don't upgrade to audited unless enough verified/high items remain
        if rec_conf == "audited":
            n_ok = sum(1 for it in kept if str(it.get("presence") or "").lower() in ("verified", "high"))
            if n_ok >= 4:
                venue["list_confidence"] = "audited"
                venue["last_presence_audit"] = audit.get("audited_at") or "2026-08-08"
                notes.append("list_confidence audited")
            else:
                venue["list_confidence"] = "partial"
                notes.append("list_confidence partial (not enough verified)")
        else:
            venue["list_confidence"] = rec_conf
            notes.append(f"list_confidence {rec_conf}")

    if audit.get("content_mode_recommended") in ("wonder", "hybrid", "curated"):
        # Only force wonder when template
        if venue.get("list_confidence") == "template" or audit.get("content_mode_recommended") == "wonder":
            if audit.get("content_mode_recommended") == "wonder":
                venue["content_mode"] = "wonder"
                notes.append("content_mode wonder")
        elif audit.get("content_mode_recommended") == "curated" and venue.get("list_confidence") == "audited":
            venue["content_mode"] = "curated"
            notes.append("content_mode curated")

    # practical fixes (safe fields only)
    practical = dict(venue.get("practical") or {})
    for fix in audit.get("practical_fixes") or []:
        if not isinstance(fix, dict):
            continue
        field = str(fix.get("field") or "")
        suggested = (fix.get("suggested") or "").strip()
        if field in PRACTICAL_FIELDS and suggested and len(suggested) < 200:
            # skip "Remove" style
            if suggested.lower() in ("remove", "n/a"):
                continue
            practical[field] = suggested
            notes.append(f"practical.{field}")
    if practical:
        venue["practical"] = practical

    if audit.get("sources"):
        venue["presence_sources"] = list(audit["sources"])[:12]

    venue["research_notes"] = (
        (venue.get("research_notes") or "")
        + f" · presence-audit {audit.get('audited_at') or '2026-08-08'}"
        + (f" [{audit.get('severity')}]" if audit.get("severity") else "")
    ).strip(" ·")

    return notes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    audits = {p.stem: load(p) for p in AUDIT_DIR.glob("*.json")}
    changed = 0
    for p in sorted(VENUE_DIR.glob("*.json")):
        slug = p.stem
        if args.slug and slug != args.slug:
            continue
        if slug in SKIP_SLUGS:
            print(f"SKIP {slug} (hand rewrite)")
            continue
        if slug not in audits:
            print(f"NO AUDIT {slug}")
            continue
        venue = load(p)
        notes = apply_one(venue, audits[slug])
        if not notes:
            print(f"noop {slug}")
            continue
        changed += 1
        print(f"OK {slug}: {', '.join(notes[:8])}")
        if not args.dry_run:
            save(p, venue)
    print(f"changed {changed}")


if __name__ == "__main__":
    main()
