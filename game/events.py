"""Event / input handling — extracted from sandbox_rpg.Game._handle_events."""
import pygame

from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.components import Inventory, PlayerStats, Equipment, Storage, Building


def handle_events(g) -> None:
    """Process all pygame events for one frame.

    ``g`` is the :class:`sandbox_rpg.Game` instance.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            g.running = False
            continue

        # Alt+Enter fullscreen toggle (works in all states)
        if (event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN
                and (event.mod & pygame.KMOD_ALT)):
            g._toggle_fullscreen()
            continue

        # Scale mouse positions from window coords to internal coords
        if hasattr(event, 'pos'):
            event.pos = g._scale_mouse_pos(event.pos)

        # F12 toggles command bar (works in all non-dead, non-menu states)
        if (event.type == pygame.KEYDOWN
                and event.key == pygame.K_F12
                and not g.dead and not g.paused):
            g.command_bar.toggle()
            continue

        # Command bar consumes events when visible
        if g.command_bar.visible:
            from game.cheats import execute_command
            g.command_bar.handle_event(
                event, lambda cmd: execute_command(g, cmd))
            continue

        # Cheat help overlay close
        if g.show_cheat_help:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                g.show_cheat_help = False
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                g.show_cheat_help = False
                continue

        # --- Dead state ---
        if g.dead:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F9:
                    g._quick_load()
                elif event.key == pygame.K_q:
                    g.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check death screen buttons
                mx, my = event.pos
                btn_w = 200
                bx = SCREEN_WIDTH // 2 - btn_w // 2
                # Quick Load button
                if pygame.Rect(bx, SCREEN_HEIGHT // 2 + 10, btn_w, 36).collidepoint(mx, my):
                    g._quick_load()
                # Load Save button
                elif pygame.Rect(bx, SCREEN_HEIGHT // 2 + 56, btn_w, 36).collidepoint(mx, my):
                    g.paused = True
                    g.dead = False
                # Restart button
                elif pygame.Rect(bx, SCREEN_HEIGHT // 2 + 102, btn_w, 36).collidepoint(mx, my):
                    g._full_restart()
            continue

        # --- Pause menu ---
        if g.paused:
            g.pause_menu.handle_event(
                event,
                save_cb=g._save_to_slot,
                load_cb=g._load_from_slot,
                delete_cb=g._delete_slot,
                resume_cb=g._resume,
                quit_cb=g._quit,
                options_cb=g._open_options_from_pause,
            )
            continue

        # --- Global hotkeys ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if g.placement_mode:
                    g.placement_mode = False
                    g.placement_item = None
                    g.placement_rarity = 'common'
                    g.placement_enchant = None
                    g.placement_slot = None
                elif g.spell_targeting:
                    g.spell_targeting = False
                    g.spell_item = None
                elif (g.show_inventory or g.show_crafting
                        or g.show_character or g.show_chest
                        or g.show_enchant_table or g.show_stone_oven):
                    g._return_held_item()
                    g.show_inventory = False
                    g.show_crafting = False
                    g.show_character = False
                    g.show_chest = False
                    g.active_chest = None
                    g.chest_ui.split_dialog.close()
                    g.show_enchant_table = False
                    g.active_enchant_table = None
                    g.show_stone_oven = False
                    g.active_stone_oven = None
                else:
                    g.paused = True
                continue
            if event.key == pygame.K_i:
                if g.show_inventory:
                    g._return_held_item()
                g.show_inventory = not g.show_inventory
                g.show_crafting = False
                g.show_character = False
                g.show_chest = False
                g.active_chest = None
                g.show_enchant_table = False
                g.active_enchant_table = None
                g.show_stone_oven = False
                g.active_stone_oven = None
                continue
            if event.key == pygame.K_c:
                g._return_held_item()
                g.show_crafting = not g.show_crafting
                g.show_inventory = False
                g.show_character = False
                g.show_chest = False
                g.active_chest = None
                g.show_enchant_table = False
                g.active_enchant_table = None
                g.show_stone_oven = False
                g.active_stone_oven = None
                continue
            if event.key == pygame.K_p:
                g._return_held_item()
                g.show_character = not g.show_character
                g.show_inventory = False
                g.show_crafting = False
                g.show_chest = False
                g.active_chest = None
                g.show_enchant_table = False
                g.active_enchant_table = None
                g.show_stone_oven = False
                g.active_stone_oven = None
                continue
            if event.key == pygame.K_f:
                g._use_equipped_item()
                continue
            if event.key == pygame.K_F5:
                g._quick_save()
                continue
            if event.key == pygame.K_F9:
                g._quick_load()
                continue

            # Number keys 1-6 → hotbar
            inv = g.em.get_component(g.player_id, Inventory)
            for n in range(1, 7):
                if event.key == getattr(pygame, f'K_{n}'):
                    inv.equipped_slot = n - 1

        # Mouse-wheel for hotbar (only when no overlay menus are open)
        if event.type == pygame.MOUSEWHEEL:
            if (not g.placement_mode and not g.spell_targeting
                    and not g.show_inventory and not g.show_crafting
                    and not g.show_character and not g.show_chest
                    and not g.show_enchant_table and not g.show_stone_oven):
                inv = g.em.get_component(g.player_id, Inventory)
                inv.equipped_slot = (inv.equipped_slot - event.y) % 6

        # Placement mode rotation
        if g.placement_mode and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                g.placement_rotation = (g.placement_rotation + 1) % 4
                continue

        # Placement mode click
        if g.placement_mode and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                g._placement_confirm()
                continue
            elif event.button == 3:
                g.placement_mode = False
                g.placement_item = None
                g.placement_rarity = 'common'
                g.placement_enchant = None
                g.placement_slot = None
                continue

        # Spell targeting click
        if g.spell_targeting and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                g._spell_cast_at_mouse()
                continue
            elif event.button == 3:
                g.spell_targeting = False
                g.spell_item = None
                continue

        # Cheats button click (below minimap)
        if (g.cheats_enabled and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1 and not g.show_cheat_help):
            from game_controller import (
                SCREEN_WIDTH as SW, MINIMAP_SIZE_PX,
                CHEAT_BTN_WIDTH, CHEAT_BTN_HEIGHT,
            )
            btn_w, btn_h = CHEAT_BTN_WIDTH, CHEAT_BTN_HEIGHT
            btn_x = SW - MINIMAP_SIZE_PX - 15
            btn_y = 50 + MINIMAP_SIZE_PX + 6
            if pygame.Rect(btn_x, btn_y, btn_w, btn_h).collidepoint(event.pos):
                g.show_cheat_help = True
                continue

        # Overlay event handling
        if g.show_chest and g.active_chest is not None:
            stor = g.em.get_component(g.active_chest, Storage)
            if stor:
                is_cave = not g.em.has_component(
                    g.active_chest, Building)
                g.chest_ui.handle_event(
                    event, stor,
                    g.em.get_component(g.player_id, Inventory),
                    is_cave_chest=is_cave)
        if g.show_enchant_table and g.active_enchant_table is not None:
            stor = g.em.get_component(g.active_enchant_table, Storage)
            if stor:
                g.enchant_table_ui.handle_event(
                    event, stor,
                    g.em.get_component(g.player_id, Inventory))
        if g.show_stone_oven:
            if event.type == pygame.MOUSEBUTTONDOWN:
                g.stone_oven_ui.handle_click(g, *event.pos, event.button)
        if g.show_inventory:
            g.inventory_ui.handle_event(event)
        if g.show_crafting:
            g.crafting_ui.handle_event(
                event,
                g.em.get_component(g.player_id, Inventory),
                g._craft)
        if g.show_character:
            g.character_menu.handle_event(
                event,
                g.em.get_component(g.player_id, PlayerStats),
                g.em.get_component(g.player_id, Equipment),
                g.em.get_component(g.player_id, Inventory),
            )
