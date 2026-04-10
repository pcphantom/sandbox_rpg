"""Multi-slot save / load with JSON serialisation."""
import json
import os
import tempfile
from typing import Dict, Any, Optional

from constants import SAVE_DIR, SAVE_SLOTS


def _slot_path(slot: int) -> str:
    os.makedirs(SAVE_DIR, exist_ok=True)
    return os.path.join(SAVE_DIR, f"save_{slot}.json")


def save_game(slot: int, data: Dict[str, Any]) -> bool:
    """Atomic save: write to temp file, fsync, then rename over target.
    Returns True on success, False on failure."""
    target = _slot_path(slot)
    try:
        fd, tmp = tempfile.mkstemp(dir=SAVE_DIR, suffix='.tmp')
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        # Atomic replace (Windows: os.replace handles overwrite)
        os.replace(tmp, target)
        return True
    except Exception:
        # Clean up temp file on failure
        try:
            os.remove(tmp)
        except OSError:
            pass
        return False


def load_game(slot: int) -> Optional[Dict[str, Any]]:
    path = _slot_path(slot)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


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
        'day_number': data.get('day_number', 1),
        'difficulty': data.get('difficulty', 0),
    }


def list_slots() -> Dict[int, Optional[Dict[str, Any]]]:
    """Return info for every slot (1-based for manual, 0 for quick)."""
    return {i: slot_info(i) for i in range(SAVE_SLOTS)}
