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

Source for the URL (checked 2026-10-31): the live embed script
https://hemant-bhangale.kit.com/ca4bfbdb8a/index.js
contains
  <form action="https://app.kit.com/forms/10124095/subscriptions" method="post">
  <input name="email_address" type="email">
The hosted page https://hemant-bhangale.kit.com/ca4bfbdb8a loads that script,
which loads https://f.convertkit.com/ckjs/ck.5.js (X-CKJS-Version 6).
That script POSTs the form with Accept: application/json and treats the
reply as success only when response.ok and JSON status is "success"
(or "quarantined", which it also sends down the success path). Any other
status, including "failed", is an error. A non-JSON redirect is judged
by its Location: back to this form's subscribe URL is not success.
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
# Public, unauthenticated form subscribe. See module docstring for the source.
KIT_FORM_SUBSCRIBE_URL = "https://app.kit.com/forms/10124095/subscriptions"
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

# Kit's "one more step" page (reCAPTCHA) for a quarantined signup. Only this exact shape is passed on.
KIT_GUARD_RE = re.compile(r"https://app\.kit\.com/forms/guards/[A-Za-z0-9-]{8,80}")

_lock = threading.Lock()
_hits: dict[str, deque[float]] = {}


@dataclass(frozen=True)
class KitPostResult:
    ok: bool
    already: bool = False
    # Set when Kit quarantined the signup: no email goes out until a person passes this check.
    verify_url: str = ""


@dataclass(frozen=True)
class NewsletterResult:
    ok: bool
    status: int
    error: str = ""
    already: bool = False
    verify_url: str = ""


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


_SUCCESS_STATUSES = frozenset({"success"})
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})



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


def _json_object(raw: bytes) -> dict | None:
    text = raw.decode("utf-8", "replace").strip()
    if not text or text[0] not in "{[":
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _header_value(headers, name: str) -> str | None:
    if headers is None:
        return None
    getter = getattr(headers, "get", None)
    if getter is None:
        return None
    value = getter(name)
    if not value:
        value = getter(name.lower())
    if not value:
        return None
    return str(value).strip() or None


def kit_guard_url(value: object) -> str:
    """Kit's guard page URL when ``value`` is exactly one, else ``""``."""
    if not isinstance(value, str):
        return ""
    candidate = value.strip()
    return candidate if KIT_GUARD_RE.fullmatch(candidate) else ""


def _redirect_means_success(location: str | None) -> bool:
    """True when Kit sent the visitor somewhere other than this subscribe URL."""
    if not location:
        return False
    lowered = location.strip().lower()
    if not lowered or lowered.startswith(("javascript:", "data:")):
        return False
    if "status=failed" in lowered or "status=error" in lowered:
        return False
    bare = lowered.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    subscribe = KIT_FORM_SUBSCRIBE_URL.lower().rstrip("/")
    if bare == subscribe or bare.endswith(f"/forms/{KIT_FORM_ID}/subscriptions"):
        return False
    if "/forms/guards/" in bare:
        # A guard (robot check) page is not a signup: nothing is sent until it is passed.
        return False
    return True


def interpret_kit_response(status: int, body: bytes, location: str | None = None) -> KitPostResult:
    """Read Kit's reply: JSON status, otherwise the redirect target.

    "quarantined" is NOT a signup. Kit then answers with a guard URL ("One more step:
    please complete this security check", reCAPTCHA) and sends no confirmation email
    until a person passes it. ck.5.js sends the visitor to that page; this proxy passes
    the URL back to the browser (KitPostResult.verify_url). Seen live 2026-11-18: every
    signup forwarded from the server was quarantined, so the old "treat as success"
    told parents to check an inbox that never got an email.

    ck.5.js (fetched 2026-10-31 from https://f.convertkit.com/ckjs/ck.5.js):
      if (!response.ok) error
      switch ((await response.json()).status) {
        case "success": success
        case "quarantined": success (after the guard)
        default: error  // includes "failed"
      }
    A 3xx with no JSON status is success only when Location is not this form.
    """
    payload = _json_object(body)
    if payload is not None and "status" in payload:
        state = str(payload.get("status") or "").strip().lower()
        if 200 <= status < 300 and state == "quarantined":
            return KitPostResult(ok=False, verify_url=kit_guard_url(payload.get("url")))
        if 200 <= status < 300 and state in _SUCCESS_STATUSES:
            text = body.decode("utf-8", "replace").lower()
            already = state == "success" and (
                "already subscribed" in text
                or "already a subscriber" in text
                or "already on the list" in text
            )
            return KitPostResult(ok=True, already=already)
        return KitPostResult(ok=False)
    if status in _REDIRECT_STATUSES and kit_guard_url(location):
        return KitPostResult(ok=False, verify_url=kit_guard_url(location))
    if status in _REDIRECT_STATUSES and _redirect_means_success(location):
        return KitPostResult(ok=True)
    return KitPostResult(ok=False)


def post_kit_subscription(email: str, *, timeout: float = KIT_TIMEOUT_SECONDS) -> KitPostResult:
    """POST email_address to Kit's public form. The address is not logged."""
    payload = urllib.parse.urlencode({"email_address": email}).encode("ascii")
    request = urllib.request.Request(
        KIT_FORM_SUBSCRIBE_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "X-CKJS-Version": "6",
            "User-Agent": KIT_USER_AGENT,
        },
    )
    try:
        with _open_kit(request, timeout) as response:
            status = int(getattr(response, "status", None) or getattr(response, "code", 200) or 200)
            raw = response.read(16384)
            location = _header_value(getattr(response, "headers", None), "Location")
    except urllib.error.HTTPError as exc:
        status = int(exc.code)
        try:
            raw = exc.read(16384)
        except Exception:
            raw = b""
        location = _header_value(getattr(exc, "headers", None), "Location")
    except (urllib.error.URLError, TimeoutError, OSError):
        return KitPostResult(ok=False)
    return interpret_kit_response(status, raw, location)



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
    if not posted.ok and posted.verify_url:
        _log("verify", placement)
        return NewsletterResult(ok=False, status=200, error="verify", verify_url=posted.verify_url)
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
    if result.error == "verify" and not kit_guard_url(result.verify_url):
        result = NewsletterResult(ok=False, status=502, error="unavailable")
    if wants_json:
        if result.error == "verify":
            return {
                "kind": "json",
                "status": 200,
                "body": {"ok": False, "error": "verify", "verify_url": result.verify_url},
            }
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
    if result.error == "verify":
        # Kit's check needs JavaScript, and form-action 'self' blocks a redirect to Kit.
        return {"kind": "redirect", "status": 303, "location": "/newsletter/one-more-step/"}
    return {"kind": "redirect", "status": 303, "location": "/newsletter/try-again/"}
