(() => {
  const places = window.FP_PLACES || [];
  const grid = document.getElementById("ready-grid");
  const chips = document.getElementById("city-chips");
  const continueChip = document.getElementById("continue-chip");
  const citySelect = document.getElementById("city-select");

  const FEATURED_READY_IDS = [
    "dallas-zoo",
    "childrens-aquarium-dallas",
    "childrens-museum-perot",
  ];
  const READY = FEATURED_READY_IDS.map((id) => places.find((p) => p.id === id)).filter(Boolean);

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // Smooth scroll primary CTA → map
  document.querySelectorAll('a.pitch-cta[href="#us-map"], a.story-jump[href="#us-map"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const map = document.getElementById("us-map");
      if (!map) return;
      e.preventDefault();
      map.scrollIntoView({ behavior: "smooth", block: "start" });
      history.replaceState(null, "", "#us-map");
    });
  });

  /**
   * Sample pops (Print hunt / Play lion):
   * Desktop — CSS hover. Touch — first tap opens pop; second tap (or tap pop) navigates.
   */
  (function wireSamplePops() {
    const steps = Array.from(document.querySelectorAll(".story-step-has-pop"));
    if (!steps.length) return;

    function isCoarse() {
      try {
        return window.matchMedia("(hover: none), (pointer: coarse)").matches;
      } catch (_) {
        return "ontouchstart" in window;
      }
    }

    function closeAll(except) {
      steps.forEach((s) => {
        if (s !== except) s.classList.remove("is-pop-open");
      });
    }

    steps.forEach((step) => {
      const link = step.querySelector("a.story-sample-link[data-sample-pop]");
      if (!link) return;

      link.addEventListener("click", (e) => {
        if (!isCoarse()) return; // desktop: normal navigate (hover already showed pop)
        if (!step.classList.contains("is-pop-open")) {
          e.preventDefault();
          e.stopPropagation();
          closeAll(step);
          step.classList.add("is-pop-open");
          return;
        }
        // already open → allow navigation (default)
      });
    });

    document.addEventListener(
      "click",
      (e) => {
        if (!isCoarse()) return;
        if (e.target.closest && e.target.closest(".story-step-has-pop.is-pop-open")) return;
        closeAll();
      },
      true
    );

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") closeAll();
    });
  })();

  // Ready cards (if present) open the map mini-panel for that venue
  if (grid && READY.length) {
    grid.innerHTML = READY.map((p) => {
      const href = `/field-pack/#/venue/${encodeURIComponent(p.id)}`;
      const short =
        p.id === "childrens-aquarium-dallas"
          ? "Children’s Aquarium"
          : p.id === "childrens-museum-perot"
            ? "Children’s Museum"
            : p.name;
      return `<a class="ready-card" href="${escapeHtml(href)}" data-venue-id="${escapeHtml(p.id)}">
        <span class="rc-emoji" aria-hidden="true">${escapeHtml(p.emoji || "")}</span>
        <h3>${escapeHtml(short)}</h3>
        <span class="rc-cta">Open on map →</span>
      </a>`;
    }).join("");

    grid.addEventListener("click", (e) => {
      const a = e.target.closest("a.ready-card[data-venue-id]");
      if (!a) return;
      const id = a.getAttribute("data-venue-id");
      if (!id) return;
      if (typeof window.fpSelectVenueOnMap === "function") {
        e.preventDefault();
        window.fpSelectVenueOnMap(id);
      }
    });
  }

  /** City chips: hover/focus shows venue links; click jumps the map. */
  const chipDefs = [
    {
      id: "dallas",
      label: "Dallas",
      match: (p) => p.region === "dfw" || ["Dallas", "Fort Worth"].includes(p.city),
    },
    {
      id: "nyc",
      label: "NYC",
      match: (p) => p.region === "nyc" || ["New York", "Bronx"].includes(p.city),
    },
    {
      id: "la",
      label: "LA",
      match: (p) =>
        p.region === "la" || ["Los Angeles", "Long Beach"].includes(p.city),
    },
    {
      id: "san-diego",
      label: "San Diego",
      match: (p) =>
        p.region === "san-diego" || ["San Diego", "Escondido"].includes(p.city),
    },
    {
      id: "london",
      label: "London",
      intl: true,
      match: (p) => p.city === "London",
    },
    {
      id: "paris",
      label: "Paris",
      intl: true,
      match: (p) => p.city === "Paris",
    },
  ];

  function venuesForChip(def) {
    return places.filter((p) => def.match(p)).sort((a, b) => (a.name || "").localeCompare(b.name || ""));
  }

  function shortVenueLabel(p) {
    if (!p) return "";
    if (p.id === "childrens-aquarium-dallas") return "Children’s Aquarium";
    if (p.id === "childrens-museum-perot") return "Children’s Museum";
    if (p.id === "dallas-world-aquarium") return "World Aquarium";
    if (p.id === "dallas-arboretum") return "Arboretum";
    if (p.id === "perot-museum") return "Perot Museum";
    if (p.id === "san-diego-safari-park") return "Safari Park";
    if (p.id === "nhm-london") return "Natural History Museum";
    if (p.id === "paris-zoo") return "Paris Zoo";
    if (p.id === "amnh") return "AMNH";
    if (p.id === "california-science-center") return "California Science Center";
    return p.name || p.id;
  }

  function focusChipWrap(wrap) {
    chips.querySelectorAll(".city-chip-wrap").forEach((w) => {
      w.classList.remove("is-open");
      const b = w.querySelector(".city-chip");
      if (b) {
        b.setAttribute("aria-pressed", "false");
        b.setAttribute("aria-expanded", "false");
      }
    });
    if (!wrap) return;
    wrap.classList.add("is-open");
    const btn = wrap.querySelector(".city-chip");
    if (btn) {
      btn.setAttribute("aria-pressed", "true");
      btn.setAttribute("aria-expanded", "true");
    }
  }

  function jumpMapToChip(def) {
    document.getElementById("map-viewport")?.scrollIntoView({ behavior: "smooth", block: "center" });
    const venues = venuesForChip(def);
    const ids = venues.map((p) => p.id);

    if (def.intl) {
      const intlBtn = document.getElementById("scope-intl");
      if (intlBtn && intlBtn.getAttribute("aria-pressed") !== "true") {
        intlBtn.click();
      }
      // Focus city cluster (or first pin) after basemap swap — same path as US
      setTimeout(() => {
        if (typeof window.fpFocusMapOnPlaces === "function" && ids.length) {
          window.fpFocusMapOnPlaces(ids, { zoom: 2.4 });
        } else if (venues[0] && typeof window.fpSelectVenueOnMap === "function") {
          window.fpSelectVenueOnMap(venues[0].id);
        }
      }, 140);
      return;
    }

    // US metro: US scope + metro filter, then pan to pin cluster
    const moreBtn = document.getElementById("scope-more");
    if (moreBtn && moreBtn.getAttribute("aria-pressed") !== "true") {
      moreBtn.click();
    }
    const runFocus = () => {
      if (citySelect && citySelect.querySelector(`option[value="${def.id}"]`)) {
        citySelect.value = def.id;
        citySelect.dispatchEvent(new Event("change", { bubbles: true }));
      }
      // citySelect change already pans; double-ensure after render if API present
      if (typeof window.fpFocusMapOnPlaces === "function" && ids.length) {
        setTimeout(() => window.fpFocusMapOnPlaces(ids), 80);
      }
    };
    // Allow US basemap restore if we just left International
    setTimeout(runFocus, moreBtn && moreBtn.getAttribute("aria-pressed") === "true" ? 0 : 140);
  }

  if (chips) {
    chips.innerHTML = chipDefs
      .map((c) => {
        const venues = venuesForChip(c);
        const menu =
          venues.length > 0
            ? `<div class="city-chip-menu" role="menu" aria-label="${escapeHtml(c.label)} places">
            ${venues
              .map((p) => {
                const href = p.href || `/field-pack/${encodeURIComponent(p.id)}/`;
                return `<a class="city-chip-menu-item" role="menuitem" href="${escapeHtml(href)}">${escapeHtml(
                  p.emoji || "📍"
                )} ${escapeHtml(shortVenueLabel(p))}</a>`;
              })
              .join("")}
          </div>`
            : "";
        return `<div class="city-chip-wrap">
          <button type="button" class="city-chip" data-city="${escapeHtml(c.id)}" data-intl="${
            c.intl ? "1" : "0"
          }" aria-pressed="false" aria-haspopup="true" aria-expanded="false">${escapeHtml(c.label)}</button>
          ${menu}
        </div>`;
      })
      .join("");

    chips.addEventListener("click", (e) => {
      // Links in menu navigate normally
      if (e.target.closest("a.city-chip-menu-item")) return;
      const btn = e.target.closest(".city-chip");
      if (!btn) return;
      const wrap = btn.closest(".city-chip-wrap");
      const id = btn.dataset.city;
      const def = chipDefs.find((c) => c.id === id);
      if (!def) return;
      focusChipWrap(wrap);
      jumpMapToChip(def);
    });

    // Keep aria-expanded / open class in sync for keyboard + hover
    chips.querySelectorAll(".city-chip-wrap").forEach((wrap) => {
      const btn = wrap.querySelector(".city-chip");
      if (!btn) return;
      wrap.addEventListener("mouseenter", () => {
        wrap.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
      });
      wrap.addEventListener("mouseleave", () => {
        // Keep open if this chip is the selected city
        if (btn.getAttribute("aria-pressed") === "true") return;
        wrap.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
      });
      wrap.addEventListener("focusin", () => {
        wrap.classList.add("is-open");
        btn.setAttribute("aria-expanded", "true");
      });
      wrap.addEventListener("focusout", (ev) => {
        if (wrap.contains(ev.relatedTarget)) return;
        if (btn.getAttribute("aria-pressed") === "true") return;
        wrap.classList.remove("is-open");
        btn.setAttribute("aria-expanded", "false");
      });
    });
  }

  try {
    const raw =
      localStorage.getItem("1less-babys-day-out-trips-v1") ||
      localStorage.getItem("arya-field-pack-trips-v2");
    if (raw && continueChip) {
      const store = JSON.parse(raw);
      const trips = store.trips || [];
      if (trips.length) {
        const last = trips[trips.length - 1];
        const venueId = last.venueId || store.selectedVenueId || "dallas-zoo";
        const href = last.id
          ? `/field-pack/app.html#/trip/${encodeURIComponent(last.id)}`
          : `/field-pack/app.html#/venue/${encodeURIComponent(venueId)}`;
        // Prefer full place name — trip titles are often short codes (e.g. AMNH)
        const fromCatalog = places.find((p) => p.id === venueId);
        const rawTitle = (last.title || "").trim();
        const looksLikeCode = !rawTitle || rawTitle.length <= 6 || /^[A-Z0-9][A-Z0-9.&'-]{1,10}$/.test(rawTitle);
        const label =
          fromCatalog?.name ||
          (!looksLikeCode ? rawTitle : null) ||
          "your last place";
        continueChip.hidden = false;
        continueChip.removeAttribute("hidden");
        continueChip.style.display = "block";
        continueChip.innerHTML = `Pick up where you left off at <strong>${escapeHtml(
          label
        )}</strong>. <a href="${href}">Continue →</a>`;
      }
    }
  } catch {
    /* ignore */
  }

  function renderWaiting() {
    const el = document.getElementById("waiting-cities");
    if (!el) return;
    let ids = [];
    try {
      ids = JSON.parse(localStorage.getItem("1less-saved-cities") || "[]");
    } catch {
      ids = [];
    }
    if (!ids.length) {
      el.hidden = true;
      el.textContent = "";
      return;
    }
    const labels = ids.map((id) => {
      const opt = citySelect?.querySelector(`option[value="${id}"]`);
      return opt ? opt.textContent.replace(/\s*·.*$/, "").trim() : id;
    });
    el.hidden = false;
    el.innerHTML = `Waiting on: <strong>${labels.map(escapeHtml).join(", ")}</strong>`;
  }
  renderWaiting();
  window.addEventListener("1less-cities-saved", renderWaiting);
})();
