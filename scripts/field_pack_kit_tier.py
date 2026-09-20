"""Kit-tier badge + place-list feedback for Field Trip Kit place pages.

Honesty rule: Verified only when existing venue JSON already has
`list_confidence == "audited"` AND a real `last_presence_audit` date.
Every other venue is a Starter list. Do not invent dates or slugs.

Feedback is two-tap (Accurate / Something changed) with GA4 via FPTrack;
mailto is optional only for the changed path.
"""

from __future__ import annotations

import re
from urllib.parse import quote

FRESHNESS_MAIL = "arku2arku@gmail.com"
FRESHNESS_PROMPT = "Was this list accurate?"
FRESHNESS_ACCURATE = "Accurate"
FRESHNESS_CHANGED = "Something changed"
FRESHNESS_THANKS = "Thanks — that helps."
KIT_LABEL_STARTER = "Starter list"
KIT_LABEL_VERIFIED_PREFIX = "We checked the animal list, exhibit names, and map link in "

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
            return f"{KIT_LABEL_VERIFIED_PREFIX}{month}."
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
        subject = f"Field Trip Kit · {slug} · accurate"
    else:
        subject = f"Field Trip Kit · {slug} · something changed"
    return f"mailto:{FRESHNESS_MAIL}?subject={quote(subject, safe='')}"


def freshness_actions_html(slug: str) -> str:
    """Two-tap buttons; changed path keeps optional mailto with place id in subject."""
    slug = str(slug or "").strip()
    if not slug:
        return ""
    mail = esc(freshness_mailto(slug, "changed"))
    return (
        f'<span class="seo-freshness-actions">'
        f'<button type="button" class="seo-freshness-btn" data-feedback="accurate">'
        f"{esc(FRESHNESS_ACCURATE)}</button>"
        f'<button type="button" class="seo-freshness-btn" data-feedback="changed" '
        f'data-mailto="{mail}">{esc(FRESHNESS_CHANGED)}</button>'
        f"</span>"
        f'<span class="seo-freshness-thanks" hidden>{esc(FRESHNESS_THANKS)}</span>'
        f'<span class="seo-freshness-note-wrap" hidden>'
        f'<label class="seo-freshness-note-label" for="place-feedback-note-{esc(slug)}">'
        f"Optional note</label>"
        f'<textarea id="place-feedback-note-{esc(slug)}" class="seo-freshness-note" '
        f'rows="2" maxlength="280" placeholder="What changed? (optional)"></textarea>'
        f'<span class="seo-freshness-note-actions">'
        f'<button type="button" class="seo-freshness-btn seo-freshness-send" '
        f'data-feedback-send="1">Email us</button>'
        f'<button type="button" class="seo-freshness-btn seo-freshness-done" '
        f'data-feedback-done="1">Done</button>'
        f"</span></span>"
    )


def freshness_html(slug: str, extra_class: str = "") -> str:
    actions = freshness_actions_html(slug)
    if not actions:
        return ""
    cls = "seo-freshness" + (f" {extra_class}" if extra_class else "")
    return (
        f'<p class="{esc(cls)}" data-place-feedback data-place-id="{esc(slug)}">'
        f'<span class="seo-freshness-prompt">{esc(FRESHNESS_PROMPT)}</span> '
        f"{actions}</p>"
    )


def freshness_span_html(slug: str, extra_class: str = "ms-freshness") -> str:
    actions = freshness_actions_html(slug)
    if not actions:
        return ""
    cls = extra_class or "ms-freshness"
    return (
        f'<span class="{esc(cls)}" data-place-feedback data-place-id="{esc(slug)}">'
        f'<span class="seo-freshness-prompt">{esc(FRESHNESS_PROMPT)}</span> '
        f"{actions}</span>"
    )
