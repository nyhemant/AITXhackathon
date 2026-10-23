#!/usr/bin/env python3
"""Sitewide header menu (2026-10-23): add Zoos / Aquariums / Museums / Parks hub links
right under "Places" in every page's shared hamburger menu (#shell-menu), and bump
shell.css to v=13 (styles for .shell-menu-sub). Idempotent (kz-menu:hubs markers).
/start/ uses its own start-menu and is not touched.
generate_bdo_seo.py does not emit these links: re-run after ANY generator run:
    python3 scripts/shell_menu_hubs.py"""
import re
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "static"
HUBS = (("/field-pack/zoos/", "Zoos"), ("/field-pack/aquariums/", "Aquariums"),
        ("/field-pack/museums/", "Museums"), ("/field-pack/national-parks/", "Parks"))
CSS_OLD, CSS_NEW = "/shell/shell.css?v=12", "/shell/shell.css?v=13"


def block(page_href):
    lines = ["<!-- kz-menu:hubs -->"]
    for href, label in HUBS:
        cur = ' aria-current="page"' if href == page_href else ""
        lines.append(f'<a class="shell-menu-sub" href="{href}"{cur} role="menuitem" data-related-link="menu_hub">{label}</a>')
    lines.append("<!-- /kz-menu:hubs -->")
    return lines


def page_href(p):
    rel = p.relative_to(STATIC).as_posix()
    return "/" + rel[: -len("index.html")] if rel.endswith("index.html") else "/" + rel


def main():
    n = 0
    for p in sorted(STATIC.rglob("*.html")):
        s = p.read_text(encoding="utf-8")
        if 'id="shell-menu"' not in s:
            continue
        t = re.sub(r"\n[ \t]*<!-- kz-menu:hubs -->.*?<!-- /kz-menu:hubs -->", "", s, flags=re.S)
        m = re.search(r'\n([ \t]*)(<a href="/field-pack/"[^>]*role="menuitem">Places</a>)', t)
        if not m:
            continue
        ind = m.group(1)
        ins = "".join("\n" + ind + l for l in block(page_href(p)))
        t = t[: m.end()] + ins + t[m.end():]
        t = t.replace(CSS_OLD, CSS_NEW)
        if t != s:
            p.write_text(t, encoding="utf-8")
            n += 1
    print("pages updated:", n)


if __name__ == "__main__":
    main()
