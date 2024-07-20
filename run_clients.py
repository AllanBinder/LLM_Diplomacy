import asyncio
import random
from diplomacy_client import DiplomacyClient

async def run_client(client_id):
    client = DiplomacyClient("ws://localhost:8765", f"Player{client_id}")
    await client.run()

async def main():
    num_clients = 7  # Number of clients to run
    clients = [run_client(i) for i in range(1, num_clients + 1)]
    await asyncio.gather(*clients)

if __name__ == "__main__":
    asyncio.run(main())