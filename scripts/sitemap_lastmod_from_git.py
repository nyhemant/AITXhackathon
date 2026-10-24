#!/usr/bin/env python3
"""Set every sitemap <lastmod> to the real git last-change date of that URL's HTML file.

Keeps the URL list and order of static/sitemap.xml exactly as committed and rewrites
only the <lastmod> values, then writes the identical copy to
static/field-pack/sitemap.xml. Run after committing page changes (uncommitted edits
are not seen by git). Added 2026-10-21.

Note: scripts/generate_bdo_seo.py (full run or --sitemap-only) keeps the public
URL list, including /printables/ pages, but lastmod follows the generator's
source-file rule and the rewrite drops <image:image> entries. Re-run
scripts/image_seo.py and then this script afterwards.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
SITE = "https://kidzookit.com"


def file_for(loc: str) -> Path:
    path = loc.replace(SITE, "", 1)
    return STATIC / path.strip("/") / "index.html" if path.endswith("/") else STATIC / path.lstrip("/")


def git_date(p: Path) -> str:
    out = subprocess.check_output(["git", "log", "-1", "--format=%cs", "--", str(p)], cwd=ROOT, text=True).strip()
    if not out:
        raise SystemExit(f"no git history for {p}")
    return out


def main() -> None:
    src = (STATIC / "sitemap.xml").read_text(encoding="utf-8")
    missing = []

    def repl(m):
        loc = m.group(2)
        f = file_for(loc)
        if not f.is_file():
            missing.append(loc)
            return m.group(0)
        return f"{m.group(1)}{loc}{m.group(3)}{git_date(f)}{m.group(5)}"

    out = re.sub(r"(<loc>)([^<]+)(</loc>\s*<lastmod>)([^<]+)(</lastmod>)", repl, src)
    if missing:
        raise SystemExit(f"no file for: {missing}")
    for p in (STATIC / "sitemap.xml", STATIC / "field-pack" / "sitemap.xml"):
        p.write_text(out, encoding="utf-8")
    n = len(re.findall(r"<loc>", out))
    print(f"{n} URLs, lastmods from git; both sitemap copies written", file=sys.stderr)


if __name__ == "__main__":
    main()
