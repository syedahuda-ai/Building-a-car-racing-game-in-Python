"""
enemy.py - Enemy car logic with pseudo-3D perspective rendering
"""

import pygame
import random
from constants import *


class EnemyCar:
    def __init__(self, road_pos, speed, color=None):
        """
        road_pos : float 0.0 (left lane) – 1.0 (right lane)
        speed    : pixels-per-frame at 'full size' (bottom of screen)
        """
        self.road_pos = road_pos    # 0..1 lateral position on road
        self.depth    = 0.0         # 0 = at horizon, 1 = at player
        self.speed    = speed
        self.color    = color or random.choice(ENEMY_COLORS)
        self.active   = True
        self.overtaken = False      # did player pass this car?

        # These are set each frame by the road renderer
        self.screen_x = 0
        self.screen_y = 0
        self.scale    = 0.1
        self.w        = ENEMY_CAR_W
        self.h        = ENEMY_CAR_H

    def update(self, dt_scale=1.0):
        """Move car toward the player (increase depth)."""
        self.depth += self.speed * 0.003 * dt_scale
        if self.depth >= 1.0:
            self.active = False

    def is_off_screen(self):
        return not self.active

    def draw(self, surface):
        if self.scale < 0.05:
            return

        cx = int(self.screen_x)
        cy = int(self.screen_y)
        w  = max(6, int(ENEMY_CAR_W * self.scale))
        h  = max(8, int(ENEMY_CAR_H * self.scale))
        self.w = w
        self.h = h

        c = self.color
        dark_c = (max(0, c[0]-50), max(0, c[1]-50), max(0, c[2]-50))

        # Shadow
        shadow_surf = pygame.Surface((w+6, int(h*0.18)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0,0,0,60), (0,0,w+6, int(h*0.18)))
        surface.blit(shadow_surf, (cx - w//2 - 3, cy + h//2 - int(h*0.1)))

        # Body
        body_pts = [
            (cx - w//2 + int(w*0.1), cy - h//2 + int(h*0.2)),
            (cx + w//2 - int(w*0.1), cy - h//2 + int(h*0.2)),
            (cx + w//2,              cy + h//2 - int(h*0.15)),
            (cx - w//2,              cy + h//2 - int(h*0.15)),
        ]
        pygame.draw.polygon(surface, c, body_pts)

        # Roof
        roof_pts = [
            (cx - int(w*0.35), cy - h//2 + int(h*0.2)),
            (cx + int(w*0.35), cy - h//2 + int(h*0.2)),
            (cx + int(w*0.30), cy - h//2 + int(h*0.03)),
            (cx - int(w*0.30), cy - h//2 + int(h*0.03)),
        ]
        pygame.draw.polygon(surface, dark_c, roof_pts)

        # Windshield (small rectangle)
        ws_rect = pygame.Rect(cx - int(w*0.28), cy - h//2 + int(h*0.04),
                              int(w*0.56), int(h*0.14))
        pygame.draw.rect(surface, (150, 210, 255), ws_rect, border_radius=2)

        # Headlights
        hl_y = cy - h//2 + int(h*0.2)
        pygame.draw.ellipse(surface, YELLOW,
                            (cx - w//2 + 2, hl_y, max(3,int(w*0.18)), max(2,int(h*0.09))))
        pygame.draw.ellipse(surface, YELLOW,
                            (cx + w//2 - 2 - max(3,int(w*0.18)), hl_y,
                             max(3,int(w*0.18)), max(2,int(h*0.09))))

        # Tail lights
        tl_y = cy + h//2 - int(h*0.18)
        pygame.draw.ellipse(surface, RED,
                            (cx - w//2 + 1, tl_y, max(3,int(w*0.18)), max(2,int(h*0.1))))
        pygame.draw.ellipse(surface, RED,
                            (cx + w//2 - 1 - max(3,int(w*0.18)), tl_y,
                             max(3,int(w*0.18)), max(2,int(h*0.1))))

        # Wheels (only draw if large enough)
        if w > 20:
            ww = max(3, int(w*0.14))
            wh = max(5, int(h*0.22))
            for wx, wy in [
                (cx - w//2 - ww//2, cy - h//4 - wh//2),
                (cx + w//2 - ww//2, cy - h//4 - wh//2),
                (cx - w//2 - ww//2, cy + h//4 - wh//2),
                (cx + w//2 - ww//2, cy + h//4 - wh//2),
            ]:
                pygame.draw.rect(surface, BLACK, (wx, wy, ww, wh), border_radius=2)
