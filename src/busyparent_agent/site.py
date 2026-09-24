"""Canonical public site URL for SEO, sitemaps, and host redirects."""

from __future__ import annotations

import json
import os
from urllib.parse import urlsplit

PUBLIC_SITE = os.environ.get("PUBLIC_SITE", "https://kidzookit.com").rstrip("/")
CANONICAL_HOST = "kidzookit.com"
LEGACY_REDIRECT_HOSTS = frozenset({"1less.app", "www.1less.app"})
WWW_REDIRECT_HOSTS = frozenset({"www.kidzookit.com"})
HEALTH_PATHS = frozenset({"/health", "/healthz", "/ready", "/readyz", "/livez", "/ping"})
# Same document as /start/. A temporary redirect left Google indexing /.
HOME_PATHS = frozenset({"/", "/index.html"})


def public_host(host_header: str | None) -> str:
    return (host_header or "").split(":", 1)[0].strip().lower()


def cookie_parent_domain(host_header: str | None) -> str | None:
    """Cookie Domain for production hosts (apex + www), or None for localhost."""
    host = public_host(host_header)
    if host == CANONICAL_HOST or host.endswith(f".{CANONICAL_HOST}"):
        return CANONICAL_HOST
    if host == "1less.app" or host.endswith(".1less.app"):
        return "1less.app"
    return None


def host_redirect_location(host_header: str | None, request_target: str) -> str | None:
    """Absolute 301 Location when Host is a legacy or www alias.

    Preserves path and query. Skips health probes. ``request_target`` is
    ``handler.path`` (path + optional query).
    """
    path = urlsplit(request_target).path or "/"
    if path in HEALTH_PATHS:
        return None
    host = public_host(host_header)
    if host in LEGACY_REDIRECT_HOSTS or host in WWW_REDIRECT_HOSTS:
        target = request_target if request_target.startswith("/") else f"/{request_target}"
        return f"{PUBLIC_SITE}{target}"
    return None


def visitor_scheme(headers) -> str | None:
    """``http`` or ``https`` from the edge, or None for local/dev.

    Cloudflare sends ``CF-Visitor`` (visitor scheme) and ``X-Forwarded-Proto``.
    The origin itself is plain HTTP behind the tunnel, so the socket is not
    the visitor scheme. ``CF-Visitor`` wins when both are present.
    """
    if headers is None:
        return None
    cf = headers.get("CF-Visitor")
    if cf:
        scheme = _scheme_from_cf_visitor(cf)
        if scheme:
            return scheme
    forwarded = headers.get("X-Forwarded-Proto")
    if not forwarded:
        return None
    return _normalize_scheme(str(forwarded).split(",")[0])


def https_upgrade_location(host_header: str | None, request_target: str, headers) -> str | None:
    """Absolute https URL when the apex visitor used plain HTTP.

    Skips health probes and requests with no forwarded scheme (localhost).
    ``/``, ``/index.html``, and slashless ``/start`` go straight to ``/start/``.
    """
    if not PUBLIC_SITE.startswith("https://"):
        return None
    if visitor_scheme(headers) != "http":
        return None
    if public_host(host_header) != CANONICAL_HOST:
        return None
    path = _path_only(request_target)
    if path in HEALTH_PATHS:
        return None
    if path in HOME_PATHS or path == "/start":
        return f"{PUBLIC_SITE}/start/"
    target = request_target if request_target.startswith("/") else f"/{request_target}"
    return f"{PUBLIC_SITE}{target}"


def _path_only(request_target: str) -> str:
    return urlsplit(request_target).path or "/"


def _scheme_from_cf_visitor(raw: str) -> str | None:
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return _normalize_scheme(str(data.get("scheme") or ""))


def _normalize_scheme(raw: str) -> str | None:
    scheme = raw.strip().lower()
    if scheme in {"http", "https"}:
        return scheme
    return None
