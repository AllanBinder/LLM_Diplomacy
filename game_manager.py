import json
import os
import traceback
from diplomacy_base import Game
from llm_agents.llm_players import GPT4MiniPlayer, TestOrderPlayer, LLMPlayerFactory
from llm_agents.negotiation_system import NegotiationSystem
from llm_agents.llm_players import gpt4_api_key
from log_config import logger

class GameManager:
    def __init__(self, player_configs):
        self.game = Game()
        self.players = self._initialize_players(player_configs)
        logger.info("Initializing GameManager")

    def _initialize_players(self, player_configs):
        players = {}
        for country in ['England', 'France', 'Germany', 'Italy', 'Austria', 'Russia', 'Turkey']:
            config = player_configs.get(country, {'llm_type': 'test-orders'})
            llm_type = config['llm_type']
            params = config.get('params', {})
            players[country] = LLMPlayerFactory.create_player(llm_type, country, **params)
        return players

    def run_game(self, max_turns=50):
        logger.info(f"Starting game with max_turns={max_turns}")
        for turn in range(1, max_turns + 1):
            logger.info(f"Starting turn {turn}")
            print(f"Turn {turn}")
            self._process_negotiations()
            orders = self._collect_orders()
            self.game.submit_orders(orders)
            self.game.resolve_turn()
            
            if self.game.check_victory():
                logger.info(f"Game ended on turn {turn}")
                print(f"Game ended on turn {turn}")
                break
        
        self._print_game_result()

    def _process_negotiations(self):
        logger.info("Processing negotiations")
        game_state = self.game.generate_game_state_json()
        for proposing_country, proposing_player in self.players.items():
            for target_country, target_player in self.players.items():
                if proposing_country != target_country:
                    proposal = NegotiationSystem.generate_proposal(game_state, proposing_country, target_country)
                    result = proposing_player.negotiate(target_country, proposal, game_state)
                    logger.info(f"Negotiation between {proposing_country} and {target_country}: {result['outcome']}")
                    if "agreement" in result['outcome'].lower():
                        print(f"Agreement reached between {proposing_country} and {target_country}")


    def _collect_orders(self):
        logger.info("Collecting orders")
        game_state = self.game.generate_game_state_json()
        orders = {}
        for country, player in self.players.items():
            logger.info(f"Generating orders for {country}")
            country_orders = player.generate_orders(game_state)
            logger.info(f"Orders received for {country}: {country_orders}")
            orders[country] = country_orders
        return orders

    def _print_game_result(self):
        winner = self.game.check_victory()
        if winner:
            logger.info(f"The game is won by {winner}")
            print(f"The game is won by {winner}")
        else:
            logger.info("The game ended without a clear winner")
            print("The game ended without a clear winner")
        
        logger.info("Final game state:")
        logger.info(self.game.generate_game_state_json())
        print("\nFinal game state:")
        print(self.game.generate_game_state_json())

player_configs = {
    'England': {'llm_type': 'gpt-4o-mini', 'params': {'api_key': gpt4_api_key}},
    'France': {'llm_type': 'test-orders'},
    'Germany': {'llm_type': 'test-orders'},
    'Italy': {'llm_type': 'test-orders'},
    'Austria': {'llm_type': 'test-orders'},
    'Russia': {'llm_type': 'gpt-4o-mini', 'params': {'api_key': gpt4_api_key}},
    'Turkey': {'llm_type': 'test-orders'}
}

if __name__ == "__main__":
    try:
        logger.info("Starting game_manager.py")
        logger.info("Initializing GameManager")
        game_manager = GameManager(player_configs)
        logger.info("GameManager initialized")
        logger.info("Running game")
        game_manager.run_game(max_turns=3)
        logger.info("Game finished")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error(traceback.format_exc())