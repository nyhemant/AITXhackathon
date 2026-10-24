# KidZooKit analytics privacy audit (2026-10-24)

Scope: what the live site sends to analytics. Source of truth is the code in
`static/shell/shell.js`, `static/shell/qr-welcome.js`, `static/shell/related-links.js`,
`static/field-pack/js/fp-analytics.js` and the page scripts that call `FPTrack`.
Not legal advice. This lists what the code does, not what any law requires.

## What runs
- Google Analytics 4 only, property `G-XB8HKLF4XY`, loaded from `www.googletagmanager.com` by `shell.js`.
  No other analytics, ad, pixel or session-replay scripts were found.
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

## Changes in this PR
- GA4 config now sets `allow_google_signals: false` and `allow_ad_personalization_signals: false`.
  This only removes data use; no events were removed. Reaches browsers as the cached
  `shell.js?v=6` expires (Cloudflare and browser cache are 24 h).
- Tests: signals / personalization stay off; no `user_id` / user properties.

## Open items for the owner (not changed here)
- In GA4 Admin, confirm Google signals is off, data retention is set to the shortest option,
  and no ads products are linked. These settings live in Google's console, not in this repo.
- The persistent `_ga` client id remains. Laws for children's sites (for example COPPA in the U.S.)
  can treat persistent identifiers as personal information. Whether to keep analytics on at all,
  add consent, or move to cookieless counting is an owner / legal-advice decision.
