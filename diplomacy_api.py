from flask import Flask, request, jsonify
from game import Game

app = Flask(__name__)
game = Game()

@app.route('/game_state', methods=['GET'])
def get_game_state():
    return jsonify(game.generate_game_state_json())

@app.route('/submit_orders', methods=['POST'])
def submit_orders():
    data = request.json
    player_name = data['player']
    orders = data['orders']
    game.process_ai_orders(player_name, orders)
    return jsonify({"status": "orders received"})

@app.route('/negotiate', methods=['POST'])
def negotiate():
    data = request.json
    # Process negotiation data
    # This would interact with the game's negotiation system
    return jsonify({"status": "negotiation processed"})

if __name__ == '__main__':
    app.run(debug=True)