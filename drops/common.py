"""Shared drop system constants and enhancement odds."""
from typing import Dict, List, Tuple

# -- Enhancement tier odds --
# Chance that an enhanced item roll is +1, +2, +3, +4, or +5.
# These must sum to 1.0.
ENHANCEMENT_ODDS: Dict[int, float] = {
    1: 0.45,   # +1: 45%
    2: 0.30,   # +2: 30%
    3: 0.15,   # +3: 15%
    4: 0.07,   # +4: 7%
    5: 0.03,   # +5: 3%
}

# -- Rarity tier odds --
# Weights (not probabilities) for rarity roll on equipment drops.
RARITY_WEIGHTS_NORMAL: Dict[str, float] = {
    'common': 70.0,
    'rare': 20.0,
    'epic': 8.0,
    'legendary': 1.5,
    'mythic': 0.5,
}

RARITY_WEIGHTS_BOSS: Dict[str, float] = {
    'common': 20.0,
    'rare': 30.0,
    'epic': 30.0,
    'legendary': 15.0,
    'mythic': 5.0,
}

# -- Material tier groupings (for building varied loot pools) --
BASIC_MATERIALS: List[str] = ['wood', 'stone', 'stick', 'bone', 'cloth', 'leather']
ADVANCED_MATERIALS: List[str] = ['iron', 'iron_ore', 'diamond', 'gunpowder']

# -- Consumable pools --
BASIC_CONSUMABLES: List[str] = ['berry', 'bandage']
ADVANCED_CONSUMABLES: List[str] = ['pie', 'health_potion', 'antidote']

# -- Spell books --
ALL_SPELLS: List[str] = ['spell_fireball', 'spell_heal', 'spell_lightning', 'spell_ice']

# -- Buff spell books --
SPELL_BUFF_TIERS: Dict[int, List[str]] = {
    1: ['spell_regen_1', 'spell_protection_1', 'spell_strength_1'],
    2: ['spell_regen_2', 'spell_protection_2', 'spell_strength_2'],
    3: ['spell_regen_3', 'spell_protection_3', 'spell_strength_3'],
}
