"""Player-centred minimap that tracks the current area."""
from __future__ import annotations

from typing import Dict, Tuple

import pygame

from core.constants import (SCREEN_WIDTH, TILE_SIZE, TILE_WATER, TILE_SAND,
                            TILE_GRASS, TILE_DIRT, TILE_STONE_FLOOR,
                            TILE_STONE_WALL, TILE_FOREST, TILE_CAVE_FLOOR,
                            TILE_CAVE_ENTRANCE, BLACK, WHITE, RED,
                            CYAN, GREEN,
                            MINIMAP_COLOR_WATER, MINIMAP_COLOR_SAND,
                            MINIMAP_COLOR_GRASS, MINIMAP_COLOR_DIRT,
                            MINIMAP_COLOR_STONE_FLOOR, MINIMAP_COLOR_STONE_WALL,
                            MINIMAP_COLOR_FOREST, MINIMAP_COLOR_CAVE_FLOOR,
                            MINIMAP_COLOR_CAVE_ENTRANCE, MINIMAP_COLOR_PLAYER,
                            MINIMAP_SIZE_PX)
from world.generator import World


TILE_COLORS: Dict[int, Tuple[int, int, int]] = {
    TILE_WATER:         MINIMAP_COLOR_WATER,
    TILE_SAND:          MINIMAP_COLOR_SAND,
    TILE_GRASS:         MINIMAP_COLOR_GRASS,
    TILE_DIRT:          MINIMAP_COLOR_DIRT,
    TILE_STONE_FLOOR:   MINIMAP_COLOR_STONE_FLOOR,
    TILE_STONE_WALL:    MINIMAP_COLOR_STONE_WALL,
    TILE_FOREST:        MINIMAP_COLOR_FOREST,
    TILE_CAVE_FLOOR:    MINIMAP_COLOR_CAVE_FLOOR,
    TILE_CAVE_ENTRANCE: MINIMAP_COLOR_CAVE_ENTRANCE,
}

# Minimap is MINIMAP_SIZE_PX × MINIMAP_SIZE_PX pixels, each pixel = 1 tile.
MAP_PX = MINIMAP_SIZE_PX
VIEW_RADIUS = 20


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
        pygame.draw.rect(screen, MINIMAP_COLOR_CAVE_ENTRANCE,
                         (dx, dy, self.size, self.size), 2)
