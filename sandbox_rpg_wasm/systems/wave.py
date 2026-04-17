"""Wave system — night-time enemy wave spawning with escalating difficulty."""
from core.constants import DIFFICULTY_EASY, DIFFICULTY_MULTIPLIERS, RANGED_ENEMY_START_DAY
from data.day_events import (WAVE_SPAWN_INITIAL_INTERVAL, WAVE_SPAWN_MIN_INTERVAL,
                             WAVE_INTERVAL_REDUCTION, WAVE_SPAWN_BATCH,
                             NIGHT_WAVE_COUNT, NIGHT_WAVE_SPACING_HOURS)
from game_controller import GAME_HOUR_IN_SECONDS


class WaveSystem:
    """Manages night-time enemy wave spawning with escalating difficulty.

    On higher difficulties, multiple waves spawn per night, spaced apart
    by game-hours defined in NIGHT_WAVE_SPACING_HOURS.
    """

    def __init__(self, difficulty: int = DIFFICULTY_EASY) -> None:
        self.night_count: int = 0
        self.was_night: bool = False
        self.wave_active: bool = False
        self.wave_spawned: int = 0
        self.wave_target: int = 0
        self.wave_timer: float = 0.0
        self.wave_spawn_interval: float = WAVE_SPAWN_INITIAL_INTERVAL
        self.current_tier: int = 0
        self.difficulty: int = difficulty
        self.boss_spawned_this_wave: bool = False
        # Multi-wave tracking
        self._waves_remaining: int = 0
        self._wave_gap_timer: float = 0.0
        self._wave_gap_target: float = 0.0
        self._wave_base_count: int = 0
        self._wave_diff: int = 0
        self._wave_day_number: int = 1

    def update(self, dt: float, is_night: bool, day_number: int = 1) -> dict | None:
        """Returns spawn request dict or None.
        {'count': N, 'tier': T, 'ranged': bool, 'boss': bool}"""
        if is_night and not self.was_night:
            # Night just started
            self.night_count += 1
            self._wave_day_number = day_number
            from data.day_events import (WAVE_START_NIGHT, WAVE_BASE_COUNT,
                                          WAVE_SCALE_PER_NIGHT,
                                          WAVE_DAY_BONUS_PER_DAY)
            if self.night_count >= WAVE_START_NIGHT:
                self._wave_diff = self.night_count - WAVE_START_NIGHT
                # How many separate waves this night?
                total_waves = NIGHT_WAVE_COUNT.get(self.difficulty, 1)
                self._waves_remaining = total_waves
                # Game-hours between waves → real seconds
                spacing_hours = NIGHT_WAVE_SPACING_HOURS.get(self.difficulty, 0.0)
                # Convert game-hours to real seconds
                self._wave_gap_target = spacing_hours * GAME_HOUR_IN_SECONDS
                self._wave_gap_timer = 0.0
                self._start_wave(WAVE_BASE_COUNT, WAVE_SCALE_PER_NIGHT,
                                 WAVE_DAY_BONUS_PER_DAY, day_number)
        elif not is_night and self.was_night:
            self.wave_active = False
            self._waves_remaining = 0
        self.was_night = is_night

        if not self.wave_active or self.wave_spawned >= self.wave_target:
            # Check for next wave in multi-wave sequence
            if self._waves_remaining > 0 and is_night:
                self._wave_gap_timer += dt
                if self._wave_gap_timer >= self._wave_gap_target:
                    from data.day_events import (WAVE_BASE_COUNT,
                                                  WAVE_SCALE_PER_NIGHT,
                                                  WAVE_DAY_BONUS_PER_DAY)
                    self._start_wave(WAVE_BASE_COUNT, WAVE_SCALE_PER_NIGHT,
                                     WAVE_DAY_BONUS_PER_DAY,
                                     self._wave_day_number)
            return None

        self.wave_timer += dt
        if self.wave_timer >= self.wave_spawn_interval:
            self.wave_timer = 0.0
            batch = min(WAVE_SPAWN_BATCH, self.wave_target - self.wave_spawned)
            self.wave_spawned += batch
            # Determine if ranged enemies should be included
            include_ranged = day_number > RANGED_ENEMY_START_DAY
            # Boss spawn: one per wave, after tier 2+
            include_boss = (not self.boss_spawned_this_wave
                            and self.current_tier >= 2
                            and self.wave_spawned >= self.wave_target // 2)
            if include_boss:
                self.boss_spawned_this_wave = True
            return {'count': batch, 'tier': self.current_tier,
                    'ranged': include_ranged, 'boss': include_boss}
        return None

    def _start_wave(self, base_count: int, scale_per_night: int,
                    day_bonus_per_day: int, day_number: int) -> None:
        """Initialize a single wave within the multi-wave night sequence."""
        self._waves_remaining -= 1
        self._wave_gap_timer = 0.0
        self.wave_active = True
        self.wave_spawned = 0
        self.boss_spawned_this_wave = False
        _, _, _, wave_mult = DIFFICULTY_MULTIPLIERS.get(
            self.difficulty, (1.0, 1.0, 1.0, 1.0))
        wave_count = base_count + self._wave_diff * scale_per_night
        day_bonus = max(0, (day_number - 1)) * day_bonus_per_day
        self.wave_target = int((wave_count + day_bonus) * wave_mult)
        self.current_tier = min(4, self._wave_diff // 2)
        self.wave_timer = 0.0
        self.wave_spawn_interval = max(WAVE_SPAWN_MIN_INTERVAL,
            WAVE_SPAWN_INITIAL_INTERVAL - self._wave_diff * WAVE_INTERVAL_REDUCTION)
