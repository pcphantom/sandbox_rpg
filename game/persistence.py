"""Save / load / persistence functions extracted from Game class.

All functions receive the Game instance as their first argument ``g``.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from core.constants import (
    TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT,
    QUICK_SAVE_SLOT,
    WALL_HP, TURRET_HP, TURRET_RANGE, TURRET_DAMAGE, TURRET_COOLDOWN,
    TURRET_ENHANCE_DAMAGE, TURRET_ENHANCE_HP,
    CHEST_CAPACITY, STONE_WALL_HP_MULT,
    ENCHANT_TABLE_CAPACITY, ENCHANT_TABLE_HP,
    DIFFICULTY_EASY,
    TIME_DAY_START, TIME_DAY_END,
    DOOR_COLLIDER_W, DOOR_COLLIDER_H,
    LIGHT_COLOR_CAMPFIRE, LIGHT_COLOR_TORCH,
)
from core.components import (
    Transform, Velocity, Renderable, Collider, Health, Inventory,
    PlayerStats, Equipment, Placeable, LightSource, Storage, Turret,
    Building,
)
from world.cave import CaveData
from systems.physics import PhysicsSystem
from game import save_load


# ======================================================================
# BUILD SAVE DATA
# ======================================================================

def build_save_data(g: 'Game') -> Dict[str, Any]:
    pt: Transform = g.em.get_component(g.player_id, Transform)
    ph: Health = g.em.get_component(g.player_id, Health)
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    eq: Equipment = g.em.get_component(g.player_id, Equipment)
    inv_data = {str(s): [iid, c] for s, (iid, c) in inv.slots.items()}

    structures: list[dict[str, Any]] = []
    from core.components import AI, Building
    for eid in g.em.get_entities_with(Transform, Placeable, Building):
        if g.em.has_component(eid, AI):
            continue
        pl = g.em.get_component(eid, Placeable)
        t = g.em.get_component(eid, Transform)
        h = g.em.get_component(eid, Health)
        struct_data: Dict[str, Any] = {
            'type': pl.item_type,
            'x': t.x, 'y': t.y,
            'hp': h.current if h else 0,
            'max_hp': h.maximum if h else 0,
            'rotation': pl.rotation,
        }
        stor = g.em.get_component(eid, Storage)
        if stor:
            struct_data['storage'] = {
                str(s): [iid, c]
                for s, (iid, c) in stor.slots.items()}
            if stor.slot_enchantments:
                struct_data['storage_enchants'] = {
                    str(s): e
                    for s, e in stor.slot_enchantments.items()}
            if stor.slot_rarities:
                struct_data['storage_rarities'] = {
                    str(s): r
                    for s, r in stor.slot_rarities.items()}
        turr = g.em.get_component(eid, Turret)
        if turr:
            struct_data['turret_damage'] = turr.damage
            if turr.enchant:
                struct_data['turret_enchant'] = turr.enchant
            if turr.rarity != 'common':
                struct_data['turret_rarity'] = turr.rarity
        structures.append(struct_data)

    return {
        'seed': g.seed,
        'px': pt.x, 'py': pt.y,
        'hp': ph.current, 'max_hp': ph.maximum,
        'level': ps.level, 'xp': ps.xp, 'kills': ps.kills,
        'xp_to_next': ps.xp_to_next,
        'stat_points': ps.stat_points,
        'strength': ps.strength, 'agility': ps.agility,
        'vitality': ps.vitality, 'luck': ps.luck,
        'inventory': inv_data, 'equipped': inv.equipped_slot,
        'hotbar': {str(s): [iid, c] for s, (iid, c) in inv.hotbar.items()},
        'inv_enchants': {str(s): e for s, e in inv.slot_enchantments.items()},
        'hotbar_enchants': {str(s): e for s, e in inv.hotbar_enchantments.items()},
        'inv_rarities': {str(s): r for s, r in inv.slot_rarities.items()},
        'hotbar_rarities': {str(s): r for s, r in inv.hotbar_rarities.items()},
        'eq_weapon': eq.weapon, 'eq_armor': eq.armor,
        'eq_shield': eq.shield, 'eq_ranged': eq.ranged,
        'eq_ammo': eq.ammo,
        'eq_ammo_count': eq.ammo_count,
        'eq_enchants': eq.enchantments,
        'eq_rarities': eq.rarities,
        'day_time': g.daynight.time,
        'day_number': g.daynight.day_number,
        'was_day': g.daynight._was_day,
        'night_count': g.wave_system.night_count,
        'difficulty': g.difficulty,
        'structures': structures,
        'in_cave': g.in_cave,
        'cave_boss_alive': g.caves.boss_alive,
        'cave_chest_looted': g.caves.chest_looted,
        'last_resource_respawn_day': g._last_resource_respawn_day,
        'last_cave_reset_day': g._last_cave_reset_day,
        'cheats_enabled': g.cheats_enabled,
        'harvested_resources': list(g.harvested_resources),
        'cave_snapshots': g.cave_snapshots,
    }


# ======================================================================
# APPLY SAVE DATA
# ======================================================================

def apply_save_data(g: 'Game', data: Dict[str, Any]) -> None:
    from world import WorldGenerator

    saved_seed = data.get('seed', g.seed)
    if saved_seed != g.seed:
        g.seed = saved_seed
        g.world_gen = WorldGenerator(seed=g.seed)
    g.world = g.world_gen.generate(WORLD_WIDTH, WORLD_HEIGHT)

    g.caves = CaveData(g.seed, g.world)
    boss_alive = data.get('cave_boss_alive', [])
    chest_looted = data.get('cave_chest_looted', [])
    for i in range(min(len(boss_alive), g.caves.count)):
        g.caves.boss_alive[i] = boss_alive[i]
    for i in range(min(len(chest_looted), g.caves.count)):
        g.caves.chest_looted[i] = chest_looted[i]
    g.in_cave = data.get('in_cave', -1)
    g.overworld = None
    g.cave_entities.clear()
    # Restore harvested resources and cave snapshots BEFORE populating
    g.harvested_resources = set(
        tuple(pos) for pos in data.get('harvested_resources', []))
    raw_snaps = data.get('cave_snapshots', {})
    g.cave_snapshots = {int(k): v for k, v in raw_snaps.items()}

    for eid in list(g.em._entities):
        if eid != g.player_id:
            g.em.destroy_entity(eid)

    g.physics = PhysicsSystem(WORLD_WIDTH, WORLD_HEIGHT)

    if g.in_cave >= 0:
        g.overworld = g.world
        g.world = g.caves.interiors[g.in_cave]
        g.physics = PhysicsSystem(g.world.width, g.world.height)
        # Restore cave from snapshot if available, otherwise fresh populate
        from game import entities as _ge
        if g.in_cave in g.cave_snapshots:
            _ge.restore_cave_snapshot(g, g.in_cave,
                                      g.cave_snapshots[g.in_cave])
        else:
            g._populate_cave(g.in_cave)
    else:
        g._populate_world()

    pt: Transform = g.em.get_component(g.player_id, Transform)
    ph: Health = g.em.get_component(g.player_id, Health)
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    eq: Equipment = g.em.get_component(g.player_id, Equipment)
    pt.x = data['px']; pt.y = data['py']
    ph.current = data['hp']; ph.maximum = data['max_hp']
    ps.level = data['level']; ps.xp = data['xp']
    ps.kills = data['kills']; ps.xp_to_next = data['xp_to_next']
    ps.stat_points = data.get('stat_points', 0)
    ps.strength = data.get('strength', 1)
    ps.agility = data.get('agility', 1)
    ps.vitality = data.get('vitality', 1)
    ps.luck = data.get('luck', data.get('dexterity', 1))
    inv.slots.clear()
    for s_str, (iid, c) in data['inventory'].items():
        inv.slots[int(s_str)] = (iid, c)
    inv.hotbar.clear()
    for s_str, (iid, c) in data.get('hotbar', {}).items():
        inv.hotbar[int(s_str)] = (iid, c)
    inv.equipped_slot = data.get('equipped', 0)
    # Enchant overlays
    inv.slot_enchantments.clear()
    for s_str, e in data.get('inv_enchants', {}).items():
        inv.slot_enchantments[int(s_str)] = e
    inv.hotbar_enchantments.clear()
    for s_str, e in data.get('hotbar_enchants', {}).items():
        inv.hotbar_enchantments[int(s_str)] = e
    # Rarity overlays
    inv.slot_rarities.clear()
    for s_str, r in data.get('inv_rarities', {}).items():
        inv.slot_rarities[int(s_str)] = r
    inv.hotbar_rarities.clear()
    for s_str, r in data.get('hotbar_rarities', {}).items():
        inv.hotbar_rarities[int(s_str)] = r
    # Normalize: every slot gets a rarity, default 'common'
    from core.item_stack import normalize_rarity
    for s in inv.slots:
        inv.slot_rarities[s] = normalize_rarity(inv.slot_rarities.get(s, 'common'))
    for s in inv.hotbar:
        inv.hotbar_rarities[s] = normalize_rarity(inv.hotbar_rarities.get(s, 'common'))
    eq.weapon = data.get('eq_weapon')
    eq.armor = data.get('eq_armor')
    eq.shield = data.get('eq_shield')
    eq.ranged = data.get('eq_ranged')
    eq.ammo = data.get('eq_ammo')
    eq.ammo_count = data.get('eq_ammo_count', 0)
    eq.enchantments = data.get('eq_enchants', {})
    eq.rarities = data.get('eq_rarities', {})
    # Normalize equipment rarities from save data
    for k in list(eq.rarities):
        eq.rarities[k] = normalize_rarity(eq.rarities.get(k, 'common'))
    inv._equipment_ref = eq
    g.daynight.time = data.get('day_time', 0.3)
    g.daynight.day_number = data.get('day_number', 1)
    is_day_now = TIME_DAY_START <= g.daynight.time < TIME_DAY_END
    g.daynight._was_day = data.get('was_day', is_day_now)
    g.daynight._day_flash_timer = 0.0
    g.daynight._night_flash_timer = 0.0
    g.wave_system.night_count = data.get('night_count', 0)
    g.wave_system.was_night = not is_day_now
    g.difficulty = data.get('difficulty', DIFFICULTY_EASY)
    g.wave_system.difficulty = g.difficulty
    g.health_bar.max_value = ph.maximum
    g.health_bar.set_value(ph.current)
    g.xp_bar.max_value = ps.xp_to_next
    g.xp_bar.set_value(ps.xp)
    g.dead = False
    g.sleeping = False
    g.sleep_timer = 0.0
    g.daynight.reset_speed()
    g._last_resource_respawn_day = data.get('last_resource_respawn_day', 1)
    g._last_cave_reset_day = data.get('last_cave_reset_day', 1)
    g.cheats_enabled = data.get('cheats_enabled', False)

    # Reset camera bounds & position for the loaded world
    if g.in_cave >= 0:
        g.camera.set_bounds(g.world.width, g.world.height)
    else:
        g.camera.set_bounds(WORLD_WIDTH, WORLD_HEIGHT)
    g.camera.follow(pt.x, pt.y)
    g.camera.snap()

    for struct in data.get('structures', []):
        restore_structure(g, struct)


# ======================================================================
# RESTORE STRUCTURE
# ======================================================================

def restore_structure(g: 'Game', struct: Dict[str, Any]) -> None:
    from core.item_stack import normalize_rarity as _nr
    item_id = struct['type']
    rotation = struct.get('rotation', 0)
    eid = g.em.create_entity()
    g.em.add_component(eid, Transform(struct['x'], struct['y']))
    g.em.add_component(eid, Placeable(item_id, rotation=rotation))

    if item_id == 'campfire':
        g.em.add_component(eid, Renderable(
            g.textures.get('campfire_True'), layer=2))
        g.em.add_component(eid, LightSource(180, LIGHT_COLOR_CAMPFIRE, 1.0))
        h = Health(struct.get('max_hp', 60))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        g.em.add_component(eid, Building('campfire'))
    elif item_id == 'torch':
        g.em.add_component(eid, Renderable(
            g.textures.get('torch_placed'), layer=2))
        g.em.add_component(eid, LightSource(120, LIGHT_COLOR_TORCH, 0.8))
        h = Health(struct.get('max_hp', 30))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        g.em.add_component(eid, Building('torch'))
    elif item_id == 'trap':
        g.em.add_component(eid, Renderable(
            g.textures.get('trap_placed'), layer=1))
        h = Health(struct.get('max_hp', 40))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        g.em.add_component(eid, Building('trap'))
    elif item_id == 'bed':
        tex = g.textures.get('bed_placed')
        if rotation % 4 != 0:
            tex = pygame.transform.rotate(tex, -90 * (rotation % 4))
        g.em.add_component(eid, Renderable(tex, layer=1))
        h = Health(struct.get('max_hp', 80))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        g.em.add_component(eid, Building('bed'))
    elif item_id == 'wall':
        g.em.add_component(eid, Renderable(
            g.textures.get('wall_placed'), layer=2))
        g.em.add_component(eid, Collider(32, 32, True))
        h = Health(struct.get('max_hp', WALL_HP))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        g.em.add_component(eid, Building('wall'))
    elif item_id == 'stone_wall_b':
        g.em.add_component(eid, Renderable(
            g.textures.get('stone_wall_placed'), layer=2))
        g.em.add_component(eid, Collider(32, 32, True))
        h = Health(struct.get('max_hp', int(WALL_HP * STONE_WALL_HP_MULT)))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        g.em.add_component(eid, Building('stone_wall'))
    # Check if this is a turret variant (turret, turret_1 .. turret_5)
    is_turret = item_id == 'turret' or (
        item_id.startswith('turret_') and item_id[len('turret_'):].isdigit())

    if is_turret:
        g.em.add_component(eid, Renderable(
            g.textures.get('turret_placed'), layer=2))
        g.em.add_component(eid, Collider(32, 32, True))
        # Restore saved HP (already includes rarity/enhance scaling)
        if item_id == 'turret':
            enhance_level = 0
        else:
            enhance_level = int(item_id[len('turret_'):])
        default_hp = TURRET_ENHANCE_HP.get(enhance_level, TURRET_HP)
        h = Health(struct.get('max_hp', default_hp))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        saved_dmg = struct.get('turret_damage',
                               TURRET_ENHANCE_DAMAGE.get(enhance_level, TURRET_DAMAGE))
        saved_enchant = struct.get('turret_enchant')
        saved_rarity = struct.get('turret_rarity', 'common')
        g.em.add_component(eid, Turret(
            saved_dmg, TURRET_RANGE, TURRET_COOLDOWN,
            enchant=saved_enchant, rarity=saved_rarity))
        g.em.add_component(eid, Building('turret'))
    elif item_id == 'chest':
        g.em.add_component(eid, Renderable(
            g.textures.get('chest_placed'), layer=1))
        h = Health(struct.get('max_hp', 60))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        stor = Storage(CHEST_CAPACITY)
        for s_str, (iid, c) in struct.get('storage', {}).items():
            stor.slots[int(s_str)] = (iid, c)
        for s_str, e in struct.get('storage_enchants', {}).items():
            stor.slot_enchantments[int(s_str)] = e
        for s_str, r in struct.get('storage_rarities', {}).items():
            stor.slot_rarities[int(s_str)] = r
        for s in stor.slots:
            stor.slot_rarities[s] = _nr(stor.slot_rarities.get(s, 'common'))
        g.em.add_component(eid, stor)
        g.em.add_component(eid, Building('chest'))
    elif item_id == 'enchantment_table':
        g.em.add_component(eid, Renderable(
            g.textures.get('enchantment_table_placed'), layer=1))
        h = Health(struct.get('max_hp', ENCHANT_TABLE_HP))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        stor = Storage(ENCHANT_TABLE_CAPACITY)
        for s_str, (iid, c) in struct.get('storage', {}).items():
            stor.slots[int(s_str)] = (iid, c)
        for s_str, e in struct.get('storage_enchants', {}).items():
            stor.slot_enchantments[int(s_str)] = e
        for s_str, r in struct.get('storage_rarities', {}).items():
            stor.slot_rarities[int(s_str)] = r
        for s in stor.slots:
            stor.slot_rarities[s] = _nr(stor.slot_rarities.get(s, 'common'))
        g.em.add_component(eid, stor)
        g.em.add_component(eid, Building('enchantment_table'))
    elif item_id == 'door':
        g.em.add_component(eid, Renderable(
            g.textures.get('door_placed'), layer=2))
        h = Health(struct.get('max_hp', 50))
        h.current = struct.get('hp', h.maximum)
        g.em.add_component(eid, h)
        g.em.add_component(eid, Collider(
            DOOR_COLLIDER_W, DOOR_COLLIDER_H, True))
        g.em.add_component(eid, Building('door'))


# ======================================================================
# SAVE / LOAD SLOTS
# ======================================================================

def quick_save(g: 'Game') -> None:
    g._return_held_item()
    if save_load.save_game(QUICK_SAVE_SLOT, build_save_data(g)):
        g._notify("Quick Saved!")
    else:
        g._notify("Save failed!")


def quick_load(g: 'Game') -> None:
    data = save_load.load_game(QUICK_SAVE_SLOT)
    if not data:
        g._notify("No quick save found!")
        return
    apply_save_data(g, data)
    g._notify("Quick Loaded!")


def save_to_slot(g: 'Game', slot: int) -> None:
    g._return_held_item()
    if save_load.save_game(slot, build_save_data(g)):
        g._notify(f"Saved to slot {slot}!")
    else:
        g._notify("Save failed!")


def load_from_slot(g: 'Game', slot: int) -> None:
    data = save_load.load_game(slot)
    if not data:
        g._notify(f"Slot {slot} is empty!")
        return
    apply_save_data(g, data)
    g.paused = False
    g._notify(f"Loaded slot {slot}!")


def delete_slot(g: 'Game', slot: int) -> None:
    save_load.delete_save(slot)
    g._notify(f"Deleted slot {slot}.")
