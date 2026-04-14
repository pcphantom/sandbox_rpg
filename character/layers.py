"""Character sprite layer rendering functions.

Each function draws onto a 24x32 SRCALPHA surface and returns it.
Layers compose bottom-to-top to create the full character sprite.
"""
import pygame
from typing import Tuple

Color = Tuple[int, int, int]

# ---------------------------------------------------------------------------
# Preset palettes — index into these from CharacterData
# ---------------------------------------------------------------------------
SKIN_COLORS: list[Color] = [
    (255, 224, 189),   # Light
    (241, 194, 125),   # Tan
    (198, 134, 66),    # Medium
    (141, 85, 36),     # Brown
    (80, 50, 30),      # Dark
    (255, 200, 200),   # Rosy
]

HAIR_COLORS: list[Color] = [
    (40, 30, 20),      # Black
    (80, 50, 30),      # Dark Brown
    (140, 90, 40),     # Brown
    (200, 160, 60),    # Blonde
    (180, 50, 30),     # Red
    (200, 200, 210),   # Silver
    (60, 60, 180),     # Blue
    (60, 160, 60),     # Green
]

SHIRT_COLORS: list[Color] = [
    (140, 60, 40),     # Brown (default tunic)
    (60, 80, 180),     # Blue
    (180, 40, 40),     # Red
    (40, 140, 60),     # Green
    (200, 200, 200),   # White
    (60, 60, 60),      # Black
    (180, 140, 60),    # Gold
    (140, 60, 180),    # Purple
]

PANTS_COLORS: list[Color] = [
    (60, 80, 180),     # Blue (default)
    (80, 60, 40),      # Brown
    (60, 60, 60),      # Black
    (40, 100, 40),     # Green
    (140, 60, 60),     # Red
    (200, 200, 200),   # White
]

HAIR_STYLES: list[str] = ['short', 'long', 'spiky', 'bald', 'ponytail', 'mohawk']
SHIRT_STYLES: list[str] = ['tunic', 'vest', 'tank']
PANTS_STYLES: list[str] = ['pants', 'shorts', 'skirt']


# ---------------------------------------------------------------------------
# Layer drawing functions
# ---------------------------------------------------------------------------

def draw_skin(color: Color) -> pygame.Surface:
    """Draw base body: head, arms, legs in skin color."""
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    c4 = (*color, 255)
    # Head (elliptical region rows 2-11, cols 7-16)
    cx, cy = 12, 7
    for y in range(2, 12):
        for x in range(7, 17):
            if (x - cx) ** 2 * 1.2 + (y - cy) ** 2 < 30:
                s.set_at((x, y), c4)
    # Eyes
    s.set_at((10, 6), (30, 30, 30, 255))
    s.set_at((14, 6), (30, 30, 30, 255))
    # Neck
    for y in range(10, 13):
        for x in range(10, 14):
            s.set_at((x, y), c4)
    # Arms
    for y in range(13, 22):
        for x in range(3, 6):
            s.set_at((x, y), c4)
        for x in range(19, 22):
            s.set_at((x, y), c4)
    # Hands
    for x in range(3, 6):
        s.set_at((x, 22), c4)
    for x in range(19, 22):
        s.set_at((x, 22), c4)
    # Legs (ankles/feet below pants)
    for y in range(28, 32):
        for x in range(7, 11):
            s.set_at((x, y), c4)
        for x in range(13, 17):
            s.set_at((x, y), c4)
    return s


def draw_hair(style: str, color: Color) -> pygame.Surface:
    """Draw hair on top of head area."""
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    if style == 'bald':
        return s
    c4 = (*color, 255)
    # Base top-of-head for all non-bald styles
    for x in range(7, 17):
        s.set_at((x, 2), c4)
        s.set_at((x, 3), c4)
    if style == 'short':
        for x in range(7, 17):
            s.set_at((x, 1), c4)
        for y in range(2, 6):
            s.set_at((6, y), c4)
            s.set_at((17, y), c4)
    elif style == 'long':
        for x in range(6, 18):
            s.set_at((x, 1), c4)
        for y in range(2, 14):
            s.set_at((5, y), c4)
            s.set_at((6, y), c4)
            s.set_at((17, y), c4)
            s.set_at((18, y), c4)
    elif style == 'spiky':
        for x in range(7, 17):
            s.set_at((x, 1), c4)
            s.set_at((x, 0), c4)
        for sx in (8, 10, 12, 14, 16):
            s.set_at((sx, 0), c4)
    elif style == 'ponytail':
        for x in range(7, 17):
            s.set_at((x, 1), c4)
        for y in range(2, 6):
            s.set_at((6, y), c4)
            s.set_at((17, y), c4)
        for y in range(5, 16):
            s.set_at((18, y), c4)
            s.set_at((19, y), c4)
    elif style == 'mohawk':
        for x in range(10, 14):
            s.set_at((x, 0), c4)
            s.set_at((x, 1), c4)
    return s


def draw_shirt(style: str, color: Color) -> pygame.Surface:
    """Draw shirt over the torso area."""
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    c4 = (*color, 255)
    if style == 'tunic':
        for y in range(12, 22):
            for x in range(5, 19):
                s.set_at((x, y), c4)
        for y in range(13, 19):
            for x in range(3, 6):
                s.set_at((x, y), c4)
            for x in range(19, 22):
                s.set_at((x, y), c4)
    elif style == 'vest':
        for y in range(12, 22):
            for x in range(5, 19):
                s.set_at((x, y), c4)
    elif style == 'tank':
        for y in range(12, 22):
            for x in range(7, 17):
                s.set_at((x, y), c4)
    return s


def draw_pants(style: str, color: Color) -> pygame.Surface:
    """Draw pants/shorts/skirt over the leg area."""
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    c4 = (*color, 255)
    if style == 'pants':
        for x in range(6, 18):
            s.set_at((x, 21), c4)
        for y in range(22, 30):
            for x in range(6, 11):
                s.set_at((x, y), c4)
            for x in range(13, 18):
                s.set_at((x, y), c4)
    elif style == 'shorts':
        for x in range(6, 18):
            s.set_at((x, 21), c4)
        for y in range(22, 26):
            for x in range(6, 11):
                s.set_at((x, y), c4)
            for x in range(13, 18):
                s.set_at((x, y), c4)
    elif style == 'skirt':
        for y in range(21, 27):
            wb = min(2, (y - 21) // 2)
            for x in range(6 - wb, 18 + wb):
                if 0 <= x < 24:
                    s.set_at((x, y), c4)
    return s


def draw_weapon_overlay(weapon_id: str) -> pygame.Surface:
    """Draw a small weapon icon at the right-hand position."""
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    if not weapon_id:
        return s
    blade = (180, 180, 200, 255)
    handle = (120, 80, 40, 255)
    if 'sword' in weapon_id:
        for y in range(12, 22):
            s.set_at((21, y), blade)
        s.set_at((20, 22), handle)
        s.set_at((22, 22), handle)
    elif 'axe' in weapon_id or 'pickaxe' in weapon_id:
        for y in range(14, 23):
            s.set_at((21, y), handle)
        for y in range(13, 18):
            s.set_at((22, y), blade)
            if 23 < 24:
                s.set_at((23, y), blade)
    elif 'mace' in weapon_id:
        for y in range(16, 23):
            s.set_at((21, y), handle)
        for y in range(13, 17):
            for x in range(20, min(24, 24)):
                s.set_at((x, y), (160, 160, 180, 255))
    elif 'spear' in weapon_id:
        for y in range(8, 23):
            s.set_at((21, y), handle)
        s.set_at((21, 7), blade)
        s.set_at((20, 8), blade)
        s.set_at((22, 8), blade)
    elif 'club' in weapon_id:
        for y in range(16, 23):
            s.set_at((21, y), (160, 140, 100, 255))
        for y in range(13, 17):
            for x in range(20, 23):
                s.set_at((x, y), (180, 160, 120, 255))
    else:
        for y in range(14, 23):
            s.set_at((21, y), blade)
    return s


def draw_shield_overlay(shield_id: str) -> pygame.Surface:
    """Draw a small shield icon at the left-hand position."""
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    if not shield_id:
        return s
    fill = (100, 80, 60, 255)
    if 'iron' in shield_id:
        fill = (160, 160, 180, 255)
    border = (80, 60, 40, 255)
    for y in range(15, 23):
        for x in range(0, 4):
            s.set_at((x, y), fill)
    for y in range(15, 23):
        s.set_at((0, y), border)
        s.set_at((3, y), border)
    for x in range(0, 4):
        s.set_at((x, 15), border)
        s.set_at((x, 22), border)
    # Center emblem
    s.set_at((1, 18), (200, 180, 60, 255))
    s.set_at((2, 18), (200, 180, 60, 255))
    s.set_at((1, 19), (200, 180, 60, 255))
    s.set_at((2, 19), (200, 180, 60, 255))
    return s


# ---------------------------------------------------------------------------
# Composition — combine all layers into the final character surface
# ---------------------------------------------------------------------------

def compose_character(skin_color: Color, hair_style: str, hair_color: Color,
                      shirt_style: str, shirt_color: Color,
                      pants_style: str, pants_color: Color,
                      weapon_id: str = '', shield_id: str = '',
                      show_equipment: bool = True) -> pygame.Surface:
    """Compose all layers into a final 24x32 character surface."""
    result = pygame.Surface((24, 32), pygame.SRCALPHA)
    result.blit(draw_skin(skin_color), (0, 0))
    result.blit(draw_pants(pants_style, pants_color), (0, 0))
    result.blit(draw_shirt(shirt_style, shirt_color), (0, 0))
    result.blit(draw_hair(hair_style, hair_color), (0, 0))
    if show_equipment:
        if weapon_id:
            result.blit(draw_weapon_overlay(weapon_id), (0, 0))
        if shield_id:
            result.blit(draw_shield_overlay(shield_id), (0, 0))
    return result
