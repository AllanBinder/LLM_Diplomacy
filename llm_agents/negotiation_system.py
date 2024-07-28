from .llm_gameplay_logic import LLMGameplayLogic

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
        # TODO: Use the LLM to generate the proposal based on this prompt
        # For now, return a dummy proposal
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
    def format_negotiation_prompt(game_state, proposing_country, target_country, proposal):
        analyzed_state = LLMGameplayLogic.analyze_game_state(game_state)
        return f"""
        You are the diplomat for {proposing_country}.
        Current game state: {analyzed_state}
        
        You are negotiating with {target_country}. Your proposal:
        {proposal}

        Craft a diplomatic message to {target_country} presenting your proposal. 
        Be persuasive and highlight mutual benefits. Consider the current game state and potential threats from other players.
        """
    
    @staticmethod
    def execute_negotiation(proposing_player, target_player, game_state):
        try:
            proposal = NegotiationSystem.generate_proposal(game_state, proposing_player.country, target_player.country)
            evaluation = NegotiationSystem.evaluate_proposal(game_state, proposing_player.country, target_player.country, proposal)
            
            if evaluation['decision'] == 'Accept':
                return {'status': 'accepted', 'agreement': proposal}
            elif evaluation['decision'] == 'Counter-propose':
                counter_proposal = evaluation['counter_proposal']
                counter_evaluation = NegotiationSystem.evaluate_proposal(game_state, target_player.country, proposing_player.country, counter_proposal)
                if counter_evaluation['decision'] == 'Accept':
                    return {'status': 'accepted', 'agreement': counter_proposal}
                else:
                    return {'status': 'failed', 'reason': 'Counter-proposal rejected'}
            else:
                return {'status': 'rejected', 'reason': evaluation['reasoning']}
        except Exception as e:
            print(f"Error during negotiation: {str(e)}")
            return {'status': 'failed', 'reason': 'Negotiation error'}