"""Platform-aware storage shim for desktop (filesystem) and browser (localStorage).

Desktop uses standard file I/O; browser (emscripten/WASM) uses JavaScript localStorage.
"""
import sys
import json
import os

_IS_WEB = sys.platform == "emscripten"

# ---- Save slots ----


def save_slot(slot: int, data: dict) -> bool:
    """Persist save data for *slot*. Returns True on success."""
    try:
        if _IS_WEB:
            import js
            js.localStorage.setItem(f"save_{slot}", json.dumps(data))
        else:
            from core.constants import SAVE_DIR
            os.makedirs(SAVE_DIR, exist_ok=True)
            path = os.path.join(SAVE_DIR, f"save_{slot}.json")
            with open(path, 'w') as f:
                json.dump(data, f)
        return True
    except Exception:
        return False


def load_slot(slot: int) -> dict | None:
    """Load save data for *slot*, or ``None`` if missing / corrupt."""
    try:
        if _IS_WEB:
            import js
            raw = js.localStorage.getItem(f"save_{slot}")
            return json.loads(raw) if raw else None
        else:
            from core.constants import SAVE_DIR
            path = os.path.join(SAVE_DIR, f"save_{slot}.json")
            if not os.path.exists(path):
                return None
            with open(path, 'r') as f:
                return json.load(f)
    except Exception:
        return None


def delete_slot(slot: int) -> None:
    """Remove save data for *slot*."""
    try:
        if _IS_WEB:
            import js
            js.localStorage.removeItem(f"save_{slot}")
        else:
            from core.constants import SAVE_DIR
            path = os.path.join(SAVE_DIR, f"save_{slot}.json")
            if os.path.exists(path):
                os.remove(path)
    except Exception:
        pass


def slot_exists(slot: int) -> bool:
    """Return True if *slot* has saved data."""
    try:
        if _IS_WEB:
            import js
            return js.localStorage.getItem(f"save_{slot}") is not None
        else:
            from core.constants import SAVE_DIR
            return os.path.exists(os.path.join(SAVE_DIR, f"save_{slot}.json"))
    except Exception:
        return False


# ---- Settings ----


def save_settings(data: dict) -> None:
    """Persist settings dict."""
    try:
        if _IS_WEB:
            import js
            js.localStorage.setItem("settings", json.dumps(data))
        else:
            from core.settings import SETTINGS_PATH
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(data, f, indent=2)
    except Exception:
        pass


def load_settings() -> dict | None:
    """Load settings dict, or ``None`` if not yet saved."""
    try:
        if _IS_WEB:
            import js
            raw = js.localStorage.getItem("settings")
            return json.loads(raw) if raw else None
        else:
            from core.settings import SETTINGS_PATH
            if not os.path.exists(SETTINGS_PATH):
                return None
            with open(SETTINGS_PATH, 'r') as f:
                return json.load(f)
    except Exception:
        return None
