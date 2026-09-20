(() => {
  const places = window.FP_PLACES || [];
  const chips = document.getElementById("city-chips");
  const citySelect = document.getElementById("city-select");

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function trackHero(name, params) {
    if (typeof window.FPTrack === "function") {
      window.FPTrack(name, params || {});
      return;
    }
    const fn =
      (window.OneLessAnalytics && window.OneLessAnalytics.track) || window.trackEvent;
    if (typeof fn === "function") fn(name, params || {});
  }

  /**
   * Places hub search — type a zoo / museum / park / city, pick a result.
   * Empty submit scrolls to the map.
   */
  function wireHeroSearch() {
    const form = document.getElementById("hero-search-form");
    const input = document.getElementById("hero-place-search");
    const results = document.getElementById("hero-place-search-results");
    if (!form || !input || !results) return;

    function hide() {
      results.hidden = true;
      results.innerHTML = "";
    }

    function goPlace(id) {
      hide();
      input.value = "";
      trackHero("hero_search_used", { venue_slug: id || "", search_mode: "place", source: "hero" });
      location.href = `/field-pack/${encodeURIComponent(id)}/`;
    }

    function search(q) {
      const needle = (q || "").trim().toLowerCase();
      if (needle.length < 2) {
        hide();
        return;
      }
      const hits = places
        .filter((p) => {
          const blob = [p.name, p.city, p.state, p.country, p.id, p.type]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();
          return blob.includes(needle);
        })
        .slice(0, 8);
      if (!hits.length) {
        results.innerHTML = `<li class="place-search-empty">No places match</li>`;
        results.hidden = false;
        return;
      }
      results.innerHTML = hits
        .map((p) => {
          const where = [p.city, p.state || p.country].filter(Boolean).join(", ");
          return `<li role="option">
            <button type="button" class="place-search-hit" data-kind="place" data-id="${escapeHtml(p.id)}">
              <strong>${escapeHtml(p.emoji || "📍")} ${escapeHtml(p.name)}</strong>
              <small>${escapeHtml(where)}</small>
            </button>
          </li>`;
        })
        .join("");
      results.hidden = false;
    }

    let t = null;
    input.addEventListener("input", () => {
      clearTimeout(t);
      t = setTimeout(() => search(input.value), 120);
    });
    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        hide();
        input.blur();
      }
      if (e.key === "Enter") {
        const first = results.querySelector(".place-search-hit");
        if (first && !results.hidden) {
          e.preventDefault();
          first.click();
        }
      }
    });
    results.addEventListener("click", (e) => {
      const btn = e.target.closest(".place-search-hit");
      if (!btn) return;
      goPlace(btn.getAttribute("data-id"));
    });
    document.addEventListener("click", (e) => {
      if (e.target.closest && e.target.closest(".place-search-wrap")) return;
      hide();
    });

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const first = results.querySelector(".place-search-hit");
      if (first && !results.hidden) {
        first.click();
        return;
      }
      const q = (input.value || "").trim();
      if (q.length >= 2) {
        input.dispatchEvent(new Event("input", { bubbles: true }));
        return;
      }
      trackHero("hero_cta_clicked", { source: "hero_empty_submit", search_mode: "place" });
      const map = document.getElementById("during") || document.getElementById("us-map");
      if (map) {
        map.scrollIntoView({ behavior: "smooth", block: "start" });
        history.replaceState(null, "", "#during");
      }
    });
  }

  wireHeroSearch();

  // T5 catalog: card pill filter + click events
  // Mobile: 6 tiles (3 rows × 2). Desktop: 12. All uses data-featured-all only.
  const cardGrid = document.getElementById("cat-card-grid");
  const pills = document.querySelectorAll("#cat-cards-showcase [data-card-filter]");
  if (pills.length && cardGrid) {
    const cardMq = window.matchMedia("(max-width: 719px)");
    let landingCardFilter = "all";
    function cardLimit() {
      return cardMq.matches ? 6 : 12;
    }
    function applyLandingCardFilter(f) {
      landingCardFilter = f;
      const limit = cardLimit();
      let n = 0;
      cardGrid.querySelectorAll(".cat-card-tile").forEach((tile) => {
        const g = tile.getAttribute("data-card-group") || "";
        const inAll = tile.hasAttribute("data-featured-all");
        const match = f === "all" ? inAll : g === f;
        if (match && n < limit) {
          tile.hidden = false;
          n += 1;
        } else {
          tile.hidden = true;
        }
      });
    }
    function ensureCardGridInView() {
      const wrap = document.getElementById("cat-cards-showcase");
      if (!wrap) return;
      const header = document.querySelector(".oneless-shell");
      const headerBottom = header ? header.getBoundingClientRect().bottom : 0;
      const first = cardGrid.querySelector(".cat-card-tile:not([hidden])");
      if (!first) return;
      const firstBottom = first.getBoundingClientRect().bottom;
      const tabs = wrap.querySelector(".place-type-tabs-cards");
      const tabsTop = tabs ? tabs.getBoundingClientRect().top : first.getBoundingClientRect().top;
      if (firstBottom < headerBottom + 24 || tabsTop < headerBottom - 8) {
        wrap.scrollIntoView({ block: "start", behavior: "smooth" });
      }
    }
    applyLandingCardFilter("all");
    const onCardMq = () => applyLandingCardFilter(landingCardFilter);
    if (cardMq.addEventListener) cardMq.addEventListener("change", onCardMq);
    else if (cardMq.addListener) cardMq.addListener(onCardMq);
    pills.forEach((btn) => {
      btn.addEventListener("click", () => {
        const f = btn.getAttribute("data-card-filter") || "all";
        pills.forEach((b) => {
          const on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
          b.setAttribute("aria-selected", on ? "true" : "false");
        });
        applyLandingCardFilter(f);
        ensureCardGridInView();
      });
    });
  }
  document.querySelectorAll(".cat-card-tile-link[data-card-id]").forEach((a) => {
    a.addEventListener("click", () => {
      trackHero("card_opened", { card_id: a.getAttribute("data-card-id") || "", source: "catalog_teaser" });
    });
  });
  document.querySelectorAll(".cat-place-hub[data-place-kind]").forEach((a) => {
    a.addEventListener("click", () => {
      trackHero("catalog_place_clicked", { place_kind: a.getAttribute("data-place-kind") || "", source: "catalog" });
    });
  });
  document.querySelectorAll(".cat-popular-chip[data-venue-slug]").forEach((a) => {
    a.addEventListener("click", () => {
      trackHero("catalog_popular_clicked", { venue_slug: a.getAttribute("data-venue-slug") || "", source: "catalog" });
    });
  });

  // Trust strip count from live places data when present
  const countEl = document.querySelector("[data-place-count]");
  if (countEl && places.length) countEl.textContent = String(places.length);

  // Smooth scroll legacy CTAs → map
  document.querySelectorAll('a.pitch-cta[href="#us-map"], a.story-jump[href="#us-map"], a[href="#during"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const map = document.getElementById("during") || document.getElementById("us-map");
      if (!map) return;
      // let native hash work for plain anchors; enhance smooth scroll
      if (a.getAttribute("href") === "#us-map" || a.classList.contains("pitch-cta")) {
        e.preventDefault();
        map.scrollIntoView({ behavior: "smooth", block: "start" });
        history.replaceState(null, "", a.getAttribute("href") || "#during");
      }
    });
  });

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
    let needBasemapWait = false;
    if (moreBtn && moreBtn.getAttribute("aria-pressed") !== "true") {
      moreBtn.click();
      needBasemapWait = true;
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
    setTimeout(runFocus, needBasemapWait ? 140 : 0);
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

  // Mission drawer “Different place?” → land on search, not another demo zoo
  try {
    if (new URLSearchParams(location.search).get("find") === "1") {
      const input = document.getElementById("hero-place-search");
      const block = document.getElementById("hero-search-block") || input;
      if (block && block.scrollIntoView) block.scrollIntoView({ block: "center" });
      if (input) {
        input.focus();
        input.setAttribute("placeholder", "Your zoo, aquarium, museum, or park…");
      }
    }
  } catch (_) {
    /* ignore */
  }
})();
