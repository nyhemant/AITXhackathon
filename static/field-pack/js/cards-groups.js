/* Cards hub "Browse by group": chips are plain anchors (work with JS off).
   With JS, open the panel that holds the group before the browser scrolls.
   Clicks are counted by /shell/related-links.js (link_type "group"). Added 2026-10-23. */
(function () {
  "use strict";
  function openFor(id) {
    var el = document.getElementById(id);
    if (!el) return;
    var d = el.closest ? el.closest("details") : null;
    if (d && !d.open) d.open = true;
    var q = document.getElementById("cards-hub-search");
    if (q && q.value) { q.value = ""; q.dispatchEvent(new Event("input")); }
  }
  document.querySelectorAll("a.cards-group-chip").forEach(function (a) {
    a.addEventListener("click", function () {
      var h = (a.getAttribute("href") || "").split("#")[1];
      if (h) openFor(h);
    });
  });
  var hash = (location.hash || "").replace(/^#/, "");
  if (/^g-/.test(hash)) {
    openFor(hash);
    var t = document.getElementById(hash);
    if (t && t.scrollIntoView) setTimeout(function () { t.scrollIntoView(); }, 0);
  }
})();
