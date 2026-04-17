"""Day/night cycle system — tracks time, day number, flash banners."""
from data.day_night import (
    TIME_NIGHT_END, TIME_DAY_START, TIME_DAY_END, TIME_NIGHT_START,
    DAY_FLASH_DURATION, NIGHT_FLASH_DURATION,
    DAWN_FLASH_DURATION, DAWN_FLASH_TEXT,
    DUSK_FLASH_DURATION, DUSK_FLASH_TEXT,
    TIME_SPEED_NORMAL,
)


class DayNightCycle:
    def __init__(self, day_length: float = 960.0) -> None:
        self.time = TIME_DAY_START
        self.day_length = day_length
        self._speed_mult = TIME_SPEED_NORMAL
        self._time_stopped = False
        self.day_number: int = 1
        self._was_day: bool = True
        self._was_dawn: bool = False
        self._was_dusk: bool = False
        self._day_flash_timer: float = 0.0
        self._night_flash_timer: float = 0.0
        self._dawn_flash_timer: float = 0.0
        self._dusk_flash_timer: float = 0.0
        # Set when day_number increments so external systems can react
        self.day_changed: bool = False

    def update(self, dt: float) -> None:
        self.day_changed = False
        speed_mult = 0.0 if self._time_stopped else self._speed_mult
        self.time = (self.time + dt * speed_mult / self.day_length) % 1.0
        is_day_now = TIME_DAY_START <= self.time < TIME_DAY_END
        is_dawn_now = TIME_NIGHT_END <= self.time < TIME_DAY_START
        is_dusk_now = TIME_DAY_END <= self.time < TIME_NIGHT_START

        # Day start (dawn -> day transition) — increment day number
        if is_day_now and not self._was_day:
            self.day_number += 1
            self._day_flash_timer = DAY_FLASH_DURATION
            self.day_changed = True

        # Night start (dusk -> night transition)
        if not is_day_now and self._was_day and not is_dusk_now:
            self._night_flash_timer = NIGHT_FLASH_DURATION

        # Dawn start
        if is_dawn_now and not self._was_dawn and DAWN_FLASH_TEXT:
            self._dawn_flash_timer = DAWN_FLASH_DURATION

        # Dusk start
        if is_dusk_now and not self._was_dusk and DUSK_FLASH_TEXT:
            self._dusk_flash_timer = DUSK_FLASH_DURATION

        # Night start (from dusk specifically)
        if not is_dusk_now and self._was_dusk and not is_day_now and not is_dawn_now:
            self._night_flash_timer = NIGHT_FLASH_DURATION

        self._was_day = is_day_now
        self._was_dawn = is_dawn_now
        self._was_dusk = is_dusk_now
        self._day_flash_timer = max(0.0, self._day_flash_timer - dt)
        self._night_flash_timer = max(0.0, self._night_flash_timer - dt)
        self._dawn_flash_timer = max(0.0, self._dawn_flash_timer - dt)
        self._dusk_flash_timer = max(0.0, self._dusk_flash_timer - dt)

    def set_speed(self, mult: float) -> None:
        self._speed_mult = mult

    def reset_speed(self) -> None:
        self._speed_mult = TIME_SPEED_NORMAL

    def stop_time(self) -> None:
        self._time_stopped = True

    def start_time(self) -> None:
        self._time_stopped = False

    def is_time_stopped(self) -> bool:
        return self._time_stopped

    def get_darkness(self) -> float:
        t = self.time
        if TIME_DAY_START < t < TIME_DAY_END:
            return 0.0
        if t <= TIME_DAY_START:
            return 1.0 - t / TIME_DAY_START
        return (t - TIME_DAY_END) / TIME_DAY_START

    def get_period_name(self) -> str:
        t = self.time
        if t < TIME_NIGHT_END:
            return "Night"
        if t < TIME_DAY_START:
            return "Dawn"
        if t < TIME_DAY_END:
            return "Day"
        if t < TIME_NIGHT_START:
            return "Dusk"
        return "Night"

    def is_night(self) -> bool:
        t = self.time
        return t < TIME_NIGHT_END or t >= TIME_NIGHT_START

    def is_sleepable(self) -> bool:
        """True during Dusk or Night — when the player should be able to sleep."""
        t = self.time
        return t < TIME_NIGHT_END or t >= TIME_DAY_END
