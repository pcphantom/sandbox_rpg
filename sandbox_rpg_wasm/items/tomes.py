"""Enchantment and transfer tome item definitions."""

ITEMS = [
    # -- Enchantment tomes (stat enhancement) --
    {'id': 'enchant_tome_1', 'name': 'Enchantment Tome I',   'desc': 'Enhance equipment +1.', 'category': 'enchant_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    {'id': 'enchant_tome_2', 'name': 'Enchantment Tome II',  'desc': 'Enhance equipment +2.', 'category': 'enchant_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    {'id': 'enchant_tome_3', 'name': 'Enchantment Tome III', 'desc': 'Enhance equipment +3.', 'category': 'enchant_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    {'id': 'enchant_tome_4', 'name': 'Enchantment Tome IV',  'desc': 'Enhance equipment +4.', 'category': 'enchant_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    {'id': 'enchant_tome_5', 'name': 'Enchantment Tome V',   'desc': 'Enhance equipment +5.', 'category': 'enchant_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    # -- Transfer / removal tomes --
    {'id': 'enchant_transfer_tome',  'name': 'Enchant Transfer Tome',  'desc': 'Transfer enchantment to another item.',   'category': 'transfer_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    {'id': 'enhance_transfer_tome',  'name': 'Enhance Transfer Tome',  'desc': 'Transfer enhancement to another item.',   'category': 'transfer_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    {'id': 'superior_transfer_tome', 'name': 'Superior Transfer Tome', 'desc': 'Transfer enchant & enhance to another.',  'category': 'transfer_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    {'id': 'disenchant_tome',        'name': 'Disenchant Tome',        'desc': 'Remove enchantment from an item.',        'category': 'transfer_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
    {'id': 'unenhance_tome',         'name': 'Unenhance Tome',         'desc': 'Remove enhancement from an item.',        'category': 'transfer_tome', 'damage': 0, 'harvest_bonus': 0, 'heal': 0, 'placeable': False, 'can_enchant': False, 'can_enhance': False, 'has_rarity': False},
]
