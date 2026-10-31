"""Same-origin newsletter subscribe proxy for Kit's public form endpoint.

Kit (formerly ConvertKit), form "KidZooKit Weekly", id 10124095, uid ca4bfbdb8a.
No API key: the free plan's public form POST is the subscribe path.

Source for the URL (checked 2026-10-31): the live embed script
https://hemant-bhangale.kit.com/ca4bfbdb8a/index.js
contains
  <form action="https://app.kit.com/forms/10124095/subscriptions" method="post">
  <input name="email_address" type="email">
The hosted page https://hemant-bhangale.kit.com/ca4bfbdb8a loads that script.
The authenticated API (POST https://api.kit.com/v4/forms/10124095/subscribers,
X-Kit-Api-Key) is not used.

This module stores nothing and never logs an email address.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass
import json
import logging
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger("busyparent_agent.newsletter")

KIT_FORM_ID = "10124095"
# Public, unauthenticated form subscribe. See module docstring for the source.
KIT_FORM_SUBSCRIBE_URL = "https://app.kit.com/forms/10124095/subscriptions"
KIT_TIMEOUT_SECONDS = 8
KIT_USER_AGENT = "KidZooKitNewsletter/1"

# Extra cap on top of the site-wide API bucket. In-memory only.
NEWSLETTER_LIMIT = 5
NEWSLETTER_WINDOW_SECONDS = 3600.0
_MAX_IPS = 8000

_PLACEMENTS = frozenset({"quiz_finish", "cards_hub_aotd"})
_HONEYPOT = "website"

_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)

_lock = threading.Lock()
_hits: dict[str, deque[float]] = {}


@dataclass(frozen=True)
class KitPostResult:
    ok: bool
    already: bool = False


@dataclass(frozen=True)
class NewsletterResult:
    ok: bool
    status: int
    error: str = ""
    already: bool = False


Poster = Callable[[str], KitPostResult]


def reset_newsletter_limits() -> None:
    """Drop the in-memory counters. Tests use this; the server does not."""
    with _lock:
        _hits.clear()


def placement_label(raw: str | None) -> str:
    """Known placement, or ``other``. Never echo raw input (it could be an email)."""
    value = (raw or "").strip()
    if value in _PLACEMENTS:
        return value
    return "other"


def valid_email(value: object) -> bool:
    if not isinstance(value, str):
        return False
    email = value.strip()
    if not email or len(email) > 254:
        return False
    if any(ch.isspace() for ch in email):
        return False
    if not _EMAIL_RE.fullmatch(email):
        return False
    domain = email.rsplit("@", 1)[1]
    if ".." in domain or domain.startswith(".") or domain.endswith("."):
        return False
    if len(domain.rsplit(".", 1)[-1]) < 2:
        return False
    return True


def newsletter_rate_limited(ip: str, *, now: float | None = None) -> bool:
    """Return True when this IP is already at the cap. A False return records the hit."""
    key = (ip or "unknown").strip()[:64] or "unknown"
    moment = time.monotonic() if now is None else now
    with _lock:
        queue = _hits.get(key)
        if queue is None:
            if len(_hits) >= _MAX_IPS:
                _hits.clear()
            queue = deque()
            _hits[key] = queue
        cutoff = moment - NEWSLETTER_WINDOW_SECONDS
        while queue and queue[0] <= cutoff:
            queue.popleft()
        if len(queue) >= NEWSLETTER_LIMIT:
            return True
        queue.append(moment)
        return False


def _log(outcome: str, placement: str) -> None:
    # outcome and placement are fixed tokens. Do not add the address here.
    logger.info("newsletter outcome=%s placement=%s", outcome, placement)


def parse_form_body(raw: bytes, content_type: str) -> dict[str, str]:
    """Parse a urlencoded, multipart, or JSON form body into strings."""
    ctype = (content_type or "").lower()
    if "multipart/form-data" in ctype:
        return _parse_multipart(raw, content_type)
    if "application/json" in ctype:
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}
        if not isinstance(data, dict):
            return {}
        out: dict[str, str] = {}
        for key, value in data.items():
            if isinstance(value, str):
                out[str(key)] = value[:500]
            elif value is None:
                out[str(key)] = ""
            else:
                out[str(key)] = str(value)[:500]
        return out
    parsed = urllib.parse.parse_qs(raw.decode("utf-8", "replace"), keep_blank_values=True)
    return {key: (values[0] if values else "")[:500] for key, values in parsed.items()}


def _parse_multipart(raw: bytes, content_type: str) -> dict[str, str]:
    match = re.search(r"boundary=([^;]+)", content_type, re.I)
    if not match:
        return {}
    boundary = match.group(1).strip().strip('"')
    if not boundary:
        return {}
    marker = ("--" + boundary).encode("utf-8", "replace")
    out: dict[str, str] = {}
    for chunk in raw.split(marker):
        if b"Content-Disposition" not in chunk:
            continue
        header, _, content = chunk.partition(b"\r\n\r\n")
        if not content:
            continue
        disposition = header.decode("utf-8", "replace")
        name_match = re.search(r'name="([^"]+)"', disposition)
        if not name_match:
            continue
        value = content
        if value.endswith(b"\r\n"):
            value = value[:-2]
        if value.endswith(b"--"):
            value = value[:-2].rstrip(b"\r\n")
        out[name_match.group(1)] = value.decode("utf-8", "replace")[:500]
    return out


def post_kit_subscription(email: str, *, timeout: float = KIT_TIMEOUT_SECONDS) -> KitPostResult:
    """POST email_address to Kit's public form. The address is not logged."""
    payload = urllib.parse.urlencode({"email_address": email}).encode("ascii")
    request = urllib.request.Request(
        KIT_FORM_SUBSCRIBE_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/json;q=0.9",
            "User-Agent": KIT_USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(getattr(response, "status", 200) or 200)
            raw = response.read(16384)
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        try:
            raw = exc.read(16384)
        except Exception:
            raw = b""
        if status in (301, 302, 303, 307, 308):
            return KitPostResult(ok=True, already=False)
    except (urllib.error.URLError, TimeoutError, OSError):
        return KitPostResult(ok=False)
    if not 200 <= status < 300:
        return KitPostResult(ok=False)
    text = raw.decode("utf-8", "replace").lower()
    already = (
        "already subscribed" in text
        or "already a subscriber" in text
        or "already on the list" in text
    )
    return KitPostResult(ok=True, already=already)


def handle_newsletter(
    fields: Mapping[str, str],
    ip: str,
    *,
    poster: Poster | None = None,
) -> NewsletterResult:
    """Validate, drop honeypot hits, rate-limit, and forward. Never logs the email."""
    website = (fields.get(_HONEYPOT) or "").strip()
    placement = placement_label(fields.get("placement"))
    if website:
        _log("honeypot", placement)
        return NewsletterResult(ok=True, status=200)
    email = (fields.get("email_address") or "").strip()
    if not valid_email(email):
        _log("invalid_email", placement)
        return NewsletterResult(ok=False, status=400, error="invalid_email")
    if newsletter_rate_limited(ip):
        _log("rate_limited", placement)
        return NewsletterResult(ok=False, status=429, error="rate_limited")
    send = poster or post_kit_subscription
    try:
        posted = send(email)
    except Exception:
        _log("unavailable", placement)
        return NewsletterResult(ok=False, status=502, error="unavailable")
    if posted.ok and posted.already:
        _log("already", placement)
        return NewsletterResult(ok=True, status=200, already=True)
    if posted.ok:
        _log("ok", placement)
        return NewsletterResult(ok=True, status=200)
    _log("unavailable", placement)
    return NewsletterResult(ok=False, status=502, error="unavailable")


def response_for(result: NewsletterResult, *, wants_json: bool) -> dict:
    """HTTP shape for the fetch path (JSON) or a no-JS form post (303)."""
    if wants_json:
        if result.ok:
            body: dict = {"ok": True}
            if result.already:
                body["already"] = True
            return {"kind": "json", "status": 200, "body": body}
        return {
            "kind": "json",
            "status": result.status,
            "body": {"ok": False, "error": result.error or "unavailable"},
        }
    if result.ok:
        return {"kind": "redirect", "status": 303, "location": "/newsletter/thanks/"}
    if result.error == "invalid_email":
        return {"kind": "redirect", "status": 303, "location": "/newsletter/oops/?reason=email"}
    return {"kind": "redirect", "status": 303, "location": "/newsletter/oops/"}
