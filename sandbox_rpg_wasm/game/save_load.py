"""Multi-slot save / load with JSON serialisation."""
import re
from typing import Dict, Any, Optional

from core import web_storage
from core.constants import SAVE_SLOTS

# -- Save-data migration: rename old ench_ item IDs to spell_ --
_ENCH_RE = re.compile(r'^ench_(regen|protection|strength)_([123])$')


def _migrate_item_id(item_id: str) -> str:
    """Convert legacy ench_* ids to spell_* ids."""
    m = _ENCH_RE.match(item_id)
    if m:
        return f'spell_{m.group(1)}_{m.group(2)}'
    return item_id


def _migrate_save_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """In-place migration of legacy item IDs in a loaded save dict."""
    # Inventory slots
    if 'inventory' in data:
        for key, val in list(data['inventory'].items()):
            if isinstance(val, list) and len(val) >= 1:
                val[0] = _migrate_item_id(val[0])
    # Chest storage
    for chest in data.get('chests', []):
        if 'slots' in chest:
            for key, val in list(chest['slots'].items()):
                if isinstance(val, list) and len(val) >= 1:
                    val[0] = _migrate_item_id(val[0])
    return data


def save_game(slot: int, data: Dict[str, Any]) -> bool:
    """Save game data for *slot*. Returns True on success."""
    return web_storage.save_slot(slot, data)


def load_game(slot: int) -> Optional[Dict[str, Any]]:
    data = web_storage.load_slot(slot)
    if data is None:
        return None
    return _migrate_save_data(data)


def delete_save(slot: int) -> None:
    web_storage.delete_slot(slot)


def slot_info(slot: int) -> Optional[Dict[str, Any]]:
    """Return a brief summary dict for a save slot, or None."""
    data = load_game(slot)
    if data is None:
        return None
    return {
        'level': data.get('level', 1),
        'kills': data.get('kills', 0),
        'day_time': data.get('day_time', 0.3),
        'day_number': data.get('day_number', 1),
        'difficulty': data.get('difficulty', 0),
    }


def list_slots() -> Dict[int, Optional[Dict[str, Any]]]:
    """Return info for every slot (1-based for manual, 0 for quick)."""
    return {i: slot_info(i) for i in range(SAVE_SLOTS)}
