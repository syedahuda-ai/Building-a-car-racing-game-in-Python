"""
hud.py - Heads-Up Display: speedometer, score, lives, etc.
"""

import pygame
import math
from constants import *


class HUD:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h

        self.font_big   = pygame.font.SysFont("Arial Black", 28, bold=True)
        self.font_med   = pygame.font.SysFont("Arial",       20, bold=True)
        self.font_small = pygame.font.SysFont("Arial",       15)

        self.score = 0
        self.lives = 3
        self.best  = 0
        self.difficulty = "EASY"
        self.speed = 0.0
        self.combo = 0        # overtake combo
        self.combo_timer = 0

    def update(self, score, lives, speed, difficulty, best, combo=0, combo_timer=0):
        self.score      = score
        self.lives      = lives
        self.speed      = speed
        self.difficulty = difficulty
        self.best       = best
        self.combo      = combo
        self.combo_timer = combo_timer

    def draw(self, surface):
        self._draw_score_panel(surface)
        self._draw_speedometer(surface)
        self._draw_lives(surface)
        self._draw_difficulty_badge(surface)
        if self.combo > 1 and self.combo_timer > 0:
            self._draw_combo(surface)

    def _draw_score_panel(self, surface):
        # Background panel
        panel = pygame.Surface((200, 55), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 150))
        surface.blit(panel, (10, 10))

        score_txt = self.font_big.render(f"{self.score:,}", True, GOLD)
        surface.blit(score_txt, (20, 15))

        label_txt = self.font_small.render("SCORE", True, LIGHT_GRAY)
        surface.blit(label_txt, (20, 48))

        if self.best > 0:
            best_txt = self.font_small.render(f"BEST: {self.best:,}", True, SILVER)
            surface.blit(best_txt, (90, 48))

    def _draw_speedometer(self, surface):
        cx, cy, r = self.sw - 80, self.sh - 80, 60
        speed_ratio = min(self.speed / PLAYER_MAX_SPEED, 1.0)

        # Outer ring
        pygame.draw.circle(surface, (30, 30, 30), (cx, cy), r)
        pygame.draw.circle(surface, GRAY, (cx, cy), r, 3)

        # Speed arc
        start_angle = math.pi * 0.75
        end_angle   = math.pi * 0.75 + math.pi * 1.5 * speed_ratio
        arc_col = GREEN if speed_ratio < 0.6 else YELLOW if speed_ratio < 0.85 else RED
        points = []
        steps = max(2, int(30 * speed_ratio))
        for i in range(steps + 1):
            a = start_angle + (end_angle - start_angle) * i / max(1, steps)
            px = cx + int((r - 8) * math.cos(a))
            py = cy + int((r - 8) * math.sin(a))
            points.append((px, py))
        if len(points) >= 2:
            pygame.draw.lines(surface, arc_col, False, points, 6)

        # Needle
        needle_angle = start_angle + math.pi * 1.5 * speed_ratio
        nx = cx + int((r - 14) * math.cos(needle_angle))
        ny = cy + int((r - 14) * math.sin(needle_angle))
        pygame.draw.line(surface, WHITE, (cx, cy), (nx, ny), 3)
        pygame.draw.circle(surface, LIGHT_GRAY, (cx, cy), 6)

        # Speed number
        spd_kmh = int(speed_ratio * 280)
        num_txt = self.font_med.render(str(spd_kmh), True, WHITE)
        nr = num_txt.get_rect(center=(cx, cy + 18))
        surface.blit(num_txt, nr)
        km_txt = self.font_small.render("km/h", True, LIGHT_GRAY)
        kr = km_txt.get_rect(center=(cx, cy + 32))
        surface.blit(km_txt, kr)

    def _draw_lives(self, surface):
        panel = pygame.Surface((130, 35), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 130))
        surface.blit(panel, (10, 70))

        lbl = self.font_small.render("LIVES:", True, LIGHT_GRAY)
        surface.blit(lbl, (18, 78))
        for i in range(3):
            col = RED if i < self.lives else DARK_GRAY
            pygame.draw.circle(surface, col, (80 + i * 20, 87), 8)
            pygame.draw.circle(surface, WHITE, (80 + i * 20, 87), 8, 1)

    def _draw_difficulty_badge(self, surface):
        cols = {"EASY": GREEN, "MEDIUM": YELLOW, "HARD": RED}
        col  = cols.get(self.difficulty, WHITE)
        badge = self.font_small.render(self.difficulty, True, col)
        bw = badge.get_width() + 16
        panel = pygame.Surface((bw, 26), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 160), (0, 0, bw, 26), border_radius=6)
        pygame.draw.rect(panel, (*col, 200), (0, 0, bw, 26), 2, border_radius=6)
        surface.blit(panel, (self.sw - bw - 10, 10))
        surface.blit(badge, (self.sw - bw - 2, 15))

    def _draw_combo(self, surface):
        alpha = min(255, self.combo_timer * 6)
        txt = self.font_big.render(f"x{self.combo} OVERTAKE!", True, NEON_CYAN)
        txt.set_alpha(alpha)
        r = txt.get_rect(center=(self.sw // 2, HORIZON_Y + 60))
        surface.blit(txt, r)
