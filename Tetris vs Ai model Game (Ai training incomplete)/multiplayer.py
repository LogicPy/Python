# multiplayer_tetris.py

import pygame
import random
import json
import os
import logging
import threading
import queue
import psutil
import hashlib
import re
from time import sleep
from copy import deepcopy
from opponent_ai import OpponentAIPlayer, load_best_move_sequence
from groq import Groq  # Ensure you have the Groq library installed
from time import sleep
import time

# ============================== #
#         Configuration          #
# ============================== #

# GA Parameters
POPULATION_SIZE = 50
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.7
GENERATIONS = 20
MAX_MOVES = 10  # Maximum number of moves in a sequence

# Screen and Grid Parameters
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10  # Standard Tetris width
GRID_HEIGHT = 20  # Standard Tetris height
DESIRED_BOTTOM_BUFFER = 10
MAX_OFFSET_Y = SCREEN_HEIGHT - (GRID_HEIGHT * BLOCK_SIZE) - DESIRED_BOTTOM_BUFFER  # 600 - 600 - 10 = -10
DESIRED_OFFSET_Y = MAX_OFFSET_Y  # Set to -10 (adjust as needed)

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

# Game States
STATE_MENU = 'MENU'
STATE_GAME = 'GAME'
STATE_GAME_OVER = 'GAME_OVER'

# Paths
ASSETS_DIR = "assets"
HIGH_SCORES_FILE = 'high_scores.json'

# Initialize Logger
logger = logging.getLogger('tetris_ai')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('tetris_ai_debug.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.propagate = False

# ============================== #
#            Classes             #
# ============================== #


class Piece:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = random.randint(0, GRID_WIDTH - len(shape[0]))
        self.y = 0

    def rotate(self):
        rotated = list(zip(*self.shape[::-1]))
        rotated = [list(row) for row in rotated]
        # Ensure all rows have the same length by padding with zeros if necessary
        max_length = max(len(row) for row in rotated)
        rotated = [row + [0] * (max_length - len(row)) for row in rotated]
        return rotated


class Player:
    def __init__(self, grid, score=0, lines_cleared=0, fall_speed=1.0):
        self.grid = grid
        self.score = score
        self.lines_cleared = lines_cleared
        self.fall_speed = fall_speed
        self.fall_time_accumulator = 0.0
        self.game_over = False
        self.current_piece = self.generate_new_piece()

    def generate_new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice([CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED])
        piece = Piece(shape, color)
        if not self.valid_move(piece, piece.x, piece.y):
            self.game_over = True
            logger.debug("New piece cannot be placed. Game Over!")
            return None
        return piece

    def valid_move(self, piece, x, y, rotation=None):
        rotated_shape = rotation if rotation else piece.shape
        for i, row in enumerate(rotated_shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x]:
                        return False
        return True

    def lock_piece(self):
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    y = self.current_piece.y + i
                    x = self.current_piece.x + j
                    if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                        self.grid[y][x] = self.current_piece.color
        self.clear_lines()
        self.current_piece = self.generate_new_piece()

    def clear_lines(self):
        lines_cleared = 0
        new_grid = [row for row in self.grid if not all(row)]
        lines_cleared = GRID_HEIGHT - len(new_grid)
        if lines_cleared > 0:
            for _ in range(lines_cleared):
                new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            self.grid = new_grid
            self.lines_cleared += lines_cleared
            self.score += lines_cleared * 100
            logger.debug(f"Cleared {lines_cleared} lines. Total lines: {self.lines_cleared}, Score: {self.score}")

    def move(self, direction):
        if direction == "left" and self.valid_move(self.current_piece, self.current_piece.x - 1, self.current_piece.y):
            self.current_piece.x -= 1
            logger.debug(f"Player moved left to ({self.current_piece.x}, {self.current_piece.y})")
        elif direction == "right" and self.valid_move(self.current_piece, self.current_piece.x + 1, self.current_piece.y):
            self.current_piece.x += 1
            logger.debug(f"Player moved right to ({self.current_piece.x}, {self.current_piece.y})")
        elif direction == "rotate":
            new_shape = self.current_piece.rotate()
            if self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y, rotation=new_shape):
                self.current_piece.shape = new_shape
                logger.debug(f"Player rotated piece to shape: {self.current_piece.shape}")

    def drop(self):
        while self.valid_move(self.current_piece, self.current_piece.x, self.current_piece.y + 1):
            self.current_piece.y += 1
        logger.debug(f"Player dropped piece to y={self.current_piece.y}")
        self.lock_piece()


class AIPlayer(Player):
    def __init__(self, grid, score=0, lines_cleared=0, fall_speed=1.0, ai_move_queue=None):
        super().__init__(grid, score, lines_cleared, fall_speed)
        self.ai_move_queue = ai_move_queue or queue.Queue()

    def apply_move_sequence(self, move_sequence):
        for move in move_sequence:
            self.move(move)
            if move == "drop":
                self.drop()
                break


class GhostPiece:
    def __init__(self, player):
        self.player = player
        self.position = (player.current_piece.x, player.current_piece.y)

    def calculate_position(self):
        piece = self.player.current_piece
        ghost_y = piece.y
        while self.player.valid_move(piece, piece.x, ghost_y + 1):
            ghost_y += 1
        self.position = (piece.x, ghost_y)

    def draw(self, screen, offset_x, offset_y):
        if self.player.current_piece:
            self.calculate_position()
            for i, row in enumerate(self.player.current_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        x = offset_x + (self.position[0] + j) * BLOCK_SIZE
                        y = offset_y + (self.position[1] + i) * BLOCK_SIZE
                        # Semi-transparent ghost color
                        ghost_color = (255, 255, 0, 100)  # RGBA
                        ghost_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
                        pygame.draw.rect(ghost_surface, ghost_color, (0, 0, BLOCK_SIZE, BLOCK_SIZE))
                        pygame.draw.rect(ghost_surface, WHITE, (0, 0, BLOCK_SIZE, BLOCK_SIZE), 1)  # Optional border
                        screen.blit(ghost_surface, (x, y))


class UI:
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.load_avatars()
        self.position_avatars()

    def load_image(self, image_name, scale=None):
        try:
            image_path = os.path.join(ASSETS_DIR, image_name)
            image = pygame.image.load(image_path).convert_alpha()
            if scale:
                image = pygame.transform.scale(image, scale)
            return image
        except pygame.error as e:
            logger.error(f"Unable to load image {image_name}: {e}")
            sys.exit()

    def load_avatars(self):
        self.human_avatar = self.load_image("human_avatar.png", scale=(100, 100))
        self.ai_avatar = self.load_image("ai_avatar.png", scale=(100, 100))

    def position_avatars(self):
        self.human_avatar_pos = self.human_avatar.get_rect(topleft=(20, 20))
        self.ai_avatar_pos = self.ai_avatar.get_rect(topright=(SCREEN_WIDTH - 20, 20))

    def draw_avatars(self):
        """
        Draws the avatars on the screen.
        """
        self.screen.blit(self.human_avatar, self.human_avatar_pos)
        self.screen.blit(self.ai_avatar, self.ai_avatar_pos)
    
    def render_labels(self):
        """
        Renders labels below avatars.
        """
        human_label = self.font.render("Player", True, WHITE)
        ai_label = self.font.render("AI", True, WHITE)

        # Position labels below avatars
        human_label_rect = human_label.get_rect(center=(self.human_avatar_pos.centerx, self.human_avatar_pos.bottom + 20))
        ai_label_rect = ai_label.get_rect(center=(self.ai_avatar_pos.centerx, self.ai_avatar_pos.bottom + 20))

        self.screen.blit(human_label, human_label_rect)
        self.screen.blit(ai_label, ai_label_rect)

    def highlight_avatar(self, active_player):
        highlight_color = GREEN
        border_width = 5
        if active_player == "Human":
            pygame.draw.rect(self.screen, highlight_color, self.human_avatar_pos, border_width)
        elif active_player == "AI":
            pygame.draw.rect(self.screen, highlight_color, self.ai_avatar_pos, border_width)

    def display_scores(self, player, ai_player):
        # Display Player Info
        player_info_x = self.human_avatar_pos.right + 20
        player_info_y = self.human_avatar_pos.top
        player_score_text = self.small_font.render(f"Score: {player.score}", True, WHITE)
        player_lines_text = self.small_font.render(f"Lines: {player.lines_cleared}", True, WHITE)
        self.screen.blit(player_score_text, (player_info_x, player_info_y))
        self.screen.blit(player_lines_text, (player_info_x, player_info_y + 30))

        # Display AI Info
        ai_info_x = self.ai_avatar_pos.left - 120
        ai_info_y = self.ai_avatar_pos.top
        ai_score_text = self.small_font.render(f"Score: {ai_player.score}", True, WHITE)
        ai_lines_text = self.small_font.render(f"Lines: {ai_player.lines_cleared}", True, WHITE)
        self.screen.blit(ai_score_text, (ai_info_x, ai_info_y))
        self.screen.blit(ai_lines_text, (ai_info_x, ai_info_y + 30))

    def display_cpu_memory_usage(self):
        process = psutil.Process(os.getpid())
        cpu_usage = process.cpu_percent(interval=0.1)
        memory_usage = process.memory_info().rss / (1024 * 1024)  # in MB
        usage_text = self.small_font.render(f"CPU: {cpu_usage}% | Mem: {memory_usage:.2f} MB", True, WHITE)
        self.screen.blit(usage_text, (SCREEN_WIDTH - 200, 10))

    def display_pause_overlay(self):
        pause_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pause_overlay.set_alpha(128)  # Transparency
        pause_overlay.fill(BLACK)
        self.screen.blit(pause_overlay, (0, 0))
        pause_text = self.font.render("PAUSED", True, WHITE)
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

    def display_game_over(self, player_score, ai_score, high_scores):
        # Determine the game result
        if player_score > ai_score:
            result_text = "🎉 You Win! 🎉"
            result_color = GREEN
        elif player_score < ai_score:
            result_text = "😞 You Lose! 😞"
            result_color = RED
        else:
            result_text = "🤝 It's a Tie! 🤝"
            result_color = YELLOW

        # Render the result text
        result_surface = self.font.render(result_text, True, result_color)
        result_rect = result_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))

        # Render the player's score
        player_score_text = self.small_font.render(f"Your Score: {player_score}", True, WHITE)
        player_score_rect = player_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        # Render the AI's score
        ai_score_text = self.small_font.render(f"AI Score: {ai_score}", True, WHITE)
        ai_score_rect = ai_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))

        # Render high scores
        high_scores_title = self.small_font.render("🏆 High Scores 🏆", True, WHITE)
        high_scores_title_rect = high_scores_title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))

        high_scores_rendered = []
        for idx, score in enumerate(high_scores):
            hs_text = self.small_font.render(f"{idx + 1}. {score}", True, WHITE)
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100 + idx * 30))
            high_scores_rendered.append((hs_text, hs_rect))

        # Instructions to restart or quit
        instruction_text = self.small_font.render("Press [R] to Restart or [Q] to Quit", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100 + len(high_scores) * 30 + 20))

        # Blit all elements onto the screen
        self.screen.blit(result_surface, result_rect)
        self.screen.blit(player_score_text, player_score_rect)
        self.screen.blit(ai_score_text, ai_score_rect)
        self.screen.blit(high_scores_title, high_scores_title_rect)
        for hs_text, hs_rect in high_scores_rendered:
            self.screen.blit(hs_text, hs_rect)
        self.screen.blit(instruction_text, instruction_rect)

        # Render avatars
        self.draw_avatars()
        self.render_labels()

    def display_menu(self, high_scores):
        # Fill the screen with black
        self.screen.fill(BLACK)

        # Render the title
        title_text = self.font.render("Multiplayer Tetris AI", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))

        # Render high scores
        high_scores_title = self.small_font.render("🏆 High Scores 🏆", True, WHITE)
        high_scores_title_rect = high_scores_title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))

        high_scores_rendered = []
        for idx, score in enumerate(high_scores):
            hs_text = self.small_font.render(f"{idx + 1}. {score}", True, WHITE)
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20 + idx * 30))
            high_scores_rendered.append((hs_text, hs_rect))

        # Render instructions to start
        instruction_text = self.small_font.render("Press [S] to Start the Game or [Q] to Quit", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 200))

        # Blit all elements onto the screen
        self.screen.blit(title_text, title_rect)
        self.screen.blit(high_scores_title, high_scores_title_rect)
        for hs_text, hs_rect in high_scores_rendered:
            self.screen.blit(hs_text, hs_rect)
        self.screen.blit(instruction_text, instruction_rect)

        # Render avatars and labels
        self.draw_avatars()
        self.render_labels()

        # Update the display
        pygame.display.flip()

    def reset_avatars(self):
        self.load_avatars()
        self.position_avatars()


class Game:
    def __init__(self):
        # Initialize Pygame and Mixer
        pygame.init()
        pygame.mixer.init()

        # Load background music
        self.load_music()

        # Initialize Screen and Fonts
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI-Based Tetris Multiplayer")
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)

        # Initialize Clock
        self.clock = pygame.time.Clock()

        # Initialize Grids
        self.player_grid = self.create_grid()
        self.ai_grid = self.create_grid()

        # Initialize Players
        self.player = Player(self.player_grid)
        self.ai_player = AIPlayer(self.ai_grid, ai_move_queue=queue.Queue())

        # Initialize Ghost Pieces
        self.player_ghost = GhostPiece(self.player)
        self.ai_ghost = GhostPiece(self.ai_player)

        # Initialize UI
        self.ui = UI(self.screen, self.font, self.small_font)

        # Initialize High Scores
        self.high_scores = self.load_high_scores()

        # Initialize AI Worker Thread
        self.ai_move_priority_queue = queue.Queue()
        self.ai_request_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.ai_thread = threading.Thread(target=self.ai_worker, args=(self.ai_request_queue, self.ai_move_priority_queue, self.stop_event), daemon=True)
        self.ai_thread.start()
        logger.debug("AI worker thread started.")

        # Game State
        self.current_state = STATE_MENU
        self.paused = False

        # Timing Variables
        self.last_ai_request_time = 0.0
        self.last_ai_move_time = 0.0

        # GA Population
        self.population = [self.random_move_sequence() for _ in range(POPULATION_SIZE)]

    def load_music(self):
        try:
            pygame.mixer.music.load(os.path.join(ASSETS_DIR, 'tetris_remix.mp3'))  # Replace with your MP3 file path
            pygame.mixer.music.play(-1)  # Play indefinitely
            pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
            logger.debug("Background music loaded and playing.")
        except pygame.error as e:
            logger.error(f"Failed to load or play background music: {e}")

    def create_grid(self):
        return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def load_high_scores(self):
        if not os.path.exists(HIGH_SCORES_FILE):
            return []
        with open(HIGH_SCORES_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                logger.error("High scores file is corrupted. Starting with empty high scores.")
                return []

    def save_high_scores(self):
        with open(HIGH_SCORES_FILE, 'w') as file:
            json.dump(self.high_scores, file)
        logger.debug("High scores saved.")

    def update_high_scores(self, player_score):
        self.high_scores.append(player_score)
        self.high_scores = sorted(self.high_scores, reverse=True)[:10]
        self.save_high_scores()
        logger.debug(f"High scores updated: {self.high_scores}")

    def random_move_sequence(self):
        """
        Generates a random move sequence.
        """
        length = random.randint(1, MAX_MOVES)
        move_sequence = [random.choice(["left", "right", "rotate", "drop"]) for _ in range(length)]
        logger.debug(f"Generated random move sequence: {move_sequence}")
        return move_sequence

    def ai_worker(self, ai_request_queue, ai_move_priority_queue, stop_event):
        """
        Worker thread that handles AI move generation.
        """
        while not stop_event.is_set():
            try:
                # Wait for a new piece to process
                piece, grid_state, score, lines_cleared = ai_request_queue.get(timeout=1)

                # Generate game state
                game_state = self.get_game_state(piece, grid_state, score, lines_cleared)
                game_state_hash = self.hash_game_state(game_state)
                logger.debug(f"AI Worker - Sending Game State to AI: {game_state}")

                # Check cache
                ai_response = ""
                if game_state_hash in ai_response_cache:
                    ai_response = ai_response_cache[game_state_hash]
                    logger.debug("AI Worker - Retrieved response from cache.")
                else:
                    ai_response = self.get_groq_response(game_state)
                    if ai_response:
                        ai_response_cache[game_state_hash] = ai_response
                        logger.debug("AI Worker - Cached the AI response.")

                if ai_response:
                    # Extract moves
                    ai_move_list = self.extract_moves(ai_response)
                    logger.debug(f"AI Worker - Extracted Moves: {ai_move_list}")

                    if ai_move_list:
                        for move in ai_move_list:
                            ai_move_priority_queue.put(move)
                        logger.debug("AI Worker - Moves enqueued successfully.")
                    else:
                        # Handle AI not providing valid moves
                        fallback_moves = self.get_fallback_moves()
                        for move in fallback_moves:
                            ai_move_priority_queue.put(move)  # Highest priority
                        logger.debug(f"AI Worker - AI did not provide valid moves. Added fallback moves: {fallback_moves}")
                else:
                    # Handle empty AI response
                    fallback_moves = self.get_fallback_moves()
                    for move in fallback_moves:
                        ai_move_priority_queue.put(move)  # Highest priority
                    logger.debug(f"AI Worker - Empty AI response. Added fallback moves: {fallback_moves}")

                ai_request_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"AI Worker - Unexpected error: {e}")
                continue

    def get_groq_response(self, game_state, max_retries=3):
        """
        Communicates with the Groq AI model to get move sequences.
        """
        try:
            client = Groq(
                api_key=os.environ.get("GROQ_API_KEY"),  # Ensure your API key is set correctly
            )

            messages = [
                {"role": "system", "content": "You are an AI assistant playing Tetris."},
                {"role": "user", "content": f"""
The current game state is: {game_state}.
Provide a JSON list of moves to position the current piece optimally.
**Use only the following moves:** left, right, rotate, drop.
**Do not include any other commands such as 'down'.**
**Ensure that 'drop' appears only once and is the final command in your response.**
**Do not include any additional text or explanations.**
**Example response:** ["rotate", "left", "drop"]
"""}
            ]

            for attempt in range(max_retries):
                try:
                    chat_completion = client.chat.completions.create(
                        messages=messages,
                        model="llama-3.1-8b-instant",  # Replace with your desired model
                    )
                    ai_response = chat_completion.choices[0].message.content.strip().lower()
                    logger.debug(f"AI Response Content: {ai_response}")
                    return ai_response
                except Exception as e:
                    logger.error(f"AI communication failed on attempt {attempt + 1}: {e}")
                    sleep(2 ** attempt)  # Exponential backoff
            logger.error("All AI communication attempts failed.")
            return ""
        except Exception as e:
            logger.error(f"Unexpected error in get_groq_response: {e}")
            return ""

    def extract_moves(self, ai_response):
        """
        Extracts valid move commands from the AI's response.
        Recognizes 'left', 'right', 'rotate', and 'drop' regardless of surrounding text.
        Ensures that 'drop' appears only once and is the last command.
        Returns a list of valid moves.
        """
        valid_commands = {"left", "right", "rotate", "drop"}
        # Use regex to find all valid commands in the response
        moves = re.findall(r'\b(left|right|rotate|drop)\b', ai_response)

        # If 'drop' is in moves, ensure it's the last command and remove any moves after it
        if 'drop' in moves:
            drop_index = moves.index('drop')
            moves = moves[:drop_index + 1]  # Keep 'drop' and remove any moves after it

        # Remove duplicate moves to prevent redundancy
        optimized_moves = []
        for move in moves:
            if not optimized_moves or move != optimized_moves[-1]:
                optimized_moves.append(move)
        return optimized_moves

    def hash_game_state(self, game_state):
        return hashlib.sha256(json.dumps(game_state, sort_keys=True).encode('utf-8')).hexdigest()

    def get_game_state(self, piece, grid, score, lines_cleared):
        """
        Constructs the current game state as a dictionary.
        """
        grid_copy = [row[:] for row in grid]
        game_state = {
            "grid": grid_copy,
            "current_piece": {
                "shape": piece.shape,
                "x": piece.x,
                "y": piece.y,
                "color": piece.color
            },
            "score": score,
            "lines_cleared": lines_cleared,
            "fall_speed": self.player.fall_speed
        }
        return game_state

    def get_fallback_moves(self):
        """
        Defines fallback moves if AI fails to provide valid moves.
        """
        return ["rotate", "drop"]

    def apply_move(self, move, player):
        """
        Applies a single move to the player.
        """
        if move == "left":
            player.move("left")
        elif move == "right":
            player.move("right")
        elif move == "rotate":
            player.move("rotate")
        elif move == "drop":
            player.drop()

    def evolve_population(self, population, game_state, ai_model=None):
        """
        Evolves the population through selection, crossover, and mutation.
        """
        logger.debug("Evolving population...")

        # Calculate fitness scores for the current population
        fitness_scores = [self.fitness_function(individual, game_state, ai_model) for individual in population]
        logger.debug(f"Fitness scores: {fitness_scores}")

        # Selection: Select the top 50% individuals based on fitness
        selected = self.selection(population, fitness_scores, POPULATION_SIZE // 2)
        logger.debug(f"Selected {len(selected)} individuals for reproduction.")

        # Crossover and Mutation to create offspring
        offspring = []
        while len(offspring) < POPULATION_SIZE // 2:
            parent1, parent2 = random.sample(selected, 2)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            offspring.append(child)
            logger.debug(f"Created offspring: {child}")

        # Combine selected individuals with offspring to form the new population
        new_population = selected + offspring
        logger.debug(f"New population size: {len(new_population)}")

        return new_population

    def selection(self, population, fitness_scores, num_selected):
        """
        Selects the top-performing individuals from the population based on fitness scores.
        """
        # Pair each individual with its fitness score
        paired = list(zip(population, fitness_scores))

        # Sort the population based on fitness scores in descending order
        sorted_paired = sorted(paired, key=lambda x: x[1], reverse=True)

        # Extract the top-performing individuals
        selected = [individual for individual, score in sorted_paired[:num_selected]]

        logger.debug(f"Selected {len(selected)} individuals out of {len(population)} based on fitness scores.")

        return selected

    def crossover(self, parent1, parent2):
        """
        Performs single-point crossover between two parent move sequences.
        """
        logger.debug(f"Crossover between parent1: {parent1} and parent2: {parent2}")

        if not parent1 or not parent2:
            child = parent1.copy() if parent1 else parent2.copy()
            logger.debug(f"One of the parents is empty. Returning child: {child}")
            return child

        # Determine crossover point
        min_length = min(len(parent1), len(parent2))

        # Ensure there is a valid range for crossover
        if min_length <= 1:
            # If move sequences are too short, skip crossover and return one of the parents
            child = parent1.copy() if random.random() < 0.5 else parent2.copy()
            logger.debug(f"Min length <=1. Skipping crossover. Returning child: {child}")
            return child

        crossover_point = random.randint(1, min_length - 1)
        logger.debug(f"Crossover point: {crossover_point}")

        # Create child by combining parts from both parents
        child = parent1[:crossover_point] + parent2[crossover_point:]
        logger.debug(f"Child after crossover: {child}")

        # Ensure child does not exceed maximum moves
        if len(child) > MAX_MOVES:
            child = child[:MAX_MOVES]
            logger.debug(f"Child truncated to MAX_MOVES: {child}")

        return child

    def mutate(self, move_sequence):
        """
        Mutates a move sequence by randomly altering some of its moves.
        """
        logger.debug(f"Original move sequence before mutation: {move_sequence}")
        for i in range(len(move_sequence)):
            if random.random() < MUTATION_RATE:
                original_move = move_sequence[i]
                move_sequence[i] = random.choice(["left", "right", "rotate", "drop"])
                logger.debug(f"Mutated move at index {i} from {original_move} to {move_sequence[i]}")
        logger.debug(f"Move sequence after mutation: {move_sequence}")
        return move_sequence

    def fitness_function(self, move_sequence, game_state, ai_model=None):
        """
        Calculates the fitness of a move sequence based on the simulated game state.

        Parameters:
            move_sequence (list): The sequence of moves to evaluate.
            game_state (dict): The current game state of the AI player.
            ai_model (object, optional): Additional AI model for fitness evaluation.

        Returns:
            float: The fitness score of the move sequence.
        """
        simulated_state = self.simulate_moves(game_state, move_sequence)
        if not simulated_state or simulated_state.get('game_over', False):
            return 0  # Poor fitness if game is over

        score = simulated_state.get('score', 0)
        lines_cleared = simulated_state.get('lines_cleared', 0)
        grid = simulated_state.get('grid', [])

        # Calculate grid metrics
        aggregate_height = sum(self.get_column_height(grid, x) for x in range(GRID_WIDTH))
        gaps = self.count_gaps(grid)
        bumpiness = self.calculate_bumpiness(grid)

        # Weight tuning
        WEIGHT_SCORE = 1.0
        WEIGHT_LINES = 100.0
        WEIGHT_AGGREGATE_HEIGHT = -0.5
        WEIGHT_GAPS = -2.0  # Heavily penalize gaps
        WEIGHT_BUMPINESS = -1.0  # Penalize uneven surfaces

        # Fitness calculation
        fitness = (
            WEIGHT_SCORE * score +
            WEIGHT_LINES * lines_cleared +
            WEIGHT_AGGREGATE_HEIGHT * aggregate_height +
            WEIGHT_GAPS * gaps +
            WEIGHT_BUMPINESS * bumpiness
        )

        # Optional AI model evaluation
        if ai_model:
            ai_evaluation = ai_model.evaluate(simulated_state)
            fitness += ai_evaluation.get('additional_metric', 0)

        return fitness

    def get_column_height(self, grid, x):
        """
        Returns the height of the column at position x.
        """
        for y in range(GRID_HEIGHT):
            if grid[y][x]:
                return GRID_HEIGHT - y
        return 0

    def count_gaps(self, grid):
        """
        Counts the number of gaps (empty cells with at least one filled cell above).
        """
        gaps = 0
        for x in range(GRID_WIDTH):
            block_found = False
            for y in range(GRID_HEIGHT):
                if grid[y][x]:
                    block_found = True
                elif block_found and not grid[y][x]:
                    gaps += 1
        return gaps

    def calculate_bumpiness(self, grid):
        """
        Calculates the bumpiness of the grid.
        """
        heights = [self.get_column_height(grid, x) for x in range(GRID_WIDTH)]
        bumpiness = sum(abs(heights[x] - heights[x+1]) for x in range(GRID_WIDTH - 1))
        return bumpiness

    def valid_move_simulated(self, piece, x, y, grid, rotated_shape=None):
        """
        Checks if the piece can move to the specified position on the simulated grid.

        Parameters:
            piece (dict): The current piece with shape, position, and color.
            x (int): The new x-coordinate.
            y (int): The new y-coordinate.
            grid (list): The simulated game grid.
            rotated_shape (list, optional): The shape after rotation.

        Returns:
            bool: True if the move is valid, False otherwise.
        """
        shape = rotated_shape if rotated_shape else piece['shape']
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    new_x = x + j
                    new_y = y + i
                    # Check horizontal boundaries
                    if new_x < 0 or new_x >= GRID_WIDTH:
                        logger.debug(f"Move invalid: x={new_x} out of bounds.")
                        return False
                    # Check vertical boundaries
                    if new_y >= GRID_HEIGHT:
                        logger.debug(f"Move invalid: y={new_y} exceeds grid height.")
                        return False
                    # Check collision only if the piece is within the grid vertically
                    if new_y >= 0 and grid[new_y][new_x]:
                        logger.debug(f"Move invalid: Collision at grid[{new_y}][{new_x}].")
                        return False
        return True


    def lock_piece_simulated(self, piece, grid):
        """
        Locks the piece into the grid.

        Parameters:
            piece (dict): The current piece with shape, position, and color.
            grid (list): The simulated game grid.

        Returns:
            list: Updated grid with the piece locked in.
        """
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    y = piece['y'] + i
                    x = piece['x'] + j
                    if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                        grid[y][x] = piece['color']
        return grid

    def clear_lines_simulated(self, grid, lines_cleared_total, score, fall_speed):
        """
        Clears completed lines from the grid.

        Parameters:
            grid (list): The simulated game grid.
            lines_cleared_total (int): Total lines cleared so far.
            score (int): Current score.
            fall_speed (float): Current fall speed.

        Returns:
            tuple: (number of lines cleared in this move, updated total lines cleared, updated score, updated fall speed)
        """
        lines_cleared = 0
        new_grid = [row for row in grid if not all(row)]
        lines_cleared = GRID_HEIGHT - len(new_grid)

        if lines_cleared > 0:
            for _ in range(lines_cleared):
                new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            grid[:] = new_grid
            lines_cleared_total += lines_cleared
            score += lines_cleared * 100

            # Optionally, adjust fall speed based on lines cleared
            fall_speed = 1.0  # Placeholder value; adjust as necessary
        else:
            fall_speed = 1.0  # No change if no lines cleared

        return lines_cleared, lines_cleared_total, score, fall_speed

    def generate_new_piece_simulated(self, grid):
        """
        Generates a new piece and checks if it can be placed on the grid.

        Parameters:
            grid (list): The simulated game grid.

        Returns:
            dict or None: The new piece if placement is possible, otherwise None.
        """
        shape = random.choice(SHAPES)
        new_piece = {
            'shape': shape,
            'x': random.randint(0, GRID_WIDTH - len(shape[0])),
            'y': 0,
            'color': random.choice([CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED])
        }

        if self.valid_move_simulated(new_piece, new_piece['x'], new_piece['y'], grid):
            return new_piece
        else:
            return None  # Game over condition


    def rotate_shape_simulated(self, shape):
        """
        Rotates the shape 90 degrees clockwise.

        Parameters:
            shape (list): The shape to rotate.

        Returns:
            list: The rotated shape.
        """
        rotated = list(zip(*shape[::-1]))  # Rotate the shape 90 degrees clockwise
        rotated = [list(row) for row in rotated]  # Convert tuples back to lists

        # Ensure all rows have the same length by padding with zeros if necessary
        max_length = max(len(row) for row in rotated)
        rotated = [row + [0] * (max_length - len(row)) for row in rotated]
        return rotated


    def simulate_moves(self, game_state, move_sequence):
        """
        Simulates applying a sequence of moves to a given game state.

        Parameters:
            game_state (dict): The current game state of the AI player.
            move_sequence (list): List of moves to simulate.

        Returns:
            dict: The simulated game state after applying the moves.
        """
        simulated_state = deepcopy(game_state)
        current_piece = simulated_state.get('current_piece')
        grid = simulated_state['grid']
        score = simulated_state['score']
        lines_cleared = simulated_state['lines_cleared']
        fall_speed = simulated_state.get('fall_speed', 1.0)
        
        logger.debug(f"Simulating moves: {move_sequence} on game_state: {game_state}")
        
        for move in move_sequence:
            if current_piece is None:
                logger.debug("No current_piece to move. Ending simulation.")
                break  # No piece to move
            
            logger.debug(f"Applying move: {move}")
            
            if move == "left":
                if self.valid_move_simulated(current_piece, current_piece['x'] - 1, current_piece['y'], grid):
                    current_piece['x'] -= 1
                    logger.debug(f"Moved left to ({current_piece['x']}, {current_piece['y']})")
            elif move == "right":
                if self.valid_move_simulated(current_piece, current_piece['x'] + 1, current_piece['y'], grid):
                    current_piece['x'] += 1
                    logger.debug(f"Moved right to ({current_piece['x']}, {current_piece['y']})")
            elif move == "rotate":
                rotated_shape = self.rotate_shape_simulated(current_piece['shape'])
                if self.valid_move_simulated(current_piece, current_piece['x'], current_piece['y'], grid, rotated_shape):
                    current_piece['shape'] = rotated_shape
                    logger.debug(f"Rotated piece to shape: {current_piece['shape']}")
            elif move == "drop":
                while self.valid_move_simulated(current_piece, current_piece['x'], current_piece['y'] + 1, grid):
                    current_piece['y'] += 1
                logger.debug(f"Dropped piece to y={current_piece['y']}")
                # Lock the piece
                grid = self.lock_piece_simulated(current_piece, grid)
                simulated_state['grid'] = grid
                # Clear lines
                lines, lines_cleared, score, fall_speed = self.clear_lines_simulated(grid, lines_cleared, score, fall_speed)
                simulated_state['lines_cleared'] = lines_cleared
                simulated_state['score'] = score
                # Generate new piece
                new_piece = self.generate_new_piece_simulated(grid)
                if new_piece:
                    simulated_state['current_piece'] = new_piece
                    logger.debug(f"Generated new piece: {new_piece}")
                else:
                    simulated_state['game_over'] = True
                    logger.debug("No valid position for new piece. Game Over.")
                    break  # Game over
        
        return simulated_state



    def get_avatar_positions(self):
        human_avatar_rect = self.ui.human_avatar.get_rect(topleft=(20, 20))
        ai_avatar_rect = self.ui.ai_avatar.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        return human_avatar_rect, ai_avatar_rect

    def run(self):
        """
        Runs the main game loop.
        """
        while True:
            if self.current_state == STATE_MENU:
                self.ui.display_menu(self.high_scores)
                self.handle_menu_events()
            elif self.current_state == STATE_GAME:
                self.game_loop()
            elif self.current_state == STATE_GAME_OVER:
                self.handle_game_over()
            else:
                logger.error(f"Unknown game state: {self.current_state}")
                break

    def handle_menu_events(self):
        """
        Handles events in the main menu.
        """
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.quit_game()
                    elif event.key == pygame.K_s:
                        waiting = False
                        self.current_state = STATE_GAME
                        logger.debug("Starting the game from menu.")
            self.clock.tick(60)

    def handle_game_over(self):
        """
        Handles the game over screen.
        """
        self.ui.display_game_over(self.player.score, self.ai_player.score, self.high_scores)
        self.update_high_scores(self.player.score)

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.quit_game()
                    elif event.key == pygame.K_r:
                        waiting = False
                        self.reset_game()
            self.clock.tick(60)

    def reset_game(self):
        """
        Resets the game to start anew.
        """
        self.player = Player(self.create_grid())
        self.ai_player = AIPlayer(self.create_grid(), ai_move_queue=self.ai_move_priority_queue)
        self.player_ghost = GhostPiece(self.player)
        self.ai_ghost = GhostPiece(self.ai_player)
        self.ui.reset_avatars()
        self.current_state = STATE_MENU
        self.population = [self.random_move_sequence() for _ in range(POPULATION_SIZE)]
        logger.debug("Game has been reset.")

    def quit_game(self):
        """
        Gracefully quits the game.
        """
        self.stop_event.set()
        self.ai_thread.join(timeout=1)
        pygame.mixer.music.stop()
        sleep(1)
        pygame.quit()
        exit()

    def game_loop(self):
        """
        Main game loop handling game logic and rendering.
        """
        while self.current_state == STATE_GAME and not self.player.game_over and not self.ai_player.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                        if self.paused:
                            logger.debug("Game paused.")
                        else:
                            logger.debug("Game resumed.")
                    elif event.key == pygame.K_m:
                        # Mute or unmute the music
                        if pygame.mixer.music.get_volume() > 0:
                            pygame.mixer.music.set_volume(0)
                            logger.debug("Background music muted.")
                        else:
                            pygame.mixer.music.set_volume(0.5)  # Reset to desired volume
                            logger.debug("Background music unmuted.")
                    elif not self.paused:
                        if event.key == pygame.K_DOWN:
                            if self.player.valid_move(self.player.current_piece, self.player.current_piece.x, self.player.current_piece.y + 1):
                                self.player.current_piece.y += 1
                                logger.debug(f"Player moved down to ({self.player.current_piece.x}, {self.player.current_piece.y})")
                        elif event.key == pygame.K_LEFT:
                            self.player.move("left")
                        elif event.key == pygame.K_RIGHT:
                            self.player.move("right")
                        elif event.key == pygame.K_UP:
                            self.player.move("rotate")
                        elif event.key == pygame.K_SPACE:
                            self.player.drop()

            if not self.paused:
                delta_time = self.clock.tick(60) / 1000  # Convert milliseconds to seconds
                self.player.fall_time_accumulator += delta_time
                self.ai_player.fall_time_accumulator += delta_time

                # Player Fall Logic
                if self.player.fall_time_accumulator >= self.player.fall_speed:
                    self.player.fall_time_accumulator -= self.player.fall_speed
                    if self.player.valid_move(self.player.current_piece, self.player.current_piece.x, self.player.current_piece.y + 1):
                        self.player.current_piece.y += 1
                    else:
                        self.player.lock_piece()

                        if self.player.game_over:
                            self.current_state = STATE_GAME_OVER
                            logger.debug("Player game over.")
                            break

                        # Enqueue AI request
                        current_time = time.time()
                        if current_time - self.last_ai_request_time >= 1.0:
                            if self.ai_player.current_piece:
                                game_state = self.get_game_state(self.ai_player.current_piece, self.ai_player.grid, self.ai_player.score, self.ai_player.lines_cleared)
                                self.ai_request_queue.put((self.ai_player.current_piece, self.ai_player.grid, self.ai_player.score, self.ai_player.lines_cleared))
                                self.last_ai_request_time = current_time
                                logger.debug("Enqueued AI request for the new AI piece.")
                            else:
                                logger.debug("AI Player has no current_piece. Skipping AI request.")

                # AI Fall Logic
                if self.ai_player.fall_time_accumulator >= self.ai_player.fall_speed:
                    self.ai_player.fall_time_accumulator -= self.ai_player.fall_speed
                    if self.ai_player.valid_move(self.ai_player.current_piece, self.ai_player.current_piece.x, self.ai_player.current_piece.y + 1):
                        self.ai_player.current_piece.y += 1
                    else:
                        self.ai_player.lock_piece()

                        if self.ai_player.game_over:
                            self.current_state = STATE_GAME_OVER
                            logger.debug("AI game over.")
                            break

                        # Enqueue AI request
                        current_time = time.time()
                        if current_time - self.last_ai_request_time >= 1.0:
                            if self.ai_player.current_piece:
                                game_state = self.get_game_state(self.ai_player.current_piece, self.ai_player.grid, self.ai_player.score, self.ai_player.lines_cleared)
                                self.ai_request_queue.put((self.ai_player.current_piece, self.ai_player.grid, self.ai_player.score, self.ai_player.lines_cleared))
                                self.last_ai_request_time = current_time
                                logger.debug("Enqueued AI request for the new AI piece.")
                            else:
                                logger.debug("AI Player has no current_piece. Skipping AI request.")

                # Evolve GA Population and Generate AI Moves
                current_time = time.time()
                if current_time - self.last_ai_request_time >= 1.0:
                    if self.ai_player.current_piece:
                        game_state = self.get_game_state(self.ai_player.current_piece, self.ai_player.grid, self.ai_player.score, self.ai_player.lines_cleared)
                        self.population = self.evolve_population(self.population, game_state, None)  # Replace None with your AI model if needed
                        fitness_scores = [self.fitness_function(individual, game_state, None) for individual in self.population]  # Replace None with your AI model if needed
                        best_move_sequence = self.population[fitness_scores.index(max(fitness_scores))]

                        # Enqueue the best move sequence
                        for move in best_move_sequence:
                            self.ai_move_priority_queue.put(move)

                        self.last_ai_request_time = current_time
                        logger.debug(f"Enqueued Best Move Sequence: {best_move_sequence}")
                    else:
                        logger.debug("AI Player has no current_piece. Skipping evolve_population.")

                # Process AI moves from the AI move queue
                while not self.ai_move_priority_queue.empty():
                    if current_time - self.last_ai_move_time >= 1.0:
                        move = self.ai_move_priority_queue.get()
                        self.apply_move(move, self.ai_player)
                        self.last_ai_move_time = current_time
                        logger.debug(f"Applied AI Move: {move}")
                    else:
                        break

                # Monitor CPU and Memory Usage
                self.ui.display_cpu_memory_usage()
                logger.debug(f"CPU and Memory Usage displayed.")

            # Rendering
            self.screen.fill(BLACK)

            # Draw Ghost Pieces
            self.player_ghost.draw(self.screen, 50, DESIRED_OFFSET_Y)
            self.ai_ghost.draw(self.screen, SCREEN_WIDTH // 2 + 50, DESIRED_OFFSET_Y)

            # Draw Grids
            self.draw_grid(self.player.grid, 50, DESIRED_OFFSET_Y)
            self.draw_grid(self.ai_player.grid, SCREEN_WIDTH // 2 + 50, DESIRED_OFFSET_Y)

            # Draw Current Pieces
            self.draw_piece(self.player.current_piece, 50, DESIRED_OFFSET_Y)
            self.draw_piece(self.ai_player.current_piece, SCREEN_WIDTH // 2 + 50, DESIRED_OFFSET_Y)

            # Draw UI Panels
            pygame.draw.rect(self.screen, (50, 50, 50), (0, 0, SCREEN_WIDTH, 50))  # Top panel

            # Display Scores and Lines
            self.ui.display_scores(self.player, self.ai_player)

            # Highlight Active Player
            active_player = "AI" if self.ai_player.score > self.player.score else "Human"
            self.ui.highlight_avatar(active_player)

            # Draw Avatars and Labels on Top
            self.ui.draw_avatars()
            self.ui.render_labels()

            # If paused, display paused message
            if self.paused:
                self.ui.display_pause_overlay()

            # Display CPU and Memory Usage
            self.ui.display_cpu_memory_usage()

            pygame.display.flip()


    def draw_grid(self, grid, offset_x, offset_y):
        """
        Draws the Tetris grid.
        """
        for y, row in enumerate(grid):
            for x, color in enumerate(row):
                if color:
                    pygame.draw.rect(self.screen, color, (offset_x + x * BLOCK_SIZE, offset_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(self.screen, WHITE, (offset_x + x * BLOCK_SIZE, offset_y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    def draw_piece(self, piece, offset_x, offset_y):
        """
        Draws a Tetris piece on the screen.
        """
        if piece:
            for i, row in enumerate(piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, piece.color,
                                         (offset_x + piece.x * BLOCK_SIZE + j * BLOCK_SIZE,
                                          offset_y + piece.y * BLOCK_SIZE + i * BLOCK_SIZE,
                                          BLOCK_SIZE, BLOCK_SIZE))

    def ai_worker_deprecated(self, ai_request_queue, ai_move_priority_queue, stop_event):
        """
        Deprecated AI worker method. Kept for reference.
        """
        pass  # Original AI worker implementation (now integrated into the Game class)

    # Additional utility methods can be added here

import os
import pygame

def play_audio(file_path):
    if file_path and os.path.exists(file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(-1)  # Loop forever
        print("Playing background music...")
    else:
        print("Audio file not found.")

file_path = "tetris_remix.mp3"  # Replace with the local MP3 file
play_audio(file_path)


# ============================== #
#           Execution            #
# ============================== #

if __name__ == "__main__":
    play_audio('tetris_remix.mp3')

    game = Game()
    game.run()
