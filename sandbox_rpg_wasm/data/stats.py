"""Player stat tuning — re-exports ALL stat-related constants from game_controller.

The single source of truth is game_controller.py.  All code that imports
``from data.stats import X`` will continue to work unchanged.
"""
from game_controller import (                                         # noqa: F401
    STAT_POINTS_PER_LEVEL,
    STR_DAMAGE_MULT,
    BASE_MELEE_DAMAGE,
    BASE_MELEE_DAMAGE_MIN,
    LEVEL_DAMAGE_MULT,
    AGI_SPEED_BONUS,
    AGI_SPEED_BONUS_CAP,
    PLAYER_BASE_SPEED,
    MOVEMENT_ACCEL_MULT,
    SPRITE_FLIP_THRESHOLD,
    AGILITY_COOLDOWN_REDUCTION,
    BASE_ATTACK_COOLDOWN,
    MIN_ATTACK_COOLDOWN,
    AGI_RANGED_SPEED_BONUS,
    AGI_RANGED_SPEED_BONUS_CAP,
    MIN_RANGED_COOLDOWN,
    AGI_RANGED_DAMAGE_MULT,
    LEVEL_UP_BASE_HP,
    VIT_HP_BONUS_PER_LEVEL,
    VITALITY_CAMPFIRE_BONUS_PER,
    CRIT_CHANCE_PER_LUCK,
    CRIT_DAMAGE_MULT,
    LUCK_HARVEST_CHANCE,
)
