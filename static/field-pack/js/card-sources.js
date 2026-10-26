/* Citable-card pilot (2026-10-26): fills today's date in the citation, copy button
 * with graceful fallback (iOS Safari: selects the text and says how to copy),
 * GA4 events via shell.js track (no-op when analytics is off):
 *   source_link_click {card, source}, cite_copy {card}
 */
(function () {
  "use strict";
  var box = document.querySelector(".card-sources[data-card]");
  if (!box) return;
  var card = box.getAttribute("data-card") || "";
  function track(name, params) {
    try {
      if (typeof window.trackEvent === "function") window.trackEvent(name, params || {});
    } catch (_) {}
  }
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  function today() {
    var d = new Date();
    return MONTHS[d.getMonth()] + " " + d.getDate() + ", " + d.getFullYear();
  }
  var dateEl = box.querySelector("[data-cite-date]");
  if (dateEl) dateEl.textContent = today();
  var textEl = box.querySelector("[data-cite-text]");
  var btn = box.querySelector("[data-cite-copy]");
  var status = box.querySelector(".card-cite-status");
  function say(msg) { if (status) status.textContent = msg; }
  function selectText() {
    try {
      var r = document.createRange();
      r.selectNodeContents(textEl);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(r);
    } catch (_) {}
  }
  function legacyCopy(text) {
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.top = "-1000px";
      document.body.appendChild(ta);
      ta.select();
      ta.setSelectionRange(0, text.length);
      var ok = document.execCommand && document.execCommand("copy");
      document.body.removeChild(ta);
      return !!ok;
    } catch (_) { return false; }
  }
  function fallback(text) {
    if (legacyCopy(text)) { say("Copied!"); track("cite_copy", { card: card }); return; }
    selectText();
    say("Text selected — press and hold (or Ctrl/Cmd+C) to copy.");
  }
  if (btn && textEl) {
    btn.hidden = false;
    btn.addEventListener("click", function () {
      if (dateEl) dateEl.textContent = today();
      var text = (textEl.textContent || "").replace(/\s+/g, " ").trim();
      if (navigator.clipboard && window.isSecureContext && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () {
          say("Copied!");
          track("cite_copy", { card: card });
        }, function () { fallback(text); });
      } else {
        fallback(text);
      }
    });
  }
  box.addEventListener("click", function (e) {
    var a = e.target && e.target.closest ? e.target.closest("a[data-cite-source]") : null;
    if (!a) return;
    track("source_link_click", { card: card, source: a.getAttribute("data-cite-source") || "" });
  });
})();
