"""Combat helper functions — melee / ranged damage and damage reduction.

Damage reduction uses a diminishing returns formula:
  effective_reduction% = DR_total / (DR_total + DR_HALF_VALUE)
capped at DR_MAX_PERCENT.  This ensures DR is meaningful at all levels
but never makes the player invincible.
"""
from core.components import PlayerStats, Equipment
from data import ARMOR_VALUES
from data.stats import (
    BASE_MELEE_DAMAGE_MIN, STR_DAMAGE_MULT, LEVEL_DAMAGE_MULT,
    AGI_RANGED_DAMAGE_MULT,
)
from game_controller import DR_HALF_VALUE, DR_MAX_PERCENT, DR_MIN_DAMAGE


def calc_melee_damage(base_item_dmg: int, stats: PlayerStats,
                      equipment: Equipment | None) -> int:
    """Calculate melee hit damage including STR bonus."""
    dmg = (max(base_item_dmg, BASE_MELEE_DAMAGE_MIN)
           + stats.strength * STR_DAMAGE_MULT
           + (stats.level - 1) * LEVEL_DAMAGE_MULT)
    return dmg


def calc_ranged_damage(ranged_base: int, ammo_bonus: int,
                       stats: PlayerStats) -> int:
    return ranged_base + ammo_bonus + stats.agility * AGI_RANGED_DAMAGE_MULT


def calc_total_dr(equipment: Equipment | None, protection_buff_value: int = 0,
                  enchant_dr: int = 0) -> int:
    """Sum all flat DR from gear, protection buff, and enchants."""
    total = 0
    if equipment:
        from systems.rarity import apply_rarity
        if equipment.armor and equipment.armor in ARMOR_VALUES:
            base_dr = ARMOR_VALUES[equipment.armor]
            base_dr = apply_rarity(base_dr, equipment.rarities.get('armor', 'common'))
            total += base_dr
        if equipment.shield and equipment.shield in ARMOR_VALUES:
            base_dr = ARMOR_VALUES[equipment.shield]
            base_dr = apply_rarity(base_dr, equipment.rarities.get('shield', 'common'))
            total += base_dr
    total += protection_buff_value
    total += enchant_dr
    return total


def apply_damage_reduction(raw_damage: int, total_dr: int) -> int:
    """Apply diminishing-returns DR to raw damage.

    Formula:  reduction% = DR / (DR + DR_HALF_VALUE), capped at DR_MAX_PERCENT
    This means:
      DR 10  with half=100 → ~9% reduction
      DR 50  with half=100 → ~33% reduction
      DR 100 with half=100 → 50% reduction
      DR 200 with half=100 → 67% reduction
      DR 500 with half=100 → 83% reduction
    Always returns at least DR_MIN_DAMAGE.
    """
    if total_dr <= 0:
        return max(DR_MIN_DAMAGE, raw_damage)
    reduction_pct = total_dr / (total_dr + DR_HALF_VALUE)
    reduction_pct = min(reduction_pct, DR_MAX_PERCENT)
    reduced = int(raw_damage * (1.0 - reduction_pct))
    return max(DR_MIN_DAMAGE, reduced)


def calc_damage_reduction(equipment: Equipment | None) -> int:
    """Legacy: return flat DR from equipment only (used by some callers)."""
    if equipment is None:
        return 0
    from systems.rarity import apply_rarity
    total = 0
    if equipment.armor and equipment.armor in ARMOR_VALUES:
        base_dr = ARMOR_VALUES[equipment.armor]
        base_dr = apply_rarity(base_dr, equipment.rarities.get('armor', 'common'))
        total += base_dr
    if equipment.shield and equipment.shield in ARMOR_VALUES:
        base_dr = ARMOR_VALUES[equipment.shield]
        base_dr = apply_rarity(base_dr, equipment.rarities.get('shield', 'common'))
        total += base_dr
    return total
