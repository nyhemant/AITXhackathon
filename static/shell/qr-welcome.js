/* KidZooKit: QR-scan next step + printable download events.
 * - When a printed sheet's QR code opens a page (utm_source=printable&utm_medium=qr),
 *   show one small, dismissible strip with ONE next step for that sheet.
 *   Once per session per sheet; never again after it has been dismissed twice.
 * - Fires GA4 events (campaign / slug / paper only, no personal data):
 *   qr_welcome_shown, qr_welcome_click, printable_download.
 * Leaves the URL (and its UTM tags) untouched. Does not modify shell.js.
 */
(function () {
  "use strict";
  var NEXT = {
    "scavenger-hunt": ["Finished your Zoo & Park Scavenger Hunt?", "See what to try next", "/printables/scavenger-hunt/#next"],
    "animal-bingo": ["Finished your Animal Bingo sheet?", "Meet the animals behind your squares", "/printables/animal-bingo/#next"],
    "zoo-day-journal": ["Finished your Zoo Day Journal?", "Find the answer to your \u201cI wonder\u2026\u201d", "/printables/zoo-day-journal/#next"],
    "park-scavenger-hunt": ["Finished your Park & Backyard Hunt?", "Try the zoo scavenger hunt next", "/printables/scavenger-hunt/"],
    "carpool": ["Made it through the Carpool Adventure Sheet?", "Pick your zoo\u2019s hunt for when you arrive", "/field-pack/zoos/"],
    "teacher-handout": ["Using the Teacher Handout?", "Print the Zoo Day Journal for after the trip", "/printables/zoo-day-journal/"],
    "chaperone-card": ["Leading a group with the Chaperone Card?", "Give each child an Animal Bingo card", "/printables/animal-bingo/"]
  };
  var LS_DISMISS = "kzk_qr_welcome_dismissed";
  var SS_SEEN = "kzk_qr_welcome_seen_";

  function send(name, params) {
    params = params || {};
    params.transport_type = "beacon";
    try {
      if (typeof window.trackEvent === "function") { window.trackEvent(name, params); return; }
      if (window.__1LESS_ANALYTICS_OFF__ === true) return;
      if (typeof window.gtag === "function") window.gtag("event", name, params);
    } catch (_) { /* never break the page for analytics */ }
  }
  function lsGet(k) { try { return window.localStorage.getItem(k); } catch (_) { return null; } }
  function lsSet(k, v) { try { window.localStorage.setItem(k, v); } catch (_) { /* blocked */ } }
  function ssGet(k) { try { return window.sessionStorage.getItem(k); } catch (_) { return null; } }
  function ssSet(k, v) { try { window.sessionStorage.setItem(k, v); } catch (_) { /* blocked */ } }

  /* ---- printable_download {slug, paper} on PDF links ---- */
  document.addEventListener("click", function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest("a[href]") : null;
    if (!a) return;
    var path;
    try { path = new URL(a.getAttribute("href"), location.href).pathname; } catch (_) { return; }
    var m = path.match(/^\/printables\/pdf\/(?:(letter|a4)\/)?([a-z0-9-]+)\.pdf$/);
    if (!m) return;
    var paper = m[1] || "letter";
    var slug = m[2].replace(/-a4$/, "");
    send("printable_download", { slug: slug, paper: paper });
  }, true);

  /* ---- QR welcome strip ---- */
  function campaign() {
    var q;
    try { q = new URLSearchParams(location.search); } catch (_) { return null; }
    if (q.get("utm_medium") !== "qr" || q.get("utm_source") !== "printable") return null;
    var c = (q.get("utm_campaign") || "").toLowerCase();
    return Object.prototype.hasOwnProperty.call(NEXT, c) ? c : null;
  }

  function show() {
    var c = campaign();
    if (!c) return;
    if (location.pathname.indexOf("/printables/") === 0) return;
    if ((parseInt(lsGet(LS_DISMISS) || "0", 10) || 0) >= 2) return;
    if (ssGet(SS_SEEN + c)) return;
    if (document.getElementById("kzk-qr-welcome")) return;
    ssSet(SS_SEEN + c, "1");

    var n = NEXT[c];
    var css = document.createElement("style");
    css.textContent =
      "#kzk-qr-welcome{display:flex;align-items:center;gap:.4rem .9rem;flex-wrap:wrap;margin:.5rem auto .75rem;max-width:56rem;width:calc(100% - 2rem);" +
      "position:relative;padding:.5rem 3rem .5rem .9rem;border-radius:14px;background:#fff8e6;border:1.5px solid #f2c75c;color:#152238;" +
      "font:600 .92rem/1.35 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;box-shadow:0 2px 8px rgba(21,34,56,.06);box-sizing:border-box}" +
      "#kzk-qr-welcome .kqw-t{flex:1 1 14rem}#kzk-qr-welcome a.kqw-go{font-size:.92rem}" +
      "#kzk-qr-welcome a.kqw-go{display:inline-flex;align-items:center;min-height:44px;padding:0 .9rem;border-radius:999px;background:#0f5c5c;color:#fff;font-weight:800;text-decoration:none}" +
      "#kzk-qr-welcome a.kqw-go:hover,#kzk-qr-welcome a.kqw-go:focus{background:#0a4545}" +
      "#kzk-qr-welcome button.kqw-x{position:absolute;top:2px;right:2px;min-width:44px;min-height:44px;border:0;background:transparent;color:#3d4f6f;font-size:1.4rem;line-height:1;cursor:pointer;border-radius:10px}" +
      "#kzk-qr-welcome button.kqw-x:hover{background:rgba(15,92,92,.08)}" +
      "#kzk-qr-welcome a:focus-visible,#kzk-qr-welcome button:focus-visible{outline:3px solid #ffcf5a;outline-offset:2px}" +
      "@media print{#kzk-qr-welcome{display:none}}";
    document.head.appendChild(css);

    var bar = document.createElement("aside");
    bar.id = "kzk-qr-welcome";
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", "Next step for your printed sheet");
    var t = document.createElement("span");
    t.className = "kqw-t";
    t.textContent = n[0] + " Here\u2019s what to try next.";
    var go = document.createElement("a");
    go.className = "kqw-go";
    go.href = n[2];
    go.textContent = n[1] + " \u2192";
    go.addEventListener("click", function () { send("qr_welcome_click", { campaign: c }); });
    var x = document.createElement("button");
    x.type = "button";
    x.className = "kqw-x";
    x.setAttribute("aria-label", "Dismiss");
    x.textContent = "\u00d7";
    x.addEventListener("click", function () {
      var k = (parseInt(lsGet(LS_DISMISS) || "0", 10) || 0) + 1;
      lsSet(LS_DISMISS, String(k));
      if (bar.parentNode) bar.parentNode.removeChild(bar);
    });
    bar.appendChild(t);
    bar.appendChild(go);
    bar.appendChild(x);

    var header = document.querySelector("header.oneless-shell");
    if (header && header.parentNode) header.parentNode.insertBefore(bar, header.nextSibling);
    else document.body.insertBefore(bar, document.body.firstChild);
    send("qr_welcome_shown", { campaign: c });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", show);
  else show();
})();
