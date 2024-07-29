import logging
import os

class LLMLogger:
    def __init__(self):
        os.makedirs('logs', exist_ok=True)
        self.logger = logging.getLogger('llm_interactions')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('logs/llm_interactions.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_interaction(self, country, model, prompt, response):
        self.logger.info(f"Country: {country}")
        self.logger.info(f"Model: {model}")
        self.logger.info(f"Prompt:\n{prompt}")
        self.logger.info(f"Response:\n{response}")
        self.logger.info("-" * 50)

llm_logger = LLMLogger()