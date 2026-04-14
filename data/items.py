"""Item definitions and categories — sourced from items/ package.

All item data, categories, and control flags are defined in the items/
package modules (grouped by category). This module re-exports them for
backward compatibility so existing ``from data.items import ...`` and
``from data import ...`` imports continue to work.
"""
from items import (
    ITEM_DATA,
    ITEM_CATEGORIES,
    NON_STACKABLE_CATEGORIES,
    CAN_ENCHANT,
    CAN_ENHANCE,
    HAS_RARITY,
    HARVEST_TYPE,
)
