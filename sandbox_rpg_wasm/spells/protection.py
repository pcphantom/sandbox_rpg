"""Protection spell — self-buff that reduces incoming damage.

Does NOT consume the spell book — uses cooldown.
Each version (I, II, III) has increasing damage reduction.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

from game_controller import (
    PROTECTION_1_COLOR, PROTECTION_2_COLOR, PROTECTION_3_COLOR,
    PROTECTION_4_COLOR, PROTECTION_5_COLOR,
)

# -- Protection I --------------------------------------------------------------
PROTECTION_1_COOLDOWN: float = 5.0     # seconds between casts
PROTECTION_1_DURATION: float = 60.0    # buff duration in seconds (1 minute)
PROTECTION_1_VALUE: int = 2            # flat damage reduction while active

# -- Protection II -------------------------------------------------------------
PROTECTION_2_COOLDOWN: float = 5.0
PROTECTION_2_DURATION: float = 75.0    # 1m 15s
PROTECTION_2_VALUE: int = 4

# -- Protection III ------------------------------------------------------------
PROTECTION_3_COOLDOWN: float = 5.0
PROTECTION_3_DURATION: float = 90.0    # 1m 30s
PROTECTION_3_VALUE: int = 6

# -- Protection IV -------------------------------------------------------------
PROTECTION_4_COOLDOWN: float = 5.0
PROTECTION_4_DURATION: float = 105.0   # 1m 45s
PROTECTION_4_VALUE: int = 9

# -- Protection V --------------------------------------------------------------
PROTECTION_5_COOLDOWN: float = 5.0
PROTECTION_5_DURATION: float = 120.0   # 2 minutes
PROTECTION_5_VALUE: int = 12

# Assembled spell data keyed by item_id
PROTECTION_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_protection_1': {
        'name': 'Protection I',
        'type': 'self_buff',
        'effect': 'protection',
        'level': 1,
        'duration': PROTECTION_1_DURATION,
        'value': PROTECTION_1_VALUE,
        'color': PROTECTION_1_COLOR,
        'cooldown': PROTECTION_1_COOLDOWN,
    },
    'spell_protection_2': {
        'name': 'Protection II',
        'type': 'self_buff',
        'effect': 'protection',
        'level': 2,
        'duration': PROTECTION_2_DURATION,
        'value': PROTECTION_2_VALUE,
        'color': PROTECTION_2_COLOR,
        'cooldown': PROTECTION_2_COOLDOWN,
    },
    'spell_protection_3': {
        'name': 'Protection III',
        'type': 'self_buff',
        'effect': 'protection',
        'level': 3,
        'duration': PROTECTION_3_DURATION,
        'value': PROTECTION_3_VALUE,
        'color': PROTECTION_3_COLOR,
        'cooldown': PROTECTION_3_COOLDOWN,
    },
    'spell_protection_4': {
        'name': 'Protection IV',
        'type': 'self_buff',
        'effect': 'protection',
        'level': 4,
        'duration': PROTECTION_4_DURATION,
        'value': PROTECTION_4_VALUE,
        'color': PROTECTION_4_COLOR,
        'cooldown': PROTECTION_4_COOLDOWN,
    },
    'spell_protection_5': {
        'name': 'Protection V',
        'type': 'self_buff',
        'effect': 'protection',
        'level': 5,
        'duration': PROTECTION_5_DURATION,
        'value': PROTECTION_5_VALUE,
        'color': PROTECTION_5_COLOR,
        'cooldown': PROTECTION_5_COOLDOWN,
    },
}
