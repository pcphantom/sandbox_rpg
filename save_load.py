"""Multi-slot save / load with JSON serialisation."""
import json
import os
from typing import Dict, Any, Optional

from constants import SAVE_DIR, SAVE_SLOTS


def _slot_path(slot: int) -> str:
    os.makedirs(SAVE_DIR, exist_ok=True)
    return os.path.join(SAVE_DIR, f"save_{slot}.json")


def save_game(slot: int, data: Dict[str, Any]) -> None:
    with open(_slot_path(slot), 'w') as f:
        json.dump(data, f, indent=2)


def load_game(slot: int) -> Optional[Dict[str, Any]]:
    path = _slot_path(slot)
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)


def delete_save(slot: int) -> None:
    path = _slot_path(slot)
    if os.path.exists(path):
        os.remove(path)


def slot_info(slot: int) -> Optional[Dict[str, Any]]:
    """Return a brief summary dict for a save slot, or None."""
    data = load_game(slot)
    if data is None:
        return None
    return {
        'level': data.get('level', 1),
        'kills': data.get('kills', 0),
        'day_time': data.get('day_time', 0.3),
    }


def list_slots() -> Dict[int, Optional[Dict[str, Any]]]:
    """Return info for every slot (1-based for manual, 0 for quick)."""
    return {i: slot_info(i) for i in range(SAVE_SLOTS)}
