"""Crafting panel — scrollable recipe list with craft-on-click."""
from __future__ import annotations

from typing import Any, Callable

import pygame

from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, RED, GREEN, GRAY
from core.components import Inventory
from data import ITEM_DATA, RECIPES, get_item_color
from ui.elements import Tooltip


class CraftingPanel:
    SCROLL_VISIBLE = 8  # recipes visible at once

    def __init__(self, textures: Any) -> None:
        self.textures = textures
        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.title_font = pygame.font.SysFont('consolas', 22, bold=True)
        self.scroll = 0

    def draw(self, surface: pygame.Surface, inventory: Inventory,
             tooltip: Tooltip) -> None:
        pw, pht = 420, 55 + self.SCROLL_VISIBLE * 52 + 30
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - pht // 2
        bg = pygame.Surface((pw, pht), pygame.SRCALPHA)
        bg.fill((18, 18, 28, 235))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, (130, 130, 155),
                         (px, py, pw, pht), 2, border_radius=10)
        title = self.title_font.render("Crafting", True, WHITE)
        surface.blit(title,
                     (px + pw // 2 - title.get_width() // 2, py + 10))
        mx, my = pygame.mouse.get_pos()

        visible = RECIPES[self.scroll:self.scroll + self.SCROLL_VISIBLE]
        for i, recipe in enumerate(visible):
            ry = py + 44 + i * 52
            can = all(inventory.has(it, co)
                      for it, co in recipe['cost'].items())
            btn = pygame.Rect(px + 10, ry, pw - 20, 44)
            hov = btn.collidepoint(mx, my)
            if can:
                bc = (60, 90, 60) if not hov else (80, 120, 80)
                bd = (100, 180, 100)
            else:
                bc = (55, 35, 35) if not hov else (75, 50, 50)
                bd = (140, 60, 60)
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
        arrow_y = py + 44 + self.SCROLL_VISIBLE * 52 + 4
        if self.scroll > 0:
            at = self.font_sm.render("^ Scroll Up", True, GRAY)
            surface.blit(at, (px + 10, arrow_y))
        if self.scroll + self.SCROLL_VISIBLE < len(RECIPES):
            at = self.font_sm.render("v Scroll Down", True, GRAY)
            surface.blit(at, (px + pw - 110, arrow_y))

    def handle_event(self, event: pygame.event.Event,
                     inventory: Inventory,
                     craft_callback: Callable) -> bool:
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(len(RECIPES) - self.SCROLL_VISIBLE,
                                     self.scroll - event.y))
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pw, pht = 420, 55 + self.SCROLL_VISIBLE * 52 + 30
            px = SCREEN_WIDTH // 2 - pw // 2
            py = SCREEN_HEIGHT // 2 - pht // 2
            visible = RECIPES[self.scroll:self.scroll + self.SCROLL_VISIBLE]
            for i, recipe in enumerate(visible):
                ry = py + 44 + i * 52
                btn = pygame.Rect(px + 10, ry, pw - 20, 44)
                if btn.collidepoint(event.pos):
                    craft_callback(recipe)
                    return True
        return False
