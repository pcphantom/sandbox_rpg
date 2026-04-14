"""Crafting recipes — data-driven list of all craftable items.

Each recipe is a dict with the following keys:
    name   (str)  : Display name shown in the crafting panel.
    cost   (dict) : {item_id: amount_required, ...} materials consumed.
    gives  (str)  : item_id of the crafted result.
    count  (int)  : How many of 'gives' are produced.  Defaults to 1.
"""
from typing import Dict, List, Any

RECIPES: List[Dict[str, Any]] = [
    # =====================================================================
    # TOOLS & MELEE WEAPONS
    # =====================================================================
    {'name': 'Hammer',          'cost': {'wood': 3, 'iron': 2},                'gives': 'hammer'},
    {'name': 'Stone Axe',       'cost': {'wood': 3, 'stone': 2},               'gives': 'axe'},
    {'name': 'Wood Sword',      'cost': {'wood': 5, 'stick': 2, 'stone': 1},   'gives': 'sword'},
    {'name': 'Iron Axe',        'cost': {'iron': 3, 'wood': 2},                'gives': 'iron_axe'},
    {'name': 'Iron Sword',      'cost': {'iron': 4, 'wood': 2},                'gives': 'iron_sword'},
    {'name': 'Iron Mace',       'cost': {'iron': 5, 'wood': 1},                'gives': 'mace'},
    {'name': 'Spear',           'cost': {'stick': 4, 'stone': 2},              'gives': 'spear'},
    {'name': 'Bone Club',       'cost': {'bone': 3, 'stick': 1},               'gives': 'bone_club'},

    # =====================================================================
    # RANGED WEAPONS
    # =====================================================================
    {'name': 'Bow',             'cost': {'wood': 5, 'stick': 3},               'gives': 'bow'},
    {'name': 'Crossbow',        'cost': {'wood': 6, 'iron': 3, 'stick': 2},    'gives': 'crossbow'},
    {'name': 'Sling',           'cost': {'stick': 2, 'leather': 1},            'gives': 'sling'},

    # =====================================================================
    # AMMUNITION
    # =====================================================================
    {'name': 'Arrow x5',        'cost': {'stick': 2, 'stone': 1},              'gives': 'arrow',        'count': 5},
    {'name': 'Fire Arrow x3',   'cost': {'arrow': 3, 'torch': 1},              'gives': 'fire_arrow',   'count': 3},
    {'name': 'Bolt x5',         'cost': {'iron': 1, 'stick': 2},               'gives': 'bolt',         'count': 5},
    {'name': 'Rock Ammo x5',    'cost': {'stone': 3},                          'gives': 'rock_ammo',    'count': 5},
    {'name': 'Sling Bullet x3', 'cost': {'stone': 2, 'stick': 1},              'gives': 'sling_bullet', 'count': 3},

    # =====================================================================
    # ARMOR & SHIELDS
    # =====================================================================
    {'name': 'Leather Armor',   'cost': {'leather': 4, 'stick': 2},            'gives': 'leather_armor'},
    {'name': 'Iron Armor',      'cost': {'iron': 6, 'leather': 2},             'gives': 'iron_armor'},
    {'name': 'Wood Shield',     'cost': {'wood': 6, 'stick': 3},               'gives': 'wood_shield'},
    {'name': 'Iron Shield',     'cost': {'iron': 4, 'wood': 2},                'gives': 'iron_shield'},

    # =====================================================================
    # CONSUMABLES
    # =====================================================================
    {'name': 'Berry Pie',       'cost': {'berry': 5, 'wood': 1},               'gives': 'pie'},
    {'name': 'Bandage',         'cost': {'cloth': 2, 'berry': 1},              'gives': 'bandage'},
    {'name': 'Health Potion',   'cost': {'berry': 8, 'stone': 2, 'cloth': 1},  'gives': 'health_potion'},
    {'name': 'Antidote',        'cost': {'berry': 3, 'bone': 1},               'gives': 'antidote'},

    # =====================================================================
    # UTILITY / PLACEABLES
    # =====================================================================
    {'name': 'Campfire',        'cost': {'wood': 5, 'stone': 3},               'gives': 'campfire'},
    {'name': 'Torch',           'cost': {'wood': 2, 'stick': 1},               'gives': 'torch'},
    {'name': 'Spike Trap',      'cost': {'stick': 4, 'stone': 3},              'gives': 'trap'},
    {'name': 'Bed',             'cost': {'wood': 8, 'cloth': 3},               'gives': 'bed'},

    # =====================================================================
    # BUILDINGS
    # =====================================================================
    {'name': 'Wood Wall',       'cost': {'wood': 6},                            'gives': 'wall'},
    {'name': 'Stone Wall',      'cost': {'stone': 8},                           'gives': 'stone_wall_b'},
    {'name': 'Turret',          'cost': {'wood': 8, 'stone': 5, 'iron': 3},    'gives': 'turret'},
    {'name': 'Chest',           'cost': {'wood': 8, 'iron': 2},                'gives': 'chest'},
    {'name': 'Door',            'cost': {'wood': 4, 'iron': 1},                'gives': 'door'},

    # =====================================================================
    # MATERIAL PROCESSING
    # =====================================================================
    {'name': 'Sticks x5',      'cost': {'wood': 1},                            'gives': 'stick',        'count': 5},
    {'name': 'Iron Ingot',      'cost': {'stone': 4, 'wood': 2},               'gives': 'iron'},
    {'name': 'Iron from Ore',   'cost': {'iron_ore': 1, 'wood': 1},            'gives': 'iron'},
    {'name': 'Cloth',           'cost': {'stick': 3, 'berry': 1},              'gives': 'cloth'},
    {'name': 'Leather',         'cost': {'bone': 2, 'berry': 1},               'gives': 'leather'},

    # =====================================================================
    # THROWABLES
    # =====================================================================
    {'name': 'Bomb',            'cost': {'gunpowder': 2, 'iron': 1},           'gives': 'bomb'},
    {'name': 'Bomb x3',         'cost': {'gunpowder': 5, 'iron': 2},           'gives': 'bomb',         'count': 3},

    # =====================================================================
    # ENCHANTMENT
    # =====================================================================
    {'name': 'Enchantment Table', 'cost': {'iron': 6, 'diamond': 2, 'wood': 4}, 'gives': 'enchantment_table'},

    # =====================================================================
    # GEMS & ADVANCED MATERIALS
    # =====================================================================
    {'name': 'Brilliant Diamond', 'cost': {'diamond': 9}, 'gives': 'brilliant_diamond'},
    {'name': 'Titanium Ingot',    'cost': {'titanium_ore': 2, 'wood': 2}, 'gives': 'titanium_ingot'},

    # =====================================================================
    # TITANIUM & DIAMOND GEAR
    # =====================================================================
    {'name': 'Titanium Axe',  'cost': {'titanium_ingot': 5, 'wood': 2}, 'gives': 'titanium_axe'},
    {'name': 'Diamond Axe',   'cost': {'titanium_axe': 1, 'brilliant_diamond': 8}, 'gives': 'diamond_axe'},
    {'name': 'Greater Enchantment Table', 'cost': {'brilliant_diamond': 4, 'iron': 8, 'wood': 6}, 'gives': 'greater_enchantment_table'},
]
