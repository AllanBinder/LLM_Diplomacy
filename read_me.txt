# Diplomacy Game Simulator

## Overview
This project is a Python-based implementation of the classic board game Diplomacy. It's designed to simulate the game mechanics and provide a platform for testing AI strategies, particularly focusing on negotiation, deception, and long-term planning.

## Features
- Full implementation of Diplomacy game rules
- Support for 7 players (England, France, Germany, Italy, Austria, Russia, Turkey)
- Turn-based gameplay with Spring, Fall, and Winter phases
- Order resolution system (Move, Support, Convoy, Hold)
- Retreat and disbanding mechanics
- Supply center control and unit adjustment
- Negotiation phase (currently player-input based, ready for AI integration)
- Compact JSON representation of game state for efficient AI processing

## Installation
1. Ensure you have Python 3.7+ installed on your system.
2. Clone this repository:
git clone https://github.com/yourusername/diplomacy-simulator.git
cd diplomacy-simulator
Copy3. No additional dependencies are required for the base game.

## Usage
To run the game:
python diplomacy_base.py
Copy
The game will start and prompt for player actions each turn. For testing purposes, you can use the `test_opening_moves` dictionary to automate the first turn.

## Game State Representation
The game state is represented in a compact JSON format:
```json
{
  "Y": 1901,        // Year
  "S": "S",         // Season (S: Spring, F: Fall, W: Winter)
  "P": {            // Players and their supply center counts
    "ENG": 3,
    "FRA": 3,
    ...
  },
  "U": {            // Units on the board
    "London": "FENG",  // Fleet of England in London
    ...
  },
  "SC": {           // Supply Center ownership
    "London": "ENG",
    ...
  }
}
Project Structure

diplomacy_base.py: Main game logic and classes
test_opening_moves: Dictionary of predefined opening moves for testing

Future Enhancements

AI player implementation
Graphical user interface
Network play support
Historical scenario simulations

Contributing
Contributions to improve the game or add new features are welcome. Please follow these steps:

Fork the repository
Create a new branch (git checkout -b feature-branch)
Make your changes and commit (git commit -am 'Add some feature')
Push to the branch (git push origin feature-branch)
Create a new Pull Request

License
MIT License
Acknowledgments

The creators and community of the original Diplomacy board game


