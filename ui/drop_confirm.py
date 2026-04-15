"""Drop-confirmation dialog shown when the player releases a held item
outside the inventory panel.  Extracted from gui.py for modularity."""

from __future__ import annotations

from typing import Optional

import pygame

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    RED, YELLOW, WHITE,
    UI_DROP_DIALOG_BG, UI_DROP_DIALOG_BORDER,
    UI_DROP_YES_BUTTON, UI_DROP_NO_BUTTON,
    UI_BORDER_BUTTON,
)
from core.item_presentation import build_item_presentation


class DropConfirmDialog:
    """Confirmation prompt when player tries to drop a held item outside the
    inventory panel.  Shows name, count, rarity, enchant info and warns the
    item will be lost forever."""

    WIDTH = 260
    HEIGHT = 130

    def __init__(self) -> None:
        self.active = False
        self.item_id: str = ''
        self.count: int = 0
        self.enchant: Optional[dict] = None
        self.rarity: str = 'common'
        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)

    def open(self, item_id: str, count: int,
             enchant: Optional[dict], rarity: str = 'common') -> None:
        self.active = True
        self.item_id = item_id
        self.count = count
        self.enchant = enchant
        self.rarity = rarity

    def close(self) -> None:
        self.active = False

    def _rect(self) -> pygame.Rect:
        return pygame.Rect(SCREEN_WIDTH // 2 - self.WIDTH // 2,
                           SCREEN_HEIGHT // 2 - self.HEIGHT // 2,
                           self.WIDTH, self.HEIGHT)

    def _build_label(self) -> str:
        return build_item_presentation(
            self.item_id,
            self.rarity,
            self.enchant,
            self.count,
            include_count=True,
        )['label']

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return
        r = self._rect()
        bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        bg.fill(UI_DROP_DIALOG_BG)
        surface.blit(bg, r.topleft)
        pygame.draw.rect(surface, UI_DROP_DIALOG_BORDER, r, 2, border_radius=6)
        mx, my = pygame.mouse.get_pos()
        title = self.font.render("Drop Item?", True, RED)
        surface.blit(title, (r.centerx - title.get_width() // 2, r.y + 8))
        presentation = build_item_presentation(
            self.item_id,
            self.rarity,
            self.enchant,
            self.count,
            include_count=True,
        )
        label = presentation['label']
        name_color = presentation['color']
        name_surf = self.font.render(label, True, name_color)
        surface.blit(name_surf, (r.centerx - name_surf.get_width() // 2, r.y + 32))
        warn = self.font_sm.render("This item will be lost forever!", True, YELLOW)
        surface.blit(warn, (r.centerx - warn.get_width() // 2, r.y + 56))
        yes_r = pygame.Rect(r.x + 20, r.bottom - 34, 90, 24)
        no_r = pygame.Rect(r.right - 110, r.bottom - 34, 90, 24)
        for br, lbl, color in [
            (yes_r, "Yes, Drop", UI_DROP_YES_BUTTON),
            (no_r, "Cancel", UI_DROP_NO_BUTTON),
        ]:
            hov = br.collidepoint(mx, my)
            c = tuple(min(255, ch + 30) for ch in color) if hov else color
            pygame.draw.rect(surface, c, br, border_radius=4)
            pygame.draw.rect(surface, UI_BORDER_BUTTON, br, 1, border_radius=4)
            lt = self.font_sm.render(lbl, True, WHITE)
            surface.blit(lt, (br.centerx - lt.get_width() // 2,
                              br.centery - lt.get_height() // 2))

    def handle_event(self, event: pygame.event.Event, inventory) -> bool:
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self._confirm_drop(inventory)
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            r = self._rect()
            mx, my = event.pos
            yes_r = pygame.Rect(r.x + 20, r.bottom - 34, 90, 24)
            no_r = pygame.Rect(r.right - 110, r.bottom - 34, 90, 24)
            if yes_r.collidepoint(mx, my):
                self._confirm_drop(inventory)
                return True
            if no_r.collidepoint(mx, my):
                self.close()
                return True
            if r.collidepoint(mx, my):
                return True
            self.close()
            return True
        return True

    def _confirm_drop(self, inventory) -> None:
        inventory.held_item = None
        inventory.held_enchant = None
        inventory.held_rarity = 'common'
        self.close()
