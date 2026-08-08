/**
 * Field Trip Kit — deterministic mission composition (no network, no LLM).
 * Browser: window.FPMission
 * Node (SEO build): load via vm
 */
(function (root) {
  const AGE_ORDER = ["2-3", "4-5", "6-8", "9+"];
  const AGE_LABELS = {
    "2-3": "2–3",
    "4-5": "4–5",
    "6-8": "6–8",
    "9+": "9+",
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

  /** Must-include stops: route_90m first, else first print-safe venue items. */
  function anchorItems(venue, age) {
    const items = printSafeItems(venue);
    const byId = Object.fromEntries(items.map((it) => [it.id, it]));
    const out = [];
    const push = (it) => {
      if (!it || out.some((x) => x.id === it.id)) return;
      if (!itemPresenceOk(it, venue)) return;
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
    // If age filter emptied anchors, take raw print-safe route/items
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

    const safeNamed = printSafeItems(venue);
    let sourceItems = safeNamed;
    if (mode === "wonder" && wondersFile) {
      sourceItems = wonderPool(venue, wondersFile);
    } else if (mode === "hybrid" && wondersFile) {
      // Print-safe venue stops first, then venue-type-safe wonders only
      const icons = filterByAge(safeNamed, age);
      const wonders = filterByAge(wonderPool(venue, wondersFile), age);
      sourceItems = icons.concat(wonders.filter((w) => !icons.some((i) => i.id === w.id)));
    } else if (mode === "curated" && wondersFile && safeNamed.length < need) {
      // Top up audited lists with wonders if short — never with unsafe named pack
      const icons = filterByAge(safeNamed, age);
      const wonders = filterByAge(wonderPool(venue, wondersFile), age);
      sourceItems = icons.concat(wonders.filter((w) => !icons.some((i) => i.id === w.id)));
    }

    let pool = filterByAge(sourceItems, age).filter((it) => itemPresenceOk(it, venue) || isWonderItem(it));
    if (!pool.length) {
      // Last resort: type-safe wonders only (never unsafe named animals)
      pool = wondersFile ? filterByAge(wonderPool(venue, wondersFile), age) : [];
    }

    const ranked = pool
      .map((it, idx) => ({
        it,
        idx,
        score: scoreItem(it, interest) + rand() * 0.01,
      }))
      .sort((a, b) => b.score - a.score || a.idx - b.idx)
      .map((x) => x.it);

    // Guarantee headline stops (print-safe route_90m / top items) before fillers
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
      for (const it of wonderPool(venue, wondersFile)) {
        if (picked.length >= need) break;
        if (seen.has(it.id)) continue;
        picked.push(it);
        seen.add(it.id);
      }
    }
    // Apply soft labels for sheet rendering
    return picked.slice(0, need).map((it) => {
      const lab = sheetLabel(it);
      if (!lab || lab === it.label) return it;
      return Object.assign({}, it, { label: lab });
    });
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
    listConfidence,
    itemPresenceOk,
    printSafeItems,
    sheetLabel,
    selectMission,
    interestOptions,
    collectTags,
    missionTitle,
    wonderPool,
  };
})(typeof window !== "undefined" ? window : globalThis);
