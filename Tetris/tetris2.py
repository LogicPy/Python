import pygame
import random

# Add this after your imports and constants
lines_cleared_total = 0

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

def new_piece():
    shape = random.choice(SHAPES)
    return {
        'shape': shape,
        'rotation': 0,
        'x': GRID_WIDTH // 2 - len(shape[0]) // 2,
        'y': 0,
        'color': random.choice([CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED])
    }

# Window setup with resizable flag
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 0.05  # Starting fall speed
current_piece = new_piece()
game_over = False
score = 0
paused = False

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

def get_ghost_position(piece):
    ghost = piece.copy()
    while valid_move(ghost, ghost['x'], ghost['y'] + 1):
        ghost['y'] += 1
    return ghost

def draw_ghost_piece(screen, ghost_piece):
    ghost_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ghost_color = (255, 255, 0, 100)  # Semi-transparent yellow

    for i, row in enumerate(ghost_piece['shape']):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    ghost_surface,
                    ghost_color,
                    (
                        BLOCK_SIZE * (ghost_piece['x'] + j),
                        BLOCK_SIZE * (ghost_piece['y'] + i),
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    )
                )
                pygame.draw.rect(
                    ghost_surface,
                    (255, 255, 0, 150),  # Slightly less transparent border
                    (
                        BLOCK_SIZE * (ghost_piece['x'] + j),
                        BLOCK_SIZE * (ghost_piece['y'] + i),
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    ),
                    1
                )
    screen.blit(ghost_surface, (0, 0))

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if paused:
                if event.key == pygame.K_p:
                    paused = False
            else:
                if event.key == pygame.K_SPACE:  # Space bar to hard drop
                    while valid_move(current_piece, current_piece['x'], current_piece['y'] + 1):
                        current_piece['y'] += 1
                    add_to_grid(current_piece)
                    lines_cleared = clear_lines()
                    lines_cleared_total += lines_cleared
                    score += lines_cleared * 100
                    current_piece = new_piece()
                    if not valid_move(current_piece, current_piece['x'], current_piece['y']):
                        game_over = True
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
                if event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        print(f"Game paused. Current fall speed: {fall_speed:.2f}")

    if not paused:
        fall_time += clock.get_rawtime()
    if fall_time / 1000 > fall_speed:
        fall_time = 0
        if valid_move(current_piece, current_piece['x'], current_piece['y'] + 1):
            current_piece['y'] += 1
        else:
            add_to_grid(current_piece)
            lines_cleared = clear_lines()
            lines_cleared_total += lines_cleared
            print(f"Lines cleared total: {lines_cleared_total}")  # Debug print
            score += lines_cleared * 100

            # Adjust fall speed
            if lines_cleared_total % 5 == 0:
                fall_speed = max(0.02, 0.05 * (0.9 ** (lines_cleared_total // 5)))
            print(f"Lines Cleared: {lines_cleared_total}, Current Fall Speed: {fall_speed:.3f}")
            print(f"Current fall speed: {fall_speed:.2f}")  # Debug print for fall_speed

            current_piece = new_piece()
            if not valid_move(current_piece, current_piece['x'], current_piece['y']):
                game_over = True

    # Drawing
    screen.fill(BLACK)
    draw_grid(screen)

    if not paused:
        # Calculate and draw the ghost piece
        ghost_piece = get_ghost_position(current_piece)
        draw_ghost_piece(screen, ghost_piece)

        # Draw current piece
        for i, row in enumerate(current_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen,
                        current_piece['color'],
                        (
                            BLOCK_SIZE * (current_piece['x'] + j),
                            BLOCK_SIZE * (current_piece['y'] + i),
                            BLOCK_SIZE,
                            BLOCK_SIZE
                        )
                    )
                    pygame.draw.rect(
                        screen,
                        WHITE,
                        (
                            BLOCK_SIZE * (current_piece['x'] + j),
                            BLOCK_SIZE * (current_piece['y'] + i),
                            BLOCK_SIZE,
                            BLOCK_SIZE
                        ),
                        1
                    )
    else:
        font = pygame.font.Font(None, 36)
        text = font.render("PAUSED - Press P to Resume", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(text, text_rect)

        speed_text = font.render(f"Fall Speed: {fall_speed:.2f}", True, WHITE)
        speed_rect = speed_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(speed_text, speed_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
