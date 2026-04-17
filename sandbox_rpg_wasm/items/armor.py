"""Armor and shield item definitions."""

ITEMS = [
    {
        'id': 'leather_armor',
        'name': 'Leather Armor',
        'desc': 'Reduces damage taken by 3.',
        'category': 'armor',
        'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False,
        'can_enchant': True, 'can_enhance': False, 'has_rarity': True,
    },
    {
        'id': 'iron_armor',
        'name': 'Iron Armor',
        'desc': 'Reduces damage taken by 6.',
        'category': 'armor',
        'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False,
        'can_enchant': True, 'can_enhance': True, 'has_rarity': True,
    },
    {
        'id': 'wood_shield',
        'name': 'Wood Shield',
        'desc': 'Blocks some incoming damage.',
        'category': 'shield',
        'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False,
        'can_enchant': True, 'can_enhance': False, 'has_rarity': True,
    },
    {
        'id': 'iron_shield',
        'name': 'Iron Shield',
        'desc': 'Sturdy metal shield. -4 DR.',
        'category': 'shield',
        'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False,
        'can_enchant': True, 'can_enhance': True, 'has_rarity': True,
    },
]
