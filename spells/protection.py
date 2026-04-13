"""Protection spell — self-buff that reduces incoming damage.

Does NOT consume the spell book — uses cooldown.
Each version (I, II, III) has increasing damage reduction.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

# -- Protection I --------------------------------------------------------------
PROTECTION_1_COOLDOWN: float = 5.0     # seconds between casts
PROTECTION_1_DURATION: float = 60.0    # buff duration in seconds
PROTECTION_1_VALUE: int = 2            # flat damage reduction while active
PROTECTION_1_COLOR = (100, 180, 255)   # particle tint

# -- Protection II -------------------------------------------------------------
PROTECTION_2_COOLDOWN: float = 5.0
PROTECTION_2_DURATION: float = 60.0
PROTECTION_2_VALUE: int = 4
PROTECTION_2_COLOR = (120, 200, 255)

# -- Protection III ------------------------------------------------------------
PROTECTION_3_COOLDOWN: float = 5.0
PROTECTION_3_DURATION: float = 60.0
PROTECTION_3_VALUE: int = 6
PROTECTION_3_COLOR = (140, 220, 255)

# -- Protection IV -------------------------------------------------------------
PROTECTION_4_COOLDOWN: float = 5.0
PROTECTION_4_DURATION: float = 60.0
PROTECTION_4_VALUE: int = 9
PROTECTION_4_COLOR = (160, 235, 255)

# -- Protection V --------------------------------------------------------------
PROTECTION_5_COOLDOWN: float = 5.0
PROTECTION_5_DURATION: float = 60.0
PROTECTION_5_VALUE: int = 12
PROTECTION_5_COLOR = (180, 245, 255)

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
