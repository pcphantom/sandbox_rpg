"""Persistent game settings — display mode, resolution, difficulty."""
import json
import os
from typing import Dict, Any

from constants import SCREEN_WIDTH, SCREEN_HEIGHT

SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "settings.json")

# Internal render resolution (all game logic uses this)
INTERNAL_WIDTH: int = SCREEN_WIDTH
INTERNAL_HEIGHT: int = SCREEN_HEIGHT

# Display mode constants
DISPLAY_WINDOWED: int = 0
DISPLAY_FULLSCREEN: int = 1
DISPLAY_BORDERLESS: int = 2

DISPLAY_MODE_NAMES = {
    DISPLAY_WINDOWED: "Windowed",
    DISPLAY_FULLSCREEN: "Fullscreen",
    DISPLAY_BORDERLESS: "Borderless Windowed",
}

# Common resolution presets (width, height)
RESOLUTION_PRESETS = [
    (1280, 720),
    (1366, 768),
    (1600, 900),
    (1920, 1080),
    (2560, 1440),
]

DEFAULTS: Dict[str, Any] = {
    'display_mode': DISPLAY_WINDOWED,
    'resolution_w': SCREEN_WIDTH,
    'resolution_h': SCREEN_HEIGHT,
    'difficulty': 0,
    'music_enabled': True,
    'music_volume': 0.6,
}


def load_settings() -> Dict[str, Any]:
    """Load settings from disk, falling back to defaults."""
    settings = dict(DEFAULTS)
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r') as f:
                saved = json.load(f)
            settings.update(saved)
        except (json.JSONDecodeError, IOError):
            pass
    return settings


def save_settings(settings: Dict[str, Any]) -> None:
    """Persist settings to disk."""
    try:
        with open(SETTINGS_PATH, 'w') as f:
            json.dump(settings, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
    except OSError:
        pass
