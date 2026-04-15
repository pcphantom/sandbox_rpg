"""Interaction, placement, crafting, and sleep functions extracted from Game class.

All functions receive the Game instance as their first argument ``g``.
"""
from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING, Dict, List, Optional, Any, Tuple

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from core.constants import (
    TILE_SIZE,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    GRAY, CYAN, ORANGE, GREEN, RED, WHITE,
    INTERACT_RANGE, HARVEST_RANGE, BED_INTERACT_RANGE,
    LUCK_HARVEST_CHANCE, REPAIR_RANGE,
    WALL_HP, TURRET_HP, TURRET_RANGE, TURRET_DAMAGE, TURRET_COOLDOWN,
    TURRET_ENHANCE_DAMAGE, TURRET_ENHANCE_HP,
    CHEST_CAPACITY, CHEST_HP_VALUE,
    ENCHANT_TABLE_CAPACITY, ENCHANT_TABLE_HP,
    STONE_WALL_HP_MULT,
    TRAP_HP, BED_HP, CAMPFIRE_HP, DOOR_HP,
    DOOR_COLLIDER_W, DOOR_COLLIDER_H,
    CAMPFIRE_LIGHT_RADIUS,
    SLEEP_DURATION, NIGHT_SLEEP_SPEED_MULT,
    PLACEMENT_PREVIEW_COLOR, PLACEMENT_INVALID_COLOR,
    PARTICLE_COLOR_TREE, LIGHT_COLOR_CAMPFIRE, LIGHT_COLOR_TORCH,
)
from game_controller import (
    BEACON_LIGHT_RADIUS, BEACON_HP,
    STONE_OVEN_HP, STONE_OVEN_SLOTS, STONE_OVEN_LIGHT_RADIUS,
)
from core.components import (
    Transform, Velocity, Renderable, Collider, Health, Inventory,
    AI, PlayerStats, Equipment, Placeable, LightSource, Storage, Turret,
    Building,
)
from data import (
    ITEM_DATA, ITEM_CATEGORIES, RECIPES,
    RANGED_DATA, AMMO_BONUS_DAMAGE,
    SPELL_DATA, SPELL_RECHARGE, BOMB_DATA,
    HARVEST_TYPE,
)


# ======================================================================
# INTERACT (E key)
# ======================================================================

def interact(g: 'Game') -> None:
    pt: Transform = g.em.get_component(g.player_id, Transform)
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    px, py = pt.x + 10, pt.y + 14

    # Storage interaction (Chest / Enchantment Table / Stone Oven)
    for eid in g.em.get_entities_with(Transform, Storage):
        ct = g.em.get_component(eid, Transform)
        if math.hypot(ct.x - px, ct.y - py) < INTERACT_RANGE:
            bld = (g.em.get_component(eid, Building)
                   if g.em.has_component(eid, Building) else None)
            if bld and bld.building_type == 'stone_oven':
                g.show_stone_oven = True
                g.active_stone_oven = eid
                g.show_inventory = True  # Open inventory alongside stone oven
            elif bld and bld.building_type == 'enchantment_table':
                g.show_enchant_table = True
                g.active_enchant_table = eid
                g.show_inventory = True  # Open inventory alongside enchantment table
            else:
                g.show_chest = True
                g.active_chest = eid
                g.chest_ui.chest_scroll = 0
                g.show_inventory = True  # Open inventory alongside chest
                if g.in_cave >= 0:
                    g.caves.chest_looted[g.in_cave] = True
            return

    # Harvest
    nearest: Optional[int] = None
    nearest_dist = HARVEST_RANGE
    for eid in g.em.get_entities_with(Transform, Renderable):
        if eid == g.player_id or g.em.has_component(eid, AI):
            continue
        pl = (g.em.get_component(eid, Placeable)
              if g.em.has_component(eid, Placeable) else None)
        is_cave_resource = pl and hasattr(pl, 'drop_item') and pl.drop_item
        if pl and not is_cave_resource:
            continue
        t: Transform = g.em.get_component(eid, Transform)
        r: Renderable = g.em.get_component(eid, Renderable)
        if (is_cave_resource
                or r.surface in (g.textures.get('tree'),
                                 g.textures.get('rock'))):
            d = math.hypot(t.x - px, t.y - py)
            if d < nearest_dist:
                nearest = eid
                nearest_dist = d

    if nearest is not None:
        r = g.em.get_component(nearest, Renderable)
        eq: Equipment = g.em.get_component(g.player_id, Equipment)
        ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
        luck_bonus = (1 if random.random() < ps.luck * LUCK_HARVEST_CHANCE
                      else 0)
        pl_check = (g.em.get_component(nearest, Placeable)
                    if g.em.has_component(nearest, Placeable) else None)
        is_cave_res = (pl_check and hasattr(pl_check, 'drop_item')
                       and pl_check.drop_item)

        # Determine resource type being gathered
        if not is_cave_res and r.surface == g.textures.get('tree'):
            resource_type = 'wood'
        else:
            resource_type = 'stone'

        # Get bonus from equipped weapon
        eq_bonus = 0
        if eq and eq.weapon and eq.weapon in ITEM_DATA:
            eq_ht = HARVEST_TYPE.get(eq.weapon, 'all')
            if eq_ht == resource_type or eq_ht == 'all':
                eq_bonus = ITEM_DATA[eq.weapon][3]

        # Get bonus from active hotbar item
        hb_bonus = 0
        hotbar_item = inv.get_equipped()
        eq_weapon = eq.weapon if eq else None
        if (hotbar_item and hotbar_item in ITEM_DATA
                and hotbar_item != eq_weapon):
            hb_ht = HARVEST_TYPE.get(hotbar_item, 'all')
            if hb_ht == resource_type or hb_ht == 'all':
                hb_bonus = ITEM_DATA[hotbar_item][3]

        bonus = max(eq_bonus, hb_bonus)

        if is_cave_res:
            drop_id = pl_check.drop_item
            drop_count = random.randint(1, 3) + bonus + luck_bonus
            inv.add_item(drop_id, drop_count)
            th = g.em.get_component(nearest, Transform)
            color = CYAN if drop_id == 'diamond' else ORANGE
            g.particles.emit(th.x + 10, th.y + 8, 8, color, 40, 0.3)
            name = (ITEM_DATA[drop_id][0] if drop_id in ITEM_DATA
                    else drop_id)
            g._notify(f"Mined {drop_count} {name}!")
        elif r.surface == g.textures.get('tree'):
            inv.add_item('wood', random.randint(2, 4) + bonus + luck_bonus)
            inv.add_item('stick', 1)
            th = g.em.get_component(nearest, Transform)
            g.particles.emit(th.x + 20, th.y + 30, 8, PARTICLE_COLOR_TREE, 40, 0.3)
        else:
            inv.add_item('stone',
                         random.randint(2, 3) + bonus + luck_bonus)
            th = g.em.get_component(nearest, Transform)
            g.particles.emit(th.x + 14, th.y + 10, 8, GRAY, 40, 0.3)
        # Track harvested overworld resource positions (skip cave resources)
        if g.in_cave < 0 and not is_cave_res:
            col_h = g.em.get_component(nearest, Collider)
            gpos = getattr(col_h, 'grid_pos', None) if col_h else None
            if gpos:
                g.harvested_resources.add(gpos)
            else:
                # Fallback for entities without grid_pos tag
                th_h = g.em.get_component(nearest, Transform)
                gx = int(th_h.x // TILE_SIZE)
                gy = int(th_h.y // TILE_SIZE)
                g.harvested_resources.add((gx, gy))
        g.em.destroy_entity(nearest)


# ======================================================================
# USE EQUIPPED ITEM (F key)
# ======================================================================

def use_equipped_item(g: 'Game') -> None:
    # Bed interaction
    pt_check: Transform = g.em.get_component(g.player_id, Transform)
    for eid in g.em.get_entities_with(Transform, Placeable):
        pl: Placeable = g.em.get_component(eid, Placeable)
        if pl.item_type == 'bed':
            bt: Transform = g.em.get_component(eid, Transform)
            if math.hypot(bt.x - pt_check.x,
                          bt.y - pt_check.y) < BED_INTERACT_RANGE:
                try_sleep(g)
                return

    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    eq_id = inv.get_equipped()
    if not eq_id or eq_id not in ITEM_DATA:
        return
    data = ITEM_DATA[eq_id]
    heal = data[4]
    placeable = data[5]
    pt: Transform = g.em.get_component(g.player_id, Transform)

    # Spell (all spell types: projectile, self-heal, and buff)
    cat = ITEM_CATEGORIES.get(eq_id, '')
    if cat == 'spell' and eq_id in SPELL_DATA:
        sdata = SPELL_DATA[eq_id]
        if eq_id in g.spell_cooldowns:
            remaining = g.spell_cooldowns[eq_id]
            g._notify(f"{sdata['name']} on cooldown ({remaining:.1f}s)")
            return
        # Self-buff spells (protection, regen, strength, levitate) — apply immediately
        if sdata.get('type') == 'self_buff':
            effect = sdata['effect']
            if effect in g.active_buffs:
                cur_level = g.active_buffs[effect][0]
                if sdata['level'] <= cur_level:
                    g._notify(f"Already have {effect.title()} {cur_level}!")
                    return
            g.active_buffs[effect] = (
                sdata['level'], sdata['value'], sdata['duration'])
            g.spell_cooldowns[eq_id] = sdata.get('cooldown', 5.0)
            color = sdata.get('color', CYAN)
            g._notify(f"Applied {sdata['name']} ({sdata['duration']:.0f}s)")
            g.particles.emit(pt.x + 10, pt.y + 14, 10, color, 60, 0.5)
            return
        # Teleport-to-bed spells (Return)
        if sdata.get('type') == 'teleport_bed':
            bed_pos = None
            for eid_check in g.em.get_entities_with(Transform, Placeable):
                pl_check = g.em.get_component(eid_check, Placeable)
                if pl_check.item_type == 'bed':
                    bed_t = g.em.get_component(eid_check, Transform)
                    bed_pos = (bed_t.x, bed_t.y)
                    break
            if bed_pos is None:
                g._notify("No bed found!")
                return
            pt.x = bed_pos[0]
            pt.y = bed_pos[1] - TILE_SIZE
            g.camera.follow(pt.x, pt.y)
            g.camera.snap()
            g.spell_cooldowns[eq_id] = sdata.get('cooldown', 600.0)
            color = sdata.get('color', CYAN)
            g._notify(f"Returned to bed!")
            g.particles.emit(pt.x + 10, pt.y + 14, 15, color, 80, 0.6)
            return
        # Self-heal spells — cast immediately
        if sdata.get('type') == 'self':
            g.spell_targeting = True
            g.spell_item = eq_id
            g._spell_cast_at_mouse()
            return
        # Projectile spells — enter targeting mode
        g.spell_targeting = True
        g.spell_item = eq_id
        g._notify("Click target to cast spell. ESC/Right-click to cancel.")
        return

    # Bomb
    if cat == 'throwable' and eq_id in BOMB_DATA:
        g.spell_targeting = True
        g.spell_item = eq_id
        g._notify("Click target to throw. ESC/Right-click to cancel.")
        return

    # Hammer repair
    if eq_id == 'hammer':
        _try_repair(g, inv, pt)
        return

    if heal > 0:
        ph: Health = g.em.get_component(g.player_id, Health)
        if ph.current >= ph.maximum:
            g._notify("Already at full health!")
            return
        ph.heal(heal)
        inv.remove_item(eq_id, 1)
        g.health_bar.set_value(ph.current)
        g.dmg_numbers.append((pt.x, pt.y - 20, f'+{heal}', GREEN, 0.8))
        g.particles.emit(pt.x + 10, pt.y + 14, 8, GREEN, 40, 0.4)
        g._notify(f"Used {data[0]} (+{heal} HP)")
    elif placeable:
        g.placement_mode = True
        g.placement_item = eq_id
        g.placement_rotation = 0
        g.placement_slot = inv.equipped_slot
        from core.item_stack import normalize_rarity
        g.placement_rarity = normalize_rarity(inv.hotbar_rarities.get(inv.equipped_slot, 'common'))
        g.placement_enchant = inv.hotbar_enchantments.get(inv.equipped_slot)
        hint = f"Click to place {data[0]}."
        if eq_id == 'bed':
            hint += " R to rotate."
        hint += " ESC/Right-click to cancel."
        g._notify(hint)


# ======================================================================
# HAMMER REPAIR
# ======================================================================

# Map from placeable item_type to its recipe cost dict
_RECIPE_COST_CACHE: Dict[str, Dict[str, int]] = {}


def _get_recipe_cost(item_type: str) -> Dict[str, int]:
    """Return the crafting cost dict for a placeable item_type, or empty."""
    if not _RECIPE_COST_CACHE:
        for recipe in RECIPES:
            _RECIPE_COST_CACHE[recipe['gives']] = recipe['cost']
    return _RECIPE_COST_CACHE.get(item_type, {})


def _try_repair(g: 'Game', inv: Inventory, pt: Transform) -> None:
    """Find nearest damaged structure and repair it using proportional resources."""
    px, py = pt.x + 10, pt.y + 14
    nearest = None
    nearest_dist = REPAIR_RANGE
    for eid in g.em.get_entities_with(Transform, Placeable, Health):
        if g.em.has_component(eid, AI):
            continue
        h: Health = g.em.get_component(eid, Health)
        if h.current >= h.maximum:
            continue
        t: Transform = g.em.get_component(eid, Transform)
        d = math.hypot(t.x - px, t.y - py)
        if d < nearest_dist:
            nearest = eid
            nearest_dist = d

    if nearest is None:
        g._notify("No damaged structure nearby!")
        return

    h: Health = g.em.get_component(nearest, Health)
    pl: Placeable = g.em.get_component(nearest, Placeable)
    recipe_cost = _get_recipe_cost(pl.item_type)
    if not recipe_cost:
        g._notify("Cannot repair this structure!")
        return

    damage_frac = (h.maximum - h.current) / h.maximum
    # Calculate proportional cost (min 1 of each resource)
    repair_cost: Dict[str, int] = {}
    for mat, base_cost in recipe_cost.items():
        needed = max(1, int(math.ceil(base_cost * damage_frac)))
        repair_cost[mat] = needed

    # Check if player has resources
    for mat, needed in repair_cost.items():
        if not inv.has(mat, needed):
            mat_name = ITEM_DATA[mat][0] if mat in ITEM_DATA else mat
            g._notify(f"Need {needed} {mat_name} to repair!")
            return

    # Consume resources and repair
    for mat, needed in repair_cost.items():
        inv.remove_item(mat, needed)
    h.current = h.maximum
    t: Transform = g.em.get_component(nearest, Transform)
    g.particles.emit(t.x + 10, t.y + 10, 10, GREEN, 50, 0.4)
    name = ITEM_DATA.get(pl.item_type, (pl.item_type,))[0]
    if g.em.has_component(nearest, Turret):
        turr = g.em.get_component(nearest, Turret)
        if turr.rarity and turr.rarity != 'common':
            name = f"{turr.rarity.title()} {name}"
        if turr.enchant:
            from enchantments.effects import get_enchant_display_prefix
            pfx = get_enchant_display_prefix(turr.enchant)
            if pfx:
                name = f"{pfx} {name}"
    cost_str = ", ".join(
        f"{n} {ITEM_DATA.get(m, (m,))[0]}" for m, n in repair_cost.items())
    g._notify(f"Repaired {name}! (Used {cost_str})")


# ======================================================================
# PLACEMENT
# ======================================================================

def get_placement_tiles(g: 'Game', tx: int,
                        ty: int) -> List[Tuple[int, int]]:
    if g.placement_item == 'bed':
        offsets = [(0, 0)]
        r = g.placement_rotation % 4
        if r == 0:
            offsets.append((1, 0))
        elif r == 1:
            offsets.append((0, 1))
        elif r == 2:
            offsets.append((-1, 0))
        else:
            offsets.append((0, -1))
        return [(tx + dx, ty + dy) for dx, dy in offsets]
    return [(tx, ty)]


# Wall-type item ids that support upgrade/replace
_WALL_ITEM_IDS = {'wall', 'stone_wall_b'}


def find_building_at_tiles(g: 'Game',
                           tiles: list) -> int:
    for bid in g.em.get_entities_with(Transform, Building, Health):
        bt: Transform = g.em.get_component(bid, Transform)
        bc = (g.em.get_component(bid, Collider)
              if g.em.has_component(bid, Collider) else None)
        bw = bc.width if bc else TILE_SIZE
        bh = bc.height if bc else TILE_SIZE
        btx = int(bt.x // TILE_SIZE)
        bty = int(bt.y // TILE_SIZE)
        btx2 = int((bt.x + bw - 1) // TILE_SIZE)
        bty2 = int((bt.y + bh - 1) // TILE_SIZE)
        for ttx, tty in tiles:
            if btx <= ttx <= btx2 and bty <= tty <= bty2:
                return bid
    return 0


def placement_confirm(g: 'Game') -> None:
    if not g.placement_mode or not g.placement_item:
        return
    # Block placement inside caves
    if g.in_cave >= 0:
        g._notify("Can't place items in caves!")
        return
    mx, my = pygame.mouse.get_pos()
    world_x = mx + g.camera.x
    world_y = my + g.camera.y
    tx = int(world_x // TILE_SIZE)
    ty = int(world_y // TILE_SIZE)
    tiles = get_placement_tiles(g, tx, ty)
    for ttx, tty in tiles:
        if g.world.is_solid(ttx, tty):
            g._notify("Can't place here!")
            return

    existing_bid = find_building_at_tiles(g, tiles)
    if existing_bid:
        existing_placeable = g.em.get_component(existing_bid, Placeable)
        if (g.placement_item in _WALL_ITEM_IDS
                and existing_placeable
                and existing_placeable.item_type in _WALL_ITEM_IDS):
            if existing_placeable.item_type == g.placement_item:
                g._notify("Same wall type already here!")
                return
            inv_check: Inventory = g.em.get_component(
                g.player_id, Inventory)
            if not inv_check.has(g.placement_item):
                g.placement_mode = False
                g.placement_item = None
                g.placement_rarity = 'common'
                g.placement_enchant = None
                g.placement_slot = None
                g._notify("No more items to place!")
                return
            inv_check.add_item(existing_placeable.item_type, 1)
            old_name = ITEM_DATA[existing_placeable.item_type][0]
            td = g.em.get_component(existing_bid, Transform)
            g.particles.emit(td.x + 10, td.y + 10, 6, GRAY, 40, 0.3)
            g.em.destroy_entity(existing_bid)
            inv_check.remove_item(g.placement_item, 1)
            min_tx = min(t[0] for t in tiles)
            min_ty = min(t[1] for t in tiles)
            place_x = min_tx * TILE_SIZE
            place_y = min_ty * TILE_SIZE
            place_item(g, g.placement_item, place_x, place_y,
                       rotation=g.placement_rotation,
                       rarity=getattr(g, 'placement_rarity', 'common'),
                       enchant=getattr(g, 'placement_enchant', None))
            new_name = ITEM_DATA[g.placement_item][0]
            ench = getattr(g, 'placement_enchant', None)
            rar = getattr(g, 'placement_rarity', 'common')
            if rar and rar != 'common':
                new_name = f"{rar.title()} {new_name}"
            if ench:
                from enchantments.effects import get_enchant_display_prefix
                pfx = get_enchant_display_prefix(ench)
                if pfx:
                    new_name = f"{pfx} {new_name}"
            g._notify(f"Replaced {old_name} with {new_name}")
            if not inv_check.has(g.placement_item):
                g.placement_mode = False
                g.placement_item = None
                g.placement_rarity = 'common'
                g.placement_enchant = None
                g.placement_slot = None
            return
        else:
            g._notify("Can't place here!")
            return

    min_tx = min(t[0] for t in tiles)
    min_ty = min(t[1] for t in tiles)
    place_x = min_tx * TILE_SIZE
    place_y = min_ty * TILE_SIZE
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    if not inv.has(g.placement_item):
        g.placement_mode = False
        g.placement_item = None
        g.placement_rarity = 'common'
        g.placement_enchant = None
        g.placement_slot = None
        g._notify("No more items to place!")
        return
    # Remove from the specific hotbar slot that initiated placement
    pslot = getattr(g, 'placement_slot', None)
    if pslot is not None and pslot in inv.hotbar:
        iid_in_slot = inv.hotbar[pslot][0]
        if iid_in_slot == g.placement_item:
            inv.remove_from_hotbar_slot(pslot, 1)
        else:
            inv.remove_item(g.placement_item, 1)
    else:
        inv.remove_item(g.placement_item, 1)
    place_item(g, g.placement_item, place_x, place_y,
               rotation=g.placement_rotation,
               rarity=getattr(g, 'placement_rarity', 'common'),
               enchant=getattr(g, 'placement_enchant', None))
    placed_name = ITEM_DATA[g.placement_item][0]
    p_rar = getattr(g, 'placement_rarity', 'common')
    p_ench = getattr(g, 'placement_enchant', None)
    if p_rar and p_rar != 'common':
        placed_name = f"{p_rar.title()} {placed_name}"
    if p_ench:
        from enchantments.effects import get_enchant_display_prefix
        pfx = get_enchant_display_prefix(p_ench)
        if pfx:
            placed_name = f"{pfx} {placed_name}"
    g._notify(f"Placed {placed_name}")
    if not inv.has(g.placement_item):
        g.placement_mode = False
        g.placement_item = None
        g.placement_rarity = 'common'
        g.placement_enchant = None
        g.placement_slot = None


def place_item(g: 'Game', item_id: str,
               px: Optional[float] = None,
               py: Optional[float] = None,
               rotation: int = 0,
               rarity: str = 'common',
               enchant: Optional[dict] = None) -> None:
    if px is None or py is None:
        pt: Transform = g.em.get_component(g.player_id, Transform)
        pr: Renderable = g.em.get_component(g.player_id, Renderable)
        offset_x = -30 if pr.flip_x else 30
        px, py = pt.x + offset_x, pt.y + 20
    eid = g.em.create_entity()
    g.em.add_component(eid, Transform(px, py))
    g.em.add_component(eid, Placeable(item_id, rotation=rotation))

    # Rarity multiplier for placeable HP
    from systems.rarity import apply_rarity

    # Check if this is a turret variant (turret, turret_1 .. turret_5)
    is_turret = item_id == 'turret' or (
        item_id.startswith('turret_') and item_id[len('turret_'):].isdigit())

    if is_turret:
        # Determine enhancement level from item_id
        if item_id == 'turret':
            enhance_level = 0
        else:
            enhance_level = int(item_id[len('turret_'):])
        base_dmg = TURRET_ENHANCE_DAMAGE.get(enhance_level, TURRET_DAMAGE)
        base_hp = TURRET_ENHANCE_HP.get(enhance_level, TURRET_HP)
        scaled_dmg = apply_rarity(base_dmg, rarity)
        scaled_hp = apply_rarity(base_hp, rarity)
        g.em.add_component(eid, Renderable(
            g.textures.get('turret_placed'), layer=2))
        g.em.add_component(eid, Collider(32, 32, True))
        g.em.add_component(eid, Health(scaled_hp))
        g.em.add_component(eid, Turret(
            scaled_dmg, TURRET_RANGE, TURRET_COOLDOWN,
            enchant=enchant, rarity=rarity))
        g.em.add_component(eid, Building('turret'))
    elif item_id == 'campfire':
        g.em.add_component(eid, Renderable(
            g.textures.get('campfire_True'), layer=2))
        g.em.add_component(eid, LightSource(
            CAMPFIRE_LIGHT_RADIUS, LIGHT_COLOR_CAMPFIRE, 1.0))
        g.em.add_component(eid, Health(apply_rarity(CAMPFIRE_HP, rarity)))
        g.em.add_component(eid, Building('campfire'))
    elif item_id == 'torch':
        g.em.add_component(eid, Renderable(
            g.textures.get('torch_placed'), layer=2))
        g.em.add_component(eid, LightSource(120, LIGHT_COLOR_TORCH, 0.8))
        g.em.add_component(eid, Health(apply_rarity(30, rarity)))
        g.em.add_component(eid, Building('torch'))
    elif item_id == 'trap':
        g.em.add_component(eid, Renderable(
            g.textures.get('trap_placed'), layer=1))
        g.em.add_component(eid, Health(apply_rarity(TRAP_HP, rarity)))
        g.em.add_component(eid, Building('trap'))
    elif item_id == 'bed':
        tex = g.textures.get('bed_placed')
        if rotation % 4 != 0:
            tex = pygame.transform.rotate(tex, -90 * (rotation % 4))
        g.em.add_component(eid, Renderable(tex, layer=1))
        g.em.add_component(eid, Health(apply_rarity(BED_HP, rarity)))
        g.em.add_component(eid, Building('bed'))
    elif item_id == 'wall':
        g.em.add_component(eid, Renderable(
            g.textures.get('wall_placed'), layer=2))
        g.em.add_component(eid, Collider(32, 32, True))
        g.em.add_component(eid, Health(apply_rarity(WALL_HP, rarity)))
        g.em.add_component(eid, Building('wall'))
    elif item_id == 'stone_wall_b':
        g.em.add_component(eid, Renderable(
            g.textures.get('stone_wall_placed'), layer=2))
        g.em.add_component(eid, Collider(32, 32, True))
        g.em.add_component(eid, Health(apply_rarity(int(WALL_HP * STONE_WALL_HP_MULT), rarity)))
        g.em.add_component(eid, Building('stone_wall'))
    elif item_id == 'chest':
        g.em.add_component(eid, Renderable(
            g.textures.get('chest_placed'), layer=1))
        g.em.add_component(eid, Health(apply_rarity(CHEST_HP_VALUE, rarity)))
        g.em.add_component(eid, Storage(CHEST_CAPACITY))
        g.em.add_component(eid, Building('chest'))
    elif item_id == 'enchantment_table':
        g.em.add_component(eid, Renderable(
            g.textures.get('enchantment_table_placed'), layer=1))
        g.em.add_component(eid, Health(apply_rarity(ENCHANT_TABLE_HP, rarity)))
        g.em.add_component(eid, Storage(ENCHANT_TABLE_CAPACITY))
        g.em.add_component(eid, Building('enchantment_table'))
    elif item_id == 'door':
        g.em.add_component(eid, Renderable(
            g.textures.get('door_placed'), layer=2))
        g.em.add_component(eid, Health(apply_rarity(DOOR_HP, rarity)))
        g.em.add_component(eid, Collider(
            DOOR_COLLIDER_W, DOOR_COLLIDER_H, True))
        g.em.add_component(eid, Building('door'))
    elif item_id == 'beacon':
        g.em.add_component(eid, Renderable(
            g.textures.get('beacon_placed'), layer=2))
        g.em.add_component(eid, Collider(64, 64, True))
        g.em.add_component(eid, Health(apply_rarity(BEACON_HP, rarity)))
        g.em.add_component(eid, LightSource(
            BEACON_LIGHT_RADIUS, LIGHT_COLOR_CAMPFIRE, 1.0))
        g.em.add_component(eid, Building('beacon'))
    elif item_id == 'stone_oven':
        g.em.add_component(eid, Renderable(
            g.textures.get('stone_oven_False'), layer=1))
        g.em.add_component(eid, Collider(32, 32, True))
        g.em.add_component(eid, Health(apply_rarity(STONE_OVEN_HP, rarity)))
        g.em.add_component(eid, Storage(STONE_OVEN_SLOTS))
        g.em.add_component(eid, Building('stone_oven'))


# ======================================================================
# CRAFTING
# ======================================================================

def craft(g: 'Game', recipe: Dict[str, Any]) -> None:
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    for item, cost in recipe['cost'].items():
        if not inv.has(item, cost):
            g._notify("Not enough materials!")
            return
    for item, cost in recipe['cost'].items():
        inv.remove_item(item, cost)
    count = recipe.get('count', 1)
    inv.add_item(recipe['gives'], count)
    g._notify(f"Crafted {recipe['name']}!")
    pt: Transform = g.em.get_component(g.player_id, Transform)
    g.particles.emit(pt.x + 10, pt.y + 14, 10, CYAN, 50, 0.4)


# ======================================================================
# BED / SLEEP
# ======================================================================

def try_sleep(g: 'Game') -> None:
    if not g.daynight.is_sleepable():
        g._notify("You can only sleep at night!")
        return
    pt: Transform = g.em.get_component(g.player_id, Transform)
    for eid in g.em.get_entities_with(Transform, Placeable):
        pl: Placeable = g.em.get_component(eid, Placeable)
        if pl.item_type == 'bed':
            bt: Transform = g.em.get_component(eid, Transform)
            if math.hypot(bt.x - pt.x, bt.y - pt.y) < BED_INTERACT_RANGE:
                g.sleeping = True
                g.sleep_timer = SLEEP_DURATION
                g.daynight.set_speed(NIGHT_SLEEP_SPEED_MULT)
                g._notify("Sleeping...")
                return
    g._notify("No bed nearby!")
