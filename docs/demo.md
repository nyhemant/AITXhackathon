# Demo Script

Use this for a short judge walkthrough. The demo is local Python only.

Requirements: Python >=3.10.

## 1. Run Tests

Before the golden demo, reset mutable local meal memory:

```bash
git restore data/meal_history.json
```

```bash
python3 -m unittest discover -s tests
```

Expected result: `OK`.

## 2. Local Web Chat

```bash
python3 -m busyparent_agent.web --host 0.0.0.0 --port 8000
```

Browse locally to:

```text
http://127.0.0.1:8000
```

`0.0.0.0` is the bind address for the server. Use `127.0.0.1` in the browser.

If port `8000` is busy:

```bash
python3 -m busyparent_agent.web --host 0.0.0.0 --port 8001
```

Then browse to:

```text
http://127.0.0.1:8001
```

Restart the web server immediately before presenting so it serves the latest code.

Use this when you want a mentor or judge to test the UX without typing in a terminal. The web UI is a demo shell around the same agent service used by the CLI.

## 2b. v2 Story Picker Local Web Demo

For the `v2-storypath` branch, keep the stable v1 dinner demo pinned separately on port `8000`. Run v2 locally on port `8001`:

```bash
python3 -m busyparent_agent.web --host 127.0.0.1 --port 8001
```

Browse locally to:

```text
http://127.0.0.1:8001
```

Use the `Dinner Planner` room for the existing dinner flow and the `Story Picker` room for the bedtime-book flow. Story Picker uses a mocked Epic-style catalog only; there is no real Epic login, API, scraping, checkout, or account access.

## 3. Close-To-Dinner Branch

Short version:

```bash
python3 -m busyparent_agent.app --scenario dinner --trace
```

Full scripted version:

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-08 17:30"
```

Call out:

- `[tool] check_delivery_window`
- `[inventory]` confidence lines show what is visible, recently ordered, or likely low
- `[decision] pantry-first because it is close to dinner`
- `[vision]` lines show mocked fridge, pantry, haul, and receipt scan evidence
- `[memory]` scoring lines boost household favorites and penalize recent repeats
- One meal first: `Egg Fried Rice`
- `Reviewable grocery list: nothing required.`
- Rejection produces three alternatives
- Guest child constraint revises the selected meal

## 4. Lunchtime Branch

Short version:

```bash
python3 -m busyparent_agent.app --scenario lunch --trace
```

Full scripted version:

```bash
python3 -m busyparent_agent.app --demo --trace --now "2026-05-09 12:30"
```

Call out:

- `[decision] grocery delivery can help because planning starts earlier`
- `[tool] mock_instacart.get_recent_orders`
- `[tool] mock_photo_scan.get_latest_scan`
- `[tool] mock_instacart.build_reviewable_cart`
- `[vision]` lines confirm visible fridge/pantry items, recent haul items, receipt parsing, and unknowns
- `[cart]` lines show required subtotal, minimum check, smart add-ons, and final subtotal
- `[memory]` scoring still runs before the recommendation
- The agent does not force pantry-only
- `Reviewable grocery cart: avocado, berries.`
- Required-for-tonight items are separated from smart add-ons
- This is still a reviewable mock grocery cart, not an automatic order

## Inventory Confidence

The demo uses four local inventory signals:

- Costco biweekly Saturday morning bulk restock for pantry and freezer staples
- Instacart short-cycle grocery delivery for fresh or missing items
- Fridge/pantry JSON snapshots for current visible inventory
- Mocked/preexisting photo scans for fridge, pantry, grocery haul, and receipt evidence

The Inventory Confidence Engine ranks items as high-confidence, medium-confidence, low-confidence, likely low, or needing a parent check. Costco shelf-stable items decay slowly, freezer items decay moderately, and fresh produce decays quickly.

Late-day planning prefers high-confidence items. Lunch planning can use the mock Instacart adapter to build a reviewable cart for fresh add-ons like avocado and berries. A real version could replace the fixtures with provider APIs and photo recognition for fridge or pantry snapshots.

The Costco data is fixture-backed receipt-photo style data with a 14-day cadence. A real version could add read-only Costco account receipt sync later; this demo does not build Costco login.

## Mock Photo Scans

`data/photo_scan_results.json` contains deterministic scan outputs for fridge, pantry, grocery-haul, and receipt demo photos. The paths in `data/sample_photos/` are placeholders so the demo can talk about preexisting images without requiring a phone camera or real image recognition.

The mock photo adapter treats scans as confidence evidence, not perfect truth. High-confidence visible items like eggs can raise inventory confidence. Maybe/uncertain items stay medium-confidence. Unknown objects such as a foil-wrapped packet are intentionally surfaced in trace output so a parent can confirm them if needed.

In production, `src/busyparent_agent/adapters/mock_photo_scan.py` could be replaced with a real vision/OCR adapter. The rest of the agent would still consume the same structured scan result shape.

## Mock Grocery Catalog

`data/mock_grocery_catalog.json` is the local shopping universe for the demo. It includes representative prices, brands, sizes, stock status, tags, and substitutes for common household items. The adapter can search this catalog, check availability, substitute an out-of-stock item, and build a priced reviewable cart.

The Smart Basket Builder starts with required dinner items, checks the mock Instacart $35.00 minimum, then adds useful household items only when needed. Add-ons favor upcoming meal ingredients, low-confidence fresh staples, recurring kid snacks/sides, and low-waste items while skipping high-confidence home inventory and Costco-covered staples.

The prices are fixture prices for demo realism only. No real Instacart API, live pricing, account, checkout, scraping, taxes, fees, or order placement is included.

## Household Memory

The demo uses local sample memory in `data/meal_history.json` with `served`, `accepted`, `rejected`, and `recommended` events. The recommendation score boosts family favorites, kid-approved meals, and popular meals, then penalizes meals served or recommended in the last 1-2 days and meals rejected recently.

The same memory file can be updated through natural chat feedback. Try `The kids loved this`, `Egg fried rice was a hit`, `We had quesadillas yesterday`, or `Don't suggest quesadillas again this week`; the agent saves an event and confirms it conversationally.

Before the golden demo, reset mutated demo memory with:

```bash
git restore data/meal_history.json
```

A real version could learn this history from parent accept/reject clicks, completed dinner plans, and repeated household behavior. This demo keeps that memory deterministic and local so judge scenarios remain reliable.

## 5. Guest Constraint Branch

```bash
python3 -m busyparent_agent.app --scenario guest --trace
```

Call out:

- Starts from the parent’s guest child constraint
- Chooses a guest-safe dinner directly
- `[tool] apply_guest_constraints`
- Avoids nuts and keeps spicy food off the shared meal
- Reminds parent to verify packaged labels

## Future Telegram Adapter

CLI and web both call `busyparent_agent.service.AgentSession`. A future Telegram bot should call that same service from a Telegram-specific adapter and send the returned `message` text plus optional trace/debug metadata. The Telegram layer should not reimplement dinner rules, allergy wording, grocery-list logic, or scenario handling.

## Sample Transcript Cues

```text
Parent: What should I make for dinner tonight?
[decision] pantry-first because it is close to dinner
Agent: Make Egg Fried Rice tonight.

Parent: Not feeling that. Anything else?
Agent: Totally. Here are three better directions:

Parent: Let's do Egg Fried Rice.
Agent: Timing: 5 minutes prep, 12-15 minutes cook.

Parent: My daughter has a friend coming over. No nuts, no spicy food.
Agent: Avoid nut ingredients...
Agent: ...verify packaged labels. This demo is not an allergy safety guarantee.
```

## One-Sentence Pitch

BusyMom Agent reduces evening decision load. Dinner Planner decides what dinner should be, explains the time-aware tradeoff, and adapts when a real parent changes the constraints; Story Picker chooses one kid-right bedtime book from a mocked Epic-style catalog.
