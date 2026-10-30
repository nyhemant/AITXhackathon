# KidZooKit analytics privacy audit (2026-10-24)

Scope: what the live site sends to analytics. Source of truth is the code in
`static/shell/shell.js`, `static/shell/qr-welcome.js`, `static/shell/related-links.js`,
`static/field-pack/js/fp-analytics.js` and the page scripts that call `FPTrack`.
Not legal advice. This lists what the code does, not what any law requires.

## What runs
- Google Analytics 4, property `G-XB8HKLF4XY`, loaded from `www.googletagmanager.com` by `shell.js`.
  No other ad, pixel or session-replay scripts were found.
- Cloudflare Web Analytics (added 2026-10-25, see the section below). It is not in this repo: Cloudflare injects it
  at the edge (auto-install), and the CSP now lets that one script run.
- Skipped on localhost / private hosts, on `/dinner`, and when the visitor opted out
  (`/analytics/off` cookie `one_less_analytics`, or localStorage `1less_analytics_off`).
- No consent banner and no Google consent mode. Nothing in the code sets `user_id`
  or user properties (a test now guards this).

## Identifiers and cookies
- gtag sets its own first-party cookies `_ga` and `_ga_XB8HKLF4XY`: a random client id
  stored in the browser. It is a persistent identifier. It is the only identifier.
- Our server sets one cookie, `one_less_analytics`, only if someone visits `/analytics/off`.
- GA4 receives the page URL (path, query string such as `utm_*` or `?from=`, and the `#` part),
  the page title and standard browser info (language, screen size, user agent, referrer).
  Google handles the visitor's IP address to receive the hit; GA4 does not show it in reports.

## Events (names and fields)
Fields are slugs, enums, counts or flags; none is free text typed by a visitor.
- `page_view`: page_path, page_title, page_location.
- Venue / mission: `venue_page_viewed` (venue_slug, venue_type), `mission_generated`,
  `mission_printed` (venue, age_band, time_budget, hunt_style, interest, shuffle,
  `personalized` = "0" or "1"), `mission_drawer_open`, `hunt_generated`,
  `home_mission_printed`, `qa_sample_printed`, `qa_catalog_printed` (venue slug / public place or card name).
- Watch Live / cards / start: `virtual_zoo_visited`, `habitat_opened`, `cam_clicked`,
  `film_clicked`, `passport_completed`, `cards_hub_visited`, `card_opened`, `hero_search_used`
  (place slug only, not the typed text), `hero_cta_clicked` (button label from page copy),
  `start_map_hotspot_clicked`, `start_map_coach_dismissed`, `related_link_click` (link_type),
  `place_feedback` (venue_slug, choice).
- Printables: `qr_welcome_shown`, `qr_welcome_click`, `printable_download` (campaign, slug, paper size).
- The optional child name on the mission sheet stays in the page. Only `personalized` 0/1 is sent
  and the name is not stored. The "Something changed" note is only put in a `mailto:` link the
  visitor sends themselves; it is never sent to analytics.

## Browser storage (stays on the device, never sent)
`fp-map-scope`, `fp-study-recent`, `fp-vft-*`, `fp-start-teaser-seen-v1`, `kz_start_map_coached`,
`kzk_qr_welcome_dismissed`, `1less_analytics_off`, `1less_ga_debug`.

## Other third parties
- Watch Live pages can embed YouTube (`youtube-nocookie.com`) and a live camera
  (`ams-28635.antmedia.cloud`) in frames. Those providers get the normal request data when a frame loads.
- Images may come from `https:` hosts allowed by the CSP.
- Cloudflare delivers the site and runs the Web Analytics beacon (above).

## Cloudflare Web Analytics beacon (2026-10-25)
Owner decision (Heymant, 2026-10-25): allow the Cloudflare beacon; analytics on at this early stage.
- What it is: Cloudflare's auto-install adds `<script src="https://static.cloudflareinsights.com/beacon.min.js/v<hash>" data-cf-beacon=...>`
  to HTML responses at the edge. Until now the CSP blocked it (`script-src-elem` violation in a real Chrome run on
  `/start/`, a card, `/about/`, `/privacy/`), so it never ran.
- CSP change (src/busyparent_agent/web.py): `script-src` gains exactly `https://static.cloudflareinsights.com`
  (host only, no wildcard; matches the versioned path). Nothing else loosened.
- No `connect-src` host was added. In a real Chrome run with the new script-src, the beacon POSTs to
  `https://kidzookit.com/cdn-cgi/rum` (our own origin, already allowed by `connect-src 'self'`) and raised no other
  violation. `cloudflareinsights.com` is only needed for a manually embedded beacon. A test fails if it is added.
- What it sends (observed): page address including any query string, load and paint timings, browser family and
  version, JS heap sizes, the Cloudflare site token and a random per-page-load id. No cookie or localStorage was set by
  us in the run. Cloudflare's docs say it is cookieless, uses no client-side state for analytics and does not track
  individual users across sites (https://developers.cloudflare.com/web-analytics/data-metrics/data-origin-and-collection/).
  /privacy/ states this as Cloudflare's description, not our promise. Cloudflare also sees normal request data (IP
  address) because it proxies the site.
- Opt-out: visitors with the `one_less_analytics=off` cookie get a CSP without the beacon host
  (`_security_headers_for`), so `/analytics/off` stops both GA4 and the beacon in that browser.
- URL check (premium review ask): query parameters the site writes are enums (`level`, `habitat`, `tab`, `from`,
  `type`, `find`). The two search boxes are GET forms with `name="q"`, but their submit handlers always `preventDefault`,
  so typed text only reaches the URL if JavaScript fails. GA4 already receives the same URLs.
- Still true, not changed: `'unsafe-inline'` remains in `script-src`; the injected tag has no SRI, so Cloudflare serves
  whatever script is at that host (Cloudflare is already in the delivery path); GA4's persistent `_ga` id is the larger
  kids'-site question below. This is not a legal sign-off.
- Premium review: Opus 5.5 and GPT-6.1 Sol, 2026-10-25, notes in `/workspace/kidzookit-loop/2026-10-25-beacon-opus-sol-review.txt`.

## GA4 data retention (2026-10-25)
Heymant is fine with 14 months (the maximum for standard properties). It is a GA4 Admin setting
(Admin > Data collection and retention > Event data retention), not in this repo, and no connector available to the
agent can set it, so it is NOT confirmed as set and /privacy/ makes no retention claim yet.

## Changes in the 2026-10-24 PR
- GA4 config now sets `allow_google_signals: false` and `allow_ad_personalization_signals: false`.
  This only removes data use; no events were removed. Reaches browsers as the cached
  `shell.js?v=6` expires (Cloudflare and browser cache are 24 h).
- Tests: signals / personalization stay off; no `user_id` / user properties.

## Open items for the owner (not changed here)
- In GA4 Admin, confirm Google signals is off, event data retention is set (owner chose 14 months on 2026-10-25;
  the older note here said shortest option), and no ads products are linked. These settings live in Google's console, not in this repo.
- The persistent `_ga` client id remains. Laws for children's sites (for example COPPA in the U.S.)
  can treat persistent identifiers as personal information. Whether to keep analytics on at all,
  add consent, or move to cookieless counting is an owner / legal-advice decision.

## Bot / self-traffic skip, page_print, retention (2026-10-30)
- `shell.js` skips GA4 (not saved) when `navigator.webdriver` is true or the user agent is a headless browser,
  automation tool or crawler (`AUTOMATION_UA_RE`, includes Googlebot/bingbot). Search crawlers still get the
  normal server response; only the in-browser tag is skipped.
- `?notrack=1` on any page = opt-out: shell.js saves `1less_analytics_off` and removes the flag from the address bar
  (history.replaceState) so a shared link does not opt others out, and the server answers that HTML with the
  same `one_less_analytics=off` cookie (1 year) as `/analytics/off`. No parallel mechanism.
- Skipped-tracking HTML (cookie off, `?notrack=1`, or a headless/automation UA; NOT search crawlers) gets
  `Cache-Control: ..., no-transform`, so Cloudflare does not inject the Web Analytics beacon (Cloudflare docs:
  auto-install cannot modify a no-transform response), and a CSP without the beacon host. HTML only: CSS/JS/images
  are edge-cached and must stay compressible.
- New GA4 event `page_print` {page_kind: card|hub|place|virtual_trip|printable|start|other} on `beforeprint`
  (print dialog opened, incl. cancelled: browser menu, Ctrl+P or our Print buttons), at most once per 5 s. No slug, no text; page address as
  for every hit.
- GA4 event data retention confirmed at 14 months in GA4 Admin (2026-10-30); /privacy/ now says so.
- Our own check runners must opt out: cookie `one_less_analytics=off` and/or `?notrack=1`, and a UA containing
  `KidZooKitCheck` (see /workspace/kidzookit-loop/kz_optout.py on the agent box).
- Premium review 2026-10-30 (Opus 5.5 + GPT-6.1 Sol): adopted softer retention / robots wording, 'print window opened', notrack stripped from the URL. Notes: /workspace/kidzookit-loop/2026-10-30-seo-tracking-review.txt.
