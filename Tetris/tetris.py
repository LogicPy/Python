import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
]

grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


# Grid
# ... (previous code remains the same until the following changes)
def new_piece():
    shape = random.choice(SHAPES)
    return {'shape': shape, 'rotation': 0, 'x': GRID_WIDTH // 2 - len(shape[0]) // 2, 'y': 0, 'color': random.choice([CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED])}

def valid_move(piece, x, y):
    for i, row in enumerate(piece['shape']):
        for j, cell in enumerate(row):
            if cell:
                new_x, new_y = x + j, y + i
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or (new_y >= 0 and grid[new_y][new_x]):
                    return False
    return True

def clear_lines():
    lines_cleared = 0
    for i, row in enumerate(grid):
        if all(row):
            del grid[i]
            grid.insert(0, [0 for _ in range(GRID_WIDTH)])  # Insert a new empty row at the top
            lines_cleared += 1
    return lines_cleared


def add_to_grid(piece):
    for i, row in enumerate(piece['shape']):
        for j, cell in enumerate(row):
            if cell:
                grid[piece['y'] + i][piece['x'] + j] = piece['color']

def clear_lines():
    full_lines = [i for i, row in enumerate(grid) if all(row)]
    for line in sorted(full_lines, reverse=True):
        del grid[line]
        grid.insert(0, [0 for _ in range(GRID_WIDTH)])
    return len(full_lines)

def draw_grid(screen):
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            if color:
                pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(screen, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def rotate_piece(piece):
    shape = piece['shape']
    new_shape = list(zip(*shape[::-1]))
    new_shape = [list(row) for row in new_shape]  # Convert tuples to lists for consistency
    # Ensure all rows have the same length, padding with zeros if necessary
    max_length = max(len(row) for row in new_shape)
    new_shape = [row + [0] * (max_length - len(row)) for row in new_shape]
    return new_shape

def valid_rotation(piece, rotation):
    for i, row in enumerate(rotation):
        for j, cell in enumerate(row):
            if cell:
                new_x, new_y = piece['x'] + j, piece['y'] + i
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or (new_y >= 0 and grid[new_y][new_x]):
                    return False
    return True

# ... (previous code remains the same until the main game loop)

# Main game loop
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 0.5
current_piece = new_piece()
game_over = False
score = 0

while not game_over:
    fall_time += clock.get_rawtime()
    clock.tick()

    if fall_time / 1000 > fall_speed:
        fall_time = 0
        if valid_move(current_piece, current_piece['x'], current_piece['y'] + 1):
            current_piece['y'] += 1
        else:
            add_to_grid(current_piece)
            score += clear_lines() * 100  # Score increases by 100 per line cleared
            current_piece = new_piece()
            if not valid_move(current_piece, current_piece['x'], current_piece['y']):
                game_over = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                if valid_move(current_piece, current_piece['x'] - 1, current_piece['y']):
                    current_piece['x'] -= 1
            if event.key == pygame.K_RIGHT:
                if valid_move(current_piece, current_piece['x'] + 1, current_piece['y']):
                    current_piece['x'] += 1
            if event.key == pygame.K_DOWN:
                if valid_move(current_piece, current_piece['x'], current_piece['y'] + 1):
                    current_piece['y'] += 1
            if event.key == pygame.K_UP:  # Rotate piece
                new_shape = rotate_piece(current_piece)
                if valid_rotation(current_piece, new_shape):
                    current_piece['shape'] = new_shape

    screen.fill(BLACK)
    draw_grid(screen)
    # Draw current piece
    for i, row in enumerate(current_piece['shape']):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, current_piece['color'], 
                                 (BLOCK_SIZE * (current_piece['x'] + j), 
                                  BLOCK_SIZE * (current_piece['y'] + i), 
                                  BLOCK_SIZE, BLOCK_SIZE))
    pygame.display.flip()

pygame.quit()