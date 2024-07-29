import logging
import os

def setup_logging():
    # Create 'logs' directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Set up logging to both console and file
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler('logs/game.log'),
                            logging.StreamHandler()
                        ])

    # Create a logger
    logger = logging.getLogger('diplomacy_game')
    return logger

# Create and configure the logger
logger = setup_logging()