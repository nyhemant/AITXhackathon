#!/usr/bin/env node
/** Apply verified visitor_map_url entries from scripts/data/visitor_map_images.json */
const fs = require("fs");
const path = require("path");
const ROOT = path.join(__dirname, "..");
const MAPS = JSON.parse(fs.readFileSync(path.join(__dirname, "data/visitor_map_images.json"), "utf8"));
const DIR = path.join(ROOT, "static/field-pack/data/venues");
let n = 0;
for (const [slug, url] of Object.entries(MAPS)) {
  const fp = path.join(DIR, slug + ".json");
  if (!fs.existsSync(fp)) {
    console.warn("miss", slug);
    continue;
  }
  const j = JSON.parse(fs.readFileSync(fp, "utf8"));
  const media = { ...(j.media || {}) };
  media.visitor_map_url = url;
  media.visitor_map_kind = "image";
  if (!media.visitor_map_page) media.visitor_map_page = j.official_url || "";
  if (!media.map_attribution) media.map_attribution = `Official map · ${j.name || slug}`;
  j.media = media;
  fs.writeFileSync(fp, JSON.stringify(j, null, 2) + "\n");
  n++;
}
console.log("applied", n);
