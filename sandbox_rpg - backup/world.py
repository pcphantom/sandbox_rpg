"""World grid and procedural generation."""
import random
from typing import List

from constants import (TILE_WATER, TILE_SAND, TILE_GRASS, TILE_DIRT,
                       TILE_STONE_FLOOR, TILE_STONE_WALL, TILE_FOREST,
                       TILE_SIZE, ELEVATION_SCALE, MOISTURE_SCALE,
                       MOISTURE_OFFSET, ELEVATION_OCTAVES, MOISTURE_OCTAVES)
from utils import fbm_noise


class World:
    def __init__(self, width: int, height: int) -> None:
        self.width = width; self.height = height
        self.tiles: List[List[int]] = [[TILE_GRASS] * height for _ in range(width)]
        self.biome_noise: List[List[float]] = [[0.0] * height for _ in range(width)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> int:
        return self.tiles[x][y] if self.in_bounds(x, y) else TILE_STONE_WALL

    def set_tile(self, x: int, y: int, tile: int) -> None:
        if self.in_bounds(x, y):
            self.tiles[x][y] = tile

    def is_solid(self, x: int, y: int) -> bool:
        t = self.get_tile(x, y)
        return t == TILE_WATER or t == TILE_STONE_WALL


class WorldGenerator:
    """Two-pass generator: elevation + moisture noise → biome, then caves."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    def generate(self, w: int, h: int) -> World:
        world = World(w, h)

        # Two-channel noise for richer biomes
        for x in range(w):
            for y in range(h):
                elev = fbm_noise(x * ELEVATION_SCALE, y * ELEVATION_SCALE,
                                 self.seed, ELEVATION_OCTAVES)
                moist = fbm_noise(x * MOISTURE_SCALE + MOISTURE_OFFSET,
                                  y * MOISTURE_SCALE + MOISTURE_OFFSET,
                                  self.seed + 777, MOISTURE_OCTAVES)
                world.biome_noise[x][y] = elev

                if elev < 0.28:
                    world.set_tile(x, y, TILE_WATER)
                elif elev < 0.34:
                    world.set_tile(x, y, TILE_SAND)
                elif elev < 0.68:
                    if moist > 0.55:
                        world.set_tile(x, y, TILE_FOREST)
                    elif moist < 0.35:
                        world.set_tile(x, y, TILE_DIRT)
                    else:
                        world.set_tile(x, y, TILE_GRASS)
                elif elev < 0.80:
                    if moist > 0.5:
                        world.set_tile(x, y, TILE_FOREST)
                    else:
                        world.set_tile(x, y, TILE_DIRT)
                else:
                    world.set_tile(x, y, TILE_STONE_FLOOR)

        # Cellular-automata caves in high-elevation regions
        grid = self._caves(w, h)
        for x in range(w):
            for y in range(h):
                if grid[x][y] == 1 and world.biome_noise[x][y] > 0.55:
                    if world.get_tile(x, y) in (TILE_GRASS, TILE_DIRT,
                                                 TILE_STONE_FLOOR):
                        world.set_tile(x, y, TILE_STONE_WALL)

        return world

    def _caves(self, w: int, h: int) -> List[List[int]]:
        g: List[List[int]] = [
            [1 if random.random() < 0.45 else 0 for _ in range(h)]
            for _ in range(w)
        ]
        for _ in range(4):
            ng: List[List[int]] = [[0] * h for _ in range(w)]
            for x in range(w):
                for y in range(h):
                    walls = sum(
                        1 for dx in range(-1, 2) for dy in range(-1, 2)
                        if (dx or dy) and (
                            not (0 <= x + dx < w and 0 <= y + dy < h)
                            or g[x + dx][y + dy] == 1
                        )
                    )
                    ng[x][y] = (1 if walls >= 5
                                else (0 if walls <= 3 else g[x][y]))
            g = ng
        return g

    @staticmethod
    def find_spawn(world: World) -> tuple:
        """Find a walkable tile near world centre for player spawn."""
        cx, cy = world.width // 2, world.height // 2
        for r in range(0, max(world.width, world.height)):
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    tx, ty = cx + dx, cy + dy
                    if world.in_bounds(tx, ty) and not world.is_solid(tx, ty):
                        return tx * TILE_SIZE + TILE_SIZE // 2, ty * TILE_SIZE + TILE_SIZE // 2
        return cx * TILE_SIZE, cy * TILE_SIZE
