"""Canonical public site URL for SEO, sitemaps, and host redirects."""

from __future__ import annotations

import os
from urllib.parse import urlsplit

PUBLIC_SITE = os.environ.get("PUBLIC_SITE", "https://kidzookit.com").rstrip("/")
CANONICAL_HOST = "kidzookit.com"
LEGACY_REDIRECT_HOSTS = frozenset({"1less.app", "www.1less.app"})
WWW_REDIRECT_HOSTS = frozenset({"www.kidzookit.com"})
HEALTH_PATHS = frozenset({"/health", "/healthz", "/ready", "/readyz", "/livez", "/ping"})


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
