"""Rarity display helpers — borders, tooltips, and slot tracking.

Shared across all UI panels (InventoryGrid, ChestUI, EnchantmentTableUI,
CharacterMenu) so rarity rendering logic lives in one place.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import pygame

from data.quality import get_rarity_color
from core.constants import UI_ENCHANT_FALLBACK


# ── drawing helpers ───────────────────────────────────────────────────

def draw_rarity_border(surface: pygame.Surface, rect: pygame.Rect,
                       rarity: str) -> bool:
    """Draw a coloured 2 px border for non-common rarity.

    Returns ``True`` if a border was drawn (caller can skip its own).
    """
    if rarity == 'common':
        return False
    pygame.draw.rect(surface, get_rarity_color(rarity), rect,
                     2, border_radius=4)
    return True


# PRESERVED for future use — inner enhancement border is currently disabled.
# def draw_enhancement_border(surface: pygame.Surface, rect: pygame.Rect,
#                             item_id: str) -> bool:
#     """Draw a coloured 2 px inner border for enhanced items (+1..+5).
#
#     Returns ``True`` if a border was drawn.
#     """
#     from core.enhancement import get_enhancement_level, ENHANCEMENT_COLORS
#     enh_lvl = get_enhancement_level(item_id)
#     if enh_lvl <= 0:
#         return False
#     enh_color = ENHANCEMENT_COLORS.get(enh_lvl, UI_ENCHANT_FALLBACK)
#     inner = rect.inflate(-4, -4)
#     pygame.draw.rect(surface, enh_color, inner, 2, border_radius=2)
#     return True


def insert_rarity_tooltip(lines: List[str], colors: List[Tuple],
                          rarity: str) -> None:
    """Insert a "Rarity: <Tier>" line + colour at index 1 (after item name)."""
    if rarity == 'common':
        return
    lines.insert(1, f"Rarity: {rarity.title()}")
    colors.insert(1, get_rarity_color(rarity))


# ── inventory slot tracking ──────────────────────────────────────────
# Mirrors the enchantment pickup/place/swap pattern for rarities.

def pick_up_rarity(inv, src: str, slot: int) -> None:
    """Move rarity from *src* dict to ``held_rarity``.

    *src*: ``'hotbar'`` or ``'slots'``.
    """
    from core.item_stack import normalize_rarity
    d = inv.hotbar_rarities if src == 'hotbar' else inv.slot_rarities
    inv.held_rarity = normalize_rarity(d.pop(slot, 'common'))


def place_rarity(inv, dst: str, slot: int) -> None:
    """Move ``held_rarity`` into *dst* dict and clear held.

    *dst*: ``'hotbar'`` or ``'slots'``.
    """
    from core.item_stack import normalize_rarity
    d = inv.hotbar_rarities if dst == 'hotbar' else inv.slot_rarities
    d[slot] = normalize_rarity(inv.held_rarity)
    inv.held_rarity = 'common'


def swap_rarity(inv, target: str, slot: int) -> None:
    """Swap ``held_rarity`` with the rarity already in *target[slot]*.

    *target*: ``'hotbar'`` or ``'slots'``.
    """
    from core.item_stack import normalize_rarity
    d = inv.hotbar_rarities if target == 'hotbar' else inv.slot_rarities
    old = d.pop(slot, 'common')
    d[slot] = normalize_rarity(inv.held_rarity)
    inv.held_rarity = normalize_rarity(old)
