"""Camera with smooth following and screen-shake."""
import random

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT
from utils import clamp, lerp


class Camera:
    def __init__(self, w: int = SCREEN_WIDTH, h: int = SCREEN_HEIGHT) -> None:
        self.x = 0.0; self.y = 0.0
        self.width = w; self.height = h
        self.target_x = 0.0; self.target_y = 0.0
        self.shake_amt = 0.0; self.shake_timer = 0.0

    def follow(self, tx: float, ty: float) -> None:
        self.target_x = tx - self.width / 2
        self.target_y = ty - self.height / 2

    def shake(self, amount: float, duration: float) -> None:
        self.shake_amt = amount; self.shake_timer = duration

    def update(self, dt: float) -> None:
        self.x = lerp(self.x, self.target_x, 0.12)
        self.y = lerp(self.y, self.target_y, 0.12)
        self.x = clamp(self.x, 0, WORLD_WIDTH * TILE_SIZE - self.width)
        self.y = clamp(self.y, 0, WORLD_HEIGHT * TILE_SIZE - self.height)
        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.x += random.uniform(-self.shake_amt, self.shake_amt)
            self.y += random.uniform(-self.shake_amt, self.shake_amt)
