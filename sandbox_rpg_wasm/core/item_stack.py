"""Centralised item-identity and stacking logic.

Every piece of code that compares, stacks, transfers, or sorts items
MUST use the helpers in this module so behaviour is consistent across
Inventory, Storage, ChestUI, save/load, and cave snapshots.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple


# ── rarity normalisation ──────────────────────────────────────────────

def normalize_rarity(rarity: str) -> str:
    """Return the canonical rarity string.

    Every item always has a rarity — ``'common'`` is the baseline.
    """
    if not rarity:
        return 'common'
    return rarity


# ── identity comparison ───────────────────────────────────────────────

def items_match(item_id_a: str, ench_a: Optional[dict],
                rar_a: str,
                item_id_b: str, ench_b: Optional[dict],
                rar_b: str) -> bool:
    """Return ``True`` when two items are the same for stacking purposes.

    Compares item_id, enchantment dict, and *normalised* rarity.
    """
    if item_id_a != item_id_b:
        return False
    if ench_a != ench_b:
        return False
    if normalize_rarity(rar_a) != normalize_rarity(rar_b):
        return False
    return True


def make_stack_key(item_id: str, ench: Optional[dict],
                   rarity: str) -> tuple:
    """Return a hashable key suitable for grouping identical items.

    Used by sort/merge logic to bucket items that should combine.
    """
    ench_key = (ench['type'], ench['level']) if ench else None
    return (item_id, ench_key, normalize_rarity(rarity))


# ── container helpers ─────────────────────────────────────────────────

def add_to_slots(slots: Dict[int, Tuple[str, int]],
                 enchants: Dict[int, dict],
                 rarities: Dict[int, str],
                 capacity: int,
                 item_id: str,
                 enchant: Optional[dict],
                 rarity: str = 'common',
                 count: int = 1,
                 non_stackable: bool = False) -> int:
    """Add *count* of an item to a slot-dict container.

    Stacks with an existing slot only when item_id + enchant + rarity all
    match (using normalised rarity).  Non-stackable items always get their
    own slot (one unit each).

    Returns the number of items that could NOT be placed (overflow).
    """
    norm_rar = normalize_rarity(rarity)

    if non_stackable:
        placed = 0
        for _ in range(count):
            for i in range(capacity):
                if i not in slots:
                    slots[i] = (item_id, 1)
                    if enchant:
                        enchants[i] = dict(enchant)
                    rarities[i] = norm_rar
                    placed += 1
                    break
            else:
                return count - placed
        return 0

    # Stackable — find matching stack
    for slot, (iid, c) in slots.items():
        if iid != item_id:
            continue
        slot_ench = enchants.get(slot)
        slot_rar = rarities.get(slot, 'common')
        if slot_ench != enchant:
            continue
        if slot_rar != norm_rar:
            continue
        slots[slot] = (iid, c + count)
        return 0

    # No matching stack — first empty slot
    for i in range(capacity):
        if i not in slots:
            slots[i] = (item_id, count)
            if enchant:
                enchants[i] = dict(enchant)
            rarities[i] = norm_rar
            return 0
    return count


def remove_from_slots(slots: Dict[int, Tuple[str, int]],
                      enchants: Dict[int, dict],
                      rarities: Dict[int, str],
                      item_id: str,
                      count: int,
                      enchant: Optional[dict] = None,
                      rarity: str = 'common',
                      match_metadata: bool = False) -> bool:
    """Remove *count* of *item_id* from a slot-dict container.

    When *match_metadata* is ``True``, only removes from a slot whose
    enchant and normalised rarity match the supplied values.  When
    ``False`` (default, for backward compat), removes from the first
    slot with the matching item_id regardless of metadata.

    Returns ``True`` on success, ``False`` if not enough items found.
    """
    for slot, (iid, c) in list(slots.items()):
        if iid != item_id:
            continue
        if match_metadata:
            if enchants.get(slot) != enchant:
                continue
            if rarities.get(slot, 'common') != rarity:
                continue
        if c > count:
            slots[slot] = (iid, c - count)
            return True
        elif c == count:
            del slots[slot]
            enchants.pop(slot, None)
            rarities.pop(slot, 'common')
            return True
    return False


def sort_slots(slots: Dict[int, Tuple[str, int]],
               enchants: Dict[int, dict],
               rarities: Dict[int, str]) -> None:
    """Merge duplicate stacks and compact into contiguous slot indices.

    Mutates the three dicts in-place.
    """
    # Group by identity
    groups: Dict[tuple, int] = {}
    group_ench: Dict[tuple, Optional[dict]] = {}
    group_rar: Dict[tuple, str] = {}
    for slot, (item_id, count) in slots.items():
        ench = enchants.get(slot)
        rar = rarities.get(slot, 'common')
        key = make_stack_key(item_id, ench, rar)
        groups[key] = groups.get(key, 0) + count
        if key not in group_ench:
            group_ench[key] = dict(ench) if ench else None
        if key not in group_rar:
            group_rar[key] = rar

    # Clear and rebuild
    slots.clear()
    enchants.clear()
    rarities.clear()
    idx = 0
    for key in sorted(groups, key=lambda k: k[0]):
        slots[idx] = (key[0], groups[key])
        ench = group_ench[key]
        rar = group_rar[key]
        if ench:
            enchants[idx] = ench
        rarities[idx] = rar
        idx += 1


def transfer_slot(src_slots: Dict[int, Tuple[str, int]],
                  src_enchants: Dict[int, dict],
                  src_rarities: Dict[int, str],
                  src_slot: int,
                  dst_slots: Dict[int, Tuple[str, int]],
                  dst_enchants: Dict[int, dict],
                  dst_rarities: Dict[int, str],
                  dst_capacity: int) -> bool:
    """Move the entire contents of *src_slot* into the destination container.

    Uses ``add_to_slots`` for proper stacking.  On partial overflow the
    remaining items stay in the source slot with their metadata intact.

    Returns ``True`` if the source slot was fully emptied.
    """
    if src_slot not in src_slots:
        return False

    item_id, count = src_slots[src_slot]
    ench = src_enchants.get(src_slot)
    rar = src_rarities.get(src_slot, 'common')

    overflow = add_to_slots(dst_slots, dst_enchants, dst_rarities,
                            dst_capacity, item_id, ench, rar, count)

    if overflow == 0:
        del src_slots[src_slot]
        src_enchants.pop(src_slot, None)
        src_rarities.pop(src_slot, 'common')
        return True
    else:
        src_slots[src_slot] = (item_id, overflow)
        # Metadata stays — we never popped it
        return False


def transfer_all(src_slots: Dict[int, Tuple[str, int]],
                 src_enchants: Dict[int, dict],
                 src_rarities: Dict[int, str],
                 dst_slots: Dict[int, Tuple[str, int]],
                 dst_enchants: Dict[int, dict],
                 dst_rarities: Dict[int, str],
                 dst_capacity: int) -> None:
    """Move every item from *src* into *dst*, preserving metadata.

    Items that don't fit stay in the source.
    """
    for slot in list(src_slots.keys()):
        transfer_slot(src_slots, src_enchants, src_rarities, slot,
                      dst_slots, dst_enchants, dst_rarities, dst_capacity)
