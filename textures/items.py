"""Item texture generation — all inventory items."""
import random
import math
import pygame
from core.utils import hash_noise


# ==================================================================
# ORIGINAL ITEM ICONS (16×16)
# ==================================================================
def generate_item_wood(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(4, 12):
            for x in range(3, 13):
                s.set_at((x, y), (140, 90, 40, 255))
            s.set_at((3, y), (110, 70, 30, 255))
            s.set_at((12, y), (160, 110, 50, 255))
        return s
    return gen._get("item_wood", make)


def generate_item_stone(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(16):
            for x in range(16):
                if (x - 8) ** 2 + (y - 8) ** 2 < 36:
                    c = 120 + int(30 * hash_noise(x, y, gen.seed + 8))
                    s.set_at((x, y), (c, c, c, 255))
        return s
    return gen._get("item_stone", make)


def generate_item_stick(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for i in range(12):
            s.set_at((3 + i, 12 - i), (140, 100, 50, 255))
            s.set_at((4 + i, 12 - i), (160, 120, 60, 255))
        return s
    return gen._get("item_stick", make)


def generate_item_berry(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(16):
            for x in range(16):
                if (x - 8) ** 2 + (y - 9) ** 2 < 30:
                    r = 180 + int(40 * hash_noise(x, y, gen.seed + 10))
                    s.set_at((x, y), (min(255, r), 30, 50, 255))
        s.set_at((8, 3), (60, 130, 40, 255))
        s.set_at((8, 4), (60, 130, 40, 255))
        s.set_at((6, 6), (255, 120, 130, 255))
        return s
    return gen._get("item_berry", make)


def generate_item_axe(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(3, 14):
            s.set_at((7, y), (120, 80, 40, 255))
        for y in range(2, 7):
            for x in range(8, 14):
                if (x - 8) + (y - 2) < 6:
                    s.set_at((x, y), (180, 180, 200, 255))
        return s
    return gen._get("item_axe", make)


def generate_item_hammer(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Handle (brown, vertical center)
        for y in range(7, 15):
            s.set_at((7, y), (120, 80, 40, 255))
            s.set_at((8, y), (100, 65, 30, 255))
        # Head (iron block, horizontal on top)
        for x in range(3, 13):
            for y in range(2, 7):
                s.set_at((x, y), (170, 170, 190, 255))
        # Head highlight (top edge)
        for x in range(3, 13):
            s.set_at((x, 2), (200, 200, 220, 255))
        # Head shadow (bottom edge)
        for x in range(3, 13):
            s.set_at((x, 6), (130, 130, 150, 255))
        # Head side highlights
        for y in range(2, 7):
            s.set_at((3, y), (190, 190, 210, 255))
            s.set_at((12, y), (140, 140, 160, 255))
        return s
    return gen._get("item_hammer", make)


def generate_item_sword(gen) -> pygame.Surface:
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
    return gen._get("item_sword", make)


def generate_item_torch(gen) -> pygame.Surface:
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
    return gen._get("item_torch", make)


def generate_item_campfire(gen) -> pygame.Surface:
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
    return gen._get("item_campfire", make)


def generate_item_pie(gen) -> pygame.Surface:
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
    return gen._get("item_pie", make)


def generate_item_bandage(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(4, 12):
            for x in range(4, 12):
                s.set_at((x, y), (230, 230, 230, 255))
        for i in range(4, 12):
            s.set_at((8, i), (200, 50, 50, 255))
            s.set_at((i, 8), (200, 50, 50, 255))
        return s
    return gen._get("item_bandage", make)


# ==================================================================
# NEW ITEM ICONS (16×16)
# ==================================================================
def generate_item_iron_sword(gen) -> pygame.Surface:
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
    return gen._get("item_iron_sword", make)


def generate_item_spear(gen) -> pygame.Surface:
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
    return gen._get("item_spear", make)


def generate_item_bow(gen) -> pygame.Surface:
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
    return gen._get("item_bow", make)


def generate_item_arrow(gen) -> pygame.Surface:
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
    return gen._get("item_arrow", make)


def generate_item_sling(gen) -> pygame.Surface:
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
    return gen._get("item_sling", make)


def generate_item_rock_ammo(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(16):
            for x in range(16):
                if (x - 8) ** 2 + (y - 8) ** 2 < 20:
                    c = 100 + int(30 * hash_noise(x, y, gen.seed + 40))
                    s.set_at((x, y), (c, c, c + 5, 255))
        return s
    return gen._get("item_rock_ammo", make)


def generate_item_sling_bullet(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(16):
            for x in range(16):
                if (x - 8) ** 2 + (y - 8) ** 2 < 16:
                    c = 140 + int(20 * hash_noise(x, y, gen.seed + 41))
                    s.set_at((x, y), (c, c, c + 10, 255))
        return s
    return gen._get("item_sling_bullet", make)


def generate_item_leather_armor(gen) -> pygame.Surface:
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
    return gen._get("item_leather_armor", make)


def generate_item_wood_shield(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(2, 14):
            for x in range(3, 13):
                dx = (x - 8) / 5.0
                dy = (y - 8) / 6.0
                if dx * dx + dy * dy < 1:
                    c = 130 + int(20 * hash_noise(x, y, gen.seed + 42))
                    s.set_at((x, y), (c, int(c * 0.7), 30, 255))
        # Metal boss
        pygame.draw.circle(s, (180, 180, 200, 255), (8, 8), 2)
        return s
    return gen._get("item_wood_shield", make)


def generate_item_trap(gen) -> pygame.Surface:
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
    return gen._get("item_trap", make)


def generate_item_bed(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        frame = (120, 80, 40, 255)
        red = (180, 35, 35, 255)
        red_dk = (150, 25, 25, 255)
        pillow = (230, 230, 240, 255)
        pillow_dk = (200, 200, 215, 255)
        # Wooden frame border (top-down view)
        for x in range(1, 15):
            s.set_at((x, 2), frame)
            s.set_at((x, 13), frame)
        for y in range(2, 14):
            s.set_at((1, y), frame)
            s.set_at((14, y), frame)
        # Red blanket (lower 2/3)
        for y in range(6, 13):
            for x in range(2, 14):
                c = red if (x + y) % 3 != 0 else red_dk
                s.set_at((x, y), c)
        # Pillow (top portion)
        for y in range(3, 6):
            for x in range(3, 13):
                c = pillow if y < 5 else pillow_dk
                s.set_at((x, y), c)
        # Pillow center crease
        for y in range(3, 6):
            s.set_at((8, y), pillow_dk)
        return s
    return gen._get("item_bed", make)


# ==================================================================
# NEW ITEM ICONS — PHASE 2 (16×16)
# ==================================================================
def generate_item_iron(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Metallic ingot shape
        for y in range(5, 12):
            for x in range(3, 13):
                c = 160 + int(25 * hash_noise(x, y, gen.seed + 61))
                s.set_at((x, y), (c, c, c + 10, 255))
        # Top highlight
        for x in range(4, 12):
            s.set_at((x, 5), (200, 200, 215, 255))
        # Bottom shadow
        for x in range(3, 13):
            s.set_at((x, 11), (120, 120, 130, 255))
        return s
    return gen._get("item_iron", make)


def generate_item_cloth(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Folded fabric shape
        for y in range(4, 13):
            for x in range(3, 13):
                c = 220 + int(15 * hash_noise(x, y, gen.seed + 62))
                s.set_at((x, y), (c, c, min(255, c - 5), 255))
        # Fold lines
        for y in range(5, 12):
            s.set_at((6, y), (190, 190, 185, 255))
            s.set_at((10, y), (190, 190, 185, 255))
        return s
    return gen._get("item_cloth", make)


def generate_item_bone(gen) -> pygame.Surface:
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
    return gen._get("item_bone", make)


def generate_item_leather(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Leather hide shape (irregular)
        for y in range(3, 14):
            for x in range(3, 13):
                dx = (x - 8) / 5.5
                dy = (y - 8.5) / 5.5
                if dx * dx + dy * dy < 0.9 + 0.1 * hash_noise(x, y, gen.seed + 63):
                    c = 140 + int(30 * hash_noise(x, y, gen.seed + 64))
                    s.set_at((x, y), (c, int(c * 0.6), int(c * 0.25), 255))
        return s
    return gen._get("item_leather", make)


def generate_item_health_potion(gen) -> pygame.Surface:
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
    return gen._get("item_health_potion", make)


def generate_item_antidote(gen) -> pygame.Surface:
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
    return gen._get("item_antidote", make)


def generate_item_iron_axe(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Handle
        for y in range(3, 14):
            s.set_at((7, y), (120, 80, 40, 255))
        # Metallic axe head (silver/gray)
        for y in range(2, 7):
            for x in range(8, 14):
                if (x - 8) + (y - 2) < 6:
                    c = 170 + int(20 * hash_noise(x, y, gen.seed + 65))
                    s.set_at((x, y), (c, c, c + 15, 255))
        return s
    return gen._get("item_iron_axe", make)


def generate_item_mace(gen) -> pygame.Surface:
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
    return gen._get("item_mace", make)


def generate_item_bone_club(gen) -> pygame.Surface:
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
    return gen._get("item_bone_club", make)


def generate_item_crossbow(gen) -> pygame.Surface:
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
    return gen._get("item_crossbow", make)


def generate_item_fire_arrow(gen) -> pygame.Surface:
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
    return gen._get("item_fire_arrow", make)


def generate_item_bolt(gen) -> pygame.Surface:
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
    return gen._get("item_bolt", make)


def generate_item_iron_armor(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        metal = (160, 165, 180, 255)
        dark = (120, 125, 140, 255)
        # Body
        for y in range(3, 14):
            for x in range(4, 12):
                c = 155 + int(20 * hash_noise(x, y, gen.seed + 66))
                s.set_at((x, y), (c, c, c + 15, 255))
        # Shoulders
        for x in range(2, 14):
            s.set_at((x, 3), dark)
            s.set_at((x, 4), dark)
        # Centre line
        for y in range(5, 13):
            s.set_at((8, y), dark)
        return s
    return gen._get("item_iron_armor", make)


def generate_item_iron_shield(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(2, 14):
            for x in range(3, 13):
                dx = (x - 8) / 5.0
                dy = (y - 8) / 6.0
                if dx * dx + dy * dy < 1:
                    c = 155 + int(25 * hash_noise(x, y, gen.seed + 67))
                    s.set_at((x, y), (c, c, c + 15, 255))
        # Metal boss
        pygame.draw.circle(s, (200, 205, 220, 255), (8, 8), 2)
        # Rivets
        s.set_at((5, 4), (120, 120, 135, 255))
        s.set_at((11, 4), (120, 120, 135, 255))
        s.set_at((5, 12), (120, 120, 135, 255))
        s.set_at((11, 12), (120, 120, 135, 255))
        return s
    return gen._get("item_iron_shield", make)


def generate_item_spell_fireball(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        # Book cover (red/orange)
        for y in range(3, 17):
            for x in range(3, 17):
                c = 180 + int(30 * hash_noise(x, y, gen.seed + 70))
                s.set_at((x, y), (c, int(c * 0.45), 20, 255))
        # Spine (darker)
        for y in range(3, 17):
            s.set_at((3, y), (120, 40, 15, 255))
            s.set_at((4, y), (140, 50, 20, 255))
        # Pages (visible edge)
        for y in range(5, 15):
            s.set_at((16, y), (240, 235, 220, 255))
        # Fire symbol on cover
        pygame.draw.circle(s, (255, 180, 40, 255), (10, 9), 3)
        pygame.draw.circle(s, (255, 100, 20, 255), (10, 9), 2)
        s.set_at((10, 6), (255, 220, 60, 255))
        return s
    return gen._get("item_spell_fireball", make)


# ==================================================================
# NEW SPELL / ITEM TEXTURES
# ==================================================================
def generate_item_spell_heal(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        for y in range(3, 17):
            for x in range(3, 17):
                c = 60 + int(30 * hash_noise(x, y, gen.seed + 80))
                s.set_at((x, y), (c, 180 + c // 3, c, 255))
        for y in range(3, 17):
            s.set_at((3, y), (30, 100, 30, 255))
            s.set_at((4, y), (40, 120, 40, 255))
        for y in range(5, 15):
            s.set_at((16, y), (240, 235, 220, 255))
        # Cross symbol
        for i in range(-2, 3):
            s.set_at((10 + i, 9), (255, 255, 200, 255))
            s.set_at((10, 9 + i), (255, 255, 200, 255))
        return s
    return gen._get("item_spell_heal", make)


def generate_item_spell_lightning(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        for y in range(3, 17):
            for x in range(3, 17):
                c = 80 + int(30 * hash_noise(x, y, gen.seed + 90))
                s.set_at((x, y), (c, c + 20, 200 + c // 4, 255))
        for y in range(3, 17):
            s.set_at((3, y), (40, 40, 120, 255))
            s.set_at((4, y), (50, 50, 140, 255))
        for y in range(5, 15):
            s.set_at((16, y), (240, 235, 220, 255))
        # Lightning bolt symbol
        pts = [(10, 5), (8, 9), (11, 9), (9, 14)]
        for i in range(len(pts) - 1):
            pygame.draw.line(s, (255, 255, 100, 255), pts[i], pts[i + 1])
        return s
    return gen._get("item_spell_lightning", make)


def generate_item_spell_ice(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        for y in range(3, 17):
            for x in range(3, 17):
                c = 100 + int(30 * hash_noise(x, y, gen.seed + 100))
                s.set_at((x, y), (c, c + 40, 220, 255))
        for y in range(3, 17):
            s.set_at((3, y), (40, 60, 140, 255))
            s.set_at((4, y), (50, 70, 160, 255))
        for y in range(5, 15):
            s.set_at((16, y), (240, 235, 220, 255))
        # Snowflake symbol
        pygame.draw.circle(s, (200, 230, 255, 255), (10, 9), 3)
        s.set_at((10, 5), (200, 230, 255, 255))
        s.set_at((10, 13), (200, 230, 255, 255))
        s.set_at((7, 9), (200, 230, 255, 255))
        s.set_at((13, 9), (200, 230, 255, 255))
        return s
    return gen._get("item_spell_ice", make)


def generate_item_diamond(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pts = [(10, 3), (15, 8), (10, 17), (5, 8)]
        pygame.draw.polygon(s, (140, 220, 255, 255), pts)
        pygame.draw.polygon(s, (100, 180, 240, 255), pts, 1)
        pygame.draw.line(s, (200, 240, 255, 255), (10, 3), (10, 17))
        pygame.draw.line(s, (200, 240, 255, 255), (5, 8), (15, 8))
        return s
    return gen._get("item_diamond", make)


def generate_item_gunpowder(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(s, (60, 60, 60, 255), (10, 12), 6)
        for i in range(8):
            x = 5 + int(10 * hash_noise(i, 0, gen.seed + 200))
            y = 7 + int(10 * hash_noise(0, i, gen.seed + 201))
            s.set_at((x, y), (40, 40, 40, 255))
        pygame.draw.circle(s, (80, 80, 80, 255), (10, 12), 3)
        return s
    return gen._get("item_gunpowder", make)


def generate_item_iron_ore(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        for y in range(5, 17):
            for x in range(4, 16):
                if ((x - 10) ** 2 + (y - 11) ** 2) < 40:
                    c = 100 + int(40 * hash_noise(x, y, gen.seed + 210))
                    s.set_at((x, y), (c, c - 10, c - 20, 255))
        # Orange-brown iron flecks
        for i in range(4):
            fx = 7 + int(6 * hash_noise(i, 1, gen.seed + 211))
            fy = 8 + int(6 * hash_noise(1, i, gen.seed + 212))
            s.set_at((fx, fy), (180, 120, 60, 255))
        return s
    return gen._get("item_iron_ore", make)


def generate_item_bomb(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(s, (50, 50, 50, 255), (10, 12), 6)
        pygame.draw.circle(s, (80, 80, 80, 255), (10, 12), 4)
        # Fuse
        pygame.draw.line(s, (140, 100, 50, 255), (10, 6), (13, 3), 1)
        s.set_at((14, 2), (255, 200, 50, 255))
        s.set_at((13, 2), (255, 150, 30, 255))
        return s
    return gen._get("item_bomb", make)


def generate_item_brilliant_diamond(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        pts = [(10, 2), (16, 8), (10, 18), (4, 8)]
        pygame.draw.polygon(s, (200, 240, 255, 255), pts)
        pygame.draw.polygon(s, (160, 210, 255, 255), pts, 1)
        pygame.draw.line(s, (255, 255, 255, 255), (10, 2), (10, 18))
        pygame.draw.line(s, (255, 255, 255, 255), (4, 8), (16, 8))
        # Sparkle dots
        s.set_at((7, 5), (255, 255, 200, 255))
        s.set_at((13, 5), (255, 255, 200, 255))
        s.set_at((7, 13), (255, 255, 200, 255))
        s.set_at((13, 13), (255, 255, 200, 255))
        return s
    return gen._get("item_brilliant_diamond", make)


def generate_item_titanium_ore(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        for y in range(5, 17):
            for x in range(4, 16):
                if ((x - 10) ** 2 + (y - 11) ** 2) < 40:
                    c = 140 + int(30 * hash_noise(x, y, gen.seed + 220))
                    s.set_at((x, y), (c, c + 10, c + 20, 255))
        # Bluish titanium flecks
        for i in range(5):
            fx = 6 + int(7 * hash_noise(i, 2, gen.seed + 221))
            fy = 7 + int(7 * hash_noise(2, i, gen.seed + 222))
            s.set_at((fx, fy), (100, 160, 220, 255))
        return s
    return gen._get("item_titanium_ore", make)


def generate_item_titanium_ingot(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y in range(5, 12):
            for x in range(3, 13):
                c = 160 + int(20 * hash_noise(x, y, gen.seed + 230))
                s.set_at((x, y), (c, c + 10, c + 25, 255))
            s.set_at((3, y), (130, 140, 160, 255))
            s.set_at((12, y), (180, 190, 210, 255))
        return s
    return gen._get("item_titanium_ingot", make)


def generate_item_titanium_axe(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Handle
        for y in range(3, 14):
            s.set_at((7, y), (120, 80, 40, 255))
        # Titanium axe head (blue-silver)
        for y in range(2, 7):
            for x in range(8, 14):
                if (x - 8) + (y - 2) < 6:
                    c = 160 + int(20 * hash_noise(x, y, gen.seed + 240))
                    s.set_at((x, y), (c, c + 10, c + 30, 255))
        return s
    return gen._get("item_titanium_axe", make)


def generate_item_diamond_axe(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        # Handle
        for y in range(3, 14):
            s.set_at((7, y), (120, 80, 40, 255))
        # Diamond axe head (light blue / brilliant)
        for y in range(2, 7):
            for x in range(8, 14):
                if (x - 8) + (y - 2) < 6:
                    c = 180 + int(20 * hash_noise(x, y, gen.seed + 250))
                    s.set_at((x, y), (c - 40, c, min(255, c + 30), 255))
        # Sparkle
        s.set_at((11, 3), (255, 255, 230, 255))
        return s
    return gen._get("item_diamond_axe", make)


def generate_item_greater_enchantment_table(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        # Table body (dark purple)
        for y in range(8, 18):
            for x in range(3, 17):
                s.set_at((x, y), (60, 30, 80, 255))
        # Top surface (lighter)
        for x in range(3, 17):
            s.set_at((x, 8), (100, 50, 130, 255))
            s.set_at((x, 9), (90, 40, 120, 255))
        # Diamond glow center
        pygame.draw.circle(s, (200, 240, 255, 200), (10, 5), 3)
        pygame.draw.circle(s, (255, 255, 255, 180), (10, 5), 1)
        return s
    return gen._get("item_greater_enchantment_table", make)


def _generate_buff_spell_book(gen, name: str,
                               color: tuple) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((20, 20), pygame.SRCALPHA)
        r, g, b = color
        for y in range(3, 17):
            for x in range(3, 17):
                n = int(20 * hash_noise(x, y, gen.seed + 300))
                s.set_at((x, y), (max(0, min(255, r + n)),
                                   max(0, min(255, g + n)),
                                   max(0, min(255, b + n)), 255))
        for y in range(3, 17):
            s.set_at((3, y), (r // 2, g // 2, b // 2, 255))
            s.set_at((4, y), (r * 2 // 3, g * 2 // 3, b * 2 // 3, 255))
        for y in range(5, 15):
            s.set_at((16, y), (240, 235, 220, 255))
        # Glow dot
        pygame.draw.circle(s, (255, 255, 220, 200), (10, 9), 2)
        return s
    return gen._get(f"item_{name}", make)


def generate_buff_spell_books(gen) -> None:
    colors = {
        'spell_regen_1': (60, 180, 60), 'spell_regen_2': (40, 200, 40),
        'spell_regen_3': (20, 220, 20), 'spell_regen_4': (10, 235, 10),
        'spell_regen_5': (0, 250, 0),
        'spell_protection_1': (60, 60, 180), 'spell_protection_2': (40, 40, 200),
        'spell_protection_3': (20, 20, 220), 'spell_protection_4': (10, 10, 235),
        'spell_protection_5': (0, 0, 250),
        'spell_strength_1': (180, 60, 60), 'spell_strength_2': (200, 40, 40),
        'spell_strength_3': (220, 20, 20), 'spell_strength_4': (235, 10, 10),
        'spell_strength_5': (250, 0, 0),
    }
    for name, color in colors.items():
        _generate_buff_spell_book(gen, name, color)


def generate_tiered_spell_books(gen) -> None:
    """Generate tier 2-5 versions of elemental spell books (plain copy — no border glow)."""
    bases = {
        'spell_fireball': (255, 120, 30),
        'spell_heal': (80, 255, 80),
        'spell_lightning': (180, 200, 255),
        'spell_ice': (100, 200, 255),
    }
    for base_key, glow_color in bases.items():
        for tier in range(2, 6):
            item_key = f"item_{base_key}_{tier}"
            def make(bk=base_key, t=tier) -> pygame.Surface:
                base = gen.cache.get(f"item_{bk}")
                if base is None:
                    base = pygame.Surface((20, 20), pygame.SRCALPHA)
                s = base.copy()
                # Tier dots at bottom (no border glow)
                dot_y = 17
                start_x = 10 - t
                for d in range(t):
                    s.set_at((start_x + d * 2, dot_y), (255, 255, 200, 255))
                return s
            gen._get(item_key, make)


def _generate_stat_weapon(gen, base_key: str, tier: int,
                          base_color: tuple) -> pygame.Surface:
    """Generate a stat weapon icon (plain copy of base — no border glow)."""
    item_key = f"item_{base_key}_{tier}"
    def make() -> pygame.Surface:
        # Start from the base weapon texture
        base = gen.cache.get(f"item_{base_key}")
        if base is None:
            base = pygame.Surface((20, 20), pygame.SRCALPHA)
        return base.copy()
    return gen._get(item_key, make)


def generate_stat_weapons(gen) -> None:
    # Rare color: blue; Epic color: purple
    for tier in range(1, 6):
        color = (80, 140, 255) if tier <= 2 else (180, 60, 255)
        _generate_stat_weapon(gen, 'iron_sword', tier, color)
        _generate_stat_weapon(gen, 'iron_axe', tier, color)
        _generate_stat_weapon(gen, 'mace', tier, color)
        _generate_stat_weapon(gen, 'titanium_axe', tier, color)
        _generate_stat_weapon(gen, 'diamond_axe', tier, color)
        _generate_stat_weapon(gen, 'iron_pickaxe', tier, color)
        _generate_stat_weapon(gen, 'titanium_pickaxe', tier, color)
        _generate_stat_weapon(gen, 'diamond_pickaxe', tier, color)


def generate_stat_ranged(gen) -> None:
    for tier in range(1, 6):
        color = (80, 140, 255) if tier <= 2 else (180, 60, 255)
        _generate_stat_weapon(gen, 'bow', tier, color)
        _generate_stat_weapon(gen, 'crossbow', tier, color)
        _generate_stat_weapon(gen, 'sling', tier, color)


def generate_stat_armors(gen) -> None:
    for tier in range(1, 6):
        color = (80, 140, 255) if tier <= 2 else (180, 60, 255)
        _generate_stat_weapon(gen, 'iron_armor', tier, color)
        _generate_stat_weapon(gen, 'iron_shield', tier, color)


def generate_stat_turrets(gen) -> None:
    for tier in range(1, 6):
        color = (80, 140, 255) if tier <= 2 else (180, 60, 255)
        _generate_stat_weapon(gen, 'turret', tier, color)


# ==================================================================
# PICKAXE ICONS (16×16)
# ==================================================================
def _draw_pickaxe_handle(s: pygame.Surface) -> None:
    """Draw the shared diagonal pickaxe handle onto a 16×16 surface."""
    for i in range(10):
        s.set_at((3 + i, 13 - i), (120, 80, 40, 255))
        s.set_at((4 + i, 13 - i), (100, 65, 30, 255))


def generate_item_pickaxe(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        _draw_pickaxe_handle(s)
        for dx in range(6):
            s.set_at((8 + dx, 4 - min(dx, 3)), (160, 160, 170, 255))
            s.set_at((8 + dx, 5 - min(dx, 3)), (140, 140, 150, 255))
        return s
    return gen._get("item_pickaxe", make)


def generate_item_iron_pickaxe(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        _draw_pickaxe_handle(s)
        for dx in range(6):
            c = 170 + int(20 * hash_noise(8 + dx, 4, gen.seed + 300))
            s.set_at((8 + dx, 4 - min(dx, 3)), (c, c, c + 15, 255))
            s.set_at((8 + dx, 5 - min(dx, 3)), (c - 20, c - 20, c - 5, 255))
        return s
    return gen._get("item_iron_pickaxe", make)


def generate_item_titanium_pickaxe(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        _draw_pickaxe_handle(s)
        for dx in range(6):
            c = 160 + int(20 * hash_noise(8 + dx, 4, gen.seed + 310))
            s.set_at((8 + dx, 4 - min(dx, 3)), (c, c + 10, c + 30, 255))
            s.set_at((8 + dx, 5 - min(dx, 3)), (c - 20, c - 10, c + 10, 255))
        return s
    return gen._get("item_titanium_pickaxe", make)


def generate_item_diamond_pickaxe(gen) -> pygame.Surface:
    def make() -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        _draw_pickaxe_handle(s)
        for dx in range(6):
            c = 180 + int(20 * hash_noise(8 + dx, 4, gen.seed + 320))
            s.set_at((8 + dx, 4 - min(dx, 3)), (c - 40, c, min(255, c + 30), 255))
            s.set_at((8 + dx, 5 - min(dx, 3)), (c - 60, c - 20, c + 10, 255))
        s.set_at((12, 2), (255, 255, 230, 255))
        return s
    return gen._get("item_diamond_pickaxe", make)
