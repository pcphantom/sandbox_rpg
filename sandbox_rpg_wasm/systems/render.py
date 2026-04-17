"""Render system — draws sprites sorted by layer and Y position."""
from typing import Any

import pygame

from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.ecs import EntityManager
from core.components import Transform, Renderable
from game_controller import RENDER_CULL_MARGIN


class RenderSystem:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def update(self, em: EntityManager, camera: Any) -> None:
        # Pre-compute sort keys and cull off-screen entities BEFORE sorting
        cam_x = camera.x
        cam_y = camera.y
        visible = []
        for eid in em.get_entities_with(Transform, Renderable):
            r = em.get_component(eid, Renderable)
            if not r.visible:
                continue
            t = em.get_component(eid, Transform)
            sx = int(t.x - cam_x + r.offset_x)
            sy = int(t.y - cam_y + r.offset_y)
            if (sx < -RENDER_CULL_MARGIN or sx > SCREEN_WIDTH + RENDER_CULL_MARGIN
                    or sy < -RENDER_CULL_MARGIN or sy > SCREEN_HEIGHT + RENDER_CULL_MARGIN):
                continue
            visible.append((r.layer, t.y, eid, sx, sy, r))
        visible.sort()
        for _layer, _y, _eid, sx, sy, r in visible:
            surf = (pygame.transform.flip(r.surface, r.flip_x, False)
                    if r.flip_x else r.surface)
            self.screen.blit(surf, (sx, sy))
