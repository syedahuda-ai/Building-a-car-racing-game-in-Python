"""
road.py - Pseudo-3D road renderer with perspective, curves, and scenery
"""

import pygame
import math
import random
from constants import *


class Road:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.offset = 0.0          # scroll offset
        self.curve  = 0.0          # current curve direction (-1..1)
        self.target_curve = 0.0
        self.curve_timer = 0
        self.curve_strength = 1.0  # set by difficulty

        # Trees on each side
        self.trees = self._init_trees()
        # Clouds
        self.clouds = [{"x": random.randint(50, screen_w-50),
                         "y": random.randint(HORIZON_Y - 60, HORIZON_Y + 10),
                         "w": random.randint(60, 120),
                         "speed": random.uniform(0.2, 0.6)}
                       for _ in range(NUM_CLOUDS)]

        # Precompute road strip positions
        self.strips = []
        self._build_strips()

    def _init_trees(self):
        trees = []
        for side in (-1, 1):   # -1 = left, 1 = right
            for i in range(NUM_TREES):
                trees.append({
                    "side":  side,
                    "depth": i / NUM_TREES,   # 0 = horizon, 1 = near
                    "offset": random.uniform(-0.15, 0.15),
                    "kind":  random.choice(["pine", "round"]),
                    "color": random.choice([GRASS_GREEN, DARK_GRASS,
                                            (30,130,50), (20,100,40)]),
                })
        return trees

    def _build_strips(self):
        """Precompute y positions for each horizontal strip of road."""
        self.strips = []
        n = 80   # number of strips
        for i in range(n):
            t = i / n             # 0 = top (horizon), 1 = bottom
            y_top = int(HORIZON_Y + (self.sh - HORIZON_Y) * (i / n))
            y_bot = int(HORIZON_Y + (self.sh - HORIZON_Y) * ((i+1) / n))

            # Road width at this depth
            road_w_t = ROAD_WIDTH_TOP  + (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * (i/n)
            road_w_b = ROAD_WIDTH_TOP  + (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * ((i+1)/n)

            # Road center (with curve offset)
            cx = self.sw // 2

            self.strips.append({
                "y_top":    y_top,
                "y_bot":    y_bot,
                "cx_top":   cx,
                "cx_bot":   cx,
                "rw_top":   road_w_t,
                "rw_bot":   road_w_b,
                "t":        t,
            })

    def update(self, player_speed, curve_strength):
        self.curve_strength = curve_strength
        # Scroll offset for road markings
        self.offset = (self.offset + player_speed * 0.5) % 80

        # Curve transition
        self.curve_timer -= 1
        if self.curve_timer <= 0:
            self.target_curve = random.uniform(-1, 1) * curve_strength
            self.curve_timer  = random.randint(120, 300)

        self.curve += (self.target_curve - self.curve) * 0.02

        # Move clouds
        for cloud in self.clouds:
            cloud["x"] -= cloud["speed"]
            if cloud["x"] < -cloud["w"]:
                cloud["x"] = self.sw + cloud["w"]

    def get_road_bounds_at_y(self, y):
        """Return (left_x, right_x) of the road at screen y coordinate."""
        if y <= HORIZON_Y:
            mid = self.sw // 2
            return mid - ROAD_WIDTH_TOP//2, mid + ROAD_WIDTH_TOP//2

        t = (y - HORIZON_Y) / (self.sh - HORIZON_Y)
        road_w = ROAD_WIDTH_TOP + (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * t
        # Curve offset grows toward player
        curve_off = self.curve * t * 160
        mid = self.sw // 2 + curve_off
        return int(mid - road_w // 2), int(mid + road_w // 2)

    def project_enemy(self, enemy):
        """
        Set enemy.screen_x, enemy.screen_y, enemy.scale based on depth.
        depth 0 = horizon, 1 = player level
        """
        t = enemy.depth
        y = HORIZON_Y + (self.sh - HORIZON_Y) * t
        road_w = ROAD_WIDTH_TOP + (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * t
        curve_off = self.curve * t * 160
        mid = self.sw // 2 + curve_off
        x = mid + (enemy.road_pos - 0.5) * road_w

        enemy.screen_x = x
        enemy.screen_y = y
        enemy.scale    = t * 0.95 + 0.05   # 0.05 at horizon → 1.0 at player

    def draw(self, surface):
        # ── Sky ──────────────────────────────────────────────────────────
        sky_rect = pygame.Rect(0, 0, self.sw, HORIZON_Y)
        pygame.draw.rect(surface, SKY_BLUE, sky_rect)

        # Sky gradient effect (draw lighter bands)
        for i in range(8):
            alpha = 30 - i * 4
            band_h = HORIZON_Y // 8
            band = pygame.Surface((self.sw, band_h), pygame.SRCALPHA)
            band.fill((255, 255, 255, max(0, alpha)))
            surface.blit(band, (0, i * band_h))

        # Clouds
        for cloud in self.clouds:
            self._draw_cloud(surface, cloud)

        # ── Grass strips (below horizon) ─────────────────────────────────
        pygame.draw.rect(surface, GRASS_GREEN,
                         (0, HORIZON_Y, self.sw, self.sh - HORIZON_Y))

        # ── Road strips ──────────────────────────────────────────────────
        n = 80
        cx_top = self.sw // 2
        curve_accum = 0.0
        prev_cx = cx_top

        for i in range(n):
            t_top = i / n
            t_bot = (i + 1) / n

            # Curved center x
            curve_accum += self.curve * 0.012
            cx_top_cur = self.sw // 2 + curve_accum * 160 * t_top
            cx_bot_cur = self.sw // 2 + curve_accum * 160 * t_bot

            y_top = int(HORIZON_Y + (self.sh - HORIZON_Y) * t_top)
            y_bot = int(HORIZON_Y + (self.sh - HORIZON_Y) * t_bot)

            rw_t = ROAD_WIDTH_TOP  + (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * t_top
            rw_b = ROAD_WIDTH_TOP  + (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * t_bot

            # Alternate dark/light grass
            is_dark = (int(t_top * 10 + self.offset * 0.1)) % 2 == 0
            grass_col = DARK_GRASS if is_dark else GRASS_GREEN

            # Full-width grass
            pygame.draw.rect(surface, grass_col,
                             (0, y_top, self.sw, y_bot - y_top))

            # Road trapezoid
            pts = [
                (cx_top_cur - rw_t//2, y_top),
                (cx_top_cur + rw_t//2, y_top),
                (cx_bot_cur + rw_b//2, y_bot),
                (cx_bot_cur - rw_b//2, y_bot),
            ]
            road_col = ROAD_DARK if is_dark else ROAD_LIGHT
            pygame.draw.polygon(surface, road_col, pts)

            # Kerb stripes (alternating red/white at road edges)
            kerb_w = max(2, int(rw_t * 0.08))
            kerb_col = RED if is_dark else WHITE
            # Left kerb
            lpts = [
                (cx_top_cur - rw_t//2, y_top),
                (cx_top_cur - rw_t//2 + kerb_w, y_top),
                (cx_bot_cur - rw_b//2 + kerb_w, y_bot),
                (cx_bot_cur - rw_b//2, y_bot),
            ]
            pygame.draw.polygon(surface, kerb_col, lpts)
            # Right kerb
            rpts = [
                (cx_top_cur + rw_t//2 - kerb_w, y_top),
                (cx_top_cur + rw_t//2, y_top),
                (cx_bot_cur + rw_b//2, y_bot),
                (cx_bot_cur + rw_b//2 - kerb_w, y_bot),
            ]
            pygame.draw.polygon(surface, kerb_col, rpts)

        # ── Center dashes ────────────────────────────────────────────────
        curve_accum = 0.0
        for i in range(n):
            t_top = i / n
            t_bot = (i+1) / n
            curve_accum += self.curve * 0.012
            cx_cur = self.sw // 2 + curve_accum * 160 * ((t_top+t_bot)/2)
            y_mid  = int(HORIZON_Y + (self.sh - HORIZON_Y) * ((t_top+t_bot)/2))

            dash_phase = (int(t_top * 12 + self.offset * 0.15)) % 2
            if dash_phase == 0:
                dash_w = max(2, int((ROAD_WIDTH_TOP + (ROAD_WIDTH_BOTTOM-ROAD_WIDTH_TOP)*t_top)*0.015))
                dash_h = max(2, int((self.sh - HORIZON_Y) / n))
                pygame.draw.rect(surface, LINE_WHITE,
                                 (int(cx_cur) - dash_w//2, y_mid, dash_w, dash_h))

        # ── Trees ─────────────────────────────────────────────────────────
        for tree in sorted(self.trees, key=lambda t: t["depth"]):
            self._draw_tree(surface, tree)

    def _draw_cloud(self, surface, cloud):
        x, y, w = int(cloud["x"]), int(cloud["y"]), int(cloud["w"])
        for ox, oy, r in [(0, 0, w//3), (w//4, -w//8, w//4),
                           (-w//4, -w//10, w//5), (w//2, w//16, w//5)]:
            pygame.draw.circle(surface, (240, 248, 255), (x+ox, y+oy), r)

    def _draw_tree(self, surface, tree):
        t = tree["depth"]
        y_base = int(HORIZON_Y + (self.sh - HORIZON_Y) * t)
        road_w = ROAD_WIDTH_TOP + (ROAD_WIDTH_BOTTOM - ROAD_WIDTH_TOP) * t
        curve_off = self.curve * t * 160
        mid = self.sw // 2 + curve_off
        gap = road_w // 2 + 20 + tree["offset"] * 80

        x = int(mid + tree["side"] * gap)

        height = max(10, int(80 * t))
        trunk_h = max(4, int(height * 0.35))
        trunk_w = max(3, int(8 * t))

        # Trunk
        pygame.draw.rect(surface, (100, 60, 20),
                         (x - trunk_w//2, y_base - trunk_h, trunk_w, trunk_h))

        # Foliage
        foliage_r = max(6, int(height * 0.65))
        if tree["kind"] == "pine":
            pts = [
                (x, y_base - trunk_h - foliage_r),
                (x - foliage_r, y_base - trunk_h),
                (x + foliage_r, y_base - trunk_h),
            ]
            pygame.draw.polygon(surface, tree["color"], pts)
        else:
            pygame.draw.circle(surface, tree["color"],
                               (x, y_base - trunk_h - foliage_r//2), foliage_r)
