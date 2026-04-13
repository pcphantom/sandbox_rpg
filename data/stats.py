"""Player stat tuning — THE single source of truth for ALL stat-related scaling.

Every effect that a player stat (Strength, Agility, Vitality, Luck) has on
the game is defined here.  When you want to change how a stat feels, this is
the ONLY file you need to touch.

Stat points are awarded on level-up (STAT_POINTS_PER_LEVEL per level).
Each point in a stat provides a linear bonus defined by the constants below.
"""

# ======================================================================
# STAT POINTS
# ======================================================================
# How many stat points the player receives per level-up.
STAT_POINTS_PER_LEVEL: int = 3

# ======================================================================
# STRENGTH — increases melee and unarmed damage
# ======================================================================
# Damage bonus per point of Strength (additive multiplier on strength stat).
STR_DAMAGE_MULT: int = 2

# Base melee damage (before weapon and strength bonuses).
BASE_MELEE_DAMAGE: int = 5

# Minimum melee damage floor (damage can't drop below this).
BASE_MELEE_DAMAGE_MIN: int = 5

# Bonus damage per level (additive per level above 1).
LEVEL_DAMAGE_MULT: int = 2

# ======================================================================
# AGILITY — increases move speed, reduces attack cooldowns
# ======================================================================
# Speed bonus per point of Agility.  This is a *multiplier fraction*
# applied as: final_speed = base * (1 + min(cap, agility * AGI_SPEED_BONUS)).
# At AGI 50 with 0.01 this gives +50% speed.
AGI_SPEED_BONUS: float = 0.01

# Maximum speed bonus from agility (1.0 = +100%, reaching 200% total speed).
AGI_SPEED_BONUS_CAP: float = 1.0

# Base player speed (pixels/second).
PLAYER_BASE_SPEED: float = 100.0

# Acceleration multiplier (how responsive movement feels).
MOVEMENT_ACCEL_MULT: int = 10

# Velocity threshold below which the sprite flips direction.
SPRITE_FLIP_THRESHOLD: float = 5.0

# -- Melee cooldown --
# Seconds reduction per point of Agility on melee attack cooldown.
AGILITY_COOLDOWN_REDUCTION: float = 0.002

# Base melee attack cooldown (seconds).
BASE_ATTACK_COOLDOWN: float = 0.30

# Absolute minimum melee cooldown (can never go below this).
MIN_ATTACK_COOLDOWN: float = 0.15

# -- Ranged attack speed --
# Attack speed bonus per point of Agility (0.01 = 1% per point).
# Applied as: cooldown = base_cooldown / (1 + min(cap, agility * bonus)).
AGI_RANGED_SPEED_BONUS: float = 0.01

# Maximum ranged attack speed bonus (1.0 = +100%, halving cooldown).
AGI_RANGED_SPEED_BONUS_CAP: float = 1.0

# Absolute minimum ranged cooldown.
MIN_RANGED_COOLDOWN: float = 0.2

# Ranged damage bonus per point of Agility.
AGI_RANGED_DAMAGE_MULT: int = 2

# ======================================================================
# VITALITY — increases max HP on level-up, campfire healing
# ======================================================================
# Base HP increase per level-up (before vitality bonus).
LEVEL_UP_BASE_HP: int = 10

# Additional max HP gained per Vitality point on each level-up.
VIT_HP_BONUS_PER_LEVEL: int = 5

# Campfire heal bonus: every this-many VIT points gives +1 heal per tick.
VITALITY_CAMPFIRE_BONUS_PER: int = 2

# ======================================================================
# LUCK — critical hits, harvest bonus
# ======================================================================
# Crit chance added per point of Luck (0.01 = 1%).
CRIT_CHANCE_PER_LUCK: float = 0.01

# Critical hit damage multiplier.
CRIT_DAMAGE_MULT: float = 1.5

# Extra harvest chance per point of Luck.
LUCK_HARVEST_CHANCE: float = 0.005
