"""Tool item definitions."""

ITEMS = [
    {
        'id': 'hammer',
        'name': 'Hammer',
        'desc': 'Repair structures. [F] near damaged.',
        'category': 'tool',
        'damage': 5, 'harvest_bonus': 0, 'heal': 0, 'placeable': False,
        'can_enchant': False, 'can_enhance': False, 'has_rarity': True,
    },
    {
        'id': 'pickaxe',
        'name': 'Stone Pickaxe',
        'desc': '+2 stone harvest yield.',
        'category': 'tool',
        'damage': 8, 'harvest_bonus': 2, 'heal': 0, 'placeable': False,
        'can_enchant': True, 'can_enhance': False, 'has_rarity': True,
        'harvest_type': 'stone',
    },
    {
        'id': 'iron_pickaxe',
        'name': 'Iron Pickaxe',
        'desc': '+4 stone harvest yield.',
        'category': 'tool',
        'damage': 15, 'harvest_bonus': 4, 'heal': 0, 'placeable': False,
        'can_enchant': True, 'can_enhance': True, 'has_rarity': True,
        'harvest_type': 'stone',
    },
    {
        'id': 'titanium_pickaxe',
        'name': 'Titanium Pickaxe',
        'desc': '+6 stone harvest yield.',
        'category': 'tool',
        'damage': 23, 'harvest_bonus': 6, 'heal': 0, 'placeable': False,
        'can_enchant': True, 'can_enhance': True, 'has_rarity': True,
        'harvest_type': 'stone',
    },
    {
        'id': 'diamond_pickaxe',
        'name': 'Diamond Pickaxe',
        'desc': '+8 stone harvest yield.',
        'category': 'tool',
        'damage': 30, 'harvest_bonus': 8, 'heal': 0, 'placeable': False,
        'can_enchant': True, 'can_enhance': True, 'has_rarity': True,
        'harvest_type': 'stone',
    },
]
