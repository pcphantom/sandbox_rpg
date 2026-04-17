"""Inventory grid — hotbar row + paginated inventory with drag-drop."""
from __future__ import annotations

from typing import Any

import pygame

from core.constants import (WHITE, GRAY, CYAN, INVENTORY_SLOTS_PER_PAGE,
                            HOTBAR_CAPACITY, INVENTORY_PAGES, INVENTORY_COLS,
                            SCREEN_WIDTH, SCREEN_HEIGHT,
                            UI_BORDER_LIGHT, UI_SLOT_BG_SELECTED,
                            UI_SLOT_BG_NORMAL, UI_TEXT_HIGHLIGHT,
                            UI_SLOT_BORDER_NORMAL, HOTBAR_SLOT_NUMBER_COLOR,
                            UI_SLOT_SEPARATOR, UI_NAV_HOVER, UI_NAV_NORMAL,
                            UI_TEXT_MUTED, UI_ENCHANT_FALLBACK,
                            UI_CHEST_SORT_HOVER, UI_CHEST_SORT_NORMAL,
                            UI_CHEST_SORT_BORDER)
from core.components import Inventory
from core.item_presentation import build_item_presentation
from data import ITEM_DATA
from ui.elements import UIElement, Tooltip
from ui.split_dialog import SplitDialog
from ui.drop_confirm import DropConfirmDialog
from ui.inventory_sort import sort_inventory_slots
from ui.rarity_display import pick_up_rarity, place_rarity, swap_rarity
from ui.draggable import DraggableWindow


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
        self.drop_confirm = DropConfirmDialog()
        # Which hotbar is shown: -1 = primary, 0+ = extra bar index
        self.hotbar_view_index: int = -1
        # Arrow rects for hotbar cycling (set during draw)
        self._up_arrow_r: pygame.Rect | None = None
        self._dn_arrow_r: pygame.Rect | None = None
        # Draggable window — positioned on right side for stone oven pairing
        self.dw = DraggableWindow(
            rect.width, rect.height, title="Inventory",
            start_x=SCREEN_WIDTH // 2 - rect.width // 2,
            start_y=SCREEN_HEIGHT // 2 - rect.height // 2 - 11)

    def _sync_rect(self) -> None:
        """Keep UIElement rect in sync with the draggable window position."""
        cr = self.dw.content_rect
        self.rect = cr

    def _page_offset(self) -> int:
        return self.page * INVENTORY_SLOTS_PER_PAGE

    def _grid_left(self) -> int:
        """Left x for centred slot grid (used for both hotbar and inventory)."""
        grid_w = self.cols * (self.slot_size + 6) - 6
        return self.rect.x + (self.rect.width - grid_w) // 2

    def _hotbar_slot_rect(self, i: int) -> pygame.Rect:
        x = self._grid_left() + i * (self.slot_size + 6)
        y = self.rect.y + 40
        return pygame.Rect(x, y, self.slot_size, self.slot_size)

    def _inv_slot_rect(self, i: int) -> pygame.Rect:
        col = i % self.cols
        row = i // self.cols
        hotbar_h = self.slot_size + 32  # hotbar row + gap + page indicator
        x = self._grid_left() + col * (self.slot_size + 6)
        y = self.rect.y + 40 + hotbar_h + row * (self.slot_size + 6)
        return pygame.Rect(x, y, self.slot_size, self.slot_size)

    def _total_hotbar_count(self) -> int:
        """Total number of hotbars: 1 primary + N extras."""
        abm = self.inventory._action_bar_ref
        return 1 + (len(abm.extra_bars) if abm else 0)

    def _get_viewed_bar(self):
        """Return (slots, enchants, rarities, is_primary) for current view."""
        if self.hotbar_view_index < 0:
            return (self.inventory.hotbar,
                    self.inventory.hotbar_enchantments,
                    self.inventory.hotbar_rarities, True)
        abm = self.inventory._action_bar_ref
        if abm and 0 <= self.hotbar_view_index < len(abm.extra_bars):
            bar = abm.extra_bars[self.hotbar_view_index]
            return (bar.slots, bar.slot_enchantments,
                    bar.slot_rarities, False)
        # Fallback to primary if index is out of range
        self.hotbar_view_index = -1
        return (self.inventory.hotbar,
                self.inventory.hotbar_enchantments,
                self.inventory.hotbar_rarities, True)

    def draw(self, surface: pygame.Surface, tooltip: Tooltip) -> None:
        if not self.visible:
            return
        self._sync_rect()
        bg = pygame.Surface((self.rect.width, self.rect.height),
                            pygame.SRCALPHA)
        bg.fill((20, 20, 32, 235))
        surface.blit(bg, self.rect.topleft)

        mx, my = pygame.mouse.get_pos()
        gl = self._grid_left()

        # -- Hotbar row label + cycling arrows --
        total_bars = self._total_hotbar_count()
        if self.hotbar_view_index < 0:
            bar_label_str = "Hotbar"
        else:
            bar_label_str = f"Bar {self.hotbar_view_index + 2}"
        hotbar_label = self.font.render(bar_label_str, True, GRAY)
        surface.blit(hotbar_label, (gl, self.rect.y + 26))

        # Up/down cycling arrows + bar indicator
        if total_bars > 1:
            # Bar indicator right after label
            bar_num = self.hotbar_view_index + 2 if self.hotbar_view_index >= 0 else 1
            ind_str = f"{bar_num}/{total_bars}"
            ind_surf = self.font.render(ind_str, True, UI_TEXT_MUTED)
            ind_x = gl + hotbar_label.get_width() + 8
            surface.blit(ind_surf, (ind_x, self.rect.y + 27))
            # Arrows to the right of the hotbar slots, vertically centred
            grid_right = gl + self.cols * (self.slot_size + 6) - 6
            arrow_x = grid_right + 8
            hotbar_center_y = self.rect.y + 40 + self.slot_size // 2
            arrow_y = hotbar_center_y - 13  # (12 + 2 + 12) / 2 = 13
            self._up_arrow_r = pygame.Rect(arrow_x, arrow_y, 20, 12)
            self._dn_arrow_r = pygame.Rect(arrow_x, arrow_y + 14, 20, 12)
            for ar, tri in [(self._up_arrow_r, 'up'),
                            (self._dn_arrow_r, 'dn')]:
                hov = ar.collidepoint(mx, my)
                pygame.draw.rect(surface,
                                 (70, 70, 100) if hov else (40, 40, 60),
                                 ar, border_radius=2)
                pygame.draw.rect(surface, (110, 110, 140), ar, 1,
                                 border_radius=2)
                cx, cy = ar.centerx, ar.centery
                if tri == 'up':
                    pygame.draw.polygon(surface, WHITE if hov else GRAY,
                                        [(cx, cy - 3), (cx - 5, cy + 3),
                                         (cx + 5, cy + 3)])
                else:
                    pygame.draw.polygon(surface, WHITE if hov else GRAY,
                                        [(cx, cy + 3), (cx - 5, cy - 3),
                                         (cx + 5, cy - 3)])
        else:
            self._up_arrow_r = None
            self._dn_arrow_r = None

        # -- Hotbar slots (primary or extra bar) --
        slots_d, enchants_d, rarities_d, is_primary = self._get_viewed_bar()
        for i in range(HOTBAR_CAPACITY):
            sr = self._hotbar_slot_rect(i)
            sel = is_primary and i == self.inventory.equipped_slot
            bg_c = UI_SLOT_BG_SELECTED if sel else UI_SLOT_BG_NORMAL
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            bd = UI_TEXT_HIGHLIGHT if sel else UI_SLOT_BORDER_NORMAL
            pygame.draw.rect(surface, bd, sr, 1, border_radius=4)
            # Slot number
            ns = self.font.render(str(i + 1), True, HOTBAR_SLOT_NUMBER_COLOR)
            surface.blit(ns, (sr.x + 3, sr.y + 2))
            if i in slots_d:
                item_id, count = slots_d[i]
                hb_ench = enchants_d.get(i)
                hb_rar = rarities_d.get(i, 'common')
                self._draw_item(surface, sr, item_id, count, mx, my, tooltip, hb_ench, hb_rar)

        # -- Separator + page indicator --
        hotbar_h = self.slot_size + 32
        sep_y = self.rect.y + 40 + self.slot_size + 6
        pygame.draw.line(surface, UI_SLOT_SEPARATOR,
                         (gl, sep_y),
                         (self.rect.right - (self.rect.right - gl
                          - self.cols * (self.slot_size + 6) + 6), sep_y), 1)
        page_label = self.font.render(
            f"Page {self.page + 1}/{INVENTORY_PAGES}", True, GRAY)
        surface.blit(page_label,
                     (self.rect.right - 12 - page_label.get_width(), sep_y + 2))

        # -- Main inventory grid (current page) --
        off = self._page_offset()
        for i in range(INVENTORY_SLOTS_PER_PAGE):
            slot_idx = off + i
            sr = self._inv_slot_rect(i)
            bg_c = UI_SLOT_BG_NORMAL
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, UI_SLOT_BORDER_NORMAL, sr, 1, border_radius=4)
            if slot_idx in self.inventory.slots:
                item_id, count = self.inventory.slots[slot_idx]
                sl_ench = self.inventory.slot_enchantments.get(slot_idx)
                sl_rar = self.inventory.slot_rarities.get(slot_idx, 'common')
                self._draw_item(surface, sr, item_id, count, mx, my, tooltip, sl_ench, sl_rar)

        # -- Page navigation arrows + Sort button --
        nav_y = (self.rect.y + 40 + hotbar_h
                 + self.rows * (self.slot_size + 6) + 4)
        btn_area_w = self.cols * (self.slot_size + 6) - 6
        prev_r = pygame.Rect(gl, nav_y, 60, 28)
        next_r = pygame.Rect(gl + btn_area_w - 60, nav_y, 60, 28)
        # Sort button centred between prev and next
        sort_r = pygame.Rect(gl + 60 + 10, nav_y, 55, 28)
        for r, label in [(prev_r, "< Prev"), (next_r, "Next >")]:
            hov = r.collidepoint(mx, my)
            pygame.draw.rect(surface, UI_NAV_HOVER if hov else UI_NAV_NORMAL,
                             r, border_radius=4)
            pygame.draw.rect(surface, UI_TEXT_MUTED, r, 1, border_radius=4)
            lt = self.font.render(label, True, WHITE)
            surface.blit(lt, (r.centerx - lt.get_width() // 2,
                              r.centery - lt.get_height() // 2))
        # Sort button
        sort_hov = sort_r.collidepoint(mx, my)
        pygame.draw.rect(surface,
                         UI_CHEST_SORT_HOVER if sort_hov else UI_CHEST_SORT_NORMAL,
                         sort_r, border_radius=4)
        pygame.draw.rect(surface, UI_CHEST_SORT_BORDER, sort_r, 1,
                         border_radius=4)
        sort_txt = self.font.render("Sort", True, WHITE)
        surface.blit(sort_txt, (sort_r.centerx - sort_txt.get_width() // 2,
                                sort_r.centery - sort_txt.get_height() // 2))

        # -- Draw held item on cursor --
        if self.inventory.held_item:
            item_id, count = self.inventory.held_item
            icon = self.textures.cache.get(f'item_{item_id}')
            if icon:
                surface.blit(pygame.transform.scale(icon, (34, 34)),
                             (mx - 17, my - 17))
            if self.inventory.held_enchant:
                pass  # No enchant border on held items — rarity only
            if count > 1:
                ct = self.font.render(str(count), True, WHITE)
                surface.blit(ct, (mx + 8, my + 8))

        # -- Split dialog overlay --
        self.split_dialog.draw(surface)

        # -- Drop confirm dialog overlay --
        self.drop_confirm.draw(surface)

        # -- Draggable window chrome (title bar, close button, resize) --
        self.dw.draw_chrome(surface)

    def _draw_item(self, surface: pygame.Surface, sr: pygame.Rect,
                   item_id: str, count: int,
                   mx: int, my: int, tooltip: Tooltip,
                   enchant: dict | None = None,
                   rarity: str = 'common') -> None:
        # Rarity border (the ONLY item border)
        if rarity and rarity != 'common':
            from ui.rarity_display import draw_rarity_border
            draw_rarity_border(surface, sr, rarity)
        icon = self.textures.cache.get(f'item_{item_id}')
        if icon:
            surface.blit(pygame.transform.scale(icon, (34, 34)),
                         (sr.x + 7, sr.y + 7))
        if count > 1:
            ct = self.font.render(str(count), True, WHITE)
            surface.blit(ct, (sr.x + self.slot_size - ct.get_width() - 4,
                              sr.y + self.slot_size - ct.get_height() - 2))
        if sr.collidepoint(mx, my) and item_id in ITEM_DATA:
            presentation = build_item_presentation(item_id, rarity, enchant)
            from data.quality import get_stat_description
            lines = [presentation['label'], get_stat_description(item_id, rarity)]
            colors = [presentation['color'], WHITE]
            if rarity and rarity != 'common':
                from ui.rarity_display import insert_rarity_tooltip
                insert_rarity_tooltip(lines, colors, rarity)
            if enchant:
                from enchantments.effects import (
                    get_enchant_display_prefix, ENCHANT_COLORS as EC2,
                )
                ench_line = (f"Enchant: {enchant['type'].title()}"
                             f" Lv.{enchant['level']}")
                lines.insert(1, ench_line)
                colors.insert(1, EC2.get(enchant['type'], CYAN))
            tooltip.show(lines, (mx, my), colors)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        self._sync_rect()
        # Draggable window chrome (drag, close, resize)
        if self.dw.handle_event(event):
            # close_requested is checked by the caller (events.py)
            return True
        # Drop confirm dialog takes priority when active
        if self.drop_confirm.active:
            return self.drop_confirm.handle_event(event, self.inventory)
        # Split dialog takes priority
        if self.split_dialog.active:
            return self.split_dialog.handle_event(event, self.inventory)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Hotbar cycling arrows
            total_bars = self._total_hotbar_count()
            if total_bars > 1:
                if (self._up_arrow_r is not None
                        and self._up_arrow_r.collidepoint(mx, my)):
                    # Cycle up: primary(-1) → last extra, or current-1
                    if self.hotbar_view_index < 0:
                        self.hotbar_view_index = total_bars - 2
                    else:
                        self.hotbar_view_index -= 1
                        if self.hotbar_view_index < -1:
                            self.hotbar_view_index = total_bars - 2
                    return True
                if (self._dn_arrow_r is not None
                        and self._dn_arrow_r.collidepoint(mx, my)):
                    # Cycle down: last extra → primary(-1)
                    if self.hotbar_view_index >= total_bars - 2:
                        self.hotbar_view_index = -1
                    else:
                        self.hotbar_view_index += 1
                    return True

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

            # Page buttons + Sort button
            gl = self._grid_left()
            hotbar_h = self.slot_size + 32
            btn_area_w = self.cols * (self.slot_size + 6) - 6
            nav_y = (self.rect.y + 40 + hotbar_h
                     + self.rows * (self.slot_size + 6) + 4)
            prev_r = pygame.Rect(gl, nav_y, 60, 28)
            next_r = pygame.Rect(gl + btn_area_w - 60, nav_y, 60, 28)
            sort_r = pygame.Rect(gl + 60 + 10, nav_y, 55, 28)
            if prev_r.collidepoint(mx, my):
                self.page = (self.page - 1) % INVENTORY_PAGES
                return True
            if next_r.collidepoint(mx, my):
                self.page = (self.page + 1) % INVENTORY_PAGES
                return True
            if sort_r.collidepoint(mx, my):
                sort_inventory_slots(
                    self.inventory.slots,
                    self.inventory.slot_enchantments,
                    self.inventory.slot_rarities)
                self.page = 0
                return True

            # Click outside panel while holding an item → drop confirm
            if self.inventory.held_item:
                # Include DW title bar area in panel check
                full_panel = self.dw.title_bar_rect.union(self.rect)
                if not full_panel.collidepoint(mx, my):
                    item_id, count = self.inventory.held_item
                    self.drop_confirm.open(
                        item_id, count,
                        self.inventory.held_enchant,
                        self.inventory.held_rarity)
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
            slots_d, enchants_d, rarities_d, is_primary = self._get_viewed_bar()
            src_type = 'hotbar' if is_primary else 'extra_bar'
            for i in range(HOTBAR_CAPACITY):
                sr = self._hotbar_slot_rect(i)
                if sr.collidepoint(mx, my) and i in slots_d:
                    iid, cnt = slots_d[i]
                    if cnt > 1:
                        if is_primary:
                            self.split_dialog.open(
                                src_type, i, iid, cnt, mx, my)
                        else:
                            self.split_dialog.open(
                                src_type, i, iid, cnt, mx, my,
                                ext_slots=slots_d,
                                ext_enchants=enchants_d,
                                ext_rarities=rarities_d)
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
        """Handle click on a hotbar slot — works for both primary and extra bars."""
        inv = self.inventory
        slots_d, enchants_d, rarities_d, is_primary = self._get_viewed_bar()
        has_held = inv.held_item is not None
        has_slot = slot in slots_d
        if not has_held and not has_slot:
            return
        if not has_held and has_slot:
            # Pick up from this bar
            inv.held_item = slots_d.pop(slot)
            inv.held_enchant = enchants_d.pop(slot, None)
            if is_primary:
                pick_up_rarity(inv, 'hotbar', slot)
            else:
                inv.held_rarity = rarities_d.pop(slot, 'common')
        elif has_held and not has_slot:
            # Place into empty slot
            slots_d[slot] = inv.held_item
            inv.held_item = None
            if inv.held_enchant:
                enchants_d[slot] = inv.held_enchant
            inv.held_enchant = None
            if is_primary:
                place_rarity(inv, 'hotbar', slot)
            else:
                rarities_d[slot] = inv.held_rarity or 'common'
                inv.held_rarity = 'common'
        else:
            # Swap held with slot
            old_ench = enchants_d.pop(slot, None)
            if inv.held_enchant:
                enchants_d[slot] = inv.held_enchant
            inv.held_enchant = old_ench
            if is_primary:
                swap_rarity(inv, 'hotbar', slot)
            else:
                old_rar = rarities_d.get(slot, 'common')
                rarities_d[slot] = inv.held_rarity or 'common'
                inv.held_rarity = old_rar
            slots_d[slot], inv.held_item = inv.held_item, slots_d[slot]

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
