import json
import logging

from diplomacy_base import Game
from llm_agents.llm_players import LLMPlayerFactory
from llm_agents.negotiation_system import NegotiationSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



class GameManager:
    def __init__(self, player_configs):
        self.game = Game()
        self.players = self._initialize_players(player_configs)
        logging.info("Initializing GameManager")

    def _initialize_players(self, player_configs):
        players = {}
        for country, config in player_configs.items():
            llm_type = config['llm_type']
            params = config.get('params', {})
            players[country] = LLMPlayerFactory.create_player(llm_type, country, **params)
        return players

    def run_game(self, max_turns=50):
        logging.info(f"Starting game with max_turns={max_turns}")
        for turn in range(1, max_turns + 1):
            logging.info(f"Starting turn {turn}")
            print(f"Turn {turn}")
            self._process_negotiations()
            orders = self._collect_orders()
            self.game.process_orders(orders)
            self.game.resolve_turn()
            
            if self.game.check_victory():
                print(f"Game ended on turn {turn}")
                break
        
        self._print_game_result()

    def _process_negotiations(self):
        logging.info("Processing negotiations")
        game_state = json.loads(self.game.generate_game_state_json())  # Parse JSON string to dict
        for proposing_country, proposing_player in self.players.items():
            for target_country, target_player in self.players.items():
                if proposing_country != target_country:
                    result = NegotiationSystem.execute_negotiation(proposing_player, target_player, game_state)
                    if result['status'] == 'accepted':
                        print(f"Agreement reached between {proposing_country} and {target_country}")

    def _collect_orders(self):
        logging.info("Collecting orders")

        game_state = json.loads(self.game.generate_game_state_json())  # Parse JSON string to dict
        orders = {}
        for country, player in self.players.items():
            orders[country] = player.generate_orders(game_state)
        return orders

    def _print_game_result(self):
        winner = self.game.check_victory()
        if winner:
            print(f"The game is won by {winner}")
        else:
            print("The game ended without a clear winner")
        
        print("\nFinal game state:")
        print(self.game.generate_game_state_json())


player_configs = {country: {'llm_type': 'test-orders'} for country in ['England', 'France', 'Germany', 'Italy', 'Austria', 'Russia', 'Turkey']}

# player_configs = {
#     'England': {'llm_type': 'gpt-4o-mini', 'params': {'api_key': 'your_api_key'}},
#     'France': {'llm_type': 'claude-haiku', 'params': {'api_key': 'your_api_key'}},
#     'Germany': {'llm_type': 'llama-3.1-8b', 'params': {'model_path': '/path/to/model.bin'}},
#     'Italy': {'llm_type': 'test-orders'},
#     'Austria': {'llm_type': 'test-orders'},
#     'Russia': {'llm_type': 'test-orders'},
#     'Turkey': {'llm_type': 'test-orders'},
# }

import traceback

if __name__ == "__main__":
    try:
        logging.info("Starting game_manager.py")
        player_configs = {country: {'llm_type': 'test-orders'} for country in ['England', 'France', 'Germany', 'Italy', 'Austria', 'Russia', 'Turkey']}
        logging.info("Initializing GameManager")
        game_manager = GameManager(player_configs)
        logging.info("GameManager initialized")
        logging.info("Running game")
        game_manager.run_game(max_turns=1)
        logging.info("Game finished")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        logging.error(traceback.format_exc())