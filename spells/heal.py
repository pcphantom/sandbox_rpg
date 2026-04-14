"""Heal spell — self-cast that restores player HP.

Each version (I, II, III) heals more with a shorter cooldown.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

from game_controller import (
    HEAL_1_COLOR, HEAL_2_COLOR, HEAL_3_COLOR, HEAL_4_COLOR, HEAL_5_COLOR,
)

# -- Heal I --------------------------------------------------------------------
HEAL_1_COOLDOWN: float = 3.0           # seconds between casts
HEAL_1_HEAL: int = 50                  # HP restored

# -- Heal II -------------------------------------------------------------------
HEAL_2_COOLDOWN: float = 2.5
HEAL_2_HEAL: int = 80

# -- Heal III ------------------------------------------------------------------
HEAL_3_COOLDOWN: float = 2.0
HEAL_3_HEAL: int = 120

# -- Heal IV -------------------------------------------------------------------
HEAL_4_COOLDOWN: float = 1.6
HEAL_4_HEAL: int = 170

# -- Heal V --------------------------------------------------------------------
HEAL_5_COOLDOWN: float = 1.2
HEAL_5_HEAL: int = 230

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
