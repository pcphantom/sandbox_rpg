"""Main menu and options menu functions extracted from Game class.

All functions receive the Game instance as their first argument ``g``.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, GRAY, DARK_GRAY, RED, GREEN, YELLOW, ORANGE, CYAN,
    QUICK_SAVE_SLOT,
    DIFFICULTY_NAMES,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    UI_BG_MAIN_MENU, UI_BG_BUTTON_HOVER, UI_BG_BUTTON_NORMAL,
    UI_BG_BUTTON_SELECTED, UI_BORDER_NORMAL, UI_BORDER_PANEL,
    VOLUME_SLIDER_BG, VOLUME_SLIDER_FILL,
    OPTIONS_INFO_TEXT, OPTIONS_BACK_HOVER, OPTIONS_BACK_NORMAL,
    OPTIONS_BACK_BORDER,
)
from core.settings import (
    save_settings,
    DISPLAY_WINDOWED, DISPLAY_FULLSCREEN, DISPLAY_BORDERLESS,
    DISPLAY_MODE_NAMES, RESOLUTION_PRESETS,
)
from game import save_load


# ======================================================================
# MAIN MENU
# ======================================================================

def handle_main_menu_events(g: 'Game') -> None:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            g.running = False
            continue
        if (event.type == pygame.KEYDOWN
                and event.key == pygame.K_RETURN
                and (event.mod & pygame.KMOD_ALT)):
            g._toggle_fullscreen()
            continue
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                g.in_main_menu = False
                g.in_char_gen = True
            elif event.key == pygame.K_q:
                g.running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = g._scale_mouse_pos(event.pos)
            btn_w, btn_h = 220, 44
            bx = SCREEN_WIDTH // 2 - btn_w // 2
            start_y = 300
            if pygame.Rect(bx, start_y, btn_w, btn_h).collidepoint(mx, my):
                g.in_main_menu = False
                g.in_char_gen = True
            load_y = start_y + 60
            if pygame.Rect(bx, load_y, btn_w, btn_h).collidepoint(mx, my):
                data = save_load.load_game(QUICK_SAVE_SLOT)
                if data:
                    g._apply_save_data(data)
                    # Check if save is missing character data (legacy save)
                    from character.legacy_save_migration import check_needs_migration
                    if check_needs_migration(data):
                        g.in_main_menu = False
                        g.in_char_gen = True
                        g.char_gen_ui._is_legacy_migration = True
                    else:
                        g.in_main_menu = False
                        g.paused = True
                        g.music_manager.start(g.daynight.is_night())
                else:
                    g.in_main_menu = False
                    g.paused = True
                    g.music_manager.start(g.daynight.is_night())
            opts_y = load_y + 60
            if pygame.Rect(bx, opts_y, btn_w, btn_h).collidepoint(mx, my):
                g.in_options_menu = True
                g.options_source = 'main'
            quit_y = opts_y + 60
            if pygame.Rect(bx, quit_y, btn_w, btn_h).collidepoint(mx, my):
                g.running = False


def draw_main_menu(g: 'Game') -> None:
    g.screen.fill(UI_BG_MAIN_MENU)
    title = g.font_xl.render("Sandbox Survival RPG", True, WHITE)
    g.screen.blit(title,
                  (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

    diff_name = DIFFICULTY_NAMES[g.difficulty]
    diff_colors = [GREEN, YELLOW, ORANGE, RED]
    sub = g.font.render(f"Difficulty: {diff_name}", True,
                        diff_colors[g.difficulty])
    g.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 240))

    mx, my = pygame.mouse.get_pos()
    btn_w, btn_h = 220, 44
    bx = SCREEN_WIDTH // 2 - btn_w // 2

    buttons = [
        (300, "Start Game", GREEN),
        (360, "Load Game", CYAN),
        (420, "Options", GRAY),
        (480, "Quit", RED),
    ]
    for by, label, color in buttons:
        r = pygame.Rect(bx, by, btn_w, btn_h)
        hov = r.collidepoint(mx, my)
        bc = UI_BG_BUTTON_HOVER if hov else UI_BG_BUTTON_NORMAL
        pygame.draw.rect(g.screen, bc, r, border_radius=6)
        bd = color if hov else UI_BORDER_NORMAL
        pygame.draw.rect(g.screen, bd, r, 2, border_radius=6)
        lt = g.font_lg.render(label, True, WHITE if hov else GRAY)
        g.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                           r.centery - lt.get_height() // 2))

    hint = g.font_sm.render(
        "Press ENTER to start  |  Q to quit", True, GRAY)
    g.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                         SCREEN_HEIGHT - 60))
    g._present()


# ======================================================================
# OPTIONS MENU
# ======================================================================

def handle_options_events(g: 'Game') -> None:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            g.running = False
            continue
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                close_options(g)
                continue
            if (event.key == pygame.K_RETURN
                    and (event.mod & pygame.KMOD_ALT)):
                g._toggle_fullscreen()
                continue
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = g._scale_mouse_pos(event.pos)
            pw, ph = 450, 560
            px = SCREEN_WIDTH // 2 - pw // 2
            py = SCREEN_HEIGHT // 2 - ph // 2

            # Difficulty
            diff_y = py + 60
            btn_w, btn_h = 100, 32
            total_w = len(DIFFICULTY_NAMES) * (btn_w + 8) - 8
            diff_bx = px + pw // 2 - total_w // 2
            for i, name in enumerate(DIFFICULTY_NAMES):
                r = pygame.Rect(
                    diff_bx + i * (btn_w + 8), diff_y, btn_w, btn_h)
                if r.collidepoint(mx, my):
                    g.difficulty = i
                    g.wave_system.difficulty = i
                    g.settings['difficulty'] = i
                    save_settings(g.settings)

            # Display mode
            mode_y = diff_y + 70
            modes = [
                (DISPLAY_WINDOWED, "Windowed"),
                (DISPLAY_FULLSCREEN, "Fullscreen"),
                (DISPLAY_BORDERLESS, "Borderless"),
            ]
            mode_bw = 130
            mode_total = len(modes) * (mode_bw + 8) - 8
            mode_bx = px + pw // 2 - mode_total // 2
            for i, (mode_id, label) in enumerate(modes):
                r = pygame.Rect(
                    mode_bx + i * (mode_bw + 8), mode_y, mode_bw, btn_h)
                if r.collidepoint(mx, my):
                    g.display_mode = mode_id
                    if mode_id in (DISPLAY_BORDERLESS, DISPLAY_FULLSCREEN):
                        info = pygame.display.Info()
                        g.window_w = info.current_w
                        g.window_h = info.current_h
                    g._apply_display_settings()

            # Resolution presets
            res_y = mode_y + 70
            res_bw = 120
            for i, (rw, rh) in enumerate(RESOLUTION_PRESETS):
                row = i // 3
                col = i % 3
                rx = px + 30 + col * (res_bw + 12)
                ry = res_y + row * 38
                r = pygame.Rect(rx, ry, res_bw, 30)
                if r.collidepoint(mx, my):
                    g.window_w = rw
                    g.window_h = rh
                    if g.display_mode != DISPLAY_BORDERLESS:
                        g._apply_display_settings()

            # Music toggle
            music_y = res_y + 90
            for i, (enabled, label) in enumerate(
                    [(True, "On"), (False, "Off")]):
                r = pygame.Rect(px + 100 + i * 78, music_y, 70, btn_h)
                if r.collidepoint(mx, my):
                    g.music_manager.set_enabled(enabled)
                    g.settings['music_enabled'] = enabled
                    save_settings(g.settings)

            # Volume slider
            vol_y = music_y + 40
            slider_x = px + 100
            slider_w = 300
            slider_r = pygame.Rect(slider_x, vol_y + 8, slider_w, 16)
            if slider_r.collidepoint(mx, my):
                vol = (mx - slider_x) / slider_w
                vol = max(0.0, min(1.0, vol))
                g.music_manager.set_volume(vol)
                g.settings['music_volume'] = round(vol, 2)
                save_settings(g.settings)

            # About button
            about_y = vol_y + 40
            about_r = pygame.Rect(px + pw // 2 - 80, about_y, 160, 36)
            if about_r.collidepoint(mx, my):
                g.in_about_menu = True
                g.in_options_menu = False
                g.about_section = ''
                g.about_scroll = 0

            # Back
            back_y = py + ph - 60
            back_r = pygame.Rect(px + pw // 2 - 80, back_y, 160, 40)
            if back_r.collidepoint(mx, my):
                close_options(g)


def close_options(g: 'Game') -> None:
    g.in_options_menu = False
    if g.options_source == 'pause':
        g.paused = True


def open_options_from_pause(g: 'Game') -> None:
    g.paused = False
    g.in_options_menu = True
    g.options_source = 'pause'


def draw_options_menu(g: 'Game') -> None:
    g.screen.fill(UI_BG_MAIN_MENU)
    mx, my = pygame.mouse.get_pos()
    pw, ph = 450, 560
    px = SCREEN_WIDTH // 2 - pw // 2
    py = SCREEN_HEIGHT // 2 - ph // 2
    bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
    bg.fill((20, 20, 35, 240))
    g.screen.blit(bg, (px, py))
    pygame.draw.rect(g.screen, UI_BORDER_PANEL,
                     (px, py, pw, ph), 2, border_radius=10)

    title = g.font_lg.render("Options", True, WHITE)
    g.screen.blit(title,
                  (px + pw // 2 - title.get_width() // 2, py + 16))

    # Difficulty
    diff_label = g.font.render("Difficulty:", True, GRAY)
    g.screen.blit(diff_label, (px + 20, py + 46))
    diff_y = py + 60
    diff_colors = [GREEN, YELLOW, ORANGE, RED]
    btn_w, btn_h = 100, 32
    total_w = len(DIFFICULTY_NAMES) * (btn_w + 8) - 8
    diff_bx = px + pw // 2 - total_w // 2
    for i, name in enumerate(DIFFICULTY_NAMES):
        r = pygame.Rect(diff_bx + i * (btn_w + 8), diff_y, btn_w, btn_h)
        sel = i == g.difficulty
        hov = r.collidepoint(mx, my)
        bc = (UI_BG_BUTTON_SELECTED if sel else UI_BG_BUTTON_HOVER if hov
              else UI_BG_BUTTON_NORMAL)
        pygame.draw.rect(g.screen, bc, r, border_radius=5)
        bd = diff_colors[i] if sel else UI_BORDER_NORMAL
        pygame.draw.rect(g.screen, bd, r, 2, border_radius=5)
        lt = g.font_sm.render(name, True,
                              diff_colors[i] if sel else WHITE)
        g.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                           r.centery - lt.get_height() // 2))

    # Display Mode
    mode_label = g.font.render("Display Mode:", True, GRAY)
    g.screen.blit(mode_label, (px + 20, py + 106))
    mode_y = diff_y + 70
    modes = [
        (DISPLAY_WINDOWED, "Windowed"),
        (DISPLAY_FULLSCREEN, "Fullscreen"),
        (DISPLAY_BORDERLESS, "Borderless"),
    ]
    mode_bw = 130
    mode_total = len(modes) * (mode_bw + 8) - 8
    mode_bx = px + pw // 2 - mode_total // 2
    for i, (mode_id, label) in enumerate(modes):
        r = pygame.Rect(mode_bx + i * (mode_bw + 8), mode_y,
                        mode_bw, btn_h)
        sel = mode_id == g.display_mode
        hov = r.collidepoint(mx, my)
        bc = (UI_BG_BUTTON_SELECTED if sel else UI_BG_BUTTON_HOVER if hov
              else UI_BG_BUTTON_NORMAL)
        pygame.draw.rect(g.screen, bc, r, border_radius=5)
        bd = CYAN if sel else UI_BORDER_NORMAL
        pygame.draw.rect(g.screen, bd, r, 2, border_radius=5)
        lt = g.font_sm.render(label, True, WHITE if sel else GRAY)
        g.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                           r.centery - lt.get_height() // 2))

    # Resolution
    res_label = g.font.render("Resolution:", True, GRAY)
    g.screen.blit(res_label, (px + 20, py + 176))
    res_y = mode_y + 70
    res_bw = 120
    for i, (rw, rh) in enumerate(RESOLUTION_PRESETS):
        row = i // 3
        col = i % 3
        rx = px + 30 + col * (res_bw + 12)
        ry = res_y + row * 38
        r = pygame.Rect(rx, ry, res_bw, 30)
        sel = (rw == g.window_w and rh == g.window_h)
        hov = r.collidepoint(mx, my)
        bc = (UI_BG_BUTTON_SELECTED if sel else UI_BG_BUTTON_HOVER if hov
              else UI_BG_BUTTON_NORMAL)
        pygame.draw.rect(g.screen, bc, r, border_radius=4)
        bd = GREEN if sel else UI_BORDER_NORMAL
        pygame.draw.rect(g.screen, bd, r, 2, border_radius=4)
        lt = g.font_sm.render(f"{rw}x{rh}", True,
                              WHITE if sel else GRAY)
        g.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                           r.centery - lt.get_height() // 2))

    # Music
    music_y = res_y + 90
    music_label = g.font.render("Music:", True, GRAY)
    g.screen.blit(music_label, (px + 20, music_y + 4))
    for i, (enabled, label) in enumerate([(True, "On"), (False, "Off")]):
        r = pygame.Rect(px + 100 + i * 78, music_y, 70, btn_h)
        sel = g.music_manager.enabled == enabled
        hov = r.collidepoint(mx, my)
        bc = (UI_BG_BUTTON_SELECTED if sel else UI_BG_BUTTON_HOVER if hov
              else UI_BG_BUTTON_NORMAL)
        pygame.draw.rect(g.screen, bc, r, border_radius=5)
        bd = GREEN if sel and enabled else RED if sel else UI_BORDER_NORMAL
        pygame.draw.rect(g.screen, bd, r, 2, border_radius=5)
        lt = g.font_sm.render(label, True, WHITE if sel else GRAY)
        g.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                           r.centery - lt.get_height() // 2))

    # Volume slider
    vol_y = music_y + 40
    vol_label = g.font.render("Volume:", True, GRAY)
    g.screen.blit(vol_label, (px + 20, vol_y + 4))
    slider_x = px + 100
    slider_w = 300
    pygame.draw.rect(g.screen, VOLUME_SLIDER_BG,
                     (slider_x, vol_y + 8, slider_w, 16),
                     border_radius=4)
    fill_w = int(slider_w * g.music_manager.volume)
    if fill_w > 0:
        pygame.draw.rect(g.screen, VOLUME_SLIDER_FILL,
                         (slider_x, vol_y + 8, fill_w, 16),
                         border_radius=4)
    pygame.draw.rect(g.screen, UI_BORDER_NORMAL,
                     (slider_x, vol_y + 8, slider_w, 16), 2,
                     border_radius=4)
    pct = g.font_sm.render(
        f"{int(g.music_manager.volume * 100)}%", True, WHITE)
    g.screen.blit(pct, (slider_x + slider_w + 10, vol_y + 8))

    # About button
    about_y = vol_y + 40
    about_r = pygame.Rect(px + pw // 2 - 80, about_y, 160, 36)
    hov = about_r.collidepoint(mx, my)
    bc = OPTIONS_BACK_HOVER if hov else OPTIONS_BACK_NORMAL
    pygame.draw.rect(g.screen, bc, about_r, border_radius=5)
    pygame.draw.rect(g.screen, UI_BORDER_NORMAL, about_r, 1, border_radius=5)
    bt = g.font.render("About", True, WHITE)
    g.screen.blit(bt, (about_r.centerx - bt.get_width() // 2,
                       about_r.centery - bt.get_height() // 2))

    # Current info
    cur_info = g.font_sm.render(
        f"Current: {g.window_w}x{g.window_h}  "
        f"{DISPLAY_MODE_NAMES.get(g.display_mode, '?')}",
        True, OPTIONS_INFO_TEXT)
    g.screen.blit(cur_info,
                  (px + pw // 2 - cur_info.get_width() // 2,
                   py + ph - 100))

    # Back
    back_y = py + ph - 60
    back_r = pygame.Rect(px + pw // 2 - 80, back_y, 160, 40)
    hov = back_r.collidepoint(mx, my)
    bc = OPTIONS_BACK_HOVER if hov else OPTIONS_BACK_NORMAL
    pygame.draw.rect(g.screen, bc, back_r, border_radius=6)
    pygame.draw.rect(g.screen, OPTIONS_BACK_BORDER, back_r, 2,
                     border_radius=6)
    bt = g.font.render("Back  [Esc]", True, WHITE)
    g.screen.blit(bt, (back_r.centerx - bt.get_width() // 2,
                       back_r.centery - bt.get_height() // 2))

    hint = g.font_sm.render("Alt+Enter toggles fullscreen", True,
                            DARK_GRAY)
    g.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                         SCREEN_HEIGHT - 40))
    g._present()
