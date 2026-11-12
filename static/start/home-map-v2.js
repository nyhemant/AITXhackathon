/* Home map v2: pins are already placed in the HTML (% of the plate), so this file only
   switches Places/Animals, opens the pin card, and handles the phone pan (start position + hint). */
(function () {
  "use strict";

  var animalsBtn = document.getElementById("home-map-animals");
  var placesBtn = document.getElementById("home-map-places");
  var placesMap = document.getElementById("home-places-map");
  var animalMap = document.getElementById("start-hero");
  var card = document.getElementById("home-pin-card");
  var listEl = document.getElementById("home-pin-list");
  var closeEl = document.getElementById("home-pin-close");
  var pins = Array.prototype.slice.call(document.querySelectorAll(".home-place-pin"));

  /* The USA plate is preloaded in <head> and drawn inline here, into a box that already has its
     final size, so the page never shifts. Pins and labels are HTML and show before it lands. */
  var base = document.querySelector("[data-kzm-svg]");
  if (base && window.fetch) {
    fetch(base.getAttribute("data-kzm-svg"), { credentials: "same-origin" }).then(function (res) {
      if (!res.ok) throw new Error("map");
      return res.text();
    }).then(function (text) {
      base.innerHTML = text;
      var svg = base.querySelector("svg");
      if (svg) {
        svg.removeAttribute("width");
        svg.removeAttribute("height");
        svg.setAttribute("preserveAspectRatio", "none");
        svg.setAttribute("aria-hidden", "true");
        svg.setAttribute("focusable", "false");
      }
      if (window.performance && performance.mark) performance.mark("kzm-usa-map-drawn");
    }).catch(function () { base.classList.add("is-failed"); });
  }

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function membersOf(pin) {
    try { return JSON.parse(pin.getAttribute("data-members") || "[]"); } catch (_) { return []; }
  }

    /* CSS snap already opened the pan box on its start point; release it so a drag glides. */
  function startPan(pan) {
    if (!pan || pan._started || !pan.clientWidth) return;
    pan._started = true;
    var keep = pan.scrollLeft;
    pan.classList.add("is-loose");
    pan.scrollLeft = keep;
  }

  function wireHint(pan, hint) {
    if (!pan || !hint) return;
    var from = null;
    var onPan = function () {
      if (from === null) { from = pan.scrollLeft; return; }
      if (Math.abs(pan.scrollLeft - from) < 8) return;
      hint.classList.add("is-gone");
      pan.removeEventListener("scroll", onPan);
    };
    pan.addEventListener("scroll", onPan, { passive: true });
    requestAnimationFrame(function () { from = pan.scrollLeft; });
  }

  function setMode(mode) {
    var places = mode !== "animals";
    if (animalsBtn) animalsBtn.setAttribute("aria-pressed", places ? "false" : "true");
    if (placesBtn) placesBtn.setAttribute("aria-pressed", places ? "true" : "false");
    if (placesMap) placesMap.hidden = !places;
    if (animalMap) animalMap.hidden = places;
    if (!places) closePin();
    startPan(document.getElementById(places ? "kzm-usa-pan" : "start-hero-pan"));
  }

  function openPin(pin) {
    if (!pin || !card || !listEl) return;
    pins.forEach(function (other) { other.classList.toggle("is-open", other === pin); });
    listEl.innerHTML = membersOf(pin).map(function (m) {
      return '<div class="home-pin-venue">' +
        '<p class="home-pin-name">' + esc(m.name) + '</p>' +
        '<p class="home-pin-city">' + esc(m.city) + '</p>' +
        '<a class="home-pin-print" data-kz-cta="home-map" href="' + esc(m.print) + '">Print the scavenger hunt</a>' +
        '<a class="home-pin-page" href="' + esc(m.page) + '">See the full page</a>' +
        '</div>';
    }).join("");
    card.hidden = false;
    /* Phone: the card sits under the map, so bring its Print button on screen. */
    if (!WIDE || !WIDE.matches) {
      var r = card.getBoundingClientRect();
      if (r.bottom > window.innerHeight) {
        window.scrollBy({ top: Math.min(r.bottom - window.innerHeight + 12, r.top - 8), behavior: REDUCED ? "auto" : "smooth" });
      }
    }
  }

  function closePin() {
    pins.forEach(function (pin) { pin.classList.remove("is-open"); });
    if (card) card.hidden = true;
  }

  var WIDE = window.matchMedia ? window.matchMedia("(min-width: 1000px)") : null;
  var REDUCED = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)").matches : false;

  /* A sideways drag never opens a card: ignore a click that ends more than 10px from where it began. */
  var down = null;
  document.addEventListener("pointerdown", function (e) { down = { x: e.clientX, y: e.clientY }; }, { passive: true, capture: true });
  function wasDrag(e) {
    return down && (Math.abs(e.clientX - down.x) > 10 || Math.abs(e.clientY - down.y) > 10);
  }
  pins.forEach(function (pin) {
    pin.addEventListener("click", function (e) { if (wasDrag(e)) return; openPin(pin); });
  });
  Array.prototype.forEach.call(document.querySelectorAll(".kzm-animal"), function (a) {
    a.addEventListener("click", function (e) { if (wasDrag(e)) e.preventDefault(); });
  });
  if (closeEl) closeEl.addEventListener("click", closePin);
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

  wireHint(document.getElementById("kzm-usa-pan"), document.getElementById("kzm-usa-hint"));
  wireHint(document.getElementById("start-hero-pan"), document.getElementById("start-pan-hint"));

  var hash = "";
  try { hash = location.hash || ""; } catch (_) { hash = ""; }
  var wanted = (hash.match(/pin=([a-z0-9-]+)/) || [])[1];
  setMode("places");
  if (wanted) {
    var opener = pins.filter(function (pin) { return membersOf(pin).some(function (m) { return m.slug === wanted; }); })[0];
    if (opener) openPin(opener);
  }
})();
