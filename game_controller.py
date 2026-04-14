"""game_controller.py — Centralized variable declarations for ALL game tuning.

This file contains ONLY declared variables — no logic, no functions, no classes.
Every script in the game that needs a tunable value imports it from here.

Sections are organized by game system with clear headers.
When you want to fine-tune the game during alpha testing, this is the ONLY
file you should need to open.

Chain of command:
    game_controller.py  (declares all control variables)
        -> data/*.py    (organizes data structures using these variables)
        -> systems/*.py (runs game logic using data and variables)
        -> game/*.py    (ties systems together for the main loop)
"""
from typing import Dict, List, Tuple, Any


# ######################################################################
#                        SCREEN / DISPLAY
# ######################################################################
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
FPS: int = 60
TILE_SIZE: int = 32
MIN_WINDOW_WIDTH: int = 640
MIN_WINDOW_HEIGHT: int = 480

# Display modes
DISPLAY_WINDOWED: int = 0
DISPLAY_FULLSCREEN: int = 1
DISPLAY_BORDERLESS: int = 2
DISPLAY_MODE_NAMES: Dict[int, str] = {
    0: "Windowed",
    1: "Fullscreen",
    2: "Borderless Windowed",
}
RESOLUTION_PRESETS: List[Tuple[int, int]] = [
    (1280, 720), (1366, 768), (1600, 900), (1920, 1080), (2560, 1440),
]


# ######################################################################
#                        GLOBAL COLOR PALETTE
# ######################################################################
# --- Base named colors (used across many systems) ---
BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
YELLOW: Tuple[int, int, int] = (255, 255, 80)
RED: Tuple[int, int, int] = (255, 60, 60)
GREEN: Tuple[int, int, int] = (60, 220, 80)
CYAN: Tuple[int, int, int] = (80, 200, 255)
GRAY: Tuple[int, int, int] = (160, 160, 170)
DARK_GRAY: Tuple[int, int, int] = (80, 80, 90)
ORANGE: Tuple[int, int, int] = (255, 160, 60)
PURPLE: Tuple[int, int, int] = (160, 80, 200)
DARK_BROWN: Tuple[int, int, int] = (60, 35, 15)
LIGHT_BLUE: Tuple[int, int, int] = (140, 200, 255)
DARK_GREEN: Tuple[int, int, int] = (30, 80, 30)

# --- Rarity tier colors (items, drops, display) ---
RARITY_COLOR_COMMON: Tuple[int, int, int] = (255, 255, 255)
RARITY_COLOR_RARE: Tuple[int, int, int] = (80, 140, 255)
RARITY_COLOR_EPIC: Tuple[int, int, int] = (180, 60, 255)
RARITY_COLOR_LEGENDARY: Tuple[int, int, int] = (255, 215, 0)
RARITY_COLOR_MYTHIC: Tuple[int, int, int] = (255, 50, 50)

# --- Enhancement level colors (+1 through +5) ---
# PRESERVED for future use — currently no inner borders are drawn.
# ENHANCEMENT_COLOR_1: Tuple[int, int, int] = (0, 200, 0)
# ENHANCEMENT_COLOR_2: Tuple[int, int, int] = (80, 140, 255)
# ENHANCEMENT_COLOR_3: Tuple[int, int, int] = (180, 60, 255)
# ENHANCEMENT_COLOR_4: Tuple[int, int, int] = (255, 215, 0)
# ENHANCEMENT_COLOR_5: Tuple[int, int, int] = (255, 50, 50)

# --- Enchantment element colors ---
ENCHANT_COLOR_FIRE: Tuple[int, int, int] = (255, 120, 30)
ENCHANT_COLOR_ICE: Tuple[int, int, int] = (100, 200, 255)
ENCHANT_COLOR_LIGHTNING: Tuple[int, int, int] = (180, 200, 255)
ENCHANT_COLOR_PROTECTION: Tuple[int, int, int] = (80, 255, 120)
ENCHANT_COLOR_REGEN: Tuple[int, int, int] = (50, 255, 50)
ENCHANT_COLOR_STRENGTH: Tuple[int, int, int] = (255, 80, 80)

# --- Spell tier colors (particle / projectile tints per spell level) ---
# Fireball I–V
FIREBALL_1_COLOR: Tuple[int, int, int] = (255, 120, 30)
FIREBALL_2_COLOR: Tuple[int, int, int] = (255, 140, 40)
FIREBALL_3_COLOR: Tuple[int, int, int] = (255, 160, 50)
FIREBALL_4_COLOR: Tuple[int, int, int] = (255, 180, 60)
FIREBALL_5_COLOR: Tuple[int, int, int] = (255, 200, 80)
# Heal I–V
HEAL_1_COLOR: Tuple[int, int, int] = (80, 255, 80)
HEAL_2_COLOR: Tuple[int, int, int] = (100, 255, 100)
HEAL_3_COLOR: Tuple[int, int, int] = (120, 255, 120)
HEAL_4_COLOR: Tuple[int, int, int] = (140, 255, 140)
HEAL_5_COLOR: Tuple[int, int, int] = (160, 255, 160)
# Lightning I–V
LIGHTNING_1_COLOR: Tuple[int, int, int] = (180, 200, 255)
LIGHTNING_2_COLOR: Tuple[int, int, int] = (200, 215, 255)
LIGHTNING_3_COLOR: Tuple[int, int, int] = (220, 230, 255)
LIGHTNING_4_COLOR: Tuple[int, int, int] = (235, 240, 255)
LIGHTNING_5_COLOR: Tuple[int, int, int] = (245, 248, 255)
# Ice Shard I–V
ICE_1_COLOR: Tuple[int, int, int] = (100, 200, 255)
ICE_2_COLOR: Tuple[int, int, int] = (120, 215, 255)
ICE_3_COLOR: Tuple[int, int, int] = (140, 225, 255)
ICE_4_COLOR: Tuple[int, int, int] = (160, 235, 255)
ICE_5_COLOR: Tuple[int, int, int] = (180, 245, 255)
# Strength I–V
STRENGTH_1_COLOR: Tuple[int, int, int] = (255, 100, 80)
STRENGTH_2_COLOR: Tuple[int, int, int] = (255, 120, 100)
STRENGTH_3_COLOR: Tuple[int, int, int] = (255, 140, 120)
STRENGTH_4_COLOR: Tuple[int, int, int] = (255, 160, 140)
STRENGTH_5_COLOR: Tuple[int, int, int] = (255, 180, 160)
# Regen I–V
REGEN_1_COLOR: Tuple[int, int, int] = (80, 255, 140)
REGEN_2_COLOR: Tuple[int, int, int] = (100, 255, 160)
REGEN_3_COLOR: Tuple[int, int, int] = (120, 255, 180)
REGEN_4_COLOR: Tuple[int, int, int] = (140, 255, 200)
REGEN_5_COLOR: Tuple[int, int, int] = (160, 255, 220)
# Protection I–V
PROTECTION_1_COLOR: Tuple[int, int, int] = (100, 180, 255)
PROTECTION_2_COLOR: Tuple[int, int, int] = (120, 200, 255)
PROTECTION_3_COLOR: Tuple[int, int, int] = (140, 220, 255)
PROTECTION_4_COLOR: Tuple[int, int, int] = (160, 235, 255)
PROTECTION_5_COLOR: Tuple[int, int, int] = (180, 245, 255)

# --- Mob body colors ---
MOB_COLOR_SLIME: Tuple[int, int, int] = (50, 200, 70)
MOB_COLOR_SKELETON: Tuple[int, int, int] = (200, 200, 210)
MOB_COLOR_WOLF: Tuple[int, int, int] = (100, 100, 100)
MOB_COLOR_GOBLIN: Tuple[int, int, int] = (80, 140, 60)
MOB_COLOR_GHOST: Tuple[int, int, int] = (180, 180, 220)
MOB_COLOR_SPIDER: Tuple[int, int, int] = (60, 40, 30)
MOB_COLOR_ORC: Tuple[int, int, int] = (80, 100, 50)
MOB_COLOR_DARK_KNIGHT: Tuple[int, int, int] = (40, 40, 50)
MOB_COLOR_ZOMBIE: Tuple[int, int, int] = (100, 140, 80)
MOB_COLOR_WRAITH: Tuple[int, int, int] = (140, 80, 180)
MOB_COLOR_TROLL: Tuple[int, int, int] = (80, 120, 60)
MOB_COLOR_SKELETON_ARCHER: Tuple[int, int, int] = (200, 200, 210)
MOB_COLOR_GOBLIN_SHAMAN: Tuple[int, int, int] = (100, 60, 160)
MOB_COLOR_BOSS_GOLEM: Tuple[int, int, int] = (180, 80, 60)
MOB_COLOR_BOSS_LICH: Tuple[int, int, int] = (120, 60, 180)

# --- Boss glow colors ---
BOSS_GLOW_GOLEM: Tuple[int, int, int] = (255, 60, 60)
BOSS_GLOW_LICH: Tuple[int, int, int] = (200, 60, 255)
BOSS_GLOW_DRAGON: Tuple[int, int, int] = (255, 140, 30)
BOSS_GLOW_NECROMANCER: Tuple[int, int, int] = (80, 255, 80)
BOSS_GLOW_TROLL_KING: Tuple[int, int, int] = (100, 180, 60)
BOSS_GLOW_DEFAULT: Tuple[int, int, int] = (255, 60, 60)
# Built from the individual boss glow constants above.
BOSS_GLOW_COLORS: Dict[str, Tuple[int, int, int]] = {
    'boss_golem':       BOSS_GLOW_GOLEM,
    'boss_lich':        BOSS_GLOW_LICH,
    'boss_dragon':      BOSS_GLOW_DRAGON,
    'boss_necromancer': BOSS_GLOW_NECROMANCER,
    'boss_troll_king':  BOSS_GLOW_TROLL_KING,
}

# --- Light source colors ---
LIGHT_COLOR_DEFAULT: Tuple[int, int, int] = (255, 200, 120)
LIGHT_COLOR_CAMPFIRE: Tuple[int, int, int] = (255, 160, 80)
LIGHT_COLOR_TORCH: Tuple[int, int, int] = (255, 180, 60)
LIGHT_COLOR_FIRE_ENCHANT: Tuple[int, int, int] = (255, 120, 30)

# --- Day period indicator colors ---
PERIOD_COLOR_DAY: Tuple[int, int, int] = (255, 255, 200)
PERIOD_COLOR_DAWN: Tuple[int, int, int] = (255, 200, 140)
PERIOD_COLOR_DUSK: Tuple[int, int, int] = (200, 140, 180)
PERIOD_COLOR_NIGHT: Tuple[int, int, int] = (140, 140, 220)

# --- Particle effect colors ---
PARTICLE_COLOR_FIRE: Tuple[int, int, int] = (255, 120, 30)
PARTICLE_COLOR_ICE: Tuple[int, int, int] = (100, 200, 255)
PARTICLE_COLOR_LIGHTNING_ARC: Tuple[int, int, int] = (180, 200, 255)
PARTICLE_COLOR_ICE_SLOW: Tuple[int, int, int] = (140, 140, 220)
PARTICLE_COLOR_TREE: Tuple[int, int, int] = (80, 50, 30)

# --- Bomb color ---
BOMB_COLOR: Tuple[int, int, int] = (255, 160, 40)

# --- Placement preview colors ---
PLACEMENT_PREVIEW_COLOR: Tuple[int, int, int, int] = (60, 220, 80, 120)
PLACEMENT_INVALID_COLOR: Tuple[int, int, int, int] = (220, 60, 60, 120)
PLACEMENT_UPGRADE_PREVIEW_COLOR: Tuple[int, int, int, int] = (255, 200, 60, 120)
PLACEMENT_VALID_BORDER: Tuple[int, int, int] = (60, 220, 80)
PLACEMENT_INVALID_BORDER: Tuple[int, int, int] = (220, 60, 60)

# --- Health bar colors ---
MOB_HP_BAR_BG: Tuple[int, int, int] = (40, 10, 10)
MOB_HP_BAR_FILL: Tuple[int, int, int] = (220, 40, 40)
PLACEABLE_HP_BAR_BG: Tuple[int, int, int] = (40, 30, 10)
PLACEABLE_HP_BAR_FILL: Tuple[int, int, int] = (200, 160, 40)

# --- Minimap tile colors ---
MINIMAP_COLOR_WATER: Tuple[int, int, int] = (30, 80, 180)
MINIMAP_COLOR_SAND: Tuple[int, int, int] = (210, 190, 140)
MINIMAP_COLOR_GRASS: Tuple[int, int, int] = (45, 120, 50)
MINIMAP_COLOR_DIRT: Tuple[int, int, int] = (100, 75, 45)
MINIMAP_COLOR_STONE_FLOOR: Tuple[int, int, int] = (110, 110, 120)
MINIMAP_COLOR_STONE_WALL: Tuple[int, int, int] = (55, 55, 65)
MINIMAP_COLOR_FOREST: Tuple[int, int, int] = (25, 80, 30)
MINIMAP_COLOR_CAVE_FLOOR: Tuple[int, int, int] = (60, 55, 50)
MINIMAP_COLOR_CAVE_ENTRANCE: Tuple[int, int, int] = (180, 180, 200)
MINIMAP_COLOR_PLAYER: Tuple[int, int, int] = (200, 160, 60)
MINIMAP_SIZE_PX: int = 160

# --- UI theme colors ---
UI_BG_MAIN_MENU: Tuple[int, int, int] = (15, 15, 30)
UI_BG_PANEL: Tuple[int, int, int, int] = (25, 25, 40, 230)
UI_BG_PANEL_DARK: Tuple[int, int, int, int] = (10, 10, 20, 150)
UI_BG_BUTTON_NORMAL: Tuple[int, int, int] = (30, 30, 50)
UI_BG_BUTTON_HOVER: Tuple[int, int, int] = (50, 50, 75)
UI_BG_BUTTON_SELECTED: Tuple[int, int, int] = (80, 80, 120)
UI_BORDER_NORMAL: Tuple[int, int, int] = (100, 100, 130)
UI_BORDER_PANEL: Tuple[int, int, int] = (140, 140, 170)
UI_BORDER_LIGHT: Tuple[int, int, int] = (130, 130, 155)
UI_BORDER_DIALOG: Tuple[int, int, int] = (160, 160, 200)
UI_BORDER_BUTTON: Tuple[int, int, int] = (160, 160, 180)
UI_TEXT_NORMAL: Tuple[int, int, int] = (200, 200, 220)
UI_TEXT_MUTED: Tuple[int, int, int] = (130, 130, 160)
UI_TEXT_HIGHLIGHT: Tuple[int, int, int] = (200, 200, 240)
UI_NOTIFICATION_TEXT: Tuple[int, int, int] = (220, 220, 240)

# --- UI slot colors (inventory/pause/chest grids) ---
UI_SLOT_BG_NORMAL: Tuple[int, int, int] = (45, 45, 60)
UI_SLOT_BG_SELECTED: Tuple[int, int, int] = (80, 80, 110)
UI_SLOT_BG_HOVER: Tuple[int, int, int] = (70, 70, 95)
UI_SLOT_BORDER_NORMAL: Tuple[int, int, int] = (100, 100, 120)
UI_SLOT_SEPARATOR: Tuple[int, int, int] = (80, 80, 100)
UI_NAV_HOVER: Tuple[int, int, int] = (70, 70, 100)
UI_NAV_NORMAL: Tuple[int, int, int] = (50, 50, 70)
UI_SAVE_SLOT_SELECTED: Tuple[int, int, int] = (70, 70, 110)
UI_SPLIT_BUTTON_NORMAL: Tuple[int, int, int] = (55, 55, 75)

# --- UI action button colors ---
UI_CONFIRM_BUTTON: Tuple[int, int, int] = (60, 120, 60)
UI_CANCEL_BUTTON: Tuple[int, int, int] = (120, 60, 60)
UI_STAT_BUTTON_HOVER: Tuple[int, int, int] = (70, 110, 70)
UI_STAT_BUTTON_NORMAL: Tuple[int, int, int] = (50, 80, 50)
UI_UNEQUIP_HOVER: Tuple[int, int, int] = (110, 50, 50)
UI_UNEQUIP_NORMAL: Tuple[int, int, int] = (80, 40, 40)
UI_EQUIP_HOVER: Tuple[int, int, int] = (50, 80, 50)
UI_EQUIP_NORMAL: Tuple[int, int, int] = (40, 60, 40)
UI_DROPDOWN_HOVER: Tuple[int, int, int] = (55, 65, 95)
UI_DROPDOWN_NORMAL: Tuple[int, int, int] = (35, 35, 55)

# --- Crafting panel colors ---
UI_CRAFT_CAN_NORMAL: Tuple[int, int, int] = (60, 90, 60)
UI_CRAFT_CAN_HOVER: Tuple[int, int, int] = (80, 120, 80)
UI_CRAFT_CAN_BORDER: Tuple[int, int, int] = (100, 180, 100)
UI_CRAFT_CANNOT_NORMAL: Tuple[int, int, int] = (55, 35, 35)
UI_CRAFT_CANNOT_HOVER: Tuple[int, int, int] = (75, 50, 50)
UI_CRAFT_CANNOT_BORDER: Tuple[int, int, int] = (140, 60, 60)

# --- Progress bar defaults ---
UI_PROGRESS_FG: Tuple[int, int, int] = (200, 60, 60)
UI_PROGRESS_BG: Tuple[int, int, int] = (40, 20, 20)

# --- Drop confirm dialog ---
UI_DROP_DIALOG_BG: Tuple[int, int, int, int] = (30, 10, 10, 240)
UI_DROP_DIALOG_BORDER: Tuple[int, int, int] = (200, 60, 60)
UI_DROP_YES_BUTTON: Tuple[int, int, int] = (140, 40, 40)
UI_DROP_NO_BUTTON: Tuple[int, int, int] = (50, 80, 50)

# --- Chest UI ---
UI_CHEST_PANEL_BG: Tuple[int, int, int, int] = (20, 20, 35, 240)
UI_CHEST_SLOT_BG_NORMAL: Tuple[int, int, int] = (50, 50, 65)
UI_CHEST_SLOT_BG_HOVER: Tuple[int, int, int] = (70, 70, 95)
UI_CHEST_SORT_HOVER: Tuple[int, int, int] = (70, 100, 70)
UI_CHEST_SORT_NORMAL: Tuple[int, int, int] = (50, 70, 50)
UI_CHEST_SORT_BORDER: Tuple[int, int, int] = (100, 160, 100)
UI_CHEST_MOVE_HOVER: Tuple[int, int, int] = (100, 70, 70)
UI_CHEST_MOVE_NORMAL: Tuple[int, int, int] = (70, 50, 50)
UI_CHEST_MOVE_BORDER: Tuple[int, int, int] = (160, 100, 100)

# --- Enchantment table UI ---
UI_ENCHANT_PANEL_BG: Tuple[int, int, int, int] = (20, 15, 30, 240)
UI_ENCHANT_PANEL_BORDER: Tuple[int, int, int] = (140, 100, 170)
UI_ENCHANT_SLOT_BG_NORMAL: Tuple[int, int, int] = (40, 30, 55)
UI_ENCHANT_SLOT_BG_HOVER: Tuple[int, int, int] = (60, 45, 80)
UI_ENCHANT_SLOT_BORDER: Tuple[int, int, int] = (120, 80, 160)
UI_ENCHANT_COMBINE_ACTIVE: Tuple[int, int, int] = (55, 95, 55)
UI_ENCHANT_COMBINE_ACTIVE_HOVER: Tuple[int, int, int] = (75, 130, 75)
UI_ENCHANT_COMBINE_ACTIVE_BORDER: Tuple[int, int, int] = (100, 200, 100)
UI_ENCHANT_COMBINE_INACTIVE: Tuple[int, int, int] = (40, 40, 50)
UI_ENCHANT_COMBINE_INACTIVE_BORDER: Tuple[int, int, int] = (75, 75, 90)
UI_ENCHANT_DIVIDER: Tuple[int, int, int] = (120, 80, 150)

# --- Enchant/enhancement color fallback (for unknown levels) ---
UI_ENCHANT_FALLBACK: Tuple[int, int, int] = (200, 200, 200)

# --- Death screen ---
DEATH_BUTTON_HOVER: Tuple[int, int, int] = (60, 60, 90)
DEATH_BUTTON_NORMAL: Tuple[int, int, int] = (40, 40, 60)

# --- HUD status area ---
HUD_STATUS_TEXT: Tuple[int, int, int] = (180, 210, 255)
HUD_RESOURCE_TEXT: Tuple[int, int, int] = (200, 200, 210)

# --- Spell targeting ---
SPELL_HELP_TEXT: Tuple[int, int, int] = (255, 180, 80)

# --- Placement borders (non-alpha versions) ---
PLACEMENT_UPGRADE_BORDER: Tuple[int, int, int] = (255, 200, 60)

# --- Hotbar colors ---
HOTBAR_BG: Tuple[int, int, int, int] = (15, 15, 25, 180)
HOTBAR_BORDER: Tuple[int, int, int] = (100, 100, 130)
HOTBAR_SLOT_SELECTED_BG: Tuple[int, int, int] = (80, 80, 115)
HOTBAR_SLOT_NORMAL_BG: Tuple[int, int, int] = (30, 30, 48)
HOTBAR_SELECTED_BORDER: Tuple[int, int, int] = (200, 200, 240)
HOTBAR_NORMAL_BORDER: Tuple[int, int, int] = (90, 90, 110)
HOTBAR_SLOT_NUMBER_COLOR: Tuple[int, int, int] = (170, 170, 190)

# --- Overlay / HUD colors ---
DARKNESS_OVERLAY_TINT: Tuple[int, int, int] = (5, 5, 20)
SLEEP_OVERLAY_BG: Tuple[int, int, int, int] = (0, 0, 30, 140)
DEATH_SCREEN_OVERLAY: Tuple[int, int, int, int] = (0, 0, 0, 180)
SPELL_COOLDOWN_OVERLAY: Tuple[int, int, int, int] = (40, 40, 40, 160)
SPELL_TARGET_RETICLE: Tuple[int, int, int] = (255, 120, 30)

# --- Options menu colors ---
OPTIONS_BG: Tuple[int, int, int, int] = (20, 20, 35, 240)
OPTIONS_BORDER: Tuple[int, int, int] = (140, 140, 170)
OPTIONS_BACK_HOVER: Tuple[int, int, int] = (60, 70, 100)
OPTIONS_BACK_NORMAL: Tuple[int, int, int] = (40, 45, 65)
OPTIONS_BACK_BORDER: Tuple[int, int, int] = (130, 130, 160)
OPTIONS_INFO_TEXT: Tuple[int, int, int] = (160, 160, 190)
VOLUME_SLIDER_BG: Tuple[int, int, int] = (30, 30, 50)
VOLUME_SLIDER_FILL: Tuple[int, int, int] = (70, 160, 255)

# --- HUD notification colors ---
HUD_DUSK_WARNING: Tuple[int, int, int] = (255, 200, 80)
HUD_WORLD_EDGE_WARNING: Tuple[int, int, int] = (170, 170, 200)
HUD_CONTROL_HINT: Tuple[int, int, int] = (130, 130, 150)
HUD_BED_PROMPT_BG: Tuple[int, int, int, int] = (10, 10, 30, 160)
HUD_BED_PROMPT_TEXT: Tuple[int, int, int] = (180, 180, 255)
HUD_REPAIR_DAMAGED_BG: Tuple[int, int, int, int] = (10, 30, 10, 160)
HUD_REPAIR_DAMAGED_TEXT: Tuple[int, int, int] = (180, 255, 180)
HUD_REPAIR_NORMAL_BG: Tuple[int, int, int, int] = (20, 20, 20, 160)
HUD_REPAIR_NORMAL_TEXT: Tuple[int, int, int] = (200, 200, 200)
HUD_HP_BAR_FG: Tuple[int, int, int] = (210, 50, 50)
HUD_HP_BAR_BG: Tuple[int, int, int] = (40, 15, 15)
HUD_XP_BAR_FG: Tuple[int, int, int] = (70, 160, 255)
HUD_XP_BAR_BG: Tuple[int, int, int] = (20, 30, 50)

# --- Attack arc / Stone wall visual ---
ATTACK_ARC_COLOR: Tuple[int, int, int] = (255, 255, 200)
STONE_WALL_OVERLAY: Tuple[int, int, int] = (50, 50, 60)
STONE_WALL_BORDER: Tuple[int, int, int] = (30, 30, 40)


# ######################################################################
#                        WORLD GENERATION
# ######################################################################
WORLD_WIDTH: int = 200
WORLD_HEIGHT: int = 150
ELEVATION_SCALE: float = 0.045
MOISTURE_SCALE: float = 0.06
MOISTURE_OFFSET: float = 500.0
ELEVATION_OCTAVES: int = 6
MOISTURE_OCTAVES: int = 4

# --- Tile types ---
TILE_WATER: int = 0
TILE_SAND: int = 1
TILE_GRASS: int = 2
TILE_DIRT: int = 3
TILE_STONE_FLOOR: int = 4
TILE_STONE_WALL: int = 5
TILE_FOREST: int = 6
TILE_CAVE_FLOOR: int = 7
TILE_CAVE_ENTRANCE: int = 8

# --- Resource population counts ---
TREE_COUNT: int = 350
FOREST_TREE_COUNT: int = 150
ROCK_COUNT: int = 200

# --- Cave generation ---
CAVE_COUNT: int = 3
CAVE_WIDTH: int = 60
CAVE_HEIGHT: int = 45
CAVE_WALL_DENSITY: float = 0.48
CAVE_SMOOTH_PASSES: int = 5
CAVE_MOB_TYPES: Tuple[str, ...] = ('skeleton', 'orc', 'dark_knight', 'troll', 'ghost', 'wraith')
CAVE_MOB_COUNT: int = 15
CAVE_BOSS_TYPES: Tuple[str, ...] = (
    'boss_golem', 'boss_lich', 'boss_dragon', 'boss_necromancer', 'boss_troll_king',
)
CAVE_ORE_COUNT: int = 8
CAVE_DIAMOND_COUNT: int = 3
CAVE_HP_MULT: float = 1.5
CAVE_DMG_MULT: float = 1.3
CAVE_ENTRANCE_MIN_DIST: float = 800.0


# ######################################################################
#                        DAY / NIGHT CONTROLS
# ######################################################################
# All times-of-day are expressed as (hour, minute) tuples in 24-hour format.
# To change when something happens, just set the time — e.g. (5, 0) = 05:00.
# The engine-facing 0.0–1.0 fractions are auto-derived below each tuple.

# --- Cycle length ---
DAY_LENGTH_BASE: float = 960.0           # real seconds for 1 full in-game day (16 min)
TIME_SPEED_NORMAL: float = 1.0           # normal time speed multiplier

# --- Sleep / Rest ---
SLEEP_DURATION: float = 5.0              # real seconds the sleep overlay lasts
SLEEP_SPEED_MULT: float = 12.0           # time passes 12x faster while sleeping
BED_INTERACT_RANGE: float = 50.0         # pixel range to interact with a bed

# --- Period schedule (24-hour clock) ---
# The day is divided into five periods that repeat every cycle:
#   Night  → 00:00 to DAWN_BEGINS
#   Dawn   → DAWN_BEGINS to DAY_BEGINS
#   Day    → DAY_BEGINS to DUSK_BEGINS
#   Dusk   → DUSK_BEGINS to NIGHT_BEGINS
#   Night  → NIGHT_BEGINS to 24:00 (wraps to 00:00)
#
# Set each as (hour, minute).  The engine fractions (TIME_*) are computed
# automatically — never edit them directly; change the (h, m) tuples instead.

DAWN_BEGINS: Tuple[int, int]  = (5, 17)    # 05:17 — night ends, dawn begins
DAY_BEGINS: Tuple[int, int]   = (7, 12)    # 07:12 — dawn ends, day begins
DUSK_BEGINS: Tuple[int, int]  = (16, 48)   # 16:48 — day ends, dusk begins
NIGHT_BEGINS: Tuple[int, int] = (18, 43)   # 18:43 — dusk ends, night begins

# Engine fractions (auto-derived — do not edit these directly)
TIME_NIGHT_END: float   = (DAWN_BEGINS[0] * 60 + DAWN_BEGINS[1]) / 1440.0
TIME_DAY_START: float   = (DAY_BEGINS[0] * 60 + DAY_BEGINS[1]) / 1440.0
TIME_DAY_END: float     = (DUSK_BEGINS[0] * 60 + DUSK_BEGINS[1]) / 1440.0
TIME_NIGHT_START: float = (NIGHT_BEGINS[0] * 60 + NIGHT_BEGINS[1]) / 1440.0

# --- Period transition messages ---
# Each period transition shows a banner on screen.
#   *_TEXT      — message text ("" = no banner for that transition)
#   *_DURATION  — real seconds the banner stays visible
#   *_FADE_DIVISOR — controls fade speed: alpha = timer / divisor (lower = slower)
#   *_COLOR     — text colour of the banner
#
# The time each message appears is the period threshold above.

# "Day X" banner — appears at DAY_BEGINS (07:12), lasts 3.0 seconds
DAY_FLASH_DURATION: float = 3.0
DAY_FLASH_FADE_DIVISOR: float = 1.0
DAY_FLASH_TEXT: str = "Day {day}"
DAY_FLASH_COLOR: Tuple[int, int, int] = (255, 255, 200)

# "Night falls — Defend!" — appears at NIGHT_BEGINS (18:43), lasts 2.5 seconds
NIGHT_FLASH_DURATION: float = 2.5
NIGHT_FLASH_FADE_DIVISOR: float = 0.8
NIGHT_FLASH_TEXT: str = "Night falls \u2014 Defend!"
NIGHT_FLASH_COLOR: Tuple[int, int, int] = (255, 120, 80)

# Dawn banner — appears at DAWN_BEGINS (05:17), lasts 2.0 seconds
DAWN_FLASH_DURATION: float = 2.0
DAWN_FLASH_TEXT: str = ""               # empty = no banner at dawn
DAWN_FLASH_COLOR: Tuple[int, int, int] = (255, 220, 150)

# "Dusk approaches..." — appears at DUSK_BEGINS (16:48), lasts 2.0 seconds
DUSK_FLASH_DURATION: float = 2.0
DUSK_FLASH_TEXT: str = "Dusk approaches..."
DUSK_FLASH_COLOR: Tuple[int, int, int] = (255, 180, 100)

# Sleeping overlay text (shown during sleep animation)
SLEEP_OVERLAY_TEXT: str = "Sleeping... Zzz"
SLEEP_OVERLAY_COLOR: Tuple[int, int, int] = (180, 180, 255)

# --- Darkness visual threshold ---
# get_darkness() returns 0.0 (full day) to 1.0+ (deep night).
# Night damage only applies when darkness exceeds this value.
NIGHT_DARKNESS_THRESHOLD: float = 0.5

# --- Night damage (base values — scaled by difficulty, see DIFFICULTY_PROFILES) ---
NIGHT_DAMAGE_BASE: int = 2               # HP per tick on day 1
NIGHT_DAMAGE_INCREASE: int = 1           # extra HP added per scaling step
NIGHT_DAMAGE_INCREASE_FREQ: int = 1      # add INCREASE every N days
NIGHT_DAMAGE_INTERVAL: float = 3.0       # real seconds between damage ticks
LIGHT_SAFETY_RADIUS: float = 200.0       # pixel radius around light sources that protects

# --- Backwards compat alias ---
NIGHT_SLEEP_SPEED_MULT: float = SLEEP_SPEED_MULT


# ######################################################################
#                        DAY EVENT CONTROLS
# ######################################################################
# --- Wave system (night-time enemy waves) ---
WAVE_START_NIGHT: int = 1                # waves begin after surviving this many nights
WAVE_BASE_COUNT: int = 3                 # mobs in the first qualifying wave
WAVE_SCALE_PER_NIGHT: int = 2            # extra mobs per night survived
WAVE_SPAWN_RADIUS: float = 350.0         # px from player where wave mobs spawn
WAVE_SPAWN_RADIUS_VARIANCE: float = 100.0  # random ± on spawn radius
WAVE_DAY_BONUS_PER_DAY: int = 1          # extra mobs per calendar day on top of night count
WAVE_SPAWN_INITIAL_INTERVAL: float = 2.0 # seconds between batches at wave start
WAVE_SPAWN_MIN_INTERVAL: float = 0.8     # fastest possible batch interval
WAVE_INTERVAL_REDUCTION: float = 0.1     # seconds shaved off interval per qualifying night
WAVE_SPAWN_BATCH: int = 3                # mobs spawned per batch tick
WAVE_RANGED_MOB_CHANCE: float = 0.25     # chance a wave mob is ranged (after RANGED_ENEMY_START_DAY)

# --- Mob respawn / population ---
MOB_RESPAWN_INTERVAL: float = 4.0        # seconds between natural respawn ticks
MOB_RESPAWN_MIN_DIST: float = 300.0      # min px from player for a new mob to spawn
MOB_MAX_COUNT: int = 80                  # hard cap on total mobs alive at once
MOB_RESPAWN_BATCH: int = 3               # mobs per respawn tick

# --- Day-based enemy progression ---
RANGED_ENEMY_START_DAY: int = 3           # ranged enemies appear after this day
PER_DAY_SCALE_FACTOR: float = 0.05       # mob stats *= (1 + day * this)

# --- Overworld spawn chances (per spawn-attempt roll) ---
MOB_SPAWN_ATTEMPTS: int = 20             # random attempts per tick
GRASS_MOB_SPAWN_CHANCE: float = 0.4
FOREST_MOB_SPAWN_CHANCE: float = 0.5
DIRT_MOB_SPAWN_CHANCE: float = 0.4
ORC_SPAWN_CHANCE: float = 0.2            # chance for orc on dirt instead of generic
GHOST_SPAWN_CHANCE: float = 0.25         # chance for ghost at night
DARK_KNIGHT_SPAWN_CHANCE: float = 0.15   # chance for dark knight at night
NIGHT_MOB_SPAWN_CHANCE: float = 0.4      # chance for any night-specific spawn

# --- Initial mob population (spawned once at world generation) ---
# Each tuple: (mob_type, required_tile_type, count)
INITIAL_MOB_SPAWNS: List[Tuple[str, int, int]] = [
    ('slime',  2, 25),    # TILE_GRASS  = 2
    ('wolf',   6, 10),    # TILE_FOREST = 6
    ('spider', 6,  8),    # TILE_FOREST = 6
    ('goblin', 3,  5),    # TILE_DIRT   = 3
]

# --- Resource respawn (overworld trees/rocks) ---
# Days between overworld resource replenishment, per difficulty.
# 0 = resources never respawn (Hardcore).
RESOURCE_RESPAWN_DAYS: Dict[int, int] = {
    0: 3,     # Easy     — every 3 days
    1: 7,     # Normal   — every 7 days
    2: 14,    # Hard     — every 14 days
    3: 0,     # Hardcore  — never
}

# --- Cave reset interval ---
# Days between automatic cave regeneration, per difficulty.
# 1 = caves rebuild every day (current default).
# 0 = caves never regenerate (one-time clear).
CAVE_RESET_DAYS: Dict[int, int] = {
    0: 1,     # Easy     — every day
    1: 1,     # Normal   — every day
    2: 2,     # Hard     — every 2 days
    3: 3,     # Hardcore  — every 3 days
}


# ######################################################################
#                        DIFFICULTY CONTROLS
# ######################################################################
DIFFICULTY_EASY: int = 0
DIFFICULTY_NORMAL: int = 1
DIFFICULTY_HARD: int = 2
DIFFICULTY_HARDCORE: int = 3
DIFFICULTY_NAMES: Tuple[str, ...] = ("Easy", "Normal", "Hard", "Hardcore")

# --- Difficulty profiles — per-difficulty multipliers and scaling ---
# All difficulty-sensitive systems read from these profiles.
# Keys:
#   enemy_hp_mult       — multiplier on mob base HP
#   enemy_dmg_mult      — multiplier on mob base damage (contact + ranged)
#   enemy_hp_per_day    — additional HP% gained per day  (mob HP *= 1 + day * this)
#   enemy_dmg_per_day   — additional DMG% gained per day (mob DMG *= 1 + day * this)
#   boss_hp_mult        — extra multiplier on boss HP (stacks with enemy_hp_mult)
#   boss_dmg_mult       — extra multiplier on boss damage
#   boss_hp_per_day     — additional boss HP% gained per day (on top of enemy growth)
#   boss_dmg_per_day    — additional boss DMG% gained per day
#   spawn_rate_mult     — multiplier on mob respawn frequency (higher = faster)
#   wave_count_mult     — multiplier on night wave mob count
#   night_dmg_mult      — multiplier on night darkness damage
#   night_dmg_per_day   — extra night damage added per day (flat, applied after mult)
#   night_dmg_tick_min  — minimum damage per night tick (floor)
#   night_dmg_tick_max  — maximum damage per night tick (0 = no cap)
#   xp_mult             — multiplier on XP earned
#   loot_luck_bonus     — flat bonus added to rarity roll weights for better tier

DIFFICULTY_PROFILES: Dict[int, Dict[str, float]] = {
    0: {  # Easy
        'enemy_hp_mult':    1.0,
        'enemy_dmg_mult':   1.0,
        'enemy_hp_per_day': 0.03,    # +3% HP per day
        'enemy_dmg_per_day': 0.02,   # +2% DMG per day
        'boss_hp_mult':     1.0,
        'boss_dmg_mult':    1.0,
        'boss_hp_per_day':  0.02,    # +2% boss HP per day (stacks with enemy growth)
        'boss_dmg_per_day': 0.01,    # +1% boss DMG per day
        'spawn_rate_mult':  1.0,
        'wave_count_mult':  1.0,
        'night_dmg_mult':   1.0,
        'night_dmg_per_day': 0.0,    # no extra night dmg per day
        'night_dmg_tick_min': 1,     # minimum 1 dmg per tick
        'night_dmg_tick_max': 0,     # 0 = no cap
        'xp_mult':          1.0,
        'loot_luck_bonus':  0.0,
    },
    1: {  # Normal
        'enemy_hp_mult':    1.3,
        'enemy_dmg_mult':   1.3,
        'enemy_hp_per_day': 0.05,    # +5% HP per day (matches PER_DAY_SCALE_FACTOR)
        'enemy_dmg_per_day': 0.05,   # +5% DMG per day
        'boss_hp_mult':     1.0,
        'boss_dmg_mult':    1.0,
        'boss_hp_per_day':  0.04,    # +4% boss HP per day
        'boss_dmg_per_day': 0.03,    # +3% boss DMG per day
        'spawn_rate_mult':  1.2,
        'wave_count_mult':  1.3,
        'night_dmg_mult':   1.0,
        'night_dmg_per_day': 0.5,    # +0.5 flat night dmg per day
        'night_dmg_tick_min': 1,
        'night_dmg_tick_max': 0,
        'xp_mult':          1.0,
        'loot_luck_bonus':  0.0,
    },
    2: {  # Hard
        'enemy_hp_mult':    1.8,
        'enemy_dmg_mult':   1.8,
        'enemy_hp_per_day': 0.08,    # +8% HP per day
        'enemy_dmg_per_day': 0.08,   # +8% DMG per day
        'boss_hp_mult':     1.3,
        'boss_dmg_mult':    1.2,
        'boss_hp_per_day':  0.06,    # +6% boss HP per day
        'boss_dmg_per_day': 0.05,    # +5% boss DMG per day
        'spawn_rate_mult':  1.5,
        'wave_count_mult':  1.8,
        'night_dmg_mult':   1.5,
        'night_dmg_per_day': 1.0,    # +1 flat night dmg per day
        'night_dmg_tick_min': 2,
        'night_dmg_tick_max': 0,
        'xp_mult':          1.2,
        'loot_luck_bonus':  0.0,
    },
    3: {  # Hardcore
        'enemy_hp_mult':    3.5,
        'enemy_dmg_mult':   3.0,
        'enemy_hp_per_day': 0.12,    # +12% HP per day
        'enemy_dmg_per_day': 0.10,   # +10% DMG per day
        'boss_hp_mult':     2.0,
        'boss_dmg_mult':    1.5,
        'boss_hp_per_day':  0.10,    # +10% boss HP per day
        'boss_dmg_per_day': 0.08,    # +8% boss DMG per day
        'spawn_rate_mult':  4.0,
        'wave_count_mult':  4.0,
        'night_dmg_mult':   2.0,
        'night_dmg_per_day': 2.0,    # +2 flat night dmg per day
        'night_dmg_tick_min': 5,
        'night_dmg_tick_max': 0,
        'xp_mult':          1.5,
        'loot_luck_bonus':  0.0,
    },
}


# ######################################################################
#                        PLAYER CONTROLS
# ######################################################################
# --- Base stats ---
PLAYER_BASE_SPEED: float = 100.0
PLAYER_FRICTION: float = 0.82
PLAYER_COLLIDER_W: int = 20
PLAYER_COLLIDER_H: int = 28
PLAYER_TORCH_LIGHT_RADIUS: int = 110
STARTING_WOOD: int = 5
STARTING_STONE: int = 3

# --- Stat points ---
STAT_POINTS_PER_LEVEL: int = 3

# --- Strength ---
STR_DAMAGE_MULT: int = 2
BASE_MELEE_DAMAGE: int = 5
BASE_MELEE_DAMAGE_MIN: int = 5
LEVEL_DAMAGE_MULT: int = 2

# --- Agility ---
AGI_SPEED_BONUS: float = 0.01
AGI_SPEED_BONUS_CAP: float = 1.0
MOVEMENT_ACCEL_MULT: int = 10
SPRITE_FLIP_THRESHOLD: float = 5.0
AGILITY_COOLDOWN_REDUCTION: float = 0.002
BASE_ATTACK_COOLDOWN: float = 0.30
MIN_ATTACK_COOLDOWN: float = 0.15
AGI_RANGED_SPEED_BONUS: float = 0.01
AGI_RANGED_SPEED_BONUS_CAP: float = 1.0
MIN_RANGED_COOLDOWN: float = 0.2
AGI_RANGED_DAMAGE_MULT: int = 2

# --- Vitality ---
LEVEL_UP_BASE_HP: int = 10
VIT_HP_BONUS_PER_LEVEL: int = 5
VITALITY_CAMPFIRE_BONUS_PER: int = 2

# --- Luck ---
CRIT_CHANCE_PER_LUCK: float = 0.01
CRIT_DAMAGE_MULT: float = 1.5
LUCK_HARVEST_CHANCE: float = 0.005


# ######################################################################
#                        COMBAT CONTROLS
# ######################################################################
# --- Melee ranges ---
SPEAR_ATTACK_RANGE: float = 65.0
WEAPON_ATTACK_RANGE: float = 55.0
UNARMED_ATTACK_RANGE: float = 38.0
MELEE_KNOCKBACK_FORCE: float = 200.0
ATTACK_ANIM_DURATION: float = 0.18

# --- Contact damage ---
CONTACT_DAMAGE_RADIUS: float = 28.0
PLAYER_HIT_INVULN: float = 0.5
DAMAGE_FLASH_DURATION: float = 0.15
HIT_SHAKE_AMOUNT: float = 4.0
HIT_SHAKE_DURATION: float = 0.2

# --- Projectiles ---
ENEMY_PROJ_HIT_RADIUS: float = 20.0
PROJ_SHAKE_AMOUNT: float = 3.0
PROJ_SHAKE_DURATION: float = 0.15
PROJ_MOB_HIT_RADIUS: float = 20.0

# --- Interaction ---
INTERACT_COOLDOWN: float = 0.25
INTERACT_RANGE: float = 50.0
HARVEST_RANGE: float = 50.0


# ######################################################################
#                        BUILDING / PLACEABLE CONTROLS
# ######################################################################
WALL_HP: int = 100
STONE_WALL_HP_MULT: float = 1.5
TURRET_HP: int = 80
TURRET_RANGE: float = 200.0
TURRET_DAMAGE: int = 8
TURRET_COOLDOWN: float = 1.5
CHEST_CAPACITY: int = 96
CHEST_HP_VALUE: int = 60
TRAP_HP: int = 40
BED_HP: int = 80
CAMPFIRE_HP: int = 60
ENCHANT_TABLE_CAPACITY: int = 9
ENCHANT_TABLE_HP: int = 60
DOOR_HP: int = 50
DOOR_COLLIDER_W: int = 24
DOOR_COLLIDER_H: int = 32

# --- Campfire healing ---
CAMPFIRE_BASE_HEAL: int = 3
CAMPFIRE_HEAL_RADIUS: float = 120.0
CAMPFIRE_HEAL_INTERVAL: float = 1.0

# --- Light radii ---
CAMPFIRE_LIGHT_RADIUS: int = 180
TORCH_LIGHT_RADIUS: int = 120
REPAIR_RANGE: float = 60.0


# ######################################################################
#                        INVENTORY / HOTBAR CONTROLS
# ######################################################################
HOTBAR_CAPACITY: int = 6
HOTBAR_SLOTS: int = 6
HOTBAR_SLOT_SIZE: int = 48
HOTBAR_SLOT_GAP: int = 6
INVENTORY_SLOTS_PER_PAGE: int = 24
INVENTORY_PAGES: int = 4
INVENTORY_COLS: int = 6
INVENTORY_TOTAL_SLOTS: int = 96


# ######################################################################
#                        SAVE / LOAD CONTROLS
# ######################################################################
SAVE_SLOTS: int = 4
QUICK_SAVE_SLOT: int = 0


# ######################################################################
#                        FONT CONTROLS
# ######################################################################
FONT_SIZE_MAIN: int = 16
FONT_SIZE_SM: int = 13
FONT_SIZE_LG: int = 22
FONT_SIZE_XL: int = 48


# ######################################################################
#                        HUD / NOTIFICATION CONTROLS
# ######################################################################
NOTIFICATION_DURATION: float = 2.5
HUD_REFRESH_INTERVAL: float = 0.5
DMG_NUMBER_FLOAT_SPEED: float = 40.0
MOB_HP_BAR_W: int = 28
MOB_HP_BAR_H: int = 4
PLACEABLE_HP_BAR_W: int = 28
PLACEABLE_HP_BAR_H: int = 3


# ######################################################################
#                        AI / MOB BEHAVIOR CONTROLS
# ######################################################################
AI_PROBE_STEP_MULT: float = 0.75
MOB_STRUCTURE_ATTACK_CD: float = 1.5
CHASE_DETECT_MULT: float = 0.7
WANDER_TIME_MIN: float = 1.5
WANDER_TIME_MAX: float = 3.5
CHASE_DISENGAGE_MULT: float = 2.0
AGGRO_DISENGAGE_MULT: float = 2.0
AGGRO_BOSS_DISENGAGE_MULT: float = 3.0
RANGED_MIN_DISTANCE: float = 60.0
RANGED_RETREAT_DISTANCE: float = 100.0
RANGED_RETREAT_SPEED_MULT: float = 0.5
RANGED_STRAFE_SPEED_MULT: float = 0.6
CHASE_MIN_DISTANCE: float = 5.0
CHASE_SPEED_MULT: float = 1.3
STUCK_WANTED_MULT: float = 0.3
STUCK_MIN_DISTANCE: float = 30.0
STUCK_TIME_THRESHOLD: float = 0.3

# --- System-level ---
VELOCITY_DEADZONE: float = 0.5
RENDER_CULL_MARGIN: int = 64

# --- Trap system ---
TRAP_TRIGGER_RADIUS: float = 24.0
TRAP_SELF_DAMAGE: int = 10
TRAP_DAMAGE: int = 15
TRAP_COOLDOWN: float = 1.5


# ######################################################################
#                        ENHANCEMENT CONTROLS
# ######################################################################
OFFENSE_BONUS_PER_LEVEL: int = 2
RANGED_OFFENSE_BONUS_PER_LEVEL: int = 2
DEFENSE_BONUS_PER_LEVEL: int = 2
TURRET_OFFENSE_BONUS_PER_LEVEL: int = 2
TURRET_DEFENSE_BONUS_PER_LEVEL: int = 2
PROTECTION_DR_PER_LEVEL: int = 2
# Built from the individual color constants above.
# PRESERVED for future use — currently no inner borders are drawn.
# ENHANCEMENT_COLORS: Dict[int, Tuple[int, int, int]] = {
#     1: ENHANCEMENT_COLOR_1,
#     2: ENHANCEMENT_COLOR_2,
#     3: ENHANCEMENT_COLOR_3,
#     4: ENHANCEMENT_COLOR_4,
#     5: ENHANCEMENT_COLOR_5,
# }

# --- Weapon base damages ---
WEAPON_BASE_IRON_SWORD: Tuple[int, int] = (30, 0)
WEAPON_BASE_IRON_AXE: Tuple[int, int] = (22, 4)
WEAPON_BASE_MACE: Tuple[int, int] = (26, 0)
WEAPON_BASES: Dict[str, Tuple[int, int]] = {
    'iron_sword': WEAPON_BASE_IRON_SWORD,
    'iron_axe':   WEAPON_BASE_IRON_AXE,
    'mace':       WEAPON_BASE_MACE,
}

# --- Ranged base damages ---
RANGED_BASE_BOW: int = 18
RANGED_BASE_CROSSBOW: int = 28
RANGED_BASE_SLING: int = 12
RANGED_BASES: Dict[str, int] = {
    'bow':      RANGED_BASE_BOW,
    'crossbow': RANGED_BASE_CROSSBOW,
    'sling':    RANGED_BASE_SLING,
}

# --- Armor base DR ---
ARMOR_BASE_IRON_ARMOR: int = 6
ARMOR_BASE_IRON_SHIELD: int = 4
ARMOR_BASES: Dict[str, int] = {
    'iron_armor':  ARMOR_BASE_IRON_ARMOR,
    'iron_shield': ARMOR_BASE_IRON_SHIELD,
}

# --- Turret base ---
TURRET_BASE_DAMAGE: int = 8
TURRET_BASE_HP: int = 80
TURRET_HP_TABLE: Dict[int, int] = {0: 80, 1: 96, 2: 112, 3: 136, 4: 160, 5: 192}


# ######################################################################
#                        ENCHANTMENT EFFECT CONTROLS
# ######################################################################
# --- Fire enchantment ---
FIRE_BONUS_DAMAGE: Dict[int, int] = {1: 5, 2: 10, 3: 18, 4: 28, 5: 40}
FIRE_LIGHT_RADIUS: Dict[int, int] = {1: 90, 2: 110, 3: 140, 4: 175, 5: 220}

# --- Ice enchantment ---
ICE_BONUS_DAMAGE: Dict[int, int] = {1: 3, 2: 7, 3: 12, 4: 19, 5: 28}
ICE_SLOW_FACTOR: Dict[int, float] = {1: 0.5, 2: 0.35, 3: 0.2, 4: 0.12, 5: 0.05}
ICE_SLOW_DURATION: Dict[int, float] = {1: 2.0, 2: 3.0, 3: 4.5, 4: 6.0, 5: 8.0}

# --- Lightning enchantment ---
LIGHTNING_BONUS_DAMAGE: Dict[int, int] = {1: 6, 2: 12, 3: 20, 4: 30, 5: 42}
LIGHTNING_ARC_RADIUS: Dict[int, float] = {1: 60.0, 2: 80.0, 3: 100.0, 4: 125.0, 5: 150.0}
LIGHTNING_ARC_DAMAGE_FRAC: Dict[int, float] = {1: 0.3, 2: 0.4, 3: 0.5, 4: 0.6, 5: 0.7}

# --- Buff enchantments ---
REGEN_HP_PER_SEC: Dict[int, int] = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
STRENGTH_BONUS_DAMAGE: Dict[int, int] = {1: 3, 2: 6, 3: 10, 4: 15, 5: 20}
ELEMENTAL_RESISTANCE: Dict[int, float] = {1: 0.15, 2: 0.25, 3: 0.40, 4: 0.55, 5: 0.70}

# Built from the individual color constants above.
ENCHANT_COLORS: Dict[str, Tuple[int, int, int]] = {
    'fire':       ENCHANT_COLOR_FIRE,
    'ice':        ENCHANT_COLOR_ICE,
    'lightning':  ENCHANT_COLOR_LIGHTNING,
    'protection': ENCHANT_COLOR_PROTECTION,
    'regen':      ENCHANT_COLOR_REGEN,
    'strength':   ENCHANT_COLOR_STRENGTH,
}

# Display name prefixes for enchanted items.
ENCHANT_PREFIX: Dict[str, str] = {
    'fire': 'Flaming',
    'ice': 'Frozen',
    'lightning': 'Shocking',
    'protection': 'Warded',
    'regen': 'Regenerating',
    'strength': 'Mighty',
}

# Maps spell book item_id prefix -> enchant type.
SPELL_TO_ENCHANT: Dict[str, str] = {
    'spell_fireball': 'fire',
    'spell_ice': 'ice',
    'spell_lightning': 'lightning',
    'spell_protection': 'protection',
    'spell_regen': 'regen',
    'spell_strength': 'strength',
}


# ######################################################################
#                        RARITY CONTROLS
# ######################################################################
RARITY_TIERS: Tuple[str, ...] = ('common', 'rare', 'epic', 'legendary', 'mythic')
RARITY_MULTIPLIERS: Dict[str, float] = {
    'common': 1.0, 'rare': 1.5, 'epic': 2.0, 'legendary': 2.5, 'mythic': 3.0,
}
RARITY_ELIGIBLE_CATEGORIES: frozenset = frozenset({
    'weapon', 'armor', 'shield', 'tool', 'placeable', 'ranged',
})
# Built from the individual color constants above — single source of truth.
RARITY_COLORS: Dict[str, Tuple[int, int, int]] = {
    'common':    RARITY_COLOR_COMMON,
    'rare':      RARITY_COLOR_RARE,
    'epic':      RARITY_COLOR_EPIC,
    'legendary': RARITY_COLOR_LEGENDARY,
    'mythic':    RARITY_COLOR_MYTHIC,
}


# ######################################################################
#                        LOOT / DROP CONTROLS
# ######################################################################
ENHANCEMENT_ODDS: Dict[int, float] = {1: 0.45, 2: 0.30, 3: 0.15, 4: 0.07, 5: 0.03}
RARITY_WEIGHTS_NORMAL: Dict[str, float] = {
    'common': 70.0, 'rare': 20.0, 'epic': 8.0, 'legendary': 1.5, 'mythic': 0.5,
}
RARITY_WEIGHTS_BOSS: Dict[str, float] = {
    'common': 20.0, 'rare': 30.0, 'epic': 30.0, 'legendary': 15.0, 'mythic': 5.0,
}


# ######################################################################
#                        RANGED WEAPON CONTROLS
# ######################################################################
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

BOMB_DATA: Dict[str, Dict[str, Any]] = {
    'bomb': {
        'damage': 50,
        'radius': 80.0,
        'speed': 300.0,
        'range': 250.0,
        'color': BOMB_COLOR,
        'fuse_time': 0.0,
    },
}


# ######################################################################
#                        SPELL CONTROLS
# ######################################################################
SPELL_RECHARGE: float = 3.0


# ######################################################################
#                        MUSIC / AUDIO CONTROLS
# ######################################################################
CROSSFADE_MS: int = 2000
DEFAULT_MUSIC_VOLUME: float = 0.6
DEFAULT_MUSIC_ENABLED: bool = True


# ######################################################################
#                        CAMERA CONTROLS
# ######################################################################
CAMERA_LERP_FACTOR: float = 0.12
