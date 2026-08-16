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

  global.FPTrack = FPTrack;
  global.FPVenueType = venueTypeForAnalytics;
  global.FPTrackVenuePageView = trackVenuePageView;
})(typeof window !== "undefined" ? window : globalThis);
