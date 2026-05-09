from datetime import datetime
import unittest

from busyparent_agent.agent import BusyParentAgent
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

    def test_rejection_returns_three_alternatives(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))
        agent.reply("What should I make for dinner tonight?")

        response = agent.reply("Not feeling that. Anything else?")

        self.assertIn("Here are three better directions", response)
        self.assertEqual(len(agent.alternatives), 3)
        self.assertNotIn("Black Bean Quesadillas", [meal["name"] for meal in agent.alternatives])

    def test_guest_constraints_revise_selected_meal(self):
        agent = BusyParentAgent(now=datetime(2026, 5, 8, 17, 30))
        agent.reply("What should I make for dinner tonight?")
        agent.reply("Not feeling that. Anything else?")
        agent.reply("Let's do egg fried rice.")

        response = agent.reply("My daughter has a friend coming over. No nuts, no spicy food.")

        self.assertIn("Avoid nut ingredients", response)
        self.assertIn("Keep spice off", response)
        self.assertIn("verify packaged labels", response)
        self.assertIn("cannot guarantee allergy safety", response)
        self.assertTrue(agent.selected_meal["guest_constraints"]["no_nuts"])
        self.assertTrue(agent.selected_meal["guest_constraints"]["no_spicy"])


if __name__ == "__main__":
    unittest.main()
