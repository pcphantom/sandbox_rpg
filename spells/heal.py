"""Heal spell — self-cast that restores player HP.

Each version (I, II, III) heals more with a shorter cooldown.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

# -- Heal I --------------------------------------------------------------------
HEAL_1_COOLDOWN: float = 3.0           # seconds between casts
HEAL_1_HEAL: int = 50                  # HP restored
HEAL_1_COLOR = (80, 255, 80)           # particle tint

# -- Heal II -------------------------------------------------------------------
HEAL_2_COOLDOWN: float = 2.5
HEAL_2_HEAL: int = 80
HEAL_2_COLOR = (100, 255, 100)

# -- Heal III ------------------------------------------------------------------
HEAL_3_COOLDOWN: float = 2.0
HEAL_3_HEAL: int = 120
HEAL_3_COLOR = (120, 255, 120)

# -- Heal IV -------------------------------------------------------------------
HEAL_4_COOLDOWN: float = 1.6
HEAL_4_HEAL: int = 170
HEAL_4_COLOR = (140, 255, 140)

# -- Heal V --------------------------------------------------------------------
HEAL_5_COOLDOWN: float = 1.2
HEAL_5_HEAL: int = 230
HEAL_5_COLOR = (160, 255, 160)

# Assembled spell data keyed by item_id
HEAL_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_heal': {
        'name': 'Heal I',
        'type': 'self',
        'heal': HEAL_1_HEAL,
        'color': HEAL_1_COLOR,
        'cooldown': HEAL_1_COOLDOWN,
    },
    'spell_heal_2': {
        'name': 'Heal II',
        'type': 'self',
        'heal': HEAL_2_HEAL,
        'color': HEAL_2_COLOR,
        'cooldown': HEAL_2_COOLDOWN,
    },
    'spell_heal_3': {
        'name': 'Heal III',
        'type': 'self',
        'heal': HEAL_3_HEAL,
        'color': HEAL_3_COLOR,
        'cooldown': HEAL_3_COOLDOWN,
    },
    'spell_heal_4': {
        'name': 'Heal IV',
        'type': 'self',
        'heal': HEAL_4_HEAL,
        'color': HEAL_4_COLOR,
        'cooldown': HEAL_4_COOLDOWN,
    },
    'spell_heal_5': {
        'name': 'Heal V',
        'type': 'self',
        'heal': HEAL_5_HEAL,
        'color': HEAL_5_COLOR,
        'cooldown': HEAL_5_COOLDOWN,
    },
}
