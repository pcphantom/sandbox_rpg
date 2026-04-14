"""Pause menu — save/load slots, resume, options, quit."""
from __future__ import annotations

from typing import Any, Callable, Dict

import pygame

from core.constants import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, SAVE_SLOTS,
                            UI_BORDER_PANEL, UI_SAVE_SLOT_SELECTED,
                            UI_SLOT_BG_NORMAL, UI_TEXT_HIGHLIGHT,
                            UI_SLOT_BORDER_NORMAL, OPTIONS_BACK_HOVER,
                            OPTIONS_BACK_NORMAL, UI_TEXT_MUTED)


class PauseMenu:
    def __init__(self) -> None:
        self.selected_slot = 1  # default to slot 1
        self.font = pygame.font.SysFont('consolas', 16)
        self.title_font = pygame.font.SysFont('consolas', 32, bold=True)
        self.font_sm = pygame.font.SysFont('consolas', 13)

    def draw(self, surface: pygame.Surface,
             slot_infos: Dict[int, Any]) -> None:
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        surface.blit(ov, (0, 0))

        pw, ph = 460, 440
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((20, 20, 35, 240))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, UI_BORDER_PANEL,
                         (px, py, pw, ph), 2, border_radius=10)

        title = self.title_font.render("PAUSED", True, WHITE)
        surface.blit(title,
                     (px + pw // 2 - title.get_width() // 2, py + 16))

        # Resume button
        self._draw_button(surface, px + 40, py + 70, pw - 80, 36,
                          "Resume  [Esc]")

        # Options button
        self._draw_button(surface, px + 40, py + 116, pw - 80, 36,
                          "Options")

        # Save slots
        sy = py + 170
        surface.blit(self.font.render("Save Slots:", True, GRAY),
                     (px + 40, sy))
        sy += 26
        for slot in range(1, SAVE_SLOTS):
            r = pygame.Rect(px + 40, sy, pw - 80, 32)
            sel = slot == self.selected_slot
            info = slot_infos.get(slot)
            label = f"Slot {slot}: "
            if info:
                day_num = info.get('day_number', '?')
                label += f"Day {day_num}  Lv.{info.get('level', '?')}  Kills:{info.get('kills', 0)}"
            else:
                label += "Empty"
            bc = UI_SAVE_SLOT_SELECTED if sel else UI_SLOT_BG_NORMAL
            pygame.draw.rect(surface, bc, r, border_radius=4)
            bd = UI_TEXT_HIGHLIGHT if sel else UI_SLOT_BORDER_NORMAL
            pygame.draw.rect(surface, bd, r, 1, border_radius=4)
            surface.blit(self.font.render(label, True, WHITE),
                         (r.x + 8, r.y + 7))
            sy += 38

        # Save / Load / Delete buttons
        btn_y = sy + 8
        btn_w = (pw - 80 - 20) // 3
        btn_gap = 10
        bx = px + 40
        self._draw_button(surface, bx, btn_y, btn_w, 32, "Save")
        self._draw_button(surface, bx + btn_w + btn_gap, btn_y, btn_w, 32, "Load")
        self._draw_button(surface, bx + 2 * (btn_w + btn_gap), btn_y, btn_w, 32, "Delete")

        # Quit button
        self._draw_button(surface, px + 40, btn_y + 50, pw - 80, 36,
                          "Quit Game  [Q]")

    def _draw_button(self, surface: pygame.Surface,
                     x: int, y: int, w: int, h: int,
                     label: str) -> None:
        mx, my = pygame.mouse.get_pos()
        r = pygame.Rect(x, y, w, h)
        hov = r.collidepoint(mx, my)
        bc = OPTIONS_BACK_HOVER if hov else OPTIONS_BACK_NORMAL
        pygame.draw.rect(surface, bc, r, border_radius=5)
        pygame.draw.rect(surface, UI_TEXT_MUTED, r, 1, border_radius=5)
        lt = self.font.render(label, True, WHITE)
        surface.blit(lt, (r.centerx - lt.get_width() // 2,
                          r.centery - lt.get_height() // 2))

    def handle_event(self, event: pygame.event.Event,
                     save_cb: Callable, load_cb: Callable,
                     delete_cb: Callable,
                     resume_cb: Callable,
                     quit_cb: Callable,
                     options_cb: Callable = None) -> bool:
        """Returns True if the event was consumed."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                resume_cb()
                return True
            if event.key == pygame.K_q:
                quit_cb()
                return True
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos
        pw, ph = 460, 440
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2

        # Resume
        if pygame.Rect(px + 40, py + 70, pw - 80, 36).collidepoint(mx, my):
            resume_cb()
            return True

        # Options
        if options_cb and pygame.Rect(px + 40, py + 116, pw - 80, 36).collidepoint(mx, my):
            options_cb()
            return True

        # Slot selection
        sy = py + 196
        for slot in range(1, SAVE_SLOTS):
            r = pygame.Rect(px + 40, sy, pw - 80, 32)
            if r.collidepoint(mx, my):
                self.selected_slot = slot
                return True
            sy += 38

        # Save / Load / Delete
        btn_y = sy + 8
        btn_w = (pw - 80 - 20) // 3
        btn_gap = 10
        bx = px + 40
        if pygame.Rect(bx, btn_y, btn_w, 32).collidepoint(mx, my):
            save_cb(self.selected_slot)
            return True
        if pygame.Rect(bx + btn_w + btn_gap, btn_y, btn_w, 32).collidepoint(mx, my):
            load_cb(self.selected_slot)
            return True
        if pygame.Rect(bx + 2 * (btn_w + btn_gap), btn_y, btn_w, 32).collidepoint(mx, my):
            delete_cb(self.selected_slot)
            return True

        # Quit
        if pygame.Rect(px + 40, btn_y + 50, pw - 80, 36).collidepoint(mx, my):
            quit_cb()
            return True

        return False
