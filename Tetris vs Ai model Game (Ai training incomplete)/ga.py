import random
import json
import logging
from copy import deepcopy
import matplotlib.pyplot as plt
import logging
from utils import get_random_tetromino

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

# Now import other modules
import matplotlib.pyplot as plt

# GA Parameters
POPULATION_SIZE = 100

MUTATION_RATE = 0.3  # Example increased rate
  # Increased mutation rate for more diversity
CROSSOVER_RATE = 0.8
GENERATIONS = 50
MAX_MOVES = 50  # Increased move sequence length

logger = logging.getLogger('tetris_ai')

# Helper functions required by fitness_function
GRID_WIDTH = 10
GRID_HEIGHT = 20

def get_column_height(grid, x):
    for y in range(GRID_HEIGHT):
        if grid[y][x]:
            return GRID_HEIGHT - y
    return 0

def valid_move(piece, x, y, grid, rotation=None):
    rotated_shape = rotation if rotation else piece['shape']
    for i, row in enumerate(rotated_shape):
        for j, cell in enumerate(row):
            if cell:
                new_x = x + j
                new_y = y + i
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or (new_y >= 0 and grid[new_y][new_x]):
                    return False
    return True

def clear_lines(grid, lines_cleared_total, score, fall_speed):
    """
    Clears completed lines from the grid.

    Parameters:
        grid (list): The game grid.
        lines_cleared_total (int): Total lines cleared so far.
        score (int): Current score.
        fall_speed (float): Current fall speed.

    Returns:
        tuple: (number of lines cleared, updated total lines cleared, updated score, updated fall speed)
    """
    lines_cleared = 0
    new_grid = []

    for row in grid:
        if all(row):  # If the row is fully filled
            lines_cleared += 1
        else:
            new_grid.append(row)

    # Add new empty rows at the top for the cleared lines
    for _ in range(lines_cleared):
        new_grid.insert(0, [0 for _ in range(len(grid[0]))])

    # Update the grid
    grid[:] = new_grid  # Modify the grid in place

    # Update score and total lines cleared
    lines_cleared_total += lines_cleared
    score += lines_cleared * 100

    # Adjust fall speed based on the total lines cleared
    if lines_cleared_total % 5 == 0 and fall_speed > 0.02:
        fall_speed *= 0.9

    return lines_cleared, lines_cleared_total, score, fall_speed



def rotate_shape(shape):
    """
    Rotates the given shape 90 degrees clockwise.

    Parameters:
        shape (list of lists): The current Tetris piece shape.

    Returns:
        list of lists: Rotated shape.
    """
    rotated = list(zip(*shape[::-1]))
    return [list(row) for row in rotated]  # Convert tuples back to lists

def add_to_grid(piece, grid):
    for i, row in enumerate(piece['shape']):
        for j, cell in enumerate(row):
            if cell:
                y = piece['y'] + i
                x = piece['x'] + j
                if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                    grid[y][x] = piece['color']

def count_gaps(grid):
    gaps = 0
    for x in range(GRID_WIDTH):
        block_found = False
        for y in range(GRID_HEIGHT):
            if grid[y][x]:
                block_found = True
            elif block_found and not grid[y][x]:
                gaps += 1
    return gaps

def calculate_bumpiness(grid):
    heights = [get_column_height(grid, x) for x in range(GRID_WIDTH)]
    bumpiness = sum(abs(heights[x] - heights[x+1]) for x in range(GRID_WIDTH - 1))
    return bumpiness

# Define evolve_population
def evolve_population(population, game_state_str, ai_model=None):
    logger.debug("Evolving population...")
    
    # Calculate fitness scores
    fitness_scores = [fitness_function(ind, game_state_str, ai_model) for ind in population]
    logger.debug(f"Fitness scores: {fitness_scores}")
    
    # Selection: Select the top 50%
    num_selected = POPULATION_SIZE // 2
    selected = selection(population, fitness_scores, num_selected)
    logger.debug(f"Selected {len(selected)} individuals for reproduction.")
    
    # Crossover and Mutation to create offspring
    offspring = []
    while len(offspring) < POPULATION_SIZE - num_selected:
        parent1, parent2 = random.sample(selected, 2)
        child = crossover(parent1, parent2)
        child = mutate(child)
        offspring.append(child)
        logger.debug(f"Created offspring: {child}")
    
    # Create new population
    new_population = selected + offspring
    logger.debug(f"New population size: {len(new_population)}")
    
    return new_population

def generate_random_game_state():
    grid = [[0]*10 for _ in range(20)]
    # Optionally, add random blocks to the grid
    for _ in range(random.randint(0, 10)):  # Random number of blocks
        x = random.randint(0, 9)
        y = random.randint(0, 19)
        grid[y][x] = 1
    current_piece = random.choice([
        {"shape": [[1, 1, 1, 1]], "color": (0, 255, 255)},  # I-piece
        {"shape": [[1, 1, 1], [0, 1, 0]], "color": (255, 165, 0)},  # T-piece
        {"shape": [[1, 1], [1, 1]], "color": (0, 255, 0)},  # O-piece
        # Add more pieces as needed
    ])
    current_piece['x'] = random.randint(0, 9 - len(current_piece['shape'][0]) + 1)
    current_piece['y'] = 0
    return {
        "grid": grid,
        "current_piece": current_piece,
        "score": 0,
        "lines_cleared": 0,
        "fall_speed": 1.0,
    }

def initialize_population():
    population = []
    for _ in range(POPULATION_SIZE):
        if random.random() < 0.2:  # 20% start with a known good strategy
            population.append(["left", "rotate", "drop", "right", "drop"])
        else:
            population.append(random_move_sequence())
    return population

def fitness_sharing(population, fitness_scores, sharing_threshold=2, sharing_coeff=1):
    adjusted_fitness = fitness_scores.copy()
    for i in range(len(population)):
        for j in range(len(population)):
            if i != j:
                similarity = len(set(population[i]) & set(population[j]))
                if similarity > sharing_threshold:
                    adjusted_fitness[i] -= sharing_coeff
    return adjusted_fitness


# In your training script
for generation in range(1, GENERATIONS + 1):
    logger.info(f"Generation {generation}/{GENERATIONS}")
    
    # Generate a new initial game state for each generation or each individual
    initial_game_state = generate_random_game_state()
    game_state_str = json.dumps(initial_game_state)
    
    # Evolve the population
    #population = evolve_population(population, game_state_str, ai_model=None)
    
    # Evaluate fitness scores
    #fitness_scores = [fitness_function(ind, game_state_str) for ind in population]
    # Rest of the loop remains the same



def print_grid(grid):
    for row in grid:
        print(''.join(['█' if cell else ' ' for cell in row]))
    print('\n')

# Call print_grid(simulated_state['grid']) after applying moves


import json
import logging

# Initialize logging
logger = logging.getLogger('tetris_ai')
logger.setLevel(logging.DEBUG)

def simulate_moves(game_state_str, move_sequence, ai_model=None):
    simulated_state = json.loads(game_state_str)
    grid = simulated_state.get('grid', [[]])
    piece = simulated_state.get('current_piece')

    move_index = 0  # To iterate through the move sequence
    
    while True:
        if move_index >= len(move_sequence):
            break  # No more moves to apply
        
        move = move_sequence[move_index]
        move_index += 1
        
        if move == "left":
            if valid_move(piece, piece['x'] - 1, piece['y'], grid):
                piece['x'] -= 1
        elif move == "right":
            if valid_move(piece, piece['x'] + 1, piece['y'], grid):
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
            # Spawn a new piece
            simulated_state['current_piece'] = get_random_tetromino()
            piece = simulated_state['current_piece']
        
        # Check for game over condition
        #if not valid_move(piece, piece['x'], piece['y'], grid):
            simulated_state['game_over'] = True
            break
    
    return simulated_state


# Define weights as constants
# Inside ga.py

# Define weights appropriately
WEIGHTS = {
    "score": 1.0,
    "lines": 100.0,
    "aggregate_height": -1.0,
    "gaps": -2.0,
    "bumpiness": -0.5
}

import numpy as np  # For variance calculation

def calculate_occupied_columns(grid):
    """Count the number of columns with at least one block."""
    return sum(1 for x in range(len(grid[0])) if get_column_height(grid, x) > 0)

def calculate_column_height_variance(grid):
    """Calculate the variance of column heights in the grid."""
    heights = [get_column_height(grid, x) for x in range(len(grid[0]))]
    return np.var(heights)  # Variance of column heights

def fitness_function(move_sequence, game_state_str, ai_model=None):
    simulated_state = simulate_moves(game_state_str, move_sequence, ai_model)
    
    if not simulated_state or simulated_state.get('game_over', False):
        return -1e6  # Assign a large negative value for game-over states
    
    # Extract game state metrics
    score = simulated_state.get('score', 0)
    lines_cleared = simulated_state.get('lines_cleared', 0)
    grid = simulated_state.get('grid', [])
    
    # Calculate metrics
    aggregate_height = sum(get_column_height(grid, x) for x in range(len(grid[0])))
    gaps = count_gaps(grid)
    bumpiness = calculate_bumpiness(grid)
    
    # Define weights
    WEIGHTS = {
        "score": 1.0,  # Optional weight for score
        "lines_single": 100.0,
        "lines_double": 300.0,
        "lines_triple": 500.0,
        "lines_tetris": 800.0,
        "aggregate_height": -5.0,  # Penalize aggregate height more heavily
        "gaps": -50.0,            # Penalize gaps heavily to encourage line clears
        "bumpiness": -2.0         # Penalize uneven terrain
    }
    WEIGHTS["occupied_columns"] = 10.0  # Encourage occupying multiple columns

    occupied_columns = calculate_occupied_columns(grid)

    # Calculate tiered line clear rewards
    if lines_cleared == 1:
        lines_reward = WEIGHTS["lines_single"]
    elif lines_cleared == 2:
        lines_reward = WEIGHTS["lines_double"]
    elif lines_cleared == 3:
        lines_reward = WEIGHTS["lines_triple"]
    elif lines_cleared >= 4:
        lines_reward = WEIGHTS["lines_tetris"]
    else:
        lines_reward = 0  # No reward for no lines cleared

    # Compute fitness
    # Add smoothness as a new metric to encourage flat terrain near the bottom
    smoothness_reward = -sum(abs(get_column_height(grid, x) - get_column_height(grid, x+1))
                             for x in range(len(grid[0]) - 1))

   # New penalty weight for uneven stacking
    WEIGHTS["column_height_variance"] = -10.0  # Penalize uneven stacking

    # Calculate column height variance
    column_height_variance = calculate_column_height_variance(grid)

    # Add to fitness calculation
    fitness = (
        WEIGHTS["score"] * score +
        lines_reward +
        WEIGHTS["aggregate_height"] * aggregate_height +
        WEIGHTS["gaps"] * gaps +
        WEIGHTS["bumpiness"] * bumpiness +
        WEIGHTS["column_height_variance"] * column_height_variance
    )
    fitness += WEIGHTS["occupied_columns"] * occupied_columns

    WEIGHTS["gaps"] = -100.0  # Heavily penalize gaps


    # Penalize no lines cleared more heavily
    if lines_cleared == 0:
        no_clear_penalty = -500.0
    else:
        no_clear_penalty = 0.0

    fitness += no_clear_penalty

    
    # Debug output for analysis
    logger.debug(
        f"Move Sequence: {move_sequence}, "
        f"Score: {score}, Lines Cleared: {lines_cleared}, "
        f"Aggregate Height: {aggregate_height}, Gaps: {gaps}, "
        f"Bumpiness: {bumpiness}, Fitness: {fitness}"
    )
    
    return fitness




# Define selection
def selection(population, fitness_scores, num_selected):
    # Tournament selection
    selected = []
    tournament_size = 5  # Define tournament size
    for _ in range(num_selected):
        competitors = random.sample(list(zip(population, fitness_scores)), tournament_size)
        winner = max(competitors, key=lambda x: x[1])[0]
        selected.append(winner)
    return selected

def crossover(parent1, parent2):
    if not parent1 or not parent2:
        return parent1.copy() if parent1 else parent2.copy()

    min_length = min(len(parent1), len(parent2))
    if min_length < 2:
        return parent1.copy() if random.random() < 0.5 else parent2.copy()

    point1 = random.randint(1, min_length - 1)
    child = parent1[:point1] + parent2[point1:]
    return child[:MAX_MOVES]  # Truncate to MAX_MOVES


def tournament_selection(population, fitness_scores, tournament_size=5):
    selected = []
    for _ in range(len(population)):
        competitors = random.sample(list(zip(population, fitness_scores)), tournament_size)
        winner = max(competitors, key=lambda x: x[1])[0]
        selected.append(winner)
    return selected


def mutate(move_sequence):
    for i in range(len(move_sequence)):
        if random.random() < MUTATION_RATE:
            move_sequence[i] = random.choice(["left", "right", "rotate", "drop"])
    return move_sequence


def random_move_sequence():
    length = random.randint(1, MAX_MOVES)
    return [random.choice(["left", "right", "rotate", "drop"]) for _ in range(length)]
