import pygame
import random
from stockfish import Stockfish
from stockfish.models import StockfishException

# Goal: Set new orientation for chess assistance application using Stockfish with 'stockfish.get_best_move()'

# Colors and settings omitted for brevity...

# Load chess pieces and initial board setup...

# Stockfish Path:
# Initialize Stockfish with the path to your Stockfish executable
stockfish = Stockfish(path="C:/Users/Admin/Downloads/stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2")

dragging = False  # Track whether a piece is being dragged
dragging_piece = None  # The piece being dragged
dragging_offset_x = 0  # Offset between cursor and piece image top-left corner
dragging_offset_y = 0
move_history = []

# Initialize pygame
pygame.init()

# Set up the display
screen_size = 600
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Wayne's Ultimate Chessbot - Superior 'Chess.com' winning Engine")

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

board_keycolor_var = "w"

def update_turn():
    global board_keycolor_var
    # Switch the turn
    board_keycolor_var = 'w' if board_keycolor_var == 'b' else 'b'
    # Debug output
    print(f"Turn switched to: {board_keycolor_var}")

def board_to_fen(board):
    global board_keycolor_var
    # Convert the board to FEN notation
    fen_rows = []
    for row in board:
        empty_count = 0
        fen_row = ""
        for cell in row:
            if cell == "--":  # Empty square
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                fen_row += cell[1].lower() if cell[0] == 'b' else cell[1]
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)
    fen_position = "/".join(fen_rows)
    
    # Assuming it's always Black's turn for simplicity, and omitting castling, en passant, halfmove, and fullmove counters
    if board_keycolor_var == "w":
        return f"{fen_position} w - - 0 1"
    elif board_keycolor_var == "b":
        return f"{fen_position} b - - 0 1"

def is_king_captured(board):
    # Assuming 'wK' for White King and 'bK' for Black King
    white_king_present = any('wK' in row for row in board)
    black_king_present = any('bK' in row for row in board)
    
    if not white_king_present:
        return 'Black wins by capturing the White King!'
    elif not black_king_present:
        return 'White wins by capturing the Black King!'
    else:
        return None  # No king has been captured

def display_end_game_message(result):
    font = pygame.font.SysFont(None, 48)
    text_surface = font.render(result, True, (255, 0, 0))  # Red text for visibility
    text_rect = text_surface.get_rect(center=(screen_size // 2, screen_size // 2))
    screen.fill((0, 0, 0))  # Optionally clear the screen or draw over the current state
    screen.blit(text_surface, text_rect)
    pygame.display.flip()  # Update the display with the message
# Assuming you have a function to apply Stockfish's move

# Assuming each move in move_history is stored as a dictionary for clarity
# e.g., {'from': 'e2', 'to': 'e4', 'piece': 'wP', 'captured': None}

def undo_move():
    global move_history, board, turn
    if move_history:
        last_move = move_history.pop()
        
        # Retrieve the details of the move
        from_square = last_move['from']
        to_square = last_move['to']
        piece_moved = last_move['piece']
        piece_captured = last_move['captured']
        
        # Convert board positions to indices, similar to notation_to_index()
        from_row, from_col = notation_to_index(from_square)
        to_row, to_col = notation_to_index(to_square)
        
        # Move the piece back to its original position
        board[from_row][from_col] = piece_moved
        # If a piece was captured, put it back
        if piece_captured:
            board[to_row][to_col] = piece_captured
        else:
            board[to_row][to_col] = '--'
        
        # Update the board display, etc.
        draw_board()
        pygame.display.flip()
        
        # Switch the turn back
        turn = 'w' if turn == 'b' else 'b'

# Modify make_move() to record full move information
def make_move(move):
    global move_history, board, turn
    # ...
    # When making a move, store all necessary information
    move_info = {
        'from': from_square,
        'to': to_square,
        'piece': piece_moved,
        'captured': piece_captured  # Store the piece that was at to_square before the move
    }
    move_history.append(move_info)
    # ...

def apply_stockfish_move(move):
    global running
    global move_history

    # Convert the move notation to board indices
    cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    from_square, to_square = move[:2], move[2:]
    
    piece_moved = get_piece_at_square(from_square)
    piece_captured = get_piece_at_square(to_square)
    
    from_row = 8 - int(from_square[1])
    from_col = cols[from_square[0]]
    to_row = 8 - int(to_square[1])
    to_col = cols[to_square[0]]
    
    # Perform the move
    moving_piece = board[from_row][from_col]
    board[to_row][to_col] = moving_piece
    board[from_row][from_col] = '--'
    
    # Auto-Function responsible for switching Ai's turn auto-ai play-through
    # Line one - update the turns using new function
    #update_turn()  # Update the global turn variable after the move
    # Line two - generated output on fen-feedback
    #print(f"Generated FEN: {fen}")  # Debug output
    # Record the move
    move_info = {
        'from': from_square,
        'to': to_square,
        'piece': piece_moved,
        'captured': piece_captured
    }
    move_history.append(move_info)

    # Continue with any other logic needed to update the game state
    # Check if move is a capture, for simplicity we'll just move the piece
    print(f"Moved {moving_piece} from {from_square} to {to_square}")
    result = is_king_captured(board)
    result = is_king_captured(board)
    if result:
        display_end_game_message(result)
        return False  # Indicate the game should end
    return True  # Indicate the game should continue

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

def get_piece_at_square(square):
    # Assuming your board is a list of lists, where rows are lists and each square is represented by a string like 'e2'
    # Convert algebraic notation (e.g., 'e2') to board indices
    col_to_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    row_index = 8 - int(square[1])  # Convert the numeric part to an index, e.g., '8' -> 0, '1' -> 7
    col_index = col_to_index[square[0]]  # Convert the letter to an index, e.g., 'a' -> 0, 'h' -> 7
    
    # Return the piece at the specified square
    return board[row_index][col_index]

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
        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_s:
                # Switch to the second board configuration
                board = [
                    ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
                    ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
                    ['--', '--', '--', '--', '--', '--', '--', '--'],
                    ['--', '--', '--', '--', '--', '--', '--', '--'],
                    ['--', '--', '--', '--', '--', '--', '--', '--'],
                    ['--', '--', '--', '--', '--', '--', '--', '--'],
                    ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
                    ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
                ]
                # You may need to update the display or other game state variables as appropriate
                draw_board()  # Redraw the board with the new configuration
                board_keycolor_var = "b"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:  # If 'u' is pressed
                    try:
                        undo_move()  # Call the undo function
                    except Exception as e:
                        print(f"Error in undo_move: {e}")
                    print("Undo pressed")

                if event.key == pygame.K_p:  # If 'u' is pressed
                    print(board)

            if event.key == pygame.K_b:
                # Assuming 'w' is white and 'b' is black
                current_color = 'w' if turn == 'w' else 'b'
                fen = board_to_fen(board)
                # Set up Stockfish for the current player's turn
                # This might involve setting the FEN position with the correct player to move
                # and then requesting the best move for that player.
                
                # Execute the move for the current color
                try:
                    stockfish.set_fen_position(fen)
                    best_move = stockfish.get_best_move()
                except Exception as e:
                    print(f"A mysterious force has ended the game: {e}")
                    # Consider ending the game or resetting the board here
                    best_move = None
                if best_move:
                    game_continues = apply_stockfish_move(best_move)
                    if not game_continues:
                        break  # Exit the loop if the game shou
                    
                    # After move, switch turn
                    turn = 'b' if turn == 'w' else 'w'

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