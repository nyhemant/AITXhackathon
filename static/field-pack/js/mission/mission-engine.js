/**
 * Field Trip Kit — deterministic mission composition (no network, no LLM).
 * Browser: window.FPMission
 * Node (SEO build): load via vm
 */
(function (root) {
  const AGE_ORDER = ["2-3", "4-5", "6-8", "9+"];
  const AGE_LABELS = {
    "2-3": "Little (2–3)",
    "4-5": "Ready (4–5)",
    "6-8": "Big (6–8)",
    "9+": "Older (9+)",
  };
  const TIME_N = { "1hr": 4, half: 6, full: 8, "90m": 4 };
  const TIME_LABELS = {
    "1hr": "~1 hr",
    "90m": "~90 min",
    half: "Half day",
    full: "Full day",
  };

  function defaultOptions() {
    return { age: "4-5", time: "half", interest: "", name: "", seed: 1 };
  }

  function contentMode(venue) {
    const m = (venue && venue.content_mode) || "";
    if (m === "wonder" || m === "hybrid" || m === "curated") return m;
    // Scaffolds default to wonder (honest long-tail)
    if ((venue && venue.verified_by) === "catalog-scaffold") return "wonder";
    if ((venue && venue.verified_by) === "research" || (venue && venue.verified_by) === "owner")
      return "curated";
    return "wonder";
  }

  function mulberry32(a) {
    return function () {
      let t = (a += 0x6d2b79f5);
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function hashSeed(str) {
    let h = 2166136261;
    const s = String(str || "");
    for (let i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function scoreItem(item, interest) {
    let s = 0;
    const tags = item.tags || [];
    if (interest && tags.includes(interest)) s += 2;
    if (tags.includes("wow")) s += 1;
    if (item.zone) s += 1;
    return s;
  }

  function filterByAge(items, age) {
    return (items || []).filter((it) => (it.age_fit || AGE_ORDER).includes(age));
  }

  /** Normalize venue.type → wonder/challenge pool keys: zoo | aquarium | museum | safari_zoo */
  function normalizeVenueType(venue) {
    const raw = String((venue && venue.type) || "zoo")
      .toLowerCase()
      .replace(/[\s+/]+/g, "_");
    if (raw.includes("aquarium") || raw === "aq" || raw === "sci_aq" || raw === "zoo_aq") {
      return "aquarium";
    }
    if (raw.includes("safari")) return "safari_zoo";
    if (raw.includes("zoo")) return "zoo";
    if (
      /museum|science|natural|history|children|space|air|^sci$|^nh$|^cm$|childrens/.test(raw)
    ) {
      return "museum";
    }
    return raw || "zoo";
  }

  function typeAllows(poolTypes, kind) {
    const types = poolTypes || [];
    if (!types.length) return true;
    if (types.includes(kind)) return true;
    if (kind === "safari_zoo" && types.includes("zoo")) return true;
    return false;
  }

  function wonderPool(venue, wondersFile) {
    const kind = normalizeVenueType(venue);
    const list = (wondersFile && wondersFile.wonders) || [];
    return list.filter((w) => {
      if (!typeAllows(w.types, kind)) return false;
      // Museum-safe: no water/splash or live-animal sleep hunts
      const tags = w.tags || [];
      if (kind === "museum") {
        if (tags.includes("water")) return false;
        if (w.id === "w_splash" || w.id === "w_sleep") return false;
      }
      return true;
    });
  }

  /** Must-include stops: route_90m first, else first venue items (top shortlist). */
  function anchorItems(venue, age) {
    const items = venue.items || [];
    const byId = Object.fromEntries(items.map((it) => [it.id, it]));
    const out = [];
    const push = (it) => {
      if (!it || out.some((x) => x.id === it.id)) return;
      const ages = it.age_fit || AGE_ORDER;
      if (!ages.includes(age)) return;
      out.push(it);
    };
    for (const id of venue.route_90m || []) {
      if (out.length >= 3) break;
      push(byId[id]);
    }
    if (!out.length) {
      for (const it of filterByAge(items, age)) {
        if (out.length >= 3) break;
        push(it);
      }
    }
    // If age filter emptied anchors, take raw route/items
    if (!out.length) {
      for (const id of venue.route_90m || []) {
        if (out.length >= 3) break;
        if (byId[id]) out.push(byId[id]);
      }
      for (const it of items) {
        if (out.length >= 3) break;
        if (!out.some((x) => x.id === it.id)) out.push(it);
      }
    }
    return out.slice(0, 3);
  }

  function pickItems(venue, opts, wondersFile) {
    const age = opts.age || "4-5";
    const time = opts.time || "half";
    const interest = (opts.interest || "").trim();
    const need = TIME_N[time] || TIME_N["90m"] || 6;
    const seed = opts.seed || 1;
    const mode = contentMode(venue);
    const rand = mulberry32(
      hashSeed(venue.slug + "|" + mode + "|" + age + "|" + time + "|" + interest + "|" + seed)
    );

    let sourceItems = venue.items || [];
    if (mode === "wonder" && wondersFile) {
      sourceItems = wonderPool(venue, wondersFile);
    } else if (mode === "hybrid" && wondersFile) {
      // Real venue stops first, then venue-type-safe wonders only
      const icons = filterByAge(venue.items || [], age);
      const wonders = filterByAge(wonderPool(venue, wondersFile), age);
      sourceItems = icons.concat(wonders.filter((w) => !icons.some((i) => i.id === w.id)));
    }

    let pool = filterByAge(sourceItems, age);
    if (!pool.length) pool = sourceItems.slice();

    const ranked = pool
      .map((it, idx) => ({
        it,
        idx,
        score: scoreItem(it, interest) + rand() * 0.01,
      }))
      .sort((a, b) => b.score - a.score || a.idx - b.idx)
      .map((x) => x.it);

    // Guarantee headline stops (route_90m / top items) before any filler wonders
    const anchors = mode === "wonder" ? [] : anchorItems(venue, age);
    const picked = [];
    const seen = new Set();
    for (const a of anchors) {
      if (picked.length >= need) break;
      picked.push(a);
      seen.add(a.id);
    }
    for (const it of ranked) {
      if (picked.length >= need) break;
      if (seen.has(it.id)) continue;
      picked.push(it);
      seen.add(it.id);
    }
    if (picked.length < need) {
      for (const it of sourceItems) {
        if (picked.length >= need) break;
        if (seen.has(it.id)) continue;
        picked.push(it);
        seen.add(it.id);
      }
    }
    return picked.slice(0, need);
  }

  function pickChallenges(challengesFile, venue, opts, selectedItems) {
    const age = opts.age || "4-5";
    const seed = (opts.seed || 1) + 17;
    const rand = mulberry32(hashSeed(venue.slug + "|ch|" + age + "|" + seed));
    const kind = normalizeVenueType(venue);
    const blocked = new Set();
    (selectedItems || []).forEach((it) => (it.tags || []).forEach((t) => blocked.add(t)));

    // Strict venue-type match — never pull zoo-only "night animal" onto a museum sheet
    let pool = (challengesFile.challenges || []).filter((c) => {
      const ages = c.age_fit || AGE_ORDER;
      if (!ages.includes(age)) return false;
      return typeAllows(c.types, kind);
    });

    pool = pool
      .map((c, idx) => {
        const tags = c.tags || [];
        const overlap = tags.filter((t) => blocked.has(t)).length;
        return { c, idx, score: -overlap + rand() };
      })
      .sort((a, b) => b.score - a.score || a.idx - b.idx)
      .map((x) => x.c);

    const out = [];
    const used = new Set();
    for (const c of pool) {
      if (out.length >= 3) break;
      if (used.has(c.id)) continue;
      out.push(c);
      used.add(c.id);
    }
    // Backfill only from type-safe pool (never all challenges)
    for (const c of pool) {
      if (out.length >= 3) break;
      if (!used.has(c.id)) {
        out.push(c);
        used.add(c.id);
      }
    }
    return out.slice(0, 3);
  }

  function missionTitle(venue, name) {
    const n = (name || "").trim();
    if (!n) return `Your Mission at ${venue.name}`;
    const poss = /s$/i.test(n) ? `${n}'` : `${n}'s`;
    return `${poss} Mission at ${venue.name}`;
  }

  function selectMission(venue, challengesFile, options, wondersFile) {
    const opts = Object.assign(defaultOptions(), options || {});
    // Allow time alias from page chips
    if (opts.time === "90m") opts.time = "90m";
    const mode = contentMode(venue);
    const finds = pickItems(venue, opts, wondersFile);
    const challenges = pickChallenges(challengesFile, venue, opts, finds);
    return {
      title: missionTitle(venue, opts.name),
      venueName: venue.name,
      slug: venue.slug,
      age: opts.age,
      ageLabel: AGE_LABELS[opts.age] || opts.age,
      time: opts.time,
      timeLabel: TIME_LABELS[opts.time] || opts.time,
      interest: opts.interest || "",
      personalized: Boolean((opts.name || "").trim()),
      contentMode: mode,
      finds,
      challenges,
      lastVerified: venue.last_verified || "",
      tagline: venue.tagline || "",
      practical: venue.practical || null,
      media: venue.media || null,
    };
  }

  function interestOptions(venue) {
    const counts = {};
    (venue.items || []).forEach((it) => {
      (it.tags || []).forEach((t) => {
        if (t === "wow") return;
        counts[t] = (counts[t] || 0) + 1;
      });
    });
    return Object.keys(counts)
      .filter((t) => counts[t] >= 1)
      .sort()
      .map((t) => ({ value: t, label: t.replace(/-/g, " ") }));
  }

  function collectTags(venue) {
    return interestOptions(venue);
  }

  root.FPMission = {
    AGE_ORDER,
    AGE_LABELS,
    TIME_N,
    TIME_LABELS,
    defaultOptions,
    contentMode,
    selectMission,
    interestOptions,
    collectTags,
    missionTitle,
    wonderPool,
  };
})(typeof window !== "undefined" ? window : globalThis);
