# Hackathon Submission

## Repo / Quick Start

Public repo: <https://github.com/nyhemant/AITXhackathon>

The repo was checked as reachable over unauthenticated HTTPS with `git ls-remote`.

## Deployed URL

Temporary demo tunnel: <https://aitx.myglucoach.app>

This URL requires the presenter's laptop to remain awake with both the local web app and Cloudflare tunnel running.

Quick start from a clean machine:

```bash
git clone https://github.com/nyhemant/AITXhackathon.git
cd AITXhackathon
python3 -m unittest discover -s tests
python3 -m busyparent_agent.app --scenario lunch --trace
```

Requirements:

- Python >=3.10
- No API keys required
- No `.env` required

## Tech Stack

- Python 3.10+
- Stdlib `unittest`
- Local JSON fixtures
- Stdlib local web server / local web chat
- Deterministic mocked adapters for Instacart, Costco, and photo scans
- No external API keys required

## Simple Architecture Diagram

```text
Parent via Web UI or CLI
        |
        v
AgentSession service
        |
        v
BusyParent Agent
        |
        v
tools/adapters
  |-- family profile
  |-- meal memory/history
  |-- inventory confidence engine
  |-- mocked photo scan
  |-- mocked Costco bulk receipts
  |-- mocked Instacart catalog/cart
        |
        v
response + trace + reviewable grocery cart
```

## Reproduce Demo / Env Vars

No API keys are required. No `.env` file is required. All integrations are local mocked fixtures.

Run from the repo root:

```bash
git restore data/meal_history.json
python3 -m unittest discover -s tests
python3 -m busyparent_agent.app --scenario dinner --trace
python3 -m busyparent_agent.app --scenario lunch --trace
python3 -m busyparent_agent.app --scenario guest --trace
python3 -m busyparent_agent.web --host 0.0.0.0 --port 8000
```

For the web demo, browse locally to:

```text
http://127.0.0.1:8000
```

`0.0.0.0` is a server bind address, not the browser URL.

## Synthetic Data & Provenance

All family, inventory, grocery, photo, receipt, catalog, and meal-memory data is synthetic or mocked for this hackathon demo.

- No real grocery accounts are used.
- No real checkout is implemented.
- No real camera capture, image recognition, or OCR is used.
- No private family photos are committed.
- Sample photo paths are placeholders backed by deterministic JSON scan results.
- Mocked Costco receipts, haul/photo-style evidence, and bulk-shopping data are fixture data.
- Instacart order history, catalog availability, substitutions, and cart pricing are fixture data.
- Prices are representative fixture prices, not live Instacart prices.

## Known Limitations & Next Steps

- Mocked integrations only.
- No real grocery checkout.
- No real photo recognition/OCR.
- Small meal library.
- Allergy guidance is not a guarantee; families must verify packaged labels.
- Future: real OCR/vision adapter.
- Future: grocery APIs and live availability.
- Future: richer meal library and preference learning.
- Future: deployed auth-backed web app.
- Future: calendar/context integration.

## Team Roster

- Hemant Bhangale — solo builder; product, agent design, implementation, demo
- Contact: <https://github.com/nyhemant>

## Short Write-Up

Busy parents do not need another recipe app; they need dinner handled. HomePlate AI / BusyParent Kitchen Agent helps families answer the daily "what should we make tonight?" question by combining time of day, family preferences, meal memory, likely home inventory, mocked photo/receipt evidence, Costco bulk shopping patterns, and a mocked Instacart catalog/cart. Instead of generating a recipe list, the agent leads with one practical dinner recommendation, explains the tradeoff, adapts to feedback or guest-child constraints, and builds a reviewable grocery cart only when delivery makes sense.

The demo uses deterministic local fixtures for photo scans, Costco receipts, Instacart history, grocery catalog pricing, and household memory so judges can reproduce the full flow without accounts, API keys, or checkout risk. The impact is reduced decision fatigue for busy parents: fewer last-minute grocery runs, less overbuying, more realistic kid-friendly dinners, and safer handling of constraints like no nuts or no spicy food.
