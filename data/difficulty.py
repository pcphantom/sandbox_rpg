"""Difficulty system — all variables that scale with the difficulty setting.

This is the single source of truth for difficulty-related multipliers.
Every system that needs to scale by difficulty imports from here.

Multipliers are stored per-difficulty-level in DIFFICULTY_PROFILES so that
each aspect can be tuned independently.
"""

# ======================================================================
# DIFFICULTY LEVELS
# ======================================================================
DIFFICULTY_EASY: int = 0
DIFFICULTY_NORMAL: int = 1
DIFFICULTY_HARD: int = 2
DIFFICULTY_HARDCORE: int = 3
DIFFICULTY_NAMES: tuple = ("Easy", "Normal", "Hard", "Hardcore")

# ======================================================================
# DIFFICULTY PROFILES
# ======================================================================
# Each profile is a dict so individual values are named and self-documenting.
# Access: DIFFICULTY_PROFILES[level]['enemy_hp_mult']
DIFFICULTY_PROFILES: dict = {
    DIFFICULTY_EASY: {
        'enemy_hp_mult':      1.0,   # multiplier on mob base HP
        'enemy_dmg_mult':     1.0,   # multiplier on mob base damage (contact + ranged)
        'spawn_rate_mult':    1.0,   # multiplier on mob respawn frequency (higher = faster)
        'wave_count_mult':    1.0,   # multiplier on night wave mob count
        'boss_hp_mult':       1.0,   # additional multiplier on boss HP (stacks with enemy_hp)
        'boss_dmg_mult':      1.0,   # additional multiplier on boss damage
        'night_dmg_mult':     1.0,   # multiplier on night darkness damage
        'xp_mult':            1.0,   # multiplier on XP earned
        'loot_luck_bonus':    0.0,   # flat bonus added to rarity roll weights for better tier
    },
    DIFFICULTY_NORMAL: {
        'enemy_hp_mult':      1.3,
        'enemy_dmg_mult':     1.3,
        'spawn_rate_mult':    1.2,
        'wave_count_mult':    1.3,
        'boss_hp_mult':       1.0,
        'boss_dmg_mult':      1.0,
        'night_dmg_mult':     1.0,
        'xp_mult':            1.0,
        'loot_luck_bonus':    0.0,
    },
    DIFFICULTY_HARD: {
        'enemy_hp_mult':      1.8,
        'enemy_dmg_mult':     1.8,
        'spawn_rate_mult':    1.5,
        'wave_count_mult':    1.8,
        'boss_hp_mult':       1.3,
        'boss_dmg_mult':      1.2,
        'night_dmg_mult':     1.5,
        'xp_mult':            1.2,
        'loot_luck_bonus':    0.0,
    },
    DIFFICULTY_HARDCORE: {
        'enemy_hp_mult':      3.5,
        'enemy_dmg_mult':     3.0,
        'spawn_rate_mult':    4.0,
        'wave_count_mult':    4.0,
        'boss_hp_mult':       2.0,
        'boss_dmg_mult':      1.5,
        'night_dmg_mult':     2.0,
        'xp_mult':            1.5,
        'loot_luck_bonus':    0.0,
    },
}


# ======================================================================
# BACKWARD-COMPATIBLE TUPLE FORMAT
# ======================================================================
# Legacy callers expect: (enemy_hp_mult, enemy_dmg_mult, spawn_rate_mult, wave_count_mult)
DIFFICULTY_MULTIPLIERS: dict = {
    level: (
        prof['enemy_hp_mult'],
        prof['enemy_dmg_mult'],
        prof['spawn_rate_mult'],
        prof['wave_count_mult'],
    )
    for level, prof in DIFFICULTY_PROFILES.items()
}


# ======================================================================
# HELPER
# ======================================================================

def get_profile(difficulty: int) -> dict:
    """Return the full profile dict for the given difficulty level."""
    return DIFFICULTY_PROFILES.get(difficulty, DIFFICULTY_PROFILES[DIFFICULTY_EASY])
