"""Combat helper functions — melee / ranged damage and damage reduction."""
from core.components import PlayerStats, Equipment
from data import ARMOR_VALUES
from data.stats import (
    BASE_MELEE_DAMAGE_MIN, STR_DAMAGE_MULT, LEVEL_DAMAGE_MULT,
    AGI_RANGED_DAMAGE_MULT,
)


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


def calc_damage_reduction(equipment: Equipment | None) -> int:
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
