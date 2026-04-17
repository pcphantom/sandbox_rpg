"""Particle system for visual effects."""
import math
import random
from typing import List, Tuple

import pygame

from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'max_life', 'size')

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: Tuple[int, int, int], life: float,
                 size: int = 2) -> None:
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.color = color; self.life = life; self.max_life = life
        self.size = size


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def emit(self, x: float, y: float, count: int,
             color: Tuple[int, int, int],
             speed: float = 80.0, life: float = 0.5) -> None:
        for _ in range(count):
            a = random.uniform(0, math.tau)
            s = random.uniform(speed * 0.3, speed)
            self.particles.append(
                Particle(x, y, math.cos(a) * s, math.sin(a) * s,
                         color, random.uniform(life * 0.5, life))
            )

    def update(self, dt: float) -> None:
        alive: List[Particle] = []
        for p in self.particles:
            p.life -= dt
            if p.life > 0:
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.vy += 80 * dt
                alive.append(p)
        self.particles = alive

    def draw(self, screen: pygame.Surface, cx: float, cy: float) -> None:
        for p in self.particles:
            sx = int(p.x - cx)
            sy = int(p.y - cy)
            if 0 <= sx < SCREEN_WIDTH and 0 <= sy < SCREEN_HEIGHT:
                r = max(1, int(p.size * (p.life / p.max_life)))
                pygame.draw.circle(screen, p.color, (sx, sy), r)
