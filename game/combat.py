"""Combat functions extracted from Game class.

All functions receive the Game instance as their first argument ``g``.
"""
from __future__ import annotations
import math
import random
from typing import TYPE_CHECKING, Optional

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from core.constants import (
    CYAN, GREEN, ORANGE, RED, YELLOW,
    CAMPFIRE_BASE_HEAL, CAMPFIRE_HEAL_RADIUS, CAMPFIRE_HEAL_INTERVAL,
    VITALITY_CAMPFIRE_BONUS_PER,
    BASE_MELEE_DAMAGE, SPEAR_ATTACK_RANGE, WEAPON_ATTACK_RANGE,
    UNARMED_ATTACK_RANGE, CRIT_CHANCE_PER_LUCK, CRIT_DAMAGE_MULT,
    MELEE_KNOCKBACK_FORCE, CONTACT_DAMAGE_RADIUS, PLAYER_HIT_INVULN,
    DAMAGE_FLASH_DURATION, HIT_SHAKE_AMOUNT, HIT_SHAKE_DURATION,
    ENEMY_PROJ_HIT_RADIUS, PROJ_SHAKE_AMOUNT, PROJ_SHAKE_DURATION,
    MIN_RANGED_COOLDOWN, AGI_RANGED_SPEED_BONUS, AGI_RANGED_SPEED_BONUS_CAP,
    PLAYER_TORCH_LIGHT_RADIUS,
    PARTICLE_COLOR_FIRE, PARTICLE_COLOR_ICE, PARTICLE_COLOR_LIGHTNING_ARC,
)
from data.day_night import (
    NIGHT_DAMAGE_BASE, NIGHT_DAMAGE_INCREASE, NIGHT_DAMAGE_INCREASE_FREQ,
    NIGHT_DAMAGE_INTERVAL, LIGHT_SAFETY_RADIUS,
    NIGHT_DARKNESS_THRESHOLD,
)
from core.components import (
    Transform, Velocity, Renderable, Collider, Health, Inventory,
    AI, PlayerStats, Equipment, Projectile, Placeable, LightSource,
)
from data import (
    ITEM_DATA, RANGED_DATA, AMMO_BONUS_DAMAGE,
    SPELL_DATA, SPELL_RECHARGE, BOMB_DATA, MOB_DATA,
)
from systems.damage_calc import (
    calc_melee_damage, calc_ranged_damage, calc_damage_reduction,
    calc_total_dr, apply_damage_reduction,
)
from core.item_stack import normalize_rarity


# ======================================================================
# DAMAGE HELPERS
# ======================================================================

def get_attack_damage(g: 'Game') -> int:
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    eq = g.em.get_component(g.player_id, Equipment)
    weapon = eq.weapon if eq and eq.weapon else inv.get_equipped()
    base = BASE_MELEE_DAMAGE
    if weapon and weapon in ITEM_DATA and ITEM_DATA[weapon][2] > 0:
        base = ITEM_DATA[weapon][2]
    # Apply rarity multiplier
    rarity = normalize_rarity(inv.get_equipped_rarity())
    if rarity == 'common' and eq:
        rarity = normalize_rarity(eq.rarities.get('weapon', 'common'))
    from systems.rarity import apply_rarity
    base = apply_rarity(base, rarity)
    dmg = calc_melee_damage(base, ps, eq)
    if 'strength' in g.active_buffs:
        dmg += int(g.active_buffs['strength'][1])
    # Enchantment bonus damage (fire/ice/lightning on weapon)
    ench = inv.get_equipped_enchant()
    if not ench and eq:
        ench = eq.enchantments.get('weapon')
    if ench:
        from enchantments.effects import get_enchant_bonus_damage
        dmg += get_enchant_bonus_damage(ench)
    return dmg


def get_attack_range(g: 'Game') -> float:
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    eq = g.em.get_component(g.player_id, Equipment)
    weapon = eq.weapon if eq and eq.weapon else inv.get_equipped()
    if weapon == 'spear':
        return SPEAR_ATTACK_RANGE
    if weapon and weapon in ITEM_DATA and ITEM_DATA[weapon][2] > 0:
        return WEAPON_ATTACK_RANGE
    return UNARMED_ATTACK_RANGE


# ======================================================================
# MELEE
# ======================================================================

def attack(g: 'Game') -> None:
    from core.spatial import spatial_hash
    pt: Transform = g.em.get_component(g.player_id, Transform)
    px, py = pt.x + 10, pt.y + 14
    rng = get_attack_range(g)
    dmg = get_attack_damage(g)
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    is_crit = random.random() < ps.luck * CRIT_CHANCE_PER_LUCK
    if is_crit:
        dmg = int(dmg * CRIT_DAMAGE_MULT)
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    eq: Equipment = g.em.get_component(g.player_id, Equipment)
    ench = inv.get_equipped_enchant()
    if not ench and eq:
        ench = eq.enchantments.get('weapon')
    candidates = spatial_hash.query_radius(px, py, rng)
    for eid in candidates:
        if not g.em.has_component(eid, AI):
            continue
        if not g.em.has_component(eid, Health):
            continue
        t: Transform = g.em.get_component(eid, Transform)
        if not t:
            continue
        dist = math.hypot(t.x - px, t.y - py)
        if dist < rng:
            h: Health = g.em.get_component(eid, Health)
            h.damage(dmg)
            # Aggro the mob on melee hit
            ai_c: AI = g.em.get_component(eid, AI)
            ai_c.aggro = True
            ai_c.state = "chase"
            v_mob = g.em.get_component(eid, Velocity)
            if v_mob and dist > 1:
                dx, dy = t.x - px, t.y - py
                v_mob.vx += (dx / dist) * MELEE_KNOCKBACK_FORCE
                v_mob.vy += (dy / dist) * MELEE_KNOCKBACK_FORCE
            if is_crit:
                g.dmg_numbers.append(
                    (t.x, t.y - 16, f'{dmg} CRIT!', ORANGE, 1.0))
                g.particles.emit(t.x + 12, t.y + 10, 10, ORANGE, 60, 0.4)
            else:
                g.dmg_numbers.append(
                    (t.x, t.y - 16, str(dmg), YELLOW, 0.8))
                g.particles.emit(t.x + 12, t.y + 10, 6, YELLOW, 50, 0.3)
            # Enchantment on-hit effects
            if ench:
                _apply_enchant_on_hit(g, eid, t, dmg, ench)


def _apply_enchant_on_hit(g: 'Game', target_eid: int, target_t: Transform,
                          base_dmg: int, ench: dict) -> None:
    """Apply fire/ice/lightning enchant effects on a melee hit."""
    etype = ench['type']
    if etype == 'fire':
        g.particles.emit(target_t.x + 12, target_t.y + 10,
                         5, PARTICLE_COLOR_FIRE, 40, 0.3)
    elif etype == 'ice':
        from enchantments.effects import get_enchant_slow_factor, get_enchant_slow_duration
        ai_c: AI = g.em.get_component(target_eid, AI)
        if ai_c:
            factor = get_enchant_slow_factor(ench)
            duration = get_enchant_slow_duration(ench)
            original_speed = ai_c.speed
            ai_c.speed *= factor
            schedule_speed_restore(g, target_eid, original_speed, duration)
        g.particles.emit(target_t.x + 12, target_t.y + 10,
                         5, PARTICLE_COLOR_ICE, 40, 0.3)
    elif etype == 'lightning':
        from enchantments.effects import get_enchant_arc_radius, get_enchant_arc_damage_frac
        from core.spatial import spatial_hash
        arc_radius = get_enchant_arc_radius(ench)
        arc_frac = get_enchant_arc_damage_frac(ench)
        arc_dmg = max(1, int(base_dmg * arc_frac))
        candidates = spatial_hash.query_radius(
            target_t.x, target_t.y, arc_radius)
        for oeid in candidates:
            if oeid == target_eid:
                continue
            if not g.em.has_component(oeid, AI):
                continue
            if not g.em.has_component(oeid, Health):
                continue
            ot: Transform = g.em.get_component(oeid, Transform)
            if not ot:
                continue
            if math.hypot(ot.x - target_t.x, ot.y - target_t.y) < arc_radius:
                oh: Health = g.em.get_component(oeid, Health)
                oh.damage(arc_dmg)
                g.dmg_numbers.append(
                    (ot.x, ot.y - 16, str(arc_dmg), PARTICLE_COLOR_LIGHTNING_ARC, 0.6))
                g.particles.emit(ot.x + 12, ot.y + 10,
                                 4, PARTICLE_COLOR_LIGHTNING_ARC, 30, 0.2)
                break  # Arc to one nearby target


# ======================================================================
# RANGED
# ======================================================================

def ranged_attack(g: 'Game') -> None:
    eq: Equipment = g.em.get_component(g.player_id, Equipment)
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    if not eq or not eq.ranged:
        g._notify("No ranged weapon equipped!")
        return
    rdata = RANGED_DATA.get(eq.ranged)
    if not rdata:
        # Enhanced variant (e.g. 'bow_5') — look up base weapon
        from core.enhancement import get_base_item_id
        base_ranged_id = get_base_item_id(eq.ranged)
        rdata = RANGED_DATA.get(base_ranged_id)
    if not rdata:
        return
    ammo_id = eq.ammo
    if ammo_id and eq.ammo_count > 0:
        # Consume from equipped ammo slot
        eq.ammo_count -= 1
        if eq.ammo_count <= 0:
            eq.ammo = None
            eq.ammo_count = 0
            eq.enchantments.pop('ammo', None)
            eq.rarities.pop('ammo', 'common')
    elif inv.has(ammo_id or ''):
        # Fallback: consume loose ammo from inventory
        inv.remove_item(ammo_id, 1)
    else:
        # Try any compatible ammo in inventory
        ammo_id = None
        for a in rdata['ammo']:
            if inv.has(a):
                ammo_id = a
                inv.remove_item(a, 1)
                break
    if not ammo_id:
        g._notify("No ammo!")
        return

    bonus = AMMO_BONUS_DAMAGE.get(ammo_id, 0)
    base_ranged = rdata['damage']
    # Apply enhancement bonus before rarity
    from core.enhancement import get_enhancement_level, RANGED_OFFENSE_BONUS_PER_LEVEL
    enh_level = get_enhancement_level(eq.ranged)
    if enh_level > 0:
        base_ranged += enh_level * RANGED_OFFENSE_BONUS_PER_LEVEL
    # Apply rarity multiplier to ranged weapon damage
    ranged_rarity = normalize_rarity(eq.rarities.get('ranged', 'common'))
    from systems.rarity import apply_rarity
    base_ranged = apply_rarity(base_ranged, ranged_rarity)
    dmg = calc_ranged_damage(base_ranged, bonus, ps)
    if 'strength' in g.active_buffs:
        dmg += int(g.active_buffs['strength'][1])
    # Enchantment bonus damage on ranged weapon
    ranged_ench = eq.enchantments.get('ranged')
    if ranged_ench:
        from enchantments.effects import get_enchant_bonus_damage
        dmg += get_enchant_bonus_damage(ranged_ench)

    pt: Transform = g.em.get_component(g.player_id, Transform)
    pr: Renderable = g.em.get_component(g.player_id, Renderable)
    dx = -1.0 if pr.flip_x else 1.0
    dy = 0.0

    from core.spatial import spatial_hash
    best_eid, best_dist = None, rdata['range']
    candidates = spatial_hash.query_radius(pt.x, pt.y, rdata['range'])
    for eid in candidates:
        if not g.em.has_component(eid, AI):
            continue
        if not g.em.has_component(eid, Health):
            continue
        mt = g.em.get_component(eid, Transform)
        if not mt:
            continue
        d = math.hypot(mt.x - pt.x, mt.y - pt.y)
        if d < best_dist:
            best_dist = d
            best_eid = eid
    if best_eid is not None:
        mt = g.em.get_component(best_eid, Transform)
        ddx, ddy = mt.x - pt.x, mt.y - pt.y
        mag = math.hypot(ddx, ddy)
        if mag > 0:
            dx, dy = ddx / mag, ddy / mag

    pid = g.em.create_entity()
    g.em.add_component(pid, Transform(pt.x + 10, pt.y + 14))
    g.em.add_component(pid, Velocity(
        dx * rdata['speed'], dy * rdata['speed'], 1.0))
    proj_tex = ('proj_arrow' if eq.ranged.startswith('bow')
                else 'proj_bolt' if eq.ranged.startswith('crossbow')
                else 'proj_rock')
    g.em.add_component(pid, Renderable(
        g.textures.get(proj_tex), layer=4))
    g.em.add_component(pid, Collider(8, 8, False))
    g.em.add_component(pid, Projectile(
        dmg, g.player_id, rdata['speed'], rdata['range']))

    agi_ranged_bonus = min(AGI_RANGED_SPEED_BONUS_CAP,
                           ps.agility * AGI_RANGED_SPEED_BONUS)
    cd = max(MIN_RANGED_COOLDOWN,
             rdata['cooldown'] / (1.0 + agi_ranged_bonus))
    g.ranged_cd = cd


# ======================================================================
# PROJECTILE HIT
# ======================================================================

def on_proj_hit(g: 'Game', target_eid: int, damage: int,
                proj_t: Transform, proj: Optional[Projectile] = None) -> None:
    if proj and proj.is_bomb:
        from core.spatial import spatial_hash
        radius = proj.bomb_radius
        candidates = spatial_hash.query_radius(proj_t.x, proj_t.y, radius)
        for mid in candidates:
            if not g.em.has_component(mid, AI):
                continue
            if not g.em.has_component(mid, Health):
                continue
            mt: Transform = g.em.get_component(mid, Transform)
            if not mt:
                continue
            d = math.hypot(mt.x - proj_t.x, mt.y - proj_t.y)
            if d < radius:
                mh: Health = g.em.get_component(mid, Health)
                falloff = 1.0 - (d / radius) * 0.5
                aoe_dmg = max(1, int(damage * falloff))
                mh.damage(aoe_dmg)
                g.dmg_numbers.append(
                    (mt.x, mt.y - 16, str(aoe_dmg), ORANGE, 0.8))
                # Aggro all mobs hit by bomb
                bomb_ai: AI = g.em.get_component(mid, AI)
                bomb_ai.aggro = True
                bomb_ai.state = "chase"
        g.particles.emit(proj_t.x, proj_t.y, 20, ORANGE, 80, 0.5)
        g.particles.emit(proj_t.x, proj_t.y, 12, RED, 60, 0.4)
        g.camera.shake(HIT_SHAKE_AMOUNT * 2, HIT_SHAKE_DURATION)
        return

    # Determine spell type for proper explosion effects
    from game_controller import SPELL_EXPLOSION_PARTICLES, SPELL_EXPLOSION_RADIUS
    spell_id = proj.spell_id if proj else None
    tier = 1
    if spell_id:
        tier = _get_spell_tier(spell_id)

    explosion_count = SPELL_EXPLOSION_PARTICLES.get(tier, 10)
    explosion_radius = SPELL_EXPLOSION_RADIUS.get(tier, 50)

    # Element-specific explosion effects
    if spell_id and 'fireball' in spell_id:
        # Fire explosion — red-orange burst
        g.dmg_numbers.append(
            (proj_t.x, proj_t.y - 16, str(damage), ORANGE, 0.8))
        g.particles.emit(proj_t.x, proj_t.y, explosion_count, PARTICLE_COLOR_FIRE,
                         explosion_radius, 0.5)
        g.particles.emit(proj_t.x, proj_t.y, explosion_count // 2, RED,
                         explosion_radius * 0.7, 0.4)
        g.particles.emit(proj_t.x, proj_t.y, explosion_count // 3, YELLOW,
                         explosion_radius * 0.4, 0.3)
        g.camera.shake(HIT_SHAKE_AMOUNT, HIT_SHAKE_DURATION)
    elif spell_id and 'ice' in spell_id:
        # Ice explosion — cyan-white burst + slow
        g.dmg_numbers.append(
            (proj_t.x, proj_t.y - 16, str(damage), PARTICLE_COLOR_ICE, 0.8))
        g.particles.emit(proj_t.x, proj_t.y, explosion_count, PARTICLE_COLOR_ICE,
                         explosion_radius, 0.5)
        g.particles.emit(proj_t.x, proj_t.y, explosion_count // 2, (200, 240, 255),
                         explosion_radius * 0.5, 0.3)
        # Apply slow effect — look up the correct tier's data
        if target_eid >= 0 and spell_id in SPELL_DATA:
            sdata = SPELL_DATA[spell_id]
            if g.em.has_component(target_eid, AI):
                ai_c: AI = g.em.get_component(target_eid, AI)
                slow_factor = sdata.get('slow_factor', 0.4)
                slow_dur = sdata.get('slow_duration', 3.0)
                ai_c.speed *= slow_factor
                original_speed = MOB_DATA.get(ai_c.mob_type, {}).get(
                    'speed', ai_c.speed / slow_factor)
                schedule_speed_restore(g, target_eid, original_speed, slow_dur)
    elif spell_id and 'lightning' in spell_id:
        # Lightning explosion — white-blue electric burst
        g.dmg_numbers.append(
            (proj_t.x, proj_t.y - 16, str(damage), PARTICLE_COLOR_LIGHTNING_ARC, 0.8))
        g.particles.emit(proj_t.x, proj_t.y, explosion_count,
                         PARTICLE_COLOR_LIGHTNING_ARC, explosion_radius, 0.4)
        g.particles.emit(proj_t.x, proj_t.y, explosion_count // 2, (240, 245, 255),
                         explosion_radius * 0.6, 0.3)
        g.camera.shake(HIT_SHAKE_AMOUNT * 0.5, HIT_SHAKE_DURATION * 0.5)
    else:
        # Generic projectile hit (arrows, etc.)
        g.dmg_numbers.append(
            (proj_t.x, proj_t.y - 16, str(damage), CYAN, 0.8))
        g.particles.emit(proj_t.x, proj_t.y, 5, CYAN, 40, 0.3)


# ======================================================================
# SPELLS & BOMBS
# ======================================================================

def _get_spell_level_multiplier(g: 'Game') -> float:
    """Return the spell damage/heal multiplier based on player level.

    Formula: 1.0 + (player_level - 1) * SPELL_LEVEL_SCALE_PERCENT
    At level 1 → 1.0, at level 50 → ~2.0, at level 100 → ~3.0
    """
    from game_controller import SPELL_LEVEL_SCALE_PERCENT
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    return 1.0 + (ps.level - 1) * SPELL_LEVEL_SCALE_PERCENT


def _find_nearest_enemy(g: 'Game', world_x: float, world_y: float,
                        radius: float) -> Optional[Transform]:
    """Find the enemy nearest to (world_x, world_y) within radius.

    Returns the Transform of the nearest enemy, or None.
    """
    from core.spatial import spatial_hash
    best_dist = radius
    best_t = None
    candidates = spatial_hash.query_radius(world_x, world_y, radius)
    for eid in candidates:
        if not g.em.has_component(eid, AI):
            continue
        if not g.em.has_component(eid, Health):
            continue
        mt = g.em.get_component(eid, Transform)
        if not mt:
            continue
        d = math.hypot(mt.x - world_x, mt.y - world_y)
        if d < best_dist:
            best_dist = d
            best_t = mt
    return best_t


def _get_spell_tier(spell_id: str) -> int:
    """Extract the tier (1-5) from a spell item_id like 'spell_fireball_3'."""
    parts = spell_id.rsplit('_', 1)
    if len(parts) == 2 and parts[1].isdigit():
        return int(parts[1])
    return 1  # Base spell (no suffix) is tier 1


def spell_cast_at_mouse(g: 'Game') -> None:
    if not g.spell_targeting or not g.spell_item:
        return

    bdata = BOMB_DATA.get(g.spell_item)
    if bdata:
        throw_bomb(g, bdata)
        return

    sdata = SPELL_DATA.get(g.spell_item)
    if not sdata:
        g.spell_targeting = False
        g.spell_item = None
        return
    if g.spell_item in g.spell_cooldowns:
        remaining = g.spell_cooldowns[g.spell_item]
        g._notify(f"{sdata['name']} on cooldown ({remaining:.1f}s)")
        return

    pt: Transform = g.em.get_component(g.player_id, Transform)
    level_mult = _get_spell_level_multiplier(g)

    if sdata.get('type') == 'self':
        heal_amt = sdata.get('heal', 0)
        if heal_amt > 0:
            # Apply level scaling to heal amount
            heal_amt = max(1, int(heal_amt * level_mult))
            ph: Health = g.em.get_component(g.player_id, Health)
            if ph.current >= ph.maximum:
                g._notify("Already at full health!")
                g.spell_targeting = False
                g.spell_item = None
                return
            ph.heal(heal_amt)
            g.health_bar.set_value(ph.current)
            g.dmg_numbers.append(
                (pt.x, pt.y - 20, f'+{heal_amt}', GREEN, 0.8))
        g.particles.emit(pt.x + 10, pt.y + 14, 12, sdata['color'], 60, 0.4)
        g._notify(f"Cast {sdata['name']}!")
        g.spell_cooldowns[g.spell_item] = sdata.get('cooldown', SPELL_RECHARGE)
        g.spell_targeting = False
        g.spell_item = None
        return

    # --- Projectile spell ---
    from game_controller import (
        SPELL_AUTO_TARGET_RADIUS, SPELL_PROJ_SIZE,
    )
    mx, my = pygame.mouse.get_pos()
    target_x = mx + g.camera.x
    target_y = my + g.camera.y

    # Auto-target: snap to nearest enemy near the crosshair click
    enemy_t = _find_nearest_enemy(g, target_x, target_y, SPELL_AUTO_TARGET_RADIUS)
    if enemy_t:
        target_x = enemy_t.x + 12  # center of enemy sprite
        target_y = enemy_t.y + 12

    dx = target_x - pt.x
    dy = target_y - pt.y
    dist = math.hypot(dx, dy)
    if dist < 1:
        return
    dx /= dist
    dy /= dist

    tier = _get_spell_tier(g.spell_item)
    proj_w, proj_h = SPELL_PROJ_SIZE.get(tier, (12, 12))

    tex_key = f"proj_{g.spell_item.replace('spell_', '')}"
    tex = g.textures.cache.get(tex_key)
    if tex is None:
        tex = g.textures.get('proj_fireball')
    # Scale texture to tier-based size
    if tex:
        tex = pygame.transform.scale(tex, (proj_w, proj_h))

    # Apply level scaling to spell damage
    spell_dmg = max(1, int(sdata['damage'] * level_mult))

    pid = g.em.create_entity()
    g.em.add_component(pid, Transform(pt.x + 10, pt.y + 14))
    g.em.add_component(pid, Velocity(
        dx * sdata['speed'], dy * sdata['speed'], 1.0))
    g.em.add_component(pid, Renderable(tex, layer=4))
    g.em.add_component(pid, Collider(proj_w, proj_h, False))
    proj = Projectile(
        spell_dmg, g.player_id, sdata['speed'], sdata['range'])
    proj.spell_id = g.spell_item
    g.em.add_component(pid, proj)
    g.particles.emit(pt.x + 10, pt.y + 14, 8, sdata['color'], 60, 0.3)
    g._notify(f"Cast {sdata['name']}!")
    g.spell_cooldowns[g.spell_item] = sdata.get('cooldown', SPELL_RECHARGE)
    g.spell_targeting = False
    g.spell_item = None


def throw_bomb(g: 'Game', bdata: dict) -> None:
    pt: Transform = g.em.get_component(g.player_id, Transform)
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    mx, my = pygame.mouse.get_pos()
    target_x = mx + g.camera.x
    target_y = my + g.camera.y
    dx = target_x - pt.x
    dy = target_y - pt.y
    dist = math.hypot(dx, dy)
    if dist < 1:
        return
    dx /= dist
    dy /= dist
    tex = g.textures.cache.get('proj_bomb')
    if tex is None:
        tex = g.textures.get('proj_fireball')
    pid = g.em.create_entity()
    g.em.add_component(pid, Transform(pt.x + 10, pt.y + 14))
    g.em.add_component(pid, Velocity(
        dx * bdata['speed'], dy * bdata['speed'], 1.0))
    g.em.add_component(pid, Renderable(tex, layer=4))
    g.em.add_component(pid, Collider(12, 12, False))
    proj = Projectile(
        bdata['damage'], g.player_id, bdata['speed'], bdata['range'])
    proj.is_bomb = True
    proj.bomb_radius = bdata['radius']
    g.em.add_component(pid, proj)
    g.particles.emit(pt.x + 10, pt.y + 14, 6, bdata['color'], 50, 0.3)
    g._notify("Bomb thrown!")
    if g.spell_item:
        inv.remove_item(g.spell_item, 1)
    g.spell_targeting = False
    g.spell_item = None


# ======================================================================
# CALLBACKS
# ======================================================================

def on_trap_hit(g: 'Game', target_eid: int, damage: int,
                trap_t: Transform) -> None:
    g.dmg_numbers.append(
        (trap_t.x, trap_t.y - 16, str(damage), RED, 0.8))
    g.particles.emit(trap_t.x, trap_t.y, 5, RED, 40, 0.3)


def on_turret_fire(g: 'Game', target_eid: int, damage: int,
                   turret_t: Transform, target_t: Transform,
                   enchant: Optional[dict] = None, arc_mobs: Optional[list] = None,
                   ice_slow_data: Optional[tuple] = None) -> None:
    # Schedule ice slow restore if turret applied a slow
    if ice_slow_data:
        slow_eid, original_speed, slow_dur = ice_slow_data
        schedule_speed_restore(g, slow_eid, original_speed, slow_dur)
    # Determine color from enchant
    from enchantments.effects import ENCHANT_COLORS
    etype = enchant['type'] if enchant else None
    shot_color = ENCHANT_COLORS.get(etype, ORANGE) if etype else ORANGE

    g.dmg_numbers.append(
        (target_t.x, target_t.y - 16, str(damage), shot_color, 0.8))
    g.particles.emit(turret_t.x + 16, turret_t.y + 8, 4, shot_color, 60, 0.2)
    g.particles.emit(target_t.x, target_t.y, 3, RED, 40, 0.2)

    # Lightning arc visual effects
    if arc_mobs:
        for _mid, arc_dmg, mt2 in arc_mobs:
            g.dmg_numbers.append(
                (mt2.x, mt2.y - 16, str(arc_dmg), PARTICLE_COLOR_LIGHTNING_ARC, 0.6))
            g.particles.emit(mt2.x, mt2.y, 4, PARTICLE_COLOR_LIGHTNING_ARC, 50, 0.2)

    # Ice enchant slow visual
    if etype == 'ice':
        g.particles.emit(target_t.x, target_t.y, 5, PARTICLE_COLOR_ICE, 30, 0.3)


def on_enemy_ranged_fire(g: 'Game', mob_eid: int, mob_t: Transform,
                         player_t: Transform) -> None:
    mob_ai = g.em.get_component(mob_eid, AI)
    if not mob_ai:
        return
    dx = player_t.x - mob_t.x
    dy = player_t.y - mob_t.y
    dist = math.hypot(dx, dy)
    if dist < 1:
        return
    dx /= dist
    dy /= dist
    pid = g.em.create_entity()
    g.em.add_component(pid, Transform(mob_t.x + 12, mob_t.y + 12))
    g.em.add_component(pid, Velocity(
        dx * mob_ai.ranged_speed, dy * mob_ai.ranged_speed, 1.0))
    g.em.add_component(pid, Renderable(
        g.textures.get('proj_enemy'), layer=4))
    g.em.add_component(pid, Collider(8, 8, False))
    proj = Projectile(mob_ai.ranged_damage, mob_eid,
                      mob_ai.ranged_speed, mob_ai.ranged_range)
    g.em.add_component(pid, proj)
    g.particles.emit(mob_t.x + 12, mob_t.y + 10, 3, RED, 40, 0.2)


# ======================================================================
# DAMAGE TO PLAYER
# ======================================================================

def _get_equipment_enchant_dr(eq: Optional[Equipment]) -> int:
    """Sum DR bonus from protection enchants on armor and shield."""
    if not eq:
        return 0
    from enchantments.effects import get_enchant_dr_bonus
    total = 0
    for attr in ('armor', 'shield'):
        ench = eq.enchantments.get(attr)
        if ench:
            total += get_enchant_dr_bonus(ench)
    return total


def _is_near_light(g: 'Game', x: float, y: float) -> bool:
    """Return True if position (x, y) is near a light source."""
    from core.spatial import spatial_hash
    candidates = spatial_hash.query_radius(x, y, LIGHT_SAFETY_RADIUS)
    for eid in candidates:
        if not g.em.has_component(eid, LightSource):
            continue
        t = g.em.get_component(eid, Transform)
        if math.hypot(t.x - x, t.y - y) < LIGHT_SAFETY_RADIUS:
            return True
    return False


def _get_night_damage_multiplier(g: 'Game', x: float, y: float) -> int:
    """Return the enemy damage multiplier at night when not in light.

    Returns 1 (no bonus) during the day, inside caves, or when near light.
    """
    if not g.daynight.is_night():
        return 1
    if g.in_cave >= 0:
        return 1
    if _is_near_light(g, x, y):
        return 1
    # Also check if player is holding a torch or fire-enchanted weapon
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    eq: Equipment = g.em.get_component(g.player_id, Equipment)
    if inv.get_equipped() == 'torch' and inv.has('torch'):
        return 1
    ench = eq.enchantments.get('weapon') if eq else None
    if not ench:
        ench = inv.get_equipped_enchant()
    if ench and ench.get('type') == 'fire':
        return 1
    from data.difficulty import get_profile
    prof = get_profile(g.difficulty)
    return int(prof.get('night_damage_multiplier', 1))


def check_contact_damage(g: 'Game', pt: Transform) -> None:
    if g.god_mode:
        return
    if g.player_hit_cd > 0:
        return
    eq: Equipment = g.em.get_component(g.player_id, Equipment)
    prot_val = int(g.active_buffs['protection'][1]) if 'protection' in g.active_buffs else 0
    enchant_dr = _get_equipment_enchant_dr(eq)
    total_dr = calc_total_dr(eq, prot_val, enchant_dr)
    night_mult = _get_night_damage_multiplier(g, pt.x, pt.y)
    from core.spatial import spatial_hash
    candidates = spatial_hash.query_radius(pt.x, pt.y, CONTACT_DAMAGE_RADIUS)
    for eid in candidates:
        if not g.em.has_component(eid, AI):
            continue
        t: Transform = g.em.get_component(eid, Transform)
        if not t:
            continue
        ai_c: AI = g.em.get_component(eid, AI)
        dist = math.hypot(t.x - pt.x, t.y - pt.y)
        if dist < CONTACT_DAMAGE_RADIUS:
            ph: Health = g.em.get_component(g.player_id, Health)
            raw = ai_c.contact_damage * night_mult
            dmg = apply_damage_reduction(raw, total_dr)
            ph.damage(dmg)
            g.health_bar.set_value(ph.current)
            g.player_hit_cd = PLAYER_HIT_INVULN
            g.damage_flash = DAMAGE_FLASH_DURATION
            g.camera.shake(HIT_SHAKE_AMOUNT, HIT_SHAKE_DURATION)
            g.particles.emit(pt.x + 10, pt.y + 14, 8, RED, 60, 0.4)
            g.dmg_numbers.append(
                (pt.x, pt.y - 16, str(dmg), RED, 0.8))
            if not ph.is_alive():
                g.dead = True
                g.dmg_numbers.append(
                    (pt.x, pt.y - 30, 'YOU DIED', RED, 2.5))
            break


def check_enemy_projectile_damage(g: 'Game', pt: Transform) -> None:
    if g.god_mode:
        return
    eq: Equipment = g.em.get_component(g.player_id, Equipment)
    prot_val = int(g.active_buffs['protection'][1]) if 'protection' in g.active_buffs else 0
    enchant_dr = _get_equipment_enchant_dr(eq)
    total_dr = calc_total_dr(eq, prot_val, enchant_dr)
    night_mult = _get_night_damage_multiplier(g, pt.x, pt.y)
    to_remove = []
    for pid in g.em.get_entities_with(Transform, Projectile):
        proj = g.em.get_component(pid, Projectile)
        if proj.owner == g.player_id:
            continue
        proj_t = g.em.get_component(pid, Transform)
        dist = math.hypot(proj_t.x - pt.x - 10, proj_t.y - pt.y - 14)
        if dist < ENEMY_PROJ_HIT_RADIUS:
            ph: Health = g.em.get_component(g.player_id, Health)
            raw = int(proj.damage * night_mult)
            dmg = apply_damage_reduction(raw, total_dr)
            ph.damage(dmg)
            g.health_bar.set_value(ph.current)
            g.damage_flash = DAMAGE_FLASH_DURATION
            g.camera.shake(PROJ_SHAKE_AMOUNT, PROJ_SHAKE_DURATION)
            g.particles.emit(pt.x + 10, pt.y + 14, 5, RED, 40, 0.3)
            g.dmg_numbers.append(
                (pt.x, pt.y - 16, str(dmg), RED, 0.8))
            to_remove.append(pid)
            if not ph.is_alive():
                g.dead = True
                g.dmg_numbers.append(
                    (pt.x, pt.y - 30, 'YOU DIED', RED, 2.5))
            break
    for pid in to_remove:
        from core.spatial import spatial_hash
        spatial_hash.remove(pid)
        g.em.destroy_entity(pid)


# ======================================================================
# HEALING & ENVIRONMENTAL
# ======================================================================

def campfire_heal(g: 'Game', dt: float, pt: Transform) -> None:
    g.campfire_heal_timer += dt
    if g.campfire_heal_timer < CAMPFIRE_HEAL_INTERVAL:
        return
    g.campfire_heal_timer = 0.0
    ph: Health = g.em.get_component(g.player_id, Health)
    if ph.current >= ph.maximum:
        return
    from core.spatial import spatial_hash
    candidates = spatial_hash.query_radius(pt.x, pt.y, CAMPFIRE_HEAL_RADIUS)
    for eid in candidates:
        if not g.em.has_component(eid, Placeable):
            continue
        pl: Placeable = g.em.get_component(eid, Placeable)
        if pl.item_type == 'campfire':
            t2: Transform = g.em.get_component(eid, Transform)
            if math.hypot(t2.x - pt.x, t2.y - pt.y) < CAMPFIRE_HEAL_RADIUS:
                ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
                vit_bonus = ps.vitality // VITALITY_CAMPFIRE_BONUS_PER
                amt = CAMPFIRE_BASE_HEAL + vit_bonus
                ph.heal(amt)
                g.health_bar.set_value(ph.current)
                g.dmg_numbers.append(
                    (pt.x, pt.y - 20, f'+{amt}', GREEN, 0.6))
                break


def night_damage(g: 'Game', dt: float, pt: Transform) -> None:
    if g.god_mode:
        return
    darkness = g.daynight.get_darkness()
    if darkness <= NIGHT_DARKNESS_THRESHOLD:
        g.night_dmg_timer = 0.0
        return
    g.night_dmg_timer += dt
    if g.night_dmg_timer < NIGHT_DAMAGE_INTERVAL:
        return
    g.night_dmg_timer = 0.0
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    near_light = (inv.get_equipped() == 'torch' and inv.has('torch'))
    if not near_light:
        # Fire enchant on equipped weapon counts as light
        # Check Equipment weapon slot first (always present regardless of hotbar)
        eq: Equipment = g.em.get_component(g.player_id, Equipment)
        ench = eq.enchantments.get('weapon') if eq else None
        if not ench:
            ench = inv.get_equipped_enchant()
        if ench and ench.get('type') == 'fire':
            near_light = True
    if not near_light:
        from core.spatial import spatial_hash
        candidates = spatial_hash.query_radius(pt.x, pt.y, LIGHT_SAFETY_RADIUS)
        for eid in candidates:
            if not g.em.has_component(eid, LightSource):
                continue
            t3: Transform = g.em.get_component(eid, Transform)
            if math.hypot(t3.x - pt.x, t3.y - pt.y) < LIGHT_SAFETY_RADIUS:
                near_light = True
                break
    if near_light:
        return
    ph: Health = g.em.get_component(g.player_id, Health)
    day = max(1, g.daynight.day_number)
    dmg = NIGHT_DAMAGE_BASE + NIGHT_DAMAGE_INCREASE * ((day - 1) // max(1, NIGHT_DAMAGE_INCREASE_FREQ))
    from data.difficulty import get_profile
    prof = get_profile(g.difficulty)
    dmg = int(dmg * prof['night_dmg_mult'])
    # Per-day flat bonus
    dmg += int((day - 1) * prof['night_dmg_per_day'])
    # Enforce min/max bounds from difficulty profile
    tick_min = int(prof['night_dmg_tick_min'])
    tick_max = int(prof['night_dmg_tick_max'])
    dmg = max(dmg, tick_min)
    if tick_max > 0:
        dmg = min(dmg, tick_max)
    ph.damage(dmg)
    g.health_bar.set_value(ph.current)
    g.damage_flash = 0.1
    g.dmg_numbers.append(
        (pt.x, pt.y - 20, str(dmg), RED, 0.8))
    if not ph.is_alive():
        g.dead = True


# ======================================================================
# SPEED RESTORES (ice slow)
# ======================================================================

def schedule_speed_restore(g: 'Game', eid: int, original_speed: float,
                           duration: float) -> None:
    g.speed_restores = [
        (e, s, t) for e, s, t in g.speed_restores if e != eid]
    g.speed_restores.append((eid, original_speed, duration))


def tick_speed_restores(g: 'Game', dt: float) -> None:
    remaining = []
    for eid, speed, timer in g.speed_restores:
        timer -= dt
        if timer <= 0:
            if g.em.has_component(eid, AI):
                ai_c: AI = g.em.get_component(eid, AI)
                ai_c.speed = speed
        else:
            remaining.append((eid, speed, timer))
    g.speed_restores = remaining
