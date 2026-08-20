"""Kit-tier badge + freshness mailto for Field Trip Kit place pages.

Honesty rule: Verified only when existing venue JSON already has
`list_confidence == "audited"` AND a real `last_presence_audit` date.
Every other venue is a Starter list. Do not invent dates or slugs.
"""

from __future__ import annotations

import re
from urllib.parse import quote

FRESHNESS_MAIL = "hello@1less.app"
FRESHNESS_PROMPT = "Was this list accurate?"
FRESHNESS_ACCURATE = "accurate"
FRESHNESS_CHANGED = "something changed"
KIT_LABEL_STARTER = "Starter list"
KIT_LABEL_VERIFIED_PREFIX = "Verified kit · checked "

# `list_confidence: audited` is the existing hand-picked / presence-checked flag.
# `status: verified` is on every scaffolded venue and is not a depth signal.
VERIFIED_CONFIDENCE = "audited"
CHECKED_DATE_FIELD = "last_presence_audit"

_MONTH_ABBR = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)
_DATE_PREFIX = re.compile(r"^(\d{4})-(\d{2})(?:-\d{2})?")


def esc(s: str) -> str:
    return (
        str(s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def checked_month_label(raw: str) -> str:
    """Format an existing YYYY-MM or YYYY-MM-DD as 'Mon YYYY'. Empty if unreadable."""
    m = _DATE_PREFIX.match(str(raw or "").strip())
    if not m:
        return ""
    year = int(m.group(1))
    month = int(m.group(2))
    if month < 1 or month > 12:
        return ""
    return f"{_MONTH_ABBR[month - 1]} {year}"


def kit_tier_label(mission_venue: dict | None) -> str:
    """Two labels only. Skip Verified when the audited flag has no real date."""
    venue = mission_venue or {}
    if (venue.get("list_confidence") or "") == VERIFIED_CONFIDENCE:
        month = checked_month_label(venue.get(CHECKED_DATE_FIELD) or "")
        if month:
            return f"{KIT_LABEL_VERIFIED_PREFIX}{month}"
    return KIT_LABEL_STARTER


def kit_tier_kind(label: str) -> str:
    return "verified" if label.startswith(KIT_LABEL_VERIFIED_PREFIX) else "starter"


def status_chip_html(mission_venue: dict | None) -> str:
    label = kit_tier_label(mission_venue)
    kind = kit_tier_kind(label)
    return f'<p class="seo-checked seo-checked-{kind}">{esc(label)}</p>'


def print_status_line(mission_venue: dict | None) -> str:
    """Same two labels as the place-page chip — used in the print header."""
    return kit_tier_label(mission_venue)


def freshness_mailto(slug: str, kind: str) -> str:
    slug = str(slug or "").strip()
    if kind == "accurate":
        subject = f"Field Trip Kit · {slug} · {FRESHNESS_ACCURATE}"
    else:
        subject = f"Field Trip Kit · {slug} · {FRESHNESS_CHANGED}"
    return f"mailto:{FRESHNESS_MAIL}?subject={quote(subject, safe='')}"


def freshness_links_html(slug: str) -> str:
    slug = str(slug or "").strip()
    if not slug:
        return ""
    return (
        f'<a href="{esc(freshness_mailto(slug, "accurate"))}">{esc(FRESHNESS_ACCURATE)}</a>'
        f" · "
        f'<a href="{esc(freshness_mailto(slug, "changed"))}">{esc(FRESHNESS_CHANGED)}</a>'
    )


def freshness_html(slug: str, extra_class: str = "") -> str:
    links = freshness_links_html(slug)
    if not links:
        return ""
    cls = "seo-freshness" + (f" {extra_class}" if extra_class else "")
    return f'<p class="{esc(cls)}">{esc(FRESHNESS_PROMPT)} {links}</p>'


def freshness_span_html(slug: str, extra_class: str = "ms-freshness") -> str:
    links = freshness_links_html(slug)
    if not links:
        return ""
    cls = extra_class or "ms-freshness"
    return f'<span class="{esc(cls)}">{esc(FRESHNESS_PROMPT)} {links}</span>'
