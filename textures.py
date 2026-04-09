"""Procedural texture generation for all game assets."""
import random
import math
from typing import Dict, Callable

import pygame

from constants import TILE_SIZE
from utils import hash_noise, fbm_noise


class TextureGenerator:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.cache: Dict[str, pygame.Surface] = {}

    def get(self, key: str) -> pygame.Surface:
        return self.cache[key]

    def _get(self, key: str, maker: Callable[[], pygame.Surface]) -> pygame.Surface:
        if key not in self.cache:
            self.cache[key] = maker()
        return self.cache[key]

    # ------------------------------------------------------------------
    # Master generator — call once after pygame.init()
    # ------------------------------------------------------------------
    def generate_all(self) -> None:
        self.generate_player()
        # Mobs
        self.generate_slime()
        self.generate_skeleton()
        self.generate_wolf()
        self.generate_goblin()
        self.generate_ghost()
        self.generate_spider()
        self.generate_orc()
        self.generate_dark_knight()
        # Resources
        self.generate_tree()
        self.generate_rock()
        # Tiles
        self.generate_grass_tile()
        self.generate_dirt_tile()
        self.generate_sand_tile()
        self.generate_water_tile(0)
        self.generate_stone_tile()
        self.generate_forest_tile()
        # Original items
        self.generate_item_wood()
        self.generate_item_stone()
        self.generate_item_stick()
        self.generate_item_berry()
        self.generate_item_axe()
        self.generate_item_sword()
        self.generate_item_torch()
        self.generate_item_campfire()
        self.generate_item_pie()
        self.generate_item_bandage()
        # New items
        self.generate_item_iron_sword()
        self.generate_item_spear()
        self.generate_item_bow()
        self.generate_item_arrow()
        self.generate_item_sling()
        self.generate_item_rock_ammo()
        self.generate_item_sling_bullet()
        self.generate_item_leather_armor()
        self.generate_item_wood_shield()
        self.generate_item_trap()
        self.generate_item_bed()
        # New items (phase 2)
        self.generate_item_iron()
        self.generate_item_cloth()
        self.generate_item_bone()
        self.generate_item_leather()
        self.generate_item_health_potion()
        self.generate_item_antidote()
        self.generate_item_iron_axe()
        self.generate_item_mace()
        self.generate_item_bone_club()
        self.generate_item_crossbow()
        self.generate_item_fire_arrow()
        self.generate_item_bolt()
        self.generate_item_iron_armor()
        self.generate_item_iron_shield()
        # Building items
        self.generate_item_wall()
        self.generate_item_stone_wall_b()
        self.generate_item_turret()
        self.generate_item_chest()
        self.generate_item_door()
        # Placed objects
        self.generate_campfire(True)
        self.generate_campfire(False)
        self.generate_torch_placed()
        self.generate_trap_placed()
        self.generate_bed_placed()
        self.generate_wall_placed()
        self.generate_stone_wall_placed()
        self.generate_turret_placed()
        self.generate_chest_placed()
        self.generate_door_placed()
        # Projectiles
        self.generate_projectile_arrow()
        self.generate_projectile_rock()
        self.generate_projectile_bolt()

    # ==================================================================
    # PLAYER
    # ==================================================================
    def generate_player(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((24, 32), pygame.SRCALPHA)
            for y in range(20, 30):
                for x in range(6, 10):
                    s.set_at((x, y), (60, 80, 180, 255))
                for x in range(14, 18):
                    s.set_at((x, y), (60, 80, 180, 255))
            for y in range(10, 22):
                for x in range(5, 19):
                    sh = 120 + int(20 * hash_noise(x, y, self.seed))
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
        return self._get("player", make)

    # ==================================================================
    # MOBS
    # ==================================================================
    def generate_slime(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((24, 18), pygame.SRCALPHA)
            for y in range(18):
                for x in range(24):
                    dx = (x - 12) / 12.0
                    dy = (y - 9) / 9.0
                    if dx * dx + dy * dy < 0.9:
                        g = 180 + int(30 * math.sin(x * 0.5))
                        s.set_at((x, y), (50, g, 70, 255))
            pygame.draw.circle(s, (200, 255, 200), (8, 6), 2)
            pygame.draw.circle(s, (200, 255, 200), (16, 6), 2)
            return pygame.transform.scale(s, (32, 24))
        return self._get("slime", make)

    def generate_skeleton(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((24, 32), pygame.SRCALPHA)
            bone = (220, 220, 210, 255)
            dark = (160, 160, 150, 255)
            for y in range(2, 10):
                for x in range(8, 16):
                    if (x - 12) ** 2 + (y - 6) ** 2 < 18:
                        s.set_at((x, y), bone)
            s.set_at((10, 5), (20, 20, 20, 255))
            s.set_at((11, 5), (20, 20, 20, 255))
            s.set_at((13, 5), (20, 20, 20, 255))
            s.set_at((14, 5), (20, 20, 20, 255))
            for x in range(9, 15):
                s.set_at((x, 9), dark)
            for y in range(10, 22):
                s.set_at((11, y), bone)
                s.set_at((12, y), bone)
            for y in range(12, 18, 2):
                for x in range(8, 16):
                    if abs(x - 12) + abs(y - 15) < 5:
                        s.set_at((x, y), dark)
            for y in range(22, 30):
                s.set_at((9, y), bone); s.set_at((10, y), bone)
                s.set_at((13, y), bone); s.set_at((14, y), bone)
            for y in range(12, 20):
                s.set_at((6, y), bone); s.set_at((7, y), bone)
                s.set_at((16, y), bone); s.set_at((17, y), bone)
            return s
        return self._get("skeleton", make)

    def generate_wolf(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((32, 24), pygame.SRCALPHA)
            # Body — dark grey ellipse
            for y in range(8, 22):
                for x in range(4, 28):
                    dx = (x - 16) / 12.0
                    dy = (y - 15) / 7.0
                    if dx * dx + dy * dy < 1.0:
                        c = 70 + int(20 * hash_noise(x, y, self.seed + 20))
                        s.set_at((x, y), (c, c, c, 255))
            # Head
            for y in range(4, 14):
                for x in range(22, 32):
                    dx = (x - 27) / 5.0
                    dy = (y - 9) / 5.0
                    if dx * dx + dy * dy < 1.0:
                        s.set_at((x, y), (80, 80, 80, 255))
            # Eyes
            s.set_at((28, 7), (255, 200, 50, 255))
            s.set_at((29, 7), (255, 200, 50, 255))
            # Legs
            for y in range(20, 24):
                s.set_at((8, y), (60, 60, 60, 255))
                s.set_at((9, y), (60, 60, 60, 255))
                s.set_at((20, y), (60, 60, 60, 255))
                s.set_at((21, y), (60, 60, 60, 255))
            return s
        return self._get("wolf", make)

    def generate_goblin(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((22, 28), pygame.SRCALPHA)
            skin = (80, 140, 60, 255)
            dark_skin = (60, 110, 45, 255)
            # Head
            for y in range(2, 12):
                for x in range(5, 17):
                    if (x - 11) ** 2 + (y - 7) ** 2 < 30:
                        s.set_at((x, y), skin)
            # Ears (pointy)
            for i in range(4):
                s.set_at((4 - i, 4 + i), skin)
                s.set_at((17 + i, 4 + i), skin)
            # Eyes
            s.set_at((9, 6), (255, 50, 50, 255))
            s.set_at((13, 6), (255, 50, 50, 255))
            # Body
            for y in range(12, 24):
                for x in range(6, 16):
                    c = 100 + int(20 * hash_noise(x, y, self.seed + 30))
                    s.set_at((x, y), (c, int(c * 0.5), 30, 255))
            # Legs
            for y in range(24, 28):
                for x in range(7, 10):
                    s.set_at((x, y), dark_skin)
                for x in range(12, 15):
                    s.set_at((x, y), dark_skin)
            return s
        return self._get("goblin", make)

    def generate_ghost(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((24, 30), pygame.SRCALPHA)
            # Ethereal body
            for y in range(30):
                for x in range(24):
                    dx = (x - 12) / 12.0
                    dy = (y - 12) / 15.0
                    if dx * dx + dy * dy < 0.85 and y < 26:
                        a = 120 + int(40 * math.sin(y * 0.4))
                        s.set_at((x, y), (180, 180, 220, a))
            # Wavy bottom edge
            for x in range(4, 20):
                wy = 24 + int(2 * math.sin(x * 0.8))
                for y in range(wy, min(wy + 4, 30)):
                    s.set_at((x, y), (160, 160, 200, 80))
            # Eyes (hollow)
            pygame.draw.circle(s, (40, 40, 60, 200), (9, 10), 3)
            pygame.draw.circle(s, (40, 40, 60, 200), (15, 10), 3)
            return s
        return self._get("ghost", make)

    def generate_spider(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((24, 20), pygame.SRCALPHA)
            body = (70, 40, 20, 255)
            leg = (50, 30, 15, 255)
            # Body ellipse
            for y in range(6, 16):
                for x in range(6, 18):
                    dx = (x - 12) / 6.0
                    dy = (y - 11) / 5.0
                    if dx * dx + dy * dy < 1.0:
                        c = 70 + int(20 * hash_noise(x, y, self.seed + 50))
                        s.set_at((x, y), (c, int(c * 0.57), int(c * 0.29), 255))
            # 8 legs (4 per side)
            for i in range(4):
                ly = 8 + i * 2
                # Left legs
                for j in range(5):
                    s.set_at((5 - j, ly - j // 2), leg)
                # Right legs
                for j in range(5):
                    s.set_at((18 + j, ly - j // 2), leg)
            # Red eyes
            s.set_at((10, 8), (255, 0, 0, 255))
            s.set_at((14, 8), (255, 0, 0, 255))
            return s
        return self._get("spider", make)

    def generate_orc(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((26, 32), pygame.SRCALPHA)
            skin = (90, 120, 60, 255)
            dark_skin = (70, 95, 45, 255)
            # Head
            for y in range(2, 12):
                for x in range(7, 19):
                    if (x - 13) ** 2 + (y - 7) ** 2 < 35:
                        c = 90 + int(20 * hash_noise(x, y, self.seed + 51))
                        s.set_at((x, y), (c, int(c * 1.3), int(c * 0.65), 255))
            # Angry red eyes
            s.set_at((10, 6), (255, 30, 30, 255))
            s.set_at((11, 6), (255, 30, 30, 255))
            s.set_at((15, 6), (255, 30, 30, 255))
            s.set_at((16, 6), (255, 30, 30, 255))
            # Tusks (white pixels near mouth)
            s.set_at((10, 10), (240, 240, 230, 255))
            s.set_at((16, 10), (240, 240, 230, 255))
            # Muscular body
            for y in range(12, 24):
                for x in range(5, 21):
                    c = 85 + int(25 * hash_noise(x, y, self.seed + 52))
                    s.set_at((x, y), (c, int(c * 1.2), int(c * 0.6), 255))
            # Dark loincloth
            for y in range(20, 26):
                for x in range(8, 18):
                    s.set_at((x, y), (50, 35, 20, 255))
            # Legs
            for y in range(26, 32):
                for x in range(7, 11):
                    s.set_at((x, y), dark_skin)
                for x in range(15, 19):
                    s.set_at((x, y), dark_skin)
            return s
        return self._get("orc", make)

    def generate_dark_knight(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((24, 34), pygame.SRCALPHA)
            armor = (35, 35, 40, 255)
            armor_hi = (55, 55, 65, 255)
            # Helmet
            for y in range(1, 10):
                for x in range(7, 17):
                    if (x - 12) ** 2 + (y - 5) ** 2 < 28:
                        s.set_at((x, y), armor)
            # Visor slit
            for x in range(9, 15):
                s.set_at((x, 5), (20, 20, 25, 255))
            # Red glowing eyes
            s.set_at((10, 5), (255, 20, 20, 255))
            s.set_at((14, 5), (255, 20, 20, 255))
            # Armored body
            for y in range(10, 24):
                for x in range(5, 19):
                    c = 35 + int(20 * hash_noise(x, y, self.seed + 53))
                    s.set_at((x, y), (c, c, c + 5, 255))
            # Shoulder pauldrons
            for y in range(10, 14):
                for x in range(3, 7):
                    s.set_at((x, y), armor_hi)
                for x in range(17, 21):
                    s.set_at((x, y), armor_hi)
            # Legs
            for y in range(24, 32):
                for x in range(6, 11):
                    s.set_at((x, y), armor)
                for x in range(13, 18):
                    s.set_at((x, y), armor)
            # Sword in right hand (thin gray line)
            for y in range(8, 22):
                s.set_at((20, y), (140, 140, 160, 255))
            s.set_at((20, 7), (180, 180, 200, 255))
            return s
        return self._get("dark_knight", make)

    # ==================================================================
    # RESOURCES
    # ==================================================================
    def generate_tree(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((48, 64), pygame.SRCALPHA)
            for y in range(24, 64):
                for x in range(20, 28):
                    c = 90 + int(30 * hash_noise(x, y, self.seed + 1))
                    s.set_at((x, y), (c, int(c * 0.6), 30, 255))
            for rad in range(18, 8, -3):
                cy = 24
                for y in range(cy - rad, cy + rad):
                    for x in range(24 - rad, 24 + rad):
                        if ((x - 24) ** 2 + (y - cy) ** 2 < rad * rad
                                and random.random() > 0.2):
                            g = 80 + int(60 * hash_noise(x, y, self.seed + 2))
                            s.set_at((x, y), (30, g, 30, 255))
            return s
        return self._get("tree", make)

    def generate_rock(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((32, 24), pygame.SRCALPHA)
            for y in range(24):
                for x in range(32):
                    n = hash_noise(x, y, self.seed + 3)
                    if ((x - 16) ** 2 / 256 + (y - 12) ** 2 / 144
                            < 0.8 + n * 0.2):
                        c = int(110 + n * 40 - y * 1.5)
                        c = max(40, min(200, c))
                        s.set_at((x, y), (c, c, c, 255))
            return s
        return self._get("rock", make)

    # ==================================================================
    # TILES
    # ==================================================================
    def generate_grass_tile(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            for y in range(TILE_SIZE):
                for x in range(TILE_SIZE):
                    n = fbm_noise(x * 0.1, y * 0.1, self.seed + 4, 3)
                    g = int(90 + n * 60)
                    s.set_at((x, y), (40, g, 40))
            for _ in range(40):
                s.set_at((random.randint(0, 31), random.randint(0, 31)),
                         (60, 180, 60))
            return s
        return self._get("grass", make)

    def generate_dirt_tile(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            for y in range(TILE_SIZE):
                for x in range(TILE_SIZE):
                    n = hash_noise(x, y, self.seed + 5)
                    c = int(80 + n * 40)
                    s.set_at((x, y), (c, int(c * 0.7), 40))
            return s
        return self._get("dirt", make)

    def generate_sand_tile(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            for y in range(TILE_SIZE):
                for x in range(TILE_SIZE):
                    n = hash_noise(x, y, self.seed + 9)
                    c = int(190 + n * 40)
                    s.set_at((x, y), (c, int(c * 0.9), int(c * 0.65)))
            return s
        return self._get("sand", make)

    def generate_water_tile(self, frame: int = 0) -> pygame.Surface:
        key = f"water_{frame}"
        def make() -> pygame.Surface:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            for y in range(TILE_SIZE):
                for x in range(TILE_SIZE):
                    n = fbm_noise((x + frame * 2) * 0.1, y * 0.1,
                                  self.seed + 6, 2)
                    b = int(140 + n * 80)
                    s.set_at((x, y), (30, 80, min(255, b)))
            return s
        return self._get(key, make)

    def generate_stone_tile(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            for y in range(TILE_SIZE):
                for x in range(TILE_SIZE):
                    n = hash_noise(x // 4, y // 4, self.seed + 7)
                    c = int(100 + n * 50)
                    s.set_at((x, y), (c, c, min(255, c + 10)))
            for _ in range(3):
                pygame.draw.line(
                    s, (70, 70, 80),
                    (random.randint(2, 29), random.randint(2, 29)),
                    (random.randint(2, 29), random.randint(2, 29)), 1)
            return s
        return self._get("stone", make)

    def generate_forest_tile(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            for y in range(TILE_SIZE):
                for x in range(TILE_SIZE):
                    n = fbm_noise(x * 0.1, y * 0.1, self.seed + 60, 3)
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
        return self._get("forest", make)

    # ==================================================================
    # ORIGINAL ITEM ICONS (16×16)
    # ==================================================================
    def generate_item_wood(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(4, 12):
                for x in range(3, 13):
                    s.set_at((x, y), (140, 90, 40, 255))
                s.set_at((3, y), (110, 70, 30, 255))
                s.set_at((12, y), (160, 110, 50, 255))
            return s
        return self._get("item_wood", make)

    def generate_item_stone(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(16):
                for x in range(16):
                    if (x - 8) ** 2 + (y - 8) ** 2 < 36:
                        c = 120 + int(30 * hash_noise(x, y, self.seed + 8))
                        s.set_at((x, y), (c, c, c, 255))
            return s
        return self._get("item_stone", make)

    def generate_item_stick(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for i in range(12):
                s.set_at((3 + i, 12 - i), (140, 100, 50, 255))
                s.set_at((4 + i, 12 - i), (160, 120, 60, 255))
            return s
        return self._get("item_stick", make)

    def generate_item_berry(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(16):
                for x in range(16):
                    if (x - 8) ** 2 + (y - 9) ** 2 < 30:
                        r = 180 + int(40 * hash_noise(x, y, self.seed + 10))
                        s.set_at((x, y), (min(255, r), 30, 50, 255))
            s.set_at((8, 3), (60, 130, 40, 255))
            s.set_at((8, 4), (60, 130, 40, 255))
            s.set_at((6, 6), (255, 120, 130, 255))
            return s
        return self._get("item_berry", make)

    def generate_item_axe(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(3, 14):
                s.set_at((7, y), (120, 80, 40, 255))
            for y in range(2, 7):
                for x in range(8, 14):
                    if (x - 8) + (y - 2) < 6:
                        s.set_at((x, y), (180, 180, 200, 255))
            return s
        return self._get("item_axe", make)

    def generate_item_sword(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(1, 10):
                s.set_at((7, y), (180, 180, 200, 255))
                s.set_at((8, y), (200, 200, 220, 255))
            for x in range(5, 11):
                s.set_at((x, 10), (130, 90, 40, 255))
            for y in range(11, 15):
                s.set_at((7, y), (100, 70, 35, 255))
                s.set_at((8, y), (80, 55, 25, 255))
            s.set_at((7, 15), (170, 150, 50, 255))
            s.set_at((8, 15), (170, 150, 50, 255))
            return s
        return self._get("item_sword", make)

    def generate_item_torch(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(6, 15):
                s.set_at((7, y), (120, 80, 40, 255))
                s.set_at((8, y), (100, 65, 30, 255))
            for y in range(2, 7):
                for x in range(6, 10):
                    if (x - 8) ** 2 + (y - 4) ** 2 < 6:
                        rv = max(0, min(255, 255 - (4 - y) * 20))
                        gv = max(0, min(255, 180 - (4 - y) * 30))
                        s.set_at((x, y), (rv, gv, 30, 220))
            return s
        return self._get("item_torch", make)

    def generate_item_campfire(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for x in range(4, 12):
                s.set_at((x, 12), (100, 60, 30, 255))
                s.set_at((x, 13), (80, 50, 25, 255))
            for y in range(5, 12):
                for x in range(6, 10):
                    if (x - 8) ** 2 + (y - 8) ** 2 < 8:
                        s.set_at((x, y), (255, max(30, 150 - (8 - y) * 15),
                                          30, 200))
            return s
        return self._get("item_campfire", make)

    def generate_item_pie(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(5, 14):
                for x in range(3, 13):
                    dx, dy = (x - 8) / 5.0, (y - 9.5) / 4.5
                    if dx * dx + dy * dy < 1:
                        s.set_at((x, y), (200, 160, 80, 255))
            for y in range(6, 12):
                for x in range(4, 12):
                    dx, dy = (x - 8) / 4.0, (y - 9) / 3.0
                    if dx * dx + dy * dy < 0.7:
                        s.set_at((x, y), (180, 40, 60, 255))
            return s
        return self._get("item_pie", make)

    def generate_item_bandage(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(4, 12):
                for x in range(4, 12):
                    s.set_at((x, y), (230, 230, 230, 255))
            for i in range(4, 12):
                s.set_at((8, i), (200, 50, 50, 255))
                s.set_at((i, 8), (200, 50, 50, 255))
            return s
        return self._get("item_bandage", make)

    # ==================================================================
    # NEW ITEM ICONS (16×16)
    # ==================================================================
    def generate_item_iron_sword(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            blade = (200, 210, 230, 255)
            edge = (170, 180, 200, 255)
            for y in range(1, 10):
                s.set_at((7, y), blade)
                s.set_at((8, y), edge)
            s.set_at((7, 0), (220, 230, 240, 255))
            for x in range(5, 11):
                s.set_at((x, 10), (180, 160, 80, 255))
            for y in range(11, 15):
                s.set_at((7, y), (80, 60, 30, 255))
                s.set_at((8, y), (60, 45, 20, 255))
            s.set_at((7, 15), (200, 180, 60, 255))
            s.set_at((8, 15), (200, 180, 60, 255))
            return s
        return self._get("item_iron_sword", make)

    def generate_item_spear(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Shaft
            for y in range(4, 16):
                s.set_at((8, y), (120, 80, 40, 255))
            # Tip
            s.set_at((8, 1), (180, 190, 210, 255))
            s.set_at((7, 2), (180, 190, 210, 255))
            s.set_at((8, 2), (200, 210, 230, 255))
            s.set_at((9, 2), (180, 190, 210, 255))
            s.set_at((8, 3), (170, 180, 200, 255))
            return s
        return self._get("item_spear", make)

    def generate_item_bow(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            wood = (140, 90, 40, 255)
            string = (200, 200, 200, 255)
            # Arc
            for y in range(2, 14):
                x = int(6 + 4 * math.sin((y - 2) * math.pi / 12))
                s.set_at((x, y), wood)
                if x > 0:
                    s.set_at((x - 1, y), wood)
            # String
            for y in range(2, 14):
                s.set_at((6, y), string)
            return s
        return self._get("item_bow", make)

    def generate_item_arrow(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Shaft
            for y in range(4, 14):
                s.set_at((8, y), (140, 100, 50, 255))
            # Tip
            s.set_at((8, 2), (180, 180, 200, 255))
            s.set_at((7, 3), (180, 180, 200, 255))
            s.set_at((8, 3), (200, 200, 220, 255))
            s.set_at((9, 3), (180, 180, 200, 255))
            # Fletching
            s.set_at((7, 13), (200, 60, 60, 255))
            s.set_at((9, 13), (200, 60, 60, 255))
            s.set_at((7, 14), (200, 60, 60, 255))
            s.set_at((9, 14), (200, 60, 60, 255))
            return s
        return self._get("item_arrow", make)

    def generate_item_sling(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            leather = (160, 100, 50, 255)
            cord = (180, 160, 120, 255)
            # Pouch
            for y in range(6, 10):
                for x in range(6, 10):
                    if (x - 8) ** 2 + (y - 8) ** 2 < 6:
                        s.set_at((x, y), leather)
            # Cords
            for i in range(6):
                s.set_at((3 + i, 5 - i // 2), cord)
                s.set_at((10 + i, 5 + i // 2), cord)
            return s
        return self._get("item_sling", make)

    def generate_item_rock_ammo(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(16):
                for x in range(16):
                    if (x - 8) ** 2 + (y - 8) ** 2 < 20:
                        c = 100 + int(30 * hash_noise(x, y, self.seed + 40))
                        s.set_at((x, y), (c, c, c + 5, 255))
            return s
        return self._get("item_rock_ammo", make)

    def generate_item_sling_bullet(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(16):
                for x in range(16):
                    if (x - 8) ** 2 + (y - 8) ** 2 < 16:
                        c = 140 + int(20 * hash_noise(x, y, self.seed + 41))
                        s.set_at((x, y), (c, c, c + 10, 255))
            return s
        return self._get("item_sling_bullet", make)

    def generate_item_leather_armor(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            leather = (140, 85, 40, 255)
            dark = (110, 65, 30, 255)
            # Body
            for y in range(3, 14):
                for x in range(4, 12):
                    s.set_at((x, y), leather)
            # Shoulders
            for x in range(2, 14):
                s.set_at((x, 3), dark)
                s.set_at((x, 4), dark)
            # Centre line
            for y in range(5, 13):
                s.set_at((8, y), dark)
            return s
        return self._get("item_leather_armor", make)

    def generate_item_wood_shield(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(2, 14):
                for x in range(3, 13):
                    dx = (x - 8) / 5.0
                    dy = (y - 8) / 6.0
                    if dx * dx + dy * dy < 1:
                        c = 130 + int(20 * hash_noise(x, y, self.seed + 42))
                        s.set_at((x, y), (c, int(c * 0.7), 30, 255))
            # Metal boss
            pygame.draw.circle(s, (180, 180, 200, 255), (8, 8), 2)
            return s
        return self._get("item_wood_shield", make)

    def generate_item_trap(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            metal = (160, 160, 180, 255)
            spike = (200, 200, 220, 255)
            # Base
            for x in range(3, 13):
                s.set_at((x, 12), metal)
                s.set_at((x, 13), metal)
            # Spikes
            for i in range(4):
                bx = 4 + i * 3
                for j in range(4):
                    s.set_at((bx, 11 - j), spike)
            return s
        return self._get("item_trap", make)

    def generate_item_bed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            frame = (120, 80, 40, 255)
            sheet = (200, 200, 220, 255)
            pillow = (220, 220, 240, 255)
            # Frame
            for x in range(2, 14):
                s.set_at((x, 12), frame)
                s.set_at((x, 13), frame)
            s.set_at((2, 11), frame); s.set_at((13, 11), frame)
            # Sheet
            for y in range(7, 12):
                for x in range(3, 13):
                    s.set_at((x, y), sheet)
            # Pillow
            for y in range(5, 8):
                for x in range(3, 7):
                    s.set_at((x, y), pillow)
            return s
        return self._get("item_bed", make)

    # ==================================================================
    # NEW ITEM ICONS — PHASE 2 (16×16)
    # ==================================================================
    def generate_item_iron(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Metallic ingot shape
            for y in range(5, 12):
                for x in range(3, 13):
                    c = 160 + int(25 * hash_noise(x, y, self.seed + 61))
                    s.set_at((x, y), (c, c, c + 10, 255))
            # Top highlight
            for x in range(4, 12):
                s.set_at((x, 5), (200, 200, 215, 255))
            # Bottom shadow
            for x in range(3, 13):
                s.set_at((x, 11), (120, 120, 130, 255))
            return s
        return self._get("item_iron", make)

    def generate_item_cloth(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Folded fabric shape
            for y in range(4, 13):
                for x in range(3, 13):
                    c = 220 + int(15 * hash_noise(x, y, self.seed + 62))
                    s.set_at((x, y), (c, c, min(255, c - 5), 255))
            # Fold lines
            for y in range(5, 12):
                s.set_at((6, y), (190, 190, 185, 255))
                s.set_at((10, y), (190, 190, 185, 255))
            return s
        return self._get("item_cloth", make)

    def generate_item_bone(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            bone = (230, 225, 210, 255)
            dark = (200, 195, 180, 255)
            # Femur shaft
            for y in range(5, 12):
                s.set_at((7, y), bone)
                s.set_at((8, y), bone)
            # Top knob
            for y in range(3, 6):
                for x in range(5, 10):
                    if (x - 7) ** 2 + (y - 4) ** 2 < 5:
                        s.set_at((x, y), bone)
            # Bottom knob
            for y in range(11, 14):
                for x in range(5, 10):
                    if (x - 8) ** 2 + (y - 12) ** 2 < 5:
                        s.set_at((x, y), bone)
            # Joint lines
            s.set_at((7, 5), dark)
            s.set_at((8, 11), dark)
            return s
        return self._get("item_bone", make)

    def generate_item_leather(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Leather hide shape (irregular)
            for y in range(3, 14):
                for x in range(3, 13):
                    dx = (x - 8) / 5.5
                    dy = (y - 8.5) / 5.5
                    if dx * dx + dy * dy < 0.9 + 0.1 * hash_noise(x, y, self.seed + 63):
                        c = 140 + int(30 * hash_noise(x, y, self.seed + 64))
                        s.set_at((x, y), (c, int(c * 0.6), int(c * 0.25), 255))
            return s
        return self._get("item_leather", make)

    def generate_item_health_potion(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            glass = (220, 220, 230, 255)
            # Flask neck
            for y in range(2, 5):
                s.set_at((7, y), glass)
                s.set_at((8, y), glass)
            # Cork
            s.set_at((7, 2), (160, 120, 70, 255))
            s.set_at((8, 2), (160, 120, 70, 255))
            # Flask body
            for y in range(5, 14):
                for x in range(4, 12):
                    dx = (x - 8) / 4.0
                    dy = (y - 9.5) / 4.5
                    if dx * dx + dy * dy < 1.0:
                        s.set_at((x, y), (200, 30, 40, 255))
            # Glass highlight
            s.set_at((6, 7), (255, 120, 130, 255))
            s.set_at((6, 8), (255, 120, 130, 255))
            return s
        return self._get("item_health_potion", make)

    def generate_item_antidote(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            glass = (220, 220, 230, 255)
            # Flask neck
            for y in range(2, 5):
                s.set_at((7, y), glass)
                s.set_at((8, y), glass)
            # Cork
            s.set_at((7, 2), (160, 120, 70, 255))
            s.set_at((8, 2), (160, 120, 70, 255))
            # Flask body (green liquid)
            for y in range(5, 14):
                for x in range(4, 12):
                    dx = (x - 8) / 4.0
                    dy = (y - 9.5) / 4.5
                    if dx * dx + dy * dy < 1.0:
                        s.set_at((x, y), (30, 180, 50, 255))
            # Glass highlight
            s.set_at((6, 7), (120, 240, 140, 255))
            s.set_at((6, 8), (120, 240, 140, 255))
            return s
        return self._get("item_antidote", make)

    def generate_item_iron_axe(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Handle
            for y in range(3, 14):
                s.set_at((7, y), (120, 80, 40, 255))
            # Metallic axe head (silver/gray)
            for y in range(2, 7):
                for x in range(8, 14):
                    if (x - 8) + (y - 2) < 6:
                        c = 170 + int(20 * hash_noise(x, y, self.seed + 65))
                        s.set_at((x, y), (c, c, c + 15, 255))
            return s
        return self._get("item_iron_axe", make)

    def generate_item_mace(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Brown handle
            for y in range(7, 15):
                s.set_at((7, y), (120, 80, 40, 255))
                s.set_at((8, y), (100, 65, 30, 255))
            # Spiked metal head
            for y in range(2, 8):
                for x in range(5, 11):
                    if (x - 8) ** 2 + (y - 5) ** 2 < 10:
                        s.set_at((x, y), (160, 160, 175, 255))
            # Spikes
            s.set_at((8, 1), (190, 190, 210, 255))
            s.set_at((4, 5), (190, 190, 210, 255))
            s.set_at((11, 5), (190, 190, 210, 255))
            s.set_at((5, 2), (190, 190, 210, 255))
            s.set_at((11, 2), (190, 190, 210, 255))
            return s
        return self._get("item_mace", make)

    def generate_item_bone_club(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            bone = (230, 225, 210, 255)
            dark = (200, 195, 180, 255)
            # Shaft (thinner bottom)
            for y in range(8, 15):
                s.set_at((7, y), bone)
                s.set_at((8, y), bone)
            # Club head (wider top)
            for y in range(2, 9):
                for x in range(5, 11):
                    if (x - 8) ** 2 + (y - 5) ** 2 < 12:
                        s.set_at((x, y), bone)
            # Cracks
            s.set_at((7, 4), dark)
            s.set_at((9, 6), dark)
            return s
        return self._get("item_bone_club", make)

    def generate_item_crossbow(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            wood = (140, 90, 40, 255)
            metal = (170, 170, 185, 255)
            string = (200, 200, 200, 255)
            # Stock (vertical)
            for y in range(5, 14):
                s.set_at((8, y), wood)
                s.set_at((9, y), wood)
            # Horizontal cross piece (bow)
            for x in range(2, 14):
                s.set_at((x, 5), wood)
                s.set_at((x, 6), wood)
            # String
            pygame.draw.line(s, string, (2, 5), (8, 7), 1)
            pygame.draw.line(s, string, (13, 5), (8, 7), 1)
            # Metal tip
            s.set_at((8, 4), metal)
            s.set_at((9, 4), metal)
            return s
        return self._get("item_crossbow", make)

    def generate_item_fire_arrow(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Shaft
            for y in range(6, 14):
                s.set_at((8, y), (140, 100, 50, 255))
            # Flame tip (orange/red)
            s.set_at((8, 3), (255, 200, 30, 255))
            s.set_at((7, 4), (255, 140, 20, 255))
            s.set_at((8, 4), (255, 80, 20, 255))
            s.set_at((9, 4), (255, 140, 20, 255))
            s.set_at((8, 5), (230, 60, 20, 255))
            s.set_at((7, 5), (255, 120, 30, 255))
            s.set_at((9, 5), (255, 120, 30, 255))
            # Fletching
            s.set_at((7, 13), (200, 60, 60, 255))
            s.set_at((9, 13), (200, 60, 60, 255))
            return s
        return self._get("item_fire_arrow", make)

    def generate_item_bolt(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Short thick shaft
            for y in range(5, 12):
                s.set_at((7, y), (140, 100, 50, 255))
                s.set_at((8, y), (140, 100, 50, 255))
            # Metal tip
            s.set_at((7, 3), (180, 180, 200, 255))
            s.set_at((8, 3), (180, 180, 200, 255))
            s.set_at((7, 4), (200, 200, 220, 255))
            s.set_at((8, 4), (200, 200, 220, 255))
            # Fletching (small)
            s.set_at((6, 11), (100, 100, 110, 255))
            s.set_at((9, 11), (100, 100, 110, 255))
            return s
        return self._get("item_bolt", make)

    def generate_item_iron_armor(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            metal = (160, 165, 180, 255)
            dark = (120, 125, 140, 255)
            # Body
            for y in range(3, 14):
                for x in range(4, 12):
                    c = 155 + int(20 * hash_noise(x, y, self.seed + 66))
                    s.set_at((x, y), (c, c, c + 15, 255))
            # Shoulders
            for x in range(2, 14):
                s.set_at((x, 3), dark)
                s.set_at((x, 4), dark)
            # Centre line
            for y in range(5, 13):
                s.set_at((8, y), dark)
            return s
        return self._get("item_iron_armor", make)

    def generate_item_iron_shield(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(2, 14):
                for x in range(3, 13):
                    dx = (x - 8) / 5.0
                    dy = (y - 8) / 6.0
                    if dx * dx + dy * dy < 1:
                        c = 155 + int(25 * hash_noise(x, y, self.seed + 67))
                        s.set_at((x, y), (c, c, c + 15, 255))
            # Metal boss
            pygame.draw.circle(s, (200, 205, 220, 255), (8, 8), 2)
            # Rivets
            s.set_at((5, 4), (120, 120, 135, 255))
            s.set_at((11, 4), (120, 120, 135, 255))
            s.set_at((5, 12), (120, 120, 135, 255))
            s.set_at((11, 12), (120, 120, 135, 255))
            return s
        return self._get("item_iron_shield", make)

    # ==================================================================
    # BUILDING / PLACEABLE ITEM ICONS (16×16)
    # ==================================================================
    def generate_item_wall(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(3, 14):
                for x in range(2, 14):
                    c = 130 + int(20 * hash_noise(x, y, self.seed + 68))
                    s.set_at((x, y), (c, int(c * 0.65), 30, 255))
            # Plank lines
            for y in range(3, 14):
                s.set_at((5, y), (100, 60, 25, 255))
                s.set_at((10, y), (100, 60, 25, 255))
            return s
        return self._get("item_wall", make)

    def generate_item_stone_wall_b(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(3, 14):
                for x in range(2, 14):
                    c = 120 + int(25 * hash_noise(x // 3, y // 3, self.seed + 69))
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
        return self._get("item_stone_wall_b", make)

    def generate_item_turret(self) -> pygame.Surface:
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
        return self._get("item_turret", make)

    def generate_item_chest(self) -> pygame.Surface:
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
        return self._get("item_chest", make)

    def generate_item_door(self) -> pygame.Surface:
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
        return self._get("item_door", make)

    # ==================================================================
    # PLACED OBJECTS
    # ==================================================================
    def generate_campfire(self, lit: bool = True) -> pygame.Surface:
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
        return self._get(f"campfire_{lit}", make)

    def generate_torch_placed(self) -> pygame.Surface:
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
        return self._get("torch_placed", make)

    def generate_trap_placed(self) -> pygame.Surface:
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
        return self._get("trap_placed", make)

    def generate_bed_placed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((48, 32), pygame.SRCALPHA)
            frame = (120, 80, 40, 255)
            sheet = (180, 180, 210, 255)
            pillow = (210, 210, 230, 255)
            # Frame
            for x in range(4, 44):
                for y in range(22, 28):
                    s.set_at((x, y), frame)
            # Mattress
            for x in range(6, 42):
                for y in range(14, 22):
                    s.set_at((x, y), sheet)
            # Pillow
            for x in range(6, 16):
                for y in range(12, 16):
                    s.set_at((x, y), pillow)
            # Headboard
            for y in range(8, 22):
                s.set_at((4, y), frame)
                s.set_at((5, y), frame)
            return s
        return self._get("bed_placed", make)

    def generate_wall_placed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((32, 32), pygame.SRCALPHA)
            for y in range(4, 28):
                for x in range(4, 28):
                    c = 130 + int(25 * hash_noise(x, y, self.seed + 70))
                    s.set_at((x, y), (c, int(c * 0.65), 30, 255))
            # Plank dividers
            for y in range(4, 28):
                s.set_at((10, y), (90, 55, 20, 255))
                s.set_at((16, y), (90, 55, 20, 255))
                s.set_at((22, y), (90, 55, 20, 255))
            return s
        return self._get("wall_placed", make)

    def generate_stone_wall_placed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((32, 32), pygame.SRCALPHA)
            for y in range(4, 28):
                for x in range(4, 28):
                    c = 115 + int(30 * hash_noise(x // 4, y // 4, self.seed + 71))
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
        return self._get("stone_wall_placed", make)

    def generate_turret_placed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((32, 32), pygame.SRCALPHA)
            wood = (130, 85, 40, 255)
            metal = (140, 140, 155, 255)
            # Wooden platform
            for y in range(20, 28):
                for x in range(4, 28):
                    c = 120 + int(20 * hash_noise(x, y, self.seed + 72))
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
        return self._get("turret_placed", make)

    def generate_chest_placed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((32, 24), pygame.SRCALPHA)
            wood = (140, 90, 40, 255)
            dark = (100, 60, 25, 255)
            gold = (220, 190, 50, 255)
            # Chest body
            for y in range(6, 20):
                for x in range(4, 28):
                    c = 135 + int(20 * hash_noise(x, y, self.seed + 73))
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
        return self._get("chest_placed", make)

    def generate_door_placed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((24, 32), pygame.SRCALPHA)
            wood = (140, 90, 45, 255)
            dark = (100, 60, 25, 255)
            # Door body
            for y in range(2, 30):
                for x in range(4, 20):
                    c = 135 + int(20 * hash_noise(x, y, self.seed + 74))
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
        return self._get("door_placed", make)

    # ==================================================================
    # PROJECTILES
    # ==================================================================
    def generate_projectile_arrow(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((8, 8), pygame.SRCALPHA)
            # Shaft
            for i in range(6):
                s.set_at((1 + i, 4), (140, 100, 50, 255))
            # Tip
            s.set_at((7, 4), (200, 200, 220, 255))
            s.set_at((7, 3), (200, 200, 220, 255))
            return s
        return self._get("proj_arrow", make)

    def generate_projectile_rock(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((8, 8), pygame.SRCALPHA)
            for y in range(2, 6):
                for x in range(2, 6):
                    if (x - 4) ** 2 + (y - 4) ** 2 < 5:
                        s.set_at((x, y), (130, 130, 140, 255))
            return s
        return self._get("proj_rock", make)

    def generate_projectile_bolt(self) -> pygame.Surface:
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
        return self._get("proj_bolt", make)
