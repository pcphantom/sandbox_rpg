"""Physics system — tile and entity collision resolution."""
from typing import Any

from core.constants import TILE_SIZE
from core.utils import clamp
from core.ecs import EntityManager
from core.components import Transform, Velocity, Collider
from core.spatial import spatial_hash


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

    def _entity_blocked(self, eid: int, x: float, y: float,
                        w: int, h: int, em: EntityManager) -> int:
        """Check if rect (x, y, w, h) overlaps any solid static collider.

        Uses the spatial hash for broadphase, then does precise AABB checks.
        Returns the blocking entity id or 0.
        """
        r = x + w
        b = y + h
        candidates = spatial_hash.query_rect(x, y, w, h)
        for bid in candidates:
            if bid == eid:
                continue
            if not em.has_component(bid, Collider):
                continue
            bc = em.get_component(bid, Collider)
            if not bc.solid:
                continue
            if em.has_component(bid, Velocity):
                continue
            bt = em.get_component(bid, Transform)
            if not bt:
                continue
            if x < bt.x + bc.width and r > bt.x and y < bt.y + bc.height and b > bt.y:
                return bid
        return 0

    def update(self, dt: float, em: EntityManager, world: Any) -> None:
        for eid in em.get_entities_with(Transform, Collider, Velocity):
            t = em.get_component(eid, Transform)
            c = em.get_component(eid, Collider)
            v = em.get_component(eid, Velocity)
            if c.solid:
                nx = t.x + v.vx * dt
                if (not self._tile_solid(nx, t.y, c.width, c.height, world)
                        and not self._entity_blocked(eid, nx, t.y,
                                                     c.width, c.height, em)):
                    t.x = nx
                else:
                    v.vx = 0
                ny = t.y + v.vy * dt
                if (not self._tile_solid(t.x, ny, c.width, c.height, world)
                        and not self._entity_blocked(eid, t.x, ny,
                                                     c.width, c.height, em)):
                    t.y = ny
                else:
                    v.vy = 0
            t.x = clamp(t.x, 0, self.ww * TILE_SIZE - c.width)
            t.y = clamp(t.y, 0, self.wh * TILE_SIZE - c.height)
