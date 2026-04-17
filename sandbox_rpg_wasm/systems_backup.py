"""Game systems — movement, physics, rendering, AI, day/night, projectiles."""
import math
import random
from typing import Any

import pygame

from constants import (TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
                       DIFFICULTY_EASY, DIFFICULTY_MULTIPLIERS,
                       MOB_RESPAWN_INTERVAL, RANGED_ENEMY_START_DAY)
from data.day_night import (TIME_NIGHT_END, TIME_DAY_START, TIME_DAY_END,
                            TIME_NIGHT_START, DAY_FLASH_DURATION,
                            NIGHT_FLASH_DURATION)
from data.day_events import (WAVE_SPAWN_INITIAL_INTERVAL, WAVE_SPAWN_MIN_INTERVAL,
                             WAVE_INTERVAL_REDUCTION, WAVE_SPAWN_BATCH)
from utils import clamp
from ecs import EntityManager
from components import (Transform, Velocity, Renderable, Collider, Health,
                        AI, Placeable, Projectile, Equipment, PlayerStats,
                        Turret, Building, Storage)
from data import ARMOR_VALUES

# -- Movement ------------------------------------------------------------------
VELOCITY_DEADZONE: float = 0.5

# -- Rendering -----------------------------------------------------------------
RENDER_CULL_MARGIN: int = 64

# -- Day/Night time boundaries (imported from data.day_night) ------------------

# -- AI behaviour --------------------------------------------------------------
AI_PROBE_STEP_MULT: float = 0.75
MOB_STRUCTURE_ATTACK_CD: float = 1.5
CHASE_DETECT_MULT: float = 0.7
WANDER_TIME_MIN: float = 1.5
WANDER_TIME_MAX: float = 3.5
CHASE_DISENGAGE_MULT: float = 2.0
AGGRO_DISENGAGE_MULT: float = 2.0      # 2x detection for aggro'd normal mobs
AGGRO_BOSS_DISENGAGE_MULT: float = 3.0 # 3x detection for aggro'd boss/elite mobs
RANGED_MIN_DISTANCE: float = 60.0
RANGED_RETREAT_DISTANCE: float = 100.0
RANGED_RETREAT_SPEED_MULT: float = 0.5
RANGED_STRAFE_SPEED_MULT: float = 0.6
CHASE_MIN_DISTANCE: float = 5.0
CHASE_SPEED_MULT: float = 1.3
STUCK_WANTED_MULT: float = 0.3
STUCK_MIN_DISTANCE: float = 30.0
STUCK_TIME_THRESHOLD: float = 0.3

# -- Projectiles ---------------------------------------------------------------
PROJ_MOB_HIT_RADIUS: float = 20.0

# -- Traps ---------------------------------------------------------------------
TRAP_TRIGGER_RADIUS: float = 24.0
TRAP_SELF_DAMAGE: int = 10

# -- Wave system (imported from data.day_events) -------------------------------

# -- Combat helpers ------------------------------------------------------------
BASE_MELEE_DAMAGE_MIN: int = 5
STR_DAMAGE_MULT: int = 2
LEVEL_DAMAGE_MULT: int = 2
AGI_RANGED_DAMAGE_MULT: int = 2


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
            if abs(v.vx) < VELOCITY_DEADZONE:
                v.vx = 0
            if abs(v.vy) < VELOCITY_DEADZONE:
                v.vy = 0


# ======================================================================
# PHYSICS
# ======================================================================
class PhysicsSystem:
    def __init__(self, ww: int, wh: int) -> None:
        self.ww = ww; self.wh = wh
        self._building_rects: list[tuple[int, float, float, int, int]] = []

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

    def _entity_blocked(self, eid: int, x: float, y: float,
                        w: int, h: int) -> int:
        """Check if rect (x, y, w, h) overlaps any solid building collider.
        Returns the blocking entity id or 0."""
        r = x + w
        b = y + h
        for bid, bx, by, bw, bh in self._building_rects:
            if bid == eid:
                continue
            if x < bx + bw and r > bx and y < by + bh and b > by:
                return bid
        return 0

    def _rebuild_building_rects(self, em: EntityManager) -> None:
        """Cache solid building/placeable collider AABBs each frame."""
        self._building_rects.clear()
        for bid in em.get_entities_with(Transform, Collider):
            # Only static solid colliders (buildings) — skip entities with Velocity
            bc = em.get_component(bid, Collider)
            if not bc.solid:
                continue
            if em.has_component(bid, Velocity):
                continue
            bt = em.get_component(bid, Transform)
            self._building_rects.append(
                (bid, bt.x, bt.y, bc.width, bc.height))

    def update(self, dt: float, em: EntityManager, world: Any) -> None:
        self._rebuild_building_rects(em)
        for eid in em.get_entities_with(Transform, Collider, Velocity):
            t = em.get_component(eid, Transform)
            c = em.get_component(eid, Collider)
            v = em.get_component(eid, Velocity)
            if c.solid:
                nx = t.x + v.vx * dt
                if (not self._tile_solid(nx, t.y, c.width, c.height, world)
                        and not self._entity_blocked(eid, nx, t.y,
                                                     c.width, c.height)):
                    t.x = nx
                else:
                    v.vx = 0
                ny = t.y + v.vy * dt
                if (not self._tile_solid(t.x, ny, c.width, c.height, world)
                        and not self._entity_blocked(eid, t.x, ny,
                                                     c.width, c.height)):
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
            if (sx < -RENDER_CULL_MARGIN or sx > SCREEN_WIDTH + RENDER_CULL_MARGIN
                    or sy < -RENDER_CULL_MARGIN or sy > SCREEN_HEIGHT + RENDER_CULL_MARGIN):
                continue
            surf = (pygame.transform.flip(r.surface, r.flip_x, False)
                    if r.flip_x else r.surface)
            self.screen.blit(surf, (sx, sy))


# ======================================================================
# DAY / NIGHT
# ======================================================================
class DayNightCycle:
    def __init__(self, day_length: float = 960.0) -> None:
        self.time = TIME_DAY_START
        self.day_length = day_length
        self._speed_mult = 1.0
        self.day_number: int = 1
        self._was_day: bool = True
        self._day_flash_timer: float = 0.0
        self._night_flash_timer: float = 0.0

    def update(self, dt: float) -> None:
        old_time = self.time
        self.time = (self.time + dt * self._speed_mult / self.day_length) % 1.0
        # Detect day transition (night -> dawn)
        is_day_now = TIME_DAY_START <= self.time < TIME_DAY_END
        if is_day_now and not self._was_day:
            self.day_number += 1
            self._day_flash_timer = DAY_FLASH_DURATION
        # Detect night start (dusk -> night)
        if not is_day_now and self._was_day:
            self._night_flash_timer = NIGHT_FLASH_DURATION
        self._was_day = is_day_now
        self._day_flash_timer = max(0.0, self._day_flash_timer - dt)
        self._night_flash_timer = max(0.0, self._night_flash_timer - dt)

    def set_speed(self, mult: float) -> None:
        self._speed_mult = mult

    def reset_speed(self) -> None:
        self._speed_mult = 1.0

    def get_darkness(self) -> float:
        t = self.time
        if TIME_DAY_START < t < TIME_DAY_END:
            return 0.0
        if t <= TIME_DAY_START:
            return 1.0 - t / TIME_DAY_START
        return (t - TIME_DAY_END) / TIME_DAY_START

    def get_period_name(self) -> str:
        t = self.time
        if t < TIME_NIGHT_END:
            return "Night"
        if t < TIME_DAY_START:
            return "Dawn"
        if t < TIME_DAY_END:
            return "Day"
        if t < TIME_NIGHT_START:
            return "Dusk"
        return "Night"

    def is_night(self) -> bool:
        t = self.time
        return t < TIME_NIGHT_END or t >= TIME_NIGHT_START

    def is_sleepable(self) -> bool:
        """True during Dusk or Night — when the player should be able to sleep."""
        t = self.time
        return t < TIME_NIGHT_END or t >= TIME_DAY_END


# ======================================================================
# AI SYSTEM
# ======================================================================
class AISystem:
    def __init__(self) -> None:
        self._stuck_timers: dict[int, float] = {}

    def _find_blocking_wall(self, eid: int, t: 'Transform',
                            dx: float, dy: float, dist: float,
                            em: EntityManager) -> int:
        """Check if a solid building is between the mob and its target.
        Returns the blocking entity id or 0."""
        if dist < 1:
            return 0
        c = em.get_component(eid, Collider)
        cw = c.width if c else 16
        ch = c.height if c else 16
        # Probe one step ahead in the direction of movement
        step = max(cw, ch) * AI_PROBE_STEP_MULT
        probe_x = t.x + (dx / dist) * step
        probe_y = t.y + (dy / dist) * step
        for bid in em.get_entities_with(Transform, Collider):
            if bid == eid:
                continue
            bc = em.get_component(bid, Collider)
            if not bc.solid:
                continue
            if em.has_component(bid, Velocity):
                continue
            if not em.has_component(bid, Health):
                continue
            bt = em.get_component(bid, Transform)
            if (probe_x < bt.x + bc.width and probe_x + cw > bt.x
                    and probe_y < bt.y + bc.height and probe_y + ch > bt.y):
                return bid
        return 0

    def update(self, dt: float, em: EntityManager, player_id: int,
               on_ranged_fire: Any = None) -> None:
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
            mob_ai.ranged_timer = max(0, mob_ai.ranged_timer - dt)
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
                            mob_ai.attack_timer = MOB_STRUCTURE_ATTACK_CD
                else:
                    mob_ai.state = "idle"
                    mob_ai.target_id = None
                # Switch to player chase if player is close
                if dist < mob_ai.detection_range * CHASE_DETECT_MULT:
                    mob_ai.state = "chase"
                    mob_ai.target_id = None
                continue

            if mob_ai.behavior == "wander":
                if dist < mob_ai.detection_range or mob_ai.aggro:
                    mob_ai.state = "chase"
                elif mob_ai.timer <= 0:
                    angle = random.uniform(0, math.tau)
                    v.vx = math.cos(angle) * mob_ai.speed
                    v.vy = math.sin(angle) * mob_ai.speed
                    mob_ai.timer = random.uniform(WANDER_TIME_MIN, WANDER_TIME_MAX)

            if mob_ai.state == "chase":
                # Determine disengage range based on aggro state
                if mob_ai.aggro:
                    disengage = mob_ai.detection_range * (
                        AGGRO_BOSS_DISENGAGE_MULT if mob_ai.is_boss
                        else AGGRO_DISENGAGE_MULT)
                else:
                    disengage = mob_ai.detection_range * CHASE_DISENGAGE_MULT
                if dist > disengage:
                    mob_ai.state = "idle"
                    mob_ai.aggro = False
                    self._stuck_timers.pop(eid, None)
                elif mob_ai.is_ranged and dist < mob_ai.ranged_range and dist > RANGED_MIN_DISTANCE:
                    # Ranged enemy: keep distance and shoot
                    if mob_ai.ranged_timer <= 0 and on_ranged_fire:
                        on_ranged_fire(eid, t, pt)
                        mob_ai.ranged_timer = mob_ai.ranged_cooldown
                    # Strafe rather than charge
                    if dist < RANGED_RETREAT_DISTANCE:
                        v.vx = -(dx / dist) * mob_ai.speed * RANGED_RETREAT_SPEED_MULT
                        v.vy = -(dy / dist) * mob_ai.speed * RANGED_RETREAT_SPEED_MULT
                    else:
                        perp_x = -dy / dist
                        perp_y = dx / dist
                        v.vx = perp_x * mob_ai.speed * RANGED_STRAFE_SPEED_MULT
                        v.vy = perp_y * mob_ai.speed * RANGED_STRAFE_SPEED_MULT
                elif dist > CHASE_MIN_DISTANCE:
                    v.vx = (dx / dist) * mob_ai.speed * CHASE_SPEED_MULT
                    v.vy = (dy / dist) * mob_ai.speed * CHASE_SPEED_MULT
                    # Detect if stuck against a wall and attack it
                    moved = math.hypot(t.x - t.prev_x, t.y - t.prev_y)
                    wanted = mob_ai.speed * CHASE_SPEED_MULT * dt * STUCK_WANTED_MULT
                    if moved < wanted and dist > STUCK_MIN_DISTANCE:
                        self._stuck_timers[eid] = self._stuck_timers.get(eid, 0) + dt
                        if self._stuck_timers[eid] > STUCK_TIME_THRESHOLD:
                            wall_id = self._find_blocking_wall(
                                eid, t, dx, dy, dist, em)
                            if wall_id:
                                mob_ai.state = "attack_structure"
                                mob_ai.target_id = wall_id
                                self._stuck_timers.pop(eid, None)
                    else:
                        self._stuck_timers.pop(eid, None)


# ======================================================================
# PROJECTILE SYSTEM
# ======================================================================
class ProjectileSystem:
    """Move projectiles, check collisions with mobs, despawn on range."""

    def update(self, dt: float, em: EntityManager,
               on_hit: Any = None) -> None:
        """on_hit(eid_target, damage, proj_transform, proj_component) callback."""
        to_remove = []
        for pid in em.get_entities_with(Transform, Velocity, Projectile):
            pt = em.get_component(pid, Transform)
            proj = em.get_component(pid, Projectile)
            vp = em.get_component(pid, Velocity)
            moved = math.hypot(vp.vx * dt, vp.vy * dt)
            proj.distance_traveled += moved
            if proj.distance_traveled >= proj.max_range:
                # Bombs explode at max range too
                if proj.is_bomb and on_hit:
                    on_hit(-1, proj.damage, pt, proj)
                to_remove.append(pid)
                continue
            # Check collision with mobs
            for mid in em.get_entities_with(Transform, Health, AI):
                mt = em.get_component(mid, Transform)
                if math.hypot(mt.x - pt.x, mt.y - pt.y) < PROJ_MOB_HIT_RADIUS:
                    mh = em.get_component(mid, Health)
                    if not proj.is_bomb:
                        mh.damage(proj.damage)
                    # Aggro the mob when hit by a player projectile
                    mob_ai = em.get_component(mid, AI)
                    if mob_ai and proj.owner != mid:
                        mob_ai.aggro = True
                        mob_ai.state = "chase"
                    if on_hit:
                        on_hit(mid, proj.damage, pt, proj)
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
                if math.hypot(mt.x - tt.x, mt.y - tt.y) < TRAP_TRIGGER_RADIUS:
                    mh = em.get_component(mid, Health)
                    mh.damage(self.TRAP_DAMAGE)
                    self._cooldowns[tid] = self.TRAP_COOLDOWN
                    # Degrade trap HP
                    th = em.get_component(tid, Health)
                    if th:
                        th.damage(TRAP_SELF_DAMAGE)
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

    def __init__(self, difficulty: int = DIFFICULTY_EASY) -> None:
        self.night_count: int = 0
        self.was_night: bool = False
        self.wave_active: bool = False
        self.wave_spawned: int = 0
        self.wave_target: int = 0
        self.wave_timer: float = 0.0
        self.wave_spawn_interval: float = WAVE_SPAWN_INITIAL_INTERVAL
        self.current_tier: int = 0
        self.difficulty: int = difficulty
        self.boss_spawned_this_wave: bool = False

    def update(self, dt: float, is_night: bool, day_number: int = 1) -> dict | None:
        """Returns spawn request dict or None.
        {'count': N, 'tier': T, 'ranged': bool, 'boss': bool}"""
        if is_night and not self.was_night:
            # Night just started
            self.night_count += 1
            from data.day_events import (WAVE_START_NIGHT, WAVE_BASE_COUNT,
                                          WAVE_SCALE_PER_NIGHT,
                                          WAVE_DAY_BONUS_PER_DAY)
            if self.night_count >= WAVE_START_NIGHT:
                self.wave_active = True
                self.wave_spawned = 0
                self.boss_spawned_this_wave = False
                diff = self.night_count - WAVE_START_NIGHT
                # Scale wave count with difficulty
                _, _, _, wave_mult = DIFFICULTY_MULTIPLIERS.get(
                    self.difficulty, (1.0, 1.0, 1.0, 1.0))
                base_count = WAVE_BASE_COUNT + diff * WAVE_SCALE_PER_NIGHT
                # Each day adds slightly more enemies
                day_bonus = max(0, (day_number - 1)) * WAVE_DAY_BONUS_PER_DAY
                self.wave_target = int((base_count + day_bonus) * wave_mult)
                self.current_tier = min(3, diff // 2)
                self.wave_timer = 0.0
                self.wave_spawn_interval = max(WAVE_SPAWN_MIN_INTERVAL,
                    WAVE_SPAWN_INITIAL_INTERVAL - diff * WAVE_INTERVAL_REDUCTION)
        elif not is_night and self.was_night:
            self.wave_active = False
        self.was_night = is_night

        if not self.wave_active or self.wave_spawned >= self.wave_target:
            return None

        self.wave_timer += dt
        if self.wave_timer >= self.wave_spawn_interval:
            self.wave_timer = 0.0
            batch = min(WAVE_SPAWN_BATCH, self.wave_target - self.wave_spawned)
            self.wave_spawned += batch
            # Determine if ranged enemies should be included
            include_ranged = day_number > RANGED_ENEMY_START_DAY
            # Boss spawn: one per wave, after tier 2+
            include_boss = (not self.boss_spawned_this_wave
                            and self.current_tier >= 2
                            and self.wave_spawned >= self.wave_target // 2)
            if include_boss:
                self.boss_spawned_this_wave = True
            return {'count': batch, 'tier': self.current_tier,
                    'ranged': include_ranged, 'boss': include_boss}
        return None


# ======================================================================
# COMBAT HELPERS
# ======================================================================
def calc_melee_damage(base_item_dmg: int, stats: PlayerStats,
                      equipment: Equipment | None) -> int:
    """Calculate melee hit damage including STR bonus."""
    dmg = max(base_item_dmg, BASE_MELEE_DAMAGE_MIN) + stats.strength * STR_DAMAGE_MULT + (stats.level - 1) * LEVEL_DAMAGE_MULT
    return dmg


def calc_ranged_damage(ranged_base: int, ammo_bonus: int,
                       stats: PlayerStats) -> int:
    return ranged_base + ammo_bonus + stats.agility * AGI_RANGED_DAMAGE_MULT


def calc_damage_reduction(equipment: Equipment | None) -> int:
    if equipment is None:
        return 0
    total = 0
    if equipment.armor and equipment.armor in ARMOR_VALUES:
        total += ARMOR_VALUES[equipment.armor]
    if equipment.shield and equipment.shield in ARMOR_VALUES:
        total += ARMOR_VALUES[equipment.shield]
    return total
