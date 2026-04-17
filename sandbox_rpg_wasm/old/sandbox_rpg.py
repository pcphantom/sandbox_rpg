# sandbox_rpg.py — Sandbox Survival RPG (Complete Edition)
# Python 3.10+ | pygame 2.5+
import pygame
import random
import math
import sys
import json
import os
from typing import List, Tuple, Dict, Optional, Any, Callable, Set, Type

pygame.init()
pygame.font.init()

# =============================================================================
# CONSTANTS
# =============================================================================
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
TILE_SIZE: int = 32
WORLD_WIDTH: int = 200
WORLD_HEIGHT: int = 150
FPS: int = 60
SAVE_FILE: str = "savegame.json"
SAVE_SLOTS: List[str] = ["saveslot_1.json", "saveslot_2.json", "saveslot_3.json"]

BLACK:  Tuple[int, int, int] = (0, 0, 0)
WHITE:  Tuple[int, int, int] = (255, 255, 255)
YELLOW: Tuple[int, int, int] = (255, 255, 80)
RED:    Tuple[int, int, int] = (255, 60, 60)
GREEN:  Tuple[int, int, int] = (60, 220, 80)
CYAN:   Tuple[int, int, int] = (80, 200, 255)
GRAY:   Tuple[int, int, int] = (160, 160, 170)

# Item data: id -> {name, desc, damage, harvest, heal, placeable, category, defense, ammo_type}
ITEM_DATA: Dict[str, Dict[str, Any]] = {
    'wood':     {'name': 'Wood',         'desc': 'Basic building material.',           'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'material', 'defense': 0, 'ammo_type': ''},
    'stone':    {'name': 'Stone',        'desc': 'Hard and durable.',                  'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'material', 'defense': 0, 'ammo_type': ''},
    'stick':    {'name': 'Stick',        'desc': 'A thin branch. Weak weapon.',        'damage': 3, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'weapon',   'defense': 0, 'ammo_type': ''},
    'berry':    {'name': 'Berry',        'desc': 'Restores 15 HP. [F] to eat.',       'damage': 0, 'harvest': 0, 'heal': 15, 'placeable': False, 'category': 'consumable','defense': 0, 'ammo_type': ''},
    'axe':      {'name': 'Stone Axe',    'desc': '+2 harvest yield. Decent weapon.',   'damage': 12,'harvest': 2, 'heal': 0,  'placeable': False, 'category': 'tool',     'defense': 0, 'ammo_type': ''},
    'sword':    {'name': 'Wood Sword',   'desc': 'Best melee damage.',                 'damage': 20,'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'weapon',   'defense': 0, 'ammo_type': ''},
    'torch':    {'name': 'Torch',        'desc': 'Hold for light. [F] to place.',     'damage': 5, 'harvest': 0, 'heal': 0,  'placeable': True,  'category': 'placeable','defense': 0, 'ammo_type': ''},
    'campfire': {'name': 'Campfire Kit', 'desc': 'Heals nearby. [F] to place.',       'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': True,  'category': 'placeable','defense': 0, 'ammo_type': ''},
    'pie':      {'name': 'Berry Pie',    'desc': 'Restores 40 HP. [F] to eat.',       'damage': 0, 'harvest': 0, 'heal': 40, 'placeable': False, 'category': 'consumable','defense': 0, 'ammo_type': ''},
    'bandage':  {'name': 'Bandage',      'desc': 'Restores 25 HP. [F] to use.',       'damage': 0, 'harvest': 0, 'heal': 25, 'placeable': False, 'category': 'consumable','defense': 0, 'ammo_type': ''},
    'fiber':    {'name': 'Fiber',        'desc': 'Plant fibers for crafting.',         'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'material', 'defense': 0, 'ammo_type': ''},
    'feather':  {'name': 'Feather',      'desc': 'Light plume from a bird.',           'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'material', 'defense': 0, 'ammo_type': ''},
    'leather':  {'name': 'Leather',      'desc': 'Tough animal hide.',                 'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'material', 'defense': 0, 'ammo_type': ''},
    'spear':    {'name': 'Spear',        'desc': 'Long reach. Decent damage.',         'damage': 16,'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'weapon',   'defense': 0, 'ammo_type': ''},
    'bow':      {'name': 'Bow',          'desc': 'Ranged weapon. Uses arrows.',        'damage': 14,'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'ranged',   'defense': 0, 'ammo_type': 'arrow'},
    'arrow':    {'name': 'Arrow',        'desc': 'Ammo for the bow.',                  'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'ammo',     'defense': 0, 'ammo_type': ''},
    'sling':    {'name': 'Sling',        'desc': 'Ranged weapon. Uses sling bullets.', 'damage': 10,'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'ranged',   'defense': 0, 'ammo_type': 'sling_bullet'},
    'sling_bullet': {'name': 'Sling Bullet', 'desc': 'Ammo for the sling.',            'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'ammo',     'defense': 0, 'ammo_type': ''},
    'leather_armor': {'name': 'Leather Armor', 'desc': '+10 Defense. Equip from [P].',  'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'armor',    'defense': 10,'ammo_type': ''},
    'wood_shield':   {'name': 'Wood Shield',   'desc': '+5 Defense. Equip from [P].',   'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': False, 'category': 'shield',   'defense': 5, 'ammo_type': ''},
    'bed_kit':  {'name': 'Bed Kit',      'desc': 'Place to sleep through night. [F]',  'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': True,  'category': 'placeable','defense': 0, 'ammo_type': ''},
    'spike_trap': {'name': 'Spike Trap', 'desc': 'Damages enemies who walk over. [F]', 'damage': 0, 'harvest': 0, 'heal': 0,  'placeable': True,  'category': 'placeable','defense': 0, 'ammo_type': ''},
}

RECIPES: List[Dict[str, Any]] = [
    {'name': 'Stone Axe',  'cost': {'wood': 3, 'stone': 2},             'gives': 'axe'},
    {'name': 'Wood Sword', 'cost': {'wood': 5, 'stick': 2, 'stone': 1}, 'gives': 'sword'},
    {'name': 'Campfire',   'cost': {'wood': 5, 'stone': 3},             'gives': 'campfire'},
    {'name': 'Torch',      'cost': {'wood': 2, 'stick': 1},             'gives': 'torch'},
    {'name': 'Berry Pie',  'cost': {'berry': 5, 'wood': 1},             'gives': 'pie'},
    {'name': 'Bandage',    'cost': {'stick': 3, 'berry': 2},            'gives': 'bandage'},
    {'name': 'Fiber',      'cost': {'stick': 3},                         'gives': 'fiber', 'qty': 5},
    {'name': 'Spear',      'cost': {'stick': 3, 'stone': 2},             'gives': 'spear'},
    {'name': 'Bow',        'cost': {'wood': 3, 'fiber': 3},              'gives': 'bow'},
    {'name': 'Arrow x5',   'cost': {'stick': 2, 'stone': 1},             'gives': 'arrow', 'qty': 5},
    {'name': 'Sling',      'cost': {'fiber': 3, 'stone': 1},             'gives': 'sling'},
    {'name': 'Bullets x5', 'cost': {'stone': 3},                         'gives': 'sling_bullet', 'qty': 5},
    {'name': 'Leather Armor', 'cost': {'leather': 5, 'fiber': 3},        'gives': 'leather_armor'},
    {'name': 'Wood Shield','cost': {'wood': 4, 'stone': 2},              'gives': 'wood_shield'},
    {'name': 'Bed Kit',    'cost': {'wood': 5, 'fiber': 4},              'gives': 'bed_kit'},
    {'name': 'Spike Trap', 'cost': {'stone': 3, 'stick': 2, 'wood': 1},  'gives': 'spike_trap'},
]

TILE_WATER: int = 0
TILE_SAND: int = 1
TILE_GRASS: int = 2
TILE_DIRT: int = 3
TILE_STONE_FLOOR: int = 4
TILE_STONE_WALL: int = 5

# =============================================================================
# UTILITY
# =============================================================================
def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def clamp(v: float, mn: float, mx: float) -> float:
    return max(mn, min(mx, v))

def hash_noise(x: int, y: int, seed: int) -> float:
    n = (x * 374761393 + y * 668265263 + seed * 374761393) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    return (n & 0x7FFFFFFF) / 0x7FFFFFFF

def value_noise_2d(x: float, y: float, seed: int) -> float:
    ix, iy = int(math.floor(x)), int(math.floor(y))
    fx, fy = x - ix, y - iy
    v00 = hash_noise(ix, iy, seed)
    v10 = hash_noise(ix + 1, iy, seed)
    v01 = hash_noise(ix, iy + 1, seed)
    v11 = hash_noise(ix + 1, iy + 1, seed)
    sx = fx * fx * (3 - 2 * fx)
    sy = fy * fy * (3 - 2 * fy)
    return lerp(lerp(v00, v10, sx), lerp(v01, v11, sx), sy)

def fbm_noise(x: float, y: float, seed: int, octaves: int = 4) -> float:
    total, amp, freq, mx = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        total += value_noise_2d(x * freq, y * freq, seed) * amp
        mx += amp
        amp *= 0.5
        freq *= 2.0
    return total / mx

# =============================================================================
# ECS CORE
# =============================================================================
class Component:
    pass

class EntityManager:
    def __init__(self) -> None:
        self._next_id: int = 1
        self._components: Dict[Type, Dict[int, Any]] = {}
        self._entities: Set[int] = set()

    def create_entity(self) -> int:
        eid = self._next_id
        self._next_id += 1
        self._entities.add(eid)
        return eid

    def destroy_entity(self, entity: int) -> None:
        self._entities.discard(entity)
        for cd in self._components.values():
            cd.pop(entity, None)

    def add_component(self, entity: int, comp: Any) -> None:
        ct = type(comp)
        if ct not in self._components:
            self._components[ct] = {}
        self._components[ct][entity] = comp

    def get_component(self, entity: int, ct: Type) -> Any:
        return self._components.get(ct, {}).get(entity)

    def has_component(self, entity: int, ct: Type) -> bool:
        return entity in self._components.get(ct, {})

    def remove_component(self, entity: int, ct: Type) -> None:
        if ct in self._components:
            self._components[ct].pop(entity, None)

    def get_entities_with(self, *cts: Type) -> List[int]:
        if not cts:
            return list(self._entities)
        sets = [set(self._components.get(c, {}).keys()) for c in cts]
        if not sets:
            return []
        r = sets[0]
        for s in sets[1:]:
            r = r.intersection(s)
        return list(r)

# =============================================================================
# COMPONENTS
# =============================================================================
class Transform(Component):
    def __init__(self, x: float, y: float, z: int = 0) -> None:
        self.x = x; self.y = y; self.z = z
        self.prev_x = x; self.prev_y = y

class Velocity(Component):
    def __init__(self, vx: float = 0.0, vy: float = 0.0, friction: float = 0.85) -> None:
        self.vx = vx; self.vy = vy; self.friction = friction

class Renderable(Component):
    def __init__(self, surface: pygame.Surface, layer: int = 0) -> None:
        self.surface = surface; self.layer = layer
        self.visible = True; self.flip_x = False
        self.offset_x = 0; self.offset_y = 0

class Collider(Component):
    def __init__(self, width: int, height: int, solid: bool = True) -> None:
        self.width = width; self.height = height; self.solid = solid

class Health(Component):
    def __init__(self, maximum: int) -> None:
        self.maximum = maximum; self.current = maximum

    def damage(self, amt: int) -> None:
        self.current = max(0, self.current - amt)

    def heal(self, amt: int) -> None:
        self.current = min(self.maximum, self.current + amt)

    def is_alive(self) -> bool:
        return self.current > 0

class Inventory(Component):
    def __init__(self, capacity: int = 24) -> None:
        self.capacity = capacity
        self.slots: Dict[int, Tuple[str, int]] = {}
        self.equipped_slot: int = 0

    def add_item(self, item_id: str, count: int = 1) -> int:
        for slot, (iid, c) in self.slots.items():
            if iid == item_id:
                self.slots[slot] = (iid, c + count)
                return 0
        for i in range(self.capacity):
            if i not in self.slots:
                self.slots[i] = (item_id, count)
                return 0
        return count

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        for slot, (iid, c) in list(self.slots.items()):
            if iid == item_id:
                if c > count:
                    self.slots[slot] = (iid, c - count)
                    return True
                elif c == count:
                    del self.slots[slot]
                    return True
        return False

    def count(self, item_id: str) -> int:
        return sum(c for iid, c in self.slots.values() if iid == item_id)

    def has(self, item_id: str, count: int = 1) -> bool:
        return self.count(item_id) >= count

    def get_equipped(self) -> Optional[str]:
        if self.equipped_slot in self.slots:
            return self.slots[self.equipped_slot][0]
        return None

class LightSource(Component):
    def __init__(self, radius: int, color: Tuple[int, int, int] = (255, 200, 120),
                 intensity: float = 1.0) -> None:
        self.radius = radius; self.color = color; self.intensity = intensity

class AI(Component):
    def __init__(self, behavior: str = "wander", mob_type: str = "slime") -> None:
        self.behavior = behavior; self.mob_type = mob_type
        self.state = "idle"; self.timer = 0.0
        self.target_id: Optional[int] = None
        self.speed = 40.0; self.detection_range = 150.0
        self.contact_damage = 5; self.xp_value = 15

class PlayerStats(Component):
    def __init__(self) -> None:
        self.level = 1; self.xp = 0; self.kills = 0
        self.xp_to_next = 50
        self.stat_points = 0
        self.str_bonus = 0; self.def_bonus = 0; self.agi_bonus = 0

    def add_xp(self, amount: int) -> bool:
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next = self.level * 50
            self.stat_points += 2
            return True
        return False

class Equipment(Component):
    SLOTS: Tuple[str, ...] = ('weapon', 'ranged', 'ammo', 'armor', 'shield')
    SLOT_CATEGORIES: Dict[str, List[str]] = {
        'weapon': ['weapon', 'tool'],
        'ranged': ['ranged'],
        'ammo': ['ammo'],
        'armor': ['armor'],
        'shield': ['shield'],
    }

    def __init__(self) -> None:
        self.slots: Dict[str, str] = {s: '' for s in self.SLOTS}

    def equip(self, slot: str, item_id: str) -> str:
        old = self.slots.get(slot, '')
        self.slots[slot] = item_id
        return old

    def unequip(self, slot: str) -> str:
        old = self.slots.get(slot, '')
        self.slots[slot] = ''
        return old

    def get(self, slot: str) -> str:
        return self.slots.get(slot, '')

    def get_total_defense(self) -> int:
        total = 0
        for slot in ('armor', 'shield'):
            item = self.slots.get(slot, '')
            if item and item in ITEM_DATA:
                total += ITEM_DATA[item]['defense']
        return total

class Projectile(Component):
    def __init__(self, vx: float, vy: float, damage: int, owner: int, lifetime: float = 3.0) -> None:
        self.vx = vx; self.vy = vy; self.damage = damage
        self.owner = owner; self.lifetime = lifetime

class Placeable(Component):
    def __init__(self, item_type: str) -> None:
        self.item_type = item_type

# =============================================================================
# SYSTEMS
# =============================================================================
class MovementSystem:
    def update(self, dt: float, em: EntityManager) -> None:
        for eid in em.get_entities_with(Transform, Velocity):
            t = em.get_component(eid, Transform)
            v = em.get_component(eid, Velocity)
            t.prev_x, t.prev_y = t.x, t.y
            t.x += v.vx * dt
            t.y += v.vy * dt
            v.vx *= v.friction
            v.vy *= v.friction
            if abs(v.vx) < 0.5:
                v.vx = 0
            if abs(v.vy) < 0.5:
                v.vy = 0

class PhysicsSystem:
    def __init__(self, ww: int, wh: int) -> None:
        self.ww = ww; self.wh = wh

    def _tile_solid(self, x: float, y: float, w: int, h: int, world: Any) -> bool:
        l = int(x // TILE_SIZE)
        r = int((x + w - 1) // TILE_SIZE)
        top = int(y // TILE_SIZE)
        bot = int((y + h - 1) // TILE_SIZE)
        for tx in range(l, r + 1):
            for ty in range(top, bot + 1):
                if world.is_solid(tx, ty):
                    return True
        return False

    def update(self, dt: float, em: EntityManager, world: Any) -> None:
        for eid in em.get_entities_with(Transform, Collider, Velocity):
            t = em.get_component(eid, Transform)
            c = em.get_component(eid, Collider)
            v = em.get_component(eid, Velocity)
            nx = t.x + v.vx * dt
            if not self._tile_solid(nx, t.y, c.width, c.height, world):
                t.x = nx
            else:
                v.vx = 0
            ny = t.y + v.vy * dt
            if not self._tile_solid(t.x, ny, c.width, c.height, world):
                t.y = ny
            else:
                v.vy = 0
            t.x = clamp(t.x, 0, self.ww * TILE_SIZE - c.width)
            t.y = clamp(t.y, 0, self.wh * TILE_SIZE - c.height)

class RenderSystem:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def update(self, em: EntityManager, camera: Any) -> None:
        ents = em.get_entities_with(Transform, Renderable)
        ents.sort(key=lambda e: (em.get_component(e, Renderable).layer,
                                 em.get_component(e, Transform).y))
        for eid in ents:
            t = em.get_component(eid, Transform)
            r = em.get_component(eid, Renderable)
            if not r.visible:
                continue
            sx = int(t.x - camera.x + r.offset_x)
            sy = int(t.y - camera.y + r.offset_y)
            if sx < -64 or sx > SCREEN_WIDTH + 64 or sy < -64 or sy > SCREEN_HEIGHT + 64:
                continue
            surf = pygame.transform.flip(r.surface, r.flip_x, False) if r.flip_x else r.surface
            self.screen.blit(surf, (sx, sy))

class DayNightCycle:
    def __init__(self, day_length: float = 300.0) -> None:
        self.time = 0.30; self.day_length = day_length

    def update(self, dt: float) -> None:
        self.time = (self.time + dt / self.day_length) % 1.0

    def get_darkness(self) -> float:
        t = self.time
        if 0.30 < t < 0.70:
            return 0.0
        if t <= 0.30:
            return 1.0 - t / 0.30
        return (t - 0.70) / 0.30

    def get_period_name(self) -> str:
        t = self.time
        if t < 0.22:
            return "Night"
        if t < 0.30:
            return "Dawn"
        if t < 0.70:
            return "Day"
        if t < 0.78:
            return "Dusk"
        return "Night"

    def is_night(self) -> bool:
        return self.time < 0.22 or self.time >= 0.78

class AISystem:
    def update(self, dt: float, em: EntityManager, player_id: int) -> None:
        pt = em.get_component(player_id, Transform)
        if not pt:
            return
        for eid in em.get_entities_with(Transform, Velocity, AI):
            if eid == player_id:
                continue
            t = em.get_component(eid, Transform)
            v = em.get_component(eid, Velocity)
            mob_ai = em.get_component(eid, AI)
            mob_ai.timer -= dt
            dx = pt.x - t.x
            dy = pt.y - t.y
            dist = math.hypot(dx, dy)
            if mob_ai.behavior == "wander":
                if dist < mob_ai.detection_range:
                    mob_ai.state = "chase"
                elif mob_ai.timer <= 0:
                    angle = random.uniform(0, math.tau)
                    v.vx = math.cos(angle) * mob_ai.speed
                    v.vy = math.sin(angle) * mob_ai.speed
                    mob_ai.timer = random.uniform(1.5, 3.5)
            if mob_ai.state == "chase":
                if dist > mob_ai.detection_range * 2.0:
                    mob_ai.state = "idle"
                elif dist > 5:
                    v.vx = (dx / dist) * mob_ai.speed * 1.3
                    v.vy = (dy / dist) * mob_ai.speed * 1.3

class ProjectileSystem:
    def update(self, dt: float, em: EntityManager, particles: Any) -> List[Tuple[int, int, int]]:
        """Returns list of (target_eid, damage, projectile_owner) for hits."""
        hits: List[Tuple[int, int, int]] = []
        for eid in list(em.get_entities_with(Transform, Projectile)):
            t = em.get_component(eid, Transform)
            proj = em.get_component(eid, Projectile)
            t.x += proj.vx * dt
            t.y += proj.vy * dt
            proj.lifetime -= dt
            if proj.lifetime <= 0:
                em.destroy_entity(eid)
                continue
            # Check collision with mobs
            for mid in em.get_entities_with(Transform, Health, AI):
                mt = em.get_component(mid, Transform)
                if math.hypot(mt.x - t.x, mt.y - t.y) < 20:
                    hits.append((mid, proj.damage, proj.owner))
                    particles.emit(t.x, t.y, 6, (255, 200, 100), 40, 0.3)
                    em.destroy_entity(eid)
                    break
        return hits

# =============================================================================
# PARTICLE SYSTEM
# =============================================================================
class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'color', 'life', 'max_life', 'size')
    def __init__(self, x: float, y: float, vx: float, vy: float,
                 color: Tuple[int, int, int], life: float, size: int = 2) -> None:
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.color = color; self.life = life; self.max_life = life; self.size = size

class ParticleSystem:
    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def emit(self, x: float, y: float, count: int, color: Tuple[int, int, int],
             speed: float = 80.0, life: float = 0.5) -> None:
        for _ in range(count):
            a = random.uniform(0, math.tau)
            s = random.uniform(speed * 0.3, speed)
            self.particles.append(Particle(x, y, math.cos(a) * s, math.sin(a) * s,
                                           color, random.uniform(life * 0.5, life)))

    def update(self, dt: float) -> None:
        alive: List[Particle] = []
        for p in self.particles:
            p.life -= dt
            if p.life > 0:
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.vy += 80 * dt
                alive.append(p)
        self.particles = alive

    def draw(self, screen: pygame.Surface, cx: float, cy: float) -> None:
        for p in self.particles:
            sx = int(p.x - cx)
            sy = int(p.y - cy)
            if 0 <= sx < SCREEN_WIDTH and 0 <= sy < SCREEN_HEIGHT:
                r = max(1, int(p.size * (p.life / p.max_life)))
                pygame.draw.circle(screen, p.color, (sx, sy), r)

# =============================================================================
# TEXTURE GENERATOR
# =============================================================================
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

    def generate_all(self) -> None:
        self.generate_player()
        self.generate_tree()
        self.generate_rock()
        self.generate_slime()
        self.generate_skeleton()
        self.generate_grass_tile()
        self.generate_dirt_tile()
        self.generate_sand_tile()
        self.generate_water_tile(0)
        self.generate_stone_tile()
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
        self.generate_item_fiber()
        self.generate_item_feather()
        self.generate_item_leather()
        self.generate_item_spear()
        self.generate_item_bow()
        self.generate_item_arrow()
        self.generate_item_sling()
        self.generate_item_sling_bullet()
        self.generate_item_leather_armor()
        self.generate_item_wood_shield()
        self.generate_item_bed_kit()
        self.generate_item_spike_trap()
        self.generate_bed_placed()
        self.generate_spike_trap_placed()
        self.generate_wolf()
        self.generate_goblin()
        self.generate_campfire(True)
        self.generate_campfire(False)
        self.generate_torch_placed()

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
                        if (x - 24) ** 2 + (y - cy) ** 2 < rad * rad and random.random() > 0.2:
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
                    if (x - 16) ** 2 / 256 + (y - 12) ** 2 / 144 < 0.8 + n * 0.2:
                        c = int(110 + n * 40 - y * 1.5)
                        c = max(40, min(200, c))
                        s.set_at((x, y), (c, c, c, 255))
            return s
        return self._get("rock", make)

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
                s.set_at((9, y), bone)
                s.set_at((10, y), bone)
                s.set_at((13, y), bone)
                s.set_at((14, y), bone)
            for y in range(12, 20):
                s.set_at((6, y), bone)
                s.set_at((7, y), bone)
                s.set_at((16, y), bone)
                s.set_at((17, y), bone)
            return s
        return self._get("skeleton", make)

    def generate_grass_tile(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            for y in range(TILE_SIZE):
                for x in range(TILE_SIZE):
                    n = fbm_noise(x * 0.1, y * 0.1, self.seed + 4, 3)
                    g = int(90 + n * 60)
                    s.set_at((x, y), (40, g, 40))
            for _ in range(40):
                s.set_at((random.randint(0, 31), random.randint(0, 31)), (60, 180, 60))
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
                    n = fbm_noise((x + frame * 2) * 0.1, y * 0.1, self.seed + 6, 2)
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
                pygame.draw.line(s, (70, 70, 80),
                                 (random.randint(2, 29), random.randint(2, 29)),
                                 (random.randint(2, 29), random.randint(2, 29)), 1)
            return s
        return self._get("stone", make)

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
                        s.set_at((x, y), (255, max(30, 150 - (8 - y) * 15), 30, 200))
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

    def generate_item_fiber(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for i in range(5):
                sx = 4 + i * 2
                for y in range(4, 13):
                    g = 100 + int(40 * hash_noise(sx, y, self.seed + 20))
                    s.set_at((sx, y), (80, g, 50, 255))
            return s
        return self._get("item_fiber", make)

    def generate_item_feather(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(2, 15):
                s.set_at((8, y), (200, 200, 210, 255))
            for y in range(3, 12):
                w = max(1, 3 - abs(y - 7) // 2)
                for x in range(8 - w, 8 + w):
                    s.set_at((x, y), (220, 220, 230, 255))
            return s
        return self._get("item_feather", make)

    def generate_item_leather(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(3, 13):
                for x in range(3, 13):
                    c = 110 + int(30 * hash_noise(x, y, self.seed + 21))
                    s.set_at((x, y), (c, int(c * 0.6), int(c * 0.3), 255))
            return s
        return self._get("item_leather", make)

    def generate_item_spear(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(4, 15):
                s.set_at((8, y), (120, 80, 40, 255))
            for dy in range(4):
                s.set_at((8, 1 + dy), (180, 180, 200, 255))
                if dy < 3:
                    s.set_at((7, 2 + dy), (160, 160, 180, 255))
                    s.set_at((9, 2 + dy), (160, 160, 180, 255))
            return s
        return self._get("item_spear", make)

    def generate_item_bow(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(2, 14):
                cx = int(10 + 3 * math.sin((y - 8) * 0.4))
                s.set_at((cx, y), (130, 80, 30, 255))
            for y in range(3, 13):
                s.set_at((6, y), (200, 200, 210, 220))
            return s
        return self._get("item_bow", make)

    def generate_item_arrow(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(3, 14):
                s.set_at((8, y), (120, 80, 40, 255))
            s.set_at((8, 2), (180, 180, 200, 255))
            s.set_at((7, 3), (160, 160, 180, 255))
            s.set_at((9, 3), (160, 160, 180, 255))
            s.set_at((7, 13), (200, 200, 210, 200))
            s.set_at((9, 13), (200, 200, 210, 200))
            return s
        return self._get("item_arrow", make)

    def generate_item_sling(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for i in range(10):
                s.set_at((3 + i, 4 + i // 3), (140, 100, 50, 255))
            for y in range(7, 11):
                for x in range(9, 13):
                    if abs(x - 11) + abs(y - 9) < 3:
                        s.set_at((x, y), (100, 70, 30, 255))
            return s
        return self._get("item_sling", make)

    def generate_item_sling_bullet(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(16):
                for x in range(16):
                    if (x - 8) ** 2 + (y - 8) ** 2 < 16:
                        c = 130 + int(20 * hash_noise(x, y, self.seed + 22))
                        s.set_at((x, y), (c, c, c, 255))
            return s
        return self._get("item_sling_bullet", make)

    def generate_item_leather_armor(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(2, 14):
                w = 5 if y < 5 else (6 if y < 10 else 4)
                for x in range(8 - w, 8 + w):
                    c = 120 + int(20 * hash_noise(x, y, self.seed + 23))
                    s.set_at((x, y), (c, int(c * 0.55), int(c * 0.25), 255))
            return s
        return self._get("item_leather_armor", make)

    def generate_item_wood_shield(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(2, 14):
                hw = 6 - abs(y - 8) // 2
                for x in range(8 - hw, 8 + hw):
                    c = 130 + int(30 * hash_noise(x, y, self.seed + 24))
                    s.set_at((x, y), (c, int(c * 0.7), 30, 255))
            pygame.draw.circle(s, (180, 180, 200), (8, 7), 2)
            return s
        return self._get("item_wood_shield", make)

    def generate_item_bed_kit(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(6, 14):
                for x in range(2, 14):
                    s.set_at((x, y), (140, 90, 50, 255))
            for y in range(4, 10):
                for x in range(3, 8):
                    s.set_at((x, y), (230, 230, 240, 255))
            return s
        return self._get("item_bed_kit", make)

    def generate_item_spike_trap(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            for y in range(10, 14):
                for x in range(2, 14):
                    s.set_at((x, y), (100, 60, 30, 255))
            for i in range(5):
                bx = 3 + i * 2
                for dy in range(5):
                    s.set_at((bx, 9 - dy), (180, 180, 190, 255))
            return s
        return self._get("item_spike_trap", make)

    def generate_bed_placed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((40, 24), pygame.SRCALPHA)
            for y in range(8, 22):
                for x in range(4, 36):
                    s.set_at((x, y), (140, 90, 50, 255))
            for y in range(4, 14):
                for x in range(5, 16):
                    s.set_at((x, y), (220, 220, 235, 255))
            for y in range(6, 20):
                for x in range(4, 36):
                    if 8 <= y <= 19:
                        s.set_at((x, y), (180, 80, 80, 255))
            return s
        return self._get("bed_placed", make)

    def generate_spike_trap_placed(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((32, 24), pygame.SRCALPHA)
            for y in range(14, 22):
                for x in range(4, 28):
                    s.set_at((x, y), (90, 55, 25, 255))
            for i in range(6):
                bx = 5 + i * 4
                for dy in range(8):
                    c = 170 + int(20 * hash_noise(bx, dy, self.seed + 25))
                    s.set_at((bx, 13 - dy), (c, c, min(255, c + 10), 255))
                    if dy < 6:
                        s.set_at((bx + 1, 13 - dy), (c - 20, c - 20, c - 10, 255))
            return s
        return self._get("spike_trap_placed", make)

    def generate_wolf(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((32, 24), pygame.SRCALPHA)
            for y in range(8, 20):
                for x in range(4, 28):
                    if 8 <= y <= 18 and abs(x - 16) + abs(y - 13) < 14:
                        c = 100 + int(30 * hash_noise(x, y, self.seed + 30))
                        s.set_at((x, y), (c, c, c, 255))
            for y in range(15, 22):
                for lx in [(8, 10), (20, 22)]:
                    for x in range(lx[0], lx[1]):
                        s.set_at((x, y), (80, 80, 80, 255))
            for y in range(6, 12):
                for x in range(24, 30):
                    if (x - 27) ** 2 + (y - 9) ** 2 < 12:
                        s.set_at((x, y), (110, 110, 110, 255))
            s.set_at((27, 8), (200, 50, 50, 255))
            s.set_at((28, 8), (200, 50, 50, 255))
            return s
        return self._get("wolf", make)

    def generate_goblin(self) -> pygame.Surface:
        def make() -> pygame.Surface:
            s = pygame.Surface((24, 28), pygame.SRCALPHA)
            for y in range(2, 12):
                for x in range(7, 17):
                    if (x - 12) ** 2 + (y - 7) ** 2 < 30:
                        g = 120 + int(30 * hash_noise(x, y, self.seed + 31))
                        s.set_at((x, y), (80, g, 60, 255))
            s.set_at((10, 6), (200, 30, 30, 255))
            s.set_at((14, 6), (200, 30, 30, 255))
            for y in range(12, 24):
                for x in range(8, 16):
                    s.set_at((x, y), (100, 70, 40, 255))
            for y in range(3, 6):
                s.set_at((6, y), (80, 140, 60, 255))
                s.set_at((17, y), (80, 140, 60, 255))
            return s
        return self._get("goblin", make)

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
                    pygame.draw.circle(s, (255, max(0, 180 - i * 20), 50, 200), (fx, fy), 5 - i)
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
                pygame.draw.circle(s, (255, max(0, 180 - i * 25), 40, 200),
                                   (fx, max(0, fy)), max(1, 3 - min(i, 2)))
            return s
        return self._get("torch_placed", make)

# =============================================================================
# WORLD
# =============================================================================
class World:
    def __init__(self, width: int, height: int) -> None:
        self.width = width; self.height = height
        self.tiles: List[List[int]] = [[TILE_GRASS] * height for _ in range(width)]
        self.biome_noise: List[List[float]] = [[0.0] * height for _ in range(width)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> int:
        return self.tiles[x][y] if self.in_bounds(x, y) else TILE_STONE_WALL

    def set_tile(self, x: int, y: int, tile: int) -> None:
        if self.in_bounds(x, y):
            self.tiles[x][y] = tile

    def is_solid(self, x: int, y: int) -> bool:
        t = self.get_tile(x, y)
        return t == TILE_WATER or t == TILE_STONE_WALL

class WorldGenerator:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def generate(self, w: int, h: int) -> World:
        world = World(w, h)
        for x in range(w):
            for y in range(h):
                n = fbm_noise(x * 0.05, y * 0.05, self.seed, 5)
                world.biome_noise[x][y] = n
                if n < 0.30:
                    world.set_tile(x, y, TILE_WATER)
                elif n < 0.35:
                    world.set_tile(x, y, TILE_SAND)
                elif n < 0.68:
                    world.set_tile(x, y, TILE_GRASS)
                elif n < 0.80:
                    world.set_tile(x, y, TILE_DIRT)
                else:
                    world.set_tile(x, y, TILE_STONE_FLOOR)
        grid = self._caves(w, h)
        for x in range(w):
            for y in range(h):
                if grid[x][y] == 1 and world.biome_noise[x][y] > 0.55:
                    if world.get_tile(x, y) in (TILE_GRASS, TILE_DIRT, TILE_STONE_FLOOR):
                        world.set_tile(x, y, TILE_STONE_WALL)
        return world

    def _caves(self, w: int, h: int) -> List[List[int]]:
        g = [[1 if random.random() < 0.45 else 0 for _ in range(h)] for _ in range(w)]
        for _ in range(4):
            ng = [[0] * h for _ in range(w)]
            for x in range(w):
                for y in range(h):
                    walls = sum(
                        1 for dx in range(-1, 2) for dy in range(-1, 2)
                        if (dx or dy) and (
                            not (0 <= x + dx < w and 0 <= y + dy < h) or g[x + dx][y + dy] == 1
                        )
                    )
                    ng[x][y] = 1 if walls >= 5 else (0 if walls <= 3 else g[x][y])
            g = ng
        return g

# =============================================================================
# CAMERA
# =============================================================================
class Camera:
    def __init__(self, w: int, h: int) -> None:
        self.x = 0.0; self.y = 0.0
        self.width = w; self.height = h
        self.target_x = 0.0; self.target_y = 0.0
        self.shake_amt = 0.0; self.shake_timer = 0.0

    def follow(self, tx: float, ty: float) -> None:
        self.target_x = tx - self.width / 2
        self.target_y = ty - self.height / 2

    def shake(self, amount: float, duration: float) -> None:
        self.shake_amt = amount; self.shake_timer = duration

    def update(self, dt: float) -> None:
        self.x = lerp(self.x, self.target_x, 0.12)
        self.y = lerp(self.y, self.target_y, 0.12)
        self.x = clamp(self.x, 0, WORLD_WIDTH * TILE_SIZE - self.width)
        self.y = clamp(self.y, 0, WORLD_HEIGHT * TILE_SIZE - self.height)
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.x += random.uniform(-self.shake_amt, self.shake_amt)
            self.y += random.uniform(-self.shake_amt, self.shake_amt)

# =============================================================================
# MINIMAP
# =============================================================================
class Minimap:
    TILE_COLORS: Dict[int, Tuple[int, int, int]] = {
        TILE_WATER: (30, 80, 180), TILE_SAND: (210, 190, 140), TILE_GRASS: (45, 120, 50),
        TILE_DIRT: (100, 75, 45), TILE_STONE_FLOOR: (110, 110, 120), TILE_STONE_WALL: (55, 55, 65),
    }

    def __init__(self, world: World, size: int = 140) -> None:
        self.size = size
        self.surface = pygame.Surface((size, size))
        sx = size / world.width
        sy = size / world.height
        for x in range(world.width):
            for y in range(world.height):
                color = self.TILE_COLORS.get(world.get_tile(x, y), BLACK)
                px, py = int(x * sx), int(y * sy)
                if px < size and py < size:
                    self.surface.set_at((px, py), color)

    def draw(self, screen: pygame.Surface, px: float, py: float) -> None:
        dx = SCREEN_WIDTH - self.size - 15
        dy = 50
        screen.blit(self.surface, (dx, dy))
        pygame.draw.rect(screen, (180, 180, 200), (dx, dy, self.size, self.size), 2)
        ppx = int((px / (WORLD_WIDTH * TILE_SIZE)) * self.size)
        ppy = int((py / (WORLD_HEIGHT * TILE_SIZE)) * self.size)
        pygame.draw.circle(screen, WHITE, (dx + ppx, dy + ppy), 3)
        pygame.draw.circle(screen, RED, (dx + ppx, dy + ppy), 3, 1)

# =============================================================================
# GUI
# =============================================================================
class UIElement:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect; self.visible = True; self.enabled = True
        self.children: List['UIElement'] = []

    def add_child(self, child: 'UIElement') -> None:
        self.children.append(child)

    def update(self, dt: float) -> None:
        if self.visible:
            for c in self.children:
                c.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.visible:
            for c in self.children:
                c.draw(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        for c in reversed(self.children):
            if c.handle_event(event):
                return True
        return False

class ProgressBar(UIElement):
    def __init__(self, rect: pygame.Rect, max_value: float,
                 fg: Tuple[int, int, int] = (200, 60, 60),
                 bg: Tuple[int, int, int] = (40, 20, 20)) -> None:
        super().__init__(rect)
        self.value = max_value; self.max_value = max_value
        self.color_fg = fg; self.color_bg = bg

    def set_value(self, v: float) -> None:
        self.value = clamp(v, 0, self.max_value)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        pygame.draw.rect(surface, self.color_bg, self.rect, border_radius=4)
        fw = int(self.rect.width * (self.value / self.max_value)) if self.max_value > 0 else 0
        pygame.draw.rect(surface, self.color_fg,
                         pygame.Rect(self.rect.x, self.rect.y, fw, self.rect.height), border_radius=4)
        pygame.draw.rect(surface, (200, 200, 220), self.rect, 2, border_radius=4)

class Tooltip:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.visible = False
        self.pos = (0, 0)
        self.font = pygame.font.SysFont('consolas', 13)

    def clear(self) -> None:
        self.visible = False

    def show(self, lines: List[str], pos: Tuple[int, int]) -> None:
        self.lines = lines; self.visible = True; self.pos = pos

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.lines:
            return
        surfs = [self.font.render(l, True, WHITE) for l in self.lines]
        mw = max(s.get_width() for s in surfs)
        th = len(surfs) * 17 + 10
        x = min(self.pos[0] + 14, SCREEN_WIDTH - mw - 20)
        y = min(self.pos[1] + 14, SCREEN_HEIGHT - th - 10)
        bg = pygame.Surface((mw + 16, th), pygame.SRCALPHA)
        bg.fill((12, 12, 22, 230))
        surface.blit(bg, (x, y))
        pygame.draw.rect(surface, (130, 130, 160), (x, y, mw + 16, th), 1, border_radius=3)
        for i, s in enumerate(surfs):
            surface.blit(s, (x + 8, y + 5 + i * 17))

class InventoryGrid(UIElement):
    SLOTS_PER_PAGE: int = 24

    def __init__(self, rect: pygame.Rect, inventory: Inventory, textures: TextureGenerator) -> None:
        super().__init__(rect)
        self.inventory = inventory; self.textures = textures
        self.slot_size = 48; self.cols = 6
        self.page = 0; self.max_pages = max(1, inventory.capacity // self.SLOTS_PER_PAGE)
        self.font = pygame.font.SysFont('consolas', 14)
        self.title_font = pygame.font.SysFont('consolas', 20, bold=True)

    def draw(self, surface: pygame.Surface, tooltip: Tooltip) -> None:
        if not self.visible:
            return
        bg = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg.fill((20, 20, 32, 235))
        surface.blit(bg, self.rect.topleft)
        pygame.draw.rect(surface, (130, 130, 155), self.rect, 2, border_radius=8)
        title = self.title_font.render(f"Inventory (Page {self.page + 1}/{self.max_pages})", True, WHITE)
        surface.blit(title, (self.rect.centerx - title.get_width() // 2, self.rect.y + 8))
        # Page nav arrows
        arrow_y = self.rect.y + 10
        left_r = pygame.Rect(self.rect.x + 10, arrow_y, 24, 24)
        right_r = pygame.Rect(self.rect.right - 34, arrow_y, 24, 24)
        lc = (180, 180, 220) if self.page > 0 else (70, 70, 90)
        rc = (180, 180, 220) if self.page < self.max_pages - 1 else (70, 70, 90)
        surface.blit(self.font.render("<", True, lc), (left_r.x + 7, left_r.y + 3))
        surface.blit(self.font.render(">", True, rc), (right_r.x + 7, right_r.y + 3))
        mx, my = pygame.mouse.get_pos()
        start_slot = self.page * self.SLOTS_PER_PAGE
        for idx in range(self.SLOTS_PER_PAGE):
            i = start_slot + idx
            col = idx % self.cols
            row = idx // self.cols
            x = self.rect.x + 12 + col * (self.slot_size + 6)
            y = self.rect.y + 38 + row * (self.slot_size + 6)
            sr = pygame.Rect(x, y, self.slot_size, self.slot_size)
            bg_c = (80, 80, 110) if i == self.inventory.equipped_slot else (45, 45, 60)
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            bd = (200, 200, 240) if i == self.inventory.equipped_slot else (100, 100, 120)
            pygame.draw.rect(surface, bd, sr, 1, border_radius=4)
            if i in self.inventory.slots:
                item_id, count = self.inventory.slots[i]
                icon = self.textures.cache.get(f'item_{item_id}')
                if icon:
                    surface.blit(pygame.transform.scale(icon, (34, 34)), (x + 7, y + 7))
                if count > 1:
                    ct = self.font.render(str(count), True, WHITE)
                    surface.blit(ct, (x + self.slot_size - ct.get_width() - 4,
                                      y + self.slot_size - ct.get_height() - 2))
                if sr.collidepoint(mx, my) and item_id in ITEM_DATA:
                    d = ITEM_DATA[item_id]
                    tooltip.show([d['name'], d['desc']], (mx, my))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Page nav
            arrow_y = self.rect.y + 10
            if pygame.Rect(self.rect.x + 10, arrow_y, 24, 24).collidepoint(mx, my):
                if self.page > 0:
                    self.page -= 1
                return True
            if pygame.Rect(self.rect.right - 34, arrow_y, 24, 24).collidepoint(mx, my):
                if self.page < self.max_pages - 1:
                    self.page += 1
                return True
            # Slot click
            start_slot = self.page * self.SLOTS_PER_PAGE
            for idx in range(self.SLOTS_PER_PAGE):
                i = start_slot + idx
                col = idx % self.cols
                row = idx // self.cols
                x = self.rect.x + 12 + col * (self.slot_size + 6)
                y = self.rect.y + 38 + row * (self.slot_size + 6)
                if pygame.Rect(x, y, self.slot_size, self.slot_size).collidepoint(mx, my):
                    self.inventory.equipped_slot = i
                    return True
        return False

# =============================================================================
# SAVE / LOAD
# =============================================================================
def save_game(path: str, data: Dict[str, Any]) -> None:
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_game(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)

# =============================================================================
# GAME
# =============================================================================
class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sandbox Survival RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dead = False
        self.paused = False
        self.seed = 42

        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.font_lg = pygame.font.SysFont('consolas', 22, bold=True)
        self.font_xl = pygame.font.SysFont('consolas', 48, bold=True)

        self.textures = TextureGenerator(seed=self.seed)
        self.textures.generate_all()

        self.world_gen = WorldGenerator(seed=self.seed)
        self.world = self.world_gen.generate(WORLD_WIDTH, WORLD_HEIGHT)

        self.em = EntityManager()
        self.movement = MovementSystem()
        self.physics = PhysicsSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.renderer = RenderSystem(self.screen)
        self.daynight = DayNightCycle(day_length=240.0)
        self.ai_system = AISystem()
        self.projectile_system = ProjectileSystem()
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = ParticleSystem()

        self.player_id = self._create_player()
        self._populate_world()

        self.show_inventory = False
        self.show_crafting = False
        self.show_character = False
        self.craft_scroll = 0
        self.tooltip = Tooltip()

        inv_comp: Inventory = self.em.get_component(self.player_id, Inventory)
        self.inventory_ui = InventoryGrid(
            pygame.Rect(SCREEN_WIDTH // 2 - 195, SCREEN_HEIGHT // 2 - 160, 390, 320),
            inv_comp, self.textures)
        self.health_bar = ProgressBar(pygame.Rect(20, 16, 200, 18), 100, (210, 50, 50), (40, 15, 15))
        self.xp_bar = ProgressBar(pygame.Rect(20, 38, 200, 12), 50, (70, 160, 255), (20, 30, 50))

        self.minimap = Minimap(self.world)

        self.interact_cd = 0.0
        self.attack_cd = 0.0
        self.attack_anim = 0.0
        self.player_hit_cd = 0.0
        self.damage_flash = 0.0
        self.mob_spawn_timer = 0.0
        self.campfire_heal_timer = 0.0
        self.night_dmg_timer = 0.0
        self.survival_timer = 0.0
        self.dmg_numbers: List[Tuple[float, float, str, Tuple[int, int, int], float]] = []
        self.notification: str = ""
        self.notification_timer: float = 0.0

    def _notify(self, msg: str, duration: float = 2.5) -> None:
        self.notification = msg
        self.notification_timer = duration

    # -- Entity Creation -------------------------------------------------------
    def _create_player(self) -> int:
        eid = self.em.create_entity()
        cx = WORLD_WIDTH * TILE_SIZE / 2
        cy = WORLD_HEIGHT * TILE_SIZE / 2
        self.em.add_component(eid, Transform(cx, cy, 1))
        self.em.add_component(eid, Velocity(0, 0, 0.82))
        self.em.add_component(eid, Renderable(self.textures.get('player'), layer=5))
        self.em.add_component(eid, Collider(20, 28, True))
        self.em.add_component(eid, Health(100))
        self.em.add_component(eid, Inventory(96))
        self.em.add_component(eid, PlayerStats())
        self.em.add_component(eid, Equipment())
        inv: Inventory = self.em.get_component(eid, Inventory)
        inv.add_item('wood', 5)
        inv.add_item('stone', 3)
        return eid

    def _create_slime(self, x: float, y: float) -> int:
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(x, y))
        self.em.add_component(eid, Velocity(random.uniform(-20, 20), random.uniform(-20, 20), 0.9))
        self.em.add_component(eid, Renderable(self.textures.get('slime'), layer=3))
        self.em.add_component(eid, Collider(24, 18, True))
        self.em.add_component(eid, Health(30))
        mob_ai = AI('wander', 'slime')
        mob_ai.speed = 35; mob_ai.detection_range = 180; mob_ai.contact_damage = 5; mob_ai.xp_value = 15
        self.em.add_component(eid, mob_ai)
        return eid

    def _create_skeleton(self, x: float, y: float) -> int:
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(x, y))
        self.em.add_component(eid, Velocity(0, 0, 0.88))
        self.em.add_component(eid, Renderable(self.textures.get('skeleton'), layer=3))
        self.em.add_component(eid, Collider(20, 28, True))
        self.em.add_component(eid, Health(60))
        mob_ai = AI('wander', 'skeleton')
        mob_ai.speed = 50; mob_ai.detection_range = 220; mob_ai.contact_damage = 10; mob_ai.xp_value = 35
        self.em.add_component(eid, mob_ai)
        return eid

    def _create_wolf(self, x: float, y: float) -> int:
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(x, y))
        self.em.add_component(eid, Velocity(random.uniform(-30, 30), random.uniform(-30, 30), 0.85))
        self.em.add_component(eid, Renderable(self.textures.get('wolf'), layer=3))
        self.em.add_component(eid, Collider(28, 20, True))
        self.em.add_component(eid, Health(40))
        mob_ai = AI('wander', 'wolf')
        mob_ai.speed = 70; mob_ai.detection_range = 200; mob_ai.contact_damage = 8; mob_ai.xp_value = 25
        self.em.add_component(eid, mob_ai)
        return eid

    def _create_goblin(self, x: float, y: float) -> int:
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(x, y))
        self.em.add_component(eid, Velocity(0, 0, 0.88))
        self.em.add_component(eid, Renderable(self.textures.get('goblin'), layer=3))
        self.em.add_component(eid, Collider(20, 24, True))
        self.em.add_component(eid, Health(45))
        mob_ai = AI('wander', 'goblin')
        mob_ai.speed = 45; mob_ai.detection_range = 250; mob_ai.contact_damage = 7; mob_ai.xp_value = 30
        self.em.add_component(eid, mob_ai)
        return eid

    def _populate_world(self) -> None:
        for _ in range(300):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
            if self.world.get_tile(x, y) == TILE_GRASS:
                eid = self.em.create_entity()
                self.em.add_component(eid, Transform(x * TILE_SIZE + 8, y * TILE_SIZE - 16))
                self.em.add_component(eid, Renderable(self.textures.get('tree'), layer=2))
                self.em.add_component(eid, Collider(24, 32, True))
        for _ in range(180):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
            if self.world.get_tile(x, y) in (TILE_GRASS, TILE_DIRT, TILE_STONE_FLOOR):
                eid = self.em.create_entity()
                self.em.add_component(eid, Transform(x * TILE_SIZE + 4, y * TILE_SIZE + 6))
                self.em.add_component(eid, Renderable(self.textures.get('rock'), layer=1))
                self.em.add_component(eid, Collider(26, 18, True))
        for _ in range(30):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
            if self.world.get_tile(x, y) == TILE_GRASS:
                self._create_slime(x * TILE_SIZE + 8, y * TILE_SIZE + 8)
        for _ in range(12):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
            if self.world.get_tile(x, y) in (TILE_GRASS, TILE_DIRT):
                self._create_wolf(x * TILE_SIZE + 8, y * TILE_SIZE + 8)
        for _ in range(8):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
            if self.world.get_tile(x, y) in (TILE_GRASS, TILE_DIRT, TILE_STONE_FLOOR):
                self._create_goblin(x * TILE_SIZE + 8, y * TILE_SIZE + 8)

    def _spawn_mob(self) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        for _ in range(20):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
            wx, wy = x * TILE_SIZE, y * TILE_SIZE
            if math.hypot(wx - pt.x, wy - pt.y) < 400:
                continue
            if self.world.is_solid(x, y):
                continue
            roll = random.random()
            if self.daynight.get_darkness() > 0.4 and roll < 0.4:
                self._create_skeleton(wx, wy)
            elif roll < 0.55:
                self._create_wolf(wx, wy)
            elif roll < 0.7:
                self._create_goblin(wx, wy)
            else:
                self._create_slime(wx, wy)
            return

    # -- Main Loop -------------------------------------------------------------
    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            if self.paused:
                pass
            elif not self.dead:
                self._update(dt)
            else:
                self.particles.update(dt)
                self.dmg_numbers = [(x, y - 40 * dt, t, c, l - dt)
                                    for x, y, t, c, l in self.dmg_numbers if l - dt > 0]
            self._render()
        pygame.quit()
        sys.exit()

    # -- Events ----------------------------------------------------------------
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if self.dead:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self._respawn()
                    elif event.key == pygame.K_q:
                        self.running = False
                continue

            # Pause menu click handling
            if self.paused:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_pause_click(event.pos)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.paused = False
                continue

            if event.type == pygame.MOUSEWHEEL:
                if self.show_crafting:
                    self.craft_scroll = max(0, self.craft_scroll - event.y)
                else:
                    inv: Inventory = self.em.get_component(self.player_id, Inventory)
                    inv.equipped_slot = (inv.equipped_slot - event.y) % 6

            if event.type == pygame.KEYDOWN:
                inv = self.em.get_component(self.player_id, Inventory)
                if event.key == pygame.K_ESCAPE:
                    if self.show_inventory or self.show_crafting or self.show_character:
                        self.show_inventory = False
                        self.show_crafting = False
                        self.show_character = False
                    else:
                        self.paused = True
                elif event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    if self.show_inventory:
                        self.show_crafting = False
                elif event.key == pygame.K_c:
                    self.show_crafting = not self.show_crafting
                    if self.show_crafting:
                        self.show_inventory = False
                elif event.key == pygame.K_p:
                    self.show_character = not self.show_character
                elif event.key == pygame.K_f:
                    self._use_equipped_item()
                elif event.key == pygame.K_r:
                    self._fire_ranged()
                elif event.key == pygame.K_F5:
                    self._save_game()
                elif event.key == pygame.K_F9:
                    self._load_game()
                for n in range(1, 7):
                    if event.key == getattr(pygame, f'K_{n}'):
                        inv.equipped_slot = n - 1

            if self.show_inventory:
                self.inventory_ui.handle_event(event)
            if self.show_crafting:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_craft_click(event.pos)
            if self.show_character:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_character_click(event.pos)

    def _handle_craft_click(self, pos: Tuple[int, int]) -> None:
        max_vis = 8
        vis_count = min(len(RECIPES), max_vis)
        pw, ph_c = 400, 55 + vis_count * 52
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph_c // 2
        for vi in range(vis_count):
            i = vi + self.craft_scroll
            if i >= len(RECIPES):
                break
            ry = py + 44 + vi * 52
            btn = pygame.Rect(px + 10, ry, pw - 20, 44)
            if btn.collidepoint(pos):
                self._craft(RECIPES[i])
                return

    # -- Update ----------------------------------------------------------------
    def _update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        pv: Velocity = self.em.get_component(self.player_id, Velocity)
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pr: Renderable = self.em.get_component(self.player_id, Renderable)
        ps_mv: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        speed = 180.0 + ps_mv.agi_bonus * 10
        if keys[pygame.K_w]:
            pv.vy -= speed * dt * 10
        if keys[pygame.K_s]:
            pv.vy += speed * dt * 10
        if keys[pygame.K_a]:
            pv.vx -= speed * dt * 10
        if keys[pygame.K_d]:
            pv.vx += speed * dt * 10
        if pv.vx < -5:
            pr.flip_x = True
        elif pv.vx > 5:
            pr.flip_x = False

        self.movement.update(dt, self.em)
        self.physics.update(dt, self.em, self.world)
        self.ai_system.update(dt, self.em, self.player_id)
        proj_hits = self.projectile_system.update(dt, self.em, self.particles)
        for mid, pdmg, _owner in proj_hits:
            if self.em.has_component(mid, Health):
                mh: Health = self.em.get_component(mid, Health)
                mh.damage(pdmg)
                mt: Transform = self.em.get_component(mid, Transform)
                self.dmg_numbers.append((mt.x, mt.y - 16, str(pdmg), YELLOW, 0.8))
                if not mh.is_alive():
                    ai_c: AI = self.em.get_component(mid, AI)
                    self._on_mob_killed(mid, ai_c)
        self.daynight.update(dt)
        self.camera.follow(pt.x, pt.y)
        self.camera.update(dt)
        self.particles.update(dt)

        # Cooldowns
        self.interact_cd = max(0, self.interact_cd - dt)
        self.attack_cd = max(0, self.attack_cd - dt)
        self.attack_anim = max(0, self.attack_anim - dt)
        self.player_hit_cd = max(0, self.player_hit_cd - dt)
        self.damage_flash = max(0, self.damage_flash - dt)
        self.notification_timer = max(0, self.notification_timer - dt)

        if keys[pygame.K_e] and self.interact_cd == 0:
            self._interact()
            self.interact_cd = 0.25
        if keys[pygame.K_SPACE] and self.attack_cd == 0:
            self._attack()
            self.attack_cd = 0.30
            self.attack_anim = 0.18

        # Damage numbers decay
        self.dmg_numbers = [(x, y - 40 * dt, t, c, l - dt)
                            for x, y, t, c, l in self.dmg_numbers if l - dt > 0]

        # Kill dead mobs
        for eid in list(self.em.get_entities_with(Health, AI)):
            h: Health = self.em.get_component(eid, Health)
            if not h.is_alive():
                mob_ai = self.em.get_component(eid, AI)  # type: AI
                self._on_mob_killed(eid, mob_ai)

        # Mob contact damage
        if self.player_hit_cd <= 0:
            for eid in self.em.get_entities_with(Transform, AI):
                t: Transform = self.em.get_component(eid, Transform)
                ai_c: AI = self.em.get_component(eid, AI)
                dist = math.hypot(t.x - pt.x, t.y - pt.y)
                if dist < 28:
                    ph: Health = self.em.get_component(self.player_id, Health)
                    equip: Equipment = self.em.get_component(self.player_id, Equipment)
                    ps_d: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
                    raw_dmg = ai_c.contact_damage
                    defense = equip.get_total_defense() + ps_d.def_bonus
                    dmg = max(1, raw_dmg - defense)
                    ph.damage(dmg)
                    self.health_bar.set_value(ph.current)
                    self.player_hit_cd = 0.5
                    self.damage_flash = 0.15
                    self.camera.shake(4.0, 0.2)
                    self.particles.emit(pt.x + 10, pt.y + 14, 8, RED, 60, 0.4)
                    self.dmg_numbers.append((pt.x, pt.y - 16, str(dmg), RED, 0.8))
                    if not ph.is_alive():
                        self.dead = True
                        self.dmg_numbers.append((pt.x, pt.y - 30, 'YOU DIED', RED, 2.5))
                    break

        # Campfire healing
        self.campfire_heal_timer += dt
        if self.campfire_heal_timer >= 1.0:
            self.campfire_heal_timer = 0.0
            ph_p: Health = self.em.get_component(self.player_id, Health)
            if ph_p.current < ph_p.maximum:
                for eid in self.em.get_entities_with(Transform, Placeable):
                    pl: Placeable = self.em.get_component(eid, Placeable)
                    if pl.item_type == 'campfire':
                        t2: Transform = self.em.get_component(eid, Transform)
                        if math.hypot(t2.x - pt.x, t2.y - pt.y) < 120:
                            amt = 3
                            ph_p.heal(amt)
                            self.health_bar.set_value(ph_p.current)
                            self.dmg_numbers.append((pt.x, pt.y - 20, f'+{amt}', GREEN, 0.6))
                            break

        # Night damage
        darkness = self.daynight.get_darkness()
        if darkness > 0.5:
            self.night_dmg_timer += dt
            if self.night_dmg_timer >= 3.0:
                self.night_dmg_timer = 0.0
                inv_n: Inventory = self.em.get_component(self.player_id, Inventory)
                near_light = inv_n.get_equipped() == 'torch' and inv_n.has('torch')
                if not near_light:
                    for eid in self.em.get_entities_with(Transform, LightSource):
                        t3: Transform = self.em.get_component(eid, Transform)
                        if math.hypot(t3.x - pt.x, t3.y - pt.y) < 200:
                            near_light = True
                            break
                if not near_light:
                    ph_n: Health = self.em.get_component(self.player_id, Health)
                    ph_n.damage(3)
                    self.health_bar.set_value(ph_n.current)
                    self.damage_flash = 0.1
                    self.dmg_numbers.append((pt.x, pt.y - 20, '3', RED, 0.8))
                    if not ph_n.is_alive():
                        self.dead = True
        else:
            self.night_dmg_timer = 0.0

        # Mob respawning
        self.mob_spawn_timer += dt
        if self.mob_spawn_timer > 20.0:
            self.mob_spawn_timer = 0.0
            if len(self.em.get_entities_with(AI)) < 50:
                self._spawn_mob()

        # Spike trap damage to mobs
        for peid in list(self.em.get_entities_with(Transform, Placeable)):
            pl: Placeable = self.em.get_component(peid, Placeable)
            if pl.item_type == 'spike_trap':
                trap_t: Transform = self.em.get_component(peid, Transform)
                for mid in self.em.get_entities_with(Transform, Health, AI):
                    mt2: Transform = self.em.get_component(mid, Transform)
                    if math.hypot(mt2.x - trap_t.x, mt2.y - trap_t.y) < 24:
                        mh2: Health = self.em.get_component(mid, Health)
                        trap_dmg = 8
                        mh2.damage(trap_dmg)
                        self.dmg_numbers.append((mt2.x, mt2.y - 16, str(trap_dmg), (200, 100, 50), 0.6))
                        # Trap takes wear damage too
                        if self.em.has_component(peid, Health):
                            trap_hp: Health = self.em.get_component(peid, Health)
                            trap_hp.damage(2)
                            if not trap_hp.is_alive():
                                self.em.destroy_entity(peid)
                                self.dmg_numbers.append((trap_t.x, trap_t.y - 10, 'Trap broke!', GRAY, 1.0))
                        break

        # AI attacks nearby placeables with health
        for mid in self.em.get_entities_with(Transform, AI):
            mt3: Transform = self.em.get_component(mid, Transform)
            ai_m: AI = self.em.get_component(mid, AI)
            if ai_m.state != 'chase':
                for peid in list(self.em.get_entities_with(Transform, Placeable, Health)):
                    pt_p: Transform = self.em.get_component(peid, Transform)
                    if math.hypot(pt_p.x - mt3.x, pt_p.y - mt3.y) < 40:
                        plh: Health = self.em.get_component(peid, Health)
                        plh.damage(1)
                        if not plh.is_alive():
                            pl_d: Placeable = self.em.get_component(peid, Placeable)
                            self.dmg_numbers.append((pt_p.x, pt_p.y - 10, f'{pl_d.item_type} destroyed!', RED, 1.2))
                            self.em.destroy_entity(peid)
                        break

        # HUD stat updates
        self.survival_timer += dt
        if self.survival_timer > 0.5:
            self.survival_timer = 0.0
            ph_u: Health = self.em.get_component(self.player_id, Health)
            self.health_bar.set_value(ph_u.current)
            ps_u: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
            self.xp_bar.max_value = ps_u.xp_to_next
            self.xp_bar.set_value(ps_u.xp)

    # -- Actions ---------------------------------------------------------------
    def _get_attack_damage(self) -> int:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        equip: Equipment = self.em.get_component(self.player_id, Equipment)
        eq = inv.get_equipped()
        base = 5
        if eq and eq in ITEM_DATA and ITEM_DATA[eq]['damage'] > 0:
            base = ITEM_DATA[eq]['damage']
        # Check equipped weapon (character menu weapon slot)
        eq_wpn = equip.get('weapon')
        if eq_wpn and eq_wpn in ITEM_DATA and ITEM_DATA[eq_wpn]['damage'] > base:
            base = ITEM_DATA[eq_wpn]['damage']
        return base + (ps.level - 1) * 2 + ps.str_bonus * 2

    def _get_attack_range(self) -> float:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        equip: Equipment = self.em.get_component(self.player_id, Equipment)
        eq = inv.get_equipped()
        # Spear gets longer range
        if eq == 'spear' or equip.get('weapon') == 'spear':
            return 65.0
        if eq and eq in ITEM_DATA and ITEM_DATA[eq]['damage'] > 0:
            return 55.0
        return 38.0

    def _attack(self) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        px, py = pt.x + 10, pt.y + 14
        rng = self._get_attack_range()
        dmg = self._get_attack_damage()
        for eid in self.em.get_entities_with(Transform, Health, AI):
            t: Transform = self.em.get_component(eid, Transform)
            dist = math.hypot(t.x - px, t.y - py)
            if dist < rng:
                h: Health = self.em.get_component(eid, Health)
                h.damage(dmg)
                v_mob = self.em.get_component(eid, Velocity)
                if v_mob and dist > 1:
                    dx, dy = t.x - px, t.y - py
                    v_mob.vx += (dx / dist) * 200
                    v_mob.vy += (dy / dist) * 200
                self.dmg_numbers.append((t.x, t.y - 16, str(dmg), YELLOW, 0.8))
                self.particles.emit(t.x + 12, t.y + 10, 6, YELLOW, 50, 0.3)

    def _on_mob_killed(self, eid: int, mob_ai: AI) -> None:
        td: Transform = self.em.get_component(eid, Transform)
        pinv: Inventory = self.em.get_component(self.player_id, Inventory)
        if mob_ai.mob_type == 'slime':
            pinv.add_item('berry', random.randint(1, 3))
            self.dmg_numbers.append((td.x, td.y - 10, '+Berry', GREEN, 1.2))
        elif mob_ai.mob_type == 'skeleton':
            pinv.add_item('stone', random.randint(2, 4))
            pinv.add_item('stick', random.randint(1, 2))
            self.dmg_numbers.append((td.x, td.y - 10, '+Loot', CYAN, 1.2))
        elif mob_ai.mob_type == 'wolf':
            pinv.add_item('leather', random.randint(1, 2))
            self.dmg_numbers.append((td.x, td.y - 10, '+Leather', (180, 120, 60), 1.2))
        elif mob_ai.mob_type == 'goblin':
            pinv.add_item('stone', random.randint(1, 3))
            pinv.add_item('fiber', random.randint(1, 2))
            if random.random() < 0.3:
                pinv.add_item('feather', 1)
            self.dmg_numbers.append((td.x, td.y - 10, '+Loot', CYAN, 1.2))
        color_map = {'slime': (50, 200, 70), 'skeleton': (200, 200, 210),
                     'wolf': (140, 140, 140), 'goblin': (80, 160, 60)}
        color = color_map.get(mob_ai.mob_type, (200, 200, 200))
        self.particles.emit(td.x + 12, td.y + 10, 15, color, 80, 0.5)
        ps_k: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        ps_k.kills += 1
        self._check_level_up(mob_ai.xp_value)
        self.em.destroy_entity(eid)

    def _fire_ranged(self) -> None:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        equip: Equipment = self.em.get_component(self.player_id, Equipment)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        # Check hotbar equipped ranged weapon first, then equipment slot
        eq = inv.get_equipped()
        ranged_id = ''
        if eq and eq in ITEM_DATA and ITEM_DATA[eq]['category'] == 'ranged':
            ranged_id = eq
        elif equip.get('ranged'):
            ranged_id = equip.get('ranged')
        if not ranged_id or ranged_id not in ITEM_DATA:
            self._notify("No ranged weapon equipped!")
            return
        ammo_type = ITEM_DATA[ranged_id]['ammo_type']
        # Check ammo in inventory or equipment ammo slot
        has_ammo = inv.has(ammo_type)
        if not has_ammo:
            self._notify(f"No {ITEM_DATA.get(ammo_type, {}).get('name', 'ammo')}!")
            return
        inv.remove_item(ammo_type, 1)
        pt: Transform = self.em.get_component(self.player_id, Transform)
        mx, my = pygame.mouse.get_pos()
        world_mx = mx + self.camera.x
        world_my = my + self.camera.y
        dx = world_mx - (pt.x + 10)
        dy = world_my - (pt.y + 14)
        dist = math.hypot(dx, dy)
        if dist < 1:
            dx, dy = 1.0, 0.0
            dist = 1.0
        speed = 350.0
        vx = (dx / dist) * speed
        vy = (dy / dist) * speed
        dmg = ITEM_DATA[ranged_id]['damage'] + ps.str_bonus
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(pt.x + 10, pt.y + 14))
        self.em.add_component(eid, Projectile(vx, vy, dmg, self.player_id))
        # Small projectile visual
        proj_s = pygame.Surface((6, 6), pygame.SRCALPHA)
        if ranged_id == 'bow':
            pygame.draw.line(proj_s, (200, 180, 120), (0, 5), (5, 0), 2)
        else:
            pygame.draw.circle(proj_s, (160, 160, 170), (3, 3), 3)
        self.em.add_component(eid, Renderable(proj_s, layer=6))

    def _interact(self) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        px, py = pt.x + 10, pt.y + 14
        nearest: Optional[int] = None
        nearest_dist = 50.0
        for eid in self.em.get_entities_with(Transform, Renderable):
            if eid == self.player_id or self.em.has_component(eid, AI):
                continue
            if self.em.has_component(eid, Placeable):
                continue
            t: Transform = self.em.get_component(eid, Transform)
            r: Renderable = self.em.get_component(eid, Renderable)
            if r.surface in (self.textures.get('tree'), self.textures.get('rock')):
                d = math.hypot(t.x - px, t.y - py)
                if d < nearest_dist:
                    nearest = eid
                    nearest_dist = d
        if nearest is not None:
            r = self.em.get_component(nearest, Renderable)
            eq = inv.get_equipped()
            bonus = ITEM_DATA[eq]['harvest'] if eq and eq in ITEM_DATA else 0
            if r.surface == self.textures.get('tree'):
                inv.add_item('wood', random.randint(2, 4) + bonus)
                inv.add_item('stick', 1)
                if random.random() < 0.4:
                    inv.add_item('fiber', random.randint(1, 2))
                if random.random() < 0.15:
                    inv.add_item('feather', 1)
                t_h: Transform = self.em.get_component(nearest, Transform)
                self.particles.emit(t_h.x + 20, t_h.y + 30, 8, (80, 50, 30), 40, 0.3)
            else:
                inv.add_item('stone', random.randint(2, 3) + bonus)
                t_h = self.em.get_component(nearest, Transform)
                self.particles.emit(t_h.x + 14, t_h.y + 10, 8, GRAY, 40, 0.3)
            self.em.destroy_entity(nearest)

    def _use_equipped_item(self) -> None:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        eq = inv.get_equipped()
        if not eq or eq not in ITEM_DATA:
            return
        data = ITEM_DATA[eq]
        heal = data['heal']
        placeable = data['placeable']
        pt: Transform = self.em.get_component(self.player_id, Transform)
        if heal > 0:
            ph: Health = self.em.get_component(self.player_id, Health)
            if ph.current >= ph.maximum:
                self._notify("Already at full health!")
                return
            ph.heal(heal)
            inv.remove_item(eq, 1)
            self.health_bar.set_value(ph.current)
            self.dmg_numbers.append((pt.x, pt.y - 20, f'+{heal}', GREEN, 0.8))
            self.particles.emit(pt.x + 10, pt.y + 14, 8, GREEN, 40, 0.4)
            self._notify(f"Used {data['name']} (+{heal} HP)")
        elif placeable:
            self._place_item(eq)
            inv.remove_item(eq, 1)
            self._notify(f"Placed {data['name']}")
        else:
            # Check if near a bed to sleep
            for eid in self.em.get_entities_with(Transform, Placeable):
                pl: Placeable = self.em.get_component(eid, Placeable)
                if pl.item_type == 'bed':
                    bt: Transform = self.em.get_component(eid, Transform)
                    if math.hypot(bt.x - pt.x, bt.y - pt.y) < 60:
                        if self.daynight.is_night():
                            self.daynight.time = 0.3  # Skip to morning
                            self._notify("You slept through the night!")
                            ph_b: Health = self.em.get_component(self.player_id, Health)
                            ph_b.heal(20)
                            self.health_bar.set_value(ph_b.current)
                        else:
                            self._notify("You can only sleep at night!")
                        return

    def _place_item(self, item_id: str) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pr: Renderable = self.em.get_component(self.player_id, Renderable)
        offset_x = -30 if pr.flip_x else 30
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(pt.x + offset_x, pt.y + 20))
        if item_id == 'campfire':
            self.em.add_component(eid, Renderable(self.textures.get('campfire_True'), layer=2))
            self.em.add_component(eid, LightSource(180, (255, 160, 80), 1.0))
            self.em.add_component(eid, Placeable('campfire'))
        elif item_id == 'torch':
            self.em.add_component(eid, Renderable(self.textures.get('torch_placed'), layer=2))
            self.em.add_component(eid, LightSource(120, (255, 180, 60), 0.8))
            self.em.add_component(eid, Placeable('torch'))
        elif item_id == 'bed_kit':
            self.em.add_component(eid, Renderable(self.textures.get('bed_placed'), layer=2))
            self.em.add_component(eid, Placeable('bed'))
            self.em.add_component(eid, Health(60))
        elif item_id == 'spike_trap':
            self.em.add_component(eid, Renderable(self.textures.get('spike_trap_placed'), layer=2))
            self.em.add_component(eid, Placeable('spike_trap'))
            self.em.add_component(eid, Health(40))

    def _craft(self, recipe: Dict[str, Any]) -> None:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        for item, cost in recipe['cost'].items():
            if not inv.has(item, cost):
                self._notify("Not enough materials!")
                return
        for item, cost in recipe['cost'].items():
            inv.remove_item(item, cost)
        qty = recipe.get('qty', 1)
        inv.add_item(recipe['gives'], qty)
        self._notify(f"Crafted {recipe['name']}!")
        pt: Transform = self.em.get_component(self.player_id, Transform)
        self.particles.emit(pt.x + 10, pt.y + 14, 10, CYAN, 50, 0.4)

    def _check_level_up(self, xp: int) -> None:
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        if ps.add_xp(xp):
            ph: Health = self.em.get_component(self.player_id, Health)
            ph.maximum += 10
            ph.current = ph.maximum
            self.health_bar.max_value = ph.maximum
            self.health_bar.set_value(ph.current)
            pt: Transform = self.em.get_component(self.player_id, Transform)
            self.dmg_numbers.append((pt.x, pt.y - 30, f'LEVEL {ps.level}!', CYAN, 2.0))
            self.particles.emit(pt.x + 10, pt.y + 14, 25, YELLOW, 100, 0.8)
            self.particles.emit(pt.x + 10, pt.y + 14, 25, CYAN, 80, 0.6)
            self._notify(f"Level Up! You are now level {ps.level}!")

    def _respawn(self) -> None:
        self.dead = False
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pt.x = WORLD_WIDTH * TILE_SIZE / 2
        pt.y = WORLD_HEIGHT * TILE_SIZE / 2
        ph: Health = self.em.get_component(self.player_id, Health)
        ph.current = ph.maximum
        self.health_bar.set_value(ph.current)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        for slot in list(inv.slots.keys()):
            item_id, count = inv.slots[slot]
            if count > 1:
                inv.slots[slot] = (item_id, max(1, count // 2))
            else:
                del inv.slots[slot]
        self._notify("Respawned! You lost some items.")

    # -- Save / Load -----------------------------------------------------------
    def _save_game(self, filepath: str = SAVE_FILE) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        ph: Health = self.em.get_component(self.player_id, Health)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        equip: Equipment = self.em.get_component(self.player_id, Equipment)
        inv_data = {str(s): [iid, c] for s, (iid, c) in inv.slots.items()}
        data = {
            'seed': self.seed,
            'px': pt.x, 'py': pt.y,
            'hp': ph.current, 'max_hp': ph.maximum,
            'level': ps.level, 'xp': ps.xp, 'kills': ps.kills,
            'xp_to_next': ps.xp_to_next,
            'stat_points': ps.stat_points,
            'str_bonus': ps.str_bonus, 'def_bonus': ps.def_bonus, 'agi_bonus': ps.agi_bonus,
            'inventory': inv_data, 'equipped': inv.equipped_slot,
            'equipment': equip.slots,
            'day_time': self.daynight.time,
        }
        save_game(filepath, data)
        self._notify("Game Saved!")

    def _load_game(self, filepath: str = SAVE_FILE) -> None:
        data = load_game(filepath)
        if not data:
            self._notify("No save file found!")
            return
        pt: Transform = self.em.get_component(self.player_id, Transform)
        ph: Health = self.em.get_component(self.player_id, Health)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        equip: Equipment = self.em.get_component(self.player_id, Equipment)
        pt.x = data['px']; pt.y = data['py']
        ph.current = data['hp']; ph.maximum = data['max_hp']
        ps.level = data['level']; ps.xp = data['xp']
        ps.kills = data['kills']; ps.xp_to_next = data['xp_to_next']
        ps.stat_points = data.get('stat_points', 0)
        ps.str_bonus = data.get('str_bonus', 0)
        ps.def_bonus = data.get('def_bonus', 0)
        ps.agi_bonus = data.get('agi_bonus', 0)
        inv.slots.clear()
        for s_str, (iid, c) in data['inventory'].items():
            inv.slots[int(s_str)] = (iid, c)
        inv.equipped_slot = data.get('equipped', 0)
        if 'equipment' in data:
            for slot, item_id in data['equipment'].items():
                equip.slots[slot] = item_id
        self.daynight.time = data.get('day_time', 0.3)
        self.health_bar.max_value = ph.maximum
        self.health_bar.set_value(ph.current)
        self.xp_bar.max_value = ps.xp_to_next
        self.xp_bar.set_value(ps.xp)
        self.dead = False
        self._notify("Game Loaded!")

    # -- Pause Menu -------------------------------------------------------------
    def _get_pause_buttons(self) -> List[Tuple[pygame.Rect, str]]:
        bw, bh, gap = 220, 38, 6
        cx = SCREEN_WIDTH // 2
        start_y = SCREEN_HEIGHT // 2 - 140
        labels = ['Resume', 'Save Slot 1', 'Save Slot 2', 'Save Slot 3',
                  'Load Slot 1', 'Load Slot 2', 'Load Slot 3', 'Quit Game']
        buttons: List[Tuple[pygame.Rect, str]] = []
        for i, label in enumerate(labels):
            r = pygame.Rect(cx - bw // 2, start_y + i * (bh + gap), bw, bh)
            buttons.append((r, label))
        return buttons

    def _handle_pause_click(self, pos: Tuple[int, int]) -> None:
        for rect, label in self._get_pause_buttons():
            if rect.collidepoint(pos):
                if label == 'Resume':
                    self.paused = False
                elif label.startswith('Save Slot'):
                    idx = int(label[-1]) - 1
                    self._save_game(SAVE_SLOTS[idx])
                elif label.startswith('Load Slot'):
                    idx = int(label[-1]) - 1
                    self._load_game(SAVE_SLOTS[idx])
                    self.paused = False
                elif label == 'Quit Game':
                    self.running = False
                break

    def _draw_pause_menu(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        title = self.font.render('PAUSED', True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2,
                                 SCREEN_HEIGHT // 2 - 180))
        mx, my = pygame.mouse.get_pos()
        for rect, label in self._get_pause_buttons():
            hovered = rect.collidepoint(mx, my)
            color = (80, 80, 120) if hovered else (50, 50, 80)
            border_color = (140, 140, 200) if hovered else (100, 100, 150)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, border_color, rect, 2, border_radius=6)
            txt = self.font_sm.render(label, True, (230, 230, 255))
            self.screen.blit(txt, (rect.centerx - txt.get_width() // 2,
                                   rect.centery - txt.get_height() // 2))
        hint = self.font_sm.render('F5 = Quick Save   F9 = Quick Load', True, (160, 160, 180))
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                SCREEN_HEIGHT // 2 + 200))

    # -- Render ----------------------------------------------------------------
    def _render(self) -> None:
        self.screen.fill(BLACK)
        self.tooltip.clear()
        self._draw_world()
        self.renderer.update(self.em, self.camera)
        self._draw_mob_health_bars()
        if self.attack_anim > 0:
            self._draw_attack_arc()
        self.particles.draw(self.screen, self.camera.x, self.camera.y)
        self._draw_damage_numbers()
        self._draw_lighting()
        if self.damage_flash > 0:
            fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fs.fill((255, 0, 0, int(80 * (self.damage_flash / 0.15))))
            self.screen.blit(fs, (0, 0))
        self._draw_hud()
        self._draw_hotbar()
        pt: Transform = self.em.get_component(self.player_id, Transform)
        self.minimap.draw(self.screen, pt.x, pt.y)
        if self.show_inventory:
            self.inventory_ui.draw(self.screen, self.tooltip)
        if self.show_crafting:
            self._draw_crafting()
        if self.show_character:
            self._draw_character_menu()
        if self.notification_timer > 0:
            alpha = min(1.0, self.notification_timer / 0.5)
            ns = self.font.render(self.notification, True,
                                  (220, 220, 240, int(255 * alpha)))
            self.screen.blit(ns, (SCREEN_WIDTH // 2 - ns.get_width() // 2,
                                  SCREEN_HEIGHT // 2 + 120))
        self.tooltip.draw(self.screen)
        if self.paused:
            self._draw_pause_menu()
        if self.dead:
            self._draw_death_screen()
        pygame.display.flip()

    def _draw_world(self) -> None:
        sx_start = max(0, int(self.camera.x // TILE_SIZE) - 1)
        sx_end = min(self.world.width, int((self.camera.x + SCREEN_WIDTH) // TILE_SIZE) + 2)
        sy_start = max(0, int(self.camera.y // TILE_SIZE) - 1)
        sy_end = min(self.world.height, int((self.camera.y + SCREEN_HEIGHT) // TILE_SIZE) + 2)
        tile_surfs = {
            TILE_WATER: self.textures.get('water_0'),
            TILE_SAND: self.textures.get('sand'),
            TILE_GRASS: self.textures.get('grass'),
            TILE_DIRT: self.textures.get('dirt'),
            TILE_STONE_FLOOR: self.textures.get('stone'),
            TILE_STONE_WALL: self.textures.get('stone'),
        }
        default_surf = self.textures.get('grass')
        for x in range(sx_start, sx_end):
            for y in range(sy_start, sy_end):
                tile = self.world.get_tile(x, y)
                scx = int(x * TILE_SIZE - self.camera.x)
                scy = int(y * TILE_SIZE - self.camera.y)
                self.screen.blit(tile_surfs.get(tile, default_surf), (scx, scy))
                if tile == TILE_STONE_WALL:
                    pygame.draw.rect(self.screen, (50, 50, 60), (scx, scy, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, (30, 30, 40), (scx, scy, TILE_SIZE, TILE_SIZE), 2)

    def _draw_lighting(self) -> None:
        darkness = self.daynight.get_darkness()
        lights = self.em.get_entities_with(Transform, LightSource)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        has_torch = inv.get_equipped() == 'torch' and inv.has('torch')
        if darkness < 0.05 and not lights and not has_torch:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        base_alpha = int(darkness * 210)
        overlay.fill((5, 5, 20, base_alpha))

        def punch_light(sx: int, sy: int, radius: int, color: Tuple[int, int, int]) -> None:
            for r in range(radius, 15, -18):
                ts = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                a = int(30 * (r / radius))
                pygame.draw.circle(ts, (color[0], color[1], color[2], max(1, a)), (r, r), r)
                overlay.blit(ts, (sx - r, sy - r), special_flags=pygame.BLEND_RGBA_SUB)

        for eid in lights:
            t: Transform = self.em.get_component(eid, Transform)
            ls: LightSource = self.em.get_component(eid, LightSource)
            lx = int(t.x - self.camera.x + 12)
            ly = int(t.y - self.camera.y + 12)
            punch_light(lx, ly, ls.radius, ls.color)

        if has_torch:
            pt: Transform = self.em.get_component(self.player_id, Transform)
            lx = int(pt.x - self.camera.x + 10)
            ly = int(pt.y - self.camera.y + 14)
            punch_light(lx, ly, 110, (255, 180, 60))

        self.screen.blit(overlay, (0, 0))

    def _draw_mob_health_bars(self) -> None:
        for eid in self.em.get_entities_with(Transform, Health, AI):
            t: Transform = self.em.get_component(eid, Transform)
            h: Health = self.em.get_component(eid, Health)
            if h.current >= h.maximum:
                continue
            sx = int(t.x - self.camera.x)
            sy = int(t.y - self.camera.y - 8)
            pygame.draw.rect(self.screen, (40, 10, 10), (sx, sy, 28, 4))
            fill = int(28 * h.current / h.maximum)
            pygame.draw.rect(self.screen, (220, 40, 40), (sx, sy, fill, 4))
        # Placeable health bars
        for eid in self.em.get_entities_with(Transform, Health, Placeable):
            t2: Transform = self.em.get_component(eid, Transform)
            h2: Health = self.em.get_component(eid, Health)
            if h2.current >= h2.maximum:
                continue
            sx = int(t2.x - self.camera.x)
            sy = int(t2.y - self.camera.y - 8)
            pygame.draw.rect(self.screen, (10, 10, 40), (sx, sy, 28, 4))
            fill = int(28 * h2.current / h2.maximum)
            pygame.draw.rect(self.screen, (80, 80, 220), (sx, sy, fill, 4))

    def _draw_attack_arc(self) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pr: Renderable = self.em.get_component(self.player_id, Renderable)
        cx = int(pt.x - self.camera.x + 10)
        cy = int(pt.y - self.camera.y + 14)
        d = -1 if pr.flip_x else 1
        ax = cx + d * 20
        alpha = int(200 * (self.attack_anim / 0.18))
        arc = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.arc(arc, (255, 255, 200, alpha), pygame.Rect(0, 0, 40, 40),
                        -0.8 if d > 0 else 2.3, 0.8 if d > 0 else 3.9, 3)
        self.screen.blit(arc, (ax - 20, cy - 20))

    def _draw_damage_numbers(self) -> None:
        for x, y, txt, color, ttl in self.dmg_numbers:
            sx = int(x - self.camera.x)
            sy = int(y - self.camera.y)
            bold = txt.startswith('+') or txt.startswith('LEVEL') or txt == 'YOU DIED'
            f = self.font_lg if bold else self.font
            surf = f.render(txt, True, color)
            self.screen.blit(surf, (sx - surf.get_width() // 2, sy))

    def _draw_hotbar(self) -> None:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        slots = 6
        ss = 48
        gap = 6
        tw = slots * ss + (slots - 1) * gap
        bx = SCREEN_WIDTH // 2 - tw // 2
        by = SCREEN_HEIGHT - ss - 14
        mx, my = pygame.mouse.get_pos()
        for i in range(slots):
            x = bx + i * (ss + gap)
            rect = pygame.Rect(x, by, ss, ss)
            sel = i == inv.equipped_slot
            bg = (80, 80, 115) if sel else (30, 30, 48)
            pygame.draw.rect(self.screen, bg, rect, border_radius=5)
            bd = (200, 200, 240) if sel else (90, 90, 110)
            pygame.draw.rect(self.screen, bd, rect, 2, border_radius=5)
            ns = self.font_sm.render(str(i + 1), True, (170, 170, 190))
            self.screen.blit(ns, (x + 3, by + 2))
            if i in inv.slots:
                item_id, count = inv.slots[i]
                icon = self.textures.cache.get(f'item_{item_id}')
                if icon:
                    self.screen.blit(pygame.transform.scale(icon, (32, 32)), (x + 8, by + 8))
                if count > 1:
                    cs = self.font_sm.render(str(count), True, WHITE)
                    self.screen.blit(cs, (x + ss - cs.get_width() - 3, by + ss - cs.get_height() - 2))
                if rect.collidepoint(mx, my) and item_id in ITEM_DATA:
                    d = ITEM_DATA[item_id]
                    self.tooltip.show([d['name'], d['desc']], (mx, my))
        eq = inv.get_equipped()
        if eq and eq in ITEM_DATA:
            nt = self.font.render(ITEM_DATA[eq]['name'], True, (220, 220, 240))
            self.screen.blit(nt, (SCREEN_WIDTH // 2 - nt.get_width() // 2, by - 22))

    def _draw_hud(self) -> None:
        # Health
        self.health_bar.draw(self.screen)
        ph: Health = self.em.get_component(self.player_id, Health)
        ht = self.font_sm.render(f"HP {ph.current}/{ph.maximum}", True, WHITE)
        self.screen.blit(ht, (24, 17))

        # Level / XP
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        self.xp_bar.draw(self.screen)
        xt = self.font_sm.render(f"Lv.{ps.level}  XP {ps.xp}/{ps.xp_to_next}", True, (180, 210, 255))
        self.screen.blit(xt, (24, 39))

        # Resources
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        res = f"Wood:{inv.count('wood')}  Stone:{inv.count('stone')}  Kills:{ps.kills}"
        self.screen.blit(self.font_sm.render(res, True, (200, 200, 210)), (20, 58))

        # Period
        period = self.daynight.get_period_name()
        period_colors = {'Day': (255, 255, 200), 'Dawn': (255, 200, 140),
                         'Dusk': (200, 140, 180), 'Night': (140, 140, 220)}
        pc = period_colors.get(period, WHITE)
        self.screen.blit(self.font.render(period, True, pc), (SCREEN_WIDTH - 155, 16))
        t_str = f"{int(self.daynight.time * 24):02d}:{int((self.daynight.time * 1440) % 60):02d}"
        self.screen.blit(self.font_sm.render(t_str, True, GRAY), (SCREEN_WIDTH - 155, 36))

        # Darkness warning
        if 0.2 < self.daynight.get_darkness() < 0.55:
            wt = self.font.render("Night approaches... find light!", True, (255, 200, 80))
            self.screen.blit(wt, (SCREEN_WIDTH // 2 - wt.get_width() // 2, 70))

        # Edge warning
        pt: Transform = self.em.get_component(self.player_id, Transform)
        tx, ty = pt.x / TILE_SIZE, pt.y / TILE_SIZE
        if tx < 4 or tx > WORLD_WIDTH - 4 or ty < 4 or ty > WORLD_HEIGHT - 4:
            et = self.font.render("~ Edge of the World ~", True, (170, 170, 200))
            self.screen.blit(et, (SCREEN_WIDTH // 2 - et.get_width() // 2, 94))

        # Controls
        ctrl = "WASD:Move  Space:Attack  E:Harvest  F:Use  I:Inv  C:Craft  P:Character  ESC:Pause"
        self.screen.blit(self.font_sm.render(ctrl, True, (140, 140, 160)), (20, SCREEN_HEIGHT - 82))

    # -- Character Menu --------------------------------------------------------
    def _get_char_panel_rect(self) -> pygame.Rect:
        pw, pht = 360, 420
        return pygame.Rect(SCREEN_WIDTH // 2 - pw // 2, SCREEN_HEIGHT // 2 - pht // 2, pw, pht)

    def _handle_character_click(self, pos: Tuple[int, int]) -> None:
        panel = self._get_char_panel_rect()
        if not panel.collidepoint(pos):
            return
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        eq: Equipment = self.em.get_component(self.player_id, Equipment)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)

        # Stat allocation buttons
        stat_y_base = panel.y + 60
        btn_w, btn_h = 22, 18
        stats = [('str_bonus', 'STR'), ('def_bonus', 'DEF'), ('agi_bonus', 'AGI')]
        for si, (attr, _label) in enumerate(stats):
            btn_rect = pygame.Rect(panel.x + 200, stat_y_base + si * 26, btn_w, btn_h)
            if btn_rect.collidepoint(pos) and ps.stat_points > 0:
                setattr(ps, attr, getattr(ps, attr) + 1)
                ps.stat_points -= 1
                return

        # Equipment slot clicks - toggle equip/unequip
        eq_y_base = panel.y + 170
        for si, slot_name in enumerate(Equipment.SLOTS):
            slot_rect = pygame.Rect(panel.x + 20, eq_y_base + si * 40, panel.width - 40, 34)
            if slot_rect.collidepoint(pos):
                current = eq.get(slot_name)
                if current:
                    # Unequip back to inventory
                    inv.add_item(current, 1)
                    eq.unequip(slot_name)
                    self._notify(f"Unequipped {ITEM_DATA[current]['name']}")
                else:
                    # Find first compatible item in inventory
                    cats = Equipment.SLOT_CATEGORIES.get(slot_name, [])
                    for _s, (iid, _c) in inv.slots.items():
                        if iid in ITEM_DATA and ITEM_DATA[iid]['category'] in cats:
                            inv.remove_item(iid, 1)
                            eq.equip(slot_name, iid)
                            self._notify(f"Equipped {ITEM_DATA[iid]['name']}")
                            break
                return

    def _draw_character_menu(self) -> None:
        panel = self._get_char_panel_rect()
        bg = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        bg.fill((18, 18, 28, 235))
        self.screen.blit(bg, panel.topleft)
        pygame.draw.rect(self.screen, (130, 130, 155), panel, 2, border_radius=10)
        title = self.font_lg.render("Character", True, WHITE)
        self.screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 10))

        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        ph: Health = self.em.get_component(self.player_id, Health)
        eq: Equipment = self.em.get_component(self.player_id, Equipment)
        lx = panel.x + 20
        sy = panel.y + 44
        self.screen.blit(self.font.render(f"Level {ps.level}   HP {ph.current}/{ph.maximum}", True, WHITE), (lx, sy))

        stat_y = panel.y + 60
        stats = [('str_bonus', 'STR'), ('def_bonus', 'DEF'), ('agi_bonus', 'AGI')]
        for si, (attr, label) in enumerate(stats):
            y = stat_y + si * 26
            val = getattr(ps, attr)
            txt = self.font.render(f"{label}: {val}", True, (200, 200, 220))
            self.screen.blit(txt, (lx, y))
            if ps.stat_points > 0:
                btn = pygame.Rect(panel.x + 200, y, 22, 18)
                pygame.draw.rect(self.screen, (60, 100, 60), btn, border_radius=3)
                pygame.draw.rect(self.screen, (100, 180, 100), btn, 1, border_radius=3)
                pt = self.font_sm.render("+", True, WHITE)
                self.screen.blit(pt, (btn.x + 6, btn.y + 1))
        if ps.stat_points > 0:
            sp_txt = self.font_sm.render(f"Points: {ps.stat_points}", True, YELLOW)
            self.screen.blit(sp_txt, (panel.x + 240, stat_y))

        # Defense total
        total_def = eq.get_total_defense() + ps.def_bonus
        self.screen.blit(self.font_sm.render(f"Total Defense: {total_def}  |  Kills: {ps.kills}", True, GRAY), (lx, panel.y + 145))

        # Equipment slots
        eq_y = panel.y + 170
        self.screen.blit(self.font.render("Equipment  (click to equip/unequip)", True, (180, 180, 200)), (lx, eq_y - 20))
        mx, my = pygame.mouse.get_pos()
        for si, slot_name in enumerate(Equipment.SLOTS):
            y = eq_y + si * 40
            slot_rect = pygame.Rect(lx, y, panel.width - 40, 34)
            hov = slot_rect.collidepoint(mx, my)
            bg_c = (40, 40, 60) if not hov else (55, 55, 80)
            pygame.draw.rect(self.screen, bg_c, slot_rect, border_radius=4)
            pygame.draw.rect(self.screen, (100, 100, 130), slot_rect, 1, border_radius=4)
            label = slot_name.capitalize()
            item_id = eq.get(slot_name)
            if item_id and item_id in ITEM_DATA:
                icon = self.textures.cache.get(f"item_{item_id}")
                if icon:
                    self.screen.blit(pygame.transform.scale(icon, (24, 24)), (lx + 4, y + 5))
                name_txt = f"{label}: {ITEM_DATA[item_id]['name']}"
                self.screen.blit(self.font.render(name_txt, True, (200, 220, 200)), (lx + 32, y + 8))
            else:
                self.screen.blit(self.font.render(f"{label}: (empty)", True, (120, 120, 140)), (lx + 8, y + 8))

    def _draw_crafting(self) -> None:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        max_vis = 8
        vis_count = min(len(RECIPES), max_vis)
        pw, pht = 400, 55 + vis_count * 52
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - pht // 2
        bg = pygame.Surface((pw, pht), pygame.SRCALPHA)
        bg.fill((18, 18, 28, 235))
        self.screen.blit(bg, (px, py))
        pygame.draw.rect(self.screen, (130, 130, 155), (px, py, pw, pht), 2, border_radius=10)
        title = self.font_lg.render("Crafting", True, WHITE)
        self.screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 10))
        mx, my = pygame.mouse.get_pos()
        max_scroll = max(0, len(RECIPES) - max_vis)
        self.craft_scroll = max(0, min(self.craft_scroll, max_scroll))
        for vi in range(vis_count):
            i = vi + self.craft_scroll
            if i >= len(RECIPES):
                break
            recipe = RECIPES[i]
            ry = py + 44 + vi * 52
            can = all(inv.has(it, co) for it, co in recipe['cost'].items())
            btn = pygame.Rect(px + 10, ry, pw - 20, 44)
            hov = btn.collidepoint(mx, my)
            if can:
                bc = (60, 90, 60) if not hov else (80, 120, 80)
                bd = (100, 180, 100)
            else:
                bc = (55, 35, 35) if not hov else (75, 50, 50)
                bd = (140, 60, 60)
            pygame.draw.rect(self.screen, bc, btn, border_radius=5)
            pygame.draw.rect(self.screen, bd, btn, 1, border_radius=5)
            icon = self.textures.cache.get(f"item_{recipe['gives']}")
            if icon:
                self.screen.blit(pygame.transform.scale(icon, (28, 28)), (btn.x + 6, ry + 8))
            self.screen.blit(self.font.render(recipe['name'], True, WHITE), (btn.x + 40, ry + 4))
            cx_pos = btn.x + 40
            for item, cost in recipe['cost'].items():
                has_e = inv.has(item, cost)
                c_color = GREEN if has_e else RED
                ct = self.font_sm.render(f"{cost}x{ITEM_DATA[item]['name']}", True, c_color)
                self.screen.blit(ct, (cx_pos, ry + 24))
                cx_pos += ct.get_width() + 14
            if hov:
                gives = recipe['gives']
                if gives in ITEM_DATA:
                    d = ITEM_DATA[gives]
                    self.tooltip.show([d['name'], d['desc']], (mx, my))
        if len(RECIPES) > max_vis:
            sc_txt = self.font_sm.render(f"Scroll: {self.craft_scroll + 1}-{min(self.craft_scroll + max_vis, len(RECIPES))} / {len(RECIPES)}", True, GRAY)
            self.screen.blit(sc_txt, (px + pw // 2 - sc_txt.get_width() // 2, py + pht - 18))

    def _draw_death_screen(self) -> None:
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        dt = self.font_xl.render("YOU DIED", True, RED)
        self.screen.blit(dt, (SCREEN_WIDTH // 2 - dt.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        ht = self.font.render("Press [R] to Respawn  |  [Q] to Quit", True, GRAY)
        self.screen.blit(ht, (SCREEN_WIDTH // 2 - ht.get_width() // 2, SCREEN_HEIGHT // 2))
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        st = self.font.render(f"Level {ps.level}  |  {ps.kills} Kills", True, WHITE)
        self.screen.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

# =============================================================================
if __name__ == "__main__":
    Game().run()
