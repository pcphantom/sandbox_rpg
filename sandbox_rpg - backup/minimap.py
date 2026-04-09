"""Player-centred minimap that tracks the current area."""
from __future__ import annotations

from typing import Dict, Tuple

import pygame

from constants import (SCREEN_WIDTH, TILE_SIZE, TILE_WATER, TILE_SAND,
                       TILE_GRASS, TILE_DIRT, TILE_STONE_FLOOR,
                       TILE_STONE_WALL, TILE_FOREST, BLACK, WHITE, RED,
                       CYAN, GREEN)
from world import World


TILE_COLORS: Dict[int, Tuple[int, int, int]] = {
    TILE_WATER:       (30, 80, 180),
    TILE_SAND:        (210, 190, 140),
    TILE_GRASS:       (45, 120, 50),
    TILE_DIRT:        (100, 75, 45),
    TILE_STONE_FLOOR: (110, 110, 120),
    TILE_STONE_WALL:  (55, 55, 65),
    TILE_FOREST:      (25, 80, 30),
}

# Minimap is 160 × 160 pixels, each pixel = 1 tile → shows 80-tile radius.
MAP_PX = 160
VIEW_RADIUS = MAP_PX // 2        # tiles visible in each direction


class Minimap:
    """Draws a scrolling minimap centred on the player. Unmapped / out-of-
    bounds tiles render as black."""

    def __init__(self, size: int = MAP_PX) -> None:
        self.size = size
        self.surface = pygame.Surface((size, size))

    def draw(self, screen: pygame.Surface, world: World,
             px: float, py: float,
             mob_positions: list | None = None,
             building_positions: list | None = None) -> None:
        """Redraw the minimap every frame (fast enough at 160²)."""
        self.surface.fill(BLACK)

        # Player tile position
        ptx = int(px / TILE_SIZE)
        pty = int(py / TILE_SIZE)

        half = self.size // 2

        for mx in range(self.size):
            for my in range(self.size):
                wx = ptx - half + mx
                wy = pty - half + my
                if world.in_bounds(wx, wy):
                    tile = world.get_tile(wx, wy)
                    self.surface.set_at((mx, my), TILE_COLORS.get(tile, BLACK))
                # else stays black

        # Building dots (cyan)
        if building_positions:
            for (bx, by) in building_positions:
                btx = int(bx / TILE_SIZE) - ptx + half
                bty = int(by / TILE_SIZE) - pty + half
                if 0 <= btx < self.size and 0 <= bty < self.size:
                    self.surface.set_at((btx, bty), CYAN)

        # Mob dots (red)
        if mob_positions:
            for (ex, ey) in mob_positions:
                etx = int(ex / TILE_SIZE) - ptx + half
                ety = int(ey / TILE_SIZE) - pty + half
                if 0 <= etx < self.size and 0 <= ety < self.size:
                    self.surface.set_at((etx, ety), RED)

        # Player dot (white with green outline)
        cx, cy = half, half
        pygame.draw.circle(self.surface, GREEN, (cx, cy), 3)
        pygame.draw.circle(self.surface, WHITE, (cx, cy), 2)

        # Blit to screen
        dx = SCREEN_WIDTH - self.size - 15
        dy = 50
        screen.blit(self.surface, (dx, dy))
        pygame.draw.rect(screen, (180, 180, 200),
                         (dx, dy, self.size, self.size), 2)
