"""
player.py - Player car logic and rendering
"""

import pygame
import math
from constants import *


class PlayerCar:
    def __init__(self, screen_w, screen_h):
        self.x = screen_w // 2
        self.y = screen_h - 130
        self.w = PLAYER_CAR_W
        self.h = PLAYER_CAR_H
        self.speed = 0.0
        self.lateral_vel = 0.0
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.alive = True
        self.invincible_timer = 0    # brief invincibility after hit
        self.crash_flash = 0
        self.tilt = 0.0             # visual tilt when turning

        # Road boundaries at player level
        self.left_bound  = 0
        self.right_bound = screen_w

    def handle_input(self, keys):
        # Acceleration / braking
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed = min(self.speed + PLAYER_ACCEL, PLAYER_MAX_SPEED)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed = max(self.speed - PLAYER_BRAKE, 0)
        else:
            self.speed = max(self.speed - 0.1, 0)   # natural deceleration

        # Lateral movement
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move = -1
            self.tilt = max(self.tilt - 1.5, -12)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move = 1
            self.tilt = min(self.tilt + 1.5, 12)
        else:
            self.tilt *= 0.85   # spring back

        lat_speed = PLAYER_LATERAL * (self.speed / PLAYER_MAX_SPEED + 0.3)
        self.x += move * lat_speed

        # Clamp to road
        self.x = max(self.left_bound + self.w // 2 + 5,
                     min(self.right_bound - self.w // 2 - 5, self.x))

    def update(self, road_left, road_right):
        self.left_bound  = road_left
        self.right_bound = road_right

        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.crash_flash > 0:
            self.crash_flash -= 1

    def collides_with(self, enemy):
        if self.invincible_timer > 0:
            return False
        rect_p = pygame.Rect(self.x - self.w//2, self.y - self.h//2,
                             self.w, self.h)
        rect_e = pygame.Rect(enemy.screen_x - enemy.w//2,
                             enemy.screen_y - enemy.h//2,
                             enemy.w, enemy.h)
        # Shrink hitboxes slightly for fairness
        rect_p = rect_p.inflate(-10, -10)
        rect_e = rect_e.inflate(-10, -10)
        return rect_p.colliderect(rect_e)

    def crash(self):
        self.invincible_timer = 120
        self.crash_flash = 30
        self.speed *= 0.3

    def draw(self, surface):
        # Skip drawing every other frame when flashing
        if self.crash_flash > 0 and self.crash_flash % 6 < 3:
            return

        cx, cy = int(self.x), int(self.y)
        w, h   = self.w, self.h
        tilt   = self.tilt

        # Shadow
        shadow_surf = pygame.Surface((w + 10, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, w + 10, 20))
        surface.blit(shadow_surf, (cx - w//2 - 5, cy + h//2 - 8))

        # ── Body ──────────────────────────────────────────────────────────
        body_pts = [
            (cx - w//2 + 8 + tilt,  cy - h//2 + 20),
            (cx + w//2 - 8 + tilt,  cy - h//2 + 20),
            (cx + w//2 + tilt,       cy + h//2 - 15),
            (cx - w//2 + tilt,       cy + h//2 - 15),
        ]
        pygame.draw.polygon(surface, (200, 30, 30), body_pts)

        # Roof / cockpit
        roof_pts = [
            (cx - w//2 + 14 + tilt*0.5, cy - h//2 + 20),
            (cx + w//2 - 14 + tilt*0.5, cy - h//2 + 20),
            (cx + w//2 - 18 + tilt*0.5, cy - h//2 + 2),
            (cx - w//2 + 18 + tilt*0.5, cy - h//2 + 2),
        ]
        pygame.draw.polygon(surface, (180, 20, 20), roof_pts)

        # Windshield
        wind_pts = [
            (cx - w//2 + 16 + tilt*0.5, cy - h//2 + 20),
            (cx + w//2 - 16 + tilt*0.5, cy - h//2 + 20),
            (cx + w//2 - 20 + tilt*0.5, cy - h//2 + 5),
            (cx - w//2 + 20 + tilt*0.5, cy - h//2 + 5),
        ]
        pygame.draw.polygon(surface, (150, 210, 255, 180), wind_pts)
        pygame.draw.polygon(surface, (100, 180, 240), wind_pts, 1)

        # Headlights
        pygame.draw.ellipse(surface, YELLOW,
                            (cx - w//2 + 4 + tilt, cy - h//2 + 18, 12, 8))
        pygame.draw.ellipse(surface, YELLOW,
                            (cx + w//2 - 16 + tilt, cy - h//2 + 18, 12, 8))

        # Side stripes
        pygame.draw.line(surface, YELLOW,
                         (cx - w//2 + 2 + tilt, cy - h//2 + 25),
                         (cx - w//2 + 2 + tilt, cy + h//2 - 18), 3)
        pygame.draw.line(surface, YELLOW,
                         (cx + w//2 - 2 + tilt, cy - h//2 + 25),
                         (cx + w//2 - 2 + tilt, cy + h//2 - 18), 3)

        # Front bumper
        pygame.draw.rect(surface, DARK_GRAY,
                         (cx - w//2 + 4 + tilt, cy - h//2 + 26, w - 8, 5), border_radius=2)

        # Rear bumper + tail lights
        pygame.draw.rect(surface, DARK_GRAY,
                         (cx - w//2 + tilt, cy + h//2 - 16, w, 6), border_radius=2)
        pygame.draw.ellipse(surface, RED,
                            (cx - w//2 + 2 + tilt, cy + h//2 - 16, 12, 7))
        pygame.draw.ellipse(surface, RED,
                            (cx + w//2 - 14 + tilt, cy + h//2 - 16, 12, 7))

        # Wheels
        ww, wh = 10, 18
        wheel_positions = [
            (cx - w//2 - 2 + tilt, cy - h//4),   # front-left
            (cx + w//2 - ww + 2 + tilt, cy - h//4),  # front-right
            (cx - w//2 - 2 + tilt, cy + h//4),   # rear-left
            (cx + w//2 - ww + 2 + tilt, cy + h//4),  # rear-right
        ]
        for wx, wy in wheel_positions:
            pygame.draw.rect(surface, BLACK,
                             (wx, wy - wh//2, ww, wh), border_radius=3)
            pygame.draw.rect(surface, GRAY,
                             (wx + 2, wy - wh//2 + 3, ww - 4, wh - 6), border_radius=2)

        # Speed glow under car
        speed_ratio = self.speed / PLAYER_MAX_SPEED
        if speed_ratio > 0.3:
            glow = pygame.Surface((w, 20), pygame.SRCALPHA)
            alpha = int(speed_ratio * 120)
            pygame.draw.ellipse(glow, (255, 100, 0, alpha), (0, 0, w, 20))
            surface.blit(glow, (cx - w//2 + tilt, cy + h//2 - 12))
