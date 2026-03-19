"""
particles.py - Particle effects: sparks, smoke, dust
"""

import pygame
import random
import math
from constants import *


class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, fade=True):
        self.x     = float(x)
        self.y     = float(y)
        self.vx    = vx
        self.vy    = vy
        self.color = color
        self.size  = size
        self.life  = life
        self.max_life = life
        self.fade  = fade

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.15   # gravity
        self.vx *= 0.96
        self.life -= 1

    def draw(self, surface):
        ratio = self.life / self.max_life
        alpha = int(255 * ratio) if self.fade else 255
        size  = max(1, int(self.size * ratio))
        col   = self.color

        surf = pygame.Surface((size*2+2, size*2+2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*col, alpha), (size+1, size+1), size)
        surface.blit(surf, (int(self.x) - size - 1, int(self.y) - size - 1))

    @property
    def alive(self):
        return self.life > 0


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_crash(self, x, y):
        """Big crash explosion."""
        for _ in range(40):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 9)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - random.uniform(1, 4)
            col = random.choice([RED, ORANGE, YELLOW, WHITE, (200,200,200)])
            size = random.randint(3, 9)
            life = random.randint(20, 45)
            self.particles.append(Particle(x, y, vx, vy, col, size, life))

    def emit_dust(self, x, y, speed):
        """Dust trail when driving fast."""
        if random.random() > 0.3:
            return
        vx = random.uniform(-0.5, 0.5)
        vy = random.uniform(-1, -0.3)
        col = (160, 140, 100)
        size = random.randint(2, 5)
        life = random.randint(12, 25)
        self.particles.append(Particle(x, y, vx, vy, col, size, life))

    def emit_skid(self, x, y):
        """Skid sparks."""
        for _ in range(3):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-4, -1)
            col = random.choice([YELLOW, ORANGE, WHITE])
            self.particles.append(Particle(x, y, vx, vy, col, 2, random.randint(8, 18)))

    def update(self):
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update()

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
