from abc import ABC, abstractmethod
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai as OpenAI
import anthropic
import logging
from log_config import logger
import random
#from llamacpp import Llama
#from mistralai.client import MistralClient
from .llm_gameplay_logic import LLMGameplayLogic
from .negotiation_system import NegotiationSystem
from .chain_of_thought import ChainOfThought
from game_utils import get_adjacent_territories
from llm_logger import llm_logger

from .chain_of_thought import ChainOfThought




claude_api_key = ""


claude_model = ""
gpt4_model = 'gpt-4o-mini'

llama31_model_path = ""

class LLMPlayer(ABC):
    def __init__(self, country, llm_type, **kwargs):
        self.country = country
        self.llm_type = llm_type
        self.negotiator = self.create_llm_instance(llm_type, **kwargs)
        self.strategist = self.create_llm_instance(llm_type, **kwargs)
        self.negotiation_history = {}
        self.strategy_memory = {}

    @abstractmethod
    def initialize_agents(self):
        pass

    @abstractmethod
    def generate_orders(self, game_state):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        possible_moves = LLMGameplayLogic.generate_possible_moves(game_state, self.country)
        prompt = LLMGameplayLogic.format_prompt(analyzed_state, self.country, possible_moves)
        
        response = openai.ChatCompletion.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": "You are a strategic planner for the game of Diplomacy."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response and convert it into valid orders
        # Implement the parsing logic here
        
        return parsed_orders

    @abstractmethod
    def create_llm_instance(self, llm_type, **kwargs):
        pass

    def generate_orders(self, game_state):
        negotiation_summary = self.summarize_negotiations()
        strategy = self.formulate_strategy(game_state, negotiation_summary)
        return self.strategist_generate_orders(game_state, strategy)

    def negotiate(self, other_player, proposal, game_state):
        negotiation_result = self.negotiator_conduct_negotiation(other_player, proposal, game_state)
        self.update_negotiation_history(other_player, negotiation_result)
        return negotiation_result

    @abstractmethod
    def negotiator_conduct_negotiation(self, other_player, proposal, game_state):
        pass

    @abstractmethod
    def strategist_generate_orders(self, game_state, strategy):
        pass

    def summarize_negotiations(self):
        # Implement logic to summarize recent negotiations for the strategist
        summary = ""
        for player, history in self.negotiation_history.items():
            summary += f"Negotiations with {player}:\n"
            for entry in history[-5:]:  # Summarize last 5 interactions
                summary += f"- {entry['turn']} {entry['season']}: {entry['outcome']}\n"
        return summary

    def formulate_strategy(self, game_state, negotiation_summary):
        # Implement logic for the strategist to formulate a strategy based on game state and negotiations
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        prompt = f"""
        Current game state: {analyzed_state}
        Recent negotiations: {negotiation_summary}
        Previous strategy: {self.strategy_memory.get('last_strategy', 'None')}

        Formulate a strategy for {self.country} considering the current game state and recent diplomatic interactions. 
        You should not become aligned with everyone, the goal of the game is to control 18 supply centers. 
        The only way to accomplish this is through making alliances with some and going to war with others.
        """
        strategy = self.strategist_llm_call(prompt)
        self.strategy_memory['last_strategy'] = strategy
        return strategy

    def update_negotiation_history(self, other_player, negotiation_result):
        if other_player not in self.negotiation_history:
            self.negotiation_history[other_player] = []
        self.negotiation_history[other_player].append({
            'turn': negotiation_result['turn'],
            'season': negotiation_result['season'],
            'outcome': negotiation_result['outcome']
        })

    @abstractmethod
    def strategist_llm_call(self, prompt):
        pass

    @abstractmethod
    def negotiator_llm_call(self, prompt):
        pass

class GPT4MiniPlayer(LLMPlayer):
    def __init__(self, country, api_key):
        super().__init__(country, 'gpt-4o-mini', api_key=api_key)
        self.client = OpenAI.Client(api_key=api_key)
        self.model = 'gpt-4o-mini'

    def create_llm_instance(self, llm_type, **kwargs):
        return OpenAI.Client(api_key=kwargs['api_key'])

    def initialize_agents(self):
        # This method is called when the player is created
        # We can use it to set up any initial state or load any necessary data
        logging.info(f"Initializing GPT4MiniPlayer for {self.country}")
        # No specific initialization needed for now, but we can add it later if required

    def plan_strategy(self, game_state):
        # This method should return a high-level strategy based on the current game state
        logging.info(f"Planning strategy for {self.country}")
        prompt = f"As {self.country}, analyze the current game state and suggest a high-level strategy:\n{game_state}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic advisor for a game of Diplomacy."},
                    {"role": "user", "content": prompt}
                ]
            )
            strategy = response.choices[0].message.content
            logging.info(f"Strategy for {self.country}: {strategy}")
            return strategy
        except Exception as e:
            logging.error(f"Error in planning strategy for {self.country}: {str(e)}")
            return "Default defensive strategy"
        
    def strategist_generate_orders(self, game_state, strategy):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        possible_moves = LLMGameplayLogic.generate_possible_moves(game_state, self.country)
        prompt = f"""
        Current game state: {analyzed_state}
        Possible moves: {possible_moves}
        Current strategy: {strategy}

        Generate orders for {self.country} based on the current strategy and game state.
        Provide your orders in the format: (Territory, Action, Target)
        """
        response = self.strategist_llm_call(prompt)
        return LLMGameplayLogic.parse_orders(response, self.country, game_state)

    def strategist_llm_call(self, prompt):
        try:
            response = self.strategist.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in strategist LLM call: {str(e)}")
            return ""

    def negotiator_llm_call(self, prompt):
        try:
            response = self.negotiator.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in negotiator LLM call: {str(e)}")
            return ""

    def parse_negotiation_response(self, response, game_state):
        lines = response.split('\n')
        outcome = lines[0] if lines else "No clear outcome"
        return {
            'turn': game_state['Y'],
            'season': game_state['S'],
            'outcome': outcome
        }
        
    def negotiator_conduct_negotiation(self, other_player, proposal, game_state):
        prompt = NegotiationSystem.format_negotiation_prompt(
            game_state, self.country, other_player, proposal, self.negotiation_history.get(other_player, [])
        )
        response = self.negotiator_llm_call(prompt)
        return self.parse_negotiation_response(response, game_state)  # Make sure this line is present

    def generate_orders(self, game_state):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        possible_moves = LLMGameplayLogic.generate_possible_moves(game_state, self.country)
        prompt = LLMGameplayLogic.format_prompt(analyzed_state, self.country, possible_moves)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic advisor for the game of Diplomacy."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw_orders = response.choices[0].message.content
            llm_logger.log_interaction(self.country, self.model, prompt, raw_orders)

            parsed_orders = LLMGameplayLogic.parse_orders(raw_orders, self.country, game_state)  # Add game_state here
            return parsed_orders
        except Exception as e:
            logging.error(f"Error in GPT-4o mini API call: {str(e)}")
            return []

    def negotiate(self, other_player, proposal, game_state):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        
        previous_negotiations = self.negotiation_history.get(other_player, [])
        
        prompt = NegotiationSystem.format_negotiation_prompt(
            analyzed_state, self.country, other_player, proposal, previous_negotiations)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a concise strategic negotiator in Diplomacy. Keep responses under 50 words."},
                {"role": "user", "content": prompt}
            ]
        )
        negotiation_response = response.choices[0].message.content
        
        result = {
            'turn': game_state['Y'],
            'season': game_state['S'],
            'outcome': negotiation_response
        }
        
        self.negotiation_history.setdefault(other_player, []).append({
            'turn': game_state['Y'],
            'season': game_state['S'],
            'from': self.country,
            'to': other_player,
            'message': negotiation_response
        })
        
        llm_logger.log_interaction(self.country, self.model, prompt, negotiation_response)

        return result  # Return the structured result instead of just the response
    
    def receive_message(self, from_player, message, game_state):
        self.negotiation_history.setdefault(from_player, []).append({
            'turn': game_state['Y'],
            'season': game_state['S'],
            'from': from_player,
            'to': self.country,
            'message': message
        })

    def gpt4_mini_call(self, prompt):
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error in GPT-4o mini API call: {e}")
            return ""


class ClaudeHaikuPlayer(LLMPlayer):
    def __init__(self, country, api_key):
        super().__init__(country)
        self.client = anthropic.Client(claude_api_key)
        self.model = "claude-3-haiku-20240307"  # Use the latest Claude Haiku model

    def generate_orders(self, game_state):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        possible_moves = LLMGameplayLogic.generate_possible_moves(game_state, self.country)
        prompt = LLMGameplayLogic.format_prompt(analyzed_state, self.country, possible_moves)
        
        task = "Generate orders for your units in the game of Diplomacy"
        cot_prompt = ChainOfThought.format_cot_prompt(task, prompt)
        
        response = self.claude_haiku_call(cot_prompt)
        
        parsed_response = ChainOfThought.parse_cot_response(response)
        raw_orders = parsed_response['decision']
        parsed_orders = LLMGameplayLogic.parse_orders(raw_orders, self.country)
        
        return parsed_orders

    def negotiate(self, other_player, proposal):
        prompt = NegotiationSystem.format_negotiation_prompt(self.game_state, self.country, other_player, proposal)
        
        task = "Negotiate with another player in the game of Diplomacy"
        cot_prompt = ChainOfThought.format_cot_prompt(task, prompt)
        
        response = self.claude_haiku_call(cot_prompt)
        
        parsed_response = ChainOfThought.parse_cot_response(response)
        # Convert the parsed response into a negotiation action
        # Implement the conversion logic here
        
        return negotiation_action

    def claude_haiku_call(self, prompt):
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error in Claude Haiku API call: {e}")
            return ""
        
class Llama31_8bPlayer(LLMPlayer):
    def __init__(self, country, model_path):
        super().__init__(country)
        self.llm = Llama(model_path=model_path, n_ctx=2048, n_batch=512)

    def generate_orders(self, game_state):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        possible_moves = LLMGameplayLogic.generate_possible_moves(game_state, self.country)
        prompt = LLMGameplayLogic.format_prompt(analyzed_state, self.country, possible_moves)
        
        task = "Generate orders for your units in the game of Diplomacy"
        cot_prompt = ChainOfThought.format_cot_prompt(task, prompt)
        
        response = self.llama_call(cot_prompt)
        
        parsed_response = ChainOfThought.parse_cot_response(response)
        raw_orders = parsed_response['decision']
        parsed_orders = LLMGameplayLogic.parse_orders(raw_orders, self.country)
        
        return parsed_orders

    def negotiate(self, other_player, proposal):
        prompt = NegotiationSystem.format_negotiation_prompt(self.game_state, self.country, other_player, proposal)
        
        task = "Negotiate with another player in the game of Diplomacy"
        cot_prompt = ChainOfThought.format_cot_prompt(task, prompt)
        
        response = self.llama_call(cot_prompt)
        
        parsed_response = ChainOfThought.parse_cot_response(response)
        # Convert the parsed response into a negotiation action
        # Implement the conversion logic here
        
        return negotiation_action

    def llama_call(self, prompt, max_tokens=1000):
        try:
            output = self.llm(prompt, max_tokens=max_tokens)
            return output['choices'][0]['text']
        except Exception as e:
            print(f"Error in Llama 3.1 8B inference: {e}")
            return ""
        
class MistralPlayer(LLMPlayer):
    def __init__(self, country, api_key, model="mistral-medium"):
        super().__init__(country)
        self.client = MistralClient(api_key=api_key)
        self.model = model

    def mistral_call(self, prompt, max_tokens=1000):
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in Mistral API call: {e}")
            return ""

    def generate_orders(self, game_state):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        possible_moves = LLMGameplayLogic.generate_possible_moves(game_state, self.country)
        prompt = LLMGameplayLogic.format_prompt(analyzed_state, self.country, possible_moves)
        
        task = "Generate orders for your units in the game of Diplomacy"
        cot_prompt = ChainOfThought.format_cot_prompt(task, prompt)
        
        response = self.mistral_call(cot_prompt)
        
        parsed_response = ChainOfThought.parse_cot_response(response)
        raw_orders = parsed_response['decision']
        parsed_orders = LLMGameplayLogic.parse_orders(raw_orders, self.country)
        
        return parsed_orders

    def negotiate(self, other_player, proposal):
        prompt = NegotiationSystem.format_negotiation_prompt(self.game_state, self.country, other_player, proposal)
        
        task = "Negotiate with another player in the game of Diplomacy"
        cot_prompt = ChainOfThought.format_cot_prompt(task, prompt)
        
        response = self.mistral_call(cot_prompt)
        
        parsed_response = ChainOfThought.parse_cot_response(response)
        # Convert the parsed response into a negotiation action
        # Implement the conversion logic here
        
        return negotiation_action
        

class TestOrderPlayer(LLMPlayer):
    def __init__(self, country):
        super().__init__(country)

    def initialize_agents(self):
        pass

    def generate_orders(self, game_state):
        from test_orders import get_orders
        from game_utils import get_adjacent_territories
        units = {t: u for t, u in game_state['U'].items() if u.endswith(self.country[:3].upper())}
        controlled_territories = set(t for t, c in game_state['SC'].items() if c == self.country[:3].upper())
        return get_orders(self.country, units, controlled_territories, get_adjacent_territories)

    def negotiate(self, other_player, proposal, game_state):
        response = random.choice(['accept', 'reject', 'counter'])
        message = self._generate_message(other_player, proposal, response)
        
        self.negotiation_history.setdefault(other_player, []).append({
            'turn': game_state['Y'],
            'season': game_state['S'],
            'from': self.country,
            'to': other_player,
            'message': message
        })
        
        return message

    def receive_message(self, from_player, message, game_state):
        self.negotiation_history.setdefault(from_player, []).append({
            'turn': game_state['Y'],
            'season': game_state['S'],
            'from': from_player,
            'to': self.country,
            'message': message
        })

    def _generate_message(self, other_player, proposal, decision):
        messages = {
            'accept': [
                f"{self.country} accepts the proposal from {other_player}.",
                f"We agree to your terms, {other_player}.",
                f"Your proposal is acceptable, {other_player}."
            ],
            'reject': [
                f"{self.country} rejects the proposal from {other_player}.",
                f"We cannot agree to these terms, {other_player}.",
                f"Your proposal is not in our interests, {other_player}."
            ],
            'counter': [
                f"{self.country} proposes a counter-offer to {other_player}.",
                f"We have a different proposal in mind, {other_player}.",
                f"Let's consider an alternative arrangement, {other_player}."
            ]
        }

    def plan_strategy(self, game_state):
        return "Generate random orders"
    
    def negotiate(self, other_player, proposal, game_state):
        import random
        return random.choice(['accept', 'reject', 'counter'])

class LLMPlayerFactory:
    @staticmethod
    def create_player(llm_type, country, **kwargs):
        if llm_type == "gpt-4o-mini":
            return GPT4MiniPlayer(country, kwargs.get("api_key"))
        elif llm_type == "claude-haiku":
            return ClaudeHaikuPlayer(country, kwargs.get("api_key"))
        elif llm_type == "llama-3.1-8b":
            return Llama31_8bPlayer(country, kwargs.get("model_path"))
        elif llm_type == "mistral":
            return MistralPlayer(country, kwargs.get("api_key"), kwargs.get("model", "mistral-medium"))
        elif llm_type == "test-orders":
            return TestOrderPlayer(country)
        else:
            raise ValueError(f"Unknown LLM type: {llm_type}")