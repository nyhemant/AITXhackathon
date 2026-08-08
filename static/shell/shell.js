(() => {
  // —— Site shell UI (More menu) ——
  function initShell(root) {
    const btn = root.querySelector(".shell-more");
    const menu = root.querySelector(".shell-menu");
    if (!btn || !menu) return;

    function close() {
      menu.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    }
    function open() {
      menu.hidden = false;
      btn.setAttribute("aria-expanded", "true");
    }
    function toggle() {
      if (menu.hidden) open();
      else close();
    }

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggle();
    });
    document.addEventListener("click", (e) => {
      if (!root.contains(e.target)) close();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
  }

  document.querySelectorAll(".oneless-shell").forEach(initShell);

  // —— Google Analytics 4 (site-wide: /field-pack + /dinner via shared shell) ——
  // Measurement ID from GA4 Admin → Data Streams → Web stream
  const GA4_MEASUREMENT_ID = "G-X6V6PNY9ZV";
  const LS_OFF_KEY = "1less_analytics_off";
  const COOKIE_NAME = "one_less_analytics";

  function readCookie(name) {
    try {
      const parts = String(document.cookie || "").split(";");
      for (const part of parts) {
        const i = part.indexOf("=");
        if (i < 0) continue;
        const k = part.slice(0, i).trim();
        if (k === name) return decodeURIComponent(part.slice(i + 1).trim());
      }
    } catch (_) {
      /* ignore */
    }
    return "";
  }

  function isLocalDevHost() {
    try {
      const h = String(location.hostname || "").toLowerCase();
      if (!h || h === "localhost" || h === "127.0.0.1" || h === "0.0.0.0" || h === "::1") {
        return true;
      }
      // Common private / preview hosts — do not count as production traffic
      if (h.endsWith(".local") || h.endsWith(".localhost")) return true;
      if (/^192\.168\.\d+\.\d+$/.test(h)) return true;
      if (/^10\.\d+\.\d+\.\d+$/.test(h)) return true;
      if (/^172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+$/.test(h)) return true;
      // file:// pages
      if (location.protocol === "file:") return true;
    } catch (_) {
      /* ignore */
    }
    return false;
  }

  /**
   * Exclude build / QA / own browsing from production stats.
   *
   * Opt out (persists in this browser):
   *   Visit https://1less.app/analytics/off
   *   or  ?analytics=off  /  ?no_ga=1  (saves localStorage)
   *   or  localStorage.setItem('1less_analytics_off','1')
   *
   * Opt back in:
   *   https://1less.app/analytics/on
   *   or  ?analytics=on
   */
  function applyQueryAnalyticsToggle() {
    try {
      const q = new URLSearchParams(location.search);
      const v = (q.get("analytics") || q.get("ga") || "").toLowerCase();
      if (v === "off" || v === "0" || q.get("no_ga") === "1") {
        localStorage.setItem(LS_OFF_KEY, "1");
        window.__1LESS_ANALYTICS_OFF__ = true;
        return "off";
      }
      if (v === "on" || v === "1") {
        localStorage.removeItem(LS_OFF_KEY);
        // Do not force on if cookie still says off — user must hit /analytics/on
        if (readCookie(COOKIE_NAME) !== "off") {
          window.__1LESS_ANALYTICS_OFF__ = false;
        }
        return "on";
      }
    } catch (_) {
      /* ignore */
    }
    return "";
  }

  function analyticsDisabled() {
    if (window.__1LESS_ANALYTICS_OFF__ === true) return true;
    if (isLocalDevHost()) return true;
    try {
      if (localStorage.getItem(LS_OFF_KEY) === "1") return true;
    } catch (_) {
      /* private mode */
    }
    if (readCookie(COOKIE_NAME) === "off") return true;
    return false;
  }

  /**
   * DebugView only shows hits with debug_mode.
   * Enable via:
   *   ?debug_mode=1  or  ?ga_debug=1
   *   localStorage.setItem('1less_ga_debug','1') then reload
   * Note: debug hits still count unless analytics is off — prefer /analytics/off while building.
   */
  function wantsDebugMode() {
    try {
      const q = new URLSearchParams(location.search);
      if (q.get("debug_mode") === "1" || q.get("ga_debug") === "1") return true;
      if (localStorage.getItem("1less_ga_debug") === "1") return true;
    } catch (_) {
      /* private mode / blocked storage */
    }
    return false;
  }

  /**
   * Safe event helper used by product pages (Dinner, Field Trip Kit).
   * No-ops when analytics is off or gtag is not yet available.
   */
  function track(name, params) {
    if (analyticsDisabled()) return;
    if (typeof window.gtag !== "function") return;
    const payload = Object.assign({}, params || {});
    if (wantsDebugMode() && payload.debug_mode == null) {
      payload.debug_mode = true;
    }
    window.gtag("event", name, payload);
  }

  function pagePath() {
    return location.pathname + location.search + location.hash;
  }

  let lastTrackedPath = null;

  function sendPageView() {
    if (analyticsDisabled()) return;
    const path = pagePath();
    // Dedupe when both hashchange and replaceState fire for the same URL
    if (path === lastTrackedPath) return;
    lastTrackedPath = path;
    track("page_view", {
      page_path: path,
      page_title: document.title,
      page_location: location.href,
    });
  }

  function loadGtagScript(id) {
    if (document.querySelector(`script[src*="googletagmanager.com/gtag/js"]`)) {
      return;
    }
    const s = document.createElement("script");
    s.async = true;
    s.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
    document.head.appendChild(s);
  }

  function patchHistoryForSpaPageViews() {
    // Field Trip Kit uses history.replaceState for #/venue/... (no hashchange event)
    ["pushState", "replaceState"].forEach((method) => {
      const original = history[method];
      if (typeof original !== "function") return;
      history[method] = function patchedHistory() {
        const ret = original.apply(this, arguments);
        queueMicrotask(sendPageView);
        return ret;
      };
    });
  }

  function initGa4() {
    applyQueryAnalyticsToggle();

    if (analyticsDisabled()) {
      window.__1LESS_ANALYTICS_OFF__ = true;
      // Quiet signal for builders — only when explicitly opted out or local
      try {
        if (isLocalDevHost() || localStorage.getItem(LS_OFF_KEY) === "1") {
          console.info(
            "[1Less GA4] off for this browser/host — production stats not counted. " +
              "Opt in: https://1less.app/analytics/on or ?analytics=on"
          );
        }
      } catch (_) {
        /* ignore */
      }
      return;
    }
    if (window.__1LESS_GA4_READY__) return;
    window.__1LESS_GA4_READY__ = true;

    window.dataLayer = window.dataLayer || [];
    if (typeof window.gtag !== "function") {
      window.gtag = function gtag() {
        window.dataLayer.push(arguments);
      };
    }

    loadGtagScript(GA4_MEASUREMENT_ID);

    const initialPath = pagePath();
    lastTrackedPath = initialPath;
    const debug = wantsDebugMode();

    window.gtag("js", new Date());
    window.gtag("config", GA4_MEASUREMENT_ID, {
      send_page_view: true,
      page_path: initialPath,
      page_title: document.title,
      // Required for GA4 Admin → DebugView (otherwise hits only appear in Realtime)
      debug_mode: debug,
    });

    if (debug) {
      console.info(
        "[1Less GA4] debug_mode ON — hits still go to reports unless you use /analytics/off. ID:",
        GA4_MEASUREMENT_ID
      );
    }

    // Hash / History SPA routes do not auto-fire page_view
    window.addEventListener("hashchange", sendPageView);
    window.addEventListener("popstate", sendPageView);
    patchHistoryForSpaPageViews();
  }

  window.OneLessAnalytics = {
    measurementId: GA4_MEASUREMENT_ID,
    track,
    pageView: sendPageView,
    wantsDebugMode,
    isDisabled: analyticsDisabled,
    isLocalDevHost,
  };
  // Back-compat for Dinner's trackEvent helper patterns
  window.trackEvent = track;

  initGa4();
})();
