"""Inventory grid — hotbar row + paginated inventory with drag-drop."""
from __future__ import annotations

from typing import Any

import pygame

from core.constants import (WHITE, GRAY, CYAN, INVENTORY_SLOTS_PER_PAGE,
                            HOTBAR_CAPACITY, INVENTORY_PAGES, INVENTORY_COLS)
from core.components import Inventory
from data import ITEM_DATA, get_item_color
from ui.elements import UIElement, Tooltip
from ui.split_dialog import SplitDialog
from ui.rarity_display import pick_up_rarity, place_rarity, swap_rarity


class InventoryGrid(UIElement):
    """Hotbar row on top, paginated 4x6 inventory below. Click to pick/swap."""

    def __init__(self, rect: pygame.Rect, inventory: Inventory,
                 textures: Any) -> None:
        super().__init__(rect)
        self.inventory = inventory; self.textures = textures
        self.slot_size = 48; self.cols = INVENTORY_COLS
        self.rows = INVENTORY_SLOTS_PER_PAGE // self.cols  # 4
        self.page = 0
        self.font = pygame.font.SysFont('consolas', 14)
        self.title_font = pygame.font.SysFont('consolas', 20, bold=True)
        self.split_dialog = SplitDialog()

    def _page_offset(self) -> int:
        return self.page * INVENTORY_SLOTS_PER_PAGE

    def _hotbar_slot_rect(self, i: int) -> pygame.Rect:
        x = self.rect.x + 12 + i * (self.slot_size + 6)
        y = self.rect.y + 38
        return pygame.Rect(x, y, self.slot_size, self.slot_size)

    def _inv_slot_rect(self, i: int) -> pygame.Rect:
        col = i % self.cols
        row = i // self.cols
        hotbar_h = self.slot_size + 14  # hotbar row height + gap
        x = self.rect.x + 12 + col * (self.slot_size + 6)
        y = self.rect.y + 38 + hotbar_h + row * (self.slot_size + 6)
        return pygame.Rect(x, y, self.slot_size, self.slot_size)

    def draw(self, surface: pygame.Surface, tooltip: Tooltip) -> None:
        if not self.visible:
            return
        bg = pygame.Surface((self.rect.width, self.rect.height),
                            pygame.SRCALPHA)
        bg.fill((20, 20, 32, 235))
        surface.blit(bg, self.rect.topleft)
        pygame.draw.rect(surface, (130, 130, 155), self.rect, 2,
                         border_radius=8)

        # Title
        title = self.title_font.render("Inventory", True, WHITE)
        surface.blit(title, (self.rect.centerx - title.get_width() // 2,
                             self.rect.y + 8))

        mx, my = pygame.mouse.get_pos()

        # -- Hotbar row (always visible) --
        hotbar_label = self.font.render("Hotbar", True, GRAY)
        surface.blit(hotbar_label, (self.rect.x + 12, self.rect.y + 26))
        for i in range(HOTBAR_CAPACITY):
            sr = self._hotbar_slot_rect(i)
            sel = i == self.inventory.equipped_slot
            bg_c = (80, 80, 110) if sel else (45, 45, 60)
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            bd = (200, 200, 240) if sel else (100, 100, 120)
            pygame.draw.rect(surface, bd, sr, 1, border_radius=4)
            # Slot number
            ns = self.font.render(str(i + 1), True, (170, 170, 190))
            surface.blit(ns, (sr.x + 3, sr.y + 2))
            if i in self.inventory.hotbar:
                item_id, count = self.inventory.hotbar[i]
                hb_ench = self.inventory.hotbar_enchantments.get(i)
                hb_rar = self.inventory.hotbar_rarities.get(i, 'common')
                self._draw_item(surface, sr, item_id, count, mx, my, tooltip, hb_ench, hb_rar)

        # -- Separator + page indicator --
        hotbar_h = self.slot_size + 14
        sep_y = self.rect.y + 38 + self.slot_size + 4
        pygame.draw.line(surface, (80, 80, 100),
                         (self.rect.x + 12, sep_y),
                         (self.rect.right - 12, sep_y), 1)
        page_label = self.font.render(
            f"Page {self.page + 1}/{INVENTORY_PAGES}", True, GRAY)
        surface.blit(page_label,
                     (self.rect.right - 12 - page_label.get_width(), sep_y + 2))

        # -- Main inventory grid (current page) --
        off = self._page_offset()
        for i in range(INVENTORY_SLOTS_PER_PAGE):
            slot_idx = off + i
            sr = self._inv_slot_rect(i)
            bg_c = (45, 45, 60)
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, (100, 100, 120), sr, 1, border_radius=4)
            if slot_idx in self.inventory.slots:
                item_id, count = self.inventory.slots[slot_idx]
                sl_ench = self.inventory.slot_enchantments.get(slot_idx)
                sl_rar = self.inventory.slot_rarities.get(slot_idx, 'common')
                self._draw_item(surface, sr, item_id, count, mx, my, tooltip, sl_ench, sl_rar)

        # -- Page navigation arrows --
        nav_y = (self.rect.y + 38 + hotbar_h
                 + self.rows * (self.slot_size + 6) + 4)
        prev_r = pygame.Rect(self.rect.x + 12, nav_y, 60, 28)
        next_r = pygame.Rect(self.rect.right - 72, nav_y, 60, 28)
        for r, label in [(prev_r, "< Prev"), (next_r, "Next >")]:
            hov = r.collidepoint(mx, my)
            pygame.draw.rect(surface, (70, 70, 100) if hov else (50, 50, 70),
                             r, border_radius=4)
            pygame.draw.rect(surface, (130, 130, 160), r, 1, border_radius=4)
            lt = self.font.render(label, True, WHITE)
            surface.blit(lt, (r.centerx - lt.get_width() // 2,
                              r.centery - lt.get_height() // 2))

        # -- Draw held item on cursor --
        if self.inventory.held_item:
            item_id, count = self.inventory.held_item
            icon = self.textures.cache.get(f'item_{item_id}')
            if icon:
                surface.blit(pygame.transform.scale(icon, (34, 34)),
                             (mx - 17, my - 17))
            if self.inventory.held_enchant:
                from enchantments.effects import ENCHANT_COLORS
                ec = ENCHANT_COLORS.get(self.inventory.held_enchant['type'],
                                        (200, 200, 200))
                pygame.draw.rect(surface, ec,
                                 (mx - 19, my - 19, 38, 38), 2,
                                 border_radius=4)
            if count > 1:
                ct = self.font.render(str(count), True, WHITE)
                surface.blit(ct, (mx + 8, my + 8))

        # -- Split dialog overlay --
        self.split_dialog.draw(surface)

    def _draw_item(self, surface: pygame.Surface, sr: pygame.Rect,
                   item_id: str, count: int,
                   mx: int, my: int, tooltip: Tooltip,
                   enchant: dict | None = None,
                   rarity: str = 'common') -> None:
        # Rarity border
        if rarity and rarity != 'common':
            from ui.rarity_display import draw_rarity_border
            draw_rarity_border(surface, sr, rarity)
        elif enchant:
            from enchantments.effects import ENCHANT_COLORS
            ec = ENCHANT_COLORS.get(enchant['type'], (200, 200, 200))
            pygame.draw.rect(surface, ec, sr, 2, border_radius=4)
        from ui.rarity_display import draw_enhancement_border
        draw_enhancement_border(surface, sr, item_id)
        icon = self.textures.cache.get(f'item_{item_id}')
        if icon:
            surface.blit(pygame.transform.scale(icon, (34, 34)),
                         (sr.x + 7, sr.y + 7))
        if count > 1:
            ct = self.font.render(str(count), True, WHITE)
            surface.blit(ct, (sr.x + self.slot_size - ct.get_width() - 4,
                              sr.y + self.slot_size - ct.get_height() - 2))
        if sr.collidepoint(mx, my) and item_id in ITEM_DATA:
            d = ITEM_DATA[item_id]
            name = d[0]
            name_color = get_item_color(item_id, rarity)
            if rarity and rarity != 'common':
                name = f"{rarity.title()} {name}"
            from data.quality import get_stat_description
            lines = [name, get_stat_description(item_id, rarity)]
            colors = [name_color, WHITE]
            if rarity and rarity != 'common':
                from ui.rarity_display import insert_rarity_tooltip
                insert_rarity_tooltip(lines, colors, rarity)
            if enchant:
                from enchantments.effects import (
                    get_enchant_display_prefix, ENCHANT_COLORS as EC2,
                )
                prefix = get_enchant_display_prefix(enchant)
                if prefix:
                    lines[0] = f"{prefix} {name}"
                    colors[0] = EC2.get(enchant['type'], name_color)
                ench_line = (f"Enchant: {enchant['type'].title()}"
                             f" Lv.{enchant['level']}")
                lines.insert(1, ench_line)
                colors.insert(1, EC2.get(enchant['type'], CYAN))
            tooltip.show(lines, (mx, my), colors)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        # Split dialog takes priority
        if self.split_dialog.active:
            return self.split_dialog.handle_event(event, self.inventory)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Check hotbar slots
            for i in range(HOTBAR_CAPACITY):
                sr = self._hotbar_slot_rect(i)
                if sr.collidepoint(mx, my):
                    self._click_hotbar_slot(i)
                    return True

            # Check inventory slots
            off = self._page_offset()
            for i in range(INVENTORY_SLOTS_PER_PAGE):
                slot_idx = off + i
                sr = self._inv_slot_rect(i)
                if sr.collidepoint(mx, my):
                    self._click_inv_slot(slot_idx)
                    return True

            # Page buttons
            hotbar_h = self.slot_size + 14
            nav_y = (self.rect.y + 38 + hotbar_h
                     + self.rows * (self.slot_size + 6) + 4)
            prev_r = pygame.Rect(self.rect.x + 12, nav_y, 60, 28)
            next_r = pygame.Rect(self.rect.right - 72, nav_y, 60, 28)
            if prev_r.collidepoint(mx, my):
                self.page = (self.page - 1) % INVENTORY_PAGES
                return True
            if next_r.collidepoint(mx, my):
                self.page = (self.page + 1) % INVENTORY_PAGES
                return True

        # Right-click: split stack or drop held item
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = event.pos
            if self.inventory.held_item:
                item_id, count = self.inventory.held_item
                overflow = self.inventory.add_item_enchanted(
                    item_id, self.inventory.held_enchant, count,
                    self.inventory.held_rarity)
                if overflow == 0:
                    self.inventory.held_item = None
                    self.inventory.held_enchant = None
                    self.inventory.held_rarity = 'common'
                return True
            # Check hotbar slots for split
            for i in range(HOTBAR_CAPACITY):
                sr = self._hotbar_slot_rect(i)
                if sr.collidepoint(mx, my) and i in self.inventory.hotbar:
                    iid, cnt = self.inventory.hotbar[i]
                    if cnt > 1:
                        self.split_dialog.open('hotbar', i, iid, cnt, mx, my)
                        return True
            # Check inventory slots for split
            off = self._page_offset()
            for i in range(INVENTORY_SLOTS_PER_PAGE):
                slot_idx = off + i
                sr = self._inv_slot_rect(i)
                if sr.collidepoint(mx, my) and slot_idx in self.inventory.slots:
                    iid, cnt = self.inventory.slots[slot_idx]
                    if cnt > 1:
                        self.split_dialog.open('slots', slot_idx, iid, cnt, mx, my)
                        return True
            return False

        # Scroll wheel for split dialog is handled above; here pass inventory scrolls
        if event.type == pygame.MOUSEWHEEL:
            return False
        return False

    def _click_hotbar_slot(self, slot: int) -> None:
        inv = self.inventory
        has_held = inv.held_item is not None
        has_slot = slot in inv.hotbar
        if not has_held and not has_slot:
            return
        if not has_held and has_slot:
            # Pick up from hotbar
            inv.held_item = inv.hotbar.pop(slot)
            inv.held_enchant = inv.hotbar_enchantments.pop(slot, None)
            pick_up_rarity(inv, 'hotbar', slot)
        elif has_held and not has_slot:
            # Place into empty hotbar slot
            inv.hotbar[slot] = inv.held_item
            inv.held_item = None
            if inv.held_enchant:
                inv.hotbar_enchantments[slot] = inv.held_enchant
            inv.held_enchant = None
            place_rarity(inv, 'hotbar', slot)
        else:
            # Swap held with hotbar slot
            old_ench = inv.hotbar_enchantments.pop(slot, None)
            if inv.held_enchant:
                inv.hotbar_enchantments[slot] = inv.held_enchant
            inv.held_enchant = old_ench
            swap_rarity(inv, 'hotbar', slot)
            inv.hotbar[slot], inv.held_item = inv.held_item, inv.hotbar[slot]

    def _click_inv_slot(self, slot: int) -> None:
        inv = self.inventory
        has_held = inv.held_item is not None
        has_slot = slot in inv.slots
        if not has_held and not has_slot:
            return
        if not has_held and has_slot:
            # Pick up from inventory
            inv.held_item = inv.slots.pop(slot)
            inv.held_enchant = inv.slot_enchantments.pop(slot, None)
            pick_up_rarity(inv, 'slots', slot)
        elif has_held and not has_slot:
            # Place into empty inventory slot
            inv.slots[slot] = inv.held_item
            inv.held_item = None
            if inv.held_enchant:
                inv.slot_enchantments[slot] = inv.held_enchant
            inv.held_enchant = None
            place_rarity(inv, 'slots', slot)
        else:
            # Swap held with inventory slot
            old_ench = inv.slot_enchantments.pop(slot, None)
            if inv.held_enchant:
                inv.slot_enchantments[slot] = inv.held_enchant
            inv.held_enchant = old_ench
            swap_rarity(inv, 'slots', slot)
            inv.slots[slot], inv.held_item = inv.held_item, inv.slots[slot]
