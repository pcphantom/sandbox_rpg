"""Difficulty system — re-exports all difficulty variables from game_controller.

The single source of truth is game_controller.py.  This module provides
backwards-compatible re-exports plus the helper functions that build
derived data structures (DIFFICULTY_MULTIPLIERS tuple format, get_profile).
"""
from game_controller import (                                         # noqa: F401
    DIFFICULTY_EASY,
    DIFFICULTY_NORMAL,
    DIFFICULTY_HARD,
    DIFFICULTY_HARDCORE,
    DIFFICULTY_NAMES,
    DIFFICULTY_PROFILES,
    RESOURCE_RESPAWN_DAYS,
    CAVE_RESET_DAYS,
)

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
