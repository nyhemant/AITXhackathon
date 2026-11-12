/* Places mode reuses fpProjectWorld + world-map.svg from the Places page.
   landing-map.js stays on /field-pack/: it needs that page's filter controls
   and draws the full catalog, not these 12 pins. */
(function () {
  "use strict";

  var TILE = "/field-pack/img/world-map.svg?v=2";
  var PLACES_JS = "/field-pack/js/places-data.js?v=27";
  var animalsBtn = document.getElementById("home-map-animals");
  var placesBtn = document.getElementById("home-map-places");
  var placesMap = document.getElementById("home-places-map");
  var animalMap = document.getElementById("start-hero");
  var host = document.getElementById("home-places-canvas");
  var layer = document.getElementById("home-pin-layer");
  var card = document.getElementById("home-pin-card");
  var nameEl = document.getElementById("home-pin-name");
  var cityEl = document.getElementById("home-pin-city");
  var printEl = document.getElementById("home-pin-print");
  var pageEl = document.getElementById("home-pin-page");
  var closeEl = document.getElementById("home-pin-close");
  var pins = Array.prototype.slice.call(document.querySelectorAll(".home-place-pin"));
  var svgEl = null;
  var placed = false;
  var NS = "http://www.w3.org/2000/svg";

  function setMode(mode) {
    var places = mode !== "animals";
    if (animalsBtn) animalsBtn.setAttribute("aria-pressed", places ? "false" : "true");
    if (placesBtn) placesBtn.setAttribute("aria-pressed", places ? "true" : "false");
    if (placesMap) placesMap.hidden = !places;
    if (animalMap) animalMap.hidden = places;
    if (places && !placed) drawPlaces();
  }

  function openPin(pin) {
    if (!pin || !card) return;
    pins.forEach(function (other) {
      other.classList.toggle("is-open", other === pin);
      if (other._dot) other._dot.setAttribute("fill", other === pin ? "#c9a227" : "#0a4545");
    });
    if (nameEl) nameEl.textContent = pin.getAttribute("data-name") || "";
    if (cityEl) cityEl.textContent = pin.getAttribute("data-city") || "";
    if (printEl) printEl.setAttribute("href", pin.getAttribute("data-print") || "#");
    if (pageEl) pageEl.setAttribute("href", pin.getAttribute("data-page") || "#");
    card.hidden = false;
  }

  function closePin() {
    pins.forEach(function (pin) {
      pin.classList.remove("is-open");
      if (pin._dot) pin._dot.setAttribute("fill", "#0a4545");
    });
    if (card) card.hidden = true;
  }

  function loadPlacesData() {
    if (window.FP_PLACES && typeof window.fpProjectWorld === "function") {
      return Promise.resolve();
    }
    return new Promise(function (resolve, reject) {
      var script = document.createElement("script");
      script.src = PLACES_JS;
      script.onload = function () { resolve(); };
      script.onerror = function () { reject(new Error("places")); };
      document.head.appendChild(script);
    });
  }

  function project(place) {
    var pt = window.fpProjectWorld(place.lat, place.lon, 1000, 500);
    if (!pt || !isFinite(pt.x) || !isFinite(pt.y)) return null;
    return pt;
  }

  function frame(points) {
    var minX = Infinity;
    var minY = Infinity;
    var maxX = -Infinity;
    var maxY = -Infinity;
    points.forEach(function (p) {
      if (p.x < minX) minX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.x > maxX) maxX = p.x;
      if (p.y > maxY) maxY = p.y;
    });
    var padX = Math.max(24, (maxX - minX) * 0.28);
    var padY = Math.max(16, (maxY - minY) * 0.55);
    return {
      x: Math.max(0, minX - padX),
      y: Math.max(0, minY - padY),
      w: Math.min(1000, maxX + padX) - Math.max(0, minX - padX),
      h: Math.min(500, maxY + padY) - Math.max(0, minY - padY)
    };
  }

  /* Screen scale from the viewBox and the SVG element's box.
     meet uses the smaller axis. This does not wait on a flushed CTM. */
  function userPerPx() {
    var vb = svgEl.viewBox && svgEl.viewBox.baseVal;
    var rect = svgEl.getBoundingClientRect();
    if (!vb || !vb.width || !vb.height || !rect.width || !rect.height) return 0;
    var scale = Math.min(rect.width / vb.width, rect.height / vb.height);
    return scale > 0 ? 1 / scale : 0;
  }

  /* Chicago, DC, and NYC each have two venues on one projected point.
     Keep the first on that point. Step the next ones one screen-gap
     inland or north/south, never a growing multiple of the gap. */
  function fan(points) {
    var unit = userPerPx();
    if (!unit) return points;
    var gap = 14 * unit;
    var placedPts = [];
    var vb = svgEl.viewBox.baseVal;
    points.forEach(function (item) {
      var inland = ((vb.x + vb.width / 2) - item.x) >= 0 ? 1 : -1;
      var tries = [
        [0, 0],
        [inland, 0],
        [0, -1],
        [0, 1],
        [inland, -1],
        [inland, 1]
      ];
      var x = item.x;
      var y = item.y;
      for (var i = 0; i < tries.length; i++) {
        var tx = item.x + tries[i][0] * gap;
        var ty = item.y + tries[i][1] * gap;
        var blocked = placedPts.some(function (prev) {
          return Math.hypot(prev.x - tx, prev.y - ty) < gap * 0.8;
        });
        if (!blocked) {
          x = tx;
          y = ty;
          break;
        }
      }
      placedPts.push({ x: x, y: y });
      item.fx = x;
      item.fy = y;
    });
    return points;
  }

  function drawDots(points) {
    var unit = userPerPx() || 1;
    var r = Math.max(2.2, 7 * unit);
    points.forEach(function (item) {
      var dot = document.createElementNS(NS, "circle");
      dot.setAttribute("cx", item.fx);
      dot.setAttribute("cy", item.fy);
      dot.setAttribute("r", r);
      dot.setAttribute("fill", "#0a4545");
      dot.setAttribute("stroke", "#fffcf7");
      dot.setAttribute("stroke-width", String(r * 0.28));
      dot.setAttribute("class", "home-svg-pin");
      dot.setAttribute("pointer-events", "none");
      svgEl.appendChild(dot);
      item.pin._dot = dot;
    });
  }

  function syncButtons() {
    if (!svgEl || !layer) return;
    var layerBox = layer.getBoundingClientRect();
    if (!layerBox.width || !layerBox.height) return;
    pins.forEach(function (pin) {
      var dot = pin._dot;
      if (!dot) return;
      var rect = dot.getBoundingClientRect();
      var cx = rect.left + rect.width / 2;
      var cy = rect.top + rect.height / 2;
      pin.style.left = ((cx - layerBox.left) / layerBox.width) * 100 + "%";
      pin.style.top = ((cy - layerBox.top) / layerBox.height) * 100 + "%";
      pin.classList.add("is-placed");
    });
  }

  function drawPlaces() {
    if (!host || placed) return;
    loadPlacesData().then(function () {
      return fetch(TILE).then(function (res) { return res.text(); });
    }).then(function (svgText) {
      host.innerHTML = svgText;
      svgEl = host.querySelector("svg");
      if (!svgEl || typeof window.fpProjectWorld !== "function") return;
      var byId = {};
      (window.FP_PLACES || []).forEach(function (place) { byId[place.id] = place; });
      var points = [];
      pins.forEach(function (pin) {
        var place = byId[pin.getAttribute("data-home-pin")];
        if (!place) return;
        var pt = project(place);
        if (!pt) return;
        points.push({ pin: pin, x: pt.x, y: pt.y });
      });
      if (!points.length) return;
      points.forEach(function (item) { item.fx = item.x; item.fy = item.y; });
      var box = frame(points);
      svgEl.setAttribute("viewBox", box.x + " " + box.y + " " + box.w + " " + box.h);
      svgEl.setAttribute("preserveAspectRatio", "xMidYMid meet");
      svgEl.style.width = "100%";
      svgEl.style.height = "100%";
      function finish(tries) {
        if (!userPerPx()) {
          if (tries < 8) requestAnimationFrame(function () { finish(tries + 1); });
          return;
        }
        fan(points);
        drawDots(points);
        syncButtons();
        placed = true;
        var hash = "";
        try { hash = location.hash || ""; } catch (_) { hash = ""; }
        var wanted = (hash.match(/pin=([a-z0-9-]+)/) || [])[1];
        var opener = wanted && pins.filter(function (pin) {
          return pin.getAttribute("data-home-pin") === wanted;
        })[0];
        if (opener) openPin(opener);
      }
      requestAnimationFrame(function () { finish(0); });
    }).catch(function () {
      if (host) host.innerHTML = '<p class="home-map-loading">Map unavailable. The place list is under the map.</p>';
    });
  }

  pins.forEach(function (pin) {
    pin.addEventListener("click", function () { openPin(pin); });
  });
  if (closeEl) closeEl.addEventListener("click", closePin);
  if (animalsBtn) animalsBtn.addEventListener("click", function () { setMode("animals"); });
  if (placesBtn) placesBtn.addEventListener("click", function () { setMode("places"); });
  window.addEventListener("resize", syncButtons);
  if (window.ResizeObserver && host) {
    new ResizeObserver(syncButtons).observe(host);
  }

  setMode("places");
})();
