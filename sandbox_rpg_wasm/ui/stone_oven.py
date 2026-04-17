"""Stone Oven UI — 4-slot (2×2) smelting/cooking interface.

The player places fuel (wood, sticks) and ingredients (ore, berries, etc.)
to produce ingots, food, and other processed items.  The oven checks
smelting recipes first, then cooking recipes.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, Tuple

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, GRAY, RED, GREEN, ORANGE, CYAN,
    UI_BG_PANEL, UI_BORDER_PANEL,
    UI_SLOT_BG_NORMAL, UI_SLOT_BORDER_NORMAL,
    UI_TEXT_NORMAL, UI_TEXT_MUTED,
)
from core.components import (
    Transform, Renderable, Storage, Building, Health, LightSource,
)
from data import ITEM_DATA, ITEM_CATEGORIES
from game_controller import (
    SMELTING_RECIPES, OVEN_COOKING_RECIPES, OVEN_FUEL,
    OVEN_VALID_CATEGORIES,
    STONE_OVEN_SLOTS, STONE_OVEN_LIGHT_RADIUS,
)
from ui.draggable import DraggableWindow


def _count_fuel(stor: Storage) -> int:
    """Return total fuel units available in the oven's storage."""
    total = 0
    for slot_idx in range(STONE_OVEN_SLOTS):
        item = stor.slots.get(slot_idx)
        if item:
            iid, cnt = item
            fuel_per = OVEN_FUEL.get(iid, 0)
            total += fuel_per * cnt
    return total


def _count_items(stor: Storage) -> Dict[str, int]:
    """Return {item_id: total_count} for all items in the oven."""
    counts: Dict[str, int] = {}
    for slot_idx in range(STONE_OVEN_SLOTS):
        item = stor.slots.get(slot_idx)
        if item:
            iid, cnt = item
            counts[iid] = counts.get(iid, 0) + cnt
    return counts


def _consume_fuel(stor: Storage, fuel_needed: int) -> bool:
    """Consume fuel_needed fuel units from storage.  Returns True on success."""
    remaining = fuel_needed
    for slot_idx in range(STONE_OVEN_SLOTS):
        if remaining <= 0:
            break
        item = stor.slots.get(slot_idx)
        if not item:
            continue
        iid, cnt = item
        fuel_per = OVEN_FUEL.get(iid, 0)
        if fuel_per <= 0:
            continue
        # How many of this item do we need to consume?
        items_needed = (remaining + fuel_per - 1) // fuel_per  # ceiling div
        consume = min(cnt, items_needed)
        remaining -= consume * fuel_per
        cnt -= consume
        if cnt <= 0:
            del stor.slots[slot_idx]
        else:
            stor.slots[slot_idx] = (iid, cnt)
    return remaining <= 0


def _consume_items(stor: Storage, item_id: str, amount: int) -> bool:
    """Consume amount of item_id from storage.  Returns True on success."""
    remaining = amount
    for slot_idx in range(STONE_OVEN_SLOTS):
        if remaining <= 0:
            break
        item = stor.slots.get(slot_idx)
        if not item or item[0] != item_id:
            continue
        iid, cnt = item
        consume = min(cnt, remaining)
        cnt -= consume
        remaining -= consume
        if cnt <= 0:
            del stor.slots[slot_idx]
        else:
            stor.slots[slot_idx] = (iid, cnt)
    return remaining <= 0


def is_valid_oven_item(item_id: str) -> bool:
    """Return True if the item can be placed into the stone oven."""
    # Fuel items are always valid
    if item_id in OVEN_FUEL:
        return True
    # Check item category
    cat = ITEM_CATEGORIES.get(item_id, '')
    if cat in OVEN_VALID_CATEGORIES:
        return True
    return False


class StoneOvenUI:
    """Renders and handles the Stone Oven interaction panel."""

    def __init__(self, textures) -> None:
        self.textures = textures
        self.font = pygame.font.SysFont('consolas', 14)
        self.font_sm = pygame.font.SysFont('consolas', 12)
        # Panel dimensions
        self.pw, self.ph = 300, 240
        # Draggable window — positioned on left side of screen
        self.dw = DraggableWindow(
            self.pw, self.ph, title="Stone Oven",
            start_x=40, start_y=(SCREEN_HEIGHT - self.ph - 22) // 2)
        # Smelting state per oven entity
        self._smelt_timers: dict[int, float] = {}  # eid -> seconds remaining
        self._smelt_recipe: dict[int, dict] = {}   # eid -> current recipe dict

    def _find_recipe(self, stor: Storage) -> Optional[dict]:
        """Find the first matching recipe from items in storage."""
        counts = _count_items(stor)
        fuel = _count_fuel(stor)
        # Check smelting recipes first
        for recipe in SMELTING_RECIPES:
            if counts.get(recipe['ore'], 0) >= recipe['ore_cost']:
                if fuel >= recipe['fuel_cost']:
                    return {'type': 'smelt', **recipe}
        # Check cooking recipes
        for recipe in OVEN_COOKING_RECIPES:
            has_all = True
            for ing_id, ing_amt in recipe['ingredients'].items():
                if counts.get(ing_id, 0) < ing_amt:
                    has_all = False
                    break
            if has_all and fuel >= recipe['fuel_cost']:
                return {'type': 'cook', **recipe}
        return None

    def _consume_materials(self, stor: Storage, recipe: dict) -> bool:
        """Consume ingredients and fuel for one processing cycle."""
        rtype = recipe.get('type', 'smelt')
        if rtype == 'smelt':
            if not _consume_items(stor, recipe['ore'], recipe['ore_cost']):
                return False
        elif rtype == 'cook':
            for ing_id, ing_amt in recipe['ingredients'].items():
                if not _consume_items(stor, ing_id, ing_amt):
                    return False
        # Consume fuel
        return _consume_fuel(stor, recipe['fuel_cost'])

    def _deposit_result(self, stor: Storage, result_id: str) -> bool:
        """Add the result to an available storage slot."""
        # Try to stack into existing slot
        for slot_idx in range(STONE_OVEN_SLOTS):
            item = stor.slots.get(slot_idx)
            if item and item[0] == result_id:
                stor.slots[slot_idx] = (result_id, item[1] + 1)
                return True
        # Try empty slot
        for slot_idx in range(STONE_OVEN_SLOTS):
            if slot_idx not in stor.slots:
                stor.slots[slot_idx] = (result_id, 1)
                return True
        return False  # No room

    def update(self, g: 'Game', dt: float) -> None:
        """Tick all active stone ovens (runs even when UI is closed)."""
        for eid in g.em.get_entities_with(Transform, Storage, Building):
            bld = g.em.get_component(eid, Building)
            if bld.building_type != 'stone_oven':
                continue
            stor = g.em.get_component(eid, Storage)
            # Check if currently smelting
            if eid in self._smelt_timers:
                self._smelt_timers[eid] -= dt
                if self._smelt_timers[eid] <= 0:
                    # Produce result
                    recipe = self._smelt_recipe.get(eid)
                    if recipe:
                        self._deposit_result(stor, recipe['result'])
                    del self._smelt_timers[eid]
                    self._smelt_recipe.pop(eid, None)
                    # Update visual — turn off fire
                    rend = g.em.get_component(eid, Renderable) if g.em.has_component(eid, Renderable) else None
                    if rend:
                        rend.surface = g.textures.get('stone_oven_False')
                    # Remove light when done
                    if g.em.has_component(eid, LightSource):
                        g.em.remove_component(eid, LightSource)
            # Try to start next cycle if not currently processing
            if eid not in self._smelt_timers:
                recipe = self._find_recipe(stor)
                if recipe:
                    if self._consume_materials(stor, recipe):
                        self._smelt_timers[eid] = recipe['time']
                        self._smelt_recipe[eid] = recipe
                        # Update visual — show fire
                        rend = g.em.get_component(eid, Renderable) if g.em.has_component(eid, Renderable) else None
                        if rend:
                            rend.surface = g.textures.get('stone_oven_True')
                        # Add light while burning
                        if not g.em.has_component(eid, LightSource):
                            from core.constants import LIGHT_COLOR_TORCH
                            g.em.add_component(eid, LightSource(
                                STONE_OVEN_LIGHT_RADIUS, LIGHT_COLOR_TORCH, 0.7))

    def draw(self, surface: pygame.Surface, g: 'Game') -> None:
        """Draw the Stone Oven UI panel."""
        if not g.show_stone_oven or g.active_stone_oven is None:
            return
        eid = g.active_stone_oven
        if not g.em.has_component(eid, Storage):
            g.show_stone_oven = False
            return
        stor = g.em.get_component(eid, Storage)

        cr = self.dw.content_rect
        px, py = cr.x, cr.y
        scale = self.dw.scale
        pw = self.dw.w
        ph = self.dw.h

        # Panel background
        panel = pygame.Rect(px, py, pw, ph)
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill(UI_BG_PANEL)
        surface.blit(bg, (px, py))

        # Draw 2×2 grid of slots
        slot_size = int(48 * scale)
        slot_gap = int(6 * scale)
        grid_w = 2 * slot_size + slot_gap
        grid_x = px + (pw - grid_w) // 2
        grid_y = py + int(8 * scale)

        for row in range(2):
            for col in range(2):
                slot_idx = row * 2 + col
                sx = grid_x + col * (slot_size + slot_gap)
                sy = grid_y + row * (slot_size + slot_gap)
                rect = pygame.Rect(sx, sy, slot_size, slot_size)
                pygame.draw.rect(surface, UI_SLOT_BG_NORMAL, rect)
                pygame.draw.rect(surface, UI_SLOT_BORDER_NORMAL, rect, 1)
                item = stor.slots.get(slot_idx)
                if item:
                    iid, cnt = item
                    tex = self.textures.cache.get(f'item_{iid}')
                    if tex:
                        icon_size = int(32 * scale)
                        scaled = pygame.transform.scale(tex, (icon_size, icon_size))
                        surface.blit(scaled, (sx + (slot_size - icon_size) // 2,
                                              sy + (slot_size - icon_size) // 2))
                    if cnt > 1:
                        ct_txt = self.font_sm.render(str(cnt), True, WHITE)
                        surface.blit(ct_txt,
                                     (sx + slot_size - ct_txt.get_width() - 4,
                                      sy + slot_size - ct_txt.get_height() - 2))

        # Smelting progress
        info_y = grid_y + 2 * (slot_size + slot_gap) + int(10 * scale)
        if eid in self._smelt_timers:
            recipe = self._smelt_recipe.get(eid)
            if recipe:
                name = ITEM_DATA[recipe['result']][0] if recipe['result'] in ITEM_DATA else recipe['result']
                remaining = max(0, self._smelt_timers[eid])
                total = recipe['time']
                progress = 1.0 - (remaining / total) if total > 0 else 1.0
                # Progress bar
                bar_w = pw - int(40 * scale)
                bar_rect = pygame.Rect(px + int(20 * scale), info_y, bar_w, int(14 * scale))
                pygame.draw.rect(surface, (60, 60, 60), bar_rect)
                fill_rect = pygame.Rect(px + int(20 * scale), info_y, int(bar_w * progress), int(14 * scale))
                pygame.draw.rect(surface, ORANGE, fill_rect)
                pygame.draw.rect(surface, UI_SLOT_BORDER_NORMAL, bar_rect, 1)
                label = "Cooking" if recipe.get('type') == 'cook' else "Smelting"
                status = self.font_sm.render(
                    f"{label} {name}... {remaining:.1f}s", True, WHITE)
                surface.blit(status, (px + int(20 * scale), info_y + int(18 * scale)))
        else:
            recipe = self._find_recipe(stor)
            if recipe:
                name = ITEM_DATA[recipe['result']][0] if recipe['result'] in ITEM_DATA else recipe['result']
                label = "cook" if recipe.get('type') == 'cook' else "smelt"
                info = self.font_sm.render(f"Ready to {label}: {name}", True, GREEN)
            else:
                info = self.font_sm.render("Add fuel + ingredients", True, UI_TEXT_MUTED)
            surface.blit(info, (px + int(20 * scale), info_y))

        # Instructions
        instr_y = py + ph - int(24 * scale)
        instr = self.font_sm.render("Drag items in/out", True, UI_TEXT_MUTED)
        surface.blit(instr, (px + (pw - instr.get_width()) // 2, instr_y))

        # Chrome (title bar, close button, resize handle)
        self.dw.draw_chrome(surface)

    def handle_click(self, g: 'Game', mx: int, my: int,
                     button: int = 1) -> bool:
        """Handle mouse clicks on the stone oven grid.

        Returns True if click was consumed.
        """
        if not g.show_stone_oven or g.active_stone_oven is None:
            return False
        eid = g.active_stone_oven
        if not g.em.has_component(eid, Storage):
            return False
        stor = g.em.get_component(eid, Storage)
        inv = g.em.get_component(g.player_id, 'Inventory')
        if inv is None:
            from core.components import Inventory
            inv = g.em.get_component(g.player_id, Inventory)

        cr = self.dw.content_rect
        px, py = cr.x, cr.y
        scale = self.dw.scale
        pw = self.dw.w

        slot_size = int(48 * scale)
        slot_gap = int(6 * scale)
        grid_w = 2 * slot_size + slot_gap
        grid_x = px + (pw - grid_w) // 2
        grid_y = py + int(8 * scale)

        for row in range(2):
            for col in range(2):
                slot_idx = row * 2 + col
                sx = grid_x + col * (slot_size + slot_gap)
                sy = grid_y + row * (slot_size + slot_gap)
                if sx <= mx < sx + slot_size and sy <= my < sy + slot_size:
                    item = stor.slots.get(slot_idx)
                    if item:
                        # Take item out to player inventory
                        iid, cnt = item
                        inv.add_item(iid, cnt)
                        del stor.slots[slot_idx]
                        g._notify(f"Took {cnt} {ITEM_DATA[iid][0] if iid in ITEM_DATA else iid}")
                    elif inv.held_item:
                        # Drop held item (from inventory drag) into oven slot
                        held_id, held_cnt = inv.held_item
                        if is_valid_oven_item(held_id):
                            stor.slots[slot_idx] = (held_id, held_cnt)
                            name = ITEM_DATA[held_id][0] if held_id in ITEM_DATA else held_id
                            g._notify(f"Added {held_cnt} {name}")
                            inv.held_item = None
                            inv.held_enchant = None
                            inv.held_rarity = 'common'
                        else:
                            g._notify("You don't want to burn that.")
                    else:
                        # Put selected hotbar item in
                        eq_id = inv.get_equipped()
                        if eq_id and inv.has(eq_id):
                            if is_valid_oven_item(eq_id):
                                # Transfer entire stack from inventory
                                total = inv.count(eq_id)
                                if total > 0:
                                    inv.remove_item(eq_id, total)
                                    stor.slots[slot_idx] = (eq_id, total)
                                    name = ITEM_DATA[eq_id][0] if eq_id in ITEM_DATA else eq_id
                                    g._notify(f"Added {total} {name}")
                            else:
                                g._notify("You don't want to burn that.")
                    return True
        return False

    def handle_event(self, event: pygame.event.Event, g: 'Game') -> bool:
        """Handle draggable window events (drag, close, resize).

        Returns True if the event was consumed.
        """
        if not g.show_stone_oven:
            return False
        consumed = self.dw.handle_event(event)
        if self.dw.close_requested:
            g.show_stone_oven = False
            g.active_stone_oven = None
        return consumed
