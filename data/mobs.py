"""Mob definitions and wave composition data."""
from typing import Dict, List, Any

MOB_DATA: Dict[str, Dict[str, Any]] = {
    'slime': {
        'hp': 30, 'speed': 35, 'detection': 180, 'damage': 5, 'xp': 15,
        'solid': True, 'ranged': False,
    },
    'skeleton': {
        'hp': 60, 'speed': 50, 'detection': 220, 'damage': 10, 'xp': 35,
        'solid': True, 'ranged': False,
    },
    'wolf': {
        'hp': 40, 'speed': 65, 'detection': 160, 'damage': 8, 'xp': 25,
        'solid': True, 'ranged': False,
    },
    'goblin': {
        'hp': 50, 'speed': 45, 'detection': 200, 'damage': 12, 'xp': 40,
        'solid': True, 'ranged': False,
    },
    'ghost': {
        'hp': 35, 'speed': 40, 'detection': 250, 'damage': 6, 'xp': 50,
        'solid': False, 'ranged': False,
    },
    'spider': {
        'hp': 25, 'speed': 55, 'detection': 140, 'damage': 7, 'xp': 20,
        'solid': True, 'ranged': False,
    },
    'orc': {
        'hp': 90, 'speed': 38, 'detection': 180, 'damage': 16, 'xp': 60,
        'solid': True, 'ranged': False,
    },
    'dark_knight': {
        'hp': 120, 'speed': 42, 'detection': 200, 'damage': 20, 'xp': 80,
        'solid': True, 'ranged': False,
    },
    # -- New enemies --
    'zombie': {
        'hp': 70, 'speed': 30, 'detection': 160, 'damage': 14, 'xp': 35,
        'solid': True, 'ranged': False,
    },
    'wraith': {
        'hp': 55, 'speed': 52, 'detection': 280, 'damage': 10, 'xp': 55,
        'solid': False, 'ranged': False,
    },
    'troll': {
        'hp': 150, 'speed': 28, 'detection': 160, 'damage': 22, 'xp': 75,
        'solid': True, 'ranged': False,
    },
    # -- Ranged enemies (appear after Day 3) --
    'skeleton_archer': {
        'hp': 50, 'speed': 35, 'detection': 260, 'damage': 8, 'xp': 45,
        'solid': True, 'ranged': True,
        'ranged_damage': 12, 'ranged_range': 250.0, 'ranged_cooldown': 2.0,
        'ranged_speed': 350.0,
    },
    'goblin_shaman': {
        'hp': 45, 'speed': 32, 'detection': 240, 'damage': 6, 'xp': 50,
        'solid': True, 'ranged': True,
        'ranged_damage': 15, 'ranged_range': 220.0, 'ranged_cooldown': 2.5,
        'ranged_speed': 300.0,
    },
    # -- Boss mobs (glow, drop spell books) --
    'boss_golem': {
        'hp': 400, 'speed': 22, 'detection': 300, 'damage': 35, 'xp': 250,
        'solid': True, 'ranged': False, 'boss': True,
        'glow_color': (255, 60, 60),
    },
    'boss_lich': {
        'hp': 300, 'speed': 35, 'detection': 350, 'damage': 28, 'xp': 300,
        'solid': True, 'ranged': True, 'boss': True,
        'glow_color': (200, 60, 255),
        'ranged_damage': 25, 'ranged_range': 300.0, 'ranged_cooldown': 1.8,
        'ranged_speed': 400.0,
    },
    'boss_dragon': {
        'hp': 500, 'speed': 30, 'detection': 350, 'damage': 40, 'xp': 350,
        'solid': True, 'ranged': True, 'boss': True,
        'glow_color': (255, 140, 30),
        'ranged_damage': 30, 'ranged_range': 280.0, 'ranged_cooldown': 1.5,
        'ranged_speed': 380.0,
    },
    'boss_necromancer': {
        'hp': 280, 'speed': 40, 'detection': 380, 'damage': 22, 'xp': 280,
        'solid': True, 'ranged': True, 'boss': True,
        'glow_color': (80, 255, 80),
        'ranged_damage': 20, 'ranged_range': 320.0, 'ranged_cooldown': 2.0,
        'ranged_speed': 320.0,
    },
    'boss_troll_king': {
        'hp': 600, 'speed': 20, 'detection': 280, 'damage': 50, 'xp': 400,
        'solid': True, 'ranged': False, 'boss': True,
        'glow_color': (100, 180, 60),
    },
}

# Mobs that can appear in night waves, ordered by difficulty tier
WAVE_MOB_TIERS: List[List[str]] = [
    ['slime', 'spider'],                            # tier 0 -- easy
    ['skeleton', 'wolf', 'goblin', 'zombie'],       # tier 1 -- medium
    ['orc', 'wraith'],                              # tier 2 -- hard
    ['dark_knight', 'troll'],                       # tier 3 -- elite
]

# Ranged enemies that join waves after RANGED_ENEMY_START_DAY
WAVE_RANGED_MOBS: List[str] = ['skeleton_archer', 'goblin_shaman']

# Boss mobs that can spawn during waves
WAVE_BOSS_MOBS: List[str] = [
    'boss_golem', 'boss_lich', 'boss_dragon',
    'boss_necromancer', 'boss_troll_king',
]
