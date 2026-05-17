from datetime import datetime
import json
import subprocess
import sys
import unittest

from busyparent_agent.agent import BusyParentAgent
from busyparent_agent.service import ALLERGY_CAVEAT, create_dinner_decision_session, create_session, parse_now, run_book_scenario
from busyparent_agent.web import HTML, MAX_REQUEST_BYTES, SECURITY_HEADERS, SESSIONS, WebHandler
from busyparent_agent import tools
from busyparent_agent import inventory as inventory_engine
from busyparent_agent.adapters import costco_bulk
from busyparent_agent.adapters import mock_instacart
from busyparent_agent.adapters import mock_photo_scan


class AgentRulesTest(unittest.TestCase):
    def test_delivery_logic_lunch_allows_delivery(self):
        result = tools.check_delivery_window(datetime(2026, 5, 8, 13, 0))

        self.assertEqual(result["strategy"], "delivery_ok")
        self.assertTrue(result["can_use_delivery"])
        self.assertFalse(result["pantry_first"])

    def test_delivery_logic_near_dinner_is_pantry_first(self):
        result = tools.check_delivery_window(datetime(2026, 5, 8, 17, 30))

        self.assertEqual(result["strategy"], "pantry_first")
        self.assertFalse(result["can_use_delivery"])
        self.assertTrue(result["pantry_first"])

    def test_first_recommendation_leads_with_one_meal(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("What should I make for dinner tonight?")

        self.assertIn("Make ", response)
        self.assertIn("Egg Fried Rice", response)
        self.assertIn("I am leading with one option", response)
        self.assertNotIn("1.", response)
        self.assertIsNotNone(agent.current_recommendation)

    def test_lunch_branch_uses_small_reviewable_grocery_list(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 9, 12, 30))

        response = agent.reply("What should I make for dinner tonight?")

        self.assertIn("Because we are planning early", response)
        self.assertIn("Reviewable grocery cart: avocado, berries.", response)
        self.assertEqual(agent.current_recommendation["missing"], ["avocado", "berries"])

    def test_close_to_dinner_branch_remains_pantry_first_nothing_required(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("What should I make for dinner tonight?")

        self.assertIn("It is close to dinner", response)
        self.assertIn("Reviewable grocery list: nothing required.", response)
        self.assertEqual(agent.delivery_window["strategy"], "pantry_first")
        self.assertEqual(agent.current_recommendation["name"], "Egg Fried Rice")

    def test_dinner_prompts_shift_recommendation_by_intent(self):
        cases = {
            "I’m exhausted — give me the lowest-effort dinner.": "Black Bean Quesadillas",
            "High-protein and kid-friendly.": "Chicken and Corn Rice Bowls",
            "Light dinner, not too heavy.": "Pasta Marinara with Carrots",
            "No grocery run tonight.": "Egg Fried Rice",
        }

        for prompt, expected in cases.items():
            with self.subTest(prompt=prompt):
                agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))
                response = agent.reply(prompt)

                self.assertIn(f"Make {expected} tonight.", response)
                self.assertEqual(agent.current_recommendation["name"], expected)

    def test_kid_friendly_prompt_does_not_trigger_guest_flow(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("Make it picky-kid friendly.")

        self.assertIn("Make Black Bean Quesadillas tonight.", response)
        self.assertNotIn("guest plan", response)
        self.assertIsNotNone(agent.current_recommendation)

    def test_dinner_intent_trace_explains_prompt_weighting(self):
        trace_lines = []
        agent = BusyParentAgent(
            now=datetime(2026, 5, 8, 17, 30),
            trace=True,
            trace_sink=trace_lines.append,
        )

        agent.reply("High-protein and kid-friendly.")

        self.assertTrue(any(line.startswith("[intent]") for line in trace_lines))
        self.assertTrue(any("strongest protein fit" in line for line in trace_lines))
        self.assertTrue(any("Chicken and Corn Rice Bowls" in line for line in trace_lines))

    def test_rejection_returns_three_alternatives(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))
        agent.reply("What should I make for dinner tonight?")

        response = agent.reply("Not feeling that. Anything else?")

        self.assertIn("Here are three better directions", response)
        self.assertIn("I’d pick Black Bean Quesadillas if you want the least effort tonight.", response)
        self.assertEqual(len(agent.alternatives), 3)
        self.assertNotIn("Egg Fried Rice", [meal["name"] for meal in agent.alternatives])

    def test_selected_egg_fried_rice_plan_is_concise_and_parent_aware(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))
        agent.reply("What should I make for dinner tonight?")
        agent.reply("Not feeling that. Anything else?")

        response = agent.reply("Let's do egg fried rice.")

        self.assertIn("5 minutes prep, 12-15 minutes cook", response)
        self.assertIn("Kid adaptation", response)
        self.assertIn("Adult upgrade", response)
        self.assertIn("if eggs get rejected", response)

    def test_guest_constraints_revise_selected_meal(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))
        agent.reply("What should I make for dinner tonight?")
        agent.reply("Not feeling that. Anything else?")
        agent.reply("Let's do egg fried rice.")

        response = agent.reply("My daughter has a friend coming over. No nuts, no spicy food.")

        self.assertIn("Avoid nut ingredients", response)
        self.assertIn("Keep spice off", response)
        self.assertIn("verify packaged labels", response)
        self.assertIn("not an allergy safety guarantee", response)
        self.assertNotIn("guaranteed safe", response)
        self.assertTrue(agent.selected_meal["guest_constraints"]["no_nuts"])
        self.assertTrue(agent.selected_meal["guest_constraints"]["no_spicy"])

    def test_nut_allergy_switches_away_from_peanut_meal(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))
        agent.reply("Let's do peanut butter noodles.")

        response = agent.reply("Guest has a nut allergy and dislikes spice.")

        self.assertNotIn("Keep Peanut Butter Noodles", response)
        self.assertIn("Peanut Butter Noodles conflicts with the nut allergy", response)
        self.assertIn("Let's switch to Egg Fried Rice", response)
        self.assertNotIn("Reviewable grocery cart: peanut butter", response)
        self.assertNotIn("- peanut butter", response)
        self.assertIn("verify packaged labels", response)
        self.assertIn("not an allergy safety guarantee", response)
        self.assertEqual(agent.selected_meal["name"], "Egg Fried Rice")
        self.assertEqual(agent.selected_meal["missing"], [])


class ScenarioCliTest(unittest.TestCase):
    def run_scenario(self, scenario: str) -> str:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "busyparent_agent.app",
                "--scenario",
                scenario,
                "--trace",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout

    def test_scenario_dinner_runs_and_includes_pantry_first(self):
        output = self.run_scenario("dinner")

        self.assertIn("1Less", output)
        self.assertIn("[decision] pantry-first because it is close to dinner", output)
        self.assertIn("Reviewable grocery list: nothing required.", output)
        self.assertNotIn("Not feeling that", output)

    def test_scenario_lunch_runs_and_includes_fresh_grocery_items(self):
        output = self.run_scenario("lunch")

        self.assertIn("[decision] grocery delivery can help because planning starts earlier", output)
        self.assertIn("Reviewable grocery cart: avocado, berries.", output)
        self.assertNotIn("Not feeling that", output)

    def test_scenario_guest_runs_and_includes_constraints(self):
        output = self.run_scenario("guest")

        self.assertNotIn("Context: Selected meal is Egg Fried Rice.", output)
        self.assertIn("Parent: My daughter has a friend coming over. No nuts, no spicy food.", output)
        self.assertIn("Agent: Make Egg Fried Rice for the guest plan:", output)
        self.assertIn("[tool] apply_guest_constraints", output)
        self.assertIn("[decision] choose guest-safe dinner from guest child constraints", output)
        self.assertIn("Avoid nut ingredients", output)
        self.assertIn("Keep spice off", output)
        self.assertIn("verify packaged labels", output)

    def test_scenario_book_runs_and_returns_one_book(self):
        output = self.run_scenario("book")

        self.assertIn("[book] mock_epic.get_catalog_books -> 35 books", output)
        self.assertIn("[book] filter age/mood/time/availability", output)
        self.assertIn("[memory] recent reading history checked", output)
        self.assertIn("[decision] chose ", output)
        self.assertEqual(output.count("Tonight's pick:"), 1)
        self.assertIn("What should I read with Kunal tonight?", output)
        self.assertIn("Why it fits Kunal tonight:", output)
        self.assertIn("Read time: about ", output)
        self.assertIn("Format/source:", output)
        self.assertIn("mocked Epic-style catalog", output)
        self.assertIn("Parent prompts:", output)
        self.assertIn("1. ", output)
        self.assertIn("2. ", output)
        self.assertIn("3. ", output)
        self.assertIn("Tiny tomorrow activity:", output)
        self.assertIn("no real Epic login, API, scraping, or checkout is used", output)

    def test_scenario_dinner_does_not_include_storypath_copy(self):
        output = self.run_scenario("dinner")

        self.assertNotIn("Tonight's pick:", output)
        self.assertNotIn("mocked Epic-style catalog", output)


class ServiceAdapterTest(unittest.TestCase):
    def test_service_response_shape_is_channel_neutral(self):
        session = create_session(parse_now(None, scenario="lunch"), trace=True, scenario="lunch")

        response = session.send("What should I make for dinner tonight?", scenario="lunch")

        self.assertEqual(response["parent_message"], "What should I make for dinner tonight?")
        self.assertIn("Make Black Bean Quesadillas tonight.", response["message"])
        self.assertIn("avocado", response["grocery_items"])
        self.assertEqual(response["metadata"]["scenario"], "lunch")
        self.assertEqual(response["metadata"]["delivery_strategy"], "delivery_ok")
        self.assertTrue(any(line.startswith("[tool]") for line in response["trace"]))
        self.assertTrue(any(line.startswith("[decision]") for line in response["trace"]))

    def test_manual_noon_planning_message_uses_delivery_aware_branch(self):
        session = create_session(datetime(2026, 5, 8, 17, 30), trace=True)

        response = session.send("It is noon and I want to plan for dinner tonight")

        self.assertEqual(response["metadata"]["delivery_strategy"], "delivery_ok")
        self.assertIn("Reviewable grocery cart: avocado, berries.", response["message"])
        self.assertIn("avocado", response["grocery_items"])
        self.assertTrue(
            any("[decision] grocery delivery can help because planning starts earlier" in line for line in response["trace"])
        )

    def test_manual_dinner_now_message_stays_pantry_first(self):
        session = create_session(datetime(2026, 5, 9, 12, 30), trace=True)

        response = session.send("I just got home and need dinner now")

        self.assertEqual(response["metadata"]["delivery_strategy"], "pantry_first")
        self.assertIn("Reviewable grocery list: nothing required.", response["message"])
        self.assertTrue(any("[decision] pantry-first because it is close to dinner" in line for line in response["trace"]))

    def test_urgent_twenty_minute_prompt_skips_grocery_shopping(self):
        session = create_session(datetime(2026, 5, 9, 12, 30), trace=True)

        response = session.send("I need dinner in 20 minutes.")

        self.assertEqual(response["metadata"]["delivery_strategy"], "pantry_first")
        self.assertIn("skipping grocery shopping", response["message"])
        self.assertIn("Reviewable grocery list: nothing required.", response["message"])
        self.assertNotIn("Reviewable grocery cart:", response["message"])
        self.assertNotIn("grocery delivery can help because planning starts earlier", "\n".join(response["trace"]))

    def test_story_picker_prompts_shift_recommendation_by_intent(self):
        cases = {
            "Pick a calm bedtime book for Kunal.": "Goodnight, Goodnight, Construction Site",
            "Pick something for Arya that feels a little grown-up.": "What Do You Do With an Idea?",
            "Give me a silly read-aloud.": "Don't Let the Pigeon Drive the Bus!",
            "Pick something about bravery and confidence.": "Giraffes Can't Dance",
            "I’m tired — keep it under 10 minutes.": "Brown Bear, Brown Bear, What Do You See?",
            "Pick a book with easy parent prompts.": "Press Here",
            "Arya wants something science-y or curious.": "Mae Among the Stars",
            "Kunal wants rhyme or repetition.": "Chicka Chicka Boom Boom",
        }

        for prompt, expected in cases.items():
            with self.subTest(prompt=prompt):
                response = run_book_scenario(trace=True, parent_message=prompt)

                self.assertEqual(response["metadata"]["book_recommendation"], expected)
                self.assertIn(f"Tonight's pick: {expected}", response["message"])
                self.assertTrue(any(line.startswith("[book] prompt intent ->") for line in response["trace"]))

    def test_locked_time_context_ignores_manual_noon_phrase(self):
        session = create_session(
            datetime(2026, 5, 8, 17, 30),
            trace=True,
            locked_time_context=True,
        )

        response = session.send("It is noon and I want to plan for dinner tonight")

        self.assertEqual(response["metadata"]["delivery_strategy"], "pantry_first")
        self.assertIn("Reviewable grocery list: nothing required.", response["message"])

    def test_web_module_command_is_available(self):
        result = subprocess.run(
            [sys.executable, "-m", "busyparent_agent.web", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("--port", result.stdout)
        self.assertIn("local web chat", result.stdout)


class WebApiScenarioTest(unittest.TestCase):
    def tearDown(self):
        SESSIONS.clear()

    def handle_scenario(self, scenario: str) -> dict:
        handler = object.__new__(WebHandler)
        handler._read_json = lambda: {"scenario": scenario}
        handler._send_json = lambda payload: setattr(handler, "json_payload", payload)
        handler.send_error = lambda code, message=None: setattr(handler, "error", (code, message))

        WebHandler._handle_scenario(handler)
        self.assertFalse(hasattr(handler, "error"))
        return handler.json_payload

    def handle_chat(self, payload: dict) -> dict:
        handler = object.__new__(WebHandler)
        handler._read_json = lambda: payload
        handler._send_json = lambda response: setattr(handler, "json_payload", response)
        handler.send_error = lambda code, message=None: setattr(handler, "error", (code, message))

        WebHandler._handle_chat(handler)
        self.assertFalse(hasattr(handler, "error"))
        return handler.json_payload

    def handle_scenario_error(self, scenario: str) -> tuple[int, str | None]:
        handler = object.__new__(WebHandler)
        handler._read_json = lambda: {"scenario": scenario}
        handler._send_json = lambda payload: setattr(handler, "json_payload", payload)
        handler.send_error = lambda code, message=None: setattr(handler, "error", (code, message))

        WebHandler._handle_scenario(handler)
        self.assertTrue(hasattr(handler, "error"))
        return handler.error

    def handle_chat_error(self, payload: dict) -> tuple[int, str | None]:
        handler = object.__new__(WebHandler)
        handler._read_json = lambda: payload
        handler._send_json = lambda response: setattr(handler, "json_payload", response)
        handler.send_error = lambda code, message=None: setattr(handler, "error", (code, message))

        WebHandler._handle_chat(handler)
        self.assertTrue(hasattr(handler, "error"))
        return handler.error

    def test_web_page_exposes_dinner_only_public_alpha(self):
        self.assertIn(">\n            Dinner\n          </div>", HTML)
        self.assertNotIn("Chapter 1", HTML)
        self.assertNotIn("Story Picker", HTML)
        self.assertNotIn("story-tab", HTML)
        self.assertNotIn('data-scenario="book"', HTML)
        self.assertNotIn('data-scenario="book_siblings"', HTML)
        self.assertNotIn("Read with both kids", HTML)
        self.assertNotIn("One bedtime book that fits tonight.", HTML)
        self.assertNotIn("Story Picker starter prompts", HTML)
        self.assertNotIn("What should I read with both of them tonight?", HTML)
        self.assertNotIn("Giving me a silly read-aloud.", HTML)
        self.assertNotIn("Reading History", HTML)
        self.assertNotIn("Instant access", HTML)
        self.assertNotIn('class="room-actions book-panel', HTML)
        self.assertNotIn('role="tab"', HTML)
        self.assertIn('role="tabpanel"', HTML)
        self.assertIn('class="brand-lockup"', HTML)
        self.assertIn('class="brand-logo"', HTML)
        self.assertIn('alt="1Less logo"', HTML)
        self.assertIn('src="/BMLogo.svg"', HTML)
        self.assertIn('<p class="tagline">One less decision for busy parents.</p>', HTML)
        self.assertIn("<strong>Alpha testing</strong>", HTML)
        self.assertNotIn("Alpha testing now:", HTML)
        self.assertNotIn("try the dinner flow with non-sensitive details and tell us if it actually removes one decision", HTML)
        self.assertNotIn("non-sensitive details", HTML)
        self.assertIn("Why dinner first?", HTML)
        self.assertIn("this alpha is dinner-only", HTML)
        self.assertIn("without creating another chore", HTML)
        self.assertIn("Dinner is the current 1Less proof point", HTML)
        self.assertIn("Tonight's dinner, decided.", HTML)
        self.assertIn("Dinner plan considers", HTML)
        self.assertIn("Fit for", HTML)
        self.assertNotIn('class="room-actions dinner-panel" data-panel="dinner"', HTML)
        self.assertNotIn("Hackathon Demo Scenarios", HTML)
        self.assertIn('class="mode-tabs" aria-label="1Less public alpha flow"', HTML)
        self.assertIn('class="mode-tab active" id="dinner-tab"', HTML)
        self.assertIn('aria-current="page"', HTML)
        self.assertNotIn('class="scenario-chip" data-scenario="dinner"', HTML)
        self.assertNotIn('aria-pressed="false">No constraints</button>', HTML)
        self.assertNotIn("let selectedScenario = null", HTML)
        self.assertNotIn("function updateScenarioButtons()", HTML)
        self.assertNotIn('button.classList.toggle("pressed", pressed)', HTML)
        self.assertNotIn('button.setAttribute("aria-pressed", String(pressed))', HTML)
        self.assertNotIn("clearScenarioState();", HTML)
        self.assertIn('<body data-mode="dinner">', HTML)
        self.assertIn("document.body.dataset.mode = activeMode", HTML)
        self.assertIn("mode: activeMode", HTML)
        self.assertIn('id="promptButton"', HTML)
        self.assertIn('aria-label="Try a real night"', HTML)
        self.assertIn('<span>Try a</span><span>real night</span>', HTML)
        self.assertNotIn('<span>Sample</span><span>Prompts</span>', HTML)
        self.assertNotIn('>Prompts</button>', HTML)
        self.assertIn('aria-label="Editable real-life dinner prompts"', HTML)
        self.assertIn("Pick one, then edit it to match tonight.", HTML)
        self.assertIn("It’s 5pm, everyone is hungry, I have 10 minutes and barely cooking energy. Make it picky-kid friendly.", HTML)
        self.assertIn("I have tortillas, cheese, black beans, rice, and apples. I have 15 minutes and no store run.", HTML)
        self.assertIn("Vegetarian tonight. I have rice, eggs, frozen peas, and 20 minutes. Normal energy.", HTML)
        self.assertIn("Avoid peanuts and tree nuts tonight. I have pasta, jarred sauce, frozen peas, and 15 minutes.", HTML)
        self.assertIn("My kid rejects mixed foods. I have chicken, rice, cucumber, yogurt, and 20 minutes. Make it easy to deconstruct.", HTML)
        self.assertIn("I have a few options but no brain left to decide. We have eggs, toast, fruit, rice, and frozen vegetables. Pick one easy dinner.", HTML)
        self.assertNotIn("Use pantry or freezer basics I already have.", HTML)
        self.assertIn("Good enough", HTML)
        self.assertIn("Give me backup", HTML)
        self.assertIn("renderPromptMenu(activeMode)", HTML)
        self.assertIn('promptMenu.setAttribute("aria-label", "Editable real-life dinner prompts")', HTML)
        self.assertIn('event.target.closest("[data-prompt]")', HTML)
        self.assertIn("async function sendCurrentInput()", HTML)
        self.assertIn("input.value = button.dataset.prompt", HTML)
        self.assertIn("input.focus();", HTML)
        self.assertNotIn("input.value = button.dataset.prompt;\n        closePromptMenu();\n        await sendCurrentInput();", HTML)
        self.assertIn("closePromptMenu();", HTML)
        self.assertIn('event.key === "Escape"', HTML)

    def test_public_demo_security_headers_are_declared(self):
        self.assertEqual(MAX_REQUEST_BYTES, 24_000)
        self.assertEqual(SECURITY_HEADERS["X-Content-Type-Options"], "nosniff")
        self.assertEqual(SECURITY_HEADERS["X-Frame-Options"], "DENY")
        self.assertIn("frame-ancestors 'none'", SECURITY_HEADERS["Content-Security-Policy"])
        self.assertIn("object-src 'none'", SECURITY_HEADERS["Content-Security-Policy"])
        self.assertIn("form-action 'self'", SECURITY_HEADERS["Content-Security-Policy"])
        self.assertIn("camera=()", SECURITY_HEADERS["Permissions-Policy"])
        self.assertIn("payment=()", SECURITY_HEADERS["Permissions-Policy"])

    def test_story_picker_code_is_preserved_outside_public_web_flow(self):
        response = run_book_scenario(trace=True, parent_message="What should I read with Kunal tonight?")

        self.assertEqual(response["metadata"]["scenario"], "book")
        self.assertIn("Tonight's pick:", response["message"])
        self.assertIn("Parent prompts:", response["message"])
        self.assertIn("Tiny tomorrow activity:", response["message"])
        self.assertIn("mocked Epic-style catalog", response["message"])
        self.assertIn("no real Epic login, API, scraping, or checkout is used", response["message"])
        self.assertTrue(any(line.startswith("[book]") for line in response["trace"]))

    def test_story_picker_web_scenarios_are_not_public_alpha_routes(self):
        self.assertEqual(self.handle_scenario_error("book"), (400, "Unknown scenario"))
        self.assertEqual(self.handle_scenario_error("book_siblings"), (400, "Unknown scenario"))

    def test_dinner_web_api_scenario_still_returns_dinner_output(self):
        payload = self.handle_scenario("dinner")
        response = payload["responses"][0]

        self.assertEqual(response["metadata"]["scenario"], "dinner")
        self.assertEqual(response["metadata"]["chapter"], "chapter_1_dinner_decision")
        self.assertIn("Tonight:", response["message"])
        self.assertIn("One decision, not a recipe search.", response["message"])
        self.assertNotIn("Reviewable grocery", response["message"])
        self.assertNotIn("Tonight's pick:", response["message"])
        self.assertNotIn("mocked Epic-style catalog", response["message"])

    def test_chapter1_dinner_session_returns_one_meal_and_feedback_backup(self):
        session = create_dinner_decision_session()

        first = session.send("I have 15 minutes and barely cooking energy.")
        backup = session.send("Give me backup")

        self.assertIn("Tonight:", first["message"])
        self.assertEqual(first["message"].count("Tonight:"), 1)
        self.assertIn("Time/effort:", first["message"])
        self.assertIn("Fallback/tweak:", first["message"])
        self.assertIn("Backup:", backup["message"])
        self.assertNotEqual(first["metadata"]["current_recommendation"], backup["metadata"]["current_recommendation"])

    def test_chapter1_too_much_work_backup_is_meaningfully_easier(self):
        session = create_dinner_decision_session()

        first = session.send("I have 30 minutes and can cook.")
        backup = session.send("Too much work")

        self.assertEqual(first["metadata"]["current_recommendation"], "Sheet-pan chicken and corn rice bowls")
        self.assertEqual(backup["metadata"]["current_recommendation"], "Rice and Peas Bowl")
        self.assertIn("Backup: Rice and Peas Bowl.", backup["message"])
        self.assertEqual(backup["message"].count("Backup:"), 1)
        self.assertIn("Why this is easier: faster and fewer steps", backup["message"])
        self.assertIn("low-effort version", backup["message"])
        self.assertIn("Time/effort: about 10 minutes, low effort.", backup["message"])
        self.assertNotIn("1.", backup["message"])
        self.assertLess(backup["message"].find("Rice and Peas Bowl"), backup["message"].find("Simple plan:"))

    def test_chapter1_too_much_work_backup_respects_avoidance(self):
        session = create_dinner_decision_session()

        session.send("Avoid eggs. I have 30 minutes and can cook.")
        backup = session.send("Too much work")

        self.assertEqual(backup["metadata"]["current_recommendation"], "Rice and Peas Bowl")
        self.assertIn(ALLERGY_CAVEAT, backup["message"])
        self.assertTrue(backup["metadata"]["allergy_caveat"])
        self.assertNotIn("egg", backup["message"].lower())

    def test_chapter1_only_have_sparse_ingredients_uses_listed_constraint(self):
        session = create_dinner_decision_session()

        response = session.send("Only rice and frozen peas tonight.")

        self.assertEqual(response["metadata"]["current_recommendation"], "Rice and Peas Bowl")
        self.assertIn("Constraint heard", response["message"])
        self.assertIn("not assuming a remembered pantry", response["message"])
        self.assertIn("simplest dinner from only the rice and peas you listed", response["message"])
        self.assertNotIn("Black Bean Tacos", response["message"])
        self.assertNotIn(ALLERGY_CAVEAT, response["message"])
        self.assertFalse(response["metadata"]["allergy_caveat"])

    def test_chapter1_allergy_avoidance_uses_mandatory_caveat_without_guarantee(self):
        session = create_dinner_decision_session()

        response = session.send("Avoid peanuts and tree nuts tonight. Make it picky-kid friendly.")

        self.assertIn(ALLERGY_CAVEAT, response["message"])
        self.assertTrue(response["metadata"]["allergy_caveat"])
        self.assertNotIn("guaranteed allergy-free", response["message"].lower())
        self.assertNotIn("safe for your child", response["message"].lower())

    def test_chapter1_plain_minutes_prompt_does_not_trigger_allergy_caveat(self):
        session = create_dinner_decision_session()

        response = session.send("I have 30 minutes and can cook.")

        self.assertNotIn(ALLERGY_CAVEAT, response["message"])
        self.assertFalse(response["metadata"]["allergy_caveat"])

    def test_chapter1_avoid_terms_do_not_leak_into_recommendation_copy(self):
        session = create_dinner_decision_session()

        response = session.send("Dairy-free, avoid eggs. I have 20 minutes.")
        lower_message = response["message"].lower()

        self.assertIn(ALLERGY_CAVEAT, response["message"])
        self.assertNotIn(" egg", lower_message)
        self.assertNotIn("eggs", lower_message)
        self.assertNotIn("cheese", lower_message)
        self.assertNotIn("milk", lower_message)
        self.assertNotIn("yogurt", lower_message)

    def test_chapter1_positive_ingredient_context_biases_recommendation_without_caveat(self):
        session = create_dinner_decision_session()

        response = session.send("I have rice, eggs, and frozen peas. I have 20 minutes and normal energy.")

        self.assertEqual(response["metadata"]["current_recommendation"], "Egg Fried Rice with peas")
        self.assertIn("Tonight: Egg Fried Rice with peas.", response["message"])
        self.assertIn("it uses ingredients you said you have", response["message"])
        self.assertNotIn(ALLERGY_CAVEAT, response["message"])
        self.assertFalse(response["metadata"]["allergy_caveat"])

    def test_chapter1_explicit_egg_avoidance_blocks_egg_meal_and_shows_caveat(self):
        session = create_dinner_decision_session()

        response = session.send("Avoid eggs. I have rice and frozen peas. I have 20 minutes.")

        self.assertNotEqual(response["metadata"]["current_recommendation"], "Egg Fried Rice with peas")
        self.assertIn(ALLERGY_CAVEAT, response["message"])
        self.assertTrue(response["metadata"]["allergy_caveat"])
        self.assertNotIn("egg", response["message"].lower())

    def test_chapter1_egg_allergy_blocks_egg_meal_and_shows_caveat(self):
        session = create_dinner_decision_session()

        response = session.send("Egg allergy. I have rice and frozen peas. I have 20 minutes.")

        self.assertNotEqual(response["metadata"]["current_recommendation"], "Egg Fried Rice with peas")
        self.assertIn(ALLERGY_CAVEAT, response["message"])
        self.assertTrue(response["metadata"]["allergy_caveat"])

    def test_chapter1_without_and_free_phrases_are_avoidance_signals(self):
        session = create_dinner_decision_session()

        response = session.send("Without dairy tonight. Egg-free too. I have rice and frozen peas. I have 20 minutes.")

        self.assertIn(ALLERGY_CAVEAT, response["message"])
        self.assertTrue(response["metadata"]["allergy_caveat"])
        self.assertNotIn("egg", response["message"].lower())
        self.assertNotIn("cheese", response["message"].lower())
        self.assertNotIn("milk", response["message"].lower())
        self.assertNotIn("yogurt", response["message"].lower())

    def test_story_picker_web_chat_mode_is_not_public_alpha_flow(self):
        error = self.handle_chat_error(
            {
                "mode": "book",
                "message": "What should I read with both of them tonight?",
            }
        )

        self.assertEqual(error, (404, "Story Picker is not part of the public alpha"))


class HouseholdMemoryTest(unittest.TestCase):
    def setUp(self):
        self.family = tools.get_family_profile()
        self.inventory = tools.estimate_inventory()
        self.meals = tools.get_meal_options()
        self.delivery_window = tools.check_delivery_window(datetime(2026, 5, 8, 17, 30))

    def meal(self, name: str) -> dict:
        return next(meal for meal in self.meals if meal["name"] == name)

    def score(self, meal_name: str, history: list[dict]) -> float:
        return tools._score_meal(
            self.meal(meal_name),
            self.family,
            self.inventory,
            self.delivery_window,
            history,
            datetime(2026, 5, 8, 17, 30),
        )

    def test_recently_served_meal_is_penalized(self):
        no_history = self.score("Black Bean Quesadillas", [])
        recent = self.score(
            "Black Bean Quesadillas",
            [{"date": "2026-05-07", "event": "served", "meal": "Black Bean Quesadillas"}],
        )

        self.assertLess(recent, no_history)

    def test_recently_rejected_meal_is_penalized(self):
        no_history = self.score("Peanut Butter Noodles", [])
        recent = self.score(
            "Peanut Butter Noodles",
            [{"date": "2026-05-07", "event": "rejected", "meal": "Peanut Butter Noodles"}],
        )

        self.assertLess(recent, no_history)

    def test_favorites_are_boosted_when_not_recent(self):
        egg = self.meal("Egg Fried Rice")
        neutral = dict(egg, favorite_score=0, kid_approved=False, usual_popularity=0)

        boosted = tools._score_meal(
            egg,
            self.family,
            self.inventory,
            self.delivery_window,
            [],
            datetime(2026, 5, 8, 17, 30),
        )
        unboosted = tools._score_meal(
            neutral,
            self.family,
            self.inventory,
            self.delivery_window,
            [],
            datetime(2026, 5, 8, 17, 30),
        )

        self.assertGreater(boosted, unboosted)

    def test_recommendation_avoids_back_to_back_repeat_when_good_alternative_exists(self):
        recommendation = tools.recommend_meal(
            self.family,
            self.inventory,
            tools.get_grocery_history(),
            self.meals,
            self.delivery_window,
            [
                {"date": "2026-05-07", "event": "served", "meal": "Black Bean Quesadillas"},
                {"date": "2026-05-05", "event": "accepted", "meal": "Egg Fried Rice"},
            ],
            datetime(2026, 5, 8, 17, 30),
        )

        self.assertEqual(recommendation["name"], "Egg Fried Rice")


class ConversationalFeedbackTest(unittest.TestCase):
    def setUp(self):
        self.history_path = tools.DATA_DIR / "meal_history.json"
        self.original_history = self.history_path.read_text(encoding="utf-8")

    def tearDown(self):
        self.history_path.write_text(self.original_history, encoding="utf-8")

    def saved_events(self) -> list[dict]:
        return json.loads(self.history_path.read_text(encoding="utf-8"))

    def test_explicit_meal_feedback_saves_hit(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("Egg fried rice was a hit.")

        self.assertIn("Egg Fried Rice was a hit", response)
        self.assertEqual(self.saved_events()[-1]["meal"], "Egg Fried Rice")
        self.assertEqual(self.saved_events()[-1]["event"], "kid_liked")

    def test_implicit_feedback_after_recommendation_uses_current_meal(self):
        traces = []
        agent = BusyParentAgent(
            now=datetime(2026, 5, 8, 17, 30),
            trace=True,
            trace_sink=traces.append,
        )
        agent.reply("What should I make for dinner tonight?")

        response = agent.reply("The kids loved this.")

        self.assertIn("Egg Fried Rice was a hit", response)
        self.assertEqual(self.saved_events()[-1]["meal"], "Egg Fried Rice")
        self.assertEqual(self.saved_events()[-1]["event"], "kid_liked")
        self.assertIn("[memory] saved feedback -> Egg Fried Rice, kid_liked", traces)

    def test_avoid_request_saves_avoid_this_week(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("Don't suggest quesadillas again this week.")

        self.assertIn("avoid Black Bean Quesadillas", response)
        self.assertEqual(self.saved_events()[-1]["meal"], "Black Bean Quesadillas")
        self.assertEqual(self.saved_events()[-1]["event"], "avoid_this_week")

    def test_served_event_from_yesterday_message(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("We had quesadillas yesterday.")

        self.assertIn("served Black Bean Quesadillas", response)
        self.assertEqual(self.saved_events()[-1]["meal"], "Black Bean Quesadillas")
        self.assertEqual(self.saved_events()[-1]["event"], "served")
        self.assertEqual(self.saved_events()[-1]["date"], "2026-05-07")

    def test_future_recommendation_penalizes_avoid_this_week_and_recently_served(self):
        family = tools.get_family_profile()
        inventory = tools.estimate_inventory()
        grocery_history = tools.get_grocery_history()
        meals = tools.get_meal_options()
        delivery_window = tools.check_delivery_window(datetime(2026, 5, 8, 17, 30))

        recommendation = tools.recommend_meal(
            family,
            inventory,
            grocery_history,
            meals,
            delivery_window,
            [
                {"date": "2026-05-08", "event": "avoid_this_week", "meal": "Egg Fried Rice"},
                {"date": "2026-05-07", "event": "served", "meal": "Egg Fried Rice"},
            ],
            datetime(2026, 5, 8, 17, 30),
        )

        self.assertEqual(recommendation["name"], "Black Bean Quesadillas")


class InventoryConfidenceTest(unittest.TestCase):
    def test_photo_scan_adapter_returns_deterministic_fixture(self):
        latest = mock_photo_scan.get_latest_scan("fridge_photo")
        scanned = mock_photo_scan.scan_photo("data/sample_photos/fridge_demo.jpg", "fridge_photo")

        self.assertEqual(latest["scan_id"], "fridge-demo-001")
        self.assertEqual(scanned["scan_id"], "fridge-demo-001")
        self.assertTrue(any(item["name"] == "eggs" for item in scanned["items"]))

    def test_photo_scan_unknown_items_are_preserved(self):
        scan = mock_photo_scan.get_scan("fridge-demo-001")

        self.assertEqual(scan["unknowns"][0]["description"], "foil-wrapped packet")
        self.assertEqual(scan["unknowns"][0]["reason"], "label not visible")

    def test_recent_instacart_order_increases_confidence(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))

        avocado = inventory_engine.confidence_for_item(inventory, "avocado")

        self.assertEqual(avocado["bucket"], "medium_confidence")
        self.assertIn("ordered 3 days ago", avocado["reason"])

    def test_visible_fridge_item_gets_high_confidence(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))

        eggs = inventory_engine.confidence_for_item(inventory, "eggs")

        self.assertEqual(eggs["bucket"], "high_confidence")
        self.assertIn("seen in fridge snapshot", eggs["reason"])
        self.assertIn("visible egg carton in fridge photo", eggs["reason"])

    def test_photo_haul_item_affects_inventory_with_shelf_life_decay(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))

        cucumbers = inventory_engine.confidence_for_item(inventory, "mini cucumbers")

        self.assertEqual(cucumbers["bucket"], "medium_confidence")
        self.assertIn("seen in haul photo, fresh item, bought 3 days ago", cucumbers["reason"])

    def test_photo_receipt_item_affects_inventory_with_decay(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))

        paper_towels = inventory_engine.confidence_for_item(inventory, "paper towels")

        self.assertEqual(paper_towels["bucket"], "high_confidence")
        self.assertIn("parsed mock Costco receipt line, shelf-stable, bought 7 days ago", paper_towels["reason"])

    def test_trace_includes_photo_scan_evidence(self):
        session = create_session(datetime(2026, 5, 9, 10, 0), trace=True)

        response = session.send("It is 10am and I want to plan for dinner tonight")

        self.assertTrue(any("[tool] mock_photo_scan.get_latest_scan -> fridge-demo-001" in line for line in response["trace"]))
        self.assertTrue(
            any("[vision] eggs -> high confidence: visible egg carton in fridge photo" in line for line in response["trace"])
        )
        self.assertTrue(
            any("[vision] foil-wrapped packet -> unknown: label not visible, ask parent if needed" in line for line in response["trace"])
        )
        self.assertTrue(
            any("[vision] receipt_photo -> parsed mock receipt with 8 Costco items" in line for line in response["trace"])
        )

    def test_photo_scan_requires_no_camera_or_real_vision_api(self):
        empty = mock_photo_scan.scan_photo("data/sample_photos/missing.jpg", "garage_photo")

        self.assertEqual(empty["scan_id"], "empty-garage_photo")
        self.assertEqual(empty["items"], [])
        self.assertEqual(empty["unknowns"][0]["reason"], "no matching mock fixture")

    def test_old_kid_snack_item_becomes_likely_low(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))

        berries = inventory_engine.confidence_for_item(inventory, "berries")

        self.assertEqual(berries["bucket"], "likely_low")
        self.assertIn("kid snack item", berries["reason"])

    def test_lunch_branch_uses_mock_instacart_cart_for_missing_fresh_items(self):
        session = create_session(parse_now(None, scenario="lunch"), trace=True, scenario="lunch")

        response = session.send("What should I make for dinner tonight?", scenario="lunch")

        self.assertIn("Reviewable grocery cart: avocado, berries.", response["message"])
        self.assertIn("Photo evidence confirms eggs, rice, tortillas, and Costco freezer staples", response["message"])
        self.assertNotIn("foil-wrapped packet", response["message"])
        self.assertEqual(response["grocery_items"], ["avocado", "berries"])
        self.assertTrue(
            any("[tool] mock_instacart.build_reviewable_cart -> avocado, berries" in line for line in response["trace"])
        )
        self.assertTrue(
            any(
                "[decision] use Instacart only for fresh gaps; rely on Costco for pantry/freezer staples" in line
                for line in response["trace"]
            )
        )

    def test_dinner_branch_avoids_relying_on_low_confidence_items(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("What should I make for dinner tonight?")

        self.assertIn("Make Egg Fried Rice tonight.", response)
        self.assertNotIn("Peanut Butter Noodles", response)
        self.assertEqual(
            tools.confidence_for_item(agent.inventory, "peanut butter")["bucket"],
            "low_confidence",
        )

    def test_next_costco_run_date_calculation(self):
        cadence = costco_bulk.get_cadence()

        self.assertEqual(cadence["frequency_days"], 14)
        self.assertEqual(cadence["usual_day"], "Saturday")
        self.assertEqual(cadence["usual_time"], "morning")
        self.assertEqual(costco_bulk.expected_next_run_date(cadence).isoformat(), "2026-05-16")

    def test_costco_fresh_item_decays_before_next_run(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 14, 12, 30))

        blueberries = inventory_engine.confidence_for_item(inventory, "blueberries")

        self.assertEqual(blueberries["bucket"], "low_confidence")
        self.assertIn("fresh Costco item, bought 12 days ago", blueberries["reason"])

    def test_costco_shelf_stable_item_remains_high_across_cycle(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 15, 12, 30))

        rice = inventory_engine.confidence_for_item(inventory, "rice")

        self.assertEqual(rice["bucket"], "high_confidence")
        self.assertIn("Costco bulk item, shelf-stable, bought 13 days ago", rice["reason"])

    def test_costco_freezer_item_remains_high_confidence(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 15, 12, 30))

        frozen_peas = inventory_engine.confidence_for_item(inventory, "frozen peas")

        self.assertEqual(frozen_peas["bucket"], "high_confidence")
        self.assertIn("Costco bulk item, freezer, bought 13 days ago", frozen_peas["reason"])

    def test_lunch_cart_does_not_add_costco_covered_staples_to_instacart(self):
        session = create_session(parse_now(None, scenario="lunch"), trace=True, scenario="lunch")

        response = session.send("What should I make for dinner tonight?", scenario="lunch")

        self.assertEqual(response["grocery_items"], ["avocado", "berries"])
        self.assertNotIn("rice", response["grocery_items"])
        self.assertNotIn("frozen corn", response["grocery_items"])

    def test_may_9_10am_uses_early_delivery_and_costco_cycle(self):
        session = create_session(datetime(2026, 5, 9, 10, 0), trace=True)

        response = session.send("It is 10am and I want to plan for dinner tonight")

        self.assertEqual(response["metadata"]["delivery_strategy"], "delivery_ok")
        self.assertEqual(response["grocery_items"], ["avocado", "berries"])
        self.assertIn("Reviewable grocery cart: avocado, berries.", response["message"])
        self.assertIn("Mock subtotal: $35.22", response["message"])
        self.assertTrue(
            any("[tool] costco_bulk.get_recent_receipts -> last run 7 days ago" in line for line in response["trace"])
        )
        self.assertTrue(
            any(
                "[decision] use Instacart only for fresh gaps; rely on Costco for pantry/freezer staples" in line
                for line in response["trace"]
            )
        )

    def test_may_9_10am_costco_confidence_buckets(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 10, 0))

        self.assertEqual(inventory["costco_cadence"]["days_until_next_run"], 7)
        self.assertEqual(inventory_engine.confidence_for_item(inventory, "rice")["bucket"], "high_confidence")
        self.assertIn(
            "Costco bulk item, shelf-stable, bought 7 days ago",
            inventory_engine.confidence_for_item(inventory, "rice")["reason"],
        )
        self.assertEqual(inventory_engine.confidence_for_item(inventory, "frozen peas")["bucket"], "high_confidence")
        self.assertEqual(inventory_engine.confidence_for_item(inventory, "blueberries")["bucket"], "low_confidence")


class MockGroceryCatalogTest(unittest.TestCase):
    def smart_cart(self, traces=None):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))
        meals = tools.get_meal_options()
        return mock_instacart.build_reviewable_cart(
            ["avocado", "berries"],
            (lambda name, payload: traces.append((name, payload))) if traces is not None else None,
            inventory=inventory,
            meal_options=meals,
            current_meal=meals[0],
        )

    def high_value_cart(self, traces=None):
        names = []
        subtotal = 0
        for item in mock_instacart.get_catalog_items():
            if not item["in_stock"] or item["category"] == "household":
                continue
            names.append(item["name"])
            subtotal += item["price"]
            if subtotal >= 105:
                break

        self.assertGreaterEqual(subtotal, 100)
        return mock_instacart.build_reviewable_cart(
            names,
            (lambda name, payload: traces.append((name, payload))) if traces is not None else None,
        )

    def test_catalog_is_deep_enough_for_demo(self):
        catalog = mock_instacart.get_catalog_items()

        self.assertGreaterEqual(len(catalog), 70)
        self.assertTrue(all("price" in item for item in catalog))
        self.assertTrue(any(item["name"] == "avocado" for item in catalog))
        self.assertTrue(any(item["name"] == "eggs" for item in catalog))

    def test_dinner_required_items_are_included_first(self):
        cart = self.smart_cart()

        self.assertEqual([line["name"] for line in cart["required_items"]], ["avocado", "berries"])
        self.assertEqual([line["name"] for line in cart["line_items"][:2]], ["avocado", "berries"])
        self.assertAlmostEqual(cart["required_subtotal"], 8.28)

    def test_below_minimum_cart_gets_smart_addons(self):
        cart = self.smart_cart()

        self.assertGreater(len(cart["smart_addons"]), 0)
        self.assertGreaterEqual(cart["subtotal"], cart["minimum_order_amount"])
        self.assertEqual(cart["status"], "meets minimum")
        self.assertAlmostEqual(cart["subtotal"], 35.22)
        self.assertFalse(cart["requires_reconfirmation"])
        self.assertEqual(cart["unavailable_items"], [])

    def test_high_confidence_home_inventory_is_not_added(self):
        cart = self.smart_cart()

        self.assertNotIn("eggs", cart["items"])
        self.assertNotIn("rice", cart["items"])

    def test_costco_covered_staples_are_skipped(self):
        traces = []

        self.smart_cart(traces)

        self.assertIn(
            ("cart_skipped_item", {"item": "rice", "reason": "Costco bulk item is high confidence"}),
            traces,
        )

    def test_out_of_stock_catalog_item_uses_available_substitute(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))

        cart = mock_instacart.build_reviewable_cart(["guacamole cup"], inventory=inventory)

        self.assertEqual(cart["required_items"][0]["name"], "avocado")
        self.assertEqual(cart["substitutions"], [{"requested": "guacamole cup", "substitute": "avocado"}])

    def test_unknown_item_is_not_added_to_cart(self):
        cart = mock_instacart.build_reviewable_cart(["dragon fruit"])

        self.assertEqual(cart["items"], [])
        self.assertEqual(cart["unavailable_items"], ["dragon fruit"])

    def test_final_cart_only_contains_catalog_item_ids(self):
        catalog_ids = {item["id"] for item in mock_instacart.get_catalog_items()}
        cart = self.smart_cart()

        self.assertTrue(all(line["id"] in catalog_ids for line in cart["line_items"]))

    def test_lunch_response_separates_required_items_from_smart_addons(self):
        session = create_session(parse_now(None, scenario="lunch"), trace=True, scenario="lunch")

        response = session.send("What should I make for dinner tonight?", scenario="lunch")

        self.assertIn("Required for tonight:", response["message"])
        self.assertIn("- avocado - $1.79", response["message"])
        self.assertIn("- berries - $6.49", response["message"])
        self.assertIn("Smart add-ons to make delivery worthwhile:", response["message"])
        self.assertIn("- mini cucumbers - $4.49", response["message"])
        self.assertIn("Mock subtotal: $35.22", response["message"])
        self.assertIn("Mock Instacart minimum: $35.00", response["message"])
        self.assertIn("Status: meets minimum", response["message"])
        self.assertNotIn("High-value cart alert", response["message"])

    def test_cart_at_100_requires_parent_reconfirmation(self):
        traces = []

        cart = self.high_value_cart(traces)

        self.assertGreaterEqual(cart["subtotal"], 100)
        self.assertEqual(cart["reconfirmation_threshold"], 100.00)
        self.assertTrue(cart["requires_reconfirmation"])
        self.assertIn("parent reconfirmation is required", cart["high_value_alert"])
        self.assertTrue(any(name == "cart_reconfirmation_required" for name, _payload in traces))

    def test_high_value_cart_warning_is_user_visible(self):
        cart = self.high_value_cart()

        message = BusyParentAgent._grocery_line(
            {
                "reviewable_items": cart["items"],
                "reviewable_cart": cart,
            }
        )

        self.assertIn("High-value cart alert", message)
        self.assertIn("$100.00 review cap", message)
        self.assertIn("Reconfirmation required", message)

    def test_receipt_household_items_do_not_enter_food_cart(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))

        cart = mock_instacart.build_reviewable_cart(
            ["avocado", "berries"],
            inventory=inventory,
            meal_options=tools.get_meal_options(),
        )

        self.assertEqual(inventory_engine.confidence_for_item(inventory, "paper towels")["bucket"], "high_confidence")
        self.assertNotIn("paper towels", cart["items"])
        self.assertTrue(all(line["category"] != "household" for line in cart["line_items"]))


if __name__ == "__main__":
    unittest.main()
