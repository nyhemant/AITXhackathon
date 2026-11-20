"""Same-origin newsletter subscribe proxy for the KidZooKit Weekly list.

Kit (formerly ConvertKit), form "KidZooKit Weekly", id 10124095, uid ca4bfbdb8a.
Sign-ups go through Kit's v4 API (create the subscriber as inactive, then add
them to the form). Adding them to this double opt-in form makes Kit send the
confirmation email from KidZooKit. The public form POST is not used: Kit
quarantines those server-side posts and asks for a robot check, and parents
drop off there.

The API key is server-side only. It is read from ``KZK_KIT_API_KEY`` or from
the config file (key ``api_key``). That file is ``~/.kidzookit-data/kit.json``
unless ``KZK_KIT_CONFIG`` names another path. The form id may be overridden
by ``KZK_KIT_FORM_ID`` or ``form_id`` in the same file; otherwise it is
10124095. Nothing here logs an address or the key.

This module never logs an email address and does not write anything to disk.
The signup limit is an in-memory map from visitor IP to recent attempt times
(see newsletter_rate_limited). The map is cleared when the process restarts.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

logger = logging.getLogger("busyparent_agent.newsletter")

KIT_FORM_ID = "10124095"
KIT_TIMEOUT_SECONDS = 8
KIT_USER_AGENT = "KidZooKitNewsletter/1"

KIT_API_SUBSCRIBERS_URL = "https://api.kit.com/v4/subscribers"
KIT_SIGNUP_REFERRER = "https://kidzookit.com/"
_FORM_ID_RE_MAX = 12

# Extra cap on top of the site-wide API bucket. In-memory only.
NEWSLETTER_LIMIT = 5
NEWSLETTER_WINDOW_SECONDS = 3600.0
_MAX_IPS = 8000

_PLACEMENTS = frozenset({"printables_hub", "printable_sheet"})
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





def config_path() -> Path:
    """Config file path. ``KZK_KIT_CONFIG`` overrides ``~/.kidzookit-data/kit.json``."""
    override = os.environ.get("KZK_KIT_CONFIG", "")
    if isinstance(override, str) and override.strip():
        return Path(override.strip()).expanduser()
    return Path.home() / ".kidzookit-data" / "kit.json"


def _config_data() -> dict:
    try:
        data = json.loads(config_path().read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _clean_form_id(raw: object) -> str | None:
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        raw = str(raw)
    if not isinstance(raw, str):
        return None
    form_id = raw.strip()
    if not form_id or len(form_id) > _FORM_ID_RE_MAX or not form_id.isdigit():
        return None
    return form_id


def kit_form_id() -> str:
    """KidZooKit Weekly form id. Env, then the config file, then the known public id."""
    env = os.environ.get("KZK_KIT_FORM_ID", "")
    if isinstance(env, str) and env.strip():
        cleaned = _clean_form_id(env)
        if cleaned:
            return cleaned
    cleaned = _clean_form_id(_config_data().get("form_id"))
    if cleaned:
        return cleaned
    return KIT_FORM_ID


def kit_api_key() -> str | None:
    """Kit v4 API key from ``KZK_KIT_API_KEY`` or the config file. Never logged."""
    env = os.environ.get("KZK_KIT_API_KEY", "")
    if isinstance(env, str) and env.strip():
        return env.strip()
    key = _config_data().get("api_key")
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def form_subscribers_url(form_id: str) -> str:
    return f"https://api.kit.com/v4/forms/{form_id}/subscribers"


class _StopRedirect(urllib.request.HTTPRedirectHandler):
    """Surface the redirect instead of following it, so Location can be read."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)


def _open_kit(request: urllib.request.Request, timeout: float):
    opener = urllib.request.build_opener(_StopRedirect)
    return opener.open(request, timeout=timeout)


def _post_kit_api(url: str, body: dict, api_key: str, timeout: float) -> int:
    """POST JSON to Kit's v4 API. Returns the HTTP status, or 0 on a network error.

    The address and the key are not logged. The response body is discarded (Kit
    may echo the address).
    """
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Kit-Api-Key": api_key,
            "User-Agent": KIT_USER_AGENT,
        },
    )
    try:
        with _open_kit(request, timeout) as response:
            response.read(16384)
            return int(getattr(response, "status", None) or getattr(response, "code", 200) or 200)
    except urllib.error.HTTPError as exc:
        return int(exc.code)
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0


def api_subscribe(email: str, form_id: str, api_key: str, *, timeout: float = KIT_TIMEOUT_SECONDS) -> KitPostResult:
    """Create the subscriber as inactive, then add them to the form.

    Adding to a double opt-in form makes Kit send its confirmation email. Create
    is an upsert that never changes an existing subscriber's state. The address
    is not logged.
    """
    created = _post_kit_api(
        KIT_API_SUBSCRIBERS_URL, {"email_address": email, "state": "inactive"}, api_key, timeout
    )
    if created not in (200, 201, 202):
        return KitPostResult(ok=False)
    added = _post_kit_api(
        form_subscribers_url(form_id),
        {"email_address": email, "referrer": KIT_SIGNUP_REFERRER},
        api_key,
        timeout,
    )
    if added not in (200, 201):
        return KitPostResult(ok=False)
    return KitPostResult(ok=True, already=added == 200)


def deliver_signup(email: str) -> KitPostResult:
    """Subscribe one address through the Kit API. The address is not logged.

    The signup route already rate-limits per IP and drops honeypot hits first.
    There is no public-form fallback: that path is what Kit quarantines.
    """
    form_id = kit_form_id()
    api_key = kit_api_key()
    if not api_key:
        logger.info("kit signup outcome=unconfigured")
        return KitPostResult(ok=False)
    try:
        result = api_subscribe(email, form_id, api_key)
    except Exception:
        logger.info("kit signup outcome=unavailable")
        return KitPostResult(ok=False)
    if not result.ok:
        logger.info("kit signup outcome=failed")
        return result
    logger.info("kit signup outcome=%s", "already" if result.already else "ok")
    return result


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
    send = poster or deliver_signup
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
    _log("failed", placement)
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
        return {"kind": "redirect", "status": 303, "location": "/newsletter/try-again/?reason=email"}
    return {"kind": "redirect", "status": 303, "location": "/newsletter/try-again/"}
