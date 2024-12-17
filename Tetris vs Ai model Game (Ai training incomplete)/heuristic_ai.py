# heuristic_ai.py

import json
import logging
from ga import valid_move, rotate_shape, add_to_grid, clear_lines, get_column_height, count_gaps, calculate_bumpiness

class HeuristicAIPlayer:
    def __init__(self, weights, initial_game_state):
        self.weights = weights  # Dictionary of heuristic weights
        self.game_state = json.loads(initial_game_state)
        self.logger = logging.getLogger('heuristic_ai')
        self.logger.setLevel(logging.DEBUG)
    
    def evaluate_move(self, move):
        # Clone the game state to simulate the move
        simulated_state = json.loads(json.dumps(self.game_state))
        piece = simulated_state['current_piece']
        grid = simulated_state['grid']
        
        # Apply the move
        if move == "left" and valid_move(piece, piece['x'] - 1, piece['y'], grid):
            piece['x'] -= 1
        elif move == "right" and valid_move(piece, piece['x'] + 1, piece['y'], grid):
            piece['x'] += 1
        elif move == "rotate":
            new_shape = rotate_shape(piece['shape'])
            if valid_move({'shape': new_shape, 'x': piece['x'], 'y': piece['y'], 'color': piece['color']}, piece['x'], piece['y'], grid):
                piece['shape'] = new_shape
        elif move == "drop":
            while valid_move(piece, piece['x'], piece['y'] + 1, grid):
                piece['y'] += 1
            add_to_grid(piece, grid)
            lines_cleared, simulated_state['lines_cleared'], simulated_state['score'], simulated_state['fall_speed'] = clear_lines(
                grid,
                simulated_state['lines_cleared'],
                simulated_state['score'],
                simulated_state['fall_speed']
            )
        
        # Calculate metrics
        aggregate_height = sum(get_column_height(grid, x) for x in range(10))
        gaps = count_gaps(grid)
        bumpiness = calculate_bumpiness(grid)
        lines_cleared = simulated_state['lines_cleared']
        score = simulated_state['score']
        
        # Calculate weighted score
        weighted_score = (
            self.weights.get("score", 0) * score +
            self.weights.get("lines", 0) * lines_cleared +
            self.weights.get("aggregate_height", 0) * aggregate_height +
            self.weights.get("gaps", 0) * gaps +
            self.weights.get("bumpiness", 0) * bumpiness
        )
        
        return weighted_score, simulated_state
    
    def choose_best_move(self):
        possible_moves = ["left", "right", "rotate", "drop"]
        best_move = None
        best_score = -float('inf')
        best_state = None
        
        for move in possible_moves:
            score, simulated_state = self.evaluate_move(move)
            self.logger.debug(f"Move: {move}, Score: {score}")
            if score > best_score:
                best_score = score
                best_move = move
                best_state = simulated_state
        
        # Apply the best move to the actual game state
        if best_move:
            self.logger.debug(f"Chosen Move: {best_move}, Score: {best_score}")
            self.apply_move(best_move, best_state)
        
        return best_move
    
    def apply_move(self, move, new_state):
        self.game_state = new_state
    
    def get_game_state(self):
        return json.dumps(self.game_state)
