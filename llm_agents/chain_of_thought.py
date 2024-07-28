class ChainOfThought:
    @staticmethod
    def format_cot_prompt(task, context):
        return f"""
        Task: {task}
        Context: {context}
        
        Let's approach this step-by-step:
        1) Analyze the current situation and identify key factors.
        2) Consider potential short-term and long-term consequences of different actions.
        3) Evaluate the risks and potential rewards of each option.
        4) Consider how your actions might affect other players and potential alliances.
        5) Make a decision based on your analysis and strategic goals.
        
        Provide your step-by-step reasoning, clearly labeling each step:
        """

    @staticmethod
    def parse_cot_response(response):
        # Split the response into steps
        steps = response.split('\n')
        
        # Extract the final decision (assuming it's in the last step)
        final_decision = steps[-1] if steps else ""
        
        # You might want to add more sophisticated parsing here,
        # e.g., extracting key points from each step
        
        return {
            'steps': steps[:-1],  # All steps except the last one
            'decision': final_decision
        }