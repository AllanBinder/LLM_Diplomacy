# run_clients.py

import asyncio
import random
import os
import logging

from diplomacy_client import DiplomacyClient

# Create 'logs' directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('logs/clients.log'),
                        logging.StreamHandler()
                    ])

async def run_client(client_id):
    client = DiplomacyClient("ws://localhost:8765", f"Player{client_id}")
    await client.run()

async def main():
    num_clients = 7  # Number of clients to run
    clients = [run_client(i) for i in range(1, num_clients + 1)]
    await asyncio.gather(*clients)

if __name__ == "__main__":
    logging.info("Starting Diplomacy clients...")
    asyncio.run(main())