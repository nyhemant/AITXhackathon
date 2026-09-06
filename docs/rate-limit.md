# 1Less origin rate limits

Lightweight scrape/bot protection for the public site. **Option 3 only:** rate limits. No email signup, no accounts, no content gate, no CAPTCHA on first paint.

Kid names stay on the device. This does not collect emails for hunts.

## Where it lives

| Layer | Role |
| --- | --- |
| `src/busyparent_agent/rate_limit.py` | Sliding-window limiter, path buckets, IP + optional UA, quiet 429 counts |
| `src/busyparent_agent/web.py` | Origin hook on `GET` / `HEAD` / `POST` (`WebHandler._reject_if_rate_limited`) |
| Mini LaunchAgent | Same stdlib `ThreadingHTTPServer` that already serves 1less.app |

There is no reverse-proxy config in this repo. Production is the Python origin behind a **Cloudflare free/tunnel edge** (`server: cloudflare`, `cf-ray`, `cf-cache-status: DYNAMIC`). The lightest real control is this in-app limiter.

**Do not turn on Cloudflare Bot Fight Mode.** That challenges first paint. Cloudflare paid Rate Limiting is not required.

The origin trusts `CF-Connecting-IP` (then `X-Forwarded-For`) only when the TCP peer is loopback or private — the usual `cloudflared → 127.0.0.1:8000` path. Public peers cannot spoof those headers.

## Default thresholds (per client IP, 60s window)

Generous enough for a family session and a ~30-kid classroom on one school NAT. Tight enough to blunt `wget -r` / Scrapy bursts.

| Bucket | Default | What counts |
| --- | --- | --- |
| `pages` | 180 | HTML: `/field-pack/…`, `/start/`, `/about/`, `/dinner` |
| `catalog` | 90 | `catalog.js`, `places-data.js`, venue JSON, `seo-venues.json` |
| `images` | 480 | photos, maps, logos, video |
| `print` | 90 | `print-kit.js`, `print-maps.js`, print CSS, `/media/maps/` |
| `api` | 40 | `/api/chat`, `/api/preview`, `/api/scenario` |
| `other` | 240 | CSS / remaining JS / xml / manifest |
| `overall` | 800 | Hard cap across buckets |

Exempt (never counted): `/robots.txt`, `/analytics/off`, `/analytics/on`, `/analytics/status`. `/llms.txt` is public at the site root (same allowlist as `/robots.txt`); it is not exempt and stays on the family/classroom budget.

When a bucket or `overall` is exceeded the origin returns **429** with **Retry-After** and a short plain-text body. Allowed requests are not logged. 429s increment an in-memory counter and log at most the first hit plus every 50th (`429 ip=… bucket=… retry=… n=…`).

Optional tighter budget for obvious bulk User-Agents (`wget`, `curl/`, `python-requests`, `scrapy`, empty UA, Bytespider, SEO crawlers like Semrush/Ahrefs). Official search and AI fetch crawlers stay on the family/classroom budget: Googlebot, Bingbot, GPTBot, ClaudeBot, Claude-Web, anthropic-ai, PerplexityBot, ChatGPT-User, Google-Extended. This is **not** a first-paint challenge.

## How to tune

Environment variables on the Mini LaunchAgent (`ai.openclaw.aitx-busymom-app`) or the shell that starts `python3 -m busyparent_agent.web`:

```text
ONELESS_RATE_LIMIT=1                 # 0 / off / false disables
ONELESS_RATE_LIMIT_WINDOW=60
ONELESS_RATE_LIMIT_PAGES=180
ONELESS_RATE_LIMIT_CATALOG=90
ONELESS_RATE_LIMIT_IMAGES=480
ONELESS_RATE_LIMIT_PRINT=90
ONELESS_RATE_LIMIT_API=40
ONELESS_RATE_LIMIT_OTHER=240
ONELESS_RATE_LIMIT_OVERALL=800
ONELESS_RATE_LIMIT_BOT_UA=1          # 0 = do not tighten scrapers
ONELESS_RATE_LIMIT_BOT_FACTOR=0.25
ONELESS_RATE_LIMIT_INCLUDE_UA=0      # 1 = key by IP+UA (weaker vs UA rotation)
ONELESS_TRUST_PROXY=1                # 0 = ignore CF / X-Forwarded-For
ONELESS_RATE_LIMIT_MAX_KEYS=20000
```

Restart the LaunchAgent after changing env so the process reloads config.

## Undo / disable

Any one of:

```bash
# LaunchAgent environment
ONELESS_RATE_LIMIT=0

# One-shot local / emergency
python3 -m busyparent_agent.web --no-rate-limit
```

`--no-rate-limit` is the same switch as `ONELESS_RATE_LIMIT=0`. No product copy or footer changes are required to undo.

## How to verify

Unit + origin burst:

```bash
python3 -m unittest tests.test_rate_limit
```

Live origin burst (family UA stays under defaults; a tiny pages budget proves 429):

```bash
ONELESS_RATE_LIMIT_PAGES=8 ./scripts/dev-serve.sh 8000
# other terminal:
./scripts/rate-limit-burst.sh http://127.0.0.1:8000/field-pack/ 16
```

Expect HTTP 200 for the first 8 HTML hits, then 429 with `Retry-After`. `/robots.txt` should stay 200.

On production, burst only from a test IP you control, and put the default pages budget back afterward. Parents should feel nothing: a normal outing page load is a handful of HTML + cached assets, far under the defaults.
