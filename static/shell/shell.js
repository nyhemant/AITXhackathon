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

  /**
   * DebugView only shows hits with debug_mode.
   * Enable via:
   *   ?debug_mode=1  or  ?ga_debug=1
   *   localStorage.setItem('1less_ga_debug','1') then reload
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
   * Safe event helper used by product pages (Dinner, Baby's Day Out).
   * No-ops when analytics is off or gtag is not yet available.
   */
  function track(name, params) {
    if (window.__1LESS_ANALYTICS_OFF__) return;
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
    // Baby's Day Out uses history.replaceState for #/venue/... (no hashchange event)
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
    if (window.__1LESS_ANALYTICS_OFF__) return;
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
      // Visible signal in DevTools that DebugView mode is on
      console.info(
        "[1Less GA4] debug_mode ON — open GA4 Admin → DebugView. Measurement ID:",
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
  };
  // Back-compat for Dinner's trackEvent helper patterns
  window.trackEvent = track;

  initGa4();
})();
