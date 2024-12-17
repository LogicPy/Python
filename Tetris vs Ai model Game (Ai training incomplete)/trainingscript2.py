# trainingscript2.py

import json
import logging
import random
import os
from copy import deepcopy
from utils import get_random_tetromino

from ga import (
    POPULATION_SIZE,
    GENERATIONS,
    random_move_sequence,
    evolve_population,
    fitness_function,
    clear_lines,
    add_to_grid,
    valid_move,
    rotate_shape,
    get_column_height,
    count_gaps,
    calculate_bumpiness,
    simulate_moves
)

# Define all tetromino shapes
TETROMINOES = {
    "I": [[1, 1, 1, 1]],
    "O": [[1, 1],
          [1, 1]],
    "T": [[0, 1, 0],
          [1, 1, 1]],
    "S": [[0, 1, 1],
          [1, 1, 0]],
    "Z": [[1, 1, 0],
          [0, 1, 1]],
    "J": [[1, 0, 0],
          [1, 1, 1]],
    "L": [[0, 0, 1],
          [1, 1, 1]]
}

# Initialize logging
logger = logging.getLogger('tetris_ga_training')
logger.setLevel(logging.DEBUG)
logging.basicConfig(
    filename='tetris_ga_training.log',  # Ensure logs are written to a file
    filemode='a',  # Append mode
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress external library debug logs
logging.getLogger('matplotlib').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)

# Function to randomly select a tetromino
def get_random_tetromino():
    piece_type = random.choice(list(TETROMINOES.keys()))
    shape = TETROMINOES[piece_type]
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Assign random color
    return {"type": piece_type, "shape": shape, "x": 5, "y": 0, "color": color}



# Function to load existing population
def load_population(piece_type, file_path=None):
    if not file_path:
        file_path = f"population_{piece_type}.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                population = json.load(f)
            logger.info(f"Loaded existing population for {piece_type} from {file_path}.")
            return population
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from {file_path}. Initializing new population.")
    else:
        logger.info(f"No existing population found for {piece_type}. Initializing new population.")
    # Initialize new population if loading fails
    return [random_move_sequence() for _ in range(POPULATION_SIZE)]

# Function to save population
def save_population(population, piece_type, file_path=None):
    if not file_path:
        file_path = f"population_{piece_type}.json"
    try:
        with open(file_path, "w") as f:
            json.dump(population, f)
        logger.info(f"Population for {piece_type} saved to {file_path}.")
    except Exception as e:
        logger.error(f"Failed to save population for {piece_type} to {file_path}: {e}")

# Function to initialize game state
def initialize_game_state(): 
    return {
        "grid": [[0]*10 for _ in range(20)],  # Standard grid size
        "current_piece": get_random_tetromino(),
        "score": 0,
        "lines_cleared": 0,
        "fall_speed": 1.0,
    }

# Function to generate a random game state
def generate_random_game_state():
    grid = [[0]*10 for _ in range(20)]
    # Optionally, add random blocks to the grid
    for _ in range(random.randint(0, 10)):  # Random number of blocks
        x = random.randint(0, 9)
        y = random.randint(0, 19)
        grid[y][x] = 1
    current_piece = get_random_tetromino()
    current_piece['x'] = random.randint(0, 9 - len(current_piece['shape'][0]) + 1)
    current_piece['y'] = 0
    return {
        "grid": grid,
        "current_piece": get_random_tetromino(),

        "score": 0,
        "lines_cleared": 0,
        "fall_speed": 1.0,
    }

# Training loop for each tetromino
# Initialize aggregated_best_sequences to store best sequences for all tetrominoes
aggregated_best_sequences = {}

# Training loop for each tetromino
for piece_type in TETROMINOES.keys():
    logger.info(f"=== Starting training for Tetromino: {piece_type} ===")
    population = load_population(piece_type)

    # Training variables
    fitness_history = []
    
    for generation in range(1, GENERATIONS + 1):
        logger.info(f"Tetromino {piece_type} - Generation {generation}/{GENERATIONS}")
        
        # Generate a new initial game state for this generation
        initial_game_state = generate_random_game_state()
        game_state_str = json.dumps(initial_game_state)
        
        # Evolve the population
        population = evolve_population(population, game_state_str, None)
        
        # Evaluate fitness scores
        fitness_scores = [fitness_function(ind, game_state_str) for ind in population]
        best_fitness = max(fitness_scores)
        best_individual = population[fitness_scores.index(best_fitness)]
        
        # Calculate average fitness
        average_fitness = sum(fitness_scores) / len(fitness_scores)
        logger.info(f"Tetromino {piece_type} - Generation {generation}: Best Fitness = {best_fitness}, Average Fitness = {average_fitness}")
        logger.debug(f"Tetromino {piece_type} - Best Move Sequence: {best_individual}")
        
        # Append to fitness history
        fitness_history.append({
            "generation": generation,
            "best_fitness": best_fitness,
            "average_fitness": average_fitness
        })
        
        # Save the best move sequence for this generation
        with open(f"best_move_sequence_{piece_type}_gen_{generation}.json", "w") as f:
            json.dump(best_individual, f)
        
        # Save the entire population for cumulative training
        save_population(population, piece_type)
        
        # Early Stopping Condition (optional)
        TARGET_FITNESS = 550.0  # Example threshold
        if best_fitness >= TARGET_FITNESS:
            logger.info(f"Tetromino {piece_type} reached target fitness at generation {generation}. Stopping training.")
            break
    
    # Save fitness history
    with open(f"fitness_history_{piece_type}.json", "w") as f:
        json.dump(fitness_history, f, indent=4)
    
    # Save the final best move sequence for the current tetromino type
    aggregated_best_sequences[piece_type] = best_individual  # Update the aggregated dictionary

    logger.info(f"=== Completed training for Tetromino: {piece_type} ===\n")

# Save the aggregated best move sequences to a single JSON file
with open("best_move_sequence.json", "w") as f:
    json.dump(aggregated_best_sequences, f, indent=4)
