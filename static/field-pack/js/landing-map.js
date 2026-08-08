(() => {
  const allPlaces = window.FP_PLACES || [];
  const TOP_IDS = new Set(window.FP_TOP_PLACE_IDS || []);
  const INTL_IDS = new Set(window.FP_INTL_PLACE_IDS || []);
  const detail = document.getElementById("pin-detail");
  const mapHost = document.getElementById("map-host");
  const citySelect = document.getElementById("city-select");
  const venueSelect = document.getElementById("venue-select-landing");
  const scopeTop = document.getElementById("scope-top");
  const scopeMore = document.getElementById("scope-more");
  const scopeIntl = document.getElementById("scope-intl");
  const stateSelect = document.getElementById("state-select");
  const stateField = document.getElementById("state-field");
  const metroField = document.getElementById("metro-field");
  const filterOr = document.querySelector(".filter-or");
  const mapCount = document.getElementById("map-count");
  const btnZoomIn = document.getElementById("map-zoom-in");
  const btnZoomOut = document.getElementById("map-zoom-out");
  const btnZoomReset = document.getElementById("map-zoom-reset");
  const mapViewport = document.getElementById("map-viewport");

  /** Metro groups for Top mode dropdown (not every pin). */
  const METRO_DEFS = [
    { id: "all", label: "Any area", symbols: "🇺🇸", states: null },
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
    { id: "florida", label: "Florida", symbols: "🚀", states: ["FL"], cities: ["Merritt Island"] },
  ];

  const INTL_REGIONS = [
    { id: "all", label: "Any region" },
    { id: "europe", label: "Europe" },
    { id: "asia", label: "Asia" },
    { id: "americas", label: "Americas" },
    { id: "oceania", label: "Oceania" },
    { id: "middle-east", label: "Middle East" },
    { id: "africa", label: "Africa" },
  ];

  let mapScope = "more"; // top | more | intl — default: all US places
  let basemap = "us"; // us | world — world only when International selected
  let mapLoadToken = 0;
  let selectedMetroId = "all";
  let selectedRegion = "all";
  let selectedState = "";
  let selectedCountry = "";
  let selectedVenueId = "";
  let clusterFocusIds = []; // nearby group open in side panel
  const MIN_ZOOM = 1;
  const MAX_ZOOM = 4;
  let zoom = 1;
  let panX = 0;
  let panY = 0;
  let svgEl = null;
  let pinsLayer = null;
  let pinRenderTimer = null;

  function isUSPlace(p) {
    if (!p) return false;
    const c = (p.country || "US").toUpperCase();
    return c === "US" || c === "USA";
  }

  function isIntlPlace(p) {
    return Boolean(p) && !isUSPlace(p);
  }

  function placeRegionLabel(p) {
    if (!p) return "";
    if (isIntlPlace(p)) return p.countryName || p.country || "";
    return p.state || "";
  }

  function placeById(id) {
    return allPlaces.find((p) => p.id === id);
  }

  function placesInScope() {
    if (mapScope === "intl") {
      return allPlaces.filter(
        (p) => isIntlPlace(p) || INTL_IDS.has(p.id) || p.tier === "intl"
      );
    }
    const us = allPlaces.filter(isUSPlace);
    if (mapScope === "top") {
      return us.filter((p) => TOP_IDS.has(p.id) || p.tier === "top");
    }
    return us;
  }

  /**
   * Places for the Place dropdown + map pins.
   * US scopes never include international pins (wrong basemap).
   * A selected state always uses the FULL US catalog for that state (not Popular top-N).
   */
  function matchesMetro(p, m) {
    if (!m || m.id === "all") return true;
    if (m.regions && m.regions.includes(p.region)) return true;
    if (m.cities && m.cities.includes(p.city)) return true;
    if (m.states && m.states.includes(p.state) && !m.cities && !m.regions) return true;
    if (m.id === "dallas") return p.region === "dfw" || ["Dallas", "Fort Worth"].includes(p.city);
    if (m.id === "houston") return p.city === "Houston";
    if (m.id === "austin") return p.city === "Austin";
    return Boolean(m.states && m.states.includes(p.state) && (!m.cities || m.cities.includes(p.city)));
  }

  function filteredPlaces() {
    let list;
    if (mapScope === "intl") {
      list = placesInScope();
      if (selectedRegion && selectedRegion !== "all") {
        list = list.filter((p) => (p.region || "") === selectedRegion);
      }
      if (selectedCountry) {
        list = list.filter((p) => (p.country || "").toUpperCase() === selectedCountry);
      }
    } else if (selectedState) {
      // Full catalog for this state — ignore Popular/top tier cap and metro
      list = allPlaces.filter((p) => isUSPlace(p) && p.state === selectedState);
    } else {
      // Popular or All places (US) — metro filter applies on both
      list = placesInScope();
      if (selectedMetroId && selectedMetroId !== "all") {
        const m = METRO_DEFS.find((x) => x.id === selectedMetroId);
        if (m) list = list.filter((p) => matchesMetro(p, m));
      }
    }
    return list.sort((a, b) => {
      if (mapScope === "intl") {
        const ar = a.status === "ready" ? 0 : 1;
        const br = b.status === "ready" ? 0 : 1;
        if (ar !== br) return ar - br;
        const ac = (a.city || "").localeCompare(b.city || "");
        if (ac !== 0) return ac;
      }
      return a.name.localeCompare(b.name);
    });
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
    const city = p.city === "Escondido" ? "San Diego area" : p.city;
    const region = placeRegionLabel(p);
    const ready = p.status === "ready" ? "✓ " : "";
    const where = region ? `${city}, ${region}` : city;
    return `${ready}${p.emoji || "📍"} ${p.name} — ${where}`;
  }

  function escapeHtml(s) {
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  /** Distinct state codes from the venue catalog (or a subset). */
  function distinctStates(list) {
    const set = new Set(
      (list || [])
        .filter(isUSPlace)
        .map((p) => (p && typeof p.state === "string" ? p.state.trim() : ""))
        .filter(Boolean)
    );
    return [...set].sort((a, b) => a.localeCompare(b));
  }

  /** Distinct countries for international scope: [{code, name}] sorted by name. */
  function distinctCountries(list) {
    const map = new Map();
    for (const p of list || []) {
      if (!isIntlPlace(p)) continue;
      const code = (p.country || "").toUpperCase();
      if (!code) continue;
      if (!map.has(code)) {
        map.set(code, p.countryName || code);
      }
    }
    return [...map.entries()]
      .map(([code, name]) => ({ code, name }))
      .sort((a, b) => a.name.localeCompare(b.name));
  }

  function clearSelect(sel) {
    if (!sel) return;
    sel.innerHTML = "";
  }

  /**
   * Always keep the State <select> filled from the full catalog so it is never
   * empty if CSS fails to honor [hidden]. Visibility depends on whether we have data.
   * Returns the sorted state list (may be empty).
   */
  function fillStateSelectOptions() {
    const states = distinctStates(allPlaces);
    if (!stateSelect) return states;

    const prev = selectedState;
    clearSelect(stateSelect);
    const o0 = document.createElement("option");
    o0.value = "";
    o0.textContent = "All states";
    stateSelect.appendChild(o0);
    for (const st of states) {
      const o = document.createElement("option");
      o.value = st;
      o.textContent = st;
      stateSelect.appendChild(o);
    }
    if (prev && states.includes(prev)) {
      selectedState = prev;
      stateSelect.value = prev;
    } else {
      selectedState = "";
      stateSelect.value = "";
    }
    return states;
  }

  /**
   * Populate Metroarea + State filters.
   * Both stay in the layout always (plus fixed Place column) so selecting State
   * never shifts the Place dropdown. When a state is chosen, metro is disabled
   * but still occupies its slot; clearing state re-enables metro.
   */
  function setStateFieldLabel(text) {
    const label = stateField && stateField.querySelector(".select-label");
    if (label) label.textContent = text;
    if (stateSelect) {
      stateSelect.setAttribute("aria-label", text === "Country" ? "Filter by country" : "Filter by state");
    }
  }

  function fillCountrySelectOptions() {
    let source = placesInScope();
    if (selectedRegion && selectedRegion !== "all") {
      source = source.filter((p) => (p.region || "") === selectedRegion);
    }
    const countries = distinctCountries(source);
    if (!stateSelect) return countries;
    const prev = selectedCountry;
    clearSelect(stateSelect);
    const o0 = document.createElement("option");
    o0.value = "";
    o0.textContent = "All countries";
    stateSelect.appendChild(o0);
    for (const c of countries) {
      const o = document.createElement("option");
      o.value = c.code;
      o.textContent = c.name;
      stateSelect.appendChild(o);
    }
    if (prev && countries.some((c) => c.code === prev)) {
      selectedCountry = prev;
      stateSelect.value = prev;
    } else {
      selectedCountry = "";
      stateSelect.value = "";
    }
    return countries;
  }

  function fillLocationSelect() {
    if (!citySelect) return;

    if (mapScope === "intl") {
      if (metroField) metroField.hidden = false;
      if (filterOr) filterOr.hidden = false;
      if (citySelect) {
        citySelect.disabled = false;
        clearSelect(citySelect);
        for (const r of INTL_REGIONS) {
          const opt = document.createElement("option");
          opt.value = r.id;
          opt.textContent = r.label;
          citySelect.appendChild(opt);
        }
        citySelect.value = selectedRegion || "all";
      }
      const metroLabel = metroField && metroField.querySelector(".select-label");
      if (metroLabel) metroLabel.textContent = "Region";
      if (citySelect) citySelect.setAttribute("aria-label", "Filter by region");
      setStateFieldLabel("Country");
      const countries = fillCountrySelectOptions();
      if (stateField) stateField.hidden = countries.length === 0;
      return;
    }

    // restore US metro label
    const metroLabelUs = metroField && metroField.querySelector(".select-label");
    if (metroLabelUs) metroLabelUs.textContent = "Metroarea";
    if (citySelect) citySelect.setAttribute("aria-label", "Choose metro area");

    // US scopes: Metro + State
    if (metroField) metroField.hidden = false;
    if (filterOr) filterOr.hidden = false;
    setStateFieldLabel("State");
    selectedCountry = "";

    const states = fillStateSelectOptions();

    // Never show an empty state control; never hide metro (layout must stay fixed)
    if (stateField) {
      stateField.hidden = states.length === 0;
    }
    if (!states.length) {
      selectedState = "";
    }

    clearSelect(citySelect);
    for (const m of METRO_DEFS) {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.textContent = m.id === "all" ? m.label : `${m.symbols} ${m.label}`;
      citySelect.appendChild(opt);
    }
    citySelect.value = selectedMetroId || "all";
    // State selection wins: keep metro visible but inactive so Place stays put
    citySelect.disabled = Boolean(selectedState);
  }

  function fillVenueSelect() {
    const list = filteredPlaces();
    venueSelect.innerHTML = "";
    const ph = document.createElement("option");
    ph.value = "";
    if (mapScope === "intl" && selectedCountry) {
      const cname = (list[0] && list[0].countryName) || selectedCountry;
      ph.textContent = `Places in ${cname} (${list.length})…`;
    } else if (mapScope === "intl") {
      ph.textContent = `Choose a place worldwide (${list.length})…`;
    } else if (selectedState) {
      ph.textContent = `All places in ${selectedState} (${list.length})…`;
    } else {
      ph.textContent = `Choose a place (${list.length})…`;
    }
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
      const usCount = allPlaces.filter(isUSPlace).length;
      const topN = allPlaces.filter((p) => isUSPlace(p) && (TOP_IDS.has(p.id) || p.tier === "top")).length;
      if (mapScope === "intl") {
        const readyN = list.filter((p) => p.status === "ready").length;
        if (selectedCountry) {
          const name =
            (list[0] && list[0].countryName) ||
            selectedCountry;
          mapCount.textContent =
            readyN > 0
              ? `International · ${list.length} in ${name} (${readyN} ready to print)`
              : `International · ${list.length} places in ${name}`;
        } else {
          mapCount.textContent =
            readyN > 0
              ? `International · ${list.length} on the world map · ${readyN} ready to print`
              : `International · ${list.length} places on the world map`;
        }
      } else if (selectedState) {
        mapCount.textContent = `Showing all ${list.length} places in ${selectedState} — pick one below or tap a pin`;
      } else if (selectedMetroId && selectedMetroId !== "all") {
        const m = METRO_DEFS.find((x) => x.id === selectedMetroId);
        const label = (m && m.label) || "this area";
        mapCount.textContent = `Showing ${list.length} places in ${label}`;
      } else if (mapScope === "top") {
        mapCount.textContent = `Showing ${list.length} popular places — switch to “All places” for more`;
      } else {
        mapCount.textContent = `Showing ${list.length} places — tap a pin or pick from the lists`;
      }
    }
  }

  /** Ensure UI is on All places so state filter can show, without wiping selectedState. */
  function ensureAllPlacesScope() {
    if (mapScope === "more") return;
    if (mapScope === "intl") return; // don't yank off world map for US state filter
    mapScope = "more";
    selectedMetroId = "all";
    updateScopeButtons();
  }

  function updateScopeButtons() {
    const isTop = mapScope === "top";
    const isMore = mapScope === "more";
    const isIntl = mapScope === "intl";
    if (scopeTop) {
      scopeTop.setAttribute("aria-pressed", isTop ? "true" : "false");
      scopeTop.classList.toggle("active", isTop);
    }
    if (scopeMore) {
      scopeMore.setAttribute("aria-pressed", isMore ? "true" : "false");
      scopeMore.classList.toggle("active", isMore);
    }
    if (scopeIntl) {
      scopeIntl.setAttribute("aria-pressed", isIntl ? "true" : "false");
      scopeIntl.classList.toggle("active", isIntl);
    }
  }

  /**
   * Clamp pan so the scaled map always covers the viewport (no white gutters).
   * Standard map-pan bound: max |pan| = (scaledSize - viewSize) / 2 with center origin.
   */
  function clampPan() {
    if (!mapViewport || !svgEl) {
      panX = 0;
      panY = 0;
      return;
    }
    if (zoom <= 1.001) {
      panX = 0;
      panY = 0;
      return;
    }
    const view = mapViewport.getBoundingClientRect();
    // Layout size without CSS transform
    const baseW = svgEl.offsetWidth || view.width;
    const baseH = svgEl.offsetHeight || view.height;
    const scaledW = baseW * zoom;
    const scaledH = baseH * zoom;
    const maxX = Math.max(0, (scaledW - view.width) / 2);
    const maxY = Math.max(0, (scaledH - view.height) / 2);
    panX = Math.min(maxX, Math.max(-maxX, panX));
    panY = Math.min(maxY, Math.max(-maxY, panY));
  }

  function applyMapTransform() {
    if (!svgEl) return;
    clampPan();
    svgEl.style.transformOrigin = "center center";
    svgEl.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
    updateMapCursor();
    updateZoomButtons();
  }

  function clampZoom(z) {
    return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, z));
  }

  function setZoom(z) {
    zoom = clampZoom(z);
    if (zoom <= 1) {
      panX = 0;
      panY = 0;
    }
    applyMapTransform();
    renderPins();
  }

  /**
   * ⟲ Reset: restore this scope's original map view — all pins, no filters,
   * pan centered, default zoom (US All places ~1.15; Popular/International = 1).
   */
  function resetMapView() {
    selectedVenueId = "";
    clusterFocusIds = [];
    selectedMetroId = "all";
    selectedRegion = "all";
    selectedState = "";
    selectedCountry = "";
    panX = 0;
    panY = 0;

    fillLocationSelect();
    fillVenueSelect();
    renderPins();
    showOverview();
    syncVenueHash("");

    // Default framing matches first open of this scope
    if (mapScope === "more" && basemap === "us") setZoom(1.15);
    else setZoom(1);
  }

  /**
   * Zoom toward a viewport point (cursor / pinch center).
   * continuous: skip pin rebuild every frame (trackpad pinch / wheel stream).
   */
  function zoomToClientPoint(clientX, clientY, newZoom, opts = {}) {
    const continuous = opts.continuous === true;
    if (!mapViewport) {
      setZoom(newZoom);
      return;
    }
    const rect = mapViewport.getBoundingClientRect();
    const ox = clientX - rect.left - rect.width / 2;
    const oy = clientY - rect.top - rect.height / 2;
    const z0 = zoom || 1;
    const z1 = clampZoom(newZoom);
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
    if (continuous && svgEl) svgEl.style.transition = "none";
    applyMapTransform();
    if (continuous) {
      if (pinRenderTimer) clearTimeout(pinRenderTimer);
      pinRenderTimer = setTimeout(() => {
        pinRenderTimer = null;
        if (svgEl) svgEl.style.transition = "transform 0.15s ease";
        renderPins();
      }, 90);
    } else {
      if (pinRenderTimer) {
        clearTimeout(pinRenderTimer);
        pinRenderTimer = null;
      }
      if (svgEl) svgEl.style.transition = "transform 0.15s ease";
      renderPins();
    }
  }

  /** Center map on a place (svg coords → pan), optional target zoom. Does not filter. */
  function panToPlace(p, targetZoom) {
    if (!p || !svgEl || !mapViewport) return;
    const pt = pinXY(p);
    if (!pt) return;
    const z = clampZoom(targetZoom != null ? targetZoom : Math.max(zoom, basemap === "world" ? 2.0 : 1.7));
    const baseW = svgEl.offsetWidth || mapViewport.clientWidth;
    const baseH = svgEl.offsetHeight || mapViewport.clientHeight;
    const vb = svgEl.viewBox && svgEl.viewBox.baseVal;
    const vw = (vb && vb.width) || (basemap === "world" ? 1000 : 959);
    const vh = (vb && vb.height) || (basemap === "world" ? 500 : 593);
    // Local coords relative to element center (transform-origin center)
    const lx = (pt.x / vw) * baseW - baseW / 2;
    const ly = (pt.y / vh) * baseH - baseH / 2;
    zoom = z;
    panX = -lx * z;
    panY = -ly * z;
    if (svgEl) svgEl.style.transition = "transform 0.2s ease";
    applyMapTransform();
    updateMapCursor();
  }

  function updateMapCursor() {
    if (!mapViewport) return;
    mapViewport.style.cursor = zoom > 1.001 ? "grab" : "default";
  }

  function updateZoomButtons() {
    if (btnZoomIn) {
      const maxed = zoom >= MAX_ZOOM - 0.01;
      btnZoomIn.disabled = maxed;
      btnZoomIn.setAttribute("aria-disabled", maxed ? "true" : "false");
      btnZoomIn.title = maxed ? "Maximum zoom" : "Zoom in";
    }
    if (btnZoomOut) {
      const mined = zoom <= MIN_ZOOM + 0.01;
      btnZoomOut.disabled = mined;
      btnZoomOut.setAttribute("aria-disabled", mined ? "true" : "false");
      btnZoomOut.title = mined ? "Minimum zoom" : "Zoom out";
    }
  }

  /** Normalize wheel delta to roughly pixel units (mouse, trackpad, Firefox). */
  function wheelDeltaPixels(e) {
    let dy = e.deltaY;
    if (e.deltaMode === 1) dy *= 16; // lines
    else if (e.deltaMode === 2) dy *= (mapViewport?.clientHeight || 400); // pages
    return dy;
  }

  /**
   * Wheel + Mac trackpad pinch (ctrl+wheel) + Safari gesture events.
   * Multiplicative zoom toward cursor — standard map practice.
   */
  function bindMapZoom() {
    if (!mapViewport) return;

    mapViewport.addEventListener(
      "wheel",
      (e) => {
        // Always preventDefault so Mac pinch does not zoom the whole page
        e.preventDefault();
        const dy = wheelDeltaPixels(e);
        if (!dy) return;
        // Pinch (ctrlKey on Chrome/Safari/Firefox Mac) needs higher sensitivity;
        // mouse wheel notches are larger absolute deltas.
        const sens = e.ctrlKey ? 0.012 : 0.0018;
        let factor = Math.exp(-dy * sens);
        // Cap per-event so a single notch is gentle; stream of pinch events stays smooth
        factor = Math.min(1.2, Math.max(1 / 1.2, factor));
        zoomToClientPoint(e.clientX, e.clientY, zoom * factor, { continuous: true });
      },
      { passive: false }
    );

    // Safari legacy trackpad pinch (when not fully covered by ctrl+wheel)
    let gestureBaseZoom = 1;
    const onGesture = (e) => {
      e.preventDefault();
      if (e.type === "gesturestart") {
        gestureBaseZoom = zoom;
        if (svgEl) svgEl.style.transition = "none";
        return;
      }
      if (e.type === "gesturechange") {
        const scale = typeof e.scale === "number" && e.scale > 0 ? e.scale : 1;
        const rect = mapViewport.getBoundingClientRect();
        zoomToClientPoint(
          rect.left + rect.width / 2,
          rect.top + rect.height / 2,
          gestureBaseZoom * scale,
          { continuous: true }
        );
        return;
      }
      // gestureend
      if (svgEl) svgEl.style.transition = "transform 0.15s ease";
      renderPins();
    };
    mapViewport.addEventListener("gesturestart", onGesture, { passive: false });
    mapViewport.addEventListener("gesturechange", onGesture, { passive: false });
    mapViewport.addEventListener("gestureend", onGesture, { passive: false });
  }

  function swallowNextClick() {
    const swallow = (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      mapViewport.removeEventListener("click", swallow, true);
    };
    mapViewport.addEventListener("click", swallow, true);
    setTimeout(() => mapViewport.removeEventListener("click", swallow, true), 0);
  }

  function endMapInteraction(moved) {
    mapViewport.classList.remove("is-dragging");
    if (svgEl) svgEl.style.transition = "transform 0.15s ease";
    applyMapTransform();
    if (pinRenderTimer) {
      clearTimeout(pinRenderTimer);
      pinRenderTimer = null;
    }
    renderPins();
    if (moved) swallowNextClick();
  }

  /**
   * Touch: one-finger pan + two-finger pinch/pan (iPhone / touch screens).
   * Pointer events only track one finger on iOS — multi-touch needs TouchEvent.
   */
  function bindMapTouchGestures() {
    if (!mapViewport) return;

    let mode = null; // null | "pan" | "pinch"
    let panState = null;
    let pinchState = null;
    let moved = false;

    const touchDist = (a, b) => {
      const dx = a.clientX - b.clientX;
      const dy = a.clientY - b.clientY;
      return Math.hypot(dx, dy) || 1;
    };
    const touchMid = (a, b) => ({
      x: (a.clientX + b.clientX) / 2,
      y: (a.clientY + b.clientY) / 2,
    });

    const startPan = (t) => {
      mode = "pan";
      panState = {
        x: t.clientX,
        y: t.clientY,
        panX0: panX,
        panY0: panY,
      };
      moved = false;
      mapViewport.classList.add("is-dragging");
      if (svgEl) svgEl.style.transition = "none";
    };

    const startPinch = (t0, t1) => {
      const mid = touchMid(t0, t1);
      mode = "pinch";
      pinchState = {
        dist0: touchDist(t0, t1),
        zoom0: zoom,
        midX: mid.x,
        midY: mid.y,
        panX0: panX,
        panY0: panY,
      };
      moved = false;
      mapViewport.classList.add("is-dragging");
      if (svgEl) svgEl.style.transition = "none";
    };

    mapViewport.addEventListener(
      "touchstart",
      (e) => {
        const onChrome =
          e.target.closest &&
          e.target.closest(".venue-pin, .zoom-btn, .scope-btn, button, a, select, .vpin-dismiss");

        if (e.touches.length >= 2) {
          // Two-finger always owned by the map (pinch / pan)
          e.preventDefault();
          startPinch(e.touches[0], e.touches[1]);
          return;
        }

        if (e.touches.length === 1) {
          if (onChrome) {
            mode = null;
            panState = null;
            pinchState = null;
            return;
          }
          // One-finger pan only when zoomed (same rule as desktop)
          if (zoom <= 1.001) return;
          e.preventDefault();
          startPan(e.touches[0]);
        }
      },
      { passive: false }
    );

    mapViewport.addEventListener(
      "touchmove",
      (e) => {
        if (!mode) return;

        if (mode === "pinch" && e.touches.length >= 2) {
          e.preventDefault();
          const t0 = e.touches[0];
          const t1 = e.touches[1];
          const mid = touchMid(t0, t1);
          const d = touchDist(t0, t1);
          const factor = d / pinchState.dist0;
          const newZoom = clampZoom(pinchState.zoom0 * factor);
          const rect = mapViewport.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          // Content under the original pinch midpoint (viewport-center coords)
          const ox0 = pinchState.midX - cx;
          const oy0 = pinchState.midY - cy;
          const contentX = (ox0 - pinchState.panX0) / pinchState.zoom0;
          const contentY = (oy0 - pinchState.panY0) / pinchState.zoom0;
          // Keep that content under the *current* midpoint (zoom + two-finger pan)
          const ox1 = mid.x - cx;
          const oy1 = mid.y - cy;
          zoom = newZoom;
          panX = ox1 - contentX * zoom;
          panY = oy1 - contentY * zoom;
          if (Math.abs(factor - 1) > 0.015 || Math.hypot(mid.x - pinchState.midX, mid.y - pinchState.midY) > 4) {
            moved = true;
          }
          if (svgEl) svgEl.style.transition = "none";
          applyMapTransform();
          // Debounce pin rebuild like continuous wheel zoom
          if (pinRenderTimer) clearTimeout(pinRenderTimer);
          pinRenderTimer = setTimeout(() => {
            pinRenderTimer = null;
            if (svgEl) svgEl.style.transition = "transform 0.15s ease";
            renderPins();
          }, 90);
          return;
        }

        if (mode === "pan" && e.touches.length === 1) {
          e.preventDefault();
          const t = e.touches[0];
          const dx = t.clientX - panState.x;
          const dy = t.clientY - panState.y;
          if (!moved && dx * dx + dy * dy > 25) moved = true;
          if (!moved) return;
          panX = panState.panX0 + dx;
          panY = panState.panY0 + dy;
          applyMapTransform();
          return;
        }

        // Finger count changed mid-gesture
        if (e.touches.length >= 2) {
          e.preventDefault();
          startPinch(e.touches[0], e.touches[1]);
        } else if (e.touches.length === 1 && zoom > 1.001) {
          e.preventDefault();
          startPan(e.touches[0]);
        }
      },
      { passive: false }
    );

    const onTouchEnd = (e) => {
      if (!mode) return;
      if (e.touches.length >= 2) {
        startPinch(e.touches[0], e.touches[1]);
        return;
      }
      if (e.touches.length === 1) {
        if (zoom > 1.001) startPan(e.touches[0]);
        else {
          mode = null;
          endMapInteraction(moved);
        }
        return;
      }
      // All fingers up
      const wasMoved = moved;
      mode = null;
      panState = null;
      pinchState = null;
      endMapInteraction(wasMoved);
    };

    mapViewport.addEventListener("touchend", onTouchEnd, { passive: false });
    mapViewport.addEventListener("touchcancel", onTouchEnd, { passive: false });
  }

  /** Pointer drag-pan for mouse / pen (touch uses bindMapTouchGestures). */
  function bindMapDrag() {
    if (!mapViewport) return;
    let drag = null; // { id, x, y, panX0, panY0, moved }

    const onMove = (e) => {
      if (!drag || e.pointerId !== drag.id) return;
      const dx = e.clientX - drag.x;
      const dy = e.clientY - drag.y;
      if (!drag.moved && dx * dx + dy * dy > 25) drag.moved = true;
      if (!drag.moved) return;
      panX = drag.panX0 + dx;
      panY = drag.panY0 + dy;
      applyMapTransform();
    };

    const endDrag = (e) => {
      if (!drag || (e && e.pointerId !== drag.id)) return;
      const wasMoved = drag.moved;
      try {
        mapViewport.releasePointerCapture(drag.id);
      } catch (_) {
        /* already released */
      }
      drag = null;
      endMapInteraction(wasMoved);
    };

    mapViewport.addEventListener("pointerdown", (e) => {
      // Touch multi-gestures handled separately (iOS only tracks one pointer)
      if (e.pointerType === "touch") return;
      if (e.button != null && e.button !== 0) return;
      if (e.target.closest && e.target.closest(".venue-pin, .zoom-btn, .scope-btn, button, a, select")) {
        return;
      }
      // Only pan when zoomed — at 1:1 there is no room to move without white space
      if (zoom <= 1.001) return;
      drag = {
        id: e.pointerId,
        x: e.clientX,
        y: e.clientY,
        panX0: panX,
        panY0: panY,
        moved: false,
      };
      mapViewport.classList.add("is-dragging");
      if (svgEl) svgEl.style.transition = "none";
      try {
        mapViewport.setPointerCapture(e.pointerId);
      } catch (_) {
        /* ignore */
      }
    });
    mapViewport.addEventListener("pointermove", onMove);
    mapViewport.addEventListener("pointerup", endDrag);
    mapViewport.addEventListener("pointercancel", endDrag);
    mapViewport.addEventListener("lostpointercapture", endDrag);

    window.addEventListener("resize", () => {
      applyMapTransform();
    });
  }

  function pinXY(p) {
    if (!svgEl || p.lat == null || p.lon == null) return null;
    const vb = svgEl.viewBox && svgEl.viewBox.baseVal;
    if (basemap === "world") {
      const w = (vb && vb.width) || 1000;
      const h = (vb && vb.height) || 500;
      if (typeof window.fpProjectWorld !== "function") return null;
      const pt = window.fpProjectWorld(p.lat, p.lon, w, h);
      if (!pt || !Number.isFinite(pt.x) || !Number.isFinite(pt.y)) return null;
      if (pt.x < 4 || pt.x > w - 4 || pt.y < 4 || pt.y > h - 4) return null;
      return pt;
    }
    const w = (vb && vb.width) || 959;
    const h = (vb && vb.height) || 593;
    if (typeof window.fpProjectUS !== "function") return null;
    const pt = window.fpProjectUS(p.lat, p.lon, w, h, p.state);
    if (!pt || !Number.isFinite(pt.x) || !Number.isFinite(pt.y)) return null;
    if (pt.x < 25 || pt.x > 940 || pt.y < 50 || pt.y > 560) return null;
    return pt;
  }

  /** Group venues whose map dots would sit on top of each other. */
  function buildClusters(list) {
    const items = [];
    for (const p of list) {
      const xy = pinXY(p);
      if (!xy) continue;
      items.push({ p, x: xy.x, y: xy.y });
    }

    // World map: cluster only same city so London stays its own pin (not mixed with Paris).
    if (basemap === "world") {
      const byCity = new Map();
      for (const it of items) {
        const key = `${(it.p.city || it.p.id).toLowerCase()}|${(it.p.country || "").toUpperCase()}`;
        if (!byCity.has(key)) byCity.set(key, []);
        byCity.get(key).push(it);
      }
      const clusters = [];
      for (const group of byCity.values()) {
        const cx = group.reduce((s, g) => s + g.x, 0) / group.length;
        const cy = group.reduce((s, g) => s + g.y, 0) / group.length;
        const places = group.map((g) => g.p).sort((a, b) => {
          const ar = a.status === "ready" ? 0 : 1;
          const br = b.status === "ready" ? 0 : 1;
          if (ar !== br) return ar - br;
          return a.name.localeCompare(b.name);
        });
        clusters.push({ x: cx, y: cy, places, ids: places.map((p) => p.id) });
      }
      return clusters;
    }

    // ~28px in SVG space; slightly tighter when zoomed in
    const thresh = zoom >= 2 ? 14 : zoom >= 1.4 ? 20 : 28;
    const used = new Array(items.length).fill(false);
    const clusters = [];
    for (let i = 0; i < items.length; i++) {
      if (used[i]) continue;
      const group = [items[i]];
      used[i] = true;
      for (let j = i + 1; j < items.length; j++) {
        if (used[j]) continue;
        const dx = items[i].x - items[j].x;
        const dy = items[i].y - items[j].y;
        if (dx * dx + dy * dy <= thresh * thresh) {
          used[j] = true;
          group.push(items[j]);
        }
      }
      // also merge if any member close to group centroid iteratively
      let changed = true;
      while (changed) {
        changed = false;
        const cx = group.reduce((s, g) => s + g.x, 0) / group.length;
        const cy = group.reduce((s, g) => s + g.y, 0) / group.length;
        for (let j = 0; j < items.length; j++) {
          if (used[j]) continue;
          const dx = cx - items[j].x;
          const dy = cy - items[j].y;
          if (dx * dx + dy * dy <= thresh * thresh) {
            used[j] = true;
            group.push(items[j]);
            changed = true;
          }
        }
      }
      const cx = group.reduce((s, g) => s + g.x, 0) / group.length;
      const cy = group.reduce((s, g) => s + g.y, 0) / group.length;
      const places = group.map((g) => g.p).sort((a, b) => a.name.localeCompare(b.name));
      clusters.push({ x: cx, y: cy, places, ids: places.map((p) => p.id) });
    }
    return clusters;
  }

  function renderPins() {
    if (!svgEl || !pinsLayer) return;
    while (pinsLayer.firstChild) pinsLayer.removeChild(pinsLayer.firstChild);
    svgEl.querySelectorAll(".city-pin").forEach((el) => {
      el.style.display = "none";
    });

    const list = filteredPlaces();
    const clusters = buildClusters(list);
    const NS = "http://www.w3.org/2000/svg";
    const focusSet = new Set(clusterFocusIds);

    for (const cl of clusters) {
      const n = cl.places.length;
      const selectedHere =
        (selectedVenueId && cl.ids.includes(selectedVenueId)) ||
        (focusSet.size && cl.ids.some((id) => focusSet.has(id)));
      const x = cl.x;
      const y = cl.y;

      const g = document.createElementNS(NS, "g");
      g.setAttribute(
        "class",
        "venue-pin" +
          (selectedHere ? " selected" : "") +
          (n > 1 ? " is-cluster" : "")
      );
      g.setAttribute("tabindex", "0");
      g.setAttribute("role", "button");
      g.setAttribute(
        "aria-label",
        n > 1
          ? `${n} places near ${cl.places[0].city || "here"}`
          : cl.places[0].name
      );
      g.dataset.clusterIds = cl.ids.join(",");
      g.style.cursor = "pointer";

      const halo = document.createElementNS(NS, "circle");
      halo.setAttribute("class", "vpin-halo");
      halo.setAttribute("cx", x);
      halo.setAttribute("cy", y);
      halo.setAttribute("r", n > 1 ? "18" : mapScope === "more" ? "12" : "16");
      g.appendChild(halo);

      const core = document.createElementNS(NS, "circle");
      core.setAttribute("class", "vpin-core");
      core.setAttribute("cx", x);
      core.setAttribute("cy", y);
      core.setAttribute("r", n > 1 ? "11" : selectedHere ? "8" : mapScope === "more" ? "5" : "7");
      g.appendChild(core);

      if (n > 1) {
        const count = document.createElementNS(NS, "text");
        count.setAttribute("class", "vpin-count");
        count.setAttribute("x", x);
        count.setAttribute("y", y + 4);
        count.setAttribute("text-anchor", "middle");
        count.textContent = String(n);
        g.appendChild(count);
      }

      // Hover / selected name chip (single only; clusters open list in panel)
      const chip = document.createElementNS(NS, "g");
      const showChipSelected = selectedHere && n === 1;
      chip.setAttribute(
        "class",
        "vpin-chip" + (showChipSelected ? " vpin-chip-on is-visible" : "")
      );
      chip.setAttribute("transform", `translate(${x + 12}, ${y - 10})`);
      const hoverName =
        n > 1
          ? `${n} places · ${cl.places[0].city || "area"}`
          : `${cl.places[0].emoji || "•"} ${
              cl.places[0].name.length > 26
                ? cl.places[0].name.slice(0, 24) + "…"
                : cl.places[0].name
            }`;
      const textW = Math.min(210, 12 + hoverName.length * 6.2 + (showChipSelected ? 18 : 0));
      const bg = document.createElementNS(NS, "rect");
      bg.setAttribute("class", "vpin-chip-bg");
      bg.setAttribute("x", "0");
      bg.setAttribute("y", "-12");
      bg.setAttribute("rx", "8");
      bg.setAttribute("ry", "8");
      bg.setAttribute("width", String(textW));
      bg.setAttribute("height", "22");
      chip.appendChild(bg);
      const label = document.createElementNS(NS, "text");
      label.setAttribute("class", "vpin-label" + (showChipSelected ? " vpin-label-on" : ""));
      label.setAttribute("x", "6");
      label.setAttribute("y", "4");
      label.textContent = hoverName;
      chip.appendChild(label);

      if (showChipSelected) {
        const dismiss = document.createElementNS(NS, "g");
        dismiss.setAttribute("class", "vpin-dismiss");
        dismiss.setAttribute("aria-label", "Clear selection");
        dismiss.style.cursor = "pointer";
        const dx = textW - 14;
        const dCircle = document.createElementNS(NS, "circle");
        dCircle.setAttribute("cx", String(dx));
        dCircle.setAttribute("cy", "0");
        dCircle.setAttribute("r", "8");
        dCircle.setAttribute("class", "vpin-dismiss-bg");
        const dX = document.createElementNS(NS, "text");
        dX.setAttribute("x", String(dx));
        dX.setAttribute("y", "4");
        dX.setAttribute("text-anchor", "middle");
        dX.setAttribute("class", "vpin-dismiss-x");
        dX.textContent = "×";
        dismiss.appendChild(dCircle);
        dismiss.appendChild(dX);
        const clear = (e) => {
          e.stopPropagation();
          e.preventDefault();
          setVenue("");
        };
        dismiss.addEventListener("click", clear);
        dismiss.addEventListener("pointerdown", (e) => e.stopPropagation());
        chip.appendChild(dismiss);
      }
      g.appendChild(chip);

      const showName = () => chip.classList.add("is-visible");
      const hideName = () => {
        if (!(selectedHere && n === 1)) chip.classList.remove("is-visible");
      };
      g.addEventListener("pointerenter", showName);
      g.addEventListener("pointerleave", hideName);
      g.addEventListener("focus", showName);
      g.addEventListener("blur", hideName);

      const activate = () => {
        if (n > 1) showClusterPicker(cl.places);
        else setVenue(cl.places[0].id, { fromPin: true });
      };

      g.addEventListener("click", (e) => {
        if (e.target.closest && e.target.closest(".vpin-dismiss")) return;
        e.stopPropagation();
        e.preventDefault();
        activate();
      });
      g.addEventListener("dblclick", (e) => {
        if (e.target.closest && e.target.closest(".vpin-dismiss")) return;
        e.stopPropagation();
        e.preventDefault();
        activate();
        zoomToClientPoint(e.clientX, e.clientY, zoom * 1.5);
      });
      g.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          activate();
        }
      });
      pinsLayer.appendChild(g);
    }

    const sel = pinsLayer.querySelector(".venue-pin.selected");
    if (sel) pinsLayer.appendChild(sel);
  }

  function showClusterPicker(places) {
    clusterFocusIds = places.map((p) => p.id);
    selectedVenueId = "";
    fillVenueSelect();
    renderPins();
    const city = places[0].city || "this area";
    const area =
      places[0].region === "dfw" || ["Dallas", "Fort Worth"].includes(places[0].city)
        ? "Dallas–Fort Worth area"
        : city;
    detail.className = "pin-detail";
    detail.innerHTML = `
      <div class="pd-title-row">
        <h3>${escapeHtml(area)}</h3>
        <button type="button" class="pd-clear" id="pd-clear-selection" aria-label="Clear">×</button>
      </div>
      <p class="pd-hint">${places.length} places here — pick one.</p>
      <div class="nearby-list" role="listbox" aria-label="Places nearby">
        ${places
          .map(
            (p) => `
          <button type="button" class="nearby-item" data-venue-id="${escapeHtml(p.id)}" role="option">
            <span class="nearby-emoji">${escapeHtml(p.emoji || "📍")}</span>
            <span class="nearby-copy">
              <strong>${escapeHtml(p.name)}</strong>
              <small>${escapeHtml([p.city, placeRegionLabel(p)].filter(Boolean).join(", "))}</small>
            </span>
            <span class="nearby-go">→</span>
          </button>`
          )
          .join("")}
      </div>
    `;
    detail.querySelector("#pd-clear-selection")?.addEventListener("click", () => {
      clusterFocusIds = [];
      setVenue("");
    });
    detail.querySelectorAll(".nearby-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = btn.getAttribute("data-venue-id");
        clusterFocusIds = [];
        setVenue(id, { fromPin: true });
      });
    });
  }

  function showOverview() {
    const list = filteredPlaces();
    const readyN = mapScope === "intl" ? list.filter((p) => p.status === "ready").length : 0;
    let scopeNote;
    if (mapScope === "intl") {
      scopeNote = `${list.length} places worldwide${readyN ? ` · ${readyN} ready` : ""}`;
    } else if (mapScope === "top") {
      scopeNote = `${list.length} popular places`;
    } else {
      scopeNote = `${list.length} places`;
    }
    detail.className = "pin-detail empty";
    detail.innerHTML = `
      <h3>Tap a pin</h3>
      <p class="pd-hint">Short list + one-page hunt for that place.</p>
      <p class="pd-meta">${escapeHtml(scopeNote)}. Numbered pins share a spot — tap to choose.</p>
    `;
  }

  function catalogVenue(venueId) {
    return typeof window.fpGetVenue === "function" ? window.fpGetVenue(venueId) : null;
  }

  function catalogItem(itemId) {
    return (window.FIELD_PACK_CATALOG && window.FIELD_PACK_CATALOG[itemId]) || null;
  }

  function sampleItemForVenue(venueId) {
    const ven = catalogVenue(venueId);
    if (!ven) return null;
    const topId =
      (window.FPPrint && window.FPPrint.topPickItemId && window.FPPrint.topPickItemId(ven)) ||
      (ven.featuredAnimalIds && ven.featuredAnimalIds[0]) ||
      (ven.animalIds && ven.animalIds[0]) ||
      null;
    return topId ? catalogItem(topId) : null;
  }

  function photoSrc(photo) {
    if (!photo) return "";
    if (photo.startsWith("http") || photo.startsWith("/")) return photo;
    return `/field-pack/${photo}`;
  }

  function syncVenueHash(venueId) {
    const next = venueId ? `#/venue/${encodeURIComponent(venueId)}` : "#us-map";
    if (location.hash !== next) {
      history.replaceState(null, "", next);
    }
  }

  function venueIdFromHash() {
    const m = (location.hash || "").match(/^#\/venue\/([^/?#]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  /** SEO pages with live mission generator — full set from mission-pilots.js */
  const MISSION_PILOTS =
    window.FP_MISSION_PILOT_SET ||
    new Set(window.FP_MISSION_PILOTS || []);

  function showVenueDetail(venueId) {
    const p = placeById(venueId);
    if (!p) {
      showOverview();
      return;
    }
    selectedVenueId = venueId;
    detail.className = "pin-detail pin-detail-rich";
    const blurb = (p.blurb || "").trim();
    const ven = catalogVenue(venueId);
    const canPrintHunt = Boolean(ven && (ven.treasureHunt || []).length);
    const sample = sampleItemForVenue(venueId);
    const samplePhoto = sample ? photoSrc(sample.photo) : "";
    const appHref = p.appHref || `/field-pack/app.html#/venue/${encodeURIComponent(venueId)}`;
    const missionHref = `/field-pack/${encodeURIComponent(venueId)}/#mission`;
    const isMissionPilot = MISSION_PILOTS.has(venueId);

    const sampleCard = sample
      ? `<button type="button" class="pd-sample-card" id="pd-print-sample" aria-label="Print sample Q&A card for ${escapeHtml(sample.name)}">
          ${
            samplePhoto
              ? `<img src="${escapeHtml(samplePhoto)}" alt="${escapeHtml(sample.name)} — sample find" width="320" height="200" loading="lazy" decoding="async" />`
              : `<span class="pd-sample-fallback" aria-hidden="true">${escapeHtml(sample.emoji || "⭐")}</span>`
          }
          <span class="pd-sample-body">
            <span class="pd-sample-kicker">Sample Q&amp;A card</span>
            <span class="pd-sample-name">${escapeHtml(sample.emoji || "")} ${escapeHtml(sample.name)}</span>
            <span class="pd-sample-blurb">${escapeHtml(sample.blurb || "Tap to print a one-page sample card.")}</span>
            <span class="pd-sample-cta">Tap to print this card →</span>
          </span>
        </button>`
      : "";

    const locLine = [p.city, placeRegionLabel(p)].filter(Boolean).join(", ");
    const isSoon = p.status === "soon";
    const quality = (ven && ven.quality) || "starter";
    const lastVerified = (ven && ven.lastVerified) || "";
    const verifiedLabel = lastVerified
      ? (() => {
          const [y, m] = lastVerified.split("-");
          const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
          const mi = Math.max(0, Math.min(11, (parseInt(m, 10) || 1) - 1));
          return `${months[mi]} ${y}`;
        })()
      : "";
    const statusBadge = isSoon
      ? `<span class="pd-status soon">Coming soon</span>`
      : canPrintHunt
        ? quality === "full"
          ? `<span class="pd-status ready">Ready to print</span>`
          : `<span class="pd-status starter">Starter list</span>`
        : "";
    const qualityHint =
      !isSoon && canPrintHunt
        ? quality === "full"
          ? `<p class="pd-hint pd-quality">Curated shortlist for a finishable kid day.${
              verifiedLabel ? ` List checked ${escapeHtml(verifiedLabel)}.` : ""
            }</p>`
          : `<p class="pd-hint pd-quality">Starter shortlist — animals change; skip anything closed or missing.</p>`
        : "";
    detail.innerHTML = `
      <p class="pin-detail-kicker">${escapeHtml(locLine)}</p>
      <div class="pd-title-row">
        <h3>${escapeHtml(p.emoji || "")} ${escapeHtml(p.name)}</h3>
        <button type="button" class="pd-clear" id="pd-clear-selection" aria-label="Clear selection">×</button>
      </div>
      ${statusBadge}
      ${blurb ? `<p class="pd-blurb">${escapeHtml(blurb)}</p>` : ""}
      ${qualityHint}
      ${
        isSoon
          ? `<p class="pd-hint">Pack in progress — shortlist and printable hunt coming next.</p>`
          : !canPrintHunt
            ? `<p class="pd-hint">Open the full list for this place’s kid shortlist and hunt.</p>`
            : ""
      }
      <div class="pd-actions">
        ${
          isMissionPilot
            ? `<a class="btn btn-primary" href="${missionHref}">Build personalized mission →</a>`
            : !isSoon && canPrintHunt
              ? `<button type="button" class="btn btn-primary" id="pd-print-hunt">One-page hunt to print</button>`
              : ""
        }
        ${
          isMissionPilot && canPrintHunt
            ? `<button type="button" class="btn btn-secondary" id="pd-print-hunt">Quick classic hunt</button>`
            : ""
        }
      </div>
      ${
        isMissionPilot
          ? `<p class="pd-hint pd-mission-hint">Personalized mission: age + time + optional name → one-page print.</p>`
          : ""
      }
      ${isSoon ? "" : sampleCard}
      ${
        !isSoon && sample
          ? `<p class="pd-more-hint">More cards in the full list</p>`
          : ""
      }
      ${
        isSoon
          ? ""
          : `<div class="pd-actions pd-actions-secondary">
        <a class="btn btn-secondary" href="${appHref}">Open full list →</a>
      </div>`
      }
    `;
    detail.querySelector("#pd-clear-selection")?.addEventListener("click", () => setVenue(""));
    detail.querySelector("#pd-print-hunt")?.addEventListener("click", () => {
      if (window.FPPrint && window.FPPrint.printTreasureForVenue(venueId)) return;
      location.href = appHref;
    });
    detail.querySelector("#pd-print-sample")?.addEventListener("click", () => {
      if (window.FPPrint && window.FPPrint.printSampleQaForVenue(venueId)) return;
      location.href = appHref;
    });
  }

  async function setVenue(venueId, opts = {}) {
    const skipHash = opts.skipHash === true;
    if (!venueId) {
      selectedVenueId = "";
      clusterFocusIds = [];
      fillVenueSelect();
      renderPins();
      showOverview();
      if (!skipHash) syncVenueHash("");
      return;
    }
    clusterFocusIds = [];
    selectedVenueId = venueId;
    const p = placeById(venueId);

    // Deep-link / pin: switch basemap only when needed (US default stays until intl).
    // Do not auto-apply country/region filters — that hid other pins and felt broken.
    let basemapSwitched = false;
    if (p && isIntlPlace(p) && mapScope !== "intl") {
      mapScope = "intl";
      selectedMetroId = "all";
      selectedState = "";
      selectedCountry = "";
      selectedRegion = "all";
      updateScopeButtons();
      await loadBasemap("world");
      basemapSwitched = true;
    } else if (p && isUSPlace(p) && mapScope === "intl") {
      mapScope = "more";
      selectedCountry = "";
      selectedRegion = "all";
      updateScopeButtons();
      await loadBasemap("us");
      basemapSwitched = true;
    } else if (p && mapScope === "top" && isUSPlace(p) && !(TOP_IDS.has(p.id) || p.tier === "top")) {
      // Don't call setScope (resets selection) — just flip mode quietly if needed
      mapScope = "more";
      updateScopeButtons();
    }

    // If a US state filter is active and the pin is outside it, clear filter so the pin stays on-map
    if (p && mapScope !== "intl" && selectedState && p.state && p.state !== selectedState) {
      selectedState = "";
      if (stateSelect) stateSelect.value = "";
    }
    // If metro filter excludes this place, clear metro so pin remains visible
    if (p && mapScope !== "intl" && selectedMetroId && selectedMetroId !== "all") {
      const m = METRO_DEFS.find((x) => x.id === selectedMetroId);
      if (m && !matchesMetro(p, m)) {
        selectedMetroId = "all";
      }
    }
    // Intl region/country filters: clear if they would hide the selected place
    if (p && mapScope === "intl") {
      if (selectedRegion && selectedRegion !== "all" && p.region !== selectedRegion) {
        selectedRegion = "all";
      }
      if (selectedCountry && (p.country || "").toUpperCase() !== selectedCountry) {
        selectedCountry = "";
      }
    }

    fillLocationSelect();
    fillVenueSelect();
    venueSelect.value = venueId;
    showVenueDetail(venueId);
    renderPins();
    // Frame the place without hiding siblings
    if (p && opts.fromPin !== false) {
      const wantZ =
        basemap === "world" ? Math.max(zoom, basemapSwitched ? 2.1 : 1.8) : Math.max(zoom, 1.6);
      panToPlace(p, wantZ);
    }
    if (!skipHash) syncVenueHash(venueId);
    if (opts.scroll !== false) {
      document.getElementById("us-map")?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  // Allow ready-cards / external links: /field-pack/#/venue/dallas-zoo
  window.fpSelectVenueOnMap = (id) => {
    void setVenue(id);
  };

  async function loadBasemap(kind) {
    const next = kind === "world" ? "world" : "us";
    const token = ++mapLoadToken;
    const url =
      next === "world"
        ? "/field-pack/img/world-map.svg?v=2"
        : "/field-pack/img/usa-map.svg?v=5";
    if (mapHost) {
      mapHost.innerHTML = `<p class="map-loading">Loading map…</p>`;
      mapHost.setAttribute("aria-label", next === "world" ? "World map" : "United States map");
    }
    const canvasWrap = mapHost && mapHost.closest(".map-canvas-wrap");
    if (canvasWrap) {
      canvasWrap.classList.toggle("is-world-map", next === "world");
    }
    try {
      const res = await fetch(url);
      const svgText = await res.text();
      if (token !== mapLoadToken) return;
      mapHost.innerHTML = svgText;
      svgEl = mapHost.querySelector("svg");
      if (svgEl) {
        svgEl.removeAttribute("width");
        svgEl.removeAttribute("height");
        svgEl.setAttribute(
          "class",
          next === "world" ? "world-real-map usa-real-map" : "usa-real-map"
        );
        svgEl.style.transition = "transform 0.15s ease";
        const NS = "http://www.w3.org/2000/svg";
        pinsLayer = document.createElementNS(NS, "g");
        pinsLayer.setAttribute("id", "venue-pins-layer");
        svgEl.appendChild(pinsLayer);
      }
      basemap = next;
      panX = 0;
      panY = 0;
      zoom = 1;
      applyMapTransform();
    } catch (err) {
      if (token !== mapLoadToken) return;
      mapHost.innerHTML = `<p class="map-loading">Map unavailable — use the menus.</p>`;
      console.error(err);
      svgEl = null;
      pinsLayer = null;
    }
  }

  async function setScope(scope) {
    const next = scope === "intl" ? "intl" : scope === "more" ? "more" : "top";
    const wasIntl = mapScope === "intl";
    const willIntl = next === "intl";
    mapScope = next;
    selectedVenueId = "";
    selectedMetroId = "all";
    selectedRegion = "all";
    selectedState = "";
    selectedCountry = "";
    clusterFocusIds = [];
    updateScopeButtons();

    if (wasIntl !== willIntl) {
      await loadBasemap(willIntl ? "world" : "us");
    }

    fillLocationSelect();
    fillVenueSelect();
    renderPins();
    showOverview();
    syncVenueHash("");
    if (mapScope === "more" && basemap === "us") setZoom(1.15);
    else setZoom(1);
  }

  async function boot() {
    if (scopeTop) scopeTop.addEventListener("click", () => void setScope("top"));
    if (scopeMore) scopeMore.addEventListener("click", () => void setScope("more"));
    if (scopeIntl) scopeIntl.addEventListener("click", () => void setScope("intl"));
    citySelect.addEventListener("change", () => {
      if (mapScope === "intl") {
        selectedRegion = citySelect.value || "all";
        selectedVenueId = "";
        selectedCountry = "";
        if (stateSelect) stateSelect.value = "";
        fillLocationSelect();
        fillVenueSelect();
        renderPins();
        showOverview();
        setZoom(1);
        return;
      }
      selectedMetroId = citySelect.value || "all";
      selectedVenueId = "";
      // Metro and State are alternatives — picking a metro clears state
      if (selectedMetroId && selectedMetroId !== "all" && selectedState) {
        selectedState = "";
        if (stateSelect) stateSelect.value = "";
      }
      fillLocationSelect();
      fillVenueSelect();
      renderPins();
      showOverview();
      if (selectedMetroId && selectedMetroId !== "all") setZoom(Math.max(zoom, 1.5));
      else setZoom(mapScope === "more" ? 1.15 : 1);
    });
    if (stateSelect) {
      stateSelect.addEventListener("change", () => {
        selectedVenueId = "";
        if (mapScope === "intl") {
          selectedCountry = (stateSelect.value || "").trim().toUpperCase();
          fillLocationSelect();
          fillVenueSelect();
          renderPins();
          showOverview();
          if (selectedCountry) setZoom(Math.max(zoom, 1.8));
          else setZoom(1);
          return;
        }
        selectedState = (stateSelect.value || "").trim();
        // Picking a state always means full catalog for that state (not Popular top-N)
        if (selectedState) {
          selectedMetroId = "all";
          ensureAllPlacesScope();
        }
        fillLocationSelect();
        fillVenueSelect();
        renderPins();
        showOverview();
        if (selectedState) setZoom(Math.max(zoom, 1.6));
        else setZoom(mapScope === "more" ? 1.15 : 1);
      });
    }
    venueSelect.addEventListener("change", () => void setVenue(venueSelect.value));

    btnZoomIn?.addEventListener("click", () => {
      if (!mapViewport) return setZoom(zoom * 1.35);
      const r = mapViewport.getBoundingClientRect();
      zoomToClientPoint(r.left + r.width / 2, r.top + r.height / 2, zoom * 1.35);
    });
    btnZoomOut?.addEventListener("click", () => {
      if (!mapViewport) return setZoom(zoom / 1.35);
      const r = mapViewport.getBoundingClientRect();
      zoomToClientPoint(r.left + r.width / 2, r.top + r.height / 2, zoom / 1.35);
    });
    // Reset: full original view for current scope (filters + pan + zoom + all pins)
    btnZoomReset?.addEventListener("click", () => resetMapView());

    // Double-click empty map: zoom in centered on that point
    mapViewport?.addEventListener("dblclick", (e) => {
      if (e.target.closest && e.target.closest(".venue-pin")) return;
      e.preventDefault();
      zoomToClientPoint(e.clientX, e.clientY, zoom * 1.6);
    });

    bindMapZoom();
    bindMapTouchGestures();
    bindMapDrag();

    /**
     * Geo-aware default: US visitors → US map; non-US → International.
     * Prefer saved scope, then timezone / language heuristics (no geolocation prompt).
     */
    function detectPreferIntl() {
      try {
        const saved = localStorage.getItem("fp-map-scope");
        if (saved === "intl") return true;
        if (saved === "us" || saved === "top" || saved === "more") return false;
      } catch (_) {
        /* private mode */
      }
      try {
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || "";
        if (/^America\//.test(tz) || tz === "Pacific/Honolulu" || tz === "US/Hawaii") {
          // America/* includes parts of South America — refine with language when possible
          const lang = (navigator.language || "").toLowerCase();
          if (lang.startsWith("en-us") || lang === "en" || lang.startsWith("en-ca") || lang.startsWith("es-us")) {
            return false;
          }
          // e.g. America/Sao_Paulo + pt-BR → intl
          if (lang && !lang.startsWith("en-us") && !lang.startsWith("en-ca") && !lang.startsWith("es-mx") && !lang.startsWith("es-us")) {
            if (/America\/(Argentina|Sao_Paulo|Bogota|Lima|Santiago|Mexico_City|Costa_Rica|Panama)/.test(tz)) {
              return true;
            }
          }
          return false; // default US for most America/* en speakers
        }
        // Europe, Asia, Africa, Australia, etc.
        return true;
      } catch (_) {
        const lang = (navigator.language || "").toLowerCase();
        if (lang.startsWith("en-us") || lang.startsWith("en-ca")) return false;
        if (lang.startsWith("en-gb") || lang.startsWith("en-au") || lang.startsWith("en-nz")) return true;
        return !lang.startsWith("en-us");
      }
    }

    function persistScopePreference(scope) {
      try {
        if (scope === "intl") localStorage.setItem("fp-map-scope", "intl");
        else localStorage.setItem("fp-map-scope", "us");
      } catch (_) {
        /* ignore */
      }
    }

    // Wrap setScope to remember preference
    const _setScope = setScope;
    setScope = async function (scope) {
      await _setScope(scope);
      persistScopePreference(scope === "intl" ? "intl" : "us");
      updateReadyChips(scope === "intl");
    };

    const preferIntl = detectPreferIntl();
    if (preferIntl) {
      await loadBasemap("world");
      mapScope = "intl";
      updateScopeButtons();
      fillLocationSelect();
      fillVenueSelect();
      renderPins();
      showOverview();
      setZoom(1);
    } else {
      await loadBasemap("us");
      mapScope = "more";
      updateScopeButtons();
      fillLocationSelect();
      fillVenueSelect();
      renderPins();
      showOverview();
      if (zoom < 1.2) setZoom(1.15);
    }
    updateReadyChips(mapScope === "intl");

    // Deep link: /field-pack/#/venue/dallas-zoo (intl ids switch basemap)
    const fromHash = venueIdFromHash();
    if (fromHash && placeById(fromHash)) {
      await setVenue(fromHash, { skipHash: true, scroll: true });
    }
    window.addEventListener("hashchange", () => {
      const id = venueIdFromHash();
      if (id && placeById(id)) {
        if (id !== selectedVenueId) void setVenue(id, { skipHash: true, scroll: true });
      } else if (!id && selectedVenueId) {
        void setVenue("", { skipHash: true });
      }
    });
  }

  /** Swap “Or try …” ready cards for US vs international visitors. */
  function updateReadyChips(isIntl) {
    const heading = document.getElementById("ready-heading");
    const grid = document.getElementById("ready-grid");
    if (!heading || !grid) return;
    const usCards = [
      { id: "dallas-zoo", emoji: "🦁", name: "Dallas Zoo" },
      { id: "childrens-aquarium-dallas", emoji: "🦈", name: "Children’s Aquarium" },
      { id: "childrens-museum-perot", emoji: "🎨", name: "Children’s Museum" },
    ];
    const intlCards = [
      { id: "london-zoo", emoji: "🦁", name: "London Zoo" },
      { id: "singapore-zoo", emoji: "🦍", name: "Singapore Zoo" },
      { id: "ueno-zoo", emoji: "🐯", name: "Ueno Zoo" },
    ];
    const cards = isIntl ? intlCards : usCards;
    heading.textContent = isIntl ? "Or try a world favorite" : "Or try Dallas";
    grid.innerHTML = cards
      .map(
        (c) => `<a class="ready-card" href="/field-pack/#/venue/${c.id}" data-venue-id="${c.id}">
            <span class="rc-emoji" aria-hidden="true">${c.emoji}</span>
            <h3>${c.name}</h3>
            <span class="rc-cta">Open on map →</span>
          </a>`
      )
      .join("");
  }

  boot();
})();
