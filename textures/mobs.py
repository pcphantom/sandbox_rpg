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
