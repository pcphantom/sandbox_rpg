"""Character / equipment menu — stats display + equip/unequip."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import pygame

from core.constants import (SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, CYAN, GREEN,
                            GRAY, YELLOW, ORANGE, LIGHT_BLUE,
                            AGI_SPEED_BONUS, AGI_SPEED_BONUS_CAP,
                            UI_BORDER_PANEL, UI_STAT_BUTTON_HOVER,
                            UI_STAT_BUTTON_NORMAL, UI_UNEQUIP_HOVER,
                            UI_UNEQUIP_NORMAL, UI_EQUIP_HOVER, UI_EQUIP_NORMAL,
                            UI_BORDER_DIALOG, UI_DROPDOWN_HOVER,
                            UI_DROPDOWN_NORMAL)
from core.components import Inventory, Health, PlayerStats, Equipment
from data import ITEM_DATA, ITEM_CATEGORIES
from ui.elements import Tooltip

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
        self._dropdown_attr: str = ''
        self._dropdown_items: List[Tuple[int, str, Optional[Dict]]] = []
        self._dropdown_rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._dropdown_scroll: int = 0
        self._dropdown_max_visible: int = 6
        self._dropdown_row_h: int = 24

    def draw(self, surface: pygame.Surface,
             stats: PlayerStats, equipment: Equipment,
             health: Health, inventory: Inventory,
             tooltip: Tooltip) -> None:
        pw, ph = 520, 480
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((20, 20, 35, 240))
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, UI_BORDER_PANEL,
                         (px, py, pw, ph), 2, border_radius=10)

        title = self.title_font.render("Character  [P]", True, WHITE)
        surface.blit(title,
                     (px + pw // 2 - title.get_width() // 2, py + 10))

        # Top-left: Level/HP header
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

        # Left column: Stats
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
                bc = UI_STAT_BUTTON_HOVER if hov else UI_STAT_BUTTON_NORMAL
                pygame.draw.rect(surface, bc, btn, border_radius=3)
                pygame.draw.rect(surface, GREEN, btn, 1, border_radius=3)
                t = self.font_sm.render("+", True, WHITE)
                surface.blit(t, (btn.centerx - t.get_width() // 2,
                                 btn.centery - t.get_height() // 2))
            sy += 24
        surface.blit(self.font_sm.render(
            f"Stat points: {stats.stat_points}", True, GRAY), (sx, sy))

        # Right column: Derived stats / bonuses (to the right of stat block)
        from systems.damage_calc import calc_damage_reduction, calc_melee_damage, calc_ranged_damage
        from systems.rarity import apply_rarity
        from core.item_stack import normalize_rarity
        from core.enhancement import get_base_item_id, get_enhancement_level, RANGED_OFFENSE_BONUS_PER_LEVEL
        from data import ITEM_DATA as _ID, RANGED_DATA as _RD, AMMO_BONUS_DAMAGE

        bx = px + 270
        by = py + 104

        # Attack damage (apply rarity to match actual combat damage)
        weapon = equipment.weapon if equipment and equipment.weapon else inventory.get_equipped()
        base_dmg = 5
        if weapon and weapon in _ID and _ID[weapon][2] > 0:
            base_dmg = _ID[weapon][2]
        w_rarity = normalize_rarity(inventory.get_equipped_rarity())
        if w_rarity == 'common' and equipment:
            w_rarity = normalize_rarity(equipment.rarities.get('weapon', 'common'))
        base_dmg = apply_rarity(base_dmg, w_rarity)
        atk = calc_melee_damage(base_dmg, stats, equipment)
        crit_pct = stats.luck * 2
        surface.blit(self.font_sm.render(
            f"Attack damage: {atk}", True, ORANGE), (bx, by))
        by += 18
        surface.blit(self.font_sm.render(
            f"Crit: {crit_pct}%", True, ORANGE), (bx, by))
        by += 18

        # Ranged damage (apply enhancement + rarity to match actual combat)
        if equipment and equipment.ranged:
            rdata = _RD.get(equipment.ranged)
            if not rdata:
                rdata = _RD.get(get_base_item_id(equipment.ranged))
            if rdata:
                base_ranged = rdata['damage']
                enh_level = get_enhancement_level(equipment.ranged)
                if enh_level > 0:
                    base_ranged += enh_level * RANGED_OFFENSE_BONUS_PER_LEVEL
                r_rarity = normalize_rarity(equipment.rarities.get('ranged', 'common'))
                base_ranged = apply_rarity(base_ranged, r_rarity)
                ammo_bonus = AMMO_BONUS_DAMAGE.get(equipment.ammo, 0) if equipment.ammo else 0
                r_dmg = calc_ranged_damage(base_ranged, ammo_bonus, stats)
                surface.blit(self.font_sm.render(
                    f"Ranged damage: {r_dmg}", True, ORANGE), (bx, by))
                by += 18

        # Defense
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

        # Bottom: Equipment (below stats)
        ex = px + 20
        ey = py + 280
        surface.blit(self.font.render("Equipment", True, YELLOW), (ex, ey))
        ey += 26
        for attr, label in _EQUIP_SLOTS:
            item_id = getattr(equipment, attr)
            name = ITEM_DATA[item_id][0] if item_id and item_id in ITEM_DATA else "\u2014"
            name_color = WHITE
            eq_ench = equipment.enchantments.get(attr)
            if eq_ench and item_id:
                from enchantments.effects import (
                    get_enchant_display_prefix, ENCHANT_COLORS,
                )
                prefix = get_enchant_display_prefix(eq_ench)
                if prefix:
                    name = f"{prefix} {name}"
                    name_color = ENCHANT_COLORS.get(eq_ench['type'], WHITE)
            surface.blit(self.font.render(f"{label}: ", True, GRAY), (ex, ey))
            surface.blit(self.font.render(name, True, name_color), (ex + 80, ey))
            # Icon
            if item_id:
                icon = self.textures.cache.get(f'item_{item_id}')
                icon_rect = pygame.Rect(ex + 350, ey - 1, 22, 22)
                if icon:
                    surface.blit(pygame.transform.scale(icon, (20, 20)),
                                 (ex + 351, ey))
                # Rarity border around icon (the ONLY item border)
                eq_rar = equipment.rarities.get(attr, 'common')
                if eq_rar != 'common':
                    from ui.rarity_display import draw_rarity_border
                    draw_rarity_border(surface, icon_rect, eq_rar)
            # Equip / Unequip button
            btn = pygame.Rect(ex + 376, ey, 20, 20)
            hov = btn.collidepoint(mx, my)
            if item_id:
                # Unequip
                pygame.draw.rect(surface,
                                 UI_UNEQUIP_HOVER if hov else UI_UNEQUIP_NORMAL,
                                 btn, border_radius=3)
                t = self.font_sm.render("x", True, WHITE)
            else:
                # Equip
                pygame.draw.rect(surface,
                                 UI_EQUIP_HOVER if hov else UI_EQUIP_NORMAL,
                                 btn, border_radius=3)
                t = self.font_sm.render("E", True, WHITE)
            surface.blit(t, (btn.centerx - t.get_width() // 2,
                             btn.centery - t.get_height() // 2))
            ey += 28

        # Equip hint
        ey += 4
        surface.blit(self.font_sm.render(
            "Click E to equip, x to unequip", True, GRAY), (ex, ey))

        # --- Equip dropdown overlay ---
        if self._dropdown_open and self._dropdown_items:
            self._draw_dropdown(surface, mx, my)

    def _draw_dropdown(self, surface: pygame.Surface,
                       mx: int, my: int) -> None:
        """Draw the equip-selection dropdown list."""
        rh = self._dropdown_row_h
        dr = self._dropdown_rect
        # Background
        bg = pygame.Surface((dr.width, dr.height), pygame.SRCALPHA)
        bg.fill((25, 25, 45, 245))
        surface.blit(bg, (dr.x, dr.y))
        pygame.draw.rect(surface, UI_BORDER_DIALOG, dr, 1, border_radius=3)
        # Title
        title_t = self.font_sm.render(
            f"Select {self._dropdown_attr.capitalize()}:", True, YELLOW)
        surface.blit(title_t, (dr.x + 6, dr.y + 3))
        # Items
        iy = dr.y + rh
        start = self._dropdown_scroll
        end = min(start + self._dropdown_max_visible,
                  len(self._dropdown_items))
        for idx in range(start, end):
            _inv_slot, iid, ench, rar = self._dropdown_items[idx]
            row_r = pygame.Rect(dr.x + 2, iy, dr.width - 4, rh)
            hov = row_r.collidepoint(mx, my)
            rc = UI_DROPDOWN_HOVER if hov else UI_DROPDOWN_NORMAL
            pygame.draw.rect(surface, rc, row_r, border_radius=2)
            # Icon
            icon = self.textures.cache.get(f'item_{iid}')
            if icon:
                surface.blit(
                    pygame.transform.scale(icon, (18, 18)),
                    (row_r.x + 4, row_r.y + 3))
            # Name (with rarity + enchant prefix)
            name = ITEM_DATA[iid][0] if iid in ITEM_DATA else iid
            name_color = WHITE
            if rar and rar != 'common':
                name = f"{rar.title()} {name}"
                from data.quality import get_rarity_color
                name_color = get_rarity_color(rar)
            if ench:
                from enchantments.effects import (
                    get_enchant_display_prefix, ENCHANT_COLORS,
                )
                prefix = get_enchant_display_prefix(ench)
                if prefix:
                    name = f"{prefix} {name}"
                    name_color = ENCHANT_COLORS.get(ench['type'], name_color)
            surface.blit(self.font_sm.render(name, True, name_color),
                         (row_r.x + 26, row_r.y + 5))
            iy += rh
        # Scroll indicators
        if self._dropdown_scroll > 0:
            surface.blit(self.font_sm.render("\u25b2", True, GRAY),
                         (dr.right - 16, dr.y + rh - 2))
        if end < len(self._dropdown_items):
            surface.blit(self.font_sm.render("\u25bc", True, GRAY),
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
                items.append((slot_idx, iid, ench, rar))
        for slot_idx, (iid, cnt) in sorted(inventory.hotbar.items()):
            cat = ITEM_CATEGORIES.get(iid, '')
            if cat in cats:
                ench = inventory.hotbar_enchantments.get(slot_idx)
                rar = inventory.hotbar_rarities.get(slot_idx, 'common')
                items.append((-(slot_idx + 1), iid, ench, rar))
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
        dh = rh * (vis + 1)
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
        inv_slot, iid, ench, rar = self._dropdown_items[idx]
        attr = self._dropdown_attr
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
        equipment.rarities[attr] = rar
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
                row_y = my - (dr.y + rh)
                if row_y >= 0:
                    row_idx = self._dropdown_scroll + row_y // rh
                    if 0 <= row_idx < len(self._dropdown_items):
                        self._equip_from_dropdown(
                            row_idx, equipment, inventory)
                        return True
                return True
            else:
                self._dropdown_open = False
                return True

        pw, ph = 520, 480
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2

        # Stat + buttons
        sx = px + 20
        sy = py + 50 + 24 + 30 + 22
        for sname in _STAT_NAMES:
            btn = pygame.Rect(sx + 180, sy, 24, 20)
            if btn.collidepoint(mx, my) and stats.stat_points > 0:
                setattr(stats, sname, getattr(stats, sname) + 1)
                stats.stat_points -= 1
                return True
            sy += 24

        # Equipment buttons (below stats)
        ex = px + 20
        ey = py + 280 + 26
        for attr, _label in _EQUIP_SLOTS:
            btn = pygame.Rect(ex + 376, ey, 20, 20)
            if btn.collidepoint(mx, my):
                item_id = getattr(equipment, attr)
                if item_id:
                    # Unequip - return to inventory (transfer enchant + rarity back)
                    ench = equipment.enchantments.pop(attr, None)
                    rar = equipment.rarities.pop(attr, 'common')
                    inventory.add_item_enchanted(item_id, ench, 1, rar)
                    setattr(equipment, attr, None)
                else:
                    # Equip — open dropdown to let player choose
                    self._open_dropdown(attr, inventory,
                                        btn.x, btn.y)
                return True
            ey += 28
        return False
