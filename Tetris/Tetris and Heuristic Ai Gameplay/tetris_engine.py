"""Core Tetris game engine - pure logic, no rendering."""

import random
from enum import Enum, auto

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# Infinite scroll settings
SCROLL_TRIGGER_ROW = BOARD_HEIGHT // 2  # scroll when stack reaches viewport middle
SCROLL_EXPAND_CHUNK = 10                # rows to add when expanding board

CELL_EMPTY = 0

SHAPES = {
    "I": [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(0, 0), (0, 1), (0, 2), (0, 3)],
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "T": [
        [(0, 0), (1, 0), (2, 0), (1, 1)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (1, 0), (2, 0), (0, 1)],
        [(0, 0), (0, 1), (0, 2), (1, 2)],
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
    "L": [
        [(0, 0), (1, 0), (2, 0), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (0, 2)],
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
    ],
}

NEON_COLORS = {
    "I": (0, 240, 255),
    "O": (255, 210, 0),
    "T": (200, 0, 255),
    "S": (0, 255, 100),
    "Z": (255, 30, 80),
    "J": (80, 100, 255),
    "L": (255, 130, 0),
}

PIECE_TYPES = list(SHAPES.keys())


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class Piece:
    def __init__(self, shape_type):
        self.shape_type = shape_type
        self.rotation = 0
        self.color = NEON_COLORS[shape_type]
        self.x = BOARD_WIDTH // 2 - 2
        self.y = 0
        self.blocks = SHAPES[shape_type][self.rotation]

    def cells(self, dx=0, dy=0, dr=0):
        rot = (self.rotation + dr) % 4
        shape = SHAPES[self.shape_type][rot]
        return [(self.x + bx + dx, self.y + by + dy) for bx, by in shape]

    def rotate_cw(self):
        self.rotation = (self.rotation + 1) % 4
        self.blocks = SHAPES[self.shape_type][self.rotation]

    def rotate_ccw(self):
        self.rotation = (self.rotation - 1) % 4
        self.blocks = SHAPES[self.shape_type][self.rotation]


class TetrisEngine:
    def __init__(self):
        self.board = [[CELL_EMPTY] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.state = GameState.MENU
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.current_piece = None
        self.next_piece = None
        self.bag = []
        self.last_cleared_rows = []
        # Infinite scroll state
        self.infinite_scroll = False
        self.scroll_anim_offset = 0.0   # pixel offset for smooth scroll animation (0..1)
        self.scroll_anim_active = False
        self.total_scroll = 0           # total rows scrolled down (for score/display)
        self._new_game()

    def _refill_bag(self):
        self.bag = PIECE_TYPES[:]
        random.shuffle(self.bag)

    def _spawn_piece(self):
        if not self.bag:
            self._refill_bag()
        shape_type = self.bag.pop()
        piece = Piece(shape_type)
        if self._collides(piece.cells()):
            self.state = GameState.GAME_OVER
        return piece

    def _new_game(self):
        self.board = [[CELL_EMPTY] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.combo = 0
        self.scroll_anim_offset = 0.0
        self.scroll_anim_active = False
        self.total_scroll = 0
        self._refill_bag()
        self.current_piece = self._spawn_piece()
        self.next_piece = self._spawn_piece()
        self.state = GameState.PLAYING

    def restart(self):
        self._new_game()

    def _collides(self, cells):
        board_h = len(self.board)
        for cx, cy in cells:
            if cx < 0 or cx >= BOARD_WIDTH:
                return True
            if cy >= board_h:
                return True
            if cy >= 0 and self.board[cy][cx] != CELL_EMPTY:
                return True
        return False

    def _lock_piece(self):
        board_h = len(self.board)
        for cx, cy in self.current_piece.cells():
            if 0 <= cy < board_h and 0 <= cx < BOARD_WIDTH:
                self.board[cy][cx] = self.current_piece.shape_type
        self._clear_lines()
        self._check_scroll()
        self.current_piece = self.next_piece
        self.next_piece = self._spawn_piece()

    def _clear_lines(self):
        cleared = 0
        cleared_rows = []
        new_board = []
        for row_idx, row in enumerate(self.board):
            if CELL_EMPTY in row:
                new_board.append(row)
            else:
                cleared += 1
                cleared_rows.append(row_idx)
        for _ in range(cleared):
            new_board.insert(0, [CELL_EMPTY] * BOARD_WIDTH)
        self.board = new_board
        if cleared > 0:
            self.combo += 1
            base_points = [0, 100, 300, 500, 800]
            pts = base_points[min(cleared, 4)] + (cleared - 4) * 400 if cleared > 4 else base_points[cleared]
            self.score += pts * self.level + self.combo * 50
            self.lines += cleared
            self.level = self.lines // 10 + 1
            self.last_cleared_rows = cleared_rows
        else:
            self.combo = 0
            self.last_cleared_rows = []

    def _highest_block_row(self):
        """Return the row index of the highest block, or len(board) if empty."""
        for y, row in enumerate(self.board):
            for x in range(BOARD_WIDTH):
                if row[x] != CELL_EMPTY:
                    return y
        return len(self.board)

    def _check_scroll(self):
        """If infinite scroll is on and stack is too high, scroll the board down."""
        if not self.infinite_scroll:
            return
        highest = self._highest_block_row()
        if highest < SCROLL_TRIGGER_ROW:
            scroll_needed = SCROLL_TRIGGER_ROW - highest
            for _ in range(scroll_needed):
                self.board.insert(0, [CELL_EMPTY] * BOARD_WIDTH)
            self._trim_board()
            self.total_scroll += scroll_needed
            self.score += scroll_needed * 10
            # Trigger smooth scroll animation
            self.scroll_anim_offset = float(scroll_needed)
            self.scroll_anim_active = True

    def update_scroll_anim(self):
        """Animate the scroll offset toward 0. Call each frame."""
        if not self.scroll_anim_active:
            return
        self.scroll_anim_offset *= 0.85
        if self.scroll_anim_offset < 0.01:
            self.scroll_anim_offset = 0.0
            self.scroll_anim_active = False

    def _trim_board(self):
        """Remove empty rows from the bottom beyond the buffer zone."""
        target_size = BOARD_HEIGHT + SCROLL_EXPAND_CHUNK
        while len(self.board) > target_size:
            # Only trim if the bottom row is empty
            if self.board[-1].count(CELL_EMPTY) == BOARD_WIDTH:
                self.board.pop()
            else:
                break

    def move_left(self):
        if self.state != GameState.PLAYING:
            return
        if not self._collides(self.current_piece.cells(dx=-1)):
            self.current_piece.x -= 1

    def move_right(self):
        if self.state != GameState.PLAYING:
            return
        if not self._collides(self.current_piece.cells(dx=1)):
            self.current_piece.x += 1

    def soft_drop(self):
        if self.state != GameState.PLAYING:
            return False
        if not self._collides(self.current_piece.cells(dy=1)):
            self.current_piece.y += 1
            self.score += 1
            return True
        self._lock_piece()
        return False

    def hard_drop(self):
        if self.state != GameState.PLAYING:
            return
        drop_distance = 0
        while not self._collides(self.current_piece.cells(dy=drop_distance + 1)):
            drop_distance += 1
        self.current_piece.y += drop_distance
        self.score += drop_distance * 2
        self._lock_piece()

    def rotate(self, direction=1):
        if self.state != GameState.PLAYING:
            return
        if direction == 1:
            self.current_piece.rotate_cw()
        else:
            self.current_piece.rotate_ccw()
        if self._collides(self.current_piece.cells()):
            for kick in [-1, 1, -2, 2]:
                if not self._collides(self.current_piece.cells(dx=kick)):
                    self.current_piece.x += kick
                    return
            if direction == 1:
                self.current_piece.rotate_ccw()
            else:
                self.current_piece.rotate_cw()

    def ghost_cells(self):
        if not self.current_piece:
            return []
        dy = 0
        while not self._collides(self.current_piece.cells(dy=dy + 1)):
            dy += 1
        return self.current_piece.cells(dy=dy)

    def get_fall_speed(self):
        return max(0.05, 0.8 - (self.level - 1) * 0.07)

    def toggle_pause(self):
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def toggle_infinite_scroll(self):
        self.infinite_scroll = not self.infinite_scroll
        return self.infinite_scroll
