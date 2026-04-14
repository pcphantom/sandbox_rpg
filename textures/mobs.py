"""Mob texture generation — slime through boss_troll_king."""
import random
import math
import pygame
from core.utils import hash_noise


def generate_slime(gen) -> pygame.Surface:
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
    return gen._get("slime", make)


def generate_skeleton(gen) -> pygame.Surface:
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
    return gen._get("skeleton", make)


def generate_wolf(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 24), pygame.SRCALPHA)
        # Body — dark grey ellipse
        for y in range(8, 22):
            for x in range(4, 28):
                dx = (x - 16) / 12.0
                dy = (y - 15) / 7.0
                if dx * dx + dy * dy < 1.0:
                    c = 70 + int(20 * hash_noise(x, y, gen.seed + 20))
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
    return gen._get("wolf", make)


def generate_goblin(gen) -> pygame.Surface:
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
                c = 100 + int(20 * hash_noise(x, y, gen.seed + 30))
                s.set_at((x, y), (c, int(c * 0.5), 30, 255))
        # Legs
        for y in range(24, 28):
            for x in range(7, 10):
                s.set_at((x, y), dark_skin)
            for x in range(12, 15):
                s.set_at((x, y), dark_skin)
        return s
    return gen._get("goblin", make)


def generate_ghost(gen) -> pygame.Surface:
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
    return gen._get("ghost", make)


def generate_spider(gen) -> pygame.Surface:
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
                    c = 70 + int(20 * hash_noise(x, y, gen.seed + 50))
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
    return gen._get("spider", make)


def generate_orc(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((26, 32), pygame.SRCALPHA)
        skin = (90, 120, 60, 255)
        dark_skin = (70, 95, 45, 255)
        # Head
        for y in range(2, 12):
            for x in range(7, 19):
                if (x - 13) ** 2 + (y - 7) ** 2 < 35:
                    c = 90 + int(20 * hash_noise(x, y, gen.seed + 51))
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
                c = 85 + int(25 * hash_noise(x, y, gen.seed + 52))
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
    return gen._get("orc", make)


def generate_dark_knight(gen) -> pygame.Surface:
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
                c = 35 + int(20 * hash_noise(x, y, gen.seed + 53))
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
    return gen._get("dark_knight", make)


def generate_zombie(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((24, 32), pygame.SRCALPHA)
        skin = (110, 140, 100, 255)
        dark_skin = (80, 105, 70, 255)
        # Head
        for y in range(2, 11):
            for x in range(8, 16):
                if (x - 12) ** 2 + (y - 6) ** 2 < 20:
                    c = 100 + int(20 * hash_noise(x, y, gen.seed + 60))
                    s.set_at((x, y), (c, int(c * 1.2), c - 10, 255))
        # Sunken eyes
        s.set_at((10, 5), (40, 20, 20, 255))
        s.set_at((11, 5), (40, 20, 20, 255))
        s.set_at((13, 5), (40, 20, 20, 255))
        s.set_at((14, 5), (40, 20, 20, 255))
        # Mouth
        for x in range(10, 14):
            s.set_at((x, 9), (50, 30, 30, 255))
        # Tattered body
        for y in range(11, 24):
            for x in range(6, 18):
                c = 80 + int(30 * hash_noise(x, y, gen.seed + 61))
                s.set_at((x, y), (c - 10, c, c - 20, 255))
        # Arms (outstretched)
        for y in range(13, 20):
            s.set_at((4, y), skin); s.set_at((5, y), skin)
            s.set_at((18, y), skin); s.set_at((19, y), skin)
        # Legs
        for y in range(24, 31):
            for x in range(7, 11):
                s.set_at((x, y), dark_skin)
            for x in range(13, 17):
                s.set_at((x, y), dark_skin)
        return s
    return gen._get("zombie", make)


def generate_wraith(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((24, 28), pygame.SRCALPHA)
        # Translucent dark body
        for y in range(28):
            for x in range(24):
                dx = (x - 12) / 12.0
                dy = (y - 11) / 14.0
                if dx * dx + dy * dy < 0.8 and y < 24:
                    a = 100 + int(40 * math.sin(y * 0.5))
                    c = 60 + int(20 * hash_noise(x, y, gen.seed + 62))
                    s.set_at((x, y), (c, 30, c + 40, a))
        # Wispy bottom
        for x in range(5, 19):
            wy = 22 + int(2 * math.sin(x * 0.9))
            for y in range(wy, min(wy + 4, 28)):
                s.set_at((x, y), (80, 30, 100, 60))
        # Glowing purple eyes
        pygame.draw.circle(s, (200, 100, 255, 220), (9, 9), 2)
        pygame.draw.circle(s, (200, 100, 255, 220), (15, 9), 2)
        return s
    return gen._get("wraith", make)


def generate_troll(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((28, 34), pygame.SRCALPHA)
        skin = (70, 110, 55, 255)
        dark_skin = (55, 85, 40, 255)
        # Large head
        for y in range(2, 13):
            for x in range(7, 21):
                if (x - 14) ** 2 + (y - 7) ** 2 < 45:
                    c = 70 + int(25 * hash_noise(x, y, gen.seed + 63))
                    s.set_at((x, y), (c, int(c * 1.4), c - 15, 255))
        # Small angry eyes
        s.set_at((11, 6), (255, 60, 20, 255))
        s.set_at((17, 6), (255, 60, 20, 255))
        # Wide mouth with teeth
        for x in range(10, 18):
            s.set_at((x, 10), (40, 25, 15, 255))
        s.set_at((11, 10), (230, 230, 210, 255))
        s.set_at((14, 10), (230, 230, 210, 255))
        s.set_at((16, 10), (230, 230, 210, 255))
        # Hulking body
        for y in range(13, 26):
            for x in range(4, 24):
                c = 65 + int(30 * hash_noise(x, y, gen.seed + 64))
                s.set_at((x, y), (c, int(c * 1.3), c - 15, 255))
        # Brown loincloth
        for y in range(22, 28):
            for x in range(8, 20):
                s.set_at((x, y), (70, 50, 30, 255))
        # Thick legs
        for y in range(28, 34):
            for x in range(7, 13):
                s.set_at((x, y), dark_skin)
            for x in range(15, 21):
                s.set_at((x, y), dark_skin)
        return s
    return gen._get("troll", make)


def generate_skeleton_archer(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((24, 32), pygame.SRCALPHA)
        bone = (220, 220, 210, 255)
        dark = (160, 160, 150, 255)
        # Skull
        for y in range(2, 10):
            for x in range(8, 16):
                if (x - 12) ** 2 + (y - 6) ** 2 < 18:
                    s.set_at((x, y), bone)
        # Hollow eyes
        s.set_at((10, 5), (20, 20, 20, 255))
        s.set_at((11, 5), (20, 20, 20, 255))
        s.set_at((13, 5), (20, 20, 20, 255))
        s.set_at((14, 5), (20, 20, 20, 255))
        # Jaw line
        for x in range(9, 15):
            s.set_at((x, 9), dark)
        # Spine
        for y in range(10, 22):
            s.set_at((11, y), bone)
            s.set_at((12, y), bone)
        # Ribs
        for y in range(12, 18, 2):
            for x in range(8, 16):
                if abs(x - 12) + abs(y - 15) < 5:
                    s.set_at((x, y), dark)
        # Legs
        for y in range(22, 30):
            s.set_at((9, y), bone); s.set_at((10, y), bone)
            s.set_at((13, y), bone); s.set_at((14, y), bone)
        # Left arm holding bow
        for y in range(12, 20):
            s.set_at((6, y), bone); s.set_at((7, y), bone)
        # Bow (curved brown line in left hand)
        for i in range(8):
            bx = 4 - abs(i - 4) // 2
            s.set_at((bx + 2, 12 + i), (120, 80, 40, 255))
        # Bowstring
        for i in range(8):
            s.set_at((5, 12 + i), (180, 180, 170, 255))
        # Right arm
        for y in range(12, 20):
            s.set_at((16, y), bone); s.set_at((17, y), bone)
        return s
    return gen._get("skeleton_archer", make)


def generate_goblin_shaman(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((22, 28), pygame.SRCALPHA)
        skin = (80, 140, 60, 255)
        robe = (90, 40, 120, 255)
        # Head
        for y in range(2, 11):
            for x in range(5, 17):
                if (x - 11) ** 2 + (y - 6) ** 2 < 28:
                    s.set_at((x, y), skin)
        # Pointy ears
        for i in range(4):
            s.set_at((4 - i, 4 + i), skin)
            s.set_at((17 + i, 4 + i), skin)
        # Glowing purple eyes
        s.set_at((9, 5), (200, 80, 255, 255))
        s.set_at((13, 5), (200, 80, 255, 255))
        # Purple robe body
        for y in range(11, 24):
            for x in range(5, 17):
                c = 80 + int(20 * hash_noise(x, y, gen.seed + 66))
                s.set_at((x, y), (c, int(c * 0.45), int(c * 1.3), 255))
        # Robe trim (gold)
        for x in range(5, 17):
            s.set_at((x, 11), (200, 180, 60, 255))
            s.set_at((x, 23), (200, 180, 60, 255))
        # Staff in right hand (purple glow tip)
        for y in range(4, 24):
            s.set_at((19, y), (100, 70, 40, 255))
        pygame.draw.circle(s, (180, 80, 240, 200), (19, 3), 2)
        # Legs
        for y in range(24, 28):
            for x in range(7, 10):
                s.set_at((x, y), (60, 110, 45, 255))
            for x in range(12, 15):
                s.set_at((x, y), (60, 110, 45, 255))
        return s
    return gen._get("goblin_shaman", make)


def generate_boss_golem(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 36), pygame.SRCALPHA)
        # Massive stone body
        for y in range(4, 30):
            for x in range(4, 28):
                dx = (x - 16) / 12.0
                dy = (y - 17) / 13.0
                if dx * dx + dy * dy < 1.0:
                    c = 120 + int(30 * hash_noise(x, y, gen.seed + 67))
                    s.set_at((x, y), (c, c - 10, c - 20, 255))
        # Stone head
        for y in range(1, 10):
            for x in range(9, 23):
                if (x - 16) ** 2 + (y - 5) ** 2 < 40:
                    c = 130 + int(20 * hash_noise(x, y, gen.seed + 68))
                    s.set_at((x, y), (c, c - 10, c - 20, 255))
        # Glowing red eyes
        pygame.draw.circle(s, (255, 40, 20, 255), (13, 5), 2)
        pygame.draw.circle(s, (255, 40, 20, 255), (19, 5), 2)
        # Cracks with red glow
        for i in range(6):
            cx = 10 + i * 2
            cy = 14 + int(2 * math.sin(i))
            s.set_at((cx, cy), (200, 50, 30, 200))
            s.set_at((cx, cy + 1), (180, 40, 25, 150))
        # Thick arms
        for y in range(10, 22):
            for x in range(1, 5):
                s.set_at((x, y), (110, 100, 90, 255))
            for x in range(27, 31):
                s.set_at((x, y), (110, 100, 90, 255))
        # Heavy legs
        for y in range(28, 36):
            for x in range(7, 14):
                s.set_at((x, y), (100, 90, 80, 255))
            for x in range(18, 25):
                s.set_at((x, y), (100, 90, 80, 255))
        return s
    return gen._get("boss_golem", make)


def generate_boss_lich(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((26, 34), pygame.SRCALPHA)
        # Dark flowing robe
        for y in range(8, 32):
            for x in range(4, 22):
                dx = (x - 13) / 9.0
                dy = (y - 20) / 12.0
                if dx * dx + dy * dy < 1.0:
                    c = 25 + int(15 * hash_noise(x, y, gen.seed + 69))
                    s.set_at((x, y), (c, c, c + 10, 255))
        # Wispy robe bottom
        for x in range(5, 21):
            wy = 29 + int(2 * math.sin(x * 0.7))
            for y in range(wy, min(wy + 3, 34)):
                s.set_at((x, y), (20, 20, 30, 180))
        # Skull-like head
        for y in range(1, 10):
            for x in range(8, 18):
                if (x - 13) ** 2 + (y - 5) ** 2 < 22:
                    s.set_at((x, y), (200, 200, 190, 255))
        # Hollow glowing purple eyes
        pygame.draw.circle(s, (180, 50, 255, 240), (11, 5), 2)
        pygame.draw.circle(s, (180, 50, 255, 240), (15, 5), 2)
        # Purple glow aura around head
        for y in range(0, 11):
            for x in range(6, 20):
                if (x - 13) ** 2 + (y - 5) ** 2 < 35:
                    if (x - 13) ** 2 + (y - 5) ** 2 >= 22:
                        a = 60 + int(30 * math.sin(x + y))
                        s.set_at((x, y), (120, 40, 180, a))
        # Staff in left hand
        for y in range(2, 30):
            s.set_at((4, y), (80, 60, 40, 255))
        pygame.draw.circle(s, (200, 80, 255, 220), (4, 1), 2)
        return s
    return gen._get("boss_lich", make)


def generate_boss_dragon(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((34, 38), pygame.SRCALPHA)
        # Dragon body (orange-red)
        for y in range(6, 32):
            for x in range(4, 30):
                dx = (x - 17) / 13.0
                dy = (y - 19) / 13.0
                if dx * dx + dy * dy < 1.0:
                    r = 180 + int(40 * hash_noise(x, y, gen.seed + 80))
                    g = 80 + int(30 * hash_noise(x, y, gen.seed + 81))
                    s.set_at((x, y), (min(r, 255), g, 20, 255))
        # Head
        for y in range(1, 10):
            for x in range(10, 24):
                if (x - 17) ** 2 + (y - 5) ** 2 < 35:
                    s.set_at((x, y), (200, 100, 30, 255))
        # Fire-orange eyes
        pygame.draw.circle(s, (255, 200, 0, 255), (14, 5), 2)
        pygame.draw.circle(s, (255, 200, 0, 255), (20, 5), 2)
        # Wings
        for y in range(8, 20):
            for x in range(0, 5):
                a = 200 - (4 - x) * 40
                s.set_at((x, y), (160, 60, 20, max(a, 40)))
            for x in range(29, 34):
                a = 200 - (x - 29) * 40
                s.set_at((x, y), (160, 60, 20, max(a, 40)))
        # Tail
        for i in range(8):
            tx = 17 + i
            ty = 30 + int(2 * math.sin(i * 0.8))
            if 0 <= tx < 34 and 0 <= ty < 38:
                s.set_at((tx, ty), (160, 70, 20, 220))
        return s
    return gen._get("boss_dragon", make)


def generate_boss_necromancer(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((26, 34), pygame.SRCALPHA)
        # Dark green robe
        for y in range(8, 32):
            for x in range(4, 22):
                dx = (x - 13) / 9.0
                dy = (y - 20) / 12.0
                if dx * dx + dy * dy < 1.0:
                    g = 40 + int(20 * hash_noise(x, y, gen.seed + 82))
                    s.set_at((x, y), (15, g, 15, 255))
        # Pale face
        for y in range(1, 10):
            for x in range(8, 18):
                if (x - 13) ** 2 + (y - 5) ** 2 < 22:
                    s.set_at((x, y), (180, 200, 170, 255))
        # Green glowing eyes
        pygame.draw.circle(s, (60, 255, 60, 240), (11, 5), 2)
        pygame.draw.circle(s, (60, 255, 60, 240), (15, 5), 2)
        # Green aura
        for y in range(0, 11):
            for x in range(6, 20):
                d2 = (x - 13) ** 2 + (y - 5) ** 2
                if 22 <= d2 < 35:
                    a = 50 + int(30 * math.sin(x + y))
                    s.set_at((x, y), (40, 180, 40, a))
        # Staff with skull
        for y in range(2, 30):
            s.set_at((4, y), (60, 50, 40, 255))
        pygame.draw.circle(s, (200, 200, 180, 220), (4, 1), 2)
        return s
    return gen._get("boss_necromancer", make)


def generate_boss_troll_king(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((34, 40), pygame.SRCALPHA)
        # Massive green-brown body
        for y in range(5, 34):
            for x in range(4, 30):
                dx = (x - 17) / 13.0
                dy = (y - 20) / 15.0
                if dx * dx + dy * dy < 1.0:
                    g = 80 + int(30 * hash_noise(x, y, gen.seed + 83))
                    s.set_at((x, y), (60, g, 40, 255))
        # Head
        for y in range(1, 10):
            for x in range(9, 25):
                if (x - 17) ** 2 + (y - 5) ** 2 < 50:
                    g = 90 + int(20 * hash_noise(x, y, gen.seed + 84))
                    s.set_at((x, y), (70, g, 50, 255))
        # Yellow angry eyes
        pygame.draw.circle(s, (255, 255, 0, 255), (13, 5), 2)
        pygame.draw.circle(s, (255, 255, 0, 255), (21, 5), 2)
        # Crown
        for x in range(10, 24):
            s.set_at((x, 0), (200, 180, 50, 255))
            if x % 3 == 0:
                s.set_at((x, -1 if -1 >= 0 else 0), (200, 180, 50, 255))
        # Massive arms
        for y in range(10, 24):
            for x in range(0, 5):
                s.set_at((x, y), (70, 100, 50, 255))
            for x in range(29, 34):
                s.set_at((x, y), (70, 100, 50, 255))
        # Thick legs
        for y in range(32, 40):
            for x in range(7, 15):
                s.set_at((x, y), (60, 80, 40, 255))
            for x in range(19, 27):
                s.set_at((x, y), (60, 80, 40, 255))
        return s
    return gen._get("boss_troll_king", make)


def generate_snake(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 16), pygame.SRCALPHA)
        green = (80, 160, 50, 255)
        dark_green = (50, 120, 30, 255)
        belly = (120, 180, 80, 255)
        # Sinuous body
        for i in range(16):
            cx = 2 + i
            cy = 8 + int(3 * math.sin(i * 0.8))
            for dy in range(-2, 3):
                y = cy + dy
                if 0 <= y < 16 and 0 <= cx < 20:
                    c = green if dy < 0 else (belly if dy == 0 else dark_green)
                    s.set_at((cx, y), c)
        # Head (wider, at right end)
        hx, hy = 18, 8 + int(3 * math.sin(15 * 0.8))
        for dy in range(-2, 3):
            for dx in range(-1, 2):
                px, py = hx + dx, hy + dy
                if 0 <= px < 20 and 0 <= py < 16:
                    s.set_at((px, py), green)
        # Eyes
        ey = hy - 1
        if 0 <= ey < 16:
            s.set_at((18, ey), (255, 200, 0, 255))
            s.set_at((19, ey), (255, 200, 0, 255))
        # Forked tongue
        if 0 <= hy < 16:
            s.set_at((19, hy), (200, 50, 50, 255))
        return s
    return gen._get("snake", make)


def generate_kobold(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((24, 28), pygame.SRCALPHA)
        skin = (140, 100, 60, 255)
        dark_skin = (110, 75, 45, 255)
        # Head (small, reptilian)
        for y in range(2, 10):
            for x in range(7, 17):
                if (x - 12) ** 2 + (y - 6) ** 2 < 22:
                    c = 130 + int(20 * hash_noise(x, y, gen.seed + 90))
                    s.set_at((x, y), (c, int(c * 0.72), int(c * 0.43), 255))
        # Pointy snout
        for i in range(3):
            s.set_at((17 + i, 7), skin)
            s.set_at((17 + i, 8), skin)
        # Yellow eyes
        s.set_at((10, 5), (255, 220, 0, 255))
        s.set_at((14, 5), (255, 220, 0, 255))
        # Small horns
        s.set_at((9, 2), dark_skin)
        s.set_at((15, 2), dark_skin)
        # Scrawny body with leather vest
        for y in range(10, 21):
            for x in range(7, 17):
                c = 90 + int(20 * hash_noise(x, y, gen.seed + 91))
                s.set_at((x, y), (c, int(c * 0.6), int(c * 0.3), 255))
        # Thin arms
        for y in range(11, 18):
            s.set_at((5, y), skin)
            s.set_at((6, y), skin)
            s.set_at((17, y), skin)
            s.set_at((18, y), skin)
        # Legs
        for y in range(21, 27):
            for x in range(8, 11):
                s.set_at((x, y), dark_skin)
            for x in range(13, 16):
                s.set_at((x, y), dark_skin)
        # Tail
        for i in range(5):
            s.set_at((12 + i, 22 + i // 2), dark_skin)
        return s
    return gen._get("kobold", make)


def generate_hobgoblin(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((24, 32), pygame.SRCALPHA)
        skin = (120, 80, 50, 255)
        dark_skin = (90, 60, 35, 255)
        # Head
        for y in range(2, 11):
            for x in range(6, 18):
                if (x - 12) ** 2 + (y - 6) ** 2 < 30:
                    c = 110 + int(20 * hash_noise(x, y, gen.seed + 92))
                    s.set_at((x, y), (c, int(c * 0.67), int(c * 0.42), 255))
        # Pointed ears
        for i in range(3):
            s.set_at((5 - i, 5 + i), skin)
            s.set_at((18 + i, 5 + i), skin)
        # Red eyes
        s.set_at((9, 5), (255, 40, 40, 255))
        s.set_at((10, 5), (255, 40, 40, 255))
        s.set_at((14, 5), (255, 40, 40, 255))
        s.set_at((15, 5), (255, 40, 40, 255))
        # Tusks
        s.set_at((9, 9), (230, 220, 200, 255))
        s.set_at((15, 9), (230, 220, 200, 255))
        # Armored body
        for y in range(11, 24):
            for x in range(5, 19):
                c = 50 + int(20 * hash_noise(x, y, gen.seed + 93))
                s.set_at((x, y), (c + 20, c, c - 10, 255))
        # Belt
        for x in range(6, 18):
            s.set_at((x, 20), (60, 50, 30, 255))
        # Arms
        for y in range(12, 20):
            s.set_at((3, y), dark_skin)
            s.set_at((4, y), dark_skin)
            s.set_at((19, y), dark_skin)
            s.set_at((20, y), dark_skin)
        # Sword in right hand
        for y in range(10, 22):
            s.set_at((21, y), (160, 160, 170, 255))
        s.set_at((21, 9), (180, 180, 200, 255))
        # Legs
        for y in range(24, 31):
            for x in range(6, 10):
                s.set_at((x, y), dark_skin)
            for x in range(14, 18):
                s.set_at((x, y), dark_skin)
        return s
    return gen._get("hobgoblin", make)


def generate_bear(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((28, 24), pygame.SRCALPHA)
        # Body — large brown ellipse
        for y in range(6, 20):
            for x in range(4, 24):
                dx = (x - 14) / 10.0
                dy = (y - 13) / 7.0
                if dx * dx + dy * dy < 1.0:
                    c = 90 + int(25 * hash_noise(x, y, gen.seed + 94))
                    s.set_at((x, y), (c, int(c * 0.7), int(c * 0.4), 255))
        # Head (round, at right)
        for y in range(3, 14):
            for x in range(20, 28):
                dx = (x - 24) / 4.0
                dy = (y - 8) / 5.5
                if dx * dx + dy * dy < 1.0:
                    c = 100 + int(15 * hash_noise(x, y, gen.seed + 95))
                    s.set_at((x, y), (c, int(c * 0.7), int(c * 0.4), 255))
        # Ears
        for dy in range(-1, 1):
            s.set_at((22, 3 + dy), (110, 75, 45, 255))
            s.set_at((26, 3 + dy), (110, 75, 45, 255))
        # Eyes
        s.set_at((23, 7), (30, 20, 10, 255))
        s.set_at((25, 7), (30, 20, 10, 255))
        # Nose
        s.set_at((27, 9), (20, 15, 10, 255))
        # Four legs
        for y in range(18, 24):
            s.set_at((7, y), (80, 55, 30, 255))
            s.set_at((8, y), (80, 55, 30, 255))
            s.set_at((11, y), (80, 55, 30, 255))
            s.set_at((12, y), (80, 55, 30, 255))
            s.set_at((17, y), (80, 55, 30, 255))
            s.set_at((18, y), (80, 55, 30, 255))
            s.set_at((21, y), (80, 55, 30, 255))
            s.set_at((22, y), (80, 55, 30, 255))
        return s
    return gen._get("bear", make)


def generate_orc_archer(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((26, 32), pygame.SRCALPHA)
        skin = (90, 120, 60, 255)
        dark_skin = (70, 95, 45, 255)
        # Head
        for y in range(2, 12):
            for x in range(7, 19):
                if (x - 13) ** 2 + (y - 7) ** 2 < 35:
                    c = 90 + int(20 * hash_noise(x, y, gen.seed + 96))
                    s.set_at((x, y), (c, int(c * 1.3), int(c * 0.65), 255))
        # Red eyes
        s.set_at((10, 6), (255, 30, 30, 255))
        s.set_at((11, 6), (255, 30, 30, 255))
        s.set_at((15, 6), (255, 30, 30, 255))
        s.set_at((16, 6), (255, 30, 30, 255))
        # Tusks
        s.set_at((10, 10), (240, 240, 230, 255))
        s.set_at((16, 10), (240, 240, 230, 255))
        # Body with leather armor
        for y in range(12, 24):
            for x in range(5, 21):
                c = 70 + int(25 * hash_noise(x, y, gen.seed + 97))
                s.set_at((x, y), (c, int(c * 0.7), int(c * 0.35), 255))
        # Left arm holding bow
        for y in range(12, 20):
            s.set_at((3, y), skin)
            s.set_at((4, y), skin)
        # Bow (curved brown line)
        for i in range(8):
            bx = 1 - abs(i - 4) // 2
            s.set_at((bx + 1, 12 + i), (120, 80, 40, 255))
        # Bowstring
        for i in range(8):
            s.set_at((3, 12 + i), (180, 180, 170, 255))
        # Right arm
        for y in range(12, 20):
            s.set_at((21, y), skin)
            s.set_at((22, y), skin)
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
    return gen._get("orc_archer", make)


def generate_mephit_fire(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 24), pygame.SRCALPHA)
        # Fiery body
        for y in range(6, 22):
            for x in range(4, 16):
                dx = (x - 10) / 6.0
                dy = (y - 14) / 8.0
                if dx * dx + dy * dy < 1.0:
                    r = 200 + int(40 * hash_noise(x, y, gen.seed + 100))
                    g = 80 + int(60 * hash_noise(x, y, gen.seed + 101))
                    s.set_at((x, y), (min(r, 255), g, 20, 255))
        # Flickering flame top
        for i in range(5):
            fx = 8 + int(2 * math.sin(i * 1.2))
            for dy in range(3):
                fy = 5 - dy - i // 3
                if 0 <= fy < 24 and 0 <= fx < 20:
                    a = 200 - dy * 50
                    s.set_at((fx, fy), (255, 160, 30, max(a, 50)))
        # Eyes (bright yellow)
        s.set_at((8, 11), (255, 255, 100, 255))
        s.set_at((12, 11), (255, 255, 100, 255))
        # Small wings (orange)
        for y in range(9, 15):
            s.set_at((2, y), (220, 100, 20, 180))
            s.set_at((3, y), (220, 100, 20, 200))
            s.set_at((16, y), (220, 100, 20, 200))
            s.set_at((17, y), (220, 100, 20, 180))
        return s
    return gen._get("mephit_fire", make)


def generate_mephit_ice(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 24), pygame.SRCALPHA)
        # Icy body
        for y in range(6, 22):
            for x in range(4, 16):
                dx = (x - 10) / 6.0
                dy = (y - 14) / 8.0
                if dx * dx + dy * dy < 1.0:
                    b = 200 + int(40 * hash_noise(x, y, gen.seed + 102))
                    g = 160 + int(40 * hash_noise(x, y, gen.seed + 103))
                    s.set_at((x, y), (180, g, min(b, 255), 230))
        # Ice crystal top
        for i in range(4):
            fx = 9 + (i % 2)
            fy = 5 - i
            if 0 <= fy < 24:
                s.set_at((fx, fy), (200, 220, 255, 220))
                s.set_at((fx + 1, fy), (200, 220, 255, 220))
        # Blue-white eyes
        s.set_at((8, 11), (150, 200, 255, 255))
        s.set_at((12, 11), (150, 200, 255, 255))
        # Small wings (pale blue)
        for y in range(9, 15):
            s.set_at((2, y), (140, 180, 240, 180))
            s.set_at((3, y), (140, 180, 240, 200))
            s.set_at((16, y), (140, 180, 240, 200))
            s.set_at((17, y), (140, 180, 240, 180))
        return s
    return gen._get("mephit_ice", make)


def generate_mephit_lightning(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 24), pygame.SRCALPHA)
        # Electric body
        for y in range(6, 22):
            for x in range(4, 16):
                dx = (x - 10) / 6.0
                dy = (y - 14) / 8.0
                if dx * dx + dy * dy < 1.0:
                    yy = 180 + int(50 * hash_noise(x, y, gen.seed + 104))
                    s.set_at((x, y), (min(yy, 255), min(yy, 255), 40, 255))
        # Spark top
        for i in range(4):
            fx = 9 + int(math.sin(i * 1.5))
            fy = 5 - i
            if 0 <= fy < 24 and 0 <= fx < 20:
                s.set_at((fx, fy), (255, 255, 100, 230))
        # Bright white eyes
        s.set_at((8, 11), (255, 255, 255, 255))
        s.set_at((12, 11), (255, 255, 255, 255))
        # Small wings (yellow)
        for y in range(9, 15):
            s.set_at((2, y), (220, 200, 40, 180))
            s.set_at((3, y), (220, 200, 40, 200))
            s.set_at((16, y), (220, 200, 40, 200))
            s.set_at((17, y), (220, 200, 40, 180))
        # Lightning crackling arcs
        for i in range(3):
            lx = 6 + i * 3
            ly = 16 + int(2 * math.sin(i * 2.0))
            if 0 <= lx < 20 and 0 <= ly < 24:
                s.set_at((lx, ly), (255, 255, 200, 200))
        return s
    return gen._get("mephit_lightning", make)


def generate_ogre(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((36, 48), pygame.SRCALPHA)
        skin = (130, 110, 70, 255)
        dark_skin = (100, 85, 50, 255)
        # Large head
        for y in range(3, 16):
            for x in range(9, 27):
                if (x - 18) ** 2 + (y - 9) ** 2 < 65:
                    c = 120 + int(25 * hash_noise(x, y, gen.seed + 106))
                    s.set_at((x, y), (c, int(c * 0.85), int(c * 0.54), 255))
        # Small dull eyes
        s.set_at((14, 8), (180, 50, 30, 255))
        s.set_at((15, 8), (180, 50, 30, 255))
        s.set_at((21, 8), (180, 50, 30, 255))
        s.set_at((22, 8), (180, 50, 30, 255))
        # Wide mouth with underbite
        for x in range(13, 23):
            s.set_at((x, 13), (80, 50, 30, 255))
        s.set_at((14, 12), (230, 220, 200, 255))
        s.set_at((17, 12), (230, 220, 200, 255))
        s.set_at((20, 12), (230, 220, 200, 255))
        # Massive body
        for y in range(16, 36):
            for x in range(5, 31):
                dx = (x - 18) / 13.0
                dy = (y - 26) / 10.0
                if dx * dx + dy * dy < 1.0:
                    c = 115 + int(25 * hash_noise(x, y, gen.seed + 107))
                    s.set_at((x, y), (c, int(c * 0.85), int(c * 0.54), 255))
        # Loincloth
        for y in range(32, 38):
            for x in range(10, 26):
                s.set_at((x, y), (60, 45, 25, 255))
        # Massive arms
        for y in range(16, 30):
            for x in range(1, 6):
                s.set_at((x, y), skin)
            for x in range(30, 35):
                s.set_at((x, y), skin)
        # Club in right hand
        for y in range(12, 30):
            s.set_at((34, y), (80, 60, 30, 255))
            s.set_at((35, y), (80, 60, 30, 255))
        for y in range(10, 16):
            for dx in range(-1, 2):
                s.set_at((34 + dx, y), (90, 70, 35, 255))
        # Thick legs
        for y in range(36, 46):
            for x in range(9, 16):
                s.set_at((x, y), dark_skin)
            for x in range(20, 27):
                s.set_at((x, y), dark_skin)
        return s
    return gen._get("ogre", make)


def generate_ogre_mage(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((36, 48), pygame.SRCALPHA)
        skin = (110, 80, 140, 255)
        dark_skin = (85, 60, 110, 255)
        # Large head
        for y in range(3, 16):
            for x in range(9, 27):
                if (x - 18) ** 2 + (y - 9) ** 2 < 65:
                    c = 100 + int(25 * hash_noise(x, y, gen.seed + 108))
                    s.set_at((x, y), (c, int(c * 0.75), int(c * 1.2), 255))
        # Glowing purple eyes
        pygame.draw.circle(s, (200, 80, 255, 255), (15, 8), 2)
        pygame.draw.circle(s, (200, 80, 255, 255), (21, 8), 2)
        # Underbite tusks
        s.set_at((14, 12), (230, 220, 200, 255))
        s.set_at((22, 12), (230, 220, 200, 255))
        # Robed body
        for y in range(16, 38):
            for x in range(5, 31):
                dx = (x - 18) / 13.0
                dy = (y - 27) / 11.0
                if dx * dx + dy * dy < 1.0:
                    c = 50 + int(25 * hash_noise(x, y, gen.seed + 109))
                    s.set_at((x, y), (c + 20, c, c + 40, 255))
        # Robe trim (gold)
        for x in range(7, 29):
            s.set_at((x, 16), (200, 180, 60, 255))
            s.set_at((x, 37), (200, 180, 60, 255))
        # Arms
        for y in range(18, 30):
            for x in range(2, 6):
                s.set_at((x, y), dark_skin)
            for x in range(30, 34):
                s.set_at((x, y), dark_skin)
        # Staff with glowing orb
        for y in range(4, 38):
            s.set_at((34, y), (80, 60, 40, 255))
        pygame.draw.circle(s, (180, 80, 240, 220), (34, 3), 3)
        # Purple magic aura around orb
        for y in range(0, 7):
            for x in range(31, 36):
                d2 = (x - 34) ** 2 + (y - 3) ** 2
                if 9 <= d2 < 20:
                    a = 50 + int(30 * math.sin(x + y))
                    px, py = x, y
                    if 0 <= px < 36 and 0 <= py < 48:
                        s.set_at((px, py), (140, 50, 200, max(a, 20)))
        # Legs
        for y in range(38, 46):
            for x in range(10, 16):
                s.set_at((x, y), dark_skin)
            for x in range(20, 26):
                s.set_at((x, y), dark_skin)
        return s
    return gen._get("ogre_mage", make)


def generate_centaur(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((32, 32), pygame.SRCALPHA)
        horse = (140, 100, 60, 255)
        horse_dark = (110, 75, 45, 255)
        skin = (180, 150, 120, 255)
        # Horse body (lower)
        for y in range(16, 26):
            for x in range(4, 28):
                dx = (x - 16) / 12.0
                dy = (y - 21) / 5.0
                if dx * dx + dy * dy < 1.0:
                    c = 130 + int(20 * hash_noise(x, y, gen.seed + 110))
                    s.set_at((x, y), (c, int(c * 0.72), int(c * 0.43), 255))
        # Four horse legs
        for y in range(24, 32):
            s.set_at((7, y), horse_dark)
            s.set_at((8, y), horse_dark)
            s.set_at((12, y), horse_dark)
            s.set_at((13, y), horse_dark)
            s.set_at((20, y), horse_dark)
            s.set_at((21, y), horse_dark)
            s.set_at((25, y), horse_dark)
            s.set_at((26, y), horse_dark)
        # Tail
        for i in range(5):
            s.set_at((3 - i // 2, 20 + i), horse_dark)
        # Human torso (upper, at front-center)
        for y in range(6, 17):
            for x in range(12, 22):
                dx = (x - 17) / 5.0
                dy = (y - 11) / 5.5
                if dx * dx + dy * dy < 1.0:
                    s.set_at((x, y), skin)
        # Head
        for y in range(1, 8):
            for x in range(13, 21):
                if (x - 17) ** 2 + (y - 4) ** 2 < 16:
                    s.set_at((x, y), skin)
        # Eyes
        s.set_at((15, 3), (60, 40, 20, 255))
        s.set_at((19, 3), (60, 40, 20, 255))
        # Left arm holding bow
        for y in range(8, 16):
            s.set_at((10, y), skin)
            s.set_at((11, y), skin)
        # Bow
        for i in range(7):
            bx = 8 - abs(i - 3) // 2
            s.set_at((bx, 8 + i), (120, 80, 40, 255))
        # Bowstring
        for i in range(7):
            s.set_at((9, 8 + i), (180, 180, 170, 255))
        # Right arm
        for y in range(8, 16):
            s.set_at((22, y), skin)
            s.set_at((23, y), skin)
        return s
    return gen._get("centaur", make)


def generate_golem(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((36, 48), pygame.SRCALPHA)
        # Massive stone body
        for y in range(8, 38):
            for x in range(5, 31):
                dx = (x - 18) / 13.0
                dy = (y - 23) / 15.0
                if dx * dx + dy * dy < 1.0:
                    c = 130 + int(30 * hash_noise(x, y, gen.seed + 112))
                    s.set_at((x, y), (c, c - 10, c - 20, 255))
        # Stone head (blocky)
        for y in range(2, 12):
            for x in range(10, 26):
                if (x - 18) ** 2 + (y - 7) ** 2 < 50:
                    c = 140 + int(25 * hash_noise(x, y, gen.seed + 113))
                    s.set_at((x, y), (c, c - 10, c - 20, 255))
        # Glowing blue eyes
        pygame.draw.circle(s, (60, 150, 255, 255), (14, 7), 2)
        pygame.draw.circle(s, (60, 150, 255, 255), (22, 7), 2)
        # Cracks with blue energy
        for i in range(8):
            cx = 10 + i * 2
            cy = 20 + int(3 * math.sin(i * 0.9))
            if 0 <= cx < 36 and 0 <= cy < 48:
                s.set_at((cx, cy), (60, 120, 220, 200))
                if cy + 1 < 48:
                    s.set_at((cx, cy + 1), (50, 100, 190, 150))
        # Massive stone arms
        for y in range(12, 28):
            for x in range(1, 6):
                c = 120 + int(20 * hash_noise(x, y, gen.seed + 114))
                s.set_at((x, y), (c, c - 10, c - 15, 255))
            for x in range(30, 35):
                c = 120 + int(20 * hash_noise(x, y, gen.seed + 114))
                s.set_at((x, y), (c, c - 10, c - 15, 255))
        # Fists (wider at bottom of arms)
        for y in range(26, 30):
            for x in range(0, 7):
                s.set_at((x, y), (110, 100, 85, 255))
            for x in range(29, 36):
                s.set_at((x, y), (110, 100, 85, 255))
        # Heavy legs
        for y in range(36, 46):
            for x in range(8, 16):
                s.set_at((x, y), (110, 100, 85, 255))
            for x in range(20, 28):
                s.set_at((x, y), (110, 100, 85, 255))
        return s
    return gen._get("golem", make)


def _make_dragon(gen, key, body_rgb, wing_rgb, eye_rgb, seed_offset):
    """Shared factory for 48x48 dragon textures."""
    def make() -> pygame.Surface:
        s = pygame.Surface((48, 48), pygame.SRCALPHA)
        br, bg, bb = body_rgb
        wr, wg, wb = wing_rgb
        er, eg, eb = eye_rgb
        # Dragon body
        for y in range(10, 40):
            for x in range(8, 40):
                dx = (x - 24) / 16.0
                dy = (y - 25) / 15.0
                if dx * dx + dy * dy < 1.0:
                    c = 0.8 + 0.2 * hash_noise(x, y, gen.seed + seed_offset)
                    s.set_at((x, y), (int(br * c), int(bg * c), int(bb * c), 255))
        # Head
        for y in range(2, 14):
            for x in range(14, 34):
                if (x - 24) ** 2 + (y - 8) ** 2 < 60:
                    c = 0.85 + 0.15 * hash_noise(x, y, gen.seed + seed_offset + 1)
                    s.set_at((x, y), (int(br * c), int(bg * c), int(bb * c), 255))
        # Horns
        for i in range(4):
            s.set_at((18, 3 - i), (min(br + 40, 255), min(bg + 40, 255), min(bb + 20, 255), 255))
            s.set_at((30, 3 - i), (min(br + 40, 255), min(bg + 40, 255), min(bb + 20, 255), 255))
        # Eyes
        pygame.draw.circle(s, (er, eg, eb, 255), (20, 8), 2)
        pygame.draw.circle(s, (er, eg, eb, 255), (28, 8), 2)
        # Snout / nostrils
        s.set_at((23, 12), (max(br - 40, 0), max(bg - 40, 0), max(bb - 20, 0), 255))
        s.set_at((25, 12), (max(br - 40, 0), max(bg - 40, 0), max(bb - 20, 0), 255))
        # Wings
        for y in range(10, 28):
            for x in range(0, 9):
                a = 200 - (8 - x) * 22
                s.set_at((x, y), (wr, wg, wb, max(a, 40)))
            for x in range(39, 48):
                a = 200 - (x - 39) * 22
                s.set_at((x, y), (wr, wg, wb, max(a, 40)))
        # Wing membrane detail
        for i in range(4):
            wy = 12 + i * 4
            for x in range(1, 8):
                s.set_at((x, wy), (wr + 20 if wr < 236 else 255,
                                    wg + 20 if wg < 236 else 255,
                                    wb + 10 if wb < 246 else 255, 120))
            for x in range(40, 47):
                s.set_at((x, wy), (wr + 20 if wr < 236 else 255,
                                    wg + 20 if wg < 236 else 255,
                                    wb + 10 if wb < 246 else 255, 120))
        # Tail
        for i in range(10):
            tx = 24 - i
            ty = 38 + int(3 * math.sin(i * 0.7))
            if 0 <= tx < 48 and 0 <= ty < 48:
                s.set_at((tx, ty), (br, bg, bb, 220))
                if ty + 1 < 48:
                    s.set_at((tx, ty + 1), (br, bg, bb, 180))
        # Belly (lighter stripe)
        for y in range(20, 35):
            for x in range(18, 30):
                dx = (x - 24) / 6.0
                dy = (y - 27) / 7.5
                if dx * dx + dy * dy < 1.0:
                    s.set_at((x, y), (min(br + 50, 255), min(bg + 50, 255),
                                       min(bb + 30, 255), 200))
        # Claws
        for lx in (12, 16, 30, 34):
            for y in range(38, 42):
                if 0 <= lx < 48 and 0 <= y < 48:
                    s.set_at((lx, y), (max(br - 30, 0), max(bg - 30, 0),
                                        max(bb - 20, 0), 255))
        return s
    return gen._get(key, make)


def generate_dragon_red(gen) -> pygame.Surface:
    return _make_dragon(gen, "dragon_red",
                        body_rgb=(200, 50, 30),
                        wing_rgb=(170, 40, 20),
                        eye_rgb=(255, 200, 0),
                        seed_offset=120)


def generate_dragon_green(gen) -> pygame.Surface:
    return _make_dragon(gen, "dragon_green",
                        body_rgb=(40, 160, 50),
                        wing_rgb=(30, 130, 40),
                        eye_rgb=(255, 255, 60),
                        seed_offset=124)


def generate_dragon_black(gen) -> pygame.Surface:
    return _make_dragon(gen, "dragon_black",
                        body_rgb=(35, 35, 45),
                        wing_rgb=(25, 25, 35),
                        eye_rgb=(200, 40, 40),
                        seed_offset=128)


def generate_dragon_white(gen) -> pygame.Surface:
    return _make_dragon(gen, "dragon_white",
                        body_rgb=(220, 220, 240),
                        wing_rgb=(200, 210, 230),
                        eye_rgb=(100, 180, 255),
                        seed_offset=132)


def generate_shadow_dragon(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((48, 48), pygame.SRCALPHA)
        br, bg, bb = 50, 20, 70
        # Shadow body with translucency
        for y in range(10, 40):
            for x in range(8, 40):
                dx = (x - 24) / 16.0
                dy = (y - 25) / 15.0
                if dx * dx + dy * dy < 1.0:
                    c = 0.7 + 0.3 * hash_noise(x, y, gen.seed + 136)
                    a = 200 + int(30 * math.sin(x * 0.3 + y * 0.3))
                    s.set_at((x, y), (int(br * c), int(bg * c),
                                       int(bb * c), min(a, 255)))
        # Head
        for y in range(2, 14):
            for x in range(14, 34):
                if (x - 24) ** 2 + (y - 8) ** 2 < 60:
                    c = 0.8 + 0.2 * hash_noise(x, y, gen.seed + 137)
                    s.set_at((x, y), (int(br * c), int(bg * c),
                                       int(bb * c), 240))
        # Horns (dark purple)
        for i in range(5):
            s.set_at((18, 3 - i), (80, 30, 110, 255))
            s.set_at((30, 3 - i), (80, 30, 110, 255))
        # Glowing purple eyes
        pygame.draw.circle(s, (200, 60, 255, 255), (20, 8), 3)
        pygame.draw.circle(s, (200, 60, 255, 255), (28, 8), 3)
        # Shadow wings (wide, translucent)
        for y in range(8, 30):
            for x in range(0, 9):
                a = 150 - (8 - x) * 16
                s.set_at((x, y), (40, 15, 60, max(a, 30)))
            for x in range(39, 48):
                a = 150 - (x - 39) * 16
                s.set_at((x, y), (40, 15, 60, max(a, 30)))
        # Purple aura around body
        for y in range(6, 44):
            for x in range(5, 43):
                dx = (x - 24) / 19.0
                dy = (y - 25) / 19.0
                d2 = dx * dx + dy * dy
                if 0.7 < d2 < 1.0:
                    a = int(60 * (1.0 - (d2 - 0.7) / 0.3))
                    a += int(20 * math.sin(x * 0.5 + y * 0.5))
                    cur = s.get_at((x, y))
                    if cur[3] == 0:
                        s.set_at((x, y), (120, 40, 180, max(min(a, 100), 10)))
        # Tail with shadow wisps
        for i in range(12):
            tx = 24 - i
            ty = 38 + int(3 * math.sin(i * 0.6))
            if 0 <= tx < 48 and 0 <= ty < 48:
                s.set_at((tx, ty), (br, bg, bb, 200))
                if ty + 1 < 48:
                    s.set_at((tx, ty + 1), (br, bg, bb, 140))
        return s
    return gen._get("shadow_dragon", make)
