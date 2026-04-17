"""Inventory sort — sorts inventory slots without merging non-stackable items.

Unlike chest sorting (which stacks all identical items regardless of
category), inventory sorting respects the NON_STACKABLE_CATEGORIES rule:
items whose category is in that set keep one unit per slot.  Stackable
items of the same identity (id + enchant + rarity) are merged.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

from core.item_stack import make_stack_key, normalize_rarity
from data import ITEM_CATEGORIES, NON_STACKABLE_CATEGORIES


def sort_inventory_slots(slots: Dict[int, Tuple[str, int]],
                         enchants: Dict[int, dict],
                         rarities: Dict[int, str]) -> None:
    """Sort and compact inventory slots in-place.

    * Stackable items with matching identity are merged into one slot.
    * Non-stackable items keep one unit per slot (never merged).
    * Slots are compacted so there are no gaps, sorted alphabetically
      by item_id then by enchant/rarity.
    """
    # Collect all items
    stackable_groups: Dict[tuple, int] = {}
    stackable_ench: Dict[tuple, Optional[dict]] = {}
    stackable_rar: Dict[tuple, str] = {}
    non_stackable_items: list = []  # list of (item_id, enchant, rarity)

    for slot, (item_id, count) in slots.items():
        ench = enchants.get(slot)
        rar = rarities.get(slot, 'common')
        cat = ITEM_CATEGORIES.get(item_id, '')
        if cat in NON_STACKABLE_CATEGORIES:
            # Each unit stays separate
            for _ in range(count):
                non_stackable_items.append((item_id, dict(ench) if ench else None, rar))
        else:
            key = make_stack_key(item_id, ench, rar)
            stackable_groups[key] = stackable_groups.get(key, 0) + count
            if key not in stackable_ench:
                stackable_ench[key] = dict(ench) if ench else None
            if key not in stackable_rar:
                stackable_rar[key] = normalize_rarity(rar)

    # Clear and rebuild
    slots.clear()
    enchants.clear()
    rarities.clear()

    idx = 0
    # Place stackable items first, sorted by item_id
    for key in sorted(stackable_groups, key=lambda k: k[0]):
        slots[idx] = (key[0], stackable_groups[key])
        ench = stackable_ench[key]
        rar = stackable_rar[key]
        if ench:
            enchants[idx] = ench
        rarities[idx] = rar
        idx += 1

    # Place non-stackable items, sorted by item_id
    non_stackable_items.sort(key=lambda x: x[0])
    for item_id, ench, rar in non_stackable_items:
        slots[idx] = (item_id, 1)
        if ench:
            enchants[idx] = ench
        rarities[idx] = normalize_rarity(rar)
        idx += 1
