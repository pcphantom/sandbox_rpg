"""Game systems — movement, physics, rendering, AI, day/night, projectiles."""
import math
import random
from typing import Any

import pygame

from constants import (TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT)
from utils import clamp
from ecs import EntityManager
from components import (Transform, Velocity, Renderable, Collider, Health,
                        AI, Placeable, Projectile, Equipment, PlayerStats,
                        Turret, Building, Storage)
from items_data import ARMOR_VALUES


# ======================================================================
# MOVEMENT
# ======================================================================
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


# ======================================================================
# PHYSICS
# ======================================================================
class PhysicsSystem:
    def __init__(self, ww: int, wh: int) -> None:
        self.ww = ww; self.wh = wh

    def _tile_solid(self, x: float, y: float, w: int, h: int,
                    world: Any) -> bool:
        left = int(x // TILE_SIZE)
        right = int((x + w - 1) // TILE_SIZE)
        top = int(y // TILE_SIZE)
        bot = int((y + h - 1) // TILE_SIZE)
        for tx in range(left, right + 1):
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


# ======================================================================
# RENDER
# ======================================================================
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
            if (sx < -64 or sx > SCREEN_WIDTH + 64
                    or sy < -64 or sy > SCREEN_HEIGHT + 64):
                continue
            surf = (pygame.transform.flip(r.surface, r.flip_x, False)
                    if r.flip_x else r.surface)
            self.screen.blit(surf, (sx, sy))


# ======================================================================
# DAY / NIGHT
# ======================================================================
class DayNightCycle:
    def __init__(self, day_length: float = 300.0) -> None:
        self.time = 0.30
        self.day_length = day_length
        self._speed_mult = 1.0

    def update(self, dt: float) -> None:
        self.time = (self.time + dt * self._speed_mult / self.day_length) % 1.0

    def set_speed(self, mult: float) -> None:
        self._speed_mult = mult

    def reset_speed(self) -> None:
        self._speed_mult = 1.0

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

    def is_night(self) -> bool:
        return self.get_darkness() > 0.4


# ======================================================================
# AI SYSTEM
# ======================================================================
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

            # Target placeables when idle/wandering
            if mob_ai.state != "chase" and mob_ai.behavior == "wander":
                best_placeable = None
                best_distance = mob_ai.detection_range
                for pid in em.get_entities_with(Transform, Placeable, Health):
                    pt2 = em.get_component(pid, Transform)
                    d2 = math.hypot(pt2.x - t.x, pt2.y - t.y)
                    if d2 < best_distance:
                        best_distance = d2
                        best_placeable = pid
                if best_placeable is not None:
                    mob_ai.state = "attack_structure"
                    mob_ai.target_id = best_placeable

            if mob_ai.state == "attack_structure":
                target = mob_ai.target_id
                if (target and em.has_component(target, Transform)
                        and em.has_component(target, Health)):
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
                # Switch to player chase if player is close
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


# ======================================================================
# PROJECTILE SYSTEM
# ======================================================================
class ProjectileSystem:
    """Move projectiles, check collisions with mobs, despawn on range."""

    def update(self, dt: float, em: EntityManager,
               on_hit: Any = None) -> None:
        """on_hit(eid_target, damage, proj_transform) callback."""
        to_remove = []
        for pid in em.get_entities_with(Transform, Velocity, Projectile):
            pt = em.get_component(pid, Transform)
            proj = em.get_component(pid, Projectile)
            vp = em.get_component(pid, Velocity)
            moved = math.hypot(vp.vx * dt, vp.vy * dt)
            proj.distance_traveled += moved
            if proj.distance_traveled >= proj.max_range:
                to_remove.append(pid)
                continue
            # Check collision with mobs
            for mid in em.get_entities_with(Transform, Health, AI):
                mt = em.get_component(mid, Transform)
                if math.hypot(mt.x - pt.x, mt.y - pt.y) < 20:
                    mh = em.get_component(mid, Health)
                    mh.damage(proj.damage)
                    if on_hit:
                        on_hit(mid, proj.damage, pt)
                    to_remove.append(pid)
                    break
        for pid in set(to_remove):
            em.destroy_entity(pid)


# ======================================================================
# TRAP SYSTEM
# ======================================================================
class TrapSystem:
    """Damage mobs that step on traps."""

    TRAP_DAMAGE = 15
    TRAP_COOLDOWN = 1.5

    def __init__(self) -> None:
        self._cooldowns: dict[int, float] = {}

    def update(self, dt: float, em: EntityManager,
               on_hit: Any = None) -> None:
        # Tick cooldowns
        for k in list(self._cooldowns):
            self._cooldowns[k] -= dt
            if self._cooldowns[k] <= 0:
                del self._cooldowns[k]

        for tid in em.get_entities_with(Transform, Placeable):
            pl = em.get_component(tid, Placeable)
            if pl.item_type != 'trap':
                continue
            if tid in self._cooldowns:
                continue
            tt = em.get_component(tid, Transform)
            for mid in em.get_entities_with(Transform, Health, AI):
                mt = em.get_component(mid, Transform)
                if math.hypot(mt.x - tt.x, mt.y - tt.y) < 24:
                    mh = em.get_component(mid, Health)
                    mh.damage(self.TRAP_DAMAGE)
                    self._cooldowns[tid] = self.TRAP_COOLDOWN
                    # Degrade trap HP
                    th = em.get_component(tid, Health)
                    if th:
                        th.damage(10)
                    if on_hit:
                        on_hit(mid, self.TRAP_DAMAGE, tt)
                    break


# ======================================================================
# TURRET SYSTEM
# ======================================================================
class TurretSystem:
    """Auto-fires projectiles at the nearest mob within range."""

    def update(self, dt: float, em: EntityManager,
               on_fire: Any = None) -> None:
        for tid in em.get_entities_with(Transform, Turret, Health):
            th = em.get_component(tid, Health)
            if not th.is_alive():
                continue
            turr = em.get_component(tid, Turret)
            turr.timer = max(0, turr.timer - dt)
            if turr.timer > 0:
                continue
            tt = em.get_component(tid, Transform)
            # Find nearest mob
            best_eid, best_dist = None, turr.fire_range
            for mid in em.get_entities_with(Transform, Health, AI):
                mt = em.get_component(mid, Transform)
                d = math.hypot(mt.x - tt.x, mt.y - tt.y)
                if d < best_dist:
                    best_dist = d
                    best_eid = mid
            if best_eid is not None:
                mt = em.get_component(best_eid, Transform)
                mh = em.get_component(best_eid, Health)
                mh.damage(turr.damage)
                turr.timer = turr.cooldown
                if on_fire:
                    on_fire(best_eid, turr.damage, tt, mt)


# ======================================================================
# WAVE SYSTEM
# ======================================================================
class WaveSystem:
    """Manages night-time enemy wave spawning with escalating difficulty."""

    def __init__(self) -> None:
        self.night_count: int = 0
        self.was_night: bool = False
        self.wave_active: bool = False
        self.wave_spawned: int = 0
        self.wave_target: int = 0
        self.wave_timer: float = 0.0
        self.wave_spawn_interval: float = 2.0
        self.current_tier: int = 0

    def update(self, dt: float, is_night: bool) -> dict | None:
        """Returns spawn request dict or None.
        {'count': N, 'tier': T} when mobs should be spawned."""
        if is_night and not self.was_night:
            # Night just started
            self.night_count += 1
            from constants import WAVE_START_NIGHT, WAVE_BASE_COUNT, WAVE_SCALE_PER_NIGHT
            if self.night_count >= WAVE_START_NIGHT:
                self.wave_active = True
                self.wave_spawned = 0
                diff = self.night_count - WAVE_START_NIGHT
                self.wave_target = WAVE_BASE_COUNT + diff * WAVE_SCALE_PER_NIGHT
                self.current_tier = min(3, diff // 2)
                self.wave_timer = 0.0
                self.wave_spawn_interval = max(0.8, 2.0 - diff * 0.1)
        elif not is_night and self.was_night:
            self.wave_active = False
        self.was_night = is_night

        if not self.wave_active or self.wave_spawned >= self.wave_target:
            return None

        self.wave_timer += dt
        if self.wave_timer >= self.wave_spawn_interval:
            self.wave_timer = 0.0
            batch = min(3, self.wave_target - self.wave_spawned)
            self.wave_spawned += batch
            return {'count': batch, 'tier': self.current_tier}
        return None


# ======================================================================
# COMBAT HELPERS
# ======================================================================
def calc_melee_damage(base_item_dmg: int, stats: PlayerStats,
                      equipment: Equipment | None) -> int:
    """Calculate melee hit damage including STR bonus."""
    dmg = max(base_item_dmg, 5) + stats.strength * 2 + (stats.level - 1) * 2
    return dmg


def calc_ranged_damage(ranged_base: int, ammo_bonus: int,
                       stats: PlayerStats) -> int:
    return ranged_base + ammo_bonus + stats.dexterity * 2


def calc_damage_reduction(equipment: Equipment | None) -> int:
    if equipment is None:
        return 0
    total = 0
    if equipment.armor and equipment.armor in ARMOR_VALUES:
        total += ARMOR_VALUES[equipment.armor]
    if equipment.shield and equipment.shield in ARMOR_VALUES:
        total += ARMOR_VALUES[equipment.shield]
    return total
