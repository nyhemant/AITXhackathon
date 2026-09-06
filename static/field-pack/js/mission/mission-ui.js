/**
 * Mission print drawer for pilot venue pages.
 * Page stays clean; #mission-open-btn opens filters + live sheet.
 */
(function () {

  function checkedMonthLabel(raw) {
    const m = String(raw || "").trim().match(/^(\d{4})-(\d{2})/);
    if (!m) return "";
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const month = Number(m[2]);
    if (month < 1 || month > 12) return "";
    return `${months[month - 1]} ${m[1]}`;
  }

  function statusLineFromVenue(venue) {
    // Same two labels as generate_bdo_seo / field_pack_kit_tier.py.
    // Verified only when list_confidence is audited AND last_presence_audit is a real date.
    const conf = (venue && venue.list_confidence) || "";
    if (conf === "audited") {
      const month = checkedMonthLabel(venue && venue.last_presence_audit);
      if (month) return `Verified kit · checked ${month}`;
    }
    return "Starter list";
  }

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  /** Map thumbnail: hover peeks; click pins enlarge on-page (no accidental leave). */
  const MapPreview = (function () {
    let docWired = false;

    function setOpen(card, open) {
      if (!card) return;
      card.classList.toggle("is-open", open);
      const btn = card.querySelector(".seo-map-enlarge-hit, .ms-map-enlarge-hit");
      const panel = card.querySelector(".seo-map-preview, .ms-map-preview");
      if (btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
      if (panel) {
        if (open) panel.removeAttribute("hidden");
        else panel.setAttribute("hidden", "");
      }
    }

    function closeAll(except) {
      document.querySelectorAll("[data-map-preview].is-open").forEach((c) => {
        if (c !== except) setOpen(c, false);
      });
    }

    function wireCard(card) {
      if (!card || card.dataset.mapPreviewWired === "1") return;
      card.dataset.mapPreviewWired = "1";
      const hit = card.querySelector(".seo-map-enlarge-hit, .ms-map-enlarge-hit");
      const closeBtn = card.querySelector(".seo-map-preview-close");
      if (hit) {
        hit.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          const next = !card.classList.contains("is-open");
          closeAll(card);
          setOpen(card, next);
        });
      }
      if (closeBtn) {
        closeBtn.addEventListener("click", (e) => {
          e.preventDefault();
          e.stopPropagation();
          setOpen(card, false);
          hit?.focus();
        });
      }
      // External links: leave behavior intentional — stop pin toggle only
      card.querySelectorAll("a[href]").forEach((a) => {
        a.addEventListener("click", (e) => e.stopPropagation());
      });
    }

    function wire(root) {
      const scope = root || document;
      scope.querySelectorAll("[data-map-preview]").forEach(wireCard);
      if (docWired) return;
      docWired = true;
      document.addEventListener("click", (e) => {
        if (e.target.closest && e.target.closest("[data-map-preview].is-open")) return;
        closeAll();
      });
      document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeAll();
      });
    }

    return { wire, closeAll, setOpen };
  })();
  window.FPMapPreview = MapPreview;

  function venueTypeForAnalytics(mission) {
    const t = String((mission && mission.venue_type) || (mission && mission.type) || "").toLowerCase();
    if (t === "national_park" || t === "park") return "park";
    if (t === "aquarium") return "aquarium";
    if (t === "museum" || t === "science_museum" || t === "children_museum") return "museum";
    if (t === "zoo" || t === "safari_zoo") return "zoo";
    // fallback from slug-less venue blob on sheet
    const v = window.__FP_MISSION_VENUE || null;
    const vt = String((v && v.type) || "").toLowerCase();
    if (vt === "national_park") return "park";
    if (vt.includes("aquarium")) return "aquarium";
    if (vt.includes("museum")) return "museum";
    if (vt.includes("zoo")) return "zoo";
    return vt || "unknown";
  }

  function track(event, params) {
    try {
      if (typeof window.FPTrack === "function") {
        window.FPTrack(event, params || {});
        return;
      }
      if (typeof gtag === "function") {
        gtag("event", event, params || {});
      } else if (window.dataLayer) {
        window.dataLayer.push(Object.assign({ event: event }, params || {}));
      }
    } catch (_) {
      /* ignore */
    }
  }

  function esc(s) {
    return String(s || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  let venue = null;
  let challenges = null;
  let wonders = null;
  let bonusHunts = null;
  let state = { age: "4-5", time: "half", interest: "", name: "", seed: 1, hunt: "classic" };
  let lastMission = null;
  let genTimer = null;
  let lastFocus = null;
  let drawerReady = false;

  function normalizeAgeKey(raw) {
    if (window.FPMission && typeof window.FPMission.normalizeAge === "function") {
      return window.FPMission.normalizeAge(raw);
    }
    const a = String(raw || "4-5");
    if (a === "9+" || a === "adults" || a === "solo") return "adult";
    if (a === "1hr") return "4-5";
    return a || "4-5";
  }

  function normalizeTimeKey(raw) {
    const t = String(raw || "half");
    // Collapse legacy ~1 hr into 90 min (same find count)
    if (t === "1hr") return "90m";
    if (t === "90m" || t === "half" || t === "full") return t;
    return "half";
  }

  function normalizeHuntKey(raw) {
    if (window.FPMission && typeof window.FPMission.normalizeHunt === "function") {
      return window.FPMission.normalizeHunt(raw);
    }
    const h = String(raw || "classic").toLowerCase();
    if (h === "alpha" || h === "ultra" || h === "expert") return "alpha";
    if (h === "bonus" || h === "hard") return "bonus";
    return "classic";
  }

  /**
   * Exclusive chip selection. Only buttons that *have* `attr` participate —
   * missing attributes must never match (null === null would mark whole rows active).
   */
  function setSegActive(rootSel, attr, value) {
    const want = value == null ? "" : String(value);
    document.querySelectorAll(rootSel).forEach((btn) => {
      if (!btn.hasAttribute(attr)) return;
      const on = String(btn.getAttribute(attr) || "") === want;
      if (on) btn.classList.add("is-active");
      else btn.classList.remove("is-active");
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  /** Activate one value inside each chip group container. */
  function setGroupChip(groupSel, attr, value) {
    const want = value == null ? "" : String(value);
    document.querySelectorAll(groupSel).forEach((group) => {
      group.querySelectorAll("button").forEach((btn) => {
        if (!btn.hasAttribute(attr)) return;
        const on = String(btn.getAttribute(attr) || "") === want;
        if (on) btn.classList.add("is-active");
        else btn.classList.remove("is-active");
        btn.setAttribute("aria-pressed", on ? "true" : "false");
      });
    });
  }

  function setSectionHeadings(mission) {
    const fh = $("#mission-finds-heading") || document.querySelector("#mission-sheet .ms-section");
    const bh = $("#mission-bonus-heading");
    if (fh) fh.textContent = mission.findsHeading || "Find these";
    if (bh) bh.textContent = mission.bonusHeading || "Bonus";
    else {
      const heads = document.querySelectorAll("#mission-sheet .ms-section");
      if (heads[1]) heads[1].textContent = mission.bonusHeading || "Bonus";
    }
  }

  function syncAudienceChrome(mission) {
    const adult = mission && mission.audience === "adult";
    const nameField = document.querySelector(".mission-field-name");
    const nameLabel = nameField && nameField.querySelector("label");
    const nameInput = $("#mission-name");
    const fav = document.querySelector(".ms-favorite");
    document.body.classList.toggle("mission-audience-adult", !!adult);
    if (nameLabel) {
      nameLabel.innerHTML = adult
        ? 'Your name <span class="mission-opt">(optional)</span>'
        : 'Kid name <span class="mission-opt">(optional)</span>';
    }
    if (nameInput) {
      nameInput.placeholder = adult ? "e.g. Alex" : "e.g. Arya";
      if (adult && !nameInput.value) {
        /* keep empty — solo sheets don't need a name */
      }
    }
    if (fav) {
      fav.textContent = adult
        ? "I'd recommend _______________________ to a friend"
        : "My favorite was _______________________";
    }
    const drawer = $("#mission-drawer");
    if (drawer) drawer.setAttribute("data-audience", adult ? "adult" : "kid");
  }

  function renderSheet(mission) {
    const title = $("#mission-title");
    const meta = $("#mission-meta");
    const findsEl = $("#mission-finds");
    const chEl = $("#mission-challenges");
    const sheet = $("#mission-sheet");
    if (title) title.textContent = mission.title;
    if (meta) {
      const parts = [mission.ageLabel, mission.timeLabel];
      if (mission.hunt === "alpha") parts.push(mission.huntLabel || "Alpha");
      else if (mission.hunt === "bonus") parts.push(mission.huntLabel || "Bonus hunt");
      else if (mission.contentMode === "wonder") parts.push("Flexible finds");
      if (mission.huntTagline && (mission.hunt === "bonus" || mission.hunt === "alpha")) {
        const tagCls = mission.hunt === "alpha" ? "ms-hunt-tag ms-hunt-tag-alpha" : "ms-hunt-tag";
        meta.innerHTML = `${esc(parts.join(" · "))}<br><span class="${tagCls}">${esc(
          mission.huntTagline
        )}</span>`;
      } else {
        meta.textContent = parts.join(" · ");
      }
    }
    if (sheet) {
      sheet.classList.toggle("ms-sheet-bonus", mission.hunt === "bonus");
      sheet.classList.toggle("ms-sheet-alpha", mission.hunt === "alpha");
    }
    setSectionHeadings(mission);
    syncAudienceChrome(mission);
    if (findsEl) {
      findsEl.innerHTML = (mission.finds || [])
        .map(
          (f) => `<li class="mission-find">
          <span class="mission-check" aria-hidden="true">☐</span>
          <span class="mission-emoji">${esc(f.emoji || "📍")}</span>
          <span class="mission-find-body">
            <strong>${esc(f.label)}</strong>
            <small>${esc(f.one_liner || "")}${f.zone ? ` · ${esc(f.zone)}` : ""}</small>
          </span>
        </li>`
        )
        .join("");
    }
    if (chEl) {
      chEl.innerHTML = (mission.challenges || [])
        .map(
          (c) => `<li class="mission-challenge">
          <span class="mission-check" aria-hidden="true">☐</span>
          <span>${esc(c.text)}</span>
        </li>`
        )
        .join("");
    }
    const ver = $("#mission-verified");
    if (ver) ver.textContent = statusLineFromVenue(venue);
    const sheetEl = $("#mission-sheet");
    // Easter egg line (bonus hunt)
    let egg = sheetEl && sheetEl.querySelector(".ms-easter-egg");
    if (sheetEl) {
      if (mission.easterEgg) {
        if (!egg) {
          egg = document.createElement("p");
          egg.className = "ms-easter-egg";
          const foot = sheetEl.querySelector(".ms-footer");
          if (foot) sheetEl.insertBefore(egg, foot);
          else sheetEl.appendChild(egg);
        }
        egg.hidden = false;
        egg.innerHTML = `<span class="mission-check" aria-hidden="true">☐</span> ${esc(
          mission.easterEgg
        )}`;
      } else if (egg) {
        egg.hidden = true;
        egg.textContent = "";
      }
    }
    if (sheetEl && !sheetEl.querySelector(".ms-favorite")) {
      const fav = document.createElement("p");
      fav.className = "ms-favorite";
      fav.textContent =
        mission.audience === "adult"
          ? "I'd recommend _______________________ to a friend"
          : "My favorite was _______________________";
      const foot = sheetEl.querySelector(".ms-footer");
      if (foot) sheetEl.insertBefore(fav, foot);
      else sheetEl.appendChild(fav);
    }

    // Park safety line (print + screen) — parks only
    if (sheetEl) {
      let safety = sheetEl.querySelector(".ms-safety-footer");
      const safetyText =
        (mission && mission.safetyFooter) ||
        (window.FPMission && window.FPMission.parkSafetyFooter
          ? window.FPMission.parkSafetyFooter(venue)
          : "");
      if (safetyText) {
        if (!safety) {
          safety = document.createElement("p");
          safety.className = "ms-safety-footer";
          const foot = sheetEl.querySelector(".ms-footer");
          if (foot) sheetEl.insertBefore(safety, foot);
          else sheetEl.appendChild(safety);
        }
        safety.hidden = false;
        safety.textContent = safetyText;
      } else if (safety) {
        safety.hidden = true;
        safety.textContent = "";
      }
    }

    renderMapHint(/* forPrint */ false);
  }

  /** Prefer local print-safe map under /field-pack/media/maps/. */
  function mapImageSrc() {
    if (!venue) return "";
    const id = venue.slug || "";
    const maps = window.FP_PRINT_MAPS || {};
    if (id && maps[id]) return maps[id];
    const m = venue.media || {};
    const u = m.print_map || m.visitor_map_url || "";
    if (u && String(u).startsWith("/field-pack/media/maps/") && !String(u).includes("..")) return u;
    if (/^https?:\/\//i.test(u)) return u;
    return "";
  }

  function renderMapHint(forPrint) {
    const mapHint = $("#mission-map-hint");
    if (!mapHint) return;
    if (!venue || !venue.media) {
      mapHint.className = "ms-map-hint";
      mapHint.textContent = "";
      return;
    }
    const page = venue.media.visitor_map_page || venue.media.visitor_map_url || "";
    const img = mapImageSrc();
    const attr = venue.media.map_attribution || "Official map";
    if (forPrint && img) {
      // Full-bleed map for one-page print — no hover chrome / link card copy
      mapHint.className = "ms-map-hint ms-map-print-fill";
      mapHint.innerHTML = `
        <div class="ms-map-print-block">
          <p class="ms-map-print-label">Park map — mark start → favorites → end</p>
          <div class="ms-map-print-frame">
            <img class="ms-map-print-img" src="${esc(img)}" alt="Official visitor map" />
          </div>
        </div>`;
      return;
    }
    if (img) {
      const refpol = img.startsWith("/") ? "" : ' referrerpolicy="no-referrer"';
      const ext = page || img;
      const extIsPdf = /\.pdf(\?|#|$)/i.test(String(ext));
      const extLabel = extIsPdf ? "Open full map PDF ↗" : "Official site ↗";
      mapHint.className = "ms-map-hint ms-map-has-preview";
      mapHint.innerHTML = `
          <div class="ms-map-card" data-map-preview>
            <button type="button" class="ms-map-enlarge-hit seo-map-enlarge-hit" aria-expanded="false" aria-label="Enlarge park map">
              <span class="ms-map-thumb-wrap">
                <img class="ms-map-thumb" src="${esc(img)}" alt="Park map preview" loading="lazy" decoding="async"${refpol} />
                <span class="ms-map-hover-hint" aria-hidden="true">Click to pin</span>
              </span>
            </button>
            <span class="ms-map-card-text">
              <strong>Park map</strong>
              <small>${esc(attr)} · click to enlarge</small>
              <a class="seo-map-ext-link" href="${esc(ext)}" target="_blank" rel="noopener noreferrer">${extLabel}</a>
            </span>
            <div class="ms-map-preview seo-map-preview" role="dialog" aria-label="Enlarged park map" hidden>
              <button type="button" class="seo-map-preview-close" aria-label="Close enlarged map">×</button>
              <img src="${esc(img)}" alt="Enlarged park map" loading="lazy" decoding="async"${refpol} />
              <span class="seo-map-preview-cap">
                <a class="seo-map-preview-ext" href="${esc(ext)}" target="_blank" rel="noopener noreferrer">${extLabel}</a>
              </span>
            </div>
          </div>`;
      // Wire after inject (boot also wires page-level cards)
      if (window.FPMapPreview && window.FPMapPreview.wire) window.FPMapPreview.wire(mapHint);
    } else if (page) {
      mapHint.className = "ms-map-hint";
      mapHint.innerHTML = `🗺️ Navigate with the <a href="${esc(page)}" target="_blank" rel="noopener noreferrer">official map</a>`;
    } else {
      mapHint.className = "ms-map-hint";
      mapHint.textContent = "";
    }
  }

  function trackVenueViewOnce() {
    try {
      const v = window.__FP_MISSION_VENUE || venue;
      if (!v) return;
      const slug = v.slug || v.id || "";
      const rawType = v.type || "";
      if (typeof window.FPTrackVenuePageView === "function") {
        window.FPTrackVenuePageView({ venue_slug: slug, venue_type: rawType });
      } else {
        track("venue_page_viewed", {
          venue_slug: slug,
          venue_type: venueTypeForAnalytics(v),
        });
      }
    } catch (_) {}
  }

  function printMission(mission) {
    track("mission_printed", {
      venue: mission.slug,
      venue_slug: mission.slug,
      venue_type: venueTypeForAnalytics(mission),
      age_band: mission.age,
      time_length: mission.time,
      time_budget: mission.time,
      style: mission.hunt || "classic",
      hunt_style: mission.hunt || "classic",
      personalized: mission.personalized ? "1" : "0",
    });
    // Swap map to full print layout before browser print
    renderMapHint(true);
    const sheet = $("#mission-sheet");
    if (sheet && mapImageSrc()) sheet.classList.add("ms-sheet-has-map");
    document.body.classList.add("printing-mission");
    document.documentElement.classList.add("printing-mission");
    const done = () => {
      document.body.classList.remove("printing-mission");
      document.documentElement.classList.remove("printing-mission");
      if (sheet) sheet.classList.remove("ms-sheet-has-map");
      renderMapHint(false);
    };
    window.addEventListener("afterprint", done, { once: true });
    // Fallback if afterprint never fires
    setTimeout(() => {
      if (document.body.classList.contains("printing-mission")) done();
    }, 60000);
    const waitImgs =
      window.FPPrint && typeof window.FPPrint.waitForPrintImages === "function"
        ? window.FPPrint.waitForPrintImages(sheet)
        : Promise.resolve();
    Promise.resolve(waitImgs).then(() => {
      setTimeout(() => window.print(), 40);
    });
  }

  /** Name / interest only — age & time live in `state` (set by chip clicks). */
  function readTextControls() {
    const nameEl = $("#mission-name");
    const interestEl = $("#mission-interest");
    state.name = nameEl ? nameEl.value : "";
    state.interest = interestEl ? interestEl.value : "";
    state.age = normalizeAgeKey(state.age);
    state.time = normalizeTimeKey(state.time);
    state.hunt = normalizeHuntKey(state.hunt);
  }

  /** Paint page bar + drawer chips from `state` (single source of truth). */
  function syncChipChrome() {
    state.age = normalizeAgeKey(state.age) || "4-5";
    state.time = normalizeTimeKey(state.time) || "half";
    state.hunt = normalizeHuntKey(state.hunt) || "classic";
    // Exclusive selection by attribute — only nodes that own that data-* participate
    setGroupChip("#mission-who-seg, .seo-chrome-row:not(.seo-chrome-row-hunt) .seo-chip-row", "data-age", state.age);
    setGroupChip("#mission-time-seg, .seo-chrome-row:not(.seo-chrome-row-hunt) .seo-chip-row", "data-time", state.time);
    setGroupChip("#mission-hunt-seg, .seo-chip-row-hunt", "data-hunt", state.hunt);
    setSegActive(".seo-age-chip[data-age], #mission-who-seg [data-age]", "data-age", state.age);
    setSegActive(".seo-time-chip[data-time], #mission-time-seg [data-time]", "data-time", state.time);
    setSegActive(".seo-hunt-chip[data-hunt], #mission-hunt-seg [data-hunt]", "data-hunt", state.hunt);
    document.body.classList.toggle("mission-hunt-bonus", state.hunt === "bonus");
    document.body.classList.toggle("mission-hunt-alpha", state.hunt === "alpha");
    document.querySelectorAll(".mission-hunt-hint, .seo-bonus-hint").forEach((el) => {
      if (el.classList.contains("seo-bonus-hint")) {
        el.textContent =
          state.hunt === "alpha"
            ? "Alpha = extra-hard cool finds."
            : state.hunt === "bonus"
              ? "Bonus = trickier second-visit finds."
              : "Classic · Bonus · Alpha styles.";
      } else {
        el.textContent =
          state.hunt === "alpha"
            ? "Alpha = extra-hard cool finds + easter egg"
            : state.hunt === "bonus"
              ? "Bonus = second visit · trickier finds + easter egg"
              : "Classic = first visit · Bonus = trickier · Alpha = extra-hard";
      }
    });
  }

  function recompute(fromShuffle) {
    if (!venue || !challenges || !window.FPMission) return;
    readTextControls();
    syncChipChrome();
    lastMission = window.FPMission.selectMission(
      venue,
      challenges,
      state,
      wonders,
      bonusHunts || (typeof window !== "undefined" ? window.FP_BONUS_HUNTS : null)
    );
    renderSheet(lastMission);
    if (genTimer) clearTimeout(genTimer);
    genTimer = setTimeout(() => {
      track("mission_generated", {
        venue_type: venueTypeForAnalytics({ type: (venue && venue.type) || "", slug: venue && venue.slug }),
        venue_slug: venue && venue.slug,
        venue: venue.slug,
        age_band: state.age,
        time_budget: state.time,
        hunt_style: state.hunt || "classic",
        interest: state.interest || "any",
        personalized: state.name.trim() ? "1" : "0",
        shuffle: fromShuffle ? "1" : "0",
      });
    }, 500);
  }

  function isOpen() {
    const ov = $("#mission-overlay");
    return ov && !ov.hasAttribute("hidden");
  }

  function openDrawer() {
    const ov = $("#mission-overlay");
    const drawer = $("#mission-drawer");
    if (!ov || !drawer) return;
    lastFocus = document.activeElement;
    ov.hidden = false;
    document.body.classList.add("mission-drawer-open");
    recompute(false);
    track("mission_drawer_open", { venue: venue && venue.slug });
    const nameEl = $("#mission-name");
    setTimeout(() => {
      (nameEl || drawer).focus();
    }, 30);
  }

  function closeDrawer() {
    const ov = $("#mission-overlay");
    if (!ov) return;
    ov.hidden = true;
    document.body.classList.remove("mission-drawer-open");
    if (lastFocus && typeof lastFocus.focus === "function") {
      try {
        lastFocus.focus();
      } catch (_) {
        /* ignore */
      }
    }
  }

  function wireControls() {
    if (drawerReady) return;
    drawerReady = true;
    ["mission-name", "mission-interest"].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("input", () => recompute(false));
      el.addEventListener("change", () => recompute(false));
    });
    // Shared chip pattern: page bar + drawer segments.
    // Set state first, then recompute — never re-read stale .is-active from the other row.
    // Use [data-*] so we never bind age handlers onto hunt buttons (or vice versa).
    document.querySelectorAll(".seo-time-chip[data-time], #mission-time-seg [data-time]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        state.time = normalizeTimeKey(btn.getAttribute("data-time") || "half");
        syncChipChrome();
        recompute(false);
      });
    });
    document.querySelectorAll(".seo-age-chip[data-age], #mission-who-seg [data-age]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        state.age = normalizeAgeKey(btn.getAttribute("data-age") || "4-5");
        syncChipChrome();
        recompute(false);
      });
    });
    document.querySelectorAll(".seo-hunt-chip[data-hunt], #mission-hunt-seg [data-hunt]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        state.hunt = normalizeHuntKey(btn.getAttribute("data-hunt") || "classic");
        syncChipChrome();
        recompute(false);
      });
    });
    $("#mission-print-btn")?.addEventListener("click", () => {
      if (lastMission) printMission(lastMission);
      else window.print();
    });
    $("#mission-shuffle-btn")?.addEventListener("click", () => {
      state.seed = (state.seed || 1) + 1;
      recompute(true);
    });
    $("#mission-close")?.addEventListener("click", closeDrawer);
    $("#mission-overlay")?.addEventListener("click", (e) => {
      if (e.target === $("#mission-overlay")) closeDrawer();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && isOpen()) {
        e.preventDefault();
        closeDrawer();
      }
    });
  }

  function populateInterest() {
    const sel = $("#mission-interest");
    if (!sel || !venue || !window.FPMission) return;
    const opts = window.FPMission.interestOptions(venue);
    if (opts.length < 3) {
      sel.closest(".mission-field")?.setAttribute("hidden", "");
      return;
    }
    opts.forEach((o) => {
      const op = document.createElement("option");
      op.value = o.value;
      op.textContent = o.label.charAt(0).toUpperCase() + o.label.slice(1);
      sel.appendChild(op);
    });
  }

  function boot() {
    const dataEl = document.getElementById("venue-data");
    const chEl = document.getElementById("challenges-data");
    const wEl = document.getElementById("wonders-data");
    const bEl = document.getElementById("bonus-hunts-data");
    if (!dataEl || !window.FPMission) return;
    try {
      venue = JSON.parse(dataEl.textContent);
      challenges = chEl ? JSON.parse(chEl.textContent) : { challenges: [] };
      wonders = wEl ? JSON.parse(wEl.textContent) : null;
      bonusHunts = bEl ? JSON.parse(bEl.textContent) : window.FP_BONUS_HUNTS || null;
      if (bonusHunts) window.FP_BONUS_HUNTS = bonusHunts;
    } catch (e) {
      console.error(e);
      return;
    }
    populateInterest();
    state.age = "4-5";
    state.time = "half";
    state.hunt = "classic";
    wireChangePlace();
    wireControls();
    // Precompute default sheet (in drawer DOM) for print/SEO consistency
    recompute(false);

    const openBtn = $("#mission-open-btn");
    openBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      openDrawer();
    });

    // Any print CTA on the venue page → mission drawer (never static treasure sheet)
    document.querySelectorAll("[data-how], #seo-print-hunt, #seo-open-mission").forEach((el) => {
      el.addEventListener("click", (e) => {
        const how = el.getAttribute("data-how") || "";
        const id = el.id || "";
        if (
          how === "print" ||
          how === "print-hunt" ||
          id === "seo-print-hunt" ||
          id === "seo-open-mission"
        ) {
          e.preventDefault();
          openDrawer();
          return;
        }
        if (how === "play") {
          // Let hash navigation work; ensure smooth scroll to shortlist/wonder
          const target =
            document.getElementById("seo-play-target") ||
            document.getElementById("shortlist-heading") ||
            document.getElementById("wonder-heading");
          if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
            try {
              target.focus({ preventScroll: true });
            } catch (_) {
              /* ignore */
            }
          }
        }
        // talk → default link to app kid list / Q&A
      });
    });

    // Deep link: #mission / #print / #mission-drawer open the hunt drawer.
    // Venue pages use <base href="/field-pack/">. If #mission has no element,
    // some browsers resolve the fragment to /field-pack/#mission (landing)
    // before this script runs — print never opens. Keep the ids as aliases
    // in the page HTML; treat all three hashes here.
    const maybeOpenFromHash = () => {
      const h = location.hash;
      if (h === "#mission" || h === "#print" || h === "#mission-drawer") openDrawer();
    };
    maybeOpenFromHash();
    window.addEventListener("hashchange", maybeOpenFromHash);

    window.FPMissionUI = {
      open: openDrawer,
      close: closeDrawer,
      isOpen,
      getVenue: () => venue,
    };

    MapPreview.wire(document);
  }

  function wireChangePlace() {
    const kicker = $(".mission-drawer-kicker");
    if (!kicker || kicker.querySelector(".mission-change-place")) return;
    let name = "";
    try {
      const raw = document.getElementById("venue-data");
      if (raw && raw.textContent) name = JSON.parse(raw.textContent).name || "";
    } catch (_) {
      name = "";
    }
    if (!name) {
      const h1 = document.querySelector("h1");
      name = (h1 && h1.textContent) || "";
      name = name.replace(/\s+scavenger hunt.*$/i, "").trim();
    }
    if (!name) name = "This place";
    const home = document.createElement("a");
    home.className = "mission-home";
    home.href = "/field-pack/";
    home.textContent = "Field Trip Kit";
    const now = document.createElement("span");
    now.className = "mission-place-now";
    now.textContent = name;
    const a = document.createElement("a");
    a.className = "mission-change-place";
    a.href = "/field-pack/?find=1";
    a.textContent = "Different place?";
    kicker.replaceChildren(home, document.createTextNode(" · "), now, document.createTextNode(" · "), a);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    trackVenueViewOnce();
  boot();
  }
})();
