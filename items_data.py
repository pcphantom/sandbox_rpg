"""Item data, categories, recipes, mob definitions, and related constants."""
from typing import Dict, Tuple, List, Any

# Item data: id -> (name, description, damage, harvest_bonus, heal, placeable)
ITEM_DATA: Dict[str, Tuple[str, str, int, int, int, bool]] = {
    'wood':          ('Wood',          'Basic building material.',            0, 0,  0, False),
    'stone':         ('Stone',         'Hard and durable.',                   0, 0,  0, False),
    'stick':         ('Stick',         'A thin branch. Weak weapon.',         3, 0,  0, False),
    'berry':         ('Berry',         'Restores 15 HP. [F] to eat.',        0, 0, 15, False),
    'axe':           ('Stone Axe',     '+2 harvest yield. Decent weapon.',  12, 2,  0, False),
    'sword':         ('Wood Sword',    'Solid melee damage.',               20, 0,  0, False),
    'torch':         ('Torch',         'Hold for light. [F] to place.',      5, 0,  0, True),
    'campfire':      ('Campfire Kit',  'Heals nearby. [F] to place.',        0, 0,  0, True),
    'pie':           ('Berry Pie',     'Restores 40 HP. [F] to eat.',       0, 0, 40, False),
    'bandage':       ('Bandage',       'Restores 25 HP. [F] to use.',       0, 0, 25, False),
    'iron_sword':    ('Iron Sword',    'A strong melee blade.',             30, 0,  0, False),
    'spear':         ('Spear',         'Long reach melee weapon.',          18, 0,  0, False),
    'bow':           ('Bow',           'Fires arrows at range.',             0, 0,  0, False),
    'arrow':         ('Arrow',         'Ammunition for the bow.',            0, 0,  0, False),
    'sling':         ('Sling',         'Fires rocks at range.',              0, 0,  0, False),
    'rock_ammo':     ('Rock Ammo',     'Rough ammo for the sling.',          0, 0,  0, False),
    'sling_bullet':  ('Sling Bullet',  'Refined sling ammo. +5 dmg.',       0, 0,  0, False),
    'leather_armor': ('Leather Armor', 'Reduces damage taken by 3.',         0, 0,  0, False),
    'wood_shield':   ('Wood Shield',   'Blocks some incoming damage.',       0, 0,  0, False),
    'trap':          ('Spike Trap',    'Damages enemies. [F] to place.',     0, 0,  0, True),
    'bed':           ('Bed',           'Sleep at night. [F] to place.',      0, 0,  0, True),
}

ITEM_CATEGORIES: Dict[str, str] = {
    'wood': 'material', 'stone': 'material', 'stick': 'material',
    'berry': 'consumable', 'pie': 'consumable', 'bandage': 'consumable',
    'axe': 'weapon', 'sword': 'weapon', 'iron_sword': 'weapon', 'spear': 'weapon',
    'torch': 'placeable', 'campfire': 'placeable', 'trap': 'placeable', 'bed': 'placeable',
    'bow': 'ranged', 'sling': 'ranged',
    'arrow': 'ammo', 'rock_ammo': 'ammo', 'sling_bullet': 'ammo',
    'leather_armor': 'armor', 'wood_shield': 'shield',
}

RANGED_DATA: Dict[str, Dict[str, Any]] = {
    'bow':   {'damage': 18, 'range': 300.0, 'ammo': ['arrow'],
              'speed': 400.0, 'cooldown': 0.6},
    'sling': {'damage': 12, 'range': 250.0, 'ammo': ['rock_ammo', 'sling_bullet'],
              'speed': 350.0, 'cooldown': 0.5},
}

AMMO_BONUS_DAMAGE: Dict[str, int] = {
    'sling_bullet': 5, 'arrow': 0, 'rock_ammo': 0,
}

ARMOR_VALUES: Dict[str, int] = {
    'leather_armor': 3, 'wood_shield': 2,
}

RECIPES: List[Dict[str, Any]] = [
    {'name': 'Stone Axe',       'cost': {'wood': 3, 'stone': 2},             'gives': 'axe'},
    {'name': 'Wood Sword',      'cost': {'wood': 5, 'stick': 2, 'stone': 1}, 'gives': 'sword'},
    {'name': 'Iron Sword',      'cost': {'stone': 8, 'wood': 3},             'gives': 'iron_sword'},
    {'name': 'Spear',           'cost': {'stick': 4, 'stone': 2},            'gives': 'spear'},
    {'name': 'Bow',             'cost': {'wood': 5, 'stick': 3},             'gives': 'bow'},
    {'name': 'Arrow x5',        'cost': {'stick': 2, 'stone': 1},            'gives': 'arrow',        'count': 5},
    {'name': 'Sling',           'cost': {'stick': 2, 'stone': 2},            'gives': 'sling'},
    {'name': 'Rock Ammo x5',    'cost': {'stone': 3},                        'gives': 'rock_ammo',    'count': 5},
    {'name': 'Sling Bullet x3', 'cost': {'stone': 2, 'stick': 1},            'gives': 'sling_bullet', 'count': 3},
    {'name': 'Leather Armor',   'cost': {'berry': 3, 'stick': 5, 'wood': 3}, 'gives': 'leather_armor'},
    {'name': 'Wood Shield',     'cost': {'wood': 6, 'stick': 3},             'gives': 'wood_shield'},
    {'name': 'Campfire',        'cost': {'wood': 5, 'stone': 3},             'gives': 'campfire'},
    {'name': 'Torch',           'cost': {'wood': 2, 'stick': 1},             'gives': 'torch'},
    {'name': 'Berry Pie',       'cost': {'berry': 5, 'wood': 1},             'gives': 'pie'},
    {'name': 'Bandage',         'cost': {'stick': 3, 'berry': 2},            'gives': 'bandage'},
    {'name': 'Spike Trap',      'cost': {'stick': 4, 'stone': 3},            'gives': 'trap'},
    {'name': 'Bed',             'cost': {'wood': 8, 'stick': 4, 'berry': 2}, 'gives': 'bed'},
]

# Mob definitions: type -> stats
MOB_DATA: Dict[str, Dict[str, Any]] = {
    'slime': {
        'hp': 30, 'speed': 35, 'detection': 180, 'damage': 5, 'xp': 15,
        'solid': True,
        'drops': [('berry', 1, 3)],
    },
    'skeleton': {
        'hp': 60, 'speed': 50, 'detection': 220, 'damage': 10, 'xp': 35,
        'solid': True,
        'drops': [('stone', 2, 4), ('stick', 1, 2)],
    },
    'wolf': {
        'hp': 40, 'speed': 65, 'detection': 160, 'damage': 8, 'xp': 25,
        'solid': True,
        'drops': [('stick', 2, 3), ('berry', 0, 1)],
    },
    'goblin': {
        'hp': 50, 'speed': 45, 'detection': 200, 'damage': 12, 'xp': 40,
        'solid': True,
        'drops': [('stone', 2, 4), ('stick', 2, 3), ('arrow', 0, 2)],
    },
    'ghost': {
        'hp': 35, 'speed': 40, 'detection': 250, 'damage': 6, 'xp': 50,
        'solid': False,
        'drops': [],
    },
}
