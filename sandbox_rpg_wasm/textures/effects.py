"""Projectile and enchantment texture generation."""
import random
import math
import pygame
from core.utils import hash_noise


def generate_projectile_arrow(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        # Shaft
        for i in range(6):
            s.set_at((1 + i, 4), (140, 100, 50, 255))
        # Tip
        s.set_at((7, 4), (200, 200, 220, 255))
        s.set_at((7, 3), (200, 200, 220, 255))
        return s
    return gen._get("proj_arrow", make)


def generate_projectile_rock(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        for y in range(2, 6):
            for x in range(2, 6):
                if (x - 4) ** 2 + (y - 4) ** 2 < 5:
                    s.set_at((x, y), (130, 130, 140, 255))
        return s
    return gen._get("proj_rock", make)


def generate_projectile_bolt(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        # Short thick bolt shaft
        for i in range(5):
            s.set_at((1 + i, 3), (140, 100, 50, 255))
            s.set_at((1 + i, 4), (140, 100, 50, 255))
        # Metal tip
        s.set_at((6, 3), (200, 200, 220, 255))
        s.set_at((6, 4), (200, 200, 220, 255))
        s.set_at((7, 3), (180, 180, 200, 255))
        # Fletching
        s.set_at((1, 2), (100, 100, 110, 255))
        s.set_at((1, 5), (100, 100, 110, 255))
        return s
    return gen._get("proj_bolt", make)


def generate_projectile_fireball(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        # Outer glow
        for y in range(12):
            for x in range(12):
                dx = (x - 6) / 6.0
                dy = (y - 6) / 6.0
                d2 = dx * dx + dy * dy
                if d2 < 1.0:
                    a = int(200 * (1.0 - d2))
                    s.set_at((x, y), (255, 120, 20, a))
        # Bright core
        pygame.draw.circle(s, (255, 200, 60, 255), (6, 6), 3)
        pygame.draw.circle(s, (255, 255, 180, 255), (6, 6), 1)
        return s
    return gen._get("proj_fireball", make)


def generate_projectile_enemy(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((8, 8), pygame.SRCALPHA)
        # Dark red/purple arrowhead
        s.set_at((6, 3), (180, 30, 60, 255))
        s.set_at((7, 3), (180, 30, 60, 255))
        s.set_at((6, 4), (180, 30, 60, 255))
        s.set_at((7, 4), (180, 30, 60, 255))
        # Shaft
        for i in range(5):
            s.set_at((1 + i, 3), (120, 40, 80, 255))
            s.set_at((1 + i, 4), (120, 40, 80, 255))
        # Purple trail
        s.set_at((0, 3), (100, 30, 120, 150))
        s.set_at((0, 4), (100, 30, 120, 150))
        return s
    return gen._get("proj_enemy", make)


def generate_projectile_lightning(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        for y in range(12):
            for x in range(12):
                dx = (x - 6) / 6.0
                dy = (y - 6) / 6.0
                d2 = dx * dx + dy * dy
                if d2 < 1.0:
                    a = int(180 * (1.0 - d2))
                    s.set_at((x, y), (180, 200, 255, a))
        pygame.draw.circle(s, (220, 240, 255, 255), (6, 6), 3)
        pygame.draw.circle(s, (255, 255, 255, 255), (6, 6), 1)
        return s
    return gen._get("proj_lightning", make)


def generate_projectile_ice(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        for y in range(12):
            for x in range(12):
                dx = (x - 6) / 6.0
                dy = (y - 6) / 6.0
                d2 = dx * dx + dy * dy
                if d2 < 1.0:
                    a = int(200 * (1.0 - d2))
                    s.set_at((x, y), (100, 200, 255, a))
        pygame.draw.circle(s, (160, 230, 255, 255), (6, 6), 3)
        pygame.draw.circle(s, (220, 245, 255, 255), (6, 6), 1)
        return s
    return gen._get("proj_ice", make)


def generate_projectile_bomb(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(s, (60, 60, 60, 255), (6, 6), 5)
        pygame.draw.circle(s, (90, 90, 90, 255), (6, 6), 3)
        # Spark
        s.set_at((6, 1), (255, 200, 50, 255))
        s.set_at((7, 1), (255, 150, 30, 200))
        return s
    return gen._get("proj_bomb", make)


def generate_enchant_tomes(gen) -> None:
    """Generate item icons for Enchantment Tome I-V."""
    # Tier colors: 1-2 rare blue, 3-5 epic purple glow
    for tier in range(1, 6):
        key = f"item_enchant_tome_{tier}"
        glow = (80, 140, 255) if tier <= 2 else (180, 60, 255)
        def make(t=tier, g=glow) -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Book body
            for y in range(3, 14):
                for x in range(3, 13):
                    s.set_at((x, y), (100, 50, 30, 255))
            # Book cover (slightly lighter front)
            for y in range(3, 14):
                s.set_at((12, y), (130, 70, 40, 255))
            # Spine
            for y in range(3, 14):
                s.set_at((3, y), (70, 35, 20, 255))
            # Pages (white edge)
            for y in range(5, 12):
                s.set_at((4, y), (230, 225, 210, 255))
            # Rune glow in center
            cx, cy = 8, 8
            r, gg, b = g
            s.set_at((cx, cy), (r, gg, b, 255))
            s.set_at((cx - 1, cy), (r, gg, b, 200))
            s.set_at((cx + 1, cy), (r, gg, b, 200))
            s.set_at((cx, cy - 1), (r, gg, b, 200))
            s.set_at((cx, cy + 1), (r, gg, b, 200))
            # Roman numeral dots (tier indicator along bottom)
            for i in range(t):
                dx = 6 + i * 2 - t
                if 0 <= dx < 16:
                    s.set_at((dx, 13), (255, 255, 200, 255))
            return s
        gen._get(key, make)


def generate_transfer_tomes(gen) -> None:
    """Generate item icons for Transfer / Removal tomes (boss drops)."""
    tomes = {
        'enchant_transfer_tome':  (100, 200, 255),   # cyan
        'enhance_transfer_tome':  (255, 200, 80),    # gold
        'superior_transfer_tome': (255, 100, 255),   # magenta
        'disenchant_tome':        (180, 180, 180),   # silver
        'unenhance_tome':         (200, 120, 60),    # bronze
    }
    for item_id, glow in tomes.items():
        key = f"item_{item_id}"
        def make(g=glow) -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Book body (darker than enchant tomes)
            for y in range(3, 14):
                for x in range(3, 13):
                    s.set_at((x, y), (60, 35, 25, 255))
            # Cover edge
            for y in range(3, 14):
                s.set_at((12, y), (80, 50, 35, 255))
            # Spine
            for y in range(3, 14):
                s.set_at((3, y), (40, 22, 14, 255))
            # Pages
            for y in range(5, 12):
                s.set_at((4, y), (220, 215, 200, 255))
            # Glow rune (larger cross pattern)
            cx, cy = 8, 8
            r, gg, b = g
            s.set_at((cx, cy), (r, gg, b, 255))
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                            (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                s.set_at((cx + dx, cy + dy), (r, gg, b, 160))
            return s
        gen._get(key, make)


def generate_item_enchantment_table(gen) -> pygame.Surface:
    """Inventory icon for the enchantment table item."""
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Table top (dark wood with rune accents)
        for y in range(4, 8):
            for x in range(2, 14):
                s.set_at((x, y), (80, 50, 35, 255))
        # Table legs
        for y in range(8, 14):
            s.set_at((3, y), (70, 40, 25, 255))
            s.set_at((4, y), (60, 35, 20, 255))
            s.set_at((11, y), (70, 40, 25, 255))
            s.set_at((12, y), (60, 35, 20, 255))
        # Rune glow on tabletop (purple/blue magic)
        for x in range(5, 11):
            s.set_at((x, 5), (120, 80, 200, 180))
            s.set_at((x, 6), (100, 60, 180, 140))
        # Center gem
        s.set_at((7, 5), (180, 100, 255, 255))
        s.set_at((8, 5), (180, 100, 255, 255))
        # Edge highlight
        for x in range(2, 14):
            s.set_at((x, 4), (100, 65, 45, 255))
        return s
    return gen._get("item_enchantment_table", make)


def generate_enchantment_table_placed(gen) -> pygame.Surface:
    """Placed enchantment table texture (32x32). Rounded runed spell bench."""
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        # Base table body (dark wood, rounded look)
        for y in range(8, 16):
            for x in range(3, 29):
                # Rounded corners
                if y < 10 and (x < 5 or x > 26):
                    continue
                shade = 75 + int(10 * hash_noise(x, y, gen.seed))
                s.set_at((x, y), (shade, shade // 2 + 10, shade // 3, 255))
        # Table top surface (slightly lighter)
        for y in range(6, 10):
            for x in range(4, 28):
                if y < 7 and (x < 6 or x > 25):
                    continue
                shade = 100 + int(8 * hash_noise(x, y, gen.seed + 1))
                s.set_at((x, y), (shade, shade // 2 + 15, shade // 3 + 5, 255))
        # Legs
        for y in range(16, 26):
            for dx in [(5, 7), (24, 26)]:
                for x in range(dx[0], dx[1]):
                    shade = 60 + int(8 * hash_noise(x, y, gen.seed + 2))
                    s.set_at((x, y), (shade, shade // 2, shade // 3, 255))
        # Cross brace
        for x in range(7, 25):
            s.set_at((x, 20), (70, 40, 25, 255))
            s.set_at((x, 21), (60, 35, 20, 255))
        # Rune circle on tabletop (glowing purple/blue)
        cx, cy = 16, 8
        for angle_step in range(24):
            a = angle_step * (3.14159 * 2 / 24)
            rx = int(cx + 7 * math.cos(a))
            ry = int(cy + 2.5 * math.sin(a))
            if 0 <= rx < 32 and 0 <= ry < 32:
                s.set_at((rx, ry), (140, 80, 220, 200))
        # Inner runes (small glowing dots)
        rune_positions = [(12, 8), (20, 8), (16, 7), (16, 9),
                          (14, 7), (18, 7), (14, 9), (18, 9)]
        for rx, ry in rune_positions:
            s.set_at((rx, ry), (180, 120, 255, 220))
        # Center gem (bright purple)
        s.set_at((15, 8), (200, 100, 255, 255))
        s.set_at((16, 8), (220, 120, 255, 255))
        s.set_at((16, 7), (200, 100, 255, 230))
        return s
    return gen._get("enchantment_table_placed", make)


def generate_greater_enchantment_table_placed(gen) -> pygame.Surface:
    """Placed greater enchantment table texture derived from the item icon."""
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        icon = gen.get('item_greater_enchantment_table')
        icon_large = pygame.transform.smoothscale(icon, (24, 24))

        shadow = pygame.Surface((24, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 1, 24, 6))
        s.blit(shadow, (4, 22))

        glow = pygame.Surface((28, 28), pygame.SRCALPHA)
        pygame.draw.circle(glow, (120, 70, 180, 70), (14, 13), 11)
        pygame.draw.circle(glow, (180, 220, 255, 60), (14, 10), 6)
        s.blit(glow, (2, 1))

        s.blit(icon_large, (4, 3))

        for x in range(8, 24):
            s.set_at((x, 27), (55, 28, 70, 180))
            s.set_at((x, 28), (40, 20, 52, 150))
        return s
    return gen._get("greater_enchantment_table_placed", make)
