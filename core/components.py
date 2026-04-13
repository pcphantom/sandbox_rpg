"""ECS Components for the sandbox RPG."""
import pygame
from typing import Dict, Tuple, Optional

from core.constants import INVENTORY_TOTAL_SLOTS, HOTBAR_CAPACITY, STAT_POINTS_PER_LEVEL


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
        self.hotbar: Dict[int, Tuple[str, int]] = {}
        self.equipped_slot: int = 0
        self.held_item: Optional[Tuple[str, int]] = None
        self.held_enchant: Optional[Dict] = None
        self.held_rarity: str = 'common'
        # Enchantment overlays per slot: slot_index -> {'type': str, 'level': int}
        self.slot_enchantments: Dict[int, Dict] = {}
        # Same for hotbar slots (keyed by hotbar index, separate namespace)
        self.hotbar_enchantments: Dict[int, Dict] = {}
        # Rarity overlays per slot: slot_index -> rarity string
        self.slot_rarities: Dict[int, str] = {}
        self.hotbar_rarities: Dict[int, str] = {}
        # Back-reference to Equipment for ammo auto-stacking (set externally)
        self._equipment_ref: Optional['Equipment'] = None

    def add_item(self, item_id: str, count: int = 1) -> int:
        return self.add_item_enchanted(item_id, None, count, 'common')

    def add_item_enchanted(self, item_id: str, enchant: Optional[dict] = None,
                           count: int = 1, rarity: str = 'common') -> int:
        """Add an item and attach its enchantment/rarity to the exact slot.

        Returns overflow count.
        """
        from core.item_stack import add_to_slots
        # Auto-stack ammo into equipped ammo slot if same type
        if self._equipment_ref and self._equipment_ref.ammo == item_id:
            from data import ITEM_CATEGORIES
            if ITEM_CATEGORIES.get(item_id) == 'ammo':
                self._equipment_ref.ammo_count += count
                return 0
        from data import ITEM_CATEGORIES, NON_STACKABLE_CATEGORIES
        cat = ITEM_CATEGORIES.get(item_id, '')
        non_stack = cat in NON_STACKABLE_CATEGORIES

        if non_stack:
            return add_to_slots(self.slots, self.slot_enchantments,
                                self.slot_rarities, self.capacity,
                                item_id, enchant, rarity, count,
                                non_stackable=True)

        # Stackable — try to merge with existing hotbar stack first
        for slot, (iid, c) in self.hotbar.items():
            if iid != item_id:
                continue
            from core.item_stack import items_match
            slot_ench = self.hotbar_enchantments.get(slot)
            slot_rar = self.hotbar_rarities.get(slot, 'common')
            if items_match(item_id, enchant, rarity,
                           iid, slot_ench, slot_rar):
                self.hotbar[slot] = (iid, c + count)
                return 0
        # No matching hotbar stack — go to main inventory
        return add_to_slots(self.slots, self.slot_enchantments,
                            self.slot_rarities, self.capacity,
                            item_id, enchant, rarity, count)

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        from core.item_stack import remove_from_slots
        # Remove from hotbar first, then main inventory
        if remove_from_slots(self.hotbar, self.hotbar_enchantments,
                             self.hotbar_rarities, item_id, count):
            return True
        return remove_from_slots(self.slots, self.slot_enchantments,
                                 self.slot_rarities, item_id, count)

    def remove_from_hotbar_slot(self, slot: int, count: int = 1) -> bool:
        """Remove *count* of whatever item is in a specific hotbar slot."""
        if slot not in self.hotbar:
            return False
        iid, c = self.hotbar[slot]
        if c > count:
            self.hotbar[slot] = (iid, c - count)
            return True
        elif c == count:
            del self.hotbar[slot]
            self.hotbar_enchantments.pop(slot, None)
            self.hotbar_rarities.pop(slot, 'common')
            return True
        return False

    def count(self, item_id: str) -> int:
        total = sum(c for iid, c in self.hotbar.values() if iid == item_id)
        total += sum(c for iid, c in self.slots.values() if iid == item_id)
        return total

    def has(self, item_id: str, count: int = 1) -> bool:
        return self.count(item_id) >= count

    def get_equipped(self) -> Optional[str]:
        if self.equipped_slot in self.hotbar:
            return self.hotbar[self.equipped_slot][0]
        return None

    def get_equipped_enchant(self) -> Optional[Dict]:
        """Return the enchantment overlay on the currently equipped hotbar item."""
        return self.hotbar_enchantments.get(self.equipped_slot)

    def get_equipped_rarity(self) -> str:
        """Return the rarity string of the currently equipped hotbar item."""
        return self.hotbar_rarities.get(self.equipped_slot, 'common')


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
        self.aggro = False  # set True when hit by player


class PlayerStats(Component):
    def __init__(self) -> None:
        self.level = 1; self.xp = 0; self.kills = 0
        self.xp_to_next = 50
        self.stat_points = 0
        self.strength = 1
        self.agility = 1
        self.vitality = 1
        self.luck = 1

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
        self.ammo_count: int = 0
        self.enchantments: Dict[str, Dict] = {}  # slot_name → {'type','level'}
        self.rarities: Dict[str, str] = {}        # slot_name → rarity string


class Projectile(Component):
    def __init__(self, damage: int, owner: int, speed: float = 400.0,
                 max_range: float = 300.0) -> None:
        self.damage = damage; self.owner = owner
        self.speed = speed; self.max_range = max_range
        self.distance_traveled = 0.0
        self.spell_id: str = ''  # set for spell projectiles (e.g. ice slow)
        self.is_bomb: bool = False  # set for bomb projectiles (AOE on hit)
        self.bomb_radius: float = 0.0


class Placeable(Component):
    def __init__(self, item_type: str, rotation: int = 0,
                 drop_item: str = "") -> None:
        self.item_type = item_type
        self.rotation = rotation
        self.drop_item = drop_item


class Storage(Component):
    """Container that holds items (chests, enchantment tables)."""
    def __init__(self, capacity: int = 24) -> None:
        self.capacity = capacity
        self.slots: Dict[int, Tuple[str, int]] = {}
        self.slot_enchantments: Dict[int, Dict] = {}
        self.slot_rarities: Dict[int, str] = {}

    def add_item(self, item_id: str, count: int = 1) -> int:
        from core.item_stack import add_to_slots
        return add_to_slots(self.slots, self.slot_enchantments,
                            self.slot_rarities, self.capacity,
                            item_id, None, 'common', count)

    def add_item_enchanted(self, item_id: str, enchant: Optional[dict] = None,
                           count: int = 1, rarity: str = 'common') -> int:
        """Add an item with its enchantment/rarity atomically to the same slot.

        Only stacks if item_id, enchantment, AND rarity all match.
        """
        from core.item_stack import add_to_slots
        return add_to_slots(self.slots, self.slot_enchantments,
                            self.slot_rarities, self.capacity,
                            item_id, enchant, rarity, count)

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        from core.item_stack import remove_from_slots
        return remove_from_slots(self.slots, self.slot_enchantments,
                                 self.slot_rarities, item_id, count)

    def sort(self) -> None:
        """Merge duplicate stacks and compact slots so there are no gaps."""
        from core.item_stack import sort_slots
        sort_slots(self.slots, self.slot_enchantments, self.slot_rarities)


class Turret(Component):
    """Auto-firing turret that targets nearby mobs."""
    def __init__(self, damage: int = 8, fire_range: float = 200.0,
                 cooldown: float = 1.5,
                 enchant: dict = None,
                 rarity: str = 'common') -> None:
        self.damage = damage
        self.fire_range = fire_range
        self.cooldown = cooldown
        self.timer: float = 0.0
        self.enchant = enchant   # {'type': str, 'level': int} or None
        self.rarity = rarity     # rarity string, always 'common' minimum
        self.regen_accum: float = 0.0  # accumulator for regen enchant self-repair


class Building(Component):
    """Marks an entity as a player-built structure."""
    def __init__(self, building_type: str = 'wall') -> None:
        self.building_type = building_type
