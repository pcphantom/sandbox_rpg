"""Per-frame update tick — extracted from sandbox_rpg.Game._update."""
import pygame

from core.constants import (
    GREEN, GRAY, ENCHANT_COLOR_REGEN,
    PLAYER_BASE_SPEED, AGI_SPEED_BONUS, AGI_SPEED_BONUS_CAP,
    MOVEMENT_ACCEL_MULT, SPRITE_FLIP_THRESHOLD,
    MIN_ATTACK_COOLDOWN, BASE_ATTACK_COOLDOWN, AGILITY_COOLDOWN_REDUCTION,
    ATTACK_ANIM_DURATION, INTERACT_COOLDOWN,
    DMG_NUMBER_FLOAT_SPEED, HUD_REFRESH_INTERVAL,
    MOB_RESPAWN_INTERVAL, MOB_MAX_COUNT, MOB_RESPAWN_BATCH,
    DIFFICULTY_MULTIPLIERS,
)
from data import RESOURCE_RESPAWN_DAYS, CAVE_RESET_DAYS
from core.components import (
    Transform, Velocity, Renderable, Health, Inventory,
    AI, PlayerStats, Equipment, Placeable,
)
from game import entities as game_entities
from enchantments.effects import get_enchant_regen_rate


def update(g, dt: float) -> None:
    """Run one simulation tick.  ``g`` is the :class:`sandbox_rpg.Game` instance."""
    # Command bar timer update (runs even when no keys are pressed)
    g.command_bar.update(dt)

    keys = pygame.key.get_pressed()
    pv: Velocity = g.em.get_component(g.player_id, Velocity)
    pt: Transform = g.em.get_component(g.player_id, Transform)
    pr: Renderable = g.em.get_component(g.player_id, Renderable)
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)

    # Movement (AGI speed bonus with cap)
    agi_bonus = min(AGI_SPEED_BONUS_CAP, ps.agility * AGI_SPEED_BONUS)
    base_speed = PLAYER_BASE_SPEED * (1.0 + agi_bonus)
    if keys[pygame.K_w]:
        pv.vy -= base_speed * dt * MOVEMENT_ACCEL_MULT
    if keys[pygame.K_s]:
        pv.vy += base_speed * dt * MOVEMENT_ACCEL_MULT
    if keys[pygame.K_a]:
        pv.vx -= base_speed * dt * MOVEMENT_ACCEL_MULT
    if keys[pygame.K_d]:
        pv.vx += base_speed * dt * MOVEMENT_ACCEL_MULT
    if pv.vx < -SPRITE_FLIP_THRESHOLD:
        pr.flip_x = True
    elif pv.vx > SPRITE_FLIP_THRESHOLD:
        pr.flip_x = False

    # Systems tick
    g.movement.update(dt, g.em)
    g.physics.update(dt, g.em, g.world)
    # Calculate night damage multiplier for structures
    _struct_night_mult = 1
    _is_night = g.daynight.is_night() and g.in_cave < 0
    if _is_night:
        from data.difficulty import get_profile as _gp
        _struct_night_mult = int(_gp(g.difficulty).get('night_damage_multiplier', 1))
    g.ai_system.update(dt, g.em, g.player_id,
                       on_ranged_fire=g._on_enemy_ranged_fire,
                       night_structure_dmg_mult=_struct_night_mult,
                       is_night=_is_night)
    g.projectile_system.update(dt, g.em, on_hit=g._on_proj_hit)
    g.trap_system.update(dt, g.em, on_hit=g._on_trap_hit)
    g.turret_system.update(dt, g.em, on_fire=g._on_turret_fire)
    g.stone_oven_ui.update(g, dt)
    g.daynight.update(dt)

    # Day change — cave regeneration and resource respawn (per difficulty)
    if g.daynight.day_changed:
        day = g.daynight.day_number
        # Cave regeneration (controlled by CAVE_RESET_DAYS per difficulty)
        cave_interval = CAVE_RESET_DAYS.get(g.difficulty, 1)
        if cave_interval > 0 and (day - g._last_cave_reset_day) >= cave_interval:
            if g.in_cave >= 0:
                g._exit_cave()
            g.caves.regenerate(day)
            g.cave_snapshots.clear()
            g._last_cave_reset_day = day
        # Resource respawn (controlled by RESOURCE_RESPAWN_DAYS per difficulty)
        res_interval = RESOURCE_RESPAWN_DAYS.get(g.difficulty, 0)
        if res_interval > 0 and (day - g._last_resource_respawn_day) >= res_interval:
            game_entities.respawn_resources(g)
            g._last_resource_respawn_day = day

    g.music_manager.update(g.daynight.is_night())
    g.camera.follow(pt.x, pt.y)
    g.camera.update(dt)
    g.particles.update(dt)

    # Cave teleport check
    g._check_cave_teleport(pt)

    # Wave system — disabled inside caves
    if g.in_cave < 0:
        wave_req = g.wave_system.update(
            dt, g.daynight.is_night(), g.daynight.day_number)
        if wave_req:
            g._spawn_wave_mobs(
                wave_req['count'], wave_req['tier'],
                include_ranged=wave_req.get('ranged', False),
                include_boss=wave_req.get('boss', False))
            if g.wave_system.wave_spawned <= wave_req['count']:
                g._notify("Defend yourself!", 2.5)

    # Sleeping (bed mechanic) — only speeds night while on bed
    if g.sleeping:
        g.sleep_timer -= dt
        if g.sleep_timer <= 0 or not g.daynight.is_night():
            g.sleeping = False
            g.daynight.reset_speed()
            g._notify("You wake up refreshed.")

    # Cooldowns
    g.interact_cd = max(0, g.interact_cd - dt)
    g.attack_cd = max(0, g.attack_cd - dt)
    g.attack_anim = max(0, g.attack_anim - dt)
    g.ranged_cd = max(0, g.ranged_cd - dt)
    g.player_hit_cd = max(0, g.player_hit_cd - dt)
    g.damage_flash = max(0, g.damage_flash - dt)
    g.notification_timer = max(0, g.notification_timer - dt)
    g.cave_teleport_cd = max(0, g.cave_teleport_cd - dt)

    # Spell cooldowns
    expired_spells = [k for k, v in g.spell_cooldowns.items()
                      if v - dt <= 0]
    for k in expired_spells:
        del g.spell_cooldowns[k]
    for k in list(g.spell_cooldowns):
        g.spell_cooldowns[k] -= dt

    # Spell buff ticking
    expired_buffs = []
    for effect, (level, value, remaining) in g.active_buffs.items():
        remaining -= dt
        if remaining <= 0:
            expired_buffs.append(effect)
        else:
            g.active_buffs[effect] = (level, value, remaining)
    for effect in expired_buffs:
        del g.active_buffs[effect]
        g._notify(f"{effect.title()} buff expired.")
    # Regen buff: heal 'value' HP per second
    if 'regen' in g.active_buffs:
        _, regen_val, _ = g.active_buffs['regen']
        g.buff_regen_accum += dt
        if g.buff_regen_accum >= 1.0:
            g.buff_regen_accum -= 1.0
            ph_r: Health = g.em.get_component(g.player_id, Health)
            if ph_r.current < ph_r.maximum:
                ph_r.heal(int(regen_val))
                g.health_bar.set_value(ph_r.current)
                g.dmg_numbers.append(
                    (pt.x, pt.y - 20, f'+{int(regen_val)}', GREEN, 0.5))
    else:
        g.buff_regen_accum = 0.0

    # Armor regen enchant: passive HP/sec while regen-enchanted armor is equipped
    eq_regen: Equipment = g.em.get_component(g.player_id, Equipment)
    armor_ench = eq_regen.enchantments.get('armor')
    armor_regen_rate = get_enchant_regen_rate(armor_ench)
    if armor_regen_rate > 0:
        g.armor_regen_accum += dt
        if g.armor_regen_accum >= 1.0:
            g.armor_regen_accum -= 1.0
            ph_ar: Health = g.em.get_component(g.player_id, Health)
            if ph_ar.current < ph_ar.maximum:
                ph_ar.heal(armor_regen_rate)
                g.health_bar.set_value(ph_ar.current)
                g.dmg_numbers.append(
                    (pt.x, pt.y - 24, f'+{armor_regen_rate}', ENCHANT_COLOR_REGEN, 0.5))
    else:
        g.armor_regen_accum = 0.0

    # Ice slow speed restores
    g._tick_speed_restores(dt)

    # Melee attack
    if keys[pygame.K_SPACE] and g.attack_cd == 0:
        g._attack()
        cd = max(MIN_ATTACK_COOLDOWN,
                 BASE_ATTACK_COOLDOWN - ps.agility * AGILITY_COOLDOWN_REDUCTION)
        g.attack_cd = cd
        g.attack_anim = ATTACK_ANIM_DURATION

    # Ranged attack (R key)
    if keys[pygame.K_r] and g.ranged_cd == 0:
        g._ranged_attack()

    # Interact
    if keys[pygame.K_e] and g.interact_cd == 0:
        g._interact()
        g.interact_cd = INTERACT_COOLDOWN

    # Damage numbers decay
    g.dmg_numbers = [
        (x, y - DMG_NUMBER_FLOAT_SPEED * dt, t, c, l - dt)
        for x, y, t, c, l in g.dmg_numbers if l - dt > 0
    ]

    # Kill dead mobs
    for eid in list(g.em.get_entities_with(Health, AI)):
        h: Health = g.em.get_component(eid, Health)
        if not h.is_alive():
            g._on_mob_killed(eid)

    # Kill dead placeables
    for eid in list(g.em.get_entities_with(Health, Placeable)):
        if g.em.has_component(eid, AI):
            continue
        h = g.em.get_component(eid, Health)
        if not h.is_alive():
            td = g.em.get_component(eid, Transform)
            g.particles.emit(td.x + 10, td.y + 10, 8, GRAY, 40, 0.3)
            if g.active_chest == eid:
                g.show_chest = False
                g.active_chest = None
                g.chest_ui.split_dialog.close()
            if g.active_enchant_table == eid:
                g.show_enchant_table = False
                g.active_enchant_table = None
            g.em.destroy_entity(eid)

    # Mob contact damage
    g._check_contact_damage(pt)

    # Enemy projectile damage to player
    g._check_enemy_projectile_damage(pt)

    # Campfire healing
    g._campfire_heal(dt, pt)

    # Night damage
    g._night_damage(dt, pt)

    # Mob respawning — disabled inside caves
    if g.in_cave < 0:
        g.mob_spawn_timer += dt
        _, _, spawn_mult, _ = DIFFICULTY_MULTIPLIERS.get(
            g.difficulty, (1.0, 1.0, 1.0, 1.0))
        respawn_interval = MOB_RESPAWN_INTERVAL / spawn_mult
        if g.mob_spawn_timer > respawn_interval:
            g.mob_spawn_timer = 0.0
            mob_count = len(g.em.get_entities_with(AI))
            if mob_count < MOB_MAX_COUNT:
                # Spawn a batch when population is low
                batch = min(MOB_RESPAWN_BATCH, MOB_MAX_COUNT - mob_count)
                for _ in range(batch):
                    g._spawn_mob()

    # HUD refresh
    g.survival_timer += dt
    if g.survival_timer > HUD_REFRESH_INTERVAL:
        g.survival_timer = 0.0
        ph: Health = g.em.get_component(g.player_id, Health)
        g.health_bar.max_value = ph.maximum
        g.health_bar.set_value(ph.current)
        g.xp_bar.max_value = ps.xp_to_next
        g.xp_bar.set_value(ps.xp)
