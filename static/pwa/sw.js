/* Field Trip Kit PWA service worker.
 *
 * Cache name: bump FTK_SHELL_CACHE when the shell strategy or precache
 * list changes (e.g. ftk-shell-v1 → ftk-shell-v2). Parents then pick up
 * a fresh worker on the next visit.
 *
 * Update story
 * ------------
 * install: skipWaiting() so the new worker activates without waiting for
 *   every tab to close.
 * activate: delete older ftk-shell-* caches, then clientsClaim() so the
 *   next navigation uses this worker. We do not auto-reload open tabs —
 *   that would yank a parent off a live cam.
 * HTML shells (start + virtual-zoo + virtual-field-trip): network-first,
 *   last-good cache fallback. Online reopen gets fresh HTML.
 * Versioned CSS/JS (?v=) and /pwa/ icons: cache-first.
 * JSON card / venue data: network-first.
 * YouTube, Ant Media, GA, and local teaser mp4s: never intercepted.
 */
/* eslint-disable no-restricted-globals */
const FTK_SHELL_CACHE = "ftk-shell-v1";
const SHELL_PATHS = [
  "/start",
  "/field-pack/virtual-zoo",
  "/field-pack/virtual-field-trip",
];
const PRECACHE = [
  "/start/",
  "/manifest.webmanifest",
  "/pwa/icon-192.png",
  "/pwa/apple-touch-icon.png",
  "/pwa/register.js?v=1",
  "/start/start.css?v=31",
];

function sameOrigin(url) {
  try {
    return new URL(url, self.location.href).origin === self.location.origin;
  } catch (e) {
    return false;
  }
}

function pathnameOf(url) {
  try {
    return new URL(url, self.location.href).pathname;
  } catch (e) {
    return "";
  }
}

function barePath(pathname) {
  if (!pathname || pathname === "/") return "/";
  return pathname.replace(/\/+$/, "") || "/";
}

function isShellHtml(url) {
  return SHELL_PATHS.indexOf(barePath(pathnameOf(url))) !== -1;
}

function isVersionedStatic(url) {
  if (!sameOrigin(url)) return false;
  let parsed;
  try {
    parsed = new URL(url, self.location.href);
  } catch (e) {
    return false;
  }
  const path = parsed.pathname;
  const asset = /\.(css|js|png|ico|svg|webp|woff2?)$/i.test(path);
  if (!asset) return false;
  if (path.indexOf("/pwa/") === 0) return true;
  return parsed.search.indexOf("v=") !== -1;
}

function isJsonData(url) {
  if (!sameOrigin(url)) return false;
  const path = pathnameOf(url);
  return /\.json$/i.test(path) || path.indexOf("/field-pack/data/") === 0;
}

function shouldBypass(url) {
  let parsed;
  try {
    parsed = new URL(url, self.location.href);
  } catch (e) {
    return true;
  }
  const href = parsed.href;
  const path = parsed.pathname;
  if (/\.(mp4|webm|m3u8)$/i.test(path)) return true;
  if (path.indexOf("/start/teasers/") === 0) return true;
  if (/youtube|youtu\.be|googletagmanager|google-analytics|doubleclick|antmedia/i.test(href)) {
    return true;
  }
  return false;
}

async function networkFirst(request, fallbackUrls) {
  const cache = await caches.open(FTK_SHELL_CACHE);
  try {
    const fresh = await fetch(request);
    if (fresh && fresh.ok) {
      cache.put(request, fresh.clone());
    }
    return fresh;
  } catch (err) {
    const cached = await cache.match(request);
    if (cached) return cached;
    const extras = fallbackUrls || [];
    for (let i = 0; i < extras.length; i += 1) {
      const hit = await cache.match(extras[i]);
      if (hit) return hit;
    }
    throw err;
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(FTK_SHELL_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  const fresh = await fetch(request);
  if (fresh && fresh.ok) {
    cache.put(request, fresh.clone());
  }
  return fresh;
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(FTK_SHELL_CACHE)
      .then((cache) => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key.indexOf("ftk-shell-") === 0 && key !== FTK_SHELL_CACHE)
            .map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = request.url;
  if (shouldBypass(url)) return;
  if (!sameOrigin(url)) return;

  if (isShellHtml(url)) {
    const fallback = [pathnameOf(url), barePath(pathnameOf(url)) + "/"];
    event.respondWith(networkFirst(request, fallback));
    return;
  }
  if (isJsonData(url)) {
    event.respondWith(networkFirst(request));
    return;
  }
  if (isVersionedStatic(url)) {
    event.respondWith(cacheFirst(request));
  }
});
