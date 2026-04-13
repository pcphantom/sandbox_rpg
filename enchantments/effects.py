"""Enchantment effect definitions and tuning constants.

Each enchantment type has per-level values for easy balancing.
Enchantments are stored as overlay data on inventory/equipment slots:
    {'type': 'fire'|'ice'|'lightning'|'protection'|'regen', 'level': 1-5}

Only ONE enchantment per item (mutually exclusive). Applying a new one
replaces the previous.
"""
from typing import Dict, Any, Optional

# ======================================================================
# CONTROL VARIABLES — tune these for balancing
# ======================================================================

# Bonus flat damage added to melee/ranged attacks when weapon has this enchant.
FIRE_BONUS_DAMAGE = {1: 5, 2: 10, 3: 18, 4: 28, 5: 40}
ICE_BONUS_DAMAGE = {1: 3, 2: 7, 3: 12, 4: 19, 5: 28}
LIGHTNING_BONUS_DAMAGE = {1: 6, 2: 12, 3: 20, 4: 30, 5: 42}

# Fire enchant emits light (acts as torch). Radius per level.
FIRE_LIGHT_RADIUS = {1: 90, 2: 110, 3: 140, 4: 175, 5: 220}

# Ice enchant slows enemies on hit.
ICE_SLOW_FACTOR = {1: 0.5, 2: 0.35, 3: 0.2, 4: 0.12, 5: 0.05}
ICE_SLOW_DURATION = {1: 2.0, 2: 3.0, 3: 4.5, 4: 6.0, 5: 8.0}

# Lightning enchant arcs to nearby enemies.
LIGHTNING_ARC_RADIUS = {1: 60.0, 2: 80.0, 3: 100.0, 4: 125.0, 5: 150.0}
LIGHTNING_ARC_DAMAGE_FRAC = {1: 0.3, 2: 0.4, 3: 0.5, 4: 0.6, 5: 0.7}

# Protection enchant on armor — flat DR bonus (from centralized enhancement module).
from core.enhancement import PROTECTION_DR_BONUS

# Regen enchant on armor — passive HP regen per second while equipped.
REGEN_HP_PER_SEC = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}

# Strength enchant on weapons — bonus flat damage while equipped.
STRENGTH_BONUS_DAMAGE = {1: 3, 2: 6, 3: 10, 4: 15, 5: 20}

# Elemental resistance on armor — fraction of elemental damage absorbed.
ELEMENTAL_RESISTANCE = {1: 0.15, 2: 0.25, 3: 0.40, 4: 0.55, 5: 0.70}

# Display name prefixes for enchanted items.
ENCHANT_PREFIX = {
    'fire': 'Flaming',
    'ice': 'Frozen',
    'lightning': 'Shocking',
    'protection': 'Warded',
    'regen': 'Regenerating',
    'strength': 'Mighty',
}

# Particle/glow colors per enchant type.
ENCHANT_COLORS = {
    'fire': (255, 120, 30),
    'ice': (100, 200, 255),
    'lightning': (180, 200, 255),
    'protection': (80, 255, 120),
    'regen': (50, 255, 50),
    'strength': (255, 80, 80),
}

# Maps spell book item_id prefix → enchant type.
SPELL_TO_ENCHANT = {
    'spell_fireball': 'fire',
    'spell_ice': 'ice',
    'spell_lightning': 'lightning',
    'spell_protection': 'protection',
    'spell_regen': 'regen',
    'spell_strength': 'strength',
}

# Combined lookup dict for UI/tooltips.
ENCHANT_EFFECTS: Dict[str, Dict[int, Dict[str, Any]]] = {
    'fire': {
        1: {'bonus_damage': FIRE_BONUS_DAMAGE[1], 'light_radius': FIRE_LIGHT_RADIUS[1]},
        2: {'bonus_damage': FIRE_BONUS_DAMAGE[2], 'light_radius': FIRE_LIGHT_RADIUS[2]},
        3: {'bonus_damage': FIRE_BONUS_DAMAGE[3], 'light_radius': FIRE_LIGHT_RADIUS[3]},
        4: {'bonus_damage': FIRE_BONUS_DAMAGE[4], 'light_radius': FIRE_LIGHT_RADIUS[4]},
        5: {'bonus_damage': FIRE_BONUS_DAMAGE[5], 'light_radius': FIRE_LIGHT_RADIUS[5]},
    },
    'ice': {
        1: {'bonus_damage': ICE_BONUS_DAMAGE[1], 'slow_factor': ICE_SLOW_FACTOR[1], 'slow_duration': ICE_SLOW_DURATION[1]},
        2: {'bonus_damage': ICE_BONUS_DAMAGE[2], 'slow_factor': ICE_SLOW_FACTOR[2], 'slow_duration': ICE_SLOW_DURATION[2]},
        3: {'bonus_damage': ICE_BONUS_DAMAGE[3], 'slow_factor': ICE_SLOW_FACTOR[3], 'slow_duration': ICE_SLOW_DURATION[3]},
        4: {'bonus_damage': ICE_BONUS_DAMAGE[4], 'slow_factor': ICE_SLOW_FACTOR[4], 'slow_duration': ICE_SLOW_DURATION[4]},
        5: {'bonus_damage': ICE_BONUS_DAMAGE[5], 'slow_factor': ICE_SLOW_FACTOR[5], 'slow_duration': ICE_SLOW_DURATION[5]},
    },
    'lightning': {
        1: {'bonus_damage': LIGHTNING_BONUS_DAMAGE[1], 'arc_radius': LIGHTNING_ARC_RADIUS[1], 'arc_frac': LIGHTNING_ARC_DAMAGE_FRAC[1]},
        2: {'bonus_damage': LIGHTNING_BONUS_DAMAGE[2], 'arc_radius': LIGHTNING_ARC_RADIUS[2], 'arc_frac': LIGHTNING_ARC_DAMAGE_FRAC[2]},
        3: {'bonus_damage': LIGHTNING_BONUS_DAMAGE[3], 'arc_radius': LIGHTNING_ARC_RADIUS[3], 'arc_frac': LIGHTNING_ARC_DAMAGE_FRAC[3]},
        4: {'bonus_damage': LIGHTNING_BONUS_DAMAGE[4], 'arc_radius': LIGHTNING_ARC_RADIUS[4], 'arc_frac': LIGHTNING_ARC_DAMAGE_FRAC[4]},
        5: {'bonus_damage': LIGHTNING_BONUS_DAMAGE[5], 'arc_radius': LIGHTNING_ARC_RADIUS[5], 'arc_frac': LIGHTNING_ARC_DAMAGE_FRAC[5]},
    },
    'protection': {
        1: {'dr_bonus': PROTECTION_DR_BONUS[1]},
        2: {'dr_bonus': PROTECTION_DR_BONUS[2]},
        3: {'dr_bonus': PROTECTION_DR_BONUS[3]},
        4: {'dr_bonus': PROTECTION_DR_BONUS[4]},
        5: {'dr_bonus': PROTECTION_DR_BONUS[5]},
    },
    'regen': {
        1: {'hp_per_sec': REGEN_HP_PER_SEC[1]},
        2: {'hp_per_sec': REGEN_HP_PER_SEC[2]},
        3: {'hp_per_sec': REGEN_HP_PER_SEC[3]},
        4: {'hp_per_sec': REGEN_HP_PER_SEC[4]},
        5: {'hp_per_sec': REGEN_HP_PER_SEC[5]},
    },
    'strength': {
        1: {'bonus_damage': STRENGTH_BONUS_DAMAGE[1]},
        2: {'bonus_damage': STRENGTH_BONUS_DAMAGE[2]},
        3: {'bonus_damage': STRENGTH_BONUS_DAMAGE[3]},
        4: {'bonus_damage': STRENGTH_BONUS_DAMAGE[4]},
        5: {'bonus_damage': STRENGTH_BONUS_DAMAGE[5]},
    },
}


# ======================================================================
# HELPER FUNCTIONS — used by combat/rendering code
# ======================================================================

# Roman numeral mapping for enchant levels.
_ROMAN = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V'}


def get_enchant_display_prefix(enchant: Optional[Dict[str, Any]]) -> str:
    """Return display prefix like 'Flaming V' for an enchant dict, or ''."""
    if not enchant:
        return ''
    prefix = ENCHANT_PREFIX.get(enchant['type'], '')
    if not prefix:
        return ''
    level = enchant.get('level', 1)
    numeral = _ROMAN.get(level, str(level))
    return f'{prefix} {numeral}'


def get_enchant_bonus_damage(enchant: Optional[Dict[str, Any]]) -> int:
    """Return flat bonus melee/ranged damage from an enchant, or 0."""
    if not enchant:
        return 0
    etype = enchant['type']
    level = enchant['level']
    lookup = {
        'fire': FIRE_BONUS_DAMAGE,
        'ice': ICE_BONUS_DAMAGE,
        'lightning': LIGHTNING_BONUS_DAMAGE,
        'strength': STRENGTH_BONUS_DAMAGE,
    }
    return lookup.get(etype, {}).get(level, 0)


def get_enchant_dr_bonus(enchant: Optional[Dict[str, Any]]) -> int:
    """Return flat DR bonus from protection enchant on armor, or 0."""
    if not enchant or enchant['type'] != 'protection':
        return 0
    return PROTECTION_DR_BONUS.get(enchant['level'], 0)


def get_enchant_light_radius(enchant: Optional[Dict[str, Any]]) -> int:
    """Return light radius from fire enchant on weapon, or 0."""
    if not enchant or enchant['type'] != 'fire':
        return 0
    return FIRE_LIGHT_RADIUS.get(enchant['level'], 0)


def get_enchant_slow_factor(enchant: Optional[Dict[str, Any]]) -> float:
    """Return slow multiplier from ice enchant, or 1.0 (no slow)."""
    if not enchant or enchant['type'] != 'ice':
        return 1.0
    return ICE_SLOW_FACTOR.get(enchant['level'], 1.0)


def get_enchant_slow_duration(enchant: Optional[Dict[str, Any]]) -> float:
    """Return slow duration from ice enchant, or 0."""
    if not enchant or enchant['type'] != 'ice':
        return 0.0
    return ICE_SLOW_DURATION.get(enchant['level'], 0.0)


def get_enchant_arc_radius(enchant: Optional[Dict[str, Any]]) -> float:
    """Return lightning arc radius, or 0."""
    if not enchant or enchant['type'] != 'lightning':
        return 0.0
    return LIGHTNING_ARC_RADIUS.get(enchant['level'], 0.0)


def get_enchant_arc_damage_frac(enchant: Optional[Dict[str, Any]]) -> float:
    """Return lightning arc damage fraction, or 0."""
    if not enchant or enchant['type'] != 'lightning':
        return 0.0
    return LIGHTNING_ARC_DAMAGE_FRAC.get(enchant['level'], 0.0)


def get_enchant_resistance(enchant: Optional[Dict[str, Any]]) -> float:
    """Return elemental resistance fraction from armor enchant, or 0."""
    if not enchant:
        return 0.0
    etype = enchant['type']
    if etype in ('protection', 'regen', 'strength'):
        return 0.0  # these give other bonuses, not resistance
    return ELEMENTAL_RESISTANCE.get(enchant['level'], 0.0)


def get_enchant_regen_rate(enchant: Optional[Dict[str, Any]]) -> int:
    """Return passive HP/sec from regen enchant, or 0."""
    if not enchant or enchant['type'] != 'regen':
        return 0
    return REGEN_HP_PER_SEC.get(enchant['level'], 0)
