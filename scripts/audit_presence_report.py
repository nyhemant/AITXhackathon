#!/usr/bin/env python3
"""Report print-list presence risk across Field Trip Kit venues.

Usage:
  python3 scripts/audit_presence_report.py
  python3 scripts/audit_presence_report.py --slug detroit-zoo
  python3 scripts/audit_presence_report.py --high-risk-only

Does not mutate data. Use for triage queues before Wave A/B audits.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENUE_DIR = ROOT / "static/field-pack/data/venues"

# Catalog icons that are frequently wrong when template-stamped
HIGH_RISK = {
    "african-elephant",
    "asian-elephant",
    "nile-hippo",
    "giant-panda",
    "koala",
    "orangutan",
    "polar-bear",
    "cheetah",
    "african-penguin",  # often wrong species
    "sumatran-tiger",  # often wrong subspecies label
}


def load_venues() -> list[dict]:
    out = []
    for p in sorted(VENUE_DIR.glob("*.json")):
        v = json.loads(p.read_text(encoding="utf-8"))
        v["_path"] = str(p)
        out.append(v)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="")
    ap.add_argument("--high-risk-only", action="store_true")
    args = ap.parse_args()

    venues = load_venues()
    if args.slug:
        venues = [v for v in venues if v.get("slug") == args.slug]
        if not venues:
            raise SystemExit(f"No venue {args.slug}")

    conf_c = Counter()
    risk_rows = []
    elephant_still = []

    for v in venues:
        conf = v.get("list_confidence") or "?"
        conf_c[conf] += 1
        dnl = {
            (row.get("catalog_id") if isinstance(row, dict) else row) or ""
            for row in (v.get("do_not_list") or [])
        }
        dnl = {str(x).lower() for x in dnl if x}
        for it in v.get("items") or []:
            cid = (it.get("catalog_id") or "").lower()
            pres = (it.get("presence") or "").lower() or "unset"
            label = it.get("display_label") or it.get("label") or ""
            is_hr = cid in HIGH_RISK or any(h in (label or "").lower() for h in ("elephant", "panda", "hippo"))
            if args.high_risk_only and not is_hr:
                continue
            bad = (
                pres in ("template", "absent", "medium", "unset")
                and conf != "audited"
                and not str(it.get("id") or "").startswith("w_")
            )
            if cid in dnl:
                bad = True
            if is_hr and conf != "audited" and pres not in ("verified", "high"):
                risk_rows.append(
                    {
                        "slug": v.get("slug"),
                        "list_confidence": conf,
                        "id": it.get("id"),
                        "label": label,
                        "catalog_id": cid,
                        "presence": pres,
                        "in_route": it.get("id") in (v.get("route_90m") or []),
                    }
                )
            if cid == "african-elephant" and conf != "audited":
                elephant_still.append(v.get("slug"))
            elif cid == "african-elephant" and pres not in ("verified", "high"):
                elephant_still.append(v.get("slug"))

        # Detroit-class: elephant still in items on non-verified
        for it in v.get("items") or []:
            if (it.get("catalog_id") or "") == "african-elephant":
                if (it.get("presence") or "") not in ("verified", "high"):
                    if v.get("slug") not in elephant_still:
                        elephant_still.append(v.get("slug"))

    print("=== list_confidence ===")
    for k, n in sorted(conf_c.items(), key=lambda x: (-x[1], x[0])):
        print(f"  {k}: {n}")

    print(f"\n=== high-risk named items on non-audited / weak presence: {len(risk_rows)} ===")
    # group by slug
    by = Counter(r["slug"] for r in risk_rows)
    print(f"  venues touched: {len(by)}")
    for slug, n in by.most_common(25):
        print(f"  {slug}: {n} risk items")

    print(f"\n=== african-elephant still on print list (weak presence): {len(set(elephant_still))} ===")
    for s in sorted(set(elephant_still))[:40]:
        print(f"  {s}")
    if len(set(elephant_still)) > 40:
        print(f"  … +{len(set(elephant_still)) - 40} more")

    if args.slug and venues:
        v = venues[0]
        print(f"\n=== detail {v.get('slug')} conf={v.get('list_confidence')} ===")
        print("route_90m:", v.get("route_90m"))
        print("do_not_list:", v.get("do_not_list"))
        for it in v.get("items") or []:
            print(
                f"  [{it.get('presence') or 'unset'}] {it.get('id')}: "
                f"{it.get('display_label') or it.get('label')} cat={it.get('catalog_id')}"
            )


if __name__ == "__main__":
    main()
