"""Ice Shard spell — offensive projectile that slows enemies on hit.

Each version (I, II, III) has escalating damage, longer slow, and reduced cooldown.
Control variables are declared at the top for easy tuning.
"""
from typing import Dict, Any

# -- Ice Shard I ---------------------------------------------------------------
ICE_1_COOLDOWN: float = 3.0            # seconds between casts
ICE_1_DAMAGE: int = 45                 # base damage on hit
ICE_1_RANGE: float = 300.0             # max projectile travel distance (px)
ICE_1_SPEED: float = 280.0             # projectile speed (px/s)
ICE_1_RADIUS: float = 60.0             # AoE splash radius (px)
ICE_1_COLOR = (100, 200, 255)          # particle / projectile tint
ICE_1_SLOW_DURATION: float = 3.0       # seconds the slow lasts
ICE_1_SLOW_FACTOR: float = 0.4         # speed multiplier while slowed

# -- Ice Shard II --------------------------------------------------------------
ICE_2_COOLDOWN: float = 2.5
ICE_2_DAMAGE: int = 70
ICE_2_RANGE: float = 350.0
ICE_2_SPEED: float = 310.0
ICE_2_RADIUS: float = 70.0
ICE_2_COLOR = (120, 215, 255)
ICE_2_SLOW_DURATION: float = 4.0
ICE_2_SLOW_FACTOR: float = 0.3

# -- Ice Shard III -------------------------------------------------------------
ICE_3_COOLDOWN: float = 2.0
ICE_3_DAMAGE: int = 100
ICE_3_RANGE: float = 400.0
ICE_3_SPEED: float = 340.0
ICE_3_RADIUS: float = 80.0
ICE_3_COLOR = (140, 225, 255)
ICE_3_SLOW_DURATION: float = 5.0
ICE_3_SLOW_FACTOR: float = 0.2

# -- Ice Shard IV --------------------------------------------------------------
ICE_4_COOLDOWN: float = 1.6
ICE_4_DAMAGE: int = 140
ICE_4_RANGE: float = 450.0
ICE_4_SPEED: float = 370.0
ICE_4_RADIUS: float = 90.0
ICE_4_COLOR = (160, 235, 255)
ICE_4_SLOW_DURATION: float = 6.0
ICE_4_SLOW_FACTOR: float = 0.15

# -- Ice Shard V ---------------------------------------------------------------
ICE_5_COOLDOWN: float = 1.2
ICE_5_DAMAGE: int = 190
ICE_5_RANGE: float = 500.0
ICE_5_SPEED: float = 400.0
ICE_5_RADIUS: float = 100.0
ICE_5_COLOR = (180, 245, 255)
ICE_5_SLOW_DURATION: float = 7.0
ICE_5_SLOW_FACTOR: float = 0.1

# Assembled spell data keyed by item_id
ICE_SPELLS: Dict[str, Dict[str, Any]] = {
    'spell_ice': {
        'name': 'Ice Shard I',
        'type': 'projectile',
        'damage': ICE_1_DAMAGE,
        'radius': ICE_1_RADIUS,
        'speed': ICE_1_SPEED,
        'range': ICE_1_RANGE,
        'color': ICE_1_COLOR,
        'cooldown': ICE_1_COOLDOWN,
        'slow_duration': ICE_1_SLOW_DURATION,
        'slow_factor': ICE_1_SLOW_FACTOR,
    },
    'spell_ice_2': {
        'name': 'Ice Shard II',
        'type': 'projectile',
        'damage': ICE_2_DAMAGE,
        'radius': ICE_2_RADIUS,
        'speed': ICE_2_SPEED,
        'range': ICE_2_RANGE,
        'color': ICE_2_COLOR,
        'cooldown': ICE_2_COOLDOWN,
        'slow_duration': ICE_2_SLOW_DURATION,
        'slow_factor': ICE_2_SLOW_FACTOR,
    },
    'spell_ice_3': {
        'name': 'Ice Shard III',
        'type': 'projectile',
        'damage': ICE_3_DAMAGE,
        'radius': ICE_3_RADIUS,
        'speed': ICE_3_SPEED,
        'range': ICE_3_RANGE,
        'color': ICE_3_COLOR,
        'cooldown': ICE_3_COOLDOWN,
        'slow_duration': ICE_3_SLOW_DURATION,
        'slow_factor': ICE_3_SLOW_FACTOR,
    },
    'spell_ice_4': {
        'name': 'Ice Shard IV',
        'type': 'projectile',
        'damage': ICE_4_DAMAGE,
        'radius': ICE_4_RADIUS,
        'speed': ICE_4_SPEED,
        'range': ICE_4_RANGE,
        'color': ICE_4_COLOR,
        'cooldown': ICE_4_COOLDOWN,
        'slow_duration': ICE_4_SLOW_DURATION,
        'slow_factor': ICE_4_SLOW_FACTOR,
    },
    'spell_ice_5': {
        'name': 'Ice Shard V',
        'type': 'projectile',
        'damage': ICE_5_DAMAGE,
        'radius': ICE_5_RADIUS,
        'speed': ICE_5_SPEED,
        'range': ICE_5_RANGE,
        'color': ICE_5_COLOR,
        'cooldown': ICE_5_COOLDOWN,
        'slow_duration': ICE_5_SLOW_DURATION,
        'slow_factor': ICE_5_SLOW_FACTOR,
    },
}
