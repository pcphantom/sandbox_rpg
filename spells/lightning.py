"""Lightning Bolt spell — fast offensive projectile.

Each version (I, II, III) has escalating damage and reduced cooldown.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

from game_controller import (
    LIGHTNING_1_COLOR, LIGHTNING_2_COLOR, LIGHTNING_3_COLOR,
    LIGHTNING_4_COLOR, LIGHTNING_5_COLOR,
)

# -- Lightning I ---------------------------------------------------------------
LIGHTNING_1_COOLDOWN: float = 3.0      # seconds between casts
LIGHTNING_1_DAMAGE: int = 80           # base damage on hit
LIGHTNING_1_RANGE: float = 350.0       # max projectile travel distance (px)
LIGHTNING_1_SPEED: float = 600.0       # projectile speed (px/s)
LIGHTNING_1_RADIUS: float = 40.0       # AoE splash radius (px)

# -- Lightning II --------------------------------------------------------------
LIGHTNING_2_COOLDOWN: float = 2.5
LIGHTNING_2_DAMAGE: int = 120
LIGHTNING_2_RANGE: float = 400.0
LIGHTNING_2_SPEED: float = 650.0
LIGHTNING_2_RADIUS: float = 50.0

# -- Lightning III -------------------------------------------------------------
LIGHTNING_3_COOLDOWN: float = 2.0
LIGHTNING_3_DAMAGE: int = 170
LIGHTNING_3_RANGE: float = 450.0
LIGHTNING_3_SPEED: float = 700.0
LIGHTNING_3_RADIUS: float = 60.0

# -- Lightning IV --------------------------------------------------------------
LIGHTNING_4_COOLDOWN: float = 1.6
LIGHTNING_4_DAMAGE: int = 230
LIGHTNING_4_RANGE: float = 500.0
LIGHTNING_4_SPEED: float = 750.0
LIGHTNING_4_RADIUS: float = 70.0

# -- Lightning V ---------------------------------------------------------------
LIGHTNING_5_COOLDOWN: float = 1.2
LIGHTNING_5_DAMAGE: int = 300
LIGHTNING_5_RANGE: float = 550.0
LIGHTNING_5_SPEED: float = 800.0
LIGHTNING_5_RADIUS: float = 80.0

# Assembled spell data keyed by item_id
LIGHTNING_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_lightning': {
        'name': 'Lightning Bolt I',
        'type': 'projectile',
        'damage': LIGHTNING_1_DAMAGE,
        'radius': LIGHTNING_1_RADIUS,
        'speed': LIGHTNING_1_SPEED,
        'range': LIGHTNING_1_RANGE,
        'color': LIGHTNING_1_COLOR,
        'cooldown': LIGHTNING_1_COOLDOWN,
    },
    'spell_lightning_2': {
        'name': 'Lightning Bolt II',
        'type': 'projectile',
        'damage': LIGHTNING_2_DAMAGE,
        'radius': LIGHTNING_2_RADIUS,
        'speed': LIGHTNING_2_SPEED,
        'range': LIGHTNING_2_RANGE,
        'color': LIGHTNING_2_COLOR,
        'cooldown': LIGHTNING_2_COOLDOWN,
    },
    'spell_lightning_3': {
        'name': 'Lightning Bolt III',
        'type': 'projectile',
        'damage': LIGHTNING_3_DAMAGE,
        'radius': LIGHTNING_3_RADIUS,
        'speed': LIGHTNING_3_SPEED,
        'range': LIGHTNING_3_RANGE,
        'color': LIGHTNING_3_COLOR,
        'cooldown': LIGHTNING_3_COOLDOWN,
    },
    'spell_lightning_4': {
        'name': 'Lightning Bolt IV',
        'type': 'projectile',
        'damage': LIGHTNING_4_DAMAGE,
        'radius': LIGHTNING_4_RADIUS,
        'speed': LIGHTNING_4_SPEED,
        'range': LIGHTNING_4_RANGE,
        'color': LIGHTNING_4_COLOR,
        'cooldown': LIGHTNING_4_COOLDOWN,
    },
    'spell_lightning_5': {
        'name': 'Lightning Bolt V',
        'type': 'projectile',
        'damage': LIGHTNING_5_DAMAGE,
        'radius': LIGHTNING_5_RADIUS,
        'speed': LIGHTNING_5_SPEED,
        'range': LIGHTNING_5_RANGE,
        'color': LIGHTNING_5_COLOR,
        'cooldown': LIGHTNING_5_COOLDOWN,
    },
}
