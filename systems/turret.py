"""Turret system — auto-fires at nearest mob in range, applies enchant effects."""
import math
from typing import Any, Callable, Optional

from core.ecs import EntityManager
from core.components import Transform, Health, AI, Turret
from enchantments.effects import (
    get_enchant_bonus_damage,
    get_enchant_arc_radius,
    get_enchant_arc_damage_frac,
    get_enchant_slow_factor,
    get_enchant_slow_duration,
    get_enchant_regen_rate,
    ENCHANT_COLORS,
)


class TurretSystem:
    """Auto-fires projectiles at the nearest mob within range.

    Applies enchant effects per shot:
      - fire / strength: bonus flat damage
      - ice: slow the target
      - lightning: arc damage to nearby mobs
      - regen: self-repair HP each second
      - protection: flat DR stacks with enhancement DR (applied in AISystem)

    Enhancement level also grants base DR from core.enhancement.TURRET_DEFENSE_BONUS_PER_LEVEL.
    """

    def update(self, dt: float, em: EntityManager,
               on_fire: Any = None) -> None:
        for tid in em.get_entities_with(Transform, Turret, Health):
            th = em.get_component(tid, Health)
            if not th.is_alive():
                continue
            turr = em.get_component(tid, Turret)

            # --- Regen enchant: self-repair ---
            regen_rate = get_enchant_regen_rate(turr.enchant)
            if regen_rate > 0 and th.current < th.maximum:
                turr.regen_accum += dt
                if turr.regen_accum >= 1.0:
                    turr.regen_accum -= 1.0
                    th.heal(regen_rate)

            # --- Firing cooldown ---
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
            if best_eid is None:
                continue

            mt = em.get_component(best_eid, Transform)
            mh = em.get_component(best_eid, Health)

            # Calculate total damage: base + enchant bonus
            total_dmg = turr.damage + get_enchant_bonus_damage(turr.enchant)
            mh.damage(total_dmg)
            turr.timer = turr.cooldown

            # --- Ice enchant: slow target (via AI speed + on_fire callback) ---
            ice_slow_data = None
            if turr.enchant and turr.enchant['type'] == 'ice':
                ai_target = em.get_component(best_eid, AI)
                if ai_target:
                    slow_factor = get_enchant_slow_factor(turr.enchant)
                    slow_dur = get_enchant_slow_duration(turr.enchant)
                    original_speed = ai_target.speed
                    ai_target.speed *= slow_factor
                    ice_slow_data = (best_eid, original_speed, slow_dur)

            # --- Lightning enchant: arc to nearby mobs ---
            arc_mobs = []
            if turr.enchant and turr.enchant['type'] == 'lightning':
                arc_radius = get_enchant_arc_radius(turr.enchant)
                arc_frac = get_enchant_arc_damage_frac(turr.enchant)
                arc_dmg = max(1, int(total_dmg * arc_frac))
                for mid2 in em.get_entities_with(Transform, Health, AI):
                    if mid2 == best_eid:
                        continue
                    mt2 = em.get_component(mid2, Transform)
                    if math.hypot(mt2.x - mt.x, mt2.y - mt.y) <= arc_radius:
                        mh2 = em.get_component(mid2, Health)
                        mh2.damage(arc_dmg)
                        arc_mobs.append((mid2, arc_dmg, mt2))

            if on_fire:
                on_fire(best_eid, total_dmg, tt, mt,
                        turr.enchant, arc_mobs, ice_slow_data)
