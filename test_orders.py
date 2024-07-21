import random

# This is a placeholder. Replace this with your complete adjacency list.
ADJACENCY = {
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

# Initial positions of units for each country
INITIAL_POSITIONS = {
    'England': {'London': 'fleet', 'Edinburgh': 'fleet', 'Liverpool': 'army'},
    'France': {'Paris': 'army', 'Marseilles': 'army', 'Brest': 'fleet'},
    'Germany': {'Berlin': 'army', 'Kiel': 'fleet', 'Munich': 'army'},
    'Italy': {'Rome': 'army', 'Venice': 'army', 'Naples': 'fleet'},
    'Austria': {'Vienna': 'army', 'Budapest': 'army', 'Trieste': 'fleet'},
    'Russia': {'Moscow': 'army', 'Sevastopol': 'fleet', 'St Petersburg': 'fleet', 'Warsaw': 'army'},
    'Turkey': {'Constantinople': 'army', 'Ankara': 'army', 'Smyrna': 'fleet'}
}

def is_valid_move(unit_type, source, target):
    if source not in ADJACENCY or target not in ADJACENCY[source]:
        return False
    if unit_type == 'army':
        return target not in ['North Atlantic Ocean', 'Norwegian Sea', 'North Sea', 'Baltic Sea', 'Adriatic Sea', 'Ionian Sea', 'Tyrrhenian Sea', 'Western Mediterranean', 'Mid-Atlantic Ocean']
    return True  # For simplicity, assume all fleet moves are valid if adjacent

def generate_random_move(country, units):
    unit_positions = list(units.keys())
    source = random.choice(unit_positions)
    unit_type = units[source]
    
    possible_targets = [t for t in ADJACENCY.get(source, []) if is_valid_move(unit_type, source, t)]
    
    if possible_targets:
        target = random.choice(possible_targets)
        return (source, 'move', target)
    else:
        return (source, 'hold')

def generate_country_orders(country, units):
    orders = []
    for _ in range(len(units)):
        move = generate_random_move(country, units)
        orders.append(move)
        if move[1] == 'move':
            units[move[2]] = units.pop(move[0])
    return orders

def get_orders(country, turn):
    units = INITIAL_POSITIONS[country].copy()
    return generate_country_orders(country, units)

# Example usage
if __name__ == "__main__":
    for country in INITIAL_POSITIONS.keys():
        print(f"{country} orders for turn 1:")
        print(get_orders(country, 1))
        print()




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