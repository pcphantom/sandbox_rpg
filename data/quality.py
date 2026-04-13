"""Item rarity tier definitions, stat multipliers, and color mappings.

Rarity is a per-slot attribute on equipment items (weapons, armor, shields,
tools, placeables, ranged).  It multiplies the base stats of the item.
Non-equipment items (spells, tomes, materials, consumables) use the legacy
intrinsic quality sets for display color only.
"""
from typing import Dict, Optional, Tuple

# ── Rarity tiers (ordered lowest → highest) ─────────────────────────
RARITY_TIERS = ('common', 'rare', 'epic', 'legendary', 'mythic')

RARITY_COLORS: Dict[str, Tuple[int, int, int]] = {
    'common':    (255, 255, 255),   # White
    'rare':      (80, 140, 255),    # Blue
    'epic':      (180, 60, 255),    # Purple
    'legendary': (255, 215, 0),     # Gold
    'mythic':    (255, 50, 50),     # Red
}

RARITY_MULTIPLIERS: Dict[str, float] = {
    'common':    1.0,
    'rare':      1.5,
    'epic':      2.0,
    'legendary': 2.5,
    'mythic':    3.0,
}

# Backward-compat alias used by a few older references
QUALITY_COLORS = RARITY_COLORS

# ── Equipment categories that can bear rarity ────────────────────────
RARITY_ELIGIBLE_CATEGORIES = frozenset({
    'weapon', 'armor', 'shield', 'tool', 'placeable', 'ranged',
})


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
