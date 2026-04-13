"""Game-wide constants for the sandbox RPG."""
import os
from typing import Tuple

# -- Re-export data module constants for backward compatibility ----------------
from data.day_night import (                                          # noqa: F401
    DAY_LENGTH_BASE, NIGHT_SLEEP_SPEED_MULT,
    TIME_NIGHT_END, TIME_DAY_START, TIME_DAY_END, TIME_NIGHT_START,
    DAY_FLASH_DURATION, NIGHT_FLASH_DURATION,
    DAY_FLASH_FADE_DIVISOR, DAY_FLASH_TEXT, DAY_FLASH_COLOR,
    NIGHT_FLASH_FADE_DIVISOR, NIGHT_FLASH_TEXT, NIGHT_FLASH_COLOR,
    DAWN_FLASH_DURATION, DAWN_FLASH_TEXT, DAWN_FLASH_COLOR,
    DUSK_FLASH_DURATION, DUSK_FLASH_TEXT, DUSK_FLASH_COLOR,
    SLEEP_OVERLAY_TEXT, SLEEP_OVERLAY_COLOR,
    NIGHT_DARKNESS_THRESHOLD,
    NIGHT_DAMAGE_BASE, NIGHT_DAMAGE_INCREASE, NIGHT_DAMAGE_INCREASE_FREQ,
    NIGHT_DAMAGE_INTERVAL, LIGHT_SAFETY_RADIUS,
    TIME_SPEED_NORMAL, SLEEP_DURATION, SLEEP_SPEED_MULT, BED_INTERACT_RANGE,
)
from data.day_events import (                                         # noqa: F401
    WAVE_START_NIGHT, WAVE_BASE_COUNT, WAVE_SCALE_PER_NIGHT,
    WAVE_SPAWN_RADIUS, WAVE_SPAWN_RADIUS_VARIANCE,
    WAVE_DAY_BONUS_PER_DAY,
    WAVE_SPAWN_INITIAL_INTERVAL, WAVE_SPAWN_MIN_INTERVAL,
    WAVE_INTERVAL_REDUCTION, WAVE_SPAWN_BATCH, WAVE_RANGED_MOB_CHANCE,
    MOB_RESPAWN_INTERVAL, MOB_RESPAWN_MIN_DIST, MOB_MAX_COUNT, MOB_RESPAWN_BATCH,
    RANGED_ENEMY_START_DAY,
    PER_DAY_SCALE_FACTOR, MOB_SPAWN_ATTEMPTS,
    GRASS_MOB_SPAWN_CHANCE, FOREST_MOB_SPAWN_CHANCE, DIRT_MOB_SPAWN_CHANCE,
    ORC_SPAWN_CHANCE, GHOST_SPAWN_CHANCE, DARK_KNIGHT_SPAWN_CHANCE,
    NIGHT_MOB_SPAWN_CHANCE,
    INITIAL_MOB_SPAWNS,
)

# -- Display -------------------------------------------------------------------
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
TILE_SIZE: int = 32
WORLD_WIDTH: int = 200
WORLD_HEIGHT: int = 150
FPS: int = 60

# -- Colours -------------------------------------------------------------------
BLACK:  Tuple[int, int, int] = (0, 0, 0)
WHITE:  Tuple[int, int, int] = (255, 255, 255)
YELLOW: Tuple[int, int, int] = (255, 255, 80)
RED:    Tuple[int, int, int] = (255, 60, 60)
GREEN:  Tuple[int, int, int] = (60, 220, 80)
CYAN:   Tuple[int, int, int] = (80, 200, 255)
GRAY:   Tuple[int, int, int] = (160, 160, 170)
DARK_GRAY:   Tuple[int, int, int] = (80, 80, 90)
ORANGE:      Tuple[int, int, int] = (255, 160, 60)
PURPLE:      Tuple[int, int, int] = (160, 80, 200)
DARK_BROWN:  Tuple[int, int, int] = (60, 35, 15)
LIGHT_BLUE:  Tuple[int, int, int] = (140, 200, 255)
DARK_GREEN:  Tuple[int, int, int] = (30, 80, 30)

# -- Tile types ----------------------------------------------------------------
TILE_WATER:       int = 0
TILE_SAND:        int = 1
TILE_GRASS:       int = 2
TILE_DIRT:        int = 3
TILE_STONE_FLOOR: int = 4
TILE_STONE_WALL:  int = 5
TILE_FOREST:      int = 6
TILE_CAVE_FLOOR:  int = 7
TILE_CAVE_ENTRANCE: int = 8

# -- Cave system ---------------------------------------------------------------
CAVE_COUNT: int = 3                  # number of caves per map
CAVE_WIDTH: int = 60                 # cave interior width in tiles
CAVE_HEIGHT: int = 45               # cave interior height in tiles
CAVE_WALL_DENSITY: float = 0.48     # cellular automata initial wall chance
CAVE_SMOOTH_PASSES: int = 5         # CA smoothing iterations
CAVE_MOB_TYPES: tuple = ('skeleton', 'orc', 'dark_knight', 'troll', 'ghost', 'wraith')
CAVE_MOB_COUNT: int = 15            # mobs per cave
CAVE_BOSS_TYPES: tuple = ('boss_golem', 'boss_lich', 'boss_dragon', 'boss_necromancer', 'boss_troll_king')
CAVE_ORE_COUNT: int = 8             # iron ore nodes per cave
CAVE_DIAMOND_COUNT: int = 3         # diamond nodes per cave
CAVE_HP_MULT: float = 1.5           # extra HP multiplier for cave mobs
CAVE_DMG_MULT: float = 1.3          # extra damage multiplier for cave mobs
CAVE_ENTRANCE_MIN_DIST: float = 800.0  # min px distance between cave entrances

# -- Save system ---------------------------------------------------------------
_PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_DIR: str = os.path.join(_PROJECT_ROOT, "save")
SAVE_SLOTS: int = 4          # 0 = quick-save, 1-3 = manual
QUICK_SAVE_SLOT: int = 0

# -- Inventory -----------------------------------------------------------------
HOTBAR_CAPACITY: int = 6
INVENTORY_SLOTS_PER_PAGE: int = 24
INVENTORY_PAGES: int = 4
INVENTORY_COLS: int = 6
INVENTORY_TOTAL_SLOTS: int = INVENTORY_SLOTS_PER_PAGE * INVENTORY_PAGES  # 96

# -- Stats & Combat (re-exported from data.stats) ------------------------------
from data.stats import (                                              # noqa: F401
    STAT_POINTS_PER_LEVEL,
    STR_DAMAGE_MULT, BASE_MELEE_DAMAGE, BASE_MELEE_DAMAGE_MIN,
    LEVEL_DAMAGE_MULT,
    AGI_SPEED_BONUS, AGI_SPEED_BONUS_CAP,
    PLAYER_BASE_SPEED, MOVEMENT_ACCEL_MULT,
    SPRITE_FLIP_THRESHOLD,
    AGILITY_COOLDOWN_REDUCTION, BASE_ATTACK_COOLDOWN, MIN_ATTACK_COOLDOWN,
    AGI_RANGED_SPEED_BONUS, AGI_RANGED_SPEED_BONUS_CAP,
    AGI_RANGED_DAMAGE_MULT, MIN_RANGED_COOLDOWN,
    LEVEL_UP_BASE_HP, VIT_HP_BONUS_PER_LEVEL, VITALITY_CAMPFIRE_BONUS_PER,
    CRIT_CHANCE_PER_LUCK, CRIT_DAMAGE_MULT, LUCK_HARVEST_CHANCE,
)

# -- Sleep (re-exported from data.day_night) ------------------------------------

# -- World Generation ----------------------------------------------------------
ELEVATION_SCALE: float = 0.045
MOISTURE_SCALE: float = 0.06
MOISTURE_OFFSET: float = 500.0
ELEVATION_OCTAVES: int = 6
MOISTURE_OCTAVES: int = 4

# -- Building system -----------------------------------------------------------
WALL_HP: int = 100
TURRET_HP: int = 80
TURRET_RANGE: float = 200.0
TURRET_DAMAGE: int = 8
TURRET_COOLDOWN: float = 1.5

# Per-enhancement-level turret scaling (from centralized enhancement module)
from core.enhancement import (                                        # noqa: F401
    TURRET_ENHANCE_DAMAGE, TURRET_ENHANCE_HP, TURRET_ENHANCE_DR,
)
CHEST_CAPACITY: int = 96
REPAIR_RANGE: float = 60.0                    # max distance to repair a structure
CAMPFIRE_BASE_HEAL: int = 3               # base HP healed per tick near campfire
CAMPFIRE_HEAL_RADIUS: float = 120.0       # proximity radius for campfire healing (px)
CAMPFIRE_HEAL_INTERVAL: float = 1.0       # seconds between campfire heal ticks
# VITALITY_CAMPFIRE_BONUS_PER re-exported from data.stats above

# -- Wave system (re-exported from data.day_events) ----------------------------

# -- Day/Night timing (re-exported from data.day_night) ------------------------

# -- Difficulty (re-exported from data.difficulty) -----------------------------
from data.difficulty import (                                          # noqa: F401
    DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD, DIFFICULTY_HARDCORE,
    DIFFICULTY_NAMES, DIFFICULTY_MULTIPLIERS, DIFFICULTY_PROFILES,
    get_profile as get_difficulty_profile,
)

# -- Mob respawn (re-exported from data.day_events) ----------------------------

# -- Ranged enemies (re-exported from data.day_events) -------------------------

# -- Placement preview ---------------------------------------------------------
PLACEMENT_PREVIEW_COLOR: Tuple[int, int, int, int] = (60, 220, 80, 120)
PLACEMENT_INVALID_COLOR: Tuple[int, int, int, int] = (220, 60, 60, 120)

# -- Font sizes ----------------------------------------------------------------
FONT_SIZE_MAIN: int = 16
FONT_SIZE_SM: int = 13
FONT_SIZE_LG: int = 22
FONT_SIZE_XL: int = 48

# -- Player (base speed, agility etc. re-exported from data.stats above) -------
PLAYER_FRICTION: float = 0.82
PLAYER_COLLIDER_W: int = 20
PLAYER_COLLIDER_H: int = 28
STARTING_WOOD: int = 5
STARTING_STONE: int = 3
PLAYER_TORCH_LIGHT_RADIUS: int = 110

# -- Melee / Ranged combat tuning (stat scaling re-exported from data.stats) ---
SPEAR_ATTACK_RANGE: float = 65.0
WEAPON_ATTACK_RANGE: float = 55.0
UNARMED_ATTACK_RANGE: float = 38.0
MELEE_KNOCKBACK_FORCE: float = 200.0
ATTACK_ANIM_DURATION: float = 0.18
INTERACT_COOLDOWN: float = 0.25

# -- Contact / projectile damage -----------------------------------------------
CONTACT_DAMAGE_RADIUS: float = 28.0
PLAYER_HIT_INVULN: float = 0.5
DAMAGE_FLASH_DURATION: float = 0.15
HIT_SHAKE_AMOUNT: float = 4.0
HIT_SHAKE_DURATION: float = 0.2
ENEMY_PROJ_HIT_RADIUS: float = 20.0
PROJ_SHAKE_AMOUNT: float = 3.0
PROJ_SHAKE_DURATION: float = 0.15

# -- Night damage (re-exported from data.day_night) ----------------------------

# -- Interaction ranges --------------------------------------------------------
INTERACT_RANGE: float = 50.0
HARVEST_RANGE: float = 50.0
# BED_INTERACT_RANGE re-exported from data/day_night.py above
# LUCK_HARVEST_CHANCE re-exported from data/stats.py above

# -- Mob spawning tuning (re-exported from data.day_events) --------------------

# -- World population ----------------------------------------------------------
TREE_COUNT: int = 350
FOREST_TREE_COUNT: int = 150
ROCK_COUNT: int = 200

# -- Building / placeable HP ---------------------------------------------------
TRAP_HP: int = 40
BED_HP: int = 80
CAMPFIRE_HP: int = 60
CHEST_HP_VALUE: int = 60
ENCHANT_TABLE_CAPACITY: int = 9
ENCHANT_TABLE_HP: int = 60
DOOR_HP: int = 50
DOOR_COLLIDER_W: int = 24
DOOR_COLLIDER_H: int = 32
STONE_WALL_HP_MULT: float = 1.5
CAMPFIRE_LIGHT_RADIUS: int = 180
TORCH_LIGHT_RADIUS: int = 120

# -- Level up (re-exported from data.stats) ------------------------------------

# -- HUD -----------------------------------------------------------------------
NOTIFICATION_DURATION: float = 2.5
HUD_REFRESH_INTERVAL: float = 0.5
DMG_NUMBER_FLOAT_SPEED: float = 40.0
MOB_HP_BAR_W: int = 28
MOB_HP_BAR_H: int = 4
PLACEABLE_HP_BAR_W: int = 28
PLACEABLE_HP_BAR_H: int = 3
HOTBAR_SLOTS: int = 6
HOTBAR_SLOT_SIZE: int = 48
HOTBAR_SLOT_GAP: int = 6

# -- Window limits -------------------------------------------------------------
MIN_WINDOW_WIDTH: int = 640
MIN_WINDOW_HEIGHT: int = 480

# -- Initial mob population (re-exported from data.day_events) -----------------
