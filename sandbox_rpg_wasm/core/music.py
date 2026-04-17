"""Music manager — day/night tracks with crossfade transitions."""
import os
import pygame
from game_controller import CROSSFADE_MS

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOUNDS_DIR = os.path.join(_PROJECT_ROOT, "sounds")
DAY_TRACK = os.path.join(SOUNDS_DIR, "little town - orchestral midi.ogg")
NIGHT_TRACK = os.path.join(SOUNDS_DIR, "Night of the Streets.ogg")


class MusicManager:
    def __init__(self, settings: dict) -> None:
        self.enabled: bool = settings.get('music_enabled', True)
        self.volume: float = settings.get('music_volume', 0.6)
        self._was_night: bool = False
        self._current_track: str = ''
        self._fading_out: bool = False
        self._pending_track: str = ''
        pygame.mixer.music.set_volume(self.volume)

    def start(self, is_night: bool) -> None:
        """Begin playing the appropriate track for current time of day."""
        self._was_night = is_night
        if self.enabled:
            track = NIGHT_TRACK if is_night else DAY_TRACK
            self._play(track)

    def update(self, is_night: bool) -> None:
        """Detect day/night transitions and crossfade."""
        # Handle pending track after fadeout completes
        if self._fading_out and not pygame.mixer.music.get_busy():
            self._fading_out = False
            if self._pending_track:
                self._play(self._pending_track)
                self._pending_track = ''

        if not self.enabled:
            return

        if is_night != self._was_night:
            self._was_night = is_night
            track = NIGHT_TRACK if is_night else DAY_TRACK
            self._crossfade(track)

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if enabled:
            track = NIGHT_TRACK if self._was_night else DAY_TRACK
            self._play(track)
        else:
            pygame.mixer.music.stop()
            self._current_track = ''
            self._fading_out = False
            self._pending_track = ''

    def set_volume(self, volume: float) -> None:
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def _play(self, track: str) -> None:
        if not os.path.exists(track):
            return
        try:
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)
            self._current_track = track
        except pygame.error:
            pass

    def _crossfade(self, new_track: str) -> None:
        if self._current_track:
            pygame.mixer.music.fadeout(CROSSFADE_MS)
            self._fading_out = True
            self._pending_track = new_track
        else:
            self._play(new_track)
