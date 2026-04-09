"""Game-wide constants for the sandbox RPG."""
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
DARK_GRAY: Tuple[int, int, int] = (80, 80, 90)
ORANGE: Tuple[int, int, int] = (255, 160, 60)
PURPLE: Tuple[int, int, int] = (160, 80, 200)

# -- Tile types ----------------------------------------------------------------
TILE_WATER:       int = 0
TILE_SAND:        int = 1
TILE_GRASS:       int = 2
TILE_DIRT:        int = 3
TILE_STONE_FLOOR: int = 4
TILE_STONE_WALL:  int = 5

# -- Save system ---------------------------------------------------------------
SAVE_DIR: str = "saves"
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
