import pygame
import random
import time

pygame.init()
pygame.mixer.init()

# Load and play background music
pygame.mixer.music.load("tetris_theme.mp3")
pygame.mixer.music.play(-1)  # The -1 makes the music play in a loop

# Define some parameters
WIDTH = 400
HEIGHT = 550
BLOCK_SIZE = 20
INITIAL_FRAMES_PER_SECOND = 10
MAX_FRAMES_PER_SECOND = 20
SPEED_INCREMENT_THRESHOLD = 5  # Increase speed after every 50 points

# Define the colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define the shapes (Corrected the shapes for standard Tetris dimensions)
SHAPES = [
    [[1, 1], [1, 1]],  # Square
    [[1, 1, 1, 1]],  # I-Shape
    [[1, 0, 0], [1, 1, 1]],  # J-Shape
    [[0, 0, 1], [1, 1, 1]],  # L-Shape
    [[0, 1, 1], [1, 1, 0]],  # S-Shape
    [[1, 1, 0], [0, 1, 1]],  # Z-Shape
    [[0, 1, 0], [1, 1, 1]]  # T-Shape
]

class Piece:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.x = int(WIDTH / 2 / BLOCK_SIZE) - len(self.shape[0]) // 2
        self.y = -len(self.shape)
        self.shape = random.choice(SHAPES)

    def rotate(self):
        # Rotate the piece 90 degrees
        self.shape = [list(reversed(col)) for col in zip(*self.shape)]

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
                    if block_y < 0 or block_x < 0 or block_x >= WIDTH // BLOCK_SIZE or block_y >= HEIGHT // BLOCK_SIZE or board[block_y][block_x] == 1:
                        return True
        return False

class Game:
    def __init__(self):
        self.board = [[0] * (WIDTH // BLOCK_SIZE) for _ in range(HEIGHT // BLOCK_SIZE)]
        self.piece = Piece()
        self.score = 0
        self.frames_per_second = INITIAL_FRAMES_PER_SECOND

    def draw_board(self, screen):
        for i in range(HEIGHT // BLOCK_SIZE):
            for j in range(WIDTH // BLOCK_SIZE):
                color = WHITE if self.board[i][j] == 1 else BLACK
                pygame.draw.rect(screen, color, (j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_piece(self, screen):
        
        for i in range(len(self.piece.shape)):
            for j in range(len(self.piece.shape[i])):
                if self.piece.shape[i][j] == 1:
                    #print(self.score)
                    pygame.draw.rect(screen, WHITE, (self.piece.x * BLOCK_SIZE + j * BLOCK_SIZE, self.piece.y * BLOCK_SIZE + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def update(self):
        self.piece.move_down()
        if self.piece.is_intersecting(self.board):
            self.piece.move_up()
            self.lock_piece()
            self.check_line()
            self.piece = Piece()

    def lock_piece(self):
        for i in range(len(self.piece.shape)):
            for j in range(len(self.piece.shape[i])):
                if self.piece.shape[i][j] == 1:
                    self.board[self.piece.y + i][self.piece.x + j] = 1

    def check_line(self):
        full_lines = 0
        for row in range(HEIGHT // BLOCK_SIZE):
            if all(self.board[row]):
                full_lines += 1
                del self.board[row]
                self.board.insert(0, [0] * (WIDTH // BLOCK_SIZE))
        self.score += full_lines ** 2
        # Adjust the frame rate based on score
        if self.score % SPEED_INCREMENT_THRESHOLD == 0 and self.frames_per_second < MAX_FRAMES_PER_SECOND:
            self.frames_per_second += 0.05

    def run(self):
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Tetris')
        clock = pygame.time.Clock()
        running = True
        start_time = time.time()
        while running:
            clock.tick(self.frames_per_second)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.piece.move_left()
                        if self.piece.is_intersecting(self.board):
                            self.piece.move_right()
                    if event.key == pygame.K_RIGHT:
                        self.piece.move_right()
                        if self.piece.is_intersecting(self.board):
                            self.piece.move_left()
                    if event.key == pygame.K_UP:
                        self.piece.rotate()
                        if self.piece.is_intersecting(self.board):
                            self.piece.rotate()  # Rotate back to original if intersecting
            self.update()
            screen.fill(BLACK)
            self.draw_board(screen)
            self.draw_piece(screen)
            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()