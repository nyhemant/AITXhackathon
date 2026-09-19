# Hermes Review — 1Less MVP Brief and Codex Task Packet

<!-- Saved from Hemant Telegram attachment on 2026-05-16. Hermes advisory review; no repo writes by Hermes. -->

    Reviewed the two GitHub files:
    
    - docs/product/1less_mvp_product_brief_v0.2.md
    - docs/product/1less_codex_task_packet_chapter1_v0.md
    
    Role: advisor/product critic only. I did not code or write to repo.
    
    Verdict:
    Almost Codex-ready, but I would not execute yet. The brief and packet are strong, but Ginnie should tighten the trust contract and Story Picker scope before Codex starts.
    
    1. Strong parts
    
    The product direction is much clearer now.
    
    Strongest pieces:
    
    1. 1Less is no longer framed as only a dinner app
    
    The brief correctly says:
    
    - 1Less is parent decision relief
    - dinner is Chapter 1
    - bedtime story/book choice is Chapter 2/future
    - dinner is the first proof point, not the whole brand
    
    That is the right architecture.
    
    2. The MVP build is narrow
    
    The packet correctly limits the build to:
    
    - Chapter 1 dinner decision
    - no generic multi-chapter platform
    - no bedtime/story buildout
    - no grocery integration
    - no weekly meal planning
    - no heavy profile setup
    - no broad parent command center
    
    Good scope discipline.
    
    3. Codex task packet is operationally useful
    
    The packet gives Codex:
    
    - source of truth
    - current repo context
    - likely files to inspect/touch
    - test command
    - local run command
    - acceptance criteria
    - smoke cases
    - stop/rollback conditions
    - suggested Codex prompt
    
    This is much better than a vague “build the MVP” prompt.
    
    4. The “one clear decision” principle is strong
    
    Both docs preserve the core product behavior:
    
    - one dinner recommendation
    - not a list
    - under 60 seconds
    - low-burden input
    - fallback/tweak option
    
    That matches the 1Less promise.
    
    5. The packet already recognizes the Story Picker risk
    
    The task packet explicitly says the current app has two tabs: Dinner Planner and Story Picker, and that Codex should not expand Story Picker. That is important because the repo already contains Story Picker code.
    
    2. Risks / scope creep
    
    Main scope risks:
    
    1. “Chapter 2 bedtime story/book choice” could tempt Codex into platform work
    
    Even though the packet says not to build it, the repo already has Story Picker code. Codex may see existing Story Picker code and decide to “harmonize,” “complete,” “polish,” or “generalize” it.
    
    Ginnie should make this even stricter:
    
    For this task:
    - Story Picker may only receive copy-safe adjustments if required to avoid brand confusion.
    - No new Story Picker behavior.
    - No new bedtime recommendation logic.
    - No shared chapter engine.
    - No chapter navigation unless already present and copy-only/trivial.
    - If Story Picker tests fail because of copy changes, adjust minimally.
    
    2. “Chapter” language could cause over-abstraction
    
    “Chapter 1” is good product language, but engineering might overreact and build:
    
    - chapter registry
    - generic chapter model
    - chapter router
    - chapter cards
    - reusable decision engine
    - multi-chapter architecture
    
    The packet says not to, but I would reinforce:
    
    Use copy-level positioning only. Do not introduce architectural chapter abstractions in this task.
    
    3. Feedback/fallback could become persistence/profile work
    
    The brief says “1Less lightly remembers what worked,” but the packet wisely says use existing backend feedback behavior where possible.
    
    Ginnie should keep this bounded:
    
    - Expose or improve lightweight feedback UI if existing backend supports it.
    - Do not add accounts.
    - Do not add long-term family memory storage.
    - Do not add database/profile schema unless already present and trivial.
    
    4. “Use what you have” can imply pantry accuracy
    
    The brief mentions “use-what-you-have guidance” and “what do you have?” That’s fine, but it can imply the app knows pantry contents accurately.
    
    Need wording:
    
    “Based only on what you enter tonight.”
    
    Not:
    
    “I know what’s in your pantry.”
    
    3. Trust / privacy / allergy concerns
    
    This is the main blocker before Codex.
    
    Your stated concerns are valid. The current docs partially address them, but not tightly enough.
    
    Concern A: “Respect basic constraints” is too broad
    
    The brief currently says:
    
    “1Less gives a busy parent one clear dinner recommendation for tonight that respects basic family constraints…”
    
    This is risky because “constraints” could be read as:
    
    - allergy safety
    - medical diet support
    - nutrition optimization
    - budget optimization
    - pantry accuracy
    - picky-eater expertise
    - cultural/religious dietary correctness
    
    Suggested revision:
    
    Replace:
    
    “respects basic family constraints”
    
    With:
    
    “uses the basic preferences and avoidances the parent enters tonight, without claiming medical, allergy, nutrition, budget, or pantry accuracy.”
    
    Better MVP promise:
    
    “1Less gives a busy parent one clear dinner recommendation for tonight using simple preferences, avoidances, time, and energy level — without claiming medical, allergy, nutrition, budget, or pantry accuracy.”
    
    Concern B: Allergy caveat must appear in-product
    
    The task packet says:
    
    - recommendation should include allergy/preference caveat when relevant
    - UI should not imply guaranteed allergy safety
    - suggested caveat included
    
    This is good, but I would make it mandatory in the task packet:
    
    If the user selects or types any allergy/avoidance, the recommendation UI must show an in-product caveat near the recommendation, not only in docs or policy copy.
    
    Suggested acceptance criterion:
    
    “When allergy or avoidance input is present, the dinner recommendation must show an in-product caution: ‘1Less can help avoid ingredients you flag, but it cannot guarantee allergy safety. Always check labels and use your judgment for serious allergies.’”
    
    Concern C: Explicitly avoid collecting sensitive data
    
    The brief says “be cautious with” child names, medical conditions, detailed health data, exact location, etc.
    
    That is not strong enough for Codex. It should say “must not ask for or require.”
    
    Suggested revision:
    
    MVP must not ask for or require:
    - child names
    - medical conditions
    - precise location
    - detailed health/nutrition goals
    - school schedules
    - photos of pantry/fridge
    - grocery purchase history
    
    If a user voluntarily types sensitive info into free text, the product should not highlight, store, or build profile features around it in this MVP.
    
    Concern D: Every recommendation should have required structure
    
    The docs mostly address this. The task packet says output should include:
    
    - meal name
    - why it fits tonight
    - estimated time/effort
    - simple ingredient/use-what-you-have guidance
    - one fallback/tweak path
    - allergy/preference caveat when relevant
    
    Good. I’d tighten it from “should include” to “must include.”
    
    Required recommendation card:
    
    Every dinner recommendation must include:
    1. Dinner name
    2. Why it fits tonight
    3. Rough time/effort
    4. One fallback/tweak action
    
    When allergy/avoidance is present:
    5. In-product allergy caveat
    
    Concern E: Picky eater claims
    
    The docs mention picky eaters. That’s okay, but avoid sounding like the app can solve picky eating.
    
    Better language:
    
    “kid-friendly / familiar option based on what you told me”
    
    Avoid:
    
    “picky-eater approved”
    “your kid will eat this”
    “guaranteed kid-friendly”
    
    4. Suggested revisions
    
    I’d ask Ginnie to make these exact changes before execution.
    
    Revision 1: Tighten MVP promise in product brief
    
    In docs/product/1less_mvp_product_brief_v0.2.md, section 4, replace:
    
    “1Less gives a busy parent one clear dinner recommendation for tonight that respects basic family constraints and requires minimal effort to act on.”
    
    With:
    
    “1Less gives a busy parent one clear dinner recommendation for tonight using simple preferences, avoidances, time, and energy level entered by the parent. It should reduce decision fatigue without claiming medical, allergy, nutrition, budget, or pantry accuracy.”
    
    Revision 2: Change “be cautious with” to “must not ask for”
    
    In section 6, replace the privacy boundary language with something firmer:
    
    “MVP must not ask for or require:
    - child names
    - medical conditions
    - precise location
    - detailed health/nutrition goals
    - school schedules
    - photos of pantry/fridge
    - grocery purchase history
    
    If a parent voluntarily types sensitive information into free text, this MVP should not highlight it, build profile features around it, or require it for future use.”
    
    Revision 3: Add required in-product allergy caveat
    
    In both brief and packet, add:
    
    “If allergy or avoidance input is present, the recommendation UI must show an in-product caveat near the recommendation. This cannot live only in docs, policy text, or footer copy.”
    
    Suggested caveat:
    
    “1Less can help avoid ingredients you flag, but it cannot guarantee allergy safety. Always check labels and use your judgment for serious allergies.”
    
    Revision 4: Make recommendation structure mandatory
    
    In packet section “Recommendation output,” change “should return” / “should include” to “must return” / “must include.”
    
    Required structure:
    
    Every recommendation must include:
    - dinner name
    - why it fits tonight
    - rough time/effort
    - simple ingredient/use-what-you-have guidance based only on parent input
    - one fallback/tweak action
    
    When relevant:
    - allergy/preference caveat
    
    Revision 5: Add strict Story Picker guard
    
    In the task packet’s Non-goals or Stop Conditions, add:
    
    “The repo already contains Story Picker code. For this task, Codex must not expand Story Picker behavior, bedtime/story recommendation logic, or generic chapter infrastructure. Story Picker may only receive minimal copy-safe adjustments if necessary to prevent brand confusion or keep existing tests passing.”
    
    Revision 6: Add “no generic chapter architecture” engineering constraint
    
    Add:
    
    “Use chapter language at the product/copy level only. Do not introduce a chapter registry, generic decision engine, chapter routing system, or multi-chapter data model in this task.”
    
    Revision 7: Tighten “use what you have”
    
    Add:
    
    “Any pantry/use-what-you-have language must be based only on what the parent enters in the current flow. Do not imply 1Less knows the household pantry or inventory.”
    
    5. Whether this is ready for Codex
    
    Not quite.
    
    My verdict:
    
    Conditionally ready after small trust/scope edits.
    
    I would not run Codex on the current packet exactly as-is because:
    
    - “respect basic constraints” is still too broad
    - sensitive data exclusions are advisory, not explicit
    - allergy caveat is present but not strongly required in-product
    - Story Picker risk needs stricter wording because the repo already has Story Picker code
    - “chapter” language needs a no-architecture guard
    
    This is not a major rewrite. It is a tightening pass.
    
    Once Ginnie patches those points, I’d consider it ready for a first Codex attempt.
    
    6. Changes Ginnie should make before execution
    
    Ask Ginnie to do the following before Codex:
    
    1. Patch product brief
    
    - Replace “respect basic constraints”
    - Add explicit “must not collect/ask for” sensitive data list
    - Add mandatory in-product allergy caveat rule
    - Clarify pantry/use-what-you-have is based only on current user input
    
    2. Patch Codex task packet
    
    - Make recommendation card structure mandatory
    - Add in-product allergy caveat acceptance criterion
    - Add no sensitive data collection acceptance criterion
    - Add stricter Story Picker guard
    - Add no generic chapter architecture constraint
    
    3. Update Codex prompt
    
    Add this to the suggested Codex prompt:
    
    “Important trust contract:
    Do not claim allergy safety, nutrition optimization, medical diet support, budget optimization, or pantry accuracy. If allergy/avoidance input is present, show an in-product allergy caveat near the recommendation. Do not ask for or require child names, medical conditions, precise location, or detailed health/nutrition goals.”
    
    And:
    
    “The repo already has Story Picker code. Do not expand Story Picker or build bedtime/story behavior. Only make minimal copy-safe adjustments if necessary.”
    
    4. Require Sophie-style review before final commit
    
    Sophie review should explicitly check:
    
    - Does the UI imply allergy safety?
    - Does “constraints” sound too broad?
    - Does any prompt invite sensitive child/medical data?
    - Does the recommendation feel like relief, not another chore?
    - Does the app avoid overclaiming pantry/nutrition/budget correctness?
    - Did Codex accidentally expand Story Picker or create a chapter platform?
    
    5. Ginnie should verify after Codex
    
    Beyond tests, Ginnie should manually inspect for:
    
    - no new Story Picker functionality
    - no new chapter engine
    - no new profile/account/data collection
    - no child-name or medical-condition prompts
    - recommendation card always has:
      - dinner name
      - why it fits
      - rough time/effort
      - one fallback action
    - allergy caveat appears in the UI when allergy/avoidance is selected/typed
    - copy says “starting with dinner” without making dinner the whole brand
    
    Bottom line
    
    The brief and task packet are strong. They correctly protect the “1Less is broader than dinner” idea while keeping the first build narrow.
    
    But Sophie’s concern is right: the trust contract needs to be more explicit before coding.
    
    My recommendation to Hemant/Ginnie:
    
    Do one small doc-patch pass first.
    Then run Codex.