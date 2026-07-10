"""Heuristic AI autoplayer for Tetris — evaluates all placements and picks the best."""

import copy

from tetris_engine import (
    BOARD_WIDTH,
    BOARD_HEIGHT,
    CELL_EMPTY,
    SHAPES,
    Piece,
    TetrisEngine,
)


class TetrisAI:
    """Pierre Dellacherie-style heuristic AI.

    Evaluates every reachable (rotation, x) placement for the current piece,
    simulates the lock + line clear, scores the resulting board, and returns
    the best (rotation, target_x) to aim for.
    """

    # Heuristic weights (tuned for aggressive line-clearing play)
    W_HEIGHT = -0.51
    W_LINES = 0.76
    W_HOLES = -0.36
    W_BUMPINESS = -0.18
    W_WELL = -0.15

    def __init__(self):
        self.target_rotation = 0
        self.target_x = 0
        self.current_plan = None

    def _simulate_drop(self, board, piece_type, rotation, px):
        """Drop a piece at (rotation, px) on a copy of the board. Returns (board, lines_cleared) or None."""
        shape = SHAPES[piece_type][rotation]
        test_board = [row[:] for row in board]

        # Find the lowest y where the piece can sit
        dy = 0
        while True:
            placed = True
            for bx, by in shape:
                cx = px + bx
                cy = by + dy
                if cx < 0 or cx >= BOARD_WIDTH:
                    return None
                if cy >= BOARD_HEIGHT:
                    return None
                if cy >= 0 and test_board[cy][cx] != CELL_EMPTY:
                    return None
                # Check cell below
                below_cy = cy + 1
                if below_cy >= BOARD_HEIGHT:
                    placed = False
                    break
                if below_cy >= 0 and test_board[below_cy][cx] != CELL_EMPTY:
                    placed = False
                    break
            if not placed:
                break
            dy += 1

        # Place the piece
        for bx, by in shape:
            cx = px + bx
            cy = by + dy
            if 0 <= cy < BOARD_HEIGHT and 0 <= cx < BOARD_WIDTH:
                test_board[cy][cx] = piece_type

        # Clear lines
        new_board = []
        lines_cleared = 0
        for row in test_board:
            if CELL_EMPTY not in row:
                lines_cleared += 1
            else:
                new_board.append(row)
        while len(new_board) < BOARD_HEIGHT:
            new_board.insert(0, [CELL_EMPTY] * BOARD_WIDTH)

        return new_board, lines_cleared

    def _evaluate_board(self, board, lines_cleared):
        """Score a board position. Higher = better."""
        heights = self._column_heights(board)
        holes = self._count_holes(board, heights)
        bumpiness = sum(abs(heights[i] - heights[i + 1]) for i in range(BOARD_WIDTH - 1))
        agg_height = sum(heights)

        # Deep wells (gaps of 3+ on one side) are bad unless going for Tetris
        well = 0
        if heights[-1] <= max(heights[:-1]) - 3 if len(heights) > 1 else False:
            well = max(heights) - heights[-1]

        score = (
            self.W_HEIGHT * agg_height
            + self.W_LINES * lines_cleared
            + self.W_HOLES * holes
            + self.W_BUMPINESS * bumpiness
            + self.W_WELL * well
        )
        return score

    def _column_heights(self, board):
        heights = [0] * BOARD_WIDTH
        for x in range(BOARD_WIDTH):
            for y in range(BOARD_HEIGHT):
                if board[y][x] != CELL_EMPTY:
                    heights[x] = BOARD_HEIGHT - y
                    break
        return heights

    def _count_holes(self, board, heights):
        holes = 0
        for x in range(BOARD_WIDTH):
            for y in range(BOARD_HEIGHT):
                if board[y][x] == CELL_EMPTY and (BOARD_HEIGHT - y) < heights[x]:
                    holes += 1
        return holes

    def best_placement(self, engine):
        """Find the best (rotation, target_x) for the current piece."""
        if not engine.current_piece:
            return None

        piece_type = engine.current_piece.shape_type
        best_score = float("-inf")
        best_rot = 0
        best_x = engine.current_piece.x

        for rotation in range(4):
            shape = SHAPES[piece_type][rotation]
            min_bx = min(b[0] for b in shape)
            max_bx = max(b[0] for b in shape)

            for px in range(-min_bx, BOARD_WIDTH - max_bx):
                result = self._simulate_drop(engine.board, piece_type, rotation, px)
                if result is None:
                    continue
                sim_board, lines_cleared = result
                score = self._evaluate_board(sim_board, lines_cleared)

                # Prefer placements that clear more lines (tie-breaker)
                if score > best_score:
                    best_score = score
                    best_rot = rotation
                    best_x = px

        return best_rot, best_x, best_score

    def compute_plan(self, engine):
        """Compute the full movement plan for the current piece."""
        result = self.best_placement(engine)
        if result is None:
            self.current_plan = None
            return
        best_rot, best_x, _ = result
        self.target_rotation = best_rot
        self.target_x = best_x
        self.current_plan = True

    def get_next_action(self, engine):
        """Return the next action string to execute, or None if done.

        Actions: 'rotate', 'left', 'right', 'drop', 'wait'
        """
        if not self.current_plan:
            self.compute_plan(engine)
            if not self.current_plan:
                return None

        # First: rotate to target rotation
        if engine.current_piece and engine.current_piece.rotation != self.target_rotation:
            return "rotate"

        # Then: move horizontally to target x
        if engine.current_piece and engine.current_piece.x < self.target_x:
            return "right"
        elif engine.current_piece and engine.current_piece.x > self.target_x:
            return "left"

        # Finally: hard drop
        self.current_plan = None
        return "drop"