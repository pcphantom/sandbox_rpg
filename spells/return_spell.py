"""Return spell — teleports the player to their last built bed.

Does NOT consume the spell book — uses cooldown.
Each version (I–V) has decreasing cooldown time.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

from game_controller import (
    RETURN_1_COLOR, RETURN_2_COLOR, RETURN_3_COLOR,
    RETURN_4_COLOR, RETURN_5_COLOR,
)

# -- Return I ------------------------------------------------------------------
RETURN_1_COOLDOWN: float = 600.0       # 10 minutes

# -- Return II -----------------------------------------------------------------
RETURN_2_COOLDOWN: float = 480.0       # 8 minutes

# -- Return III ----------------------------------------------------------------
RETURN_3_COOLDOWN: float = 360.0       # 6 minutes

# -- Return IV -----------------------------------------------------------------
RETURN_4_COOLDOWN: float = 240.0       # 4 minutes

# -- Return V ------------------------------------------------------------------
RETURN_5_COOLDOWN: float = 120.0       # 2 minutes

# Assembled spell data keyed by item_id
RETURN_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_return_1': {
        'name': 'Return I',
        'type': 'teleport_bed',
        'duration': 0,
        'color': RETURN_1_COLOR,
        'cooldown': RETURN_1_COOLDOWN,
    },
    'spell_return_2': {
        'name': 'Return II',
        'type': 'teleport_bed',
        'duration': 0,
        'color': RETURN_2_COLOR,
        'cooldown': RETURN_2_COOLDOWN,
    },
    'spell_return_3': {
        'name': 'Return III',
        'type': 'teleport_bed',
        'duration': 0,
        'color': RETURN_3_COLOR,
        'cooldown': RETURN_3_COOLDOWN,
    },
    'spell_return_4': {
        'name': 'Return IV',
        'type': 'teleport_bed',
        'duration': 0,
        'color': RETURN_4_COLOR,
        'cooldown': RETURN_4_COOLDOWN,
    },
    'spell_return_5': {
        'name': 'Return V',
        'type': 'teleport_bed',
        'duration': 0,
        'color': RETURN_5_COLOR,
        'cooldown': RETURN_5_COOLDOWN,
    },
}
