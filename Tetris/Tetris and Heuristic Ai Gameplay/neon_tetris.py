"""
Neon cyber-punk Tetris renderer and game loop using pygame.

Visual style: glowing 3D blocks with neon edges, dark grid background,
particle effects on line clears, scanline overlay, animated background.

Play game:
'Python neon_tetris.py'

Coded by LogicPy and GLM 5.2

"""

import math
import random
import sys

import pygame
from pygame import gfxdraw

from tetris_engine import (
    BOARD_WIDTH,
    BOARD_HEIGHT,
    NEON_COLORS,
    GameState,
    TetrisEngine,
)
from tetris_ai import TetrisAI

CELL = 32
BOARD_PX_W = BOARD_WIDTH * CELL
BOARD_PX_H = BOARD_HEIGHT * CELL
BOARD_OFFSET_X = 280
BOARD_OFFSET_Y = 40

SCREEN_W = BOARD_OFFSET_X + BOARD_PX_W + 280
SCREEN_H = BOARD_OFFSET_Y + BOARD_PX_H + 40

BG_COLOR = (8, 8, 18)
GRID_COLOR = (22, 22, 40)
PANEL_COLOR = (14, 14, 30)
TEXT_COLOR = (0, 240, 255)
ACCENT_COLOR = (255, 0, 200)

BAG_QUEUE_SIZE = 3


class NeonButton:
    """A glowing neon toggle button with hover and click effects."""

    def __init__(self, rect, label, font, color, active_color):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.font = font
        self.color = color
        self.active_color = active_color
        self.active = False
        self.hover = False
        self.click_anim = 0

    def update(self, mouse_pos, mouse_clicked):
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.hover and mouse_clicked:
            self.active = not self.active
            self.click_anim = 15
            return True
        if self.click_anim > 0:
            self.click_anim -= 1
        return False

    def draw(self, surface):
        glow_color = self.active_color if self.active else self.color
        intensity = 1.0
        if self.hover:
            intensity = 1.3
        if self.click_anim > 0:
            intensity += self.click_anim * 0.04

        # Background
        bg_alpha = 40 if self.active else 20
        bg_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        bg_surf.fill((*glow_color, bg_alpha))
        surface.blit(bg_surf, self.rect.topleft)

        # Glow border
        for thickness, alpha in [(4, 30), (3, 60), (2, 120)]:
            glow_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surf, (*glow_color, int(alpha * intensity)),
                (0, 0, self.rect.w, self.rect.h),
                width=thickness, border_radius=6,
            )
            surface.blit(glow_surf, self.rect.topleft, special_flags=pygame.BLEND_RGBA_ADD)

        # Crisp border
        border_color = tuple(min(255, int(c * intensity)) for c in glow_color)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=6)

        # Label
        text_color = border_color if self.active else (180, 180, 200)
        label_surf = self.font.render(self.label, True, text_color)
        label_rect = label_surf.get_rect(center=self.rect.center)
        surface.blit(label_surf, label_rect.topleft)


class NeonRenderer:
    """Handles all cyber-punk neon drawing."""

    def __init__(self, screen):
        self.screen = screen
        self.particles = []
        self.flash_rows = []
        self.flash_timer = 0
        self.scanline_offset = 0
        self.time = 0
        self._init_fonts()
        self._init_background()
        self._init_buttons()

    def _init_fonts(self):
        pygame.font.init()
        font_name = pygame.font.match_font(
            "consolas,couriernew,monospace,dejavusans"
        )
        self.font_title = pygame.font.Font(font_name, 56)
        self.font_large = pygame.font.Font(font_name, 36)
        self.font_mid = pygame.font.Font(font_name, 22)
        self.font_small = pygame.font.Font(font_name, 16)

    def _init_background(self):
        self.bg_surface = pygame.Surface((SCREEN_W, SCREEN_H))
        self.bg_surface.fill(BG_COLOR)
        for y in range(0, SCREEN_H, 3):
            shade = max(0, int(8 + 10 * math.sin(y * 0.01)))
            shade2 = min(shade + 8, 255)
            pygame.draw.line(
                self.bg_surface,
                (shade, shade, shade2),
                (0, y),
                (SCREEN_W, y),
            )
        for _ in range(60):
            x = random.randint(0, SCREEN_W - 1)
            y = random.randint(0, SCREEN_H - 1)
            brightness = random.randint(20, 60)
            b2 = min(brightness + 20, 255)
            self.bg_surface.set_at((x, y), (brightness, brightness, b2))

    def _init_buttons(self):
        rx = BOARD_OFFSET_X + BOARD_PX_W + 20
        by = BOARD_OFFSET_Y + 545
        self.ai_button = NeonButton(
            (rx, by, 240, 44),
            "AI: OFF",
            self.font_mid,
            TEXT_COLOR,
            ACCENT_COLOR,
        )

    # ---- Block rendering ----

    def draw_neon_block(self, surface, rect, color, intensity=1.0):
        """Draw a single glowing 3D neon block."""
        x, y, w, h = rect
        pad = 3
        inner = pygame.Rect(x + pad, y + pad, w - pad * 2, h - pad * 2)

        # Outer dark fill (block body)
        body_color = tuple(int(c * 0.12) for c in color)
        pygame.draw.rect(surface, body_color, rect, border_radius=4)

        # Inner gradient fill (center brighter)
        center = inner.center
        for i in range(inner.width // 2, 0, -2):
            t = i / (inner.width / 2)
            t = max(0.0, min(1.0, t))
            r = int(color[0] * (1 - t) * 0.45 * intensity + color[0] * 0.1)
            g = int(color[1] * (1 - t) * 0.45 * intensity + color[1] * 0.1)
            b = int(color[2] * (1 - t) * 0.45 * intensity + color[2] * 0.1)
            r, g, b = min(r, 255), min(g, 255), min(b, 255)
            radius = max(1, int(i))
            pygame.draw.circle(surface, (r, g, b), center, radius)

        # Top-left highlight (3D effect)
        highlight = tuple(min(255, int(c * 0.8 * intensity + 60)) for c in color)
        pygame.draw.line(
            surface, highlight,
            (inner.left, inner.top),
            (inner.right, inner.top), 2
        )
        pygame.draw.line(
            surface, highlight,
            (inner.left, inner.top),
            (inner.left, inner.bottom), 2
        )

        # Bottom-right shadow (3D depth)
        shadow = tuple(int(c * 0.25) for c in color)
        pygame.draw.line(
            surface, shadow,
            (inner.right, inner.top + 2),
            (inner.right, inner.bottom), 2
        )
        pygame.draw.line(
            surface, shadow,
            (inner.left + 2, inner.bottom),
            (inner.right, inner.bottom), 2
        )

        # Neon border with glow
        glow_color = tuple(min(255, int(c * intensity)) for c in color)
        for thickness, alpha in [(6, 30), (4, 60), (2, 120)]:
            glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(
                glow_surf, (*glow_color, alpha),
                (pad - 1, pad - 1, w - pad * 2 + 2, h - pad * 2 + 2),
                width=thickness, border_radius=4,
            )
            surface.blit(glow_surf, (x, y), special_flags=pygame.BLEND_RGBA_ADD)

        # Crisp inner border
        pygame.draw.rect(
            surface, glow_color, inner, width=1, border_radius=3
        )

        # Center dot sparkle
        sparkle = tuple(min(255, c + 80) for c in color)
        sx, sy = center
        for r, a in [(3, 200), (2, 255)]:
            gfxdraw.filled_circle(surface, sx, sy, r, (*sparkle, a))
        gfxdraw.pixel(surface, sx, sy, (255, 255, 255))

    def draw_ghost_block(self, surface, rect, color):
        """Draw a translucent ghost preview block."""
        x, y, w, h = rect
        pad = 5
        ghost_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        border_color = (*color, 80)
        inner_color = (*color, 20)
        pygame.draw.rect(
            ghost_surf, inner_color,
            (pad, pad, w - pad * 2, h - pad * 2),
            border_radius=3,
        )
        pygame.draw.rect(
            ghost_surf, border_color,
            (pad, pad, w - pad * 2, h - pad * 2),
            width=1, border_radius=3,
        )
        # Dashed effect
        for i in range(pad, w - pad, 6):
            pygame.draw.rect(
                ghost_surf, (*color, 60),
                (i, pad, 3, 1),
            )
            pygame.draw.rect(
                ghost_surf, (*color, 60),
                (i, h - pad - 1, 3, 1),
            )
        surface.blit(ghost_surf, (x, y))

    # ---- Board ----

    def draw_board_background(self, surface):
        # Board panel
        panel = pygame.Rect(
            BOARD_OFFSET_X - 4, BOARD_OFFSET_Y - 4,
            BOARD_PX_W + 8, BOARD_PX_H + 8
        )
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=6)
        pygame.draw.rect(surface, (30, 30, 60), panel, width=2, border_radius=6)

        # Grid
        for x in range(BOARD_WIDTH + 1):
            px = BOARD_OFFSET_X + x * CELL
            pygame.draw.line(
                surface, GRID_COLOR,
                (px, BOARD_OFFSET_Y),
                (px, BOARD_OFFSET_Y + BOARD_PX_H),
            )
        for y in range(BOARD_HEIGHT + 1):
            py = BOARD_OFFSET_Y + y * CELL
            pygame.draw.line(
                surface, GRID_COLOR,
                (BOARD_OFFSET_X, py),
                (BOARD_OFFSET_X + BOARD_PX_W, py),
            )

    def draw_locked_blocks(self, surface, engine):
        for y, row in enumerate(engine.board):
            for x, cell in enumerate(row):
                if cell != 0:
                    rect = pygame.Rect(
                        BOARD_OFFSET_X + x * CELL,
                        BOARD_OFFSET_Y + y * CELL,
                        CELL, CELL,
                    )
                    intensity = 1.0
                    if self.flash_timer > 0 and y in self.flash_rows:
                        intensity = 1.0 + min(
                            1.0, self.flash_timer * 0.15
                        )
                    color = NEON_COLORS.get(cell, (100, 100, 100))
                    self.draw_neon_block(surface, rect, color, intensity)

    def draw_current_piece(self, surface, engine):
        if not engine.current_piece:
            return
        color = engine.current_piece.color
        for cx, cy in engine.current_piece.cells():
            if cy < 0:
                continue
            rect = pygame.Rect(
                BOARD_OFFSET_X + cx * CELL,
                BOARD_OFFSET_Y + cy * CELL,
                CELL, CELL,
            )
            self.draw_neon_block(surface, rect, color, 1.0)

    def draw_ghost(self, surface, engine):
        if engine.state != GameState.PLAYING:
            return
        color = engine.current_piece.color if engine.current_piece else (100, 100, 100)
        for cx, cy in engine.ghost_cells():
            if cy < 0:
                continue
            rect = pygame.Rect(
                BOARD_OFFSET_X + cx * CELL,
                BOARD_OFFSET_Y + cy * CELL,
                CELL, CELL,
            )
            self.draw_ghost_block(surface, rect, color)

    # ---- HUD / Panels ----

    def draw_panel(self, surface, x, y, w, h, title=None):
        panel = pygame.Rect(x, y, w, h)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=8)
        pygame.draw.rect(surface, (35, 35, 70), panel, width=1, border_radius=8)
        if title:
            label = self.font_small.render(title, True, TEXT_COLOR)
            surface.blit(label, (x + 12, y + 8))

    def draw_hud(self, surface, engine):
        rx = BOARD_OFFSET_X + BOARD_PX_W + 20
        ry = BOARD_OFFSET_Y

        # Next piece panel
        self.draw_panel(surface, rx, ry, 240, 140, "NEXT")
        if engine.next_piece:
            self._draw_mini_piece(surface, engine.next_piece, rx + 70, ry + 50)

        # Score panel
        self.draw_panel(surface, rx, ry + 160, 240, 180, "STATS")
        stats = [
            ("SCORE", f"{engine.score:,}"),
            ("LINES", f"{engine.lines}"),
            ("LEVEL", f"{engine.level}"),
            ("COMBO", f"x{engine.combo}"),
        ]
        for i, (label, val) in enumerate(stats):
            ly = ry + 160 + 40 + i * 30
            lbl = self.font_small.render(label, True, (120, 120, 160))
            surface.blit(lbl, (rx + 14, ly))
            v = self.font_mid.render(val, True, TEXT_COLOR)
            surface.blit(v, (rx + 100, ly - 4))

        # Controls panel
        self.draw_panel(surface, rx, ry + 360, 240, 170, "CONTROLS")
        controls = [
            "← →   Move",
            "↑     Rotate",
            "↓     Soft Drop",
            "SPACE Hard Drop",
            "A     Toggle AI",
            "P     Pause",
            "R     Restart",
            "ESC   Quit",
        ]
        for i, line in enumerate(controls):
            txt = self.font_small.render(line, True, (110, 110, 150))
            surface.blit(txt, (rx + 14, ry + 360 + 36 + i * 18))

        # AI toggle button
        self.ai_button.label = "AI: ON" if self.ai_button.active else "AI: OFF"
        self.ai_button.draw(surface)

        # Left side: title
        title = self.font_title.render("NEON", True, TEXT_COLOR)
        title2 = self.font_title.render("BLOCKS", True, ACCENT_COLOR)
        surface.blit(title, (40, 40))
        surface.blit(title2, (40, 100))

    def _draw_mini_piece(self, surface, piece, ox, oy):
        color = piece.color
        cells = piece.cells()
        min_x = min(c[0] for c in cells)
        max_x = max(c[0] for c in cells)
        min_y = min(c[1] for c in cells)
        max_y = max(c[1] for c in cells)
        pw = (max_x - min_x + 1) * 24
        ph = (max_y - min_y + 1) * 24
        start_x = ox + (100 - pw) // 2
        start_y = oy + (40 - ph) // 2
        for cx, cy in cells:
            rect = pygame.Rect(
                start_x + (cx - min_x) * 24,
                start_y + (cy - min_y) * 24,
                24, 24,
            )
            self.draw_neon_block(surface, rect, color, 1.0)

    # ---- Effects ----

    def trigger_line_flash(self, rows, board_colors=None):
        """Trigger block-breaking animation on cleared rows.

        board_colors: dict of {(row, col): color_tuple} for the actual piece
        colors that were on the board before clearing. If None, random neon.
        """
        self.flash_rows = rows[:]
        self.flash_timer = 25
        for row in rows:
            for x in range(BOARD_WIDTH):
                px = BOARD_OFFSET_X + x * CELL + CELL // 2
                py = BOARD_OFFSET_Y + row * CELL + CELL // 2
                if board_colors and (row, x) in board_colors:
                    color = board_colors[(row, x)]
                else:
                    color = NEON_COLORS.get(
                        random.choice(list(NEON_COLORS.keys()))
                    )
                # Shatter debris — small block fragments flying outward
                for _ in range(8):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(2, 7)
                    self.particles.append({
                        "x": px + random.uniform(-8, 8),
                        "y": py + random.uniform(-8, 8),
                        "vx": math.cos(angle) * speed,
                        "vy": math.sin(angle) * speed - 2,
                        "life": random.randint(25, 40),
                        "max_life": 40,
                        "color": color,
                        "size": random.randint(2, 6),
                        "type": "shard",
                    })
                # Bright spark particles
                for _ in range(4):
                    self.particles.append({
                        "x": px,
                        "y": py,
                        "vx": random.uniform(-3, 3),
                        "vy": random.uniform(-8, 0),
                        "life": random.randint(15, 25),
                        "max_life": 25,
                        "color": (255, 255, 255),
                        "size": random.randint(1, 3),
                        "type": "spark",
                    })
                # Block fragment — larger rectangular pieces
                for _ in range(3):
                    self.particles.append({
                        "x": px,
                        "y": py,
                        "vx": random.uniform(-5, 5),
                        "vy": random.uniform(-7, -1),
                        "life": random.randint(30, 50),
                        "max_life": 50,
                        "color": color,
                        "size": random.randint(4, 8),
                        "rot": random.uniform(0, 360),
                        "rot_speed": random.uniform(-10, 10),
                        "type": "fragment",
                    })

    def update_effects(self):
        if self.flash_timer > 0:
            self.flash_timer -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.25
            p["life"] -= 1
            if "rot" in p:
                p["rot"] += p.get("rot_speed", 0)

    def draw_particles(self, surface):
        for p in self.particles:
            alpha = p["life"] / p["max_life"]
            r = max(1, int(p["size"] * alpha))
            color = p["color"]
            ptype = p.get("type", "shard")

            if ptype == "fragment":
                # Rotating rectangular block fragment
                size = max(2, int(p["size"] * alpha))
                frag_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.rect(
                    frag_surf,
                    (*color, int(255 * alpha)),
                    (0, 0, size * 2, size * 2),
                    border_radius=2,
                )
                # Glow
                glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.rect(
                    glow_surf,
                    (*color, int(60 * alpha)),
                    (size, size, size * 2, size * 2),
                    border_radius=4,
                )
                rot = p.get("rot", 0)
                rotated = pygame.transform.rotate(frag_surf, rot)
                rotated_glow = pygame.transform.rotate(glow_surf, rot)
                gr = rotated_glow.get_rect(center=(p["x"], p["y"]))
                surface.blit(rotated_glow, gr.topleft, special_flags=pygame.BLEND_RGBA_ADD)
                rr = rotated.get_rect(center=(p["x"], p["y"]))
                surface.blit(rotated, rr.topleft)
            elif ptype == "spark":
                # Bright white spark with additive glow
                glow_surf = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf,
                    (*color, int(200 * alpha)),
                    (r * 3, r * 3), r * 3,
                )
                pygame.draw.circle(
                    glow_surf,
                    (*color, int(255 * alpha)),
                    (r * 3, r * 3), max(1, r),
                )
                surface.blit(
                    glow_surf,
                    (p["x"] - r * 3, p["y"] - r * 3),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )
            else:
                # Default shard — glowing circle
                glow_surf = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf,
                    (*color, int(180 * alpha)),
                    (r * 2, r * 2), r * 2,
                )
                pygame.draw.circle(
                    glow_surf,
                    (*color, int(255 * alpha)),
                    (r * 2, r * 2), r,
                )
                surface.blit(
                    glow_surf,
                    (p["x"] - r * 2, p["y"] - r * 2),
                    special_flags=pygame.BLEND_RGBA_ADD,
                )

    def draw_scanlines(self, surface):
        self.scanline_offset = (self.scanline_offset + 0.5) % 4
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for y in range(0, SCREEN_H, 4):
            pygame.draw.line(
                overlay, (0, 0, 0, 20),
                (0, int(y + self.scanline_offset)),
                (SCREEN_W, int(y + self.scanline_offset)),
            )
        surface.blit(overlay, (0, 0))

    def draw_game_over(self, surface, engine):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        txt = self.font_title.render("GAME OVER", True, ACCENT_COLOR)
        rect = txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 40))
        surface.blit(txt, rect)

        score_txt = self.font_large.render(
            f"Score: {engine.score:,}", True, TEXT_COLOR
        )
        score_rect = score_txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 20))
        surface.blit(score_txt, score_rect)

        prompt = self.font_mid.render("Press R to Restart", True, (200, 200, 220))
        prompt_rect = prompt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 70))
        surface.blit(prompt, prompt_rect)

    def draw_pause(self, surface):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))
        txt = self.font_title.render("PAUSED", True, TEXT_COLOR)
        rect = txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
        surface.blit(txt, rect)

    def draw_menu(self, surface):
        # Animated title
        pulse = 0.5 + 0.5 * math.sin(self.time * 2)
        title_color = tuple(
            int(ACCENT_COLOR[i] * (0.6 + 0.4 * pulse))
            for i in range(3)
        )
        title = self.font_title.render("NEON BLOCKS", True, title_color)
        rect = title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 60))
        surface.blit(title, rect)

        subtitle = self.font_mid.render(
            "Cyber-Punk Tetris", True, TEXT_COLOR
        )
        sub_rect = subtitle.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 10))
        surface.blit(subtitle, sub_rect)

        prompt_pulse = 0.5 + 0.5 * math.sin(self.time * 3)
        prompt_color = tuple(int(180 * prompt_pulse + 75) for _ in range(3))
        prompt = self.font_mid.render(
            "Press ENTER to Start", True, prompt_color
        )
        prompt_rect = prompt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 50))
        surface.blit(prompt, prompt_rect)

        hint = self.font_small.render(
            "Arrows to move  •  Up to rotate  •  Space to hard drop",
            True, (120, 120, 150)
        )
        hint_rect = hint.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 90))
        surface.blit(hint, hint_rect)

    def render(self, surface, engine):
        surface.blit(self.bg_surface, (0, 0))

        if engine.state == GameState.MENU:
            self.draw_menu(surface)
            self.draw_scanlines(surface)
            return

        self.draw_board_background(surface)
        self.draw_ghost(surface, engine)
        self.draw_locked_blocks(surface, engine)
        self.draw_current_piece(surface, engine)
        self.draw_hud(surface, engine)
        self.draw_particles(surface)

        if engine.state == GameState.PAUSED:
            self.draw_pause(surface)
        elif engine.state == GameState.GAME_OVER:
            self.draw_game_over(surface, engine)

        self.draw_scanlines(surface)


class NeonTetrisGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(
            (SCREEN_W, SCREEN_H),
            pygame.SCALED,
            vsync=1,
        )
        pygame.display.set_caption("Neon Blocks - Cyber-Punk Tetris")
        self.clock = pygame.time.Clock()
        self.engine = TetrisEngine()
        self.renderer = NeonRenderer(self.screen)
        self.fall_timer = 0.0
        self.running = True
        self._play_beep(440, 0.05)

        # DAS (Delayed Auto Shift) for arrow key repeat control
        self.das_delay = 0.15      # seconds before auto-repeat kicks in
        self.das_repeat = 0.06     # seconds between auto-repeats
        self.das_timers = {}        # key -> elapsed hold time
        self.das_activated = {}     # key -> bool (delay passed, now repeating)
        self.das_keys = {
            pygame.K_LEFT: "move_left",
            pygame.K_RIGHT: "move_right",
            pygame.K_DOWN: "soft_drop",
        }

        # AI autoplayer
        self.ai = TetrisAI()
        self.ai_active = False
        self.ai_action_timer = 0.0
        self.ai_action_delay = 0.03  # seconds between AI actions (fast but visible)

    def _play_beep(self, freq, duration, volume=0.15):
        try:
            sample_rate = 22050
            num_samples = int(sample_rate * duration)
            buf = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                env = math.exp(-t * 8)
                sample = int(volume * 32767 * env * math.sin(2 * math.pi * freq * t))
                buf += sample.to_bytes(2, "little", signed=True)
            sound = pygame.mixer.Sound(buffer=bytes(buf))
            sound.play()
        except Exception:
            pass

    def _play_clear_sound(self, lines_cleared):
        freqs = {1: 523, 2: 659, 3: 784, 4: 1047}
        self._play_beep(freqs.get(lines_cleared, 523), 0.2, 0.2)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.engine.toggle_pause()
                elif event.key == pygame.K_r:
                    self.engine.restart()
                    self.fall_timer = 0
                    self.das_timers.clear()
                    self.das_activated.clear()
                    self.ai.current_plan = None
                elif event.key == pygame.K_a:
                    self.ai_active = not self.ai_active
                    self.renderer.ai_button.active = self.ai_active
                    self.ai.current_plan = None
                elif self.engine.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.engine.restart()
                elif self.engine.state == GameState.PLAYING and not self.ai_active:
                    if event.key == pygame.K_UP:
                        self.engine.rotate(1)
                        self._play_beep(330, 0.03)
                    elif event.key == pygame.K_z:
                        self.engine.rotate(-1)
                    elif event.key == pygame.K_SPACE:
                        ghost = self.engine.ghost_cells()
                        affected_rows = set(cy for cx, cy in ghost)
                        board_colors = self._capture_board_colors_before(affected_rows)
                        piece_color = self.engine.current_piece.color
                        for cx, cy in ghost:
                            if cy >= 0:
                                board_colors[(cy, cx)] = piece_color
                        self.engine.hard_drop()
                        self._play_beep(220, 0.08)
                        if self.engine.last_cleared_rows:
                            cleared = len(self.engine.last_cleared_rows)
                            self._play_clear_sound(cleared)
                            self.renderer.trigger_line_flash(
                                self.engine.last_cleared_rows, board_colors
                            )
                # Register DAS key press — immediate first action (skip if AI active)
                if (event.key in self.das_keys
                        and self.engine.state == GameState.PLAYING
                        and not self.ai_active):
                    action = self.das_keys[event.key]
                    getattr(self.engine, action)()
                    self.das_timers[event.key] = 0.0
                    self.das_activated[event.key] = False

        # Handle AI button click
        if self.renderer.ai_button.update(mouse_pos, mouse_clicked):
            self.ai_active = self.renderer.ai_button.active
            self.ai.current_plan = None
            if self.ai_active:
                self._play_beep(660, 0.1, 0.2)

        if self.engine.state != GameState.PLAYING:
            self.das_timers.clear()
            self.das_activated.clear()
            return

        if self.ai_active:
            return

        # DAS: handle held keys with delay + repeat
        dt = self.clock.get_time() / 1000.0
        for key, action in self.das_keys.items():
            if keys[key]:
                if key not in self.das_timers:
                    continue
                self.das_timers[key] += dt
                if not self.das_activated[key]:
                    if self.das_timers[key] >= self.das_delay:
                        self.das_activated[key] = True
                        self.das_timers[key] = 0.0
                        getattr(self.engine, action)()
                else:
                    if self.das_timers[key] >= self.das_repeat:
                        self.das_timers[key] = 0.0
                        getattr(self.engine, action)()
            else:
                self.das_timers.pop(key, None)
                self.das_activated.pop(key, None)

    def _capture_board_colors_before(self, rows):
        """Capture colors of blocks on specified rows BEFORE they are cleared.

        Must be called before the line clear happens. Since hard_drop clears
        lines internally, we capture the full bottom rows first.
        """
        from tetris_engine import NEON_COLORS as COLORS
        board_colors = {}
        for row in rows:
            if row < len(self.engine.board):
                for x in range(BOARD_WIDTH):
                    cell = self.engine.board[row][x]
                    if cell and cell in COLORS:
                        board_colors[(row, x)] = COLORS[cell]
        return board_colors

    def _run_ai(self):
        """Execute one AI action if enough time has elapsed."""
        self.ai_action_timer += self.clock.get_time() / 1000.0
        if self.ai_action_timer < self.ai_action_delay:
            return
        self.ai_action_timer = 0.0

        action = self.ai.get_next_action(self.engine)
        if action is None:
            self.ai.compute_plan(self.engine)
            action = self.ai.get_next_action(self.engine)
            if action is None:
                return

        if action == "rotate":
            self.engine.rotate(1)
        elif action == "left":
            self.engine.move_left()
        elif action == "right":
            self.engine.move_right()
        elif action == "drop":
            # Predict which rows might clear (the rows the piece will occupy)
            piece_cells = self.engine.current_piece.cells()
            # Find the ghost position (where it will land)
            ghost = self.engine.ghost_cells()
            affected_rows = set(cy for cx, cy in ghost)
            # Capture colors from those rows before the drop
            board_colors = self._capture_board_colors_before(affected_rows)
            # Also capture the piece's own color for its cells
            piece_color = self.engine.current_piece.color
            for cx, cy in ghost:
                if cy >= 0:
                    board_colors[(cy, cx)] = piece_color
            self.engine.hard_drop()
            self._play_beep(220, 0.08)
            if self.engine.last_cleared_rows:
                cleared = len(self.engine.last_cleared_rows)
                self._play_clear_sound(cleared)
                self.renderer.trigger_line_flash(
                    self.engine.last_cleared_rows, board_colors
                )
            self.ai.current_plan = None

    def update(self, dt):
        self.renderer.time += dt
        self.renderer.update_effects()

        if self.engine.state != GameState.PLAYING:
            return

        if self.ai_active:
            self._run_ai()
            return

        self.fall_timer += dt
        fall_speed = self.engine.get_fall_speed()

        if self.fall_timer >= fall_speed:
            self.fall_timer = 0
            # Capture colors of the piece's landing position before potential clear
            ghost = self.engine.ghost_cells()
            affected_rows = set(cy for cx, cy in ghost)
            board_colors = self._capture_board_colors_before(affected_rows)
            piece_color = self.engine.current_piece.color
            for cx, cy in ghost:
                if cy >= 0:
                    board_colors[(cy, cx)] = piece_color
            prev_lines = self.engine.lines
            self.engine.soft_drop()
            if self.engine.lines > prev_lines:
                cleared = self.engine.lines - prev_lines
                self._play_clear_sound(cleared)
                if self.engine.last_cleared_rows:
                    self.renderer.trigger_line_flash(
                        self.engine.last_cleared_rows, board_colors
                    )

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 0.1)
            self.handle_input()
            self.update(dt)
            self.renderer.render(self.screen, self.engine)
            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = NeonTetrisGame()
    game.run()
