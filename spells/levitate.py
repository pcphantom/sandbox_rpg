"""Levitate spell — self-buff that negates terrain movement slowdowns.

Does NOT consume the spell book — uses cooldown.
Each version (I–V) has increasing buff duration.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

from game_controller import (
    LEVITATE_1_COLOR, LEVITATE_2_COLOR, LEVITATE_3_COLOR,
    LEVITATE_4_COLOR, LEVITATE_5_COLOR,
)

# -- Levitate I ----------------------------------------------------------------
LEVITATE_1_COOLDOWN: float = 5.0       # seconds between casts
LEVITATE_1_DURATION: float = 30.0      # buff duration in seconds

# -- Levitate II ---------------------------------------------------------------
LEVITATE_2_COOLDOWN: float = 5.0
LEVITATE_2_DURATION: float = 45.0

# -- Levitate III --------------------------------------------------------------
LEVITATE_3_COOLDOWN: float = 5.0
LEVITATE_3_DURATION: float = 60.0

# -- Levitate IV ---------------------------------------------------------------
LEVITATE_4_COOLDOWN: float = 5.0
LEVITATE_4_DURATION: float = 75.0

# -- Levitate V ----------------------------------------------------------------
LEVITATE_5_COOLDOWN: float = 5.0
LEVITATE_5_DURATION: float = 90.0

# Assembled spell data keyed by item_id
LEVITATE_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_levitate_1': {
        'name': 'Levitate I',
        'type': 'self_buff',
        'effect': 'levitate',
        'level': 1,
        'duration': LEVITATE_1_DURATION,
        'value': 1,
        'color': LEVITATE_1_COLOR,
        'cooldown': LEVITATE_1_COOLDOWN,
    },
    'spell_levitate_2': {
        'name': 'Levitate II',
        'type': 'self_buff',
        'effect': 'levitate',
        'level': 2,
        'duration': LEVITATE_2_DURATION,
        'value': 1,
        'color': LEVITATE_2_COLOR,
        'cooldown': LEVITATE_2_COOLDOWN,
    },
    'spell_levitate_3': {
        'name': 'Levitate III',
        'type': 'self_buff',
        'effect': 'levitate',
        'level': 3,
        'duration': LEVITATE_3_DURATION,
        'value': 1,
        'color': LEVITATE_3_COLOR,
        'cooldown': LEVITATE_3_COOLDOWN,
    },
    'spell_levitate_4': {
        'name': 'Levitate IV',
        'type': 'self_buff',
        'effect': 'levitate',
        'level': 4,
        'duration': LEVITATE_4_DURATION,
        'value': 1,
        'color': LEVITATE_4_COLOR,
        'cooldown': LEVITATE_4_COOLDOWN,
    },
    'spell_levitate_5': {
        'name': 'Levitate V',
        'type': 'self_buff',
        'effect': 'levitate',
        'level': 5,
        'duration': LEVITATE_5_DURATION,
        'value': 1,
        'color': LEVITATE_5_COLOR,
        'cooldown': LEVITATE_5_COOLDOWN,
    },
}
