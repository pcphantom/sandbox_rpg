"""Trap system — damage mobs that step on player-placed traps."""
import math
from typing import Any

from core.ecs import EntityManager
from core.components import Transform, Health, AI, Placeable
from game_controller import (
    TRAP_TRIGGER_RADIUS, TRAP_SELF_DAMAGE, TRAP_DAMAGE, TRAP_COOLDOWN,
)


class TrapSystem:
    """Damage mobs that step on traps."""

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
                    mh.damage(TRAP_DAMAGE)
                    self._cooldowns[tid] = TRAP_COOLDOWN
                    # Degrade trap HP
                    th = em.get_component(tid, Health)
                    if th:
                        th.damage(TRAP_SELF_DAMAGE)
                    if on_hit:
                        on_hit(mid, TRAP_DAMAGE, tt)
                    break
