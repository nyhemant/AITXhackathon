/* related_link_click: which kind of internal link was used (card, place, printable,
   hub, see_all, breadcrumb, start_trip). No URL, text or personal data is sent.
   Uses the shell's trackEvent, so it respects analytics-off. Added 2026-10-21. */
(function () {
  "use strict";
  document.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[data-related-link]") : null;
    if (!a) return;
    var type = a.getAttribute("data-related-link") || "other";
    try {
      if (typeof window.trackEvent === "function") window.trackEvent("related_link_click", { link_type: type });
    } catch (err) {}
  }, true);
})();
