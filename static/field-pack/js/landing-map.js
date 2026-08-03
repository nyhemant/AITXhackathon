(() => {
  const allPlaces = window.FP_PLACES || [];
  const TOP_IDS = new Set(window.FP_TOP_PLACE_IDS || []);
  const detail = document.getElementById("pin-detail");
  const mapHost = document.getElementById("map-host");
  const citySelect = document.getElementById("city-select");
  const venueSelect = document.getElementById("venue-select-landing");
  const scopeTop = document.getElementById("scope-top");
  const scopeMore = document.getElementById("scope-more");
  const stateSelect = document.getElementById("state-select");
  const stateField = document.getElementById("state-field");
  const mapCount = document.getElementById("map-count");
  const btnZoomIn = document.getElementById("map-zoom-in");
  const btnZoomOut = document.getElementById("map-zoom-out");
  const btnZoomReset = document.getElementById("map-zoom-reset");
  const mapViewport = document.getElementById("map-viewport");

  /** Metro groups for Top mode dropdown (not every pin). */
  const METRO_DEFS = [
    { id: "all", label: "All (Top list)", symbols: "🇺🇸", states: null },
    { id: "dallas", label: "Dallas area", symbols: "🦁", states: ["TX"], regions: ["dfw"] },
    { id: "houston", label: "Houston", symbols: "🐘", states: ["TX"], cities: ["Houston"] },
    { id: "austin", label: "Austin", symbols: "🔬", states: ["TX"], cities: ["Austin"] },
    { id: "san-diego", label: "San Diego", symbols: "🐼", states: ["CA"], cities: ["San Diego", "Escondido"] },
    { id: "la", label: "Los Angeles", symbols: "🦅", states: ["CA"], cities: ["Los Angeles", "Long Beach"] },
    { id: "monterey", label: "Monterey", symbols: "🌊", states: ["CA"], cities: ["Monterey"] },
    { id: "sf", label: "San Francisco", symbols: "🌿", states: ["CA"], cities: ["San Francisco"] },
    { id: "chicago", label: "Chicago", symbols: "🐠", states: ["IL"], cities: ["Chicago"] },
    { id: "atlanta", label: "Atlanta", symbols: "🐋", states: ["GA"], cities: ["Atlanta"] },
    { id: "dc", label: "Washington, DC", symbols: "🦥", states: ["DC"], cities: ["Washington"] },
    { id: "nyc", label: "New York", symbols: "🦴", states: ["NY"], cities: ["New York", "Bronx"] },
    { id: "boston", label: "Boston", symbols: "🦞", states: ["MA"], cities: ["Boston"] },
    { id: "florida", label: "Florida Space", symbols: "🚀", states: ["FL"], cities: ["Merritt Island"] },
  ];

  let mapScope = "top"; // top | more
  let selectedMetroId = "all";
  let selectedState = "";
  let selectedVenueId = "";
  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let svgEl = null;
  let pinsLayer = null;

  function placeById(id) {
    return allPlaces.find((p) => p.id === id);
  }

  function placesInScope() {
    if (mapScope === "top") {
      return allPlaces.filter((p) => TOP_IDS.has(p.id) || p.tier === "top");
    }
    return [...allPlaces];
  }

  function filteredPlaces() {
    let list = placesInScope();
    if (mapScope === "top") {
      if (selectedMetroId !== "all") {
        const m = METRO_DEFS.find((x) => x.id === selectedMetroId);
        if (m) {
          list = list.filter((p) => {
            if (m.regions && m.regions.includes(p.region)) return true;
            if (m.cities && m.cities.includes(p.city)) return true;
            if (m.states && m.states.includes(p.state) && !m.cities && !m.regions) return true;
            // TX special: dallas metro only TX cities in metro
            if (m.id === "dallas") return p.region === "dfw" || ["Dallas", "Fort Worth"].includes(p.city);
            if (m.id === "houston") return p.city === "Houston";
            if (m.id === "austin") return p.city === "Austin";
            return m.states && m.states.includes(p.state) && (!m.cities || m.cities.includes(p.city));
          });
        }
      }
    } else {
      // More: filter by state
      if (selectedState) {
        list = list.filter((p) => p.state === selectedState);
      }
    }
    return list.sort((a, b) => a.name.localeCompare(b.name));
  }

  function kidTypeLabel(type) {
    const t = (type || "").toLowerCase();
    if (t.includes("safari")) return "Safari zoo";
    if (t.includes("zoo")) return "Zoo";
    if (t.includes("aquarium")) return "Aquarium";
    if (t.includes("children")) return "Kids museum";
    if (t.includes("space") || t.includes("air")) return "Space / air";
    if (t.includes("science")) return "Science";
    if (t.includes("natural") || t.includes("history")) return "Nature museum";
    return type || "Place";
  }

  function venueOptionLabel(p) {
    const kind = kidTypeLabel(p.type);
    const city = p.city === "Escondido" ? "San Diego area" : p.city;
    return `${p.emoji || "📍"} ${p.name} — ${city}, ${p.state}`;
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function statesInMore() {
    const set = new Set(allPlaces.map((p) => p.state).filter(Boolean));
    return [...set].sort();
  }

  function fillLocationSelect() {
    citySelect.innerHTML = "";
    if (mapScope === "top") {
      for (const m of METRO_DEFS) {
        const opt = document.createElement("option");
        opt.value = m.id;
        opt.textContent = m.id === "all" ? m.label : `${m.symbols} ${m.label}`;
        citySelect.appendChild(opt);
      }
      citySelect.value = selectedMetroId;
      if (stateField) stateField.hidden = true;
    } else {
      const optAll = document.createElement("option");
      optAll.value = "all";
      optAll.textContent = "All states (More)";
      citySelect.appendChild(optAll);
      // use state select
      if (stateSelect) {
        stateSelect.innerHTML = "";
        const o0 = document.createElement("option");
        o0.value = "";
        o0.textContent = "All states";
        stateSelect.appendChild(o0);
        for (const st of statesInMore()) {
          const o = document.createElement("option");
          o.value = st;
          o.textContent = st;
          stateSelect.appendChild(o);
        }
        stateSelect.value = selectedState;
      }
      if (stateField) stateField.hidden = false;
      citySelect.innerHTML = "";
      const o = document.createElement("option");
      o.value = "all";
      o.textContent = selectedState ? `State: ${selectedState}` : "Browse by state →";
      citySelect.appendChild(o);
      citySelect.disabled = true;
    }
    if (mapScope === "top") citySelect.disabled = false;
  }

  function fillVenueSelect() {
    const list = filteredPlaces();
    venueSelect.innerHTML = "";
    const ph = document.createElement("option");
    ph.value = "";
    ph.textContent =
      mapScope === "top"
        ? `Venues (${list.length} in Top)…`
        : selectedState
          ? `Venues in ${selectedState} (${list.length})…`
          : `All venues (${list.length})…`;
    venueSelect.appendChild(ph);
    for (const p of list) {
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = venueOptionLabel(p);
      venueSelect.appendChild(opt);
    }
    if (selectedVenueId && list.some((p) => p.id === selectedVenueId)) {
      venueSelect.value = selectedVenueId;
    } else {
      selectedVenueId = "";
      venueSelect.value = "";
    }
    if (mapCount) {
      const topN = allPlaces.filter((p) => TOP_IDS.has(p.id) || p.tier === "top").length;
      mapCount.textContent =
        mapScope === "top"
          ? `Showing Top ${topN} tourist magnets`
          : `Showing all ${allPlaces.length} places` + (selectedState ? ` · ${selectedState}` : "");
    }
  }

  function applyMapTransform() {
    if (!svgEl) return;
    svgEl.style.transformOrigin = "center center";
    svgEl.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
  }

  function setZoom(z) {
    zoom = Math.min(3.5, Math.max(1, z));
    if (zoom === 1) {
      panX = 0;
      panY = 0;
    }
    applyMapTransform();
    renderPins();
  }

  /** Zoom so the viewport point (clientX/Y) becomes the center. */
  function zoomToClientPoint(clientX, clientY, newZoom) {
    if (!mapViewport) {
      setZoom(newZoom);
      return;
    }
    const rect = mapViewport.getBoundingClientRect();
    const ox = clientX - rect.left - rect.width / 2;
    const oy = clientY - rect.top - rect.height / 2;
    const z0 = zoom || 1;
    const z1 = Math.min(3.5, Math.max(1, newZoom));
    const contentX = (ox - panX) / z0;
    const contentY = (oy - panY) / z0;
    zoom = z1;
    if (zoom <= 1) {
      panX = 0;
      panY = 0;
    } else {
      panX = -contentX * zoom;
      panY = -contentY * zoom;
    }
    applyMapTransform();
    renderPins();
  }

  function renderPins() {
    if (!svgEl || !pinsLayer) return;
    while (pinsLayer.firstChild) pinsLayer.removeChild(pinsLayer.firstChild);
    // hide legacy city pins when showing venue layer
    svgEl.querySelectorAll(".city-pin").forEach((el) => {
      el.style.display = "none";
    });

    const vb = svgEl.viewBox.baseVal;
    const w = vb.width || 1000;
    const h = vb.height || 620;
    const list = filteredPlaces();
    const NS = "http://www.w3.org/2000/svg";

    for (const p of list) {
      if (p.lat == null || p.lon == null) continue;
      const { x, y } = window.fpProjectUS(p.lat, p.lon, w, h);
      const selected = p.id === selectedVenueId;
      const g = document.createElementNS(NS, "g");
      g.setAttribute("class", "venue-pin" + (selected ? " selected" : ""));
      g.setAttribute("tabindex", "0");
      g.setAttribute("role", "button");
      g.setAttribute("aria-label", p.name);
      g.dataset.venueId = p.id;
      g.style.cursor = "pointer";

      const halo = document.createElementNS(NS, "circle");
      halo.setAttribute("class", "vpin-halo");
      halo.setAttribute("cx", x);
      halo.setAttribute("cy", y);
      halo.setAttribute("r", mapScope === "more" ? "12" : "16");
      g.appendChild(halo);

      const core = document.createElementNS(NS, "circle");
      core.setAttribute("class", "vpin-core");
      core.setAttribute("cx", x);
      core.setAttribute("cy", y);
      core.setAttribute("r", selected ? "8" : mapScope === "more" ? "5" : "7");
      g.appendChild(core);

      // Name always on selected pin; otherwise when top list / zoomed / state filter
      const showLabel =
        selected || mapScope === "top" || zoom >= 1.4 || Boolean(selectedState);
      if (showLabel) {
        const label = document.createElementNS(NS, "text");
        label.setAttribute("class", "vpin-label" + (selected ? " vpin-label-on" : ""));
        label.setAttribute("x", x + 10);
        label.setAttribute("y", y + 4);
        const text =
          (p.emoji || "•") +
          " " +
          (selected || mapScope === "top"
            ? p.name.length > 26
              ? p.name.slice(0, 24) + "…"
              : p.name
            : p.name.length > 18
              ? p.name.slice(0, 16) + "…"
              : p.name);
        label.textContent = text;
        g.appendChild(label);
      }

      g.addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        // One click: select pin, show name, fill right detail panel
        setVenue(p.id, { fromPin: true });
      });
      g.addEventListener("dblclick", (e) => {
        e.stopPropagation();
        e.preventDefault();
        setVenue(p.id, { fromPin: true });
        zoomToClientPoint(e.clientX, e.clientY, Math.min(3.5, zoom + 0.75));
      });
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          setVenue(p.id, { fromPin: true });
        }
      });
      pinsLayer.appendChild(g);
    }
  }

  function showOverview() {
    const list = filteredPlaces();
    detail.className = "pin-detail";
    detail.innerHTML = `
      <p class="pin-detail-kicker">${mapScope === "top" ? "Top list" : "More places"}</p>
      <h3>🗺️ ${list.length} places</h3>
      <p class="pd-meta">${
        mapScope === "top"
          ? "Tourist magnets covering most US family trips."
          : "Expanded list — filter by state to unclutter."
      }</p>
      <p class="pd-blurb"><strong>Click a pin</strong> to select it (name + details here). <strong>Double-click</strong> to zoom in on that spot.</p>
      <p class="pd-blurb">Or use the venue menu. + / − also zoom.</p>
    `;
  }

  function showVenueDetail(venueId) {
    const p = placeById(venueId);
    if (!p) {
      showOverview();
      return;
    }
    selectedVenueId = venueId;
    const kind = kidTypeLabel(p.type);
    detail.className = "pin-detail";
    detail.innerHTML = `
      <p class="pin-detail-kicker">Selected · ${escapeHtml(kind)}</p>
      <h3>${escapeHtml(p.emoji || "")} ${escapeHtml(p.name)}</h3>
      <p class="pd-meta">${escapeHtml(p.city)}, ${escapeHtml(p.state)} · ${
      p.tier === "top" || TOP_IDS.has(p.id) ? "Top list" : "More"
    }</p>
      <span class="pd-status ready">Ready to play</span>
      <p class="pd-blurb">${escapeHtml(p.blurb)}</p>
      <div class="pd-actions">
        <a class="btn btn-primary" href="${p.appHref || "#"}">Start outing →</a>
        <a class="btn btn-secondary" href="${p.href || "#"}">Place info</a>
      </div>
      <p class="pd-blurb" style="margin-top:10px;font-size:0.88rem">Double-click the pin to zoom the map here.</p>
    `;
  }

  function setVenue(venueId, opts = {}) {
    if (!venueId) {
      selectedVenueId = "";
      fillVenueSelect();
      renderPins();
      showOverview();
      return;
    }
    selectedVenueId = venueId;
    const p = placeById(venueId);
    // Don't call setScope (resets selection) — just flip mode quietly if needed
    if (p && mapScope === "top" && !(TOP_IDS.has(p.id) || p.tier === "top")) {
      mapScope = "more";
      scopeTop?.setAttribute("aria-pressed", "false");
      scopeMore?.setAttribute("aria-pressed", "true");
      scopeTop?.classList.remove("active");
      scopeMore?.classList.add("active");
      fillLocationSelect();
    }
    if (p && mapScope === "more" && selectedState && p.state !== selectedState) {
      selectedState = p.state;
      if (stateSelect) stateSelect.value = selectedState;
    }
    fillVenueSelect();
    venueSelect.value = venueId;
    showVenueDetail(venueId);
    renderPins();
  }

  function setScope(scope) {
    mapScope = scope === "more" ? "more" : "top";
    selectedVenueId = "";
    selectedMetroId = "all";
    selectedState = "";
    if (scopeTop) scopeTop.setAttribute("aria-pressed", mapScope === "top" ? "true" : "false");
    if (scopeMore) scopeMore.setAttribute("aria-pressed", mapScope === "more" ? "true" : "false");
    scopeTop?.classList.toggle("active", mapScope === "top");
    scopeMore?.classList.toggle("active", mapScope === "more");
    fillLocationSelect();
    fillVenueSelect();
    renderPins();
    showOverview();
    if (mapScope === "more" && zoom < 1.2) setZoom(1.15);
    if (mapScope === "top") setZoom(1);
  }

  async function boot() {
    if (scopeTop) scopeTop.addEventListener("click", () => setScope("top"));
    if (scopeMore) scopeMore.addEventListener("click", () => setScope("more"));
    citySelect.addEventListener("change", () => {
      if (mapScope === "top") {
        selectedMetroId = citySelect.value || "all";
        selectedVenueId = "";
        fillVenueSelect();
        renderPins();
        showOverview();
      }
    });
    if (stateSelect) {
      stateSelect.addEventListener("change", () => {
        selectedState = stateSelect.value || "";
        selectedVenueId = "";
        fillLocationSelect();
        fillVenueSelect();
        renderPins();
        showOverview();
        if (selectedState) setZoom(Math.max(zoom, 1.6));
        else setZoom(1.15);
      });
    }
    venueSelect.addEventListener("change", () => setVenue(venueSelect.value));

    btnZoomIn?.addEventListener("click", () => {
      if (!mapViewport) return setZoom(zoom + 0.35);
      const r = mapViewport.getBoundingClientRect();
      zoomToClientPoint(r.left + r.width / 2, r.top + r.height / 2, zoom + 0.35);
    });
    btnZoomOut?.addEventListener("click", () => {
      if (!mapViewport) return setZoom(zoom - 0.35);
      const r = mapViewport.getBoundingClientRect();
      zoomToClientPoint(r.left + r.width / 2, r.top + r.height / 2, zoom - 0.35);
    });
    btnZoomReset?.addEventListener("click", () => setZoom(1));

    // Double-click empty map: zoom in centered on that point
    mapViewport?.addEventListener("dblclick", (e) => {
      if (e.target.closest && e.target.closest(".venue-pin")) return;
      e.preventDefault();
      zoomToClientPoint(e.clientX, e.clientY, Math.min(3.5, zoom + 0.75));
    });

    // drag pan when zoomed (ignore if starting on a pin)
    let dragging = false;
    let lastX = 0;
    let lastY = 0;
    let dragMoved = false;
    mapViewport?.addEventListener("pointerdown", (e) => {
      if (e.target.closest && e.target.closest(".venue-pin")) return;
      if (zoom <= 1) return;
      dragging = true;
      dragMoved = false;
      lastX = e.clientX;
      lastY = e.clientY;
      mapViewport.setPointerCapture(e.pointerId);
    });
    mapViewport?.addEventListener("pointermove", (e) => {
      if (!dragging) return;
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      if (Math.abs(dx) + Math.abs(dy) > 2) dragMoved = true;
      panX += dx;
      panY += dy;
      lastX = e.clientX;
      lastY = e.clientY;
      applyMapTransform();
    });
    mapViewport?.addEventListener("pointerup", () => {
      dragging = false;
    });
    mapViewport?.addEventListener(
      "wheel",
      (e) => {
        e.preventDefault();
        zoomToClientPoint(e.clientX, e.clientY, zoom + (e.deltaY < 0 ? 0.15 : -0.15));
      },
      { passive: false }
    );

    try {
      const res = await fetch("/field-pack/img/usa-map.svg?v=5");
      const svgText = await res.text();
      mapHost.innerHTML = svgText;
      svgEl = mapHost.querySelector("svg");
      if (svgEl) {
        svgEl.removeAttribute("width");
        svgEl.removeAttribute("height");
        svgEl.setAttribute("class", "usa-real-map");
        svgEl.style.transition = "transform 0.15s ease";
        const NS = "http://www.w3.org/2000/svg";
        pinsLayer = document.createElementNS(NS, "g");
        pinsLayer.setAttribute("id", "venue-pins-layer");
        svgEl.appendChild(pinsLayer);
      }
    } catch (err) {
      mapHost.innerHTML = `<p class="map-loading">Map unavailable — use the menus.</p>`;
      console.error(err);
    }

    fillLocationSelect();
    fillVenueSelect();
    renderPins();
    showOverview();
    scopeTop?.classList.add("active");
  }

  boot();
})();
