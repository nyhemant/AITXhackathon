#!/usr/bin/env python3
"""Generate indexable Field Trip Kit venue pages + sitemap/robots.

Run from repo root:
  python3 scripts/generate_bdo_seo.py

Outputs:
  static/field-pack/<venue-id>/index.html  (×N)
  static/sitemap.xml
  static/robots.txt
  static/field-pack/seo-venues.json        (machine list of URLs)
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FIELD = REPO / "static" / "field-pack"
VENUE_DATA_DIR = FIELD / "data" / "venues"
CHALLENGES_JSON = FIELD / "data" / "challenges.json"
WONDERS_JSON = FIELD / "data" / "wonders.json"
BONUS_HUNTS_JSON = FIELD / "data" / "bonus-hunts.json"
MISSION_ENGINE = FIELD / "js" / "mission" / "mission-engine.js"
STATIC = REPO / "static"
CATALOG_JS = FIELD / "js" / "catalog.js"
PLACES_JS = FIELD / "js" / "places-data.js"
SITE = "https://1less.app"
TODAY = date.today().isoformat()

RESERVED = {
    "app.html",
    "css",
    "img",
    "index.html",
    "js",
    "photos",
    "places",
    "seo-venues.json",
}

TYPE_PHRASE = {
    "zoo": ("zoo", "animals", "scavenger hunt"),
    "safari_zoo": ("safari park", "animals", "scavenger hunt"),
    "zoo_aq": ("zoo and aquarium", "animals", "scavenger hunt"),
    "aquarium": ("aquarium", "sea life", "scavenger hunt"),
    "aq": ("aquarium", "sea life", "scavenger hunt"),
    "sci_aq": ("science museum and aquarium", "exhibits", "scavenger hunt"),
    "childrens_museum": ("children's museum", "play zones", "scavenger hunt"),
    "cm": ("children's museum", "play zones", "scavenger hunt"),
    "science": ("science museum", "exhibits", "scavenger hunt"),
    "sci": ("science museum", "exhibits", "scavenger hunt"),
    "natural_history": ("natural history museum", "exhibits", "scavenger hunt"),
    "nh": ("natural history museum", "exhibits", "scavenger hunt"),
    "space": ("space center", "exhibits", "scavenger hunt"),
}


def esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def load_venues() -> list[dict]:
    """Extract venues via Node (same source of truth as the app)."""
    script = r"""
const fs = require('fs');
const vm = require('vm');
const ctx = { window: {}, console };
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx);
const venues = ctx.window.FIELD_PACK_VENUES;
const places = ctx.window.FP_PLACES;
const catalog = ctx.window.FIELD_PACK_CATALOG;
const byId = Object.fromEntries(places.map(p => [p.id, p]));
const out = Object.keys(venues).map(id => {
  const ven = venues[id];
  const pl = byId[id] || {};
  const idList = [...new Set([...(ven.featuredAnimalIds || []), ...(ven.animalIds || [])])];
  const items = idList.slice(0, 12).map(iid => {
    const it = catalog[iid];
    if (!it) return null;
    return {
      id: iid,
      name: it.name,
      emoji: it.emoji || '',
      blurb: it.blurb || '',
      photo: it.photo || '',
    };
  }).filter(Boolean);
  const hunt = (ven.treasureHunt || []).map(h => h.text);
  return {
    id,
    name: ven.name,
    shortName: ven.shortName || ven.name,
    location: ven.location || [pl.city, pl.state].filter(Boolean).join(', '),
    city: pl.city || '',
    state: pl.state || '',
    type: ven.type || pl.type || 'zoo',
    blurb: ven.blurb || pl.blurb || '',
    website: ven.website || '',
    emoji: pl.emoji || '',
    itemLabel: ven.itemLabel || 'things',
    packTemplate: ven.packTemplate || 'animals',
    quality: ven.quality || 'starter',
    lastVerified: ven.lastVerified || '',
    featured: items,
    hunt,
  };
});
process.stdout.write(JSON.stringify(out));
"""
    proc = subprocess.run(
        ["node", "-e", script, str(CATALOG_JS), str(PLACES_JS)],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def type_bits(v: dict) -> tuple[str, str, str]:
    t = (v.get("type") or "zoo").lower().replace(" ", "_").replace("-", "_")
    place, things, hunt = TYPE_PHRASE.get(t, ("attraction", "things to find", "scavenger hunt"))
    return place, things, hunt


def pick(seed: str, options: list[str]) -> str:
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return options[h % len(options)]



def status_chip_html(mission_venue: dict) -> str:
    """Honest list status — never claim Verified without presence audit."""
    conf = (mission_venue or {}).get("list_confidence") or ""
    audited = (mission_venue or {}).get("last_presence_audit") or ""
    month = audited[:7] if len(audited) >= 7 else ""
    if conf == "audited" and month:
        return (
            f'<p class="seo-checked seo-checked-verified">'
            f'✓ Verified with venue website · {esc(month)}</p>'
        )
    if conf == "partial":
        m = month or ((mission_venue or {}).get("last_verified") or "")[:7]
        extra = f" · {esc(m)}" if m else ""
        return (
            f'<p class="seo-checked seo-checked-partial">'
            f'Local shortlist · confirm on arrival{extra}</p>'
        )
    # template / unknown
    return (
        '<p class="seo-checked seo-checked-starter">'
        'Starter hunt · flexible finds — skip anything closed</p>'
    )


def print_status_line(mission_venue: dict) -> str:
    conf = (mission_venue or {}).get("list_confidence") or ""
    audited = (mission_venue or {}).get("last_presence_audit") or ""
    month = audited[:7] if len(audited) >= 7 else ""
    if conf == "audited" and month:
        return f"Verified {month}"
    if conf == "partial":
        return "Confirm on arrival"
    return "Flexible finds"


def practical_chips_html(practical: dict | None, last_v: str = "") -> str:
    """Scannable venue facts — duration, energy, tickets, transit. No paragraph soup."""
    p = practical or {}
    chips: list[tuple[str, str]] = []
    if p.get("typical_duration"):
        chips.append(("Time", str(p["typical_duration"])))
    if p.get("energy_note"):
        chips.append(("Setting", str(p["energy_note"])))
    if p.get("ticket_note"):
        chips.append(("Tickets", str(p["ticket_note"])))
    if p.get("transit_note"):
        chips.append(("Get there", str(p["transit_note"])))
    if not chips and not last_v:
        return ""
    lis = "".join(
        f'<li class="seo-fact-chip"><span class="seo-fact-k">{esc(k)}</span>'
        f'<span class="seo-fact-v">{esc(val)}</span></li>'
        for k, val in chips
    )
    return f"""
        <ul class="seo-fact-chips" aria-label="Visit facts">{lis}</ul>"""


def unique_body(
    v: dict,
    exclude_ids: set[str] | None = None,
) -> str:
    """Visual shortlist + hunt checklist. No long SEO prose walls."""
    featured_all = v.get("featured") or []
    # Prefer remaining stops when “start here” already showed the first picks
    exclude_ids = exclude_ids or set()
    featured_rest = [it for it in featured_all if it.get("id") not in exclude_ids]
    featured = featured_rest if len(featured_rest) >= 2 else featured_all
    hunt = v.get("hunt") or []

    # Photo cards first (visual), plus crawlable text for SEO
    cards = []
    feat_html_parts = []
    for it in featured[:12]:
        photo = (it.get("photo") or "").strip()
        # Catalog paths are like photos/foo.jpg; base href is /field-pack/
        if photo and not photo.startswith("/") and not photo.startswith("http"):
            src = photo
        elif photo.startswith("/field-pack/"):
            src = photo[len("/field-pack/") :]
        else:
            src = photo
        alt = f"{it.get('name') or 'Animal'} — shortlist photo"
        item_blurb = _card_blurb(it.get("blurb") or "") or "Worth a look if you have time."
        item_id = it.get("id") or ""
        card_inner = ""
        if src:
            card_inner = f"""<img src="{esc(src)}" alt="{esc(alt)}" width="640" height="400" loading="lazy" decoding="async" />
          <div class="seo-animal-meta">
            <h3>{esc(it.get('emoji',''))} {esc(it['name'])}</h3>
            <p>{esc(item_blurb)}</p>
          </div>"""
        if card_inner:
            # Link card to interactive app item for Q&A print path
            href = f"/field-pack/app.html#/venue/{esc(v['id'])}/item/{esc(item_id)}" if item_id else f"/field-pack/app.html#/venue/{esc(v['id'])}"
            cards.append(
                f"""<a class="seo-animal-card" href="{href}" role="listitem">
          {card_inner}
        </a>"""
            )
        feat_html_parts.append(
            f"<li><strong>{esc(it.get('emoji',''))} {esc(it['name'])}</strong> — {esc(item_blurb)}</li>"
        )

    hunt_lis = "".join(
        f'<li><span class="seo-hunt-box" aria-hidden="true">☐</span><span>{esc(t)}</span></li>'
        for t in hunt[:8]
    ) or '<li><span class="seo-hunt-box" aria-hidden="true">☐</span><span>Find your favorite stop and check it off</span></li>'
    cards_html = (
        f'<div class="seo-animal-grid" role="list">{"".join(cards)}</div>'
        if cards
        else ""
    )

    showing_rest = bool(
        exclude_ids and featured is not featured_all and len(featured_all) > len(featured)
    )
    shortlist_lead = (
        "More stops if you have the energy."
        if showing_rest
        else "Tap a card for printable Q&amp;A."
    )
    return f"""
    <section class="seo-list-block seo-visual-shortlist" aria-labelledby="shortlist-heading">
      <h2 id="shortlist-heading">{"More if you have energy" if showing_rest else "Kid shortlist"}</h2>
      <p>{shortlist_lead}</p>
      {cards_html}
      <ul class="seo-shortlist seo-shortlist-sr">
        {"".join(feat_html_parts) or "<li>Open the interactive outing for the full shortlist.</li>"}
      </ul>
    </section>
    <section class="seo-list-block seo-hunt-block" aria-labelledby="hunt-heading">
      <h2 id="hunt-heading">Create and print your mission</h2>
      <p>Pick age and time, then print one page — no app at the venue.</p>
      <p class="seo-hunt-cta-wrap no-print">
        <button type="button" class="btn btn-secondary" id="seo-open-mission" data-how="print">
          Open print options
        </button>
      </p>
      <details class="seo-hunt-examples">
        <summary>Example finds that may appear on the sheet</summary>
        <ol class="seo-hunt-list">
          {hunt_lis}
        </ol>
      </details>
    </section>
"""


def h1_for(v: dict) -> str:
    """Visible page heading — venue name only. SEO phrase lives in title/meta."""
    return v["name"]


def seo_hunt_label(v: dict) -> str:
    """Search/social title phrase (not the on-page H1)."""
    return f"{v['name']} Scavenger Hunt for Kids (Free Printable)"


def title_for(v: dict) -> str:
    return f"{seo_hunt_label(v)} · 1Less"


def meta_for(v: dict) -> str:
    city = v["city"] or v["location"] or ""
    place, things, _ = type_bits(v)
    # Keep well under ~155 chars so SERP/OG don't truncate mid-word
    name = v["name"]
    base = f"Printable {name} scavenger hunt for kids in {city}. Short list + one-page mission — Field Trip Kit."
    if len(base) > 155:
        base = f"{name} scavenger hunt for kids ({city}). One-page printable mission — Field Trip Kit."
    return base[:155].rsplit(" ", 1)[0] if len(base) > 155 else base


def venue_json_ld(v: dict, url: str) -> str:
    steps = []
    for i, t in enumerate((v.get("hunt") or [])[:8], 1):
        steps.append(
            {
                "@type": "HowToStep",
                "position": i,
                "text": t,
            }
        )
    if not steps:
        steps = [{"@type": "HowToStep", "position": 1, "text": f"Explore {v['name']} with kids using the shortlist."}]

    hunt_name = seo_hunt_label(v)
    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": hunt_name,
        "description": meta_for(v),
        "totalTime": "PT2H",
        "tool": [{"@type": "HowToTool", "name": "Printed one-page hunt sheet"}],
        "step": steps,
        "url": url,
    }
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": hunt_name,
        "description": meta_for(v),
        "author": {"@type": "Organization", "name": "1Less"},
        "publisher": {"@type": "Organization", "name": "1Less", "url": SITE},
        "mainEntityOfPage": url,
        "about": {"@type": "Place", "name": v["name"], "address": v.get("location") or ""},
    }
    return json.dumps(howto, ensure_ascii=False) + "\n" + json.dumps(article, ensure_ascii=False)



def load_mission_venue(slug: str) -> dict | None:
    p = VENUE_DATA_DIR / f"{slug}.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def default_mission_via_node(venue: dict) -> dict:
    """Run mission-engine.js in Node for SEO default list (age 4-5, half day)."""
    script = r"""
const fs = require('fs');
const vm = require('vm');
const ctx = { console, globalThis: {} };
vm.createContext(ctx);
const engine = fs.readFileSync(process.argv[1], 'utf8');
vm.runInContext(engine + '\nthis.FPMission = globalThis.FPMission;', ctx);
const venue = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const challenges = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const wonders = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
const FP = ctx.FPMission || ctx.globalThis.FPMission;
const mission = FP.selectMission(venue, challenges, { age: '4-5', time: 'half', name: '', seed: 1 }, wonders);
process.stdout.write(JSON.stringify(mission));
"""
    proc = subprocess.run(
        [
            "node",
            "-e",
            script,
            str(MISSION_ENGINE),
            str(VENUE_DATA_DIR / f"{venue['slug']}.json"),
            str(CHALLENGES_JSON),
            str(WONDERS_JSON),
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def content_mode_of(mission_venue: dict, catalog_v: dict | None = None) -> str:
    """SEO body mode. Template / unaudited lists never show a fake species grid."""
    conf = (mission_venue or {}).get("list_confidence") or ""
    if conf == "template":
        return "wonder"
    m = (mission_venue or {}).get("content_mode") or ""
    if m in ("wonder", "hybrid", "curated"):
        # Hybrid without print-safe named items → wonder page body
        if m == "hybrid" and not _print_safe_items(mission_venue):
            return "wonder"
        return m
    by = (mission_venue or {}).get("verified_by") or ""
    if by == "catalog-scaffold" or conf == "template":
        return "wonder"
    if by == "owner" or conf == "audited":
        return "curated"
    # "research" alone is not a collection census
    q = (catalog_v or {}).get("quality") or ""
    return "wonder" if conf == "template" else ("curated" if q == "full" and conf == "partial" else "wonder")


def _do_not_list_keys(mission_venue: dict) -> set[str]:
    keys: set[str] = set()
    for row in (mission_venue or {}).get("do_not_list") or []:
        if isinstance(row, str):
            keys.add(row.lower())
            continue
        if not isinstance(row, dict):
            continue
        for k in ("catalog_id", "name", "id"):
            if row.get(k):
                keys.add(str(row[k]).lower())
    return keys


def _item_presence_ok(it: dict, mission_venue: dict) -> bool:
    """Mirror mission-engine itemPresenceOk for SEO shortlist / start-here."""
    if not it:
        return False
    fid = str(it.get("id") or "")
    if fid.startswith("w_") or str(it.get("zone") or "").lower() == "wonder":
        return True
    p = str(it.get("presence") or "").lower()
    if p == "absent":
        return False
    label = str(it.get("display_label") or it.get("label") or it.get("name") or "").lower()
    cid = str(it.get("catalog_id") or "").lower()
    for row in (mission_venue or {}).get("do_not_list") or []:
        if isinstance(row, str):
            ban_name, ban_cat = row.lower(), ""
        elif isinstance(row, dict):
            ban_name = str(row.get("name") or "").lower()
            ban_cat = str(row.get("catalog_id") or "").lower()
        else:
            continue
        if ban_name and len(ban_name) >= 4 and ban_name in label:
            return False
        if ban_cat and cid == ban_cat:
            if p in ("verified", "high") and ban_name and ban_name not in label:
                pass  # soft label + verified photo reuse
            elif p not in ("verified", "high"):
                return False
            elif not ban_name:
                return False
    if p in ("template", "medium"):
        return False
    if p in ("verified", "high"):
        return True
    conf = (mission_venue or {}).get("list_confidence") or ""
    if conf == "audited":
        return True
    if conf == "template":
        return False
    if conf == "partial":
        return True
    return False


def _print_safe_items(mission_venue: dict) -> list[dict]:
    return [it for it in (mission_venue or {}).get("items") or [] if _item_presence_ok(it, mission_venue)]


def _item_sheet_label(it: dict) -> str:
    return (it.get("display_label") or it.get("label") or it.get("name") or "").strip()


def _featured_from_mission(mission_venue: dict, catalog_v: dict | None = None) -> list[dict]:
    """Build SEO photo shortlist from print-safe mission items only."""
    feat_by_id = {
        f.get("id"): f for f in (catalog_v or {}).get("featured") or [] if f.get("id")
    }
    # Also index global catalog via mission catalog_id when available on catalog_v featured only
    out: list[dict] = []
    for it in _print_safe_items(mission_venue):
        cid = (it.get("catalog_id") or "").strip()
        iid = (it.get("id") or "").replace("_", "-")
        feat = feat_by_id.get(cid) or feat_by_id.get(iid) or {}
        name = _item_sheet_label(it) or feat.get("name") or "Stop"
        out.append(
            {
                "id": cid or iid,
                "name": name,
                "emoji": it.get("emoji") or feat.get("emoji") or "",
                "blurb": it.get("one_liner") or feat.get("blurb") or "",
                "photo": feat.get("photo") or it.get("photo") or "",
            }
        )
    return out


def map_card_html(mission_venue: dict) -> str:
    """Official map card — thumbnail + hover/focus enlarge when image URL known."""
    media = (mission_venue or {}).get("media") or {}
    page = (media.get("visitor_map_page") or mission_venue.get("official_url") or "").strip()
    img = (media.get("visitor_map_url") or "").strip()
    kind = (media.get("visitor_map_kind") or "page").strip()
    attr = (media.get("map_attribution") or "Official visitor map").strip()
    if not page and not img:
        return ""
    href = page or img
    def _safe_map_img(u: str) -> bool:
        u = (u or "").strip()
        if u.startswith("https://") or u.startswith("http://"):
            return True
        # Self-hosted previews (e.g. PDF→PNG) under /field-pack/media/maps/
        if u.startswith("/field-pack/media/maps/") and ".." not in u:
            return True
        return False

    has_img = _safe_map_img(img)
    is_pdf = ".pdf" in href.lower() or href.lower().endswith("/pdf")
    # Prefer image mode whenever we have a verified map image (kind may lag)
    if has_img and kind in ("image", "page", ""):
        # Local previews don't need no-referrer; remote maps keep it for fewer hotlink blocks
        refpol = "" if img.startswith("/") else ' referrerpolicy="no-referrer"'
        ext_label = "Open PDF on official site ↗" if is_pdf else "Open on official site ↗"
        # Click pins enlarge in-page; external leave is a small secondary link only
        return f"""
    <div class="seo-map-card seo-map-card-image seo-map-has-preview no-print" data-map-preview>
      <button type="button" class="seo-map-enlarge-hit" aria-expanded="false" aria-controls="seo-map-preview-panel" aria-label="Enlarge park map">
        <span class="seo-map-thumb-wrap">
          <img class="seo-map-thumb" src="{esc(img)}" alt="Park map preview" width="640" height="400" loading="lazy" decoding="async"{refpol} />
          <span class="seo-map-hover-hint" aria-hidden="true">Tap to enlarge</span>
        </span>
      </button>
      <div class="seo-map-card-body">
        <span class="seo-map-kicker">Park map</span>
        <strong>Visitor map</strong>
        <small>{esc(attr)} · tap to enlarge</small>
        <a class="seo-map-ext-link" href="{esc(href)}" target="_blank" rel="noopener noreferrer">{esc(ext_label)}</a>
      </div>
      <div class="seo-map-preview" id="seo-map-preview-panel" role="dialog" aria-label="Enlarged park map" hidden>
        <button type="button" class="seo-map-preview-close" aria-label="Close enlarged map">×</button>
        <img src="{esc(img)}" alt="Enlarged park map" loading="lazy" decoding="async"{refpol} />
        <span class="seo-map-preview-cap">
          {esc(attr)}
          · <a class="seo-map-preview-ext" href="{esc(href)}" target="_blank" rel="noopener noreferrer">{esc(ext_label)}</a>
        </span>
      </div>
    </div>"""
    tab_note = "PDF · opens in a new tab" if is_pdf else "opens in a new tab"
    cta = "Open the print map (PDF)" if is_pdf else "Open the official map page"
    return f"""
    <a class="seo-map-card no-print" href="{esc(href)}" target="_blank" rel="noopener noreferrer">
      <span class="seo-map-icon" aria-hidden="true">🗺️</span>
      <span class="seo-map-card-body">
        <span class="seo-map-kicker">Official map</span>
        <strong>{cta}</strong>
        <small>{esc(attr)} · {tab_note}</small>
      </span>
      <span class="seo-map-go" aria-hidden="true">→</span>
    </a>"""

def is_wonder_find(find: dict) -> bool:
    """True flexible backups (taller than you, three colors) — not real animals/exhibits.

    Animals carry catalog_id and belong in photo shortlist / Q&A, not emoji stubs.
    """
    if not find:
        return False
    if find.get("catalog_id"):
        return False
    fid = str(find.get("id") or "")
    if fid.startswith("w_"):
        return True
    # Wonder-pool items never use catalog_id; zone sometimes tagged Wonder
    zone = str(find.get("zone") or "").lower()
    if zone == "wonder":
        return True
    # Abstract backup: no catalog link and not a venue item id pattern
    return not fid or fid.startswith("w")


def wonder_grid_html(mission: dict) -> str:
    """Emoji tiles for flexible backups only — animals stay out of this block."""
    finds = [f for f in (mission.get("finds") or []) if is_wonder_find(f)][:8]
    if not finds:
        return ""
    tiles = "".join(
        f"""<li class="seo-wonder-tile">
        <span class="seo-wonder-emoji" aria-hidden="true">{esc(f.get("emoji") or "✨")}</span>
        <strong>{esc(f.get("label") or "Wonder")}</strong>
        <small>{esc(_card_blurb(f.get("one_liner") or "") or f.get("one_liner") or "")}</small>
      </li>"""
        for f in finds
    )
    return f"""
    <section class="seo-wonder-block" aria-labelledby="wonder-heading">
      <h2 id="wonder-heading">Also look for</h2>
      <p class="seo-wonder-lead">Flexible backups if a favorite is closed, crowded, or napping — no fixed path.</p>
      <ul class="seo-wonder-grid">{tiles}</ul>
    </section>"""


def page_mission_chrome_html() -> str:
    """Primary print CTA + compact who/time chips (desktop row / phone stack)."""
    return """
        <div class="seo-mission-bar no-print" aria-label="Create and print your mission">
          <button type="button" class="btn btn-primary seo-print-btn" id="mission-open-btn" aria-haspopup="dialog" aria-controls="mission-drawer" aria-label="Create and print your mission">
            <span class="seo-print-btn-long">
              <span class="seo-print-btn-line">Create and print</span>
              <span class="seo-print-btn-line seo-print-btn-sub">your mission</span>
            </span>
            <span class="seo-print-btn-short">Create/print mission</span>
          </button>
          <div class="seo-mission-chrome" id="seo-mission-chrome">
            <div class="seo-chrome-row">
              <span class="seo-chrome-k" id="seo-who-label">Who</span>
              <div class="seo-chip-row" role="group" aria-labelledby="seo-who-label">
                <button type="button" class="seo-age-chip" data-age="2-3">2–4</button>
                <button type="button" class="seo-age-chip is-active" data-age="4-5" aria-pressed="true">5–8</button>
                <button type="button" class="seo-age-chip" data-age="6-8">9–12</button>
                <button type="button" class="seo-age-chip" data-age="adult">Adults</button>
              </div>
            </div>
            <div class="seo-chrome-row">
              <span class="seo-chrome-k" id="seo-time-label">Time</span>
              <div class="seo-chip-row" role="group" aria-labelledby="seo-time-label">
                <button type="button" class="seo-time-chip" data-time="90m">90 min</button>
                <button type="button" class="seo-time-chip is-active" data-time="half" aria-pressed="true">Half day</button>
                <button type="button" class="seo-time-chip" data-time="full">Full day</button>
              </div>
            </div>
            <div class="seo-chrome-row seo-chrome-row-hunt">
              <span class="seo-chrome-k" id="seo-hunt-label">Style</span>
              <div class="seo-chip-row seo-chip-row-hunt" role="group" aria-labelledby="seo-hunt-label">
                <button type="button" class="seo-hunt-chip is-active" data-hunt="classic" aria-pressed="true">Classic</button>
                <button type="button" class="seo-hunt-chip seo-hunt-bonus" data-hunt="bonus">Bonus</button>
                <button type="button" class="seo-hunt-chip seo-hunt-alpha" data-hunt="alpha">Alpha</button>
              </div>
            </div>
          </div>
        </div>
        <p class="seo-print-fallback no-print">No printer? Open the sheet on your phone, or print later. <span class="seo-bonus-hint">Classic · Bonus · Alpha (extra-hard cool finds).</span></p>"""


def _photo_src(photo: str) -> str:
    photo = (photo or "").strip()
    if not photo:
        return ""
    if photo.startswith("/field-pack/"):
        return photo[len("/field-pack/") :]
    return photo


def _route_90m_picks(mission_venue: dict, mission: dict) -> list[dict]:
    """Same pick order as the start-here section (print-safe route_90m, else mission finds)."""
    safe = _print_safe_items(mission_venue)
    items = {it.get("id"): it for it in safe}
    picks: list[dict] = []
    for rid in (mission_venue.get("route_90m") or [])[:3]:
        if rid in items:
            picks.append(items[rid])
    if len(picks) < 3:
        for f in mission.get("finds") or []:
            if len(picks) >= 3:
                break
            if not any(p.get("id") == f.get("id") for p in picks):
                picks.append(f)
    return picks[:3]


def _start_here_catalog_ids(mission_venue: dict, mission: dict) -> set[str]:
    out: set[str] = set()
    for p in _route_90m_picks(mission_venue, mission):
        cid = (p.get("catalog_id") or "").strip()
        if cid:
            out.add(cid)
        elif p.get("id"):
            out.add(str(p["id"]).replace("_", "-"))
    return out


def _card_blurb(text: str) -> str:
    """Use a one-liner only if it reads as a full clue, not a 2–3 word stub."""
    t = (text or "").strip()
    if not t:
        return ""
    # Cryptic stubs create more questions than they answer
    if len(t.split()) < 5 and len(t) < 28:
        return ""
    return t


def route_90m_html(mission_venue: dict, mission: dict, catalog_v: dict | None = None) -> str:
    """Short-visit picks: 2–3 real stops with photos — the “start here” path.

    Exists so a half-day page still answers “we only have an hour.”
    Not a second shortlist: same finds, tighter cut, numbered.
    No separate “First stop” tip — the numbered cards are the plan.
    """
    # catalog featured: id (sci-dinosaur) → photo/blurb
    feat_by_id = {f.get("id"): f for f in (catalog_v or {}).get("featured") or [] if f.get("id")}
    picks = _route_90m_picks(mission_venue, mission)
    if len(picks) < 2:
        return ""

    slug = mission_venue.get("slug") or ""
    n = min(3, len(picks))
    cards = []
    for i, p in enumerate(picks[:3], 1):
        cat_id = (p.get("catalog_id") or "").replace("_", "-") or (p.get("id") or "").replace("_", "-")
        feat = feat_by_id.get(cat_id) or feat_by_id.get(p.get("id") or "") or {}
        # also try matching featured by name-ish catalog ids already hyphenated
        if not feat and p.get("catalog_id"):
            feat = feat_by_id.get(p["catalog_id"]) or {}
        src = _photo_src(feat.get("photo") or p.get("photo") or "")
        label = _item_sheet_label(p) or feat.get("name") or "Stop"
        emoji = p.get("emoji") or feat.get("emoji") or ""
        one = _card_blurb(p.get("one_liner") or feat.get("blurb") or "")
        # Prefer catalog id for app Q&A cards; underscore venue ids won't resolve in catalog
        item_id = (p.get("catalog_id") or "").strip() or cat_id
        # Has a real catalog photo/entry → deep-link to talk card; else venue list in app
        if item_id and feat:
            href = f"/field-pack/app.html#/venue/{esc(slug)}/item/{esc(item_id)}"
        elif item_id and p.get("catalog_id"):
            href = f"/field-pack/app.html#/venue/{esc(slug)}/item/{esc(item_id)}"
        else:
            href = f"/field-pack/app.html#/venue/{esc(slug)}" if slug else "/field-pack/app.html"
        if src:
            media = (
                f'<img src="{esc(src)}" alt="" width="640" height="400" '
                f'loading="{"eager" if i == 1 else "lazy"}" decoding="async" />'
            )
        else:
            media = f'<span class="seo-start-emoji" aria-hidden="true">{esc(emoji or "✨")}</span>'
        cards.append(
            f"""<a class="seo-start-card" href="{href}">
        <span class="seo-start-num" aria-hidden="true">{i}</span>
        {media}
        <span class="seo-start-meta">
          <strong>{esc(emoji + " " if emoji else "")}{esc(label)}</strong>
          {f"<small>{esc(one)}</small>" if one else ""}
        </span>
      </a>"""
        )

    lead = (
        f"Do these {n} in order if you can — enough for a short visit. "
        "Tap a stop for talk tips &amp; photos. Create and print your mission is above."
    )
    return f"""
    <section class="seo-start-here no-print" aria-labelledby="route90-heading">
      <h2 id="route90-heading">Short on time? Start here</h2>
      <p class="seo-start-lead">{esc(lead)}</p>
      <div class="seo-start-grid">{"".join(cards)}</div>
    </section>"""


def mission_drawer_html(mission_venue: dict, mission: dict) -> str:
    """Slide-over drawer: filters + live sheet. Page stays clean; CTA opens this."""
    vid = mission_venue["slug"]
    loc = ", ".join(x for x in [mission_venue.get("city"), mission_venue.get("region")] if x)
    verified_line = print_status_line(mission_venue)
    mission_title = esc(mission.get("title") or f"Your Mission at {mission_venue['name']}")
    age_label = esc(mission.get("ageLabel") or "Kids · 5–8")
    time_label = esc(mission.get("timeLabel") or "Half day")
    finds_html = "".join(
        f'<li class="mission-find">'
        f'<span class="mission-check" aria-hidden="true">☐</span>'
        f'<span class="mission-emoji">{esc(f.get("emoji") or "📍")}</span>'
        f'<span class="mission-find-body"><strong>{esc(f["label"])}</strong>'
        f'<small>{esc(f.get("one_liner") or "")}'
        f'{(" · " + esc(f["zone"])) if f.get("zone") else ""}</small></span></li>'
        for f in mission.get("finds") or []
    )
    ch_html = "".join(
        f'<li class="mission-challenge">'
        f'<span class="mission-check" aria-hidden="true">☐</span>'
        f"<span>{esc(c.get('text') or '')}</span></li>"
        for c in mission.get("challenges") or []
    )
    return f"""
  <div class="mission-overlay no-print" id="mission-overlay" hidden>
    <div
      class="mission-drawer"
      id="mission-drawer"
      role="dialog"
      aria-modal="true"
      aria-labelledby="mission-heading"
      tabindex="-1"
    >
      <header class="mission-drawer-head">
        <div>
          <p class="mission-drawer-kicker">Field Trip Kit</p>
          <h2 id="mission-heading">Create and print your mission</h2>
        </div>
        <button type="button" class="mission-drawer-close" id="mission-close" aria-label="Close">×</button>
      </header>
      <div class="mission-drawer-body">
        <aside class="mission-filters" id="mission-controls" aria-label="Personalize">
          <div class="mission-field mission-field-name">
            <label for="mission-name">Kid name <span class="mission-opt">(optional)</span></label>
            <input type="text" id="mission-name" maxlength="24" placeholder="e.g. Arya" autocomplete="off" />
            <p class="mission-privacy">Stays on this page — never sent anywhere.</p>
          </div>
          <div class="mission-field mission-field-who">
            <span class="mission-field-label" id="mission-who-label">Who’s going?</span>
            <div class="mission-seg" id="mission-who-seg" role="group" aria-labelledby="mission-who-label">
              <button type="button" class="mission-seg-btn" data-age="2-3">2–4</button>
              <button type="button" class="mission-seg-btn is-active" data-age="4-5" aria-pressed="true">5–8</button>
              <button type="button" class="mission-seg-btn" data-age="6-8">9–12</button>
              <button type="button" class="mission-seg-btn" data-age="adult">Adults</button>
            </div>
          </div>
          <div class="mission-field mission-field-time">
            <span class="mission-field-label" id="mission-time-label">How long?</span>
            <div class="mission-seg" id="mission-time-seg" role="group" aria-labelledby="mission-time-label">
              <button type="button" class="mission-seg-btn" data-time="90m">90 min</button>
              <button type="button" class="mission-seg-btn is-active" data-time="half" aria-pressed="true">Half day</button>
              <button type="button" class="mission-seg-btn" data-time="full">Full day</button>
            </div>
          </div>
          <div class="mission-field mission-field-hunt">
            <span class="mission-field-label" id="mission-hunt-label">Mission style</span>
            <div class="mission-seg" id="mission-hunt-seg" role="group" aria-labelledby="mission-hunt-label">
              <button type="button" class="mission-seg-btn is-active" data-hunt="classic" aria-pressed="true">Classic</button>
              <button type="button" class="mission-seg-btn mission-seg-bonus" data-hunt="bonus">Bonus</button>
              <button type="button" class="mission-seg-btn mission-seg-alpha" data-hunt="alpha">Alpha</button>
            </div>
            <p class="mission-hunt-hint">Classic = first visit · Bonus = trickier · Alpha = extra-hard cool finds</p>
          </div>
          <div class="mission-field">
            <label for="mission-interest">What are they into? <span class="mission-opt">(optional)</span></label>
            <select id="mission-interest">
              <option value="">Any</option>
            </select>
          </div>
          <p class="mission-filters-hint">Sheet updates live — then print one page.</p>
        </aside>
        <div class="mission-preview">
          <div class="mission-sheet" id="mission-sheet">
            <p class="ms-brand">Field Trip Kit{f' · {esc(loc)}' if loc else ""}</p>
            <h3 class="ms-title" id="mission-title">{mission_title}</h3>
            <p class="ms-meta" id="mission-meta">{age_label} · {time_label}</p>
            <h4 class="ms-section" id="mission-finds-heading">Find these</h4>
            <ol class="mission-finds" id="mission-finds" aria-label="Finds">{finds_html}</ol>
            <h4 class="ms-section" id="mission-bonus-heading">Bonus</h4>
            <ul class="mission-challenges" id="mission-challenges" aria-label="Challenges">{ch_html}</ul>
            <p class="ms-favorite">My favorite was _______________________</p>
            <p class="ms-footer">
              <span id="mission-verified">{esc(verified_line)}</span>
              · free at 1less.app/field-pack/{esc(vid)}/
            </p>
            <p class="ms-map-hint" id="mission-map-hint"></p>
          </div>
        </div>
      </div>
      <footer class="mission-drawer-foot">
        <button type="button" class="btn btn-ghost" id="mission-shuffle-btn">Give me different stops</button>
        <button type="button" class="btn btn-primary btn-big" id="mission-print-btn">Create and print your mission</button>
      </footer>
    </div>
  </div>
"""


def render_mission_venue_page(v: dict, mission_venue: dict) -> str:
    """Full SEO venue page (photos + shortlist); mission opens in a drawer."""
    vid = v["id"]
    if vid in RESERVED:
        raise SystemExit(f"Venue id collides with reserved path: {vid}")
    url = f"{SITE}/field-pack/{vid}/"
    app_href = f"/field-pack/app.html#/venue/{vid}"
    map_href = f"/field-pack/#/venue/{vid}"
    place, _, _ = type_bits(v)

    def soft_title(s: str) -> str:
        parts = []
        for w in (s or "").replace("_", " ").split():
            if not w:
                continue
            if "'" in w:
                a, b = w.split("'", 1)
                parts.append(
                    (a[:1].upper() + a[1:].lower())
                    + "'"
                    + (b[:1].upper() + b[1:].lower() if b else "")
                )
            else:
                parts.append(w[:1].upper() + w[1:].lower() if len(w) > 1 else w.upper())
        return " ".join(parts)

    loc_chip = " · ".join(
        x for x in [soft_title(place.replace("_", " ")), v.get("location") or ""] if x
    )
    mode = content_mode_of(mission_venue, v)
    last_v = (v.get("lastVerified") or mission_venue.get("last_verified") or "")[:7]

    mission = default_mission_via_node(mission_venue)
    drawer = mission_drawer_html(mission_venue, mission)
    map_card = map_card_html(mission_venue)
    chrome = page_mission_chrome_html()
    route90 = route_90m_html(mission_venue, mission, catalog_v=v)
    # Catalog ids already shown in “start here” — don’t repeat in shortlist grid
    start_exclude = _start_here_catalog_ids(mission_venue, mission)
    practical = mission_venue.get("practical") or {}
    # Prefer print-safe mission items over catalog.js animal pack (stops false elephants)
    v_body = dict(v)
    safe_feat = _featured_from_mission(mission_venue, catalog_v=v)
    if safe_feat:
        v_body["featured"] = safe_feat
    elif (mission_venue or {}).get("list_confidence") == "template":
        v_body["featured"] = []  # never show template catalog pack
    if mode == "wonder":
        hunt = v.get("hunt") or []
        hunt_lis = "".join(
            f'<li><span class="seo-hunt-box" aria-hidden="true">☐</span><span>{esc(t)}</span></li>'
            for t in hunt[:8]
        )
        hunt_sec = (
            f"""
    <section class="seo-list-block seo-hunt-block" aria-labelledby="hunt-heading">
      <h2 id="hunt-heading">Create and print your mission</h2>
      <p>Pick age and time, then print one page — no app at the venue.</p>
      <p class="seo-hunt-cta-wrap no-print">
        <button type="button" class="btn btn-secondary" id="seo-open-mission" data-how="print">
          Open print options
        </button>
      </p>
      <details class="seo-hunt-examples">
        <summary>Example finds that may appear on the sheet</summary>
        <ol class="seo-hunt-list">{hunt_lis}</ol>
      </details>
    </section>"""
            if hunt_lis
            else ""
        )
        body = wonder_grid_html(mission) + hunt_sec
    elif mode == "hybrid":
        wonder_sec = wonder_grid_html(mission)
        body = unique_body(v_body, exclude_ids=start_exclude) + wonder_sec
    else:
        body = unique_body(v_body, exclude_ids=start_exclude)
    h1 = h1_for(v)
    title = title_for(v)
    desc = meta_for(v)
    og_img = f"{SITE}/1LessMark.png"
    json_ld = venue_json_ld(v, url)
    venue_json = json.dumps(mission_venue, ensure_ascii=False)
    challenges_json = CHALLENGES_JSON.read_text(encoding="utf-8")
    wonders_json = WONDERS_JSON.read_text(encoding="utf-8") if WONDERS_JSON.is_file() else "{}"
    # Per-venue bonus slice only — full catalog is huge; engine also reads venue.bonus_hunt.
    bonus_json = "{}"
    if BONUS_HUNTS_JSON.is_file():
        try:
            _bh_all = json.loads(BONUS_HUNTS_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            _bh_all = {}
        _slug = mission_venue.get("slug") or v.get("id") or ""
        _bh_slim = {
            "version": _bh_all.get("version", 1),
            "generic": _bh_all.get("generic") or {},
        }
        if _bh_all.get("kits"):
            _bh_slim["kits"] = _bh_all["kits"]
        _one = (_bh_all.get("venues") or {}).get(_slug)
        if not _one and isinstance(mission_venue.get("bonus_hunt"), dict):
            _one = mission_venue["bonus_hunt"]
        if _one:
            _bh_slim["venues"] = {_slug: _one}
        else:
            _bh_slim["venues"] = {}
        # Alpha slice (extra-hard mode)
        _alpha_all = _bh_all.get("alpha") or {}
        _alpha_one = (_alpha_all.get("venues") or {}).get(_slug)
        if not _alpha_one and isinstance(mission_venue.get("alpha_hunt"), dict):
            _alpha_one = mission_venue["alpha_hunt"]
        _alpha_slim = {
            "generic": _alpha_all.get("generic") or {},
            "venues": {_slug: _alpha_one} if _alpha_one else {},
        }
        _bh_slim["alpha"] = _alpha_slim
        bonus_json = json.dumps(_bh_slim, ensure_ascii=False)
    lead = (
        mission_venue.get("tagline")
        or v.get("blurb")
        or f"Free printable scavenger hunt and kid shortlist for {v['name']}."
    )
    facts_html = practical_chips_html(practical, last_v) + status_chip_html(mission_venue)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{esc(url)}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="1Less" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(url)}" />
  <meta property="og:image" content="{esc(og_img)}" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{esc(og_img)}" />
  <meta name="color-scheme" content="light" />
  <base href="/field-pack/" />
  <link rel="stylesheet" href="/shell/shell.css?v=5" />
  <link rel="stylesheet" href="/field-pack/css/styles.css?v=22" />
  <link rel="stylesheet" href="/field-pack/css/landing.css?v=64" />
  <link rel="stylesheet" href="/field-pack/css/seo-venue.css?v=13" />
  <link rel="stylesheet" href="/field-pack/css/mission.css?v=13" />
  <script type="application/ld+json">
{json_ld.split(chr(10))[0]}
  </script>
  <script type="application/ld+json">
{json_ld.split(chr(10))[1]}
  </script>
</head>
<body class="landing-body seo-venue-body mission-venue-body" data-content-mode="{esc(mode)}">
  <div class="app landing-app seo-venue">
    <header class="oneless-shell no-print" data-product="bdo">
      <a class="shell-brand" href="/field-pack/" aria-label="Field Trip Kit home">
        <img src="/1LessMark.png" alt="" width="52" height="52" />
      </a>
      <p class="shell-product">
        Field Trip Kit
        <small>Zoo, aquarium &amp; museum days</small>
      </p>
      <div class="shell-more-wrap">
        <button type="button" class="shell-more" aria-expanded="false" aria-haspopup="true" aria-controls="shell-menu">More</button>
        <div id="shell-menu" class="shell-menu" hidden role="menu">
          <a href="/field-pack/" role="menuitem">All places<small>Map &amp; outings</small></a>
          <a href="/field-pack/#about" role="menuitem">About<small>1Less &amp; contact</small></a>
        </div>
      </div>
    </header>

    <nav class="seo-crumbs no-print" aria-label="Breadcrumb">
      <a href="/field-pack/">All places</a>
      <span aria-hidden="true"> / </span>
      <span>{esc(v['shortName'])}</span>
      <span class="seo-crumb-extra"> · <a href="{esc(map_href)}">Map</a></span>
    </nav>

    <article class="seo-article">
      <header class="seo-hero">
        <p class="promise-pill">{esc(loc_chip)}</p>
        <h1>{esc(v.get('emoji',''))} {esc(h1)}</h1>
        <p class="lead">{esc(lead)}</p>
        {facts_html}
        {chrome}
        <p class="seo-secondary-links no-print">
          <a href="{esc(app_href)}">Stops &amp; talk cards</a>
          <span aria-hidden="true"> · </span>
          <a href="{esc(map_href)}">Find on map</a>
        </p>
      </header>

      {map_card}
      {route90}
      <div id="seo-play-target" class="seo-play-anchor" tabindex="-1"></div>
      {body}

      <p class="seo-official no-print">
        {f'Official site: <a href="{esc(v["website"])}" rel="noopener noreferrer" target="_blank">{esc(v["name"])} website</a>.' if v.get("website") else ""}
        Always check hours and tickets before you go.
      </p>
    </article>

    <footer class="site-footer site-footer-slim no-print">
      <p>
        <strong>Field Trip Kit</strong>
        <span class="footer-dot">·</span>
        <a href="/field-pack/">All places</a>
        <span class="footer-dot">·</span>
        <a href="/field-pack/#about">About</a>
        <span class="footer-dot">·</span>
        <a href="mailto:hello@1less.app">Contact</a>
      </p>
      <p class="footer-privacy">Kid names stay on your device. We don’t collect accounts or emails for hunts.</p>
    </footer>
  </div>

  {drawer}

  <div id="print-sheet" class="print-sheet" aria-hidden="true"></div>
  <div id="treasure-sheet" class="print-sheet treasure-sheet" aria-hidden="true"></div>

  <script type="application/json" id="venue-data">{venue_json}</script>
  <script type="application/json" id="challenges-data">{challenges_json}</script>
  <script type="application/json" id="wonders-data">{wonders_json}</script>
  <script type="application/json" id="bonus-hunts-data">{bonus_json}</script>
  <script src="/shell/shell.js?v=4"></script>
  <script src="/field-pack/js/catalog.js?v=23"></script>
  <script src="/field-pack/js/print-maps.js?v=2"></script>
  <script src="/field-pack/js/print-kit.js?v=9"></script>
  <script src="/field-pack/js/mission/mission-engine.js?v=13"></script>
  <script src="/field-pack/js/mission/mission-ui.js?v=13"></script>
</body>
</html>
"""



def render_venue_page(v: dict) -> str:
    vid = v["id"]
    if vid in RESERVED:
        raise SystemExit(f"Venue id collides with reserved path: {vid}")
    url = f"{SITE}/field-pack/{vid}/"
    app_href = f"/field-pack/app.html#/venue/{vid}"
    map_href = f"/field-pack/#/venue/{vid}"
    place, things, _ = type_bits(v)
    # Apostrophe-safe title case (avoid Children'S)
    def soft_title(s: str) -> str:
        parts = []
        for w in (s or "").replace("_", " ").split():
            if not w:
                continue
            if "'" in w:
                a, b = w.split("'", 1)
                parts.append((a[:1].upper() + a[1:].lower()) + "'" + (b[:1].upper() + b[1:].lower() if b else ""))
            else:
                parts.append(w[:1].upper() + w[1:].lower() if len(w) > 1 else w.upper())
        return " ".join(parts)

    loc_chip = " · ".join(
        x for x in [soft_title(place.replace("_", " ")), v.get("location") or ""] if x
    )
    body = unique_body(v)
    h1 = h1_for(v)
    title = title_for(v)
    desc = meta_for(v)
    og_img = f"{SITE}/1LessMark.png"
    json_ld = venue_json_ld(v, url)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <link rel="canonical" href="{esc(url)}" />
  <meta name="robots" content="index,follow" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="1Less" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(url)}" />
  <meta property="og:image" content="{esc(og_img)}" />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{esc(og_img)}" />
  <meta name="color-scheme" content="light" />
  <base href="/field-pack/" />
  <link rel="stylesheet" href="/shell/shell.css?v=5" />
  <link rel="stylesheet" href="/field-pack/css/styles.css?v=22" />
  <link rel="stylesheet" href="/field-pack/css/landing.css?v=52" />
  <link rel="stylesheet" href="/field-pack/css/seo-venue.css?v=13" />
  <script type="application/ld+json">
{json_ld.split(chr(10))[0]}
  </script>
  <script type="application/ld+json">
{json_ld.split(chr(10))[1]}
  </script>
</head>
<body class="landing-body seo-venue-body">
  <div class="app landing-app seo-venue">
    <header class="oneless-shell no-print" data-product="bdo">
      <a class="shell-brand" href="/field-pack/" aria-label="Field Trip Kit home">
        <img src="/1LessMark.png" alt="" width="52" height="52" />
      </a>
      <p class="shell-product">
        Field Trip Kit
        <small>Zoo, aquarium &amp; museum days</small>
      </p>
      <div class="shell-more-wrap">
        <button type="button" class="shell-more" aria-expanded="false" aria-haspopup="true" aria-controls="shell-menu">More</button>
        <div id="shell-menu" class="shell-menu" hidden role="menu">
          <a href="/field-pack/" role="menuitem">All places<small>Map &amp; outings</small></a>
          <a href="/field-pack/#about" role="menuitem">About<small>1Less &amp; contact</small></a>
        </div>
      </div>
    </header>

    <nav class="seo-crumbs no-print" aria-label="Breadcrumb">
      <a href="/field-pack/">All places</a>
      <span aria-hidden="true"> / </span>
      <span>{esc(v['shortName'])}</span>
    </nav>

    <article class="seo-article">
      <header class="seo-hero">
        <p class="promise-pill">{esc(loc_chip)}</p>
        <h1>{esc(v.get('emoji',''))} {esc(h1)}</h1>
        <p class="lead">{esc(v.get('blurb') or f'Free printable scavenger hunt and kid shortlist for {v["name"]}.')}</p>
        <p class="seo-quality-note">{esc(
          (
            "Short kid list for a half-day visit."
            + (f' Status {v["lastVerified"][:7]}.' if (v.get("lastVerified") or "")[:7] else "")
          )
          if (v.get("quality") or "starter") == "full"
          else "Short flexible list — animals and exhibits change; skip anything closed or missing."
        )}</p>
        <p class="seo-brand-note"><strong>Field Trip Kit</strong> by 1Less — free printable hunts for families.</p>
        <div class="landing-cta-row seo-cta no-print">
          <a class="btn btn-primary btn-big" href="{esc(map_href)}">Open on map →</a>
          <button type="button" class="btn btn-secondary btn-big" id="seo-print-hunt" data-venue="{esc(vid)}">
            One-page hunt to print
          </button>
          <a class="btn btn-ghost" href="{esc(app_href)}">Full interactive list →</a>
        </div>
      </header>

      <div id="seo-play-target" class="seo-play-anchor" tabindex="-1"></div>
      {body}

      <section class="seo-how no-print" aria-labelledby="how-heading">
        <h2 id="how-heading">How it works</h2>
        <p class="how-hint">Tap a step to jump there.</p>
        <ol class="how-steps how-steps-visual how-steps-linked">
          <li>
            <button type="button" class="how-step-btn" data-how="print-hunt" id="how-print-btn">
              <span class="how-ico" aria-hidden="true">🖨️</span>
              <strong>Print</strong>
              <span>One-page hunt</span>
            </button>
          </li>
          <li>
            <a class="how-step-btn" href="#seo-play-target" data-how="play" id="how-play-link">
              <span class="how-ico" aria-hidden="true">👀</span>
              <strong>Play</strong>
              <span>Use the shortlist on site</span>
            </a>
          </li>
          <li>
            <a class="how-step-btn" href="{esc(app_href)}" data-how="talk" id="how-talk-link">
              <span class="how-ico" aria-hidden="true">💬</span>
              <strong>Optional</strong>
              <span>Talk cards after</span>
            </a>
          </li>
        </ol>
      </section>

      <p class="seo-official">
        {f'Official site: <a href="{esc(v["website"])}" rel="noopener noreferrer" target="_blank">{esc(v["name"])} website</a>.' if v.get("website") else ""}
        Always check hours and tickets before you go.
      </p>
    </article>

    <footer class="site-footer site-footer-slim no-print">
      <p>
        <a href="/field-pack/">All places</a> ·
        <strong>Field Trip Kit</strong> ·
        <a href="/field-pack/#about">About</a>
      </p>
    </footer>
  </div>

  <div id="print-sheet" class="print-sheet" aria-hidden="true"></div>
  <div id="treasure-sheet" class="print-sheet treasure-sheet" aria-hidden="true"></div>

  <script src="/shell/shell.js?v=4"></script>
  <script src="/field-pack/js/catalog.js?v=23"></script>
  <script src="/field-pack/js/print-maps.js?v=2"></script>
  <script src="/field-pack/js/print-kit.js?v=9"></script>
  <script>
    (function () {{
      var btn = document.getElementById("seo-print-hunt");
      function printHunt() {{
        // Prefer mission drawer when present; else legacy static treasure
        if (window.FPPrint && window.FPPrint.printTreasureForVenue) {{
          var id = (btn && btn.getAttribute("data-venue")) || "";
          if (window.FPPrint.printTreasureForVenue(id)) return true;
        }}
        if (btn) {{
          location.href = "/field-pack/app.html#/venue/" + encodeURIComponent(btn.getAttribute("data-venue") || "");
        }}
        return false;
      }}
      if (btn) btn.addEventListener("click", printHunt);
      document.querySelectorAll("[data-how]").forEach(function (el) {{
        el.addEventListener("click", function (e) {{
          var how = el.getAttribute("data-how");
          if (how === "print-hunt" || how === "print") {{
            e.preventDefault();
            printHunt();
            return;
          }}
          if (how === "play") {{
            var t = document.getElementById("seo-play-target")
              || document.getElementById("shortlist-heading");
            if (t) {{
              e.preventDefault();
              t.scrollIntoView({{ behavior: "smooth", block: "start" }});
            }}
          }}
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def write_sitemap(venues: list[dict]) -> None:
    urls = [f"{SITE}/field-pack/"]
    urls += [f"{SITE}/field-pack/{v['id']}/" for v in venues]
    # also root redirect target
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        pri = "1.0" if u.endswith("/field-pack/") else "0.8"
        body.append("  <url>")
        body.append(f"    <loc>{esc(u)}</loc>")
        body.append(f"    <lastmod>{TODAY}</lastmod>")
        body.append(f"    <changefreq>weekly</changefreq>")
        body.append(f"    <priority>{pri}</priority>")
        body.append("  </url>")
    body.append("</urlset>")
    body.append("")
    (STATIC / "sitemap.xml").write_text("\n".join(body), encoding="utf-8")
    # also under field-pack for convenience
    (FIELD / "sitemap.xml").write_text("\n".join(body), encoding="utf-8")


def write_robots() -> None:
    text = f"""User-agent: *
Allow: /
Allow: /field-pack/
Disallow: /dinner
Disallow: /analytics/
Disallow: /api/

Sitemap: {SITE}/sitemap.xml
"""
    (STATIC / "robots.txt").write_text(text, encoding="utf-8")
    (REPO / "static" / "robots.txt").write_text(text, encoding="utf-8")


SEO_CSS = """/* SEO venue pages — visual-first, same brand language as outing cards */
.seo-venue-body .seo-crumbs {
  margin: 0 0 12px;
  font-weight: 700;
  font-size: 0.9rem;
  color: #3d4f6f;
}
.seo-venue-body .seo-crumbs a {
  color: #0f5c5c;
  font-weight: 800;
  text-decoration: none;
}
.seo-venue-body .seo-crumbs a:hover { text-decoration: underline; }
.seo-article {
  max-width: 52rem;
  margin: 0 auto 28px;
  padding: 22px 22px 28px;
  border-radius: 24px;
  background: rgba(255,255,255,0.92);
  border: 1.5px solid rgba(15, 92, 92, 0.12);
  box-shadow: 0 12px 36px rgba(21, 34, 56, 0.08);
}
.seo-hero h1 {
  margin: 8px 0 12px;
  font-size: clamp(1.55rem, 4vw, 2.1rem);
  line-height: 1.15;
  color: #0a4545;
  letter-spacing: -0.02em;
}
.seo-brand-note {
  margin: 0 0 14px;
  font-weight: 650;
  color: #3d4f6f;
  font-size: 0.95rem;
}

/* Top photo strip under CTAs */
.seo-hero-photos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin: 0 0 22px;
}
.seo-hero-photos img {
  width: 100%;
  height: 148px;
  object-fit: cover;
  border-radius: 16px;
  border: 1.5px solid rgba(15, 92, 92, 0.12);
  box-shadow: 0 8px 20px rgba(21, 34, 56, 0.08);
  background: #dfe7f2;
  display: block;
}

/* Animal / exhibit photo cards (match outing visual energy) */
.seo-animal-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin: 12px 0 8px;
}
.seo-animal-card {
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1.5px solid rgba(15, 92, 92, 0.12);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 14px rgba(21, 34, 56, 0.06);
  min-height: 220px;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease;
}
.seo-animal-card:hover {
  border-color: #d9652e;
  box-shadow: 0 8px 20px rgba(217, 101, 46, 0.14);
  transform: translateY(-1px);
}
.seo-card-hint {
  margin: 4px 0 0 !important;
  font-size: 0.8rem !important;
  font-weight: 800 !important;
  color: #d9652e !important;
}
.seo-animal-card {
  cursor: pointer;
}
.seo-animal-card img {
  width: 100%;
  height: 132px;
  object-fit: cover;
  background: linear-gradient(145deg, #e8f0f8, #d4e4d8);
  display: block;
}
.seo-animal-meta {
  padding: 12px 12px 14px;
  display: grid;
  gap: 4px;
}
.seo-animal-meta h3 {
  margin: 0;
  font-size: 1.02rem;
  font-weight: 800;
  letter-spacing: -0.01em;
  color: #0a4545;
  line-height: 1.2;
}
.seo-animal-meta p {
  margin: 0;
  font-size: 0.88rem;
  font-weight: 650;
  color: #3d4f6f;
  line-height: 1.35;
}

/* Keep text list for crawlers / no-image clients, but de-emphasize visually */
.seo-shortlist-sr {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.seo-prose p {
  margin: 0 0 12px;
  line-height: 1.55;
  font-weight: 600;
  color: #2a3d55;
  font-size: 1.02rem;
}
.seo-list-block {
  margin: 22px 0 8px;
  position: relative;
}
.seo-list-block h2 {
  margin: 0 0 8px;
  font-size: 1.2rem;
  color: #0a4545;
}
.seo-list-block > p {
  margin: 0 0 8px;
  font-weight: 650;
  color: #3d4f6f;
}
.seo-shortlist, .seo-hunt-list {
  margin: 0;
  padding-left: 1.2rem;
  font-weight: 650;
  color: #2a3d55;
  line-height: 1.5;
}
.seo-shortlist li, .seo-hunt-list li { margin-bottom: 6px; }
.seo-how { margin-top: 22px; }
.seo-how h2 { margin: 0 0 10px; font-size: 1.2rem; color: #0a4545; }
.seo-official {
  margin: 18px 0 0;
  font-weight: 650;
  color: #3d4f6f;
  font-size: 0.95rem;
}
.seo-official a { color: #0f5c5c; font-weight: 800; }
.seo-cta { flex-wrap: wrap; gap: 10px; }
.seo-directory {
  margin: 28px 0 18px;
  padding: 20px 18px 22px;
  border-radius: 24px;
  background: rgba(255,255,255,0.9);
  border: 1.5px solid rgba(15, 92, 92, 0.12);
}
.seo-directory h2 {
  margin: 0 0 8px;
  font-size: 1.25rem;
  color: #0a4545;
}
.seo-directory > p {
  margin: 0 0 14px;
  font-weight: 650;
  color: #3d4f6f;
}
.seo-dir-grid {
  columns: 2;
  column-gap: 24px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.seo-dir-grid li {
  break-inside: avoid;
  margin: 0 0 8px;
  font-weight: 700;
}
.seo-dir-grid a {
  color: #0a4545;
  text-decoration: none;
  border-bottom: 1px solid rgba(15, 92, 92, 0.25);
}
.seo-dir-grid a:hover { color: #0f5c5c; border-bottom-color: #0f5c5c; }
.seo-dir-grid small {
  display: block;
  font-weight: 600;
  color: #5a6b82;
  font-size: 0.82rem;
  margin-top: 1px;
}
.seo-faq {
  margin: 18px 0 24px;
  padding: 20px 18px 8px;
  border-radius: 24px;
  background: rgba(255,255,255,0.9);
  border: 1.5px solid rgba(15, 92, 92, 0.12);
}
.seo-faq h2 {
  margin: 0 0 12px;
  font-size: 1.25rem;
  color: #0a4545;
}
.seo-faq details {
  margin: 0 0 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(232, 246, 240, 0.55);
  border: 1px solid rgba(15, 92, 92, 0.1);
}
.seo-faq summary {
  cursor: pointer;
  font-weight: 800;
  color: #0a4545;
}
.seo-faq details p {
  margin: 8px 0 0;
  font-weight: 600;
  color: #2a3d55;
  line-height: 1.5;
}
@media (max-width: 720px) {
  .seo-animal-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .seo-hero-photos { grid-template-columns: 1fr 1fr; }
  .seo-hero-photos img:nth-child(3) { display: none; }
}
@media (max-width: 640px) {
  .seo-dir-grid { columns: 1; }
  .seo-article { padding: 16px; }
  .seo-animal-grid { grid-template-columns: 1fr; }
  .seo-hero-photos { grid-template-columns: 1fr 1fr; }
  .seo-animal-card img, .seo-hero-photos img { height: 160px; }
}
"""


# Light continent buckets (<10) — venue names stay visible under each heading
_CONTINENT_ORDER = (
    "North America",
    "South America",
    "Europe",
    "Africa & Middle East",
    "Asia",
    "Oceania",
)

# Country / territory label (from location string) → continent
_COUNTRY_CONTINENT = {
    "united states": "North America",
    "usa": "North America",
    "us": "North America",
    "canada": "North America",
    "mexico": "North America",
    "brazil": "South America",
    "argentina": "South America",
    "chile": "South America",
    "peru": "South America",
    "colombia": "South America",
    "united kingdom": "Europe",
    "uk": "Europe",
    "france": "Europe",
    "germany": "Europe",
    "spain": "Europe",
    "italy": "Europe",
    "netherlands": "Europe",
    "belgium": "Europe",
    "ireland": "Europe",
    "austria": "Europe",
    "switzerland": "Europe",
    "portugal": "Europe",
    "sweden": "Europe",
    "norway": "Europe",
    "finland": "Europe",
    "denmark": "Europe",
    "poland": "Europe",
    "hungary": "Europe",
    "czechia": "Europe",
    "czech republic": "Europe",
    "greece": "Europe",
    "russia": "Europe",
    "türkiye": "Europe",
    "turkey": "Europe",
    "uae": "Africa & Middle East",
    "united arab emirates": "Africa & Middle East",
    "south africa": "Africa & Middle East",
    "kenya": "Africa & Middle East",
    "egypt": "Africa & Middle East",
    "india": "Asia",
    "japan": "Asia",
    "china": "Asia",
    "south korea": "Asia",
    "korea": "Asia",
    "singapore": "Asia",
    "taiwan": "Asia",
    "thailand": "Asia",
    "indonesia": "Asia",
    "philippines": "Asia",
    "malaysia": "Asia",
    "hong kong": "Asia",
    "australia": "Oceania",
    "new zealand": "Oceania",
}


def _venue_country_label(v: dict) -> str:
    loc = (v.get("location") or "").strip()
    if "," in loc:
        return loc.split(",")[-1].strip()
    st = (v.get("state") or "").strip()
    if st and len(st) <= 3:
        return "United States"
    if loc and loc not in (v.get("city") or ""):
        return loc
    if st:
        return "United States"
    # Single-name city-states (Singapore) or bare city
    city = (v.get("city") or loc or "").strip()
    if city.lower() in _COUNTRY_CONTINENT:
        return city
    if city.lower() == "singapore":
        return "Singapore"
    if city.lower() == "hong kong":
        return "Hong Kong"
    return city or "International"


def _venue_continent(v: dict) -> str:
    st = (v.get("state") or "").strip()
    # US/CA style state codes → North America
    if st and len(st) <= 3 and st.isalpha():
        # TX, CA, ON-style; DC too
        if st.upper() not in ("UAE",):  # not a US state
            # International places rarely have 2-letter US states
            if st.upper() in {
                "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
                "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
                "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
                "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
                "WV", "WI", "WY",
            }:
                return "North America"
    country = _venue_country_label(v)
    key = country.lower()
    if key in _COUNTRY_CONTINENT:
        return _COUNTRY_CONTINENT[key]
    # Fallback: city match
    city = (v.get("city") or "").strip().lower()
    if city in _COUNTRY_CONTINENT:
        return _COUNTRY_CONTINENT[city]
    return "Asia"  # rare unknown intl → Asia bucket rather than orphan


def _dir_item_html(v: dict) -> str:
    loc = v.get("city") or ""
    if not loc:
        loc = (v.get("location") or "").split(",")[0].strip()
    city = esc(loc) if loc else ""
    small = f"<small>{city}</small>" if city else ""
    return (
        f'<li><a href="/field-pack/{esc(v["id"])}/">{esc(v.get("emoji") or "")} {esc(v["name"])}</a>'
        f"{small}</li>"
    )


def _dir_region_slug(title: str) -> str:
    return (
        title.lower()
        .replace("&", "and")
        .replace(" ", "-")
        .replace(",", "")
    )


def _dir_continent_html(title: str, venues: list[dict]) -> str:
    """Always-open section — venue names stay visible (light structure only)."""
    if not venues:
        return ""
    venues = sorted(
        venues,
        key=lambda x: ((x.get("city") or "").lower(), (x.get("name") or "").lower()),
    )
    items = "\n            ".join(_dir_item_html(v) for v in venues)
    slug = esc(_dir_region_slug(title))
    return (
        f'<section class="seo-dir-region" data-region="{slug}">\n'
        f'          <h3 class="seo-dir-region-title">{esc(title)} '
        f'<span class="seo-dir-count">{len(venues)}</span></h3>\n'
        f'          <ul class="seo-dir-grid">\n            {items}\n          </ul>\n'
        f"        </section>"
    )


def patch_landing_directory(venues: list[dict]) -> None:
    """Fill landing directory in a few continent groups; names always visible."""
    index = FIELD / "index.html"
    html = index.read_text(encoding="utf-8")

    buckets: dict[str, list[dict]] = {c: [] for c in _CONTINENT_ORDER}
    for v in venues:
        cont = _venue_continent(v)
        if cont not in buckets:
            buckets[cont] = []
        buckets[cont].append(v)

    parts = [
        _dir_continent_html(title, buckets[title])
        for title in _CONTINENT_ORDER
        if buckets.get(title)
    ]
    # Any leftover continents not in order
    for title, vs in buckets.items():
        if title not in _CONTINENT_ORDER and vs:
            parts.append(_dir_continent_html(title, vs))

    block = "\n        ".join(parts)
    pattern = re.compile(
        r"(<!-- SEO:DIR-BODY:START -->)([\s\S]*?)(<!-- SEO:DIR-BODY:END -->)",
        re.M,
    )
    if not pattern.search(html):
        print("  WARN: landing directory marker not found")
        return
    html = pattern.sub(
        rf'\1\n        <div id="seo-venue-directory" class="seo-dir-body">\n        {block}\n        </div>\n        \3',
        html,
    )
    index.write_text(html, encoding="utf-8")
    counts = {t: len(buckets[t]) for t in _CONTINENT_ORDER if buckets.get(t)}
    print(f"  patched landing venue directory (continents: {counts})")


def patch_places_data_hrefs(venues: list[dict]) -> None:
    """Point places-data href to indexable /field-pack/<id>/ URLs."""
    path = PLACES_JS
    text = path.read_text(encoding="utf-8")
    for v in venues:
        # href: "places/dallas-zoo.html" → href: "/field-pack/dallas-zoo/"
        text = re.sub(
            rf'(id:\s*"{re.escape(v["id"])}"[\s\S]*?href:\s*)"(?:places/)?{re.escape(v["id"])}\.html"',
            rf'\1"/field-pack/{v["id"]}/"',
            text,
            count=1,
        )
    path.write_text(text, encoding="utf-8")
    print("  patched places-data.js hrefs → /field-pack/<id>/")


def main() -> int:
    print("Loading venues…")
    venues = load_venues()
    venues.sort(key=lambda v: (v.get("state") or "", v.get("city") or "", v["name"]))
    print(f"  {len(venues)} venues")

    css_path = FIELD / "css" / "seo-venue.css"
    # Prefer hand-maintained css (visual-first enhancements); seed once if missing
    if not css_path.is_file() or css_path.stat().st_size < 500:
        css_path.write_text(SEO_CSS, encoding="utf-8")
        print(f"  seeded {css_path.relative_to(REPO)}")
    else:
        print(f"  kept {css_path.relative_to(REPO)} (not overwritten)")

    # Validate mission venue data when present
    try:
        from validate_venue_data import main as validate_main
        import sys as _sys
        _rc = validate_main()
        if _rc != 0:
            print("  WARN: venue data validation reported issues")
    except Exception as ex:
        print(f"  WARN: validator skip ({ex})")

    urls = []
    for v in venues:
        out_dir = FIELD / v["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        mission_v = load_mission_venue(v["id"])
        if mission_v:
            try:
                html = render_mission_venue_page(v, mission_v)
                print(f"  mission page {v['id']}")
            except Exception as ex:
                print(f"  WARN mission page failed {v['id']}: {ex}; using legacy")
                html = render_venue_page(v)
        else:
            html = render_venue_page(v)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        urls.append(f"/field-pack/{v['id']}/")
        text = re.sub(r"<[^>]+>", " ", html)
        words = len(re.findall(r"\w+", text))
        if words < 120:
            print(f"  WARN thin page {v['id']}: ~{words} words")

    patch_landing_directory(venues)
    patch_places_data_hrefs(venues)
    write_sitemap(venues)
    write_robots()
    manifest = {
        "generated": TODAY,
        "count": len(urls),
        "urls": [f"{SITE}{u}" for u in urls],
        "landing": f"{SITE}/field-pack/",
    }
    (FIELD / "seo-venues.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    # human-readable URL list for Search Console
    (FIELD / "SEO_URLS.txt").write_text(
        "\n".join([manifest["landing"]] + manifest["urls"]) + "\n",
        encoding="utf-8",
    )
    print(f"  wrote {len(urls)} venue pages")
    print(f"  sitemap → static/sitemap.xml")
    print(f"  robots  → static/robots.txt")
    print(f"  URL list → static/field-pack/SEO_URLS.txt")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as e:
        print(e.stderr or e.stdout, file=sys.stderr)
        raise SystemExit(1)
