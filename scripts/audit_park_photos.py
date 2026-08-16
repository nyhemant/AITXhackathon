#!/usr/bin/env python3
"""Audit park photo provenance from catalog.js + hero files. Updates ledger + report."""
from __future__ import annotations
import json, subprocess
from pathlib import Path
from datetime import date
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "static/field-pack/photos"
LEDGER = ROOT / "scripts/data/park_photo_ledger.json"
AUDIT = ROOT / "scripts/data/park_photo_audit_report.md"
TODAY = date.today().isoformat()

def classify(credit: str) -> str:
    c = (credit or "").lower()
    if "illustration" in c or "field trip kit" in c:
        return "ai_illustration"
    if "wikimedia" in c:
        return "wikimedia"
    if "nps" in c:
        return "nps"
    if "photo" in c:
        return "real_other"
    return "unknown"

def main():
    r = subprocess.run(
        ["node", "-e", open(ROOT/"scripts/_park_photo_scan.js").read() if (ROOT/"scripts/_park_photo_scan.js").exists() else r"""
const fs=require("fs");const vm=require("vm");
const c={window:{}};vm.createContext(c);
vm.runInContext(fs.readFileSync("static/field-pack/js/catalog.js","utf8"),c);
const cat=c.window.FIELD_PACK_CATALOG||{}, venues=c.window.FIELD_PACK_VENUES||{};
const catalog=[], parkVenues=[];
for (const [id,v] of Object.entries(cat)) {
  const ph=String(v.photo||""), cr=String(v.photoCredit||"");
  const isPark = id.startsWith("np-") || /^(yell|zion|yose|grca|grsm|romo|acad|glac|arch|olym)-/.test(id)
    || ["american-bison","elk","american-alligator","old-faithful","sequoia-general-sherman"].includes(id)
    || ph.includes("np-");
  if (isPark) catalog.push({id,name:v.name||id,photo:ph,credit:cr});
}
for (const [id,v] of Object.entries(venues)) if (v.type==="national_park") parkVenues.push(id);
console.log(JSON.stringify({catalog, parkVenues}));
"""],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    # simpler inline always
    r = subprocess.run(["node","-e",'''
const fs=require("fs");const vm=require("vm");
const c={window:{}};vm.createContext(c);
vm.runInContext(fs.readFileSync("static/field-pack/js/catalog.js","utf8"),c);
const cat=c.window.FIELD_PACK_CATALOG||{}, venues=c.window.FIELD_PACK_VENUES||{};
const catalog=[], parkVenues=[];
for (const [id,v] of Object.entries(cat)) {
  const ph=String(v.photo||""), cr=String(v.photoCredit||"");
  const isPark = id.startsWith("np-") || /^(yell|zion|yose|grca|grsm|romo|acad|glac|arch|olym)-/.test(id)
    || ["american-bison","elk","american-alligator","old-faithful","sequoia-general-sherman"].includes(id)
    || ph.includes("np-");
  if (isPark) catalog.push({id,name:v.name||id,photo:ph,credit:cr});
}
for (const [id,v] of Object.entries(venues)) if (v.type==="national_park") parkVenues.push(id);
console.log(JSON.stringify({catalog, parkVenues}));
'''], cwd=str(ROOT), capture_output=True, text=True)
    data = json.loads(r.stdout)
    ledger = {"version":1,"updated":TODAY,"assets":[]}
    if LEDGER.exists():
        try:
            ledger = json.loads(LEDGER.read_text())
        except Exception:
            pass
    by_id = {a["asset_id"]: a for a in ledger.get("assets") or []}

    def upsert(asset):
        old = by_id.get(asset["asset_id"])
        if old and old.get("status") == "accepted" and asset.get("provenance") == "ai_illustration":
            # keep accepted real if ledger says so
            if old.get("provenance") in ("wikimedia","nps","real_other"):
                return old
        if old and old.get("status") == "accepted":
            # refresh path/credit only
            old["local_path"] = asset.get("local_path", old.get("local_path"))
            old["credit_ui"] = asset.get("credit_ui") or old.get("credit_ui")
            old["provenance"] = asset.get("provenance") or old.get("provenance")
            return old
        return asset

    assets = []
    for slug in sorted(set(data["parkVenues"]) | {p.stem.replace("np-hero-","") for p in PHOTOS.glob("np-hero-*.jpg")}):
        rel = f"photos/np-hero-{slug}.jpg"
        prov = "ai_illustration"
        st = "todo"
        aid = f"hero:{slug}"
        if aid in by_id and by_id[aid].get("status") == "accepted":
            assets.append(by_id[aid]); continue
        assets.append(upsert({
            "asset_id": aid, "role":"hero", "slug":slug, "catalog_id":None,
            "status": st, "provenance": prov, "source_url":"", "source_page":"",
            "license":"", "credit_ui":"Photo via Wikimedia Commons", "credit_full":"",
            "local_path": rel, "candidates":[], "score":None,
            "notes":"hero", "checked_date":None,
        }))

    for it in data["catalog"]:
        ph = it["photo"].split("?")[0]
        local = ph if ph.startswith("photos/") else ("photos/"+ph.replace("/field-pack/photos/",""))
        prov = classify(it["credit"])
        role = "wildlife" if it["id"] in ("american-bison","elk","american-alligator") else (
            "shared" if it["id"].startswith("np-") else "stop")
        st = "accepted" if prov in ("wikimedia","nps","real_other") else "todo"
        aid = f"catalog:{it['id']}"
        assets.append(upsert({
            "asset_id": aid, "role":role, "slug":None, "catalog_id":it["id"], "name":it["name"],
            "status": st, "provenance": prov, "source_url":"", "source_page":"",
            "license": "Commons" if prov=="wikimedia" else "",
            "credit_ui": it["credit"], "credit_full":"",
            "local_path": local, "candidates":[], "score": 4 if st=="accepted" else None,
            "notes":"", "checked_date": TODAY if st=="accepted" else None,
        }))

    ledger["assets"] = assets
    ledger["updated"] = TODAY
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False)+"\n")

    by_prov = Counter(a["provenance"] for a in assets)
    todo = Counter(a["role"] for a in assets if a["status"]=="todo")
    lines = [f"# Park photo audit\n\n**Date:** {TODAY}\n\nTotal: **{len(assets)}**\n\n## Provenance\n"]
    for k,n in by_prov.most_common():
        lines.append(f"- `{k}`: {n}\n")
    lines.append("\n## Todo by role\n")
    for k,n in todo.most_common():
        lines.append(f"- **{k}**: {n}\n")
    lines.append("\n## AI catalog still todo\n")
    for a in assets:
        if a["status"]=="todo" and a.get("catalog_id"):
            lines.append(f"- `{a['catalog_id']}` ({a['role']})\n")
    lines.append(f"\n## AI heroes todo: {sum(1 for a in assets if a['role']=='hero' and a['status']=='todo')}\n")
    AUDIT.write_text("".join(lines))
    print("assets", len(assets), "prov", dict(by_prov), "todo", dict(todo))
    print("wrote", LEDGER)
    print("wrote", AUDIT)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
