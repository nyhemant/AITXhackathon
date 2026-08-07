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

  // Personalized mission featured strip (full pilot set lives on every SEO venue page)
  const pilotLinks = document.getElementById("pilot-mission-links");
  const pilotMore = document.getElementById("pilot-mission-more");
  const pilotLead = document.getElementById("pilot-mission-lead");
  const featuredIds = window.FP_MISSION_PILOTS_FEATURED || [];
  const allPilotIds = window.FP_MISSION_PILOTS || [];
  if (pilotLinks && featuredIds.length) {
    const shortName = (p) => {
      if (!p) return "";
      if (p.id === "childrens-aquarium-dallas") return "Children’s Aquarium";
      if (p.id === "childrens-museum-perot") return "Perot Museum";
      if (p.id === "monterey-bay-aquarium") return "Monterey Bay";
      if (p.id === "san-diego-safari-park") return "Safari Park";
      if (p.id === "kennedy-space-center") return "Kennedy Space";
      if (p.id === "amnh") return "AMNH";
      return p.name || p.id;
    };
    pilotLinks.innerHTML = featuredIds
      .map((id) => {
        const p = places.find((x) => x.id === id);
        const label = shortName(p) || id;
        return `<a class="pilot-mission-link" href="/field-pack/${encodeURIComponent(id)}/">${escapeHtml(
          label
        )}</a>`;
      })
      .join("");
    if (pilotLead) {
      pilotLead.innerHTML = `Age slider, time segments, optional name — live preview, one-page print.
        <strong>${allPilotIds.length} places</strong> have personalized missions. Popular starters:`;
    }
    if (pilotMore && allPilotIds.length > featuredIds.length) {
      pilotMore.hidden = false;
      pilotMore.innerHTML = `Or pick any pin on the map → <strong>Build personalized mission</strong>. ${
        allPilotIds.length - featuredIds.length
      } more places ready.`;
    }
  }

  // Ready cards open the map mini-panel for that venue (not the SEO static page)
  if (grid) {
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
      // Prefer in-page map panel (no full reload) when already on the landing map
      if (typeof window.fpSelectVenueOnMap === "function") {
        e.preventDefault();
        window.fpSelectVenueOnMap(id);
      }
    });
  }

  const chipDefs = [
    { id: "dallas", label: "Dallas" },
    { id: "nyc", label: "NYC" },
    { id: "chicago", label: "Chicago" },
    { id: "la", label: "LA" },
    { id: "san-diego", label: "San Diego" },
    { id: "austin", label: "Austin" },
  ];

  if (chips) {
    chips.innerHTML = chipDefs
      .map(
        (c) =>
          `<button type="button" class="city-chip" data-city="${c.id}" aria-pressed="false">${escapeHtml(
            c.label
          )}</button>`
      )
      .join("");

    chips.addEventListener("click", (e) => {
      const btn = e.target.closest(".city-chip");
      if (!btn) return;
      const id = btn.dataset.city;
      chips.querySelectorAll(".city-chip").forEach((b) => b.setAttribute("aria-pressed", "false"));
      btn.setAttribute("aria-pressed", "true");
      if (citySelect && citySelect.querySelector(`option[value="${id}"]`)) {
        citySelect.value = id;
        citySelect.dispatchEvent(new Event("change", { bubbles: true }));
      }
      document.getElementById("map-viewport")?.scrollIntoView({ behavior: "smooth", block: "center" });
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
