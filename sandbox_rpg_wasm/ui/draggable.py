"""DraggableWindow — reusable base for all UI panels.

Provides close button (X), drag-to-move, and resize-with-aspect-ratio
for every UI window in the game.  Individual panels embed a DraggableWindow
and delegate hit-testing / drawing of the chrome (title bar, close btn,
resize handle) to it.

Usage:
    dw = DraggableWindow(pw, ph, title="Inventory")
    # In draw():
    dw.draw_chrome(surface)
    # In handle_event():
    if dw.handle_event(event):
        if dw.close_requested:
            ... close the panel ...
        return True
"""
from __future__ import annotations

import pygame

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, RED, GRAY,
    UI_BORDER_PANEL,
)

# Title-bar height and close button sizing
TITLE_BAR_H: int = 22
CLOSE_BTN_SIZE: int = 18
CLOSE_BTN_MARGIN: int = 3
RESIZE_HANDLE_SIZE: int = 10
MIN_SCALE: float = 0.5
MAX_SCALE: float = 2.0


class DraggableWindow:
    """Manages position, drag, close-button and resize for a UI panel."""

    def __init__(self, base_w: int, base_h: int, title: str = "",
                 start_x: int | None = None, start_y: int | None = None) -> None:
        self.base_w = base_w
        self.base_h = base_h
        self.title = title
        self.scale = 1.0

        # Current position (top-left of the full window including title bar)
        if start_x is not None and start_y is not None:
            self.x = start_x
            self.y = start_y
        else:
            self.x = (SCREEN_WIDTH - base_w) // 2
            self.y = (SCREEN_HEIGHT - base_h - TITLE_BAR_H) // 2

        # Drag state
        self._dragging = False
        self._drag_ox = 0
        self._drag_oy = 0

        # Resize state
        self._resizing = False
        self._resize_ox = 0
        self._resize_oy = 0
        self._resize_start_scale = 1.0

        # Close signal — checked by the owning panel after handle_event
        self.close_requested = False

        self._font = pygame.font.SysFont('consolas, monospace', 13, bold=True)

    # ------------------------------------------------------------------
    #  Computed rectangles
    # ------------------------------------------------------------------

    @property
    def w(self) -> int:
        return int(self.base_w * self.scale)

    @property
    def h(self) -> int:
        return int(self.base_h * self.scale)

    @property
    def total_h(self) -> int:
        """Height including title bar."""
        return self.h + TITLE_BAR_H

    @property
    def title_bar_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, TITLE_BAR_H)

    @property
    def close_btn_rect(self) -> pygame.Rect:
        bx = self.x + self.w - CLOSE_BTN_SIZE - CLOSE_BTN_MARGIN
        by = self.y + (TITLE_BAR_H - CLOSE_BTN_SIZE) // 2
        return pygame.Rect(bx, by, CLOSE_BTN_SIZE, CLOSE_BTN_SIZE)

    @property
    def content_rect(self) -> pygame.Rect:
        """The area below the title bar where the panel draws its content."""
        return pygame.Rect(self.x, self.y + TITLE_BAR_H, self.w, self.h)

    @property
    def full_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.w, self.total_h)

    @property
    def resize_handle_rect(self) -> pygame.Rect:
        rx = self.x + self.w - RESIZE_HANDLE_SIZE
        ry = self.y + self.total_h - RESIZE_HANDLE_SIZE
        return pygame.Rect(rx, ry, RESIZE_HANDLE_SIZE, RESIZE_HANDLE_SIZE)

    # ------------------------------------------------------------------
    #  Drawing
    # ------------------------------------------------------------------

    def draw_chrome(self, surface: pygame.Surface) -> None:
        """Draw title bar, close button, and resize handle.

        The owning panel draws its content into ``content_rect`` *before*
        calling this, so the chrome overlays properly.
        """
        # Title bar background
        tb = self.title_bar_rect
        pygame.draw.rect(surface, (35, 35, 55), tb)
        pygame.draw.rect(surface, UI_BORDER_PANEL, tb, 1)

        # Title text
        if self.title:
            ts = self._font.render(self.title, True, WHITE)
            surface.blit(ts, (tb.x + 6, tb.y + (TITLE_BAR_H - ts.get_height()) // 2))

        # Close button (X)
        cb = self.close_btn_rect
        mx, my = pygame.mouse.get_pos()
        hover = cb.collidepoint(mx, my)
        bg_color = (180, 50, 50) if hover else (100, 40, 40)
        pygame.draw.rect(surface, bg_color, cb, border_radius=3)
        pygame.draw.rect(surface, RED if hover else GRAY, cb, 1, border_radius=3)
        xs = self._font.render("X", True, WHITE)
        surface.blit(xs, (cb.centerx - xs.get_width() // 2,
                          cb.centery - xs.get_height() // 2))

        # Resize handle (small triangle in bottom-right)
        rh = self.resize_handle_rect
        points = [(rh.right, rh.top), (rh.right, rh.bottom), (rh.left, rh.bottom)]
        pygame.draw.polygon(surface, (100, 100, 130), points)

        # Full window border
        pygame.draw.rect(surface, UI_BORDER_PANEL, self.full_rect, 1)

    # ------------------------------------------------------------------
    #  Event handling — returns True if the event was consumed
    # ------------------------------------------------------------------

    def handle_event(self, event: pygame.event.Event) -> bool:
        self.close_requested = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Close button click
            if self.close_btn_rect.collidepoint(mx, my):
                self.close_requested = True
                return True

            # Resize handle
            if self.resize_handle_rect.collidepoint(mx, my):
                self._resizing = True
                self._resize_ox = mx
                self._resize_oy = my
                self._resize_start_scale = self.scale
                return True

            # Title bar drag
            if self.title_bar_rect.collidepoint(mx, my):
                self._dragging = True
                self._drag_ox = mx - self.x
                self._drag_oy = my - self.y
                return True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                self._dragging = False
                return True
            if self._resizing:
                self._resizing = False
                return True

        if event.type == pygame.MOUSEMOTION:
            if self._dragging:
                mx, my = event.pos
                self.x = mx - self._drag_ox
                self.y = my - self._drag_oy
                # Clamp to screen
                self.x = max(0, min(self.x, SCREEN_WIDTH - self.w))
                self.y = max(0, min(self.y, SCREEN_HEIGHT - self.total_h))
                return True
            if self._resizing:
                mx, my = event.pos
                dx = mx - self._resize_ox
                # Scale proportionally based on horizontal drag distance
                delta_scale = dx / max(1, self.base_w)
                new_scale = self._resize_start_scale + delta_scale
                new_scale = max(MIN_SCALE, min(MAX_SCALE, new_scale))
                self.scale = new_scale
                # Clamp position after resize
                self.x = max(0, min(self.x, SCREEN_WIDTH - self.w))
                self.y = max(0, min(self.y, SCREEN_HEIGHT - self.total_h))
                return True

        return False

    def reset_position(self, x: int | None = None, y: int | None = None) -> None:
        """Reset window to center or specified position."""
        if x is not None and y is not None:
            self.x = x
            self.y = y
        else:
            self.x = (SCREEN_WIDTH - self.w) // 2
            self.y = (SCREEN_HEIGHT - self.total_h) // 2
        self.scale = 1.0
