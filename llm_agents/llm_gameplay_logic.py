from game_utils import ADJACENCY, SEA_TERRITORIES, COASTAL_TERRITORIES, get_adjacent_territories


class LLMGameplayLogic:
    @staticmethod
    def analyze_game_state(game_state):
        if isinstance(game_state, str):
            game_state = json.loads(game_state)
        
        supply_centers = game_state['SC']
        units = game_state['U']
        player_scores = game_state['P']
        
        return {
            'supply_centers': supply_centers,
            'units': units,
            'player_scores': player_scores,
            'year': game_state['Y'],
            'season': game_state['S']
        }

    @staticmethod
    def generate_possible_moves(game_state, country):
        possible_moves = []
        units = game_state['U']
        for territory, unit in units.items():
            if unit.endswith(country[:3].upper()):
                unit_type = unit[0]  # 'A' for Army, 'F' for Fleet
                adjacent_territories = ADJACENCY[territory]
                for adj in adjacent_territories:
                    if LLMGameplayLogic.is_valid_move(territory, adj, unit_type):
                        possible_moves.append((territory, 'move', adj))
                possible_moves.append((territory, 'hold'))
                # Add support and convoy options
        return possible_moves

    @staticmethod
    def is_valid_move(source, target, unit_type):
        if target not in ADJACENCY[source]:
            return False

        if unit_type == 'A':
            return target not in SEA_TERRITORIES
        elif unit_type == 'F':
            if source in COASTAL_TERRITORIES and target in COASTAL_TERRITORIES:
                return True
            return source in SEA_TERRITORIES or target in SEA_TERRITORIES
        
        return False

    @staticmethod
    def format_prompt(analyzed_state, country, possible_moves):
        prompt = f"""
        Current game state:
        Year: {analyzed_state['year']}, Season: {analyzed_state['season']}
        Your country: {country}
        Your supply centers: {', '.join(k for k, v in analyzed_state['supply_centers'].items() if v == country[:3].upper())}
        Your units: {', '.join(f"{k}: {v}" for k, v in analyzed_state['units'].items() if v.endswith(country[:3].upper()))}
        Player scores: {analyzed_state['player_scores']}

        Possible moves:
        {', '.join(str(move) for move in possible_moves)}

        Based on this information, what orders should you give to your units? Consider your strategic position, potential alliances, and the actions of other players. Provide your orders in the format:
        (Territory, Action, Target) for each unit, e.g., (London, move, North Sea)
        """
        return prompt
    
    @staticmethod
    def parse_orders(raw_orders, country):
        parsed_orders = []
        for line in raw_orders.split('\n'):
            if '(' in line and ')' in line:
                order = line[line.index('(')+1:line.index(')')].split(',')
                if len(order) >= 2:
                    territory = order[0].strip()
                    action = order[1].strip().lower()
                    target = order[2].strip() if len(order) > 2 else None
                    if LLMGameplayLogic.is_valid_order(territory, action, target, country):
                        parsed_orders.append((territory, action, target))
        return parsed_orders

    @staticmethod
    def is_valid_order(territory, action, target, country, game_state):
        if territory not in game_state['U'] or not game_state['U'][territory].endswith(country[:3].upper()):
            return False

        unit_type = game_state['U'][territory][0]  # 'A' for Army, 'F' for Fleet

        if action == 'hold':
            return True
        elif action == 'move':
            return LLMGameplayLogic.is_valid_move(territory, target, unit_type)
        elif action in ['support', 'convoy']:
            # Check if the supporting/convoying unit is adjacent to the target
            return target in ADJACENCY[territory]
        else:
            return False