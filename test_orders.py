import random
import logging
from game_utils import get_adjacent_territories, ADJACENCY, INITIAL_POSITIONS, SEA_TERRITORIES, COASTAL_TERRITORIES


# This is a placeholder. Replace this with your complete adjacency list.


def generate_random_move(territory, unit_type, get_adjacent_territories_func):
    possible_targets = [t for t in get_adjacent_territories_func(territory) if is_valid_move(territory, t, unit_type, get_adjacent_territories_func)]
    
    if possible_targets:
        target = random.choice(possible_targets)
        return (territory, 'move', target)
    else:
        return (territory, 'hold')

def is_valid_move(source, target, unit_type, get_adjacent_territories_func):
    if target not in get_adjacent_territories_func(source):
        return False
    if unit_type == 'A':
        return target not in SEA_TERRITORIES
    elif unit_type == 'F':
        if source in COASTAL_TERRITORIES and target in COASTAL_TERRITORIES:
            return True
        if source in SEA_TERRITORIES or target in SEA_TERRITORIES:
            return True
    return False

def generate_country_orders(units, controlled_territories):
    orders = []
    for source, unit_type in units.items():
        if random.random() < 0.2:  # 20% chance to hold
            orders.append((source, 'hold'))
        else:
            move = generate_random_move({source: unit_type}, controlled_territories)
            orders.append(move)
    return orders


def find_possible_convoy_routes(sea_territory, get_adjacent_territories):
    adjacent_coasts = [t for t in get_adjacent_territories(sea_territory) if t in COASTAL_TERRITORIES]
    possible_routes = []
    for source in adjacent_coasts:
        for target in adjacent_coasts:
            if source != target:
                possible_routes.append((source, target))
    return possible_routes

def get_orders(country, units, controlled_territories, get_adjacent_territories_func):
    orders = []
    logging.info(f"Generating orders for {country}")
    for territory, unit_type in units.items():
        if random.random() < 0.1:  # 10% chance to hold
            orders.append((territory, 'hold'))
            logging.info(f"Generated hold order for {territory}")
        elif unit_type == 'F' and territory in SEA_TERRITORIES and random.random() < 0.3:  # 30% chance for fleets in sea to convoy
            possible_convoy_routes = find_possible_convoy_routes(territory, get_adjacent_territories_func)
            if possible_convoy_routes:
                convoy_from, convoy_to = random.choice(possible_convoy_routes)
                orders.append((territory, 'convoy', convoy_from, convoy_to))
                logging.info(f"Generated convoy order for {territory}: {convoy_from} to {convoy_to}")
        else:
            move = generate_random_move(territory, unit_type, get_adjacent_territories_func)
            orders.append(move)
            logging.info(f"Generated move order for {territory}: {move}")
    
    # Generate support orders for units
    for territory, unit_type in units.items():
        if random.random() < 0.3:  # 30% chance to support
            adjacent_territories = get_adjacent_territories_func(territory)
            possible_support_targets = [t for t in adjacent_territories if t in controlled_territories]
            if possible_support_targets:
                support_target = random.choice(possible_support_targets)
                orders.append((territory, 'support', support_target))
                logging.info(f"Generated support order for {territory}: supporting {support_target}")
    
    logging.info(f"Final orders for {country}: {orders}")
    return orders

def find_possible_convoy_routes(sea_territory, get_adjacent_territories_func):
    adjacent_coasts = [t for t in get_adjacent_territories_func(sea_territory) if t in COASTAL_TERRITORIES]
    possible_routes = []
    for source in adjacent_coasts:
        for target in adjacent_coasts:
            if source != target:
                possible_routes.append((source, target))
    return possible_routes
    
# Example usage
if __name__ == "__main__":
    test_units = {'London': 'F', 'Edinburgh': 'F', 'Liverpool': 'A'}
    test_territories = {'London', 'Edinburgh', 'Liverpool', 'Yorkshire'}
    print(f"Test orders:")
    print(get_orders('England', test_units, test_territories))



# test_orders = {
#     'England': [
#         # Turn 1
#         [('London', 'move', 'North Sea'), ('Edinburgh', 'move', 'Norwegian Sea'), ('Liverpool', 'move', 'Yorkshire')],
#         # Turn 2
#         [('North Sea', 'move', 'Norway'), ('Norwegian Sea', 'support', 'North Sea', 'Norway'), ('Yorkshire', 'move', 'London')],
#         # Turn 3
#         [('Norway', 'hold'), ('Norwegian Sea', 'move', 'Barents Sea'), ('London', 'move', 'Wales')],
#         # Turn 4
#         [('Norway', 'move', 'St Petersburg'), ('Barents Sea', 'support', 'Norway', 'St Petersburg'), ('Wales', 'move', 'Brest')],
#         # Turn 5
#         [('St Petersburg', 'hold'), ('Barents Sea', 'move', 'Norway'), ('Brest', 'hold')]
#     ],
#     'France': [
#         # Turn 1
#         [('Paris', 'move', 'Burgundy'), ('Marseilles', 'move', 'Spain'), ('Brest', 'move', 'Mid-Atlantic Ocean')],
#         # Turn 2
#         [('Burgundy', 'move', 'Munich'), ('Spain', 'hold'), ('Mid-Atlantic Ocean', 'move', 'North Africa')],
#         # Turn 3
#         [('Munich', 'hold'), ('Spain', 'move', 'Portugal'), ('North Africa', 'move', 'Tunis')],
#         # Turn 4
#         [('Munich', 'move', 'Ruhr'), ('Portugal', 'move', 'Spain'), ('Tunis', 'hold')],
#         # Turn 5
#         [('Ruhr', 'move', 'Holland'), ('Spain', 'move', 'Marseilles'), ('Tunis', 'move', 'Ionian Sea')]
#     ],
#     'Germany': [
#         # Turn 1
#         [('Berlin', 'move', 'Kiel'), ('Munich', 'move', 'Ruhr'), ('Kiel', 'move', 'Denmark')],
#         # Turn 2
#         [('Kiel', 'move', 'Holland'), ('Ruhr', 'move', 'Belgium'), ('Denmark', 'support', 'Kiel', 'Holland')],
#         # Turn 3
#         [('Holland', 'hold'), ('Belgium', 'hold'), ('Denmark', 'move', 'Sweden')],
#         # Turn 4
#         [('Holland', 'move', 'North Sea'), ('Belgium', 'move', 'Picardy'), ('Sweden', 'move', 'Norway')],
#         # Turn 5
#         [('North Sea', 'move', 'Edinburgh'), ('Picardy', 'move', 'Paris'), ('Norway', 'hold')]
#     ],
#     'Italy': [
#         # Turn 1
#         [('Venice', 'move', 'Tyrolia'), ('Rome', 'move', 'Venice'), ('Naples', 'move', 'Ionian Sea')],
#         # Turn 2
#         [('Tyrolia', 'move', 'Munich'), ('Venice', 'move', 'Trieste'), ('Ionian Sea', 'move', 'Tunis')],
#         # Turn 3
#         [('Munich', 'hold'), ('Trieste', 'move', 'Serbia'), ('Tunis', 'move', 'North Africa')],
#         # Turn 4
#         [('Munich', 'move', 'Bohemia'), ('Serbia', 'move', 'Budapest'), ('North Africa', 'move', 'Mid-Atlantic Ocean')],
#         # Turn 5
#         [('Bohemia', 'move', 'Vienna'), ('Budapest', 'hold'), ('Mid-Atlantic Ocean', 'move', 'Western Mediterranean')]
#     ],
#     'Austria': [
#         # Turn 1
#         [('Vienna', 'move', 'Galicia'), ('Budapest', 'move', 'Serbia'), ('Trieste', 'move', 'Albania')],
#         # Turn 2
#         [('Galicia', 'move', 'Warsaw'), ('Serbia', 'move', 'Greece'), ('Albania', 'support', 'Serbia', 'Greece')],
#         # Turn 3
#         [('Warsaw', 'hold'), ('Greece', 'move', 'Bulgaria'), ('Albania', 'move', 'Serbia')],
#         # Turn 4
#         [('Warsaw', 'move', 'Ukraine'), ('Bulgaria', 'support', 'Serbia', 'Rumania'), ('Serbia', 'move', 'Rumania')],
#         # Turn 5
#         [('Ukraine', 'move', 'Sevastopol'), ('Bulgaria', 'move', 'Constantinople'), ('Rumania', 'hold')]
#     ],
#     'Russia': [
#         # Turn 1
#         [('St Petersburg', 'move', 'Gulf of Bothnia'), ('Moscow', 'move', 'Ukraine'), ('Warsaw', 'move', 'Galicia'), ('Sevastopol', 'move', 'Black Sea')],
#         # Turn 2
#         [('Gulf of Bothnia', 'move', 'Sweden'), ('Ukraine', 'move', 'Rumania'), ('Galicia', 'hold'), ('Black Sea', 'support', 'Ukraine', 'Rumania')],
#         # Turn 3
#         [('Sweden', 'move', 'Norway'), ('Rumania', 'hold'), ('Galicia', 'move', 'Vienna'), ('Black Sea', 'move', 'Bulgaria')],
#         # Turn 4
#         [('Norway', 'move', 'St Petersburg'), ('Rumania', 'support', 'Black Sea', 'Bulgaria'), ('Vienna', 'move', 'Trieste'), ('Bulgaria', 'hold')],
#         # Turn 5
#         [('St Petersburg', 'hold'), ('Rumania', 'move', 'Budapest'), ('Trieste', 'move', 'Venice'), ('Bulgaria', 'move', 'Greece')]
#     ],
#     'Turkey': [
#         # Turn 1
#         [('Constantinople', 'move', 'Bulgaria'), ('Ankara', 'move', 'Black Sea'), ('Smyrna', 'move', 'Constantinople')],
#         # Turn 2
#         [('Bulgaria', 'move', 'Greece'), ('Black Sea', 'move', 'Rumania'), ('Constantinople', 'support', 'Bulgaria', 'Greece')],
#         # Turn 3
#         [('Greece', 'hold'), ('Rumania', 'support', 'Greece'), ('Constantinople', 'move', 'Bulgaria')],
#         # Turn 4
#         [('Greece', 'move', 'Serbia'), ('Rumania', 'move', 'Ukraine'), ('Bulgaria', 'support', 'Greece', 'Serbia')],
#         # Turn 5
#         [('Serbia', 'move', 'Trieste'), ('Ukraine', 'move', 'Moscow'), ('Bulgaria', 'move', 'Rumania')]
#     ]
# }

# def get_orders(country, turn):
#     print(f"Checking country: {country}, turn: {turn}")
#     if country in test_orders:
#         print(f"{country} found in test_orders")
#         if 0 <= turn - 1 < len(test_orders[country]):
#             print(f"Turn {turn} is valid")
#             return test_orders[country][turn - 1]
#         else:
#             print(f"Turn {turn} is invalid")
#     else:
#         print(f"{country} not found in test_orders")
#     return []