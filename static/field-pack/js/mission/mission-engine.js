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

  function wonderPool(venue, wondersFile) {
    const type = (venue.type || "zoo").toLowerCase();
    const list = (wondersFile && wondersFile.wonders) || [];
    return list.filter((w) => {
      const types = w.types || [];
      if (!types.length) return true;
      return types.includes(type) || (type === "safari_zoo" && types.includes("zoo"));
    });
  }

  function pickItems(venue, opts, wondersFile) {
    const age = opts.age || "4-5";
    const time = opts.time || "half";
    const interest = (opts.interest || "").trim();
    const need = TIME_N[time] || TIME_N["90m"] || 6;
    const seed = opts.seed || 1;
    const mode = contentMode(venue);
    const rand = mulberry32(hashSeed(venue.slug + "|" + mode + "|" + age + "|" + time + "|" + interest + "|" + seed));

    let sourceItems = venue.items || [];
    if (mode === "wonder" && wondersFile) {
      sourceItems = wonderPool(venue, wondersFile);
    } else if (mode === "hybrid" && wondersFile) {
      // Prefer real icons first, then fill with wonders
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

    let picked = ranked.slice(0, need);
    if (picked.length < need) {
      const rest = sourceItems.filter((it) => !picked.some((p) => p.id === it.id));
      picked = picked.concat(rest.slice(0, need - picked.length));
    }
    return picked.slice(0, need);
  }

  function pickChallenges(challengesFile, venue, opts, selectedItems) {
    const age = opts.age || "4-5";
    const seed = (opts.seed || 1) + 17;
    const rand = mulberry32(hashSeed(venue.slug + "|ch|" + age + "|" + seed));
    const type = (venue.type || "zoo").toLowerCase();
    const blocked = new Set();
    (selectedItems || []).forEach((it) => (it.tags || []).forEach((t) => blocked.add(t)));

    let pool = (challengesFile.challenges || []).filter((c) => {
      const types = c.types || [];
      const ages = c.age_fit || AGE_ORDER;
      if (!ages.includes(age)) return false;
      if (types.length && !types.includes(type) && !types.includes("zoo")) {
        // museum-only challenges stay museum; aquarium types strict
        if (type === "museum") return types.includes("museum");
        if (type === "aquarium") return types.includes("aquarium");
        return types.includes(type);
      }
      return types.includes(type) || types.includes("zoo") || types.length === 0;
    });

    // Prefer challenges that don't heavily overlap item tags
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
    // backfill any
    for (const c of challengesFile.challenges || []) {
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
