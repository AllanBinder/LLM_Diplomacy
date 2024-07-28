import sys
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

logging.info("Starting minimal_llm_players.py")

logging.info("Importing ABC and abstractmethod")
from abc import ABC, abstractmethod
logging.info("ABC and abstractmethod imported successfully")

logging.info("Importing openai")
import openai
logging.info("openai imported successfully")


logging.info("Importing anthropic")
import anthropic
logging.info("anthropic imported successfully")



logging.info("Importing LLMGameplayLogic")
from .llm_gameplay_logic import LLMGameplayLogic
logging.info("LLMGameplayLogic imported successfully")

class LLMPlayerFactory:
    @staticmethod
    def create_player(llm_type, country, **kwargs):
        logging.info(f"Creating player of type {llm_type} for {country}")
        return DummyPlayer(country)

class DummyPlayer:
    def __init__(self, country):
        self.country = country

logging.info("All classes defined")

if __name__ == "__main__":
    logging.info("Testing LLMPlayerFactory")
    player = LLMPlayerFactory.create_player("test-orders", "England")
    logging.info(f"Player created for {player.country}")