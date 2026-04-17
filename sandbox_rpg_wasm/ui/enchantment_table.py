"""Enchantment Table UI — extracted from gui.py.

3×3 input grid, combine button, and paginated inventory panel.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

import pygame

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, CYAN, PURPLE,
    INVENTORY_SLOTS_PER_PAGE, INVENTORY_PAGES,
    UI_ENCHANT_PANEL_BG, UI_ENCHANT_PANEL_BORDER,
    UI_ENCHANT_SLOT_BG_NORMAL, UI_ENCHANT_SLOT_BG_HOVER,
    UI_ENCHANT_SLOT_BORDER,
    UI_ENCHANT_COMBINE_ACTIVE, UI_ENCHANT_COMBINE_ACTIVE_HOVER,
    UI_ENCHANT_COMBINE_ACTIVE_BORDER,
    UI_ENCHANT_COMBINE_INACTIVE, UI_ENCHANT_COMBINE_INACTIVE_BORDER,
    UI_ENCHANT_DIVIDER,
    UI_CHEST_SLOT_BG_NORMAL, UI_CHEST_SLOT_BG_HOVER,
    UI_SLOT_BORDER_NORMAL,
    UI_ENCHANT_FALLBACK,
    UI_NAV_HOVER, UI_NAV_NORMAL,
    UI_TEXT_MUTED,
)
from core.item_presentation import build_item_presentation
from data import ITEM_DATA, get_stat_description
from core.components import Storage, Inventory
from ui.rarity_display import draw_rarity_border, insert_rarity_tooltip
from ui.draggable import DraggableWindow


class EnchantmentTableUI:
    """Enchantment table — 3×3 input grid, combine button, + inventory."""

    CAPACITY = 9
    PW, PH = 570, 300
    RESULT_BAR_H = 34   # height of result preview bar at bottom

    def __init__(self, textures: Any) -> None:
        self.textures = textures
        self.font = pygame.font.SysFont('consolas, monospace', 14)
        self.title_font = pygame.font.SysFont('consolas, monospace', 18, bold=True)
        self.slot_size = 44
        self.table_cols = 3
        self.inv_cols = 6
        self.inv_page: int = 0
        self.dw = DraggableWindow(570, 300, title="Enchantment Table")

    # -- layout helpers --
    def _panel_rect(self) -> Tuple[int, int]:
        return self.dw.content_rect.topleft

    def _grid_origin(self, px: int, py: int) -> Tuple[int, int]:
        return px + 14, py + 30

    def _divider_x(self, px: int) -> int:
        """X position of the vertical divider between table and inventory."""
        return px + 14 + self.table_cols * (self.slot_size + 4) + 48

    def _inv_origin(self, px: int, py: int) -> Tuple[int, int]:
        return self._divider_x(px) + 12, py + 30

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, storage: Storage,
             inventory: Inventory, tooltip: 'Tooltip') -> None:
        px, py = self._panel_rect()
        pw, ph = self.PW, self.PH
        ss = self.slot_size
        bar_h = self.RESULT_BAR_H
        content_h = ph - bar_h  # top area above result bar

        # Main panel background
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill(UI_ENCHANT_PANEL_BG)
        surface.blit(bg, (px, py))
        mx, my = pygame.mouse.get_pos()

        # ---- Left: Enchantment Table ----
        grid_ox, grid_oy = self._grid_origin(px, py)
        self._draw_table_grid(surface, storage, grid_ox, grid_oy,
                              mx, my, tooltip)

        # Combine button
        btn_y = grid_oy + 3 * (ss + 4) + 6
        btn_w = 3 * (ss + 4) - 4
        btn_r = pygame.Rect(grid_ox, btn_y, btn_w, 26)
        from enchantments.recipes import try_combine
        result = try_combine(storage.slots, storage.slot_enchantments,
                             storage.slot_rarities)
        hov = btn_r.collidepoint(mx, my)
        if result:
            bc = UI_ENCHANT_COMBINE_ACTIVE if not hov else UI_ENCHANT_COMBINE_ACTIVE_HOVER
            bd = UI_ENCHANT_COMBINE_ACTIVE_BORDER
        else:
            bc = UI_ENCHANT_COMBINE_INACTIVE
            bd = UI_ENCHANT_COMBINE_INACTIVE_BORDER
        pygame.draw.rect(surface, bc, btn_r, border_radius=5)
        pygame.draw.rect(surface, bd, btn_r, 1, border_radius=5)
        ct = self.font.render("Combine", True, WHITE if result else GRAY)
        surface.blit(ct, (btn_r.centerx - ct.get_width() // 2,
                          btn_r.centery - ct.get_height() // 2))

        # ---- Divider ----
        div_x = self._divider_x(px)
        pygame.draw.line(surface, GRAY,
                         (div_x, py + 6), (div_x, py + content_h - 4), 1)

        # ---- Right: Inventory (paginated) ----
        inv_ox, inv_oy = self._inv_origin(px, py)
        title_r = self.title_font.render("Inventory", True, CYAN)
        surface.blit(title_r, (inv_ox, py + 6))
        page_label = self.font.render(
            f"Page {self.inv_page + 1}/{INVENTORY_PAGES}", True, GRAY)
        surface.blit(page_label,
                     (px + pw - 10 - page_label.get_width(), py + 8))

        page_off = self.inv_page * INVENTORY_SLOTS_PER_PAGE
        for i in range(INVENTORY_SLOTS_PER_PAGE):
            real = page_off + i
            col = i % self.inv_cols
            row = i // self.inv_cols
            x = inv_ox + col * (ss + 4)
            y = inv_oy + row * (ss + 4)
            sr = pygame.Rect(x, y, ss, ss)
            bg_c = UI_CHEST_SLOT_BG_NORMAL if not sr.collidepoint(mx, my) else UI_CHEST_SLOT_BG_HOVER
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, UI_SLOT_BORDER_NORMAL, sr, 1, border_radius=4)
            if real in inventory.slots:
                item_id, count = inventory.slots[real]
                ench = inventory.slot_enchantments.get(real)
                rar = inventory.slot_rarities.get(real, 'common')
                self._draw_slot_item(surface, sr, item_id, count,
                                     mx, my, tooltip,
                                     "Click: Move to Table", ench, rar)

        # Page nav
        grid_bottom = inv_oy + (INVENTORY_SLOTS_PER_PAGE // self.inv_cols) * (ss + 4) + 2
        prev_r = pygame.Rect(inv_ox, grid_bottom, 55, 22)
        next_r = pygame.Rect(px + pw - 10 - 55, grid_bottom, 55, 22)
        for r, label in [(prev_r, "< Prev"), (next_r, "Next >")]:
            hov2 = r.collidepoint(mx, my)
            pygame.draw.rect(surface, UI_NAV_HOVER if hov2 else UI_NAV_NORMAL,
                             r, border_radius=4)
            pygame.draw.rect(surface, UI_TEXT_MUTED, r, 1, border_radius=4)
            lt = self.font.render(label, True, WHITE)
            surface.blit(lt, (r.centerx - lt.get_width() // 2,
                              r.centery - lt.get_height() // 2))

        # ---- Bottom result bar ----
        bar_y = py + content_h
        bar_rect = pygame.Rect(px + 2, bar_y, pw - 4, bar_h - 2)
        pygame.draw.line(surface, UI_ENCHANT_DIVIDER,
                         (px + 6, bar_y), (px + pw - 6, bar_y), 1)
        if result:
            rid = result['result_item']
            if rid in ITEM_DATA:
                ench = result.get('result_enchant')
                rr = result.get('result_rarity', 'common')
                presentation = build_item_presentation(rid, rr, ench)
                icon = self.textures.cache.get(f'item_{rid}')
                icon_x = px + 14
                text_x = icon_x + 26
                center_y = bar_y + (bar_h - 2) // 2
                if icon:
                    surface.blit(pygame.transform.scale(icon, (20, 20)),
                                 (icon_x, center_y - 10))
                nt = self.font.render(presentation['label'], True,
                                      presentation['color'])
                surface.blit(nt, (text_x, center_y - nt.get_height() // 2))

        # Chrome
        self.dw.draw_chrome(surface)

    def _draw_table_grid(self, surface: pygame.Surface, storage: Storage,
                         ox: int, oy: int, mx: int, my: int,
                         tooltip: 'Tooltip') -> None:
        ss = self.slot_size
        for i in range(self.CAPACITY):
            col = i % self.table_cols
            row = i // self.table_cols
            x = ox + col * (ss + 4)
            y = oy + row * (ss + 4)
            sr = pygame.Rect(x, y, ss, ss)
            bg_c = UI_ENCHANT_SLOT_BG_NORMAL if not sr.collidepoint(mx, my) else UI_ENCHANT_SLOT_BG_HOVER
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, UI_ENCHANT_SLOT_BORDER, sr, 1, border_radius=4)
            if i in storage.slots:
                item_id, count = storage.slots[i]
                ench = storage.slot_enchantments.get(i)
                rar = storage.slot_rarities.get(i, 'common')
                self._draw_slot_item(surface, sr, item_id, count,
                                     mx, my, tooltip,
                                     "Click: Return to Inventory", ench, rar)

    def _draw_slot_item(self, surface: pygame.Surface, sr: pygame.Rect,
                        item_id: str, count: int, mx: int, my: int,
                        tooltip: 'Tooltip', action: str,
                        enchant: Optional[Dict] = None,
                        rarity: str = 'common') -> None:
        ss = self.slot_size
        # Rarity border (the ONLY item border)
        if rarity != 'common':
            draw_rarity_border(surface, sr, rarity)
        icon = self.textures.cache.get(f'item_{item_id}')
        if icon:
            surface.blit(pygame.transform.scale(icon, (30, 30)),
                         (sr.x + 7, sr.y + 7))
        if count > 1:
            ct = self.font.render(str(count), True, WHITE)
            surface.blit(ct, (sr.x + ss - ct.get_width() - 3,
                              sr.y + ss - ct.get_height() - 2))
        if sr.collidepoint(mx, my) and item_id in ITEM_DATA:
            presentation = build_item_presentation(item_id, rarity, enchant)
            lines = [presentation['label'], get_stat_description(item_id, rarity), action]
            colors = [presentation['color'], WHITE, GRAY]
            insert_rarity_tooltip(lines, colors, rarity)
            if enchant:
                from enchantments.effects import ENCHANT_COLORS as EC
                ench_line = (f"Enchant: {enchant['type'].title()}"
                             f" Lv.{enchant['level']}")
                lines.insert(1, ench_line)
                colors.insert(1, EC.get(enchant['type'], CYAN))
            tooltip.show(lines, (mx, my), colors)

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event,
                     storage: Storage, inventory: Inventory) -> bool:
        if self.dw.handle_event(event):
            return True
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos
        px, py = self._panel_rect()
        pw, ph = self.PW, self.PH
        ss = self.slot_size
        grid_ox, grid_oy = self._grid_origin(px, py)

        # Click table slot → return item to inventory
        for i in range(self.CAPACITY):
            col = i % self.table_cols
            row = i // self.table_cols
            x = grid_ox + col * (ss + 4)
            y = grid_oy + row * (ss + 4)
            if pygame.Rect(x, y, ss, ss).collidepoint(mx, my):
                if i in storage.slots:
                    item_id, count = storage.slots[i]
                    enchant = storage.slot_enchantments.pop(i, None)
                    rarity = storage.slot_rarities.pop(i, 'common')
                    overflow = inventory.add_item_enchanted(
                        item_id, enchant, count, rarity)
                    if overflow == 0:
                        del storage.slots[i]
                    else:
                        storage.slots[i] = (item_id, overflow)
                        if enchant:
                            storage.slot_enchantments[i] = enchant
                        if rarity != 'common':
                            storage.slot_rarities[i] = rarity
                return True

        # Combine button
        btn_y = grid_oy + 3 * (ss + 4) + 6
        btn_w = 3 * (ss + 4) - 4
        if pygame.Rect(grid_ox, btn_y, btn_w, 26).collidepoint(mx, my):
            self._do_combine(storage, inventory)
            return True

        # Click inventory slot → move to table (auto-separate stacks)
        inv_ox, inv_oy = self._inv_origin(px, py)
        page_off = self.inv_page * INVENTORY_SLOTS_PER_PAGE
        for i in range(INVENTORY_SLOTS_PER_PAGE):
            col = i % self.inv_cols
            row = i // self.inv_cols
            x = inv_ox + col * (ss + 4)
            y = inv_oy + row * (ss + 4)
            if pygame.Rect(x, y, ss, ss).collidepoint(mx, my):
                real = page_off + i
                if real in inventory.slots:
                    item_id, count = inventory.slots[real]
                    enchant = inventory.slot_enchantments.get(real)
                    rarity = inventory.slot_rarities.get(real, 'common')
                    # Place exactly 1 into the table — NEVER stack on table
                    placed = False
                    for ti in range(self.CAPACITY):
                        if ti not in storage.slots:
                            storage.slots[ti] = (item_id, 1)
                            if enchant:
                                storage.slot_enchantments[ti] = dict(enchant)
                            if rarity != 'common':
                                storage.slot_rarities[ti] = rarity
                            placed = True
                            break
                    if placed:
                        if count > 1:
                            inventory.slots[real] = (item_id, count - 1)
                        else:
                            del inventory.slots[real]
                            inventory.slot_enchantments.pop(real, None)
                            inventory.slot_rarities.pop(real, 'common')
                return True

        # Page nav
        grid_bottom = inv_oy + (INVENTORY_SLOTS_PER_PAGE // self.inv_cols) * (ss + 4) + 2
        prev_r = pygame.Rect(inv_ox, grid_bottom, 55, 22)
        next_r = pygame.Rect(px + pw - 10 - 55, grid_bottom, 55, 22)
        if prev_r.collidepoint(mx, my):
            self.inv_page = (self.inv_page - 1) % INVENTORY_PAGES
            return True
        if next_r.collidepoint(mx, my):
            self.inv_page = (self.inv_page + 1) % INVENTORY_PAGES
            return True
        return False

    def _do_combine(self, storage: Storage,
                    inventory: Inventory) -> None:
        from enchantments.recipes import try_combine
        result = try_combine(storage.slots, storage.slot_enchantments,
                             storage.slot_rarities)
        if not result:
            return
        for idx in result['consume']:
            storage.slots.pop(idx, None)
            storage.slot_enchantments.pop(idx, None)
            storage.slot_rarities.pop(idx, 'common')
        result_item = result['result_item']
        result_enchant = result.get('result_enchant')
        result_rarity = result.get('result_rarity', 'common')
        for i in range(self.CAPACITY):
            if i not in storage.slots:
                storage.slots[i] = (result_item, 1)
                if result_enchant:
                    storage.slot_enchantments[i] = result_enchant
                if result_rarity != 'common':
                    storage.slot_rarities[i] = result_rarity
                return
        overflow = inventory.add_item_enchanted(
            result_item, result_enchant, 1, result_rarity)
