import openai

class LLMWrapper:
    def __init__(self, model="gpt4o-mini"):
        self.model = model

    def chain_of_thought(self, prompt, max_tokens=1000):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Think step-by-step to solve the problem."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message['content']

    def function_call(self, prompt, functions, function_call="auto"):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            functions=functions,
            function_call=function_call
        )
        return response.choices[0].message