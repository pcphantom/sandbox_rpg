"""Regen spell — self-buff that heals HP over time.

Does NOT consume the spell book — uses cooldown.
Each version (I, II, III) has increasing heal-per-second.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

from game_controller import (
    REGEN_1_COLOR, REGEN_2_COLOR, REGEN_3_COLOR,
    REGEN_4_COLOR, REGEN_5_COLOR,
)

# -- Regen I -------------------------------------------------------------------
REGEN_1_COOLDOWN: float = 5.0          # seconds between casts
REGEN_1_DURATION: float = 30.0         # buff duration in seconds
REGEN_1_VALUE: int = 2                 # HP healed per second

# -- Regen II ------------------------------------------------------------------
REGEN_2_COOLDOWN: float = 5.0
REGEN_2_DURATION: float = 30.0
REGEN_2_VALUE: int = 4

# -- Regen III -----------------------------------------------------------------
REGEN_3_COOLDOWN: float = 5.0
REGEN_3_DURATION: float = 30.0
REGEN_3_VALUE: int = 6

# -- Regen IV ------------------------------------------------------------------
REGEN_4_COOLDOWN: float = 5.0
REGEN_4_DURATION: float = 30.0
REGEN_4_VALUE: int = 9

# -- Regen V -------------------------------------------------------------------
REGEN_5_COOLDOWN: float = 5.0
REGEN_5_DURATION: float = 30.0
REGEN_5_VALUE: int = 12

# Assembled spell data keyed by item_id
REGEN_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_regen_1': {
        'name': 'Regen I',
        'type': 'self_buff',
        'effect': 'regen',
        'level': 1,
        'duration': REGEN_1_DURATION,
        'value': REGEN_1_VALUE,
        'color': REGEN_1_COLOR,
        'cooldown': REGEN_1_COOLDOWN,
    },
    'spell_regen_2': {
        'name': 'Regen II',
        'type': 'self_buff',
        'effect': 'regen',
        'level': 2,
        'duration': REGEN_2_DURATION,
        'value': REGEN_2_VALUE,
        'color': REGEN_2_COLOR,
        'cooldown': REGEN_2_COOLDOWN,
    },
    'spell_regen_3': {
        'name': 'Regen III',
        'type': 'self_buff',
        'effect': 'regen',
        'level': 3,
        'duration': REGEN_3_DURATION,
        'value': REGEN_3_VALUE,
        'color': REGEN_3_COLOR,
        'cooldown': REGEN_3_COOLDOWN,
    },
    'spell_regen_4': {
        'name': 'Regen IV',
        'type': 'self_buff',
        'effect': 'regen',
        'level': 4,
        'duration': REGEN_4_DURATION,
        'value': REGEN_4_VALUE,
        'color': REGEN_4_COLOR,
        'cooldown': REGEN_4_COOLDOWN,
    },
    'spell_regen_5': {
        'name': 'Regen V',
        'type': 'self_buff',
        'effect': 'regen',
        'level': 5,
        'duration': REGEN_5_DURATION,
        'value': REGEN_5_VALUE,
        'color': REGEN_5_COLOR,
        'cooldown': REGEN_5_COOLDOWN,
    },
}
