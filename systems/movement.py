"""Movement system — applies velocity to transforms."""
from core.ecs import EntityManager
from core.components import Transform, Velocity, Collider
from core.constants import FPS
from core.spatial import spatial_hash
from game_controller import VELOCITY_DEADZONE


class MovementSystem:
    def update(self, dt: float, em: EntityManager) -> None:
        for eid in em.get_entities_with(Transform, Velocity):
            t = em.get_component(eid, Transform)
            v = em.get_component(eid, Velocity)
            t.prev_x, t.prev_y = t.x, t.y
            t.x += v.vx * dt
            t.y += v.vy * dt
            # Frame-rate-independent friction: normalize to target FPS
            # so speed is consistent regardless of actual frame rate.
            f = v.friction ** (dt * FPS)
            v.vx *= f
            v.vy *= f
            if abs(v.vx) < VELOCITY_DEADZONE:
                v.vx = 0
            if abs(v.vy) < VELOCITY_DEADZONE:
                v.vy = 0
            # Update spatial hash when position actually changed
            if t.x != t.prev_x or t.y != t.prev_y:
                c = em.get_component(eid, Collider) if em.has_component(eid, Collider) else None
                cw = c.width if c else 0
                ch = c.height if c else 0
                spatial_hash.update(eid, t.x, t.y, cw, ch)
