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


def unique_body(v: dict) -> str:
    """150–250+ words of unique, venue-specific copy."""
    place, things, hunt_word = type_bits(v)
    name = v["name"]
    city = v["city"] or v["location"] or "your city"
    state = v["state"] or ""
    loc = v["location"] or ", ".join(x for x in [city, state] if x)
    blurb = (v.get("blurb") or "").rstrip(".")
    featured = v.get("featured") or []
    hunt = v.get("hunt") or []
    label = v.get("itemLabel") or things
    emoji = v.get("emoji") or ""

    feat_names = [f["name"] for f in featured[:6]]
    feat_phrase = (
        ", ".join(feat_names[:-1]) + f", and {feat_names[-1]}"
        if len(feat_names) > 1
        else (feat_names[0] if feat_names else "kid favorites")
    )

    openers = [
        f"Planning a kid-friendly day at {name} in {loc}? Field Trip Kit by 1Less gives you a free printable {hunt_word} and a short list of {label} so you are not staring at a map of hundreds of options.",
        f"Visiting {name} with kids does not have to mean wandering until everyone is tired. This free one-page {hunt_word} for {loc} keeps the day focused and fun.",
        f"If you searched for a {name} scavenger hunt for kids or a printable checklist for {city}, you are in the right place — a finishable kit, not an encyclopedia.",
        f"{emoji + ' ' if emoji else ''}{name} is a classic {place} stop in {loc}. Families use this free printable scavenger hunt to give little explorers a clear mission without overpacking the day.",
    ]
    middles = [
        f"The shortlist highlights {feat_phrase}. Each pick has a kid-sized blurb so a preschooler or early elementary explorer can understand why it is cool before you arrive.",
        f"Instead of racing through every exhibit, start with top picks like {feat_phrase}. That keeps toddlers and school-age kids engaged without overwhelm.",
        f"Your printable kit focuses on {feat_phrase} — a manageable set for young kids through about age 10–11, with room to skip anything that is closed or crowded.",
    ]
    hunt_bits = "; ".join(hunt[:4]) if hunt else "spot something tall, find a pattern, and photo a favorite"
    hunt_para = [
        f"The treasure hunt is one page: check boxes as you go. Sample challenges include {hunt_bits}. There is no score and no app required on site — print before you leave home or save the page for later.",
        f"On the hunt sheet, kids can check off finds such as {hunt_bits}. Grown-ups stay free to enjoy the day; the paper does the guiding.",
    ]
    tips = [
        f"Practical tip for {city}: print the hunt the night before, pack a pen, and start with one or two favorites near the entrance so early energy pays off.",
        f"For {name}, arrive with the one-page hunt in your bag, pick a first target from the shortlist, and treat the rest as bonus — a calm day beats a complete checklist.",
        f"Weather or crowds in {state or city} can change plans. The shortlist and hunt are designed so you can reorder stops without losing the fun.",
    ]
    closes = [
        f"{blurb + '. ' if blurb else ''}Field Trip Kit is free to use. Open the full interactive list when you want optional Q&A cards, or use the one-page hunt alone for a lighter outing.",
        f"{'About this place: ' + blurb + '. ' if blurb else ''}Everything here is free to print and share with co-parents or grandparents joining the day.",
        f"{blurb + '. ' if blurb else ''}1Less keeps the promise simple: one less decision before a museum or zoo day with kids.",
    ]

    seed = v["id"]
    p1 = pick(seed + "a", openers)
    p2 = pick(seed + "b", middles)
    p3 = pick(seed + "c", hunt_para)
    p4 = pick(seed + "d", tips)
    p5 = pick(seed + "e", closes)

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
        blurb = it.get("blurb") or "A favorite stop for curious kids."
        item_id = it.get("id") or ""
        card_inner = ""
        if src:
            card_inner = f"""<img src="{esc(src)}" alt="{esc(alt)}" width="640" height="400" loading="lazy" decoding="async" />
          <div class="seo-animal-meta">
            <h3>{esc(it.get('emoji',''))} {esc(it['name'])}</h3>
            <p>{esc(blurb)}</p>
            <p class="seo-card-hint">Open the interactive list for this Q&amp;A card</p>
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
            f"<li><strong>{esc(it.get('emoji',''))} {esc(it['name'])}</strong> — {esc(blurb)}</li>"
        )

    hunt_lis = "".join(f"<li>{esc(t)}</li>" for t in hunt[:8]) or "<li>Find your favorite stop and check it off</li>"
    cards_html = (
        f'<div class="seo-animal-grid" role="list">{"".join(cards)}</div>'
        if cards
        else ""
    )

    words = " ".join([p1, p2, p3, p4, p5])
    if len(words.split()) < 150:
        p5 += (
            f" Families comparing printable zoo scavenger hunts, aquarium checklists, "
            f"and museum treasure hunts for kids can use this {name} page as a ready-made plan for {loc}."
        )

    # Hero strip: first 3 photos if available
    hero_photos = []
    for it in featured[:3]:
        photo = (it.get("photo") or "").strip()
        if not photo:
            continue
        if photo.startswith("/field-pack/"):
            src = photo[len("/field-pack/") :]
        else:
            src = photo
        hero_photos.append(
            f'<img src="{esc(src)}" alt="{esc(it.get("name") or "Highlight")} — shortlist photo" width="400" height="280" loading="eager" decoding="async" />'
        )
    hero_strip = (
        f'<div class="seo-hero-photos" aria-hidden="false">{"".join(hero_photos)}</div>'
        if hero_photos
        else ""
    )

    return f"""
    {hero_strip}
    <section class="seo-list-block seo-visual-shortlist" aria-labelledby="shortlist-heading">
      <h2 id="shortlist-heading">More Q&amp;A cards at {esc(name)}</h2>
      <p>Photo cards for the kid shortlist — open any card for the interactive outing and printable Q&amp;A.</p>
      {cards_html}
      <ul class="seo-shortlist seo-shortlist-sr">
        {"".join(feat_html_parts) or "<li>Open the interactive outing for the full shortlist.</li>"}
      </ul>
    </section>
    <section class="seo-prose">
      <p>{esc(p1)}</p>
      <p>{esc(p2)}</p>
      <p>{esc(p3)}</p>
      <p>{esc(p4)}</p>
      <p>{esc(p5)}</p>
    </section>
    <section class="seo-list-block" aria-labelledby="hunt-heading">
      <h2 id="hunt-heading">Treasure hunt checklist (printable)</h2>
      <p>Sample finds from the free one-page hunt for {esc(name)}:</p>
      <ol class="seo-hunt-list">
        {hunt_lis}
      </ol>
    </section>
"""


def h1_for(v: dict) -> str:
    place, _, hunt_word = type_bits(v)
    # Prefer scavenger hunt wording for SEO
    return f"{v['name']} Scavenger Hunt for Kids (Free Printable)"


def title_for(v: dict) -> str:
    return f"{h1_for(v)} · 1Less"


def meta_for(v: dict) -> str:
    city = v["city"] or v["location"] or ""
    place, things, _ = type_bits(v)
    base = (
        f"Free printable {v['name']} scavenger hunt for kids in {city}. "
        f"Short kid list of {things}, one-page treasure hunt — Field Trip Kit by 1Less."
    )
    return base[:158]


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

    howto = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": h1_for(v),
        "description": meta_for(v),
        "totalTime": "PT2H",
        "tool": [{"@type": "HowToTool", "name": "Printed one-page hunt sheet"}],
        "step": steps,
        "url": url,
    }
    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": h1_for(v),
        "description": meta_for(v),
        "author": {"@type": "Organization", "name": "1Less"},
        "publisher": {"@type": "Organization", "name": "1Less", "url": SITE},
        "mainEntityOfPage": url,
        "about": {"@type": "Place", "name": v["name"], "address": v.get("location") or ""},
    }
    return json.dumps(howto, ensure_ascii=False) + "\n" + json.dumps(article, ensure_ascii=False)


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
  <link rel="stylesheet" href="/shell/shell.css?v=4" />
  <link rel="stylesheet" href="/field-pack/css/styles.css?v=18" />
  <link rel="stylesheet" href="/field-pack/css/landing.css?v=35" />
  <link rel="stylesheet" href="/field-pack/css/seo-venue.css?v=3" />
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
      <a class="shell-brand" href="/">
        <img src="/1LessMark.png" alt="1Less logo" width="52" height="52" />
        1Less
      </a>
      <p class="shell-product">
        Field Trip Kit
        <small>Zoo, aquarium &amp; museum days</small>
      </p>
      <div class="shell-more-wrap">
        <button type="button" class="shell-more" aria-expanded="false" aria-haspopup="true" aria-controls="shell-menu">More</button>
        <div id="shell-menu" class="shell-menu" hidden role="menu">
          <a href="/field-pack/" role="menuitem">Field Trip Kit<small>Map &amp; outings</small></a>
          <a href="/dinner" role="menuitem">Dinner<small>Tonight’s meal</small></a>
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
            "Curated shortlist for a finishable kid day."
            + (f' List checked {v["lastVerified"][:7]}.' if (v.get("lastVerified") or "")[:7] else "")
          )
          if (v.get("quality") or "starter") == "full"
          else "Starter shortlist — animals and exhibits change; skip anything closed or missing."
        )}</p>
        <p class="seo-brand-note">Part of <strong>Field Trip Kit</strong> by 1Less — free for families.</p>
        <div class="landing-cta-row seo-cta no-print">
          <a class="btn btn-primary btn-big" href="{esc(map_href)}">Open on map →</a>
          <button type="button" class="btn btn-secondary btn-big" id="seo-print-hunt" data-venue="{esc(vid)}">
            One-page hunt to print
          </button>
          <a class="btn btn-ghost" href="{esc(app_href)}">Full interactive list →</a>
        </div>
      </header>

      {body}

      <section class="seo-how" aria-labelledby="how-heading">
        <h2 id="how-heading">How it works</h2>
        <ol class="how-steps">
          <li><strong>1</strong><span>Print the one-page hunt</span></li>
          <li><strong>2</strong><span>Use the shortlist on site</span></li>
          <li><strong>3</strong><span>Optional: open Q&amp;A cards after</span></li>
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
        <strong>1Less</strong> · Field Trip Kit ·
        <a href="/dinner">Dinner</a>
      </p>
    </footer>
  </div>

  <div id="print-sheet" class="print-sheet" aria-hidden="true"></div>
  <div id="treasure-sheet" class="print-sheet treasure-sheet" aria-hidden="true"></div>

  <script src="/shell/shell.js?v=3"></script>
  <script src="/field-pack/js/catalog.js?v=12"></script>
  <script src="/field-pack/js/print-kit.js?v=1"></script>
  <script>
    (function () {{
      var btn = document.getElementById("seo-print-hunt");
      if (!btn || !window.FPPrint) return;
      btn.addEventListener("click", function () {{
        var id = btn.getAttribute("data-venue");
        if (!window.FPPrint.printTreasureForVenue(id)) {{
          location.href = "/field-pack/app.html#/venue/" + encodeURIComponent(id);
        }}
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


def patch_landing_directory(venues: list[dict]) -> None:
    """Fill #seo-venue-directory list on the landing page."""
    index = FIELD / "index.html"
    html = index.read_text(encoding="utf-8")
    items = []
    for v in venues:
        loc = ", ".join(x for x in [v.get("city"), v.get("state")] if x) or v.get("location") or ""
        items.append(
            f'<li><a href="/field-pack/{esc(v["id"])}/">{esc(v.get("emoji",""))} {esc(v["name"])}</a>'
            f"<small>{esc(loc)} · free printable scavenger hunt</small></li>"
        )
    block = "\n          ".join(items)
    pattern = re.compile(
        r'(<ul class="seo-dir-grid" id="seo-venue-directory">)([\s\S]*?)(</ul>)',
        re.M,
    )
    if not pattern.search(html):
        print("  WARN: landing directory marker not found")
        return
    html = pattern.sub(rf"\1\n          {block}\n        \3", html)
    index.write_text(html, encoding="utf-8")
    print("  patched landing venue directory")


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
    css_path.write_text(SEO_CSS, encoding="utf-8")
    print(f"  wrote {css_path.relative_to(REPO)}")

    urls = []
    for v in venues:
        out_dir = FIELD / v["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
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
