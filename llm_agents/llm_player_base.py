from abc import ABC, abstractmethod

class LLMPlayer(ABC):
    def __init__(self, country):
        self.country = country
        self.planner = None
        self.negotiator = None

    @abstractmethod
    def initialize_agents(self):
        pass

    @abstractmethod
    def generate_orders(self, game_state):
        pass

    @abstractmethod
    def negotiate(self, other_player, proposal):
        pass

    @abstractmethod
    def plan_strategy(self, game_state):
        pass