#!/usr/bin/env python3
"""NPS hierarchy restyle: fade pictorial grounds, dark road, classy pads."""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

ROOT = Path("/Users/arku/Projects/AITXhackathon/static/field-pack")
VENUES = ROOT / "data/virtual-venues"

FADE = {
    "virtual-zoo": 0.42,
    "virtual-aquarium": 0.34,
    "virtual-nhm": 0.32,
    "virtual-science": 0.38,
}

WASH = {
    "virtual-zoo": 0.18,
    "virtual-aquarium": 0.22,
    "virtual-nhm": 0.24,
    "virtual-science": 0.20,
}


def windy_d(pts: list[tuple[float, float]], amp: float = 28.0) -> str:
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
        bow = amp * (0.55 + min(L, 240) / 320)
        cx1 = x0 + dx * 0.32 + nx * bow * sign
        cy1 = y0 + dy * 0.32 + ny * bow * sign
        cx2 = x0 + dx * 0.68 - nx * bow * 0.4 * sign
        cy2 = y0 + dy * 0.68 - ny * bow * 0.4 * sign
        d.append(f"C{cx1:.1f},{cy1:.1f} {cx2:.1f},{cy2:.1f} {x1:.1f},{y1:.1f}")
    return " ".join(d)


def pad_centers(svg: str, order: list[str]) -> list[tuple[float, float]]:
    blocks = re.findall(
        r'<a[^>]*data-habitat="([^"]+)"[^>]*>.*?</a>',
        svg,
        flags=re.S,
    )
    pos = {}
    for hid, block in re.findall(
        r'<a[^>]*data-habitat="([^"]+)"[^>]*>(.*?)</a>',
        svg,
        flags=re.S,
    ):
        m = re.search(r'class="vz-hit"[^>]*x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"', block)
        if not m:
            continue
        x, y, w, h = map(float, m.groups())
        pos[hid] = (x + w / 2, y + h / 2)
    return [pos[i] for i in order if i in pos]


def gate_center(svg: str, gid: str) -> tuple[float, float] | None:
    m = re.search(
        rf'<g id="{gid}"[^>]*>\s*<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',
        svg,
    )
    if not m:
        return None
    x, y, w, h = map(float, m.groups())
    return (x + w / 2, y + h / 2)


def viewbox(svg: str) -> tuple[float, float]:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    return (float(m.group(1)), float(m.group(2))) if m else (800.0, 800.0)


def inject_defs(svg: str, sat: float) -> str:
    fade = f"""    <filter id="vz-ground-fade" color-interpolation-filters="sRGB">
      <feColorMatrix type="saturate" values="{sat:.2f}"/>
      <feComponentTransfer>
        <feFuncR type="linear" slope="0.90" intercept="0.09"/>
        <feFuncG type="linear" slope="0.90" intercept="0.09"/>
        <feFuncB type="linear" slope="0.90" intercept="0.09"/>
      </feComponentTransfer>
    </filter>"""
    shadow = """    <filter id="pad-shadow" x="-20%" y="-20%" width="140%" height="150%">
      <feDropShadow dx="0" dy="5" stdDeviation="3.2" flood-color="#1a1814" flood-opacity="0.38"/>
    </filter>"""
    svg = re.sub(
        r'<filter id="pad-shadow"[\s\S]*?</filter>',
        shadow.strip(),
        svg,
        count=1,
    )
    if "id=\"vz-ground-fade\"" not in svg:
        svg = svg.replace("</defs>", fade + "\n  </defs>", 1)
    else:
        svg = re.sub(
            r'<filter id="vz-ground-fade"[\s\S]*?</filter>',
            fade.strip(),
            svg,
            count=1,
        )
    return svg


def fade_ground(svg: str, wash: float, w: float, h: float) -> str:
    svg = re.sub(
        r'(<image href="/field-pack/media/virtual-[^"]+/park-ground\.jpg[^"]*"[^>]*)(/>)',
        lambda m: (m.group(1) if "filter=" in m.group(1) else m.group(1) + ' filter="url(#vz-ground-fade)"') + m.group(2),
        svg,
        count=1,
    )
    # if filter already present, leave; else we added it
    if 'filter="url(#vz-ground-fade)"' not in svg:
        svg = re.sub(
            r'(<image href="/field-pack/media/virtual-[^"]+/park-ground\.jpg[^"]*")',
            r'\1 filter="url(#vz-ground-fade)"',
            svg,
            count=1,
        )
    wash_rect = f'<rect class="vz-wash" x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="#f4ead6" opacity="{wash:.2f}" pointer-events="none"/>'
    if 'class="vz-wash"' in svg:
        svg = re.sub(
            r'<rect class="vz-wash"[^/]*/>',
            wash_rect,
            svg,
            count=1,
        )
    else:
        svg = re.sub(
            r'(<image href="/field-pack/media/virtual-[^"]+/park-ground\.jpg[^/]*/>)',
            r"\1\n  " + wash_rect,
            svg,
            count=1,
        )
    return svg


def restyle_silos(svg: str) -> str:
    # unify silo stroke to dark classy rim
    svg = re.sub(
        r'(<rect class="vz-silo"[^>]*)stroke="[^"]*"',
        r'\1stroke="#1f2a2a"',
        svg,
    )
    svg = re.sub(
        r'(<rect class="vz-silo"[^>]*)stroke-width="[^"]*"',
        r'\1stroke-width="2.6"',
        svg,
    )
    # insert white halo behind each silo if missing
    def add_halo(m: re.Match) -> str:
        block = m.group(0)
        if 'class="vz-halo"' in block:
            return block
        sm = re.search(
            r'<rect class="vz-silo" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" rx="([\d.]+)"',
            block,
        )
        if not sm:
            return block
        x, y, w, h, rx = map(float, sm.groups())
        halo = (
            f'<rect class="vz-halo" x="{x - 5:.1f}" y="{y - 5:.1f}" '
            f'width="{w + 10:.1f}" height="{h + 10:.1f}" rx="{rx + 4:.1f}"/>\n    '
        )
        return block.replace('<rect class="vz-silo"', halo + '<rect class="vz-silo"', 1)

    return re.sub(r'<a[^>]*class="vz-spot"[^>]*>.*?</a>', add_halo, svg, flags=re.S)


def insert_road(svg: str, d: str) -> str:
    road = (
        f'<g class="vz-road" fill="none" stroke-linecap="round" stroke-linejoin="round">\n'
        f'  <path d="{d}" stroke="#f7f1e4" stroke-width="8"/>\n'
        f'  <path d="{d}" stroke="#3a2a1c" stroke-width="4.2"/>\n'
        f"</g>"
    )
    if 'class="vz-road"' in svg:
        svg = re.sub(r'<g class="vz-road"[\s\S]*?</g>', road, svg, count=1)
    else:
        # sit above wash, under gates/pads
        svg = re.sub(r'(<g id="vz-entry")', road + "\n  \\1", svg, count=1)
    return svg


def restyle_pictorial(kind: str, svg_path: Path, order: list[str]) -> None:
    svg = svg_path.read_text(encoding="utf-8")
    w, h = viewbox(svg)
    svg = inject_defs(svg, FADE[kind])
    svg = fade_ground(svg, WASH[kind], w, h)
    pads = pad_centers(svg, order)
    pts = []
    inn = gate_center(svg, "vz-entry")
    out = gate_center(svg, "vz-exit")
    if inn and pads and math.hypot(inn[0] - pads[0][0], inn[1] - pads[0][1]) < 220:
        pts.append(inn)
    pts.extend(pads)
    if out and pads and math.hypot(out[0] - pads[-1][0], out[1] - pads[-1][1]) < 220:
        pts.append(out)
    d = windy_d(pts, amp=26 if kind != "virtual-nhm" else 18)
    svg = insert_road(svg, d)
    svg = restyle_silos(svg)
    svg_path.write_text(svg, encoding="utf-8")
    print(f"pictorial {kind}: {len(pts)} pts → {svg_path}")


def restyle_parks(svg_path: Path) -> None:
    svg = svg_path.read_text(encoding="utf-8")
    # stronger pad shadow
    svg = re.sub(
        r'<filter id="pad-shadow"[\s\S]*?</filter>',
        """<filter id="pad-shadow" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="5" stdDeviation="3.2" flood-color="#1a1814" flood-opacity="0.38"/>
  </filter>""",
        svg,
        count=1,
    )
    # dark solid road (keep existing d)
    svg = re.sub(
        r'(<path d="[^"]+" fill="none" stroke="#f7e2b2"[^/]*)/>',
        lambda m: m.group(0)
        .replace('stroke="#f7e2b2"', 'stroke="#f7f1e4"')
        .replace('stroke-width="10"', 'stroke-width="8"')
        .replace(' opacity="0.95"', ""),
        svg,
        count=1,
    )
    svg = re.sub(
        r'(<path d="[^"]+" fill="none" stroke="#c45c26"[^/]*)/>',
        lambda m: m.group(0)
        .replace('stroke="#c45c26"', 'stroke="#3a2a1c"')
        .replace('stroke-width="3.2"', 'stroke-width="4.2"')
        .replace(' stroke-dasharray="10 8"', ""),
        svg,
        count=1,
    )
    svg = restyle_silos(svg)
    svg_path.write_text(svg, encoding="utf-8")
    print(f"parks → {svg_path}")


def habitat_order(json_path: Path) -> list[str]:
    data = json.loads(json_path.read_text())
    habs = sorted(data["habitats"], key=lambda h: h.get("seq") or 0)
    return [h["id"] for h in habs]


def main() -> None:
    restyle_pictorial("virtual-zoo", ROOT / "media/virtual-zoo/map.svg", habitat_order(VENUES / "virtual-zoo.json"))
    restyle_pictorial(
        "virtual-aquarium",
        ROOT / "media/virtual-aquarium/map.svg",
        habitat_order(VENUES / "virtual-aquarium.json"),
    )
    restyle_pictorial("virtual-nhm", ROOT / "media/virtual-nhm/map.svg", habitat_order(VENUES / "virtual-nhm.json"))
    restyle_pictorial(
        "virtual-science",
        ROOT / "media/virtual-science/map.svg",
        habitat_order(VENUES / "virtual-science.json"),
    )
    restyle_parks(ROOT / "media/virtual-parks/map.svg")


if __name__ == "__main__":
    main()
