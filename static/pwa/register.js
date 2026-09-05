/* Register the Field Trip Kit service worker. Quiet on purpose:
 * no Chrome install banner, no every-visit install sheet.
 * On iOS Safari only, a one-time footer tip explains Add to Home Screen.
 */
(() => {
  const IOS_TIP_KEY = "ftk-pwa-ios-tip-dismissed-v1";

  function canRegister() {
    return "serviceWorker" in navigator && window.isSecureContext !== false;
  }

  function registerWorker() {
    if (!canRegister()) return;
    const loc = window.location;
    const insecureLocal =
      loc.protocol === "http:" && loc.hostname !== "localhost" && loc.hostname !== "127.0.0.1";
    if (insecureLocal) return;
    navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch(() => {});
  }

  function isIosBrowser() {
    const ua = navigator.userAgent || "";
    const iPhone = /iPad|iPhone|iPod/.test(ua);
    const iPadOs = navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1;
    return iPhone || iPadOs;
  }

  function isStandalone() {
    if (window.navigator.standalone === true) return true;
    return window.matchMedia && window.matchMedia("(display-mode: standalone)").matches;
  }

  function dismissed() {
    try {
      return window.localStorage.getItem(IOS_TIP_KEY) === "1";
    } catch (e) {
      return true;
    }
  }

  function markDismissed() {
    try {
      window.localStorage.setItem(IOS_TIP_KEY, "1");
    } catch (e) {
      /* ignore quota / private mode */
    }
  }

  function showIosTip() {
    if (!isIosBrowser() || isStandalone() || dismissed()) return;
    const foot = document.querySelector(".start-foot");
    if (!foot) return;

    const row = document.createElement("p");
    row.className = "start-pwa-tip";
    row.setAttribute("data-pwa-ios-tip", "1");

    const text = document.createElement("span");
    text.textContent = "On iPhone: Share, then Add to Home Screen.";

    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "Got it";
    btn.addEventListener("click", () => {
      markDismissed();
      row.remove();
    });

    row.appendChild(text);
    row.appendChild(btn);
    foot.appendChild(row);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      registerWorker();
      showIosTip();
    });
  } else {
    registerWorker();
    showIosTip();
  }
})();
