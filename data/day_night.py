"""Day/Night cycle — THE single source of truth for ALL time-related controls.

Everything that involves the passage of time in the game is defined here:
  * How fast time moves (normal and during rest)
  * How long each day period lasts (Night, Dawn, Day, Dusk)
  * When and what messages appear for period transitions
  * Sleep / rest duration and speed multipliers
  * Night damage timing and values
  * Darkness thresholds

For effects that scale across multiple *days* (waves, spawning ramps,
mob progression, etc.), see data/day_events.py.

Time is represented as a float 0.0-1.0 over a full day cycle where
0.0 = midnight, 0.25 = dawn, 0.5 = noon, 0.75 = dusk.
"""

# ======================================================================
# CYCLE LENGTH — how fast time moves
# ======================================================================
# Total real-world seconds for one full in-game day.
DAY_LENGTH_BASE: float = 960.0           # 16 real minutes = 1 game day

# Normal time speed multiplier (1.0 = default).
TIME_SPEED_NORMAL: float = 1.0

# ======================================================================
# SLEEP / REST — how sleeping works
# ======================================================================
# Real-world seconds the sleep animation / overlay lasts.
SLEEP_DURATION: float = 5.0

# Time-advancement multiplier while sleeping (how fast time passes in-game).
# E.g. 12.0 means sleeping skips through the night 12x faster.
SLEEP_SPEED_MULT: float = 12.0

# Pixel range within which the player can interact with a bed to sleep.
BED_INTERACT_RANGE: float = 50.0

# ======================================================================
# PERIOD THRESHOLDS (fraction of the day cycle, 0.0-1.0)
# ======================================================================
# These four values carve the day into five visual periods:
#   Night  (0.00 -> TIME_NIGHT_END)
#   Dawn   (TIME_NIGHT_END -> TIME_DAY_START)
#   Day    (TIME_DAY_START -> TIME_DAY_END)
#   Dusk   (TIME_DAY_END -> TIME_NIGHT_START)
#   Night  (TIME_NIGHT_START -> 1.00)
TIME_NIGHT_END: float   = 0.22   # night -> dawn transition
TIME_DAY_START: float   = 0.30   # dawn  -> day  transition
TIME_DAY_END: float     = 0.70   # day   -> dusk transition
TIME_NIGHT_START: float = 0.78   # dusk  -> night transition

# ======================================================================
# PERIOD MESSAGES — what text appears and when for each transition
# ======================================================================
# --- "Day X" banner — shown when day period starts ---
DAY_FLASH_DURATION: float      = 3.0       # seconds the text stays on screen
DAY_FLASH_FADE_DIVISOR: float  = 1.0       # alpha = timer / this  (lower = fades slower)
DAY_FLASH_TEXT: str             = "Day {day}"   # {day} is replaced at runtime
DAY_FLASH_COLOR: tuple          = (255, 255, 200)

# --- "Night falls" banner — shown when night period starts ---
NIGHT_FLASH_DURATION: float     = 2.5      # seconds the text stays on screen
NIGHT_FLASH_FADE_DIVISOR: float = 0.8      # alpha = timer / this
NIGHT_FLASH_TEXT: str           = "Night falls \u2014 Defend!"
NIGHT_FLASH_COLOR: tuple        = (255, 120, 80)

# --- Dawn message (shown when dawn period starts) ---
DAWN_FLASH_DURATION: float      = 2.0
DAWN_FLASH_TEXT: str            = ""        # empty = no message at dawn
DAWN_FLASH_COLOR: tuple         = (255, 220, 150)

# --- Dusk message (shown when dusk period starts) ---
DUSK_FLASH_DURATION: float      = 2.0
DUSK_FLASH_TEXT: str            = "Dusk approaches..."
DUSK_FLASH_COLOR: tuple         = (255, 180, 100)

# --- Sleeping overlay text ---
SLEEP_OVERLAY_TEXT: str          = "Sleeping... Zzz"
SLEEP_OVERLAY_COLOR: tuple       = (180, 180, 255)

# ======================================================================
# DARKNESS — when night visual effects kick in
# ======================================================================
# get_darkness() returns 0.0 (full day) to 1.0+ (deep night).
# Night damage only applies when darkness exceeds this value.
NIGHT_DARKNESS_THRESHOLD: float = 0.5

# ======================================================================
# NIGHT DAMAGE — periodic damage when outside light at night
# ======================================================================
NIGHT_DAMAGE_BASE: int         = 2         # starting HP per tick on day 1
NIGHT_DAMAGE_INCREASE: int     = 1         # extra HP added per scaling step
NIGHT_DAMAGE_INCREASE_FREQ: int = 1        # add INCREASE every N days
NIGHT_DAMAGE_INTERVAL: float   = 3.0       # seconds between ticks
LIGHT_SAFETY_RADIUS: float     = 200.0     # pixel radius around a light that protects

# ======================================================================
# BACKWARDS COMPATIBILITY — aliases for old names
# ======================================================================
# Old code may reference NIGHT_SLEEP_SPEED_MULT; point to the new name.
NIGHT_SLEEP_SPEED_MULT: float = SLEEP_SPEED_MULT
