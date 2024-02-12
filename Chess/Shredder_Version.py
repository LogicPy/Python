import pygame
import random
#from stockfish import Stockfish
#from stockfish.models import StockfishException

# Goal: Set new orientation for chess assistance application using Stockfish with 'stockfish.get_best_move()'

# Colors and settings omitted for brevity...

# Load chess pieces and initial board setup...

# Stockfish Path:
# Initialize Stockfish with the path to your Stockfish executable
#stockfish = Stockfish(path="C:/Users/Admin/Downloads/stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2")
import chess
import chess.engine

# Initialize your chess board and engine
board = chess.Board()
engine_path = "C:/Program Files (x86)/ShredderChess/Shredder Classic 5/EngineClassic5UCIx64"  # Update with your engine's path

# Specify the path to the UCI-compatible executable of Shredder
#shredder_path = "C:/Program Files (x86)/ShredderChess/Shredder Classic 5/EngineClassic5UCIx64"

pieces = {
    "wP": pygame.image.load("assets/wP.png"),
    "bP": pygame.image.load("assets/bP.png"),
    "bB": pygame.image.load("assets/bB.png"),
    "wB": pygame.image.load("assets/wB.png"),
    "bN": pygame.image.load("assets/bN.png"),
    "wN": pygame.image.load("assets/wN.png"),
    "bQ": pygame.image.load("assets/bQ.png"),
    "wQ": pygame.image.load("assets/wQ.png"),
    "bK": pygame.image.load("assets/bK.png"),
    "wK": pygame.image.load("assets/wK.png"),
    "bR": pygame.image.load("assets/bR.png"),
    "wR": pygame.image.load("assets/wR.png"),
    # Load other pieces similarly...
}

dragging = False
dragging_piece = None
dragging_offset_x = 0
dragging_offset_y = 0
dragging_from_square = None

# Initialize pygame
pygame.init()

screen_width, screen_height = 500, 500
screen = pygame.display.set_mode((screen_width, screen_height))

selected_piece_pos = None
circle_radius = 20
border_thickness = 5
sprite_width, sprite_height = 50, 50
#rect1 = pygame.rect(200, 100, 150, 100)

# Set up the display
screen_size = 480
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Wayne's Ultimate Chessbot - Superior 'Chess.com' winning Engine")

# A list to keep track of all the moves made
move_history = []

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (58, 63, 82)
move_notation = ""
move_coordinates = 0
input_error = False
board_offset_x = 10  # Adjust this based on your application's layout
board_offset_y = 10  # Adjust this based on your application's layout
# Outside the event loop, before the main game loop
dragging_piece_image = None  # Initialize to None

# Chess board settings
#board_size = 8
#square_size = screen_size // board_size
#square_size = screen_size // board_size
# Adjust square_size to the desired size of your board squares
square_size = 50  # Adjust this value as needed

# Load chess pieces
pieces = {}
pieces_names = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
for name in pieces_names:
    pieces[name] = pygame.transform.scale(pygame.image.load(f'assets/{name}.png'), (square_size, square_size))

# Initial chess board
# Simple setup without pawns and only kings for simplicity
board_keycolor_var = "w"

def update_turn():
    global board_keycolor_var
    # Switch the turn
    board_keycolor_var = 'w' if board_keycolor_var == 'b' else 'b'
    # Debug output
    print(f"Turn switched to: {board_keycolor_var}")

def internal_to_shredder(piece):
    if piece.startswith('w'):
        return piece[1].upper()  # White pieces are uppercase
    elif piece.startswith('b'):
        return piece[1].lower()  # Black pieces are lowercase
    else:
        return None  # or some error handling

def shredder_to_internal(piece, is_white):
    if is_white:
        return 'w' + piece.upper()
    else:
        return 'b' + piece.lower()

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

def mouse_pos_to_board_index(mouse_x, mouse_y, board_offset_x, board_offset_y, board_height, square_size):
    col = (mouse_x - board_offset_x) // square_size
    # Invert the y calculation by subtracting from the board height
    row = (board_height - (mouse_y - board_offset_y)) // square_size
    # Adjust if your board's (0,0) square is at the bottom-left
    return row, col

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

def get_piece_at_square(square):
    # Assuming your board is a list of lists, where rows are lists and each square is represented by a string like 'e2'
    # Convert algebraic notation (e.g., 'e2') to board indices
    col_to_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    row_index = 8 - int(square[1])  # Convert the numeric part to an index, e.g., '8' -> 0, '1' -> 7
    col_index = col_to_index[square[0]]  # Convert the letter to an index, e.g., 'a' -> 0, 'h' -> 7
    
    # Return the piece at the specified square
    return board[row_index][col_index]


# Assuming you have a function to apply Stockfish's move
def apply_stockfish_move(move):
    global move_history

    move_history.append(move)

    # Parse the move (assuming it's in the format 'e2e4')
    from_square = move[:2]
    to_square = move[2:]
    
    # Assuming you have functions or logic to determine the moved piece and any captured piece
    piece_moved = get_piece_at_square(from_square)
    piece_captured = get_piece_at_square(to_square)
    
    cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    from_square, to_square = move[:2], move[2:]
    
    from_row = 8 - int(from_square[1])
    from_col = cols[from_square[0]]
    to_row = 8 - int(to_square[1])
    to_col = cols[to_square[0]]
    
    # Perform the move
    moving_piece = board[from_row][from_col]
    board[to_row][to_col] = moving_piece
    board[from_row][from_col] = '--'
    # Apply the move to the board
    # (This is where you'd normally update your board representation)
    
    # Record the move
    move_info = {
        'from': from_square,
        'to': to_square,
        'piece': piece_moved,
        'captured': piece_captured
    }
    move_history.append(move_info)
    print(f"Moved {moving_piece} from {from_square} to {to_square}")
    result = is_king_captured(board)
    result = is_king_captured(board)
    if result:
        display_end_game_message(result)
        return False  # Indicate the game should end
    return True  # Indicate the game should continue


    # Continue with any other logic needed to update the game state


    
    # Auto-Function responsible for switching Ai's turn auto-ai play-through
    # Line one - update the turns using new function
    #update_turn()  # Update the global turn variable after the move
    # Line two - generated output on fen-feedback
    #print(f"Generated FEN: {fen}")  # Debug output

    # Check if move is a capture, for simplicity we'll just move the piece
def draw_board(screen, board, pieces):
    square_size = 60  # Define the size of a square on your board
    colors = [pygame.Color("white"), pygame.Color("gray")]  # Define board colors

    for square in chess.SQUARES:
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        color = colors[(rank + file) % 2]
        rect = pygame.Rect(file * square_size, (7 - rank) * square_size, square_size, square_size)
        pygame.draw.rect(screen, color, rect)

        piece = board.piece_at(square)
        if piece:
            symbol = piece.symbol()
            if piece.color == chess.WHITE:
                piece_name = 'w' + symbol.upper()
            else:
                piece_name = 'b' + symbol.upper()
            # Draw the piece on the board using the loaded images
            screen.blit(pieces[piece_name], rect)




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
   
# Assuming each move in move_history is stored as a dictionary for clarity
# e.g., {'from': 'e2', 'to': 'e4', 'piece': 'wP', 'captured': None}
def mouse_pos_to_square(mouse_x, mouse_y):
    col = (mouse_x - board_offset_x) // square_size
    row = 7 - ((mouse_y - board_offset_y) // square_size)
    if 0 <= col <= 7 and 0 <= row <= 7:
        return chess.square(col, row)
    else:
        return None

def undo_move():
    global board
    if board.move_stack:
        board.pop()  # Undo the last move
        draw_board(screen, board, pieces)
        pygame.display.flip()

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
# Main game loop
running = True

while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()  # Get mouse position
    screen.fill((0, 0, 0))  # Clear the screen
    draw_board(screen, board, pieces)  # Draw the board and static pieces

    pygame.display.flip()
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

            if event.key == pygame.K_b:
                # Assuming 'w' is white and 'b' is black
                #current_color = 'w' if turn == 'w' else 'b'
                #fen = board_to_fen(board)
                # Set up (Previous 'Stockfish')'Shredder' for the current player's turn
                # This might involve setting the FEN position with the correct player to move
                # and then requesting the best move for that player.
                if turn == 'b':
                    current_color = 'b'
                    fen = board_to_fen(board)
                    # Now let's use the engine to get the move
                    with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
                        result = engine.play(board, chess.engine.Limit(time=0.1))
                        move = result.move
                        board.push(move)
                    turn = 'w'  # Switch turn to white

                with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
                    result = engine.play(board, chess.engine.Limit(time=0.1))
                    move = result.move
                    print("Engine recommends move:", move)
                    # Apply the move to your board representation
                    board.push(move)
                
                # Check for end of game
                if board.is_game_over():
                    print("Game over", board.result())
                    running = False
                # Execute the move for the current color
                    # After move, switch turn
                    #turn = 'b' if turn == 'w' else 'w'

            if event.key == pygame.K_p:
                print(board)

            if event.key == pygame.K_u:  # If 'u' is pressed
                try:
                    undo_move()  # Call the undo function
                except Exception as e:
                    print(f"Error in undo_move: {e}")
                print("Undo pressed")

             
        if event.type == pygame.MOUSEBUTTONDOWN:
            col, row = (mouse_x - board_offset_x) // square_size, (mouse_y - board_offset_y) // square_size
            dragging_from_square = chess.square(col, row)
            piece = board.piece_at(dragging_from_square)
            if piece:
                dragging = True
                dragging_piece = piece
                dragging_piece_image = pieces[shredder_to_internal(dragging_piece.symbol(), dragging_piece.color == chess.WHITE)]  # Translate piece symbol to internal representation
                dragging_offset_x = mouse_x - (col * square_size + board_offset_x)
                dragging_offset_y = mouse_y - (row * square_size + board_offset_y)
        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            col, row = (mouse_x - board_offset_x) // square_size, (mouse_y - board_offset_y) // square_size
            to_square = chess.square(col, row)
            move = chess.Move(dragging_from_square, to_square)
            if move in board.legal_moves:
                board.push(move)
            dragging = False
            dragging_piece = None
        elif event.type == pygame.MOUSEMOTION and dragging:
            col, row = (mouse_x - board_offset_x) // square_size, (mouse_y - board_offset_y) // square_size
            dragging_piece_x = col * square_size + board_offset_x - dragging_offset_x
            dragging_piece_y = row * square_size + board_offset_y - dragging_offset_y

# Outside the event loop, draw the piece being dragged on top of everything else
if dragging_piece:
    screen.blit(dragging_piece_image, (dragging_piece_x, dragging_piece_y))


# Outside the event loop, draw the piece being dragged on top of everything else
if dragging_piece:
    screen.blit(dragging_piece_image, (dragging_piece_x, dragging_piece_y))


pygame.quit()

