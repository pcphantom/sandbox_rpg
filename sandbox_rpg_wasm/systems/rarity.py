"""Rarity system — stat application and drop rolling.

Centralises all rarity multiplier logic so callers don't scatter
``get_rarity_multiplier`` calls and weight-table lookups inline.
"""
from __future__ import annotations

import random

from data.quality import (
    get_rarity_multiplier,
)
from data.items import HAS_RARITY


# ── stat application ──────────────────────────────────────────────────

def apply_rarity(base: int, rarity: str) -> int:
    """Return *base* scaled by the rarity multiplier (no-op for common)."""
    if rarity == 'common':
        return base
    return int(base * get_rarity_multiplier(rarity))


# ── drop rolling ──────────────────────────────────────────────────────

def roll_rarity(item_id: str, is_boss: bool,
                rng: random.Random,
                luck_bonus: float = 0.0) -> str:
    """Roll a rarity tier for *item_id*, or ``'common'`` if not eligible.

    *luck_bonus* multiplies non-common weights by ``(1 + luck_bonus)``,
    making rarer tiers more likely.
    """
    if not HAS_RARITY.get(item_id, False):
        return 'common'
    # Deferred import to avoid circular: drops/__init__ imports this module
    from drops.common import RARITY_WEIGHTS_NORMAL, RARITY_WEIGHTS_BOSS
    weights = RARITY_WEIGHTS_BOSS if is_boss else RARITY_WEIGHTS_NORMAL
    tiers = list(weights.keys())
    wts = list(weights.values())
    if luck_bonus > 0:
        wts = [w * (1 + luck_bonus) if t != 'common' else w
               for t, w in zip(tiers, wts)]
    return rng.choices(tiers, weights=wts, k=1)[0]
