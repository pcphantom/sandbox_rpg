"""GUI elements — HUD, inventory with pages, crafting, pause menu,
character/equipment menu, chest UI, tooltip, progress bars."""
from __future__ import annotations

from typing import List, Tuple, Dict, Optional, Any, Callable

import pygame

from core.constants import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN,
                       CYAN, GRAY, YELLOW, DARK_GRAY, ORANGE, LIGHT_BLUE,
                       PURPLE,
                       INVENTORY_SLOTS_PER_PAGE, HOTBAR_CAPACITY,
                       INVENTORY_PAGES, INVENTORY_COLS, SAVE_SLOTS,
                       QUICK_SAVE_SLOT, CHEST_CAPACITY,
                       AGI_SPEED_BONUS, AGI_SPEED_BONUS_CAP)
from core.components import Inventory, Health, PlayerStats, Equipment, Storage
from data import ITEM_DATA, ITEM_CATEGORIES, RECIPES, ARMOR_VALUES, get_item_color
from core.item_stack import normalize_rarity
from ui.rarity_display import (
    draw_rarity_border, insert_rarity_tooltip,
    pick_up_rarity, place_rarity, swap_rarity,
)


# ======================================================================
# BASE
# ======================================================================
class UIElement:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect; self.visible = True; self.enabled = True
        self.children: List[UIElement] = []

    def add_child(self, child: UIElement) -> None:
        self.children.append(child)

    def update(self, dt: float) -> None:
        if self.visible:
            for c in self.children:
                c.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.visible:
            for c in self.children:
                c.draw(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        for c in reversed(self.children):
            if c.handle_event(event):
                return True
        return False


# ======================================================================
# PROGRESS BAR
# ======================================================================
class ProgressBar(UIElement):
    def __init__(self, rect: pygame.Rect, max_value: float,
                 fg: Tuple[int, int, int] = (200, 60, 60),
                 bg: Tuple[int, int, int] = (40, 20, 20)) -> None:
        super().__init__(rect)
        self.value = max_value; self.max_value = max_value
        self.color_fg = fg; self.color_bg = bg

    def set_value(self, v: float) -> None:
        from core.utils import clamp as _clamp
        self.value = _clamp(v, 0, self.max_value)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        pygame.draw.rect(surface, self.color_bg, self.rect, border_radius=4)
        fw = (int(self.rect.width * (self.value / self.max_value))
              if self.max_value > 0 else 0)
        pygame.draw.rect(
            surface, self.color_fg,
            pygame.Rect(self.rect.x, self.rect.y, fw, self.rect.height),
            border_radius=4)
        pygame.draw.rect(surface, (200, 200, 220), self.rect, 2,
                         border_radius=4)


# ======================================================================
# TOOLTIP
# ======================================================================
class Tooltip:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.colors: List[Tuple[int, int, int]] = []
        self.visible = False
        self.pos = (0, 0)
        self.font = pygame.font.SysFont('consolas', 13)

    def clear(self) -> None:
        self.visible = False

    def show(self, lines: List[str], pos: Tuple[int, int],
             colors: Optional[List[Tuple[int, int, int]]] = None) -> None:
        self.lines = lines; self.visible = True; self.pos = pos
        self.colors = colors or [WHITE] * len(lines)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.lines:
            return
        surfs = [self.font.render(l, True,
                 self.colors[i] if i < len(self.colors) else WHITE)
                 for i, l in enumerate(self.lines)]
        mw = max(s.get_width() for s in surfs)
        th = len(surfs) * 17 + 10
        x = min(self.pos[0] + 14, SCREEN_WIDTH - mw - 20)
        y = min(self.pos[1] + 14, SCREEN_HEIGHT - th - 10)
        bg = pygame.Surface((mw + 16, th), pygame.SRCALPHA)
        bg.fill((12, 12, 22, 230))
        surface.blit(bg, (x, y))
        pygame.draw.rect(surface, (130, 130, 160),
                         (x, y, mw + 16, th), 1, border_radius=3)
        for i, s in enumerate(surfs):
            surface.blit(s, (x + 8, y + 5 + i * 17))


# ======================================================================
# STACK SPLIT DIALOG
# ======================================================================
class SplitDialog:
    """Small popup for splitting a stack.  Scroll wheel / +/- / type amount."""

    WIDTH  = 180
    HEIGHT = 120

    def __init__(self) -> None:
        self.active = False
        self.source: str = ''         # 'hotbar' or 'slots'
        self.slot: int = 0
        self.item_id: str = ''
        self.total: int = 0
        self.amount: int = 0          # amount to split off
        self.typing: str = ''         # keyboard buffer
        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)

    def open(self, source: str, slot: int, item_id: str, total: int,
             mx: int, my: int) -> None:
        self.active = True
        self.source = source
        self.slot = slot
        self.item_id = item_id
        self.total = total
        self.amount = max(1, total // 2)
        self.typing = ''
        # Position near the mouse, clamped to screen
        self.x = min(mx, SCREEN_WIDTH - self.WIDTH - 4)
        self.y = min(my, SCREEN_HEIGHT - self.HEIGHT - 4)

    def close(self) -> None:
        self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return
        r = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        bg.fill((25, 25, 40, 240))
        surface.blit(bg, r.topleft)
        pygame.draw.rect(surface, (160, 160, 200), r, 2, border_radius=6)

        mx, my = pygame.mouse.get_pos()

        # Title
        title = self.font.render("Split Stack", True, WHITE)
        surface.blit(title, (r.centerx - title.get_width() // 2, r.y + 6))

        # Amount display
        amt_text = self.font.render(
            f"{self.amount} / {self.total}", True, YELLOW)
        surface.blit(amt_text,
                     (r.centerx - amt_text.get_width() // 2, r.y + 30))

        # Minus / Plus buttons
        btn_w, btn_h = 36, 24
        minus_r = pygame.Rect(r.x + 14, r.y + 56, btn_w, btn_h)
        plus_r  = pygame.Rect(r.right - 14 - btn_w, r.y + 56, btn_w, btn_h)
        for br, label in [(minus_r, "-"), (plus_r, "+")]:
            hov = br.collidepoint(mx, my)
            pygame.draw.rect(surface,
                             (80, 80, 110) if hov else (55, 55, 75),
                             br, border_radius=4)
            pygame.draw.rect(surface, (130, 130, 160), br, 1, border_radius=4)
            lt = self.font.render(label, True, WHITE)
            surface.blit(lt, (br.centerx - lt.get_width() // 2,
                              br.centery - lt.get_height() // 2))

        # Typing hint
        hint = self.font_sm.render("Scroll / type / +/-", True, GRAY)
        surface.blit(hint,
                     (r.centerx - hint.get_width() // 2, r.y + 56 + 4))

        # Confirm / Cancel
        conf_r = pygame.Rect(r.x + 10, r.bottom - 28, 75, 22)
        canc_r = pygame.Rect(r.right - 85, r.bottom - 28, 75, 22)
        for br, label, color in [
            (conf_r, "Confirm", (60, 120, 60)),
            (canc_r, "Cancel",  (120, 60, 60)),
        ]:
            hov = br.collidepoint(mx, my)
            c = tuple(min(255, ch + 30) for ch in color) if hov else color
            pygame.draw.rect(surface, c, br, border_radius=4)
            pygame.draw.rect(surface, (160, 160, 180), br, 1, border_radius=4)
            lt = self.font_sm.render(label, True, WHITE)
            surface.blit(lt, (br.centerx - lt.get_width() // 2,
                              br.centery - lt.get_height() // 2))

    def handle_event(self, event: pygame.event.Event,
                     inventory: 'Inventory') -> bool:
        """Returns True if the event was consumed."""
        if not self.active:
            return False

        if event.type == pygame.MOUSEWHEEL:
            self.amount = max(1, min(self.total - 1,
                                     self.amount + event.y))
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
            plus_r  = pygame.Rect(r.right - 14 - btn_w, r.y + 56, btn_w, btn_h)
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
            return True  # click inside dialog is consumed

        return False

    def _confirm(self, inventory: 'Inventory') -> None:
        """Split: reduce source slot, put split amount into held_item."""
        if self.amount < 1 or self.amount >= self.total:
            self.close()
            return
        remain = self.total - self.amount
        storage = inventory.hotbar if self.source == 'hotbar' else inventory.slots
        if self.slot in storage:
            storage[self.slot] = (self.item_id, remain)
            inventory.held_item = (self.item_id, self.amount)
            # Transfer enchant + rarity to held portion (source slot keeps its copy)
            ench_dict = (inventory.hotbar_enchantments
                         if self.source == 'hotbar'
                         else inventory.slot_enchantments)
            rar_dict = (inventory.hotbar_rarities
                        if self.source == 'hotbar'
                        else inventory.slot_rarities)
            ench = ench_dict.get(self.slot)
            if ench:
                inventory.held_enchant = dict(ench)
            inventory.held_rarity = normalize_rarity(rar_dict.get(self.slot, 'common'))
        self.close()


# ======================================================================
# DROP CONFIRM DIALOG
# ======================================================================
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

    # -- rect helper (centered on screen) --
    def _rect(self) -> pygame.Rect:
        return pygame.Rect(SCREEN_WIDTH // 2 - self.WIDTH // 2,
                           SCREEN_HEIGHT // 2 - self.HEIGHT // 2,
                           self.WIDTH, self.HEIGHT)

    def _build_label(self) -> str:
        """Build a display name including enchant prefix, rarity, and count."""
        name = ITEM_DATA[self.item_id][0] if self.item_id in ITEM_DATA else self.item_id
        if self.enchant:
            from enchantments.effects import get_enchant_display_prefix
            prefix = get_enchant_display_prefix(self.enchant)
            if prefix:
                name = f"{prefix} {name}"
        if self.rarity != 'common':
            name = f"{self.rarity.title()} {name}"
        if self.count > 1:
            name = f"{name} x{self.count}"
        return name

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return
        r = self._rect()
        bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
        bg.fill((30, 10, 10, 240))
        surface.blit(bg, r.topleft)
        pygame.draw.rect(surface, (200, 60, 60), r, 2, border_radius=6)

        mx, my = pygame.mouse.get_pos()

        # Title
        title = self.font.render("Drop Item?", True, RED)
        surface.blit(title, (r.centerx - title.get_width() // 2, r.y + 8))

        # Item name
        label = self._build_label()
        name_color = get_item_color(self.item_id, self.rarity)
        name_surf = self.font.render(label, True, name_color)
        surface.blit(name_surf,
                     (r.centerx - name_surf.get_width() // 2, r.y + 32))

        # Warning
        warn = self.font_sm.render("This item will be lost forever!", True,
                                   YELLOW)
        surface.blit(warn,
                     (r.centerx - warn.get_width() // 2, r.y + 56))

        # Yes / No buttons
        yes_r = pygame.Rect(r.x + 20, r.bottom - 34, 90, 24)
        no_r = pygame.Rect(r.right - 110, r.bottom - 34, 90, 24)
        for br, lbl, color in [
            (yes_r, "Yes, Drop", (140, 40, 40)),
            (no_r, "Cancel", (50, 80, 50)),
        ]:
            hov = br.collidepoint(mx, my)
            c = tuple(min(255, ch + 30) for ch in color) if hov else color
            pygame.draw.rect(surface, c, br, border_radius=4)
            pygame.draw.rect(surface, (160, 160, 180), br, 1, border_radius=4)
            lt = self.font_sm.render(lbl, True, WHITE)
            surface.blit(lt, (br.centerx - lt.get_width() // 2,
                              br.centery - lt.get_height() // 2))

    def handle_event(self, event: pygame.event.Event,
                     inventory: Inventory) -> bool:
        """Returns True if the event was consumed."""
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
            # Click anywhere inside the dialog is consumed
            if r.collidepoint(mx, my):
                return True
            # Click outside dialog cancels it
            self.close()
            return True

        return True  # consume all events while dialog is active

    def _confirm_drop(self, inventory: Inventory) -> None:
        """Destroy the held item permanently."""
        inventory.held_item = None
        inventory.held_enchant = None
        inventory.held_rarity = 'common'
        self.close()


# ======================================================================
# INVENTORY GRID (with hotbar row + pages + drag-drop)
# ======================================================================
class InventoryGrid(UIElement):
    """Hotbar row on top, paginated 4×6 inventory below. Click to pick/swap."""

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
        self.drop_dialog = DropConfirmDialog()

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

        # -- Drop confirm dialog overlay --
        self.drop_dialog.draw(surface)

    def _draw_item(self, surface: pygame.Surface, sr: pygame.Rect,
                   item_id: str, count: int,
                   mx: int, my: int, tooltip: Tooltip,
                   enchant: dict | None = None,
                   rarity: str = 'common') -> None:
        # Border: rarity takes priority over enchant glow
        if rarity != 'common':
            draw_rarity_border(surface, sr, rarity)
        elif enchant:
            from enchantments.effects import ENCHANT_COLORS
            ec = ENCHANT_COLORS.get(enchant['type'], (200, 200, 200))
            pygame.draw.rect(surface, ec, sr, 2, border_radius=4)
        else:
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
            d = ITEM_DATA[item_id]
            name = d[0]
            name_color = get_item_color(item_id, rarity)
            lines = [name, d[1]]
            colors = [name_color, WHITE]
            insert_rarity_tooltip(lines, colors, rarity)
            if enchant:
                from enchantments.effects import (
                    get_enchant_display_prefix, ENCHANT_COLORS as EC2,
                )
                prefix = get_enchant_display_prefix(enchant)
                if prefix:
                    lines[0] = f"{prefix} {name}"
                    # Only use enchant color when there's no rarity color
                    if normalize_rarity(rarity) == 'common':
                        colors[0] = EC2.get(enchant['type'], name_color)
                ench_line = (f"Enchant: {enchant['type'].title()}"
                             f" Lv.{enchant['level']}")
                lines.insert(1, ench_line)
                colors.insert(1, EC2.get(enchant['type'], CYAN))
            tooltip.show(lines, (mx, my), colors)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        # Drop confirm dialog takes priority
        if self.drop_dialog.active:
            return self.drop_dialog.handle_event(event, self.inventory)
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

            # Click outside inventory panel while holding an item → drop prompt
            if self.inventory.held_item and not self.rect.collidepoint(mx, my):
                item_id, count = self.inventory.held_item
                self.drop_dialog.open(item_id, count,
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


# ======================================================================
# CRAFTING PANEL
# ======================================================================
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


# ======================================================================
# PAUSE MENU
# ======================================================================
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
        pygame.draw.rect(surface, (140, 140, 170),
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
            bc = (70, 70, 110) if sel else (45, 45, 60)
            pygame.draw.rect(surface, bc, r, border_radius=4)
            bd = (200, 200, 240) if sel else (100, 100, 120)
            pygame.draw.rect(surface, bd, r, 1, border_radius=4)
            surface.blit(self.font.render(label, True, WHITE),
                         (r.x + 8, r.y + 7))
            sy += 38

        # Save / Load / Delete buttons
        btn_y = sy + 8
        btn_w = (pw - 80 - 20) // 3  # evenly spaced across panel
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
        bc = (60, 70, 100) if hov else (40, 45, 65)
        pygame.draw.rect(surface, bc, r, border_radius=5)
        pygame.draw.rect(surface, (130, 130, 160), r, 1, border_radius=5)
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


# ======================================================================
# CHARACTER / EQUIPMENT MENU  (P key)
# ======================================================================
_EQUIP_SLOTS = [
    ('weapon',  'Weapon'),
    ('armor',   'Armor'),
    ('shield',  'Shield'),
    ('ranged',  'Ranged'),
    ('ammo',    'Ammo'),
]

_SLOT_CATEGORIES: Dict[str, list[str]] = {
    'weapon': ['weapon'],
    'armor':  ['armor'],
    'shield': ['shield'],
    'ranged': ['ranged'],
    'ammo':   ['ammo'],
}

_STAT_NAMES = ['strength', 'agility', 'vitality', 'luck']


class CharacterMenu:
    """Full-screen character panel: stats + equipment."""

    def __init__(self, textures: Any) -> None:
        self.textures = textures
        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.title_font = pygame.font.SysFont('consolas', 24, bold=True)
        # Dropdown state for equip selection
        self._dropdown_open: bool = False
        self._dropdown_attr: str = ''        # equipment slot attribute name
        self._dropdown_items: List[Tuple[int, str, Optional[Dict]]] = []  # (inv_slot, item_id, enchant)
        self._dropdown_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._dropdown_scroll: int = 0
        self._dropdown_max_visible: int = 6
        self._dropdown_row_h: int = 24

    def draw(self, surface: pygame.Surface,
             stats: PlayerStats, equipment: Equipment,
             health: Health, inventory: Inventory,
             tooltip: Tooltip) -> None:
        pw, ph = 540, 460
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((20, 20, 35, 240))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, (140, 140, 170),
                         (px, py, pw, ph), 2, border_radius=10)

        title = self.title_font.render("Character  [P]", True, WHITE)
        surface.blit(title,
                     (px + pw // 2 - title.get_width() // 2, py + 10))

        # ---- Left column: Stats ----
        sx = px + 20
        sy = py + 50
        surface.blit(self.font.render(
            f"Level {stats.level}   XP {stats.xp}/{stats.xp_to_next}",
            True, CYAN), (sx, sy))
        sy += 24
        surface.blit(self.font.render(
            f"HP {health.current}/{health.maximum}   Kills {stats.kills}",
            True, WHITE), (sx, sy))
        sy += 30

        surface.blit(self.font.render("Stats", True, YELLOW), (sx, sy))
        sy += 22
        mx, my = pygame.mouse.get_pos()
        for sname in _STAT_NAMES:
            val = getattr(stats, sname)
            label = f"{sname.capitalize():>10}: {val}"
            surface.blit(self.font.render(label, True, WHITE), (sx, sy))
            # + button
            if stats.stat_points > 0:
                btn = pygame.Rect(sx + 180, sy, 24, 20)
                hov = btn.collidepoint(mx, my)
                bc = (70, 110, 70) if hov else (50, 80, 50)
                pygame.draw.rect(surface, bc, btn, border_radius=3)
                pygame.draw.rect(surface, GREEN, btn, 1, border_radius=3)
                t = self.font_sm.render("+", True, WHITE)
                surface.blit(t, (btn.centerx - t.get_width() // 2,
                                 btn.centery - t.get_height() // 2))
            sy += 24
        surface.blit(self.font_sm.render(
            f"Stat points: {stats.stat_points}", True, GRAY), (sx, sy))

        # ---- Right column: Bonuses ----
        bx = px + 270
        by = py + 50
        surface.blit(self.font.render("Bonuses", True, YELLOW), (bx, by))
        by += 26

        from systems import calc_damage_reduction, calc_melee_damage
        from data import ITEM_DATA as _ID, RANGED_DATA as _RD

        weapon = equipment.weapon if equipment and equipment.weapon else inventory.get_equipped()
        base_dmg = 5
        if weapon and weapon in _ID and _ID[weapon][2] > 0:
            base_dmg = _ID[weapon][2]
        atk = calc_melee_damage(base_dmg, stats, equipment)
        crit_pct = stats.luck * 2
        surface.blit(self.font_sm.render(
            f"Attack damage: {atk}", True, ORANGE), (bx, by))
        by += 18
        surface.blit(self.font_sm.render(
            f"Crit: {crit_pct}%", True, ORANGE), (bx, by))
        by += 18

        if equipment and equipment.ranged and equipment.ranged in _RD:
            rd = _RD[equipment.ranged]
            r_dmg = rd['damage'] + stats.agility * 2
            surface.blit(self.font_sm.render(
                f"Ranged damage: {r_dmg}", True, ORANGE), (bx, by))
            by += 18

        dr = calc_damage_reduction(equipment)
        surface.blit(self.font_sm.render(
            f"Defense: {dr}", True, LIGHT_BLUE), (bx, by))
        by += 18
        speed_bonus = int(min(AGI_SPEED_BONUS_CAP, stats.agility * AGI_SPEED_BONUS) * 100)
        surface.blit(self.font_sm.render(
            f"Speed bonus: +{speed_bonus}%", True, GRAY), (bx, by))
        by += 18
        luck_bonus = stats.luck * 10
        surface.blit(self.font_sm.render(
            f"Harvest luck: +{luck_bonus}%", True, GRAY), (bx, by))

        # ---- Bottom: Equipment (full width) ----
        ex = px + 20
        ey = py + 260
        surface.blit(self.font.render("Equipment", True, YELLOW), (ex, ey))
        ey += 26
        for attr, label in _EQUIP_SLOTS:
            item_id = getattr(equipment, attr)
            name = ITEM_DATA[item_id][0] if item_id and item_id in ITEM_DATA else "—"
            name_color = WHITE
            eq_rar = equipment.rarities.get(attr, 'common')
            if item_id:
                name_color = get_item_color(item_id, eq_rar)
            if eq_rar != 'common' and item_id:
                name = f"{eq_rar.title()} {name}"
            eq_ench = equipment.enchantments.get(attr)
            if eq_ench and item_id:
                from enchantments.effects import (
                    get_enchant_display_prefix, ENCHANT_COLORS,
                )
                prefix = get_enchant_display_prefix(eq_ench)
                if prefix:
                    name = f"{prefix} {name}"
                    # Only use enchant color when there's no rarity color
                    if not eq_rar or eq_rar == 'common':
                        name_color = ENCHANT_COLORS.get(eq_ench['type'], name_color)
            surface.blit(self.font.render(f"{label}: ", True, GRAY), (ex, ey))
            # Append ammo count to name
            if attr == 'ammo' and item_id and equipment.ammo_count > 0:
                name = f"{name} x{equipment.ammo_count}"
            surface.blit(self.font.render(name, True, name_color), (ex + 80, ey))
            # Icon
            if item_id:
                icon = self.textures.cache.get(f'item_{item_id}')
                if icon:
                    surface.blit(pygame.transform.scale(icon, (20, 20)),
                                 (ex + 440, ey))
            # Equip / Unequip button
            btn = pygame.Rect(ex + 465, ey, 20, 20)
            hov = btn.collidepoint(mx, my)
            if item_id:
                # Unequip
                pygame.draw.rect(surface,
                                 (110, 50, 50) if hov else (80, 40, 40),
                                 btn, border_radius=3)
                t = self.font_sm.render("x", True, WHITE)
            else:
                # Equip
                pygame.draw.rect(surface,
                                 (50, 80, 50) if hov else (40, 60, 40),
                                 btn, border_radius=3)
                t = self.font_sm.render("E", True, WHITE)
            surface.blit(t, (btn.centerx - t.get_width() // 2,
                             btn.centery - t.get_height() // 2))
            ey += 28

        # Help text
        ey += 6
        surface.blit(self.font_sm.render(
            "Click E to equip, x to unequip", True, GRAY), (ex, ey))

        # --- Equip dropdown overlay ---
        if self._dropdown_open and self._dropdown_items:
            self._draw_dropdown(surface, mx, my)

    def _draw_dropdown(self, surface: pygame.Surface,
                       mx: int, my: int) -> None:
        """Draw the equip-selection dropdown list."""
        rh = self._dropdown_row_h
        vis = min(len(self._dropdown_items), self._dropdown_max_visible)
        dr = self._dropdown_rect
        # Background
        bg = pygame.Surface((dr.width, dr.height), pygame.SRCALPHA)
        bg.fill((25, 25, 45, 245))
        surface.blit(bg, (dr.x, dr.y))
        pygame.draw.rect(surface, (160, 160, 200), dr, 1, border_radius=3)
        # Title
        title_t = self.font_sm.render(
            f"Select {self._dropdown_attr.capitalize()}:", True, YELLOW)
        surface.blit(title_t, (dr.x + 6, dr.y + 3))
        # Items
        iy = dr.y + rh  # first row after title
        start = self._dropdown_scroll
        end = min(start + self._dropdown_max_visible,
                  len(self._dropdown_items))
        for idx in range(start, end):
            _inv_slot, iid, ench, rar, slot_cnt = self._dropdown_items[idx]
            row_r = pygame.Rect(dr.x + 2, iy, dr.width - 4, rh)
            hov = row_r.collidepoint(mx, my)
            rc = (55, 65, 95) if hov else (35, 35, 55)
            pygame.draw.rect(surface, rc, row_r, border_radius=2)
            # Icon
            icon = self.textures.cache.get(f'item_{iid}')
            if icon:
                surface.blit(
                    pygame.transform.scale(icon, (18, 18)),
                    (row_r.x + 4, row_r.y + 3))
            # Name (with rarity + enchant prefix)
            name = ITEM_DATA[iid][0] if iid in ITEM_DATA else iid
            name_color = get_item_color(iid, rar)
            if rar and rar != 'common':
                name = f"{rar.title()} {name}"
            if ench:
                from enchantments.effects import (
                    get_enchant_display_prefix, ENCHANT_COLORS,
                )
                prefix = get_enchant_display_prefix(ench)
                if prefix:
                    name = f"{prefix} {name}"
                    # Only use enchant color when there's no rarity color
                    if not rar or rar == 'common':
                        name_color = ENCHANT_COLORS.get(ench['type'], name_color)
            if slot_cnt > 1:
                name = f"{name} x{slot_cnt}"
            surface.blit(self.font_sm.render(name, True, name_color),
                         (row_r.x + 26, row_r.y + 5))
            iy += rh
        # Scroll indicators
        if self._dropdown_scroll > 0:
            surface.blit(self.font_sm.render("▲", True, GRAY),
                         (dr.right - 16, dr.y + rh - 2))
        if end < len(self._dropdown_items):
            surface.blit(self.font_sm.render("▼", True, GRAY),
                         (dr.right - 16, dr.bottom - rh + 4))

    def _open_dropdown(self, attr: str, inventory: Inventory,
                       btn_x: int, btn_y: int) -> None:
        """Populate and open the equip dropdown for a given slot."""
        cats = _SLOT_CATEGORIES.get(attr, [])
        items: List[Tuple[int, str, Optional[Dict], str]] = []
        for slot_idx, (iid, cnt) in sorted(inventory.slots.items()):
            cat = ITEM_CATEGORIES.get(iid, '')
            if cat in cats:
                ench = inventory.slot_enchantments.get(slot_idx)
                rar = inventory.slot_rarities.get(slot_idx, 'common')
                items.append((slot_idx, iid, ench, rar, cnt))
        for slot_idx, (iid, cnt) in sorted(inventory.hotbar.items()):
            cat = ITEM_CATEGORIES.get(iid, '')
            if cat in cats:
                ench = inventory.hotbar_enchantments.get(slot_idx)
                rar = inventory.hotbar_rarities.get(slot_idx, 'common')
                # Use negative index to distinguish hotbar slots
                items.append((-(slot_idx + 1), iid, ench, rar, cnt))
        if not items:
            self._dropdown_open = False
            self._dropdown_items = []
            return
        self._dropdown_attr = attr
        self._dropdown_items = items
        self._dropdown_scroll = 0
        rh = self._dropdown_row_h
        vis = min(len(items), self._dropdown_max_visible)
        dw = 200
        dh = rh * (vis + 1)  # +1 for title row
        # Position below the button, clamp to screen
        dx = btn_x - dw + 20
        dy = btn_y + 22
        if dy + dh > SCREEN_HEIGHT:
            dy = btn_y - dh
        if dx < 0:
            dx = 4
        self._dropdown_rect = pygame.Rect(dx, dy, dw, dh)
        self._dropdown_open = True

    def _equip_from_dropdown(self, idx: int, equipment: Equipment,
                             inventory: Inventory) -> None:
        """Equip the item at dropdown index idx."""
        inv_slot, iid, ench, rar, _cnt = self._dropdown_items[idx]
        attr = self._dropdown_attr
        if attr == 'ammo':
            # Move full arrow stack from inventory into equipment slot
            if inv_slot < 0:
                hb_slot = -(inv_slot + 1)
                item_tuple = inventory.hotbar.pop(hb_slot, None)
                inventory.hotbar_enchantments.pop(hb_slot, None)
                inventory.hotbar_rarities.pop(hb_slot, 'common')
            else:
                item_tuple = inventory.slots.pop(inv_slot, None)
                inventory.slot_enchantments.pop(inv_slot, None)
                inventory.slot_rarities.pop(inv_slot, 'common')
            ammo_cnt = item_tuple[1] if item_tuple else 1
            # If same ammo type already equipped, stack the counts
            if equipment.ammo == iid:
                equipment.ammo_count += ammo_cnt
            else:
                equipment.ammo = iid
                equipment.ammo_count = ammo_cnt
            if ench:
                equipment.enchantments[attr] = ench
            else:
                equipment.enchantments.pop(attr, None)
            equipment.rarities[attr] = normalize_rarity(rar)
            self._dropdown_open = False
            return
        if inv_slot < 0:
            hb_slot = -(inv_slot + 1)
            inventory.hotbar.pop(hb_slot, None)
            inventory.hotbar_enchantments.pop(hb_slot, None)
            inventory.hotbar_rarities.pop(hb_slot, 'common')
        else:
            # Remove from exact slot to avoid mismatched enchant transfer
            inventory.slots.pop(inv_slot, None)
            inventory.slot_enchantments.pop(inv_slot, None)
            inventory.slot_rarities.pop(inv_slot, 'common')
        setattr(equipment, attr, iid)
        if ench:
            equipment.enchantments[attr] = ench
        else:
            equipment.enchantments.pop(attr, None)
        equipment.rarities[attr] = normalize_rarity(rar)
        self._dropdown_open = False

    def handle_event(self, event: pygame.event.Event,
                     stats: PlayerStats, equipment: Equipment,
                     inventory: Inventory) -> bool:
        # Handle dropdown scroll
        if self._dropdown_open and event.type == pygame.MOUSEWHEEL:
            max_scroll = max(0, len(self._dropdown_items)
                             - self._dropdown_max_visible)
            self._dropdown_scroll = max(
                0, min(max_scroll, self._dropdown_scroll - event.y))
            return True

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos

        # If dropdown is open, handle clicks on it first
        if self._dropdown_open:
            dr = self._dropdown_rect
            if dr.collidepoint(mx, my):
                rh = self._dropdown_row_h
                row_y = my - (dr.y + rh)  # offset past title row
                if row_y >= 0:
                    row_idx = self._dropdown_scroll + row_y // rh
                    if 0 <= row_idx < len(self._dropdown_items):
                        self._equip_from_dropdown(
                            row_idx, equipment, inventory)
                        return True
                return True  # click inside dropdown but on title — consume
            else:
                # Click outside dropdown — close it
                self._dropdown_open = False
                return True

        pw, ph = 540, 460
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2

        # Stat + buttons
        sx = px + 20
        sy = py + 50 + 24 + 30 + 22  # after header lines
        for sname in _STAT_NAMES:
            btn = pygame.Rect(sx + 180, sy, 24, 20)
            if btn.collidepoint(mx, my) and stats.stat_points > 0:
                setattr(stats, sname, getattr(stats, sname) + 1)
                stats.stat_points -= 1
                return True
            sy += 24

        # Equipment buttons (bottom section, full width)
        ex = px + 20
        ey = py + 260 + 26
        for attr, _label in _EQUIP_SLOTS:
            btn = pygame.Rect(ex + 465, ey, 20, 20)
            if btn.collidepoint(mx, my):
                item_id = getattr(equipment, attr)
                if item_id:
                    # Unequip → return to inventory (transfer enchant + rarity back)
                    ench = equipment.enchantments.pop(attr, None)
                    rar = equipment.rarities.pop(attr, 'common')
                    if attr == 'ammo':
                        # Return all arrows from equipment back to inventory
                        inventory.add_item_enchanted(
                            item_id, ench, equipment.ammo_count, rar)
                        equipment.ammo_count = 0
                    else:
                        inventory.add_item_enchanted(item_id, ench, 1, rar)
                    setattr(equipment, attr, None)
                else:
                    # Equip → open dropdown to let player choose
                    self._open_dropdown(attr, inventory,
                                        btn.x, btn.y)
                return True
            ey += 28
        return False


# ======================================================================
# CHEST UI
# ======================================================================
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

    def draw(self, surface: pygame.Surface, storage: Storage,
             inventory: Inventory, tooltip: Tooltip,
             is_cave_chest: bool = False) -> None:
        pw, ph = 620, 320
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((20, 20, 35, 240))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, (140, 140, 170),
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
                             (70, 100, 70) if loot_hov else (50, 70, 50),
                             loot_r, border_radius=4)
            pygame.draw.rect(surface, (100, 160, 100), loot_r, 1,
                             border_radius=4)
            lt = self.font.render("Loot All", True, WHITE)
            surface.blit(lt, (loot_r.centerx - lt.get_width() // 2,
                              loot_r.centery - lt.get_height() // 2))
        else:
            # Crafted chest: Sort + All→Inv buttons
            sort_r = pygame.Rect(px + 10, chest_grid_bottom, 55, 22)
            sort_hov = sort_r.collidepoint(mx, my)
            pygame.draw.rect(surface,
                             (70, 100, 70) if sort_hov else (50, 70, 50),
                             sort_r, border_radius=4)
            pygame.draw.rect(surface, (100, 160, 100), sort_r, 1,
                             border_radius=4)
            sort_txt = self.font.render("Sort", True, WHITE)
            surface.blit(sort_txt, (sort_r.centerx - sort_txt.get_width() // 2,
                                    sort_r.centery - sort_txt.get_height() // 2))
            # "All→Inv" button
            ai_r = pygame.Rect(px + 10 + 60, chest_grid_bottom, 70, 22)
            ai_hov = ai_r.collidepoint(mx, my)
            pygame.draw.rect(surface,
                             (100, 70, 70) if ai_hov else (70, 50, 50),
                             ai_r, border_radius=4)
            pygame.draw.rect(surface, (160, 100, 100), ai_r, 1,
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
            pygame.draw.rect(surface, (70, 70, 100) if hov else (50, 50, 70),
                             r, border_radius=4)
            pygame.draw.rect(surface, (130, 130, 160), r, 1, border_radius=4)
            lt = self.font.render(label, True, WHITE)
            surface.blit(lt, (r.centerx - lt.get_width() // 2,
                              r.centery - lt.get_height() // 2))

    def _draw_grid(self, surface: pygame.Surface,
                   slots: Dict[int, tuple],
                   enchants: Dict[int, dict],
                   rarities: Dict[int, str],
                   capacity: int,
                   ox: int, oy: int, mx: int, my: int,
                   tooltip: Tooltip, side: str) -> None:
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
            bg_c = (50, 50, 65) if not sr.collidepoint(mx, my) else (70, 70, 95)
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, (100, 100, 120), sr, 1, border_radius=4)
            ench = enchants.get(i)
            rar = rarities.get(i, 'common')
            if rar != 'common':
                draw_rarity_border(surface, sr, rar)
            elif ench:
                ec = ENCHANT_COLORS.get(ench['type'], (200, 200, 200))
                pygame.draw.rect(surface, ec, sr, 2, border_radius=4)
            else:
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
                    lines = [name, d[1], action]
                    colors = [name_color, WHITE, GRAY]
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
                    from core.item_stack import transfer_slot
                    transfer_slot(
                        storage.slots, storage.slot_enchantments,
                        storage.slot_rarities, real,
                        inventory.slots, inventory.slot_enchantments,
                        inventory.slot_rarities, inventory.capacity)
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
    def _move_all(src, dst) -> None:
        """Move all items from *src* container to *dst*, preserving metadata."""
        from core.item_stack import transfer_all
        transfer_all(src.slots, src.slot_enchantments, src.slot_rarities,
                     dst.slots, dst.slot_enchantments, dst.slot_rarities,
                     dst.capacity)


# ======================================================================
# ENCHANTMENT TABLE UI
# ======================================================================
class EnchantmentTableUI:
    """Enchantment table — 3×3 input grid, combine button, + inventory."""

    CAPACITY = 9
    PW, PH = 520, 260

    def __init__(self, textures: Any) -> None:
        self.textures = textures
        self.font = pygame.font.SysFont('consolas', 14)
        self.title_font = pygame.font.SysFont('consolas', 18, bold=True)
        self.slot_size = 44
        self.table_cols = 3
        self.inv_cols = 6
        self.inv_page: int = 0

    # -- layout helpers --
    def _panel_rect(self) -> Tuple[int, int]:
        return (SCREEN_WIDTH // 2 - self.PW // 2,
                SCREEN_HEIGHT // 2 - self.PH // 2)

    def _grid_origin(self, px: int, py: int) -> Tuple[int, int]:
        return px + 14, py + 30

    def _inv_origin(self, px: int, py: int) -> Tuple[int, int]:
        gx, _ = self._grid_origin(px, py)
        div_x = gx + self.table_cols * (self.slot_size + 4) + 10
        return div_x + 10, py + 30

    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, storage: Storage,
             inventory: Inventory, tooltip: 'Tooltip') -> None:
        px, py = self._panel_rect()
        pw, ph = self.PW, self.PH
        ss = self.slot_size
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((20, 15, 30, 240))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, (140, 100, 170),
                         (px, py, pw, ph), 2, border_radius=10)
        mx, my = pygame.mouse.get_pos()

        # ---- Left: Enchantment Table ----
        title_l = self.title_font.render("Enchantment Table", True, PURPLE)
        surface.blit(title_l, (px + 14, py + 6))
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
            bc = (55, 95, 55) if not hov else (75, 130, 75)
            bd = (100, 200, 100)
        else:
            bc = (40, 40, 50)
            bd = (75, 75, 90)
        pygame.draw.rect(surface, bc, btn_r, border_radius=5)
        pygame.draw.rect(surface, bd, btn_r, 1, border_radius=5)
        ct = self.font.render("Combine", True, WHITE if result else GRAY)
        surface.blit(ct, (btn_r.centerx - ct.get_width() // 2,
                          btn_r.centery - ct.get_height() // 2))

        # Result preview
        if result:
            pvy = btn_y + 32
            rid = result['result_item']
            if rid in ITEM_DATA:
                d = ITEM_DATA[rid]
                name = d[0]
                ench = result.get('result_enchant')
                rr = result.get('result_rarity', 'common')
                color = get_item_color(rid, rr)
                if ench:
                    from enchantments.effects import (
                        get_enchant_display_prefix, ENCHANT_COLORS,
                    )
                    prefix = get_enchant_display_prefix(ench)
                    if prefix:
                        name = f"{prefix} {name}"
                    # Only use enchant color when there's no rarity color
                    if not rr or rr == 'common':
                        color = ENCHANT_COLORS.get(ench['type'], WHITE)
                if rr and rr != 'common':
                    name = f"{rr.title()} {name}"
                icon = self.textures.cache.get(f'item_{rid}')
                if icon:
                    surface.blit(pygame.transform.scale(icon, (20, 20)),
                                 (grid_ox, pvy))
                nt = self.font.render(name, True, color)
                surface.blit(nt, (grid_ox + 24, pvy + 2))

        # ---- Divider ----
        div_x = grid_ox + 3 * (ss + 4) + 10
        pygame.draw.line(surface, GRAY,
                         (div_x, py + 6), (div_x, py + ph - 6), 1)

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
            bg_c = (50, 50, 65) if not sr.collidepoint(mx, my) else (70, 70, 95)
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, (100, 100, 120), sr, 1, border_radius=4)
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
            pygame.draw.rect(surface, (70, 70, 100) if hov2 else (50, 50, 70),
                             r, border_radius=4)
            pygame.draw.rect(surface, (130, 130, 160), r, 1, border_radius=4)
            lt = self.font.render(label, True, WHITE)
            surface.blit(lt, (r.centerx - lt.get_width() // 2,
                              r.centery - lt.get_height() // 2))

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
            bg_c = (40, 30, 55) if not sr.collidepoint(mx, my) else (60, 45, 80)
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, (120, 80, 160), sr, 1, border_radius=4)
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
        if rarity != 'common':
            draw_rarity_border(surface, sr, rarity)
        elif enchant:
            from enchantments.effects import ENCHANT_COLORS
            ec = ENCHANT_COLORS.get(enchant['type'], (200, 200, 200))
            pygame.draw.rect(surface, ec, sr, 2, border_radius=4)
        else:
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
            d = ITEM_DATA[item_id]
            name = d[0]
            lines = [name, d[1], action]
            colors = [get_item_color(item_id, rarity), WHITE, GRAY]
            insert_rarity_tooltip(lines, colors, rarity)
            if enchant:
                from enchantments.effects import (
                    get_enchant_display_prefix, ENCHANT_COLORS as EC,
                )
                prefix = get_enchant_display_prefix(enchant)
                if prefix:
                    lines[0] = f"{prefix} {name}"
                    # Only use enchant color when there's no rarity color
                    if normalize_rarity(rarity) == 'common':
                        colors[0] = EC.get(enchant['type'], WHITE)
                ench_line = (f"Enchant: {enchant['type'].title()}"
                             f" Lv.{enchant['level']}")
                lines.insert(1, ench_line)
                colors.insert(1, EC.get(enchant['type'], CYAN))
            tooltip.show(lines, (mx, my), colors)

    # ------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event,
                     storage: Storage, inventory: Inventory) -> bool:
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
