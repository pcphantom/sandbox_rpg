"""Mob definitions and wave composition data.

Boss glow colors are sourced from game_controller.py.
"""
from typing import Dict, List, Any
from game_controller import (
    BOSS_GLOW_GOLEM, BOSS_GLOW_LICH, BOSS_GLOW_DRAGON,
    BOSS_GLOW_NECROMANCER, BOSS_GLOW_TROLL_KING,
    BOSS_GLOW_DRAGON_RED, BOSS_GLOW_DRAGON_GREEN,
    BOSS_GLOW_DRAGON_BLACK, BOSS_GLOW_DRAGON_WHITE,
    BOSS_GLOW_SHADOW_DRAGON,
)

MOB_DATA: Dict[str, Dict[str, Any]] = {
    # ====================================================================
    # TIER 0 — Easy / Early game (days 1-3, weak overworld spawns)
    # ====================================================================
    'slime': {
        'hp': 30, 'speed': 35, 'detection': 180, 'damage': 5, 'xp': 15,
        'solid': True, 'ranged': False,
    },
    'spider': {
        'hp': 25, 'speed': 55, 'detection': 140, 'damage': 7, 'xp': 20,
        'solid': True, 'ranged': False,
    },
    'snake': {
        'hp': 20, 'speed': 60, 'detection': 120, 'damage': 6, 'xp': 18,
        'solid': True, 'ranged': False,
    },
    'kobold': {
        'hp': 28, 'speed': 50, 'detection': 160, 'damage': 6, 'xp': 22,
        'solid': True, 'ranged': False,
    },

    # ====================================================================
    # TIER 1 — Medium (early-mid game)
    # ====================================================================
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
    'zombie': {
        'hp': 70, 'speed': 30, 'detection': 160, 'damage': 14, 'xp': 35,
        'solid': True, 'ranged': False,
    },
    'ghost': {
        'hp': 35, 'speed': 40, 'detection': 250, 'damage': 6, 'xp': 50,
        'solid': False, 'ranged': False,
    },

    # ====================================================================
    # TIER 2 — Hard (mid game, ~week 1+)
    # ====================================================================
    'orc': {
        'hp': 90, 'speed': 38, 'detection': 180, 'damage': 16, 'xp': 60,
        'solid': True, 'ranged': False,
    },
    'wraith': {
        'hp': 55, 'speed': 52, 'detection': 280, 'damage': 10, 'xp': 55,
        'solid': False, 'ranged': False,
    },
    'hobgoblin': {
        'hp': 80, 'speed': 42, 'detection': 200, 'damage': 14, 'xp': 55,
        'solid': True, 'ranged': False,
    },
    'bear': {
        'hp': 100, 'speed': 35, 'detection': 140, 'damage': 18, 'xp': 65,
        'solid': True, 'ranged': False,
    },
    'mephit_fire': {
        'hp': 45, 'speed': 55, 'detection': 220, 'damage': 12, 'xp': 50,
        'solid': True, 'ranged': True,
        'ranged_damage': 14, 'ranged_range': 200.0, 'ranged_cooldown': 2.0,
        'ranged_speed': 320.0,
    },
    'mephit_ice': {
        'hp': 45, 'speed': 55, 'detection': 220, 'damage': 10, 'xp': 50,
        'solid': True, 'ranged': True,
        'ranged_damage': 12, 'ranged_range': 200.0, 'ranged_cooldown': 2.2,
        'ranged_speed': 300.0,
    },
    'mephit_lightning': {
        'hp': 45, 'speed': 58, 'detection': 230, 'damage': 11, 'xp': 55,
        'solid': True, 'ranged': True,
        'ranged_damage': 16, 'ranged_range': 210.0, 'ranged_cooldown': 1.8,
        'ranged_speed': 380.0,
    },

    # ====================================================================
    # TIER 3 — Elite (mid-late game, ~week 2+)
    # ====================================================================
    'dark_knight': {
        'hp': 120, 'speed': 42, 'detection': 200, 'damage': 20, 'xp': 80,
        'solid': True, 'ranged': False,
    },
    'troll': {
        'hp': 150, 'speed': 28, 'detection': 160, 'damage': 22, 'xp': 75,
        'solid': True, 'ranged': False,
    },
    'ogre': {
        'hp': 180, 'speed': 24, 'detection': 160, 'damage': 28, 'xp': 90,
        'solid': True, 'ranged': False, 'large': True,
    },
    'ogre_mage': {
        'hp': 140, 'speed': 30, 'detection': 240, 'damage': 18, 'xp': 100,
        'solid': True, 'ranged': True, 'large': True,
        'ranged_damage': 22, 'ranged_range': 260.0, 'ranged_cooldown': 2.0,
        'ranged_speed': 340.0,
    },
    'golem': {
        'hp': 220, 'speed': 18, 'detection': 140, 'damage': 30, 'xp': 100,
        'solid': True, 'ranged': False, 'large': True,
    },

    # ====================================================================
    # TIER 4 — Late game (week 3+), dragons and high-tier
    # ====================================================================
    'centaur': {
        'hp': 110, 'speed': 55, 'detection': 280, 'damage': 15, 'xp': 85,
        'solid': True, 'ranged': True,
        'ranged_damage': 18, 'ranged_range': 280.0, 'ranged_cooldown': 1.5,
        'ranged_speed': 400.0,
    },
    'dragon_red': {
        'hp': 500, 'speed': 32, 'detection': 350, 'damage': 40, 'xp': 300,
        'solid': True, 'ranged': True, 'boss': True, 'large': True,
        'glow_color': BOSS_GLOW_DRAGON_RED,
        'ranged_damage': 35, 'ranged_range': 300.0, 'ranged_cooldown': 1.5,
        'ranged_speed': 380.0,
    },
    'dragon_green': {
        'hp': 450, 'speed': 34, 'detection': 340, 'damage': 35, 'xp': 280,
        'solid': True, 'ranged': True, 'boss': True, 'large': True,
        'glow_color': BOSS_GLOW_DRAGON_GREEN,
        'ranged_damage': 30, 'ranged_range': 280.0, 'ranged_cooldown': 1.6,
        'ranged_speed': 360.0,
    },
    'dragon_black': {
        'hp': 550, 'speed': 30, 'detection': 360, 'damage': 42, 'xp': 320,
        'solid': True, 'ranged': True, 'boss': True, 'large': True,
        'glow_color': BOSS_GLOW_DRAGON_BLACK,
        'ranged_damage': 38, 'ranged_range': 310.0, 'ranged_cooldown': 1.4,
        'ranged_speed': 400.0,
    },
    'dragon_white': {
        'hp': 480, 'speed': 36, 'detection': 350, 'damage': 38, 'xp': 300,
        'solid': True, 'ranged': True, 'boss': True, 'large': True,
        'glow_color': BOSS_GLOW_DRAGON_WHITE,
        'ranged_damage': 32, 'ranged_range': 290.0, 'ranged_cooldown': 1.5,
        'ranged_speed': 370.0,
    },
    'shadow_dragon': {
        'hp': 800, 'speed': 28, 'detection': 400, 'damage': 55, 'xp': 500,
        'solid': True, 'ranged': True, 'boss': True, 'large': True,
        'glow_color': BOSS_GLOW_SHADOW_DRAGON,
        'ranged_damage': 45, 'ranged_range': 320.0, 'ranged_cooldown': 1.2,
        'ranged_speed': 420.0,
    },

    # ====================================================================
    # Ranged enemies (appear after RANGED_ENEMY_START_DAY)
    # ====================================================================
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
    'orc_archer': {
        'hp': 70, 'speed': 35, 'detection': 250, 'damage': 12, 'xp': 65,
        'solid': True, 'ranged': True,
        'ranged_damage': 16, 'ranged_range': 260.0, 'ranged_cooldown': 1.8,
        'ranged_speed': 360.0,
    },

    # ====================================================================
    # BOSS mobs (glow, drop spell books)
    # ====================================================================
    'boss_golem': {
        'hp': 400, 'speed': 22, 'detection': 300, 'damage': 35, 'xp': 250,
        'solid': True, 'ranged': False, 'boss': True,
        'glow_color': BOSS_GLOW_GOLEM,
    },
    'boss_lich': {
        'hp': 300, 'speed': 35, 'detection': 350, 'damage': 28, 'xp': 300,
        'solid': True, 'ranged': True, 'boss': True,
        'glow_color': BOSS_GLOW_LICH,
        'ranged_damage': 25, 'ranged_range': 300.0, 'ranged_cooldown': 1.8,
        'ranged_speed': 400.0,
    },
    'boss_dragon': {
        'hp': 500, 'speed': 30, 'detection': 350, 'damage': 40, 'xp': 350,
        'solid': True, 'ranged': True, 'boss': True,
        'glow_color': BOSS_GLOW_DRAGON,
        'ranged_damage': 30, 'ranged_range': 280.0, 'ranged_cooldown': 1.5,
        'ranged_speed': 380.0,
    },
    'boss_necromancer': {
        'hp': 280, 'speed': 40, 'detection': 380, 'damage': 22, 'xp': 280,
        'solid': True, 'ranged': True, 'boss': True,
        'glow_color': BOSS_GLOW_NECROMANCER,
        'ranged_damage': 20, 'ranged_range': 320.0, 'ranged_cooldown': 2.0,
        'ranged_speed': 320.0,
    },
    'boss_troll_king': {
        'hp': 600, 'speed': 20, 'detection': 280, 'damage': 50, 'xp': 400,
        'solid': True, 'ranged': False, 'boss': True,
        'glow_color': BOSS_GLOW_TROLL_KING,
    },
}

# Mobs that can appear in night waves, ordered by difficulty tier
WAVE_MOB_TIERS: List[List[str]] = [
    ['slime', 'spider', 'snake', 'kobold'],                         # tier 0 -- easy
    ['skeleton', 'wolf', 'goblin', 'zombie', 'ghost'],              # tier 1 -- medium
    ['orc', 'wraith', 'hobgoblin', 'bear', 'mephit_fire',
     'mephit_ice', 'mephit_lightning'],                             # tier 2 -- hard
    ['dark_knight', 'troll', 'ogre', 'ogre_mage', 'golem'],        # tier 3 -- elite
    ['centaur', 'dragon_red', 'dragon_green',
     'dragon_black', 'dragon_white'],                               # tier 4 -- late game
]

# Ranged enemies that join waves after RANGED_ENEMY_START_DAY
WAVE_RANGED_MOBS: List[str] = [
    'skeleton_archer', 'goblin_shaman', 'orc_archer',
    'mephit_fire', 'mephit_ice', 'mephit_lightning', 'centaur',
]

# Boss mobs that can spawn during waves
WAVE_BOSS_MOBS: List[str] = [
    'boss_golem', 'boss_lich', 'boss_dragon',
    'boss_necromancer', 'boss_troll_king',
    'dragon_red', 'dragon_green', 'dragon_black', 'dragon_white',
    'shadow_dragon',
]

# Undead enemy types — these should only spawn at night on the overworld
UNDEAD_MOB_TYPES: frozenset = frozenset({
    'skeleton', 'zombie', 'ghost', 'wraith', 'skeleton_archer',
})

# Day spawn table — enemies that can appear during daytime on the overworld.
# These are generally non-undead, appropriate for each biome.
DAY_SPAWN_TABLE: Dict[str, List[str]] = {
    'grass':  ['slime', 'snake', 'kobold'],
    'forest': ['wolf', 'spider', 'bear', 'snake'],
    'dirt':   ['goblin', 'kobold', 'hobgoblin', 'orc'],
}

# Night spawn table — enemies that can appear at night on the overworld.
# Includes undead types plus tougher variants.
NIGHT_SPAWN_TABLE: Dict[str, List[str]] = {
    'grass':  ['skeleton', 'zombie', 'ghost', 'wraith'],
    'forest': ['wolf', 'spider', 'skeleton', 'ghost', 'wraith'],
    'dirt':   ['dark_knight', 'orc', 'hobgoblin', 'skeleton', 'zombie'],
}
