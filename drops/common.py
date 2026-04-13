"""Shared drop system constants and enhancement odds.

Odds/weights are sourced from game_controller.py.
Material/consumable/spell pools are drop-specific game data.
"""
from typing import Dict, List, Tuple

from game_controller import (                                         # noqa: F401
    ENHANCEMENT_ODDS, RARITY_WEIGHTS_NORMAL, RARITY_WEIGHTS_BOSS,
)

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
