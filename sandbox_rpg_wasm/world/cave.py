"""Cave generation and management.

Each cave is an independent World instance generated from the main game seed
plus a per-cave offset.  The overworld gets TILE_CAVE_ENTRANCE markers placed
during generation; walking over one teleports the player into the cave's
interior.  A matching exit tile inside the cave returns the player to the
overworld at the entrance coordinates.
"""
import math
import random
from typing import List, Tuple, Optional

from core.constants import (
    TILE_STONE_WALL, TILE_CAVE_FLOOR, TILE_CAVE_ENTRANCE,
    TILE_SIZE,
    CAVE_COUNT, CAVE_WIDTH, CAVE_HEIGHT,
    CAVE_WALL_DENSITY, CAVE_SMOOTH_PASSES,
    CAVE_ENTRANCE_MIN_DIST,
    WORLD_WIDTH, WORLD_HEIGHT,
    TILE_WATER, TILE_SAND, TILE_GRASS, TILE_DIRT,
    TILE_STONE_FLOOR, TILE_FOREST,
)
from world.generator import World


# ---------------------------------------------------------------------------
# Cave interior generation
# ---------------------------------------------------------------------------

def generate_cave_interior(seed: int, cave_index: int) -> World:
    """Create a small cave world using cellular automata.

    Returns a World where walkable areas are TILE_CAVE_FLOOR and walls are
    TILE_STONE_WALL.  The exit tile (TILE_CAVE_ENTRANCE) is placed near the
    centre of the southern edge.
    """
    rng = random.Random(seed + 50000 + cave_index * 7919)
    w, h = CAVE_WIDTH, CAVE_HEIGHT
    cave = World(w, h)

    # -- Cellular automata --------------------------------------------------
    grid: List[List[int]] = [
        [1 if rng.random() < CAVE_WALL_DENSITY else 0 for _ in range(h)]
        for _ in range(w)
    ]
    # Force border to be walls
    for x in range(w):
        grid[x][0] = 1
        grid[x][h - 1] = 1
    for y in range(h):
        grid[0][y] = 1
        grid[w - 1][y] = 1

    for _ in range(CAVE_SMOOTH_PASSES):
        ng: List[List[int]] = [[0] * h for _ in range(w)]
        for x in range(w):
            for y in range(h):
                walls = sum(
                    1 for dx in range(-1, 2) for dy in range(-1, 2)
                    if (dx or dy) and (
                        not (0 <= x + dx < w and 0 <= y + dy < h)
                        or grid[x + dx][y + dy] == 1
                    )
                )
                ng[x][y] = 1 if walls >= 5 else (0 if walls <= 3 else grid[x][y])
        grid = ng

    # Write to world
    for x in range(w):
        for y in range(h):
            cave.set_tile(x, y, TILE_STONE_WALL if grid[x][y] == 1 else TILE_CAVE_FLOOR)

    # -- Carve exit near bottom-centre --------------------------------------
    ex, ey = w // 2, h - 2
    _carve_area(cave, ex, ey, 2)
    cave.set_tile(ex, ey, TILE_CAVE_ENTRANCE)

    # -- Carve boss arena near top-centre -----------------------------------
    bx, by = w // 2, 5
    _carve_area(cave, bx, by, 4)

    # -- Ensure connectivity from exit to boss arena with a rough corridor --
    _carve_corridor(cave, ex, ey, bx, by, rng)

    return cave


def _carve_area(cave: World, cx: int, cy: int, radius: int) -> None:
    """Clear a circular area of floor tiles around (cx, cy)."""
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx * dx + dy * dy <= radius * radius:
                nx, ny = cx + dx, cy + dy
                if cave.in_bounds(nx, ny):
                    tile = cave.get_tile(nx, ny)
                    if tile == TILE_STONE_WALL:
                        cave.set_tile(nx, ny, TILE_CAVE_FLOOR)


def _carve_corridor(cave: World, x0: int, y0: int,
                    x1: int, y1: int, rng: random.Random) -> None:
    """Carve a drunkard-walk corridor between two points."""
    x, y = x0, y0
    while x != x1 or y != y1:
        if rng.random() < 0.5:
            x += 1 if x < x1 else (-1 if x > x1 else 0)
        else:
            y += 1 if y < y1 else (-1 if y > y1 else 0)
        # Widen corridor slightly
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                if cave.in_bounds(nx, ny) and cave.get_tile(nx, ny) == TILE_STONE_WALL:
                    cave.set_tile(nx, ny, TILE_CAVE_FLOOR)


# ---------------------------------------------------------------------------
# Entrance placement on the overworld
# ---------------------------------------------------------------------------

def find_cave_entrances(seed: int, world: World,
                        count: int = CAVE_COUNT) -> List[Tuple[int, int]]:
    """Deterministically pick *count* cave entrance locations on the overworld.

    Entrances are placed on walkable, non-water/sand tiles that are reasonably
    far from each other and from the world centre (where the player spawns).
    """
    rng = random.Random(seed + 77777)
    entrances: List[Tuple[int, int]] = []
    min_dist_tiles = CAVE_ENTRANCE_MIN_DIST / TILE_SIZE
    cx, cy = world.width // 2, world.height // 2
    # Minimum distance from centre so player doesn't spawn on top of one
    min_centre = 20

    attempts = 0
    while len(entrances) < count and attempts < 5000:
        attempts += 1
        x = rng.randint(8, world.width - 9)
        y = rng.randint(8, world.height - 9)
        tile = world.get_tile(x, y)
        if tile in (TILE_WATER, TILE_SAND, TILE_STONE_WALL):
            continue
        # Not too close to centre
        if math.hypot(x - cx, y - cy) < min_centre:
            continue
        # Not too close to other entrances
        too_close = False
        for ex, ey in entrances:
            if math.hypot(x - ex, y - ey) < min_dist_tiles:
                too_close = True
                break
        if too_close:
            continue
        entrances.append((x, y))

    return entrances


def place_entrances_on_world(world: World,
                             entrances: List[Tuple[int, int]]) -> None:
    """Stamp TILE_CAVE_ENTRANCE onto the overworld at each entrance pos."""
    for x, y in entrances:
        world.set_tile(x, y, TILE_CAVE_ENTRANCE)
        # Clear a small walkable area around entrance
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if world.in_bounds(nx, ny) and world.is_solid(nx, ny):
                    world.set_tile(nx, ny, TILE_GRASS)


# ---------------------------------------------------------------------------
# Cave data container
# ---------------------------------------------------------------------------

class CaveData:
    """Holds all generated cave state for one map."""

    def __init__(self, seed: int, world: World) -> None:
        self.seed = seed
        self.entrances: List[Tuple[int, int]] = find_cave_entrances(seed, world)
        self.interiors: List[World] = []
        self.boss_alive: List[bool] = []
        self.chest_looted: List[bool] = []
        for i in range(len(self.entrances)):
            self.interiors.append(generate_cave_interior(seed, i))
            self.boss_alive.append(True)
            self.chest_looted.append(False)
        place_entrances_on_world(world, self.entrances)

    @property
    def count(self) -> int:
        return len(self.entrances)

    def get_entrance_pixel(self, index: int) -> Tuple[float, float]:
        """Return the overworld pixel position of cave entrance *index*."""
        x, y = self.entrances[index]
        return x * TILE_SIZE + TILE_SIZE // 2, y * TILE_SIZE + TILE_SIZE // 2

    def regenerate(self, day_number: int) -> None:
        """Rebuild all cave interiors for a new day.

        Uses day_number as part of the seed so each day produces different
        cave layouts, mobs, and resources.  Resets boss_alive and chest_looted
        so bosses and chests reappear.
        """
        self.interiors.clear()
        self.boss_alive.clear()
        self.chest_looted.clear()
        for i in range(len(self.entrances)):
            day_seed = self.seed + day_number * 99991
            self.interiors.append(generate_cave_interior(day_seed, i))
            self.boss_alive.append(True)
            self.chest_looted.append(False)

    def get_exit_pixel(self, index: int) -> Tuple[float, float]:
        """Return the pixel position of the exit tile inside cave *index*."""
        cave = self.interiors[index]
        ex, ey = cave.width // 2, cave.height - 2
        return ex * TILE_SIZE + TILE_SIZE // 2, ey * TILE_SIZE + TILE_SIZE // 2

    def get_boss_spawn(self, index: int) -> Tuple[float, float]:
        """Pixel position of the boss arena centre in cave *index*."""
        cave = self.interiors[index]
        bx, by = cave.width // 2, 5
        return bx * TILE_SIZE + TILE_SIZE // 2, by * TILE_SIZE + TILE_SIZE // 2

    def entrance_at(self, px: float, py: float,
                    threshold: float = 24.0) -> Optional[int]:
        """Return cave index if pixel (px, py) is near an overworld entrance,
        else None."""
        for i, (ex, ey) in enumerate(self.entrances):
            epx = ex * TILE_SIZE + TILE_SIZE // 2
            epy = ey * TILE_SIZE + TILE_SIZE // 2
            if math.hypot(px - epx, py - epy) < threshold:
                return i
        return None

    def at_exit(self, cave_index: int, px: float, py: float,
                threshold: float = 24.0) -> bool:
        """Return True if pixel (px, py) is near the exit tile in the cave."""
        exp, eyp = self.get_exit_pixel(cave_index)
        return math.hypot(px - exp, py - eyp) < threshold
