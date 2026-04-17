"""Strength spell — self-buff that increases melee and ranged damage.

Does NOT consume the spell book — uses cooldown.
Each version (I, II, III) has increasing bonus damage.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

from game_controller import (
    STRENGTH_1_COLOR, STRENGTH_2_COLOR, STRENGTH_3_COLOR,
    STRENGTH_4_COLOR, STRENGTH_5_COLOR,
)

# -- Strength I ----------------------------------------------------------------
STRENGTH_1_COOLDOWN: float = 5.0       # seconds between casts
STRENGTH_1_DURATION: float = 60.0      # buff duration in seconds
STRENGTH_1_VALUE: int = 3              # bonus flat damage while active

# -- Strength II ---------------------------------------------------------------
STRENGTH_2_COOLDOWN: float = 5.0
STRENGTH_2_DURATION: float = 60.0
STRENGTH_2_VALUE: int = 6

# -- Strength III --------------------------------------------------------------
STRENGTH_3_COOLDOWN: float = 5.0
STRENGTH_3_DURATION: float = 60.0
STRENGTH_3_VALUE: int = 10

# -- Strength IV ---------------------------------------------------------------
STRENGTH_4_COOLDOWN: float = 5.0
STRENGTH_4_DURATION: float = 60.0
STRENGTH_4_VALUE: int = 15

# -- Strength V ----------------------------------------------------------------
STRENGTH_5_COOLDOWN: float = 5.0
STRENGTH_5_DURATION: float = 60.0
STRENGTH_5_VALUE: int = 20

# Assembled spell data keyed by item_id
STRENGTH_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_strength_1': {
        'name': 'Strength I',
        'type': 'self_buff',
        'effect': 'strength',
        'level': 1,
        'duration': STRENGTH_1_DURATION,
        'value': STRENGTH_1_VALUE,
        'color': STRENGTH_1_COLOR,
        'cooldown': STRENGTH_1_COOLDOWN,
    },
    'spell_strength_2': {
        'name': 'Strength II',
        'type': 'self_buff',
        'effect': 'strength',
        'level': 2,
        'duration': STRENGTH_2_DURATION,
        'value': STRENGTH_2_VALUE,
        'color': STRENGTH_2_COLOR,
        'cooldown': STRENGTH_2_COOLDOWN,
    },
    'spell_strength_3': {
        'name': 'Strength III',
        'type': 'self_buff',
        'effect': 'strength',
        'level': 3,
        'duration': STRENGTH_3_DURATION,
        'value': STRENGTH_3_VALUE,
        'color': STRENGTH_3_COLOR,
        'cooldown': STRENGTH_3_COOLDOWN,
    },
    'spell_strength_4': {
        'name': 'Strength IV',
        'type': 'self_buff',
        'effect': 'strength',
        'level': 4,
        'duration': STRENGTH_4_DURATION,
        'value': STRENGTH_4_VALUE,
        'color': STRENGTH_4_COLOR,
        'cooldown': STRENGTH_4_COOLDOWN,
    },
    'spell_strength_5': {
        'name': 'Strength V',
        'type': 'self_buff',
        'effect': 'strength',
        'level': 5,
        'duration': STRENGTH_5_DURATION,
        'value': STRENGTH_5_VALUE,
        'color': STRENGTH_5_COLOR,
        'cooldown': STRENGTH_5_COOLDOWN,
    },
}
