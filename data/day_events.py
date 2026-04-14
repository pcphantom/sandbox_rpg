"""Day events — re-exports all day-event tuning from game_controller.

This module exists for backwards compatibility.  The single source of truth
is game_controller.py.  All code that imports ``from data.day_events import X``
will continue to work unchanged.

For per-cycle (time-of-day) tuning see data/day_night.py.
"""
from game_controller import (                                         # noqa: F401
    WAVE_START_NIGHT,
    WAVE_BASE_COUNT,
    WAVE_SCALE_PER_NIGHT,
    WAVE_SPAWN_RADIUS,
    WAVE_SPAWN_RADIUS_VARIANCE,
    WAVE_DAY_BONUS_PER_DAY,
    WAVE_SPAWN_INITIAL_INTERVAL,
    WAVE_SPAWN_MIN_INTERVAL,
    WAVE_INTERVAL_REDUCTION,
    WAVE_SPAWN_BATCH,
    WAVE_RANGED_MOB_CHANCE,
    NIGHT_WAVE_COUNT,
    NIGHT_WAVE_SPACING_HOURS,
    MOB_RESPAWN_INTERVAL,
    MOB_RESPAWN_MIN_DIST,
    MOB_MAX_COUNT,
    MOB_RESPAWN_BATCH,
    RANGED_ENEMY_START_DAY,
    PER_DAY_SCALE_FACTOR,
    MOB_SPAWN_ATTEMPTS,
    GRASS_MOB_SPAWN_CHANCE,
    FOREST_MOB_SPAWN_CHANCE,
    DIRT_MOB_SPAWN_CHANCE,
    ORC_SPAWN_CHANCE,
    GHOST_SPAWN_CHANCE,
    DARK_KNIGHT_SPAWN_CHANCE,
    NIGHT_MOB_SPAWN_CHANCE,
    INITIAL_MOB_SPAWNS,
    RESOURCE_RESPAWN_DAYS,
    CAVE_RESET_DAYS,
)
