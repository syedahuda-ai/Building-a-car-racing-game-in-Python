"""
game.py - Central Game class: state machine, game loop logic
"""

import pygame
import random
from constants import *
from road      import Road
from player    import PlayerCar
from enemy     import EnemyCar
from hud       import HUD
from ui        import UIRenderer
from particles import ParticleSystem
from highscores import HighScoreManager


class Game:
    def __init__(self, screen, sw, sh):
        self.screen = screen
        self.sw     = sw
        self.sh     = sh

        self.state = STATE_MENU

        # Sub-systems
        self.road     = Road(sw, sh)
        self.player   = PlayerCar(sw, sh)
        self.hud      = HUD(sw, sh)
        self.ui       = UIRenderer(sw, sh)
        self.particles = ParticleSystem()
        self.hs_mgr   = HighScoreManager()

        # Game state
        self.enemies       = []
        self.score         = 0
        self.lives         = 3
        self.difficulty    = "MEDIUM"
        self.spawn_timer   = 0
        self.combo         = 0
        self.combo_timer   = 0
        self.crash_freeze  = 0   # brief freeze frames after crash

    # ── RESET ────────────────────────────────────────────────────────────

    def _reset_game(self):
        self.player    = PlayerCar(self.sw, self.sh)
        self.road      = Road(self.sw, self.sh)
        self.particles = ParticleSystem()
        self.enemies   = []
        self.score     = 0
        self.lives     = 3
        self.spawn_timer  = 0
        self.combo        = 0
        self.combo_timer  = 0
        self.crash_freeze = 0
        self.difficulty   = self.ui.get_selected_difficulty()

    # ── EVENT HANDLER ────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mp = event.pos
            if self.state == STATE_MENU:
                action = self.ui.get_menu_action(mp)
                if action == STATE_PLAYING:
                    self._reset_game()
                    self.state = STATE_PLAYING
                elif action == STATE_DIFFICULTY:
                    self.state = STATE_DIFFICULTY
                elif action == STATE_HIGH_SCORES:
                    self.state = STATE_HIGH_SCORES
                elif action == "QUIT":
                    import sys; pygame.quit(); sys.exit()

            elif self.state == STATE_DIFFICULTY:
                action = self.ui.get_difficulty_action(mp)
                if action == STATE_PLAYING:
                    self._reset_game()
                    self.state = STATE_PLAYING
                elif action == STATE_MENU:
                    self.state = STATE_MENU
                elif action == "SELECT":
                    pass   # already updated in ui

            elif self.state == STATE_PAUSED:
                action = self.ui.get_pause_action(mp)
                if action:
                    if action == STATE_PLAYING:
                        self.state = STATE_PLAYING
                    else:
                        self.state = STATE_MENU

            elif self.state == STATE_GAME_OVER:
                action = self.ui.get_game_over_action(mp)
                if action == STATE_PLAYING:
                    self._reset_game()
                    self.state = STATE_PLAYING
                elif action == STATE_MENU:
                    self.state = STATE_MENU

            elif self.state == STATE_HIGH_SCORES:
                action = self.ui.get_high_scores_action(mp)
                if action:
                    self.state = STATE_MENU

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.state == STATE_PLAYING:
                    self.state = STATE_PAUSED
                elif self.state == STATE_PAUSED:
                    self.state = STATE_PLAYING
                elif self.state in (STATE_MENU, STATE_DIFFICULTY,
                                    STATE_GAME_OVER, STATE_HIGH_SCORES):
                    self.state = STATE_MENU

    # ── UPDATE ────────────────────────────────────────────────────────────

    def update(self):
        self.ui.update()

        if self.state != STATE_PLAYING:
            return

        if self.crash_freeze > 0:
            self.crash_freeze -= 1
            return

        diff_cfg = DIFFICULTIES[self.difficulty]
        keys     = pygame.key.get_pressed()

        # Player
        self.player.handle_input(keys)
        road_l, road_r = self.road.get_road_bounds_at_y(self.player.y)
        self.player.update(road_l, road_r)

        # Road
        self.road.update(self.player.speed, diff_cfg["curve_strength"])

        # Spawn enemies
        self.spawn_timer += 1
        if self.spawn_timer >= diff_cfg["spawn_interval"]:
            self.spawn_timer = 0
            self._spawn_enemy(diff_cfg)

        # Update enemies + project
        for enemy in self.enemies:
            enemy.update()
            self.road.project_enemy(enemy)

        # Check overtake scoring
        for enemy in self.enemies:
            if not enemy.overtaken and enemy.depth > 0.95:
                enemy.overtaken = True
                self.combo += 1
                self.combo_timer = 40
                self.score += SCORE_OVERTAKE * self.combo * diff_cfg["score_mult"]

        # Combo timer decay
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo = 0

        # Collision detection
        for enemy in self.enemies:
            if 0.7 < enemy.depth < 1.0:
                if self.player.collides_with(enemy):
                    self._handle_crash()
                    break

        # Remove off-screen enemies
        self.enemies = [e for e in self.enemies if not e.is_off_screen()]

        # Particles
        if self.player.speed > 3:
            wheel_y = self.player.y + self.player.h // 2 - 10
            self.particles.emit_dust(self.player.x, wheel_y, self.player.speed)

        self.particles.update()

        # Score
        if self.player.speed > 0:
            self.score += int(SCORE_PER_FRAME * diff_cfg["score_mult"]
                              * (self.player.speed / PLAYER_MAX_SPEED + 0.3))

        # HUD
        self.hud.update(
            score      = self.score,
            lives      = self.lives,
            speed      = self.player.speed,
            difficulty = self.difficulty,
            best       = self.hs_mgr.get_best(),
            combo      = self.combo,
            combo_timer= self.combo_timer,
        )

    def _spawn_enemy(self, diff_cfg):
        # Choose a lane (don't spawn directly on player)
        attempts = 0
        while attempts < 5:
            road_pos = random.uniform(0.1, 0.9)
            player_road_pos = (self.player.x - (self.sw//2 - ROAD_WIDTH_BOTTOM//2)) / ROAD_WIDTH_BOTTOM
            if abs(road_pos - player_road_pos) > 0.15:
                break
            attempts += 1

        speed = diff_cfg["enemy_speed"] * random.uniform(0.8, 1.2)
        color = random.choice(ENEMY_COLORS)
        self.enemies.append(EnemyCar(road_pos, speed, color))

    def _handle_crash(self):
        self.player.crash()
        self.particles.emit_crash(self.player.x, self.player.y)
        self.crash_freeze = 15
        self.combo = 0
        self.combo_timer = 0
        self.lives -= 1
        if self.lives <= 0:
            self.hs_mgr.add_score(self.score, self.difficulty)
            self.state = STATE_GAME_OVER

    # ── DRAW ──────────────────────────────────────────────────────────────

    def draw(self):
        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen, self.hs_mgr.get_best())

        elif self.state == STATE_DIFFICULTY:
            self.ui.draw_difficulty(self.screen)

        elif self.state == STATE_HIGH_SCORES:
            self.ui.draw_high_scores(self.screen, self.hs_mgr.get_all())

        elif self.state == STATE_PLAYING:
            self.road.draw(self.screen)
            self.particles.draw(self.screen)

            # Draw enemies sorted back-to-front
            for enemy in sorted(self.enemies, key=lambda e: e.depth):
                enemy.draw(self.screen)

            self.player.draw(self.screen)
            self.hud.draw(self.screen)

        elif self.state == STATE_PAUSED:
            self.road.draw(self.screen)
            for enemy in sorted(self.enemies, key=lambda e: e.depth):
                enemy.draw(self.screen)
            self.player.draw(self.screen)
            self.hud.draw(self.screen)
            self.ui.draw_pause(self.screen)

        elif self.state == STATE_GAME_OVER:
            self.ui.draw_game_over(
                self.screen, self.score,
                self.hs_mgr.get_best(), self.difficulty
            )
