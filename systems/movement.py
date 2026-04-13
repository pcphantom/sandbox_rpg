"""Movement system — applies velocity to transforms."""
from core.ecs import EntityManager
from core.components import Transform, Velocity
from core.constants import FPS

VELOCITY_DEADZONE: float = 0.5


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
