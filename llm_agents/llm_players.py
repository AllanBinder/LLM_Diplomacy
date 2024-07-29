from abc import ABC, abstractmethod
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

claude_api_key = ""
gpt4_api_key = "sk-proj-YbGRduD116A7i4E3tD9kT3BlbkFJnuJbVNVaL1ZDP1ESq187"

#GPTclient = OpenAI(api_key="sk-proj-YbGRduD116A7i4E3tD9kT3BlbkFJnuJbVNVaL1ZDP1ESq187")

claude_model = ""
gpt4_model = ""

llama31_model_path = ""

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
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        possible_moves = LLMGameplayLogic.generate_possible_moves(game_state, self.country)
        prompt = LLMGameplayLogic.format_prompt(analyzed_state, self.country, possible_moves)
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a strategic planner for the game of Diplomacy."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response and convert it into valid orders
        # Implement the parsing logic here
        
        return parsed_orders

    @abstractmethod
    def negotiate(self, other_player, proposal):
        pass

    @abstractmethod
    def plan_strategy(self, game_state):
        pass

class GPT4MiniPlayer(LLMPlayer):
    def __init__(self, country, api_key):
        super().__init__(country)
        self.api_key = gpt4_api_key
        self.model = 'gpt-4o-mini'
        self.client = OpenAI.Client(api_key=self.api_key)
        self.negotiation_history = {}
        # Initialize GPT-4o-mini API client here

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
            
            self.negotiation_history.setdefault(other_player, []).append({
                'turn': game_state['Y'],
                'season': game_state['S'],
                'from': self.country,
                'to': other_player,
                'message': negotiation_response
            })
            
            llm_logger.log_interaction(self.country, self.model, prompt, negotiation_response)

            return negotiation_response
    
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