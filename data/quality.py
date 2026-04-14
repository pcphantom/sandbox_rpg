"""Item rarity tier definitions, stat multipliers, and color mappings.

Rarity is a per-slot attribute on equipment items (weapons, armor, shields,
tools, placeables, ranged).  It multiplies the base stats of the item.
Non-equipment items (spells, tomes, materials, consumables) use the legacy
intrinsic quality sets for display color only.

All tuning constants are sourced from game_controller.py.
"""
from typing import Dict, Optional, Tuple

from game_controller import (                                         # noqa: F401
    RARITY_TIERS, RARITY_COLORS, RARITY_MULTIPLIERS,
    RARITY_ELIGIBLE_CATEGORIES,
)

# Backward-compat alias used by a few older references
QUALITY_COLORS = RARITY_COLORS


def next_rarity(rarity: str) -> Optional[str]:
    """Return the next rarity tier above *rarity*, or None if mythic."""
    idx = RARITY_TIERS.index(rarity)
    if idx + 1 < len(RARITY_TIERS):
        return RARITY_TIERS[idx + 1]
    return None


def get_rarity_color(rarity: str) -> Tuple[int, int, int]:
    """Return the display color for a rarity tier."""
    return RARITY_COLORS.get(rarity, RARITY_COLORS['common'])


def get_rarity_multiplier(rarity: str) -> float:
    """Return the stat multiplier for a rarity tier."""
    return RARITY_MULTIPLIERS.get(rarity, 1.0)


# ── Intrinsic quality for non-equipment items (spells, tomes, etc.) ──
# These items always show at a fixed color regardless of slot rarity.
RARE_ITEMS = {
    'diamond',
    'spell_regen_1', 'spell_protection_1', 'spell_strength_1',
    'enchant_tome_1', 'enchant_tome_2',
}

EPIC_ITEMS = {
    'spell_fireball', 'spell_fireball_2', 'spell_fireball_3',
    'spell_fireball_4', 'spell_fireball_5',
    'spell_heal', 'spell_heal_2', 'spell_heal_3',
    'spell_heal_4', 'spell_heal_5',
    'spell_lightning', 'spell_lightning_2', 'spell_lightning_3',
    'spell_lightning_4', 'spell_lightning_5',
    'spell_ice', 'spell_ice_2', 'spell_ice_3',
    'spell_ice_4', 'spell_ice_5',
    'spell_regen_2', 'spell_regen_3', 'spell_regen_4', 'spell_regen_5',
    'spell_protection_2', 'spell_protection_3', 'spell_protection_4', 'spell_protection_5',
    'spell_strength_2', 'spell_strength_3', 'spell_strength_4', 'spell_strength_5',
    'enchant_tome_3', 'enchant_tome_4', 'enchant_tome_5',
}


def get_item_quality(item_id: str) -> str:
    """Return the intrinsic quality tier of an item (for non-equipment)."""
    if item_id in EPIC_ITEMS:
        return 'epic'
    if item_id in RARE_ITEMS:
        return 'rare'
    return 'common'


def get_item_color(item_id: str, rarity: str = 'common') -> Tuple[int, int, int]:
    """Return the display color for an item.

    If *rarity* is provided (equipment slot rarity), use it.
    Otherwise fall back to intrinsic quality.
    """
    if rarity != 'common':
        return get_rarity_color(rarity)
    return RARITY_COLORS[get_item_quality(item_id)]


def get_stat_description(item_id: str, rarity: str = 'common') -> str:
    """Return the item description with rarity-adjusted stats.

    For weapons/ranged: adjusts displayed damage by rarity multiplier.
    For armor/shields: adjusts displayed DR by rarity multiplier.
    Non-equipment items return the static description unchanged.
    """
    from data.items import ITEM_DATA, ITEM_CATEGORIES
    if item_id not in ITEM_DATA:
        return ''
    base_desc = ITEM_DATA[item_id][1]
    cat = ITEM_CATEGORIES.get(item_id, '')
    if rarity == 'common' or cat not in ('weapon', 'ranged', 'armor', 'shield'):
        return base_desc

    mult = get_rarity_multiplier(rarity)

    if cat == 'weapon':
        base_dmg = ITEM_DATA[item_id][2]
        if base_dmg > 0:
            actual = int(base_dmg * mult)
            return f'{base_desc.split(".")[0]}. {actual} damage.'
        return base_desc

    if cat == 'ranged':
        from data.combat import RANGED_DATA
        from core.enhancement import get_base_item_id, get_enhancement_level, RANGED_OFFENSE_BONUS_PER_LEVEL
        base_id = get_base_item_id(item_id)
        if base_id in RANGED_DATA:
            base_dmg = RANGED_DATA[base_id]['damage']
            enh_lvl = get_enhancement_level(item_id)
            total_dmg = base_dmg + enh_lvl * RANGED_OFFENSE_BONUS_PER_LEVEL
            actual = int(total_dmg * mult)
            return f'{base_desc.split(".")[0]}. {actual} damage.'
        return base_desc

    if cat in ('armor', 'shield'):
        from data import ARMOR_VALUES
        if item_id in ARMOR_VALUES:
            base_dr = ARMOR_VALUES[item_id]
            actual = int(base_dr * mult)
            return f'{base_desc.split(".")[0]}. {actual} DR.'
        return base_desc

    return base_desc
