"""Physics system — tile and entity collision resolution."""
from typing import Any

from core.constants import TILE_SIZE
from core.utils import clamp
from core.ecs import EntityManager
from core.components import Transform, Velocity, Collider


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
