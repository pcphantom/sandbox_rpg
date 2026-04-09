"""Game-wide constants for the sandbox RPG."""
import os
from typing import Tuple

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

# -- Save system ---------------------------------------------------------------
SAVE_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save")
SAVE_SLOTS: int = 4          # 0 = quick-save, 1-3 = manual
QUICK_SAVE_SLOT: int = 0

# -- Inventory -----------------------------------------------------------------
INVENTORY_SLOTS_PER_PAGE: int = 24
INVENTORY_PAGES: int = 4
INVENTORY_COLS: int = 6
INVENTORY_TOTAL_SLOTS: int = INVENTORY_SLOTS_PER_PAGE * INVENTORY_PAGES  # 96

# -- Stats ---------------------------------------------------------------------
STAT_POINTS_PER_LEVEL: int = 3

# -- Combat --------------------------------------------------------------------
MIN_ATTACK_COOLDOWN: float = 0.15
BASE_ATTACK_COOLDOWN: float = 0.30
AGILITY_COOLDOWN_REDUCTION: float = 0.02

# -- Sleep ---------------------------------------------------------------------
SLEEP_DURATION: float = 5.0
SLEEP_TIME_MULTIPLIER: float = 12.0

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
CHEST_CAPACITY: int = 24

# -- Wave system ---------------------------------------------------------------
WAVE_START_NIGHT: int = 3
WAVE_BASE_COUNT: int = 3
WAVE_SCALE_PER_NIGHT: int = 2
WAVE_SPAWN_RADIUS: float = 350.0

# -- Day/Night timing ----------------------------------------------------------
DAY_LENGTH_BASE: float = 960.0           # 4x slower than old 240.0
NIGHT_SLEEP_SPEED_MULT: float = 12.0     # speed mult when sleeping on bed at night

# -- Difficulty ----------------------------------------------------------------
DIFFICULTY_EASY: int = 0
DIFFICULTY_NORMAL: int = 1
DIFFICULTY_HARD: int = 2
DIFFICULTY_HARDCORE: int = 3
DIFFICULTY_NAMES: Tuple[str, ...] = ("Easy", "Normal", "Hard", "Hardcore")

# Difficulty multipliers: (enemy_hp_mult, enemy_dmg_mult, spawn_rate_mult, wave_count_mult)
DIFFICULTY_MULTIPLIERS: dict = {
    DIFFICULTY_EASY:     (1.0, 1.0, 1.0, 1.0),
    DIFFICULTY_NORMAL:   (1.3, 1.3, 1.2, 1.3),
    DIFFICULTY_HARD:     (1.8, 1.8, 1.5, 1.8),
    DIFFICULTY_HARDCORE: (2.5, 2.5, 2.0, 2.5),
}

# -- Mob respawn ---------------------------------------------------------------
MOB_RESPAWN_INTERVAL: float = 8.0    # seconds between natural mob respawns

# -- Ranged enemies ------------------------------------------------------------
RANGED_ENEMY_START_DAY: int = 3      # ranged enemies appear after this day

# -- Placement preview ---------------------------------------------------------
PLACEMENT_PREVIEW_COLOR: Tuple[int, int, int, int] = (60, 220, 80, 120)
PLACEMENT_INVALID_COLOR: Tuple[int, int, int, int] = (220, 60, 60, 120)
