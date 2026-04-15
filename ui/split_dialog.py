"""Stack split dialog — popup for splitting item stacks."""
from __future__ import annotations

import pygame

from core.constants import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, GRAY,
                            UI_BORDER_DIALOG, UI_SLOT_BG_SELECTED,
                            UI_SPLIT_BUTTON_NORMAL, UI_TEXT_MUTED,
                            UI_CONFIRM_BUTTON, UI_CANCEL_BUTTON,
                            UI_BORDER_BUTTON)
from core.components import Inventory
from core.item_stack import normalize_rarity


class SplitDialog:
    """Small popup for splitting a stack.  Scroll wheel / +/- / type amount."""

    WIDTH = 180
    HEIGHT = 120

    def __init__(self) -> None:
        self.active = False
        self.source: str = ''         # 'hotbar', 'slots', 'extra_bar', or 'chest'
        self.slot: int = 0
        self.item_id: str = ''
        self.total: int = 0
        self.amount: int = 0          # amount to split off
        self.typing: str = ''         # keyboard buffer
        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        # External storage refs (used for extra_bar splits or chest splits)
        self._ext_slots = None
        self._ext_enchants = None
        self._ext_rarities = None
        self._transfer_to_inventory = False

    def open(self, source: str, slot: int, item_id: str, total: int,
             mx: int, my: int, *,
             ext_slots=None, ext_enchants=None, ext_rarities=None,
             transfer_to_inventory: bool = False) -> None:
        self.active = True
        self.source = source
        self.slot = slot
        self.item_id = item_id
        self.total = total
        self.amount = max(1, total // 2)
        self.typing = ''
        self._ext_slots = ext_slots
        self._ext_enchants = ext_enchants
        self._ext_rarities = ext_rarities
        self._transfer_to_inventory = transfer_to_inventory
        # Position near the mouse, clamped to screen
        self.x = min(mx, SCREEN_WIDTH - self.WIDTH - 4)
        self.y = min(my, SCREEN_HEIGHT - self.HEIGHT - 4)

    def close(self) -> None:
        self.active = False
        self._ext_slots = None
        self._ext_enchants = None
        self._ext_rarities = None
        self._transfer_to_inventory = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return
        r = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        bg.fill((25, 25, 40, 240))
        surface.blit(bg, r.topleft)
        pygame.draw.rect(surface, UI_BORDER_DIALOG, r, 2, border_radius=6)

        mx, my = pygame.mouse.get_pos()

        title = self.font.render('Split Stack', True, WHITE)
        surface.blit(title, (r.centerx - title.get_width() // 2, r.y + 6))

        amt_text = self.font.render(
            f'{self.amount} / {self.total}', True, YELLOW)
        surface.blit(amt_text,
                     (r.centerx - amt_text.get_width() // 2, r.y + 30))

        btn_w, btn_h = 36, 24
        minus_r = pygame.Rect(r.x + 14, r.y + 56, btn_w, btn_h)
        plus_r = pygame.Rect(r.right - 14 - btn_w, r.y + 56, btn_w, btn_h)
        for br, label in [(minus_r, '-'), (plus_r, '+')]:
            hov = br.collidepoint(mx, my)
            pygame.draw.rect(surface,
                             UI_SLOT_BG_SELECTED if hov else UI_SPLIT_BUTTON_NORMAL,
                             br, border_radius=4)
            pygame.draw.rect(surface, UI_TEXT_MUTED, br, 1, border_radius=4)
            lt = self.font.render(label, True, WHITE)
            surface.blit(lt, (br.centerx - lt.get_width() // 2,
                              br.centery - lt.get_height() // 2))

        hint = self.font_sm.render('Scroll / type / +/-', True, GRAY)
        surface.blit(hint,
                     (r.centerx - hint.get_width() // 2, r.y + 56 + 4))

        conf_r = pygame.Rect(r.x + 10, r.bottom - 28, 75, 22)
        canc_r = pygame.Rect(r.right - 85, r.bottom - 28, 75, 22)
        for br, label, color in [
            (conf_r, 'Confirm', UI_CONFIRM_BUTTON),
            (canc_r, 'Cancel', UI_CANCEL_BUTTON),
        ]:
            hov = br.collidepoint(mx, my)
            button_color = tuple(min(255, ch + 30) for ch in color) if hov else color
            pygame.draw.rect(surface, button_color, br, border_radius=4)
            pygame.draw.rect(surface, UI_BORDER_BUTTON, br, 1, border_radius=4)
            lt = self.font_sm.render(label, True, WHITE)
            surface.blit(lt, (br.centerx - lt.get_width() // 2,
                              br.centery - lt.get_height() // 2))

    def handle_event(self, event: pygame.event.Event,
                     inventory: 'Inventory') -> bool:
        """Return True if the event was consumed."""
        if not self.active:
            return False

        if event.type == pygame.MOUSEWHEEL:
            self.amount = max(1, min(self.total - 1, self.amount + event.y))
            return True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self._confirm(inventory)
                return True
            if event.key == pygame.K_BACKSPACE:
                self.typing = self.typing[:-1]
                if self.typing:
                    self.amount = max(1, min(self.total - 1, int(self.typing)))
                return True
            if event.unicode.isdigit():
                self.typing += event.unicode
                self.amount = max(1, min(self.total - 1, int(self.typing)))
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            r = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
            if not r.collidepoint(mx, my):
                self.close()
                return True

            btn_w, btn_h = 36, 24
            minus_r = pygame.Rect(r.x + 14, r.y + 56, btn_w, btn_h)
            plus_r = pygame.Rect(r.right - 14 - btn_w, r.y + 56, btn_w, btn_h)
            if minus_r.collidepoint(mx, my):
                self.amount = max(1, self.amount - 1)
                return True
            if plus_r.collidepoint(mx, my):
                self.amount = min(self.total - 1, self.amount + 1)
                return True

            conf_r = pygame.Rect(r.x + 10, r.bottom - 28, 75, 22)
            canc_r = pygame.Rect(r.right - 85, r.bottom - 28, 75, 22)
            if conf_r.collidepoint(mx, my):
                self._confirm(inventory)
                return True
            if canc_r.collidepoint(mx, my):
                self.close()
                return True
            return True

        return False

    def _confirm(self, inventory: 'Inventory') -> None:
        """Split a stack into held item or directly into inventory."""
        if self.amount < 1:
            self.close()
            return

        if self.source in ('extra_bar', 'chest') and self._ext_slots is not None:
            storage = self._ext_slots
            ench_dict = self._ext_enchants or {}
            rar_dict = self._ext_rarities or {}
        elif self.source == 'hotbar':
            storage = inventory.hotbar
            ench_dict = inventory.hotbar_enchantments
            rar_dict = inventory.hotbar_rarities
        else:
            storage = inventory.slots
            ench_dict = inventory.slot_enchantments
            rar_dict = inventory.slot_rarities

        if self.slot not in storage:
            self.close()
            return

        current_total = storage[self.slot][1]
        if self.amount >= current_total:
            self.close()
            return

        ench = ench_dict.get(self.slot)
        rarity = normalize_rarity(rar_dict.get(self.slot, 'common'))

        if self._transfer_to_inventory:
            overflow = inventory.add_item_enchanted(
                self.item_id,
                dict(ench) if ench else None,
                self.amount,
                rarity,
            )
            moved = self.amount - overflow
            if moved > 0:
                storage[self.slot] = (self.item_id, current_total - moved)
            self.close()
            return

        storage[self.slot] = (self.item_id, current_total - self.amount)
        inventory.held_item = (self.item_id, self.amount)
        if ench:
            inventory.held_enchant = dict(ench)
        inventory.held_rarity = rarity
        self.close()
