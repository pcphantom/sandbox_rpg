"""Loot tables for ranged enemies.

Same format as normal.py tables.

Pool tuple format: (item_id, weight, min_count, max_count)
    item_id   – item identifier string
    weight    – relative selection weight (higher = more likely to be picked)
    min_count – minimum amount dropped if this item is selected
    max_count – maximum amount dropped if this item is selected
"""
from typing import Any, Dict

RANGED_LOOT: Dict[str, Dict[str, Any]] = {
    'skeleton_archer': {
        'drop_chance': 0.95,
        'min_items': 1,
        'max_items': 3,
        'pool': [
            ('bone',        35, 1, 2),
            ('arrow',       30, 2, 5),
            ('fire_arrow',  10, 1, 2),
            ('bow',          5, 1, 1),
            ('stone',       10, 1, 2),
            ('iron',         5, 1, 1),
        ],
    },
    'goblin_shaman': {
        'drop_chance': 0.95,
        'min_items': 1,
        'max_items': 3,
        'pool': [
            ('stick',              25, 2, 3),
            ('cloth',              20, 1, 2),
            ('berry',              15, 1, 3),
            ('health_potion',       8, 1, 1),
            ('spell_regen_1',        5, 1, 1),
            ('spell_regen_2',        2, 1, 1),
            ('spell_strength_1',     5, 1, 1),
            ('spell_strength_2',     2, 1, 1),
            ('spell_protection_1',   5, 1, 1),
            ('spell_protection_2',   2, 1, 1),
            ('spell_heal',          3, 1, 1),
            ('spell_heal_2',        1, 1, 1),
            ('enchant_tome_1',      2, 1, 1),
        ],
    },
}
