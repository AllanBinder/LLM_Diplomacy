import asyncio
import websockets
import json
import random
import logging

logging.basicConfig(level=logging.INFO)

class DiplomacyClient:
    def __init__(self, uri, player_name):
        self.uri = uri
        self.player_name = player_name
        self.websocket = None
        self.registered = False
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

    async def submit_orders(self, orders):
        order_message = json.dumps({"type": "orders", "orders": orders})
        await self.websocket.send(order_message)
        logging.info(f"Submitted orders: {orders}")

    async def receive_messages(self):
        try:
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)
                logging.info(f"Received message: {data}")

                if data['type'] in ['game_start', 'new_turn']:
                    logging.info(f"{'Game started' if data['type'] == 'game_start' else 'New turn'}. Submitting orders.")
                    orders = self.submit_random_orders(data['game_state'])
                    logging.info(f"Generated orders: {orders}")
                    await self.submit_orders(orders)
                elif data['type'] == 'turn_resolved':
                    logging.info("Turn resolved.")
                elif data['type'] == 'game_end':
                    logging.info(f"Game ended. {data['message']}")
                    break
                elif data['type'] == 'error':
                    logging.error(f"Received error from server: {data['message']}")
        except websockets.exceptions.ConnectionClosed:
            logging.info("Connection with server closed")
        except Exception as e:
            logging.error(f"An error occurred while receiving messages: {e}")

    def submit_random_orders(self, game_state):
        game_state_data = json.loads(game_state)
        player_units = {territory: unit for territory, unit in game_state_data['U'].items() if unit[1:4] == self.player_name[:3].upper()}
        
        orders = []
        for territory, unit in player_units.items():
            unit_type = 'army' if unit[0] == 'A' else 'fleet'
            adjacent_territories = self.get_adjacent_territories(territory)
            valid_moves = [t for t in adjacent_territories if self.is_valid_move(territory, t, unit_type)]
            
            if valid_moves:
                order_type = random.choice(['hold', 'move', 'support'])
                if order_type == 'hold':
                    orders.append((territory, 'hold'))
                elif order_type == 'move':
                    target = random.choice(valid_moves)
                    orders.append((territory, 'move', target))
                elif order_type == 'support':
                    supported_territory = random.choice(adjacent_territories)
                    support_target = random.choice(self.get_adjacent_territories(supported_territory) + [supported_territory])
                    orders.append((territory, 'support', supported_territory, support_target))
            else:
                orders.append((territory, 'hold'))
        
        logging.info(f"Generated orders for {self.player_name}: {orders}")
        return orders
    
    def is_valid_move(self, source, target, unit_type):
        source_type = self.get_territory_type(source)
        target_type = self.get_territory_type(target)
        
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