"""Game systems for the sandbox RPG."""
import math
import random
import pygame
from typing import Any

from ecs import EntityManager
from components import (Transform, Velocity, Renderable, Collider, Health,
                        AI, Placeable)

TILE_SIZE = 32
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


def clamp(v: float, mn: float, mx: float) -> float:
    return max(mn, min(mx, v))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class MovementSystem:
    def update(self, dt: float, em: EntityManager) -> None:
        for eid in em.get_entities_with(Transform, Velocity):
            t = em.get_component(eid, Transform)
            v = em.get_component(eid, Velocity)
            t.prev_x, t.prev_y = t.x, t.y
            t.x += v.vx * dt
            t.y += v.vy * dt
            v.vx *= v.friction
            v.vy *= v.friction
            if abs(v.vx) < 0.5:
                v.vx = 0
            if abs(v.vy) < 0.5:
                v.vy = 0


class PhysicsSystem:
    def __init__(self, ww: int, wh: int) -> None:
        self.ww = ww; self.wh = wh

    def _tile_solid(self, x: float, y: float, w: int, h: int, world: Any) -> bool:
        l = int(x // TILE_SIZE)
        r = int((x + w - 1) // TILE_SIZE)
        top = int(y // TILE_SIZE)
        bot = int((y + h - 1) // TILE_SIZE)
        for tx in range(l, r + 1):
            for ty in range(top, bot + 1):
                if world.is_solid(tx, ty):
                    return True
        return False

    def update(self, dt: float, em: EntityManager, world: Any) -> None:
        for eid in em.get_entities_with(Transform, Collider, Velocity):
            t = em.get_component(eid, Transform)
            c = em.get_component(eid, Collider)
            v = em.get_component(eid, Velocity)
            if c.solid:
                nx = t.x + v.vx * dt
                if not self._tile_solid(nx, t.y, c.width, c.height, world):
                    t.x = nx
                else:
                    v.vx = 0
                ny = t.y + v.vy * dt
                if not self._tile_solid(t.x, ny, c.width, c.height, world):
                    t.y = ny
                else:
                    v.vy = 0
            t.x = clamp(t.x, 0, self.ww * TILE_SIZE - c.width)
            t.y = clamp(t.y, 0, self.wh * TILE_SIZE - c.height)


class RenderSystem:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def update(self, em: EntityManager, camera: Any) -> None:
        ents = em.get_entities_with(Transform, Renderable)
        ents.sort(key=lambda e: (em.get_component(e, Renderable).layer,
                                 em.get_component(e, Transform).y))
        for eid in ents:
            t = em.get_component(eid, Transform)
            r = em.get_component(eid, Renderable)
            if not r.visible:
                continue
            sx = int(t.x - camera.x + r.offset_x)
            sy = int(t.y - camera.y + r.offset_y)
            if sx < -64 or sx > SCREEN_WIDTH + 64 or sy < -64 or sy > SCREEN_HEIGHT + 64:
                continue
            surf = pygame.transform.flip(r.surface, r.flip_x, False) if r.flip_x else r.surface
            self.screen.blit(surf, (sx, sy))


class DayNightCycle:
    def __init__(self, day_length: float = 300.0) -> None:
        self.time = 0.30; self.day_length = day_length

    def update(self, dt: float) -> None:
        self.time = (self.time + dt / self.day_length) % 1.0

    def get_darkness(self) -> float:
        t = self.time
        if 0.30 < t < 0.70:
            return 0.0
        if t <= 0.30:
            return 1.0 - t / 0.30
        return (t - 0.70) / 0.30

    def get_period_name(self) -> str:
        t = self.time
        if t < 0.22:
            return "Night"
        if t < 0.30:
            return "Dawn"
        if t < 0.70:
            return "Day"
        if t < 0.78:
            return "Dusk"
        return "Night"


class AISystem:
    def update(self, dt: float, em: EntityManager, player_id: int) -> None:
        pt = em.get_component(player_id, Transform)
        if not pt:
            return
        for eid in em.get_entities_with(Transform, Velocity, AI):
            if eid == player_id:
                continue
            t = em.get_component(eid, Transform)
            v = em.get_component(eid, Velocity)
            mob_ai = em.get_component(eid, AI)
            mob_ai.timer -= dt
            mob_ai.attack_timer = max(0, mob_ai.attack_timer - dt)
            dx = pt.x - t.x
            dy = pt.y - t.y
            dist = math.hypot(dx, dy)

            # Check for nearby placeables to attack
            if mob_ai.state != "chase" and mob_ai.behavior == "wander":
                best_placeable = None
                best_dist = mob_ai.detection_range
                for pid in em.get_entities_with(Transform, Placeable, Health):
                    pt2 = em.get_component(pid, Transform)
                    d2 = math.hypot(pt2.x - t.x, pt2.y - t.y)
                    if d2 < best_dist:
                        best_dist = d2
                        best_placeable = pid
                if best_placeable is not None:
                    mob_ai.state = "attack_structure"
                    mob_ai.target_id = best_placeable

            if mob_ai.state == "attack_structure":
                target = mob_ai.target_id
                if target and em.has_component(target, Transform) and em.has_component(target, Health):
                    tt = em.get_component(target, Transform)
                    th = em.get_component(target, Health)
                    if not th.is_alive():
                        mob_ai.state = "idle"
                        mob_ai.target_id = None
                    else:
                        ddx = tt.x - t.x
                        ddy = tt.y - t.y
                        ddist = math.hypot(ddx, ddy)
                        if ddist > mob_ai.detection_range * 2:
                            mob_ai.state = "idle"
                            mob_ai.target_id = None
                        elif ddist > 20:
                            v.vx = (ddx / ddist) * mob_ai.speed
                            v.vy = (ddy / ddist) * mob_ai.speed
                        elif mob_ai.attack_timer <= 0:
                            th.damage(mob_ai.contact_damage)
                            mob_ai.attack_timer = 1.5
                else:
                    mob_ai.state = "idle"
                    mob_ai.target_id = None
                if dist < mob_ai.detection_range * 0.7:
                    mob_ai.state = "chase"
                    mob_ai.target_id = None
                continue

            if mob_ai.behavior == "wander":
                if dist < mob_ai.detection_range:
                    mob_ai.state = "chase"
                elif mob_ai.timer <= 0:
                    angle = random.uniform(0, math.tau)
                    v.vx = math.cos(angle) * mob_ai.speed
                    v.vy = math.sin(angle) * mob_ai.speed
                    mob_ai.timer = random.uniform(1.5, 3.5)
            if mob_ai.state == "chase":
                if dist > mob_ai.detection_range * 2.0:
                    mob_ai.state = "idle"
                elif dist > 5:
                    v.vx = (dx / dist) * mob_ai.speed * 1.3
                    v.vy = (dy / dist) * mob_ai.speed * 1.3
