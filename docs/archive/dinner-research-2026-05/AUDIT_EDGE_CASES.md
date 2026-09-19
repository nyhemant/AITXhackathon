# Edge-Case Audit

Feature build remains frozen. This audit reviews edge-case behavior and test coverage without adding features or broad refactors.

Initial git status before audit: clean. The UX P1 copy fix was already committed. The P1 allergy-conflict finding below was fixed in the follow-up change that guards against nut-allergy meal conflicts.

Reviewed:

- CLI behavior via `AgentSession` probes and scenario code review
- Running web/API behavior via `POST /api/chat` and `POST /api/scenario`
- Inventory/photo scan adapter behavior via direct module probes
- Cart/catalog behavior via direct adapter probes
- Existing `tests/test_agent_rules.py` coverage
- JSON fixture parse health

## Executive Summary

No P0 demo blockers were found for the scripted happy paths.

One P1 edge-case risk should be fixed before a live, unscripted demo: if a parent explicitly chooses `Peanut Butter Noodles` and then says a guest has a nut allergy, the agent keeps the peanut meal and still lists `peanut butter` in the reviewable grocery cart. The happy-path guest scenario is safe because it starts from `Egg Fried Rice`, but this edge case is a visible safety/copy mismatch if a judge explores.

Other edge cases are mostly acceptable for a hackathon demo or already covered by tests. Missing/corrupt JSON fixtures and malformed API JSON are not graceful, but they are unlikely in the scripted demo. Mutable `meal_history.json` is intentional for the learning feature, but it can make repeated manual demos less predictable unless reset.

## P0 Demo Blockers

None found.

## P1 Should-Fix Before Demo

Status after follow-up: fixed. The agent now switches away from `Peanut Butter Noodles` to `Egg Fried Rice` when a nut-allergy guest is introduced, and the peanut butter cart item is removed.

1. Requested meal conflicts with allergy.

Manual check:

```text
Parent: Let's do peanut butter noodles.
Agent: Reviewable grocery cart: peanut butter.

Parent: Guest has a nut allergy and dislikes spice.
Agent: Keep Peanut Butter Noodles, but make it guest-safe in practice:
- Avoid nut ingredients and skip any nut-based toppings.
Reviewable grocery cart: peanut butter.
For allergy-sensitive guests, avoid the named ingredients and verify packaged labels. This demo is not an allergy safety guarantee.
```

Risk: The agent says to avoid nuts but keeps a peanut-based meal and peanut butter cart item. This is not an allergy guarantee, but it is still a mismatch between the stated constraint and the action.

Suggested behavior: if `no_nuts` and selected meal allergens include `peanut` or `tree nut`, do not keep that meal. Return a short safe refusal/replan, for example:

```text
Peanut Butter Noodles conflicts with the nut allergy, so I would not serve that for this guest. Let's switch to Egg Fried Rice and verify packaged labels.
```

2. Reset mutable demo memory before judging, or avoid feedback-learning messages during the golden run.

Risk: conversational feedback intentionally writes to `data/meal_history.json`. If a presenter or judge records dislikes/avoid events before running scenarios again, recommendations can shift.

Mitigation: reset `data/meal_history.json` to the committed fixture before the official demo, or keep feedback-learning as a separate isolated demo segment.

## P2 Nice-To-Have

- Empty/nonsense input currently returns a meal recommendation. It does not crash, but a more conversational response would be nicer.
- Repeated rejection returns the same three alternatives because the original recommendation remains the rejection anchor.
- Ambiguous time phrases like `later`, `soon`, and `tonight maybe` do not update time context. The agent falls back to the session time.
- Missing/corrupt `data/photo_scan_results.json` raises `FileNotFoundError` or `JSONDecodeError`. This is fixture-robustness, not a normal user path.
- Malformed JSON posted to `/api/chat` logs a handler exception and returns an empty HTTP response. The browser UI sends valid JSON, so demo risk is low.
- Out-of-stock required item with no substitute is represented in `unavailable_items` at adapter level, but there is no polished user-facing explanation path because supported recommendations are filtered before cart construction.
- Running web server can be stale after code changes. During this audit, the already-running web server served pre-copy-fix text (`Reviewable cart/list`, `low confidence`) while CLI from HEAD showed the corrected copy. Restart web before demo.

## Edge-Case Coverage Table

| Area | Edge case | Status | Notes |
|---|---|---:|---|
| User input | Empty message | Manually checked | API returns a normal lunch recommendation; browser prevents empty sends. P2 copy polish only. |
| User input | Nonsense message | Manually checked | Returns the default meal recommendation. Not harmful, but not conversational. |
| User input | Unclear time: `later` | Manually checked | Uses existing session time; no crash. |
| User input | Unclear time: `soon` | Manually checked | Uses existing session time; no crash. |
| User input | Unclear time: `tonight maybe` | Manually checked | Uses existing session time; no crash. |
| User input | Rejects first meal | Covered by test | `test_rejection_returns_three_alternatives`. |
| User input | Rejects all available meals / repeated rejection | Manually checked / gap | Repeats the same alternatives. P2. |
| User input | Impossible request: `nut-free peanut noodles` | Manually checked / gap | Not parsed as a meal+constraint request; default recommendation returned. Lower risk than selected-meal allergy conflict. |
| User input | Kid disliked recommended meal | Covered by test + manually checked | `kid_rejected` event saves and future scoring penalizes it. |
| User input | `what can I make without groceries?` | Manually checked | Returns pantry-first Egg Fried Rice with nothing required. Acceptable. |
| Inventory/photo | Unknown photo scan item preserved | Covered by test | `test_photo_scan_unknown_items_are_preserved`; trace surfaces unknowns. |
| Inventory/photo | Missing latest fridge scan | Manually checked | If fridge scan is absent, inventory still uses JSON fridge snapshot; no crash. |
| Inventory/photo | Missing latest pantry scan | Manually checked | If pantry scan is absent, inventory still uses JSON pantry snapshot; no crash. |
| Inventory/photo | Missing `photo_scan_results.json` | Manually checked / gap | Raises `FileNotFoundError`. P2 unless fixture is accidentally deleted. |
| Inventory/photo | Corrupt `photo_scan_results.json` | Manually checked / gap | Raises `JSONDecodeError`. P2 unless fixture is accidentally edited. |
| Inventory/photo | Duplicate item from photo + Costco + Instacart | Manually checked | Handled sensibly by canonical item key and source priority. Example: eggs/rice combine evidence without duplicate cart items. |
| Inventory/photo | Low-confidence fresh item treated as definitely available | Covered by test | `test_dinner_branch_avoids_relying_on_low_confidence_items`; low/likely-low buckets are penalized for pantry-first. |
| Catalog/cart | Out-of-stock required item uses substitute | Covered by test | `guacamole cup` substitutes to `avocado`. |
| Catalog/cart | Out-of-stock/unknown with no substitute | Covered at adapter level | `dragon fruit` returns `unavailable_items`; no polished user-facing path. |
| Catalog/cart | Below-minimum cart expands with add-ons | Covered by test | Smart Basket Builder reaches $35.22. |
| Catalog/cart | High-confidence home inventory not reordered | Covered by test | Eggs/rice are skipped. |
| Catalog/cart | Costco-covered staple skipped | Covered by test | Rice skipped as Costco bulk high-confidence. |
| Catalog/cart | Cart only contains catalog-backed item IDs | Covered by test | `test_final_cart_only_contains_catalog_item_ids`. |
| Catalog/cart | Smart add-ons exclude household non-food | Covered by test | `paper towels` does not enter food cart. |
| Catalog/cart | Cart does not over-add fresh perishables | Covered by trace/manual, partial test gap | Trace shows `skipped strawberries because fresh add-on limit`; no direct assertion for max fresh count. |
| Guest/allergy | Guest has nut allergy, happy path | Covered by test | Guest scenario with Egg Fried Rice is safe and label wording is good. |
| Guest/allergy | Guest dislikes spice | Covered by test | Spice kept off shared meal; adult heat only after serving. |
| Guest/allergy | Requested meal conflicts with allergy | Manually checked / gap | P1: Peanut Butter Noodles remains selected and peanut butter stays in cart. |
| Guest/allergy | Avoid medical/allergy guarantees | Covered by test | Wording says verify labels and not an allergy safety guarantee. |
| Data/files | All JSON fixtures parse | Manually checked | All current `data/*.json` parse. |
| Data/files | Missing/corrupt JSON graceful fallback | Manually checked / gap | Most fixture reads fail hard; okay for committed demo data, but not robust. |
| API | Bad input does not crash app/web API | Manually checked / partial gap | Unknown scenario returns 400. Malformed JSON logs exception and returns empty response, but server keeps running. |
| Demo memory | Mutable `meal_history.json` predictability | Covered by tests for restore, process gap | Tests restore history after mutation. Manual demo feedback can still alter future scenario output. |

## Suggested Tests To Add

High-value if one more small test pass is allowed:

1. Allergy conflict test:

```text
Select Peanut Butter Noodles, then add a nut-allergy guest. Assert the response does not keep Peanut Butter Noodles and does not include peanut butter in the cart.
```

2. Web bad JSON test:

```text
Post malformed JSON to `/api/chat`; assert HTTP 400 rather than an unhandled request exception.
```

3. Photo scan missing/corrupt fixture tests:

```text
Monkeypatch mock_photo_scan fixture loading to raise FileNotFoundError/JSONDecodeError; assert inventory can continue without photo evidence.
```

4. Fresh add-on limit test:

```text
Assert the smart cart never adds more than MAX_SMART_FRESH_ITEMS fresh add-ons.
```

5. Repeat rejection test:

```text
After rejecting the first meal and rejecting alternatives, assert the agent either asks for a constraint or returns a different fallback response instead of repeating the same list.
```

## Suggested Small Fixes

Only apply after explicit approval.

1. P1 allergy conflict guard in `apply_guest_constraints` or `BusyParentAgent._handle_guest_constraints`.

Small behavior change:

- If `constraints["no_nuts"]` and selected meal allergens include `peanut` or `tree nut`, do not keep the selected meal.
- Prefer a safe known alternative such as Egg Fried Rice, or ask the parent to pick a non-nut option.
- Ensure the grocery list no longer contains peanut butter.

2. P2 API bad JSON guard in `web.py`.

Small behavior change:

- Wrap `_read_json()` in `try/except json.JSONDecodeError`.
- Return HTTP 400 with `Bad JSON` instead of an unhandled handler exception.

3. P2 photo fixture fallback in `mock_photo_scan.py`.

Small behavior change:

- If `photo_scan_results.json` is missing or corrupt, return no scans and trace `none for fridge_photo` rather than crashing.
- This keeps the demo running from fridge/pantry snapshots if photo fixtures are damaged.

4. P2 demo reset helper or docs note.

Small process change:

- Add a short README/demo note to reset `data/meal_history.json` before the official golden run, or provide a local reset command.

## Recommendation: Fix Now Vs Defer

Fix now if the demo will allow judges to freely explore guest/allergy prompts:

- P1 allergy conflict guard for selected Peanut Butter Noodles + nut-allergy guest.

Defer if the demo is strictly scripted:

- Empty/nonsense input copy
- Repeated rejection handling
- Malformed API JSON handling
- Missing/corrupt fixture fallback
- Fresh add-on limit direct test
- Demo memory reset helper

Operationally, restart the web app before demo so it serves the latest committed copy. During this audit, the already-running server was stale relative to HEAD.
