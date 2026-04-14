"""AI system — mob wander, chase, ranged, and structure-attack behaviours."""
import math
import random
from typing import Any

from core.ecs import EntityManager
from core.components import (Transform, Velocity, Collider, Health,
                             AI, Placeable, Turret, Building)
from enchantments.effects import get_enchant_dr_bonus
from core.enhancement import enhanced_turret_dr
from game_controller import (
    AI_PROBE_STEP_MULT, MOB_STRUCTURE_ATTACK_CD,
    CHASE_DETECT_MULT, WANDER_TIME_MIN, WANDER_TIME_MAX,
    CHASE_DISENGAGE_MULT, AGGRO_DISENGAGE_MULT, AGGRO_BOSS_DISENGAGE_MULT,
    RANGED_MIN_DISTANCE, RANGED_RETREAT_DISTANCE,
    RANGED_RETREAT_SPEED_MULT, RANGED_STRAFE_SPEED_MULT,
    CHASE_MIN_DISTANCE, CHASE_SPEED_MULT,
    STUCK_WANTED_MULT, STUCK_MIN_DISTANCE, STUCK_TIME_THRESHOLD,
    BEACON_ATTRACT_RADIUS, BEACON_ATTRACT_SPEED_OUTSIDE,
    BEACON_ATTRACT_SPEED_INSIDE, BEACON_LIGHT_RADIUS,
)

BEACON_MIN_DISTANCE: float = 20.0  # stop moving when this close to beacon


class AISystem:
    def __init__(self) -> None:
        self._stuck_timers: dict[int, float] = {}

    def _find_blocking_wall(self, eid: int, t: 'Transform',
                            dx: float, dy: float, dist: float,
                            em: EntityManager) -> int:
        if dist < 1:
            return 0
        c = em.get_component(eid, Collider)
        cw = c.width if c else 16
        ch = c.height if c else 16
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
               on_ranged_fire: Any = None,
               night_structure_dmg_mult: int = 1,
               is_night: bool = False) -> None:
        pt = em.get_component(player_id, Transform)
        if not pt:
            return
        # Cache beacon positions for attraction logic
        self._is_night = is_night
        self._beacon_positions = []
        if is_night:
            for bid in em.get_entities_with(Transform, Placeable, Building):
                bld = em.get_component(bid, Building)
                if bld.building_type == 'beacon':
                    bt = em.get_component(bid, Transform)
                    self._beacon_positions.append((bt.x + 32, bt.y + 32))
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
                for pid in em.get_entities_with(Transform, Building, Health):
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
                            raw_dmg = mob_ai.contact_damage
                            # Apply night damage multiplier if structure is not near light
                            if night_structure_dmg_mult > 1:
                                near_light = False
                                from core.components import LightSource
                                from game_controller import LIGHT_SAFETY_RADIUS
                                for lid in em.get_entities_with(Transform, LightSource):
                                    lt = em.get_component(lid, Transform)
                                    if math.hypot(lt.x - tt.x, lt.y - tt.y) < LIGHT_SAFETY_RADIUS:
                                        near_light = True
                                        break
                                if not near_light:
                                    raw_dmg *= night_structure_dmg_mult
                            turr = em.get_component(target, Turret)
                            if turr:
                                # Enhancement DR from turret level
                                plc = em.get_component(target, Placeable)
                                if plc and plc.item_type.startswith('turret_') and plc.item_type[len('turret_'):].isdigit():
                                    enh_level = int(plc.item_type[len('turret_'):])
                                else:
                                    enh_level = 0
                                total_dr = enhanced_turret_dr(enh_level)
                                # Protection enchant DR stacks on top
                                if turr.enchant:
                                    total_dr += get_enchant_dr_bonus(turr.enchant)
                                raw_dmg = max(1, raw_dmg - total_dr)
                            th.damage(raw_dmg)
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
                elif self._is_night and self._beacon_positions:
                    # Beacon attraction at night — override wander
                    best_beacon = None
                    best_bdist = BEACON_ATTRACT_RADIUS
                    for bx, by in self._beacon_positions:
                        bdist = math.hypot(bx - t.x, by - t.y)
                        if bdist < best_bdist:
                            best_bdist = bdist
                            best_beacon = (bx, by)
                    if best_beacon is not None and best_bdist > BEACON_MIN_DISTANCE:
                        bx, by = best_beacon
                        bdx = bx - t.x
                        bdy = by - t.y
                        # Inside beacon light → slower approach
                        if best_bdist < BEACON_LIGHT_RADIUS:
                            speed_mult = BEACON_ATTRACT_SPEED_INSIDE
                        else:
                            speed_mult = BEACON_ATTRACT_SPEED_OUTSIDE
                        v.vx = (bdx / best_bdist) * mob_ai.speed * speed_mult
                        v.vy = (bdy / best_bdist) * mob_ai.speed * speed_mult
                    elif mob_ai.timer <= 0:
                        angle = random.uniform(0, math.tau)
                        v.vx = math.cos(angle) * mob_ai.speed
                        v.vy = math.sin(angle) * mob_ai.speed
                        mob_ai.timer = random.uniform(WANDER_TIME_MIN, WANDER_TIME_MAX)
                elif mob_ai.timer <= 0:
                    angle = random.uniform(0, math.tau)
                    v.vx = math.cos(angle) * mob_ai.speed
                    v.vy = math.sin(angle) * mob_ai.speed
                    mob_ai.timer = random.uniform(WANDER_TIME_MIN, WANDER_TIME_MAX)

            if mob_ai.state == "chase":
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
                    if mob_ai.ranged_timer <= 0 and on_ranged_fire:
                        on_ranged_fire(eid, t, pt)
                        mob_ai.ranged_timer = mob_ai.ranged_cooldown
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
