# Field Trip Kit — Polish task queue

Program **closed** 2026-08-12. Full write-up: `docs/LAUNCH-QA.md`.  
Shared rules: `docs/AGENT-BRIEF.md`.

| ID | Title | Status | Completion note |
|----|--------|--------|-----------------|
| T1 | Bug fixes & counts audit | done | VI already NA; AS Oceania; HI NA — no reclass. Tagline `HEADER_TAGLINE` single constant in generator. Counts: trust strip + hubs + compact catalog from data (`218` places). |
| T2 | Analytics foundation | done | `fp-analytics.js` (`FPTrack`, venue pageview helper). `mission_printed` already had venue_type/slug/age_band/time_length/style. Wired mission-ui, print-kit, landing-hook, SEO pages. |
| T3 | Static cards hub `/field-pack/cards/` | done | 109 cards, 3 sections, nav+sitemap, events, blurbs from catalog only. |
| T4 | Hero: paired previews + Before/During/After | done | Mission+lion pair; secondary → cards only; B/D/A list; extras near FAQ; hero events. Search primary CTA kept. |
| T4b | Hero: moment-strip promotion | done | 3-across strip (real mission+card crops); H1→strip→search→trust; subhead/diff/pair retired (commented); `hero_moment_clicked`; fold-checked 390×844. |
| T4c | Hero moments: distinct Before/After cards | done | Before=dino Q&A (attraction), During=mission, After=lion Q&A (wildlife); labels Learn before you go / What did we notice?. |
| T5 | Catalog: cards showcase + compact places | done | Featured×12 + pills; 4 hubs; 12 popular chips; map tabs map-only; reachability 218/218. Popular seeds listed in LAUNCH-QA. |
| T6 | Item-uniqueness lint (report-only) | done | Warn-only default; `docs/item-uniqueness-report.md`. Headline: desc=36 generic_core=68 pairs=4511 top10_clean=YES. |
| T7 | Parks depth pass, batch 1 | done | Content already depth-quality; verify todos listed in LAUNCH-QA; top10 lint clean. |
| T8 | Parks depth pass, batch 2 | done | Same; verify todos in LAUNCH-QA. |
| T9 | NPS public-domain assets | done | Maps local for all 10; manifest `docs/nps-assets-manifest.md`; PD stop-photo batch deferred (gap list). |
| T10 | Print sheet: slice label + park safety footer | done | Engine/print already emit slice title + park safety footer. Device print matrix deferred. |
| T11 | Final QA sweep + lint enforcement | done | `--enforce-top10` OK; reachability OK; dinner untouched; `docs/LAUNCH-QA.md` + smoke script. |
| T12 | Virtual Zoo PoC | done | Live; now a tab on Virtual Field Trip. `/virtual-zoo/` kept as alias. |
| T13 | Virtual Field Trip tabs | done | `/virtual-field-trip/` tabs Zoo · Aquarium · Natural history · Science · National parks. `/virtual-zoo/` alias. Parks = 10 famous CONUS road trip. |
| T12b | Virtual Field Trip fixes | done | Static stop lists in HTML (5 tabs, not 4). Hero copy constants. Dialog heading hidden until open. OG map crop. Events keep T12 names + `tab`. Audit below. |
| T12c | Film next to live cam | done | Watch = Live + Pre-recorded. Player takes the photo well on Pre-recorded (autoplay). Live cam has no empty overlay. `film_clicked`. Inventory below. |

### T12b notes (2026-08-13)

**Indexable `<main>` words:** ~70 before (H1 + lead + Passport + print labels) → **808** after (all five stop lists + catalog/place teasers + cam lines).

**Lighthouse:** CLI not installed here — not recorded. SEO substance is the static lists, not a score gate.

**Events (unchanged names):** `virtual_zoo_visited` `{venue_kind, tab}`, `habitat_opened` `{animal_id, venue_kind, tab}`, `cam_clicked` `{animal_id, venue_kind, tab}`, `passport_completed` `{venue_kind, tab, count}`, `home_mission_printed` `{mode, venue_kind, tab}`. No rename to `vft_visited`.

**Screens:** `docs/t12b-screens/` (390 + 1280 per tab).

| Tab | Stops | Existing cards/kits | Cams (link-out, sourced) | Teasers unique | Photos | Print both | Parity |
|-----|------:|---------------------|--------------------------|----------------|--------|------------|--------|
| Zoo | 10 | catalog animals | 10/10 zoo cams | yes | enhanced animal photos | yes | bar |
| Aquarium | 10 | catalog sea | 4/10 Monterey (jelly, shark, ray, open sea). Others hidden, not invented | yes | enhanced animal photos | yes | fewer cams than zoo — honest |
| Natural history | 4 | catalog halls | 0/4 — no fake museum cams | yes | exhibit illos (allowed) | yes | 4 halls by design, not padded to 10 |
| Science | 10 | catalog sci/cm | 0/10 — no fake lab cams | yes | exhibit illos (allowed) | yes | cam gap vs zoo — honest |
| Parks | 10 | venue kits, not Q&A cards | 7/10 NPS webcam pages. Everglades, Big Bend, Badlands none | yes | `np-hero-*` | yes | print = park hunt; no catalog Q&A |

**Deferred:** replace exhibit illos; invent cams; ARIA tablist (anchors used); Letter/A4 print rebuild (existing sheets); Lighthouse numbers.

**QA:** JS-off lists in source + noscript unhide; `?tab=` + `#aquarium` + `#habitat=`; dialog `hidden` pre-open; cams link-out only; landing + Dallas Zoo 200.

### T12c notes (2026-08-14)

Film is a sibling, never an auto-swap. Live cam hours stay on **Watch live**. Hint “If the yard looks empty, try the film.” only when both exist. YouTube on VFT JSON only (not catalog). oEmbed 20/20 on 2026-08-14.

| Stop | Channel | Film (watch URL) | Notes |
|------|---------|------------------|-------|
| Flamingo | Houston Zoo | `u2k4lSTZxS4` | Chicks on exhibit (no keeper talk) |
| Otter | Smithsonian NZP | `zboaajdMGHg` | Habitat forage |
| Penguin | San Diego Zoo | `RQ56IFZO6N0` | African penguin pool party |
| Hippo | San Diego Zoo | `Zdl4ndfjYBA` | Baby hippo splash |
| Giraffe | Houston Zoo | `uANV7BWv6Co` | Feeding platform |
| Elephant | Smithsonian NZP | `Qzy0r4MUlQk` | Asian herd at the same zoo as the cam (card is African) |
| Lion | Nat Geo Kids | `tlZwYsJpqjo` | Not SI memorial video |
| Tiger | San Diego Zoo | `04kwMlYsYis` | Safari Park Sumatran |
| Gorilla | Houston Zoo | `pRDIYTMvhhE` | Bachelor troop |
| Panda | Smithsonian NZP | `iOm9F5ISj_4` | Qing Bao birthday |
| Clownfish | Nat Geo Kids | `hwtLABCaZbs` | No live cam |
| Crab | Monterey | `7tU4k4zjCCM` | Pelagic red crabs |
| Eel | Monterey | `pPETUfzEx4k` | California moray (swapped from wolf eel) |
| Sea turtle | Monterey | `owf_zFHt_lQ` | Sunbath |
| Seahorse | Monterey | `iOrMzleVoGs` | Secret Lives |
| Shark | Monterey | `oeaDJYIrlik` | Feeding sharks |
| Starfish | MBARI | `KjsmnveGmN8` | Sunflower sea star |
| Octopus | Monterey | `CYBFRu4gkdA` | Giant Pacific |
| Stingray | National Geographic | `Nbuu1Fa-c1k` | Adult Nat Geo channel |
| Jellyfish | Monterey | `nbY7dSf3GYE` | Bell jellies |

**Events:** `film_clicked` `{animal_id, venue_kind, tab}` — do not reuse `cam_clicked`.

## Commands

```bash
python3 scripts/generate_bdo_seo.py
python3 scripts/lint_item_uniqueness.py              # warn-only
python3 scripts/lint_item_uniqueness.py --enforce-top10
python3 scripts/check_venue_reachability.py
scripts/smoke_field_pack_polish.sh
```


## Dual-mode at-home session (2026-08-20)

Print-first live site flipped to a standalone virtual session. Printable hunts kept as optional companion.

| Area | Change |
|------|--------|
| Homepage | H1/Ready/About/FAQ/nav: at-home first. Ready cards → place pages. VFT subtitle “Explore at home”. Map noscript + failed-fetch fallback. |
| Place pages | Generator: dual CTA, `#at-home` cards with catalog Q&A + existing VFT cams/films. Title/meta not print-only. Hunt drawer stays. |
| Card pages | Render catalog DEPTH (photo, talk Q&A from `key` + missions). VFT cam/film when already sourced. Print secondary. |
| Sitemap | `/sitemap.xml` + `/field-pack/sitemap.xml` serve static XML 200 (`web.py`). `/google*.html` Search Console tags from `static/`. |
| Dinner | Untouched. |

QA: landing, dallas-zoo, san-diego-zoo, cards/african-lion, virtual-field-trip, sitemap 200, dinner files unchanged.

## Honesty badges + freshness (2026-08-20)

Place pages show one of two kit-tier labels from existing venue JSON only:

- **Verified kit · checked {Mon YYYY}** when `list_confidence == "audited"` and `last_presence_audit` is a real ISO date (52 venues). Month is formatted from that field — no new dates.
- **Starter list** for every other venue (166), including `content_mode: curated` / `status: verified` / `last_verified` without an audit. Those flags are not a presence check.

Freshness is static: “Was this list accurate?” with `accurate` / `something changed` mailto links to hello@1less.app (subject includes the venue slug). Same line on the print-sheet footer. Print header reuses the two labels. Dinner, cards, and VFT spec untouched.

QA: `python3 -m unittest tests.test_card_kind tests.test_field_pack_session tests.test_field_pack_sitemap tests.test_kit_tier` · regen `python3 scripts/generate_bdo_seo.py`.

## Dallas Zoo session path (2026-08-20)

At-home path is giraffe → elephant → lion without a 12-card dump first.

| Area | Change |
|------|--------|
| Dallas place page | Start here (existing `route_90m` 3) above `#at-home` dump. No new animals. |
| Public cards | Dallas chain Next links: giraffe → African elephant → African lion. SD same-template free: panda → koala → African elephant (Dallas owns the shared elephant card). |
| Cousin cams | First visible line on a cam/film link is `Live from {zoo}` / `Film from {zoo}` parsed from existing VFT labels. |
| SD place page | Same start-here-first template reorder + cam first-line. No new SD animals. |
| Dinner / VFT / SEO factory | Untouched / no mass regen. |

QA: `python3 -m unittest tests.test_card_kind tests.test_field_pack_session tests.test_field_pack_sitemap tests.test_kit_tier`.

ParentTest nits (same PR): card-page 6-Q grid stays 1-up so “Meat” / “Run fast” chips wrap instead of clipping; Art Lab footer is “This museum's cards” (venue-kind CTA — zoo/aquarium/museum/park/place). No Q&A rewrite.

## Dallas Zoo session path (2026-08-20)

At-home path is giraffe → elephant → lion without a 12-card dump first.

| Area | Change |
|------|--------|
| Dallas place page | Start here (existing `route_90m` 3) above `#at-home` dump. No new animals. |
| Public cards | Dallas chain Next links: giraffe → African elephant → African lion. SD same-template free: panda → koala → African elephant (Dallas owns the shared elephant card). |
| Cousin cams | First visible line on a cam/film link is `Live from {zoo}` / `Film from {zoo}` parsed from existing VFT labels. |
| SD place page | Same start-here-first template reorder + cam first-line. No new SD animals. |
| Dinner / VFT / SEO factory | Untouched / no mass regen. |

QA: `python3 -m unittest tests.test_card_kind tests.test_field_pack_session tests.test_field_pack_sitemap tests.test_kit_tier`.

## Follow-on (Grok 4.6 live review) — 2026-08-12

| ID | Title | Status | Note |
|----|--------|--------|------|
| N1 | Cards hub membership + routing | done | 51 cards (was 109); park trails/orphans gone; href `/cards/{id}/` |
| N2 | Lead amp, map kicker, FW gorilla | done | `&amp;` once; Zoo/Park map; gorilla photo |
| N3 | Type-hub Start here | done | Zoos: Dallas…FW; aquariums: Georgia…Seattle; museums prefer list |
| N4 | Place-page start-here stays on venue | done | `#mission` not app.html |
| N5 | Static card pages | done | `/field-pack/cards/{id}/` + print; app.html alias link |

| N6 | Cards hub 390 scan | done | Photo thumbs + Find a card filter; 51 cards |
| N7 | og:image hunt sheet | done | Landing, hubs, card pages, Dallas fallback → sample-mission-dallas-zoo.jpg |
| N8 | One print control | done | Removed “Open print options”; examples-only block remains |
| N9 | Device print QA | done | Drawer screenshots for Dallas, Yellowstone, Children’s Aquarium. Paper/iOS still human. |
