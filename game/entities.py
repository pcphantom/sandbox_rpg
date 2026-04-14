"""Entity creation and lifecycle functions extracted from Game class.

All functions receive the Game instance as their first argument ``g``.
"""
from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING, List, Tuple

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from core.constants import (
    TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT,
    TILE_GRASS, TILE_DIRT, TILE_STONE_FLOOR, TILE_FOREST,
    TILE_CAVE_FLOOR, TILE_CAVE_ENTRANCE,
    GRAY, CYAN, YELLOW, ORANGE, GREEN,
    PER_DAY_SCALE_FACTOR, MOB_SPAWN_ATTEMPTS,
    GHOST_SPAWN_CHANCE, NIGHT_MOB_SPAWN_CHANCE, DARK_KNIGHT_SPAWN_CHANCE,
    FOREST_MOB_SPAWN_CHANCE, DIRT_MOB_SPAWN_CHANCE, ORC_SPAWN_CHANCE,
    GRASS_MOB_SPAWN_CHANCE, WAVE_SPAWN_RADIUS_VARIANCE,
    WAVE_RANGED_MOB_CHANCE,
    TREE_COUNT, FOREST_TREE_COUNT, ROCK_COUNT,
    STARTING_WOOD, STARTING_STONE,
    PLAYER_COLLIDER_W, PLAYER_COLLIDER_H, PLAYER_FRICTION,
    WAVE_SPAWN_RADIUS, INITIAL_MOB_SPAWNS,
    LEVEL_UP_BASE_HP, VIT_HP_BONUS_PER_LEVEL,
    MOB_RESPAWN_MIN_DIST,
    CAVE_MOB_TYPES, CAVE_MOB_COUNT, CAVE_BOSS_TYPES,
    CAVE_ORE_COUNT, CAVE_DIAMOND_COUNT,
    CAVE_HP_MULT, CAVE_DMG_MULT,
    CHEST_CAPACITY,
)
from core.utils import clamp
from core.components import (
    Transform, Velocity, Renderable, Collider, Health, Inventory,
    AI, PlayerStats, Equipment, Placeable, Storage, Building, Turret,
)
from data import (
    ITEM_DATA, MOB_DATA, WAVE_MOB_TIERS, WAVE_RANGED_MOBS, WAVE_BOSS_MOBS,
)
from drops import LOOT_TABLES, CAVE_CHEST_LOOT, roll_loot, pick_weighted, maybe_enhance
from world.generator import WorldGenerator
from game_controller import (
    MOB_COLOR_SLIME, MOB_COLOR_SKELETON, MOB_COLOR_WOLF, MOB_COLOR_GOBLIN,
    MOB_COLOR_GHOST, MOB_COLOR_SPIDER, MOB_COLOR_ORC, MOB_COLOR_DARK_KNIGHT,
    MOB_COLOR_ZOMBIE, MOB_COLOR_WRAITH, MOB_COLOR_TROLL,
    MOB_COLOR_SKELETON_ARCHER, MOB_COLOR_GOBLIN_SHAMAN,
    MOB_COLOR_BOSS_GOLEM, MOB_COLOR_BOSS_LICH, BOSS_GLOW_DEFAULT,
)


# ======================================================================
# PLAYER
# ======================================================================

def create_player(g: 'Game') -> int:
    eid = g.em.create_entity()
    sx, sy = WorldGenerator.find_spawn(g.world)
    g.em.add_component(eid, Transform(sx, sy))
    g.em.add_component(eid, Velocity(0, 0, PLAYER_FRICTION))
    g.em.add_component(eid, Renderable(g.textures.get('player'), layer=5))
    g.em.add_component(eid, Collider(PLAYER_COLLIDER_W, PLAYER_COLLIDER_H, True))
    g.em.add_component(eid, Health(100))
    g.em.add_component(eid, Inventory())
    g.em.add_component(eid, PlayerStats())
    g.em.add_component(eid, Equipment())
    inv: Inventory = g.em.get_component(eid, Inventory)
    eq: Equipment = g.em.get_component(eid, Equipment)
    inv._equipment_ref = eq
    inv.add_item('wood', STARTING_WOOD)
    inv.add_item('stone', STARTING_STONE)
    return eid


# ======================================================================
# MOBS
# ======================================================================

def create_mob(g: 'Game', x: float, y: float, mob_type: str) -> int:
    data = MOB_DATA[mob_type]
    tex_key = mob_type
    eid = g.em.create_entity()
    g.em.add_component(eid, Transform(x, y))
    g.em.add_component(eid, Velocity(
        random.uniform(-20, 20), random.uniform(-20, 20), 0.9))
    g.em.add_component(eid, Renderable(g.textures.get(tex_key), layer=3))
    surf = g.textures.get(tex_key)
    g.em.add_component(eid, Collider(
        surf.get_width(), surf.get_height(), data['solid']))
    from data.difficulty import get_profile
    prof = get_profile(g.difficulty)
    hp_mult = prof['enemy_hp_mult']
    dmg_mult = prof['enemy_dmg_mult']
    days_elapsed = max(0, g.daynight.day_number - 1)
    hp_day_scale = 1.0 + days_elapsed * prof['enemy_hp_per_day']
    dmg_day_scale = 1.0 + days_elapsed * prof['enemy_dmg_per_day']
    scaled_hp = int(data['hp'] * hp_mult * hp_day_scale)
    scaled_dmg = int(data['damage'] * dmg_mult * dmg_day_scale)
    g.em.add_component(eid, Health(scaled_hp))
    mob_ai = AI('wander', mob_type)
    mob_ai.speed = data['speed']
    mob_ai.detection_range = data['detection']
    mob_ai.contact_damage = scaled_dmg
    mob_ai.xp_value = data['xp']
    if data.get('ranged', False):
        mob_ai.is_ranged = True
        mob_ai.ranged_damage = int(
            data.get('ranged_damage', 10) * dmg_mult * dmg_day_scale)
        mob_ai.ranged_range = data.get('ranged_range', 200.0)
        mob_ai.ranged_cooldown = data.get('ranged_cooldown', 2.0)
        mob_ai.ranged_speed = data.get('ranged_speed', 350.0)
    if data.get('boss', False):
        mob_ai.is_boss = True
        mob_ai.glow_color = data.get('glow_color', BOSS_GLOW_DEFAULT)
        # Boss-specific scaling (stacks with enemy multipliers)
        boss_hp_day = 1.0 + days_elapsed * prof['boss_hp_per_day']
        boss_dmg_day = 1.0 + days_elapsed * prof['boss_dmg_per_day']
        boss_hp_m = prof['boss_hp_mult'] * boss_hp_day
        boss_dmg_m = prof['boss_dmg_mult'] * boss_dmg_day
        h = g.em.get_component(eid, Health)
        h.maximum = int(h.maximum * boss_hp_m)
        h.current = h.maximum
        mob_ai.contact_damage = int(mob_ai.contact_damage * boss_dmg_m)
        if mob_ai.is_ranged:
            mob_ai.ranged_damage = int(mob_ai.ranged_damage * boss_dmg_m)
    g.em.add_component(eid, mob_ai)
    return eid


# ======================================================================
# WORLD POPULATION
# ======================================================================

def populate_world(g: 'Game') -> None:
    rng = random.Random(g.seed + 12345)
    harvested = g.harvested_resources
    for _ in range(TREE_COUNT):
        x = rng.randint(5, WORLD_WIDTH - 5)
        y = rng.randint(5, WORLD_HEIGHT - 5)
        if (x, y) in harvested:
            continue
        tile = g.world.get_tile(x, y)
        if tile in (TILE_GRASS, TILE_FOREST):
            eid = g.em.create_entity()
            g.em.add_component(eid, Transform(
                x * TILE_SIZE + 8, y * TILE_SIZE - 16))
            g.em.add_component(eid, Renderable(
                g.textures.get('tree'), layer=2))
            g.em.add_component(eid, Collider(24, 32, True))
    for _ in range(FOREST_TREE_COUNT):
        x = rng.randint(5, WORLD_WIDTH - 5)
        y = rng.randint(5, WORLD_HEIGHT - 5)
        if (x, y) in harvested:
            continue
        if g.world.get_tile(x, y) == TILE_FOREST:
            eid = g.em.create_entity()
            g.em.add_component(eid, Transform(
                x * TILE_SIZE + 8, y * TILE_SIZE - 16))
            g.em.add_component(eid, Renderable(
                g.textures.get('tree'), layer=2))
            g.em.add_component(eid, Collider(24, 32, True))
    for _ in range(ROCK_COUNT):
        x = rng.randint(5, WORLD_WIDTH - 5)
        y = rng.randint(5, WORLD_HEIGHT - 5)
        if (x, y) in harvested:
            continue
        if g.world.get_tile(x, y) in (TILE_GRASS, TILE_DIRT,
                                       TILE_STONE_FLOOR, TILE_FOREST):
            eid = g.em.create_entity()
            g.em.add_component(eid, Transform(
                x * TILE_SIZE + 4, y * TILE_SIZE + 6))
            g.em.add_component(eid, Renderable(
                g.textures.get('rock'), layer=1))
            g.em.add_component(eid, Collider(26, 18, True))
    for mob_type, biome, count in INITIAL_MOB_SPAWNS:
        for _ in range(count):
            x = rng.randint(5, WORLD_WIDTH - 5)
            y = rng.randint(5, WORLD_HEIGHT - 5)
            tile = g.world.get_tile(x, y)
            if tile == biome or (biome == TILE_GRASS and tile == TILE_FOREST):
                create_mob(g, x * TILE_SIZE + 8, y * TILE_SIZE + 8, mob_type)


def spawn_mob(g: 'Game') -> None:
    pt: Transform = g.em.get_component(g.player_id, Transform)
    for _ in range(MOB_SPAWN_ATTEMPTS):
        x = random.randint(5, WORLD_WIDTH - 5)
        y = random.randint(5, WORLD_HEIGHT - 5)
        wx, wy = x * TILE_SIZE, y * TILE_SIZE
        if math.hypot(wx - pt.x, wy - pt.y) < MOB_RESPAWN_MIN_DIST:
            continue
        if g.world.is_solid(x, y):
            continue
        tile = g.world.get_tile(x, y)
        is_night = g.daynight.is_night()
        if is_night and random.random() < GHOST_SPAWN_CHANCE:
            mob = 'ghost'
        elif is_night and random.random() < NIGHT_MOB_SPAWN_CHANCE:
            mob = ('dark_knight' if random.random() < DARK_KNIGHT_SPAWN_CHANCE
                   else 'skeleton')
        elif tile == TILE_FOREST and random.random() < FOREST_MOB_SPAWN_CHANCE:
            mob = random.choice(['wolf', 'spider'])
        elif (tile in (TILE_DIRT, TILE_STONE_FLOOR)
              and random.random() < DIRT_MOB_SPAWN_CHANCE):
            mob = 'orc' if random.random() < ORC_SPAWN_CHANCE else 'goblin'
        elif tile == TILE_GRASS and random.random() < GRASS_MOB_SPAWN_CHANCE:
            mob = 'wolf'
        else:
            mob = 'slime'
        create_mob(g, wx, wy, mob)
        return


def spawn_wave_mobs(g: 'Game', count: int, tier: int,
                    include_ranged: bool = False,
                    include_boss: bool = False) -> None:
    pt: Transform = g.em.get_component(g.player_id, Transform)
    target_x, target_y = pt.x, pt.y
    buildings = g.em.get_entities_with(Transform, Building)
    if buildings:
        b_eid = random.choice(buildings)
        bt = g.em.get_component(b_eid, Transform)
        target_x, target_y = bt.x, bt.y

    available: list[str] = []
    for t in range(min(tier + 1, len(WAVE_MOB_TIERS))):
        available.extend(WAVE_MOB_TIERS[t])

    for i in range(count):
        angle = random.uniform(0, math.tau)
        dist = WAVE_SPAWN_RADIUS + random.uniform(
            0, WAVE_SPAWN_RADIUS_VARIANCE)
        wx = target_x + math.cos(angle) * dist
        wy = target_y + math.sin(angle) * dist
        wx = clamp(wx, TILE_SIZE * 2, (WORLD_WIDTH - 2) * TILE_SIZE)
        wy = clamp(wy, TILE_SIZE * 2, (WORLD_HEIGHT - 2) * TILE_SIZE)

        if include_boss and i == 0:
            mob_type = random.choice(WAVE_BOSS_MOBS)
        elif include_ranged and random.random() < WAVE_RANGED_MOB_CHANCE:
            mob_type = random.choice(WAVE_RANGED_MOBS)
        else:
            mob_type = random.choice(available)
        create_mob(g, wx, wy, mob_type)


# ======================================================================
# MOB KILLED / LEVEL UP
# ======================================================================

def on_mob_killed(g: 'Game', eid: int) -> None:
    td: Transform = g.em.get_component(eid, Transform)
    mob_ai: AI = g.em.get_component(eid, AI)
    pinv: Inventory = g.em.get_component(g.player_id, Inventory)

    # -- Use data-driven loot tables from drops/ package --
    table = LOOT_TABLES.get(mob_ai.mob_type)
    if table:
        from data.difficulty import get_profile
        luck = get_profile(g.difficulty)['loot_luck_bonus']
        drops = roll_loot(table, luck_bonus=luck)
        for item_id, amt, rar in drops:
            pinv.add_item_enchanted(item_id, None, amt, rar)
        if drops:
            has_notable = any(rar and rar != 'common' for _, _, rar in drops)
            if has_notable:
                g.dmg_numbers.append((td.x, td.y - 10, '+Loot', CYAN, 1.2))

    mob_colors = {
        'slime': MOB_COLOR_SLIME, 'skeleton': MOB_COLOR_SKELETON,
        'wolf': MOB_COLOR_WOLF, 'goblin': MOB_COLOR_GOBLIN,
        'ghost': MOB_COLOR_GHOST, 'spider': MOB_COLOR_SPIDER,
        'orc': MOB_COLOR_ORC, 'dark_knight': MOB_COLOR_DARK_KNIGHT,
        'zombie': MOB_COLOR_ZOMBIE, 'wraith': MOB_COLOR_WRAITH,
        'troll': MOB_COLOR_TROLL, 'skeleton_archer': MOB_COLOR_SKELETON_ARCHER,
        'goblin_shaman': MOB_COLOR_GOBLIN_SHAMAN,
        'boss_golem': MOB_COLOR_BOSS_GOLEM, 'boss_lich': MOB_COLOR_BOSS_LICH,
    }
    color = mob_colors.get(mob_ai.mob_type, GRAY)
    g.particles.emit(td.x + 12, td.y + 10, 15, color, 80, 0.5)

    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    ps.kills += 1
    from data.difficulty import get_profile
    xp_mult = get_profile(g.difficulty)['xp_mult']
    check_level_up(g, int(mob_ai.xp_value * xp_mult))

    if g.in_cave >= 0 and mob_ai.is_boss:
        g.caves.boss_alive[g.in_cave] = False
        g._notify("Cave boss defeated! Loot added to inventory!", 3.0)

    g.em.destroy_entity(eid)


def check_level_up(g: 'Game', xp: int) -> None:
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    if ps.add_xp(xp):
        ph: Health = g.em.get_component(g.player_id, Health)
        ph.maximum += LEVEL_UP_BASE_HP + ps.vitality * VIT_HP_BONUS_PER_LEVEL
        ph.current = ph.maximum
        g.health_bar.max_value = ph.maximum
        g.health_bar.set_value(ph.current)
        pt: Transform = g.em.get_component(g.player_id, Transform)
        g.dmg_numbers.append(
            (pt.x, pt.y - 30, f'LEVEL {ps.level}!', CYAN, 2.0))
        g.particles.emit(pt.x + 10, pt.y + 14, 25, YELLOW, 100, 0.8)
        g.particles.emit(pt.x + 10, pt.y + 14, 25, CYAN, 80, 0.6)
        g._notify(f"Level Up! Level {ps.level}  (+3 stat points)")


# ======================================================================
# CAVE POPULATION
# ======================================================================

def populate_cave(g: 'Game', cave_index: int) -> None:
    cave = g.caves.interiors[cave_index]
    rng = random.Random(g.seed + 60000 + cave_index * 1013)
    g.cave_entities.clear()

    floor_tiles: List[Tuple[int, int]] = []
    for x in range(2, cave.width - 2):
        for y in range(2, cave.height - 2):
            if cave.get_tile(x, y) == TILE_CAVE_FLOOR:
                floor_tiles.append((x, y))
    rng.shuffle(floor_tiles)
    tile_idx = 0

    for _ in range(CAVE_MOB_COUNT):
        if tile_idx >= len(floor_tiles):
            break
        tx, ty = floor_tiles[tile_idx]; tile_idx += 1
        mob_type = rng.choice(CAVE_MOB_TYPES)
        eid = create_cave_mob(
            g, tx * TILE_SIZE + TILE_SIZE // 2,
            ty * TILE_SIZE + TILE_SIZE // 2, mob_type)
        g.cave_entities.append(eid)

    if g.caves.boss_alive[cave_index]:
        bx, by = g.caves.get_boss_spawn(cave_index)
        boss_type = rng.choice(CAVE_BOSS_TYPES)
        boss_eid = create_cave_mob(g, bx, by, boss_type)
        g.cave_entities.append(boss_eid)

    for _ in range(CAVE_ORE_COUNT):
        if tile_idx >= len(floor_tiles):
            break
        tx, ty = floor_tiles[tile_idx]; tile_idx += 1
        eid = create_cave_resource(
            g, tx * TILE_SIZE + 4, ty * TILE_SIZE + 6,
            'ore_node', 'iron_ore')
        g.cave_entities.append(eid)

    for _ in range(CAVE_DIAMOND_COUNT):
        if tile_idx >= len(floor_tiles):
            break
        tx, ty = floor_tiles[tile_idx]; tile_idx += 1
        eid = create_cave_resource(
            g, tx * TILE_SIZE + 5, ty * TILE_SIZE + 7,
            'diamond_node', 'diamond')
        g.cave_entities.append(eid)

    # Cave chest always spawns (boss does NOT gate it); only skip if
    # already looted this cycle.
    if not g.caves.chest_looted[cave_index]:
        bx, by = g.caves.get_boss_spawn(cave_index)
        eid = create_cave_chest(g, bx + TILE_SIZE, by, cave_index, rng)
        g.cave_entities.append(eid)


def create_cave_mob(g: 'Game', x: float, y: float,
                    mob_type: str) -> int:
    eid = create_mob(g, x, y, mob_type)
    h = g.em.get_component(eid, Health)
    ai = g.em.get_component(eid, AI)
    if h:
        h.maximum = int(h.maximum * CAVE_HP_MULT)
        h.current = h.maximum
    if ai:
        ai.contact_damage = int(ai.contact_damage * CAVE_DMG_MULT)
        if ai.is_ranged:
            ai.ranged_damage = int(ai.ranged_damage * CAVE_DMG_MULT)
    return eid


def create_cave_resource(g: 'Game', x: float, y: float,
                         texture_key: str, drop_item: str) -> int:
    eid = g.em.create_entity()
    g.em.add_component(eid, Transform(x, y))
    surf = g.textures.get(texture_key)
    g.em.add_component(eid, Renderable(surf, layer=1))
    g.em.add_component(eid, Collider(
        surf.get_width(), surf.get_height(), True))
    g.em.add_component(eid, Health(30))
    pl = Placeable(texture_key, drop_item=drop_item)
    g.em.add_component(eid, pl)
    return eid


def create_cave_chest(g: 'Game', x: float, y: float,
                      cave_index: int, rng: random.Random) -> int:
    """Create a gold-coloured cave chest.  No Building component so AI
    ignores it — only player-placed structures get Building."""
    eid = g.em.create_entity()
    g.em.add_component(eid, Transform(x, y))
    g.em.add_component(eid, Renderable(
        g.textures.get('cave_chest_placed'), layer=1))
    g.em.add_component(eid, Collider(28, 24, True))
    g.em.add_component(eid, Health(200))
    stor = Storage(CHEST_CAPACITY)
    # -- Use data-driven cave chest loot from drops/ package --
    from systems.rarity import roll_rarity
    from core.item_stack import normalize_rarity
    slot_idx = 0
    # Guaranteed base items
    for item_id, lo, hi in CAVE_CHEST_LOOT['base']:
        amt = rng.randint(lo, hi)
        if amt > 0 and slot_idx < CHEST_CAPACITY:
            stor.slots[slot_idx] = (item_id, amt)
            rar = roll_rarity(item_id, True, rng)
            stor.slot_rarities[slot_idx] = normalize_rarity(rar)
            slot_idx += 1
    # Weighted pool rolls (equipment, spells, tomes, consumables)
    num_pool = rng.randint(
        CAVE_CHEST_LOOT['min_pool_rolls'],
        CAVE_CHEST_LOOT['max_pool_rolls'])
    pool_drops = pick_weighted(CAVE_CHEST_LOOT['pool'], num_pool, rng)
    # Enhancement roll: one random pool item may become +1..+5
    enhanced_chance = CAVE_CHEST_LOOT.get('enhanced_chance', 0.0)
    if enhanced_chance > 0 and pool_drops and rng.random() < enhanced_chance:
        idx = rng.randrange(len(pool_drops))
        iid, cnt = pool_drops[idx]
        enhanced = maybe_enhance(iid, rng)
        if enhanced != iid:
            pool_drops[idx] = (enhanced, cnt)
    for item_id, amt in pool_drops:
        if slot_idx < CHEST_CAPACITY:
            stor.slots[slot_idx] = (item_id, amt)
            rar = roll_rarity(item_id, True, rng)
            stor.slot_rarities[slot_idx] = normalize_rarity(rar)
            slot_idx += 1
    g.em.add_component(eid, stor)
    g.em.add_component(eid, Placeable('chest'))
    return eid


def snapshot_structures(g: 'Game') -> list:
    """Capture all player-placed structures as serialisable dicts."""
    from game.persistence import build_save_data
    # Re-use the same structure serialisation logic from persistence
    structs: list = []
    for eid in g.em.get_entities_with(Transform, Placeable, Building):
        if g.em.has_component(eid, AI):
            continue
        pl = g.em.get_component(eid, Placeable)
        t = g.em.get_component(eid, Transform)
        h = g.em.get_component(eid, Health)
        sd: dict = {
            'type': pl.item_type,
            'x': t.x, 'y': t.y,
            'hp': h.current if h else 0,
            'max_hp': h.maximum if h else 0,
            'rotation': pl.rotation,
        }
        stor = g.em.get_component(eid, Storage) if g.em.has_component(eid, Storage) else None
        if stor:
            sd['storage'] = {
                str(s): [iid, c]
                for s, (iid, c) in stor.slots.items()}
            if stor.slot_enchantments:
                sd['storage_enchants'] = {
                    str(s): e
                    for s, e in stor.slot_enchantments.items()}
            if stor.slot_rarities:
                sd['storage_rarities'] = {
                    str(s): r
                    for s, r in stor.slot_rarities.items()}
        turr = g.em.get_component(eid, Turret) if g.em.has_component(eid, Turret) else None
        if turr:
            sd['turret_damage'] = turr.damage
            if turr.enchant:
                sd['turret_enchant'] = turr.enchant
            if turr.rarity != 'common':
                sd['turret_rarity'] = turr.rarity
        structs.append(sd)
    return structs


def restore_structures(g: 'Game', structs: list) -> None:
    """Recreate structures from snapshot dicts."""
    from game.persistence import restore_structure
    for sd in structs:
        restore_structure(g, sd)


def snapshot_cave_entities(g: 'Game') -> list:
    """Capture all cave entity state for later restoration."""
    data = []
    for eid in g.cave_entities:
        if not g.em.has_component(eid, Transform):
            continue
        t = g.em.get_component(eid, Transform)
        entry: dict = {'x': t.x, 'y': t.y}
        if g.em.has_component(eid, AI):
            ai = g.em.get_component(eid, AI)
            h = g.em.get_component(eid, Health) if g.em.has_component(eid, Health) else None
            if h and not h.is_alive():
                continue  # Skip dead mobs
            entry['etype'] = 'mob'
            entry['mob_type'] = ai.mob_type
            entry['hp'] = h.current if h else 0
            entry['max_hp'] = h.maximum if h else 0
            entry['is_boss'] = ai.is_boss
        elif g.em.has_component(eid, Placeable):
            pl = g.em.get_component(eid, Placeable)
            h = g.em.get_component(eid, Health) if g.em.has_component(eid, Health) else None
            if g.em.has_component(eid, Storage):
                stor = g.em.get_component(eid, Storage)
                entry['etype'] = 'chest'
                entry['hp'] = h.current if h else 0
                entry['max_hp'] = h.maximum if h else 200
                entry['storage'] = {
                    str(s): [iid, c]
                    for s, (iid, c) in stor.slots.items()
                }
                entry['storage_rarities'] = {
                    str(s): r
                    for s, r in stor.slot_rarities.items()
                }
                if stor.slot_enchantments:
                    entry['storage_enchants'] = {
                        str(s): e
                        for s, e in stor.slot_enchantments.items()
                    }
            elif hasattr(pl, 'drop_item') and pl.drop_item:
                entry['etype'] = 'resource'
                entry['texture_key'] = pl.item_type
                entry['drop_item'] = pl.drop_item
                entry['hp'] = h.current if h else 0
            else:
                continue
        else:
            continue
        data.append(entry)
    return data


def restore_cave_snapshot(g: 'Game', cave_index: int,
                          snapshot: list) -> None:
    """Restore cave entities from a snapshot instead of repopulating."""
    g.cave_entities.clear()
    for entry in snapshot:
        etype = entry.get('etype', '')
        if etype == 'mob':
            hp = entry.get('hp', 0)
            if hp <= 0:
                continue  # Dead mob, skip
            eid = create_cave_mob(g, entry['x'], entry['y'],
                                  entry['mob_type'])
            h = g.em.get_component(eid, Health) if g.em.has_component(eid, Health) else None
            if h:
                h.maximum = entry.get('max_hp', h.maximum)
                h.current = min(hp, h.maximum)
            g.cave_entities.append(eid)
        elif etype == 'resource':
            eid = create_cave_resource(
                g, entry['x'], entry['y'],
                entry['texture_key'], entry['drop_item'])
            h = g.em.get_component(eid, Health) if g.em.has_component(eid, Health) else None
            if h:
                h.current = entry.get('hp', h.current)
            g.cave_entities.append(eid)
        elif etype == 'chest':
            eid = g.em.create_entity()
            g.em.add_component(eid, Transform(entry['x'], entry['y']))
            g.em.add_component(eid, Renderable(
                g.textures.get('cave_chest_placed'), layer=1))
            g.em.add_component(eid, Collider(28, 24, True))
            max_hp = entry.get('max_hp', 200)
            g.em.add_component(eid, Health(max_hp))
            h = g.em.get_component(eid, Health)
            h.current = entry.get('hp', max_hp)
            stor = Storage(CHEST_CAPACITY)
            from core.item_stack import normalize_rarity
            for s_str, (iid, c) in entry.get('storage', {}).items():
                stor.slots[int(s_str)] = (iid, c)
            for s_str, r in entry.get('storage_rarities', {}).items():
                stor.slot_rarities[int(s_str)] = normalize_rarity(r)
            for s_str, e in entry.get('storage_enchants', {}).items():
                stor.slot_enchantments[int(s_str)] = e
            g.em.add_component(eid, stor)
            g.em.add_component(eid, Placeable('chest'))
            g.cave_entities.append(eid)


def destroy_non_player_entities(g: 'Game') -> None:
    for eid in list(g.em._entities):
        if eid != g.player_id:
            g.em.destroy_entity(eid)


def respawn_resources(g: 'Game') -> None:
    """Replenish overworld trees and rocks that have been harvested.

    Clears the harvested_resources tracking set so all positions become
    available again, then uses a seed-based placement to add resources at
    positions that are not already occupied by other entities.
    """
    g.harvested_resources.clear()
    rng = random.Random(g.seed + 12345 + g.daynight.day_number)
    occupied = set()
    for eid in g.em.get_entities_with(Transform, Collider):
        t = g.em.get_component(eid, Transform)
        occupied.add((int(t.x // TILE_SIZE), int(t.y // TILE_SIZE)))

    for _ in range(TREE_COUNT):
        x = rng.randint(5, WORLD_WIDTH - 5)
        y = rng.randint(5, WORLD_HEIGHT - 5)
        if (x, y) in occupied:
            continue
        tile = g.world.get_tile(x, y)
        if tile in (TILE_GRASS, TILE_FOREST):
            eid = g.em.create_entity()
            g.em.add_component(eid, Transform(
                x * TILE_SIZE + 8, y * TILE_SIZE - 16))
            g.em.add_component(eid, Renderable(
                g.textures.get('tree'), layer=2))
            g.em.add_component(eid, Collider(24, 32, True))
            occupied.add((x, y))
    for _ in range(FOREST_TREE_COUNT):
        x = rng.randint(5, WORLD_WIDTH - 5)
        y = rng.randint(5, WORLD_HEIGHT - 5)
        if (x, y) in occupied:
            continue
        if g.world.get_tile(x, y) == TILE_FOREST:
            eid = g.em.create_entity()
            g.em.add_component(eid, Transform(
                x * TILE_SIZE + 8, y * TILE_SIZE - 16))
            g.em.add_component(eid, Renderable(
                g.textures.get('tree'), layer=2))
            g.em.add_component(eid, Collider(24, 32, True))
            occupied.add((x, y))
    for _ in range(ROCK_COUNT):
        x = rng.randint(5, WORLD_WIDTH - 5)
        y = rng.randint(5, WORLD_HEIGHT - 5)
        if (x, y) in occupied:
            continue
        if g.world.get_tile(x, y) in (TILE_GRASS, TILE_DIRT,
                                       TILE_STONE_FLOOR, TILE_FOREST):
            eid = g.em.create_entity()
            g.em.add_component(eid, Transform(
                x * TILE_SIZE + 4, y * TILE_SIZE + 6))
            g.em.add_component(eid, Renderable(
                g.textures.get('rock'), layer=1))
            g.em.add_component(eid, Collider(26, 18, True))
            occupied.add((x, y))
