/**
 * Field Trip Kit — deterministic mission composition (no network, no LLM).
 * Browser: window.FPMission
 * Node (SEO build): load via vm
 */
(function (root) {
  /**
   * Audience bands (UI chips). Internal keys stay short for data compatibility.
   * 2-3  → Little kids 2–4 (shorter, play-first sheet)
   * 4-5  → Kids 5–8
   * 6-8  → Big kids 9–12
   * adult → Solo adults / young tourists (not a parenting sheet)
   * Legacy "9+" in item age_fit maps to big kids + adults.
   */
  const AGE_ORDER = ["2-3", "4-5", "6-8", "adult"];
  const AGE_LABELS = {
    "2-3": "Little · 2–4",
    "4-5": "Kids · 5–8",
    "6-8": "Big · 9–12",
    adult: "Adults",
    // legacy display if stored mid-migrate
    "9+": "Adults",
  };
  const AGE_CHIP_LABELS = {
    "2-3": "2–4",
    "4-5": "5–8",
    "6-8": "9–12",
    adult: "Adults",
  };
  const TIME_N = { "1hr": 4, half: 6, full: 8, "90m": 4 };
  const TIME_LABELS = {
    "1hr": "~1 hr",
    "90m": "~90 min",
    half: "Half day",
    full: "Full day",
  };

  function normalizeAge(age) {
    const a = String(age || "4-5");
    if (a === "9+" || a === "adults" || a === "solo") return "adult";
    if (AGE_ORDER.includes(a)) return a;
    return "4-5";
  }

  function isAdult(age) {
    return normalizeAge(age) === "adult";
  }

  function isLittle(age) {
    return normalizeAge(age) === "2-3";
  }

  function needCount(time, age) {
    const base = TIME_N[time] || TIME_N.half || 6;
    const a = normalizeAge(age);
    if (a === "2-3") return Math.max(3, base - 2); // half → 4, shorter attention
    if (a === "adult") return Math.min(10, base + 1); // half → 7, denser solo day
    return base;
  }

  function defaultOptions() {
    return { age: "4-5", time: "half", interest: "", name: "", seed: 1 };
  }

  function contentMode(venue) {
    const m = (venue && venue.content_mode) || "";
    if (m === "wonder" || m === "hybrid" || m === "curated") return m;
    // Scaffolds / unaudited templates: wonder-first (honest long-tail)
    if ((venue && venue.list_confidence) === "template") return "wonder";
    if ((venue && venue.verified_by) === "catalog-scaffold") return "wonder";
    // Owner lists may be curated; plain "research" without content_mode is not a census
    if ((venue && venue.verified_by) === "owner") return "curated";
    if ((venue && venue.list_confidence) === "audited") return "curated";
    return "wonder";
  }

  /** Presence gate — never print a named find we only guessed. */
  const PRESENCE_OK = new Set(["verified", "high"]);
  const PRESENCE_BLOCK = new Set(["absent", "template", "medium"]);

  function listConfidence(venue) {
    const c = (venue && venue.list_confidence) || "";
    if (c === "audited" || c === "partial" || c === "template") return c;
    if ((venue && venue.verified_by) === "owner") return "partial";
    if ((venue && venue.verified_by) === "catalog-scaffold") return "template";
    // Hybrid "research" without a presence audit is template-risk
    if ((venue && venue.content_mode) === "hybrid") return "template";
    return "partial";
  }

  function doNotListSet(venue) {
    const out = new Set();
    for (const row of (venue && venue.do_not_list) || []) {
      if (!row) continue;
      if (typeof row === "string") {
        out.add(row.toLowerCase());
        continue;
      }
      if (row.catalog_id) out.add(String(row.catalog_id).toLowerCase());
      if (row.name) out.add(String(row.name).toLowerCase());
      if (row.id) out.add(String(row.id).toLowerCase());
    }
    return out;
  }

  function isWonderItem(it) {
    if (!it) return false;
    const id = String(it.id || "");
    if (id.startsWith("w_")) return true;
    if (String(it.zone || "").toLowerCase() === "wonder") return true;
    if (it.kind === "wonder") return true;
    return false;
  }

  /**
   * Named animals/exhibits need presence confidence.
   * Wonders always allowed. Grandfather: owner/partial venues may use
   * items without a presence field until Wave A tags them.
   */
  function itemPresenceOk(it, venue) {
    if (!it) return false;
    if (isWonderItem(it)) return true;

    const p = String(it.presence || "").toLowerCase();
    if (p === "absent") return false;

    // Sheet-facing label (soft names win over catalog species)
    const label = String(it.display_label || it.label || it.name || "").toLowerCase();
    const cid = String(it.catalog_id || "").toLowerCase();
    const id = String(it.id || "").toLowerCase();

    // do_not_list blocks by *name* always; catalog_id ban only if label wasn't softened
    for (const row of (venue && venue.do_not_list) || []) {
      if (!row) continue;
      const banName = String((typeof row === "string" ? row : row.name) || "").toLowerCase();
      const banCat = String((typeof row === "object" && row.catalog_id) || "").toLowerCase();
      if (banName && banName.length >= 4 && label.includes(banName)) return false;
      // catalog_id ban: skip when presence is verified/high and label differs from ban name
      if (banCat && cid === banCat) {
        if (PRESENCE_OK.has(p) && banName && !label.includes(banName)) {
          /* photo reuse OK — e.g. catalog african-penguin + label "Penguin" */
        } else if (!PRESENCE_OK.has(p)) {
          return false;
        } else if (!banName) {
          return false;
        }
      }
    }

    if (PRESENCE_BLOCK.has(p)) return false;
    if (PRESENCE_OK.has(p)) return true;

    // No presence field yet
    const conf = listConfidence(venue);
    if (conf === "audited") return true; // venue-level audit without per-item tags
    if (conf === "template") return false;
    // partial (owner / museum halls): allow until per-item audit lands
    if (conf === "partial") return true;
    return false;
  }

  function printSafeItems(venue) {
    return (venue.items || []).filter((it) => itemPresenceOk(it, venue));
  }

  /** Prefer display_label (soft species name) on sheets. */
  function sheetLabel(it) {
    if (!it) return "";
    return (it.display_label || it.label || it.name || "").trim();
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

  function scoreItem(item, interest, age) {
    let s = 0;
    const tags = item.tags || [];
    const a = normalizeAge(age);
    if (interest && tags.includes(interest)) s += 2;
    if (tags.includes("wow")) s += 1;
    if (item.zone) s += 1;

    const lab = String(item.label || item.display_label || item.id || "").toLowerCase();
    if (a === "2-3") {
      // Little kids: play / reset / easy wow — not long reads
      if (tags.includes("kids") || tags.includes("play")) s += 3;
      if (tags.includes("rest") || tags.includes("hands")) s += 2;
      if (tags.includes("read")) s -= 2;
      if (/toddler|early explor|children|kids zoo|farm|playground|garden|tower|climb|splash|water play/.test(lab)) {
        s += 2.5;
      }
      if (/planetarium|label|evolution|history hall/.test(lab)) s -= 1.5;
    } else if (a === "4-5") {
      if (tags.includes("play") || tags.includes("hands")) s += 1;
      if (tags.includes("wow")) s += 0.5;
    } else if (a === "6-8") {
      if (tags.includes("read") || tags.includes("wow")) s += 1;
      if (tags.includes("kids") && tags.includes("rest") && !tags.includes("wow")) s -= 1;
    } else if (a === "adult") {
      // Solo adults: signature stops, not toddler pens
      if (tags.includes("kids") && tags.includes("rest") && !tags.includes("wow")) s -= 4;
      if (tags.includes("kids") && !tags.includes("wow") && !tags.includes("big")) s -= 2;
      if (tags.includes("wow") || tags.includes("big")) s += 2;
      if (/toddler|early explor|children's zoo|quiet corner|free explore/.test(lab)) s -= 3;
      if (/submarine|storms|dinosaur|gorilla|elephant|panda|planetarium|tower|tunnel/.test(lab)) s += 1.5;
    }
    return s;
  }

  /** Does this item belong on a sheet for the selected audience? */
  function itemFitsAge(it, age) {
    if (!it) return false;
    const a = normalizeAge(age);
    const fit = it.age_fit;
    const tags = it.tags || [];
    const lab = String(it.label || it.id || "").toLowerCase();

    if (a === "adult") {
      // Drop toddler-only and pure little-kid reset stops
      if (fit && fit.length && fit.every((x) => x === "2-3")) return false;
      if (/toddler|early explor|quiet corner/.test(lab)) return false;
      if (tags.includes("kids") && tags.includes("rest") && !tags.includes("wow") && !tags.includes("big")) {
        return false;
      }
      return true;
    }

    // No age_fit → allow all kid bands (legacy data)
    if (!fit || !fit.length) return true;

    if (a === "2-3") {
      // Little: must be ok for 2-3, OR explicitly play/kids tagged even if age_fit missed 2-3
      if (fit.includes("2-3")) return true;
      if ((tags.includes("kids") || tags.includes("play")) && fit.includes("4-5")) return true;
      return false;
    }
    if (a === "4-5") {
      return fit.includes("4-5") || fit.includes("6-8") || fit.includes("2-3");
    }
    if (a === "6-8") {
      // Big kids: older bands; still allow 4-5 staples
      return fit.includes("6-8") || fit.includes("9+") || fit.includes("4-5");
    }
    return fit.includes(a);
  }

  function filterByAge(items, age) {
    return (items || []).filter((it) => itemFitsAge(it, age));
  }

  function simplifyOneLiner(text, age) {
    const t = String(text || "").trim();
    if (!t) return isLittle(age) ? "Go see it together." : "";
    if (!isLittle(age)) return t;
    const part = t.split(/[.—]/)[0].trim();
    if (part.length <= 42) return part;
    return part.slice(0, 40).trim() + "…";
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

  /** Must-include stops: route_90m first, else first print-safe venue items. */
  function anchorItems(venue, age) {
    const a = normalizeAge(age);
    const items = printSafeItems(venue);
    const byId = Object.fromEntries(items.map((it) => [it.id, it]));
    const out = [];
    const push = (it) => {
      if (!it || out.some((x) => x.id === it.id)) return;
      if (!itemPresenceOk(it, venue)) return;
      if (!itemFitsAge(it, a)) return;
      out.push(it);
    };
    for (const id of venue.route_90m || []) {
      if (out.length >= 3) break;
      push(byId[id]);
    }
    // Little kids: if route anchors are all "hard", still keep 1–2 icons then fill play stops later
    if (!out.length || (a === "2-3" && out.length < 2)) {
      const rankedLittle = filterByAge(items, a)
        .slice()
        .sort((x, y) => scoreItem(y, "", a) - scoreItem(x, "", a));
      for (const it of rankedLittle) {
        if (out.length >= 3) break;
        push(it);
      }
    }
    if (!out.length) {
      for (const it of filterByAge(items, a)) {
        if (out.length >= 3) break;
        push(it);
      }
    }
    // If age filter emptied anchors, take raw print-safe route/items that fit
    if (!out.length) {
      for (const id of venue.route_90m || []) {
        if (out.length >= 3) break;
        const it = byId[id];
        if (it && itemFitsAge(it, a)) out.push(it);
      }
      for (const it of items) {
        if (out.length >= 3) break;
        if (!out.some((x) => x.id === it.id) && itemFitsAge(it, a)) out.push(it);
      }
    }
    return out.slice(0, a === "2-3" ? 2 : 3);
  }

  function pickItems(venue, opts, wondersFile) {
    const age = normalizeAge(opts.age || "4-5");
    const time = opts.time || "half";
    const interest = (opts.interest || "").trim();
    const need = needCount(time, age);
    const seed = opts.seed || 1;
    const mode = contentMode(venue);
    const rand = mulberry32(
      hashSeed(venue.slug + "|" + mode + "|" + age + "|" + time + "|" + interest + "|" + seed)
    );

    const safeNamed = printSafeItems(venue);
    let sourceItems = safeNamed;
    if (mode === "wonder" && wondersFile) {
      sourceItems = wonderPool(venue, wondersFile);
    } else if (mode === "hybrid" && wondersFile) {
      const icons = filterByAge(safeNamed, age);
      const wonders = filterByAge(wonderPool(venue, wondersFile), age);
      sourceItems = icons.concat(wonders.filter((w) => !icons.some((i) => i.id === w.id)));
    } else if (mode === "curated" && wondersFile && filterByAge(safeNamed, age).length < need) {
      const icons = filterByAge(safeNamed, age);
      const wonders = filterByAge(wonderPool(venue, wondersFile), age);
      sourceItems = icons.concat(wonders.filter((w) => !icons.some((i) => i.id === w.id)));
    }

    let pool = filterByAge(sourceItems, age).filter((it) => itemPresenceOk(it, venue) || isWonderItem(it));
    if (!pool.length) {
      pool = wondersFile ? filterByAge(wonderPool(venue, wondersFile), age) : [];
    }

    const ranked = pool
      .map((it, idx) => ({
        it,
        idx,
        score: scoreItem(it, interest, age) + rand() * 0.01,
      }))
      .sort((a, b) => b.score - a.score || a.idx - b.idx)
      .map((x) => x.it);

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
    if (picked.length < need && wondersFile) {
      for (const it of filterByAge(wonderPool(venue, wondersFile), age)) {
        if (picked.length >= need) break;
        if (seen.has(it.id)) continue;
        picked.push(it);
        seen.add(it.id);
      }
    }
    return picked.slice(0, need).map((it) => {
      const lab = sheetLabel(it);
      const line = simplifyOneLiner(it.one_liner, age);
      const out = Object.assign({}, it);
      if (lab && lab !== it.label) out.label = lab;
      if (line) out.one_liner = line;
      return out;
    });
  }

  function challengeFitsAge(c, age) {
    const a = normalizeAge(age);
    const fit = c.age_fit || [];
    if (!fit.length) return a !== "adult";
    // Explicit bands only — don't leak "read a kid label" into little/kids
    if (a === "adult") return fit.includes("adult");
    if (a === "2-3") return fit.includes("2-3");
    if (a === "4-5") return fit.includes("4-5");
    if (a === "6-8") return fit.includes("6-8") || fit.includes("9+");
    return fit.includes(a);
  }

  function pickChallenges(challengesFile, venue, opts, selectedItems) {
    const age = normalizeAge(opts.age || "4-5");
    const seed = (opts.seed || 1) + 17;
    const rand = mulberry32(hashSeed(venue.slug + "|ch|" + age + "|" + seed));
    const kind = normalizeVenueType(venue);
    const blocked = new Set();
    (selectedItems || []).forEach((it) => (it.tags || []).forEach((t) => blocked.add(t)));

    let pool = (challengesFile.challenges || []).filter((c) => {
      if (!challengeFitsAge(c, age)) return false;
      return typeAllows(c.types, kind);
    });

    // Adult: never baby-talk challenges
    if (age === "adult") {
      pool = pool.filter((c) => (c.age_fit || []).includes("adult") || (c.tags || []).includes("adult"));
    }

    pool = pool
      .map((c, idx) => {
        const tags = c.tags || [];
        const overlap = tags.filter((t) => blocked.has(t)).length;
        let bonus = 0;
        if (age === "2-3" && (tags.includes("rest") || tags.includes("play") || tags.includes("color"))) bonus += 1;
        if (age === "adult" && tags.includes("adult")) bonus += 2;
        return { c, idx, score: -overlap + bonus + rand() };
      })
      .sort((a, b) => b.score - a.score || a.idx - b.idx)
      .map((x) => x.c);

    const out = [];
    const used = new Set();
    const want = age === "adult" ? 3 : 3;
    for (const c of pool) {
      if (out.length >= want) break;
      if (used.has(c.id)) continue;
      out.push(c);
      used.add(c.id);
    }
    for (const c of pool) {
      if (out.length >= want) break;
      if (!used.has(c.id)) {
        out.push(c);
        used.add(c.id);
      }
    }
    return out.slice(0, want);
  }

  function missionTitle(venue, name, age) {
    if (isAdult(age)) {
      const n = (name || "").trim();
      if (n) return `${n} · ${venue.name}`;
      return `Solo day at ${venue.name}`;
    }
    const n = (name || "").trim();
    if (!n) return `Your Mission at ${venue.name}`;
    const poss = /s$/i.test(n) ? `${n}'` : `${n}'s`;
    return `${poss} Mission at ${venue.name}`;
  }

  function selectMission(venue, challengesFile, options, wondersFile) {
    const opts = Object.assign(defaultOptions(), options || {});
    opts.age = normalizeAge(opts.age);
    if (opts.time === "90m") opts.time = "90m";
    // Adults don't use kid name personalization the same way
    if (opts.age === "adult") opts.name = (opts.name || "").trim();
    const mode = contentMode(venue);
    const finds = pickItems(venue, opts, wondersFile);
    const challenges = pickChallenges(challengesFile, venue, opts, finds);
    const adult = opts.age === "adult";
    return {
      title: missionTitle(venue, opts.name, opts.age),
      venueName: venue.name,
      slug: venue.slug,
      age: opts.age,
      ageLabel: AGE_LABELS[opts.age] || opts.age,
      time: opts.time,
      timeLabel: TIME_LABELS[opts.time] || opts.time,
      interest: opts.interest || "",
      personalized: Boolean((opts.name || "").trim()),
      contentMode: mode,
      audience: adult ? "adult" : "kid",
      findsHeading: adult ? "Don't miss" : isLittle(opts.age) ? "Go see" : "Find these",
      bonusHeading: adult ? "While you're there" : "Bonus",
      nameLabel: adult ? "Your name (optional)" : "Kid name",
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
    AGE_CHIP_LABELS,
    TIME_N,
    TIME_LABELS,
    defaultOptions,
    normalizeAge,
    isAdult,
    contentMode,
    listConfidence,
    itemPresenceOk,
    itemFitsAge,
    printSafeItems,
    sheetLabel,
    selectMission,
    interestOptions,
    collectTags,
    missionTitle,
    wonderPool,
  };
})(typeof window !== "undefined" ? window : globalThis);
