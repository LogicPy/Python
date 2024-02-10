import pygame
import random

# Colors and settings omitted for brevity...

# Load chess pieces and initial board setup...

dragging = False  # Track whether a piece is being dragged
dragging_piece = None  # The piece being dragged
dragging_offset_x = 0  # Offset between cursor and piece image top-left corner
dragging_offset_y = 0

# Initialize pygame
pygame.init()

# Set up the display
screen_size = 600
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption('Pygame Chess')

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (58, 63, 82)
move_notation = ""
move_coordinates = 0
input_error = False

# Chess board settings
board_size = 8
square_size = screen_size // board_size

# Load chess pieces
pieces = {}
pieces_names = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
for name in pieces_names:
    pieces[name] = pygame.transform.scale(pygame.image.load(f'assets/{name}.png'), (square_size, square_size))

# Initial chess board
# Simple setup without pawns and only kings for simplicity
board = [
    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['--', '--', '--', '--', '--', '--', '--', '--'],
    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
]

# Function to draw the chess board
def draw_board():
    for row in range(board_size):
        for col in range(board_size):
            color = white if (row + col) % 2 == 0 else gray
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))
            piece = board[row][col]
            if piece != '--':
                screen.blit(pieces[piece], (col * square_size, row * square_size))

# Basic AI movement (random move generator for demonstration)
def basic_ai_move():
    # This is a placeholder for AI logic to be implemented
    # For simplicity, it does not perform any move, just returns
    return

def display_turn_information(turn, screen):
    font = pygame.font.SysFont(None, 36)  # Choose a font and size
    if turn == "w":
        text_surface = font.render("Black's turn", True, pygame.Color('white'))
    else:
        text_surface = font.render("White's turn", True, pygame.Color('white'))
    
    # Position the text_surface object on the screen at the desired location
    screen.blit(text_surface, (10, screen.get_height() - 50))

def get_move_coordinates(move_notation):
    if len(move_notation) >= 4:  # For full move notations like "e2e4"
        from_square = move_notation[:2]
        to_square = move_notation[2:]
        # Convert 'from_square' and 'to_square' to board coordinates
    elif len(move_notation) == 2:  # For single square inputs
        column = move_notation[0]
        row = move_notation[1]
        # Convert to board coordinates
    else:
        # Handle error or invalid input
        print("Invalid move notation.")
        input_error_check(screen, True)
    return move_notation

def make_move(move):
    """Makes a move on the board without legality checks."""
    from_square, to_square = move[:2], move[2:]
    from_row, from_col = notation_to_index(from_square)
    to_row, to_col = notation_to_index(to_square)
    board[to_row][to_col] = board[from_row][from_col]  # Move the piece
    board[from_row][from_col] = '--'  # Clear the old square
    from_row, from_col = notation_to_index(from_square)
    to_row, to_col = notation_to_index(to_square)
    print(f"Move from ({from_row}, {from_col}) to ({to_row}, {to_col}) on "+turn+'.')
    print(f"Making move: {move_coordinates}")

def notation_to_index(notation):
    col_to_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    row = 8 - int(notation[1])  # Convert row number to array index
    col = col_to_index[notation[0]]  # Convert column letter to array index
    return row, col

def input_error_check(screen, input_error):
    # Display error message
    if input_error:
        font = pygame.font.SysFont(None, 36)
        error_message = font.render("Invalid move. Try again.", True, pygame.Color('red'))
        screen.blit(error_message, (10, screen.get_height() - 80))

# Misc data settings for loop
current_move = ''
turn = 'w'  # Start with white's turn
waiting_for_move = True
running = True
current_input = ""
input_error = False

# Initialize font outside the loop
font = pygame.font.Font(None, 36)

while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()  # Get mouse position

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for row in range(board_size):
                for col in range(board_size):
                    piece = board[row][col]
                    if piece != '--':
                        x, y = col * square_size, row * square_size
                        if x < mouse_x < x + square_size and y < mouse_y < y + square_size:
                            dragging = True
                            dragging_piece = piece
                            dragging_offset_x = mouse_x - x
                            dragging_offset_y = mouse_y - y
                            board[row][col] = '--'  # Remove the piece from the board
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                target_row, target_col = mouse_y // square_size, mouse_x // square_size
                board[target_row][target_col] = dragging_piece  # Place the piece at the new location
                dragging = False
                dragging_piece = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                # During dragging, we don't need to update the board; the piece follows the mouse cursor.
                pass

    screen.fill((0, 0, 0))  # Clear screen
    draw_board()  # Draw the board and pieces

    if dragging:
        # Draw the dragging piece at the mouse position, offset by the initial click position.
        piece_image = pieces[dragging_piece]
        screen.blit(piece_image, (mouse_x - dragging_offset_x, mouse_y - dragging_offset_y))

    pygame.display.flip()

pygame.quit()