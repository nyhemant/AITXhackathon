/**
 * Virtual Field Trip engine — zoo / aquarium / museums / parks.
 * Tabs load a JSON + map SVG. Cams are link-out; films embed.
 * Zoo tab with no #habitat= deep link opens flamingo as the default stop.
 * Kid name is not collected.
 */
(() => {
  const root = document.querySelector("[data-virtual-venue]");
  if (!root) return;

  const TAB_ORDER = [
    { id: "zoo", label: "Zoo" },
    { id: "aquarium", label: "Aquarium" },
    { id: "museum", label: "Museum", tabs: ["natural-history", "science"], defaultTab: "natural-history" },
    { id: "parks", label: "Parks" },
  ];
  const MUSEUM_TABS = ["natural-history", "science"];
  const MUSEUM_CHIPS = [
    { id: "natural-history", label: "Natural history" },
    { id: "science", label: "Science" },
  ];
  const MUSEUM_LAST_KEY = "fp-vft-museum-tab";
  const TAB_CONFIGS = {
    zoo: "/field-pack/data/virtual-venues/virtual-zoo.json?v=26",
    aquarium: "/field-pack/data/virtual-venues/virtual-aquarium.json?v=26",
    "natural-history": "/field-pack/data/virtual-venues/virtual-nhm.json?v=15",
    science: "/field-pack/data/virtual-venues/virtual-science.json?v=17",
    parks: "/field-pack/data/virtual-venues/virtual-parks.json?v=24",
  };

  const mapMount = document.getElementById("vz-map");
  const stampList = document.getElementById("vz-stamps");
  const progressEl = document.getElementById("vz-progress");
  const stopsDrawer = document.getElementById("vz-stops-drawer");
  const pathPicker = document.getElementById("vz-zoo-picker");
  const PICK_BY_KIND = {
    zoo: {
      key: "fp-virtual-zoo-picks-v1",
      libUrl: "/field-pack/data/virtual-venues/zoo-film-library.json?v=7",
      title: "Create your own virtual zoo",
      noun: "zoo",
      track: "zoo_picks_saved",
    },
    aquarium: {
      key: "fp-virtual-aquarium-picks-v1",
      libUrl: "/field-pack/data/virtual-venues/aquarium-film-library.json?v=5",
      title: "Create your own virtual aquarium",
      noun: "aquarium",
      track: "aquarium_picks_saved",
    },
    science: {
      key: "fp-virtual-science-picks-v1",
      libUrl: "/field-pack/data/virtual-venues/science-film-library.json?v=3",
      title: "Create your own virtual science museum",
      noun: "science museum",
      track: "science_picks_saved",
    },
    park: {
      key: "fp-virtual-parks-picks-v1",
      libUrl: "/field-pack/data/virtual-venues/parks-map-library.json?v=2",
      title: "Make your own parks map",
      noun: "road trip",
      track: "parks_picks_saved",
      layout: "set",
    },
  };
  const pickLibs = {};
  const pickLibPromises = {};
  let pickBaseHabitats = null;
  let pickDraft = null;
  let pickHold = null;
  const dialog = document.getElementById("vz-dialog");
  const backdrop = document.getElementById("vz-backdrop");
  const sheet = document.getElementById("vz-sheet");
  const titleEl = document.getElementById("vz-dialog-title");
  const photoEl = document.getElementById("vz-photo");
  const blurbEl = document.getElementById("vz-blurb");
  const watchEl = document.getElementById("vz-watch");
  const camLink = document.getElementById("vz-cam");
  const filmLink = document.getElementById("vz-film");
  const filmHint = document.getElementById("vz-film-hint");
  const placeLink = document.getElementById("vz-place");
  const challengeEl = document.getElementById("vz-challenge");
  const closeBtn = document.getElementById("vz-close");
  const printCardBtn = document.getElementById("vz-print-card");
  const printWatch = document.getElementById("vz-print-watch");
  const passCount = document.getElementById("vz-pass-count");
  const camPop = document.getElementById("vz-cam-pop");
  const camPopTitle = document.getElementById("vz-cam-pop-title");
  const camPopNote = document.getElementById("vz-cam-pop-note");
  const camPopBack = document.getElementById("vz-cam-pop-back");
  const camFrame = document.getElementById("vz-cam-frame");
  let camWin = null;
  let currentPhotoSrc = "";

  let config = null;
  let stamps = [];
  let lastFocus = null;
  let openedIds = [];
  let currentCardId = "";
  let currentHabitatId = "";
  let currentPrint = { type: "qa", id: "" };
  let loadGen = 0;
  const DEFAULT_ZOO_STOP = "caribbean-flamingo";

  function setTourChrome() {
    document.documentElement.setAttribute("data-vft-chrome", "tour");
    root.classList.remove("is-vft-first-run");
  }

  function habitatHashId() {
    const m = (location.hash || "").match(/habitat=([^&]+)/);
    return m ? decodeURIComponent(m[1]) : "";
  }

  function queryHabitat() {
    try {
      return new URLSearchParams(location.search).get("habitat") || "";
    } catch (_) {
      return "";
    }
  }

  function cardFocusId() {
    return habitatHashId() || queryHabitat() || currentHabitatId || "";
  }

  function wantsCutoutPrint() {
    try {
      if (new URLSearchParams(location.search).get("print") === "1") return true;
    } catch (_) {}
    const hash = (location.hash || "").replace(/^#/, "");
    return hash === "print";
  }

  function revealPrintReady() {
    if (!wantsCutoutPrint()) return;
    const row = document.getElementById("print") || printWatch?.closest(".vz-print-row");
    if (!row) return;
    row.classList.add("is-print-ready");
    document.documentElement.setAttribute("data-vft-print", "1");
    setTourChrome();
    const go = () => {
      row.scrollIntoView({ block: "center", behavior: "smooth" });
      printWatch?.focus({ preventScroll: true });
    };
    if (typeof requestAnimationFrame === "function") requestAnimationFrame(go);
    else go();
  }

  function track(name, params) {
    if (typeof window.FPTrack === "function") window.FPTrack(name, params || {});
  }

  function currentTab() {
    const hash = (location.hash || "").replace(/^#/, "");
    if (hash && !hash.startsWith("habitat=") && TAB_CONFIGS[hash]) return hash;
    const q = new URLSearchParams(location.search).get("tab");
    if (q && TAB_CONFIGS[q]) return q;
    const def = root.getAttribute("data-default-tab") || "zoo";
    return TAB_CONFIGS[def] ? def : "zoo";
  }

  function fromCard() {
    try {
      return new URLSearchParams(location.search).get("from") === "card";
    } catch (_) {
      return false;
    }
  }

  function cardReturnVenue() {
    try {
      return new URLSearchParams(location.search).get("return") || "";
    } catch (_) {
      return "";
    }
  }

  function tabUrl(id, habitat) {
    const q = new URLSearchParams();
    q.set("tab", id);
    if (fromCard()) q.set("from", "card");
    const ret = cardReturnVenue();
    if (ret) q.set("return", ret);
    const hid = habitat === "" ? "" : habitat || (fromCard() ? cardFocusId() : "");
    if (fromCard() && hid) q.set("habitat", hid);
    const hash = hid ? "#habitat=" + encodeURIComponent(hid) : "#" + id;
    return location.pathname + "?" + q.toString() + hash;
  }

  function nextAfter(id) {
    const list = fullWalkList();
    const i = list.findIndex((h) => h.id === id);
    if (i < 0 || list.length < 2) return null;
    return list[(i + 1) % list.length];
  }

  function cardHrefFor(h) {
    const cid = (h && (h.cardId || h.id)) || currentCardId;
    if (!cid) return "/field-pack/cards/";
    const ret = cardReturnVenue();
    return "/field-pack/cards/" + encodeURIComponent(cid) + "/" + (ret ? "?from=" + encodeURIComponent(ret) : "");
  }

  function syncCardNav(h) {
    const nav = document.getElementById("vz-card-nav");
    const back = document.getElementById("vz-back-card");
    const nextBtn = document.getElementById("vz-next-stop");
    if (!nav) return;
    if (!fromCard()) {
      nav.hidden = true;
      return;
    }
    nav.hidden = false;
    if (back) {
      back.href = cardHrefFor(h);
      back.textContent = "Back to card";
    }
    const nxt = h ? nextAfter(h.id) : null;
    if (nextBtn) {
      nextBtn.hidden = !nxt;
      if (nxt) nextBtn.textContent = "Next";
    }
  }

  function isMuseumTab(id) {
    return MUSEUM_TABS.indexOf(id) !== -1;
  }

  function lastMuseumTab() {
    try {
      const last = sessionStorage.getItem(MUSEUM_LAST_KEY);
      if (isMuseumTab(last)) return last;
    } catch (_) {}
    return "natural-history";
  }

  function rememberMuseumTab(id) {
    if (!isMuseumTab(id)) return;
    try {
      sessionStorage.setItem(MUSEUM_LAST_KEY, id);
    } catch (_) {}
  }

  function resolveVenueTab(id) {
    if (id === "museum") return lastMuseumTab();
    return id;
  }

  function showPanels(tab) {
    document.querySelectorAll("[data-vz-panel]").forEach((p) => {
      p.hidden = p.getAttribute("data-vz-panel") !== tab;
    });
  }

  function configUrlFor(tab) {
    return TAB_CONFIGS[tab] || TAB_CONFIGS.zoo;
  }

  function loadStamps(key) {
    try {
      const raw = JSON.parse(localStorage.getItem(key) || "[]");
      return Array.isArray(raw) ? raw.filter((x) => typeof x === "string") : [];
    } catch (_) {
      return [];
    }
  }

  function saveStamps(key, ids) {
    try {
      localStorage.setItem(key, JSON.stringify(ids));
    } catch (_) {}
  }

  function fullWalkList() {
    return [...((config && config.habitats) || [])].sort((a, b) => (a.seq || 0) - (b.seq || 0));
  }

  function walkList() {
    const all = fullWalkList();
    if (!fromCard()) return all;
    const focus = cardFocusId();
    if (!focus) return all;
    const one = all.find((h) => h.id === focus);
    return one ? [one] : all;
  }

  function catalogItem(id) {
    return (
      (typeof window.fpGetAnimal === "function" && window.fpGetAnimal(id)) ||
      (window.FIELD_PACK_CATALOG && window.FIELD_PACK_CATALOG[id]) ||
      null
    );
  }

  function cardPhotoSrc(cardId) {
    const item = catalogItem(cardId);
    if (!item) return "";
    if (window.FPPrint && window.FPPrint.itemPhotoSrc) return window.FPPrint.itemPhotoSrc(item);
    const p = item.photo || "";
    if (!p) return "";
    if (/^https?:\/\//i.test(p) || p.charAt(0) === "/") return p;
    if (p.indexOf("photos/") === 0) return "/field-pack/" + p;
    return "/field-pack/photos/" + p.replace(/^\/+/, "");
  }

  function pickSpec(kind) {
    return PICK_BY_KIND[kind || (config && config.kind)] || null;
  }

  function pickLibrary(kind) {
    const spec = pickSpec(kind);
    return spec ? pickLibs[spec.key] || null : null;
  }

  function ensurePickLibrary(kind) {
    const spec = pickSpec(kind);
    if (!spec) return Promise.resolve(null);
    if (pickLibs[spec.key]) return Promise.resolve(pickLibs[spec.key]);
    if (pickLibPromises[spec.key]) return pickLibPromises[spec.key];
    pickLibPromises[spec.key] = fetch(spec.libUrl)
      .then((r) => {
        if (!r.ok) throw new Error("pick library " + r.status);
        return r.json();
      })
      .then((data) => {
        pickLibs[spec.key] = data;
        return data;
      })
      .catch((err) => {
        delete pickLibPromises[spec.key];
        console.warn("[virtual-venue] pick library", err);
        return null;
      });
    return pickLibPromises[spec.key];
  }

  function pickDefaultIds(lib) {
    return (lib.cards || [])
      .filter((c) => c.defaultTour)
      .sort((a, b) => (a.seq || 0) - (b.seq || 0))
      .map((c) => c.cardId);
  }

  function loadPicks(spec) {
    if (!spec) return null;
    try {
      const raw = localStorage.getItem(spec.key);
      if (raw == null) return null;
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return null;
      return parsed.map((x) => (typeof x === "string" && x ? x : ""));
    } catch (_) {
      return null;
    }
  }

  function savePicks(spec, ids) {
    if (!spec) return;
    try {
      localStorage.setItem(spec.key, JSON.stringify(ids));
    } catch (_) {}
  }

  function parkPickState() {
    const spec = pickSpec();
    if (!spec || spec.layout !== "set") return { mode: "tour", unset: true };
    try {
      const raw = localStorage.getItem(spec.key);
      if (raw == null) return { mode: "tour", unset: true };
      const parsed = JSON.parse(raw);
      if (parsed && parsed.mode === "custom" && Array.isArray(parsed.ids)) return parsed;
      return { mode: "tour" };
    } catch (_) {
      return { mode: "tour", unset: true };
    }
  }

  function saveParkPickState(state) {
    const spec = pickSpec();
    if (!spec) return;
    try {
      localStorage.setItem(spec.key, JSON.stringify(state));
    } catch (_) {}
  }

  function isParkCustom() {
    const spec = pickSpec();
    return Boolean(spec && spec.layout === "set" && parkPickState().mode === "custom");
  }

  function normalizeParkIds(ids, lib) {
    const allowed = new Set((lib.cards || []).map((c) => c.cardId));
    const seen = new Set();
    const out = [];
    (ids || []).forEach((id) => {
      if (id && allowed.has(id) && !seen.has(id) && out.length < 10) {
        out.push(id);
        seen.add(id);
      }
    });
    return out;
  }

  function pickLibById(lib) {
    const byId = {};
    ((lib && lib.cards) || []).forEach((c) => {
      byId[c.cardId] = c;
    });
    return byId;
  }

  function habitatFilms(h) {
    if (!h) return [];
    const listed = Array.isArray(h.videos) ? h.videos.filter((v) => v && v.url) : [];
    if (listed.length) return listed;
    return h.video && h.video.url ? [h.video] : [];
  }

  function cardHasFilm(card) {
    return habitatFilms(card).length > 0;
  }

  function normalizePicks(saved, lib) {
    const allowed = new Set((lib.cards || []).map((c) => c.cardId));
    if (saved == null) return pickDefaultIds(lib).slice(0, 10);
    const seen = new Set();
    const slots = [];
    for (let i = 0; i < 10; i++) {
      const id = saved[i] || "";
      if (id && allowed.has(id) && !seen.has(id)) {
        slots.push(id);
        seen.add(id);
      } else {
        slots.push("");
      }
    }
    return slots;
  }

  function parkSlots(ids, lib) {
    const filled = normalizeParkIds(ids, lib);
    const slots = filled.slice();
    while (slots.length < 10) slots.push("");
    return slots;
  }

  function pickerDraft(spec, lib) {
    if (spec && spec.layout === "set") {
      const state = parkPickState();
      if (state.unset) return Array.from({ length: 10 }, () => "");
      if (state.mode === "custom") return parkSlots(state.ids, lib);
      return parkSlots(pickDefaultIds(lib), lib);
    }
    const saved = loadPicks(spec);
    if (saved == null) return Array.from({ length: 10 }, () => "");
    return normalizePicks(saved, lib);
  }

  function filledPicks(slots) {
    return (slots || []).filter(Boolean);
  }

  function habitatFromParkCard(card, i) {
    if (!card) return null;
    return {
      id: card.cardId,
      cardId: card.cardId,
      label: card.label,
      emoji: card.emoji || "🏞️",
      photo: card.photo || "",
      blurb: card.blurb || "",
      challenge: card.challenge || "",
      printAnswer: card.printAnswer || "",
      placeHref: card.placeHref || "/field-pack/" + card.cardId + "/",
      hotspot: { svgId: "habitat-" + card.cardId },
      cam: card.cam && card.cam.url ? card.cam : {},
      video: card.video && card.video.url ? card.video : {},
      videos: Array.isArray(card.videos) ? card.videos : undefined,
      seq: i + 1,
      x: card.x,
      y: card.y,
      short: card.short || card.label,
    };
  }

  function applyParkPicks(cfg) {
    const spec = pickSpec(cfg && cfg.kind);
    const lib = pickLibrary(cfg && cfg.kind);
    if (!cfg || !spec || !lib) return;
    if (!pickBaseHabitats || !pickBaseHabitats.length) {
      pickBaseHabitats = JSON.parse(JSON.stringify(cfg.habitats || []));
    }
    const state = parkPickState();
    if (state.mode !== "custom") {
      cfg.habitats = JSON.parse(JSON.stringify(pickBaseHabitats));
      cfg.sequential = true;
      return;
    }
    const byId = pickLibById(lib);
    const ids = normalizeParkIds(state.ids, lib);
    if (!ids.length) {
      cfg.habitats = JSON.parse(JSON.stringify(pickBaseHabitats));
      cfg.sequential = true;
      return;
    }
    cfg.habitats = ids.map((id, i) => habitatFromParkCard(byId[id], i)).filter(Boolean);
    cfg.sequential = false;
  }

  function applyPicks(cfg) {
    const spec = pickSpec(cfg && cfg.kind);
    const lib = pickLibrary(cfg && cfg.kind);
    if (!cfg || !spec || !lib) return;
    if (spec.layout === "set") {
      applyParkPicks(cfg);
      return;
    }
    if (!pickBaseHabitats || !pickBaseHabitats.length) {
      pickBaseHabitats = JSON.parse(JSON.stringify(cfg.habitats || []));
    }
    const saved = loadPicks(spec);
    if (saved == null) return;
    const bases = JSON.parse(JSON.stringify(pickBaseHabitats)).sort(
      (a, b) => (a.seq || 0) - (b.seq || 0)
    );
    const byId = pickLibById(lib);
    const picks = normalizePicks(saved, lib);
    const next = [];
    picks.forEach((cardId, i) => {
      const slot = bases[i];
      const card = cardId && byId[cardId];
      if (!slot || !card) return;
      slot.id = card.cardId;
      slot.cardId = card.cardId;
      slot.label = card.label;
      slot.challenge = card.challenge || slot.challenge;
      slot.printAnswer = card.printAnswer || slot.printAnswer;
      slot.video = card.video && card.video.url ? card.video : {};
      if (Array.isArray(card.videos) && card.videos.length) slot.videos = card.videos;
      else delete slot.videos;
      slot.cam = card.cam && card.cam.url ? card.cam : {};
      slot.seq = next.length + 1;
      next.push(slot);
    });
    cfg.habitats = next;
  }

  function applyMapPhotos() {
    if (!mapMount || !config) return;
    walkList().forEach((h) => {
      const svgId = h.hotspot && h.hotspot.svgId;
      const el = svgId && mapMount.querySelector("#" + cssEscape(svgId));
      if (!el) return;
      const src = h.photo || cardPhotoSrc(h.cardId || h.id);
      const img = el.querySelector("image");
      if (img && src) {
        img.setAttribute("href", src);
        img.setAttributeNS("http://www.w3.org/1999/xlink", "href", src);
      }
    });
  }

  function svgNS() {
    return "http://www.w3.org/2000/svg";
  }

  // Zoo trail: Catmull-Rom through pin centers + small beside offsets and
  // landscape vias (river / savanna / forest). Replaces the Phase 1 global
  // midpoint bulge so each stop gets its own curve.
  const ZOO_TRAIL_WAYPOINTS = [
    { gate: "in" },
    { via: [350, 720] },
    { stop: "caribbean-flamingo", beside: [-16, -28] },
    { via: [248, 608] },
    { stop: "asian-small-clawed-otter", beside: [-18, -14] },
    { via: [148, 458] },
    { via: [115, 405] },
    { stop: "african-penguin", beside: [28, 0] },
    { via: [168, 292] },
    { via: [260, 278] },
    { stop: "nile-hippo", beside: [-14, 20] },
    { via: [312, 208] },
    { via: [300, 132] },
    { stop: "reticulated-giraffe", beside: [6, 30] },
    { via: [430, 50] },
    { stop: "african-elephant", beside: [0, 26] },
    { via: [600, 122] },
    { via: [650, 168] },
    { stop: "african-lion", beside: [-24, 10] },
    { via: [655, 298] },
    { stop: "sumatran-tiger", beside: [-26, 2] },
    { via: [690, 472] },
    { stop: "western-lowland-gorilla", beside: [-22, -12] },
    { via: [575, 622] },
    { stop: "giant-panda", beside: [6, -24] },
    { gate: "out" },
  ];

  function trailPt(x, y) {
    return { x: x, y: y };
  }

  function catmullRomPath(points) {
    if (!points || points.length < 2) return "";
    const pts = points.map((p) => trailPt(p.x, p.y));
    const dist = (a, b) => Math.hypot(b.x - a.x, b.y - a.y) || 1e-6;
    const alpha = 0.5;
    const handles = (p0, p1, p2, p3) => {
      const t0 = 0;
      const t1 = Math.pow(dist(p0, p1), alpha);
      const t2 = t1 + Math.pow(dist(p1, p2), alpha);
      const t3 = t2 + Math.pow(dist(p2, p3), alpha);
      const dt = t2 - t1 || 1e-6;
      return {
        c1: {
          x: p1.x + ((p2.x - p0.x) * dt) / ((t2 - t0) || 1e-6) / 3,
          y: p1.y + ((p2.y - p0.y) * dt) / ((t2 - t0) || 1e-6) / 3,
        },
        c2: {
          x: p2.x - ((p3.x - p1.x) * dt) / ((t3 - t1) || 1e-6) / 3,
          y: p2.y - ((p3.y - p1.y) * dt) / ((t3 - t1) || 1e-6) / 3,
        },
      };
    };
    const parts = [`M${pts[0].x.toFixed(1)},${pts[0].y.toFixed(1)}`];
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = i > 0 ? pts[i - 1] : pts[i];
      const p1 = pts[i];
      const p2 = pts[i + 1];
      const p3 = i + 2 < pts.length ? pts[i + 2] : pts[i + 1];
      const h = handles(p0, p1, p2, p3);
      parts.push(
        `C${h.c1.x.toFixed(1)},${h.c1.y.toFixed(1)} ${h.c2.x.toFixed(1)},${h.c2.y.toFixed(1)} ${p2.x.toFixed(1)},${p2.y.toFixed(1)}`
      );
    }
    return parts.join(" ");
  }

  function pathDestinations(d) {
    if (!d) return [];
    const tokens = d.match(/[MLQCZmlqcz]|-?\d*\.?\d+(?:e[-+]?\d+)?/g);
    if (!tokens || !tokens.length) return [];
    let i = 0;
    const pts = [];
    const num = () => {
      const n = parseFloat(tokens[i]);
      i += 1;
      return Number.isFinite(n) ? n : 0;
    };
    while (i < tokens.length) {
      const raw = tokens[i];
      if (!/^[MLQCZmlqcz]$/.test(raw)) break;
      const cmd = raw.toUpperCase();
      i += 1;
      if (cmd === "Z") continue;
      if (cmd === "M" || cmd === "L") {
        pts.push(trailPt(num(), num()));
        continue;
      }
      if (cmd === "Q") {
        while (i < tokens.length && !/^[MLQCZmlqcz]$/.test(tokens[i])) {
          num();
          num();
          pts.push(trailPt(num(), num()));
        }
        continue;
      }
      if (cmd === "C") {
        while (i < tokens.length && !/^[MLQCZmlqcz]$/.test(tokens[i])) {
          num();
          num();
          num();
          num();
          pts.push(trailPt(num(), num()));
        }
        continue;
      }
    }
    return pts;
  }

  function spotCenter(el) {
    if (!el) return null;
    const hit = el.querySelector(".vz-hit") || el.querySelector(".vz-silo");
    if (!hit) return null;
    const x = parseFloat(hit.getAttribute("x") || "0");
    const y = parseFloat(hit.getAttribute("y") || "0");
    const w = parseFloat(hit.getAttribute("width") || "0");
    const h = parseFloat(hit.getAttribute("height") || "0");
    return trailPt(x + w / 2, y + h / 2);
  }

  function gateCenter(which) {
    const id = which === "out" ? "vz-exit" : "vz-entry";
    const g = mapMount && mapMount.querySelector("#" + id);
    const r = g && g.querySelector("rect");
    if (!r) return null;
    return trailPt(
      parseFloat(r.getAttribute("x") || "0") + parseFloat(r.getAttribute("width") || "0") / 2,
      parseFloat(r.getAttribute("y") || "0") + parseFloat(r.getAttribute("height") || "0") / 2
    );
  }

  function skipTrailVias() {
    return walkList().length <= 2;
  }

  function zooTrailPoints() {
    const byId = {};
    walkList().forEach((h) => {
      const svgId = h.hotspot && h.hotspot.svgId;
      const el = svgId && mapMount.querySelector("#" + cssEscape(svgId));
      const c = spotCenter(el);
      if (c) byId[h.id] = c;
    });
    const pts = [];
    const shortPath = skipTrailVias();
    ZOO_TRAIL_WAYPOINTS.forEach((step) => {
      if (step.gate) {
        const g = gateCenter(step.gate);
        if (g) pts.push(g);
        return;
      }
      if (step.via) {
        if (shortPath) return;
        pts.push(trailPt(step.via[0], step.via[1]));
        return;
      }
      if (!step.stop) return;
      const c = byId[step.stop];
      if (!c) return;
      const b = step.beside || [0, 0];
      pts.push(trailPt(c.x + b[0], c.y + b[1]));
    });
    return pts;
  }

  function applyTrailD(g, d) {
    if (!d) return;
    g.querySelectorAll("path").forEach((p) => p.setAttribute("d", d));
    let sh = g.querySelector(".vz-trail-shadow");
    if (!sh) {
      sh = document.createElementNS(svgNS(), "path");
      sh.setAttribute("class", "vz-trail-shadow");
      sh.setAttribute("fill", "none");
      g.insertBefore(sh, g.firstChild);
    }
    sh.setAttribute("d", d);
  }

  function circlePhotoClip() {
    const svg = mapMount && mapMount.querySelector("svg");
    if (!svg) return;
    let defs = svg.querySelector("defs");
    if (!defs) {
      defs = document.createElementNS(svgNS(), "defs");
      svg.insertBefore(defs, svg.firstChild);
    }
    let clip = svg.querySelector("#vz-photo-clip");
    if (!clip) {
      clip = document.createElementNS(svgNS(), "clipPath");
      clip.setAttribute("id", "vz-photo-clip");
      clip.setAttribute("clipPathUnits", "objectBoundingBox");
      defs.appendChild(clip);
    }
    if (clip.querySelector("circle")) return;
    while (clip.firstChild) clip.removeChild(clip.firstChild);
    const c = document.createElementNS(svgNS(), "circle");
    c.setAttribute("cx", "0.5");
    c.setAttribute("cy", "0.5");
    c.setAttribute("r", "0.5");
    clip.appendChild(c);
  }

  function roundPictorialPins() {
    if (!mapMount) return;
    mapMount.querySelectorAll(".vz-silo, .vz-halo").forEach((el) => {
      const w = parseFloat(el.getAttribute("width") || "0");
      const h = parseFloat(el.getAttribute("height") || "0");
      if (!w || !h) return;
      const r = Math.min(w, h) / 2;
      el.setAttribute("rx", String(r));
      el.setAttribute("ry", String(r));
    });
    mapMount.querySelectorAll(".vz-spot image").forEach((img) => {
      img.setAttribute("clip-path", "url(#vz-photo-clip)");
    });
  }

  function polishTrail() {
    if (!mapMount) return;
    const g = mapMount.querySelector("#vz-trail");
    if (!g || g.getAttribute("data-polished") === "1") return;
    const bed = g.querySelector(".vz-trail-bed");
    const dash = g.querySelector(".vz-trail-dash");
    const src = bed || dash;
    if (!src) return;
    const authored = src.getAttribute("d") || "";
    let d = authored;
    let mode = "authored";
    const kind = config && config.kind;
    if (kind === "zoo") {
      const pts = zooTrailPoints();
      if (pts.length >= 3) {
        d = catmullRomPath(pts);
        mode = "hug";
      }
    } else if (kind !== "aquarium" && kind !== "park" && /[Qq]/.test(authored)) {
      const pts = pathDestinations(authored);
      if (pts.length >= 3) {
        d = catmullRomPath(pts);
        mode = "smooth";
      }
    }
    applyTrailD(g, d);
    g.setAttribute("data-polished", "1");
    g.setAttribute("data-trail", mode);
  }

  function polishPictorialMap() {
    if (!mapMount) return;
    if (mapMount.classList.contains("is-pictorial")) {
      circlePhotoClip();
      roundPictorialPins();
    }
    polishTrail();
  }

  function cssEscape(id) {
    if (window.CSS && CSS.escape) return CSS.escape(id);
    return String(id).replace(/([^a-zA-Z0-9_-])/g, "\\$1");
  }

  const PARK_PAD = 72;

  function parkMarkParts(spot) {
    const pin = spot.previousElementSibling;
    const label = spot.nextElementSibling;
    return {
      pin: pin && pin.tagName && pin.tagName.toLowerCase() === "circle" ? pin : null,
      label: label && label.tagName && label.tagName.toLowerCase() === "text" ? label : null,
    };
  }

  function setParkMarkVisible(spot, on) {
    const parts = parkMarkParts(spot);
    [spot, parts.pin, parts.label].forEach((el) => {
      if (!el) return;
      el.style.display = on ? "" : "none";
    });
    if (on) {
      spot.removeAttribute("data-empty");
      spot.removeAttribute("aria-hidden");
    } else {
      spot.setAttribute("data-empty", "1");
      spot.setAttribute("aria-hidden", "true");
      spot.setAttribute("data-habitat", "");
    }
  }

  function customParksLayer() {
    const svg = mapMount && mapMount.querySelector("svg");
    if (!svg) return null;
    const NS = "http://www.w3.org/2000/svg";
    let layer = svg.querySelector("#vz-custom-parks");
    if (!layer) {
      layer = document.createElementNS(NS, "g");
      layer.setAttribute("id", "vz-custom-parks");
      svg.appendChild(layer);
    }
    return layer;
  }

  function injectParkMark(h) {
    const layer = customParksLayer();
    if (!layer || h.x == null || h.y == null) return;
    const NS = "http://www.w3.org/2000/svg";
    const cx = Number(h.x);
    const cy = Number(h.y);
    const half = PARK_PAD / 2;
    const px = Math.min(Math.max(cx, half + 8), 1000 - half - 8);
    const py = Math.min(Math.max(cy, half + 8), 620 - half - 22);
    const x = px - half;
    const y = py - half;
    const g = document.createElementNS(NS, "g");
    g.setAttribute("class", "vz-park-extra");
    const pin = document.createElementNS(NS, "circle");
    pin.setAttribute("cx", String(cx));
    pin.setAttribute("cy", String(cy));
    pin.setAttribute("r", "3.4");
    pin.setAttribute("fill", "#0f5c5c");
    pin.setAttribute("stroke", "#fff");
    pin.setAttribute("stroke-width", "1.4");
    const a = document.createElementNS(NS, "a");
    a.setAttribute("href", "/field-pack/virtual-field-trip/?tab=parks#habitat=" + encodeURIComponent(h.id));
    a.setAttribute("id", "habitat-" + h.id);
    a.setAttribute("class", "vz-spot");
    a.setAttribute("data-habitat", h.id);
    a.setAttribute("aria-label", h.label || h.id);
    const hit = document.createElementNS(NS, "rect");
    hit.setAttribute("class", "vz-hit");
    hit.setAttribute("x", String(x));
    hit.setAttribute("y", String(y));
    hit.setAttribute("width", String(PARK_PAD));
    hit.setAttribute("height", String(PARK_PAD));
    hit.setAttribute("fill", "transparent");
    const halo = document.createElementNS(NS, "rect");
    halo.setAttribute("class", "vz-halo");
    halo.setAttribute("x", String(x - 2));
    halo.setAttribute("y", String(y - 2));
    halo.setAttribute("width", String(PARK_PAD + 4));
    halo.setAttribute("height", String(PARK_PAD + 4));
    halo.setAttribute("rx", "16");
    const silo = document.createElementNS(NS, "rect");
    silo.setAttribute("class", "vz-silo");
    silo.setAttribute("x", String(x + 3));
    silo.setAttribute("y", String(y + 3));
    silo.setAttribute("width", String(PARK_PAD - 6));
    silo.setAttribute("height", String(PARK_PAD - 6));
    silo.setAttribute("rx", "12");
    silo.setAttribute("fill", "#fff");
    silo.setAttribute("stroke", "#1f2a2a");
    silo.setAttribute("stroke-width", "2.6");
    silo.setAttribute("filter", "url(#pad-shadow)");
    const img = document.createElementNS(NS, "image");
    const src = h.photo || "";
    img.setAttribute("href", src);
    img.setAttributeNS("http://www.w3.org/1999/xlink", "href", src);
    img.setAttribute("x", String(x + 6));
    img.setAttribute("y", String(y + 6));
    img.setAttribute("width", String(PARK_PAD - 12));
    img.setAttribute("height", String(PARK_PAD - 12));
    img.setAttribute("preserveAspectRatio", "xMidYMin slice");
    img.setAttribute("clip-path", "url(#vz-photo-clip)");
    a.appendChild(hit);
    a.appendChild(halo);
    a.appendChild(silo);
    a.appendChild(img);
    const t = document.createElementNS(NS, "text");
    t.setAttribute("x", String(px));
    t.setAttribute("y", String(y + PARK_PAD + 13));
    t.setAttribute("text-anchor", "middle");
    t.setAttribute("font-family", "Georgia,serif");
    t.setAttribute("font-size", "11");
    t.setAttribute("font-weight", "700");
    t.setAttribute("fill", "#0a4545");
    t.textContent = h.short || h.label || h.id;
    g.appendChild(pin);
    g.appendChild(a);
    g.appendChild(t);
    layer.appendChild(g);
    wrapPad(a);
    wireSpot(a);
  }

  function applyParkMap() {
    const spec = pickSpec();
    if (!mapMount || !config || !spec || spec.layout !== "set") return;
    const custom = isParkCustom();
    mapMount.classList.toggle("is-park-custom", custom);
    ["vz-trail", "vz-arrows", "vz-entry", "vz-exit"].forEach((id) => {
      const el = mapMount.querySelector("#" + id);
      if (el) el.style.display = custom ? "none" : "";
    });
    const extras = mapMount.querySelector("#vz-custom-parks");
    if (extras) extras.replaceChildren();
    mapMount.querySelectorAll(".vz-park-extra").forEach((n) => n.remove());
    const live = new Set(walkList().map((h) => h.id));
    mapMount.querySelectorAll("a.vz-spot").forEach((el) => {
      if (el.closest(".vz-park-extra")) return;
      const id = (el.getAttribute("id") || "").replace(/^habitat-/, "");
      const on = live.has(id);
      setParkMarkVisible(el, on);
      if (on) {
        const h = habitatById(id);
        el.setAttribute("data-habitat", h ? h.id : id);
        el.setAttribute("aria-label", (h && h.label) || id);
      }
    });
    if (!custom) return;
    walkList().forEach((h) => {
      if (mapMount.querySelector("#habitat-" + cssEscape(h.id))) return;
      injectParkMark(h);
    });
  }

  function remapPickPads() {
    const spec = pickSpec();
    if (!mapMount || !config || !spec || spec.layout === "set") return;
    const bySvg = {};
    walkList().forEach((h) => {
      const svgId = h.hotspot && h.hotspot.svgId;
      if (svgId) bySvg[svgId] = h;
    });
    (pickBaseHabitats || []).forEach((base) => {
      const svgId = base.hotspot && base.hotspot.svgId;
      const el = svgId && mapMount.querySelector("#" + svgId);
      if (!el) return;
      const h = bySvg[svgId];
      if (!h) {
        el.setAttribute("data-habitat", "");
        el.setAttribute("data-empty", "1");
        el.setAttribute("aria-hidden", "true");
        el.setAttribute("tabindex", "-1");
        el.style.display = "none";
        return;
      }
      el.style.display = "";
      el.removeAttribute("data-empty");
      el.removeAttribute("aria-hidden");
      el.setAttribute("data-habitat", h.id);
      el.setAttribute("aria-label", h.label || h.id);
      const src = cardPhotoSrc(h.cardId || h.id);
      const img = el.querySelector("image");
      if (img && src) {
        img.setAttribute("href", src);
        img.setAttributeNS("http://www.w3.org/1999/xlink", "href", src);
      }
    });
  }

  function pickCardName(cardId, lib) {
    const item = catalogItem(cardId);
    const card = pickLibById(lib)[cardId];
    return (item && item.name) || (card && card.label) || cardId;
  }

  function pickCardThumb(cardId) {
    const lib = pickLibrary();
    const card = pickLibById(lib)[cardId];
    const src = (card && card.photo) || cardPhotoSrc(cardId);
    return src ? `<img src="${escapeHtml(src)}" alt="" width="120" height="90" loading="lazy" decoding="async" />` : "";
  }

  function renderPathPicker() {
    if (!pathPicker) return;
    const spec = pickSpec();
    const lib = pickLibrary();
    const live = Boolean(spec && lib);
    pathPicker.hidden = !live;
    if (!live) {
      pathPicker.innerHTML = "";
      pickDraft = null;
      pickHold = null;
      return;
    }
    if (spec.layout === "set") {
      renderParkPicker(spec, lib);
      return;
    }
    if (!pickDraft || pickDraft.length !== 10) {
      pickDraft = pickerDraft(spec, lib).slice();
      while (pickDraft.length < 10) pickDraft.push("");
      pickHold = null;
    }
    const used = new Set(pickDraft.filter(Boolean));
    const n = filledPicks(pickDraft).length;
    const bench = (lib.cards || []).filter((c) => !used.has(c.cardId) && cardHasFilm(c));
    const holdSlot = pickHold && pickHold.type === "slot" ? pickHold.i : -1;
    const holdCard = pickHold && pickHold.type === "bench" ? pickHold.cardId : "";
    pathPicker.innerHTML = `
      <p class="vz-pick-lead">Build the walk here. Empty slots first — tap something waiting to drop it in. Tap two slots to swap. Or auto-design the ${escapeHtml(spec.noun)} if you want it done.</p>
      <ol class="vz-slot-row">
        ${pickDraft
          .map((id, i) => {
            const on = holdSlot === i ? " is-hold" : "";
            const empty = id ? "" : " is-empty";
            const body = id
              ? `${pickCardThumb(id)}<span>${escapeHtml(pickCardName(id, lib))}</span>`
              : `<span class="vz-slot-empty">Add</span>`;
            return `<li>
              <button type="button" class="vz-slot${on}${empty}" data-slot="${i}">
                <span class="vz-slot-num">${i + 1}</span>
                ${body}
              </button>
            </li>`;
          })
          .join("")}
      </ol>
      <p class="vz-pick-count">${n} on the path</p>
      <p class="vz-pick-bench-label">Waiting</p>
      <ul class="vz-pick-grid">
        ${bench
          .map((c) => {
            const on = holdCard === c.cardId ? " is-hold" : "";
            return `<li>
              <button type="button" class="vz-pick-card${on}" data-bench="${escapeHtml(c.cardId)}">
                ${pickCardThumb(c.cardId)}
                <span>${escapeHtml(pickCardName(c.cardId, lib))}</span>
              </button>
            </li>`;
          })
          .join("")}
      </ul>
      <div class="vz-pick-actions">
        <button type="button" class="btn btn-primary" id="vz-pick-defaults"${draftIsDefaults(lib) ? " disabled" : ""}>Auto-design the ${escapeHtml(spec.noun)}</button>
        <button type="button" class="btn btn-secondary" id="vz-pick-apply"${n ? "" : " disabled"}>Create your own ${escapeHtml(spec.noun)}</button>
      </div>
    `;
    pathPicker.querySelectorAll("[data-slot]").forEach((btn) => {
      btn.addEventListener("click", () => tapPickSlot(parseInt(btn.getAttribute("data-slot"), 10)));
    });
    pathPicker.querySelectorAll("[data-bench]").forEach((btn) => {
      btn.addEventListener("click", () => tapPickBench(btn.getAttribute("data-bench")));
    });
    const applyBtn = pathPicker.querySelector("#vz-pick-apply");
    if (applyBtn) applyBtn.addEventListener("click", commitPickPath);
    const defaultsBtn = pathPicker.querySelector("#vz-pick-defaults");
    if (defaultsBtn) defaultsBtn.addEventListener("click", autoDesignPath);
  }

  function renderParkPicker(spec, lib) {
    if (!pickDraft || pickDraft.length !== 10) {
      pickDraft = pickerDraft(spec, lib).slice();
      while (pickDraft.length < 10) pickDraft.push("");
      pickHold = null;
    }
    const used = new Set(pickDraft.filter(Boolean));
    const n = filledPicks(pickDraft).length;
    const bench = (lib.cards || []).filter((c) => !used.has(c.cardId));
    const holdSlot = pickHold && pickHold.type === "slot" ? pickHold.i : -1;
    const holdCard = pickHold && pickHold.type === "bench" ? pickHold.cardId : "";
    pathPicker.innerHTML = `
      <p class="vz-pick-lead">Empty boxes first — tap a park waiting below to drop it in. Tap two boxes to swap. Auto-design fills the Maine-to-Rockies road trip. Show these parks drops the road and leaves them where they really are. This map is the lower 48.</p>
      <ol class="vz-slot-row">
        ${pickDraft
          .map((id, i) => {
            const on = holdSlot === i ? " is-hold" : "";
            const empty = id ? "" : " is-empty";
            const body = id
              ? `${pickCardThumb(id)}<span>${escapeHtml(pickCardName(id, lib))}</span>`
              : `<span class="vz-slot-empty">Add</span>`;
            return `<li>
              <button type="button" class="vz-slot${on}${empty}" data-slot="${i}">
                <span class="vz-slot-num">${i + 1}</span>
                ${body}
              </button>
            </li>`;
          })
          .join("")}
      </ol>
      <p class="vz-pick-count">${n} of 10 on the map</p>
      <p class="vz-pick-bench-label">Waiting</p>
      <ul class="vz-pick-grid">
        ${bench
          .map((c) => {
            const on = holdCard === c.cardId ? " is-hold" : "";
            return `<li>
              <button type="button" class="vz-pick-card${on}" data-bench="${escapeHtml(c.cardId)}">
                ${pickCardThumb(c.cardId)}
                <span>${escapeHtml(pickCardName(c.cardId, lib))}</span>
              </button>
            </li>`;
          })
          .join("")}
      </ul>
      <div class="vz-pick-actions">
        <button type="button" class="btn btn-primary" id="vz-pick-defaults"${draftIsDefaults(lib) ? " disabled" : ""}>Auto-design the road trip</button>
        <button type="button" class="btn btn-secondary" id="vz-pick-apply"${n ? "" : " disabled"}>Show these parks</button>
      </div>
    `;
    pathPicker.querySelectorAll("[data-slot]").forEach((btn) => {
      btn.addEventListener("click", () => tapPickSlot(parseInt(btn.getAttribute("data-slot"), 10)));
    });
    pathPicker.querySelectorAll("[data-bench]").forEach((btn) => {
      btn.addEventListener("click", () => tapPickBench(btn.getAttribute("data-bench")));
    });
    const applyBtn = pathPicker.querySelector("#vz-pick-apply");
    if (applyBtn) applyBtn.addEventListener("click", commitParkCustom);
    const defaultsBtn = pathPicker.querySelector("#vz-pick-defaults");
    if (defaultsBtn) defaultsBtn.addEventListener("click", autoDesignPath);
  }

  function draftIsDefaults(lib) {
    const ids = pickDefaultIds(lib).slice(0, 10);
    while (ids.length < 10) ids.push("");
    return Boolean(pickDraft && pickDraft.length === ids.length && pickDraft.every((id, i) => id === ids[i]));
  }

  function fillPickDefaults() {
    const lib = pickLibrary();
    if (!lib) return;
    pickDraft = parkSlots(pickDefaultIds(lib), lib);
    pickHold = null;
  }

  function autoDesignPath() {
    fillPickDefaults();
    const spec = pickSpec();
    if (spec && spec.layout === "set") commitParkTour();
    else commitPickPath();
  }

  function refreshAfterPicks(spec) {
    if (config.storageKey) {
      stamps = [];
      saveStamps(config.storageKey, stamps);
    }
    root.dataset.passportFired = "";
    applyPicks(config);
    remapPickPads();
    applyParkMap();
    applyMapPhotos();
    polishPictorialMap();
    renderPassport();
    markMapStamps();
    mapMount?.querySelectorAll("[data-habitat]").forEach((el) => {
      if (el.getAttribute("data-habitat")) wrapPad(el);
    });
    wireMap();
    closeDialog();
    pickHold = null;
    renderPathPicker();
    if (stopsDrawer) stopsDrawer.open = false;
    applyChrome();
    track(spec.track, { count: walkList().length, tab: currentTab(), mode: isParkCustom() ? "custom" : "tour" });
  }

  function commitParkTour() {
    const spec = pickSpec();
    const lib = pickLibrary();
    if (!spec || !lib || !config) return;
    saveParkPickState({ mode: "tour" });
    pickDraft = parkSlots(pickDefaultIds(lib), lib);
    refreshAfterPicks(spec);
  }

  function commitParkCustom() {
    const spec = pickSpec();
    const lib = pickLibrary();
    if (!spec || !lib || !config) return;
    const ids = normalizeParkIds(pickDraft, lib);
    if (!ids.length) return;
    saveParkPickState({ mode: "custom", ids });
    pickDraft = parkSlots(ids, lib);
    refreshAfterPicks(spec);
  }

  function tapPickSlot(i) {
    if (!pickDraft) return;
    if (pickHold && pickHold.type === "bench") {
      const prev = pickDraft[i];
      pickDraft[i] = pickHold.cardId;
      pickHold = prev ? { type: "bench", cardId: prev } : null;
      renderPathPicker();
      return;
    }
    if (pickHold && pickHold.type === "slot") {
      if (pickHold.i === i) {
        pickDraft[i] = "";
        pickHold = null;
      } else {
        const a = pickDraft[pickHold.i];
        pickDraft[pickHold.i] = pickDraft[i];
        pickDraft[i] = a;
        pickHold = null;
      }
      renderPathPicker();
      return;
    }
    pickHold = { type: "slot", i };
    renderPathPicker();
  }

  function tapPickBench(cardId) {
    if (!pickDraft) return;
    if (pickHold && pickHold.type === "slot") {
      const prev = pickDraft[pickHold.i];
      pickDraft[pickHold.i] = cardId;
      pickHold = prev ? { type: "bench", cardId: prev } : null;
      renderPathPicker();
      return;
    }
    const empty = pickDraft.findIndex((id) => !id);
    if (empty !== -1 && !(pickHold && pickHold.type === "bench")) {
      pickDraft[empty] = cardId;
      pickHold = null;
      renderPathPicker();
      return;
    }
    pickHold = pickHold && pickHold.type === "bench" && pickHold.cardId === cardId ? null : { type: "bench", cardId };
    renderPathPicker();
  }

  function commitPickPath() {
    const spec = pickSpec();
    const lib = pickLibrary();
    if (!pickDraft || !spec || !lib || !config) return;
    const next = normalizePicks(pickDraft, lib);
    if (!filledPicks(next).length) return;
    savePicks(spec, next);
    if (config.storageKey) {
      stamps = [];
      saveStamps(config.storageKey, stamps);
    }
    root.dataset.passportFired = "";
    applyPicks(config);
    remapPickPads();
    applyParkMap();
    applyMapPhotos();
    polishPictorialMap();
    renderPassport();
    markMapStamps();
    mapMount?.querySelectorAll("[data-habitat]").forEach((el) => {
      if (el.getAttribute("data-habitat")) wrapPad(el);
    });
    closeDialog();
    pickHold = null;
    pickDraft = next.slice();
    renderPathPicker();
    if (stopsDrawer) stopsDrawer.open = false;
    track(spec.track, { count: filledPicks(next).length, tab: currentTab() });
  }

  function nextHabitat() {
    return walkList().find((h) => !stamps.includes(h.id)) || null;
  }

  function stopNum(id) {
    const i = walkList().findIndex((h) => h.id === id);
    return i >= 0 ? i + 1 : 0;
  }

  function isDesk() {
    return window.matchMedia("(min-width: 720px)").matches;
  }

  function isPictorialMap() {
    return Boolean(mapMount && mapMount.classList.contains("is-pictorial"));
  }

  // Desktop pictorial pins were 0.56 / 0.68 of the SVG pad and looked small
  // on the wide map. Mobile keeps scale 1 (the authored ~136 unit pad).
  const DESK_PICTORIAL_REST = 0.8;
  const DESK_PICTORIAL_NEXT = 0.9;

  function padRestScale(el) {
    if (!isDesk()) return 1;
    if (walkList().length <= 4) return 0.9;
    if (isPictorialMap()) {
      return el.getAttribute("data-next") === "1" ? DESK_PICTORIAL_NEXT : DESK_PICTORIAL_REST;
    }
    return el.getAttribute("data-next") === "1" ? 0.68 : 0.56;
  }

  function padPopScale() {
    if (!isDesk()) return 1.08;
    if (config && config.kind === "park") return 3.4;
    if (isPictorialMap()) return 1.22;
    return 1.14;
  }

  function hitBox(hit) {
    if (!hit.dataset.bx) {
      hit.dataset.bx = hit.getAttribute("x") || "0";
      hit.dataset.by = hit.getAttribute("y") || "0";
      hit.dataset.bw = hit.getAttribute("width") || "0";
      hit.dataset.bh = hit.getAttribute("height") || "0";
    }
    return {
      x: parseFloat(hit.dataset.bx) || 0,
      y: parseFloat(hit.dataset.by) || 0,
      w: parseFloat(hit.dataset.bw) || 0,
      h: parseFloat(hit.dataset.bh) || 0,
    };
  }

  function setPadTransform(el, s) {
    const g = el.querySelector(".vz-pad");
    const hit = el.querySelector(".vz-hit");
    if (!g || !hit) return;
    const box = hitBox(hit);
    const cx = box.x + box.w / 2;
    const cy = box.y + box.h / 2;
    if (s === 1) g.removeAttribute("transform");
    else g.setAttribute("transform", `translate(${cx} ${cy}) scale(${s}) translate(${-cx} ${-cy})`);
    // Grow the tap target with the visual pin on desktop pictorial maps.
    // Mobile keeps the authored hit rect (scale 1).
    const hitScale = isDesk() && isPictorialMap() ? Math.max(s, 1) : s > 1 ? s : 1;
    if (hitScale > 1) {
      const nw = box.w * hitScale;
      const nh = box.h * hitScale;
      hit.setAttribute("x", String(cx - nw / 2));
      hit.setAttribute("y", String(cy - nh / 2));
      hit.setAttribute("width", String(nw));
      hit.setAttribute("height", String(nh));
    } else {
      hit.setAttribute("x", String(box.x));
      hit.setAttribute("y", String(box.y));
      hit.setAttribute("width", String(box.w));
      hit.setAttribute("height", String(box.h));
    }
  }

  function liftSpot(el) {
    const svg = el && el.closest("svg");
    if (!svg || el.parentNode !== svg) return;
    if (svg.lastElementChild !== el) svg.appendChild(el);
  }

  function wrapPad(el) {
    if (!el) return;
    let g = el.querySelector(":scope > .vz-pad") || el.querySelector(".vz-pad");
    const hit = el.querySelector(".vz-hit");
    if (!g) {
      const NS = "http://www.w3.org/2000/svg";
      g = document.createElementNS(NS, "g");
      g.setAttribute("class", "vz-pad");
      [...el.children].forEach((kid) => {
        if (kid === hit || kid.classList.contains("vz-hit")) return;
        if (kid.classList.contains("vz-spot-label-g") || kid.classList.contains("vz-spot-label")) return;
        if (kid.classList.contains("vz-next-tag") || kid.classList.contains("vz-open-chip")) return;
        if (kid.classList.contains("vz-play-mark") || kid.classList.contains("vz-bullet")) return;
        if (kid.classList.contains("vz-stamp-mark")) return;
        g.appendChild(kid);
      });
      el.appendChild(g);
    }
    const live = () => {
      const pop = el.classList.contains("is-open") || el.matches(":hover") || document.activeElement === el;
      if (pop) liftSpot(el);
      setPadTransform(el, pop ? padPopScale() : padRestScale(el));
    };
    if (el.dataset.scaleWired !== "1") {
      el.dataset.scaleWired = "1";
      el.addEventListener("pointerenter", live);
      el.addEventListener("pointerleave", live);
      el.addEventListener("focus", live);
      el.addEventListener("blur", live);
    }
    live();
  }

  function placeBullet(el, n) {
    if (config && config.pinLabels) {
      const old = el.querySelector(".vz-bullet");
      if (old) old.remove();
      return;
    }
    if (!el || n < 1) return;
    const hit = el.querySelector(".vz-hit");
    if (!hit) return;
    const NS = "http://www.w3.org/2000/svg";
    let g = el.querySelector(".vz-bullet");
    const x = parseFloat(hit.getAttribute("x")) || 0;
    const y = parseFloat(hit.getAttribute("y")) || 0;
    const w = parseFloat(hit.getAttribute("width")) || 80;
    const desk = isDesk() && isPictorialMap();
    const r = Math.max(desk ? 16 : 13, Math.min(desk ? 23 : 19, w * (desk ? 0.16 : 0.14)));
    const cx = x + r + 2;
    const cy = y + r + 2;
    if (!g) {
      g = document.createElementNS(NS, "g");
      g.setAttribute("class", "vz-bullet");
      g.setAttribute("pointer-events", "none");
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("class", "vz-bullet-disc");
      const t = document.createElementNS(NS, "text");
      t.setAttribute("class", "vz-bullet-num");
      t.setAttribute("text-anchor", "middle");
      g.appendChild(c);
      g.appendChild(t);
      el.appendChild(g);
    }
    const c = g.querySelector(".vz-bullet-disc");
    const t = g.querySelector(".vz-bullet-num");
    c.setAttribute("cx", String(cx));
    c.setAttribute("cy", String(cy));
    c.setAttribute("r", String(r));
    t.setAttribute("x", String(cx));
    t.setAttribute("y", String(cy + r * 0.38));
    t.setAttribute("font-size", String(Math.round(r * 1.2)));
    t.textContent = String(n);
  }

  function placePlayMark(el, hasFilm) {
    if (!el) return;
    const old = el.querySelector(":scope > .vz-play-mark");
    if (!hasFilm) {
      if (old) old.remove();
      return;
    }
    const hit = el.querySelector(".vz-hit");
    if (!hit) return;
    const NS = "http://www.w3.org/2000/svg";
    let g = old;
    if (!g) {
      g = document.createElementNS(NS, "g");
      g.setAttribute("class", "vz-play-mark");
      g.setAttribute("pointer-events", "none");
      const c = document.createElementNS(NS, "circle");
      c.setAttribute("class", "vz-play-disc");
      const t = document.createElementNS(NS, "polygon");
      t.setAttribute("class", "vz-play-tri");
      g.appendChild(c);
      g.appendChild(t);
      el.appendChild(g);
    }
    const x = parseFloat(hit.getAttribute("x")) || 0;
    const y = parseFloat(hit.getAttribute("y")) || 0;
    const w = parseFloat(hit.getAttribute("width")) || 80;
    const h = parseFloat(hit.getAttribute("height")) || 50;
    const r = Math.max(8, Math.min(12, w * 0.09));
    const cx = x + w - r - 4;
    const cy = y + h - r - 4;
    g.querySelector(".vz-play-disc").setAttribute("cx", String(cx));
    g.querySelector(".vz-play-disc").setAttribute("cy", String(cy));
    g.querySelector(".vz-play-disc").setAttribute("r", String(r));
    const s = r * 0.42;
    const pts = `${cx - s * 0.55},${cy - s} ${cx - s * 0.55},${cy + s} ${cx + s},${cy}`;
    g.querySelector(".vz-play-tri").setAttribute("points", pts);
  }

  function isSequential() {
    return Boolean(config && config.sequential);
  }

  function canOpen(id) {
    // Free map: any habitat/stop opens. Sequential "Next" is a hint only.
    return Boolean(id);
  }

  function placeStampMark(el, done) {
    if (!el) return;
    const old = el.querySelector(".vz-stamp-mark");
    if (!done || (config && config.pinLabels)) {
      if (old) old.remove();
      return;
    }
    const hit = el.querySelector(".vz-hit");
    if (!hit) return;
    let g = old;
    if (!g) {
      g = document.createElementNS(svgNS(), "g");
      g.setAttribute("class", "vz-stamp-mark");
      g.setAttribute("pointer-events", "none");
      const c = document.createElementNS(svgNS(), "circle");
      c.setAttribute("class", "vz-stamp-mark-disc");
      const check = document.createElementNS(svgNS(), "path");
      check.setAttribute("class", "vz-stamp-mark-check");
      g.appendChild(c);
      g.appendChild(check);
      el.appendChild(g);
    }
    const x = parseFloat(hit.getAttribute("x")) || 0;
    const y = parseFloat(hit.getAttribute("y")) || 0;
    const w = parseFloat(hit.getAttribute("width")) || 80;
    const h = parseFloat(hit.getAttribute("height")) || 80;
    const desk = isDesk() && isPictorialMap();
    const r = Math.max(desk ? 10 : 8, Math.min(desk ? 14 : 12, w * (desk ? 0.105 : 0.09)));
    const cx = x + r + 3;
    const cy = y + h - r - 4;
    g.querySelector(".vz-stamp-mark-disc").setAttribute("cx", String(cx));
    g.querySelector(".vz-stamp-mark-disc").setAttribute("cy", String(cy));
    g.querySelector(".vz-stamp-mark-disc").setAttribute("r", String(r));
    const s = r * 0.45;
    g.querySelector(".vz-stamp-mark-check").setAttribute(
      "d",
      `M${cx - s},${cy} L${cx - s * 0.15},${cy + s * 0.85} L${cx + s},${cy - s * 0.7}`
    );
  }

  function refreshOpenChip() {
    if (!mapMount) return;
    mapMount.querySelectorAll(".vz-open-chip").forEach((n) => n.remove());
    if (config && config.pinLabels) return;
    const open = mapMount.querySelector(".vz-spot.is-open");
    if (!open) return;
    const hit = open.querySelector(".vz-hit");
    if (!hit) return;
    const id = open.getAttribute("data-habitat");
    const hab = habitatById(id);
    const name = (hab && hab.label) || id;
    if (!name) return;
    const x = parseFloat(hit.getAttribute("x")) || 0;
    const y = parseFloat(hit.getAttribute("y")) || 0;
    const w = parseFloat(hit.getAttribute("width")) || 0;
    const desk = isDesk() && isPictorialMap();
    const fs = desk ? 15 : 13;
    const lx = x + w / 2;
    const ly = Math.max(18, y - (desk ? 22 : 8));
    const boxW = Math.max(desk ? 88 : 72, name.length * fs * 0.56) + (desk ? 22 : 16);
    const boxH = desk ? 24 : 20;
    const g = document.createElementNS(svgNS(), "g");
    g.setAttribute("class", "vz-open-chip");
    g.setAttribute("pointer-events", "none");
    const bg = document.createElementNS(svgNS(), "rect");
    bg.setAttribute("class", "vz-open-chip-bg");
    bg.setAttribute("x", String(lx - boxW / 2));
    bg.setAttribute("y", String(ly - fs * 0.85));
    bg.setAttribute("width", String(boxW));
    bg.setAttribute("height", String(boxH));
    bg.setAttribute("rx", "10");
    const t = document.createElementNS(svgNS(), "text");
    t.setAttribute("class", "vz-open-chip-text");
    t.setAttribute("x", String(lx));
    t.setAttribute("y", String(ly + 2));
    t.setAttribute("text-anchor", "middle");
    t.textContent = name;
    g.appendChild(bg);
    g.appendChild(t);
    open.appendChild(g);
  }

  function placePinLabel(el, name) {
    if (!el || !name || !(config && config.pinLabels)) return;
    const hit = el.querySelector(".vz-hit");
    if (!hit) return;
    const trapped = el.querySelector(".vz-pad .vz-spot-label-g, .vz-pad .vz-spot-label");
    if (trapped) trapped.remove();
    const NS = "http://www.w3.org/2000/svg";
    let g = el.querySelector(":scope > .vz-spot-label-g");
    if (!g) {
      g = document.createElementNS(NS, "g");
      g.setAttribute("class", "vz-spot-label-g");
      const bg = document.createElementNS(NS, "rect");
      bg.setAttribute("class", "vz-spot-label-bg");
      const t = document.createElementNS(NS, "text");
      t.setAttribute("class", "vz-spot-label");
      t.setAttribute("text-anchor", "middle");
      g.appendChild(bg);
      g.appendChild(t);
      el.appendChild(g);
    }
    const t = g.querySelector(".vz-spot-label");
    const bg = g.querySelector(".vz-spot-label-bg");
    const x = parseFloat(hit.getAttribute("x")) || 0;
    const y = parseFloat(hit.getAttribute("y")) || 0;
    const w = parseFloat(hit.getAttribute("width")) || 0;
    const h = parseFloat(hit.getAttribute("height")) || 0;
    const fs = 28;
    const lx = x + w / 2;
    const ly = y + h + fs * 0.92;
    const boxW = Math.max(108, name.length * fs * 0.54) + 22;
    const boxH = fs * 1.18;
    t.setAttribute("x", String(lx));
    t.setAttribute("y", String(ly));
    t.setAttribute("font-size", String(fs));
    t.textContent = name;
    if (bg) {
      bg.setAttribute("x", String(lx - boxW / 2));
      bg.setAttribute("y", String(ly - fs * 0.78));
      bg.setAttribute("width", String(boxW));
      bg.setAttribute("height", String(boxH));
      bg.setAttribute("rx", "10");
    }
  }

  function habitatById(id) {
    return ((config && config.habitats) || []).find((h) => h.id === id || h.cardId === id) || null;
  }

  function itemFor(h) {
    if (!h) return null;
    const id = h.cardId || h.id;
    const fromCat =
      (typeof window.fpGetAnimal === "function" && window.fpGetAnimal(id)) ||
      (window.FIELD_PACK_CATALOG && window.FIELD_PACK_CATALOG[id]) ||
      null;
    if (fromCat && !h.photo) return fromCat;
    if (h.photo || h.blurb || h.synthetic || h.placeHref) {
      return {
        id,
        name: h.label || (fromCat && fromCat.name) || id,
        emoji: h.emoji || (fromCat && fromCat.emoji) || "🐾",
        photo: h.photo || (fromCat && fromCat.photo) || "",
        blurb: h.blurb || (fromCat && fromCat.blurb) || "",
      };
    }
    return fromCat;
  }

  function renderMuseumChips(tab) {
    const row = document.getElementById("vz-museum-chips");
    if (!row) return;
    const show = isMuseumTab(tab);
    row.hidden = !show;
    row.classList.toggle("is-on", show);
    if (!row.querySelector("[data-tab]")) {
      row.innerHTML = MUSEUM_CHIPS.map((c) => {
        return `<a class="vz-chip" href="${escapeHtml(tabUrl(c.id))}" data-tab="${escapeHtml(c.id)}">${escapeHtml(c.label)}</a>`;
      }).join("");
    }
    row.querySelectorAll("[data-tab]").forEach((a) => {
      const id = a.getAttribute("data-tab");
      const on = id === tab;
      a.classList.toggle("is-on", on);
      if (on) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
      a.setAttribute("href", tabUrl(id));
      if (!a.dataset.wired) {
        a.dataset.wired = "1";
        a.addEventListener("click", (e) => {
          e.preventDefault();
          switchTab(a.getAttribute("data-tab"));
        });
      }
    });
  }

  function renderTabs() {
    const nav = document.getElementById("vz-tabs");
    if (!nav) return;
    const tab = currentTab();
    rememberMuseumTab(tab);
    if (!nav.querySelector("[data-tab]")) {
      nav.innerHTML = TAB_ORDER.map((t) => {
        const target = t.id === "museum" ? lastMuseumTab() : t.id;
        const venue = t.id === "museum" ? ' data-venue="museum"' : "";
        return `<a class="vz-tab" href="${escapeHtml(tabUrl(target, ""))}" data-tab="${escapeHtml(t.id)}"${venue}>${escapeHtml(t.label)}</a>`;
      }).join("");
    }
    nav.querySelectorAll("[data-tab]").forEach((a) => {
      const id = a.getAttribute("data-tab");
      const venue = a.getAttribute("data-venue") || id;
      const on = venue === "museum" ? isMuseumTab(tab) : id === tab;
      a.classList.toggle("is-on", on);
      if (on) a.setAttribute("aria-current", "page");
      else a.removeAttribute("aria-current");
      const hrefId = venue === "museum" ? lastMuseumTab() : id;
      a.setAttribute("href", tabUrl(hrefId, ""));
      if (!a.dataset.wired) {
        a.dataset.wired = "1";
        a.addEventListener("click", (e) => {
          e.preventDefault();
          switchTab(resolveVenueTab(a.getAttribute("data-tab")));
        });
      }
    });
    renderMuseumChips(tab);
  }

  function applyChrome() {
    const tab = currentTab();
    showPanels(tab);
    const crumb = document.getElementById("vz-crumb-here");
    if (crumb && config) crumb.textContent = config.crumb || config.title || "Field trip";
    const title = document.getElementById("vz-title");
    const lead = document.getElementById("vz-lead");
    if (title && config && config.h1) title.textContent = config.h1;
    if (lead && config && config.lead) {
      lead.textContent = isParkCustom() ? "Your parks · lower 48 · free" : config.lead;
    }
    if (config && config.title) document.title = config.title;
    if (mapMount && config) {
      mapMount.classList.toggle("is-wide", Boolean(config.mapClass) || config.kind === "park");
      mapMount.classList.toggle("is-pictorial", config.kind !== "park");
      mapMount.setAttribute("data-kind", config.kind || tab);
      const where =
        config.kind === "park"
          ? "National parks map"
          : config.kind === "science"
            ? "Science museum map"
            : config.kind === "natural_history"
              ? "Natural history museum map"
              : config.kind === "aquarium"
                ? "Aquarium map"
                : "Zoo map";
      mapMount.setAttribute("aria-label", where);
    }
    if (config) root.setAttribute("data-kind", config.kind || tab);
    if (stampList) stampList.classList.toggle("is-few", walkList().length <= 4);
  }

  function renderPassport() {
    if (!config) return;
    const habs = walkList();
    const nxt = nextHabitat();
    const unit = isSequential() ? "stops" : config.kind === "park" ? "parks" : "halls";
    const count = `${stamps.length} of ${habs.length} ${unit}`;
    const extra = isSequential()
      ? nxt
        ? ` · Next: ${nxt.label}`
        : habs.length
          ? " · Path complete"
          : ""
      : "";
    if (progressEl) progressEl.textContent = count + extra;
    if (passCount) passCount.textContent = `${stamps.length}/${habs.length}`;
    if (stopsDrawer) {
      const sum = stopsDrawer.querySelector("summary");
      if (sum) {
        const spec = pickSpec(config.kind);
        sum.textContent =
          config.kind === "park" ? "Park kits and links" : spec ? spec.title : "Stops and cards";
      }
    }
    if (stamps.length === habs.length && habs.length) {
      if (!root.dataset.passportFired) {
        root.dataset.passportFired = "1";
        track("passport_completed", { venue_kind: config.kind || "zoo", tab: currentTab(), count: stamps.length });
      }
    }
  }

  function markMapStamps() {
    if (!mapMount) return;
    const nxt = nextHabitat();
    mapMount.querySelectorAll("[data-habitat]").forEach((el) => {
      const id = el.getAttribute("data-habitat");
      if (!id) return;
      const done = stamps.includes(id);
      const isNext = Boolean(nxt && nxt.id === id);
      el.setAttribute("data-stamped", done ? "1" : "0");
      el.setAttribute("data-next", isNext ? "1" : "0");
      el.setAttribute("data-lock", "0");
      el.setAttribute("tabindex", "0");
      el.removeAttribute("aria-disabled");
      const hab = habitatById(id);
      const label = (hab && hab.label) || id;
      const num = stopNum(id);
      el.setAttribute("data-stop", String(num));
      placeBullet(el, num);
      wrapPad(el);
      placePinLabel(el, label);
      placePlayMark(el, habitatFilms(hab).length > 0);
      placeStampMark(el, done);
      el.setAttribute(
        "aria-label",
        isNext
          ? `Next: stop ${num}, ${label}`
          : done
            ? `Open again: ${label}`
            : `Stop ${num}, ${label}`
      );
      if (isNext) el.setAttribute("aria-current", "step");
      else el.removeAttribute("aria-current");
    });
    mapMount.querySelectorAll(".vz-next-tag").forEach((n) => n.remove());
    const nextEl = mapMount.querySelector('[data-next="1"]');
    if (nextEl) {
      const hit = nextEl.querySelector(".vz-hit");
      if (hit) {
        const x = parseFloat(hit.getAttribute("x")) + parseFloat(hit.getAttribute("width")) / 2;
        const y = Math.max(14, parseFloat(hit.getAttribute("y")) - 6);
        const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
        t.setAttribute("class", "vz-next-tag");
        t.setAttribute("x", String(x));
        t.setAttribute("y", String(y));
        t.setAttribute("text-anchor", "middle");
        t.textContent = "Next";
        nextEl.appendChild(t);
      }
    }
    refreshOpenChip();
    const exit = mapMount.querySelector("#vz-exit");
    if (exit) exit.setAttribute("data-open", nxt ? "0" : "1");
  }

  function escapeHtml(s) {
    return String(s ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function youtubeId(url) {
    if (!url) return "";
    try {
      const u = new URL(url, location.origin);
      if (u.hostname === "youtu.be" || u.hostname.endsWith(".youtu.be")) {
        return (u.pathname || "").replace(/^\//, "").split("/")[0] || "";
      }
      if (u.hostname.includes("youtube.com") || u.hostname.includes("youtube-nocookie.com")) {
        return u.searchParams.get("v") || (u.pathname.match(/\/embed\/([^/?]+)/) || [])[1] || "";
      }
    } catch (_) {}
    return "";
  }

  const FILM_START_DEFAULT = 20;

  function filmStartSec(start) {
    if (start === undefined || start === null || start === "") return FILM_START_DEFAULT;
    const n = Math.floor(Number(start));
    if (Number.isFinite(n) && n >= 0) return n;
    return FILM_START_DEFAULT;
  }

  function youtubeEmbed(url, opts) {
    const id = youtubeId(url);
    if (!id) return "";
    const extra = opts && opts.autoplay ? "&autoplay=1&mute=1&enablejsapi=1" : "";
    const start = `&start=${encodeURIComponent(String(filmStartSec(opts && opts.start)))}`;
    const loop = `&loop=1&playlist=${encodeURIComponent(id)}`;
    const origin = encodeURIComponent(location.origin);
    return `https://www.youtube-nocookie.com/embed/${encodeURIComponent(id)}?rel=0&modestbranding=1&playsinline=1${extra}${start}${loop}&origin=${origin}`;
  }

  function isYoutubeWatchUrl(url) {
    return Boolean(youtubeId(url));
  }

  function inPageFilmHref(habitatId) {
    return habitatId ? tabUrl(currentTab(), habitatId) : "#";
  }

  function sealFilmControl(el, habitatId) {
    if (!el) return;
    if (el.tagName === "A") {
      const href = el.getAttribute("href") || "";
      if (!href || href === "#" || isYoutubeWatchUrl(href)) {
        el.setAttribute("href", habitatId ? inPageFilmHref(habitatId) : "#");
      }
      el.removeAttribute("target");
      if (!el.getAttribute("role")) el.setAttribute("role", "button");
    }
    if (habitatId && !el.getAttribute("data-habitat")) {
      el.setAttribute("data-habitat", habitatId);
    }
  }

  function habitatFromFilmControl(el) {
    if (!el || !config) return null;
    const hid = el.getAttribute("data-habitat");
    if (hid) return habitatById(hid);
    const href = el.getAttribute("href") || "";
    const m = href.match(/[#?&]habitat=([^&]+)/);
    if (m) return habitatById(decodeURIComponent(m[1]));
    return (
      (config.habitats || []).find((x) => habitatFilms(x).some((v) => v.url === href)) || null
    );
  }

  function sealStaticFilms() {
    document.querySelectorAll("a.vz-static-film").forEach((a) => {
      const hab = habitatFromFilmControl(a);
      const href = a.getAttribute("href") || "";
      if (hab) {
        a.setAttribute("data-habitat", hab.id);
        if (isYoutubeWatchUrl(href) || !href || href === "#") {
          a.setAttribute("href", inPageFilmHref(hab.id));
        }
        a.removeAttribute("target");
        if (!a.getAttribute("role")) a.setAttribute("role", "button");
        return;
      }
      if (isYoutubeWatchUrl(href)) {
        a.setAttribute("href", "#");
        a.removeAttribute("target");
        a.setAttribute("role", "button");
      }
    });
    if (filmLink) sealFilmControl(filmLink, currentCardId);
  }

  function filmControlFromEvent(e) {
    const t = e.target && e.target.closest ? e.target.closest("a, button") : null;
    if (!t) return null;
    if (t.id === "vz-film" || t.classList.contains("vz-static-film")) return t;
    return null;
  }

  function ytCommand(frame, func) {
    if (!frame || !frame.contentWindow) return;
    try {
      frame.contentWindow.postMessage(JSON.stringify({ event: "command", func: func, args: [] }), "*");
    } catch (_) {}
  }

  function isLocalUrl(url) {
    if (!url) return false;
    try {
      const u = new URL(url, location.origin);
      return u.origin === location.origin;
    } catch (_) {
      return url.charAt(0) === "/";
    }
  }

  function fillPhoto() {
    if (!photoEl) return;
    photoEl.classList.remove("is-playing");
    photoEl.innerHTML = currentPhotoSrc
      ? `<img src="${escapeHtml(currentPhotoSrc)}" alt="" width="640" height="400" decoding="async" />`
      : "";
    hideSoundTip(true);
  }

  function stopWatchPlayer() {
    const frame = photoEl && photoEl.querySelector("iframe.vz-watch-frame");
    if (frame) frame.removeAttribute("src");
    fillPhoto();
  }

  const SOUND_TIP_KEY = "fp-vft-sound-tip-v1";
  const FILM_SEEN_KEY = "fp-vft-film-seen-v1";
  const SOUND_TIP_MS = 7000;
  let soundTipTimer = 0;

  function soundTipEl() {
    return document.getElementById("vz-sound-tip");
  }

  function hideSoundTip(immediate) {
    const el = soundTipEl();
    if (soundTipTimer) {
      clearTimeout(soundTipTimer);
      soundTipTimer = 0;
    }
    if (!el) return;
    el.classList.remove("is-on");
    if (immediate) {
      el.hidden = true;
      return;
    }
    soundTipTimer = setTimeout(() => {
      el.hidden = true;
      soundTipTimer = 0;
    }, 380);
  }

  function soundTipSeen() {
    try {
      return sessionStorage.getItem(SOUND_TIP_KEY) === "1";
    } catch (_) {
      return false;
    }
  }

  function markSoundTipSeen() {
    try {
      sessionStorage.setItem(SOUND_TIP_KEY, "1");
    } catch (_) {}
  }

  function showSoundTip() {
    const el = soundTipEl();
    if (!el || soundTipSeen()) return;
    markSoundTipSeen();
    el.hidden = false;
    requestAnimationFrame(() => el.classList.add("is-on"));
    if (soundTipTimer) clearTimeout(soundTipTimer);
    soundTipTimer = setTimeout(() => hideSoundTip(false), SOUND_TIP_MS);
  }

  function loadFilmSeen() {
    try {
      const raw = sessionStorage.getItem(FILM_SEEN_KEY);
      const data = raw ? JSON.parse(raw) : {};
      return data && typeof data === "object" && !Array.isArray(data) ? data : {};
    } catch (_) {
      return {};
    }
  }

  function saveFilmSeen(data) {
    try {
      sessionStorage.setItem(FILM_SEEN_KEY, JSON.stringify(data));
    } catch (_) {}
  }

  function habitatFilmKey(h) {
    return (h && (h.id || h.cardId)) || "";
  }

  function pickHabitatFilm(h) {
    const films = habitatFilms(h);
    if (!films.length) return null;
    const key = habitatFilmKey(h);
    const seenMap = loadFilmSeen();
    const shown = Array.isArray(seenMap[key]) ? seenMap[key].map(String) : [];
    const shownSet = new Set(shown);
    const unseen = films.filter((f) => {
      const id = youtubeId(f.url);
      return id && !shownSet.has(id);
    });
    const pool = unseen.length ? unseen : films;
    const pick = pool[Math.floor(Math.random() * pool.length)];
    const pickId = pick && youtubeId(pick.url);
    if (key && pickId) {
      seenMap[key] = unseen.length ? shown.concat([pickId]) : [pickId];
      saveFilmSeen(seenMap);
    }
    return pick || null;
  }

  function playHabitatFilm(h) {
    const film = pickHabitatFilm(h);
    if (!film) return false;
    return playFilmInline(film.url, film.title || (h && h.label) || "Pre-recorded", film.start);
  }

  function playFilmInline(url, label, start) {
    const embed = youtubeEmbed(url, {
      autoplay: true,
      start: filmStartSec(start),
    });
    if (!embed || !photoEl) return false;
    photoEl.classList.add("is-playing");
    photoEl.innerHTML = `<iframe class="vz-watch-frame" title="${escapeHtml(label || "Pre-recorded")}" src="${embed}" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>`;
    const frame = photoEl.querySelector("iframe.vz-watch-frame");
    const kick = () => {
      ytCommand(frame, "playVideo");
    };
    if (frame) {
      frame.addEventListener("load", kick, { once: true });
      kick();
    }
    showSoundTip();
    return true;
  }

  function closeCamPopup() {
    if (camWin && !camWin.closed) {
      try {
        camWin.close();
      } catch (_) {}
    }
    camWin = null;
    if (camFrame) {
      camFrame.hidden = true;
      camFrame.removeAttribute("src");
    }
    if (camPop) camPop.hidden = true;
  }

  function openExternal(url) {
    const availW = (window.screen && window.screen.availWidth) || 960;
    const availH = (window.screen && window.screen.availHeight) || 720;
    const w = Math.min(960, Math.max(480, availW - 48));
    const h = Math.min(720, Math.max(400, availH - 96));
    const left = Math.max(0, (availW - w) / 2);
    const top = Math.max(0, (availH - h) / 4);
    const features = `popup=yes,width=${Math.round(w)},height=${Math.round(h)},left=${Math.round(left)},top=${Math.round(top)},menubar=no,toolbar=no,location=yes,status=no,resizable=yes,scrollbars=yes`;
    try {
      camWin = window.open(url, "vzCam", features);
      if (camWin) camWin.focus();
    } catch (_) {
      camWin = null;
    }
    if (!camWin || camWin.closed) {
      try {
        camWin = window.open(url, "_blank", "noopener");
      } catch (_) {
        camWin = null;
      }
    }
  }

  function openCamEmbed(url, label) {
    if (!url || !camFrame) return false;
    if (camWin && !camWin.closed) {
      try {
        camWin.close();
      } catch (_) {}
      camWin = null;
    }
    if (camPopTitle) camPopTitle.textContent = label || "Live";
    if (camPopNote) camPopNote.hidden = true;
    camFrame.hidden = false;
    camFrame.title = label || "Live";
    camFrame.src = url;
    if (camPop) camPop.hidden = false;
    camPopBack?.focus();
    return true;
  }

  function openCamPopup(url, label, mode) {
    if (!url || url === "#") return;
    const local = isLocalUrl(url);
    const film = mode === "film";
    const embed = film ? youtubeEmbed(url) : "";
    if (film) {
      if (playFilmInline(url, label)) return;
      if (embed && camFrame) {
        if (camPopTitle) camPopTitle.textContent = label || "Pre-recorded";
        if (camPopNote) camPopNote.hidden = true;
        camFrame.hidden = false;
        camFrame.title = label || "Pre-recorded";
        camFrame.src = embed;
        if (camPop) camPop.hidden = false;
        camPopBack?.focus();
        return;
      }
      return;
    }
    if (local && camFrame) {
      openCamEmbed(url, label || "Park kit");
      return;
    }
    if (fromCard()) {
      return;
    }
    closeCamPopup();
    openExternal(url);
  }

  function closeDialog() {
    stopWatchPlayer();
    sheet?.classList.remove("is-cinema");
    dialog?.classList.remove("is-cinema");
    if (blurbEl) blurbEl.hidden = false;
    hideSoundTip(true);
    if (!dialog || dialog.hidden) return;
    dialog.hidden = true;
    dialog.setAttribute("aria-hidden", "true");
    mapMount?.querySelectorAll(".vz-spot").forEach((el) => {
      el.classList.remove("is-open");
      wrapPad(el);
    });
    refreshOpenChip();
    if (titleEl) {
      titleEl.hidden = true;
      titleEl.textContent = "";
    }
    if (fromCard()) {
      const hid = currentHabitatId || habitatHashId() || queryHabitat();
      history.replaceState(null, "", tabUrl(currentTab(), hid || ""));
    } else if (location.hash && location.hash.indexOf("habitat=") !== -1) {
      history.replaceState(null, "", tabUrl(currentTab(), ""));
    }
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  function trapTab(e) {
    if (e.key !== "Tab" || !sheet) return;
    const nodes = [...sheet.querySelectorAll("a, button, [href], [tabindex]:not([tabindex='-1'])")].filter(
      (n) => !n.hasAttribute("disabled") && n.offsetParent !== null
    );
    if (!nodes.length) return;
    const first = nodes[0];
    const last = nodes[nodes.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function openHabitat(id, fromEl, opts) {
    const h = habitatById(id);
    if (!h || !dialog) return;
    const fromHash = Boolean(opts && opts.fromHash);
    // Map taps, drawer links, and deep links (?tab=zoo#habitat=giraffe)
    // all open the same stop dialog. Next is a suggestion, not a gate.
    if (!canOpen(id)) return;
    stopWatchPlayer();
    lastFocus = fromEl || document.activeElement;
    const item = itemFor(h);
    if (titleEl) {
      titleEl.hidden = false;
      titleEl.textContent = h.label || (item && item.name) || "Stop";
    }
    currentCardId = (item && item.id) || h.cardId || h.id;
    currentHabitatId = h.id;
    const isPark = Boolean(h.placeHref) || (config && config.kind === "park");
    currentPrint = isPark ? { type: "hunt", id: h.id } : { type: "qa", id: currentCardId };
    currentPhotoSrc =
      (item && window.FPPrint && window.FPPrint.itemPhotoSrc && window.FPPrint.itemPhotoSrc(item)) ||
      h.photo ||
      "";
    fillPhoto();
    const cam = h.cam || {};
    const films = habitatFilms(h);
    const video = films[0] || {};
    const hasCam = Boolean(cam.url);
    const hasFilm = Boolean(video.url);
    const cinema = hasFilm && Boolean(config && (config.kind === "park" || config.kind === "science" || config.kind === "natural_history"));
    sheet?.classList.toggle("is-cinema", cinema);
    dialog?.classList.toggle("is-cinema", cinema);
    if (blurbEl) {
      if (cinema) {
        blurbEl.hidden = true;
        blurbEl.textContent = "";
      } else {
        blurbEl.hidden = false;
        const wow = item && window.FPPrint && window.FPPrint.wowFactFromItem ? window.FPPrint.wowFactFromItem(item) : null;
        const line = (item && item.blurb) || h.blurb || "";
        const wowA = wow && wow.a ? String(wow.a).trim() : "";
        const extra = wowA && wowA !== line.trim() ? ` <strong>${escapeHtml(wowA)}</strong>` : "";
        blurbEl.innerHTML = line ? `${escapeHtml(line)}${extra}` : extra;
      }
    }
    if (watchEl) {
      const canWatch = fromCard() ? Boolean(cam.embed) || hasFilm : hasCam || hasFilm;
      watchEl.hidden = cinema ? !hasCam : !canWatch;
    }
    if (camLink) {
      const inPageCam = Boolean(cam.embed);
      const showCam = fromCard() ? inPageCam : hasCam;
      camLink.hidden = !showCam;
      if (showCam) {
        camLink.href = fromCard() ? "#" : cam.url;
        camLink.innerHTML = `Live<small>${escapeHtml(cam.camLabel || "Live camera")}${
          cam.hours ? " · " + escapeHtml(cam.hours) : ""
        }</small>`;
        camLink.onclick = (e) => {
          e.preventDefault();
          if (fromCard() && cam.embed) {
            openCamEmbed(cam.embed, cam.camLabel || h.label || "Live");
          } else {
            openCamPopup(cam.url, cam.camLabel || h.label || "Live");
          }
          track("cam_clicked", { animal_id: h.cardId || h.id, venue_kind: (config && config.kind) || "zoo", tab: currentTab() });
        };
      } else {
        camLink.removeAttribute("href");
        camLink.onclick = null;
      }
    }
    if (filmLink) {
      filmLink.hidden = cinema || !hasFilm;
      if (hasFilm) {
        filmLink.href = inPageFilmHref(h.id);
        filmLink.setAttribute("role", "button");
        filmLink.removeAttribute("target");
        filmLink.innerHTML = `Pre-recorded<small>${escapeHtml(video.title || "A short video")}</small>`;
        filmLink.onclick = (e) => {
          e.preventDefault();
          playHabitatFilm(h);
          track("film_clicked", { animal_id: h.cardId || h.id, venue_kind: (config && config.kind) || "zoo", tab: currentTab() });
        };
      } else {
        filmLink.removeAttribute("href");
        filmLink.onclick = null;
      }
    }
    if (filmHint) filmHint.hidden = true;
    const skipFilm = Boolean(opts && opts.skipFilm);
    if (hasFilm && !skipFilm) playHabitatFilm(h);
    if (placeLink) {
      if (h.placeHref) {
        placeLink.hidden = false;
        placeLink.href = h.placeHref;
        placeLink.textContent = "Open park kit";
        placeLink.onclick = (e) => {
          e.preventDefault();
          openCamPopup(h.placeHref, h.label || "Park kit");
        };
      } else {
        placeLink.hidden = true;
        placeLink.removeAttribute("href");
        placeLink.onclick = null;
      }
    }
    if (printCardBtn) {
      printCardBtn.textContent = isPark ? "Print park hunt" : "Print this card";
    }
    if (challengeEl) challengeEl.textContent = h.challenge || "";

    if (!stamps.includes(h.id)) {
      stamps = stamps.concat([h.id]);
      saveStamps(config.storageKey, stamps);
      renderPassport();
      markMapStamps();
    }
    if (!openedIds.includes(h.id)) openedIds.push(h.id);

    mapMount?.querySelectorAll(".vz-spot").forEach((el) => {
      el.classList.toggle("is-open", el.getAttribute("data-habitat") === h.id);
      wrapPad(el);
    });
    refreshOpenChip();

    dialog.hidden = false;
    dialog.setAttribute("aria-hidden", "false");
    syncCardNav(h);
    track("habitat_opened", { animal_id: h.cardId || h.id, venue_kind: (config && config.kind) || "zoo", tab: currentTab() });
    const next = tabUrl(currentTab(), h.id);
    if (location.pathname + location.search + location.hash !== next) history.replaceState(null, "", next);
    closeBtn?.focus();
  }

  function onHash() {
    let hid = habitatHashId();
    if (!hid && fromCard()) hid = queryHabitat();
    if (hid) {
      openHabitat(hid, null, { fromHash: true });
      return;
    }
    if (wantsCutoutPrint()) {
      closeDialog();
      return;
    }
    if (currentTab() === "zoo") {
      if (fromCard()) {
        closeDialog();
        return;
      }
      openHabitat(DEFAULT_ZOO_STOP, null, { fromHash: true });
      return;
    }
    closeDialog();
  }

  function wireSpot(el) {
    if (!el || el.dataset.clickWired === "1") return;
    el.dataset.clickWired = "1";
    el.addEventListener("click", (e) => {
      e.preventDefault();
      const id = el.getAttribute("data-habitat");
      if (!id) return;
      openHabitat(id, el);
    });
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openHabitat(el.getAttribute("data-habitat"), el);
      }
    });
  }

  function wireMap() {
    if (!mapMount) return;
    mapMount.querySelectorAll("[data-habitat]").forEach(wireSpot);
  }

  function printMode() {
    if (!config) return;
    if (window.FPPrint && typeof window.FPPrint.printHomeSafari === "function") {
      window.FPPrint.printHomeSafari(config, walkList());
    }
  }

  function refreshCardFocusMap() {
    remapPickPads();
    applyParkMap();
    applyMapPhotos();
    const trail = mapMount && mapMount.querySelector("#vz-trail");
    if (trail) trail.removeAttribute("data-polished");
    polishPictorialMap();
    renderPassport();
    markMapStamps();
    wireMap();
  }

  function switchTab(id) {
    if (!TAB_CONFIGS[id] || id === currentTab()) return;
    history.replaceState(null, "", tabUrl(id, ""));
    if (dialog && !dialog.hidden) {
      dialog.hidden = true;
      dialog.setAttribute("aria-hidden", "true");
    }
    loadVenue();
  }

  function loadVenue() {
    const gen = ++loadGen;
    const tab = currentTab();
    const url = configUrlFor(tab);
    root.dataset.passportFired = "";
    openedIds = [];
    currentCardId = "";
    config = null;
    stamps = [];
    renderTabs();
    if (mapMount) mapMount.innerHTML = "";
    if (stampList) stampList.innerHTML = "";

    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error("config " + r.status);
        return r.json();
      })
      .then((cfg) => {
        if (gen !== loadGen) return null;
        config = cfg;
        const spec = pickSpec(cfg.kind);
        const ready = spec
          ? ensurePickLibrary(cfg.kind).then(() => {
              pickBaseHabitats = JSON.parse(JSON.stringify(cfg.habitats || []));
              applyPicks(cfg);
            })
          : Promise.resolve();
        return ready.then(() => {
          if (gen !== loadGen) return null;
          stamps = loadStamps(cfg.storageKey);
          applyChrome();
          track("virtual_zoo_visited", { venue_kind: cfg.kind || tab, tab });
          if (mapMount && cfg.mapSvg) {
            return fetch(cfg.mapSvg).then((r) => r.text()).then((svg) => {
              if (gen !== loadGen) return;
              mapMount.innerHTML = svg;
            });
          }
          return null;
        });
      })
      .then(() => {
        if (gen !== loadGen) return;
        if (stopsDrawer && !root.dataset.drawerReady) {
          root.dataset.drawerReady = "1";
          stopsDrawer.open = false;
        }
        pickDraft = null;
        pickHold = null;
        remapPickPads();
        applyParkMap();
        applyMapPhotos();
        polishPictorialMap();
        renderPathPicker();
        renderPassport();
        markMapStamps();
        wireMap();
        onHash();
        sealStaticFilms();
        revealPrintReady();
      })
      .catch((err) => {
        if (gen !== loadGen) return;
        if (mapMount) mapMount.innerHTML = "<p>Couldn’t load the map. Refresh?</p>";
        console.warn("[virtual-venue]", err);
      });
  }

  camPopBack?.addEventListener("click", closeCamPopup);
  ["click", "auxclick"].forEach((type) => {
    document.addEventListener(
      type,
      (e) => {
        const filmEl = filmControlFromEvent(e);
        if (!filmEl) return;
        e.preventDefault();
      },
      true
    );
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== " " && e.key !== "Spacebar") return;
    const t = filmControlFromEvent(e);
    if (!t) return;
    e.preventDefault();
    t.click();
  });
  document.addEventListener("auxclick", (e) => {
    const t = filmControlFromEvent(e);
    if (!t) return;
    e.preventDefault();
    if (t.id === "vz-film") {
      const h = currentCardId ? habitatById(currentCardId) : null;
      if (h) playHabitatFilm(h);
      return;
    }
    if (t.classList.contains("vz-static-film")) {
      const hab = habitatFromFilmControl(t);
      if (hab) {
        openHabitat(hab.id, t, { fromHash: true });
        playHabitatFilm(hab);
      }
    }
  });
  document.addEventListener("click", (e) => {
    const t = e.target && e.target.closest ? e.target.closest("a") : null;
    if (!t || !t.getAttribute("href")) return;
    if (t.classList.contains("vz-static-cam")) {
      e.preventDefault();
      if (fromCard()) {
        const row = t.closest && t.closest("li");
        const film = row && row.querySelector(".vz-static-film");
        const hab = habitatFromFilmControl(film || t) || habitatById(t.getAttribute("data-habitat") || "");
        if (hab) openHabitat(hab.id, t, { fromHash: true });
        return;
      }
      openCamPopup(t.getAttribute("href"), t.textContent.replace(/^Live cam — /, "").trim() || "Live cam");
      track("cam_clicked", { animal_id: "static", venue_kind: (config && config.kind) || "zoo", tab: currentTab() });
      return;
    }
    if (t.classList.contains("vz-static-film")) {
      e.preventDefault();
      const hab = habitatFromFilmControl(t);
      if (hab) {
        openHabitat(hab.id, t, { fromHash: true });
        playHabitatFilm(hab);
      }
      track("film_clicked", { animal_id: (hab && (hab.cardId || hab.id)) || "static", venue_kind: (config && config.kind) || "zoo", tab: currentTab() });
      return;
    }
    const stopA = t.closest && t.closest(".vz-static-stops a");
    if (!stopA || stopA.classList.contains("vz-static-cam") || stopA.classList.contains("vz-static-film")) return;
    const href = stopA.getAttribute("href") || "";
    const slug = href.replace(/\/+$/, "").split("/").pop();
    const hab = slug && habitatById(slug);
    if (hab) {
      e.preventDefault();
      openHabitat(hab.id, stopA);
      return;
    }
    if (href.indexOf("/field-pack/") === 0) {
      e.preventDefault();
      openCamPopup(href, stopA.textContent.trim() || "Park kit");
    }
  });
  document.getElementById("vz-sound-tip-dismiss")?.addEventListener("click", () => hideSoundTip(true));
  document.getElementById("vz-next-stop")?.addEventListener("click", () => {
    const nxt = nextAfter(currentHabitatId || habitatHashId() || queryHabitat() || currentCardId);
    if (!nxt) return;
    if (fromCard()) {
      currentHabitatId = nxt.id;
      history.replaceState(null, "", tabUrl(currentTab(), nxt.id));
      refreshCardFocusMap();
    }
    openHabitat(nxt.id, null, { fromHash: true });
  });
  closeBtn?.addEventListener("click", closeDialog);
  backdrop?.addEventListener("click", closeDialog);
  dialog?.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      e.preventDefault();
      if (camPop && !camPop.hidden) closeCamPopup();
      else closeDialog();
    } else trapTab(e);
  });
  camPop?.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      e.preventDefault();
      closeCamPopup();
    }
  });
  window.addEventListener("resize", () => {
    mapMount?.querySelectorAll(".vz-spot").forEach(wrapPad);
  });
  window.addEventListener("hashchange", () => {
    const hash = (location.hash || "").replace(/^#/, "");
    if (hash && TAB_CONFIGS[hash]) {
      const keep = fromCard() && (queryHabitat() || currentHabitatId);
      if (keep) {
        history.replaceState(null, "", tabUrl(hash, queryHabitat() || currentHabitatId));
        onHash();
        return;
      }
      loadVenue();
      return;
    }
    onHash();
  });
  window.addEventListener("popstate", () => loadVenue());
  printWatch?.addEventListener("click", () => printMode());
  printCardBtn?.addEventListener("click", () => {
    if (!window.FPPrint) return;
    if (currentPrint.type === "hunt" && window.FPPrint.printTreasureForVenue) {
      window.FPPrint.printTreasureForVenue(currentPrint.id);
      return;
    }
    if (currentCardId && window.FPPrint.printQaForItem) {
      window.FPPrint.printQaForItem(currentCardId, null);
    }
  });

  setTourChrome();
  loadVenue();
})();
