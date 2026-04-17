"""Day/Night cycle — re-exports ALL time-related controls from game_controller.

This module exists for backwards compatibility.  The single source of truth
for every time-of-day variable is game_controller.py.  All code that
imports ``from data.day_night import X`` will continue to work unchanged.

For effects that scale across multiple *days* (waves, spawning ramps,
mob progression, etc.), see data/day_events.py.
"""
from game_controller import (                                         # noqa: F401
    DAY_LENGTH_BASE,
    TIME_SPEED_NORMAL,
    SLEEP_DURATION,
    SLEEP_SPEED_MULT,
    BED_INTERACT_RANGE,
    DAWN_BEGINS,
    DAY_BEGINS,
    DUSK_BEGINS,
    NIGHT_BEGINS,
    TIME_NIGHT_END,
    TIME_DAY_START,
    TIME_DAY_END,
    TIME_NIGHT_START,
    DAY_FLASH_DURATION,
    DAY_FLASH_FADE_DIVISOR,
    DAY_FLASH_TEXT,
    DAY_FLASH_COLOR,
    NIGHT_FLASH_DURATION,
    NIGHT_FLASH_FADE_DIVISOR,
    NIGHT_FLASH_TEXT,
    NIGHT_FLASH_COLOR,
    DAWN_FLASH_DURATION,
    DAWN_FLASH_TEXT,
    DAWN_FLASH_COLOR,
    DUSK_FLASH_DURATION,
    DUSK_FLASH_TEXT,
    DUSK_FLASH_COLOR,
    SLEEP_OVERLAY_TEXT,
    SLEEP_OVERLAY_COLOR,
    NIGHT_DARKNESS_THRESHOLD,
    NIGHT_DAMAGE_BASE,
    NIGHT_DAMAGE_INCREASE,
    NIGHT_DAMAGE_INCREASE_FREQ,
    NIGHT_DAMAGE_INTERVAL,
    LIGHT_SAFETY_RADIUS,
    NIGHT_SLEEP_SPEED_MULT,
)
