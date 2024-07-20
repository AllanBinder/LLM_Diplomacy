import random

import json


class Territory:
    def __init__(self, name, type):
        self.name = name
        self.type = type  # 'land', 'sea', or 'coast'
        self.owner = None
        self.units = 0
        self.adjacent = []
        self.is_supply_center = False
        self.unit = None  # Add this line

    def can_host(self, unit_type):
        if unit_type == 'army':
            return self.type in ['land', 'coast']
        elif unit_type == 'fleet':
            return self.type in ['sea', 'coast']
        return False
    
class Order:
    def __init__(self, unit, order_type, source, target=None, support_target=None):
        self.unit = unit
        self.type = order_type  # 'move', 'support', 'convoy', 'hold'
        self.source = source
        self.target = target
        self.support_target = support_target

class Player:
    def __init__(self, name):
        self.name = name
        self.territories = []
        self.supply_centers = []
        self.units = []

class Unit:
    def __init__(self, unit_type):
        self.type = unit_type  # 'army' or 'fleet'

class Game:
    def __init__(self):
        self.players = {}
        self.territories = {}
        self.orders = {}
        self.year = 1901  
        self.season = 'Spring'  
        self.player_orders = {}  # To track orders from each player
        self.players_ready = set()  # To track which players have submitted orders
        self.is_active = True
        self.initialize_game()

    def initialize_game(self):
        # Create territories with adjacencies
        self.create_map()

         # Create players
        player_names = ["England", "France", "Germany", "Italy", "Austria", "Russia", "Turkey"]
        for name in player_names:
            self.players[name] = {"territories": [], "supply_centers": [], "units": []}


        # Assign initial territories, units, and supply centers
        self.assign_initial_state()

    def process_ai_orders(self, player_name, orders):
        if player_name not in self.players_ready:
            self.player_orders[player_name] = orders
            self.players_ready.add(player_name)

    def all_orders_received(self):
        return len(self.players_ready) == len(self.players)

        
    def create_map(self):
        # Full Diplomacy map with all 75 territories
        territories = {
            # Format: 'name': ('type', ['adjacent territories'], is_supply_center)
            
            # England
            'Clyde': ('coast', ['Edinburgh', 'Liverpool', 'North Atlantic Ocean', 'Norwegian Sea'], False),
            'Edinburgh': ('coast', ['Clyde', 'Yorkshire', 'North Sea', 'Norwegian Sea'], True),
            'Liverpool': ('coast', ['Clyde', 'Yorkshire', 'Wales', 'Irish Sea', 'North Atlantic Ocean'], True),
            'Yorkshire': ('coast', ['Edinburgh', 'Liverpool', 'Wales', 'London', 'North Sea'], False),
            'Wales': ('coast', ['Liverpool', 'Yorkshire', 'London', 'English Channel', 'Irish Sea'], False),
            'London': ('coast', ['Yorkshire', 'Wales', 'North Sea', 'English Channel'], True),
            
            # France
            'Brest': ('coast', ['English Channel', 'Mid-Atlantic Ocean', 'Gascony', 'Paris', 'Picardy'], True),
            'Paris': ('land', ['Brest', 'Picardy', 'Burgundy', 'Gascony'], True),
            'Picardy': ('coast', ['English Channel', 'Belgium', 'Burgundy', 'Paris', 'Brest'], False),
            'Burgundy': ('land', ['Paris', 'Picardy', 'Belgium', 'Ruhr', 'Munich', 'Marseilles', 'Gascony'], False),
            'Marseilles': ('coast', ['Burgundy', 'Gascony', 'Spain', 'Gulf of Lyon', 'Piedmont'], True),
            'Gascony': ('coast', ['Brest', 'Paris', 'Burgundy', 'Marseilles', 'Spain', 'Mid-Atlantic Ocean'], False),
            
            # Germany
            'Kiel': ('coast', ['Denmark', 'Helgoland Bight', 'Holland', 'Ruhr', 'Munich', 'Berlin', 'Baltic Sea'], True),
            'Berlin': ('coast', ['Kiel', 'Baltic Sea', 'Prussia', 'Silesia', 'Munich'], True),
            'Prussia': ('coast', ['Berlin', 'Silesia', 'Warsaw', 'Livonia', 'Baltic Sea'], False),
            'Ruhr': ('land', ['Holland', 'Kiel', 'Munich', 'Burgundy', 'Belgium'], False),
            'Munich': ('land', ['Ruhr', 'Kiel', 'Berlin', 'Silesia', 'Bohemia', 'Tyrolia', 'Burgundy'], True),
            
            # Italy
            'Piedmont': ('coast', ['Marseilles', 'Gulf of Lyon', 'Tuscany', 'Venice', 'Tyrolia'], False),
            'Venice': ('coast', ['Piedmont', 'Tuscany', 'Rome', 'Apulia', 'Adriatic Sea', 'Tyrolia', 'Trieste'], True),
            'Tuscany': ('coast', ['Piedmont', 'Gulf of Lyon', 'Tyrrhenian Sea', 'Rome', 'Venice'], False),
            'Rome': ('coast', ['Tuscany', 'Venice', 'Apulia', 'Naples', 'Tyrrhenian Sea'], True),
            'Apulia': ('coast', ['Venice', 'Adriatic Sea', 'Ionian Sea', 'Naples', 'Rome'], False),
            'Naples': ('coast', ['Rome', 'Apulia', 'Ionian Sea', 'Tyrrhenian Sea'], True),
            
            # Austria
            'Bohemia': ('land', ['Munich', 'Silesia', 'Galicia', 'Vienna', 'Tyrolia'], False),
            'Galicia': ('land', ['Warsaw', 'Ukraine', 'Rumania', 'Budapest', 'Vienna', 'Bohemia', 'Silesia'], False),
            'Tyrolia': ('land', ['Munich', 'Bohemia', 'Vienna', 'Trieste', 'Venice', 'Piedmont'], False),
            'Vienna': ('land', ['Bohemia', 'Galicia', 'Budapest', 'Trieste', 'Tyrolia'], True),
            'Budapest': ('land', ['Vienna', 'Galicia', 'Rumania', 'Serbia', 'Trieste'], True),
            'Trieste': ('coast', ['Tyrolia', 'Vienna', 'Budapest', 'Serbia', 'Albania', 'Adriatic Sea', 'Venice'], True),
            
            # Russia
            'St Petersburg': ('coast', ['Norway', 'Finland', 'Livonia', 'Moscow', 'Gulf of Bothnia'], True),
            'Moscow': ('land', ['St Petersburg', 'Livonia', 'Ukraine', 'Sevastopol', 'Warsaw'], True),
            'Warsaw': ('land', ['Prussia', 'Silesia', 'Galicia', 'Ukraine', 'Moscow', 'Livonia'], True),
            'Livonia': ('coast', ['Baltic Sea', 'Prussia', 'Warsaw', 'Moscow', 'St Petersburg', 'Gulf of Bothnia'], False),
            'Ukraine': ('land', ['Warsaw', 'Moscow', 'Sevastopol', 'Rumania', 'Galicia'], False),
            'Sevastopol': ('coast', ['Ukraine', 'Moscow', 'Armenia', 'Black Sea', 'Rumania'], True),
            
            # Turkey
            'Constantinople': ('coast', ['Bulgaria', 'Black Sea', 'Ankara', 'Smyrna', 'Aegean Sea'], True),
            'Ankara': ('coast', ['Black Sea', 'Armenia', 'Smyrna', 'Constantinople'], True),
            'Smyrna': ('coast', ['Constantinople', 'Ankara', 'Armenia', 'Syria', 'Eastern Mediterranean', 'Aegean Sea'], True),
            'Syria': ('coast', ['Smyrna', 'Armenia', 'Eastern Mediterranean'], False),
            'Armenia': ('coast', ['Black Sea', 'Sevastopol', 'Syria', 'Smyrna', 'Ankara'], False),
            
            # Neutral territories
            'Norway': ('coast', ['Norwegian Sea', 'North Sea', 'Skagerrak', 'Sweden', 'Finland', 'St Petersburg'], True),
            'Sweden': ('coast', ['Norway', 'Finland', 'Gulf of Bothnia', 'Baltic Sea', 'Denmark', 'Skagerrak'], True),
            'Finland': ('coast', ['Norway', 'St Petersburg', 'Gulf of Bothnia', 'Sweden'], False),
            'Denmark': ('coast', ['North Sea', 'Skagerrak', 'Baltic Sea', 'Kiel', 'Helgoland Bight'], True),
            'Holland': ('coast', ['North Sea', 'Helgoland Bight', 'Kiel', 'Ruhr', 'Belgium'], True),
            'Belgium': ('coast', ['North Sea', 'English Channel', 'Picardy', 'Burgundy', 'Ruhr', 'Holland'], True),
            'Spain': ('coast', ['Mid-Atlantic Ocean', 'Gascony', 'Marseilles', 'Gulf of Lyon', 'Western Mediterranean', 'Portugal'], True),
            'Portugal': ('coast', ['Mid-Atlantic Ocean', 'Spain'], True),
            'Rumania': ('coast', ['Black Sea', 'Bulgaria', 'Serbia', 'Budapest', 'Galicia', 'Ukraine', 'Sevastopol'], True),
            'Serbia': ('land', ['Budapest', 'Rumania', 'Bulgaria', 'Greece', 'Albania', 'Trieste'], True),
            'Albania': ('coast', ['Trieste', 'Serbia', 'Greece', 'Ionian Sea', 'Adriatic Sea'], False),
            'Greece': ('coast', ['Albania', 'Serbia', 'Bulgaria', 'Aegean Sea', 'Ionian Sea'], True),
            'Bulgaria': ('coast', ['Rumania', 'Black Sea', 'Constantinople', 'Aegean Sea', 'Greece', 'Serbia'], True),
            
            # Sea zones
            'North Sea': ('sea', ['Norwegian Sea', 'Norway', 'Skagerrak', 'Denmark', 'Helgoland Bight', 'Holland', 'Belgium', 'English Channel', 'London', 'Yorkshire', 'Edinburgh'], False),
            'Norwegian Sea': ('sea', ['North Atlantic Ocean', 'Clyde', 'Edinburgh', 'Norway', 'North Sea'], False),
            'Barents Sea': ('sea', ['Norwegian Sea', 'Norway', 'St Petersburg'], False),
            'Baltic Sea': ('sea', ['Gulf of Bothnia', 'Livonia', 'Prussia', 'Berlin', 'Kiel', 'Denmark', 'Sweden'], False),
            'Gulf of Bothnia': ('sea', ['Sweden', 'Finland', 'St Petersburg', 'Livonia', 'Baltic Sea'], False),
            'Skagerrak': ('sea', ['Norway', 'Sweden', 'Denmark', 'North Sea'], False),
            'Helgoland Bight': ('sea', ['North Sea', 'Denmark', 'Kiel', 'Holland'], False),
            'English Channel': ('sea', ['Irish Sea', 'Wales', 'London', 'North Sea', 'Belgium', 'Picardy', 'Brest', 'Mid-Atlantic Ocean'], False),
            'Irish Sea': ('sea', ['North Atlantic Ocean', 'Liverpool', 'Wales', 'English Channel'], False),
            'Mid-Atlantic Ocean': ('sea', ['North Atlantic Ocean', 'Irish Sea', 'English Channel', 'Brest', 'Gascony', 'Spain', 'Portugal', 'Western Mediterranean', 'North Africa'], False),
            'Gulf of Lyon': ('sea', ['Spain', 'Marseilles', 'Piedmont', 'Tuscany', 'Tyrrhenian Sea', 'Western Mediterranean'], False),
            'Western Mediterranean': ('sea', ['Mid-Atlantic Ocean', 'Spain', 'Gulf of Lyon', 'Tyrrhenian Sea', 'Tunis', 'North Africa'], False),
            'Tyrrhenian Sea': ('sea', ['Western Mediterranean', 'Gulf of Lyon', 'Tuscany', 'Rome', 'Naples', 'Ionian Sea', 'Tunis'], False),
            'Ionian Sea': ('sea', ['Tyrrhenian Sea', 'Naples', 'Apulia', 'Adriatic Sea', 'Albania', 'Greece', 'Aegean Sea', 'Eastern Mediterranean', 'Tunis'], False),
            'Adriatic Sea': ('sea', ['Venice', 'Trieste', 'Albania', 'Ionian Sea', 'Apulia'], False),
            'Aegean Sea': ('sea', ['Greece', 'Bulgaria', 'Constantinople', 'Smyrna', 'Eastern Mediterranean', 'Ionian Sea'], False),
            'Eastern Mediterranean': ('sea', ['Ionian Sea', 'Aegean Sea', 'Smyrna', 'Syria', 'Egypt'], False),
            'Black Sea': ('sea', ['Bulgaria', 'Rumania', 'Sevastopol', 'Armenia', 'Ankara', 'Constantinople'], False),
            'North Atlantic Ocean': ('sea', ['Norwegian Sea', 'Clyde', 'Liverpool', 'Irish Sea', 'Mid-Atlantic Ocean'], False),
            
            # Non-standard territories (often used in variants)
            'North Africa': ('coast', ['Mid-Atlantic Ocean', 'Western Mediterranean', 'Tunis'], False),
            'Tunis': ('coast', ['North Africa', 'Western Mediterranean', 'Tyrrhenian Sea', 'Ionian Sea'], True),
            'Egypt': ('coast', ['Eastern Mediterranean'], False),
            'Silesia': ('land', ['Berlin', 'Prussia', 'Warsaw', 'Galicia', 'Bohemia', 'Munich'], False),
        }

        for name, (type, adjacent, is_supply_center) in territories.items():
            self.territories[name] = Territory(name, type)
            self.territories[name].is_supply_center = is_supply_center

        # Set adjacencies
        for name, (_, adjacent, _) in territories.items():
            self.territories[name].adjacent = [self.territories[adj] for adj in adjacent]


    def assign_initial_state(self):
        initial_setup = {
            'England': [('London', 'fleet'), ('Edinburgh', 'fleet'), ('Liverpool', 'army')],
            'France': [('Paris', 'army'), ('Marseilles', 'army'), ('Brest', 'fleet')],
            'Germany': [('Berlin', 'army'), ('Kiel', 'fleet'), ('Munich', 'army')],
            'Italy': [('Rome', 'army'), ('Venice', 'army'), ('Naples', 'fleet')],
            'Austria': [('Vienna', 'army'), ('Budapest', 'army'), ('Trieste', 'fleet')],
            'Russia': [('Moscow', 'army'), ('Sevastopol', 'fleet'), ('St Petersburg', 'fleet'), ('Warsaw', 'army')],
            'Turkey': [('Constantinople', 'army'), ('Ankara', 'army'), ('Smyrna', 'fleet')]
        }

        for player_name, territories in initial_setup.items():
            for territory_name, unit_type in territories:
                territory = self.territories[territory_name]
                territory.owner = player_name
                unit = Unit(unit_type)
                territory.unit = unit
                self.players[player_name]["territories"].append(territory)
                self.players[player_name]["units"].append(unit)
                if territory.is_supply_center:
                    self.players[player_name]["supply_centers"].append(territory)


    def play_year(self):
        self.play_spring_turn()
        self.play_fall_turn()
        self.winter_adjustments()

    def play_spring_turn(self):
        print(f"\n--- {self.year} Spring ---")
        self.play_turn()
        self.retreat_and_disband()
        self.season = 'Fall'

    def play_fall_turn(self):
        print(f"\n--- {self.year} Fall ---")
        self.play_turn()
        self.retreat_and_disband()
        self.season = 'Winter'

    def winter_adjustments(self):
        print(f"\n--- {self.year} Winter Adjustments ---")
        for player in self.players:
            supply_centers = len(player.supply_centers)
            units = len(player.units)
            
            if supply_centers > units:
                self.build_units(player, supply_centers - units)
            elif units > supply_centers:
                self.remove_units(player, units - supply_centers)
            else:
                print(f"{player.name} has {units} units and {supply_centers} supply centers. No adjustments needed.")

        self.year += 1
        self.season = 'Spring'
        self.display_game_state_json()

    def play_turn(self):
        self.orders.clear()
        if self.season == 'Spring':
            self.season = 'Fall'
        elif self.season == 'Fall':
            self.season = 'Spring'
            self.year += 1
        return self.generate_game_state_json()

    def submit_orders(self, player_name, orders):
        self.orders[player_name] = orders
        return self.all_orders_received(), self.generate_game_state_json()
    
    def all_orders_received(self):
        return len(self.orders) == len(self.players)

    def get_player_orders(self, player):
        print(f"\n{player.name}'s turn to give orders:")
        for territory in player.territories:
            if territory.unit:
                while True:
                    print(f"\nUnit in {territory.name} ({territory.unit.type}):")
                    order_type = input("Enter order type (move/support/convoy/hold): ").lower()
                    if order_type == 'move':
                        target = input("Enter target territory: ")
                        if target in self.territories and self.is_valid_move(territory, self.territories[target], territory.unit.type):
                            self.orders.append(Order(territory.unit, 'move', territory, self.territories[target]))
                            break
                    elif order_type == 'support':
                        support_from = input("Enter territory to support from: ")
                        support_to = input("Enter territory to support to (or 'hold' for support to hold): ")
                        if support_from in self.territories and (support_to in self.territories or support_to == 'hold'):
                            if self.is_valid_support(territory, self.territories[support_from], self.territories[support_to] if support_to != 'hold' else None):
                                support_target = self.territories[support_to] if support_to != 'hold' else None
                                self.orders.append(Order(territory.unit, 'support', territory, self.territories[support_from], support_target))
                                break
                    elif order_type == 'convoy':
                        convoy_from = input("Enter territory to convoy from: ")
                        convoy_to = input("Enter territory to convoy to: ")
                        if convoy_from in self.territories and convoy_to in self.territories:
                            if self.is_valid_convoy(territory, self.territories[convoy_from], self.territories[convoy_to]):
                                self.orders.append(Order(territory.unit, 'convoy', territory, self.territories[convoy_from], self.territories[convoy_to]))
                                break
                    elif order_type == 'hold':
                        self.orders.append(Order(territory.unit, 'hold', territory))
                        break
                    print("Invalid order. Please try again.")

    def resolve_orders(self):
        print(f"Starting to resolve {len(self.orders)} orders.")
        move_orders = [order for order in self.orders if order.type == 'move']
        
        print(f"Move orders: {len(move_orders)}")

        # Calculate initial strengths
        strengths = {t: 1 if t.unit else 0 for t in self.territories.values()}

        # Add strength for moving units
        for move in move_orders:
            strengths[move.target] += 1

        # Resolve moves
        successful_moves = []
        for move in move_orders:
            print(f"Evaluating move: {move.source.name} to {move.target.name}")
            # Check for head-to-head battles
            opposite_move = next((m for m in move_orders if m.target == move.source and m.source == move.target), None)
            if opposite_move:
                if strengths[move.target] > strengths[move.source]:
                    successful_moves.append(move)
                    print(f"Successful head-to-head move: {move.source.name} to {move.target.name}")
                else:
                    print(f"Failed head-to-head move: {move.source.name} to {move.target.name}")
                continue

            # Check if move is successful
            if move.target.unit is None or strengths[move.target] <= strengths[move.source]:
                successful_moves.append(move)
                print(f"Successful move: {move.source.name} to {move.target.name}")
            else:
                print(f"Failed move: {move.source.name} to {move.target.name}")

        # Execute successful moves and identify dislodged units
        self.dislodged_units = {}
        for move in successful_moves:
            if move.target.unit:
                self.dislodged_units[move.target] = move.target.unit
            
            # Update the source and target territories
            source_owner = move.source.owner
            target_owner = move.target.owner

            if source_owner:
                self.players[source_owner]["territories"].remove(move.source)
                self.players[source_owner]["units"].remove(move.source.unit)

            if target_owner and target_owner != source_owner:
                self.players[target_owner]["territories"].remove(move.target)
                if move.target.unit in self.players[target_owner]["units"]:
                    self.players[target_owner]["units"].remove(move.target.unit)

            # Update the source owner's territories and units
            if source_owner:
                self.players[source_owner]["territories"].append(move.target)
                self.players[source_owner]["units"].append(move.source.unit)

            # Update the units in territories
            move.target.unit = move.source.unit
            move.source.unit = None
            move.target.owner = source_owner

            # Update supply centers
            if move.target.is_supply_center and source_owner:
                if move.target not in self.players[source_owner]["supply_centers"]:
                    self.players[source_owner]["supply_centers"].append(move.target)
                if target_owner and move.target in self.players[target_owner]["supply_centers"]:
                    self.players[target_owner]["supply_centers"].remove(move.target)

        print(f"Resolved {len(successful_moves)} successful moves.")
        print(f"Dislodged units: {len(self.dislodged_units)}")

        # Update game state
        self.update_game_state()

    def resolve_turn(self):
        print(f"Starting to resolve {len(self.orders)} orders.")
        move_orders = []
        support_orders = []
        hold_orders = []
        convoy_orders = []
        
        for player, orders in self.orders.items():
            for order in orders:
                if order[1] == 'move':
                    move_orders.append((player, order))
                elif order[1] == 'support':
                    support_orders.append((player, order))
                elif order[1] == 'hold':
                    hold_orders.append((player, order))
                elif order[1] == 'convoy':
                    convoy_orders.append((player, order))

        # Process support orders
        support_strength = self.process_support_orders(support_orders)

        # Process convoy orders (placeholder for future implementation)
        self.process_convoy_orders(convoy_orders)

        # Calculate initial strengths
        strengths = {t.name: 1 if t.unit else 0 for t in self.territories.values()}

        # Add strength for moving units and their supports
        for _, order in move_orders:
            source, _, target = order
            strengths[target] += 1 + support_strength.get(source, 0)

        # Resolve moves
        successful_moves = []
        for player, order in move_orders:
            source, _, target = order
            if target not in self.territories:
                print(f"Invalid move: {source} to {target}")
                continue
            
            # Check for head-to-head battles
            opposite_move = next((m for m in move_orders if m[1][2] == source and m[1][0] == target), None)
            if opposite_move:
                if strengths[target] > strengths[source]:
                    successful_moves.append((player, order))
                    print(f"Successful head-to-head move: {source} to {target}")
                else:
                    print(f"Failed head-to-head move: {source} to {target}")
                continue

            # Check if move is successful
            if self.territories[target].unit is None or strengths[target] <= strengths[source]:
                successful_moves.append((player, order))
                print(f"Successful move: {source} to {target}")
            else:
                print(f"Failed move: {source} to {target}")

        # Execute successful moves and identify dislodged units
        self.dislodged_units = {}
        for player, order in successful_moves:
            source, _, target = order
            if self.territories[target].unit:
                self.dislodged_units[target] = self.territories[target].unit
            
            # Update the source and target territories
            self.territories[target].unit = self.territories[source].unit
            self.territories[source].unit = None
            self.territories[target].owner = player

            # Update supply centers
            if self.territories[target].is_supply_center:
                if player not in self.players:
                    self.players[player] = {"supply_centers": [], "units": []}
                if target not in self.players[player]["supply_centers"]:
                    self.players[player]["supply_centers"].append(target)
                if self.territories[target].owner and self.territories[target].owner != player:
                    self.players[self.territories[target].owner]["supply_centers"].remove(target)

        # Process hold orders
        self.process_hold_orders(hold_orders)

        # Update game state
        self.update_game_state()

        print(f"Resolved {len(successful_moves)} successful moves.")
        print(f"Dislodged units: {len(self.dislodged_units)}")

    def process_support_orders(self, support_orders):
        support_strength = {}
        for player, order in support_orders:
            _, _, source, target = order
            if source not in support_strength:
                support_strength[source] = 0
            support_strength[source] += 1
        return support_strength
    
    def process_convoy_orders(self, convoy_orders):
        # Placeholder for future implementation
        pass

    def process_hold_orders(self, hold_orders):
        for player, order in hold_orders:
            territory, _ = order
            if territory in self.territories:
                self.territories[territory].owner = player

    def negotiation_phase(self):
        print(f"\n--- {self.year} {self.season} Negotiation Phase ---")
        skip_negotiation = input("Skip negotiation phase? (y/n): ").lower() == 'y'
        if skip_negotiation:
            print("Skipping negotiation phase.")
            return {}
        negotiations = {}
        
        for player in self.players:
            negotiations[player.name] = {}
            for other_player in self.players:
                if player != other_player:
                    negotiations[player.name][other_player.name] = []

        while True:
            initiator = input("Enter the name of the player initiating communication (or 'done' to end phase): ")
            if initiator.lower() == 'done':
                break
            
            if initiator not in [p.name for p in self.players]:
                print("Invalid player name. Please try again.")
                continue
            
            recipient = input("Enter the name of the player receiving communication: ")
            if recipient not in [p.name for p in self.players] or recipient == initiator:
                print("Invalid recipient. Please try again.")
                continue
            
            message = input("Enter the message: ")
            negotiations[initiator][recipient].append(message)
            
            # Option for immediate response
            if input("Immediate response? (y/n): ").lower() == 'y':
                response = input(f"Enter {recipient}'s response: ")
                negotiations[recipient][initiator].append(response)

        # Display negotiation summary
        print("\nNegotiation Summary:")
        for player1 in negotiations:
            for player2, messages in negotiations[player1].items():
                if messages:
                    print(f"\n{player1} to {player2}:")
                    for message in messages:
                        print(f"- {message}")

        return negotiations

    def adjust_units(self, player):
        supply_centers = len(player.supply_centers)
        units = len(player.units)
        
        if supply_centers > units:
            self.build_units(player, supply_centers - units)
        elif units > supply_centers:
            self.remove_units(player, units - supply_centers)

    def build_units(self, player, count):
        print(f"{player.name} can build {count} unit(s)")
        for _ in range(count):
            while True:
                territory_name = input(f"Enter home supply center to build in for {player.name}: ")
                if territory_name in self.territories and self.territories[territory_name].owner == player and \
                self.territories[territory_name].is_supply_center and not self.territories[territory_name].unit:
                    unit_type = input("Enter unit type (army/fleet): ").lower()
                    if unit_type in ['army', 'fleet'] and self.territories[territory_name].can_host(unit_type):
                        new_unit = Unit(unit_type)
                        self.territories[territory_name].unit = new_unit
                        player.units.append(new_unit)
                        print(f"Built a {unit_type} in {territory_name}")
                        break
                print("Invalid build. Please try again.")

    def remove_units(self, player, count):
        print(f"{player.name} must remove {count} unit(s)")
        for _ in range(count):
            while True:
                territory_name = input(f"Enter territory to remove unit from for {player.name}: ")
                if territory_name in self.territories and self.territories[territory_name].owner == player and \
                self.territories[territory_name].unit:
                    removed_unit = self.territories[territory_name].unit
                    self.territories[territory_name].unit = None
                    player.units.remove(removed_unit)
                    print(f"Removed {removed_unit.type} from {territory_name}")
                    break
                print("Invalid removal. Please try again.")
                

    def display_status(self, player):
            print(f"Territories owned by {player.name}:")
            for territory in player.territories:
                unit_type = territory.unit.type if territory.unit else "No unit"
                print(f"- {territory.name}: {unit_type}")
            print(f"Supply centers: {len(player.supply_centers)}")


    



    
    def is_valid_support(self, source, support_from, support_to):
        if source.unit.type != 'fleet' and (support_from.type == 'sea' or (support_to and support_to.type == 'sea')):
            return False
        return support_from in source.adjacent and (support_to is None or support_to in support_from.adjacent)

    def is_valid_convoy(self, source, convoy_from, convoy_to):
        return source.unit.type == 'fleet' and source.type == 'sea' and convoy_from.type != 'sea' and convoy_to.type != 'sea'

    def is_valid_move(self, source, target, unit_type):
        if unit_type == 'army':
            return target in source.adjacent and target.can_host('army')
        elif unit_type == 'fleet':
            return target in source.adjacent and target.can_host('fleet')
        return False
    
    def retreat_and_disband(self):
        if not self.dislodged_units:
            return

        print("\n--- Retreat Phase ---")
        for territory, unit in self.dislodged_units.items():
            owner = territory.owner
            if owner is None:
                print(f"Warning: No owner found for dislodged unit in {territory.name}")
                continue

            print(f"{owner}'s {unit.type} in {territory.name} must retreat.")
            
            retreat_options = [adj for adj in territory.adjacent 
                            if adj.unit is None and 
                            adj not in self.dislodged_units and
                            adj.can_host(unit.type)]
            
            if not retreat_options:
                print(f"No valid retreat options. The unit is disbanded.")
                if unit in self.players[owner]["units"]:
                    self.players[owner]["units"].remove(unit)
                continue

            while True:
                print("Retreat options:", ", ".join(t.name for t in retreat_options))
                choice = input(f"Enter retreat location for {owner}'s {unit.type} in {territory.name} or 'disband': ")
                
                if choice.lower() == 'disband':
                    if unit in self.players[owner]["units"]:
                        self.players[owner]["units"].remove(unit)
                    break
                elif choice in [t.name for t in retreat_options]:
                    retreat_to = next(t for t in retreat_options if t.name == choice)
                    retreat_to.unit = unit
                    retreat_to.owner = owner
                    self.players[owner]["territories"].append(retreat_to)
                    if unit in self.players[owner]["units"]:
                        self.players[owner]["units"].remove(unit)
                    self.players[owner]["units"].append(retreat_to.unit)
                    break
                else:
                    print("Invalid choice. Please try again.")

        self.dislodged_units.clear()

    

    def update_game_state(self):
        for player in self.players:
            self.players[player]["territories"] = [t.name for t in self.territories.values() if t.owner == player]
            self.players[player]["units"] = [t.name for t in self.territories.values() if t.owner == player and t.unit]

        # Update season and year
        if self.season == 'Fall':
            self.season = 'Spring'
            self.year += 1
        else:
            self.season = 'Fall'


    def generate_game_state_json(self):
        return json.dumps({
            "Y": self.year,
            "S": self.season[0],  # Just the first letter of the season
            "P": {name: len(data["supply_centers"]) for name, data in self.players.items()},
            "U": {t.name: f"{t.unit.type[0].upper()}{t.owner[0:3].upper()}" 
                for t in self.territories.values() if t.unit},
            "SC": {t.name: t.owner[0:3].upper() 
                for t in self.territories.values() if t.is_supply_center and t.owner}
        })

    def display_game_state_json(self):
        print(self.generate_game_state_json())

    def check_convoy_path(self, start, end, target):
        # Implement a pathfinding algorithm (e.g., BFS) to check if there's a valid convoy path
        # This is a simplified version and may need to be expanded for a full implementation
        visited = set()
        queue = [(start, [])]
        while queue:
            current, path = queue.pop(0)
            if current == end:
                return True
            for adj in current.adjacent:
                if adj.type == 'sea' and adj not in visited:
                    visited.add(adj)
                    queue.append((adj, path + [adj]))
        return False

    def check_victory(self):
        supply_center_count = sum(len(player_data["supply_centers"]) for player_data in self.players.values())
        for player_name, player_data in self.players.items():
            if len(player_data["supply_centers"]) > supply_center_count // 2:
                return player_name
        return None
    
    def end_game(self):
        self.is_active = False
    

    def load_test_orders(self, test_orders):
        self.orders = []
        for player_name, player_orders in test_orders.items():
            try:
                player = next(p for p in self.players if p.name == player_name)
            except StopIteration:
                print(f"Warning: Player {player_name} not found in game.")
                continue
            
            for unit_location, order_type, *order_details in player_orders:
                try:
                    unit = next(t.unit for t in player.territories if t.name == unit_location)
                    source = next(t for t in player.territories if t.name == unit_location)
                except StopIteration:
                    print(f"Warning: Unit or territory {unit_location} not found for {player_name}.")
                    continue
                
                try:
                    if order_type == 'move':
                        target = self.territories[order_details[0]]
                        self.orders.append(Order(unit, 'move', source, target))
                    elif order_type == 'support':
                        support_from = self.territories[order_details[0]]
                        support_to = self.territories[order_details[1]] if len(order_details) > 1 else None
                        self.orders.append(Order(unit, 'support', source, support_from, support_to))
                    elif order_type == 'convoy':
                        convoy_from = self.territories[order_details[0]]
                        convoy_to = self.territories[order_details[1]]
                        self.orders.append(Order(unit, 'convoy', source, convoy_from, convoy_to))
                    elif order_type == 'hold':
                        self.orders.append(Order(unit, 'hold', source))
                    else:
                        print(f"Warning: Unknown order type {order_type} for {player_name} in {unit_location}.")
                except KeyError as e:
                    print(f"Warning: Territory {e} not found in map data.")
                except IndexError:
                    print(f"Warning: Insufficient order details for {player_name} in {unit_location}.")
        
        print(f"Loaded {len(self.orders)} test orders.")

    def display_game_summary(self):
        print("\n=== Game Summary ===")
        print(f"Year: {self.year}, Season: {self.season}")
        for player in self.players:
            print(f"\n{player.name}:")
            print(f"  Supply Centers: {len(player.supply_centers)}")
            print(f"  Units: {len(player.units)}")
            print("  Territories:")
            for territory in player.territories:
                unit_type = territory.unit.type if territory.unit else "No unit"
                print(f"    - {territory.name}: {unit_type}")
        
        print("\nUnowned Supply Centers:")
        unowned_sc = [t.name for t in self.territories.values() if t.is_supply_center and not t.owner]
        print(", ".join(unowned_sc) if unowned_sc else "None")


test_opening_moves = {
    'England': [
        ('London', 'move', 'North Sea'),
        ('Edinburgh', 'move', 'Norwegian Sea'),
        ('Liverpool', 'move', 'Yorkshire')
    ],
    'France': [
        ('Brest', 'move', 'English Channel'),
        ('Paris', 'move', 'Burgundy'),
        ('Marseilles', 'move', 'Spain')
    ],
    'Germany': [
        ('Kiel', 'move', 'Denmark'),
        ('Berlin', 'move', 'Kiel'),
        ('Munich', 'move', 'Ruhr')
    ],
    'Italy': [
        ('Venice', 'move', 'Tyrolia'),
        ('Rome', 'move', 'Venice'),
        ('Naples', 'move', 'Ionian Sea')
    ],
    'Austria': [
        ('Vienna', 'move', 'Galicia'),
        ('Budapest', 'move', 'Serbia'),
        ('Trieste', 'move', 'Adriatic Sea')
    ],
    'Russia': [
        ('St Petersburg', 'move', 'Gulf of Bothnia'),
        ('Moscow', 'move', 'Ukraine'),
        ('Warsaw', 'move', 'Galicia'),
        ('Sevastopol', 'move', 'Black Sea')
    ],
    'Turkey': [
        ('Constantinople', 'move', 'Bulgaria'),
        ('Ankara', 'move', 'Armenia'),
        ('Smyrna', 'move', 'Aegean Sea')
    ]
}



    # Main game loop
if __name__ == "__main__":
    print("Starting the game...")
    game = Game()
    max_years = 10

    for year in range(game.year, game.year + max_years):
        print(f"\n=== Year {year} ===")
        
        print("\n--- Spring ---")
        game.season = 'Spring'
        game.play_turn(test_opening_moves if year == 1901 else None)
        game.retreat_and_disband()
        game.display_game_summary()
        
        print("\n--- Fall ---")
        game.season = 'Fall'
        game.play_turn()
        game.retreat_and_disband()
        game.display_game_summary()
        
        print("\n--- Winter ---")
        game.winter_adjustments()
        game.display_game_summary()
        
        # Check for victory
        winner = game.check_victory()
        if winner:
            print(f"\n{winner.name} has won the game!")
            break
    else:
        print("\nGame ended without a clear winner after 10 years.")

    print("Game ended.")


## python "/Users/Shared/Documents/gpt pilot/gpt-pilot/workspace/LLM_dimplomacy/diplomacy_base.py"