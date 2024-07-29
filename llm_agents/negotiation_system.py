from .llm_gameplay_logic import LLMGameplayLogic
from log_config import logger

class NegotiationSystem:
    @staticmethod
    def generate_proposal(game_state, proposing_country, target_country):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        prompt = f"""
        As {proposing_country}, generate a diplomatic proposal for {target_country}.
        Current game state: {analyzed_state}
        
        Consider the following in your proposal:
        1. Mutual threats from other players
        2. Potential for territorial exchanges or support
        3. Long-term strategic alliances
        4. Economic cooperation (sharing supply centers)

        Format your proposal as a clear, numbered list of suggested actions and their benefits.
        """
        # This should be replaced with an actual LLM call in a real implementation
        return "1. Mutual non-aggression pact\n2. Share intelligence on other players"


    @staticmethod
    def evaluate_proposal(game_state, proposing_country, target_country, proposal):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        prompt = f"""
        As {target_country}, evaluate this proposal from {proposing_country}:
        {proposal}

        Current game state: {analyzed_state}

        Consider the following in your evaluation:
        1. Short-term and long-term benefits and risks
        2. Trustworthiness of {proposing_country} based on past actions
        3. How this proposal affects your relationships with other countries
        4. The proposal's impact on your overall strategy

        Provide your reasoning and decision: Accept, Reject, or Counter-propose.
        If Counter-proposing, include your counter-proposal.
        """
        # TODO: Use the LLM to evaluate the proposal based on this prompt
        # For now, return a dummy evaluation
        return {
            'decision': 'Accept',
            'reasoning': 'The proposal seems beneficial and low-risk.',
            'counter_proposal': None
        }




    @staticmethod
    def format_negotiation_prompt(game_state, proposing_country, target_country, proposal, previous_negotiations):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        negotiation_history = "\n".join([f"{neg['turn']} {neg['season']} - Outcome: {neg['outcome']}" for neg in previous_negotiations[-5:]])
        return f"""
        You are {proposing_country}. Current state: {analyzed_state}
        
        Previous negotiations with {target_country}:
        {negotiation_history}

        Your proposal to {target_country}: {proposal}

        Respond to {target_country}. Be strategic and consider past interactions.
        Provide a clear response (accept, reject, or counter-propose) and a brief explanation.
        """

    @staticmethod
    def execute_negotiation(proposing_player, target_player, game_state, is_gpt_player=False, is_target_gpt_player=False):
        proposal = NegotiationSystem.generate_proposal(game_state, proposing_player.country, target_player.country)
        
        # Proposing player sends a message
        if is_gpt_player:
            proposing_message = proposing_player.negotiate(target_player.country, proposal, game_state)
        else:
            proposing_message = f"{proposing_player.country} proposes: {proposal}"

        # Target player receives and responds
        if is_target_gpt_player:
            target_player.receive_message(proposing_player.country, proposing_message, game_state)
            target_message = target_player.negotiate(proposing_player.country, proposal, game_state)
        else:
            target_message = f"{target_player.country} responds: {target_player.negotiate(proposing_player.country, proposal, game_state)}"

        # Proposing player receives the response
        if is_gpt_player:
            proposing_player.receive_message(target_player.country, target_message, game_state)

        # Determine the outcome
        if "accept" in proposing_message.lower() and "accept" in target_message.lower():
            return {'status': 'accepted', 'agreement': proposal, 'messages': [proposing_message, target_message]}
        elif "counter" in proposing_message.lower() or "counter" in target_message.lower():
            return {'status': 'failed', 'reason': 'Counter-proposal offered', 'messages': [proposing_message, target_message]}
        else:
            return {'status': 'rejected', 'reason': 'One or both players rejected the proposal', 'messages': [proposing_message, target_message]}