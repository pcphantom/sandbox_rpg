"""Player, resource, and tile texture generation."""
import random
import math
import pygame
from core.constants import TILE_SIZE
from core.utils import hash_noise, fbm_noise


def generate_player(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((24, 32), pygame.SRCALPHA)
        for y in range(20, 30):
            for x in range(6, 10):
                s.set_at((x, y), (60, 80, 180, 255))
            for x in range(14, 18):
                s.set_at((x, y), (60, 80, 180, 255))
        for y in range(10, 22):
            for x in range(5, 19):
                sh = 120 + int(20 * hash_noise(x, y, gen.seed))
                s.set_at((x, y), (sh, 60, 40, 255))
        for y in range(2, 12):
            for x in range(7, 17):
                s.set_at((x, y), (220, 180, 140, 255))
        s.set_at((10, 6), (30, 30, 30, 255))
        s.set_at((14, 6), (30, 30, 30, 255))
        for x in range(6, 18):
            s.set_at((x, 2), (80, 50, 30, 255))
            s.set_at((x, 3), (100, 70, 40, 255))
        return s
    return gen._get("player", make)


def generate_tree(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((48, 64), pygame.SRCALPHA)
        for y in range(24, 64):
            for x in range(20, 28):
                c = 90 + int(30 * hash_noise(x, y, gen.seed + 1))
                s.set_at((x, y), (c, int(c * 0.6), 30, 255))
        for rad in range(18, 8, -3):
            cy = 24
            for y in range(cy - rad, cy + rad):
                for x in range(24 - rad, 24 + rad):
                    if ((x - 24) ** 2 + (y - cy) ** 2 < rad * rad
                            and random.random() > 0.2):
                        g = 80 + int(60 * hash_noise(x, y, gen.seed + 2))
                        s.set_at((x, y), (30, g, 30, 255))
        return s
    return gen._get("tree", make)


def generate_rock(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 24), pygame.SRCALPHA)
        for y in range(24):
            for x in range(32):
                n = hash_noise(x, y, gen.seed + 3)
                if ((x - 16) ** 2 / 256 + (y - 12) ** 2 / 144
                        < 0.8 + n * 0.2):
                    c = int(110 + n * 40 - y * 1.5)
                    c = max(40, min(200, c))
                    s.set_at((x, y), (c, c, c, 255))
        return s
    return gen._get("rock", make)


def generate_grass_tile(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                n = fbm_noise(x * 0.1, y * 0.1, gen.seed + 4, 3)
                g = int(90 + n * 60)
                s.set_at((x, y), (40, g, 40))
        for _ in range(40):
            s.set_at((random.randint(0, 31), random.randint(0, 31)),
                     (60, 180, 60))
        return s
    return gen._get("grass", make)


def generate_dirt_tile(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                n = hash_noise(x, y, gen.seed + 5)
                c = int(80 + n * 40)
                s.set_at((x, y), (c, int(c * 0.7), 40))
        return s
    return gen._get("dirt", make)


def generate_sand_tile(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                n = hash_noise(x, y, gen.seed + 9)
                c = int(190 + n * 40)
                s.set_at((x, y), (c, int(c * 0.9), int(c * 0.65)))
        return s
    return gen._get("sand", make)


def generate_water_tile(gen, frame: int = 0) -> pygame.Surface:
    key = f"water_{frame}"
    def make() -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                n = fbm_noise((x + frame * 2) * 0.1, y * 0.1,
                              gen.seed + 6, 2)
                b = int(140 + n * 80)
                s.set_at((x, y), (30, 80, min(255, b)))
        return s
    return gen._get(key, make)


def generate_stone_tile(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                n = hash_noise(x // 4, y // 4, gen.seed + 7)
                c = int(100 + n * 50)
                s.set_at((x, y), (c, c, min(255, c + 10)))
        for _ in range(3):
            pygame.draw.line(
                s, (70, 70, 80),
                (random.randint(2, 29), random.randint(2, 29)),
                (random.randint(2, 29), random.randint(2, 29)), 1)
        return s
    return gen._get("stone", make)


def generate_forest_tile(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                n = fbm_noise(x * 0.1, y * 0.1, gen.seed + 60, 3)
                g = int(60 + n * 50)
                s.set_at((x, y), (25, g, 25))
        # Small tree dots scattered
        for _ in range(12):
            tx = random.randint(2, 29)
            ty = random.randint(2, 29)
            s.set_at((tx, ty), (20, 90, 20))
            s.set_at((tx + 1, ty), (20, 90, 20))
            s.set_at((tx, ty + 1), (20, 90, 20))
            s.set_at((tx + 1, ty + 1), (20, 90, 20))
        return s
    return gen._get("forest", make)


def generate_cave_floor_tile(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        for y in range(TILE_SIZE):
            for x in range(TILE_SIZE):
                n = hash_noise(x // 3, y // 3, gen.seed + 40)
                c = int(45 + n * 30)
                s.set_at((x, y), (c, c - 5, c + 5))
        # Scattered pebbles
        for _ in range(5):
            px = random.randint(2, 29)
            py = random.randint(2, 29)
            s.set_at((px, py), (75, 72, 80))
        return s
    return gen._get("cave_floor", make)


def generate_cave_entrance_tile(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((TILE_SIZE, TILE_SIZE))
        # Dark centre hole with stone border
        s.fill((35, 35, 40))
        pygame.draw.rect(s, (70, 65, 60), (0, 0, TILE_SIZE, TILE_SIZE), 3)
        # Dark gradient centre
        for dy in range(6, 26):
            for dx in range(6, 26):
                dist = max(abs(dx - 16), abs(dy - 16))
                shade = max(10, 35 - dist * 2)
                s.set_at((dx, dy), (shade, shade, shade + 5))
        # Small stalagmite hints at top corners
        for cx in (4, 27):
            for cy in range(2, 7):
                s.set_at((cx, cy), (55, 52, 50))
        return s
    return gen._get("cave_entrance", make)


def generate_ore_node(gen) -> pygame.Surface:
    """Iron ore node for cave interiors (32x32 resource object)."""
    def make() -> pygame.Surface:
        s = pygame.Surface((24, 20), pygame.SRCALPHA)
        # Rocky base
        for y in range(20):
            for x in range(24):
                if (x - 12) ** 2 + (y - 10) ** 2 < 100:
                    c = random.randint(70, 95)
                    s.set_at((x, y), (c, c - 5, c + 5, 255))
        # Orange-brown ore flecks
        for _ in range(8):
            ox = random.randint(4, 19)
            oy = random.randint(3, 16)
            if (ox - 12) ** 2 + (oy - 10) ** 2 < 80:
                s.set_at((ox, oy), (180, 120, 50, 255))
                s.set_at((ox + 1, oy), (160, 100, 40, 255))
        return s
    return gen._get("ore_node", make)


def generate_diamond_node(gen) -> pygame.Surface:
    """Diamond node for cave interiors (smaller sparkling rock)."""
    def make() -> pygame.Surface:
        s = pygame.Surface((22, 18), pygame.SRCALPHA)
        # Rocky base
        for y in range(18):
            for x in range(22):
                if (x - 11) ** 2 + (y - 9) ** 2 < 80:
                    c = random.randint(65, 85)
                    s.set_at((x, y), (c, c, c + 10, 255))
        # Cyan diamond flecks
        for _ in range(5):
            ox = random.randint(4, 17)
            oy = random.randint(3, 14)
            if (ox - 11) ** 2 + (oy - 9) ** 2 < 60:
                s.set_at((ox, oy), (120, 220, 255, 255))
                s.set_at((ox + 1, oy), (100, 200, 240, 255))
        return s
    return gen._get("diamond_node", make)
