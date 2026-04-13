"""Wave system — night-time enemy wave spawning with escalating difficulty."""
from core.constants import DIFFICULTY_EASY, DIFFICULTY_MULTIPLIERS, RANGED_ENEMY_START_DAY
from data.day_events import (WAVE_SPAWN_INITIAL_INTERVAL, WAVE_SPAWN_MIN_INTERVAL,
                             WAVE_INTERVAL_REDUCTION, WAVE_SPAWN_BATCH)


class WaveSystem:
    """Manages night-time enemy wave spawning with escalating difficulty."""

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

    def update(self, dt: float, is_night: bool, day_number: int = 1) -> dict | None:
        """Returns spawn request dict or None.
        {'count': N, 'tier': T, 'ranged': bool, 'boss': bool}"""
        if is_night and not self.was_night:
            # Night just started
            self.night_count += 1
            from data.day_events import (WAVE_START_NIGHT, WAVE_BASE_COUNT,
                                          WAVE_SCALE_PER_NIGHT,
                                          WAVE_DAY_BONUS_PER_DAY)
            if self.night_count >= WAVE_START_NIGHT:
                self.wave_active = True
                self.wave_spawned = 0
                self.boss_spawned_this_wave = False
                diff = self.night_count - WAVE_START_NIGHT
                # Scale wave count with difficulty
                _, _, _, wave_mult = DIFFICULTY_MULTIPLIERS.get(
                    self.difficulty, (1.0, 1.0, 1.0, 1.0))
                base_count = WAVE_BASE_COUNT + diff * WAVE_SCALE_PER_NIGHT
                # Each day adds slightly more enemies
                day_bonus = max(0, (day_number - 1)) * WAVE_DAY_BONUS_PER_DAY
                self.wave_target = int((base_count + day_bonus) * wave_mult)
                self.current_tier = min(3, diff // 2)
                self.wave_timer = 0.0
                self.wave_spawn_interval = max(WAVE_SPAWN_MIN_INTERVAL,
                    WAVE_SPAWN_INITIAL_INTERVAL - diff * WAVE_INTERVAL_REDUCTION)
        elif not is_night and self.was_night:
            self.wave_active = False
        self.was_night = is_night

        if not self.wave_active or self.wave_spawned >= self.wave_target:
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
