/* Places mode reuses fpProjectWorld + world-map.svg from the Places page.
   Pins are circles inside that SVG, so the viewBox moves land and pins together.
   landing-map.js stays on /field-pack/: it needs that page's filter controls. */
(function () {
  "use strict";

  var TILE = "/field-pack/img/world-map.svg?v=2";
  var PLACES_JS = "/field-pack/js/places-data.js?v=27";
  /* Lower 48 plus southern Ontario, with room so a 44px target is not clipped. */
  var FRAME = { x: 136.78, y: 96.5, w: 194.5, h: 101.44 };
  var MIN_GAP = 46;
  /* Count plate is 20px across with 13px type, in the same SVG units as the land. */
  var BADGE = 20;
  var BADGE_TEXT = 13;
  var animalsBtn = document.getElementById("home-map-animals");
  var placesBtn = document.getElementById("home-map-places");
  var placesMap = document.getElementById("home-places-map");
  var animalMap = document.getElementById("start-hero");
  var host = document.getElementById("home-places-canvas");
  var layer = document.getElementById("home-pin-layer");
  var card = document.getElementById("home-pin-card");
  var listEl = document.getElementById("home-pin-list");
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
    if (places && placed) syncButtons();
  }

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function membersOf(pin) {
    try {
      return JSON.parse(pin.getAttribute("data-members") || "[]");
    } catch (_) {
      return [];
    }
  }

  function openPin(pin) {
    if (!pin || !card || !listEl) return;
    var members = membersOf(pin);
    pins.forEach(function (other) {
      other.classList.toggle("is-open", other === pin);
      if (other._dot) other._dot.setAttribute("fill", other === pin ? "#c9a227" : "#0a4545");
    });
    listEl.innerHTML = members.map(function (m) {
      return '<div class="home-pin-venue">' +
        '<p class="home-pin-name">' + esc(m.name) + '</p>' +
        '<p class="home-pin-city">' + esc(m.city) + '</p>' +
        '<a class="home-pin-print" data-kz-cta="home-map" href="' + esc(m.print) + '">Print the scavenger hunt</a>' +
        '<a class="home-pin-page" href="' + esc(m.page) + '">See the full page</a>' +
        '</div>';
    }).join("");
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

  function pxPerUser() {
    var rect = svgEl.getBoundingClientRect();
    if (!rect.width || !rect.height) return 0;
    return Math.min(rect.width / FRAME.w, rect.height / FRAME.h);
  }

  /* Push metro pins apart in SVG units until their 44px targets do not overlap. */
  function separate(items) {
    var scale = pxPerUser();
    if (!scale) return;
    items.forEach(function (item) {
      item.fx = item.x;
      item.fy = item.y;
    });
    var guard = 0;
    var moved = true;
    while (moved && guard < 40) {
      moved = false;
      guard += 1;
      for (var i = 0; i < items.length; i++) {
        for (var j = i + 1; j < items.length; j++) {
          var dx = (items[j].fx - items[i].fx) * scale;
          var dy = (items[j].fy - items[i].fy) * scale;
          var dist = Math.hypot(dx, dy);
          if (dist >= MIN_GAP) continue;
          var push = ((MIN_GAP - dist) / 2 + 0.4) / scale;
          var ux = dist ? dx / dist : 1;
          var uy = dist ? dy / dist : 0;
          items[i].fx -= ux * push;
          items[i].fy -= uy * push;
          items[j].fx += ux * push;
          items[j].fy += uy * push;
          moved = true;
        }
      }
    }
  }

  function drawDots(items) {
    var scale = pxPerUser() || 1;
    var r = 7 / scale;
    items.forEach(function (item) {
      var dot = document.createElementNS(NS, "circle");
      dot.setAttribute("cx", item.fx);
      dot.setAttribute("cy", item.fy);
      dot.setAttribute("r", r);
      dot.setAttribute("fill", "#0a4545");
      dot.setAttribute("stroke", "#fffcf7");
      dot.setAttribute("stroke-width", String(2 / scale));
      dot.setAttribute("class", "home-svg-pin");
      dot.setAttribute("pointer-events", "none");
      svgEl.appendChild(dot);
      item.pin._dot = dot;
      var count = membersOf(item.pin).length;
      if (count > 1) {
        var badge = document.createElementNS(NS, "g");
        badge.setAttribute("pointer-events", "none");
        var bx = item.fx + r * 0.85;
        var by = item.fy - r * 0.85;
        var plate = document.createElementNS(NS, "circle");
        plate.setAttribute("cx", bx);
        plate.setAttribute("cy", by);
        plate.setAttribute("r", (BADGE / 2) / scale);
        plate.setAttribute("fill", "#fffcf7");
        plate.setAttribute("stroke", "#0a4545");
        plate.setAttribute("stroke-width", String(1.5 / scale));
        var num = document.createElementNS(NS, "text");
        num.setAttribute("x", bx);
        num.setAttribute("y", by);
        num.setAttribute("text-anchor", "middle");
        num.setAttribute("dominant-baseline", "central");
        num.setAttribute("fill", "#0a4545");
        num.setAttribute("font-size", String(BADGE_TEXT / scale));
        num.setAttribute("font-family", "system-ui, sans-serif");
        num.setAttribute("font-weight", "700");
        num.textContent = String(count);
        badge.appendChild(plate);
        badge.appendChild(num);
        svgEl.appendChild(badge);
      }
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
      var items = [];
      pins.forEach(function (pin) {
        var members = membersOf(pin);
        var xs = [];
        var ys = [];
        members.forEach(function (m) {
          var place = byId[m.slug];
          if (!place) return;
          var pt = project(place);
          if (!pt) return;
          xs.push(pt.x);
          ys.push(pt.y);
        });
        if (!xs.length) return;
        var x = xs.reduce(function (a, b) { return a + b; }, 0) / xs.length;
        var y = ys.reduce(function (a, b) { return a + b; }, 0) / ys.length;
        items.push({ pin: pin, x: x, y: y });
      });
      if (!items.length) return;
      svgEl.setAttribute("viewBox", FRAME.x + " " + FRAME.y + " " + FRAME.w + " " + FRAME.h);
      svgEl.setAttribute("preserveAspectRatio", "xMidYMid meet");
      svgEl.style.width = "100%";
      svgEl.style.height = "100%";
      function finish(tries) {
        if (!pxPerUser()) {
          if (tries < 8) requestAnimationFrame(function () { finish(tries + 1); });
          return;
        }
        separate(items);
        drawDots(items);
        syncButtons();
        placed = true;
        var hash = "";
        try { hash = location.hash || ""; } catch (_) { hash = ""; }
        var wanted = (hash.match(/pin=([a-z0-9-]+)/) || [])[1];
        var opener = null;
        if (wanted) {
          opener = pins.filter(function (pin) {
            return membersOf(pin).some(function (m) { return m.slug === wanted; });
          })[0];
        }
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
  /* Escape closes an open card (focus goes back to its pin). On wider screens a click
     outside the card and the pins closes it too, so pins under the card stay reachable. */
  var WIDE = window.matchMedia ? window.matchMedia("(min-width: 721px)") : null;
  document.addEventListener("keydown", function (event) {
    if (!card || card.hidden) return;
    if (event.key !== "Escape" && event.key !== "Esc") return;
    var open = pins.filter(function (pin) { return pin.classList.contains("is-open"); })[0];
    closePin();
    if (open && typeof open.focus === "function") open.focus();
  });
  document.addEventListener("click", function (event) {
    if (!card || card.hidden || !WIDE || !WIDE.matches) return;
    var target = event.target;
    if (!target || !target.closest || !document.documentElement.contains(target)) return;
    if (card.contains(target) || target.closest(".home-place-pin")) return;
    closePin();
  });
  if (animalsBtn) animalsBtn.addEventListener("click", function () { setMode("animals"); });
  if (placesBtn) placesBtn.addEventListener("click", function () { setMode("places"); });
  window.addEventListener("resize", syncButtons);
  if (window.ResizeObserver && host) {
    new ResizeObserver(syncButtons).observe(host);
  }

  /* Phone: the Animals map opens on the Americas and pans sideways. The hint goes after the first drag. */
  var pan = document.getElementById("start-hero-pan");
  var hint = document.getElementById("start-pan-hint");
  if (pan && hint) {
    var onPan = function () {
      if (pan.scrollLeft < 8) return;
      hint.classList.add("is-gone");
      pan.removeEventListener("scroll", onPan);
    };
    pan.addEventListener("scroll", onPan, { passive: true });
  }

  setMode("places");
})();
