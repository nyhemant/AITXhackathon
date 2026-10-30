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

  // —— Google Analytics 4 (KidZooKit Field Trip Kit / start / about) ——
  // KidZooKit property G-XB8HKLF4XY; historical 1Less was G-X6V6PNY9ZV.
  // Dinner (/dinner) is the old meal product — do not send it to this property.
  const GA4_MEASUREMENT_ID = "G-XB8HKLF4XY";
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
   *   Visit https://kidzookit.com/analytics/off
   *   or  ?analytics=off  /  ?no_ga=1  /  ?notrack=1  (saves localStorage;
   *       ?notrack=1 also gets the one_less_analytics=off cookie from the server)
   * Always skipped (not saved): navigator.webdriver, headless / automation /
   *   crawler user agents (see AUTOMATION_UA_RE).
   *   or  localStorage.setItem('1less_analytics_off','1')
   *
   * Opt back in:
   *   https://kidzookit.com/analytics/on
   *   or  ?analytics=on
   */
  function applyQueryAnalyticsToggle() {
    try {
      const q = new URLSearchParams(location.search);
      const v = (q.get("analytics") || q.get("ga") || "").toLowerCase();
      // ?notrack=1 is the opt-out our own check runners use. The server also sets
      // the one_less_analytics=off cookie on that response (same as /analytics/off).
      if (v === "off" || v === "0" || q.get("no_ga") === "1" || q.get("notrack") === "1") {
        window.__1LESS_ANALYTICS_OFF__ = true;
        if (q.get("notrack") === "1") {
          // Drop the flag from the address bar so a copied/shared link does not
          // opt someone else out. The opt-out itself is already saved.
          try {
            q.delete("notrack");
            const rest = q.toString();
            history.replaceState(history.state, "", location.pathname + (rest ? "?" + rest : "") + location.hash);
          } catch (_) {
            /* ignore */
          }
        }
        localStorage.setItem(LS_OFF_KEY, "1");
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

  function isDinnerPath() {
    try {
      const p = String(location.pathname || "");
      return p === "/dinner" || p.startsWith("/dinner/");
    } catch (_) {
      return false;
    }
  }

  // Headless browsers, automation and crawlers are not visitors. Not persisted:
  // this only skips the tag for that page load.
  const AUTOMATION_UA_RE =
    /HeadlessChrome|Headless|Lighthouse|PTST|GTmetrix|Pingdom|UptimeRobot|PhantomJS|Puppeteer|Playwright|Selenium|Cypress|python-requests|python-urllib|curl\/|Wget|KidZooKitCheck|kz-verify|Googlebot|Google-InspectionTool|GoogleOther|Storebot-Google|AdsBot-Google|Mediapartners-Google|APIs-Google|bingbot|BingPreview|msnbot|DuckDuckBot|YandexBot|Baiduspider|Applebot|facebookexternalhit|meta-externalagent|Twitterbot|Slackbot|Discordbot|LinkedInBot|Pinterestbot|AhrefsBot|SemrushBot|MJ12bot|DotBot|PetalBot|GPTBot|ChatGPT-User|OAI-SearchBot|ClaudeBot|Claude-User|PerplexityBot|CCBot|Bytespider|Amazonbot|\b(?:bot|crawler|spider)\b|[a-z]bot\/\d/i;

  function isAutomatedVisitor() {
    try {
      if (navigator.webdriver === true) return true;
      if (AUTOMATION_UA_RE.test(String(navigator.userAgent || ""))) return true;
    } catch (_) {
      /* ignore */
    }
    return false;
  }

  function analyticsDisabled() {
    if (window.__1LESS_ANALYTICS_OFF__ === true) return true;
    if (isDinnerPath()) return true;
    if (isLocalDevHost()) return true;
    if (isAutomatedVisitor()) return true;
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
   * Safe event helper used by Field Trip Kit / start / about.
   * No-ops when analytics is off, on Dinner paths, or gtag is not yet available.
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

  /** page_kind enum from the path only (no slugs, no query). */
  function pageKind() {
    const p = String(location.pathname || "");
    if (/^\/field-pack\/cards\/[^/]+\/?$/.test(p)) return "card";
    if (p === "/field-pack/" || /^\/field-pack\/(cards|zoos|aquariums|museums|national-parks)\/$/.test(p)) return "hub";
    if (p.indexOf("/field-pack/virtual-field-trip/") === 0) return "virtual_trip";
    if (/^\/field-pack\/[^/]+\/?$/.test(p)) return "place";
    if (p.indexOf("/printables/") === 0) return "printable";
    if (p.indexOf("/start/") === 0) return "start";
    return "other";
  }

  let lastPrintAt = 0;

  function sendPagePrint() {
    const now = Date.now();
    if (now - lastPrintAt < 5000) return;
    lastPrintAt = now;
    track("page_print", { page_kind: pageKind() });
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

    if (isDinnerPath()) {
      return;
    }

    if (analyticsDisabled()) {
      window.__1LESS_ANALYTICS_OFF__ = true;
      // Quiet signal for builders — only when explicitly opted out or local
      try {
        if (isLocalDevHost() || localStorage.getItem(LS_OFF_KEY) === "1") {
          console.info(
            "[KidZooKit GA4] off for this browser/host — production stats not counted. " +
              "Opt in: https://kidzookit.com/analytics/on or ?analytics=on"
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
      // Kids' site: no Google signals, no ad personalization. Event data stays
      // product analytics only (slugs / enums, no names, emails or free text).
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      // Required for GA4 Admin → DebugView (otherwise hits only appear in Realtime)
      debug_mode: debug,
    });

    if (debug) {
      console.info(
        "[KidZooKit GA4] debug_mode ON — hits still go to reports unless you use /analytics/off. ID:",
        GA4_MEASUREMENT_ID
      );
    }

    // Any print of a page (browser menu, Ctrl+P, or our Print buttons).
    window.addEventListener("beforeprint", sendPagePrint);

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
    isDinnerPath,
    isAutomatedVisitor,
  };
  // Back-compat for Dinner's trackEvent helper patterns
  window.trackEvent = track;

  initGa4();
})();
