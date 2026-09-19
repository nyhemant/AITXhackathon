<!-- Saved from Hemant Telegram attachment on 2026-05-16. Source of truth: GitHub repo + Mac mini working copy. -->

# 1Less MVP Product Brief v0.2

**Parent Decision Relief, Starting with Dinner**

## 1. Product positioning

1Less is a parent decision-relief product.

It helps busy parents remove one recurring household decision at a time without creating another chore.

The first chapter is dinner because “What are we eating tonight?” is frequent, emotionally loaded, time-sensitive, and easy to validate.

But 1Less should not be framed as only a dinner app.

The broader product architecture is chapter-based:

- Chapter 1: Dinner decision
- Chapter 2: Bedtime story/book choice
- Future chapters: other repeat parent decision moments

Company-level promise:

“One less decision for busy parents.”

Chapter 1 promise:

“Tonight’s dinner, decided.”

Chapter 1 emotional hook after Reddit observation scan:

“For the 4:47pm dinner meltdown: one realistic dinner decision, not a recipe rabbit hole.”

Chapter 2 future promise:

“Tonight’s bedtime story, chosen.”

The MVP should prove the 1Less pattern through dinner, while keeping the brand open for future chapters.

## 2. Target parent/user

Primary user:

A busy parent who is mentally overloaded by repeated household decisions and wants one practical answer at the moment of need.

For Chapter 1, this means:

A parent facing the late-afternoon or evening dinner decision, often with kids, constraints, limited energy, and limited time.

Early validation should prioritize working parents / working moms with young or school-age kids, because the strongest observed Chapter 1 pain is the post-work dinner-crunch moment: the parent may already have ideas, but has no decision energy left to make one happen.

Likely traits:

- Has young or school-age kids
- Is often tired by dinner time
- Has to account for picky eaters, allergies, preferences, leftovers, pantry limits, or time pressure
- Does not want to browse recipes
- Does not want to maintain a complex meal plan
- Wants relief, not another management system

Emotional truth:

The parent is not asking for “recipe discovery.”

They are asking:

“Please take this one decision off my plate in a way I can trust.”

## 3. Painful moment being solved

The broad 1Less painful moment:

A parent is already overloaded and faces a recurring household decision that feels small from the outside but draining in the moment.

For Chapter 1:

It is late afternoon or evening. Dinner is coming. The parent is tired. Kids may be hungry. There may be random ingredients, partial leftovers, picky preferences, allergy concerns, budget concerns, and little time.

The parent does not want inspiration.
The parent wants a decision.

Job-to-be-done:

“When I’m tired and dinner is coming, give me one realistic meal my family can actually eat tonight.”

Refined Chapter 1 JTBD after Reddit observation:

“When it is late afternoon/evening and I have no decision energy left, give me one realistic, good-enough dinner I can execute tonight with my time, energy, kid constraints, and what I say I have — plus one easier fallback if it misses.”

The pain is:

- decision fatigue
- too many options
- fear kids will reject the meal
- safety/allergy uncertainty
- time pressure
- guilt about nutrition
- resentment toward planning tools that require setup
- feeling like AI still makes me do the work

## 4. MVP promise

MVP promise for Chapter 1:

1Less gives a busy parent one clear dinner recommendation for tonight using simple preferences, avoidances, time, and energy level entered by the parent. It should reduce decision fatigue without claiming medical, allergy, nutrition, budget, or pantry accuracy.

A good MVP answer includes:

- One recommended dinner
- Why this dinner fits tonight
- Estimated time/effort
- Simple ingredient/use-what-you-have guidance based only on what the parent enters tonight
- Allergy/preference caveat if relevant
- One fallback/tweak path if the answer does not work

MVP success test:

“Does this remove one real dinner decision without creating another chore?”

Emotional success test:

“Did the parent move from ‘I do not have the brain for this’ to ‘good enough, decided’ in under 60 seconds?”

Broader product success test:

“Does this remove one real decision for a busy parent without creating another chore?”

The MVP should not promise:

- perfect nutrition
- medical or allergy guarantees
- full pantry accuracy
- grocery delivery
- automated weekly planning
- parenting advice
- full household management
- generic AI assistant behavior

## 5. Core user loop

The 1Less loop should be reusable across chapters:

## 1. Parent enters a decision moment
   Example: dinner, bedtime story, lunchbox, weekend activity.

## 2. 1Less asks for only the minimum context needed

## 3. 1Less gives one clear recommendation

## 4. Parent accepts, rejects, or tweaks

## 5. 1Less lightly remembers what worked

For Chapter 1, the dinner loop is:

Step 1:
Parent opens 1Less at dinner-decision time.

Prompt:
“What’s tonight like?”

Step 2:
Parent gives minimal context.

Potential inputs:

- Time available:
  - 10 min
  - 20 min
  - 30 min

- Energy level:
  - barely cooking
  - normal
  - can cook

- Constraints:
  - picky eater / familiar kid-friendly option based on what the parent says, not a guarantee the child will eat it
  - vegetarian
  - nut-free
  - dairy-free
  - use leftovers
  - pantry/freezer meal

- Optional free text:
  “What do you have?”
  “Anything to avoid?”

Any pantry/use-what-you-have language should be based only on what the parent enters in the current flow. 1Less should not imply it knows the household pantry or inventory.

Step 3:
1Less returns one dinner decision.

Example:

“Tonight: bean & cheese quesadillas with fruit and yogurt.

Why: 15 minutes, familiar/kid-friendly based on what you told me, low cleanup, uses pantry/freezer staples you say you have.

Check: If dairy is a concern, swap cheese/yogurt for your safe alternative.”

Step 4:
Parent can respond:

- Good enough
- Too much cooking
- Kid won’t eat this
- Missing ingredient
- Give me backup

The fallback must be easier, not merely different. If the parent says “Too much work,” reduce at least one of cooking time, cleanup, steps, active attention, or ingredient complexity. If the parent says “Kid won’t eat this,” first try a deconstructed/familiar-side version before jumping to a totally unrelated adult recipe.

Step 5:
1Less learns lightly.

Do not create a heavy profile yet. Capture only low-burden signals if current architecture supports it:

- accepted/rejected
- reason rejected
- known hard constraints
- favorite fallback meals

The product should get easier over time because it remembers what worked, not because the parent filled out a large setup form.

## 6. Trust/privacy/allergy boundaries

This likely needs Sophie review before user-facing implementation.

Trust principle:

1Less should be practical and reassuring, but never overclaim.

Use language like:

- “Based on what you told me…”
- “I’ll avoid ingredients you marked as unsafe.”
- “Please check labels for allergies.”
- “For serious allergies, verify packaged foods and cross-contact risk.”

Avoid language like:

- “Safe for your child”
- “Guaranteed allergy-free”
- “Medically approved”
- “Perfectly balanced”
- “Nutritionist recommended” unless actually backed

Privacy boundary:

The MVP should collect the minimum data needed to make dinner easier.

Likely okay to store:

- household preferences
- disliked foods
- basic dietary constraints
- accepted/rejected meal history
- saved fallback meals

MVP must not ask for or require:

- children’s names
- medical conditions
- precise location
- detailed health/nutrition goals
- school schedules
- photos of pantry/fridge
- grocery purchase history

If a parent voluntarily types sensitive information into free text, this MVP should not highlight it, build profile features around it, or require it for future use.

Suggested privacy posture:

“1Less only needs enough family preference information to make this decision easier. You can use it without entering names or sensitive health details.”

Allergy boundary:

1Less can support avoidance but cannot certify safety.

MVP boundary:

- User can mark allergens/avoidances
- App avoids obvious conflicting suggestions
- App displays allergy caveat
- App does not guarantee packaged food safety, cross-contact safety, restaurant safety, or medical advice

Suggested wording:

“1Less can help avoid ingredients you flag, but it cannot guarantee allergy safety. Always check labels and use your judgment for serious allergies.”

If allergy or avoidance input is present, the recommendation UI must show this caution near the recommendation. This cannot live only in docs, policy text, or footer copy.

## 7. Retention hypothesis

Retention hypothesis:

Parents will return if 1Less reliably reduces a recurring parent decision in under 60 seconds.

For Chapter 1:

Parents return if dinner decisions feel easier, faster, and less guilt-inducing.

The habit is not:

“I use a meal-planning app.”

The habit is:

“I ask 1Less when I’m stuck.”

Potential retention drivers:

- Saved family memory:
  “Last time your kids liked this.”

- Fast fallback meals:
  “Want one of your reliable 15-minute dinners?”

- Low-energy mode:
  “Bare minimum dinner tonight?”

- Progressive learning:
  Every accepted/rejected meal improves future suggestions.

- Emotional relief:
  “I don’t have to start from zero.”

Metric candidates:

- Time from open to accepted dinner
- Accepted vs rejected meal recommendation
- Repeat use within 7 days
- Number of fallback requests
- User saves a “worked for us” meal
- User marks “good enough” or “made this”

MVP should optimize for:

“Decision accepted quickly.”

Observed Reddit-informed optimization target:

“One realistic answer, not twenty recipes.”

Not:

- session length
- recipe browsing
- number of recommendations viewed
- complex planning depth

## 8. Non-goals

MVP non-goals:

- No bedtime story/book flow yet
- No multi-chapter platform build yet
- No generic parent command center
- No full weekly meal planning
- No full grocery list generation
- No grocery delivery integration
- No nutrition/macros optimization
- No medical diet management
- No photo pantry scanning
- No calendar integration
- No school lunch planning
- No weekend activity planning
- No social sharing
- No recipe marketplace
- No full family profile wizard
- No broad AI assistant interface
- No parallel local repo copies

Near-term but not MVP: lunchbox/snack defaults and panic-dinner defaults are promising future extensions, but they should wait until Chapter 1 dinner relief is validated with real parents.

Important distinction:

The product vision is broad.
The first build is narrow.

Dinner is the first proof point, not the full identity.

## 9. Suggested first Codex-sized build task

Task name:

Build 1Less Chapter 1: Dinner Decision MVP Flow v0

Objective:

Implement the first 1Less chapter: a dinner decision-relief flow that proves the broader 1Less pattern without building future chapters yet.

Reddit-informed positioning to preserve:

For the 4:47pm dinner meltdown, 1Less should provide one realistic dinner decision, not recipe browsing, meal-planning homework, or another system to manage.

Scope:

- Add or update the MVP dinner decision screen/flow
- Position dinner as “Chapter 1” or “starting with dinner” where appropriate
- Do not frame 1Less as only a dinner app
- Let the parent provide minimal context:
  - time available
  - energy level
  - dietary/allergy constraints
  - optional ingredients / what they have
  - picky eater / familiar kid-friendly option based on what the parent says, not a guarantee the child will eat it note
- Return one dinner recommendation, not a long list
- Recommendation should include:
  - meal name
  - why this meal fits
  - estimated time/effort
  - simple ingredient/step outline
  - one fallback/tweak action
  - allergy/privacy caveat where applicable
- Add lightweight feedback actions:
  - Good enough
  - Too much work
  - Kid won’t eat
  - Missing ingredient
- Include empty/loading/error states
- Use existing app architecture and patterns
- Add tests where appropriate

Non-goals:

- Do not implement bedtime/story choice
- Do not build chapter navigation unless already trivial in current app
- Do not build a generic multi-chapter engine
- Do not add grocery integrations
- Do not add full meal planning
- Do not add heavy profile setup
- Do not make medical/nutrition/allergy guarantees
- Do not touch unrelated files
- Use the active local 1Less working copy at /Users/arku/Projects/AITXhackathon until the repo is renamed

Acceptance criteria:

- A parent can complete the dinner decision flow in under 60 seconds
- Output is one clear dinner decision, not many competing options
- The product copy preserves the broader 1Less positioning: parent decision relief, starting with dinner
- Dinner is treated as the first chapter/proof point, not the entire brand identity
- Allergy/diet constraints are reflected in the recommendation and caveat
- Parent can request a fallback/tweak without restarting the whole flow
- UI does not imply guaranteed allergy safety
- The flow feels like relief, not another form to fill out
- Existing app tests pass
- New tests cover the recommendation flow, constraint handling, and empty/error states where applicable
- Git diff contains only intended changes

Testing expectations:

- Run existing test suite
- Add unit/component tests if applicable
- Manual smoke test these cases:
  1. No constraints
  2. 15-minute low-energy dinner
  3. Nut allergy / ingredient avoidance
  4. Picky eater
  5. Missing ingredient / fallback
  6. Copy check: 1Less is not framed as dinner-only
  7. Copy check: no allergy guarantee or medical claim

Sophie review trigger:

Required before finalizing user-facing copy for:

- allergy caveat
- privacy language
- onboarding prompt
- parent-facing tone
- any wording around kids, safety, trust, or family memory

Stop / rollback condition:

Stop if the implementation starts expanding into:

- bedtime/story choice
- generic multi-chapter platform
- weekly meal planning
- grocery integrations
- detailed family profiles
- nutrition/medical claims
- broad parent command center functionality

Stop if Codex starts deciding product direction instead of implementing the approved task.

## 10. What Ginnie should verify before execution

Before any Codex execution, Ginnie should verify:

Source of truth:

- GitHub repo is https://github.com/nyhemant/AITXhackathon — legacy repo name; product name is 1Less
- Only active local 1Less working copy is /Users/arku/Projects/AITXhackathon on Mac mini until repo rename
- No MacBook Air or iCloud Drive copy is being used

Repo state:

- Current branch
- Git status
- Latest remote sync
- Uncommitted changes
- Existing work-in-progress task, if any
- Whether a product brief or operating-model doc already exists in the repo

Product clarity:

- Hemant approved this brief or revised it
- Dinner is Chapter 1 / first proof point
- 1Less is not framed as only a dinner app
- No bedtime implementation yet
- No generic chapter-platform implementation yet

Implementation readiness:

- Existing app architecture identified
- Likely files to touch listed before coding
- Test command known
- Local run/smoke command known
- Rollback plan clear

Trust/UX:

- Sophie review required before final copy if allergy/privacy/kid-safety wording is touched
- No unsafe claims
- No medical/nutrition guarantees
- No excessive sensitive data collection

Codex task quality:

- Objective is specific
- Scope and non-goals are explicit
- Acceptance criteria are testable
- Task is small enough for one Codex pass
- Codex is not asked to decide broader product direction

