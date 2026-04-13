"""Base UI elements — UIElement, ProgressBar, Tooltip."""
from __future__ import annotations

from typing import List, Tuple, Optional

import pygame

from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE


class UIElement:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect; self.visible = True; self.enabled = True
        self.children: List[UIElement] = []

    def add_child(self, child: UIElement) -> None:
        self.children.append(child)

    def update(self, dt: float) -> None:
        if self.visible:
            for c in self.children:
                c.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        if self.visible:
            for c in self.children:
                c.draw(surface)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
        for c in reversed(self.children):
            if c.handle_event(event):
                return True
        return False


class ProgressBar(UIElement):
    def __init__(self, rect: pygame.Rect, max_value: float,
                 fg: Tuple[int, int, int] = (200, 60, 60),
                 bg: Tuple[int, int, int] = (40, 20, 20)) -> None:
        super().__init__(rect)
        self.value = max_value; self.max_value = max_value
        self.color_fg = fg; self.color_bg = bg

    def set_value(self, v: float) -> None:
        from core.utils import clamp as _clamp
        self.value = _clamp(v, 0, self.max_value)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        pygame.draw.rect(surface, self.color_bg, self.rect, border_radius=4)
        fw = (int(self.rect.width * (self.value / self.max_value))
              if self.max_value > 0 else 0)
        pygame.draw.rect(
            surface, self.color_fg,
            pygame.Rect(self.rect.x, self.rect.y, fw, self.rect.height),
            border_radius=4)
        pygame.draw.rect(surface, (200, 200, 220), self.rect, 2,
                         border_radius=4)


class Tooltip:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.colors: List[Tuple[int, int, int]] = []
        self.visible = False
        self.pos = (0, 0)
        self.font = pygame.font.SysFont('consolas', 13)

    def clear(self) -> None:
        self.visible = False

    def show(self, lines: List[str], pos: Tuple[int, int],
             colors: Optional[List[Tuple[int, int, int]]] = None) -> None:
        self.lines = lines; self.visible = True; self.pos = pos
        self.colors = colors or [WHITE] * len(lines)

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.lines:
            return
        surfs = [self.font.render(l, True,
                 self.colors[i] if i < len(self.colors) else WHITE)
                 for i, l in enumerate(self.lines)]
        mw = max(s.get_width() for s in surfs)
        th = len(surfs) * 17 + 10
        x = min(self.pos[0] + 14, SCREEN_WIDTH - mw - 20)
        y = min(self.pos[1] + 14, SCREEN_HEIGHT - th - 10)
        bg = pygame.Surface((mw + 16, th), pygame.SRCALPHA)
        bg.fill((12, 12, 22, 230))
        surface.blit(bg, (x, y))
        pygame.draw.rect(surface, (130, 130, 160),
                         (x, y, mw + 16, th), 1, border_radius=3)
        for i, s in enumerate(surfs):
            surface.blit(s, (x + 8, y + 5 + i * 17))
