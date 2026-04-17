"""Enchantment effect definitions and tuning constants.

Each enchantment type has per-level values for easy balancing.
Enchantments are stored as overlay data on inventory/equipment slots:
    {'type': 'fire'|'ice'|'lightning'|'protection'|'regen', 'level': 1-5}

Only ONE enchantment per item (mutually exclusive). Applying a new one
replaces the previous.

All tuning constants are sourced from game_controller.py.
"""
from typing import Dict, Any, Optional

from game_controller import (
    FIRE_BONUS_DAMAGE, ICE_BONUS_DAMAGE, LIGHTNING_BONUS_DAMAGE,
    FIRE_LIGHT_RADIUS,
    ICE_SLOW_FACTOR, ICE_SLOW_DURATION,
    LIGHTNING_ARC_RADIUS, LIGHTNING_ARC_DAMAGE_FRAC,
    REGEN_HP_PER_SEC, STRENGTH_BONUS_DAMAGE, ELEMENTAL_RESISTANCE,
    ENCHANT_PREFIX, ENCHANT_COLORS, SPELL_TO_ENCHANT,
)

# Protection enchant DR bonus (derived from centralized enhancement module).
from core.enhancement import PROTECTION_DR_BONUS

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
