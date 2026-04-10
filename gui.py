"""GUI elements — HUD, inventory with pages, crafting, pause menu,
character/equipment menu, chest UI, tooltip, progress bars."""
from __future__ import annotations

from typing import List, Tuple, Dict, Optional, Any, Callable

import pygame

from constants import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN,
                       CYAN, GRAY, YELLOW, DARK_GRAY, ORANGE, LIGHT_BLUE,
                       INVENTORY_SLOTS_PER_PAGE,
                       INVENTORY_PAGES, INVENTORY_COLS, SAVE_SLOTS,
                       QUICK_SAVE_SLOT, CHEST_CAPACITY)
from components import Inventory, Health, PlayerStats, Equipment, Storage
from items_data import ITEM_DATA, ITEM_CATEGORIES, RECIPES, ARMOR_VALUES


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
        from utils import clamp as _clamp
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
        self.visible = False
        self.pos = (0, 0)
        self.font = pygame.font.SysFont('consolas', 13)

    def clear(self) -> None:
        self.visible = False

    def show(self, lines: List[str], pos: Tuple[int, int]) -> None:
        self.lines = lines; self.visible = True; self.pos = pos

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.lines:
            return
        surfs = [self.font.render(l, True, WHITE) for l in self.lines]
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
# INVENTORY GRID (with pages)
# ======================================================================
class InventoryGrid(UIElement):
    """Paginated inventory grid — 4 pages × 24 slots."""

    def __init__(self, rect: pygame.Rect, inventory: Inventory,
                 textures: Any) -> None:
        super().__init__(rect)
        self.inventory = inventory; self.textures = textures
        self.slot_size = 48; self.cols = INVENTORY_COLS
        self.rows = INVENTORY_SLOTS_PER_PAGE // self.cols  # 4
        self.page = 0
        self.font = pygame.font.SysFont('consolas', 14)
        self.title_font = pygame.font.SysFont('consolas', 20, bold=True)

    def _page_offset(self) -> int:
        return self.page * INVENTORY_SLOTS_PER_PAGE

    def draw(self, surface: pygame.Surface, tooltip: Tooltip) -> None:
        if not self.visible:
            return
        bg = pygame.Surface((self.rect.width, self.rect.height),
                            pygame.SRCALPHA)
        bg.fill((20, 20, 32, 235))
        surface.blit(bg, self.rect.topleft)
        pygame.draw.rect(surface, (130, 130, 155), self.rect, 2,
                         border_radius=8)

        # Title + page indicator
        title = self.title_font.render(
            f"Inventory  ({self.page + 1}/{INVENTORY_PAGES})", True, WHITE)
        surface.blit(title, (self.rect.centerx - title.get_width() // 2,
                             self.rect.y + 8))

        mx, my = pygame.mouse.get_pos()
        off = self._page_offset()
        for i in range(INVENTORY_SLOTS_PER_PAGE):
            slot_idx = off + i
            col = i % self.cols
            row = i // self.cols
            x = self.rect.x + 12 + col * (self.slot_size + 6)
            y = self.rect.y + 38 + row * (self.slot_size + 6)
            sr = pygame.Rect(x, y, self.slot_size, self.slot_size)
            sel = slot_idx == self.inventory.equipped_slot
            bg_c = (80, 80, 110) if sel else (45, 45, 60)
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            bd = (200, 200, 240) if sel else (100, 100, 120)
            pygame.draw.rect(surface, bd, sr, 1, border_radius=4)
            if slot_idx in self.inventory.slots:
                item_id, count = self.inventory.slots[slot_idx]
                icon = self.textures.cache.get(f'item_{item_id}')
                if icon:
                    surface.blit(pygame.transform.scale(icon, (34, 34)),
                                 (x + 7, y + 7))
                if count > 1:
                    ct = self.font.render(str(count), True, WHITE)
                    surface.blit(ct, (x + self.slot_size - ct.get_width() - 4,
                                      y + self.slot_size - ct.get_height() - 2))
                if sr.collidepoint(mx, my) and item_id in ITEM_DATA:
                    d = ITEM_DATA[item_id]
                    tooltip.show([d[0], d[1]], (mx, my))

        # Page navigation arrows
        nav_y = (self.rect.y + 38
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

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            off = self._page_offset()
            for i in range(INVENTORY_SLOTS_PER_PAGE):
                slot_idx = off + i
                col = i % self.cols
                row = i // self.cols
                x = self.rect.x + 12 + col * (self.slot_size + 6)
                y = self.rect.y + 38 + row * (self.slot_size + 6)
                if pygame.Rect(x, y, self.slot_size,
                               self.slot_size).collidepoint(mx, my):
                    self.inventory.equipped_slot = slot_idx
                    return True
            # Page buttons
            nav_y = (self.rect.y + 38
                     + self.rows * (self.slot_size + 6) + 4)
            prev_r = pygame.Rect(self.rect.x + 12, nav_y, 60, 28)
            next_r = pygame.Rect(self.rect.right - 72, nav_y, 60, 28)
            if prev_r.collidepoint(mx, my):
                self.page = (self.page - 1) % INVENTORY_PAGES
                return True
            if next_r.collidepoint(mx, my):
                self.page = (self.page + 1) % INVENTORY_PAGES
                return True
        return False


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
                    tooltip.show([d[0], d[1]], (mx, my))

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

        pw, ph = 360, 430
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
                label += f"Day {day_num}  Lv.{info['level']}  Kills:{info['kills']}"
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
        self._draw_button(surface, px + 40, btn_y, 80, 32, "Save")
        self._draw_button(surface, px + 140, btn_y, 80, 32, "Load")
        self._draw_button(surface, px + 240, btn_y, 80, 32, "Delete")

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
        pw, ph = 360, 430
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
        if pygame.Rect(px + 40, btn_y, 80, 32).collidepoint(mx, my):
            save_cb(self.selected_slot)
            return True
        if pygame.Rect(px + 140, btn_y, 80, 32).collidepoint(mx, my):
            load_cb(self.selected_slot)
            return True
        if pygame.Rect(px + 240, btn_y, 80, 32).collidepoint(mx, my):
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

    def draw(self, surface: pygame.Surface,
             stats: PlayerStats, equipment: Equipment,
             health: Health, inventory: Inventory,
             tooltip: Tooltip) -> None:
        pw, ph = 520, 420
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

        # Left: Stats
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
        sy += 26

        # Derived stats
        from systems import calc_damage_reduction, calc_melee_damage
        from items_data import ITEM_DATA as _ID, RANGED_DATA as _RD

        # Attack damage
        weapon = equipment.weapon if equipment and equipment.weapon else inventory.get_equipped()
        base_dmg = 5
        if weapon and weapon in _ID and _ID[weapon][2] > 0:
            base_dmg = _ID[weapon][2]
        atk = calc_melee_damage(base_dmg, stats, equipment)
        crit_pct = stats.luck * 2
        surface.blit(self.font_sm.render(
            f"Attack damage: {atk}   Crit: {crit_pct}%", True, ORANGE),
            (sx, sy))
        sy += 18

        # Ranged damage (if ranged weapon equipped)
        if equipment and equipment.ranged and equipment.ranged in _RD:
            rd = _RD[equipment.ranged]
            r_dmg = rd['damage'] + stats.agility * 2
            surface.blit(self.font_sm.render(
                f"Ranged damage: {r_dmg}", True, ORANGE), (sx, sy))
            sy += 18

        # Defense
        dr = calc_damage_reduction(equipment)
        surface.blit(self.font_sm.render(
            f"Defense: {dr}", True, LIGHT_BLUE), (sx, sy))
        sy += 18
        speed_bonus = stats.agility * 5
        surface.blit(self.font_sm.render(
            f"Speed bonus: +{speed_bonus}%", True, GRAY), (sx, sy))
        sy += 18
        luck_bonus = stats.luck * 10
        surface.blit(self.font_sm.render(
            f"Harvest luck: +{luck_bonus}%", True, GRAY), (sx, sy))

        # Right: Equipment
        ex = px + 270
        ey = py + 50
        surface.blit(self.font.render("Equipment", True, YELLOW), (ex, ey))
        ey += 26
        for attr, label in _EQUIP_SLOTS:
            item_id = getattr(equipment, attr)
            name = ITEM_DATA[item_id][0] if item_id and item_id in ITEM_DATA else "—"
            surface.blit(self.font.render(f"{label}: ", True, GRAY), (ex, ey))
            surface.blit(self.font.render(name, True, WHITE), (ex + 80, ey))
            # Icon
            if item_id:
                icon = self.textures.cache.get(f'item_{item_id}')
                if icon:
                    surface.blit(pygame.transform.scale(icon, (20, 20)),
                                 (ex + 200, ey))
            # Equip / Unequip button
            btn = pygame.Rect(ex + 225, ey, 20, 20)
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

        # Compatible items from inventory
        ey += 12
        surface.blit(self.font_sm.render(
            "Click E to equip, x to unequip", True, GRAY), (ex, ey))

    def handle_event(self, event: pygame.event.Event,
                     stats: PlayerStats, equipment: Equipment,
                     inventory: Inventory) -> bool:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos
        pw, ph = 520, 420
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

        # Equipment buttons
        ex = px + 270
        ey = py + 50 + 26
        for attr, _label in _EQUIP_SLOTS:
            btn = pygame.Rect(ex + 225, ey, 20, 20)
            if btn.collidepoint(mx, my):
                item_id = getattr(equipment, attr)
                if item_id:
                    # Unequip → return to inventory
                    inventory.add_item(item_id, 1)
                    setattr(equipment, attr, None)
                else:
                    # Equip → find first matching item in inventory
                    cats = _SLOT_CATEGORIES.get(attr, [])
                    for _slot, (iid, cnt) in sorted(inventory.slots.items()):
                        cat = ITEM_CATEGORIES.get(iid, '')
                        if cat in cats:
                            setattr(equipment, attr, iid)
                            inventory.remove_item(iid, 1)
                            break
                return True
            ey += 28
        return False


# ======================================================================
# CHEST UI
# ======================================================================
class ChestUI:
    """Side-by-side chest + player inventory panel for transferring items."""

    def __init__(self, textures: Any) -> None:
        self.textures = textures
        self.font = pygame.font.SysFont('consolas', 14)
        self.title_font = pygame.font.SysFont('consolas', 18, bold=True)
        self.slot_size = 44
        self.cols = 6
        self.chest_entity: int | None = None

    def draw(self, surface: pygame.Surface, storage: Storage,
             inventory: Inventory, tooltip: Tooltip) -> None:
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
        self._draw_grid(surface, storage.slots, storage.capacity,
                        px + 10, py + 34, mx, my, tooltip, 'chest')

        # Divider
        pygame.draw.line(surface, GRAY,
                         (px + pw // 2, py + 8),
                         (px + pw // 2, py + ph - 8), 1)

        # Right half: Player inventory (first page)
        title_r = self.title_font.render("Inventory", True, CYAN)
        surface.blit(title_r, (px + pw // 2 + 20, py + 8))
        self._draw_grid(surface, inventory.slots, 24,
                        px + pw // 2 + 10, py + 34, mx, my, tooltip, 'inv')

    def _draw_grid(self, surface: pygame.Surface,
                   slots: Dict[int, tuple], capacity: int,
                   ox: int, oy: int, mx: int, my: int,
                   tooltip: Tooltip, side: str) -> None:
        ss = self.slot_size
        for i in range(min(capacity, 24)):
            col = i % self.cols
            row = i // self.cols
            x = ox + col * (ss + 4)
            y = oy + row * (ss + 4)
            sr = pygame.Rect(x, y, ss, ss)
            bg_c = (50, 50, 65) if not sr.collidepoint(mx, my) else (70, 70, 95)
            pygame.draw.rect(surface, bg_c, sr, border_radius=4)
            pygame.draw.rect(surface, (100, 100, 120), sr, 1, border_radius=4)
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
                    action = "Click: Move to " + ("Inventory" if side == 'chest' else "Chest")
                    tooltip.show([d[0], d[1], action], (mx, my))

    def handle_event(self, event: pygame.event.Event,
                     storage: Storage, inventory: Inventory) -> bool:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos
        pw, ph = 620, 320
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        ss = self.slot_size

        # Click in chest grid → move to inventory
        for i in range(min(storage.capacity, 24)):
            col = i % self.cols
            row = i // self.cols
            x = px + 10 + col * (ss + 4)
            y = py + 34 + row * (ss + 4)
            if pygame.Rect(x, y, ss, ss).collidepoint(mx, my):
                if i in storage.slots:
                    item_id, count = storage.slots[i]
                    overflow = inventory.add_item(item_id, count)
                    if overflow == 0:
                        del storage.slots[i]
                    else:
                        storage.slots[i] = (item_id, overflow)
                    return True

        # Click in inventory grid → move to chest
        for i in range(24):
            col = i % self.cols
            row = i // self.cols
            x = px + pw // 2 + 10 + col * (ss + 4)
            y = py + 34 + row * (ss + 4)
            if pygame.Rect(x, y, ss, ss).collidepoint(mx, my):
                if i in inventory.slots:
                    item_id, count = inventory.slots[i]
                    overflow = storage.add_item(item_id, count)
                    if overflow == 0:
                        del inventory.slots[i]
                    else:
                        inventory.slots[i] = (item_id, overflow)
                    return True
        return False
