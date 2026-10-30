#!/usr/bin/env python3
"""Submit kidzookit.com URLs to IndexNow (Bing, Yandex, Seznam, Naver...) after a deploy.

Usage (run on the prod box after `git pull --ff-only` + kickstart, once the site is up):
  python3 scripts/indexnow_ping.py --since ORIG_HEAD   # only sitemap URLs whose page file changed
  python3 scripts/indexnow_ping.py --all               # every sitemap URL (e.g. first run)
  add --dry-run to print what would be sent.

Key: INDEXNOW_KEY in src/busyparent_agent/web.py, served at https://kidzookit.com/<key>.txt.
Docs: https://www.indexnow.org/documentation . 200/202 = accepted. Google does not use IndexNow.
Added 2026-10-30.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
SITE = "https://kidzookit.com"
HOST = "kidzookit.com"
ENDPOINT = "https://api.indexnow.org/indexnow"


def indexnow_key() -> str:
    src = (ROOT / "src" / "busyparent_agent" / "web.py").read_text(encoding="utf-8")
    m = re.search(r'^INDEXNOW_KEY = "([0-9a-f]{32})"', src, re.M)
    if not m:
        raise SystemExit("INDEXNOW_KEY not found in web.py")
    return m.group(1)


def sitemap_urls() -> list[str]:
    xml = (STATIC / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>(https://kidzookit\.com/[^<]*)</loc>", xml)


def file_for(loc: str) -> Path:
    path = loc.replace(SITE, "", 1)
    return STATIC / path.strip("/") / "index.html" if path.endswith("/") else STATIC / path.lstrip("/")


def changed_files(since: str) -> set[Path]:
    out = subprocess.check_output(
        ["git", "diff", "--name-only", f"{since}..HEAD", "--", "static"], cwd=ROOT, text=True
    )
    return {(ROOT / line).resolve() for line in out.splitlines() if line.strip()}


def submit(urls: list[str], key: str) -> int:
    body = json.dumps(
        {"host": HOST, "key": key, "keyLocation": f"{SITE}/{key}.txt", "urlList": urls}
    ).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8", "User-Agent": "KidZooKitCheck-IndexNow/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        print(f"IndexNow HTTP {e.code}: {e.read()[:300]!r}", file=sys.stderr)
        return e.code


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true")
    g.add_argument("--since", help="git rev; submit sitemap URLs whose page file changed since it")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    key = indexnow_key()
    urls = sitemap_urls()
    if args.since:
        changed = changed_files(args.since)
        urls = [u for u in urls if file_for(u).resolve() in changed]
    print(f"{len(urls)} URL(s) to submit", file=sys.stderr)
    if not urls:
        return 0
    if args.dry_run:
        print("\n".join(urls))
        return 0
    worst = 200
    for i in range(0, len(urls), 10000):
        status = submit(urls[i : i + 10000], key)
        print(f"batch {i // 10000 + 1}: HTTP {status}", file=sys.stderr)
        if status not in (200, 202):
            worst = status
    return 0 if worst in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
