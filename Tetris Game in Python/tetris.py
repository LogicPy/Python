import pygame
import random
import time
import sys
import os

pygame.init()
pygame.mixer.init()

# Load and play background music
if os.path.exists("tetris_theme.mp3"):
    pygame.mixer.music.load("tetris_theme.mp3")
    pygame.mixer.music.play(-1)  # The -1 makes the music play in a loop
else:
    print("Background music file 'tetris_theme.mp3' not found. Proceeding without music.")

# Define some parameters
WIDTH = 400
HEIGHT = 550
BLOCK_SIZE = 20
INITIAL_FRAMES_PER_SECOND = 10
MAX_FRAMES_PER_SECOND = 20
SPEED_INCREMENT_SCORE = 50  # Increase speed after every 50 points

# Define the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Assign colors to shapes
SHAPE_COLORS = [
    GREEN,    # Square
    CYAN,     # I-Shape
    BLUE,     # J-Shape
    ORANGE,   # L-Shape
    RED,      # S-Shape
    MAGENTA,  # Z-Shape
    YELLOW    # T-Shape
]

# Define the shapes (Standard Tetris dimensions)
SHAPES = [
    [[1, 1],
     [1, 1]],  # Square

    [[1, 1, 1, 1]],  # I-Shape

    [[1, 0, 0],
     [1, 1, 1]],  # J-Shape

    [[0, 0, 1],
     [1, 1, 1]],  # L-Shape

    [[0, 1, 1],
     [1, 1, 0]],  # S-Shape

    [[1, 1, 0],
     [0, 1, 1]],  # Z-Shape

    [[0, 1, 0],
     [1, 1, 1]]   # T-Shape
]

class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = SHAPE_COLORS[SHAPES.index(self.shape)]
        # Center the piece without exceeding horizontal boundaries
        self.x = (WIDTH // BLOCK_SIZE - len(self.shape[0])) // 2
        self.y = -len(self.shape) + 1  # Spawn slightly higher

    def rotate(self):
        # Rotate the piece 90 degrees clockwise
        self.shape = [list(reversed(col)) for col in zip(*self.shape)]

    def rotate_counter_clockwise(self):
        # Rotate the piece 90 degrees counter-clockwise
        self.shape = [list(col) for col in zip(*self.shape)][::-1]

    def move_down(self):
        self.y += 1

    def move_up(self):
        self.y -= 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def is_intersecting(self, board):
        for i in range(len(self.shape)):
            for j in range(len(self.shape[i])):
                if self.shape[i][j] == 1:
                    block_y = self.y + i
                    block_x = self.x + j

                    # Check horizontal boundaries
                    if block_x < 0 or block_x >= WIDTH // BLOCK_SIZE:
                        return True

                    # Check vertical boundaries
                    if block_y >= HEIGHT // BLOCK_SIZE:
                        return True

                    # Check collision only if the block is within the board
                    if block_y >= 0 and board[block_y][block_x] > 0:
                        return True
        return False

class Game:
    def __init__(self):
        self.board = [[0] * (WIDTH // BLOCK_SIZE) for _ in range(HEIGHT // BLOCK_SIZE)]
        self.piece = Piece()
        self.next_piece = Piece()
        self.score = 0
        self.high_score = self.load_high_score()
        self.frames_per_second = INITIAL_FRAMES_PER_SECOND
        self.game_over = False
        self.font = pygame.font.SysFont('Arial', 24)
        self.state = 'menu'  # Possible states: 'menu', 'playing', 'game_over', 'paused'

    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            with open("highscore.txt", "r") as file:
                try:
                    return int(file.read())
                except:
                    return 0
        return 0

    def save_high_score(self):
        if self.score > self.high_score:
            with open("highscore.txt", "w") as file:
                file.write(str(self.score))

    def draw_board(self, screen):
        for i in range(HEIGHT // BLOCK_SIZE):
            for j in range(WIDTH // BLOCK_SIZE):
                color = SHAPE_COLORS[self.board[i][j]-1] if self.board[i][j] > 0 else BLACK
                pygame.draw.rect(screen, color, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, GREY, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)  # Grid lines

    def draw_piece(self, screen, piece):
        for i in range(len(piece.shape)):
            for j in range(len(piece.shape[i])):
                if piece.shape[i][j] == 1:
                    pygame.draw.rect(screen, piece.color, 
                                     (piece.x * BLOCK_SIZE + j * BLOCK_SIZE, 
                                      piece.y * BLOCK_SIZE + i * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, GREY, 
                                     (piece.x * BLOCK_SIZE + j * BLOCK_SIZE, 
                                      piece.y * BLOCK_SIZE + i * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE), 1)  # Grid lines

    def draw_next_piece(self, screen):
        label = self.font.render('Next:', True, WHITE)
        screen.blit(label, (WIDTH + 20, 20))
        for i in range(len(self.next_piece.shape)):
            for j in range(len(self.next_piece.shape[i])):
                if self.next_piece.shape[i][j] == 1:
                    pygame.draw.rect(screen, self.next_piece.color, 
                                     (WIDTH + 20 + j * BLOCK_SIZE, 
                                      50 + i * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(screen, GREY, 
                                     (WIDTH + 20 + j * BLOCK_SIZE, 
                                      50 + i * BLOCK_SIZE, 
                                      BLOCK_SIZE, BLOCK_SIZE), 1)  # Grid lines

    def draw_score(self, screen):
        score_label = self.font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_label, (WIDTH + 20, 200))
        high_score_label = self.font.render(f'High Score: {self.high_score}', True, WHITE)
        screen.blit(high_score_label, (WIDTH + 20, 230))

    def draw_game_over(self, screen):
        over_font = pygame.font.SysFont('Arial', 48)
        over_label = over_font.render('GAME OVER', True, RED)
        screen.blit(over_label, (WIDTH // 2 - over_label.get_width() // 2, HEIGHT // 2 - over_label.get_height() // 2))
        restart_label = self.font.render('Press R to Restart or Q to Quit', True, WHITE)
        screen.blit(restart_label, (WIDTH // 2 - restart_label.get_width() // 2, HEIGHT // 2 + over_label.get_height()))

    def draw_menu(self, screen):
        menu_font = pygame.font.SysFont('Arial', 48)
        menu_label = menu_font.render('TETRIS', True, WHITE)
        screen.blit(menu_label, (WIDTH // 2 - menu_label.get_width() // 2, HEIGHT // 2 - menu_label.get_height()))
        prompt_font = pygame.font.SysFont('Arial', 24)
        prompt_label = prompt_font.render('Press ENTER to Play or Q to Quit', True, WHITE)
        screen.blit(prompt_label, (WIDTH // 2 - prompt_label.get_width() // 2, HEIGHT // 2 + 10))

    def draw_pause(self, screen):
        pause_font = pygame.font.SysFont('Arial', 48)
        pause_label = pause_font.render('PAUSED', True, WHITE)
        screen.blit(pause_label, (WIDTH // 2 - pause_label.get_width() // 2, HEIGHT // 2 - pause_label.get_height() // 2))
        resume_label = self.font.render('Press P to Resume', True, WHITE)
        screen.blit(resume_label, (WIDTH // 2 - resume_label.get_width() // 2, HEIGHT // 2 + pause_label.get_height()))

    def update(self):
        self.piece.move_down()
        if self.piece.is_intersecting(self.board):
            self.piece.move_up()
            self.lock_piece()
            self.check_line()
            self.piece = self.next_piece
            self.next_piece = Piece()
            if self.piece.is_intersecting(self.board):
                self.game_over = True
                self.save_high_score()

    def lock_piece(self):
        for i in range(len(self.piece.shape)):
            for j in range(len(self.piece.shape[i])):
                if self.piece.shape[i][j] == 1:
                    board_y = self.piece.y + i
                    board_x = self.piece.x + j
                    if 0 <= board_y < HEIGHT // BLOCK_SIZE and 0 <= board_x < WIDTH // BLOCK_SIZE:
                        self.board[board_y][board_x] = SHAPE_COLORS.index(self.piece.color) + 1
                        # Debugging Statement
                        print(f"Locked piece at ({board_x}, {board_y}) with value {self.board[board_y][board_x]}")

    def check_line(self):
        full_lines = 0
        for row in range(HEIGHT // BLOCK_SIZE):
            if all(self.board[row]):
                full_lines += 1
                del self.board[row]
                self.board.insert(0, [0] * (WIDTH // BLOCK_SIZE))
        if full_lines > 0:
            self.score += full_lines ** 2  # Scoring: 1 line = 1, 2 lines = 4, etc.
            # Adjust the frame rate based on score
            level = self.score // SPEED_INCREMENT_SCORE
            if level > 0 and self.frames_per_second < MAX_FRAMES_PER_SECOND:
                self.frames_per_second = min(INITIAL_FRAMES_PER_SECOND + level, MAX_FRAMES_PER_SECOND)

    def run(self):
        screen_width = WIDTH + 200  # Extra space for next piece and score
        screen = pygame.display.set_mode((screen_width, HEIGHT))
        pygame.display.set_caption('Tetris')
        clock = pygame.time.Clock()
        running = True

        while running:
            clock.tick(self.frames_per_second)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.save_high_score()
                if event.type == pygame.KEYDOWN:
                    if self.state == 'menu':
                        if event.key == pygame.K_RETURN:
                            self.state = 'playing'
                        if event.key == pygame.K_q:
                            running = False
                            self.save_high_score()
                    elif self.state == 'playing':
                        if not self.game_over:
                            if event.key == pygame.K_LEFT:
                                self.piece.move_left()
                                if self.piece.is_intersecting(self.board):
                                    self.piece.move_right()
                            if event.key == pygame.K_RIGHT:
                                self.piece.move_right()
                                if self.piece.is_intersecting(self.board):
                                    self.piece.move_left()
                            if event.key == pygame.K_DOWN:
                                self.piece.move_down()
                                if self.piece.is_intersecting(self.board):
                                    self.piece.move_up()
                            if event.key == pygame.K_UP:
                                self.piece.rotate()
                                if self.piece.is_intersecting(self.board):
                                    # Implement wall kick: try moving piece right, then left
                                    self.piece.move_right()
                                    if self.piece.is_intersecting(self.board):
                                        self.piece.move_left()
                                        self.piece.rotate_counter_clockwise()  # Rotate back if still intersecting
                            if event.key == pygame.K_p:
                                self.pause(screen)
                        else:
                            if event.key == pygame.K_r:
                                self.reset()
                                self.state = 'playing'
                            if event.key == pygame.K_q:
                                running = False
                                self.save_high_score()
                    elif self.state == 'game_over':
                        if event.key == pygame.K_r:
                            self.reset()
                            self.state = 'playing'
                        if event.key == pygame.K_q:
                            running = False
                            self.save_high_score()
                    elif self.state == 'paused':
                        if event.key == pygame.K_p:
                            self.state = 'playing'

            if self.state == 'playing' and not self.game_over:
                self.update()

            screen.fill(BLACK)

            if self.state == 'menu':
                self.draw_menu(screen)
            elif self.state == 'playing':
                self.draw_board(screen)
                if not self.game_over:
                    self.draw_piece(screen, self.piece)
                    self.draw_next_piece(screen)
                    self.draw_score(screen)
                else:
                    self.draw_game_over(screen)
                    self.draw_score(screen)
            elif self.state == 'game_over':
                self.draw_game_over(screen)
                self.draw_score(screen)
            elif self.state == 'paused':
                self.draw_board(screen)
                self.draw_piece(screen, self.piece)
                self.draw_next_piece(screen)
                self.draw_score(screen)
                self.draw_pause(screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def pause(self, screen):
        self.state = 'paused'

    def reset(self):
        self.board = [[0] * (WIDTH // BLOCK_SIZE) for _ in range(HEIGHT // BLOCK_SIZE)]
        self.piece = Piece()
        self.next_piece = Piece()
        self.score = 0
        self.frames_per_second = INITIAL_FRAMES_PER_SECOND
        self.game_over = False

if __name__ == '__main__':
    game = Game()
    game.run()
