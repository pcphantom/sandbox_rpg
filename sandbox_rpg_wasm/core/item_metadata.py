"""Shared item metadata validation and loot rolling helpers."""
from __future__ import annotations

import random
from typing import Dict, Optional, Tuple

from core.enhancement import get_base_item_id, get_enhancement_level
from core.item_stack import normalize_rarity
from data import CAN_ENCHANT, CAN_ENHANCE, ITEM_CATEGORIES, ITEM_DATA
from data.quality import RARITY_TIERS
from game_controller import ENHANCEMENT_ODDS
from systems.rarity import roll_rarity

ROMAN_NUMERAL_LEVELS: Dict[str, int] = {
    'i': 1,
    'ii': 2,
    'iii': 3,
    'iv': 4,
    'v': 5,
}

ENCHANT_TYPE_ALIASES: Dict[str, str] = {
    'fire': 'fire',
    'flame': 'fire',
    'flaming': 'fire',
    'fireball': 'fire',
    'ice': 'ice',
    'frozen': 'ice',
    'lightning': 'lightning',
    'shock': 'lightning',
    'shocking': 'lightning',
    'protect': 'protection',
    'protection': 'protection',
    'prot': 'protection',
    'warded': 'protection',
    'regen': 'regen',
    'regenerating': 'regen',
    'strength': 'strength',
    'strong': 'strength',
    'mighty': 'strength',
}

RARITY_ALIASES: Dict[str, str] = {
    tier: tier for tier in RARITY_TIERS
}

OFFENSIVE_ENCHANT_TYPES: Tuple[str, ...] = (
    'fire', 'ice', 'lightning', 'strength',
)
DEFENSIVE_ENCHANT_TYPES: Tuple[str, ...] = (
    'protection', 'regen',
)


def parse_level_token(token: str) -> Optional[int]:
    """Parse a numeric, +N, or roman-numeral level token."""
    cleaned = token.strip().lower()
    if not cleaned:
        return None
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    if cleaned.isdigit():
        level = int(cleaned)
        if 1 <= level <= 5:
            return level
        return None
    return ROMAN_NUMERAL_LEVELS.get(cleaned)


def resolve_enchant_type_token(token: str) -> Optional[str]:
    """Resolve a human-friendly enchant token to its canonical type."""
    return ENCHANT_TYPE_ALIASES.get(token.strip().lower())


def resolve_rarity_token(token: str) -> Optional[str]:
    """Resolve a human-friendly rarity token to its canonical tier."""
    return RARITY_ALIASES.get(token.strip().lower())


def can_apply_enchant_to_item(item_id: str, enchant_type: str) -> bool:
    """Return True if an explicit enchant type can be applied to an item."""
    if not CAN_ENCHANT.get(item_id, False):
        return False
    category = ITEM_CATEGORIES.get(item_id, '')
    if enchant_type in DEFENSIVE_ENCHANT_TYPES:
        return category in ('armor', 'shield', 'placeable')
    return enchant_type in OFFENSIVE_ENCHANT_TYPES


def get_random_enchant_types(item_id: str) -> Tuple[str, ...]:
    """Return the sensible random-enchant pool for a loot item."""
    if not CAN_ENCHANT.get(item_id, False):
        return ()
    category = ITEM_CATEGORIES.get(item_id, '')
    if category in ('armor', 'shield'):
        return DEFENSIVE_ENCHANT_TYPES
    if category == 'placeable':
        return OFFENSIVE_ENCHANT_TYPES + DEFENSIVE_ENCHANT_TYPES
    return OFFENSIVE_ENCHANT_TYPES


def set_item_enhancement_level(item_id: str,
                               enhancement_level: int) -> Optional[str]:
    """Return the exact item id for the requested enhancement level."""
    target_level = max(0, min(5, enhancement_level))
    base_item_id = get_base_item_id(item_id)
    if base_item_id == item_id and not CAN_ENHANCE.get(item_id, False):
        return item_id if target_level == 0 else None
    if target_level == 0:
        return base_item_id
    enhanced_item_id = f'{base_item_id}_{target_level}'
    if enhanced_item_id in ITEM_DATA:
        return enhanced_item_id
    return None


def _roll_enhancement_level_once(rng: random.Random) -> int:
    roll = rng.random()
    cumulative = 0.0
    for level, chance in sorted(ENHANCEMENT_ODDS.items()):
        cumulative += chance
        if roll <= cumulative:
            return level
    return 1


def _roll_metadata_level(rng: random.Random,
                         day_number: int,
                         elite_tier: int,
                         is_boss: bool) -> int:
    max_level = 1
    max_level += min(2, max(0, day_number - 1) // 14)
    if elite_tier >= 2:
        max_level += 1
    if elite_tier >= 4:
        max_level += 1
    if is_boss:
        max_level += 1
    max_level = min(5, max_level)

    levels = list(range(1, max_level + 1))
    weights = [max_level - level + 2 for level in levels]
    chosen_level = rng.choices(levels, weights=weights, k=1)[0]
    rerolls = min(3, elite_tier // 2 + (1 if is_boss else 0)
                  + max(0, day_number - 1) // 21)
    for _ in range(rerolls):
        chosen_level = max(
            chosen_level,
            rng.choices(levels, weights=weights, k=1)[0],
        )
    return chosen_level


def _roll_enhancement_level(rng: random.Random,
                            day_number: int,
                            elite_tier: int,
                            is_boss: bool) -> int:
    chosen_level = _roll_enhancement_level_once(rng)
    rerolls = min(3, elite_tier // 2 + (1 if is_boss else 0)
                  + max(0, day_number - 1) // 21)
    for _ in range(rerolls):
        chosen_level = max(chosen_level, _roll_enhancement_level_once(rng))
    return chosen_level


def roll_random_enchant(item_id: str,
                        rng: random.Random,
                        *,
                        day_number: int = 1,
                        elite_tier: int = 0,
                        is_boss: bool = False) -> Optional[dict]:
    """Roll a random enchant dict for a loot item, or None if unsupported."""
    random_enchant_types = get_random_enchant_types(item_id)
    if not random_enchant_types:
        return None
    enchant_type = rng.choice(random_enchant_types)
    enchant_level = _roll_metadata_level(
        rng, day_number, elite_tier, is_boss)
    return {'type': enchant_type, 'level': enchant_level}


def _roll_metadata_chance(base_chance: float,
                          day_number: int,
                          elite_tier: int,
                          is_boss: bool,
                          item_id: str,
                          turret_bonus: float) -> float:
    chance = max(0.0, base_chance)
    chance += min(0.20, max(0, day_number - 1) * 0.004)
    chance += elite_tier * 0.06
    if is_boss:
        chance += 0.12
    if get_base_item_id(item_id) == 'turret':
        chance += turret_bonus
    return min(0.95, chance)


def _roll_rarity_bonus(item_id: str,
                       luck_bonus: float,
                       day_number: int,
                       elite_tier: int,
                       is_boss: bool) -> float:
    rarity_bonus = max(0.0, luck_bonus)
    rarity_bonus += min(0.35, max(0, day_number - 1) * 0.01)
    rarity_bonus += elite_tier * 0.25
    if is_boss:
        rarity_bonus += 0.20
    if get_base_item_id(item_id) == 'turret':
        rarity_bonus += 0.35
    return rarity_bonus


def roll_item_metadata(item_id: str,
                       rng: random.Random,
                       *,
                       is_boss: bool = False,
                       luck_bonus: float = 0.0,
                       day_number: int = 1,
                       elite_tier: int = 0,
                       enhancement_chance: float = 0.0,
                       enchant_chance: float = 0.0) -> Tuple[str, Optional[dict], str]:
    """Roll enhancement, enchant, and rarity metadata for a loot item."""
    rolled_item_id = item_id
    current_enhancement = get_enhancement_level(rolled_item_id)
    if CAN_ENHANCE.get(get_base_item_id(rolled_item_id), False):
        final_enhance_chance = _roll_metadata_chance(
            enhancement_chance, day_number, elite_tier, is_boss,
            rolled_item_id, 0.15)
        if rng.random() < final_enhance_chance:
            rolled_level = max(
                current_enhancement,
                _roll_enhancement_level(rng, day_number, elite_tier, is_boss),
            )
            enhanced_item_id = set_item_enhancement_level(
                rolled_item_id, rolled_level)
            if enhanced_item_id:
                rolled_item_id = enhanced_item_id

    enchant = None
    final_enchant_chance = _roll_metadata_chance(
        enchant_chance, day_number, elite_tier, is_boss, rolled_item_id, 0.25)
    if rng.random() < final_enchant_chance:
        enchant = roll_random_enchant(
            rolled_item_id, rng,
            day_number=day_number,
            elite_tier=elite_tier,
            is_boss=is_boss,
        )

    rarity = normalize_rarity(roll_rarity(
        rolled_item_id,
        is_boss,
        rng,
        _roll_rarity_bonus(rolled_item_id, luck_bonus,
                           day_number, elite_tier, is_boss),
    ))
    return rolled_item_id, enchant, rarity


__all__ = [
    'OFFENSIVE_ENCHANT_TYPES',
    'DEFENSIVE_ENCHANT_TYPES',
    'ROMAN_NUMERAL_LEVELS',
    'ENCHANT_TYPE_ALIASES',
    'RARITY_ALIASES',
    'parse_level_token',
    'resolve_enchant_type_token',
    'resolve_rarity_token',
    'can_apply_enchant_to_item',
    'get_random_enchant_types',
    'set_item_enhancement_level',
    'roll_random_enchant',
    'roll_item_metadata',
]