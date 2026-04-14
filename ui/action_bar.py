"""Action Bar system — manages primary hotbar (draggable) + extra action bars.

The primary hotbar keeps using ``inv.hotbar`` / ``inv.equipped_slot``.
Extra bars store their own item data independently.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING

import pygame

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, CYAN,
    HOTBAR_SLOTS, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_GAP,
    HOTBAR_BG, HOTBAR_BORDER,
    HOTBAR_SLOT_SELECTED_BG, HOTBAR_SLOT_NORMAL_BG,
    HOTBAR_SELECTED_BORDER, HOTBAR_NORMAL_BORDER,
    HOTBAR_SLOT_NUMBER_COLOR, RED,
)

if TYPE_CHECKING:
    from sandbox_rpg import Game

# Keys for the first extra action bar (7,8,9,0,-,=)
SECONDARY_HOTKEYS = [
    pygame.K_7, pygame.K_8, pygame.K_9,
    pygame.K_0, pygame.K_MINUS, pygame.K_EQUALS,
]
SECONDARY_KEY_LABELS = ['7', '8', '9', '0', '-', '=']


class ExtraActionBar:
    """An additional action bar with 6 slots."""

    def __init__(self, x: int, y: int, has_hotkeys: bool = False) -> None:
        self.x = x
        self.y = y
        self.has_hotkeys = has_hotkeys
        self.slots: Dict[int, Tuple[str, int]] = {}
        self.slot_enchantments: Dict[int, Dict] = {}
        self.slot_rarities: Dict[int, str] = {}
        self.selected_slot: int = -1
        self._dragging = False
        self._drag_ox = 0
        self._drag_oy = 0

    def get_rect(self) -> pygame.Rect:
        ss = HOTBAR_SLOT_SIZE
        gap = HOTBAR_SLOT_GAP
        tw = HOTBAR_SLOTS * ss + (HOTBAR_SLOTS - 1) * gap
        return pygame.Rect(self.x - 8, self.y - 6, tw + 16, ss + 12)


class ActionBarManager:
    """Manages the primary hotbar position (draggable) and extra action bars."""

    def __init__(self) -> None:
        ss = HOTBAR_SLOT_SIZE
        gap = HOTBAR_SLOT_GAP
        tw = HOTBAR_SLOTS * ss + (HOTBAR_SLOTS - 1) * gap
        self.primary_x: int = SCREEN_WIDTH // 2 - tw // 2
        self.primary_y: int = SCREEN_HEIGHT - ss - 14
        self._primary_dragging = False
        self._primary_drag_ox = 0
        self._primary_drag_oy = 0

        self.extra_bars: List[ExtraActionBar] = []

        # Context menu state
        self.show_context_menu = False
        self.context_menu_x = 0
        self.context_menu_y = 0
        self.context_menu_bar_index = -1  # -1 = primary, 0+ = extra index

        self.font: Optional[pygame.font.Font] = None
        self.font_sm: Optional[pygame.font.Font] = None

    def _ensure_fonts(self) -> None:
        if self.font is None:
            self.font = pygame.font.SysFont('consolas', 14)
        if self.font_sm is None:
            self.font_sm = pygame.font.SysFont('consolas', 12)

    def create_extra_bar(self) -> ExtraActionBar:
        """Create a new extra action bar."""
        has_hotkeys = len(self.extra_bars) == 0
        offset = len(self.extra_bars)
        y = self.primary_y - 70 - offset * 70
        x = self.primary_x
        bar = ExtraActionBar(x, y, has_hotkeys)
        self.extra_bars.append(bar)
        return bar

    def get_primary_rect(self) -> pygame.Rect:
        ss = HOTBAR_SLOT_SIZE
        gap = HOTBAR_SLOT_GAP
        tw = HOTBAR_SLOTS * ss + (HOTBAR_SLOTS - 1) * gap
        return pygame.Rect(self.primary_x - 8, self.primary_y - 6,
                           tw + 16, ss + 12)

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event, g: 'Game') -> bool:
        """Handle events for all action bars.  Returns True if consumed."""
        # Context menu clicks
        if self.show_context_menu:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                cm_rect = pygame.Rect(self.context_menu_x,
                                      self.context_menu_y, 180, 28)
                if cm_rect.collidepoint(mx, my):
                    self.create_extra_bar()
                    self.show_context_menu = False
                    return True
                if self.context_menu_bar_index >= 0:
                    close_rect = pygame.Rect(self.context_menu_x,
                                             self.context_menu_y + 30,
                                             180, 28)
                    if close_rect.collidepoint(mx, my):
                        idx = self.context_menu_bar_index
                        if 0 <= idx < len(self.extra_bars):
                            self.extra_bars.pop(idx)
                        self.show_context_menu = False
                        return True
                self.show_context_menu = False
                return True

        # Right-click on any bar → context menu
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = event.pos
            if self.get_primary_rect().collidepoint(mx, my):
                self.show_context_menu = True
                self.context_menu_x = mx
                self.context_menu_y = my - 30
                self.context_menu_bar_index = -1
                return True
            for i, bar in enumerate(self.extra_bars):
                if bar.get_rect().collidepoint(mx, my):
                    self.show_context_menu = True
                    self.context_menu_x = mx
                    self.context_menu_y = my - 60
                    self.context_menu_bar_index = i
                    return True

        # Drag start (left-click on bar background, NOT on a slot)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            pr = self.get_primary_rect()
            if pr.collidepoint(mx, my) and not self._point_in_primary_slot(mx, my):
                self._primary_dragging = True
                self._primary_drag_ox = mx - self.primary_x
                self._primary_drag_oy = my - self.primary_y
                return True
            for bar in self.extra_bars:
                br = bar.get_rect()
                if br.collidepoint(mx, my) and not self._point_in_extra_slot(bar, mx, my):
                    bar._dragging = True
                    bar._drag_ox = mx - bar.x
                    bar._drag_oy = my - bar.y
                    return True

        # Drag end
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._primary_dragging:
                self._primary_dragging = False
                return True
            for bar in self.extra_bars:
                if bar._dragging:
                    bar._dragging = False
                    return True

        # Drag motion
        if event.type == pygame.MOUSEMOTION:
            if self._primary_dragging:
                mx, my = event.pos
                self.primary_x = mx - self._primary_drag_ox
                self.primary_y = my - self._primary_drag_oy
                return True
            for bar in self.extra_bars:
                if bar._dragging:
                    mx, my = event.pos
                    bar.x = mx - bar._drag_ox
                    bar.y = my - bar._drag_oy
                    return True

        # Key handling for secondary bar (first extra)
        if event.type == pygame.KEYDOWN and self.extra_bars:
            first_extra = self.extra_bars[0]
            if first_extra.has_hotkeys:
                for i, key in enumerate(SECONDARY_HOTKEYS):
                    if event.key == key:
                        first_extra.selected_slot = i
                        return True

        # Left-click on extra bar slot to select it
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for bar in self.extra_bars:
                for i in range(HOTBAR_SLOTS):
                    sr = self._extra_slot_rect(bar, i)
                    if sr.collidepoint(mx, my):
                        bar.selected_slot = i
                        return True

        return False

    def handle_close_click(self, event: pygame.event.Event) -> bool:
        """Handle close-button clicks on extra bars.  Returns True if consumed."""
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        mx, my = event.pos
        ss = HOTBAR_SLOT_SIZE
        gap = HOTBAR_SLOT_GAP
        tw = HOTBAR_SLOTS * ss + (HOTBAR_SLOTS - 1) * gap
        for i, bar in enumerate(self.extra_bars):
            close_x = bar.x + tw + 2
            close_y = bar.y - 6
            close_r = pygame.Rect(close_x, close_y, 14, 14)
            if close_r.collidepoint(mx, my):
                self.extra_bars.pop(i)
                return True
        return False

    def handle_extra_bar_drop(self, event: pygame.event.Event,
                              inv: Any) -> bool:
        """Place a held inventory item into an extra bar slot.

        Returns True if consumed.
        """
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False
        if inv.held_item is None:
            return False
        mx, my = event.pos
        for bar in self.extra_bars:
            for i in range(HOTBAR_SLOTS):
                sr = self._extra_slot_rect(bar, i)
                if sr.collidepoint(mx, my):
                    if i in bar.slots:
                        old_item = bar.slots[i]
                        old_ench = bar.slot_enchantments.get(i)
                        old_rar = bar.slot_rarities.get(i, 'common')
                        bar.slots[i] = inv.held_item
                        bar.slot_enchantments[i] = inv.held_enchant
                        bar.slot_rarities[i] = inv.held_rarity or 'common'
                        inv.held_item = old_item
                        inv.held_enchant = old_ench
                        inv.held_rarity = old_rar
                    else:
                        bar.slots[i] = inv.held_item
                        bar.slot_enchantments[i] = inv.held_enchant
                        bar.slot_rarities[i] = inv.held_rarity or 'common'
                        inv.held_item = None
                        inv.held_enchant = None
                        inv.held_rarity = 'common'
                    return True
        return False

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _point_in_primary_slot(self, mx: int, my: int) -> bool:
        ss = HOTBAR_SLOT_SIZE
        gap = HOTBAR_SLOT_GAP
        for i in range(HOTBAR_SLOTS):
            x = self.primary_x + i * (ss + gap)
            if pygame.Rect(x, self.primary_y, ss, ss).collidepoint(mx, my):
                return True
        return False

    def _point_in_extra_slot(self, bar: ExtraActionBar,
                             mx: int, my: int) -> bool:
        for i in range(HOTBAR_SLOTS):
            if self._extra_slot_rect(bar, i).collidepoint(mx, my):
                return True
        return False

    def _extra_slot_rect(self, bar: ExtraActionBar, i: int) -> pygame.Rect:
        ss = HOTBAR_SLOT_SIZE
        gap = HOTBAR_SLOT_GAP
        x = bar.x + i * (ss + gap)
        return pygame.Rect(x, bar.y, ss, ss)

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw_extra_bars(self, surface: pygame.Surface, g: 'Game') -> None:
        """Draw all extra action bars and the context menu if open."""
        self._ensure_fonts()
        for bar in self.extra_bars:
            self._draw_extra_bar(surface, bar, g)
        if self.show_context_menu:
            self._draw_context_menu(surface)

    def _draw_extra_bar(self, surface: pygame.Surface,
                        bar: ExtraActionBar, g: 'Game') -> None:
        ss = HOTBAR_SLOT_SIZE
        gap = HOTBAR_SLOT_GAP
        tw = HOTBAR_SLOTS * ss + (HOTBAR_SLOTS - 1) * gap

        # Background
        bg = pygame.Surface((tw + 16, ss + 12), pygame.SRCALPHA)
        bg.fill(HOTBAR_BG)
        surface.blit(bg, (bar.x - 8, bar.y - 6))
        pygame.draw.rect(surface, HOTBAR_BORDER,
                         (bar.x - 8, bar.y - 6, tw + 16, ss + 12),
                         1, border_radius=6)

        # Close button (small X in top-right corner)
        close_x = bar.x + tw + 2
        close_y = bar.y - 6
        close_r = pygame.Rect(close_x, close_y, 14, 14)
        mx, my = pygame.mouse.get_pos()
        hover = close_r.collidepoint(mx, my)
        pygame.draw.rect(surface,
                         (180, 50, 50) if hover else (80, 40, 40),
                         close_r, border_radius=2)
        xs = self.font_sm.render("x", True, WHITE)
        surface.blit(xs, (close_r.centerx - xs.get_width() // 2,
                          close_r.centery - xs.get_height() // 2))

        # Slots
        for i in range(HOTBAR_SLOTS):
            x = bar.x + i * (ss + gap)
            rect = pygame.Rect(x, bar.y, ss, ss)
            sel = i == bar.selected_slot
            bg_c = HOTBAR_SLOT_SELECTED_BG if sel else HOTBAR_SLOT_NORMAL_BG
            pygame.draw.rect(surface, bg_c, rect, border_radius=5)
            bd = HOTBAR_SELECTED_BORDER if sel else HOTBAR_NORMAL_BORDER
            pygame.draw.rect(surface, bd, rect, 2, border_radius=5)

            # Key label
            if bar.has_hotkeys and i < len(SECONDARY_KEY_LABELS):
                ns = self.font_sm.render(SECONDARY_KEY_LABELS[i], True,
                                         HOTBAR_SLOT_NUMBER_COLOR)
                surface.blit(ns, (x + 3, bar.y + 2))

            # Item icon and overlays
            if i in bar.slots:
                item_id, count = bar.slots[i]
                icon = g.textures.cache.get(f'item_{item_id}')
                if icon:
                    surface.blit(
                        pygame.transform.scale(icon, (32, 32)),
                        (x + 8, bar.y + 8))
                if count > 1:
                    cs = self.font_sm.render(str(count), True, WHITE)
                    surface.blit(cs, (x + ss - cs.get_width() - 3,
                                      bar.y + ss - cs.get_height() - 2))
                # Spell cooldown overlay
                if item_id in g.spell_cooldowns:
                    from data import SPELL_DATA
                    from data import SPELL_RECHARGE
                    remaining = g.spell_cooldowns[item_id]
                    sdata = SPELL_DATA.get(item_id)
                    total = sdata['cooldown'] if sdata else SPELL_RECHARGE
                    frac = max(0.0, min(1.0, remaining / total))
                    oh = int(ss * frac)
                    if oh > 0:
                        ov = pygame.Surface((ss, oh), pygame.SRCALPHA)
                        ov.fill((40, 40, 40, 160))
                        surface.blit(ov, (x, bar.y))
                # Rarity border
                rar = bar.slot_rarities.get(i, 'common')
                if rar and rar != 'common':
                    from ui.rarity_display import draw_rarity_border
                    draw_rarity_border(surface, rect, rar)

                # Tooltip on hover
                if rect.collidepoint(mx, my):
                    from data import ITEM_DATA
                    if item_id in ITEM_DATA:
                        d = ITEM_DATA[item_id]
                        name = d[0]
                        hb_rar = bar.slot_rarities.get(i, 'common')
                        if hb_rar and hb_rar != 'common':
                            name = f"{hb_rar.title()} {name}"
                        from data.quality import get_stat_description
                        lines = [name, get_stat_description(item_id, hb_rar)]
                        colors = [WHITE, WHITE]
                        if hb_rar and hb_rar != 'common':
                            from data.quality import get_rarity_color
                            colors[0] = get_rarity_color(hb_rar)
                        hb_ench = bar.slot_enchantments.get(i)
                        if hb_ench:
                            from enchantments.effects import (
                                get_enchant_display_prefix,
                                ENCHANT_COLORS as EC2,
                            )
                            prefix = get_enchant_display_prefix(hb_ench)
                            if prefix:
                                lines[0] = f"{prefix} {name}"
                                colors[0] = EC2.get(hb_ench['type'], colors[0])
                            ench_line = (f"Enchant: {hb_ench['type'].title()}"
                                         f" Lv.{hb_ench['level']}")
                            lines.insert(1, ench_line)
                            colors.insert(1, EC2.get(hb_ench['type'], CYAN))
                        if hb_rar and hb_rar != 'common':
                            from ui.rarity_display import insert_rarity_tooltip
                            insert_rarity_tooltip(lines, colors, hb_rar)
                        g.tooltip.show(lines, (mx, my), colors)

    def _draw_context_menu(self, surface: pygame.Surface) -> None:
        items_list = ["Create New Action Bar"]
        if self.context_menu_bar_index >= 0:
            items_list.append("Close Action Bar")

        menu_w = 180
        menu_h = len(items_list) * 30 + 4
        mx_pos, my_pos = pygame.mouse.get_pos()

        bg = pygame.Surface((menu_w, menu_h), pygame.SRCALPHA)
        bg.fill((25, 25, 40, 230))
        surface.blit(bg, (self.context_menu_x, self.context_menu_y))
        pygame.draw.rect(surface, HOTBAR_BORDER,
                         (self.context_menu_x, self.context_menu_y,
                          menu_w, menu_h), 1, border_radius=4)

        for idx, label in enumerate(items_list):
            iy = self.context_menu_y + 2 + idx * 30
            ir = pygame.Rect(self.context_menu_x + 2, iy, menu_w - 4, 28)
            hover = ir.collidepoint(mx_pos, my_pos)
            if hover:
                pygame.draw.rect(surface, (60, 60, 90), ir, border_radius=3)
            lt = self.font.render(label, True, WHITE if hover else GRAY)
            surface.blit(lt, (ir.x + 8, ir.centery - lt.get_height() // 2))

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def get_save_data(self) -> dict:
        return {
            'primary_x': self.primary_x,
            'primary_y': self.primary_y,
            'extra_bars': [
                {
                    'x': bar.x, 'y': bar.y,
                    'has_hotkeys': bar.has_hotkeys,
                    'slots': {str(s): [iid, c]
                              for s, (iid, c) in bar.slots.items()},
                    'slot_enchantments': {str(s): e
                                          for s, e in bar.slot_enchantments.items()},
                    'slot_rarities': {str(s): r
                                      for s, r in bar.slot_rarities.items()},
                }
                for bar in self.extra_bars
            ],
        }

    def load_save_data(self, data: dict) -> None:
        self.primary_x = data.get('primary_x', self.primary_x)
        self.primary_y = data.get('primary_y', self.primary_y)
        self.extra_bars.clear()
        for bd in data.get('extra_bars', []):
            bar = ExtraActionBar(bd['x'], bd['y'],
                                 bd.get('has_hotkeys', False))
            for s_str, (iid, c) in bd.get('slots', {}).items():
                bar.slots[int(s_str)] = (iid, c)
            for s_str, e in bd.get('slot_enchantments', {}).items():
                bar.slot_enchantments[int(s_str)] = e
            for s_str, r in bd.get('slot_rarities', {}).items():
                bar.slot_rarities[int(s_str)] = r
            self.extra_bars.append(bar)
