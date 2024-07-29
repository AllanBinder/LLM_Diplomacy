
# tests/test_llm_player.py

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import Mock, patch
from llm_agents.llm_players import GPT4MiniPlayer
from llm_agents.negotiation_system import NegotiationSystem
from llm_agents.llm_gameplay_logic import LLMGameplayLogic

class TestGPT4MiniPlayer(unittest.TestCase):
    @patch('llm_agents.llm_players.OpenAI.Client')
    def setUp(self, mock_client):
        self.mock_client = mock_client
        self.player = GPT4MiniPlayer("England", "fake_api_key")
        self.game_state = {
            "Y": 1901,
            "S": "S",
            "U": {"London": "FENG"},
            "SC": {"London": "ENG"},
            "P": {"ENG": 1}
        }

    def test_negotiate(self):
        self.mock_client.return_value.chat.completions.create.return_value.choices[0].message.content = "Accept the proposal"
        result = self.player.negotiate("France", "Non-aggression pact", self.game_state)
        print(f"Negotiate result: {result}")  # For debugging
        self.assertIn("outcome", result)
        self.assertEqual(result["turn"], 1901)
        self.assertEqual(result["season"], "S")
        self.assertEqual(result["outcome"], "Accept the proposal")

    def test_generate_orders(self):
        self.mock_client.return_value.chat.completions.create.return_value.choices[0].message.content = "(London, hold)"
        orders = self.player.generate_orders(self.game_state)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0], ("London", "hold", None))

    def test_summarize_negotiations(self):
        self.player.negotiation_history = {
            "France": [
                {"turn": 1901, "season": "S", "outcome": "Accepted non-aggression pact"},
                {"turn": 1901, "season": "F", "outcome": "Rejected support request"}
            ]
        }
        summary = self.player.summarize_negotiations()
        self.assertIn("France", summary)
        self.assertIn("1901 S: Accepted non-aggression pact", summary)
        self.assertIn("1901 F: Rejected support request", summary)


if __name__ == '__main__':
    unittest.main()