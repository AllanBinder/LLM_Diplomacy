# diplomacy_server.py
import asyncio
import websockets
import json
import logging
import signal
import traceback
import os
from diplomacy_base import Game

os.makedirs('logs', exist_ok=True)

# Set up logging to both console and file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('logs/server.log'),
                        logging.StreamHandler()
                    ])

MAX_TURNS = 3

class DiplomacyServer:
    def __init__(self):
        self.game = Game()
        self.connected_players = {}
        self.lock = asyncio.Lock()
        self.turn_counter = 0
        self.max_turns = 3  # Set to 10 for a longer game
        logging.info("DiplomacyServer initialized")

    async def register(self, websocket, player_name):
        async with self.lock:
            if player_name in self.connected_players:
                logging.info(f"Player {player_name} already registered")
                return

            if len(self.connected_players) < 7:
                self.connected_players[player_name] = websocket
                await websocket.send(json.dumps({"type": "registration", "status": "success"}))
                logging.info(f"Player {player_name} registered. Total players: {len(self.connected_players)}")
                if len(self.connected_players) == 7:
                    logging.info("All players joined. Starting the game.")
                    await self.start_game()
            else:
                await websocket.send(json.dumps({"type": "registration", "status": "failed", "reason": "Game is full"}))
                logging.info(f"Registration failed for {player_name}. Game is full.")

    async def unregister(self, player_name):
        if player_name in self.connected_players:
            del self.connected_players[player_name]
            logging.info(f"Player {player_name} unregistered. Total players: {len(self.connected_players)}")


    async def start_game(self):
        try:
            game_state = self.game.play_turn()
            await self.broadcast({"type": "game_start", "game_state": game_state})
        except Exception as e:
            logging.error(f"Error starting the game: {e}")
            await self.broadcast({"type": "error", "message": "Failed to start the game"})

    async def broadcast(self, message):
        if self.connected_players:
            await asyncio.gather(
                *[ws.send(json.dumps(message)) for ws in self.connected_players.values()]
            )

    async def end_game(self):
        winner = self.game.check_victory()
        message = f"Game ended. "
        if winner:
            message += f"{winner} has won the game!"
        else:
            message += "No clear winner."
        await self.broadcast({"type": "game_end", "message": message})
        for ws in self.connected_players.values():
            await ws.close()

    async def handle_orders(self, player_name, orders):
        async with self.lock:
            try:
                logging.info(f"Received orders from {player_name}: {orders}")
                self.game.orders[player_name] = orders
                logging.info(f"Current orders: {self.game.orders}")
                logging.info(f"Connected players: {self.connected_players}")
                
                if len(self.game.orders) == len(self.connected_players):
                    logging.info("All orders received. Resolving turn.")
                    self.game.resolve_turn()
                    new_game_state = self.game.generate_game_state_json()
                    logging.info(f"New game state: {new_game_state}")
                    await self.broadcast({"type": "turn_resolved", "game_state": new_game_state})
                    
                    self.turn_counter += 1
                    logging.info(f"Turn {self.turn_counter} completed")
                    
                    if self.turn_counter >= self.max_turns or self.game.check_victory():
                        logging.info("Game end condition met.")
                        await self.end_game()
                    else:
                        self.game.orders.clear()  # Clear orders for the next turn
                        next_game_state = self.game.generate_game_state_json()
                        await self.broadcast({"type": "new_turn", "game_state": next_game_state})
            except Exception as e:
                logging.error(f"Error processing orders: {str(e)}")
                logging.error(f"Traceback: {traceback.format_exc()}")
                await self.notify_player(player_name, {"type": "error", "message": "Error processing orders"})

    def all_active_players_submitted(self):
        # Consider a player active if they're connected and have units
        active_players = [p for p in self.connected_players if self.game.players[p]["units"]]
        return len(self.game.orders) == len(active_players)

    async def handle_connection(self, websocket, path):
        player_name = None
        try:
            async for message in websocket:
                data = json.loads(message)
                logging.info(f"Received message: {data}")

                if data["type"] == "register":
                    player_name = data["player_name"]
                    await self.register(websocket, player_name)
                elif data["type"] == "orders" and player_name and self.game.is_active:
                    await self.handle_orders(player_name, data["orders"])
                elif data["type"] == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))

        except websockets.exceptions.ConnectionClosed:
            logging.info(f"Connection closed for {player_name}")
        except Exception as e:
            logging.error(f"Error in handle_connection: {str(e)}")
            logging.error(traceback.format_exc())
        finally:
            if player_name:
                await self.unregister(player_name)
    
    async def notify_player(self, player_name, message):
        if player_name in self.connected_players:
            await self.connected_players[player_name].send(json.dumps(message))

    async def main(self):
        server = await websockets.serve(self.handle_connection, "localhost", 8765)
        logging.info("Server started. Waiting for connections...")
        try:
            await server.wait_closed()
        except asyncio.CancelledError:
            logging.info("Server shutting down...")
        finally:
            await self.end_game()
            logging.info("Game ended.")

if __name__ == "__main__":
    logging.info("Starting the Diplomacy server...")
    server = DiplomacyServer()
    asyncio.run(server.main())