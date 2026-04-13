"""Loot tables for normal (non-ranged, non-boss) enemies.

Each table is a dict with:
    drop_chance  – probability (0.0–1.0) that any loot drops at all
    min_items    – minimum distinct item types dropped per kill
    max_items    – maximum distinct item types dropped per kill
    pool         – list of (item_id, weight, min_count, max_count)

Pool tuple format:
    item_id   – item identifier string
    weight    – relative selection weight (higher = more likely to be picked)
    min_count – minimum amount dropped if this item is selected
    max_count – maximum amount dropped if this item is selected
"""
from typing import Any, Dict

NORMAL_LOOT: Dict[str, Dict[str, Any]] = {
    # -- Tier 0: Easy -------------------------------------------------------
    'slime': {
        'drop_chance': 0.90,
        'min_items': 1,
        'max_items': 2,
        'pool': [
            ('berry',   40, 1, 3),
            ('stick',   20, 1, 2),
            ('cloth',   10, 1, 1),
        ],
    },
    'spider': {
        'drop_chance': 0.85,
        'min_items': 1,
        'max_items': 2,
        'pool': [
            ('cloth',   40, 1, 3),
            ('stick',   25, 0, 1),
            ('berry',   15, 1, 2),
        ],
    },
    # -- Tier 1: Medium -----------------------------------------------------
    'skeleton': {
        'drop_chance': 0.95,
        'min_items': 1,
        'max_items': 3,
        'pool': [
            ('bone',        35, 1, 3),
            ('stone',       25, 1, 3),
            ('arrow',       15, 1, 4),
            ('iron',         5, 1, 1),
            ('bone_club',    8, 1, 1),
            ('bow',          4, 1, 1),
        ],
    },
    'wolf': {
        'drop_chance': 0.90,
        'min_items': 1,
        'max_items': 2,
        'pool': [
            ('leather', 45, 1, 2),
            ('bone',    30, 0, 1),
            ('berry',   15, 1, 2),
        ],
    },
    'goblin': {
        'drop_chance': 0.95,
        'min_items': 1,
        'max_items': 3,
        'pool': [
            ('stone',       25, 2, 4),
            ('stick',       20, 2, 3),
            ('arrow',       18, 1, 3),
            ('iron',         8, 1, 1),
            ('bomb',         3, 1, 1),
            ('leather',     10, 1, 1),
            ('sword',        6, 1, 1),
            ('sling',        4, 1, 1),
        ],
    },
    'zombie': {
        'drop_chance': 0.90,
        'min_items': 1,
        'max_items': 3,
        'pool': [
            ('cloth',       30, 1, 2),
            ('bone',        30, 1, 2),
            ('berry',       12, 1, 2),
            ('bandage',      8, 1, 1),
            ('iron',         5, 1, 1),
            ('leather_armor', 4, 1, 1),
            ('iron_sword',   3, 1, 1),
        ],
    },
    # -- Tier 2: Hard -------------------------------------------------------
    'orc': {
        'drop_chance': 1.0,
        'min_items': 2,
        'max_items': 3,
        'enhanced_chance': 0.15,     # 15% chance one drop becomes +1..+5
        'pool': [
            ('iron',        25, 1, 2),
            ('leather',     20, 1, 2),
            ('bone',        15, 1, 3),
            ('stone',       10, 2, 3),
            ('health_potion', 5, 1, 1),
            ('mace',         8, 1, 1),
            ('iron_armor',   5, 1, 1),
            ('leather_armor', 6, 1, 1),
        ],
    },
    'wraith': {
        'drop_chance': 0.95,
        'min_items': 1,
        'max_items': 2,
        'enhanced_chance': 0.10,     # 10% chance one drop becomes +1..+5
        'pool': [
            ('cloth',           30, 2, 3),
            ('bone',            15, 1, 2),
            ('spell_regen_1',     6, 1, 1),
            ('spell_protection_1', 6, 1, 1),
            ('spell_regen_2',     2, 1, 1),
            ('spell_protection_2', 2, 1, 1),
            ('health_potion',    8, 1, 1),
            ('iron_sword',       5, 1, 1),
            ('iron_shield',      4, 1, 1),
        ],
    },
    # -- Tier 2.5: Ghost (non-solid) ----------------------------------------
    'ghost': {
        'drop_chance': 0.85,
        'min_items': 1,
        'max_items': 2,
        'pool': [
            ('cloth',           45, 1, 2),
            ('bone',            20, 1, 1),
            ('spell_protection_1', 5, 1, 1),
            ('spell_protection_2', 2, 1, 1),
            ('bandage',         15, 1, 1),
        ],
    },
    # -- Tier 3: Elite ------------------------------------------------------
    'dark_knight': {
        'drop_chance': 1.0,
        'min_items': 2,
        'max_items': 4,
        'enhanced_chance': 0.25,     # 25% chance one drop becomes +1..+5
        'pool': [
            ('iron',            20, 2, 4),
            ('bone',            10, 1, 2),
            ('cloth',            8, 1, 2),
            ('iron_sword',      10, 1, 1),
            ('iron_armor',       8, 1, 1),
            ('iron_shield',      8, 1, 1),
            ('mace',             6, 1, 1),
            ('iron_axe',         5, 1, 1),
            ('health_potion',    6, 1, 1),
            ('diamond',          4, 1, 1),
            ('spell_strength_1',  4, 1, 1),
            ('spell_strength_2',  2, 1, 1),
            ('spell_fireball',    2, 1, 1),
            ('spell_heal',        2, 1, 1),
            ('enchant_tome_1',   3, 1, 1),
            ('enchant_tome_2',   2, 1, 1),
            ('enchant_tome_3',   1, 1, 1),
        ],
    },
    'troll': {
        'drop_chance': 1.0,
        'min_items': 2,
        'max_items': 4,
        'enhanced_chance': 0.20,     # 20% chance one drop becomes +1..+5
        'pool': [
            ('stone',          20, 3, 5),
            ('iron',           20, 1, 3),
            ('leather',        15, 2, 3),
            ('bone',            8, 1, 2),
            ('mace',            8, 1, 1),
            ('iron_axe',        6, 1, 1),
            ('iron_armor',      5, 1, 1),
            ('health_potion',   6, 1, 1),
            ('iron_ore',        5, 1, 2),
            ('spell_regen_1',   2, 1, 1),
            ('spell_strength_1', 2, 1, 1),
            ('enchant_tome_1',  3, 1, 1),
            ('enchant_tome_2',  2, 1, 1),
        ],
    },
}
