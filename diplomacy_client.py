#diplomacy_client.py

import asyncio
import websockets
import json
import random
import logging
import traceback
import os
from test_orders import get_orders
from game_utils import ADJACENCY, get_adjacent_territories
#from llm_agents.llm_players import LLMPlayerFactory


# Create 'logs' directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up logging to both console and file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('logs/clients.log'),
                        logging.StreamHandler()
                    ])

class DiplomacyClient:
    def __init__(self, uri, player_name, llm_type, **llm_kwargs):
        self.uri = uri
        self.player_name = player_name
        self.llm_player = LLMPlayerFactory.create_player(llm_type, player_name, **llm_kwargs)
        self.websocket = None
        self.registered = False
        self.turn_counter = 0
        self.units = {}
        self.controlled_territories = set()
        self.adjacency = {}
        self.logger = logging.getLogger(f"Client-{player_name}")
        self.logger.info(f"DiplomacyClient initialized for {player_name}")

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.logger.info(f"Connected to server at {self.uri}")
            await self.register()
        except Exception as e:
            self.logger.error(f"An error occurred while connecting: {e}")

    async def register(self):
        try:
            register_message = json.dumps({"type": "register", "player_name": self.player_name})
            await self.websocket.send(register_message)
            logging.info(f"Sent registration message for {self.player_name}")
            response = await self.websocket.recv()
            logging.info(f"Registration response: {response}")
            response_data = json.loads(response)
            if response_data.get("status") == "success":
                self.registered = True
                return True
            else:
                logging.error(f"Registration failed: {response_data.get('reason', 'Unknown reason')}")
                return False
        except Exception as e:
            logging.error(f"Error during registration: {e}")
            return False

    async def submit_orders(self, game_state):
        try:
            self.turn_counter += 1
            is_active = self.parse_game_state(game_state)
            
            if not is_active:
                logging.info(f"{self.player_name} has no units or territories. Skipping order submission.")
                return

            country = self.get_country_from_player_name()
            orders = get_orders(country, self.units, self.controlled_territories, self.adjacency)
            
            if orders:
                logging.info(f"Generated orders for {self.player_name} (Turn {self.turn_counter}): {orders}")
                order_message = json.dumps({"type": "orders", "orders": orders})
                await self.websocket.send(order_message)
                logging.info(f"Submitted orders: {orders}")
            else:
                logging.warning(f"No valid orders generated for {self.player_name} (Turn {self.turn_counter}).")
        except Exception as e:
            logging.error(f"Error submitting orders: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")

    def submit_random_orders(self, game_state):
        self.turn_count += 1
        country = self.get_country_from_player_name()
        orders = get_orders(country, self.turn_count)
        
        if orders:
            logging.info(f"Generated orders for {self.player_name} (Turn {self.turn_count}): {orders}")
        else:
            logging.warning(f"No predefined orders for {self.player_name} (Turn {self.turn_count}). Generating empty order list.")
        
        return orders
    
    def parse_game_state(self, game_state_json):
        game_state = json.loads(game_state_json)
        country = self.get_country_from_player_name()
        country_code = country[:3].upper()

        self.units = {}
        self.controlled_territories = set()

        for territory, unit in game_state['U'].items():
            if unit.endswith(country_code):
                self.units[territory] = unit[0]  # 'A' for Army, 'F' for Fleet
                self.controlled_territories.add(territory)

        for territory, owner in game_state['SC'].items():
            if owner == country_code:
                self.controlled_territories.add(territory)

        # Update adjacency information
        self.adjacency = ADJACENCY  # Import ADJACENCY from test_orders.py

        logging.info(f"{self.player_name} units: {self.units}")
        logging.info(f"{self.player_name} controlled territories: {self.controlled_territories}")

        return len(self.units) > 0 or len(self.controlled_territories) > 0

    def get_country_from_player_name(self):
        country_mapping = {
            'Player1': 'England',
            'Player2': 'France',
            'Player3': 'Germany',
            'Player4': 'Italy',
            'Player5': 'Austria',
            'Player6': 'Russia',
            'Player7': 'Turkey'
        }
        return country_mapping.get(self.player_name, 'Unknown')

    async def receive_messages(self):
        try:
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)
                logging.info(f"Received message: {data}")

                if data['type'] in ['game_start', 'new_turn']:
                    logging.info(f"{'Game started' if data['type'] == 'game_start' else 'New turn'}. Submitting orders.")
                    await self.submit_orders(data['game_state'])
                elif data['type'] == 'turn_resolved':
                    logging.info("Turn resolved.")
                elif data['type'] == 'game_end':
                    logging.info(f"Game ended. {data['message']}")
                    break
                elif data['type'] == 'error':
                    logging.error(f"Received error from server: {data['message']}")
                elif data['type'] == 'pong':
                    logging.info("Received pong from server")
        except websockets.exceptions.ConnectionClosed:
            logging.info("Connection with server closed")
        except Exception as e:
            logging.error(f"An error occurred while receiving messages: {e}")

    def is_valid_move(self, source, target, unit_type):
        source_type = self.get_territory_type(source)
        target_type = self.get_territory_type(target)
        
        logging.info(f"Checking move validity: {source} ({source_type}) to {target} ({target_type}) for {unit_type}")
        
        if unit_type == 'army':
            return target_type in ['land', 'coast']
        elif unit_type == 'fleet':
            if source_type == 'coast' and target_type == 'coast':
                return True
            return target_type == 'sea'
        return False

    def get_territory_type(self, territory):
        land_territories = ['Moscow', 'St Petersburg', 'Warsaw', 'Livonia', 'Ukraine', 'Sevastopol', 'Armenia', 'Syria', 'Smyrna', 'Ankara', 'Constantinople', 'Bulgaria', 'Rumania', 'Serbia', 'Greece', 'Albania', 'Trieste', 'Vienna', 'Budapest', 'Galicia', 'Bohemia', 'Tyrolia', 'Piedmont', 'Tuscany', 'Rome', 'Apulia', 'Naples', 'Venice', 'Munich', 'Ruhr', 'Prussia', 'Silesia', 'Berlin', 'Kiel', 'Holland', 'Belgium', 'Picardy', 'Burgundy', 'Marseilles', 'Gascony', 'Paris', 'Brest', 'Spain', 'Portugal', 'North Africa', 'Tunis']
        sea_territories = ['Barents Sea', 'Norwegian Sea', 'North Sea', 'Skagerrak', 'Helgoland Bight', 'Baltic Sea', 'Gulf of Bothnia', 'Gulf of Lyon', 'Tyrrhenian Sea', 'Ionian Sea', 'Adriatic Sea', 'Aegean Sea', 'Eastern Mediterranean', 'Black Sea', 'Mid-Atlantic Ocean', 'Western Mediterranean', 'North Atlantic Ocean']
        
        if territory in land_territories:
            return 'land'
        elif territory in sea_territories:
            return 'sea'
        else:
            return 'coast'  # Assume any territory not explicitly listed is a coastal territory

    
    async def ping(self):
        while True:
            try:
                await asyncio.sleep(30)  # Send a ping every 30 seconds
                await self.websocket.send(json.dumps({"type": "ping"}))
                logging.info("Sent ping to server")
            except websockets.exceptions.ConnectionClosed:
                break

    async def run(self):
        await self.connect()
        if self.registered:
            await self.receive_messages()
        await self.websocket.close()

    async def main():
        client = DiplomacyClient("ws://localhost:8765", f"Player{random.randint(1,100)}")
        await client.run()

if __name__ == "__main__":
    client = DiplomacyClient("ws://localhost:8765", f"Player{random.randint(1,100)}")
    asyncio.run(client.run())