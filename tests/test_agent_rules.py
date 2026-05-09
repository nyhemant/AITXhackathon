from datetime import datetime
import subprocess
import sys
import unittest

from busyparent_agent.agent import BusyParentAgent
from busyparent_agent.service import create_session, parse_now
from busyparent_agent import tools


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
        self.assertIn("Black Bean Quesadillas", response)
        self.assertIn("I am leading with one option", response)
        self.assertNotIn("1.", response)
        self.assertIsNotNone(agent.current_recommendation)

    def test_lunch_branch_uses_small_reviewable_grocery_list(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 9, 12, 30))

        response = agent.reply("What should I make for dinner tonight?")

        self.assertIn("Because we are planning early", response)
        self.assertIn("Reviewable grocery list: avocado, berries.", response)
        self.assertEqual(agent.current_recommendation["missing"], ["avocado", "berries"])

    def test_close_to_dinner_branch_remains_pantry_first_nothing_required(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))

        response = agent.reply("What should I make for dinner tonight?")

        self.assertIn("It is close to dinner", response)
        self.assertIn("Reviewable grocery list: nothing required.", response)
        self.assertEqual(agent.delivery_window["strategy"], "pantry_first")

    def test_rejection_returns_three_alternatives(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))
        agent.reply("What should I make for dinner tonight?")

        response = agent.reply("Not feeling that. Anything else?")

        self.assertIn("Here are three better directions", response)
        self.assertIn("I’d pick Egg Fried Rice if you want the least effort tonight.", response)
        self.assertEqual(len(agent.alternatives), 3)
        self.assertNotIn("Black Bean Quesadillas", [meal["name"] for meal in agent.alternatives])

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
        self.assertIn("Reviewable grocery list: avocado, berries.", output)
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
        self.assertIn("Reviewable grocery list: avocado, berries.", response["message"])
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


if __name__ == "__main__":
    unittest.main()
