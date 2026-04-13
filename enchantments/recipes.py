"""Enchantment table combination recipes.

The enchantment table has 9 input slots. Valid combinations:
1. Enchantment Tome I-V + base/enhanced equipment → stat enhanced equipment (+1..+5)
2. Elemental spell book + equipment → elemental enchant on that item
3. Protection spell book + armor/shield → protection enchant on that item
4. Tome + Spell Book + Equipment → stat + enchant at once
5. 9 identical items → 1 item at next rarity tier (rarity upgrade)
6. Enchant Transfer Tome + enchanted equip + blank equip → transfer enchant
7. Enhancement Transfer Tome + enhanced equip + non-enhanced equip → transfer +N
8. Superior Transfer Tome + source equip + blank equip → transfer both
9. Disenchant Tome + enchanted equip → remove enchant
10. Unenhance Tome + enhanced equip → revert to base item

Returns (result_item_id, result_enchant_or_None, consumed_slot_indices).
"""
from typing import Dict, List, Optional, Tuple, Any

from data import ITEM_DATA, ITEM_CATEGORIES, CAN_ENCHANT, CAN_ENHANCE, HAS_RARITY
from data.quality import next_rarity

from enchantments.effects import SPELL_TO_ENCHANT

# Transfer / removal tome item_ids
_TRANSFER_TOMES = {
    'enchant_transfer_tome', 'enhance_transfer_tome',
    'superior_transfer_tome', 'disenchant_tome', 'unenhance_tome',
}


def _get_base_item(item_id: str) -> Optional[str]:
    """Strip +N suffix to get base item id, or None if not enhanceable."""
    # Check if item itself is enhanceable
    if CAN_ENHANCE.get(item_id, False):
        # It's a base item or an enhanced variant — find root base
        for base_id, flag in CAN_ENHANCE.items():
            if not flag:
                continue
            if item_id == base_id:
                return base_id
            if (item_id.startswith(base_id + '_')
                    and item_id[len(base_id) + 1:].isdigit()):
                return base_id
    return None


def _get_current_level(item_id: str) -> int:
    """Return current +N level (0 for base item)."""
    for base_id, flag in CAN_ENHANCE.items():
        if not flag:
            continue
        if item_id.startswith(base_id + '_'):
            suffix = item_id[len(base_id) + 1:]
            if suffix.isdigit():
                return int(suffix)
    return 0


def _get_tome_level(item_id: str) -> int:
    """Return tome level 1-5 from enchant_tome_N, or 0."""
    if item_id.startswith('enchant_tome_'):
        suffix = item_id[len('enchant_tome_'):]
        if suffix.isdigit():
            return int(suffix)
    return 0


def _get_spell_enchant_info(item_id: str) -> Optional[Tuple[str, int]]:
    """Return (enchant_type, level) from a spell book item_id, or None.

    e.g. 'spell_fireball_2' → ('fire', 2), 'spell_protection_1' → ('protection', 1)
    """
    for prefix, etype in SPELL_TO_ENCHANT.items():
        if item_id == prefix:
            return (etype, 1)
        if item_id.startswith(prefix + '_'):
            suffix = item_id[len(prefix) + 1:]
            if suffix.isdigit():
                return (etype, int(suffix))
    return None


def _is_equipment(item_id: str) -> bool:
    """Check if item can receive an enchantment (reads can_enchant flag)."""
    return CAN_ENCHANT.get(item_id, False)


def _is_rarity_eligible(item_id: str) -> bool:
    """Check if item can have rarity (reads has_rarity flag)."""
    return HAS_RARITY.get(item_id, False)


def _is_armor_or_shield(item_id: str) -> bool:
    cat = ITEM_CATEGORIES.get(item_id, '')
    return cat in ('armor', 'shield')


def _is_weapon_or_ranged(item_id: str) -> bool:
    cat = ITEM_CATEGORIES.get(item_id, '')
    return cat in ('weapon', 'ranged')


def _is_placeable(item_id: str) -> bool:
    cat = ITEM_CATEGORIES.get(item_id, '')
    return cat == 'placeable'


def _is_enhanced(item_id: str) -> bool:
    """Check if item has a +N enhancement suffix."""
    return _get_base_item(item_id) is not None and _get_current_level(item_id) > 0


def try_combine(slots: Dict[int, Tuple[str, int]],
                slot_enchantments: Dict[int, Dict[str, Any]],
                slot_rarities: Optional[Dict[int, str]] = None
                ) -> Optional[Dict[str, Any]]:
    """Try to find a valid enchantment combination from the table's slots.

    Parameters
    ----------
    slots : the 9-slot dict {slot_index: (item_id, count)}
    slot_enchantments : enchant overlays for the table slots
    slot_rarities : rarity overlays for the table slots

    Returns
    -------
    None if no valid combo, or a dict:
        {
            'result_item': str,           # resulting item_id
            'result_enchant': dict|None,  # {'type': str, 'level': int} or None
            'result_rarity': str,         # rarity string (always 'common' minimum)
            'consume': list[int],         # slot indices consumed
            'source_enchant_slot': int|None, # slot of equipment that had enchant
        }
    """
    if slot_rarities is None:
        slot_rarities = {}

    filled = [(idx, iid) for idx, (iid, _count) in slots.items()]

    # === Recipe 5: 9-Identical-Item Rarity Upgrade ===
    if len(filled) == 9:
        result = _try_rarity_upgrade(filled, slot_enchantments, slot_rarities)
        if result is not None:
            return result

    if len(filled) < 2:
        return None

    # Separate items by type
    tomes = []           # (slot_idx, tome_level)
    spell_books = []     # (slot_idx, enchant_type, enchant_level)
    equipment = []       # (slot_idx, item_id)
    transfer_tomes = []  # (slot_idx, tome_item_id)

    for idx, iid in filled:
        if iid in _TRANSFER_TOMES:
            transfer_tomes.append((idx, iid))
            continue
        tome_lv = _get_tome_level(iid)
        if tome_lv > 0:
            tomes.append((idx, tome_lv))
            continue
        spell_info = _get_spell_enchant_info(iid)
        if spell_info is not None:
            spell_books.append((idx, spell_info[0], spell_info[1]))
            continue
        if _is_equipment(iid):
            equipment.append((idx, iid))

    # === Recipes 6-10: Transfer / Removal Tomes ===
    if len(transfer_tomes) == 1:
        tome_slot, tome_id = transfer_tomes[0]
        result = _try_transfer_recipe(
            tome_slot, tome_id, equipment,
            slot_enchantments, slot_rarities, filled
        )
        if result is not None:
            return result

    # === Combo 1: Stat Enhancement (Tome + Equipment) ===
    if len(tomes) == 1 and len(equipment) == 1 and len(spell_books) == 0:
        tome_slot, tome_lv = tomes[0]
        eq_slot, eq_id = equipment[0]
        base = _get_base_item(eq_id)
        if base is not None and 1 <= tome_lv <= 5:
            result_id = f'{base}_{tome_lv}'
            if result_id in ITEM_DATA:
                existing_enchant = slot_enchantments.get(eq_slot)
                existing_rarity = slot_rarities.get(eq_slot, 'common')
                return {
                    'result_item': result_id,
                    'result_enchant': existing_enchant,
                    'result_rarity': existing_rarity,
                    'consume': [tome_slot, eq_slot],
                    'source_enchant_slot': eq_slot if existing_enchant else None,
                }

    # === Combo 2: Spell Enchantment (Spell Book + Equipment) ===
    if len(spell_books) == 1 and len(equipment) == 1 and len(tomes) == 0:
        sp_slot, ench_type, ench_level = spell_books[0]
        eq_slot, eq_id = equipment[0]

        valid = False
        if ench_type in ('fire', 'ice', 'lightning', 'strength'):
            if _is_equipment(eq_id):
                valid = True
        elif ench_type == 'protection':
            if _is_armor_or_shield(eq_id) or _is_placeable(eq_id):
                valid = True
        elif ench_type == 'regen':
            if _is_armor_or_shield(eq_id) or _is_placeable(eq_id):
                valid = True

        if valid:
            new_enchant = {'type': ench_type, 'level': ench_level}
            existing_rarity = slot_rarities.get(eq_slot, 'common')
            return {
                'result_item': eq_id,
                'result_enchant': new_enchant,
                'result_rarity': existing_rarity,
                'consume': [sp_slot, eq_slot],
                'source_enchant_slot': eq_slot,
            }

    # === Combo 3: Tome + Spell Book + Equipment (stat + elemental at once) ===
    if len(tomes) == 1 and len(spell_books) == 1 and len(equipment) == 1:
        tome_slot, tome_lv = tomes[0]
        sp_slot, ench_type, ench_level = spell_books[0]
        eq_slot, eq_id = equipment[0]
        base = _get_base_item(eq_id)
        if base is not None and 1 <= tome_lv <= 5:
            result_id = f'{base}_{tome_lv}'
            if result_id in ITEM_DATA:
                valid = False
                if ench_type in ('fire', 'ice', 'lightning', 'strength') and _is_equipment(eq_id):
                    valid = True
                elif ench_type == 'protection' and (_is_armor_or_shield(eq_id) or _is_placeable(eq_id)):
                    valid = True
                elif ench_type == 'regen' and (_is_armor_or_shield(eq_id) or _is_placeable(eq_id)):
                    valid = True
                if valid:
                    new_enchant = {'type': ench_type, 'level': ench_level}
                    existing_rarity = slot_rarities.get(eq_slot, 'common')
                    return {
                        'result_item': result_id,
                        'result_enchant': new_enchant,
                        'result_rarity': existing_rarity,
                        'consume': [tome_slot, sp_slot, eq_slot],
                        'source_enchant_slot': eq_slot,
                    }

    return None


def _try_rarity_upgrade(filled: list, slot_enchantments: dict,
                        slot_rarities: dict) -> Optional[Dict[str, Any]]:
    """Check if all 9 filled slots are identical items for rarity upgrade."""
    # All items must have count == 1
    first_idx, first_id = filled[0]
    if not _is_rarity_eligible(first_id):
        return None

    first_enchant = slot_enchantments.get(first_idx)
    first_rarity = slot_rarities.get(first_idx, 'common')

    upgraded = next_rarity(first_rarity)
    if upgraded is None:
        return None  # already mythic, can't upgrade

    # Verify all 9 slots are identical
    all_indices = []
    for idx, iid in filled:
        if iid != first_id:
            return None
        ench = slot_enchantments.get(idx)
        rar = slot_rarities.get(idx, 'common')
        if ench != first_enchant:
            return None
        if rar != first_rarity:
            return None
        all_indices.append(idx)

    return {
        'result_item': first_id,
        'result_enchant': first_enchant,
        'result_rarity': upgraded,
        'consume': all_indices,
        'source_enchant_slot': None,
    }


def _try_transfer_recipe(tome_slot: int, tome_id: str,
                         equipment: list,
                         slot_enchantments: dict,
                         slot_rarities: dict,
                         filled: list) -> Optional[Dict[str, Any]]:
    """Handle transfer/removal tome recipes (6-10)."""

    # === Recipe 9: Disenchant Tome + enchanted equip → remove enchant ===
    if tome_id == 'disenchant_tome':
        if len(equipment) == 1 and len(filled) == 2:
            eq_slot, eq_id = equipment[0]
            existing_enchant = slot_enchantments.get(eq_slot)
            if existing_enchant:
                existing_rarity = slot_rarities.get(eq_slot, 'common')
                return {
                    'result_item': eq_id,
                    'result_enchant': None,
                    'result_rarity': existing_rarity,
                    'consume': [tome_slot, eq_slot],
                    'source_enchant_slot': None,
                }
        return None

    # === Recipe 10: Unenhance Tome + enhanced equip → revert to base ===
    if tome_id == 'unenhance_tome':
        if len(equipment) == 1 and len(filled) == 2:
            eq_slot, eq_id = equipment[0]
            base = _get_base_item(eq_id)
            if base is not None and _get_current_level(eq_id) > 0:
                existing_enchant = slot_enchantments.get(eq_slot)
                existing_rarity = slot_rarities.get(eq_slot, 'common')
                return {
                    'result_item': base,
                    'result_enchant': existing_enchant,
                    'result_rarity': existing_rarity,
                    'consume': [tome_slot, eq_slot],
                    'source_enchant_slot': eq_slot if existing_enchant else None,
                }
        return None

    # === Recipe 6: Enchant Transfer Tome + enchanted + non-enchanted ===
    if tome_id == 'enchant_transfer_tome':
        if len(equipment) == 2 and len(filled) == 3:
            eq_a_slot, eq_a_id = equipment[0]
            eq_b_slot, eq_b_id = equipment[1]
            ench_a = slot_enchantments.get(eq_a_slot)
            ench_b = slot_enchantments.get(eq_b_slot)
            # Identify source (has enchant) and target (no enchant)
            if ench_a and not ench_b:
                src_slot, src_id = eq_a_slot, eq_a_id
                tgt_slot, tgt_id = eq_b_slot, eq_b_id
                src_ench = ench_a
            elif ench_b and not ench_a:
                src_slot, src_id = eq_b_slot, eq_b_id
                tgt_slot, tgt_id = eq_a_slot, eq_a_id
                src_ench = ench_b
            else:
                return None  # both enchanted or neither

            # Validate enchant is compatible with target
            ench_type = src_ench.get('type', '')
            if ench_type in ('fire', 'ice', 'lightning', 'strength'):
                if not _is_equipment(tgt_id):
                    return None
            elif ench_type in ('protection', 'regen'):
                if not (_is_armor_or_shield(tgt_id) or _is_placeable(tgt_id)):
                    return None

            tgt_rarity = slot_rarities.get(tgt_slot, 'common')
            return {
                'result_item': tgt_id,
                'result_enchant': src_ench,
                'result_rarity': tgt_rarity,
                'consume': [tome_slot, src_slot, tgt_slot],
                'source_enchant_slot': None,
            }
        return None

    # === Recipe 7: Enhancement Transfer Tome + enhanced + non-enhanced ===
    if tome_id == 'enhance_transfer_tome':
        if len(equipment) == 2 and len(filled) == 3:
            eq_a_slot, eq_a_id = equipment[0]
            eq_b_slot, eq_b_id = equipment[1]
            lvl_a = _get_current_level(eq_a_id)
            lvl_b = _get_current_level(eq_b_id)
            base_a = _get_base_item(eq_a_id)
            base_b = _get_base_item(eq_b_id)
            # Identify source (enhanced) and target (non-enhanced, enhanceable)
            if lvl_a > 0 and lvl_b == 0 and base_b is not None:
                src_slot = eq_a_slot
                tgt_slot, tgt_id = eq_b_slot, eq_b_id
                transfer_level = lvl_a
                tgt_base = base_b
            elif lvl_b > 0 and lvl_a == 0 and base_a is not None:
                src_slot = eq_b_slot
                tgt_slot, tgt_id = eq_a_slot, eq_a_id
                transfer_level = lvl_b
                tgt_base = base_a
            else:
                return None

            result_id = f'{tgt_base}_{transfer_level}'
            if result_id not in ITEM_DATA:
                return None

            tgt_enchant = slot_enchantments.get(tgt_slot)
            tgt_rarity = slot_rarities.get(tgt_slot, 'common')
            return {
                'result_item': result_id,
                'result_enchant': tgt_enchant,
                'result_rarity': tgt_rarity,
                'consume': [tome_slot, src_slot, tgt_slot],
                'source_enchant_slot': tgt_slot if tgt_enchant else None,
            }
        return None

    # === Recipe 8: Superior Transfer Tome + source + blank target ===
    if tome_id == 'superior_transfer_tome':
        if len(equipment) == 2 and len(filled) == 3:
            eq_a_slot, eq_a_id = equipment[0]
            eq_b_slot, eq_b_id = equipment[1]
            ench_a = slot_enchantments.get(eq_a_slot)
            ench_b = slot_enchantments.get(eq_b_slot)
            lvl_a = _get_current_level(eq_a_id)
            lvl_b = _get_current_level(eq_b_id)

            # Source must have enchant or enhancement; target must have neither
            a_has = bool(ench_a) or lvl_a > 0
            b_has = bool(ench_b) or lvl_b > 0
            b_blank = not ench_b and lvl_b == 0
            a_blank = not ench_a and lvl_a == 0

            if a_has and b_blank:
                src_slot, src_id, src_ench, src_lvl = eq_a_slot, eq_a_id, ench_a, lvl_a
                tgt_slot, tgt_id = eq_b_slot, eq_b_id
            elif b_has and a_blank:
                src_slot, src_id, src_ench, src_lvl = eq_b_slot, eq_b_id, ench_b, lvl_b
                tgt_slot, tgt_id = eq_a_slot, eq_a_id
            else:
                return None

            # Build result item: apply enhancement to target if source has one
            result_id = tgt_id
            if src_lvl > 0:
                tgt_base = _get_base_item(tgt_id)
                if tgt_base is None:
                    return None  # target must be enhanceable for +N transfer
                result_id = f'{tgt_base}_{src_lvl}'
                if result_id not in ITEM_DATA:
                    return None

            # Validate enchant compatibility with target
            result_enchant = None
            if src_ench:
                ench_type = src_ench.get('type', '')
                if ench_type in ('fire', 'ice', 'lightning', 'strength'):
                    if not _is_equipment(tgt_id):
                        return None
                elif ench_type in ('protection', 'regen'):
                    if not (_is_armor_or_shield(tgt_id) or _is_placeable(tgt_id)):
                        return None
                result_enchant = src_ench

            tgt_rarity = slot_rarities.get(tgt_slot, 'common')
            return {
                'result_item': result_id,
                'result_enchant': result_enchant,
                'result_rarity': tgt_rarity,
                'consume': [tome_slot, src_slot, tgt_slot],
                'source_enchant_slot': None,
            }
        return None

    return None
