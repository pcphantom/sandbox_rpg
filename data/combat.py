"""Ranged weapon data, ammo bonuses, and armor values."""
from typing import Dict, Any
from core.enhancement import ARMOR_VALUES

RANGED_DATA: Dict[str, Dict[str, Any]] = {
    'bow':      {'damage': 18, 'range': 300.0, 'ammo': ['arrow', 'fire_arrow'],
                 'speed': 400.0, 'cooldown': 0.6},
    'crossbow': {'damage': 28, 'range': 350.0, 'ammo': ['bolt'],
                 'speed': 500.0, 'cooldown': 1.2},
    'sling':    {'damage': 12, 'range': 250.0, 'ammo': ['rock_ammo', 'sling_bullet'],
                 'speed': 350.0, 'cooldown': 0.5},
}

AMMO_BONUS_DAMAGE: Dict[str, int] = {
    'sling_bullet': 5, 'arrow': 0, 'rock_ammo': 0,
    'fire_arrow': 8, 'bolt': 0,
}

# ARMOR_VALUES is imported from systems.enhancement (single source of truth).

# Bomb/throwable data
BOMB_DATA: Dict[str, Dict[str, Any]] = {
    'bomb': {
        'damage': 50,
        'radius': 80.0,
        'speed': 300.0,
        'range': 250.0,
        'color': (255, 160, 40),
        'fuse_time': 0.0,
    },
}
