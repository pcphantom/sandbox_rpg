"""Fireball spell — offensive projectile that deals fire damage.

Each version (I, II, III) has escalating damage, range, and reduced cooldown.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

# -- Fireball I ----------------------------------------------------------------
FIREBALL_1_COOLDOWN: float = 3.0       # seconds between casts
FIREBALL_1_DAMAGE: int = 60            # base damage on hit
FIREBALL_1_RANGE: float = 400.0        # max projectile travel distance (px)
FIREBALL_1_SPEED: float = 350.0        # projectile speed (px/s)
FIREBALL_1_RADIUS: float = 80.0        # AoE splash radius (px)
FIREBALL_1_COLOR = (255, 120, 30)      # particle / projectile tint

# -- Fireball II ---------------------------------------------------------------
FIREBALL_2_COOLDOWN: float = 2.5
FIREBALL_2_DAMAGE: int = 90
FIREBALL_2_RANGE: float = 450.0
FIREBALL_2_SPEED: float = 380.0
FIREBALL_2_RADIUS: float = 100.0
FIREBALL_2_COLOR = (255, 140, 40)

# -- Fireball III --------------------------------------------------------------
FIREBALL_3_COOLDOWN: float = 2.0
FIREBALL_3_DAMAGE: int = 130
FIREBALL_3_RANGE: float = 500.0
FIREBALL_3_SPEED: float = 420.0
FIREBALL_3_RADIUS: float = 120.0
FIREBALL_3_COLOR = (255, 160, 50)

# -- Fireball IV ---------------------------------------------------------------
FIREBALL_4_COOLDOWN: float = 1.6
FIREBALL_4_DAMAGE: int = 180
FIREBALL_4_RANGE: float = 550.0
FIREBALL_4_SPEED: float = 460.0
FIREBALL_4_RADIUS: float = 140.0
FIREBALL_4_COLOR = (255, 180, 60)

# -- Fireball V ----------------------------------------------------------------
FIREBALL_5_COOLDOWN: float = 1.2
FIREBALL_5_DAMAGE: int = 240
FIREBALL_5_RANGE: float = 600.0
FIREBALL_5_SPEED: float = 500.0
FIREBALL_5_RADIUS: float = 160.0
FIREBALL_5_COLOR = (255, 200, 80)

# Assembled spell data keyed by item_id
FIREBALL_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_fireball': {
        'name': 'Fireball I',
        'type': 'projectile',
        'damage': FIREBALL_1_DAMAGE,
        'radius': FIREBALL_1_RADIUS,
        'speed': FIREBALL_1_SPEED,
        'range': FIREBALL_1_RANGE,
        'color': FIREBALL_1_COLOR,
        'cooldown': FIREBALL_1_COOLDOWN,
    },
    'spell_fireball_2': {
        'name': 'Fireball II',
        'type': 'projectile',
        'damage': FIREBALL_2_DAMAGE,
        'radius': FIREBALL_2_RADIUS,
        'speed': FIREBALL_2_SPEED,
        'range': FIREBALL_2_RANGE,
        'color': FIREBALL_2_COLOR,
        'cooldown': FIREBALL_2_COOLDOWN,
    },
    'spell_fireball_3': {
        'name': 'Fireball III',
        'type': 'projectile',
        'damage': FIREBALL_3_DAMAGE,
        'radius': FIREBALL_3_RADIUS,
        'speed': FIREBALL_3_SPEED,
        'range': FIREBALL_3_RANGE,
        'color': FIREBALL_3_COLOR,
        'cooldown': FIREBALL_3_COOLDOWN,
    },
    'spell_fireball_4': {
        'name': 'Fireball IV',
        'type': 'projectile',
        'damage': FIREBALL_4_DAMAGE,
        'radius': FIREBALL_4_RADIUS,
        'speed': FIREBALL_4_SPEED,
        'range': FIREBALL_4_RANGE,
        'color': FIREBALL_4_COLOR,
        'cooldown': FIREBALL_4_COOLDOWN,
    },
    'spell_fireball_5': {
        'name': 'Fireball V',
        'type': 'projectile',
        'damage': FIREBALL_5_DAMAGE,
        'radius': FIREBALL_5_RADIUS,
        'speed': FIREBALL_5_SPEED,
        'range': FIREBALL_5_RANGE,
        'color': FIREBALL_5_COLOR,
        'cooldown': FIREBALL_5_COOLDOWN,
    },
}
