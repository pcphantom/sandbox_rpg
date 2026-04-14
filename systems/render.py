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
        ents = em.get_entities_with(Transform, Renderable)
        ents.sort(key=lambda e: (em.get_component(e, Renderable).layer,
                                 em.get_component(e, Transform).y))
        for eid in ents:
            t = em.get_component(eid, Transform)
            r = em.get_component(eid, Renderable)
            if not r.visible:
                continue
            sx = int(t.x - camera.x + r.offset_x)
            sy = int(t.y - camera.y + r.offset_y)
            if (sx < -RENDER_CULL_MARGIN or sx > SCREEN_WIDTH + RENDER_CULL_MARGIN
                    or sy < -RENDER_CULL_MARGIN or sy > SCREEN_HEIGHT + RENDER_CULL_MARGIN):
                continue
            surf = (pygame.transform.flip(r.surface, r.flip_x, False)
                    if r.flip_x else r.surface)
            self.screen.blit(surf, (sx, sy))
