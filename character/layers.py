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

HAIR_STYLES: list[str] = ['short', 'long', 'spiky', 'bald', 'ponytail', 'mohawk',
                          'mullet', 'curly', 'dreads', 'afro']
SHIRT_STYLES: list[str] = ['tunic', 'vest', 'tank', 'tube_top', 'bikini_top']
PANTS_STYLES: list[str] = ['pants', 'shorts', 'skirt', 'short_shorts']

SHOE_STYLES: list[str] = ['barefoot', 'shoes', 'boots', 'sandals']
SHOE_COLORS: list[Color] = [
    (80, 50, 30),      # Brown
    (40, 40, 40),      # Black
    (120, 80, 40),     # Tan
    (180, 40, 40),     # Red
    (60, 60, 160),     # Blue
    (200, 200, 200),   # White
]

ACCESSORY_STYLES: list[str] = ['none', 'skull', 'rainbow', 'no_sign', 'star', 'heart']


# ---------------------------------------------------------------------------
# Layer drawing functions
# ---------------------------------------------------------------------------

def draw_skin(color: Color) -> pygame.Surface:
    """Draw base body: head, torso, arms, legs in skin color."""
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
    # Torso (full body under clothes — visible with narrow tops)
    for y in range(12, 22):
        for x in range(5, 19):
            s.set_at((x, y), c4)
    # Arms from shoulder down to hands (extended up for shoulder coverage)
    for y in range(12, 23):
        for x in range(3, 6):
            s.set_at((x, y), c4)
        for x in range(19, 22):
            s.set_at((x, y), c4)
    # Full legs (upper thighs through feet — visible with short clothing)
    for y in range(22, 32):
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
    elif style == 'mullet':
        # Short on top, long in back
        for x in range(7, 17):
            s.set_at((x, 1), c4)
        for y in range(2, 6):
            s.set_at((6, y), c4)
            s.set_at((17, y), c4)
        # Long flow in back
        for y in range(5, 18):
            s.set_at((17, y), c4)
            s.set_at((18, y), c4)
    elif style == 'curly':
        # Fluffy curly mass around head
        for x in range(6, 18):
            s.set_at((x, 0), c4)
            s.set_at((x, 1), c4)
            s.set_at((x, 2), c4)
        for y in range(1, 10):
            s.set_at((5, y), c4)
            s.set_at((18, y), c4)
        # Curly bumps on sides
        for y in (2, 4, 6, 8):
            s.set_at((4, y), c4)
            s.set_at((19, y), c4)
    elif style == 'dreads':
        # Top covering
        for x in range(7, 17):
            s.set_at((x, 1), c4)
            s.set_at((x, 2), c4)
        # Hanging dread strands on sides
        for y in range(3, 18):
            s.set_at((6, y), c4)
            s.set_at((8, y), c4)
            s.set_at((15, y), c4)
            s.set_at((17, y), c4)
        # Outer strands
        for y in range(5, 14):
            s.set_at((5, y), c4)
            s.set_at((18, y), c4)
    elif style == 'afro':
        # Large round afro dome above and around head
        cx_a, cy_a = 12, 4
        for y in range(0, 12):
            for x in range(3, 21):
                dx = (x - cx_a) / 9.0
                dy = (y - cy_a) / 5.5
                if dx * dx + dy * dy <= 1.0:
                    # Leave the face visible
                    if 8 <= x <= 15 and y >= 5:
                        continue
                    s.set_at((x, y), c4)
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
    elif style == 'tube_top':
        # Horizontal band across chest
        for y in range(13, 17):
            for x in range(6, 18):
                s.set_at((x, y), c4)
    elif style == 'bikini_top':
        # Shoulder straps
        s.set_at((8, 12), c4)
        s.set_at((15, 12), c4)
        # Connector band
        for x in range(9, 15):
            s.set_at((x, 13), c4)
        # Left cup
        for y in range(13, 16):
            for x in range(7, 10):
                s.set_at((x, y), c4)
        # Right cup
        for y in range(13, 16):
            for x in range(14, 17):
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
    elif style == 'short_shorts':
        # Very short — waistband + minimal leg coverage
        for x in range(6, 18):
            s.set_at((x, 21), c4)
        for y in range(22, 24):
            for x in range(6, 11):
                s.set_at((x, y), c4)
            for x in range(13, 18):
                s.set_at((x, y), c4)
    return s


# ---------------------------------------------------------------------------
# Weapon overlay colour profiles — keyed by weapon_id substring match order.
# Each entry: (handle_color, head_color)
# Matched top-to-bottom; first match wins.
# ---------------------------------------------------------------------------
_WEAPON_PROFILES: list[tuple[str, Color, Color]] = [
    # --- swords (blade + guard + handle) ---
    ('iron_sword',   (80, 60, 30),  (200, 210, 230)),
    ('sword',        (100, 70, 35), (180, 180, 200)),
    # --- pickaxes (before axe so 'pickaxe' matches first) ---
    ('diamond_pickaxe',  (120, 80, 40), (140, 200, 255)),
    ('titanium_pickaxe', (120, 80, 40), (160, 170, 200)),
    ('iron_pickaxe',     (120, 80, 40), (170, 170, 190)),
    ('pickaxe',          (120, 80, 40), (160, 160, 170)),
    # --- axes ---
    ('diamond_axe',   (120, 80, 40), (140, 200, 255)),
    ('titanium_axe',  (120, 80, 40), (160, 170, 200)),
    ('iron_axe',      (120, 80, 40), (170, 170, 190)),
    ('axe',           (120, 80, 40), (180, 180, 200)),
    # --- mace ---
    ('mace',  (120, 80, 40), (160, 160, 175)),
    # --- spear ---
    ('spear', (120, 80, 40), (180, 190, 210)),
    # --- bone club ---
    ('bone_club', (200, 195, 180), (230, 225, 210)),
]


def _match_weapon(weapon_id: str) -> tuple[str, Color, Color]:
    """Return (weapon_type, handle_color, head_color) for a weapon_id."""
    for key, handle, head in _WEAPON_PROFILES:
        if key in weapon_id:
            # Determine broad type for drawing shape
            if 'sword' in key:
                return 'sword', handle, head
            if 'pickaxe' in key:
                return 'pickaxe', handle, head
            if 'axe' in key:
                return 'axe', handle, head
            if 'mace' in key:
                return 'mace', handle, head
            if 'spear' in key:
                return 'spear', handle, head
            if 'club' in key:
                return 'club', handle, head
    return 'generic', (120, 80, 40), (180, 180, 200)


def draw_weapon_overlay(weapon_id: str) -> pygame.Surface:
    """Draw a small weapon icon at the right-hand position.

    Each weapon type has a distinct silhouette and uses colour profiles
    derived from the matching item texture so the overlay is an accurate
    miniature representation of the equipped weapon.
    """
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    if not weapon_id:
        return s

    wtype, handle_c, head_c = _match_weapon(weapon_id)
    h4 = (*handle_c, 255)
    m4 = (*head_c, 255)
    # Slightly brighter version for edge highlights
    hi4 = (min(255, head_c[0] + 20),
           min(255, head_c[1] + 20),
           min(255, head_c[2] + 20), 255)

    if wtype == 'sword':
        # Blade — 2-pixel-wide, pointing up from hand
        for y in range(12, 22):
            s.set_at((21, y), m4)
            s.set_at((22, y), hi4)
        s.set_at((21, 11), hi4)  # tip
        # Guard
        guard = (min(255, handle_c[0] + 60),
                 min(255, handle_c[1] + 40), 30, 255)
        for x in range(20, 24):
            if x < 24:
                s.set_at((x, 22), guard)
        # Pommel
        s.set_at((21, 23), h4)
        s.set_at((22, 23), h4)
    elif wtype == 'axe':
        # Handle
        for y in range(15, 24):
            s.set_at((21, y), h4)
        # Axe head — triangular on one side
        for y in range(12, 17):
            s.set_at((22, y), m4)
            s.set_at((23, y), m4 if y < 16 else hi4)
        s.set_at((22, 11), hi4)  # top edge
    elif wtype == 'pickaxe':
        # Handle
        for y in range(16, 24):
            s.set_at((21, y), h4)
        # Pick head — horizontal pointed shape
        for x in range(19, 24):
            if x < 24:
                s.set_at((x, 14), m4)
                s.set_at((x, 15), m4)
        s.set_at((19, 13), hi4)  # pointed tip left
        s.set_at((23, 13), hi4)  # pointed tip right
    elif wtype == 'mace':
        # Handle
        for y in range(17, 24):
            s.set_at((21, y), h4)
        # Spiked head — rough circle
        for y in range(13, 17):
            for x in range(20, 24):
                if x < 24 and (x - 21) ** 2 + (y - 15) ** 2 < 5:
                    s.set_at((x, y), m4)
        # Spikes
        s.set_at((21, 12), hi4)
        s.set_at((19, 15), hi4)
        s.set_at((23, 15), hi4)
    elif wtype == 'spear':
        # Long shaft
        for y in range(10, 24):
            s.set_at((21, y), h4)
        # Spear tip
        s.set_at((21, 8), hi4)
        s.set_at((20, 9), m4)
        s.set_at((21, 9), m4)
        s.set_at((22, 9), m4)
    elif wtype == 'club':
        # Shaft
        for y in range(17, 24):
            s.set_at((21, y), h4)
        # Thick head
        for y in range(13, 18):
            for x in range(20, 23):
                s.set_at((x, y), m4)
    else:
        # Generic fallback
        for y in range(14, 24):
            s.set_at((21, y), m4)
    return s


# ---------------------------------------------------------------------------
# Shield overlay colour profiles
# ---------------------------------------------------------------------------
_SHIELD_PROFILES: list[tuple[str, Color, Color, Color]] = [
    # (key, fill_color, border_color, emblem_color)
    ('iron_shield', (160, 160, 180), (120, 120, 135), (200, 205, 220)),
    ('wood_shield', (130, 91, 30),   (80, 60, 40),    (180, 180, 200)),
]


def draw_shield_overlay(shield_id: str) -> pygame.Surface:
    """Draw a small shield icon at the left-hand position.

    Uses colour profiles matched to the item texture so the overlay
    accurately represents the equipped shield.
    """
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    if not shield_id:
        return s

    # Match profile
    fill = (100, 80, 60)
    border_c = (80, 60, 40)
    emblem_c = (200, 180, 60)
    for key, fc, bc, ec in _SHIELD_PROFILES:
        if key in shield_id:
            fill, border_c, emblem_c = fc, bc, ec
            break

    f4 = (*fill, 255)
    b4 = (*border_c, 255)
    e4 = (*emblem_c, 255)

    # Shield body (4x8 rectangle at left hand)
    for y in range(15, 23):
        for x in range(0, 4):
            s.set_at((x, y), f4)
    # Border edges
    for y in range(15, 23):
        s.set_at((0, y), b4)
        s.set_at((3, y), b4)
    for x in range(0, 4):
        s.set_at((x, 15), b4)
        s.set_at((x, 22), b4)
    # Center emblem (boss)
    s.set_at((1, 18), e4)
    s.set_at((2, 18), e4)
    s.set_at((1, 19), e4)
    s.set_at((2, 19), e4)
    return s


# ---------------------------------------------------------------------------
# Shoes
# ---------------------------------------------------------------------------

def draw_shoes(style: str, color: Color) -> pygame.Surface:
    """Draw shoes/boots/sandals on feet."""
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    if style == 'barefoot':
        return s
    c4 = (*color, 255)
    dark = (max(0, color[0] - 30), max(0, color[1] - 30),
            max(0, color[2] - 30), 255)
    if style == 'shoes':
        # Standard shoes covering feet
        for y in range(30, 32):
            for x in range(6, 11):
                s.set_at((x, y), c4)
            for x in range(13, 18):
                s.set_at((x, y), c4)
        # Sole
        for x in range(6, 11):
            s.set_at((x, 31), dark)
        for x in range(13, 18):
            s.set_at((x, 31), dark)
    elif style == 'boots':
        # Tall boots covering ankles
        for y in range(27, 32):
            for x in range(6, 11):
                s.set_at((x, y), c4)
            for x in range(13, 18):
                s.set_at((x, y), c4)
        # Boot top rim
        for x in range(6, 11):
            s.set_at((x, 27), dark)
        for x in range(13, 18):
            s.set_at((x, 27), dark)
        # Sole
        for x in range(6, 11):
            s.set_at((x, 31), dark)
        for x in range(13, 18):
            s.set_at((x, 31), dark)
    elif style == 'sandals':
        # Minimal sandals — thin soles and straps
        for x in range(7, 11):
            s.set_at((x, 31), c4)
        for x in range(13, 17):
            s.set_at((x, 31), c4)
        # Straps across top of foot
        s.set_at((7, 30), c4)
        s.set_at((10, 30), c4)
        s.set_at((13, 30), c4)
        s.set_at((16, 30), c4)
    return s


# ---------------------------------------------------------------------------
# Accessories — small emblem overlays drawn on the chest area
# ---------------------------------------------------------------------------

def draw_accessory(style: str) -> pygame.Surface:
    """Draw an accessory emblem over the shirt/chest area."""
    s = pygame.Surface((24, 32), pygame.SRCALPHA)
    if style == 'none':
        return s
    if style == 'skull':
        w = (240, 240, 240, 255)
        d = (60, 60, 60, 255)
        # Top of skull
        for x in range(10, 14):
            s.set_at((x, 14), w)
        # Sides + eye sockets
        s.set_at((9, 15), w)
        s.set_at((10, 15), d)
        s.set_at((11, 15), w)
        s.set_at((12, 15), d)
        s.set_at((13, 15), w)
        # Jaw
        for x in range(10, 13):
            s.set_at((x, 16), w)
        # Teeth
        s.set_at((10, 17), w)
        s.set_at((12, 17), w)
    elif style == 'rainbow':
        stripes = [
            (255, 0, 0, 255),
            (255, 165, 0, 255),
            (255, 255, 0, 255),
            (0, 200, 0, 255),
            (0, 100, 255, 255),
        ]
        for i, rc in enumerate(stripes):
            for x in range(9, 14):
                s.set_at((x, 14 + i), rc)
    elif style == 'no_sign':
        r = (220, 40, 40, 255)
        # Circle outline
        for x in range(9, 14):
            s.set_at((x, 14), r)
            s.set_at((x, 18), r)
        s.set_at((9, 15), r)
        s.set_at((13, 15), r)
        s.set_at((9, 16), r)
        s.set_at((13, 16), r)
        s.set_at((9, 17), r)
        s.set_at((13, 17), r)
        # Diagonal slash
        s.set_at((10, 15), r)
        s.set_at((11, 16), r)
        s.set_at((12, 17), r)
    elif style == 'star':
        y_c = (255, 220, 40, 255)
        s.set_at((11, 14), y_c)
        for x in range(9, 14):
            s.set_at((x, 15), y_c)
        for x in range(10, 13):
            s.set_at((x, 16), y_c)
        s.set_at((9, 17), y_c)
        s.set_at((13, 17), y_c)
    elif style == 'heart':
        r = (220, 40, 80, 255)
        s.set_at((10, 14), r)
        s.set_at((12, 14), r)
        s.set_at((9, 15), r)
        s.set_at((10, 15), r)
        s.set_at((11, 15), r)
        s.set_at((12, 15), r)
        s.set_at((13, 15), r)
        s.set_at((10, 16), r)
        s.set_at((11, 16), r)
        s.set_at((12, 16), r)
        s.set_at((11, 17), r)
    return s


# ---------------------------------------------------------------------------
# Composition — combine all layers into the final character surface
# ---------------------------------------------------------------------------

def compose_character(skin_color: Color, hair_style: str, hair_color: Color,
                      shirt_style: str, shirt_color: Color,
                      pants_style: str, pants_color: Color,
                      shoe_style: str = 'barefoot',
                      shoe_color: Color = (80, 50, 30),
                      accessory: str = 'none',
                      weapon_id: str = '', shield_id: str = '',
                      show_equipment: bool = True) -> pygame.Surface:
    """Compose all layers into a final 24x32 character surface."""
    result = pygame.Surface((24, 32), pygame.SRCALPHA)
    result.blit(draw_skin(skin_color), (0, 0))
    result.blit(draw_pants(pants_style, pants_color), (0, 0))
    result.blit(draw_shoes(shoe_style, shoe_color), (0, 0))
    result.blit(draw_shirt(shirt_style, shirt_color), (0, 0))
    result.blit(draw_accessory(accessory), (0, 0))
    result.blit(draw_hair(hair_style, hair_color), (0, 0))
    if show_equipment:
        if weapon_id:
            result.blit(draw_weapon_overlay(weapon_id), (0, 0))
        if shield_id:
            result.blit(draw_shield_overlay(shield_id), (0, 0))
    return result
