"""Item data, categories, recipes, mob definitions, and related constants."""
from typing import Dict, Tuple, List, Any

# Item data: id -> (name, description, damage, harvest_bonus, heal, placeable)
ITEM_DATA: Dict[str, Tuple[str, str, int, int, int, bool]] = {
    # -- Materials --
    'wood':          ('Wood',          'Basic building material.',            0, 0,  0, False),
    'stone':         ('Stone',         'Hard and durable.',                   0, 0,  0, False),
    'stick':         ('Stick',         'A thin branch. Weak weapon.',         3, 0,  0, False),
    'iron':          ('Iron Ingot',    'Smelted metal for strong gear.',      0, 0,  0, False),
    'cloth':         ('Cloth',         'Woven fabric for crafting.',          0, 0,  0, False),
    'bone':          ('Bone',          'Dropped by skeletons.',               0, 0,  0, False),
    'leather':       ('Leather',       'Animal hide, used for armor.',        0, 0,  0, False),
    # -- Consumables --
    'berry':         ('Berry',         'Restores 15 HP. [F] to eat.',        0, 0, 15, False),
    'pie':           ('Berry Pie',     'Restores 40 HP. [F] to eat.',        0, 0, 40, False),
    'bandage':       ('Bandage',       'Restores 25 HP. [F] to use.',        0, 0, 25, False),
    'health_potion': ('Health Potion', 'Restores 80 HP. [F] to drink.',      0, 0, 80, False),
    'antidote':      ('Antidote',      'Cures poison. Restores 10 HP.',      0, 0, 10, False),
    # -- Spell books (consumable, cast on use) --
    'spell_fireball': ('Fireball Tome', 'Cast fireball at target. [F] use.', 0, 0,  0, False),
    # -- Melee weapons --
    'axe':           ('Stone Axe',     '+2 harvest yield. Decent weapon.',  12, 2,  0, False),
    'sword':         ('Wood Sword',    'Solid melee damage.',               20, 0,  0, False),
    'iron_sword':    ('Iron Sword',    'A strong melee blade.',             30, 0,  0, False),
    'spear':         ('Spear',         'Long reach melee weapon.',          18, 0,  0, False),
    'iron_axe':      ('Iron Axe',      '+4 harvest yield. Strong weapon.',  22, 4,  0, False),
    'mace':          ('Iron Mace',     'Heavy blunt weapon.',               26, 0,  0, False),
    'bone_club':     ('Bone Club',     'Crude but effective.',              14, 0,  0, False),
    # -- Ranged weapons --
    'bow':           ('Bow',           'Fires arrows at range.',             0, 0,  0, False),
    'crossbow':      ('Crossbow',      'Powerful, slow ranged weapon.',      0, 0,  0, False),
    'sling':         ('Sling',         'Fires rocks at range.',              0, 0,  0, False),
    # -- Ammo --
    'arrow':         ('Arrow',         'Ammunition for the bow.',            0, 0,  0, False),
    'fire_arrow':    ('Fire Arrow',    'Flaming arrow. +8 damage.',          0, 0,  0, False),
    'bolt':          ('Bolt',          'Crossbow ammunition.',               0, 0,  0, False),
    'rock_ammo':     ('Rock Ammo',     'Rough ammo for the sling.',          0, 0,  0, False),
    'sling_bullet':  ('Sling Bullet',  'Refined sling ammo. +5 dmg.',       0, 0,  0, False),
    # -- Armor --
    'leather_armor': ('Leather Armor', 'Reduces damage taken by 3.',         0, 0,  0, False),
    'iron_armor':    ('Iron Armor',    'Reduces damage taken by 6.',         0, 0,  0, False),
    'wood_shield':   ('Wood Shield',   'Blocks some incoming damage.',       0, 0,  0, False),
    'iron_shield':   ('Iron Shield',   'Sturdy metal shield. -4 DR.',       0, 0,  0, False),
    # -- Light sources / placeables --
    'torch':         ('Torch',         'Hold for light. [F] to place.',      5, 0,  0, True),
    'campfire':      ('Campfire Kit',  'Heals nearby. [F] to place.',        0, 0,  0, True),
    # -- Traps & structures --
    'trap':          ('Spike Trap',    'Damages enemies. [F] to place.',     0, 0,  0, True),
    'bed':           ('Bed',           'Sleep at night. [F] to place.',      0, 0,  0, True),
    # -- Buildings --
    'wall':          ('Wood Wall',     'A defensive wall. [F] to place.',    0, 0,  0, True),
    'stone_wall_b':  ('Stone Wall',    'Tough stone wall. [F] to place.',    0, 0,  0, True),
    'turret':        ('Turret',        'Auto-attacks enemies. [F] to place.',0, 0,  0, True),
    'chest':         ('Chest',         'Store items. [F] to place.',         0, 0,  0, True),
    'door':          ('Door',          'Walk-through barrier. [F] place.',   0, 0,  0, True),
}

ITEM_CATEGORIES: Dict[str, str] = {
    'wood': 'material', 'stone': 'material', 'stick': 'material',
    'iron': 'material', 'cloth': 'material', 'bone': 'material',
    'leather': 'material',
    'berry': 'consumable', 'pie': 'consumable', 'bandage': 'consumable',
    'health_potion': 'consumable', 'antidote': 'consumable',
    'spell_fireball': 'spell',
    'axe': 'weapon', 'sword': 'weapon', 'iron_sword': 'weapon',
    'spear': 'weapon', 'iron_axe': 'weapon', 'mace': 'weapon',
    'bone_club': 'weapon',
    'torch': 'placeable', 'campfire': 'placeable', 'trap': 'placeable',
    'bed': 'placeable', 'wall': 'placeable', 'stone_wall_b': 'placeable',
    'turret': 'placeable', 'chest': 'placeable', 'door': 'placeable',
    'bow': 'ranged', 'crossbow': 'ranged', 'sling': 'ranged',
    'arrow': 'ammo', 'fire_arrow': 'ammo', 'bolt': 'ammo',
    'rock_ammo': 'ammo', 'sling_bullet': 'ammo',
    'leather_armor': 'armor', 'iron_armor': 'armor',
    'wood_shield': 'shield', 'iron_shield': 'shield',
}

RANGED_DATA: Dict[str, Dict[str, Any]] = {
    'bow':      {'damage': 18, 'range': 300.0, 'ammo': ['arrow', 'fire_arrow'],
                 'speed': 400.0, 'cooldown': 0.6},
    'crossbow': {'damage': 28, 'range': 350.0, 'ammo': ['bolt'],
                 'speed': 500.0, 'cooldown': 1.2},
    'sling':    {'damage': 12, 'range': 250.0, 'ammo': ['rock_ammo', 'sling_bullet'],
                 'speed': 350.0, 'cooldown': 0.5},
}

AMMO_BONUS_DAMAGE: Dict[str, int] = {
    'sling_bullet': 5, 'arrow': 0, 'rock_ammo': 0,
    'fire_arrow': 8, 'bolt': 0,
}

ARMOR_VALUES: Dict[str, int] = {
    'leather_armor': 3, 'iron_armor': 6,
    'wood_shield': 2, 'iron_shield': 4,
}

# --------------------------------------------------------------------------
# RECIPES
# --------------------------------------------------------------------------
RECIPES: List[Dict[str, Any]] = [
    # -- Tools & melee weapons --
    {'name': 'Stone Axe',       'cost': {'wood': 3, 'stone': 2},               'gives': 'axe'},
    {'name': 'Wood Sword',      'cost': {'wood': 5, 'stick': 2, 'stone': 1},   'gives': 'sword'},
    {'name': 'Iron Axe',        'cost': {'iron': 3, 'wood': 2},                'gives': 'iron_axe'},
    {'name': 'Iron Sword',      'cost': {'iron': 4, 'wood': 2},                'gives': 'iron_sword'},
    {'name': 'Iron Mace',       'cost': {'iron': 5, 'wood': 1},                'gives': 'mace'},
    {'name': 'Spear',           'cost': {'stick': 4, 'stone': 2},              'gives': 'spear'},
    {'name': 'Bone Club',       'cost': {'bone': 3, 'stick': 1},               'gives': 'bone_club'},
    # -- Ranged weapons --
    {'name': 'Bow',             'cost': {'wood': 5, 'stick': 3},               'gives': 'bow'},
    {'name': 'Crossbow',        'cost': {'wood': 6, 'iron': 3, 'stick': 2},    'gives': 'crossbow'},
    {'name': 'Sling',           'cost': {'stick': 2, 'leather': 1},            'gives': 'sling'},
    # -- Ammunition --
    {'name': 'Arrow x5',        'cost': {'stick': 2, 'stone': 1},              'gives': 'arrow',        'count': 5},
    {'name': 'Fire Arrow x3',   'cost': {'arrow': 3, 'torch': 1},              'gives': 'fire_arrow',   'count': 3},
    {'name': 'Bolt x5',         'cost': {'iron': 1, 'stick': 2},               'gives': 'bolt',         'count': 5},
    {'name': 'Rock Ammo x5',    'cost': {'stone': 3},                          'gives': 'rock_ammo',    'count': 5},
    {'name': 'Sling Bullet x3', 'cost': {'stone': 2, 'stick': 1},              'gives': 'sling_bullet', 'count': 3},
    # -- Armor --
    {'name': 'Leather Armor',   'cost': {'leather': 4, 'stick': 2},            'gives': 'leather_armor'},
    {'name': 'Iron Armor',      'cost': {'iron': 6, 'leather': 2},             'gives': 'iron_armor'},
    {'name': 'Wood Shield',     'cost': {'wood': 6, 'stick': 3},               'gives': 'wood_shield'},
    {'name': 'Iron Shield',     'cost': {'iron': 4, 'wood': 2},                'gives': 'iron_shield'},
    # -- Consumables --
    {'name': 'Berry Pie',       'cost': {'berry': 5, 'wood': 1},               'gives': 'pie'},
    {'name': 'Bandage',         'cost': {'cloth': 2, 'berry': 1},              'gives': 'bandage'},
    {'name': 'Health Potion',   'cost': {'berry': 8, 'stone': 2, 'cloth': 1},  'gives': 'health_potion'},
    {'name': 'Antidote',        'cost': {'berry': 3, 'bone': 1},               'gives': 'antidote'},
    # -- Utility / placeables --
    {'name': 'Campfire',        'cost': {'wood': 5, 'stone': 3},               'gives': 'campfire'},
    {'name': 'Torch',           'cost': {'wood': 2, 'stick': 1},               'gives': 'torch'},
    {'name': 'Spike Trap',      'cost': {'stick': 4, 'stone': 3},              'gives': 'trap'},
    {'name': 'Bed',             'cost': {'wood': 8, 'cloth': 3},               'gives': 'bed'},
    # -- Buildings --
    {'name': 'Wood Wall',       'cost': {'wood': 6},                            'gives': 'wall'},
    {'name': 'Stone Wall',      'cost': {'stone': 8},                           'gives': 'stone_wall_b'},
    {'name': 'Turret',          'cost': {'wood': 8, 'stone': 5, 'iron': 3},    'gives': 'turret'},
    {'name': 'Chest',           'cost': {'wood': 8, 'iron': 2},                'gives': 'chest'},
    {'name': 'Door',            'cost': {'wood': 4, 'iron': 1},                'gives': 'door'},
    # -- Material processing --
    {'name': 'Iron Ingot',      'cost': {'stone': 4, 'wood': 2},               'gives': 'iron'},
    {'name': 'Cloth',           'cost': {'stick': 3, 'berry': 1},              'gives': 'cloth'},
    {'name': 'Leather',         'cost': {'bone': 2, 'berry': 1},               'gives': 'leather'},
]

# --------------------------------------------------------------------------
# MOB DEFINITIONS
# --------------------------------------------------------------------------
MOB_DATA: Dict[str, Dict[str, Any]] = {
    'slime': {
        'hp': 30, 'speed': 35, 'detection': 180, 'damage': 5, 'xp': 15,
        'solid': True, 'ranged': False,
        'drops': [('berry', 1, 3)],
    },
    'skeleton': {
        'hp': 60, 'speed': 50, 'detection': 220, 'damage': 10, 'xp': 35,
        'solid': True, 'ranged': False,
        'drops': [('stone', 1, 3), ('bone', 1, 2)],
    },
    'wolf': {
        'hp': 40, 'speed': 65, 'detection': 160, 'damage': 8, 'xp': 25,
        'solid': True, 'ranged': False,
        'drops': [('leather', 1, 2), ('bone', 0, 1)],
    },
    'goblin': {
        'hp': 50, 'speed': 45, 'detection': 200, 'damage': 12, 'xp': 40,
        'solid': True, 'ranged': False,
        'drops': [('stone', 2, 4), ('stick', 2, 3), ('arrow', 0, 2)],
    },
    'ghost': {
        'hp': 35, 'speed': 40, 'detection': 250, 'damage': 6, 'xp': 50,
        'solid': False, 'ranged': False,
        'drops': [('cloth', 1, 2)],
    },
    'spider': {
        'hp': 25, 'speed': 55, 'detection': 140, 'damage': 7, 'xp': 20,
        'solid': True, 'ranged': False,
        'drops': [('cloth', 1, 3), ('stick', 0, 1)],
    },
    'orc': {
        'hp': 90, 'speed': 38, 'detection': 180, 'damage': 16, 'xp': 60,
        'solid': True, 'ranged': False,
        'drops': [('iron', 1, 2), ('leather', 1, 2), ('bone', 1, 3)],
    },
    'dark_knight': {
        'hp': 120, 'speed': 42, 'detection': 200, 'damage': 20, 'xp': 80,
        'solid': True, 'ranged': False,
        'drops': [('iron', 2, 4), ('bone', 1, 2), ('cloth', 1, 2)],
    },
    # -- New enemies --
    'zombie': {
        'hp': 70, 'speed': 30, 'detection': 160, 'damage': 14, 'xp': 35,
        'solid': True, 'ranged': False,
        'drops': [('cloth', 1, 2), ('bone', 1, 2)],
    },
    'wraith': {
        'hp': 55, 'speed': 52, 'detection': 280, 'damage': 10, 'xp': 55,
        'solid': False, 'ranged': False,
        'drops': [('cloth', 2, 3)],
    },
    'troll': {
        'hp': 150, 'speed': 28, 'detection': 160, 'damage': 22, 'xp': 75,
        'solid': True, 'ranged': False,
        'drops': [('stone', 3, 5), ('iron', 1, 3), ('leather', 2, 3)],
    },
    # -- Ranged enemies (appear after Day 3) --
    'skeleton_archer': {
        'hp': 50, 'speed': 35, 'detection': 260, 'damage': 8, 'xp': 45,
        'solid': True, 'ranged': True,
        'ranged_damage': 12, 'ranged_range': 250.0, 'ranged_cooldown': 2.0,
        'ranged_speed': 350.0,
        'drops': [('bone', 1, 2), ('arrow', 1, 3)],
    },
    'goblin_shaman': {
        'hp': 45, 'speed': 32, 'detection': 240, 'damage': 6, 'xp': 50,
        'solid': True, 'ranged': True,
        'ranged_damage': 15, 'ranged_range': 220.0, 'ranged_cooldown': 2.5,
        'ranged_speed': 300.0,
        'drops': [('stick', 2, 3), ('cloth', 1, 2), ('berry', 1, 3)],
    },
    # -- Boss mobs (glow, drop spell books) --
    'boss_golem': {
        'hp': 400, 'speed': 22, 'detection': 300, 'damage': 35, 'xp': 250,
        'solid': True, 'ranged': False, 'boss': True,
        'glow_color': (255, 60, 60),
        'drops': [('iron', 4, 8), ('stone', 5, 10), ('spell_fireball', 1, 1)],
    },
    'boss_lich': {
        'hp': 300, 'speed': 35, 'detection': 350, 'damage': 28, 'xp': 300,
        'solid': True, 'ranged': True, 'boss': True,
        'glow_color': (200, 60, 255),
        'ranged_damage': 25, 'ranged_range': 300.0, 'ranged_cooldown': 1.8,
        'ranged_speed': 400.0,
        'drops': [('bone', 5, 8), ('cloth', 3, 5), ('spell_fireball', 1, 1)],
    },
}

# Mobs that can appear in night waves, ordered by difficulty tier
WAVE_MOB_TIERS: List[List[str]] = [
    ['slime', 'spider'],                            # tier 0 -- easy
    ['skeleton', 'wolf', 'goblin', 'zombie'],       # tier 1 -- medium
    ['orc', 'wraith'],                              # tier 2 -- hard
    ['dark_knight', 'troll'],                       # tier 3 -- elite
]

# Ranged enemies that join waves after RANGED_ENEMY_START_DAY
WAVE_RANGED_MOBS: List[str] = ['skeleton_archer', 'goblin_shaman']

# Boss mobs that can spawn during waves
WAVE_BOSS_MOBS: List[str] = ['boss_golem', 'boss_lich']

# Spell data for spell items
SPELL_DATA: Dict[str, Dict[str, Any]] = {
    'spell_fireball': {
        'name': 'Fireball',
        'damage': 60,
        'radius': 80.0,
        'speed': 350.0,
        'range': 400.0,
        'color': (255, 120, 30),
    },
}
