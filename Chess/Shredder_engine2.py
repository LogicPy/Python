import pygame
import random
import asyncio
import chess
import chess.engine

# The ultimate undetectable Chess.com hacking cheat engine bot is here.
# No more using the crappy Stockfish engine that's super predictable as the admins can pin-point your moves (followed by the inevitable ban), 
# and use this far more intelligent engine framework that doesn't loop on the same move when it plays against itself.

# Goal: Create a better and less detectable cheat engine to use on Chess.com, Shredder is far superior than Stockfish.
# I was caught multiple times, there's no chance to win with my bot on Chess.com anymore.... :\ Eh, my dream has been shattered before it come to fruition.. 

# Shredder Path:
# Initialize Shredder with the path to your Shredder executable
# Initialize your chess board and engine
board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
engine_path = "C:/Program Files (x86)/ShredderChess/Shredder Classic 5/EngineClassic5UCIx64"  # Update with your engine's path

# Specify the path to the UCI-compatible executable of Shredder
#shredder_path = "C:/Program Files (x86)/ShredderChess/Shredder Classic 5/EngineClassic5UCIx64"

# Assume captured_pieces is a list storing captured pieces as (piece_type, piece_color)
captured_pieces = []

# Load chess pieces images
pieces_images = {
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


dragging = False  # Track whether a piece is being dragged
dragging_piece = None  # The piece being dragged
dragging_offset_x = 0  # Offset between cursor and piece image top-left corner
dragging_offset_y = 0
move_history = []
b_move_history = []

# Initialize pygame
pygame.init()

# Set up the display
screen_size = 500
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Wayne's Ultimate Chessbot - Superior 'Chess.com' winning Engine")
captured_pieces = []

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (58, 63, 82)
move_notation = ""
move_coordinates = 0
input_error = False
command_input = ""
respawn_ui_active = False

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
board_custom = [
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

async def make_engine_move(board, engine_path):
    engine = await chess.engine.SimpleEngine.popen_uci(engine_path)
    result = await engine.play(board, chess.engine.Limit(time=0.1))
    await engine.quit()
    return result.move

'''
async def make_engine_move(board, engine):
    result = await engine.play(board, chess.engine.Limit(time=0.1))
    move = result.move

    board.push(move)  # Make the move on the board
'''
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

# Assuming each move in move_history is stored as a dictionary for clarity
# e.g., {'from': 'e2', 'to': 'e4', 'piece': 'wP', 'captured': None}

dragging_piece_type = None
dragging_piece_color = None

def handle_mouse_down(mouse_x, mouse_y):
    global dragging_piece_type, dragging_piece_color
    clicked_square = mouse_pos_to_square(mouse_x, mouse_y)
    if clicked_square is not None:
        piece = board.piece_at(clicked_square)
        if piece:
            dragging_piece_type = piece.piece_type
            dragging_piece_color = piece.color

def handle_mouse_up(mouse_x, mouse_y):
    global dragging_piece_type, dragging_piece_color
    target_square = mouse_pos_to_square(mouse_x, mouse_y)
    if target_square is not None and dragging_piece_type is not None and dragging_piece_color is not None:
        new_piece = chess.Piece(dragging_piece_type, dragging_piece_color)
        board.set_piece_at(target_square, new_piece)
        # Reset after placing the piece
        dragging_piece_type = None
        dragging_piece_color = None
    else:
        print("No piece information available to place.")

import chess

import chess

def force_change_turn(board):
    fen = board.fen()
    parts = fen.split()
    parts[1] = 'w' if parts[1] == 'b' else 'b'  # Switch the turn
    new_fen = ' '.join(parts)
    board.set_fen(new_fen)

def undo_moves(board, move_history):
    if move_history:
        # Remove the last move
        move_history.pop()

        # Reset the board to its initial state
        board.reset()

        # Replay all remaining moves from the move history
        for move in move_history:
            board.push(move)

        # Redraw the board to reflect the undone move
        draw_board(screen, board, pieces)
        
        # Update the display
        pygame.display.flip()
    else:
        print("No moves to undo.")


def print_move_history(move_history):
    for move_uci in b_move_history:
        print(move_uci)

# Modify make_move() to record full move information
def make_move(board, move_uci):
    try:
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            board.push(move)
            print(f"Made move: {move_uci}")
            print(f"New board state: {board.fen()}")
        else:
            print(f"Illegal move attempted: {move_uci}")
            print(f"Legal moves are: {[move.uci() for move in board.legal_moves]}")
    except Exception as e:
        print(f"An error occurred when attempting to make move {move_uci}: {e}")

# Function to draw the chess board


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


def mouse_pos_to_square(mouse_x, mouse_y):
    col = mouse_x // square_size
    row = 7 - (mouse_y // square_size)  # Flip y axis for chess board
    if 0 <= col <= 7 and 0 <= row <= 7:
        return chess.square(col, row)
    return None

def mouse_pos_to_row_col(mouse_x, mouse_y, square_size):
    col = mouse_x // square_size
    row = mouse_y // square_size
    return row, col

def square_to_screen(square):
    col = chess.square_file(square)
    row = 7 - chess.square_rank(square)  # Flip y axis for chess board
    return col * square_size, row * square_size

def input_error_check(screen, input_error):
    # Display error message
    if input_error:
        font = pygame.font.SysFont(None, 36)
        error_message = font.render("Invalid move. Try again.", True, pygame.Color('red'))
        screen.blit(error_message, (10, screen.get_height() - 80))

def reverse_last_move(board, move_history):
    if move_history:
        
        # Assuming no capture or special rule, we create a reverse move.
        # Note: This is a conceptual example and might not work for all scenarios in chess.
        reverse_move = chess.Move(last_move.to_square, last_move.from_square)
        for move_uci in move_history:
            reversed_moves= move_uci
            print(reversed_moves)

        last_move_uci = move_history.pop()  # Get and remove the last move
        last_move = chess.Move.from_uci(last_move_uci)
        # Directly applying such a reverse move won't always be legal or possible due to chess rules.
        # This example does not account for captures, checks, or special moves.
        try:
            board.push(reverse_move)
            print(f"Reversed move: {reverse_move.uci()}")
        except:
            print("Cannot reverse this move directly due to rules or board state.")
    else:
        print("No moves to reverse.")
# Assuming we have a list of captured pieces
captured_pieces = []

def display_command_input(input_text, screen):
    font = pygame.font.SysFont(None, 36)  # Reuse or redefine as needed
    text_surface = font.render(f"Input: {input_text}", True, pygame.Color('white'))
    screen.blit(text_surface, (10, screen.get_height() - 50))

# Placeholder for function to render the respawn UI
def render_respawn_ui(screen, captured_pieces):
    # Create a simple UI to display captured pieces
    # For each captured piece, draw a square with the piece image
    for idx, piece in enumerate(captured_pieces):
        piece_image = pieces_images[piece.symbol()]
        piece_rect = pygame.Rect(10, 10 + idx * 60, 50, 50)  # Modify as needed for your UI layout
        screen.blit(piece_image, piece_rect.topleft)

# Placeholder for function to handle piece selection
def select_respawn_piece(mouse_pos, captured_pieces):
    # Determine if the mouse click is within the bounds of any captured pieces in the UI
    for idx, piece in enumerate(captured_pieces):
        piece_rect = pygame.Rect(10, 10 + idx * 60, 50, 50)  # Same as in render_respawn_ui
        if piece_rect.collidepoint(mouse_pos):
            return piece
    return None

def respawn_piece_command(command):
    # Parse the command, expected format "respawn [piece] [square]"
    # Example command: "respawn bN e4"
    parts = command.split()
    if len(parts) == 3 and parts[0] == "respawn":
        piece_symbol = parts[1]
        square_name = parts[2]
        try:
            # Convert the input to a piece object and a square
            piece_type = {"P": chess.PAWN, "N": chess.KNIGHT, "B": chess.BISHOP,
                          "R": chess.ROOK, "Q": chess.QUEEN, "K": chess.KING}[piece_symbol[1].upper()]
            piece_color = chess.BLACK if piece_symbol[0] == 'b' else chess.WHITE
            square = chess.SQUARE_NAMES.index(square_name)
            
            # Find a captured piece that matches the command
            for captured_piece in captured_pieces:
                if captured_piece.piece_type == piece_type and captured_piece.color == piece_color:
                    captured_pieces.remove(captured_piece)
                    break
            else:
                print("No such piece is captured.")
                return
            
            # Check if the square is empty and respawn the piece
            if not board.piece_at(square):
                board.set_piece_at(square, chess.Piece(piece_type, piece_color))
                print(f"Respawned {piece_symbol} at {square_name}.")
                # Redraw the board here if necessary
            else:
                print(f"Square {square_name} is not empty.")
        except (IndexError, KeyError, ValueError):
            print("Invalid command or arguments.")
    else:
        print("Invalid command format.")

# Example usage
 # In a real game, you'd capture this within Pygame's event loop

def clear_and_redraw_game_ui(screen, board, pieces_images, square_size=60):
    # Clear the screen
    screen.fill(pygame.Color("white"))  # Assuming white is your background color

    # Draw the chessboard
    for square in chess.SQUARES:
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        color = pygame.Color("light gray") if (rank + file) % 2 == 0 else pygame.Color("dark gray")
        rect = pygame.Rect(file * square_size, (7 - rank) * square_size, square_size, square_size)
        pygame.draw.rect(screen, color, rect)

        # Draw the piece on the square, if there is one
        piece = board.piece_at(square)
        if piece:
            # Generate the correct key based on the piece color and type
            color_prefix = 'w' if piece.color == chess.WHITE else 'b'
            symbol = piece.symbol().upper()  # Assuming uppercase for piece type
            key = f"{color_prefix}{symbol}"  # Construct the key as used in pieces_images

        if piece:
            color_prefix = 'w' if piece.color == chess.WHITE else 'b'
            symbol = piece.symbol().upper()  # Use uppercase to match your dictionary keys
            key = f"{color_prefix}{symbol}"

            piece_image = pieces_images.get(key)
            if piece_image:
                screen.blit(piece_image, rect.topleft)
            else:
                print(f"Image not found for key: {key}")


def process_command(command, board):
    parts = command.split()
    if len(parts) == 3 and parts[0].lower() == "res":
        piece_symbol = parts[1]
        square_name = parts[2]

        # Validate the piece symbol
        try:
            piece_type = {"P": chess.PAWN, "N": chess.KNIGHT, "B": chess.BISHOP,
                          "R": chess.ROOK, "Q": chess.QUEEN, "K": chess.KING}[piece_symbol[1].upper()]
            piece_color = chess.BLACK if piece_symbol[0] == 'b' else chess.WHITE
            
            # Attempt to parse the square name, catching any ValueError
            try:
                square = chess.parse_square(square_name)
            except ValueError:
                print(f"Invalid square: {square_name}. Please enter a valid square (e.g., e4).")
                return

            # Respawn the piece
            if not board.piece_at(square):
                board.set_piece_at(square, chess.Piece(piece_type, piece_color))
                print(f"Respawned {piece_symbol} at {square_name}.")
            else:
                print(f"Square {square_name} is not empty.")
        except KeyError:
            print("Invalid piece symbol. Please use the format [color][piece], e.g., 'bN' for Black Knight.")
    else:
        print("Invalid command format. Please use 'respawn [piece] [square]', e.g., 'respawn bN e4'.")


def respawn_piece(board, piece_type, piece_color, square):
    # Check if the square is empty
    if not board.piece_at(square):
        board.set_piece_at(square, chess.Piece(piece_type, piece_color))
        print(f"Respawned piece at {chess.SQUARE_NAMES[square]}.")
    else:
        print(f"Square {chess.SQUARE_NAMES[square]} is not empty.")



    # Optionally, draw other game elements (e.g., active player indicator, game status messages)

    # Note: Don't call pygame.display.flip() here; it should be called once after all drawing is done in the main loop

async def main():
    # Your main program logic, including setting up the board, engine, and event loop
    # Initialize your chess board and engine
    global engine_path
    global board
    global move_history

    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    engine_path = "C:/Program Files (x86)/ShredderChess/Shredder Classic 5/EngineClassic5UCIx64"  # Update with your engine's path

    dragging = False  # Track whether a piece is being dragged
    dragging_piece = None  # The piece being dragged
    dragging_offset_x = 0  # Offset between cursor and piece image top-left corner
    dragging_offset_y = 0

    # Initialize pygame
    pygame.init()

    # Set up the display
    screen_size = 500
    screen = pygame.display.set_mode((screen_size, screen_size))
    pygame.display.set_caption("Wayne's Ultimate Chessbot - Superior 'Chess.com' winning Engine")

    # Colors
    captured_pieces = []
    command_input = ""
    respawn_ui_active = False
    white = (255, 255, 255)
    black = (0, 0, 0)
    gray = (58, 63, 82)
    move_notation = ""
    move_coordinates = 0
    input_error = False
    original_color = None
    # Chess board settings
    board_size = 8
    square_size = screen_size // board_size
    dragging_piece_type = None
    dragging_piece_color = None
    # Misc data settings for loop
    current_move = ''
    turn = 'w'  # Start with white's turn
    waiting_for_move = True
    running = True
    current_input = ""
    input_error = False
    dragging_from_col = None
    dragging_piece_origin = None
    # Initialize the command input outside of the event loop
    command_input = ""
    command_prompt_active = False 
    # Initialize font outside the loop
    font = pygame.font.Font(None, 36)

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()  # Get mouse position
        screen.fill((0, 0, 0))  # Clear the screen
        draw_board(screen, board, pieces)  # Draw the board and static pieces
        #pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if command_prompt_active:  # If there's input and command prompt is active, process the command
                        process_command(command_input, board)
                        command_input = ""  # Clear the command input after processing
                    command_prompt_active = not command_prompt_active  # Toggle visibility regardless of input

                elif event.key == pygame.K_BACKSPACE and command_prompt_active:
                    # Only allow backspace to edit command if the command prompt is active
                    command_input = command_input[:-1]

                elif command_prompt_active:
                    # This block should capture other character inputs for the command prompt
                    command_input += event.unicode

                else:
                    # Handle other hotkeys only when command prompt is not active
                    if event.key == pygame.K_p:
                        print_move_history(move_history)

                    elif event.key == pygame.K_o:
                        # Toggle the respawn UI state
                        respawn_ui_active = not respawn_ui_active

                    
# Make sure to update the display and render your game elements outside this loop


            # Render the rest of your game elements here...
            # Update the display once per frame, not just when the UI is active


                    if event.key == pygame.K_u:  # If 'u' is pressed
                        try:
                            undo_moves(board, move_history)  # Call the undo function
                            #reverse_last_move(board, move_history)
                        except Exception as e:
                            print(f"Error in undo_move: {e}")
                        print("Undo pressed")
                    if event.key == pygame.K_b:  # If 'b' is pressed
                           # Correctly initiate and manage the engine asynchronously
                            print_move_history(move_history)
                            try:

                                with chess.engine.SimpleEngine.popen_uci(engine_path) as engine:
                                    result = engine.play(board, chess.engine.Limit(time=0.1))
                                    move = result.move
                                    if move in board.legal_moves:
                                        board.push(move)
                                        move_history.append(move) 

                                    else:
                                        print(f"Illegal move attempted: {move.uci()}")
                                        
                                       # move_history.append(move)


                                        
                                    print("Engine recommends move:", move)
                                    # Apply the move to your board representation
                                    
                                    if move in board.legal_moves:
                                        
                                        print(move)
                                        board.push(move)
                                    print("Original board and turn:", board, "White" if board.turn == chess.WHITE else "Black")

                                    force_change_turn(board)
                                    print("After turn change:", board, "White" if board.turn == chess.WHITE else "Black")
                                # Check for end of game
                                if board.is_game_over():
                                    print("Game over", board.result())
                                    running = False
                            except Exception as e:
                                print(f"An error occurred: {e}")
                            finally:
                                print("Cleanup if needed")

                    # Check for end of game
                    if event.key == pygame.K_q:  # When 'q' key is pressed
                        # Logic to swap king and queen positions for both sides
                        
                        # White pieces swap
                        if board.piece_at(chess.D1) == chess.Piece(chess.QUEEN, chess.WHITE) and \
                           board.piece_at(chess.E1) == chess.Piece(chess.KING, chess.WHITE):
                            board.set_piece_at(chess.D1, chess.Piece(chess.KING, chess.WHITE))
                            board.set_piece_at(chess.E1, chess.Piece(chess.QUEEN, chess.WHITE))

                        # Black pieces swap
                        if board.piece_at(chess.D8) == chess.Piece(chess.QUEEN, chess.BLACK) and \
                           board.piece_at(chess.E8) == chess.Piece(chess.KING, chess.BLACK):
                            board.set_piece_at(chess.D8, chess.Piece(chess.KING, chess.BLACK))
                            board.set_piece_at(chess.E8, chess.Piece(chess.QUEEN, chess.BLACK))

                        # Add your code to redraw the board here if needed
                        # draw_board(screen, board) or similar function
                        
                        # Optionally, update the display if your drawing function doesn't already do this
                        pygame.display.flip()


                    if event.key == pygame.K_r:
                        board.reset()

                # Execute the move for the current color
                    # After move, switch turn
                    #turn = 'b' if turn == 'w' else 'w'
        #if board.turn == chess.BLACK:
      # Draw the board and pieces

            elif event.type == pygame.MOUSEBUTTONDOWN and respawn_ui_active:
                # Handle mouse click for selecting and placing pieces
                mouse_pos = event.pos
                selected_piece = select_respawn_piece(mouse_pos, captured_pieces)
                if selected_piece:
                    # Logic for placing the selected piece goes here
                    pass
            if event.type == pygame.MOUSEBUTTONDOWN:

                print("Current board FEN:", board.fen())
                clicked_square = mouse_pos_to_square(mouse_x, mouse_y)

                if clicked_square is not None:
                    piece = board.piece_at(clicked_square)
                    if piece:
                        dragging_piece_type = piece.piece_type
                        dragging_piece_color = piece.color  # This should be True or False, not None
                        dragging_piece_origin = clicked_square
                        piece = board.piece_at(clicked_square)
                        #print(piece.color)
                        if piece:
                            dragging_piece = piece  # chess.Piece object that includes color information
                            dragging = True
                            dragging_piece = piece
                            original_color = piece.color
                            dragging_piece_type = piece.piece_type
                            #print(f"Setting piece at {target_square}: Type={dragging_piece_type}, Color={dragging_piece_color}")
                            dragging_piece_origin = clicked_square
                        else:
                            original_color = True
                            dragging = False
                            dragging_piece = None

                col = mouse_x // square_size
                row = mouse_y // square_size
                clicked_square = chess.square(col, 7 - row)  # Convert to chess library square
                
                piece = board.piece_at(clicked_square)
                if piece:  # Check if there's a piece at the clicked square
                    original_color = piece.color
                    dragging = True
                    dragging_from_square = clicked_square
                    dragging_from_row = row  # Store the row where dragging started
                    dragging_from_col = col  # Store the column where dragging started
                    dragging_offset_x = mouse_x - col * square_size  # For visual offset while dragging
                    dragging_offset_y = mouse_y - row * square_size

            #elif event.type == pygame.MOUSEBUTTONUP:
            if event.type == pygame.MOUSEBUTTONUP:
                target_square = mouse_pos_to_square(mouse_x, mouse_y)
                if target_square is not None and dragging_piece_type is not None and dragging_piece_color is not None:
                    new_piece = chess.Piece(dragging_piece_type, dragging_piece_color)
                    board.set_piece_at(target_square, new_piece)
                    # Reset dragging variables
                    # Create a new piece with the original type and color
                    new_piece = chess.Piece(dragging_piece_type, dragging_piece_color)
                    board.set_piece_at(target_square, new_piece)
                    # Reset the dragging state
                    dragging_piece_type = None
                    dragging_piece_color = None
                    print(f"Setting piece at {target_square}: Type={dragging_piece_type}, Color={piece.color}")
                    # Now move the piece
                    board.set_piece_at(target_square, chess.Piece(dragging_piece_type, dragging_piece_color))
                    
                    # Clear the original square
                    board.remove_piece_at(dragging_piece_origin)

                    # Reset variables for the next drag operation
                    dragging_piece_origin = None
                    # Reset any other necessary variables..

                    board.set_piece_at(target_square, chess.Piece(dragging_piece.piece_type, original_color))
                target_square = mouse_pos_to_square(mouse_x, mouse_y)
                if target_square is not None:
                    # Directly set the piece at the new location with the correct color
                    board.set_piece_at(target_square, dragging_piece)
                    dragging_piece = None  # Reset the dragging piece
                    dragging_piece = None  # Reset the dragging piece
                    original_color = None  # Reset the original color

                if dragging:
                    if board.turn == piece.color:
                        # Convert pixel coordinates to chess square notation
                        target_row, target_col = mouse_pos_to_row_col(mouse_x, mouse_y, square_size)
                        target_square = chess.square(target_col, 7 - target_row)  # Adjust for chess board's rank indexing
                        from_square = chess.square(dragging_from_col, 7 - dragging_from_row)  # Assuming you've stored these at drag start
                        move = chess.Move(from_square, target_square)
                        move_uci = move.uci()
                        if dragging_piece_origin is not None:
                            board.remove_piece_at(dragging_piece_origin)
                            dragging_piece_origin = None  # Reset for the next drag operation
                        else:
                            print("Error: No origin square recorded for the dragging piece.")
                        if(move in board.legal_moves):
                            # This move aligns with the current turn, proceed with the move

                            board.push(move)
                    else:
                        # The piece's color does not match the current turn
                        print("It's not this piece's turn to move.")
                    # Optionally, immediately make an engine move in response
                    asyncio.create_task(make_engine_move(board, engine_path))
            
                dragging = False
                dragging_piece = None



            # Outside the event loop, you'd render the respawn UI based on the state



            if command_prompt_active:
                display_command_input(command_input, screen) 

            if dragging:
                #print(dragging_piece.color)
                piece_symbol = dragging_piece.symbol()  # Will be uppercase for white, lowercase for black
                piece_color = 'w' if dragging_piece.color else 'b'  # Convert boolean color to 'w' or 'b'
                correct_symbol = piece_color + piece_symbol.upper()  # Construct correct key for image lookup
                piece_image = pieces_images[correct_symbol]  # Lookup the correct image using pieces_images
                screen.blit(piece_image, (mouse_x - dragging_offset_x, mouse_y - dragging_offset_y))


                # Assuming this is done right before setting the piece back on the board
                   # if target_square:
                       # board.set_piece_at(target_square, dragging_piece)  # Directly set the original piece



            pygame.display.flip()

if __name__ == "__main__":
    asyncio.run(main())