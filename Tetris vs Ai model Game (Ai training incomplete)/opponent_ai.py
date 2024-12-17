# opponent_ai.py

from ga import valid_move, rotate_shape, add_to_grid, clear_lines, get_column_height, count_gaps, calculate_bumpiness
# opponent_ai.py

import json
TETROMINO_TYPES = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']
TETROMINOES = ['I', 'O', 'T', 'S', 'Z', 'J', 'L']

for tetromino in TETROMINOES:
   
    def load_best_move_sequence(filename = f"best_move_sequence.json"):
        try:
            with open(filename, "r") as f:
                move_sequence = json.load(f)
            return move_sequence
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return []
        except json.JSONDecodeError:
            print(f"File {filename} is not a valid JSON.")
            return []

# Example usage
best_move_sequence = load_best_move_sequence()
print("Loaded Move Sequence:", best_move_sequence)


# opponent_ai.py

import json
import logging

class OpponentAIPlayer:
    def __init__(self):
        self.current_move_sequence = []
        self.current_move_index = 0
        self.logger = logging.getLogger('opponent_ai')
        self.logger.setLevel(logging.DEBUG)
    
    def load_move_sequence(self, piece_type):
        file_path = f"best_move_sequence_{piece_type}_gen_14.json"
        try:
            with open(file_path, "r") as f:
                self.current_move_sequence = json.load(f)
            self.current_move_index = 0
            self.logger.info(f"Loaded move sequence for piece {piece_type} from {file_path}")
        except FileNotFoundError:
            self.logger.error(f"Move sequence file {file_path} not found.")
            self.current_move_sequence = []
        except json.JSONDecodeError:
            self.logger.error(f"Move sequence file {file_path} is not a valid JSON.")
            self.current_move_sequence = []
    
    def execute_next_move(self, game_state):
        if self.current_move_index >= len(self.current_move_sequence):
            self.logger.info("No more moves left in the sequence.")
            return  # Optionally, generate a new move sequence or handle as needed
        
        move = self.current_move_sequence[self.current_move_index]
        self.logger.debug(f"Executing move: {move}")
        
        # Apply the move to the game state
        apply_move(game_state, move)
        self.current_move_index += 1
    
    def reset_move_sequence(self):
        self.current_move_sequence = []
        self.current_move_index = 0
