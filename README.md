# KidZooKit

KidZooKit is a free Field Trip Kit for families: an at-home virtual zoo (plus aquariums, museums, and parks). Pick a place or an animal. Get a short activity with real photos, questions to ask, and an optional printable mission.

Live site: [kidzookit.com](https://kidzookit.com). Legacy `1less.app` / `www.1less.app` 301 here.

No account, no email, no ads. Kid-facing printables use **mission** language (for example, “Your mission at the Dallas Zoo”).

The GitHub repo is still `nyhemant/AITXhackathon` and the Python package is still `busyparent_agent`. Those are implementation leftovers — not product names.

## What it is

Three doors from Start:

- **Watch Live** — virtual field trip / live cams
- **Places** — map and venue kits (zoos, aquariums, museums, parks)
- **Cards** — animals and sea life to look up at home

A printable hunt or cutouts is an optional companion if you are going in person.

## Run locally

Requirements: Python >= 3.10

From the repo root:

```bash
./scripts/dev-serve.sh
```

Then open `http://127.0.0.1:8000/` — the server **302s `/` to `/start/`**. Also useful:

```text
http://127.0.0.1:8000/start/
http://127.0.0.1:8000/field-pack/
http://127.0.0.1:8000/field-pack/cards/
```

Same server, any host/port:

```bash
python3 -m busyparent_agent.web --host 127.0.0.1 --port 8000
```

If port `8000` is busy, pass another port to the script (`./scripts/dev-serve.sh 8001`) or to `web.py`.

Origin scrape/bot rate limits are on by default (`docs/rate-limit.md`). A normal family browse will not notice them. Emergency off:

```bash
ONELESS_RATE_LIMIT=0 python3 -m busyparent_agent.web --host 127.0.0.1 --port 8000
# or
python3 -m busyparent_agent.web --no-rate-limit
```

Automated tests:

```bash
python3 -m unittest discover -s tests
```

## Main routes

| Path | What |
|------|------|
| `/` | **302** to `/start/` |
| `/start/` | First screen. Doors: Watch Live, Places, Cards |
| `/zoo` | **301** to `/start/` |
| `/field-pack/` | Places — map explorer (stays **200**; does not redirect to Start) |
| `/field-pack/cards/` | Cards hub |
| `/field-pack/{slug}/` | Place page (example: `/field-pack/dallas-zoo/`) |
| `/field-pack/virtual-field-trip/` | Watch Live |
| `/field-pack/print/` | Print cutouts (cut · hide · seek) |
| `/about/` | About, FAQ, Experimental extras |
| `/dinner` | Dinner — secondary, **Experimental** |

Field Trip Kit static lives under `static/field-pack/` and is served at `/field-pack/`. In-app links are absolute `/field-pack/...` (pages use `<base href="/field-pack/">`).

## Dinner (secondary)

Dinner still runs at `/dinner`. It is an Experimental leftover from Chapter 1 (“tonight’s meal”), not the default product. Frozen dinner-app notes: `docs/demo.md`, `docs/product-reference.md`. Those are dinner validation / history — not current product validation.

## Documentation

- Session continuity for Field Trip Kit: `.grok/HANDOFF.md`
- Agent brief: `docs/AGENT-BRIEF.md`
- Origin scrape/bot rate limits: `docs/rate-limit.md`
- Dinner local validation (not current product): `docs/demo.md`
- Dinner Chapter 1 reference (not current product): `docs/product-reference.md`
- `docs/product/` — pointer only; not live research
- Archived May 2026 dinner/Reddit research: `docs/archive/dinner-research-2026-05/`
- Legacy dinner model 1.1 freeze: `docs/legacy/model-1.1.md` (`legacy/model-1.1`, tag `legacy-model-1.1`)
- Other archived historical docs: `docs/archive/`

## Project structure

```text
static/start/            first-time landing (`/start/`)
static/field-pack/       Field Trip Kit (places, cards, Watch Live, print)
static/about/            About + FAQ
static/shell/            shared chrome
src/busyparent_agent/
  web.py                 stdlib server: Start, Field Trip Kit, About, /dinner
  rate_limit.py          per-IP scrape/bot limits
  service.py             dinner session (secondary)
scripts/dev-serve.sh     local QA server
tests/                   unittest coverage
docs/product/            pointer only (research archived)
docs/archive/dinner-research-2026-05/
```
