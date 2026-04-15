"""Spatial hash grid for fast proximity queries.

Divides the world into a grid of fixed-size cells.  Each entity occupies
one or more cells based on its bounding box.  Proximity queries only need
to check entities in nearby cells instead of iterating every entity.

A module-level singleton ``spatial_hash`` is provided for global access.
"""
from __future__ import annotations

from typing import Dict, Set, Tuple, List

# Default cell size in pixels — 128 px = 4 tiles.
SPATIAL_CELL_SIZE: int = 128


class SpatialHash:
    """Grid-based spatial index mapping entity IDs to cells."""

    __slots__ = ('cell_size', '_cells', '_entity_cells')

    def __init__(self, cell_size: int = SPATIAL_CELL_SIZE) -> None:
        self.cell_size: int = cell_size
        # cell (cx, cy) -> set of entity ids
        self._cells: Dict[Tuple[int, int], Set[int]] = {}
        # eid -> set of cells it currently occupies (for O(1) removal)
        self._entity_cells: Dict[int, Set[Tuple[int, int]]] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _cell_keys(self, x: float, y: float,
                   w: float = 0, h: float = 0) -> Set[Tuple[int, int]]:
        """Return the set of grid cells covered by the AABB (x, y, w, h)."""
        cs = self.cell_size
        min_cx = int(x) // cs
        min_cy = int(y) // cs
        max_cx = int(x + w) // cs if w > 0 else min_cx
        max_cy = int(y + h) // cs if h > 0 else min_cy
        keys: Set[Tuple[int, int]] = set()
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                keys.add((cx, cy))
        return keys

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, eid: int, x: float, y: float,
               w: float = 0, h: float = 0) -> None:
        """Insert an entity into the spatial hash.

        If the entity already exists it will be removed first.
        """
        if eid in self._entity_cells:
            self.remove(eid)
        keys = self._cell_keys(x, y, w, h)
        self._entity_cells[eid] = keys
        for k in keys:
            try:
                self._cells[k].add(eid)
            except KeyError:
                self._cells[k] = {eid}

    def remove(self, eid: int) -> None:
        """Remove an entity from the spatial hash."""
        keys = self._entity_cells.pop(eid, None)
        if keys is None:
            return
        for k in keys:
            bucket = self._cells.get(k)
            if bucket is not None:
                bucket.discard(eid)
                if not bucket:
                    del self._cells[k]

    def update(self, eid: int, x: float, y: float,
               w: float = 0, h: float = 0) -> None:
        """Update an entity's position.  Skips re-insertion if cells unchanged."""
        new_keys = self._cell_keys(x, y, w, h)
        old_keys = self._entity_cells.get(eid)
        if old_keys == new_keys:
            return  # Same cells — nothing to do
        # Remove from old cells
        if old_keys is not None:
            for k in old_keys:
                bucket = self._cells.get(k)
                if bucket is not None:
                    bucket.discard(eid)
                    if not bucket:
                        del self._cells[k]
        # Insert into new cells
        self._entity_cells[eid] = new_keys
        for k in new_keys:
            try:
                self._cells[k].add(eid)
            except KeyError:
                self._cells[k] = {eid}

    def query_rect(self, x: float, y: float,
                   w: float, h: float) -> Set[int]:
        """Return all entity ids whose cells overlap the given rectangle."""
        result: Set[int] = set()
        for k in self._cell_keys(x, y, w, h):
            bucket = self._cells.get(k)
            if bucket:
                result.update(bucket)
        return result

    def query_radius(self, cx: float, cy: float,
                     radius: float) -> Set[int]:
        """Return all entity ids whose cells are within *radius* of (cx, cy).

        This is a broadphase — callers should do a precise distance check
        on the returned set.
        """
        return self.query_rect(
            cx - radius, cy - radius, radius * 2, radius * 2)

    def clear(self) -> None:
        """Remove all entries."""
        self._cells.clear()
        self._entity_cells.clear()


# Module-level singleton — imported by systems and game modules.
spatial_hash = SpatialHash()
