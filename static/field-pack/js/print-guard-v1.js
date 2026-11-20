/*
 * Print guard (K4). A quick double tap on a Print button used to open the
 * browser print dialog twice. This wraps window.print once per page load: a
 * second call within 2 seconds of the first is ignored, so one tap, or two
 * quick taps, give one dialog. Later prints (after the dialog closes) work as
 * before. Loaded before mission-ui.js on venue pages. No tracking, no storage.
 */
(function () {
  "use strict";
  if (window.__kzPrintGuard || typeof window.print !== "function") return;
  window.__kzPrintGuard = true;
  var original = window.print;
  var last = 0;
  var WINDOW_MS = 2000;
  window.print = function () {
    var now = Date.now();
    if (last && now - last < WINDOW_MS) return;
    last = now;
    return original.apply(window, arguments);
  };
})();
