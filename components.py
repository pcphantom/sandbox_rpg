"""ECS Components for the sandbox RPG."""
import pygame
from typing import Dict, Tuple, Optional

from constants import INVENTORY_TOTAL_SLOTS, STAT_POINTS_PER_LEVEL


class Component:
    pass


class Transform(Component):
    def __init__(self, x: float, y: float, z: int = 0) -> None:
        self.x = x; self.y = y; self.z = z
        self.prev_x = x; self.prev_y = y


class Velocity(Component):
    def __init__(self, vx: float = 0.0, vy: float = 0.0,
                 friction: float = 0.85) -> None:
        self.vx = vx; self.vy = vy; self.friction = friction


class Renderable(Component):
    def __init__(self, surface: pygame.Surface, layer: int = 0) -> None:
        self.surface = surface; self.layer = layer
        self.visible = True; self.flip_x = False
        self.offset_x = 0; self.offset_y = 0


class Collider(Component):
    def __init__(self, width: int, height: int, solid: bool = True) -> None:
        self.width = width; self.height = height; self.solid = solid


class Health(Component):
    def __init__(self, maximum: int) -> None:
        self.maximum = maximum; self.current = maximum

    def damage(self, amt: int) -> None:
        self.current = max(0, self.current - amt)

    def heal(self, amt: int) -> None:
        self.current = min(self.maximum, self.current + amt)

    def is_alive(self) -> bool:
        return self.current > 0


class Inventory(Component):
    def __init__(self, capacity: int = INVENTORY_TOTAL_SLOTS) -> None:
        self.capacity = capacity
        self.slots: Dict[int, Tuple[str, int]] = {}
        self.equipped_slot: int = 0

    def add_item(self, item_id: str, count: int = 1) -> int:
        for slot, (iid, c) in self.slots.items():
            if iid == item_id:
                self.slots[slot] = (iid, c + count)
                return 0
        for i in range(self.capacity):
            if i not in self.slots:
                self.slots[i] = (item_id, count)
                return 0
        return count

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        for slot, (iid, c) in list(self.slots.items()):
            if iid == item_id:
                if c > count:
                    self.slots[slot] = (iid, c - count)
                    return True
                elif c == count:
                    del self.slots[slot]
                    return True
        return False

    def count(self, item_id: str) -> int:
        return sum(c for iid, c in self.slots.values() if iid == item_id)

    def has(self, item_id: str, count: int = 1) -> bool:
        return self.count(item_id) >= count

    def get_equipped(self) -> Optional[str]:
        if self.equipped_slot in self.slots:
            return self.slots[self.equipped_slot][0]
        return None


class LightSource(Component):
    def __init__(self, radius: int,
                 color: Tuple[int, int, int] = (255, 200, 120),
                 intensity: float = 1.0) -> None:
        self.radius = radius; self.color = color; self.intensity = intensity


class AI(Component):
    def __init__(self, behavior: str = "wander",
                 mob_type: str = "slime") -> None:
        self.behavior = behavior; self.mob_type = mob_type
        self.state = "idle"; self.timer = 0.0
        self.target_id: Optional[int] = None
        self.speed = 40.0; self.detection_range = 150.0
        self.contact_damage = 5; self.xp_value = 15
        self.attack_timer = 0.0
        self.is_ranged = False
        self.ranged_damage = 0
        self.ranged_range = 0.0
        self.ranged_cooldown = 2.0
        self.ranged_speed = 350.0
        self.ranged_timer = 0.0
        self.is_boss = False
        self.glow_color: Optional[Tuple[int, int, int]] = None


class PlayerStats(Component):
    def __init__(self) -> None:
        self.level = 1; self.xp = 0; self.kills = 0
        self.xp_to_next = 50
        self.stat_points = 0
        self.strength = 1
        self.agility = 1
        self.vitality = 1
        self.dexterity = 1

    def add_xp(self, amount: int) -> bool:
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = self.level * 50
            self.stat_points += STAT_POINTS_PER_LEVEL
            return True
        return False


class Equipment(Component):
    def __init__(self) -> None:
        self.weapon: Optional[str] = None
        self.armor: Optional[str] = None
        self.shield: Optional[str] = None
        self.ranged: Optional[str] = None
        self.ammo: Optional[str] = None


class Projectile(Component):
    def __init__(self, damage: int, owner: int, speed: float = 400.0,
                 max_range: float = 300.0) -> None:
        self.damage = damage; self.owner = owner
        self.speed = speed; self.max_range = max_range
        self.distance_traveled = 0.0


class Placeable(Component):
    def __init__(self, item_type: str) -> None:
        self.item_type = item_type


class Storage(Component):
    """Container that holds items (chests)."""
    def __init__(self, capacity: int = 24) -> None:
        self.capacity = capacity
        self.slots: Dict[int, Tuple[str, int]] = {}

    def add_item(self, item_id: str, count: int = 1) -> int:
        for slot, (iid, c) in self.slots.items():
            if iid == item_id:
                self.slots[slot] = (iid, c + count)
                return 0
        for i in range(self.capacity):
            if i not in self.slots:
                self.slots[i] = (item_id, count)
                return 0
        return count  # overflow

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        for slot, (iid, c) in list(self.slots.items()):
            if iid == item_id:
                if c > count:
                    self.slots[slot] = (iid, c - count)
                    return True
                elif c == count:
                    del self.slots[slot]
                    return True
        return False


class Turret(Component):
    """Auto-firing turret that targets nearby mobs."""
    def __init__(self, damage: int = 8, fire_range: float = 200.0,
                 cooldown: float = 1.5) -> None:
        self.damage = damage
        self.fire_range = fire_range
        self.cooldown = cooldown
        self.timer: float = 0.0


class Building(Component):
    """Marks an entity as a player-built structure."""
    def __init__(self, building_type: str = 'wall') -> None:
        self.building_type = building_type
