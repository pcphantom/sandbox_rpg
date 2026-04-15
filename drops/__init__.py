"""Drops package — unified loot tables and drop-roll logic.

Usage:
    from drops import LOOT_TABLES, roll_loot, CAVE_CHEST_LOOT

    table = LOOT_TABLES.get(mob_type)
    items = roll_loot(table)          # returns list of (item_id, count, rarity, enchant)
"""
from __future__ import annotations
import random
from typing import Any, Dict, List, Tuple

from drops.common import (
    ENHANCEMENT_ODDS,
)
from drops.normal import NORMAL_LOOT
from drops.ranged import RANGED_LOOT
from drops.bosses import BOSS_LOOT, CAVE_CHEST_LOOT
from core.item_metadata import roll_item_metadata
from systems.rarity import roll_rarity as _roll_rarity
from data.items import CAN_ENHANCE

# Merge all tables into a single lookup
LOOT_TABLES: Dict[str, Dict[str, Any]] = {}
LOOT_TABLES.update(NORMAL_LOOT)
LOOT_TABLES.update(RANGED_LOOT)
LOOT_TABLES.update(BOSS_LOOT)


def pick_weighted(pool: List[Tuple[str, int, int, int]],
                  count: int,
                  rng: random.Random) -> List[Tuple[str, int]]:
    """Pick *count* unique items from *pool* using weighted random selection.

    Returns list of (item_id, amount).
    """
    if not pool or count <= 0:
        return []
    items: List[Tuple[str, int, int, int]] = list(pool)
    results: List[Tuple[str, int]] = []
    for _ in range(count):
        if not items:
            break
        weights = [w for _, w, _, _ in items]
        chosen = rng.choices(items, weights=weights, k=1)[0]
        item_id, _w, lo, hi = chosen
        amt = rng.randint(lo, hi)
        if amt > 0:
            results.append((item_id, amt))
        items.remove(chosen)
    return results


def maybe_enhance(item_id: str, rng: random.Random) -> str:
    """If item_id is an enhanceable base item, roll an enhanced variant."""
    if not CAN_ENHANCE.get(item_id, False):
        return item_id
    roll = rng.random()
    cumulative = 0.0
    for tier, chance in sorted(ENHANCEMENT_ODDS.items()):
        cumulative += chance
        if roll <= cumulative:
            return f'{item_id}_{tier}'
    return f'{item_id}_1'


def _bonus_roll_count(day_number: int, elite_tier: int) -> int:
    bonus_rolls = 0
    if elite_tier > 0:
        bonus_rolls += 1
    if day_number >= 21:
        bonus_rolls += 1
    return bonus_rolls


def _default_enchant_chance(table: Dict[str, Any], is_boss: bool) -> float:
    enchant_chance = table.get('enchant_chance', 0.0)
    if enchant_chance > 0:
        return enchant_chance
    enchant_chance = table.get('enhanced_chance', 0.0) * 0.45
    if is_boss:
        enchant_chance += 0.10
    return min(0.75, enchant_chance)


def roll_loot(table: Dict[str, Any],
              rng: random.Random | None = None,
              luck_bonus: float = 0.0,
              day_number: int = 1,
              elite_tier: int = 0,
              ) -> List[Tuple[str, int, str, dict | None]]:
    """Roll drops from a loot table.

    Returns a list of (item_id, count, rarity, enchant) tuples.
    Rarity is always a valid tier string (``'common'`` minimum, never None).
    *luck_bonus* is forwarded to `roll_rarity` to boost non-common weights.
    """
    if rng is None:
        rng = random.Random()

    if rng.random() > table['drop_chance']:
        return []

    is_boss = bool(table.get('guaranteed'))

    results: List[Tuple[str, int, str, dict | None]] = []
    enhancement_chance = table.get('enhanced_chance', 0.0)
    enchant_chance = _default_enchant_chance(table, is_boss)

    # Guaranteed drops (bosses)
    for item_id, lo, hi in table.get('guaranteed', []):
        amt = rng.randint(lo, hi)
        if amt > 0:
            rolled_item_id, enchant, rarity = roll_item_metadata(
                item_id,
                rng,
                is_boss=is_boss,
                luck_bonus=luck_bonus,
                day_number=day_number,
                elite_tier=elite_tier,
                enhancement_chance=enhancement_chance,
                enchant_chance=enchant_chance,
            )
            results.append((rolled_item_id, amt, rarity, enchant))

    # Roll pool items
    num_items = rng.randint(table['min_items'], table['max_items'])
    num_items += _bonus_roll_count(day_number, elite_tier)
    num_items = min(len(table['pool']), num_items)
    pool_drops = pick_weighted(table['pool'], num_items, rng)
    for iid, cnt in pool_drops:
        rolled_item_id, enchant, rarity = roll_item_metadata(
            iid,
            rng,
            is_boss=is_boss,
            luck_bonus=luck_bonus,
            day_number=day_number,
            elite_tier=elite_tier,
            enhancement_chance=enhancement_chance,
            enchant_chance=enchant_chance,
        )
        results.append((rolled_item_id, cnt, rarity, enchant))

    return results


__all__ = [
    'LOOT_TABLES', 'CAVE_CHEST_LOOT',
    'roll_loot', 'pick_weighted', 'maybe_enhance',
    'ENHANCEMENT_ODDS',
    'NORMAL_LOOT', 'RANGED_LOOT', 'BOSS_LOOT',
]
