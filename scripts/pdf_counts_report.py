#!/usr/bin/env python3
"""Print weekly and per-page printable PDF totals.

Reads pdf-counts-YYYY-MM.json from the counts directory. Stdlib only.
Meant to be run over SSH by the person who owns the counts files.

  python3 scripts/pdf_counts_report.py
  python3 scripts/pdf_counts_report.py --dir ~/.kidzookit/counts
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def counts_dir(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit)
    raw = os.environ.get("KZK_COUNTS_DIR", "").strip()
    if raw:
        return Path(raw)
    return Path.home() / ".kidzookit" / "counts"


def _int(value: object) -> int:
    return value if isinstance(value, int) and value >= 0 else 0


def week_heading(day: str) -> str | None:
    """Monday–Sunday label for a YYYY-MM-DD key. None when the day is not a date."""
    try:
        dt = datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        return None
    monday = dt - timedelta(days=dt.weekday())
    sunday = monday + timedelta(days=6)
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d} ({monday.date().isoformat()} to {sunday.date().isoformat()})"


def load_days(directory: Path) -> dict[str, dict]:
    """Merge every pdf-counts-*.json. Later files add onto the same day."""
    days: dict[str, dict] = {}
    if not directory.is_dir():
        return days
    for path in sorted(directory.glob("pdf-counts-*.json")):
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            print(f"skip {path.name}", file=sys.stderr)
            continue
        if not isinstance(loaded, dict):
            continue
        for day, rows in loaded.items():
            if not isinstance(rows, dict):
                continue
            bucket = days.setdefault(str(day), {})
            for key, row in rows.items():
                if not isinstance(row, dict):
                    continue
                acc = bucket.setdefault(str(key), {"site": 0, "search": 0, "other": 0, "pages": {}})
                for name in ("site", "search", "other"):
                    acc[name] = _int(acc.get(name)) + _int(row.get(name))
                pages = row.get("pages")
                if isinstance(pages, dict):
                    dest = acc.setdefault("pages", {})
                    if not isinstance(dest, dict):
                        dest = {}
                        acc["pages"] = dest
                    for page, count in pages.items():
                        dest[str(page)] = _int(dest.get(page)) + _int(count)
    return days


def format_report(days: dict) -> str:
    weeks: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: defaultdict(lambda: {"site": 0, "search": 0, "other": 0})
    )
    page_totals: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for day, rows in days.items():
        heading = week_heading(str(day))
        if heading is None or not isinstance(rows, dict):
            continue
        for key, row in rows.items():
            if not isinstance(row, dict):
                continue
            acc = weeks[heading][str(key)]
            for name in ("site", "search", "other"):
                acc[name] += _int(row.get(name))
            pages = row.get("pages")
            if isinstance(pages, dict):
                for page, count in pages.items():
                    page_totals[str(page)][str(key)] += _int(count)

    lines = ["Weekly totals"]
    if not weeks:
        lines.append("(no counts)")
    for heading in sorted(weeks):
        lines.append(heading)
        week = weeks[heading]
        keys = sorted(k for k, row in week.items() if row["site"] + row["search"] + row["other"])
        site = search = other = 0
        for key in keys:
            row = week[key]
            total = row["site"] + row["search"] + row["other"]
            site += row["site"]
            search += row["search"]
            other += row["other"]
            lines.append(
                f"  {key}  site={row['site']} search={row['search']} other={row['other']} total={total}"
            )
        lines.append(f"  ALL  site={site} search={search} other={other} total={site + search + other}")

    lines.append("")
    lines.append("Per-page totals")
    pages_sorted = sorted(
        (page, pdfs) for page, pdfs in page_totals.items() if sum(pdfs.values())
    )
    if not pages_sorted:
        lines.append("(no page counts)")
    grand = 0
    for page, pdfs in pages_sorted:
        total = sum(pdfs.values())
        grand += total
        lines.append(f"  {page}  {total}")
        for key in sorted(pdfs):
            if pdfs[key]:
                lines.append(f"    {key}  {pdfs[key]}")
    if pages_sorted:
        lines.append(f"  ALL  {grand}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print weekly and per-page PDF download totals.")
    parser.add_argument(
        "--dir",
        default="",
        help="Counts directory (default: $KZK_COUNTS_DIR or ~/.kidzookit/counts)",
    )
    args = parser.parse_args(argv)
    directory = counts_dir(args.dir or None)
    print(f"Counts directory: {directory}")
    sys.stdout.write(format_report(load_days(directory)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
