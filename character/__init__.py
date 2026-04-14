"""Character customization package — layered sprite composition and generator UI."""
from character.layers import (
    compose_character,
    SKIN_COLORS, HAIR_COLORS, SHIRT_COLORS, PANTS_COLORS,
    HAIR_STYLES, SHIRT_STYLES, PANTS_STYLES,
    draw_weapon_overlay, draw_shield_overlay,
)
from character.generator import CharacterData, CharacterGenerator

__all__ = [
    'compose_character',
    'SKIN_COLORS', 'HAIR_COLORS', 'SHIRT_COLORS', 'PANTS_COLORS',
    'HAIR_STYLES', 'SHIRT_STYLES', 'PANTS_STYLES',
    'draw_weapon_overlay', 'draw_shield_overlay',
    'CharacterData', 'CharacterGenerator',
]
