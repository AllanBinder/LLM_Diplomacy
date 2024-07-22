#diplomacy_client.py

import asyncio
import websockets
import json
import random
import logging
import traceback
from test_orders import get_orders
from test_orders import ADJACENCY


logging.basicConfig(level=logging.INFO)

class DiplomacyClient:
    def __init__(self, uri, player_name):
        self.uri = uri
        self.player_name = player_name
        self.websocket = None
        self.registered = False
        self.turn_counter = 0
        self.units = {}
        self.controlled_territories = set()
        self.adjacency = {}  # Add this line
        logging.info(f"DiplomacyClient initialized for {player_name}")

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            logging.info(f"Connected to server at {self.uri}")
            await self.register()
        except Exception as e:
            logging.error(f"An error occurred while connecting: {e}")

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

    def get_adjacent_territories(self, territory):
        adjacency = {
            # Land territories
            'Clyde': ['Edinburgh', 'Liverpool', 'North Atlantic Ocean', 'Norwegian Sea'],
            'Edinburgh': ['Clyde', 'Yorkshire', 'North Sea', 'Norwegian Sea'],
            'Yorkshire': ['Edinburgh', 'Liverpool', 'London', 'North Sea', 'Wales'],
            'Liverpool': ['Clyde', 'Yorkshire', 'Wales', 'Irish Sea', 'North Atlantic Ocean'],
            'Wales': ['Liverpool', 'Yorkshire', 'London', 'English Channel', 'Irish Sea'],
            'London': ['Yorkshire', 'Wales', 'North Sea', 'English Channel'],
            'Norway': ['St Petersburg', 'Sweden', 'Skagerrak', 'Norwegian Sea', 'Barents Sea', 'Finland'],
            'Sweden': ['Norway', 'Finland', 'Gulf of Bothnia', 'Baltic Sea', 'Skagerrak', 'Denmark'],
            'Finland': ['Norway', 'St Petersburg', 'Gulf of Bothnia', 'Sweden'],
            'St Petersburg': ['Norway', 'Finland', 'Gulf of Bothnia', 'Livonia', 'Moscow', 'Barents Sea'],
            'Moscow': ['St Petersburg', 'Livonia', 'Ukraine', 'Sevastopol', 'Warsaw'],
            'Livonia': ['St Petersburg', 'Gulf of Bothnia', 'Baltic Sea', 'Prussia', 'Warsaw', 'Moscow'],
            'Warsaw': ['Livonia', 'Prussia', 'Silesia', 'Galicia', 'Ukraine', 'Moscow'],
            'Ukraine': ['Warsaw', 'Galicia', 'Rumania', 'Sevastopol', 'Moscow'],
            'Sevastopol': ['Ukraine', 'Rumania', 'Black Sea', 'Armenia', 'Moscow'],
            'Armenia': ['Sevastopol', 'Syria', 'Smyrna', 'Ankara', 'Black Sea'],
            'Syria': ['Armenia', 'Smyrna', 'Eastern Mediterranean'],
            'Smyrna': ['Syria', 'Armenia', 'Ankara', 'Constantinople', 'Aegean Sea', 'Eastern Mediterranean'],
            'Ankara': ['Armenia', 'Smyrna', 'Constantinople', 'Black Sea'],
            'Constantinople': ['Ankara', 'Smyrna', 'Bulgaria', 'Black Sea', 'Aegean Sea'],
            'Bulgaria': ['Rumania', 'Constantinople', 'Greece', 'Serbia', 'Black Sea', 'Aegean Sea'],
            'Rumania': ['Ukraine', 'Galicia', 'Budapest', 'Serbia', 'Bulgaria', 'Black Sea', 'Sevastopol'],
            'Serbia': ['Budapest', 'Trieste', 'Albania', 'Greece', 'Bulgaria', 'Rumania'],
            'Greece': ['Serbia', 'Albania', 'Ionian Sea', 'Aegean Sea', 'Bulgaria'],
            'Albania': ['Serbia', 'Trieste', 'Adriatic Sea', 'Ionian Sea', 'Greece'],
            'Galicia': ['Warsaw', 'Silesia', 'Bohemia', 'Budapest', 'Rumania', 'Ukraine'],
            'Budapest': ['Galicia', 'Vienna', 'Trieste', 'Serbia', 'Rumania'],
            'Vienna': ['Bohemia', 'Tyrolia', 'Trieste', 'Budapest', 'Galicia'],
            'Bohemia': ['Silesia', 'Munich', 'Tyrolia', 'Vienna', 'Galicia'],
            'Tyrolia': ['Munich', 'Bohemia', 'Vienna', 'Trieste', 'Venice', 'Piedmont'],
            'Trieste': ['Venice', 'Tyrolia', 'Vienna', 'Budapest', 'Serbia', 'Albania', 'Adriatic Sea'],
            'Venice': ['Piedmont', 'Tyrolia', 'Trieste', 'Adriatic Sea', 'Apulia', 'Rome'],
            'Rome': ['Tuscany', 'Venice', 'Apulia', 'Naples', 'Tyrrhenian Sea'],
            'Naples': ['Rome', 'Apulia', 'Ionian Sea', 'Tyrrhenian Sea'],
            'Apulia': ['Venice', 'Rome', 'Naples', 'Adriatic Sea', 'Ionian Sea'],
            'Tuscany': ['Piedmont', 'Venice', 'Rome', 'Gulf of Lyon', 'Tyrrhenian Sea'],
            'Piedmont': ['Marseilles', 'Tyrolia', 'Venice', 'Tuscany', 'Gulf of Lyon'],
            'Marseilles': ['Spain', 'Gascony', 'Burgundy', 'Piedmont', 'Gulf of Lyon'],
            'Gascony': ['Brest', 'Paris', 'Burgundy', 'Marseilles', 'Spain', 'Mid-Atlantic Ocean'],
            'Paris': ['Picardy', 'Burgundy', 'Gascony', 'Brest'],
            'Brest': ['English Channel', 'Picardy', 'Paris', 'Gascony', 'Mid-Atlantic Ocean'],
            'Picardy': ['Belgium', 'Burgundy', 'Paris', 'Brest', 'English Channel'],
            'Belgium': ['Holland', 'Ruhr', 'Burgundy', 'Picardy', 'English Channel', 'North Sea'],
            'Holland': ['North Sea', 'Helgoland Bight', 'Kiel', 'Ruhr', 'Belgium'],
            'Ruhr': ['Holland', 'Kiel', 'Munich', 'Burgundy', 'Belgium'],
            'Burgundy': ['Belgium', 'Ruhr', 'Munich', 'Marseilles', 'Gascony', 'Paris', 'Picardy'],
            'Munich': ['Ruhr', 'Kiel', 'Berlin', 'Silesia', 'Bohemia', 'Tyrolia', 'Burgundy'],
            'Kiel': ['Denmark', 'Berlin', 'Munich', 'Ruhr', 'Holland', 'Helgoland Bight', 'Baltic Sea'],
            'Berlin': ['Kiel', 'Baltic Sea', 'Prussia', 'Silesia', 'Munich'],
            'Prussia': ['Baltic Sea', 'Livonia', 'Warsaw', 'Silesia', 'Berlin'],
            'Silesia': ['Berlin', 'Prussia', 'Warsaw', 'Galicia', 'Bohemia', 'Munich'],
            'Denmark': ['Kiel', 'Baltic Sea', 'Sweden', 'Skagerrak', 'North Sea'],
            'Spain': ['Portugal', 'Gascony', 'Marseilles', 'Gulf of Lyon', 'Western Mediterranean', 'Mid-Atlantic Ocean'],
            'Portugal': ['Spain', 'Mid-Atlantic Ocean'],
            
            # Sea territories
            'Norwegian Sea': ['North Atlantic Ocean', 'Clyde', 'Edinburgh', 'Norway', 'North Sea', 'Barents Sea'],
            'Barents Sea': ['Norwegian Sea', 'Norway', 'St Petersburg'],
            'North Sea': ['Norwegian Sea', 'Edinburgh', 'Yorkshire', 'London', 'English Channel', 'Belgium', 'Holland', 'Helgoland Bight', 'Denmark', 'Skagerrak', 'Norway'],
            'Skagerrak': ['Norway', 'Sweden', 'Denmark', 'North Sea'],
            'Helgoland Bight': ['North Sea', 'Denmark', 'Kiel', 'Holland'],
            'Baltic Sea': ['Gulf of Bothnia', 'Livonia', 'Prussia', 'Berlin', 'Kiel', 'Denmark', 'Sweden'],
            'Gulf of Bothnia': ['Sweden', 'Finland', 'St Petersburg', 'Livonia', 'Baltic Sea'],
            'Irish Sea': ['North Atlantic Ocean', 'Liverpool', 'Wales', 'English Channel'],
            'English Channel': ['Irish Sea', 'Wales', 'London', 'North Sea', 'Belgium', 'Picardy', 'Brest', 'Mid-Atlantic Ocean'],
            'Mid-Atlantic Ocean': ['North Atlantic Ocean', 'Irish Sea', 'English Channel', 'Brest', 'Gascony', 'Spain', 'Portugal', 'Western Mediterranean', 'North Africa'],
            'North Atlantic Ocean': ['Norwegian Sea', 'Clyde', 'Liverpool', 'Irish Sea', 'Mid-Atlantic Ocean'],
            'Western Mediterranean': ['Spain', 'Gulf of Lyon', 'Tyrrhenian Sea', 'Tunis', 'North Africa', 'Mid-Atlantic Ocean'],
            'Gulf of Lyon': ['Spain', 'Marseilles', 'Piedmont', 'Tuscany', 'Tyrrhenian Sea', 'Western Mediterranean'],
            'Tyrrhenian Sea': ['Gulf of Lyon', 'Tuscany', 'Rome', 'Naples', 'Ionian Sea', 'Tunis', 'Western Mediterranean'],
            'Ionian Sea': ['Tyrrhenian Sea', 'Naples', 'Apulia', 'Adriatic Sea', 'Albania', 'Greece', 'Aegean Sea', 'Eastern Mediterranean', 'Tunis'],
            'Adriatic Sea': ['Venice', 'Trieste', 'Albania', 'Ionian Sea', 'Apulia'],
            'Aegean Sea': ['Greece', 'Bulgaria', 'Constantinople', 'Smyrna', 'Eastern Mediterranean', 'Ionian Sea'],
            'Eastern Mediterranean': ['Ionian Sea', 'Aegean Sea', 'Smyrna', 'Syria', 'Egypt'],
            'Black Sea': ['Bulgaria', 'Rumania', 'Sevastopol', 'Armenia', 'Ankara', 'Constantinople'],
            
            # Non-standard territories (often used in variants)
            'North Africa': ['Mid-Atlantic Ocean', 'Western Mediterranean', 'Tunis'],
            'Tunis': ['North Africa', 'Western Mediterranean', 'Tyrrhenian Sea', 'Ionian Sea'],
            'Egypt': ['Eastern Mediterranean'],
        }
        return adjacency.get(territory, [])

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
    logging.basicConfig(level=logging.INFO)
    client = DiplomacyClient("ws://localhost:8765", f"Player{random.randint(1,100)}")
    asyncio.run(client.run())