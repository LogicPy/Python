import pygame
import random
import asyncio
import chess
import chess.engine

# The ultimate undetectable Chess.com hacking cheat engine bot is here.
# No more using the crappy Stockfish engine that's super predictable as the admins can pin-point your moves (followed by the inevitable ban), 
# and use this far more intelligent engine framework that doesn't loop on the same move when it plays against itself.

# Goal: Create a better and less detectable cheat engine to use on Chess.com, Shredder is far superior than Stockfish.
# Test it yourself, use my super updated Stockfish bot and player the Shredder engine game on hard-mode, not only won't you win, but you won't predict the moves of the ai opponent.
# I'm loving the Shredder engine. Chess.com, good luck figuring me out! xD Hahaha! 

# Shredder Path:
# Initialize Shredder with the path to your Shredder executable
# Initialize your chess board and engine
board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
engine_path = "C:/Program Files (x86)/ShredderChess/Shredder Classic 5/EngineClassic5UCIx64"  # Update with your engine's path

# Specify the path to the UCI-compatible executable of Shredder
#shredder_path = "C:/Program Files (x86)/ShredderChess/Shredder Classic 5/EngineClassic5UCIx64"


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

    # Initialize font outside the loop
    font = pygame.font.Font(None, 36)

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()  # Get mouse position
        screen.fill((0, 0, 0))  # Clear the screen
        draw_board(screen, board, pieces)  # Draw the board and static pieces
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_p:
                    print_move_history(move_history)

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

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    # During dragging, we don't need to update the board; the piece follows the mouse cursor.
                    pass

        screen.fill((0, 0, 0))  # Clear screen
        draw_board(screen, board, pieces)   # Draw the board and pieces

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