"""Building and placed-object texture generation."""
import random
import math
import pygame
from core.constants import TILE_SIZE
from core.utils import hash_noise


# ==================================================================
# BUILDING ITEM ICONS (16×16)
# ==================================================================
def generate_item_wall(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(3, 14):
            for x in range(2, 14):
                c = 130 + int(20 * hash_noise(x, y, gen.seed + 68))
                s.set_at((x, y), (c, int(c * 0.65), 30, 255))
        # Plank lines
        for y in range(3, 14):
            s.set_at((5, y), (100, 60, 25, 255))
            s.set_at((10, y), (100, 60, 25, 255))
        return s
    return gen._get("item_wall", make)


def generate_item_stone_wall_b(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(3, 14):
            for x in range(2, 14):
                c = 120 + int(25 * hash_noise(x // 3, y // 3, gen.seed + 69))
                s.set_at((x, y), (c, c, c + 5, 255))
        # Mortar lines
        for x in range(2, 14):
            s.set_at((x, 6), (90, 90, 95, 255))
            s.set_at((x, 10), (90, 90, 95, 255))
        for y in range(3, 7):
            s.set_at((8, y), (90, 90, 95, 255))
        for y in range(7, 11):
            s.set_at((5, y), (90, 90, 95, 255))
            s.set_at((11, y), (90, 90, 95, 255))
        return s
    return gen._get("item_stone_wall_b", make)


def generate_item_turret(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        wood = (130, 85, 40, 255)
        metal = (150, 150, 165, 255)
        # Wooden base
        for y in range(10, 15):
            for x in range(3, 13):
                s.set_at((x, y), wood)
        # Metal top / mechanism
        for y in range(4, 10):
            for x in range(5, 11):
                s.set_at((x, y), metal)
        # Barrel
        for x in range(11, 15):
            s.set_at((x, 7), (130, 130, 145, 255))
            s.set_at((x, 8), (130, 130, 145, 255))
        return s
    return gen._get("item_turret", make)


def generate_item_chest(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        wood = (140, 90, 40, 255)
        dark = (100, 60, 25, 255)
        gold = (220, 190, 50, 255)
        # Chest body
        for y in range(5, 13):
            for x in range(3, 13):
                s.set_at((x, y), wood)
        # Lid (top)
        for x in range(3, 13):
            s.set_at((x, 5), dark)
            s.set_at((x, 6), dark)
        # Gold clasp
        s.set_at((7, 8), gold)
        s.set_at((8, 8), gold)
        s.set_at((7, 9), gold)
        s.set_at((8, 9), gold)
        # Bottom edge
        for x in range(3, 13):
            s.set_at((x, 12), dark)
        return s
    return gen._get("item_chest", make)


def generate_item_door(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        wood = (140, 90, 45, 255)
        dark = (100, 60, 25, 255)
        # Door body
        for y in range(2, 15):
            for x in range(4, 12):
                s.set_at((x, y), wood)
        # Frame
        for y in range(2, 15):
            s.set_at((4, y), dark)
            s.set_at((11, y), dark)
        for x in range(4, 12):
            s.set_at((x, 2), dark)
            s.set_at((x, 14), dark)
        # Handle
        s.set_at((10, 8), (200, 180, 50, 255))
        s.set_at((10, 9), (200, 180, 50, 255))
        return s
    return gen._get("item_door", make)


# ==================================================================
# PLACED OBJECTS
# ==================================================================
def generate_campfire(gen, lit: bool = True) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        for x in range(8, 24):
            s.set_at((x, 22), (100, 60, 30, 255))
            s.set_at((x, 23), (80, 50, 25, 255))
        pygame.draw.line(s, (120, 70, 35), (10, 20), (22, 20), 3)
        if lit:
            for i in range(5):
                fx = 16 + random.randint(-4, 4)
                fy = 18 - i * 3
                pygame.draw.circle(s, (255, max(0, 180 - i * 20), 50, 200),
                                   (fx, fy), 5 - i)
        return s
    return gen._get(f"campfire_{lit}", make)


def generate_torch_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 32), pygame.SRCALPHA)
        for y in range(10, 32):
            s.set_at((7, y), (100, 70, 35, 255))
            s.set_at((8, y), (120, 85, 40, 255))
        for i in range(5):
            fx = 8 + random.randint(-2, 2)
            fy = 8 - i * 2
            pygame.draw.circle(
                s, (255, max(0, 180 - i * 25), 40, 200),
                (fx, max(0, fy)), max(1, 3 - min(i, 2)))
        return s
    return gen._get("torch_placed", make)


def generate_trap_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 16), pygame.SRCALPHA)
        metal = (140, 140, 160, 255)
        spike = (180, 180, 200, 255)
        for x in range(4, 28):
            s.set_at((x, 12), metal)
            s.set_at((x, 13), metal)
        for i in range(6):
            bx = 6 + i * 4
            for j in range(5):
                s.set_at((bx, 11 - j), spike)
        return s
    return gen._get("trap_placed", make)


def generate_bed_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        # Top-down bed: 2 tiles wide (64px) x 1 tile tall (32px)
        s = pygame.Surface((64, 32), pygame.SRCALPHA)
        frame = (120, 80, 40, 255)
        frame_dk = (90, 60, 30, 255)
        red = (180, 35, 35, 255)
        red_dk = (150, 25, 25, 255)
        red_lt = (200, 50, 50, 255)
        pillow = (230, 230, 240, 255)
        pillow_dk = (200, 200, 215, 255)
        # Wooden frame border
        for x in range(0, 64):
            s.set_at((x, 0), frame)
            s.set_at((x, 1), frame)
            s.set_at((x, 30), frame)
            s.set_at((x, 31), frame)
        for y in range(0, 32):
            s.set_at((0, y), frame)
            s.set_at((1, y), frame)
            s.set_at((62, y), frame)
            s.set_at((63, y), frame)
        # Headboard (thicker left edge)
        for y in range(0, 32):
            s.set_at((2, y), frame_dk)
            s.set_at((3, y), frame_dk)
        # Red blanket (right 2/3)
        for y in range(2, 30):
            for x in range(22, 62):
                c = red if (x + y) % 4 != 0 else red_dk
                s.set_at((x, y), c)
        # Blanket fold line
        for y in range(3, 29):
            s.set_at((22, y), red_lt)
            s.set_at((23, y), red_lt)
        # Pillow area (left portion)
        for y in range(4, 28):
            for x in range(5, 21):
                c = pillow if y < 16 else pillow_dk
                s.set_at((x, y), c)
        # Pillow divider (two pillows)
        for y in range(4, 28):
            s.set_at((13, y), pillow_dk)
        # Pillow outlines
        for x in range(5, 21):
            s.set_at((x, 4), pillow_dk)
            s.set_at((x, 27), pillow_dk)
        return s
    return gen._get("bed_placed", make)


def generate_wall_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        for y in range(4, 28):
            for x in range(4, 28):
                c = 130 + int(25 * hash_noise(x, y, gen.seed + 70))
                s.set_at((x, y), (c, int(c * 0.65), 30, 255))
        # Plank dividers
        for y in range(4, 28):
            s.set_at((10, y), (90, 55, 20, 255))
            s.set_at((16, y), (90, 55, 20, 255))
            s.set_at((22, y), (90, 55, 20, 255))
        return s
    return gen._get("wall_placed", make)


def generate_stone_wall_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        for y in range(4, 28):
            for x in range(4, 28):
                c = 115 + int(30 * hash_noise(x // 4, y // 4, gen.seed + 71))
                s.set_at((x, y), (c, c, c + 5, 255))
        # Mortar lines (horizontal)
        for x in range(4, 28):
            s.set_at((x, 10), (85, 85, 90, 255))
            s.set_at((x, 16), (85, 85, 90, 255))
            s.set_at((x, 22), (85, 85, 90, 255))
        # Mortar lines (vertical, offset per row)
        for y in range(4, 10):
            s.set_at((12, y), (85, 85, 90, 255))
            s.set_at((20, y), (85, 85, 90, 255))
        for y in range(11, 16):
            s.set_at((8, y), (85, 85, 90, 255))
            s.set_at((16, y), (85, 85, 90, 255))
            s.set_at((24, y), (85, 85, 90, 255))
        for y in range(17, 22):
            s.set_at((12, y), (85, 85, 90, 255))
            s.set_at((20, y), (85, 85, 90, 255))
        return s
    return gen._get("stone_wall_placed", make)


def generate_turret_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        wood = (130, 85, 40, 255)
        metal = (140, 140, 155, 255)
        # Wooden platform
        for y in range(20, 28):
            for x in range(4, 28):
                c = 120 + int(20 * hash_noise(x, y, gen.seed + 72))
                s.set_at((x, y), (c, int(c * 0.65), 30, 255))
        # Crossbow on top
        for y in range(10, 20):
            for x in range(10, 22):
                s.set_at((x, y), metal)
        # Barrel
        for x in range(22, 28):
            s.set_at((x, 14), (160, 160, 175, 255))
            s.set_at((x, 15), (160, 160, 175, 255))
        # Support post
        for y in range(16, 28):
            s.set_at((15, y), wood)
            s.set_at((16, y), wood)
        return s
    return gen._get("turret_placed", make)


def generate_chest_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 24), pygame.SRCALPHA)
        wood = (140, 90, 40, 255)
        dark = (100, 60, 25, 255)
        gold = (220, 190, 50, 255)
        # Chest body
        for y in range(6, 20):
            for x in range(4, 28):
                c = 135 + int(20 * hash_noise(x, y, gen.seed + 73))
                s.set_at((x, y), (c, int(c * 0.65), 30, 255))
        # Lid
        for x in range(4, 28):
            s.set_at((x, 6), dark)
            s.set_at((x, 7), dark)
            s.set_at((x, 8), dark)
        # Gold clasp
        for y in range(11, 14):
            for x in range(14, 18):
                s.set_at((x, y), gold)
        # Bottom edge
        for x in range(4, 28):
            s.set_at((x, 19), dark)
        # Metal bands
        for y in range(6, 20):
            s.set_at((10, y), (120, 120, 135, 255))
            s.set_at((22, y), (120, 120, 135, 255))
        return s
    return gen._get("chest_placed", make)


def generate_cave_chest_placed(gen) -> pygame.Surface:
    """Gold-coloured chest used in caves."""
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 24), pygame.SRCALPHA)
        gold_body = (200, 170, 50, 255)
        dark_gold = (150, 120, 30, 255)
        bright_gold = (255, 220, 80, 255)
        # Chest body — golden
        for y in range(6, 20):
            for x in range(4, 28):
                c = 180 + int(30 * hash_noise(x, y, gen.seed + 97))
                s.set_at((x, y), (c, int(c * 0.85), 30, 255))
        # Lid — darker gold
        for x in range(4, 28):
            s.set_at((x, 6), dark_gold)
            s.set_at((x, 7), dark_gold)
            s.set_at((x, 8), dark_gold)
        # Bright gold clasp
        for y in range(11, 14):
            for x in range(14, 18):
                s.set_at((x, y), bright_gold)
        # Bottom edge
        for x in range(4, 28):
            s.set_at((x, 19), dark_gold)
        # Gold bands
        for y in range(6, 20):
            s.set_at((10, y), bright_gold)
            s.set_at((22, y), bright_gold)
        return s
    return gen._get("cave_chest_placed", make)


def generate_door_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((24, 32), pygame.SRCALPHA)
        wood = (140, 90, 45, 255)
        dark = (100, 60, 25, 255)
        # Door body
        for y in range(2, 30):
            for x in range(4, 20):
                c = 135 + int(20 * hash_noise(x, y, gen.seed + 74))
                s.set_at((x, y), (c, int(c * 0.65), 30, 255))
        # Frame
        for y in range(2, 30):
            s.set_at((4, y), dark)
            s.set_at((5, y), dark)
            s.set_at((19, y), dark)
            s.set_at((18, y), dark)
        for x in range(4, 20):
            s.set_at((x, 2), dark)
            s.set_at((x, 3), dark)
            s.set_at((x, 29), dark)
        # Handle
        s.set_at((16, 15), (200, 180, 50, 255))
        s.set_at((16, 16), (200, 180, 50, 255))
        s.set_at((17, 15), (200, 180, 50, 255))
        s.set_at((17, 16), (200, 180, 50, 255))
        # Horizontal planks
        for x in range(6, 18):
            s.set_at((x, 10), dark)
            s.set_at((x, 20), dark)
        return s
    return gen._get("door_placed", make)


# ==================================================================
# BEACON (item icon 16×16)
# ==================================================================
def generate_item_beacon(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        stone = (130, 130, 140, 255)
        fire = (255, 200, 50, 255)
        glow = (255, 160, 40, 200)
        # Stone base
        for y in range(10, 15):
            for x in range(3, 13):
                s.set_at((x, y), stone)
        # Pillar
        for y in range(4, 10):
            for x in range(5, 11):
                s.set_at((x, y), (120, 120, 130, 255))
        # Fire/glow on top
        for i in range(3):
            fx = 8 + random.randint(-1, 1)
            fy = 3 - i
            pygame.draw.circle(s, fire if i == 0 else glow,
                               (fx, max(0, fy)), 2 - min(i, 1))
        return s
    return gen._get("item_beacon", make)


# ==================================================================
# BEACON (placed 64×64 — 2×2 tiles)
# ==================================================================
def generate_beacon_placed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((64, 64), pygame.SRCALPHA)
        stone = (130, 130, 140, 255)
        stone_dk = (100, 100, 110, 255)
        fire = (255, 200, 50, 255)
        glow = (255, 160, 40, 200)
        # Stone base platform
        for y in range(40, 58):
            for x in range(8, 56):
                c = 120 + int(20 * hash_noise(x // 4, y // 4, gen.seed + 80))
                s.set_at((x, y), (c, c, c + 5, 255))
        # Central stone pillar
        for y in range(14, 40):
            for x in range(22, 42):
                c = 115 + int(25 * hash_noise(x // 3, y // 3, gen.seed + 81))
                s.set_at((x, y), (c, c, c + 5, 255))
        # Mortar lines
        for x in range(22, 42):
            s.set_at((x, 24), stone_dk)
            s.set_at((x, 32), stone_dk)
        # Fire bowl on top
        for i in range(8):
            fx = 32 + random.randint(-6, 6)
            fy = 12 - i * 2
            r = max(1, 6 - i)
            pygame.draw.circle(s, fire if i < 4 else glow,
                               (fx, max(0, fy)), r)
        return s
    return gen._get("beacon_placed", make)


# ==================================================================
# STONE OVEN (item icon 16×16)
# ==================================================================
def generate_item_stone_oven(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        stone = (130, 130, 140, 255)
        dark = (90, 90, 100, 255)
        fire = (255, 120, 30, 255)
        # Body
        for y in range(4, 14):
            for x in range(3, 13):
                s.set_at((x, y), stone)
        # Opening / mouth
        for y in range(7, 12):
            for x in range(5, 11):
                s.set_at((x, y), dark)
        # Embers
        s.set_at((7, 10), fire)
        s.set_at((8, 10), fire)
        s.set_at((7, 9), (255, 160, 40, 255))
        # Top vent
        for x in range(6, 10):
            s.set_at((x, 4), dark)
        return s
    return gen._get("item_stone_oven", make)


# ==================================================================
# STONE OVEN (placed 32×32)
# ==================================================================
def generate_stone_oven_placed(gen, burning: bool = False) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        stone = (130, 130, 140, 255)
        dark = (80, 80, 90, 255)
        # Stone body
        for y in range(6, 28):
            for x in range(4, 28):
                c = 120 + int(20 * hash_noise(x // 3, y // 3, gen.seed + 82))
                s.set_at((x, y), (c, c, c + 5, 255))
        # Front opening
        for y in range(14, 24):
            for x in range(10, 22):
                s.set_at((x, y), dark)
        if burning:
            # Fire inside
            for i in range(4):
                fx = 16 + random.randint(-3, 3)
                fy = 22 - i * 2
                pygame.draw.circle(s, (255, max(0, 180 - i * 30), 40, 200),
                                   (fx, fy), 3 - min(i, 2))
        # Top vent
        for x in range(12, 20):
            s.set_at((x, 6), dark)
            s.set_at((x, 7), dark)
        # Mortar lines
        for x in range(4, 28):
            s.set_at((x, 12), (90, 90, 95, 255))
        return s
    return gen._get(f"stone_oven_{burning}", make)
