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
    });
    if (nameEl) nameEl.textContent = pin.getAttribute("data-name") || "";
    if (cityEl) cityEl.textContent = pin.getAttribute("data-city") || "";
    if (printEl) printEl.setAttribute("href", pin.getAttribute("data-print") || "#");
    if (pageEl) pageEl.setAttribute("href", pin.getAttribute("data-page") || "#");
    card.hidden = false;
  }

  function closePin() {
    pins.forEach(function (pin) { pin.classList.remove("is-open"); });
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

  function positionPins(points) {
    if (!svgEl || !layer) return;
    var box = layer.getBoundingClientRect();
    var ctm = svgEl.getScreenCTM();
    if (!ctm || !box.width || !box.height) return;
    var used = [];
    points.forEach(function (item) {
      var sp = svgEl.createSVGPoint();
      sp.x = item.x;
      sp.y = item.y;
      var screen = sp.matrixTransform(ctm);
      var leftPx = screen.x - box.left;
      var topPx = screen.y - box.top;
      var n = 0;
      while (n < 6 && used.some(function (prev) {
        return Math.abs(prev.left - leftPx) < 22 && Math.abs(prev.top - topPx) < 22;
      })) {
        n += 1;
        leftPx += n % 2 ? 20 : -20;
        topPx += n > 2 ? 18 : 0;
      }
      used.push({ left: leftPx, top: topPx });
      item.pin.style.left = (leftPx / box.width) * 100 + "%";
      item.pin.style.top = (topPx / box.height) * 100 + "%";
      item.pin.classList.add("is-placed");
    });
    placed = true;
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
      var box = frame(points);
      svgEl.setAttribute("viewBox", box.x + " " + box.y + " " + box.w + " " + box.h);
      svgEl.setAttribute("preserveAspectRatio", "xMidYMid meet");
      svgEl.style.width = "100%";
      svgEl.style.height = "100%";
      requestAnimationFrame(function () {
        positionPins(points);
        var hash = "";
        try { hash = location.hash || ""; } catch (_) { hash = ""; }
        var wanted = (hash.match(/pin=([a-z0-9-]+)/) || [])[1];
        var opener = wanted && pins.filter(function (pin) {
          return pin.getAttribute("data-home-pin") === wanted;
        })[0];
        if (opener) openPin(opener);
      });
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

  setMode("places");
})();
