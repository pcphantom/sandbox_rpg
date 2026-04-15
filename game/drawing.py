"""Drawing / rendering functions extracted from Game class.

All functions receive the Game instance as their first argument ``g``.
"""
from __future__ import annotations
import math
from typing import TYPE_CHECKING, Tuple

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from game.interaction import _WALL_ITEM_IDS

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT,
    BLACK, WHITE, GRAY, DARK_GRAY, RED, GREEN, CYAN, ORANGE, YELLOW,
    LIGHT_BLUE,
    TILE_WATER, TILE_SAND, TILE_GRASS, TILE_DIRT, TILE_STONE_FLOOR,
    TILE_STONE_WALL, TILE_FOREST, TILE_CAVE_FLOOR, TILE_CAVE_ENTRANCE,
    DIFFICULTY_NAMES,
    PLACEMENT_PREVIEW_COLOR, PLACEMENT_INVALID_COLOR,
    PLACEMENT_UPGRADE_PREVIEW_COLOR,
    ATTACK_ANIM_DURATION, DAMAGE_FLASH_DURATION,
    MOB_HP_BAR_W, MOB_HP_BAR_H, PLACEABLE_HP_BAR_W, PLACEABLE_HP_BAR_H,
    HOTBAR_SLOTS, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_GAP,
    PLAYER_TORCH_LIGHT_RADIUS,
    REPAIR_RANGE,
    UI_NOTIFICATION_TEXT, UI_ENCHANT_FALLBACK,
    STONE_WALL_OVERLAY, STONE_WALL_BORDER,
    LIGHT_COLOR_TORCH, LIGHT_COLOR_FIRE_ENCHANT,
    MOB_HP_BAR_BG, MOB_HP_BAR_FILL,
    PLACEABLE_HP_BAR_BG, PLACEABLE_HP_BAR_FILL,
    HOTBAR_BORDER, HOTBAR_SLOT_SELECTED_BG, HOTBAR_SLOT_NORMAL_BG,
    HOTBAR_SELECTED_BORDER, HOTBAR_NORMAL_BORDER, HOTBAR_SLOT_NUMBER_COLOR,
    HUD_STATUS_TEXT, HUD_RESOURCE_TEXT,
    PERIOD_COLOR_DAY, PERIOD_COLOR_DAWN, PERIOD_COLOR_DUSK, PERIOD_COLOR_NIGHT,
    HUD_DUSK_WARNING, HUD_WORLD_EDGE_WARNING, HUD_CONTROL_HINT,
    HUD_BED_PROMPT_TEXT,
    HUD_REPAIR_DAMAGED_TEXT, HUD_REPAIR_NORMAL_TEXT,
    DEATH_BUTTON_HOVER, DEATH_BUTTON_NORMAL,
    PLACEMENT_UPGRADE_BORDER, PLACEMENT_VALID_BORDER, PLACEMENT_INVALID_BORDER,
    SPELL_TARGET_RETICLE, SPELL_HELP_TEXT,
)
from data.day_night import (
    DAY_FLASH_FADE_DIVISOR, DAY_FLASH_TEXT, DAY_FLASH_COLOR,
    NIGHT_FLASH_FADE_DIVISOR, NIGHT_FLASH_TEXT, NIGHT_FLASH_COLOR,
    SLEEP_OVERLAY_TEXT, SLEEP_OVERLAY_COLOR,
)
from core.components import (
    Transform, Renderable, Health, Inventory, AI, PlayerStats,
    Equipment, Placeable, LightSource, Building, Storage, Turret,
)
from data import ITEM_DATA, SPELL_DATA, SPELL_RECHARGE
from game import save_load


# ======================================================================
# MAIN RENDER
# ======================================================================

def render(g: 'Game') -> None:
    g.screen.fill(BLACK)
    g.tooltip.clear()
    draw_world(g)
    draw_elite_outlines(g)   # outlines BEHIND sprites
    g.renderer.update(g.em, g.camera)
    draw_boss_glow(g)        # boss aura ON TOP (large pulsing circle)
    draw_mob_health_bars(g)
    draw_placeable_health_bars(g)
    if g.attack_anim > 0:
        draw_attack_arc(g)
    g.particles.draw(g.screen, g.camera.x, g.camera.y)
    draw_damage_numbers(g)
    draw_lighting(g)
    if g.damage_flash > 0:
        fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        alpha = int(80 * (g.damage_flash / DAMAGE_FLASH_DURATION))
        fs.fill((255, 0, 0, min(255, alpha)))
        g.screen.blit(fs, (0, 0))
    if g.placement_mode and g.placement_item:
        draw_placement_preview(g)
    if g.spell_targeting:
        draw_spell_targeting(g)
    draw_hud(g)
    draw_hotbar(g)

    # Minimap
    mob_pos = []
    for eid in g.em.get_entities_with(Transform, AI):
        mt = g.em.get_component(eid, Transform)
        mob_pos.append((mt.x, mt.y))
    build_pos = []
    for eid in g.em.get_entities_with(Transform, Building):
        bt = g.em.get_component(eid, Transform)
        build_pos.append((bt.x, bt.y))
    pt: Transform = g.em.get_component(g.player_id, Transform)
    g.minimap.draw(g.screen, g.world, pt.x, pt.y, mob_pos, build_pos)

    # Cheats button (below minimap, visible when cheats enabled)
    if g.cheats_enabled:
        _draw_cheats_button(g)

    # Overlays
    if g.show_chest and g.active_chest is not None:
        stor = g.em.get_component(g.active_chest, Storage)
        if stor:
            is_cave = not g.em.has_component(g.active_chest, Building)
            g.chest_ui.draw(
                g.screen, stor,
                g.em.get_component(g.player_id, Inventory),
                g.tooltip, is_cave_chest=is_cave)
    if g.show_enchant_table and g.active_enchant_table is not None:
        stor = g.em.get_component(g.active_enchant_table, Storage)
        if stor:
            g.enchant_table_ui.draw(
                g.screen, stor,
                g.em.get_component(g.player_id, Inventory),
                g.tooltip)
    if g.show_stone_oven:
        g.stone_oven_ui.draw(g.screen, g)
    if g.show_inventory:
        g.inventory_ui.draw(g.screen, g.tooltip)
    if g.show_crafting:
        g.crafting_ui.draw(
            g.screen,
            g.em.get_component(g.player_id, Inventory),
            g.tooltip)
    if g.show_character:
        g.character_menu.draw(
            g.screen,
            g.em.get_component(g.player_id, PlayerStats),
            g.em.get_component(g.player_id, Equipment),
            g.em.get_component(g.player_id, Health),
            g.em.get_component(g.player_id, Inventory),
            g.tooltip)
    if g.paused:
        g.pause_menu.draw(g.screen, save_load.list_slots())
    if g.notification_timer > 0:
        alpha = min(1.0, g.notification_timer / 0.5)
        ns = g.font.render(g.notification, True, UI_NOTIFICATION_TEXT)
        nbg = pygame.Surface((ns.get_width() + 20, ns.get_height() + 8),
                             pygame.SRCALPHA)
        nbg.fill((10, 10, 20, int(180 * alpha)))
        nx = SCREEN_WIDTH // 2 - ns.get_width() // 2
        ny = SCREEN_HEIGHT // 2 + 120
        g.screen.blit(nbg, (nx - 10, ny - 4))
        g.screen.blit(ns, (nx, ny))
    # Command bar overlay (F12)
    g.command_bar.draw(g.screen)
    # Cheat help overlay
    if g.show_cheat_help:
        _draw_cheat_help(g)
    g.tooltip.draw(g.screen)
    if g.dead:
        draw_death_screen(g)

    # Sleeping overlay
    if g.sleeping:
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 30, 140))
        g.screen.blit(ov, (0, 0))
        zt = g.font_lg.render(SLEEP_OVERLAY_TEXT, True, SLEEP_OVERLAY_COLOR)
        g.screen.blit(zt, (SCREEN_WIDTH // 2 - zt.get_width() // 2,
                            SCREEN_HEIGHT // 2 - 20))

    # Day number flash
    if g.daynight._day_flash_timer > 0:
        alpha = min(1.0, g.daynight._day_flash_timer / DAY_FLASH_FADE_DIVISOR)
        dt_text = g.font_xl.render(
            DAY_FLASH_TEXT.format(day=g.daynight.day_number), True, DAY_FLASH_COLOR)
        dt_text.set_alpha(int(255 * alpha))
        g.screen.blit(dt_text,
                       (SCREEN_WIDTH // 2 - dt_text.get_width() // 2,
                        SCREEN_HEIGHT // 4))

    # Night warning flash
    if g.daynight._night_flash_timer > 0:
        alpha = min(1.0, g.daynight._night_flash_timer / NIGHT_FLASH_FADE_DIVISOR)
        nt = g.font_lg.render(NIGHT_FLASH_TEXT, True, NIGHT_FLASH_COLOR)
        nt.set_alpha(int(255 * alpha))
        g.screen.blit(nt,
                       (SCREEN_WIDTH // 2 - nt.get_width() // 2,
                        SCREEN_HEIGHT // 4 + 60))

    g._present()


# ======================================================================
# WORLD TILES
# ======================================================================

def draw_world(g: 'Game') -> None:
    sx_start = max(0, int(g.camera.x // TILE_SIZE) - 1)
    sx_end = min(g.world.width,
                 int((g.camera.x + SCREEN_WIDTH) // TILE_SIZE) + 2)
    sy_start = max(0, int(g.camera.y // TILE_SIZE) - 1)
    sy_end = min(g.world.height,
                 int((g.camera.y + SCREEN_HEIGHT) // TILE_SIZE) + 2)
    tile_surfs = {
        TILE_WATER: g.textures.get('water_0'),
        TILE_SAND: g.textures.get('sand'),
        TILE_GRASS: g.textures.get('grass'),
        TILE_DIRT: g.textures.get('dirt'),
        TILE_STONE_FLOOR: g.textures.get('stone'),
        TILE_STONE_WALL: g.textures.get('stone'),
        TILE_FOREST: g.textures.get('forest'),
        TILE_CAVE_FLOOR: g.textures.get('cave_floor'),
        TILE_CAVE_ENTRANCE: g.textures.get('cave_entrance'),
    }
    default_surf = g.textures.get('grass')
    for x in range(sx_start, sx_end):
        for y in range(sy_start, sy_end):
            tile = g.world.get_tile(x, y)
            scx = int(x * TILE_SIZE - g.camera.x)
            scy = int(y * TILE_SIZE - g.camera.y)
            g.screen.blit(tile_surfs.get(tile, default_surf), (scx, scy))
            if tile == TILE_STONE_WALL:
                pygame.draw.rect(g.screen, STONE_WALL_OVERLAY,
                                 (scx, scy, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(g.screen, STONE_WALL_BORDER,
                                 (scx, scy, TILE_SIZE, TILE_SIZE), 2)


# ======================================================================
# LIGHTING
# ======================================================================

# Cache: (radius, color_r, color_g, color_b) -> pre-blitted light surface
_light_surface_cache: dict[tuple[int, int, int, int], pygame.Surface] = {}


def _get_light_surface(radius: int,
                       color: Tuple[int, int, int]) -> pygame.Surface:
    """Return a cached concentric-ring light punch surface."""
    key = (radius, color[0], color[1], color[2])
    surf = _light_surface_cache.get(key)
    if surf is not None:
        return surf
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 15, -18):
        ts = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        a = int(30 * (r / radius))
        pygame.draw.circle(
            ts, (color[0], color[1], color[2], max(1, a)), (r, r), r)
        surf.blit(ts, (radius - r, radius - r),
                  special_flags=pygame.BLEND_RGBA_SUB)
    _light_surface_cache[key] = surf
    return surf


def draw_lighting(g: 'Game') -> None:
    darkness = g.daynight.get_darkness()
    lights = g.em.get_entities_with(Transform, LightSource)
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    has_torch = inv.get_equipped() == 'torch' and inv.has('torch')
    # Fire enchant on equipped weapon also provides light
    fire_light_radius = 0
    # Check Equipment weapon slot first (always available regardless of hotbar)
    eq: Equipment = g.em.get_component(g.player_id, Equipment)
    ench = eq.enchantments.get('weapon') if eq else None
    # Hotbar enchant can also provide light (e.g. fire-enchanted torch/weapon in hand)
    if not ench:
        ench = inv.get_equipped_enchant()
    if ench and ench.get('type') == 'fire':
        from enchantments.effects import get_enchant_light_radius
        fire_light_radius = get_enchant_light_radius(ench)
    if darkness < 0.05 and not lights and not has_torch and not fire_light_radius:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    base_alpha = int(darkness * 210)
    overlay.fill((5, 5, 20, base_alpha))

    def punch_light(sx: int, sy: int, radius: int,
                    color: Tuple[int, int, int]) -> None:
        light_surf = _get_light_surface(radius, color)
        overlay.blit(light_surf, (sx - radius, sy - radius),
                     special_flags=pygame.BLEND_RGBA_SUB)

    for eid in lights:
        t: Transform = g.em.get_component(eid, Transform)
        ls: LightSource = g.em.get_component(eid, LightSource)
        lx = int(t.x - g.camera.x + 12)
        ly = int(t.y - g.camera.y + 12)
        punch_light(lx, ly, ls.radius, ls.color)

    if has_torch:
        pt: Transform = g.em.get_component(g.player_id, Transform)
        lx = int(pt.x - g.camera.x + 10)
        ly = int(pt.y - g.camera.y + 14)
        punch_light(lx, ly, PLAYER_TORCH_LIGHT_RADIUS, LIGHT_COLOR_TORCH)

    if fire_light_radius > 0:
        pt2: Transform = g.em.get_component(g.player_id, Transform)
        lx = int(pt2.x - g.camera.x + 10)
        ly = int(pt2.y - g.camera.y + 14)
        punch_light(lx, ly, fire_light_radius, LIGHT_COLOR_FIRE_ENCHANT)

    g.screen.blit(overlay, (0, 0))


# ======================================================================
# HEALTH BARS
# ======================================================================

def draw_mob_health_bars(g: 'Game') -> None:
    for eid in g.em.get_entities_with(Transform, Health, AI):
        t: Transform = g.em.get_component(eid, Transform)
        h: Health = g.em.get_component(eid, Health)
        if h.current >= h.maximum:
            continue
        sx = int(t.x - g.camera.x)
        sy = int(t.y - g.camera.y - 8)
        pygame.draw.rect(g.screen, MOB_HP_BAR_BG,
                         (sx, sy, MOB_HP_BAR_W, MOB_HP_BAR_H))
        fill = int(MOB_HP_BAR_W * h.current / h.maximum)
        pygame.draw.rect(g.screen, MOB_HP_BAR_FILL,
                         (sx, sy, fill, MOB_HP_BAR_H))


def draw_placeable_health_bars(g: 'Game') -> None:
    for eid in g.em.get_entities_with(Transform, Health, Placeable):
        if g.em.has_component(eid, AI):
            continue
        t: Transform = g.em.get_component(eid, Transform)
        h: Health = g.em.get_component(eid, Health)
        if h.current >= h.maximum:
            continue
        sx = int(t.x - g.camera.x)
        sy = int(t.y - g.camera.y - 6)
        pygame.draw.rect(g.screen, PLACEABLE_HP_BAR_BG,
                         (sx, sy, PLACEABLE_HP_BAR_W, PLACEABLE_HP_BAR_H))
        fill = int(PLACEABLE_HP_BAR_W * h.current / h.maximum)
        pygame.draw.rect(g.screen, PLACEABLE_HP_BAR_FILL,
                         (sx, sy, fill, PLACEABLE_HP_BAR_H))


# ======================================================================
# ATTACK ARC
# ======================================================================

def draw_attack_arc(g: 'Game') -> None:
    pt: Transform = g.em.get_component(g.player_id, Transform)
    pr: Renderable = g.em.get_component(g.player_id, Renderable)
    cx = int(pt.x - g.camera.x + 10)
    cy = int(pt.y - g.camera.y + 14)
    d = -1 if pr.flip_x else 1
    ax = cx + d * 20
    alpha = int(200 * (g.attack_anim / ATTACK_ANIM_DURATION))
    arc = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.arc(arc, (255, 255, 200, alpha),
                    pygame.Rect(0, 0, 40, 40),
                    -0.8 if d > 0 else 2.3,
                    0.8 if d > 0 else 3.9, 3)
    g.screen.blit(arc, (ax - 20, cy - 20))


# ======================================================================
# DAMAGE NUMBERS
# ======================================================================

def draw_damage_numbers(g: 'Game') -> None:
    for x, y, txt, color, ttl in g.dmg_numbers:
        sx = int(x - g.camera.x)
        sy = int(y - g.camera.y)
        bold = (txt.startswith('+') or txt.startswith('LEVEL')
                or txt == 'YOU DIED')
        f = g.font_lg if bold else g.font
        surf = f.render(txt, True, color)
        g.screen.blit(surf, (sx - surf.get_width() // 2, sy))


# ======================================================================
# HOTBAR
# ======================================================================

def draw_hotbar(g: 'Game') -> None:
    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    slots = HOTBAR_SLOTS
    ss = HOTBAR_SLOT_SIZE
    gap = HOTBAR_SLOT_GAP
    tw = slots * ss + (slots - 1) * gap
    bx = g.action_bar_mgr.primary_x
    by = g.action_bar_mgr.primary_y
    mx, my = pygame.mouse.get_pos()

    bg = pygame.Surface((tw + 16, ss + 12), pygame.SRCALPHA)
    bg.fill((15, 15, 25, 180))
    g.screen.blit(bg, (bx - 8, by - 6))
    pygame.draw.rect(g.screen, HOTBAR_BORDER,
                     (bx - 8, by - 6, tw + 16, ss + 12), 1, border_radius=6)

    for i in range(slots):
        x = bx + i * (ss + gap)
        rect = pygame.Rect(x, by, ss, ss)
        sel = i == inv.equipped_slot
        bg_c = HOTBAR_SLOT_SELECTED_BG if sel else HOTBAR_SLOT_NORMAL_BG
        pygame.draw.rect(g.screen, bg_c, rect, border_radius=5)
        bd = HOTBAR_SELECTED_BORDER if sel else HOTBAR_NORMAL_BORDER
        pygame.draw.rect(g.screen, bd, rect, 2, border_radius=5)
        ns = g.font_sm.render(str(i + 1), True, HOTBAR_SLOT_NUMBER_COLOR)
        g.screen.blit(ns, (x + 3, by + 2))
        if i in inv.hotbar:
            item_id, count = inv.hotbar[i]
            icon = g.textures.cache.get(f'item_{item_id}')
            if icon:
                g.screen.blit(
                    pygame.transform.scale(icon, (32, 32)),
                    (x + 8, by + 8))
            if count > 1:
                cs = g.font_sm.render(str(count), True, WHITE)
                g.screen.blit(
                    cs, (x + ss - cs.get_width() - 3,
                         by + ss - cs.get_height() - 2))
            # -- Spell cooldown overlay (grey shrinks top→bottom) --
            if item_id in g.spell_cooldowns:
                remaining = g.spell_cooldowns[item_id]
                sdata = SPELL_DATA.get(item_id)
                total = sdata['cooldown'] if sdata else SPELL_RECHARGE
                frac = max(0.0, min(1.0, remaining / total))
                oh = int(ss * frac)
                if oh > 0:
                    overlay = pygame.Surface((ss, oh), pygame.SRCALPHA)
                    overlay.fill((40, 40, 40, 160))
                    g.screen.blit(overlay, (x, by))
            # -- Rarity border (the ONLY item border) --
            hb_ench = inv.hotbar_enchantments.get(i)
            hb_rar = inv.hotbar_rarities.get(i, 'common')
            if hb_rar and hb_rar != 'common':
                from ui.rarity_display import draw_rarity_border
                draw_rarity_border(g.screen, rect, hb_rar)
            if rect.collidepoint(mx, my) and item_id in ITEM_DATA:
                d = ITEM_DATA[item_id]
                name = d[0]
                hb_rar = inv.hotbar_rarities.get(i, 'common')
                if hb_rar and hb_rar != 'common':
                    name = f"{hb_rar.title()} {name}"
                from data.quality import get_stat_description
                lines = [name, get_stat_description(item_id, hb_rar)]
                colors = [WHITE, WHITE]
                if hb_rar and hb_rar != 'common':
                    from data.quality import get_rarity_color
                    colors[0] = get_rarity_color(hb_rar)
                if hb_ench:
                    from enchantments.effects import (
                        get_enchant_display_prefix, ENCHANT_COLORS as EC2,
                    )
                    prefix = get_enchant_display_prefix(hb_ench)
                    if prefix:
                        lines[0] = f"{prefix} {name}"
                        colors[0] = EC2.get(hb_ench['type'], colors[0])
                    ench_line = (f"Enchant: {hb_ench['type'].title()}"
                                 f" Lv.{hb_ench['level']}")
                    lines.insert(1, ench_line)
                    colors.insert(1, EC2.get(hb_ench['type'], CYAN))
                if hb_rar and hb_rar != 'common':
                    from ui.rarity_display import insert_rarity_tooltip
                    insert_rarity_tooltip(lines, colors, hb_rar)
                g.tooltip.show(lines, (mx, my), colors)
    # Equipped item name below hotbar
    eq_item = inv.get_equipped()
    if eq_item and eq_item in ITEM_DATA:
        eq_ench = inv.get_equipped_enchant()
        eq_rar = inv.get_equipped_rarity()
        name = ITEM_DATA[eq_item][0]
        name_color = UI_NOTIFICATION_TEXT
        if eq_rar and eq_rar != 'common':
            name = f"{eq_rar.title()} {name}"
            from data.quality import get_rarity_color
            name_color = get_rarity_color(eq_rar)
        if eq_ench:
            from enchantments.effects import (
                get_enchant_display_prefix, ENCHANT_COLORS as EC3,
            )
            prefix = get_enchant_display_prefix(eq_ench)
            if prefix:
                name = f"{prefix} {name}"
                name_color = EC3.get(eq_ench['type'], name_color)
        nt = g.font.render(name, True, name_color)
        name_cx = bx + tw // 2
        g.screen.blit(nt, (name_cx - nt.get_width() // 2, by - 22))

    # Draw extra action bars
    g.action_bar_mgr.draw_extra_bars(g.screen, g)


# ======================================================================
# HUD
# ======================================================================

def draw_hud(g: 'Game') -> None:
    hud_bg = pygame.Surface((250, 88), pygame.SRCALPHA)
    hud_bg.fill((10, 10, 20, 150))
    g.screen.blit(hud_bg, (12, 10))

    g.health_bar.draw(g.screen)
    ph: Health = g.em.get_component(g.player_id, Health)
    ht = g.font_sm.render(f"HP {ph.current}/{ph.maximum}", True, WHITE)
    g.screen.blit(ht, (24, 17))

    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    g.xp_bar.draw(g.screen)
    xt = g.font_sm.render(
        f"Lv.{ps.level}  XP {ps.xp}/{ps.xp_to_next}", True,
        HUD_STATUS_TEXT)
    g.screen.blit(xt, (24, 39))

    inv: Inventory = g.em.get_component(g.player_id, Inventory)
    res = (f"Wood:{inv.count('wood')}  Stone:{inv.count('stone')}"
           f"  Iron:{inv.count('iron')}")
    g.screen.blit(g.font_sm.render(res, True, HUD_RESOURCE_TEXT), (20, 58))
    row2 = f"Day:{g.daynight.day_number}  Kills:{ps.kills}"
    g.screen.blit(g.font_sm.render(row2, True, HUD_RESOURCE_TEXT), (20, 74))

    # Time of day + Day number
    period = g.daynight.get_period_name()
    period_colors = {'Day': PERIOD_COLOR_DAY, 'Dawn': PERIOD_COLOR_DAWN,
                     'Dusk': PERIOD_COLOR_DUSK, 'Night': PERIOD_COLOR_NIGHT}
    pc = period_colors.get(period, WHITE)
    tr_bg = pygame.Surface((200, 55), pygame.SRCALPHA)
    tr_bg.fill((10, 10, 20, 150))
    g.screen.blit(tr_bg, (SCREEN_WIDTH - 210, 8))
    day_str = f"Day {g.daynight.day_number}  {period}"
    g.screen.blit(g.font.render(day_str, True, pc),
                  (SCREEN_WIDTH - 200, 14))
    t_str = (f"{int(g.daynight.time * 24):02d}"
             f":{int((g.daynight.time * 1440) % 60):02d}")
    diff_name = (DIFFICULTY_NAMES[g.difficulty]
                 if 0 <= g.difficulty < len(DIFFICULTY_NAMES) else "?")
    g.screen.blit(g.font_sm.render(
        f"{t_str}   [{diff_name}]", True, GRAY),
        (SCREEN_WIDTH - 200, 36))

    # Wave info
    if g.wave_system.wave_active:
        wave_txt = "DEFEND!"
        wt = g.font.render(wave_txt, True, RED)
        wbg = pygame.Surface((wt.get_width() + 16, wt.get_height() + 6),
                             pygame.SRCALPHA)
        wbg.fill((40, 10, 10, 180))
        wx = SCREEN_WIDTH // 2 - wt.get_width() // 2
        g.screen.blit(wbg, (wx - 8, 8))
        g.screen.blit(wt, (wx, 11))

    # Cave indicator
    if g.in_cave >= 0:
        cave_txt = f"CAVE {g.in_cave + 1}"
        ct_surf = g.font.render(cave_txt, True, ORANGE)
        cbg = pygame.Surface((ct_surf.get_width() + 16,
                              ct_surf.get_height() + 6), pygame.SRCALPHA)
        cbg.fill((30, 20, 5, 180))
        cx = SCREEN_WIDTH // 2 - ct_surf.get_width() // 2
        g.screen.blit(cbg, (cx - 8, 30))
        g.screen.blit(ct_surf, (cx, 33))

    # Active buffs
    buff_y = 76
    buff_colors = {'regen': GREEN, 'protection': LIGHT_BLUE, 'strength': RED}
    for effect, (level, value, remaining) in g.active_buffs.items():
        bc = buff_colors.get(effect, WHITE)
        bt = g.font_sm.render(
            f"{effect.title()} {level}  {remaining:.0f}s", True, bc)
        g.screen.blit(bt, (20, buff_y))
        buff_y += 14

    # Spell cooldowns
    if g.spell_cooldowns:
        for spell_id, cd_remaining in g.spell_cooldowns.items():
            sdata = SPELL_DATA.get(spell_id)
            if sdata:
                sct = g.font_sm.render(
                    f"{sdata['name']}: {cd_remaining:.1f}s", True, GRAY)
                g.screen.blit(sct, (20, buff_y))
                buff_y += 14

    # Warnings — only during dusk (evening)
    dn_period = g.daynight.get_period_name()
    if dn_period == "Dusk":
        wt = g.font.render("Night approaches... find light!",
                            True, HUD_DUSK_WARNING)
        g.screen.blit(wt, (SCREEN_WIDTH // 2 - wt.get_width() // 2, 70))
    pt: Transform = g.em.get_component(g.player_id, Transform)
    tx, ty = pt.x / TILE_SIZE, pt.y / TILE_SIZE
    if (tx < 4 or tx > WORLD_WIDTH - 4
            or ty < 4 or ty > WORLD_HEIGHT - 4):
        et = g.font.render("~ Edge of the World ~", True, HUD_WORLD_EDGE_WARNING)
        g.screen.blit(et, (SCREEN_WIDTH // 2 - et.get_width() // 2, 94))

    # Controls hint
    if not (g.show_inventory or g.show_crafting
            or g.show_character or g.show_chest
            or g.show_stone_oven or g.paused):
        controls = [
            "WASD  Move",
            "Space Attack",
            "R     Ranged",
            "E     Harvest",
            "F     Use Item",
            "I     Inventory",
            "C     Crafting",
            "P     Stats",
            "Esc   Menu",
        ]
        line_h = 15
        ctrl_x = 14
        ctrl_y = SCREEN_HEIGHT - len(controls) * line_h - 80
        bg_w = 120
        bg_h = len(controls) * line_h + 6
        ctrl_bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        ctrl_bg.fill((10, 10, 20, 120))
        g.screen.blit(ctrl_bg, (ctrl_x - 4, ctrl_y - 3))
        for i, line in enumerate(controls):
            cs = g.font_sm.render(line, True, HUD_CONTROL_HINT)
            g.screen.blit(cs, (ctrl_x, ctrl_y + i * line_h))

    # Contextual bed prompt
    if not g.sleeping and g.daynight.is_night():
        pt_bed: Transform = g.em.get_component(g.player_id, Transform)
        for eid in g.em.get_entities_with(Transform, Placeable):
            pl = g.em.get_component(eid, Placeable)
            if pl.item_type == 'bed':
                bt = g.em.get_component(eid, Transform)
                if math.hypot(bt.x - pt_bed.x, bt.y - pt_bed.y) < 50:
                    bed_txt = g.font.render(
                        "Press F to Sleep", True, HUD_BED_PROMPT_TEXT)
                    bed_bg = pygame.Surface(
                        (bed_txt.get_width() + 16,
                         bed_txt.get_height() + 8), pygame.SRCALPHA)
                    bed_bg.fill((10, 10, 30, 160))
                    bbx = SCREEN_WIDTH // 2 - bed_txt.get_width() // 2
                    bby = SCREEN_HEIGHT // 2 + 60
                    g.screen.blit(bed_bg, (bbx - 8, bby - 4))
                    g.screen.blit(bed_txt, (bbx, bby))
                    break

    # Contextual hammer repair prompt
    inv_h: Inventory = g.em.get_component(g.player_id, Inventory)
    if inv_h.get_equipped() == 'hammer':
        pt_h: Transform = g.em.get_component(g.player_id, Transform)
        px_h, py_h = pt_h.x + 10, pt_h.y + 14
        for eid in g.em.get_entities_with(Transform, Placeable, Health):
            if g.em.has_component(eid, AI):
                continue
            bt = g.em.get_component(eid, Transform)
            if math.hypot(bt.x - px_h, bt.y - py_h) >= REPAIR_RANGE:
                continue
            pl_h = g.em.get_component(eid, Placeable)
            h = g.em.get_component(eid, Health)
            struct_name = ITEM_DATA[pl_h.item_type][0] if pl_h.item_type in ITEM_DATA else pl_h.item_type
            if g.em.has_component(eid, Turret):
                turr = g.em.get_component(eid, Turret)
                if turr.rarity and turr.rarity != 'common':
                    struct_name = f"{turr.rarity.title()} {struct_name}"
                if turr.enchant:
                    from enchantments.effects import get_enchant_display_prefix
                    prefix = get_enchant_display_prefix(turr.enchant)
                    if prefix:
                        struct_name = f"{prefix} {struct_name}"
            if h.current < h.maximum:
                label = f"{struct_name} - Press F to Repair"
                color = HUD_REPAIR_DAMAGED_TEXT
                bg_color = (10, 30, 10, 160)
            else:
                label = struct_name
                color = HUD_REPAIR_NORMAL_TEXT
                bg_color = (20, 20, 20, 160)
            repair_txt = g.font.render(label, True, color)
            repair_bg = pygame.Surface(
                (repair_txt.get_width() + 16,
                 repair_txt.get_height() + 8), pygame.SRCALPHA)
            repair_bg.fill(bg_color)
            rbx = SCREEN_WIDTH // 2 - repair_txt.get_width() // 2
            rby = SCREEN_HEIGHT // 2 + 80
            g.screen.blit(repair_bg, (rbx - 8, rby - 4))
            g.screen.blit(repair_txt, (rbx, rby))
            break


# ======================================================================
# DEATH SCREEN
# ======================================================================

def draw_death_screen(g: 'Game') -> None:
    ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 180))
    g.screen.blit(ov, (0, 0))
    dt_text = g.font_xl.render("YOU DIED", True, RED)
    g.screen.blit(
        dt_text, (SCREEN_WIDTH // 2 - dt_text.get_width() // 2,
                  SCREEN_HEIGHT // 2 - 100))
    ps: PlayerStats = g.em.get_component(g.player_id, PlayerStats)
    st = g.font.render(
        f"Day {g.daynight.day_number}  |  Level {ps.level}  |  "
        f"{ps.kills} Kills", True, WHITE)
    g.screen.blit(
        st, (SCREEN_WIDTH // 2 - st.get_width() // 2,
             SCREEN_HEIGHT // 2 - 30))

    mx, my = pygame.mouse.get_pos()
    btn_w = 200
    bx = SCREEN_WIDTH // 2 - btn_w // 2
    buttons = [
        (SCREEN_HEIGHT // 2 + 10, "Quick Load [F9]"),
        (SCREEN_HEIGHT // 2 + 56, "Load Save..."),
        (SCREEN_HEIGHT // 2 + 102, "Restart"),
    ]
    for by, label in buttons:
        r = pygame.Rect(bx, by, btn_w, 36)
        hov = r.collidepoint(mx, my)
        bc = DEATH_BUTTON_HOVER if hov else DEATH_BUTTON_NORMAL
        pygame.draw.rect(g.screen, bc, r, border_radius=5)
        pygame.draw.rect(g.screen, GRAY, r, 1, border_radius=5)
        lt = g.font.render(label, True, WHITE)
        g.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                           r.centery - lt.get_height() // 2))

    quit_hint = g.font_sm.render("Press Q to quit", True, GRAY)
    g.screen.blit(quit_hint,
                  (SCREEN_WIDTH // 2 - quit_hint.get_width() // 2,
                   SCREEN_HEIGHT // 2 + 160))


# ======================================================================
# PLACEMENT PREVIEW
# ======================================================================

def draw_placement_preview(g: 'Game') -> None:
    # No placement allowed inside caves
    if g.in_cave >= 0:
        return
    mx, my = pygame.mouse.get_pos()
    world_x = mx + g.camera.x
    world_y = my + g.camera.y
    tx = int(world_x // TILE_SIZE)
    ty = int(world_y // TILE_SIZE)

    tiles = g._get_placement_tiles(tx, ty)
    terrain_ok = all(
        not g.world.is_solid(ttx, tty) for ttx, tty in tiles)

    existing_bid = g._find_building_at_tiles(tiles) if terrain_ok else 0
    is_upgrade = False
    if existing_bid and terrain_ok:
        ep = g.em.get_component(existing_bid, Placeable)
        if (g.placement_item in _WALL_ITEM_IDS
                and ep and ep.item_type in _WALL_ITEM_IDS
                and ep.item_type != g.placement_item):
            is_upgrade = True

    all_valid = terrain_ok and (not existing_bid or is_upgrade)

    for ttx, tty in tiles:
        tsx = int(ttx * TILE_SIZE - g.camera.x)
        tsy = int(tty * TILE_SIZE - g.camera.y)
        if is_upgrade:
            color = PLACEMENT_UPGRADE_PREVIEW_COLOR
            bd_color = PLACEMENT_UPGRADE_BORDER
        elif all_valid:
            color = PLACEMENT_PREVIEW_COLOR
            bd_color = PLACEMENT_VALID_BORDER
        else:
            color = PLACEMENT_INVALID_COLOR
            bd_color = PLACEMENT_INVALID_BORDER
        ghost = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        ghost.fill(color)
        g.screen.blit(ghost, (tsx, tsy))
        pygame.draw.rect(g.screen, bd_color,
                         (tsx, tsy, TILE_SIZE, TILE_SIZE), 2)

    if g.placement_item:
        tex_key = None
        for k in [f'{g.placement_item}_placed',
                  f'campfire_True',
                  f'item_{g.placement_item}']:
            if k in g.textures.cache:
                tex_key = k
                break
        if tex_key:
            icon = g.textures.get(tex_key)
            min_tx = min(t[0] for t in tiles)
            min_ty = min(t[1] for t in tiles)
            max_tx = max(t[0] for t in tiles)
            max_ty = max(t[1] for t in tiles)
            pw = (max_tx - min_tx + 1) * TILE_SIZE
            pht = (max_ty - min_ty + 1) * TILE_SIZE
            bsx = int(min_tx * TILE_SIZE - g.camera.x)
            bsy = int(min_ty * TILE_SIZE - g.camera.y)
            rot = g.placement_rotation % 4
            if rot != 0 and g.placement_item == 'bed':
                icon = pygame.transform.rotate(icon, -90 * rot)
            scaled = pygame.transform.scale(icon, (pw, pht))
            scaled.set_alpha(140)
            g.screen.blit(scaled, (bsx, bsy))

    hint_parts = ["Click to place"]
    if g.placement_item == 'bed':
        hint_parts.append("R to rotate")
    hint_parts.append("ESC/Right-click to cancel")
    hint = g.font_sm.render(" | ".join(hint_parts), True, WHITE)
    g.screen.blit(hint,
                  (SCREEN_WIDTH // 2 - hint.get_width() // 2, 40))


# ======================================================================
# SPELL TARGETING
# ======================================================================

def draw_spell_targeting(g: 'Game') -> None:
    mx, my = pygame.mouse.get_pos()
    pygame.draw.circle(g.screen, SPELL_TARGET_RETICLE, (mx, my), 16, 2)
    pygame.draw.line(g.screen, SPELL_TARGET_RETICLE,
                     (mx - 20, my), (mx + 20, my), 1)
    pygame.draw.line(g.screen, SPELL_TARGET_RETICLE,
                     (mx, my - 20), (mx, my + 20), 1)
    hint = g.font_sm.render(
        "Click to cast | ESC/Right-click to cancel", True, SPELL_HELP_TEXT)
    g.screen.blit(hint,
                  (SCREEN_WIDTH // 2 - hint.get_width() // 2, 40))


# ======================================================================
# ELITE OUTLINE (drawn BEFORE sprites so it sits behind them)
# ======================================================================

# Cache: (id(sprite_surface), flip_x, elite_tier) -> outline Surface
_elite_outline_cache: dict[tuple[int, bool, int], pygame.Surface] = {}


def draw_elite_outlines(g: 'Game') -> None:
    """Draw a precise pixel-perfect outline behind every elite mob sprite.

    The expensive mask->silhouette->8-dir stamp computation is cached per
    (sprite id, flip_x, tier).  Only set_alpha() is called each frame
    for the pulsing effect.
    """
    from game_controller import (
        ELITE_TIER_COLORS, ELITE_GLOW_EXPAND,
        ELITE_GLOW_PULSE_SPEED, ELITE_GLOW_ALPHA_MIN, ELITE_GLOW_ALPHA_MAX,
        RENDER_CULL_MARGIN,
    )
    expand = ELITE_GLOW_EXPAND

    # Compute pulsing alpha once per frame
    pulse = (math.sin(pygame.time.get_ticks() * ELITE_GLOW_PULSE_SPEED) + 1.0) * 0.5
    alpha = int(ELITE_GLOW_ALPHA_MIN + pulse * (ELITE_GLOW_ALPHA_MAX - ELITE_GLOW_ALPHA_MIN))

    for eid in g.em.get_entities_with(Transform, AI):
        ai_c = g.em.get_component(eid, AI)
        if not (ai_c.is_elite and ai_c.elite_tier > 0):
            continue
        rend = g.em.get_component(eid, Renderable)
        if not (rend and rend.surface and rend.visible):
            continue

        t = g.em.get_component(eid, Transform)
        sx = int(t.x - g.camera.x + rend.offset_x)
        sy = int(t.y - g.camera.y + rend.offset_y)

        # Cull off-screen
        if (sx < -RENDER_CULL_MARGIN or sx > SCREEN_WIDTH + RENDER_CULL_MARGIN
                or sy < -RENDER_CULL_MARGIN or sy > SCREEN_HEIGHT + RENDER_CULL_MARGIN):
            continue

        cache_key = (id(rend.surface), rend.flip_x, ai_c.elite_tier)
        outline_surf = _elite_outline_cache.get(cache_key)

        if outline_surf is None:
            sprite = (pygame.transform.flip(rend.surface, rend.flip_x, False)
                      if rend.flip_x else rend.surface)
            sw, sh = sprite.get_size()
            tier_color = ELITE_TIER_COLORS.get(ai_c.elite_tier, (60, 140, 255))

            # Build the outline at full alpha (255) -- pulsing via set_alpha
            mask = pygame.mask.from_surface(sprite)
            silhouette = mask.to_surface(
                setcolor=(*tier_color, 255),
                unsetcolor=(0, 0, 0, 0),
            )
            outline_w = sw + expand * 2
            outline_h = sh + expand * 2
            outline_surf = pygame.Surface((outline_w, outline_h), pygame.SRCALPHA)
            for d in range(1, expand + 1):
                for ox, oy in [(-d, 0), (d, 0), (0, -d), (0, d),
                               (-d, -d), (d, -d), (-d, d), (d, d)]:
                    outline_surf.blit(silhouette, (expand + ox, expand + oy))
            _elite_outline_cache[cache_key] = outline_surf

        # Pulse via set_alpha (fast, no surface re-creation)
        outline_surf.set_alpha(alpha)
        g.screen.blit(outline_surf, (sx - expand, sy - expand))


# ======================================================================
# BOSS GLOW (pulsing aura circle — drawn ON TOP of sprites)
# ======================================================================

def draw_boss_glow(g: 'Game') -> None:
    for eid in g.em.get_entities_with(Transform, AI):
        ai_c = g.em.get_component(eid, AI)
        if not (ai_c.is_boss and ai_c.glow_color):
            continue
        t = g.em.get_component(eid, Transform)
        sx = int(t.x - g.camera.x + 14)
        sy = int(t.y - g.camera.y + 14)
        pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.005)
        radius = int(40 * pulse)
        glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        r, gv, b = ai_c.glow_color
        pygame.draw.circle(glow_surf, (r, gv, b, int(60 * pulse)),
                           (radius, radius), radius)
        g.screen.blit(glow_surf, (sx - radius, sy - radius),
                       special_flags=pygame.BLEND_RGBA_ADD)


# ======================================================================
# CHEATS BUTTON & HELP OVERLAY
# ======================================================================

def _draw_cheats_button(g: 'Game') -> None:
    """Draw 'Cheats' button below the minimap."""
    from game_controller import (
        MINIMAP_SIZE_PX,
        CHEAT_BTN_BG, CHEAT_BTN_BORDER, CHEAT_BTN_HOVER, CHEAT_BTN_TEXT,
        CHEAT_BTN_WIDTH, CHEAT_BTN_HEIGHT,
    )
    mx, my = pygame.mouse.get_pos()
    btn_w, btn_h = CHEAT_BTN_WIDTH, CHEAT_BTN_HEIGHT
    btn_x = SCREEN_WIDTH - MINIMAP_SIZE_PX - 15
    btn_y = 50 + MINIMAP_SIZE_PX + 6
    r = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
    hover = r.collidepoint(mx, my)
    bg_c = CHEAT_BTN_HOVER if hover else CHEAT_BTN_BG
    bg_surf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
    bg_surf.fill(bg_c)
    g.screen.blit(bg_surf, (btn_x, btn_y))
    pygame.draw.rect(g.screen, CHEAT_BTN_BORDER, r, 1, border_radius=3)
    label = g.font_sm.render("Cheats Enabled", True, CHEAT_BTN_TEXT)
    g.screen.blit(label, (r.centerx - label.get_width() // 2,
                          r.centery - label.get_height() // 2))


def _draw_cheat_help(g: 'Game') -> None:
    """Draw a translucent overlay listing available cheat commands."""
    from game_controller import (
        CHEAT_HELP_BG, CHEAT_HELP_BORDER, CHEAT_HELP_TEXT,
        CHEAT_HELP_WIDTH, CHEAT_HELP_HEIGHT,
    )
    pw, ph = CHEAT_HELP_WIDTH, CHEAT_HELP_HEIGHT
    px = SCREEN_WIDTH // 2 - pw // 2
    py = SCREEN_HEIGHT // 2 - ph // 2
    bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
    bg.fill(CHEAT_HELP_BG)
    g.screen.blit(bg, (px, py))
    pygame.draw.rect(g.screen, CHEAT_HELP_BORDER,
                     (px, py, pw, ph), 2, border_radius=8)

    title = g.font.render("Cheat Commands (F12 to open bar)", True, WHITE)
    g.screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 10))

    lines = [
        "enable cheats      - Enable cheat mode",
        "set health <val>   - Set HP",
        "set maxhp <val>    - Set max HP",
        "set level <val>    - Set player level",
        "set xp <val>       - Set XP",
        "set points <val>   - Set stat points",
        "set str <val>      - Set strength",
        "set agi <val>      - Set agility",
        "set vit <val>      - Set vitality",
        "set luck <val>     - Set luck",
        "set kills <val>    - Set kill count",
        "set day <val>      - Set day number",
        "give <item> [n]    - Give item(s)",
        "god                - Toggle invincibility",
        "heal               - Full heal",
        "kill               - Kill all enemies",
        "levelup [n]        - Level up n times",
    ]
    y = py + 38
    for line in lines:
        lt = g.font_sm.render(line, True, CHEAT_HELP_TEXT)
        g.screen.blit(lt, (px + 16, y))
        y += 15

    hint = g.font_sm.render("Click or press ESC to close", True, GRAY)
    g.screen.blit(hint, (px + pw // 2 - hint.get_width() // 2, py + ph - 20))
