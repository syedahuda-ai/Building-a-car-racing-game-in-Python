"""
ui.py - All UI screens: main menu, difficulty selector, game over, high scores
"""

import pygame
import math
from constants import *


class UIRenderer:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.tick = 0  # animation counter

        self.font_title  = pygame.font.SysFont("Impact",      72, bold=True)
        self.font_sub    = pygame.font.SysFont("Arial Black", 34, bold=True)
        self.font_med    = pygame.font.SysFont("Arial",       24, bold=True)
        self.font_small  = pygame.font.SysFont("Arial",       18)
        self.font_tiny   = pygame.font.SysFont("Arial",       14)

        self.selected_diff = 1   # 0=Easy,1=Medium,2=Hard
        self.diff_names = list(DIFFICULTIES.keys())

    def update(self):
        self.tick += 1

    # ── HELPERS ────────────────────────────────────────────────────────────

    def _draw_bg(self, surface):
        surface.fill((10, 10, 20))
        # Moving grid
        offset = self.tick % 40
        for x in range(-40, self.sw + 40, 40):
            pygame.draw.line(surface, (20, 20, 50), (x, 0), (x, self.sh), 1)
        for y in range(-40 + offset, self.sh + 40, 40):
            pygame.draw.line(surface, (20, 20, 50), (0, y), (self.sw, y), 1)

    def _draw_button(self, surface, rect, text, font, active=False,
                     color=None, text_col=WHITE):
        col  = color or (50, 50, 80)
        bcol = (100, 200, 100) if active else (80, 80, 120)
        pygame.draw.rect(surface, col,  rect, border_radius=10)
        pygame.draw.rect(surface, bcol, rect, 3, border_radius=10)
        txt = font.render(text, True, text_col)
        tr  = txt.get_rect(center=rect.center)
        surface.blit(txt, tr)

    def _glow_text(self, surface, text, font, color, glow_col, x, y, center=True):
        # Glow layer
        for dx, dy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,2)]:
            g = font.render(text, True, glow_col)
            gr = g.get_rect()
            if center:
                gr.center = (x + dx, y + dy)
            else:
                gr.topleft = (x + dx, y + dy)
            surface.blit(g, gr)
        # Main text
        t = font.render(text, True, color)
        tr = t.get_rect()
        if center:
            tr.center = (x, y)
        else:
            tr.topleft = (x, y)
        surface.blit(t, tr)

    # ── MAIN MENU ──────────────────────────────────────────────────────────

    def draw_menu(self, surface, high_score=0):
        self._draw_bg(surface)

        # Animated title
        bob = math.sin(self.tick * 0.04) * 8
        self._glow_text(surface, "TURBO RACE", self.font_title,
                        GOLD, (180, 80, 0), self.sw//2, 120 + bob)
        self._glow_text(surface, "3D", self.font_title,
                        NEON_CYAN, (0, 80, 120), self.sw//2, 190 + bob)

        # Decorative cars
        self._draw_menu_car(surface, self.sw//2 - 200, 310,  RED,   1)
        self._draw_menu_car(surface, self.sw//2 + 140, 310,  BLUE,  -1)

        # Buttons
        buttons = ["▶  PLAY GAME", "⚙  DIFFICULTY", "🏆  HIGH SCORES", "✖  QUIT"]
        bw, bh = 280, 52
        start_y = 390
        for i, label in enumerate(buttons):
            rect = pygame.Rect(self.sw//2 - bw//2, start_y + i*(bh+12), bw, bh)
            self._draw_button(surface, rect, label, self.font_med)

        if high_score > 0:
            hs = self.font_small.render(f"Best Score: {high_score:,}", True, GOLD)
            hsr = hs.get_rect(center=(self.sw//2, start_y - 25))
            surface.blit(hs, hsr)

        # Controls hint
        hint = self.font_tiny.render("ARROW KEYS / WASD to drive   |   ESC to pause", True, GRAY)
        hr   = hint.get_rect(center=(self.sw//2, self.sh - 20))
        surface.blit(hint, hr)

    def _draw_menu_car(self, surface, cx, cy, color, flip):
        w, h = 55, 90
        pts = [
            (cx - w//2*flip, cy - h//2 + 20),
            (cx + w//2*flip, cy - h//2 + 20),
            (cx + w//2*flip, cy + h//2),
            (cx - w//2*flip, cy + h//2),
        ]
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.rect(surface, YELLOW,
                         (cx - w//4, cy - h//2 + 22, w//2, 8))
        # Wheels
        for wy in [cy - h//4, cy + h//4]:
            pygame.draw.rect(surface, BLACK, (cx - w//2*flip - 8*flip, wy - 10, 8, 20), border_radius=2)
            pygame.draw.rect(surface, BLACK, (cx + w//2*flip,        wy - 10, 8, 20), border_radius=2)

    def get_menu_action(self, mouse_pos):
        bw, bh = 280, 52
        start_y = 390
        actions = [STATE_DIFFICULTY, STATE_DIFFICULTY, STATE_HIGH_SCORES, "QUIT"]
        labels  = ["▶  PLAY GAME", "⚙  DIFFICULTY", "🏆  HIGH SCORES", "✖  QUIT"]
        for i, action in enumerate(actions):
            rect = pygame.Rect(self.sw//2 - bw//2, start_y + i*(bh+12), bw, bh)
            if rect.collidepoint(mouse_pos):
                if i == 0:
                    return STATE_PLAYING
                return action
        return None

    # ── DIFFICULTY SCREEN ──────────────────────────────────────────────────

    def draw_difficulty(self, surface):
        self._draw_bg(surface)
        self._glow_text(surface, "SELECT DIFFICULTY",
                        self.font_sub, WHITE, GRAY, self.sw//2, 80)

        diff_info = [
            ("EASY",   GREEN,  "Slow traffic · Gentle curves · 1× score"),
            ("MEDIUM", YELLOW, "Fast traffic · Curvy road   · 2× score"),
            ("HARD",   RED,    "Crazy speed  · Wild curves   · 3× score"),
        ]
        bw, bh = 460, 80
        sy = 150
        for i, (name, col, desc) in enumerate(diff_info):
            rect = pygame.Rect(self.sw//2 - bw//2, sy + i*(bh+16), bw, bh)
            active = (i == self.selected_diff)
            # Highlight glow
            if active:
                glow = pygame.Surface((bw+10, bh+10), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*col, 60), (0,0,bw+10,bh+10), border_radius=12)
                surface.blit(glow, (rect.x-5, rect.y-5))
            self._draw_button(surface, rect, "", self.font_med, active, (30,30,50))
            # Name
            nm = self.font_med.render(name, True, col)
            surface.blit(nm, (rect.x + 20, rect.y + 12))
            # Desc
            ds = self.font_small.render(desc, True, LIGHT_GRAY)
            surface.blit(ds, (rect.x + 20, rect.y + 44))
            # Checkmark
            if active:
                ck = self.font_med.render("✔", True, col)
                surface.blit(ck, (rect.right - 40, rect.y + 24))

        # Buttons
        play_rect = pygame.Rect(self.sw//2 - 140, sy + 3*(bh+16) + 10, 130, 48)
        back_rect = pygame.Rect(self.sw//2 + 10,  sy + 3*(bh+16) + 10, 130, 48)
        self._draw_button(surface, play_rect, "▶ PLAY",  self.font_med,
                          color=(30, 120, 40), text_col=WHITE)
        self._draw_button(surface, back_rect, "◀ BACK",  self.font_med,
                          color=(80, 30, 30), text_col=WHITE)
        return play_rect, back_rect

    def get_difficulty_action(self, mouse_pos):
        diff_info = ["EASY", "MEDIUM", "HARD"]
        bw, bh = 460, 80
        sy = 150
        for i in range(3):
            rect = pygame.Rect(self.sw//2 - bw//2, sy + i*(bh+16), bw, bh)
            if rect.collidepoint(mouse_pos):
                self.selected_diff = i
                return "SELECT"
        play_rect = pygame.Rect(self.sw//2 - 140, sy + 3*(bh+16) + 10, 130, 48)
        back_rect = pygame.Rect(self.sw//2 + 10,  sy + 3*(bh+16) + 10, 130, 48)
        if play_rect.collidepoint(mouse_pos):
            return STATE_PLAYING
        if back_rect.collidepoint(mouse_pos):
            return STATE_MENU
        return None

    def get_selected_difficulty(self):
        return self.diff_names[self.selected_diff]

    # ── PAUSE SCREEN ───────────────────────────────────────────────────────

    def draw_pause(self, surface):
        overlay = pygame.Surface((self.sw, self.sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self._glow_text(surface, "PAUSED", self.font_title,
                        WHITE, GRAY, self.sw//2, self.sh//2 - 80)

        bw, bh = 240, 50
        resume_rect = pygame.Rect(self.sw//2 - bw//2, self.sh//2,     bw, bh)
        menu_rect   = pygame.Rect(self.sw//2 - bw//2, self.sh//2 + 70, bw, bh)
        self._draw_button(surface, resume_rect, "▶ RESUME",   self.font_med, color=(30,120,40))
        self._draw_button(surface, menu_rect,   "◀ MAIN MENU",self.font_med, color=(80,30,30))
        return resume_rect, menu_rect

    def get_pause_action(self, mouse_pos):
        bw, bh = 240, 50
        resume_rect = pygame.Rect(self.sw//2 - bw//2, self.sh//2, bw, bh)
        menu_rect   = pygame.Rect(self.sw//2 - bw//2, self.sh//2 + 70, bw, bh)
        if resume_rect.collidepoint(mouse_pos): return STATE_PLAYING
        if menu_rect.collidepoint(mouse_pos):   return STATE_MENU
        return None

    # ── GAME OVER ──────────────────────────────────────────────────────────

    def draw_game_over(self, surface, score, best, difficulty):
        self._draw_bg(surface)

        pulse = abs(math.sin(self.tick * 0.05))
        col = (int(200 + 55*pulse), int(30*pulse), int(30*pulse))
        self._glow_text(surface, "GAME OVER", self.font_title,
                        col, (100, 0, 0), self.sw//2, 120)

        # Stats panel
        panel = pygame.Surface((380, 180), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0,0,0,180), (0,0,380,180), border_radius=14)
        pygame.draw.rect(panel, GOLD, (0,0,380,180), 2, border_radius=14)
        surface.blit(panel, (self.sw//2 - 190, 210))

        rows = [
            ("SCORE",      f"{score:,}",      GOLD),
            ("BEST",       f"{best:,}",        SILVER),
            ("DIFFICULTY", difficulty,         {"EASY":GREEN,"MEDIUM":YELLOW,"HARD":RED}.get(difficulty, WHITE)),
        ]
        for i, (label, val, col) in enumerate(rows):
            lbl = self.font_small.render(label, True, LIGHT_GRAY)
            vl  = self.font_med.render(val,   True, col)
            surface.blit(lbl, (self.sw//2 - 170, 228 + i*52))
            surface.blit(vl,  (self.sw//2 + 20,  225 + i*52))

        is_new_best = score >= best and score > 0
        if is_new_best:
            nb = self.font_med.render("🏆 NEW HIGH SCORE!", True, GOLD)
            nbr = nb.get_rect(center=(self.sw//2, 408))
            surface.blit(nb, nbr)

        bw, bh = 200, 50
        retry_rect  = pygame.Rect(self.sw//2 - bw - 10, 440, bw, bh)
        menu_rect   = pygame.Rect(self.sw//2 + 10,       440, bw, bh)
        self._draw_button(surface, retry_rect, "▶ RETRY",     self.font_med, color=(30,120,40))
        self._draw_button(surface, menu_rect,  "◀ MAIN MENU", self.font_med, color=(60,30,80))
        return retry_rect, menu_rect

    def get_game_over_action(self, mouse_pos):
        bw, bh = 200, 50
        retry_rect = pygame.Rect(self.sw//2 - bw - 10, 440, bw, bh)
        menu_rect  = pygame.Rect(self.sw//2 + 10,       440, bw, bh)
        if retry_rect.collidepoint(mouse_pos): return STATE_PLAYING
        if menu_rect.collidepoint(mouse_pos):  return STATE_MENU
        return None

    # ── HIGH SCORES ────────────────────────────────────────────────────────

    def draw_high_scores(self, surface, scores):
        self._draw_bg(surface)
        self._glow_text(surface, "🏆  HIGH SCORES", self.font_sub,
                        GOLD, (100, 60, 0), self.sw//2, 60)

        medals = [(GOLD, "1st"), (SILVER, "2nd"), (BRONZE, "3rd")]
        panel_h = min(len(scores), 10) * 48 + 20
        panel = pygame.Surface((500, max(panel_h, 80)), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0,0,0,160), (0,0,500,max(panel_h,80)), border_radius=12)
        surface.blit(panel, (self.sw//2 - 250, 110))

        if not scores:
            no_txt = self.font_med.render("No scores yet! Play a game.", True, GRAY)
            nr = no_txt.get_rect(center=(self.sw//2, 155))
            surface.blit(no_txt, nr)
        else:
            for i, entry in enumerate(scores[:10]):
                y = 122 + i * 48
                # Rank medal
                if i < 3:
                    mc = medals[i][0]
                    mt = self.font_med.render(medals[i][1], True, mc)
                    surface.blit(mt, (self.sw//2 - 240, y))
                else:
                    rt = self.font_small.render(f"{i+1}.", True, LIGHT_GRAY)
                    surface.blit(rt, (self.sw//2 - 240, y + 3))

                sc_txt = self.font_med.render(f"{entry['score']:,}", True, WHITE)
                surface.blit(sc_txt, (self.sw//2 - 170, y))

                diff_col = {"EASY":GREEN,"MEDIUM":YELLOW,"HARD":RED}.get(entry.get("diff",""), WHITE)
                df_txt = self.font_small.render(entry.get("diff", ""), True, diff_col)
                surface.blit(df_txt, (self.sw//2 + 60, y + 4))

        # Back button
        back_rect = pygame.Rect(self.sw//2 - 100, self.sh - 80, 200, 48)
        self._draw_button(surface, back_rect, "◀ BACK", self.font_med, color=(60,30,80))
        return back_rect

    def get_high_scores_action(self, mouse_pos):
        back_rect = pygame.Rect(self.sw//2 - 100, self.sh - 80, 200, 48)
        if back_rect.collidepoint(mouse_pos): return STATE_MENU
        return None
