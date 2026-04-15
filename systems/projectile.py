"""Projectile system — movement, collision, and despawn."""
import math
from typing import Any

from core.ecs import EntityManager
from core.components import Transform, Velocity, Health, AI, Projectile
from core.spatial import spatial_hash
from game_controller import PROJ_MOB_HIT_RADIUS


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
            # Only player-owned projectiles check collision with mobs.
            # Enemy projectiles targeting the player are handled separately
            # by check_enemy_projectile_damage() in game/combat.py.
            is_player_proj = not em.has_component(proj.owner, AI)
            if not is_player_proj:
                continue
            # Use spatial hash for mob collision
            candidates = spatial_hash.query_radius(
                pt.x, pt.y, PROJ_MOB_HIT_RADIUS)
            for mid in candidates:
                if not em.has_component(mid, AI):
                    continue
                if not em.has_component(mid, Health):
                    continue
                mt = em.get_component(mid, Transform)
                if not mt:
                    continue
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
            spatial_hash.remove(pid)
            em.destroy_entity(pid)
