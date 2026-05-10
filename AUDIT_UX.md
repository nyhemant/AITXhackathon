# UX Happy-Path Audit

Feature build is frozen. This audit reviewed the current CLI and running web/API happy paths without making product-code changes.

Commands reviewed:

- `python3 -m busyparent_agent.app --scenario dinner --trace`
- `python3 -m busyparent_agent.app --scenario lunch --trace`
- `python3 -m busyparent_agent.app --scenario guest --trace`
- `POST /api/scenario` for `lunch`
- `POST /api/scenario` for `dinner`
- `GET /` for the local web UI

## Overall UX Verdict

Demo is in good shape for a hackathon happy path. The agent leads with one concrete meal, explains the time-aware decision, keeps normal user copy concise, and reserves detailed tool/memory/vision reasoning for trace mode. The product story is coherent: pantry-first near dinner, delivery-aware earlier in the day, mocked Smart Basket Builder for realistic grocery minimums, and photo evidence as confidence support rather than perfect truth.

There are no P0 blockers. The biggest demo polish issue is a small wording mismatch in the lunch cart add-on reason: `mini cucumbers` are classified as medium-confidence from haul evidence, but the user-facing add-on reason says `recurring kid side + low confidence`.

## Dinner Happy-Path Notes

User-facing response:

```text
Make Egg Fried Rice tonight.
Why: Uses pantry rice, eggs, and frozen vegetables without a grocery run.
Time: about 18 minutes, low effort.
Plan: It is close to dinner, so I am prioritizing what is already at home.
Photo evidence confirms eggs, rice, tortillas, and Costco freezer staples; a few unknown items need confirmation.
Reviewable grocery list: nothing required.
I am leading with one option so dinner moves forward.
```

Assessment:

- Concise enough for a busy mom.
- Leads with one smart default.
- Pantry-first is clear and matched by behavior: no cart is created and no grocery run is required.
- Photo evidence helps without dumping scanned items into user copy.
- Trace is detailed but appropriate for judge mode.
- No mismatch found in the dinner user-facing recommendation.

## Lunch Happy-Path Notes

User-facing response:

```text
Make Black Bean Quesadillas tonight.
Why: Fast, warm, and mostly already in the kitchen.
Time: about 20 minutes, low effort.
Plan: Because we are planning early, I can use a small delivery to make dinner better instead of forcing pantry-only.
Photo evidence confirms eggs, rice, tortillas, and Costco freezer staples; a few unknown items need confirmation.
Reviewable cart/list: avocado, berries.
Required for tonight:
- avocado - $1.79
- berries - $6.49
Smart add-ons to make delivery worthwhile:
- mini cucumbers - $4.49 - recurring kid side + low confidence
- bananas - $1.99 - kid snack staple + low waste
- salad kit - $5.49 - useful for next dinner side
- applesauce pouches - $4.99 - lunchbox backup + low waste
- granola bars - $5.49 - kid snack staple + low waste
- crackers - $4.49 - kid side + pantry snack
Mock subtotal: $35.22
Mock Instacart minimum: $35.00
Status: meets minimum
```

Assessment:

- The lunch branch clearly explains why delivery is allowed.
- Smart Basket Builder is understandable: required items first, add-ons second, subtotal/minimum/status at the end.
- The phrase `Reviewable cart/list` reinforces that no order is placed automatically.
- The trace clearly shows required subtotal, minimum check, skipped Costco-covered staples, and final subtotal.
- The one mismatch is `mini cucumbers`: trace/inventory say medium confidence from haul evidence, but cart copy says `low confidence`.

## Guest Happy-Path Notes

User-facing response:

```text
Keep Egg Fried Rice, but make it guest-safe in practice:
- Avoid nut ingredients and skip any nut-based toppings.
- Keep spice off the shared meal; add heat only to adult plates after serving.
Reviewable grocery list: nothing required.
For allergy-sensitive guests, avoid the named ingredients and verify packaged labels. This demo is not an allergy safety guarantee.
```

Assessment:

- Clear and safe.
- Good allergy wording: it avoids overclaiming and tells the parent to verify packaged labels.
- Keeps the selected meal instead of restarting the plan.
- No grocery list noise.
- This is one of the strongest user-facing responses in the demo.

## Web UI/API Notes

- The running API returns the same user-facing response and trace as the CLI for lunch and dinner.
- The web UI is simple and usable for demo purposes.
- The trace toggle defaults to checked. That is useful for judges, but it can overwhelm a normal parent. Presenter should either explain trace mode or turn it off during a parent-style demo.
- In the web rendering order, trace appears before the parent bubble for each response. This is acceptable for a technical demo, but slightly odd for a normal chat transcript.
- API trace length is long but appropriate for trace/debug mode. User-facing `message` stays concise and does not dump every scanned item.

## P0 Blockers

None.

## P1 Should-Fix Before Demo

- Fix the `mini cucumbers` add-on reason mismatch. It currently says `recurring kid side + low confidence`, while inventory says `mini cucumbers -> medium confidence: seen in haul photo, fresh item, bought 3 days ago`.

Suggested copy:

```text
mini cucumbers - $4.49 - recurring kid side + useful for lunchboxes
```

or:

```text
mini cucumbers - $4.49 - recurring kid side + haul is a few days old
```

## P2 Nice-To-Have

- Consider defaulting the web trace toggle off for parent-style demos, while turning it on deliberately for judge walkthroughs.
- Consider changing `Reviewable cart/list` to `Reviewable grocery cart` if the demo presenter wants more natural consumer wording. Current wording is acceptable and reinforces the no-auto-purchase constraint.
- Consider moving trace display after the parent/agent bubbles in the web UI so the transcript reads more naturally.
- The photo evidence summary is good, but it could be slightly shorter if needed:

```text
Photo evidence confirms key staples; a few unknown items need confirmation.
```

## Exact Suggested Copy Changes

Primary suggested change:

```text
Before:
- mini cucumbers - $4.49 - recurring kid side + low confidence

After:
- mini cucumbers - $4.49 - recurring kid side + useful for lunchboxes
```

Optional shorter photo summary:

```text
Before:
Photo evidence confirms eggs, rice, tortillas, and Costco freezer staples; a few unknown items need confirmation.

After:
Photo evidence confirms key staples; a few unknown items need confirmation.
```

Optional cart label:

```text
Before:
Reviewable cart/list: avocado, berries.

After:
Reviewable grocery cart: avocado, berries.
```
