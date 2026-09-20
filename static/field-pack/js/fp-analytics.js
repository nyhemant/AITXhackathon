/**
 * Field Trip Kit — shared analytics helper
 * ========================================
 * Use for all product events so later tasks add one-liners:
 *
 *   FPTrack("hero_search_used", { venue_slug: id, source: "hero" });
 *   FPTrack("mission_printed", { venue_slug, venue_type, age_band, time_length, style });
 *   FPTrack("card_opened", { card_id: id });
 *
 * Rules:
 * - No PII, no free-text kid names, no emails.
 * - Prefer enums/slugs: venue_type = zoo|aquarium|museum|park
 * - No-ops when analytics is off (localhost, opt-out cookie, etc.)
 * - Delegates to window.OneLessAnalytics.track (shell.js) when present.
 *
 * Debug: ?analytics=on&debug_mode=1 or localStorage 1less_ga_debug=1
 */
(function (global) {
  "use strict";

  var PRODUCT = "field_trip_kit";

  /**
   * Normalize venue type to analytics enum.
   * @param {string} raw
   * @returns {"zoo"|"aquarium"|"museum"|"park"|string}
   */
  function venueTypeForAnalytics(raw) {
    var vt = String(raw || "").toLowerCase();
    if (vt === "national_park" || vt === "park" || vt.indexOf("park") !== -1) return "park";
    if (vt.indexOf("aquarium") !== -1 || vt === "aq") return "aquarium";
    if (vt.indexOf("museum") !== -1 || vt === "sci" || vt === "nh") return "museum";
    if (vt.indexOf("zoo") !== -1 || vt.indexOf("safari") !== -1) return "zoo";
    return vt || "unknown";
  }

  /**
   * Emit a named event with optional properties (no PII).
   * @param {string} name
   * @param {object} [params]
   */
  function FPTrack(name, params) {
    if (!name) return;
    var payload = Object.assign({ product: PRODUCT }, params || {});
    // Strip accidental name-like free text keys if ever passed
    if (payload.kid_name != null) delete payload.kid_name;
    if (payload.child_name != null) delete payload.child_name;
    if (payload.name != null && payload.personalized == null) {
      // never send free-text display names as event props
      delete payload.name;
    }
    try {
      var fn =
        (global.OneLessAnalytics && global.OneLessAnalytics.track) ||
        global.trackEvent;
      if (typeof fn === "function") {
        fn(name, payload);
        return;
      }
      if (typeof global.gtag === "function") {
        global.gtag("event", name, payload);
        return;
      }
      if (global.__1LESS_ANALYTICS_OFF__ && global.console && console.debug) {
        console.debug("[FPTrack:off]", name, payload);
      }
    } catch (_) {
      /* ignore */
    }
  }

  /**
   * Venue SEO page pageview enrichment (shell already sends path-only page_view).
   * Call once on mission/venue pages with data attributes or venue JSON.
   */
  function trackVenuePageView(opts) {
    opts = opts || {};
    var slug = opts.venue_slug || opts.slug || "";
    var vtype = venueTypeForAnalytics(opts.venue_type || opts.type || "");
    if (!slug && !vtype) return;
    FPTrack("venue_page_viewed", {
      venue_slug: slug,
      venue_type: vtype,
    });
  }

  /**
   * Place-list accuracy two-tap (Accurate / Something changed).
   * Fires place_feedback with venue_slug + choice; Accurate needs no mail.
   * Note text is only used in optional mailto body — never sent to GA.
   */
  function bindPlaceFeedback(root) {
    root = root || document;
    var nodes = root.querySelectorAll("[data-place-feedback]");
    if (!nodes.length) return;

    function trackChoice(slug, choice) {
      FPTrack("place_feedback", {
        venue_slug: slug || "",
        choice: choice,
      });
    }

    function showThanks(wrap) {
      var actions = wrap.querySelector(".seo-freshness-actions");
      var thanks = wrap.querySelector(".seo-freshness-thanks");
      var note = wrap.querySelector(".seo-freshness-note-wrap");
      var prompt = wrap.querySelector(".seo-freshness-prompt");
      if (actions) actions.hidden = true;
      if (note) note.hidden = true;
      if (prompt) prompt.hidden = true;
      if (thanks) thanks.hidden = false;
    }

    nodes.forEach(function (wrap) {
      if (wrap.getAttribute("data-feedback-bound") === "1") return;
      wrap.setAttribute("data-feedback-bound", "1");
      var slug = wrap.getAttribute("data-place-id") || "";

      wrap.addEventListener("click", function (ev) {
        var t = ev.target;
        if (!t || !t.closest) return;
        var btn = t.closest("[data-feedback]");
        if (btn && wrap.contains(btn)) {
          var choice = btn.getAttribute("data-feedback");
          if (choice === "accurate") {
            trackChoice(slug, "accurate");
            showThanks(wrap);
            return;
          }
          if (choice === "changed") {
            trackChoice(slug, "changed");
            var actions = wrap.querySelector(".seo-freshness-actions");
            var note = wrap.querySelector(".seo-freshness-note-wrap");
            if (actions) actions.hidden = true;
            if (note) note.hidden = false;
            return;
          }
        }
        var done = t.closest("[data-feedback-done]");
        if (done && wrap.contains(done)) {
          showThanks(wrap);
          return;
        }
        var send = t.closest("[data-feedback-send]");
        if (send && wrap.contains(send)) {
          var changedBtn = wrap.querySelector('[data-feedback="changed"]');
          var mail = changedBtn && changedBtn.getAttribute("data-mailto");
          var ta = wrap.querySelector(".seo-freshness-note");
          var noteText = ta && ta.value ? String(ta.value).trim() : "";
          if (mail) {
            var href = mail;
            if (noteText) {
              href +=
                (href.indexOf("?") >= 0 ? "&" : "?") +
                "body=" +
                encodeURIComponent(noteText.slice(0, 280));
            }
            window.location.href = href;
          }
          showThanks(wrap);
        }
      });
    });
  }

  function onReady(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  onReady(function () {
    bindPlaceFeedback(document);
  });

  global.FPTrack = FPTrack;
  global.FPVenueType = venueTypeForAnalytics;
  global.FPTrackVenuePageView = trackVenuePageView;
  global.FPBindPlaceFeedback = bindPlaceFeedback;
})(typeof window !== "undefined" ? window : globalThis);
