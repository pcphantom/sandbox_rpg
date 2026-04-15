"""Items package — centralised item definitions with control flags.

Every item defines three control booleans:
    can_enchant  — item can receive an enchantment at the enchantment table
    can_enhance  — item can receive +1..+5 stat enhancement via tomes
    has_rarity   — item can roll/carry a rarity tier (common..mythic)

Enhanced variants (e.g., iron_sword_1 .. iron_sword_5) are generated
automatically from base items that have can_enhance=True.  They inherit
can_enchant and has_rarity from their base, and their own can_enhance
is True (they can be enhanced further up to +5).
"""
from typing import Dict, Tuple

from items.materials import ITEMS as _MATERIALS
from items.consumables import ITEMS as _CONSUMABLES
from items.weapons import ITEMS as _WEAPONS
from items.ranged import ITEMS as _RANGED
from items.ammo import ITEMS as _AMMO
from items.armor import ITEMS as _ARMOR
from items.placeables import ITEMS as _PLACEABLES
from items.spells import ITEMS as _SPELLS
from items.tools import ITEMS as _TOOLS
from items.tomes import ITEMS as _TOMES
from items.throwables import ITEMS as _THROWABLES

# Collect all base item dicts
_ALL_BASE_ITEMS = (
    _MATERIALS + _CONSUMABLES + _WEAPONS + _RANGED + _AMMO +
    _ARMOR + _PLACEABLES + _SPELLS + _TOOLS + _TOMES + _THROWABLES
)

# ── Build the lookup dicts from base items ───────────────────────────

# Legacy ITEM_DATA format: id -> (name, desc, damage, harvest_bonus, heal, placeable)
ITEM_DATA: Dict[str, Tuple[str, str, int, int, int, bool]] = {}
ITEM_CATEGORIES: Dict[str, str] = {}
CAN_ENCHANT: Dict[str, bool] = {}
CAN_ENHANCE: Dict[str, bool] = {}
HAS_RARITY: Dict[str, bool] = {}
HARVEST_TYPE: Dict[str, str] = {}

for _item in _ALL_BASE_ITEMS:
    _id = _item['id']
    ITEM_DATA[_id] = (
        _item['name'], _item['desc'],
        _item['damage'], _item['harvest_bonus'],
        _item['heal'], _item['placeable'],
    )
    ITEM_CATEGORIES[_id] = _item['category']
    CAN_ENCHANT[_id] = _item['can_enchant']
    CAN_ENHANCE[_id] = _item['can_enhance']
    HAS_RARITY[_id] = _item['has_rarity']
    HARVEST_TYPE[_id] = _item.get('harvest_type', 'all')

# ── Generate enhanced variants from base items with can_enhance=True ─

from core.enhancement import (
    build_enhanced_weapon_items,
    build_enhanced_armor_items,
    build_enhanced_turret_items,
    build_enhanced_ranged_items,
    build_enhanced_categories,
)

# Merge dynamically-generated enhanced item data
ITEM_DATA.update(build_enhanced_weapon_items())
ITEM_DATA.update(build_enhanced_armor_items())
ITEM_DATA.update(build_enhanced_turret_items())
ITEM_DATA.update(build_enhanced_ranged_items())
ITEM_CATEGORIES.update(build_enhanced_categories())

# Propagate flags for enhanced variants: inherit from base item
_BASE_IDS = [_id for _id, flag in CAN_ENHANCE.items() if flag]
for _base_id in _BASE_IDS:
    for _lvl in range(1, 6):
        _enhanced_id = f'{_base_id}_{_lvl}'
        if _enhanced_id in ITEM_DATA:
            CAN_ENCHANT[_enhanced_id] = CAN_ENCHANT[_base_id]
            CAN_ENHANCE[_enhanced_id] = True
            HAS_RARITY[_enhanced_id] = HAS_RARITY[_base_id]
            HARVEST_TYPE[_enhanced_id] = HARVEST_TYPE.get(_base_id, 'all')

# Categories whose items must NOT stack — each occupies its own slot.
NON_STACKABLE_CATEGORIES: set = {
    'weapon', 'ranged', 'armor', 'shield', 'spell', 'tool',
    'enchant_tome', 'transfer_tome',
}
