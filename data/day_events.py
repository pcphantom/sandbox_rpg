"""Day events — everything that scales or triggers based on which day it is.

For per-cycle (time-of-day) tuning see data/day_night.py.

This module controls:
  * Wave system parameters (when waves start, how they scale)
  * Mob respawn / population tuning
  * Day-based enemy unlocks & spawn-chance ramps
  * Initial overworld mob population table
"""
from typing import List, Tuple

# ======================================================================
# WAVE SYSTEM
# ======================================================================
# Waves only begin once the player has survived this many nights.
WAVE_START_NIGHT: int             = 1

# Base number of mobs in the first qualifying wave.
WAVE_BASE_COUNT: int              = 3

# Additional mobs added per night survived beyond WAVE_START_NIGHT.
WAVE_SCALE_PER_NIGHT: int        = 2

# Radius (px) from the player at which wave mobs spawn.
WAVE_SPAWN_RADIUS: float         = 350.0

# Random variance added/subtracted from WAVE_SPAWN_RADIUS.
WAVE_SPAWN_RADIUS_VARIANCE: float = 100.0

# Each successive day adds this many bonus mobs to the wave total
# (applied on top of the night-count scaling).
WAVE_DAY_BONUS_PER_DAY: int      = 1

# -- Spawn pacing within a wave --
# Seconds between batches at wave start.
WAVE_SPAWN_INITIAL_INTERVAL: float = 2.0
# Fastest possible interval (hard floor).
WAVE_SPAWN_MIN_INTERVAL: float     = 0.8
# Seconds shaved off the interval per qualifying night.
WAVE_INTERVAL_REDUCTION: float     = 0.1
# How many mobs spawn per batch tick.
WAVE_SPAWN_BATCH: int              = 3

# -- Wave composition --
# Chance that a given wave mob will be ranged (archer / mage) instead of melee,
# only after RANGED_ENEMY_START_DAY.
WAVE_RANGED_MOB_CHANCE: float      = 0.25

# ======================================================================
# MOB RESPAWN / POPULATION
# ======================================================================
# Seconds between natural mob respawn ticks (ambient overworld replenishment).
MOB_RESPAWN_INTERVAL: float = 4.0

# Minimum distance (px) from the player for a new mob to spawn.
MOB_RESPAWN_MIN_DIST: float = 300.0

# Hard cap on total mobs alive at once.
MOB_MAX_COUNT: int          = 80

# Mobs spawned per respawn tick when population is below the cap.
MOB_RESPAWN_BATCH: int      = 3

# ======================================================================
# DAY-BASED ENEMY PROGRESSION
# ======================================================================
# Ranged enemies (skeleton archers, etc.) start appearing after this day.
RANGED_ENEMY_START_DAY: int     = 3

# Every day, each mob's base stats are multiplied by (1 + day * SCALE_FACTOR).
PER_DAY_SCALE_FACTOR: float     = 0.05

# ======================================================================
# OVERWORLD SPAWN CHANCES  (per spawn-attempt roll)
# ======================================================================
# How many random attempts the spawner makes per tick.
MOB_SPAWN_ATTEMPTS: int          = 20

# -- Biome / tile spawn chances --
# On grass tiles:
GRASS_MOB_SPAWN_CHANCE: float    = 0.4
# On forest tiles:
FOREST_MOB_SPAWN_CHANCE: float   = 0.5
# On dirt tiles:
DIRT_MOB_SPAWN_CHANCE: float     = 0.4

# -- Special mob spawn chances --
# Chance for an orc instead of a generic dirt mob.
ORC_SPAWN_CHANCE: float          = 0.2
# Chance that a night-time spawn is a ghost.
GHOST_SPAWN_CHANCE: float        = 0.25
# Chance that a night-time spawn is a dark knight.
DARK_KNIGHT_SPAWN_CHANCE: float  = 0.15
# Chance that a non-specific night spawn is created.
NIGHT_MOB_SPAWN_CHANCE: float    = 0.4

# ======================================================================
# INITIAL MOB POPULATION (spawned once at world generation)
# ======================================================================
# Each tuple: (mob_type, required_tile_type, count)
# Tile constants imported inline to avoid circular deps.
INITIAL_MOB_SPAWNS: List[Tuple[str, int, int]] = [
    ('slime',  2, 25),    # TILE_GRASS  = 2
    ('wolf',   6, 10),    # TILE_FOREST = 6
    ('spider', 6,  8),    # TILE_FOREST = 6
    ('goblin', 3,  5),    # TILE_DIRT   = 3
]
