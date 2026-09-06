"""In-app scrape/bot rate limits for the public 1Less origin.

No accounts, no email capture, no CAPTCHA on first paint. Parents and
normal browsers should not notice this. A school classroom on one NAT IP
should still load Field Trip Kit. Naive bulk scrapers get 429 + Retry-After.

Production (1less.app) already sits behind a Cloudflare free/tunnel edge
(`server: cloudflare`, `cf-ray`). This module runs on the Mini origin
(LaunchAgent → stdlib ThreadingHTTPServer). Trust CF-Connecting-IP only
when the peer is loopback/private (cloudflared → 127.0.0.1). Do not enable
Cloudflare Bot Fight Mode — that walls first paint with a challenge.

Undo / disable:
  ONELESS_RATE_LIMIT=0
  python3 -m busyparent_agent.web --no-rate-limit
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
import ipaddress
import logging
import math
import os
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit

logger = logging.getLogger("busyparent_agent.rate_limit")

# Generous enough for a family session + ~30-kid classroom on one school NAT.
# Tight enough that wget -r / scrapy bursts trip 429 before they empty the kit.
DEFAULT_WINDOW_SECONDS = 60
DEFAULT_LIMITS: dict[str, int] = {
    "pages": 180,  # HTML place/hub/start/dinner documents
    "catalog": 90,  # catalog.js, venue JSON, places-data
    "images": 480,  # photos, maps, logos, video
    "print": 90,  # print-kit / print-maps / print CSS
    "api": 40,  # /api/chat, /api/preview, /api/scenario
    "other": 240,  # CSS/JS/xml/manifest and leftover static
    "overall": 800,  # hard cap across buckets
}

# Obvious bulk clients get a fraction of the budget — not an instant ban.
# A handful of curl/wget smoke checks still succeed.
DEFAULT_BOT_FACTOR = 0.25
DEFAULT_BOT_FLOOR = 8

# Memory bound so a spoof flood cannot grow unbounded deques.
DEFAULT_MAX_KEYS = 20_000

ENV_ENABLED = "ONELESS_RATE_LIMIT"
ENV_WINDOW = "ONELESS_RATE_LIMIT_WINDOW"
ENV_BOT_UA = "ONELESS_RATE_LIMIT_BOT_UA"
ENV_BOT_FACTOR = "ONELESS_RATE_LIMIT_BOT_FACTOR"
ENV_INCLUDE_UA = "ONELESS_RATE_LIMIT_INCLUDE_UA"
ENV_TRUST_PROXY = "ONELESS_TRUST_PROXY"
ENV_MAX_KEYS = "ONELESS_RATE_LIMIT_MAX_KEYS"
ENV_LIMIT_PREFIX = "ONELESS_RATE_LIMIT_"

EXEMPT_PATHS = frozenset(
    {
        "/robots.txt",
        "/analytics/off",
        "/analytics/on",
        "/analytics/status",
    }
)

CATALOG_NAMES = frozenset(
    {
        "catalog.js",
        "places-data.js",
        "seo-venues.json",
        "landing-map.js",
    }
)

# Tighter budget only — never a first-paint CAPTCHA, never a hard block list.
# AI fetch crawlers (GPTBot, ClaudeBot, …) are on the family allowlist below.
BOT_UA_NEEDLES = (
    "scrapy",
    "wget",
    "python-requests",
    "python-urllib",
    "aiohttp",
    "httpx/",
    "go-http-client",
    "libwww-perl",
    "curl/",
    "bytespider",
    "ccbot",
    "semrush",
    "ahrefs",
    "dotbot",
    "mj12bot",
    "petalbot",
    "dataforseo",
    "magpie-crawler",
)

# Official search / social / AI fetch crawlers stay on the family budget.
# 1Less wants agents to find the kit — do not treat these as scrapers.
FRIENDLY_UA_NEEDLES = (
    "googlebot",
    "bingbot",
    "applebot",
    "duckduckbot",
    "slurp",
    "yandex",
    "facebookexternalhit",
    "twitterbot",
    "linkedinbot",
    "gptbot",
    "claudebot",
    "claude-web",
    "anthropic-ai",
    "perplexitybot",
    "chatgpt-user",
    "google-extended",
)

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off", ""}


def env_flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in _FALSE


def env_int(name: str, default: int, *, minimum: int = 1) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(minimum, value)


def env_float(name: str, default: float, *, minimum: float = 0.01) -> float:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return max(minimum, value)


def limits_from_env(base: Mapping[str, int] | None = None) -> dict[str, int]:
    limits = dict(base or DEFAULT_LIMITS)
    for bucket in list(limits):
        env_name = f"{ENV_LIMIT_PREFIX}{bucket.upper()}"
        limits[bucket] = env_int(env_name, limits[bucket])
    return limits


def classify_path(url_path: str) -> str:
    """Map a URL path to a rate-limit bucket."""
    path = urlsplit(url_path).path or "/"
    lowered = path.lower()
    if lowered in EXEMPT_PATHS:
        return "exempt"
    if lowered.startswith("/api/"):
        return "api"
    name = Path(lowered).name
    suffix = Path(lowered).suffix
    if (
        "print-kit" in lowered
        or "print-maps" in lowered
        or "print.css" in lowered
        or "/media/maps/" in lowered
        or "/print/" in lowered
    ):
        return "print"
    if (
        suffix == ".json"
        or name in CATALOG_NAMES
        or "/data/venues/" in lowered
        or "/data/virtual-venues/" in lowered
        or lowered.endswith("/seo-venues.json")
    ):
        return "catalog"
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".ico", ".mp4"}:
        return "images"
    if (
        suffix in {".html", ".htm"}
        or lowered.endswith("/")
        or lowered in {"/", "/dinner", "/field-pack", "/start", "/about"}
    ):
        return "pages"
    return "other"


def normalize_ip(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip().strip("[]")
    if not text:
        return None
    if text.lower().startswith("::ffff:"):
        text = text[7:]
    return text or None


def _parse_ip(value: str | None) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    text = normalize_ip(value)
    if not text:
        return None
    try:
        return ipaddress.ip_address(text)
    except ValueError:
        return None


_TRUSTED_V4 = (
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("127.0.0.0/8"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.168.0.0/16"),
)
_TRUSTED_V6 = (
    ipaddress.IPv6Network("::1/128"),
    ipaddress.IPv6Network("fc00::/7"),
)


def peer_is_trusted(peer: str | None) -> bool:
    """Loopback + RFC1918 / IPv6 ULA only.

    Documentation / TEST-NET ranges (203.0.113.0/24, …) must not be trusted:
    some Python builds mark them ``is_private``.
    """
    parsed = _parse_ip(peer)
    if parsed is None:
        return False
    if parsed.is_loopback:
        return True
    if isinstance(parsed, ipaddress.IPv4Address):
        return any(parsed in network for network in _TRUSTED_V4)
    return any(parsed in network for network in _TRUSTED_V6)


def looks_like_ip(value: str | None) -> bool:
    return _parse_ip(value) is not None


def resolve_client_ip(
    peer: str | None,
    headers: Mapping[str, str] | None,
    *,
    trust_proxy: bool = True,
) -> str | None:
    """Best-effort client IP.

    When the Mini origin is reached via Cloudflare tunnel, the TCP peer is
    127.0.0.1 and the real visitor is in CF-Connecting-IP / X-Forwarded-For.
    Forwarded headers are ignored unless the peer is loopback/private.
    """
    hdrs = headers or {}
    trusted = trust_proxy and peer_is_trusted(peer)

    def _header(*names: str) -> str | None:
        for name in names:
            raw = hdrs.get(name)
            if raw:
                return raw
            # email.message.Message is case-insensitive; dict tests may not be.
            lower = name.lower()
            for key, value in hdrs.items():
                if str(key).lower() == lower and value:
                    return value
        return None

    if trusted:
        cf = normalize_ip(_header("CF-Connecting-IP", "Cf-Connecting-IP"))
        if looks_like_ip(cf):
            return cf
        xff = _header("X-Forwarded-For", "X-Forwarded-For")
        if xff:
            first = normalize_ip(xff.split(",", 1)[0])
            if looks_like_ip(first):
                return first
    return normalize_ip(peer)


def ua_is_friendly(user_agent: str) -> bool:
    ua = (user_agent or "").lower()
    return any(needle in ua for needle in FRIENDLY_UA_NEEDLES)


def ua_looks_like_bot(user_agent: str) -> bool:
    ua = (user_agent or "").strip()
    if not ua:
        return True
    if ua_is_friendly(ua):
        return False
    lowered = ua.lower()
    return any(needle in lowered for needle in BOT_UA_NEEDLES)


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    bucket: str
    retry_after: int = 0
    ip: str | None = None
    limited: bool = False
    skipped: bool = False

    @property
    def rejected(self) -> bool:
        return (not self.allowed) and (not self.skipped)


@dataclass
class RateLimitStats:
    allowed: int = 0
    limited: int = 0
    skipped: int = 0
    by_bucket: dict[str, int] = field(default_factory=dict)

    def bump(self, field_name: str, bucket: str) -> None:
        setattr(self, field_name, getattr(self, field_name) + 1)
        if field_name == "limited":
            self.by_bucket[bucket] = self.by_bucket.get(bucket, 0) + 1


class _Window:
    __slots__ = ("events",)

    def __init__(self) -> None:
        self.events: deque[float] = deque()

    def prune(self, cutoff: float) -> None:
        events = self.events
        while events and events[0] <= cutoff:
            events.popleft()

    def retry_after(self, now: float, window: float) -> int:
        if not self.events:
            return 1
        return max(1, math.ceil(self.events[0] + window - now))


class RateLimiter:
    """Thread-safe sliding-window limiter keyed by IP (+ optional UA)."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        limits: Mapping[str, int] | None = None,
        window_seconds: int = DEFAULT_WINDOW_SECONDS,
        bot_ua: bool = True,
        bot_factor: float = DEFAULT_BOT_FACTOR,
        include_ua: bool = False,
        trust_proxy: bool = True,
        max_keys: int = DEFAULT_MAX_KEYS,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self.enabled = enabled
        self.limits = dict(limits or DEFAULT_LIMITS)
        self.window_seconds = max(1, int(window_seconds))
        self.bot_ua = bot_ua
        self.bot_factor = max(0.01, float(bot_factor))
        self.include_ua = include_ua
        self.trust_proxy = trust_proxy
        self.max_keys = max(32, int(max_keys))
        self._clock = clock or time.monotonic
        self._lock = threading.Lock()
        self._windows: dict[tuple[str, str], _Window] = {}
        self.stats = RateLimitStats()
        self._log_hits: dict[tuple[str, str], int] = {}

    @classmethod
    def from_env(cls) -> "RateLimiter":
        return cls(
            enabled=env_flag(ENV_ENABLED, True),
            limits=limits_from_env(),
            window_seconds=env_int(ENV_WINDOW, DEFAULT_WINDOW_SECONDS),
            bot_ua=env_flag(ENV_BOT_UA, True),
            bot_factor=env_float(ENV_BOT_FACTOR, DEFAULT_BOT_FACTOR),
            include_ua=env_flag(ENV_INCLUDE_UA, False),
            trust_proxy=env_flag(ENV_TRUST_PROXY, True),
            max_keys=env_int(ENV_MAX_KEYS, DEFAULT_MAX_KEYS, minimum=32),
        )

    def reset(self) -> None:
        with self._lock:
            self._windows.clear()
            self._log_hits.clear()
            self.stats = RateLimitStats()

    def limit_for(self, bucket: str, *, bot: bool) -> int:
        base = self.limits.get(bucket, self.limits["other"])
        if not bot:
            return base
        return max(DEFAULT_BOT_FLOOR, int(base * self.bot_factor))

    def _client_key(self, ip: str, user_agent: str) -> str:
        if not self.include_ua:
            return ip
        ua = (user_agent or "").strip().lower()[:80]
        return f"{ip}|{ua}" if ua else ip

    def _window(self, key: tuple[str, str]) -> _Window:
        window = self._windows.get(key)
        if window is None:
            if len(self._windows) >= self.max_keys:
                self._evict_one()
            window = _Window()
            self._windows[key] = window
        return window

    def _evict_one(self) -> None:
        # Drop the window with the oldest first event (or an empty one).
        oldest_key = None
        oldest_ts = None
        for key, window in self._windows.items():
            ts = window.events[0] if window.events else 0.0
            if oldest_ts is None or ts < oldest_ts:
                oldest_ts = ts
                oldest_key = key
        if oldest_key is not None:
            del self._windows[oldest_key]

    def check(
        self,
        *,
        ip: str | None,
        path: str,
        user_agent: str = "",
        now: float | None = None,
    ) -> RateLimitDecision:
        bucket = classify_path(path)
        if not self.enabled:
            self.stats.bump("skipped", bucket)
            return RateLimitDecision(allowed=True, bucket=bucket, skipped=True, ip=ip)
        if not ip:
            self.stats.bump("skipped", bucket)
            return RateLimitDecision(allowed=True, bucket=bucket, skipped=True, ip=ip)
        if bucket == "exempt":
            self.stats.bump("skipped", bucket)
            return RateLimitDecision(allowed=True, bucket="exempt", skipped=True, ip=ip)

        bot = self.bot_ua and ua_looks_like_bot(user_agent)
        client = self._client_key(ip, user_agent)
        stamp = self._clock() if now is None else now
        cutoff = stamp - self.window_seconds

        with self._lock:
            bucket_window = self._window((client, bucket))
            overall_window = self._window((client, "overall"))
            bucket_window.prune(cutoff)
            overall_window.prune(cutoff)

            bucket_limit = self.limit_for(bucket, bot=bot)
            overall_limit = self.limit_for("overall", bot=bot)

            if len(bucket_window.events) >= bucket_limit:
                retry = bucket_window.retry_after(stamp, self.window_seconds)
                self._record_limited(ip, bucket, retry)
                return RateLimitDecision(
                    allowed=False,
                    bucket=bucket,
                    retry_after=retry,
                    ip=ip,
                    limited=True,
                )
            if len(overall_window.events) >= overall_limit:
                retry = overall_window.retry_after(stamp, self.window_seconds)
                self._record_limited(ip, "overall", retry)
                return RateLimitDecision(
                    allowed=False,
                    bucket="overall",
                    retry_after=retry,
                    ip=ip,
                    limited=True,
                )

            bucket_window.events.append(stamp)
            overall_window.events.append(stamp)
            self.stats.bump("allowed", bucket)
            return RateLimitDecision(allowed=True, bucket=bucket, ip=ip)

    def _record_limited(self, ip: str, bucket: str, retry: int) -> None:
        self.stats.bump("limited", bucket)
        key = (ip, bucket)
        count = self._log_hits.get(key, 0) + 1
        self._log_hits[key] = count
        if count == 1 or count % 50 == 0:
            logger.info(
                "429 ip=%s bucket=%s retry=%s n=%s",
                ip,
                bucket,
                retry,
                count,
            )


_limiter: RateLimiter | None = None
_limiter_lock = threading.Lock()


def get_limiter() -> RateLimiter:
    global _limiter
    with _limiter_lock:
        if _limiter is None:
            _limiter = RateLimiter.from_env()
        return _limiter


def set_limiter(limiter: RateLimiter | None) -> RateLimiter:
    """Replace the process-wide limiter (tests / --no-rate-limit)."""
    global _limiter
    with _limiter_lock:
        _limiter = limiter if limiter is not None else RateLimiter.from_env()
        return _limiter


def reset_limiter() -> RateLimiter:
    """Drop in-memory counts and reload config from the environment."""
    return set_limiter(RateLimiter.from_env())


def evaluate_request(
    *,
    peer: str | None,
    headers: Mapping[str, str] | None,
    path: str,
    user_agent: str = "",
) -> RateLimitDecision:
    limiter = get_limiter()
    ip = resolve_client_ip(peer, headers, trust_proxy=limiter.trust_proxy)
    ua = user_agent
    if not ua and headers:
        for key, value in headers.items():
            if str(key).lower() == "user-agent":
                ua = value or ""
                break
    return limiter.check(ip=ip, path=path, user_agent=ua)
