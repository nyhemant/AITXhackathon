#!/usr/bin/env python3
"""Build the Virtual Field Trip CONUS parks SVG (accurate lat/lon + windy road)."""
from __future__ import annotations

import json
import math
from pathlib import Path

GEO = Path("/tmp/us-states.json")
OUT = Path("/Users/arku/Projects/AITXhackathon/static/field-pack/media/virtual-parks/map.svg")

# Albers Equal Area CONUS (standard parallels 29.5 / 45.5, origin 37.5N 96W)
LAT0 = math.radians(37.5)
LON0 = math.radians(-96.0)
SP1 = math.radians(29.5)
SP2 = math.radians(45.5)
N = 0.5 * (math.sin(SP1) + math.sin(SP2))
C = math.cos(SP1) ** 2 + 2 * N * math.sin(SP1)
RHO0 = math.sqrt(C - 2 * N * math.sin(LAT0)) / N

SKIP = {"Alaska", "Hawaii", "Puerto Rico"}

# Road-trip order: famous + scattered, non-overlapping, lower 48.
PARKS = [
    {"id": "acadia", "label": "Acadia", "lat": 44.3386, "lon": -68.2733, "short": "Acadia"},
    {"id": "great-smoky-mountains", "label": "Smokies", "lat": 35.6532, "lon": -83.5070, "short": "Smokies"},
    {"id": "everglades", "label": "Everglades", "lat": 25.2866, "lon": -80.8987, "short": "Everglades"},
    {"id": "big-bend", "label": "Big Bend", "lat": 29.1275, "lon": -103.2425, "short": "Big Bend"},
    {"id": "grand-canyon", "label": "Grand Canyon", "lat": 36.0544, "lon": -112.1401, "short": "Grand Canyon"},
    {"id": "yosemite", "label": "Yosemite", "lat": 37.7459, "lon": -119.5936, "short": "Yosemite"},
    {"id": "olympic", "label": "Olympic", "lat": 48.0414, "lon": -123.4186, "short": "Olympic"},
    {"id": "yellowstone", "label": "Yellowstone", "lat": 44.4605, "lon": -110.8281, "short": "Yellowstone"},
    {"id": "rocky-mountain", "label": "Rocky Mtn", "lat": 40.3428, "lon": -105.6836, "short": "Rocky Mtn"},
    {"id": "badlands", "label": "Badlands", "lat": 43.8554, "lon": -102.3397, "short": "Badlands"},
]

W, H = 1000, 620
PAD = 36
PHOTO = 72


def albers(lat: float, lon: float) -> tuple[float, float]:
    la = math.radians(lat)
    lo = math.radians(lon)
    theta = N * (lo - LON0)
    rho = math.sqrt(C - 2 * N * math.sin(la)) / N
    x = rho * math.sin(theta)
    y = RHO0 - rho * math.cos(theta)
    return x, y


def rings_of(geom) -> list[list[list[float]]]:
    t = geom["type"]
    if t == "Polygon":
        return geom["coordinates"]
    if t == "MultiPolygon":
        out = []
        for poly in geom["coordinates"]:
            out.extend(poly)
        return out
    return []


def fit_transform(pts: list[tuple[float, float]]):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    sx = (W - 2 * PAD) / (maxx - minx)
    sy = (H - 2 * PAD) / (maxy - miny)
    s = min(sx, sy)
    # Center in the leftover space
    ox = PAD + ((W - 2 * PAD) - (maxx - minx) * s) / 2
    oy = PAD + ((H - 2 * PAD) - (maxy - miny) * s) / 2

    def xf(x, y):
        return ox + (x - minx) * s, H - (oy + (y - miny) * s)

    return xf


def path_from_ring(ring, xf) -> str:
    if len(ring) < 3:
        return ""
    parts = []
    for i, (lon, lat) in enumerate(ring):
        x, y = xf(*albers(lat, lon))
        parts.append(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}")
    parts.append("Z")
    return "".join(parts)


def dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def windy_d(pts: list[tuple[float, float]], amp: float = 34.0) -> str:
    """Cubic path through pts with alternating perpendicular bows."""
    if len(pts) < 2:
        return ""
    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        sign = 1 if i % 2 == 0 else -1
        # stronger bow on long hops so the road reads as a trip, not a ruler
        bow = amp * (0.7 + min(L, 280) / 280)
        cx1 = x0 + dx * 0.32 + nx * bow * sign
        cy1 = y0 + dy * 0.32 + ny * bow * sign
        cx2 = x0 + dx * 0.68 - nx * bow * 0.45 * sign
        cy2 = y0 + dy * 0.68 - ny * bow * 0.45 * sign
        d.append(f"C{cx1:.1f},{cy1:.1f} {cx2:.1f},{cy2:.1f} {x1:.1f},{y1:.1f}")
    return " ".join(d)


def pad_offset(i: int, parks: list[dict]) -> tuple[float, float]:
    """Nudge photo pad so neighbors don't overlap; pin stays on true lat/lon."""
    me = parks[i]
    r = PHOTO + 10
    ox = oy = 0.0
    for j, other in enumerate(parks):
        if i == j:
            continue
        d = dist((me["x"], me["y"]), (other["x"], other["y"]))
        if d >= r:
            continue
        # push this pad away from the neighbor
        ux = (me["x"] - other["x"]) / (d or 1)
        uy = (me["y"] - other["y"]) / (d or 1)
        need = (r - d) * 0.6
        ox += ux * need
        oy += uy * need
    # Prefer pushing pads inland / toward empty map, clamp so they stay on canvas
    return ox, oy


def main() -> None:
    data = json.loads(GEO.read_text())
    land_paths = []
    state_paths = []
    sample_pts = []
    for feat in data["features"]:
        name = (feat.get("properties") or {}).get("name")
        if name in SKIP:
            continue
        geom = feat["geometry"]
        for ring in rings_of(geom):
            # skip tiny island rings
            if len(ring) < 8:
                continue
            for lon, lat in ring[:: max(1, len(ring) // 80)]:
                sample_pts.append(albers(lat, lon))
    xf = fit_transform(sample_pts)

    for feat in data["features"]:
        name = (feat.get("properties") or {}).get("name")
        if name in SKIP:
            continue
        for idx, ring in enumerate(rings_of(feat["geometry"])):
            if len(ring) < 8:
                continue
            d = path_from_ring(ring, xf)
            if not d:
                continue
            if idx == 0:
                land_paths.append(d)
            state_paths.append(d)

    for p in PARKS:
        p["x"], p["y"] = xf(*albers(p["lat"], p["lon"]))

    # Report pairwise distances (centers)
    print("Park screen positions (Albers → SVG):")
    for p in PARKS:
        print(f"  {p['id']:28s}  {p['x']:7.1f},{p['y']:7.1f}")
    print("Nearest pairs:")
    pairs = []
    for i, a in enumerate(PARKS):
        for b in PARKS[i + 1 :]:
            pairs.append((dist((a["x"], a["y"]), (b["x"], b["y"])), a["id"], b["id"]))
    for d, a, b in sorted(pairs)[:6]:
        print(f"  {d:6.1f}px  {a} — {b}")

    land_svg = "".join(f'<path d="{d}"/>' for d in land_paths)
    state_svg = "".join(f'<path d="{d}"/>' for d in state_paths)
    road = windy_d([(p["x"], p["y"]) for p in PARKS], amp=38)

    # IN just east of Acadia; OUT just east of Badlands
    ac = PARKS[0]
    bd = PARKS[-1]
    in_x, in_y = min(W - 70, ac["x"] + 58), min(H - 36, ac["y"] + 42)
    out_x, out_y = min(W - 70, bd["x"] + 62), max(28, bd["y"] - 48)

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 620" role="img">',
        "<title>National parks road trip. Follow the glowing park on the map of the lower 48.</title>",
        "<defs>",
        '  <clipPath id="vz-photo-clip" clipPathUnits="objectBoundingBox">',
        '    <rect x="0" y="0" width="1" height="1" rx="0.14" ry="0.14"/>',
        "  </clipPath>",
        '  <filter id="pad-shadow" x="-15%" y="-15%" width="130%" height="140%">',
        '    <feDropShadow dx="0" dy="3" stdDeviation="2.2" flood-color="#0a4545" flood-opacity="0.22"/>',
        "  </filter>",
        '  <linearGradient id="water" x1="0" y1="0" x2="0" y2="1">',
        '    <stop offset="0" stop-color="#c9dcea"/>',
        '    <stop offset="1" stop-color="#b7cfe0"/>',
        "  </linearGradient>",
        "</defs>",
        '<rect x="0" y="0" width="1000" height="620" fill="url(#water)"/>',
        f'<g fill="#f4ead6" stroke="#c9b48a" stroke-width="0.8" stroke-linejoin="round">{land_svg}</g>',
        f'<g fill="none" stroke="#d8c9a4" stroke-width="0.55" stroke-linejoin="round" opacity="0.85">{state_svg}</g>',
        f'<path d="{road}" fill="none" stroke="#f7e2b2" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" opacity="0.95"/>',
        f'<path d="{road}" fill="none" stroke="#c45c26" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="10 8"/>',
        f'<g id="vz-entry" class="vz-gate"><rect x="{in_x - 22:.1f}" y="{in_y - 13:.1f}" width="50" height="26" rx="7" fill="#0f5c5c"/><text x="{in_x + 3:.1f}" y="{in_y + 5:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="12" font-weight="700" fill="#fff">IN</text></g>',
        f'<g id="vz-exit" class="vz-gate"><rect x="{out_x - 24:.1f}" y="{out_y - 13:.1f}" width="54" height="26" rx="7" fill="#8a9aaf"/><text x="{out_x + 3:.1f}" y="{out_y + 5:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="12" font-weight="700" fill="#fff">OUT</text></g>',
    ]

    half = PHOTO / 2
    for i, p in enumerate(PARKS):
        ox, oy = pad_offset(i, PARKS)
        cx, cy = p["x"] + ox, p["y"] + oy
        # keep pad on canvas
        cx = min(max(cx, half + 8), W - half - 8)
        cy = min(max(cy, half + 8), H - half - 22)
        x = cx - half
        y = cy - half
        href = f"/field-pack/virtual-field-trip/?tab=parks#habitat={p['id']}"
        photo = f"/field-pack/photos/np-hero-{p['id']}.jpg?v=q3"
        # pin at true location
        parts.append(
            f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="3.4" fill="#0f5c5c" stroke="#fff" stroke-width="1.4"/>'
        )
        if abs(ox) > 2 or abs(oy) > 2:
            parts.append(
                f'<path d="M{p["x"]:.1f},{p["y"]:.1f} L{cx:.1f},{cy:.1f}" fill="none" stroke="#0f5c5c" stroke-width="1.2" opacity="0.45"/>'
            )
        parts.append(
            f'<a href="{href}" id="habitat-{p["id"]}" class="vz-spot" data-habitat="{p["id"]}" aria-label="{p["label"]}">'
        )
        parts.append(f'  <rect class="vz-hit" x="{x:.1f}" y="{y:.1f}" width="{PHOTO}" height="{PHOTO}" fill="transparent"/>')
        parts.append(
            f'  <rect class="vz-silo" x="{x + 3:.1f}" y="{y + 3:.1f}" width="{PHOTO - 6}" height="{PHOTO - 6}" rx="12" fill="#fff" stroke="#0f5c5c" stroke-width="2.4" filter="url(#pad-shadow)"/>'
        )
        parts.append(
            f'  <image href="{photo}" x="{x + 6:.1f}" y="{y + 6:.1f}" width="{PHOTO - 12}" height="{PHOTO - 12}" preserveAspectRatio="xMidYMin slice" clip-path="url(#vz-photo-clip)"/>'
        )
        parts.append("</a>")
        parts.append(
            f'<text x="{cx:.1f}" y="{y + PHOTO + 13:.1f}" text-anchor="middle" font-family="Georgia,serif" font-size="11" font-weight="700" fill="#0a4545">{p["short"]}</text>'
        )

    parts.append("</svg>\n")
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
