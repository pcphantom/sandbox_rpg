"""Shared item presentation helpers for UI text and rarity styling.

Canonical visible label:
    <effect prefix> <base item name><upgrade suffix>

Rarity never participates in the item label text. It only affects display
colour, borders, and tooltip metadata.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from core.enhancement import get_base_item_id, get_enhancement_level
from core.item_stack import normalize_rarity
from data.items import ITEM_DATA
from data.quality import get_item_color, get_rarity_color
from enchantments.effects import get_enchant_display_prefix


def get_base_item_display_name(item_id: str) -> str:
    """Return the non-upgraded base display name for an item id."""
    base_id = get_base_item_id(item_id)
    if base_id in ITEM_DATA:
        return ITEM_DATA[base_id][0]
    if item_id in ITEM_DATA:
        name = ITEM_DATA[item_id][0]
        level = get_enhancement_level(item_id)
        suffix = f" +{level}"
        if level > 0 and name.endswith(suffix):
            return name[:-len(suffix)]
        return name
    return item_id


def get_item_upgrade_suffix(item_id: str) -> str:
    """Return the +N suffix for an upgraded item id, or an empty string."""
    level = get_enhancement_level(item_id)
    if level <= 0:
        return ''
    return f' +{level}'


def get_item_display_label(item_id: str,
                           enchant: Optional[Dict[str, Any]] = None,
                           count: int = 1,
                           include_count: bool = False) -> str:
    """Return the canonical display label for an item.

    The label uses the effect prefix from the enchant overlay and the upgrade
    suffix from the item id. Rarity is intentionally excluded from the label.
    """
    label = get_base_item_display_name(item_id)
    prefix = get_enchant_display_prefix(enchant)
    if prefix:
        label = f'{prefix} {label}'
    label = f'{label}{get_item_upgrade_suffix(item_id)}'
    if include_count and count > 1:
        label = f'{label} x{count}'
    return label


def build_item_presentation(item_id: str,
                            rarity: str = 'common',
                            enchant: Optional[Dict[str, Any]] = None,
                            count: int = 1,
                            include_count: bool = False) -> Dict[str, Any]:
    """Return canonical label plus rarity-driven colour metadata."""
    normalized_rarity = normalize_rarity(rarity)
    border_color = None
    if normalized_rarity != 'common':
        border_color = get_rarity_color(normalized_rarity)
    return {
        'label': get_item_display_label(item_id, enchant, count,
                                        include_count=include_count),
        'color': get_item_color(item_id, normalized_rarity),
        'border_color': border_color,
        'rarity': normalized_rarity,
    }