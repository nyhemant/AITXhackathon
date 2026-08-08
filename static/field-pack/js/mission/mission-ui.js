/**
 * Mission print drawer for pilot venue pages.
 * Page stays clean; #mission-open-btn opens filters + live sheet.
 */
(function () {
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

  function track(event, params) {
    try {
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
  let state = { age: "4-5", time: "half", interest: "", name: "", seed: 1 };
  let lastMission = null;
  let genTimer = null;
  let lastFocus = null;
  let drawerReady = false;

  function AGE_FROM_SLIDER(v) {
    const n = parseInt(v, 10) || 1;
    return ["2-3", "4-5", "6-8", "9+"][Math.max(0, Math.min(3, n))] || "4-5";
  }

  function renderSheet(mission) {
    const title = $("#mission-title");
    const meta = $("#mission-meta");
    const findsEl = $("#mission-finds");
    const chEl = $("#mission-challenges");
    if (title) title.textContent = mission.title;
    if (meta) {
      const mode = mission.contentMode === "wonder" ? " · Wonder sheet" : "";
      meta.textContent = `${mission.ageLabel} · ${mission.timeLabel}${mode}`;
    }
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
              <a class="seo-map-ext-link" href="${esc(ext)}" target="_blank" rel="noopener noreferrer">Official site ↗</a>
            </span>
            <div class="ms-map-preview seo-map-preview" role="dialog" aria-label="Enlarged park map" hidden>
              <button type="button" class="seo-map-preview-close" aria-label="Close enlarged map">×</button>
              <img src="${esc(img)}" alt="Enlarged park map" loading="lazy" decoding="async"${refpol} />
              <span class="seo-map-preview-cap">
                <a class="seo-map-preview-ext" href="${esc(ext)}" target="_blank" rel="noopener noreferrer">Open on official site ↗</a>
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

  function printMission(mission) {
    track("mission_printed", {
      venue: mission.slug,
      age_band: mission.age,
      time_budget: mission.time,
      personalized: mission.personalized ? "1" : "0",
    });
    // Swap map to full print layout before browser print
    renderMapHint(true);
    const sheet = $("#mission-sheet");
    if (sheet && mapImageSrc()) sheet.classList.add("ms-sheet-has-map");
    document.body.classList.add("printing-mission");
    const done = () => {
      document.body.classList.remove("printing-mission");
      if (sheet) sheet.classList.remove("ms-sheet-has-map");
      renderMapHint(false);
    };
    window.addEventListener("afterprint", done, { once: true });
    // Fallback if afterprint never fires
    setTimeout(() => {
      if (document.body.classList.contains("printing-mission")) done();
    }, 60000);
    setTimeout(() => window.print(), 80);
  }

  function readControls() {
    const nameEl = $("#mission-name");
    const ageEl = $("#mission-age");
    const timeEl = document.querySelector('input[name="mission-time"]:checked');
    const interestEl = $("#mission-interest");
    state.name = nameEl ? nameEl.value : "";
    state.age = ageEl ? AGE_FROM_SLIDER(ageEl.value) : "4-5";
    state.time = timeEl ? timeEl.value : "half";
    state.interest = interestEl ? interestEl.value : "";
    const ageLabel = $("#mission-age-label");
    if (ageLabel && window.FPMission) {
      ageLabel.textContent = window.FPMission.AGE_LABELS[state.age] || state.age;
    }
  }

  function syncPageChrome() {
    document.querySelectorAll(".seo-time-chip").forEach((btn) => {
      const on = btn.getAttribute("data-time") === state.time;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    const ageIdx = (window.FPMission.AGE_ORDER || []).indexOf(state.age);
    document.querySelectorAll(".seo-age-chip").forEach((btn) => {
      const idx = parseInt(btn.getAttribute("data-age-idx") || "1", 10);
      const on = idx === ageIdx;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    // Keep drawer controls in sync
    const ageEl = $("#mission-age");
    if (ageEl && ageIdx >= 0) ageEl.value = String(ageIdx);
    document.querySelectorAll('input[name="mission-time"]').forEach((el) => {
      el.checked = el.value === state.time || (state.time === "1hr" && el.value === "90m");
    });
  }

  function recompute(fromShuffle) {
    if (!venue || !challenges || !window.FPMission) return;
    readControls();
    syncPageChrome();
    lastMission = window.FPMission.selectMission(venue, challenges, state, wonders);
    renderSheet(lastMission);
    if (genTimer) clearTimeout(genTimer);
    genTimer = setTimeout(() => {
      track("mission_generated", {
        venue: venue.slug,
        age_band: state.age,
        time_budget: state.time,
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
    ["mission-name", "mission-age", "mission-interest"].forEach((id) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("input", () => recompute(false));
      el.addEventListener("change", () => recompute(false));
    });
    document.querySelectorAll('input[name="mission-time"]').forEach((el) => {
      el.addEventListener("change", () => recompute(false));
    });
    document.querySelectorAll(".seo-time-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.time = btn.getAttribute("data-time") || "half";
        const radio = document.querySelector(`input[name="mission-time"][value="${state.time}"]`);
        if (radio) radio.checked = true;
        recompute(false);
      });
    });
    document.querySelectorAll(".seo-age-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        const idx = parseInt(btn.getAttribute("data-age-idx") || "1", 10);
        state.age = AGE_FROM_SLIDER(idx);
        const ageEl = $("#mission-age");
        if (ageEl) ageEl.value = String(idx);
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
    if (!dataEl || !window.FPMission) return;
    try {
      venue = JSON.parse(dataEl.textContent);
      challenges = chEl ? JSON.parse(chEl.textContent) : { challenges: [] };
      wonders = wEl ? JSON.parse(wEl.textContent) : null;
    } catch (e) {
      console.error(e);
      return;
    }
    populateInterest();
    const age = $("#mission-age");
    if (age) age.value = "1";
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

    // Deep link: #mission opens drawer (landing pin CTA, shared links)
    const maybeOpenFromHash = () => {
      if (location.hash === "#mission" || location.hash === "#print") openDrawer();
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

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
