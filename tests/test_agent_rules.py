from datetime import datetime
import json
import subprocess
import sys
import unittest

from busyparent_agent.agent import BusyParentAgent
from busyparent_agent.service import create_session, parse_now
from busyparent_agent import tools
from busyparent_agent import inventory as inventory_engine
from busyparent_agent.adapters import mock_instacart


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
        self.assertIn("Reviewable cart/list: avocado, berries.", response)
        self.assertEqual(agent.current_recommendation["missing"], ["avocado", "berries"])

    def test_close_to_dinner_branch_remains_pantry_first_nothing_required(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("What should I make for dinner tonight?")

        self.assertIn("It is close to dinner", response)
        self.assertIn("Reviewable grocery list: nothing required.", response)
        self.assertEqual(agent.delivery_window["strategy"], "pantry_first")
        self.assertEqual(agent.current_recommendation["name"], "Egg Fried Rice")

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

        self.assertIn("BusyParent Kitchen Agent / HomePlate AI", output)
        self.assertIn("[decision] pantry-first because it is close to dinner", output)
        self.assertIn("Reviewable grocery list: nothing required.", output)
        self.assertNotIn("Not feeling that", output)

    def test_scenario_lunch_runs_and_includes_fresh_grocery_items(self):
        output = self.run_scenario("lunch")

        self.assertIn("[decision] grocery delivery can help because planning starts earlier", output)
        self.assertIn("Reviewable cart/list: avocado, berries.", output)
        self.assertNotIn("Not feeling that", output)

    def test_scenario_guest_runs_and_includes_constraints(self):
        output = self.run_scenario("guest")

        self.assertIn("Context: Selected meal is Egg Fried Rice.", output)
        self.assertIn("[tool] apply_guest_constraints", output)
        self.assertIn("Avoid nut ingredients", output)
        self.assertIn("Keep spice off", output)
        self.assertIn("verify packaged labels", output)


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
        self.assertIn("Reviewable cart/list: avocado, berries.", response["message"])
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

    def test_old_kid_snack_item_becomes_likely_low(self):
        inventory = inventory_engine.build_confidence_inventory(datetime(2026, 5, 9, 12, 30))

        berries = inventory_engine.confidence_for_item(inventory, "berries")

        self.assertEqual(berries["bucket"], "likely_low")
        self.assertIn("kid snack item", berries["reason"])

    def test_lunch_branch_uses_mock_instacart_cart_for_missing_fresh_items(self):
        session = create_session(parse_now(None, scenario="lunch"), trace=True, scenario="lunch")

        response = session.send("What should I make for dinner tonight?", scenario="lunch")

        self.assertIn("Reviewable cart/list: avocado, berries.", response["message"])
        self.assertEqual(response["grocery_items"], ["avocado", "berries"])
        self.assertTrue(
            any("[tool] mock_instacart.build_reviewable_cart -> avocado, berries" in line for line in response["trace"])
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


class MockGroceryCatalogTest(unittest.TestCase):
    def test_catalog_is_deep_enough_for_demo(self):
        catalog = mock_instacart.get_catalog_items()

        self.assertGreaterEqual(len(catalog), 70)
        self.assertTrue(all("price" in item for item in catalog))
        self.assertTrue(any(item["name"] == "avocado" for item in catalog))
        self.assertTrue(any(item["name"] == "eggs" for item in catalog))

    def test_reviewable_cart_uses_catalog_prices(self):
        cart = mock_instacart.build_reviewable_cart(["avocado", "berries"])

        self.assertEqual(cart["items"], ["avocado", "berries"])
        self.assertEqual(len(cart["line_items"]), 2)
        self.assertAlmostEqual(cart["subtotal"], 8.28)
        self.assertEqual(cart["unavailable_items"], [])

    def test_out_of_stock_catalog_item_uses_available_substitute(self):
        cart = mock_instacart.build_reviewable_cart(["guacamole cup"])

        self.assertEqual(cart["items"], ["avocado"])
        self.assertEqual(cart["substitutions"], [{"requested": "guacamole cup", "substitute": "avocado"}])

    def test_unknown_item_is_not_added_to_cart(self):
        cart = mock_instacart.build_reviewable_cart(["dragon fruit"])

        self.assertEqual(cart["items"], [])
        self.assertEqual(cart["unavailable_items"], ["dragon fruit"])

    def test_lunch_response_includes_mock_catalog_price(self):
        session = create_session(parse_now(None, scenario="lunch"), trace=True, scenario="lunch")

        response = session.send("What should I make for dinner tonight?", scenario="lunch")

        self.assertIn("Mock estimate: $8.28", response["message"])


if __name__ == "__main__":
    unittest.main()
