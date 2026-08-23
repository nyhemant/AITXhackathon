(() => {
  const allPlaces = window.FP_PLACES || [];
  window.FP_READY_STRIP = {
    us: [
      "dallas-zoo",
      "childrens-aquarium-dallas",
      "childrens-museum-perot",
      "houston-zoo",
      "san-diego-zoo",
      "national-zoo",
    ],
    intl: ["london-zoo", "singapore-zoo", "ueno-zoo"],
  };
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
  let selectedTypeKind = "all"; // all | zoo | aquarium | museum
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
    // Type tab: All | Zoos | Aquariums | Museums
    if (selectedTypeKind && selectedTypeKind !== "all") {
      list = list.filter((p) => pinTypeKind(p.type) === selectedTypeKind);
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

  /** Map pin color family: zoo | aquarium | museum | park | other */
  function pinTypeKind(type) {
    const t = (type || "").toLowerCase();
    // Aquarium before zoo (handles "Science + aquarium")
    if (t.includes("aquarium")) return "aquarium";
    if (t.includes("zoo") || t.includes("safari")) return "zoo";
    // National park before generic "park" in museum names is rare; check park first
    if (
      t.includes("national park") ||
      t === "national_park" ||
      t === "park" ||
      t.includes("national_park")
    ) {
      return "park";
    }
    if (
      t.includes("museum") ||
      t.includes("science") ||
      t.includes("natural") ||
      t.includes("history") ||
      t.includes("space") ||
      t.includes("children") ||
      t.includes("air")
    ) {
      return "museum";
    }
    return "other";
  }

  function clusterPinKind(places) {
    if (!places || !places.length) return "other";
    const kinds = places.map((p) => pinTypeKind(p.type));
    const first = kinds[0];
    if (kinds.every((k) => k === first)) return first;
    return "mixed";
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
      // Quiet status only — no “tap a pin / pick from lists” coaching
      if (mapScope === "intl") {
        if (selectedCountry) {
          const name = (list[0] && list[0].countryName) || selectedCountry;
          mapCount.textContent = `${list.length} in ${name}`;
        } else {
          mapCount.textContent = `${list.length} worldwide`;
        }
      } else if (selectedState) {
        mapCount.textContent = `${list.length} in ${selectedState}`;
      } else if (selectedMetroId && selectedMetroId !== "all") {
        const m = METRO_DEFS.find((x) => x.id === selectedMetroId);
        const label = (m && m.label) || "this area";
        mapCount.textContent = `${list.length} in ${label}`;
      } else if (mapScope === "top") {
        mapCount.textContent = `${list.length} popular US places`;
      } else {
        mapCount.textContent = `${list.length} US places`;
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

  /** Keep pin screen size constant while the basemap SVG scales with zoom. */
  function applyPinCounterScale() {
    if (!pinsLayer) return;
    const inv = 1 / (zoom || 1);
    pinsLayer.querySelectorAll(".venue-pin").forEach((g) => {
      const x = g.dataset.x;
      const y = g.dataset.y;
      if (x == null || y == null) return;
      g.setAttribute("transform", `translate(${x},${y}) scale(${inv})`);
    });
  }

  function applyMapTransform() {
    if (!svgEl) return;
    clampPan();
    svgEl.style.transformOrigin = "center center";
    svgEl.style.transform = `translate(${panX}px, ${panY}px) scale(${zoom})`;
    applyPinCounterScale();
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

  /** Center map on SVG point (pin coords), optional target zoom. Returns false if skipped. */
  function panToSvgPoint(pt, targetZoom) {
    if (!pt || !svgEl || !mapViewport) return false;
    const z = clampZoom(
      targetZoom != null ? targetZoom : Math.max(zoom, basemap === "world" ? 2.0 : 1.7)
    );
    const baseW = svgEl.offsetWidth || mapViewport.clientWidth;
    const baseH = svgEl.offsetHeight || mapViewport.clientHeight;
    if (!baseW || !baseH) return false;
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
    return true;
  }

  /** Center map on a place (svg coords → pan), optional target zoom. Does not filter. */
  function panToPlace(p, targetZoom) {
    if (!p || !svgEl || !mapViewport) return false;
    const pt = pinXY(p);
    if (!pt) return false;
    return panToSvgPoint(pt, targetZoom);
  }

  /**
   * Pan/zoom to a metro’s pins. Uses centroid when several places share a city.
   * Skips zoom entirely if projection fails (better than a bad center zoom).
   */
  function panToPlacesCluster(places, targetZoom) {
    if (!places || !places.length) return false;
    const pts = places.map((p) => pinXY(p)).filter(Boolean);
    if (!pts.length) return false;
    const cx = pts.reduce((s, p) => s + p.x, 0) / pts.length;
    const cy = pts.reduce((s, p) => s + p.y, 0) / pts.length;
    // Slightly higher zoom for tight city clusters
    const z =
      targetZoom != null
        ? targetZoom
        : basemap === "world"
          ? 2.2
          : pts.length <= 2
            ? 2.4
            : 2.1;
    return panToSvgPoint({ x: cx, y: cy }, z);
  }

  // City chips (landing-hook) call this after selecting a metro/intl city
  window.fpFocusMapOnPlaces = function fpFocusMapOnPlaces(ids, opts) {
    const idSet = new Set((ids || []).filter(Boolean));
    const list = places.filter((p) => idSet.has(p.id));
    const z = opts && opts.zoom != null ? opts.zoom : undefined;
    if (!list.length) return false;
    // Wait a frame so basemap / pin layer are ready after scope swap
    requestAnimationFrame(() => {
      renderPins();
      if (!panToPlacesCluster(list, z)) {
        // Projection failed — leave zoom alone rather than a useless center zoom
      }
    });
    return true;
  };

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

      const pinKind = n > 1 ? clusterPinKind(cl.places) : pinTypeKind(cl.places[0].type);
      const g = document.createElementNS(NS, "g");
      g.setAttribute(
        "class",
        "venue-pin pin-type-" +
          pinKind +
          (selectedHere ? " selected" : "") +
          (n > 1 ? " is-cluster" : "")
      );
      g.setAttribute("tabindex", "0");
      g.setAttribute("role", "button");
      g.setAttribute(
        "aria-label",
        n > 1
          ? `${n} places near ${cl.places[0].city || "here"}`
          : `${cl.places[0].name} (${kidTypeLabel(cl.places[0].type)})`
      );
      g.dataset.clusterIds = cl.ids.join(",");
      // Local origin at pin; counter-scale so dots stay constant screen size when map zooms
      g.dataset.x = String(x);
      g.dataset.y = String(y);
      const inv = 1 / (zoom || 1);
      g.setAttribute("transform", `translate(${x},${y}) scale(${inv})`);
      g.style.cursor = "pointer";

      const halo = document.createElementNS(NS, "circle");
      halo.setAttribute("class", "vpin-halo");
      halo.setAttribute("cx", "0");
      halo.setAttribute("cy", "0");
      halo.setAttribute("r", n > 1 ? "18" : mapScope === "more" ? "12" : "16");
      g.appendChild(halo);

      const core = document.createElementNS(NS, "circle");
      core.setAttribute("class", "vpin-core");
      core.setAttribute("cx", "0");
      core.setAttribute("cy", "0");
      core.setAttribute("r", n > 1 ? "11" : selectedHere ? "8" : mapScope === "more" ? "5" : "7");
      g.appendChild(core);

      if (n > 1) {
        const count = document.createElementNS(NS, "text");
        count.setAttribute("class", "vpin-count");
        count.setAttribute("x", "0");
        count.setAttribute("y", "4");
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
      chip.setAttribute("transform", "translate(12, -10)");
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
        else goToPlacePage(cl.places[0].id);
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
    revealPinCard("pin-detail map-pin-card", `${places.length} places — pick one`);
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
        goToPlacePage(id);
      });
    });
  }

  function showOverview() {
    // Full-width map: no empty side panel. Place count is under the map (#map-count).
    detail.className = "pin-detail map-pin-card empty";
    detail.innerHTML = "";
    detail.hidden = true;
    detail.removeAttribute("aria-label");
  }

  function revealPinCard(className, ariaLabel) {
    detail.hidden = false;
    detail.className = className;
    if (ariaLabel) detail.setAttribute("aria-label", ariaLabel);
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

  function placePagePath(venueId) {
    const id = String(venueId || "").trim();
    if (!id || /[/?#\\]/.test(id) || id.includes("..")) return "";
    return `/field-pack/${encodeURIComponent(id)}/`;
  }

  /** Hub hashes that used to open a second venue panel. Place page is canonical. */
  function resolveHubVenueHash(hash) {
    const m = String(hash || "").match(/^#\/?venue\/([^/?#]+)/i);
    if (!m) return "";
    try {
      return placePagePath(decodeURIComponent(m[1]));
    } catch {
      return "";
    }
  }

  function goToPlacePage(venueId, opts) {
    const href = placePagePath(venueId);
    if (!href) return false;
    if (opts && opts.replace) location.replace(href);
    else location.assign(href);
    return true;
  }

  function syncVenueHash(venueId) {
    // Do not write #/venue/{id} on the hub — that hash now leaves for the place page.
    if (venueId) return;
    if (/^#\/?venue\//i.test(location.hash || "")) {
      history.replaceState(null, "", "#us-map");
    }
  }

  function venueIdFromHash() {
    const m = (location.hash || "").match(/^#\/?venue\/([^/?#]+)/i);
    return m ? decodeURIComponent(m[1]) : "";
  }

  window.fpPlacePagePath = placePagePath;
  window.fpResolveHubVenueHash = resolveHubVenueHash;

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
    revealPinCard("pin-detail map-pin-card pin-detail-rich", p.name || "Selected place");
    const blurb = (p.blurb || "").trim();
    const ven = catalogVenue(venueId);
    const canPrintHunt = Boolean(ven && (ven.treasureHunt || []).length);
    const sample = sampleItemForVenue(venueId);
    const samplePhoto = sample ? photoSrc(sample.photo) : "";
    const appHref = p.appHref || `/field-pack/app.html#/venue/${encodeURIComponent(venueId)}`;
    const missionHref = `/field-pack/${encodeURIComponent(venueId)}/#mission`;
    const isMissionPilot = MISSION_PILOTS.has(venueId);
    // Park (and any) hero illustration when present on disk
    const isPark =
      pinTypeKind(p.type) === "park" ||
      (ven && String(ven.type || "").toLowerCase().includes("national_park"));
    let heroSrc = "";
    if (isPark) {
      const heroPath = `/field-pack/photos/np-hero-${encodeURIComponent(venueId)}.jpg?v=q2`;
      heroSrc = heroPath;
    }

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
    // One primary CTA: mission page has age/time chips + print. No second “quick hunt”
    // (every place is a mission pilot) and no “ready to print” badge clutter.
    const primaryCta = isSoon
      ? ""
      : isMissionPilot
        ? `<a class="btn btn-primary pd-mission-cta" href="${missionHref}">
            <span class="pd-cta-main pd-cta-long">Create and print your mission</span>
            <span class="pd-cta-main pd-cta-short">Create/print mission</span>
          </a>`
        : canPrintHunt
          ? `<button type="button" class="btn btn-primary" id="pd-print-hunt">Print one-page hunt</button>`
          : "";
    const heroBlock = heroSrc
      ? `<div class="pd-park-hero">
          <img src="${escapeHtml(heroSrc)}" alt="${escapeHtml(p.name || "Park")} — illustrated day"
            width="640" height="360" loading="lazy" decoding="async"
            onerror="this.parentElement.hidden=true" />
        </div>`
      : "";
    detail.innerHTML = `
      <p class="pin-detail-kicker">${escapeHtml(locLine)}</p>
      <div class="pd-title-row">
        <h3>${
          isSoon
            ? `${escapeHtml(p.emoji || "")} ${escapeHtml(p.name)}`
            : `<a class="pd-title-link" href="${appHref}">${escapeHtml(p.emoji || "")} ${escapeHtml(p.name)}</a>`
        }</h3>
        <button type="button" class="pd-clear" id="pd-clear-selection" aria-label="Clear selection">×</button>
      </div>
      ${heroBlock}
      ${isSoon ? `<span class="pd-status soon">Coming soon</span>` : ""}
      ${blurb ? `<p class="pd-blurb">${escapeHtml(blurb)}</p>` : ""}
      ${
        isSoon
          ? `<p class="pd-hint">Pack in progress — shortlist and printable hunt coming next.</p>`
          : ""
      }
      ${primaryCta ? `<div class="pd-actions">${primaryCta}</div>` : ""}
      ${isSoon ? "" : sampleCard}
      ${
        isSoon
          ? ""
          : `<div class="pd-actions pd-actions-secondary">
        <a class="btn btn-soft pd-details-btn" href="${appHref}">Details</a>
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
    const stayOnMap = opts.stayOnMap === true;
    if (!venueId) {
      selectedVenueId = "";
      clusterFocusIds = [];
      fillVenueSelect();
      renderPins();
      showOverview();
      if (!skipHash) syncVenueHash("");
      return;
    }
    // Pin, dropdown, and hash: leave the hub for the SEO place page.
    // stayOnMap is only for city-chip focus (not a second venue page).
    if (!stayOnMap && goToPlacePage(venueId)) return;
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
    // Mid-browse map focus: pin chip only — not a second full venue page.
    showOverview();
    renderPins();
    // Frame the place without hiding siblings
    if (p && opts.fromPin !== false) {
      const wantZ =
        basemap === "world" ? Math.max(zoom, basemapSwitched ? 2.1 : 1.8) : Math.max(zoom, 1.6);
      panToPlace(p, wantZ);
    }
    if (!skipHash) syncVenueHash(venueId);
    if (opts.scroll !== false) {
      (document.getElementById("during") || document.getElementById("us-map"))?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  // City-chip fallback: focus the pin. Venue clicks use goToPlacePage.
  window.fpSelectVenueOnMap = (id) => {
    void setVenue(id, { stayOnMap: true, skipHash: true });
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
      const shell = mapHost.closest(".map-canvas-wrap") || document.getElementById("during");
      if (shell) shell.classList.add("map-js-ready");
      const fallback = document.getElementById("map-fallback");
      if (fallback) fallback.hidden = true;
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
      const popular = (window.FP_READY_STRIP && window.FP_READY_STRIP.us) || [];
      const chips = popular
        .map((id) => {
          const p = placeById(id) || {};
          const name = p.name || id;
          return `<li><a href="/field-pack/${id}/">${p.emoji || "📍"} ${name}</a></li>`;
        })
        .join("");
      mapHost.innerHTML = chips
        ? `<p class="map-fallback-lead">Map didn’t load. Explore a place:</p><ul class="map-fallback-list">${chips}</ul>`
        : `<p class="map-loading">Map unavailable — use the place list below.</p>`;
      const fallback = document.getElementById("map-fallback");
      if (fallback) fallback.hidden = false;
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
    // Deep link: /field-pack/#/venue/houston-zoo → /field-pack/houston-zoo/
    const fromHash = resolveHubVenueHash(location.hash);
    if (fromHash) {
      location.replace(fromHash);
      return;
    }
    window.addEventListener("hashchange", () => {
      const dest = resolveHubVenueHash(location.hash);
      if (dest) {
        location.replace(dest);
        return;
      }
      if (!venueIdFromHash() && selectedVenueId) {
        void setVenue("", { skipHash: true });
      }
    });

    const jsFallback = document.getElementById("map-fallback");
    if (jsFallback) jsFallback.hidden = true;
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
      if (selectedMetroId && selectedMetroId !== "all") {
        // Pan to metro pin cluster (not just zoom map center — that felt broken for US cities)
        const metroList = filteredPlaces();
        if (!panToPlacesCluster(metroList)) {
          /* keep current view if pins can’t be projected */
        }
      } else {
        setZoom(mapScope === "more" ? 1.15 : 1);
      }
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
    venueSelect.addEventListener("change", () => {
      const id = venueSelect.value;
      if (id) goToPlacePage(id);
      else void setVenue("");
    });

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

    // Type tabs: All | Zoos | Aquariums | Museums (filters map + directory)
    wirePlaceTypeTabs();
    bindCatalogPrintClicks();
  }

  /** Swap Ready strip for US vs international map scope. */
  function updateReadyChips(isIntl) {
    const heading = document.getElementById("ready-heading");
    const grid = document.getElementById("ready-grid");
    if (!heading || !grid) return;
    const spec = window.FP_READY_STRIP || { us: [], intl: [] };
    const ids = isIntl ? spec.intl : spec.us;
    const shortName = {
      "childrens-aquarium-dallas": "Children’s Aquarium",
      "childrens-museum-perot": "Children’s Museum",
      "national-zoo": "National Zoo",
    };
    heading.textContent = isIntl ? "Try a place" : "Explore a place at home";
    grid.innerHTML = ids
      .map((id) => {
        const p = placeById(id) || {};
        const emoji = p.emoji || "📍";
        const name = shortName[id] || p.name || id;
        return `<a class="ready-card" href="/field-pack/${id}/" data-venue-id="${id}">
            <span class="rc-emoji" aria-hidden="true">${emoji}</span>
            <h3>${name}</h3>
            <span class="rc-cta">Explore →</span>
          </a>`;
      })
      .join("");
  }

  boot();

  /** Place tab → paired card family (data-pairs-place / data-catalog). */
  const PLACE_CARD_PAIR = {
    zoo: "wildlife",
    aquarium: "sealife",
    museum: "attractions",
    park: null,
  };

  const TYPE_TAB_COPY = {
    all: {
      pitch: "Explore a place at home — or print a hunt for the visit",
      dir: "Cards & places",
      blurb:
        "Tabs above filter the map and this catalog together. Each day type pairs places with matching cards (zoos↔wildlife, aquariums↔sea life, museums↔attractions).",
    },
    zoo: {
      pitch: "Explore a zoo at home — or print a hunt for the visit",
      dir: "Zoos · wildlife cards",
      blurb: "Map shows zoos. Catalog: wildlife cards + zoo places.",
    },
    aquarium: {
      pitch: "Explore an aquarium at home — or print a hunt for the visit",
      dir: "Aquariums · sea life cards",
      blurb: "Map shows aquariums. Catalog: sea life cards + aquarium places.",
    },
    museum: {
      pitch: "Explore a museum at home — or print a hunt for the visit",
      dir: "Museums · attraction cards",
      blurb: "Map shows museums. Catalog: attraction cards + museum places.",
    },
    park: {
      pitch: "Explore a park at home — or print a hunt for the visit",
      dir: "Parks",
      blurb:
        "Map shows parks. One finishable slice (rim, boardwalk, lakeshore) — not the whole park.",
    },
  };

  function syncTypeTabs() {
    document.querySelectorAll(".place-type-tab[data-place-type]").forEach((btn) => {
      const on = btn.getAttribute("data-place-type") === selectedTypeKind;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    const copy = TYPE_TAB_COPY[selectedTypeKind] || TYPE_TAB_COPY.all;
    // Hero H1 stays outcome-led (do not overwrite #pitch-heading from type tabs)
    const dirH = document.getElementById("dir-heading");
    if (dirH) dirH.textContent = copy.dir;
    const dirP =
      document.getElementById("dir-blurb") ||
      document.querySelector("#all-places > p:not(#seo-dir-empty)");
    if (dirP) dirP.textContent = copy.blurb;
    document.body.setAttribute("data-place-type", selectedTypeKind || "all");
    filterDirectoryByType();
  }

  function filterDirectoryByType() {
    const root = document.getElementById("seo-venue-directory");
    if (!root) return;
    const byId = Object.fromEntries((allPlaces || []).map((p) => [p.id, p]));
    const filterKind =
      selectedTypeKind && selectedTypeKind !== "all" ? selectedTypeKind : null;
    // T5: map tabs no longer drive landing catalog (compact showcase)
    if (document.querySelector(".seo-dir-body-compact")) {
      return;
    }
    const pairCard = filterKind ? PLACE_CARD_PAIR[filterKind] : null;
    let visiblePlaces = 0;
    let visibleCards = 0;

    const placesRail = root.querySelector('#dir-places, [data-rail="places"]');
    const cardsRail = root.querySelector('#dir-printables, [data-rail="cards"]');

    // --- Places: show only matching day type ---
    const placeBlocks = root.querySelectorAll(
      ".seo-dir-type[data-place-type]:not([data-catalog])"
    );
    placeBlocks.forEach((block) => {
      const blockKind = block.getAttribute("data-place-type") || "";
      const blockMatch = !filterKind || blockKind === filterKind;
      let blockCount = 0;
      block.querySelectorAll(".seo-dir-region, .seo-dir-cat").forEach((region) => {
        let n = 0;
        region.querySelectorAll("li").forEach((li) => {
          const a = li.querySelector("a[href*='/field-pack/']");
          if (!a || a.hasAttribute("data-print-item")) return;
          const m = String(a.getAttribute("href") || "").match(
            /\/field-pack\/([^/#]+)\/?/
          );
          const id = m ? m[1] : "";
          if (!id || id === "app.html") return;
          const place = byId[id];
          const kind = place ? pinTypeKind(place.type) : blockKind || "other";
          const show = blockMatch && (!filterKind || kind === filterKind);
          li.hidden = !show;
          if (show) n += 1;
        });
        region.hidden = n === 0;
        const countEl = region.querySelector(
          ":scope > summary .seo-dir-count, :scope > .seo-dir-count"
        );
        if (countEl) countEl.textContent = String(n);
        blockCount += n;
      });
      block
        .querySelectorAll(":scope > .seo-dir-type-body > .seo-dir-samples li")
        .forEach((li) => {
          const a = li.querySelector("a[href*='/field-pack/']");
          if (!a || a.hasAttribute("data-print-item")) return;
          const m = String(a.getAttribute("href") || "").match(
            /\/field-pack\/([^/#]+)\/?/
          );
          const id = m ? m[1] : "";
          const place = byId[id];
          const kind = place ? pinTypeKind(place.type) : blockKind || "other";
          li.hidden = !(blockMatch && (!filterKind || kind === filterKind));
        });
      block.hidden = !blockMatch;
      if (blockMatch) {
        if (filterKind) block.open = true;
        visiblePlaces += 1;
      }
      const typeCount = block.querySelector(
        ":scope > summary .seo-dir-count, .seo-dir-type-sum .seo-dir-count"
      );
      if (typeCount && blockCount) typeCount.textContent = String(blockCount);
    });

    // --- Cards: pair with place type (wildlife↔zoo, sealife↔aquarium, attractions↔museum) ---
    const cardBlocks = root.querySelectorAll(".seo-dir-type[data-catalog]");
    cardBlocks.forEach((block) => {
      const catalog = block.getAttribute("data-catalog") || "";
      const pairs = block.getAttribute("data-pairs-place") || "";
      const show =
        !filterKind ||
        (pairCard && (catalog === pairCard || pairs === filterKind));
      block.hidden = !show;
      if (show) {
        visibleCards += 1;
        if (filterKind) block.open = true;
      }
    });

    if (placesRail) {
      placesRail.hidden = ![...placeBlocks].some((b) => !b.hidden);
    }
    if (cardsRail) {
      // Parks have no card family — hide cards rail
      if (filterKind === "park") cardsRail.hidden = true;
      else cardsRail.hidden = ![...cardBlocks].some((b) => !b.hidden);
    }

    const jumps = document.querySelector(".seo-dir-jumps");
    if (jumps) jumps.hidden = true; // unified top tabs only

    const empty = document.getElementById("seo-dir-empty");
    if (empty) {
      const any =
        (placesRail && !placesRail.hidden) || (cardsRail && !cardsRail.hidden);
      empty.hidden = !!any;
    }
  }

  /** Catalog Print buttons + card links (prevent full navigation when print works). */
  function bindCatalogPrintClicks() {
    const root = document.getElementById("seo-venue-directory");
    if (!root || root.dataset.printBound === "1") return;
    root.dataset.printBound = "1";
    root.addEventListener("click", (e) => {
      const t = e.target;
      if (!(t instanceof Element)) return;
      const btn = t.closest("[data-print-item]");
      if (!btn) return;
      // Only intercept Print buttons; plain card links navigate to app
      if (btn.tagName !== "BUTTON" && !btn.classList.contains("seo-dir-print-btn")) {
        return;
      }
      const itemId = btn.getAttribute("data-print-item");
      const venueId = btn.getAttribute("data-print-venue") || "";
      if (!itemId || !window.FPPrint || typeof window.FPPrint.printQaForItem !== "function") {
        return;
      }
      e.preventDefault();
      e.stopPropagation();
      window.FPPrint.printQaForItem(itemId, venueId || null);
    });
  }

  function setPlaceType(kind, opts) {
    const k = ["all", "zoo", "aquarium", "museum", "park"].includes(kind) ? kind : "all";
    selectedTypeKind = k;
    syncTypeTabs();
    // Refresh map pins + selectors for the type slice
    if (typeof fillLocationSelect === "function") fillLocationSelect();
    if (typeof fillVenueSelect === "function") fillVenueSelect();
    if (typeof renderPins === "function") renderPins();
    if (typeof showOverview === "function" && !selectedVenueId) showOverview();
    // Drop selection if it no longer matches the type filter
    if (selectedVenueId) {
      const p = placeById(selectedVenueId);
      if (p && k !== "all" && pinTypeKind(p.type) !== k) {
        if (typeof setVenue === "function") setVenue("", { skipHash: true });
      }
    }
    if (!opts || !opts.skipHash) {
      try {
        const url = new URL(location.href);
        if (k === "all") url.searchParams.delete("type");
        else url.searchParams.set("type", k);
        history.replaceState(null, "", url.pathname + url.search + url.hash);
      } catch (_) {
        /* ignore */
      }
    }
  }

  function wirePlaceTypeTabs() {
    const root = document.getElementById("place-type-tabs");
    if (!root) return;
    root.querySelectorAll(".place-type-tab[data-place-type]").forEach((btn) => {
      btn.addEventListener("click", (ev) => {
        // Left-click filters the map in place; middle-click / modified click keep href (SEO landings).
        if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || ev.button === 1) return;
        if (typeof ev.preventDefault === "function") ev.preventDefault();
        setPlaceType(btn.getAttribute("data-place-type") || "all");
      });
    });
    // Deep-link ?type=zoo|aquarium|museum|park
    try {
      const q = new URLSearchParams(location.search).get("type");
      if (q && ["zoo", "aquarium", "museum", "park", "all"].includes(q)) {
        selectedTypeKind = q;
      }
    } catch (_) {
      /* ignore */
    }
    syncTypeTabs();
  }

})();
