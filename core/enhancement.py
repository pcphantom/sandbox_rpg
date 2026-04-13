"""Centralized enhancement scaling module — single source of truth.

All enhancement-level scaling (weapons, armor, turrets, protection enchant)
is defined here with separate control variables for offense, defense, and
turret-specific tuning.

Turrets are hybrid structures: they deal damage AND take damage, so they
receive BOTH offense (damage) and defense (DR) scaling per enhancement level.
"""
from typing import Dict, Tuple

# ======================================================================
# CONTROL VARIABLES — adjust these to tune scaling
# ======================================================================

# Offense: bonus damage per enhancement level for melee weapons.
OFFENSE_BONUS_PER_LEVEL: int = 2

# Defense: bonus damage reduction per enhancement level for armor/shields.
DEFENSE_BONUS_PER_LEVEL: int = 2

# Turret offense: bonus damage per enhancement level.
TURRET_OFFENSE_BONUS_PER_LEVEL: int = 2

# Turret defense: bonus DR per enhancement level (applied when mobs attack).
TURRET_DEFENSE_BONUS_PER_LEVEL: int = 2

# Protection enchant: DR per enchant level (stacks with armor/turret DR).
PROTECTION_DR_PER_LEVEL: int = 2

# ======================================================================
# BASE VALUES — the unenhanced stats for each item type
# ======================================================================

# Weapon bases: item_id -> (base_damage, harvest_bonus)
WEAPON_BASES: Dict[str, Tuple[int, int]] = {
    'iron_sword': (30, 0),
    'iron_axe':   (22, 4),
    'mace':       (26, 0),
}

# Armor bases: item_id -> base_DR
ARMOR_BASES: Dict[str, int] = {
    'iron_armor':  6,
    'iron_shield': 4,
}

# Turret base stats (enhancement level 0)
TURRET_BASE_DAMAGE: int = 8
TURRET_BASE_HP: int = 80

# Turret HP per enhancement level (non-linear, kept as explicit table).
TURRET_HP_TABLE: Dict[int, int] = {
    0: 80,
    1: 96,
    2: 112,
    3: 136,
    4: 160,
    5: 192,
}

# ======================================================================
# DERIVED LOOKUPS — computed from control variables + bases
# ======================================================================

def enhanced_weapon_damage(base_id: str, level: int) -> int:
    """Return total damage for a weapon at a given enhancement level."""
    base_dmg, _ = WEAPON_BASES[base_id]
    return base_dmg + level * OFFENSE_BONUS_PER_LEVEL


def enhanced_weapon_harvest(base_id: str) -> int:
    """Return harvest bonus for a weapon (unchanged by enhancement)."""
    _, harvest = WEAPON_BASES[base_id]
    return harvest


def enhanced_armor_dr(base_id: str, level: int) -> int:
    """Return total DR for an armor/shield at a given enhancement level."""
    base_dr = ARMOR_BASES[base_id]
    return base_dr + level * DEFENSE_BONUS_PER_LEVEL


def enhanced_turret_damage(level: int) -> int:
    """Return turret damage at a given enhancement level."""
    return TURRET_BASE_DAMAGE + level * TURRET_OFFENSE_BONUS_PER_LEVEL


def enhanced_turret_hp(level: int) -> int:
    """Return turret HP at a given enhancement level."""
    return TURRET_HP_TABLE.get(level, TURRET_BASE_HP)


def enhanced_turret_dr(level: int) -> int:
    """Return turret DR at a given enhancement level (0 = no DR)."""
    return level * TURRET_DEFENSE_BONUS_PER_LEVEL


def protection_dr(level: int) -> int:
    """Return protection enchant DR for a given enchant level (1-5)."""
    return level * PROTECTION_DR_PER_LEVEL


# ======================================================================
# TABLE GENERATORS — produce the lookup dicts consumed by other modules
# ======================================================================

def build_turret_enhance_damage() -> Dict[int, int]:
    """Generate {level: damage} dict for turret enhancement levels 0-5."""
    return {lvl: enhanced_turret_damage(lvl) for lvl in range(6)}


def build_turret_enhance_hp() -> Dict[int, int]:
    """Generate {level: hp} dict for turret enhancement levels 0-5."""
    return {lvl: enhanced_turret_hp(lvl) for lvl in range(6)}


def build_turret_enhance_dr() -> Dict[int, int]:
    """Generate {level: dr} dict for turret enhancement levels 0-5."""
    return {lvl: enhanced_turret_dr(lvl) for lvl in range(6)}


def build_armor_values() -> Dict[str, int]:
    """Generate the full ARMOR_VALUES dict including all enhanced variants."""
    values: Dict[str, int] = {
        'leather_armor': 3,
        'iron_armor': ARMOR_BASES['iron_armor'],
        'wood_shield': 2,
        'iron_shield': ARMOR_BASES['iron_shield'],
    }
    for base_id in ARMOR_BASES:
        for lvl in range(1, 6):
            values[f'{base_id}_{lvl}'] = enhanced_armor_dr(base_id, lvl)
    return values


def build_protection_dr_bonus() -> Dict[int, int]:
    """Generate {level: dr} dict for protection enchant levels 1-5."""
    return {lvl: protection_dr(lvl) for lvl in range(1, 6)}


def build_enhanced_weapon_items() -> Dict[str, Tuple[str, str, int, int, int, bool]]:
    """Generate ITEM_DATA entries for all enhanced weapon variants (+1 to +5)."""
    # Display name mappings
    names = {
        'iron_sword': 'Iron Sword',
        'iron_axe':   'Iron Axe',
        'mace':       'Iron Mace',
    }
    # Description tiers
    tier_labels = {1: 'Enhanced', 2: 'Enhanced', 3: 'Fine', 4: 'Superior', 5: 'Masterwork'}

    items: Dict[str, Tuple[str, str, int, int, int, bool]] = {}
    for base_id, (base_dmg, harvest) in WEAPON_BASES.items():
        name = names[base_id]
        for lvl in range(1, 6):
            bonus = lvl * OFFENSE_BONUS_PER_LEVEL
            item_id = f'{base_id}_{lvl}'
            display = f'{name} +{lvl}'
            desc = f'{tier_labels[lvl]} {name.lower().split()[-1]}. +{bonus} damage.'
            dmg = enhanced_weapon_damage(base_id, lvl)
            items[item_id] = (display, desc, dmg, harvest, 0, False)
    return items


def build_enhanced_armor_items() -> Dict[str, Tuple[str, str, int, int, int, bool]]:
    """Generate ITEM_DATA entries for all enhanced armor/shield variants (+1 to +5)."""
    names = {
        'iron_armor':  'Iron Armor',
        'iron_shield': 'Iron Shield',
    }
    tier_labels = {1: 'Enhanced', 2: 'Enhanced', 3: 'Fine', 4: 'Superior', 5: 'Masterwork'}
    short = {'iron_armor': 'armor', 'iron_shield': 'shield'}

    items: Dict[str, Tuple[str, str, int, int, int, bool]] = {}
    for base_id, base_dr in ARMOR_BASES.items():
        name = names[base_id]
        s = short[base_id]
        for lvl in range(1, 6):
            bonus = lvl * DEFENSE_BONUS_PER_LEVEL
            item_id = f'{base_id}_{lvl}'
            display = f'{name} +{lvl}'
            desc = f'{tier_labels[lvl]} {s}. +{bonus} DR.'
            items[item_id] = (display, desc, 0, 0, 0, False)
    return items


def build_enhanced_turret_items() -> Dict[str, Tuple[str, str, int, int, int, bool]]:
    """Generate ITEM_DATA entries for enhanced turret variants (+1 to +5)."""
    tier_labels = {1: 'Enhanced', 2: 'Enhanced', 3: 'Fine', 4: 'Superior', 5: 'Masterwork'}
    items: Dict[str, Tuple[str, str, int, int, int, bool]] = {}
    for lvl in range(1, 6):
        item_id = f'turret_{lvl}'
        display = f'Turret +{lvl}'
        desc = f'{tier_labels[lvl]} turret. +{lvl}. [F] to place.'
        items[item_id] = (display, desc, 0, 0, 0, True)
    return items


def build_enhanced_categories() -> Dict[str, str]:
    """Generate ITEM_CATEGORIES entries for all enhanced weapon/armor/turret variants."""
    cats: Dict[str, str] = {}
    for base_id in WEAPON_BASES:
        for lvl in range(1, 6):
            cats[f'{base_id}_{lvl}'] = 'weapon'
    for base_id in ARMOR_BASES:
        category = 'shield' if 'shield' in base_id else 'armor'
        for lvl in range(1, 6):
            cats[f'{base_id}_{lvl}'] = category
    for lvl in range(1, 6):
        cats[f'turret_{lvl}'] = 'placeable'
    return cats


# Pre-built tables for direct import by consumers.
TURRET_ENHANCE_DAMAGE: Dict[int, int] = build_turret_enhance_damage()
TURRET_ENHANCE_HP: Dict[int, int] = build_turret_enhance_hp()
TURRET_ENHANCE_DR: Dict[int, int] = build_turret_enhance_dr()
ARMOR_VALUES: Dict[str, int] = build_armor_values()
PROTECTION_DR_BONUS: Dict[int, int] = build_protection_dr_bonus()
