/**
 * Shared print helpers for Field Trip Kit (landing pin panel + outing app).
 * Requires: catalog.js (fpGetVenue, FIELD_PACK_CATALOG, fpMissionsForVenue)
 * DOM: #print-sheet, #treasure-sheet
 */
(() => {
  function escapeHtml(s) {
    return String(s ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replaceAll("'", "&#39;");
  }

  function track(name, params) {
    const fn =
      (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
    if (typeof fn === "function") fn(name, params || {});
  }

  function sheets() {
    return {
      printSheet: document.getElementById("print-sheet"),
      treasureSheet: document.getElementById("treasure-sheet"),
    };
  }

  function getVenue(id) {
    return typeof window.fpGetVenue === "function" ? window.fpGetVenue(id) : null;
  }

  function getItem(id) {
    return (window.FIELD_PACK_CATALOG && window.FIELD_PACK_CATALOG[id]) || null;
  }

  function missionsFor(venue) {
    if (typeof window.fpMissionsForVenue === "function") return window.fpMissionsForVenue(venue);
    return window.FIELD_PACK_MISSIONS_ANIMALS || [];
  }

  /** Featured / top-pick item id for a venue (first featured, else first animal). */
  function topPickItemId(venue) {
    if (!venue) return null;
    const featured = venue.featuredAnimalIds || [];
    if (featured.length) return featured[0];
    const all = venue.animalIds || [];
    return all[0] || null;
  }

  /** Print-safe local map path (prefer hosted preview under /field-pack/media/maps/). */
  function printMapForVenue(venue) {
    const id = (venue && (venue.id || venue.slug)) || "";
    const maps = window.FP_PRINT_MAPS || {};
    if (id && maps[id]) return maps[id];
    // SEO pages embed full mission venue JSON
    try {
      const el = document.getElementById("venue-data");
      if (el && el.textContent) {
        const data = JSON.parse(el.textContent);
        const m = (data && data.media) || {};
        const u = m.print_map || m.visitor_map_url || "";
        if (u && String(u).startsWith("/field-pack/media/maps/")) return u;
      }
    } catch (_) {
      /* ignore */
    }
    const m = (venue && venue.media) || {};
    const u = m.print_map || m.visitor_map_url || "";
    if (u && String(u).startsWith("/field-pack/media/maps/")) return u;
    return "";
  }

  function buildTreasureHtml(venue, starIds) {
    const hunts = (venue.treasureHunt || []).slice(0, 8);
    const huntHtml = hunts
      .map(
        (h, i) => `
      <div class="th-row">
        <span class="th-box"></span>
        <span class="th-num">${i + 1}</span>
        <span class="th-text">${escapeHtml(h.text)}</span>
      </div>`
      )
      .join("");
    const ids = (starIds && starIds.length ? starIds : venue.featuredAnimalIds || []).slice(0, 6);
    const stars = ids
      .map((id) => {
        const it = getItem(id);
        return it ? `<span class="th-chip">${it.emoji || "•"} ${escapeHtml(it.name)}</span>` : "";
      })
      .join("");
    const mapSrc = printMapForVenue(venue);
    const mapBlock = mapSrc
      ? `<div class="th-map th-map-has-photo">
          <p class="th-map-title">Park map — mark start → favorite → end</p>
          <div class="th-map-photo-wrap">
            <img class="th-map-photo" src="${escapeAttr(mapSrc)}" alt="Official visitor map" />
          </div>
        </div>`
      : `<div class="th-map">
          <p class="th-map-title">Path doodle <span class="th-map-hint">— start → favorite → end</span></p>
          <div class="th-map-box"></div>
        </div>`;
    return `
      <div class="th-page${mapSrc ? " th-page-with-map" : ""}">
        <div class="th-banner">
          <h1>🗺️ Your mission</h1>
          <p>${escapeHtml(venue.name)} · One-page hunt · Field Trip Kit</p>
        </div>
        <div class="th-meta">
          <p><strong>Place:</strong> ${escapeHtml(venue.name)}
          &nbsp;·&nbsp; <strong>Where:</strong> ${escapeHtml(venue.location || "")}</p>
          <p><strong>Explorer:</strong> <span class="write-in-line">________________</span>
          &nbsp;&nbsp; <strong>Date:</strong> ____________</p>
        </div>
        <p class="th-intro">Your mission: check each box when you find it. No rush!</p>
        <div class="th-list">${huntHtml}</div>
        <div class="th-stars">
          <p class="th-stars-title">Star list (top picks)</p>
          <div class="th-chips">${stars}</div>
        </div>
        ${mapBlock}
        <p class="th-footer">Optional after: open Field Trip Kit → tap a card → Q&A</p>
      </div>`;
  }

  /** Resolve catalog photo path for print/screen. */
  function itemPhotoSrc(item) {
    const p = (item && item.photo) || "";
    if (!p) return "";
    if (/^https?:\/\//i.test(p) || p.startsWith("/")) return p;
    // catalog uses "photos/foo.jpg"
    if (p.startsWith("photos/")) return "/field-pack/" + p;
    return "/field-pack/photos/" + p.replace(/^\/+/, "");
  }

  /**
   * One kid/parent wow line — prefer blurb, else superpower / home fact.
   * Returns { q, a } for a tight Did-you-know strip under the big photo.
   */
  function wowFactFromItem(item) {
    if (!item) return null;
    const key = item.key || {};
    const superpower = [].concat(key.superpower || []).filter(Boolean);
    const home = [].concat(key.home || []).filter(Boolean);
    const food = [].concat(key.food || []).filter(Boolean);
    const name = item.name || "This animal";

    if (item.blurb && String(item.blurb).trim()) {
      return { q: "Did you know?", a: String(item.blurb).trim() };
    }
    if (superpower.length) {
      return {
        q: `What's ${name}'s superpower?`,
        a: superpower.slice(0, 2).join(" · "),
      };
    }
    if (home.length) {
      return {
        q: `Where does a ${name} feel at home?`,
        a: home.slice(0, 2).join(" · "),
      };
    }
    if (food.length) {
      return {
        q: `What's on the menu?`,
        a: food.slice(0, 2).join(" · "),
      };
    }
    return null;
  }

  function buildQaCardHtml(item, venue) {
    const missions = missionsFor(venue);
    const cards = missions
      .map((mission, index) => {
        const choices = (mission.choices || [])
          .map(
            (label) =>
              `<div class="ps-choice"><span class="ps-dot"></span><span>${escapeHtml(label)}</span></div>`
          )
          .join("");
        return `<section class="ps-card c${index}">
          <div class="ps-card-head"><span class="ps-num">${escapeHtml(mission.num)}</span>
          <p class="ps-title">${escapeHtml(mission.title)}</p></div>
          <h3 class="ps-q">${escapeHtml(mission.question)}</h3>
          <div class="ps-choices">${choices}</div></section>`;
      })
      .join("");
    const photo = itemPhotoSrc(item);
    const wow = wowFactFromItem(item);
    const wowHtml = wow
      ? `<div class="ps-wow">
          <strong class="ps-wow-q">${escapeHtml(wow.q)}</strong>
          <span class="ps-wow-a">${escapeHtml(wow.a)}</span>
        </div>`
      : "";
    const photoBlock = photo
      ? `<div class="ps-photo-fill">
          <div class="ps-photo-frame">
            <img class="ps-photo-big" src="${escapeAttr(photo)}" alt="${escapeAttr(item.name || "Animal")}" />
          </div>
          ${wowHtml}
        </div>`
      : wowHtml
        ? `<div class="ps-wow ps-wow-solo">
            <strong class="ps-wow-q">${escapeHtml(wow.q)}</strong>
            <span class="ps-wow-a">${escapeHtml(wow.a)}</span>
          </div>`
        : "";

    return `
      <div class="ps-page${photo ? " ps-page-with-photo" : ""}">
        <div class="ps-banner"><h1>FIELD TRIP KIT</h1>
        <p>${escapeHtml(venue.name)} · Sample mission card · Circle answers · No scores</p></div>
        <header class="ps-head">
          <h2>${escapeHtml(item.emoji || "")} ${escapeHtml(item.name)}</h2>
          <p class="ps-line"><strong>Explorer:</strong> <span class="write-in-line">________________</span>
          &nbsp;&nbsp; <strong>Place:</strong> ${escapeHtml(venue.name)}</p>
        </header>
        <div class="ps-grid">${cards}</div>
        ${photoBlock}
        <p class="ps-footer">Sample Q&amp;A · open the outing for more animals &amp; tips</p>
      </div>`;
  }

  function runPrint({ treasure }) {
    document.body.classList.toggle("printing-treasure", Boolean(treasure));
    const cleanup = () => {
      document.body.classList.remove("printing-treasure");
      window.removeEventListener("afterprint", cleanup);
    };
    window.addEventListener("afterprint", cleanup);
    requestAnimationFrame(() => requestAnimationFrame(() => window.print()));
  }

  /**
   * Print treasure hunt for a venue (full catalog hunt + star list).
   */
  function printTreasureForVenue(venueId) {
    const venue = getVenue(venueId);
    const { printSheet, treasureSheet } = sheets();
    if (!venue || !treasureSheet) {
      console.warn("[FPPrint] missing venue or #treasure-sheet", venueId);
      return false;
    }
    if (!(venue.treasureHunt && venue.treasureHunt.length)) {
      console.warn("[FPPrint] no treasure hunt for", venueId);
      return false;
    }
    treasureSheet.innerHTML = buildTreasureHtml(venue, venue.featuredAnimalIds);
    if (printSheet) printSheet.innerHTML = "";
    track("hunt_generated", {
      venue_slug: venue.id || venueId,
      venue_name: venue.name || "",
      product: "babys_day_out",
      source: "print_kit",
    });
    runPrint({ treasure: true });
    return true;
  }

  /**
   * Print one sample Q&A card — first featured / top-pick item for the venue.
   */
  function printSampleQaForVenue(venueId) {
    const venue = getVenue(venueId);
    const itemId = topPickItemId(venue);
    const item = itemId ? getItem(itemId) : null;
    const { printSheet, treasureSheet } = sheets();
    if (!venue || !item || !printSheet) {
      console.warn("[FPPrint] sample Q&A unavailable for", venueId);
      return false;
    }
    printSheet.innerHTML = buildQaCardHtml(item, venue);
    if (treasureSheet) treasureSheet.innerHTML = "";
    track("qa_sample_printed", {
      venue_slug: venue.id || venueId,
      venue_name: venue.name || "",
      item_id: item.id,
      item_name: item.name || "",
      product: "babys_day_out",
    });
    runPrint({ treasure: false });
    return true;
  }

  window.FPPrint = {
    printTreasureForVenue,
    printSampleQaForVenue,
    topPickItemId,
    getVenue,
    getItem,
  };
})();
