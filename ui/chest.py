"""Chest UI — side-by-side chest + player inventory panel for transferring items."""
from __future__ import annotations

from typing import Dict, Any

import pygame

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, CYAN, ORANGE,
    INVENTORY_SLOTS_PER_PAGE, INVENTORY_PAGES,
    UI_CHEST_PANEL_BG, UI_BORDER_PANEL,
    UI_CHEST_SLOT_BG_NORMAL, UI_CHEST_SLOT_BG_HOVER,
    UI_SLOT_BORDER_NORMAL, UI_ENCHANT_FALLBACK,
    UI_CHEST_SORT_HOVER, UI_CHEST_SORT_NORMAL, UI_CHEST_SORT_BORDER,
    UI_CHEST_MOVE_HOVER, UI_CHEST_MOVE_NORMAL, UI_CHEST_MOVE_BORDER,
    UI_NAV_HOVER, UI_NAV_NORMAL, UI_TEXT_MUTED,
)
from core.components import Storage, Inventory
from data import ITEM_DATA, get_item_color, get_stat_description
from ui.rarity_display import (
    draw_rarity_border, insert_rarity_tooltip,
)
from ui.split_dialog import SplitDialog


# ──────────────────────────────────────────────────────────────────────
# CHEST STACKING RULE — DO NOT "FIX" THIS, IT IS INTENTIONAL:
# Items that do NOT stack in the player inventory (books, weapons, etc.)
# DO stack inside chests as long as they are *identical* — same item_id,
# same enchant dict, same enhancement level, and same rarity.  This lets
# the player compact their storage while the inventory keeps items
# separate for quick equip/swap.  The Storage component (core/components.py)
# handles the stacking logic; ChestUI simply delegates to it.
# ──────────────────────────────────────────────────────────────────────
class ChestUI:
    """Side-by-side chest + player inventory panel for transferring items."""

    VISIBLE_ROWS = 4  # rows shown at once on the chest side

    def __init__(self, textures: Any) -> None:
        self.textures = textures
        self.font = pygame.font.SysFont('consolas', 14)
        self.title_font = pygame.font.SysFont('consolas', 18, bold=True)
        self.slot_size = 44
        self.cols = 6
        self.chest_entity: int | None = None
        self.inv_page: int = 0
        self.chest_scroll: int = 0  # top row offset for chest grid
        self.split_dialog = SplitDialog()

    def draw(self, surface: pygame.Surface, storage: Storage,
             inventory: Inventory, tooltip,
             is_cave_chest: bool = False) -> None:
        pw, ph = 620, 320
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill(UI_CHEST_PANEL_BG)
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, UI_BORDER_PANEL,
                         (px, py, pw, ph), 2, border_radius=10)

        mx, my = pygame.mouse.get_pos()
        ss = self.slot_size

        # Left half: Chest
        title_l = self.title_font.render("Chest", True, ORANGE)
        surface.blit(title_l, (px + 20, py + 8))
        total_rows = (storage.capacity + self.cols - 1) // self.cols
        max_scroll = max(0, total_rows - self.VISIBLE_ROWS)
        self.chest_scroll = max(0, min(self.chest_scroll, max_scroll))
        start_slot = self.chest_scroll * self.cols
        vis_count = self.VISIBLE_ROWS * self.cols
        vis_slots: Dict[int, tuple] = {}
        vis_enchants: Dict[int, dict] = {}
        vis_rarities: Dict[int, str] = {}
        for i in range(vis_count):
            real = start_slot + i
            if real < storage.capacity and real in storage.slots:
                vis_slots[i] = storage.slots[real]
                if real in storage.slot_enchantments:
                    vis_enchants[i] = storage.slot_enchantments[real]
                if real in storage.slot_rarities:
                    vis_rarities[i] = storage.slot_rarities[real]
        self._draw_grid(surface, vis_slots, vis_enchants, vis_rarities,
                        min(vis_count, storage.capacity - start_slot),
                        px + 10, py + 34, mx, my, tooltip, 'chest')
        # Scroll indicator for chest
        if max_scroll > 0:
            ind = self.font.render(
                f"\u25B2\u25BC {self.chest_scroll + 1}-"
                f"{min(self.chest_scroll + self.VISIBLE_ROWS, total_rows)}"
                f"/{total_rows}", True, GRAY)
            surface.blit(ind, (px + 10 + self.cols * (ss + 4) - ind.get_width(),
                               py + 8))

        # Buttons below chest grid
        chest_grid_bottom = py + 34 + self.VISIBLE_ROWS * (ss + 4) + 2
        if is_cave_chest:
            # Cave chest: single "Loot All" button
            loot_r = pygame.Rect(px + 10, chest_grid_bottom, 120, 22)
            loot_hov = loot_r.collidepoint(mx, my)
            pygame.draw.rect(surface,
                             UI_CHEST_SORT_HOVER if loot_hov else UI_CHEST_SORT_NORMAL,
                             loot_r, border_radius=4)
            pygame.draw.rect(surface, UI_CHEST_SORT_BORDER, loot_r, 1,
                             border_radius=4)
            lt = self.font.render("Loot All", True, WHITE)
            surface.blit(lt, (loot_r.centerx - lt.get_width() // 2,
                              loot_r.centery - lt.get_height() // 2))
        else:
            # Crafted chest: Sort + All→Inv buttons
            sort_r = pygame.Rect(px + 10, chest_grid_bottom, 55, 22)
            sort_hov = sort_r.collidepoint(mx, my)
            pygame.draw.rect(surface,
                             UI_CHEST_SORT_HOVER if sort_hov else UI_CHEST_SORT_NORMAL,
                             sort_r, border_radius=4)
            pygame.draw.rect(surface, UI_CHEST_SORT_BORDER, sort_r, 1,
                             border_radius=4)
            sort_txt = self.font.render("Sort", True, WHITE)
            surface.blit(sort_txt, (sort_r.centerx - sort_txt.get_width() // 2,
                                    sort_r.centery - sort_txt.get_height() // 2))
            # "All→Inv" button
            ai_r = pygame.Rect(px + 10 + 60, chest_grid_bottom, 70, 22)
            ai_hov = ai_r.collidepoint(mx, my)
            pygame.draw.rect(surface,
                             UI_CHEST_MOVE_HOVER if ai_hov else UI_CHEST_MOVE_NORMAL,
                             ai_r, border_radius=4)
            pygame.draw.rect(surface, UI_CHEST_MOVE_BORDER, ai_r, 1,
                             border_radius=4)
            ai_txt = self.font.render("All\u2192Inv", True, WHITE)
            surface.blit(ai_txt, (ai_r.centerx - ai_txt.get_width() // 2,
                                  ai_r.centery - ai_txt.get_height() // 2))

        # Divider
        pygame.draw.line(surface, GRAY,
                         (px + pw // 2, py + 8),
                         (px + pw // 2, py + ph - 8), 1)

        # Right half: Player inventory (paginated)
        title_r = self.title_font.render("Inventory", True, CYAN)
        surface.blit(title_r, (px + pw // 2 + 20, py + 8))
        page_label = self.font.render(
            f"Page {self.inv_page + 1}/{INVENTORY_PAGES}", True, GRAY)
        surface.blit(page_label,
                     (px + pw - 10 - page_label.get_width(), py + 10))
        inv_ox = px + pw // 2 + 10
        # Build a view of the current page's slots
        page_off = self.inv_page * INVENTORY_SLOTS_PER_PAGE
        page_slots: Dict[int, tuple] = {}
        page_enchants: Dict[int, dict] = {}
        page_rarities: Dict[int, str] = {}
        for i in range(INVENTORY_SLOTS_PER_PAGE):
            real = page_off + i
            if real in inventory.slots:
                page_slots[i] = inventory.slots[real]
                if real in inventory.slot_enchantments:
                    page_enchants[i] = inventory.slot_enchantments[real]
                if real in inventory.slot_rarities:
                    page_rarities[i] = inventory.slot_rarities[real]
        self._draw_grid(surface, page_slots, page_enchants, page_rarities,
                        INVENTORY_SLOTS_PER_PAGE,
                        inv_ox, py + 34, mx, my, tooltip, 'inv')
        # Page nav buttons
        grid_bottom = py + 34 + (INVENTORY_SLOTS_PER_PAGE // self.cols) * (ss + 4) + 2
        prev_r = pygame.Rect(inv_ox, grid_bottom, 55, 22)
        next_r = pygame.Rect(inv_ox + pw // 2 - 10 - 55, grid_bottom, 55, 22)
        for r, label in [(prev_r, "< Prev"), (next_r, "Next >")]:
            hov = r.collidepoint(mx, my)
            pygame.draw.rect(surface, UI_NAV_HOVER if hov else UI_NAV_NORMAL,
                             r, border_radius=4)
            pygame.draw.rect(surface, UI_TEXT_MUTED, r, 1, border_radius=4)
            lt = self.font.render(label, True, WHITE)
            surface.blit(lt, (r.centerx - lt.get_width() // 2,
                              r.centery - lt.get_height() // 2))

        # Split dialog overlay (drawn last so it's on top)
        self.split_dialog.draw(surface)

    def _draw_grid(self, surface: pygame.Surface,
                   slots: Dict[int, tuple],
                   enchants: Dict[int, dict],
                   rarities: Dict[int, str],
                   capacity: int,
                   ox: int, oy: int, mx: int, my: int,
                   tooltip, side: str) -> None:
        from enchantments.effects import (
            get_enchant_display_prefix, ENCHANT_COLORS,
        )
        ss = self.slot_size
        for i in range(capacity):
            col = i % self.cols
            row = i // self.cols
            x = ox + col * (ss + 4)
            y = oy + row * (ss + 4)
            sr = pygame.Rect(x, y, ss, ss)
            bg_c = UI_CHEST_SLOT_BG_NORMAL if not sr.collidepoint(mx, my) else UI_CHEST_SLOT_BG_HOVER
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, UI_SLOT_BORDER_NORMAL, sr, 1, border_radius=4)
            ench = enchants.get(i)
            rar = rarities.get(i, 'common')
            # Rarity border (the ONLY item border)
            if rar != 'common':
                draw_rarity_border(surface, sr, rar)
            if i in slots:
                item_id, count = slots[i]
                icon = self.textures.cache.get(f'item_{item_id}')
                if icon:
                    surface.blit(pygame.transform.scale(icon, (30, 30)),
                                 (x + 7, y + 7))
                if count > 1:
                    ct = self.font.render(str(count), True, WHITE)
                    surface.blit(ct, (x + ss - ct.get_width() - 3,
                                      y + ss - ct.get_height() - 2))
                if sr.collidepoint(mx, my) and item_id in ITEM_DATA:
                    d = ITEM_DATA[item_id]
                    name = d[0]
                    name_color = get_item_color(item_id, rar)
                    action = "Click: Move to " + (
                        "Inventory" if side == 'chest' else "Chest")
                    lines = [name, get_stat_description(item_id, rar), action]
                    colors = [name_color, WHITE, GRAY]
                    if side == 'chest' and count > 1:
                        lines.append("Right-click: Choose amount")
                        colors.append(GRAY)
                    insert_rarity_tooltip(lines, colors, rar)
                    if ench:
                        prefix = get_enchant_display_prefix(ench)
                        if prefix:
                            lines[0] = f"{prefix} {name}"
                            colors[0] = ENCHANT_COLORS.get(
                                ench['type'], name_color)
                        ench_line = (f"Enchant: {ench['type'].title()}"
                                     f" Lv.{ench['level']}")
                        lines.insert(1, ench_line)
                        colors.insert(1, ENCHANT_COLORS.get(
                            ench['type'], CYAN))
                    tooltip.show(lines, (mx, my), colors)

    def handle_event(self, event: pygame.event.Event,
                     storage: Storage, inventory: Inventory,
                     is_cave_chest: bool = False) -> bool:
        pw, ph = 620, 320
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        ss = self.slot_size

        # Split dialog takes priority over all other events
        if self.split_dialog.active:
            return self.split_dialog.handle_event(event, inventory)

        # Scroll wheel — chest side vs inventory page
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            panel_r = pygame.Rect(px, py, pw, ph)
            if not panel_r.collidepoint(mx, my):
                return False
            chest_half = pygame.Rect(px, py, pw // 2, ph)
            if chest_half.collidepoint(mx, my):
                total_rows = (storage.capacity + self.cols - 1) // self.cols
                max_scroll = max(0, total_rows - self.VISIBLE_ROWS)
                self.chest_scroll = max(0, min(max_scroll,
                                               self.chest_scroll - event.y))
                return True
            else:
                # Scroll on inventory side changes page
                if event.y > 0:
                    self.inv_page = (self.inv_page - 1) % INVENTORY_PAGES
                elif event.y < 0:
                    self.inv_page = (self.inv_page + 1) % INVENTORY_PAGES
                return True

        # Right-click on chest slot → open split dialog
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = event.pos
            start_slot = self.chest_scroll * self.cols
            vis_count = self.VISIBLE_ROWS * self.cols
            for i in range(min(vis_count, storage.capacity - start_slot)):
                col = i % self.cols
                row = i // self.cols
                x = px + 10 + col * (ss + 4)
                y = py + 34 + row * (ss + 4)
                if pygame.Rect(x, y, ss, ss).collidepoint(mx, my):
                    real = start_slot + i
                    if real in storage.slots:
                        iid, cnt = storage.slots[real]
                        if cnt > 1:
                            self.split_dialog.open_chest(
                                real, iid, cnt, mx, my,
                                storage, inventory)
                            return True
            return False

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos

        # Click in chest grid → move to inventory
        start_slot = self.chest_scroll * self.cols
        vis_count = self.VISIBLE_ROWS * self.cols
        for i in range(min(vis_count, storage.capacity - start_slot)):
            col = i % self.cols
            row = i // self.cols
            x = px + 10 + col * (ss + 4)
            y = py + 34 + row * (ss + 4)
            if pygame.Rect(x, y, ss, ss).collidepoint(mx, my):
                real = start_slot + i
                if real in storage.slots:
                    item_id, count = storage.slots[real]
                    ench = storage.slot_enchantments.get(real)
                    rar = storage.slot_rarities.get(real, 'common')
                    overflow = inventory.add_item_enchanted(
                        item_id, ench, count, rar)
                    if overflow == 0:
                        del storage.slots[real]
                        storage.slot_enchantments.pop(real, None)
                        storage.slot_rarities.pop(real, 'common')
                    elif overflow < count:
                        storage.slots[real] = (item_id, overflow)
                    return True

        # Click in inventory grid → move to chest (crafted chests only)
        if not is_cave_chest:
            page_off = self.inv_page * INVENTORY_SLOTS_PER_PAGE
            for i in range(INVENTORY_SLOTS_PER_PAGE):
                col = i % self.cols
                row = i // self.cols
                x = px + pw // 2 + 10 + col * (ss + 4)
                y = py + 34 + row * (ss + 4)
                if pygame.Rect(x, y, ss, ss).collidepoint(mx, my):
                    real = page_off + i
                    if real in inventory.slots:
                        from core.item_stack import transfer_slot
                        transfer_slot(
                            inventory.slots, inventory.slot_enchantments,
                            inventory.slot_rarities, real,
                            storage.slots, storage.slot_enchantments,
                            storage.slot_rarities, storage.capacity)
                        return True

        # Page nav buttons
        grid_bottom = py + 34 + (INVENTORY_SLOTS_PER_PAGE // self.cols) * (ss + 4) + 2
        inv_ox = px + pw // 2 + 10
        prev_r = pygame.Rect(inv_ox, grid_bottom, 55, 22)
        next_r = pygame.Rect(inv_ox + pw // 2 - 10 - 55, grid_bottom, 55, 22)
        if prev_r.collidepoint(mx, my):
            self.inv_page = (self.inv_page - 1) % INVENTORY_PAGES
            return True
        if next_r.collidepoint(mx, my):
            self.inv_page = (self.inv_page + 1) % INVENTORY_PAGES
            return True

        # Buttons below chest grid
        chest_grid_bottom = py + 34 + self.VISIBLE_ROWS * (ss + 4) + 2
        if is_cave_chest:
            # "Loot All" — move everything from chest to inventory
            loot_r = pygame.Rect(px + 10, chest_grid_bottom, 120, 22)
            if loot_r.collidepoint(mx, my):
                self._move_all(storage, inventory)
                return True
        else:
            # "Sort" button
            sort_r = pygame.Rect(px + 10, chest_grid_bottom, 55, 22)
            if sort_r.collidepoint(mx, my):
                storage.sort()
                self.chest_scroll = 0
                return True
            # "All→Inv" button
            ai_r = pygame.Rect(px + 10 + 60, chest_grid_bottom, 70, 22)
            if ai_r.collidepoint(mx, my):
                self._move_all(storage, inventory)
                return True

        return False

    @staticmethod
    def _move_all(storage, inventory) -> None:
        """Move all items from storage into inventory, respecting non-stackable."""
        for slot in list(storage.slots.keys()):
            item_id, count = storage.slots[slot]
            ench = storage.slot_enchantments.get(slot)
            rar = storage.slot_rarities.get(slot, 'common')
            overflow = inventory.add_item_enchanted(item_id, ench, count, rar)
            if overflow == 0:
                del storage.slots[slot]
                storage.slot_enchantments.pop(slot, None)
                storage.slot_rarities.pop(slot, 'common')
            elif overflow < count:
                storage.slots[slot] = (item_id, overflow)
