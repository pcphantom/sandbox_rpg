"""Crafting panel — scrollable recipe list with craft-on-click."""
from __future__ import annotations

from typing import Any, Callable

import pygame

from core.constants import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GREEN, GRAY,
                            UI_BORDER_LIGHT, UI_CRAFT_CAN_NORMAL,
                            UI_CRAFT_CAN_HOVER, UI_CRAFT_CAN_BORDER,
                            UI_CRAFT_CANNOT_NORMAL, UI_CRAFT_CANNOT_HOVER,
                            UI_CRAFT_CANNOT_BORDER)
from core.components import Inventory
from data import ITEM_DATA, RECIPES, get_item_color
from ui.elements import Tooltip
from ui.draggable import DraggableWindow


class CraftingPanel:
    SCROLL_VISIBLE = 8  # recipes visible at once

    def __init__(self, textures: Any) -> None:
        self.textures = textures
        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.title_font = pygame.font.SysFont('consolas', 22, bold=True)
        self.scroll = 0
        pw = 420
        pht = 55 + self.SCROLL_VISIBLE * 52 + 30
        self.dw = DraggableWindow(pw, pht, title="Crafting")

    def draw(self, surface: pygame.Surface, inventory: Inventory,
             tooltip: Tooltip) -> None:
        cr = self.dw.content_rect
        px, py = cr.x, cr.y
        pw, pht = self.dw.w, self.dw.h
        bg = pygame.Surface((pw, pht), pygame.SRCALPHA)
        bg.fill((18, 18, 28, 235))
        surface.blit(bg, (px, py))
        mx, my = pygame.mouse.get_pos()

        visible = RECIPES[self.scroll:self.scroll + self.SCROLL_VISIBLE]
        for i, recipe in enumerate(visible):
            ry = py + 10 + i * 52
            can = all(inventory.has(it, co)
                      for it, co in recipe['cost'].items())
            btn = pygame.Rect(px + 10, ry, pw - 20, 44)
            hov = btn.collidepoint(mx, my)
            if can:
                bc = UI_CRAFT_CAN_NORMAL if not hov else UI_CRAFT_CAN_HOVER
                bd = UI_CRAFT_CAN_BORDER
            else:
                bc = UI_CRAFT_CANNOT_NORMAL if not hov else UI_CRAFT_CANNOT_HOVER
                bd = UI_CRAFT_CANNOT_BORDER
            pygame.draw.rect(surface, bc, btn, border_radius=5)
            pygame.draw.rect(surface, bd, btn, 1, border_radius=5)
            icon = self.textures.cache.get(f"item_{recipe['gives']}")
            if icon:
                surface.blit(pygame.transform.scale(icon, (28, 28)),
                             (btn.x + 6, ry + 8))
            surface.blit(
                self.font.render(recipe['name'], True, WHITE),
                (btn.x + 40, ry + 4))
            cx_pos = btn.x + 40
            for item, cost in recipe['cost'].items():
                has_e = inventory.has(item, cost)
                c_color = GREEN if has_e else RED
                ct = self.font_sm.render(
                    f"{cost}x{ITEM_DATA[item][0]}", True, c_color)
                surface.blit(ct, (cx_pos, ry + 24))
                cx_pos += ct.get_width() + 14
            if hov:
                gives = recipe['gives']
                if gives in ITEM_DATA:
                    d = ITEM_DATA[gives]
                    name_color = get_item_color(gives)
                    tooltip.show([d[0], d[1]], (mx, my),
                                 [name_color, WHITE])

        # Scroll arrows
        arrow_y = py + 10 + self.SCROLL_VISIBLE * 52 + 4
        if self.scroll > 0:
            at = self.font_sm.render("^ Scroll Up", True, GRAY)
            surface.blit(at, (px + 10, arrow_y))
        if self.scroll + self.SCROLL_VISIBLE < len(RECIPES):
            at = self.font_sm.render("v Scroll Down", True, GRAY)
            surface.blit(at, (px + pw - 110, arrow_y))

        # Chrome
        self.dw.draw_chrome(surface)

    def handle_event(self, event: pygame.event.Event,
                     inventory: Inventory,
                     craft_callback: Callable) -> bool:
        # Draggable window chrome
        if self.dw.handle_event(event):
            return True
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(len(RECIPES) - self.SCROLL_VISIBLE,
                                     self.scroll - event.y))
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cr = self.dw.content_rect
            px, py = cr.x, cr.y
            pw = self.dw.w
            visible = RECIPES[self.scroll:self.scroll + self.SCROLL_VISIBLE]
            for i, recipe in enumerate(visible):
                ry = py + 10 + i * 52
                btn = pygame.Rect(px + 10, ry, pw - 20, 44)
                if btn.collidepoint(event.pos):
                    craft_callback(recipe)
                    return True
        return False
