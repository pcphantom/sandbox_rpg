"""F12 run command bar — text input overlay for running game commands."""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional, Tuple

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from game_controller import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    CMD_BAR_BG, CMD_BAR_BORDER, CMD_BAR_INPUT_BG, CMD_BAR_INPUT_BORDER,
    CMD_BAR_TEXT, CMD_BAR_PLACEHOLDER, CMD_BAR_CLOSE_HOVER,
    CMD_BAR_CLOSE_NORMAL, CMD_BAR_RESULT_OK, CMD_BAR_RESULT_ERR,
    WHITE, GRAY,
)

BAR_WIDTH = 500
BAR_HEIGHT = 110
CLOSE_SIZE = 22


class CommandBar:
    """Overlay text-input bar opened with F12."""

    def __init__(self) -> None:
        self.visible: bool = False
        self.text: str = ""
        self.result_msg: str = ""
        self.result_ok: bool = True
        self.result_timer: float = 0.0
        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)

    def toggle(self) -> None:
        self.visible = not self.visible
        if self.visible:
            self.text = ""
            self.result_msg = ""
            self.result_timer = 0.0

    def close(self) -> None:
        self.visible = False
        self.text = ""

    def _set_result(self, msg: str, ok: bool = True) -> None:
        self.result_msg = msg
        self.result_ok = ok
        self.result_timer = 3.0

    def handle_event(self, event: pygame.event.Event,
                     execute_cb: Callable[[str], Tuple[bool, str]]) -> bool:
        """Process keyboard events. Returns True if event was consumed."""
        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True
            if event.key == pygame.K_RETURN:
                cmd = self.text.strip()
                if cmd:
                    ok, msg = execute_cb(cmd)
                    self._set_result(msg, ok)
                self.text = ""
                return True
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            return False

        if event.type == pygame.TEXTINPUT:
            self.text += event.text
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Close button check
            bx = SCREEN_WIDTH // 2 + BAR_WIDTH // 2 - CLOSE_SIZE - 6
            by = SCREEN_HEIGHT // 2 - BAR_HEIGHT // 2 + 6
            close_r = pygame.Rect(bx, by, CLOSE_SIZE, CLOSE_SIZE)
            if close_r.collidepoint(event.pos):
                self.close()
                return True

        return False

    def update(self, dt: float) -> None:
        if self.result_timer > 0:
            self.result_timer -= dt

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        mx, my = pygame.mouse.get_pos()

        # Panel
        px = SCREEN_WIDTH // 2 - BAR_WIDTH // 2
        py = SCREEN_HEIGHT // 2 - BAR_HEIGHT // 2
        bg = pygame.Surface((BAR_WIDTH, BAR_HEIGHT), pygame.SRCALPHA)
        bg.fill(CMD_BAR_BG)
        surface.blit(bg, (px, py))
        pygame.draw.rect(surface, CMD_BAR_BORDER,
                         (px, py, BAR_WIDTH, BAR_HEIGHT), 2, border_radius=6)

        # Title
        title = self.font.render("Run Command (F12)", True, WHITE)
        surface.blit(title, (px + 12, py + 8))

        # Close button
        cbx = px + BAR_WIDTH - CLOSE_SIZE - 6
        cby = py + 6
        close_r = pygame.Rect(cbx, cby, CLOSE_SIZE, CLOSE_SIZE)
        hover = close_r.collidepoint(mx, my)
        cc = CMD_BAR_CLOSE_HOVER if hover else CMD_BAR_CLOSE_NORMAL
        pygame.draw.rect(surface, cc, close_r, border_radius=3)
        xt = self.font_sm.render("X", True, WHITE)
        surface.blit(xt, (cbx + (CLOSE_SIZE - xt.get_width()) // 2,
                          cby + (CLOSE_SIZE - xt.get_height()) // 2))

        # Input field
        input_y = py + 34
        input_r = pygame.Rect(px + 10, input_y, BAR_WIDTH - 20, 26)
        pygame.draw.rect(surface, CMD_BAR_INPUT_BG, input_r, border_radius=3)
        pygame.draw.rect(surface, CMD_BAR_INPUT_BORDER, input_r, 1,
                         border_radius=3)
        if self.text:
            it = self.font.render(self.text, True, CMD_BAR_TEXT)
        else:
            it = self.font.render("Type a command and press Enter...",
                                  True, CMD_BAR_PLACEHOLDER)
        surface.blit(it, (px + 14, input_y + 4))

        # Cursor blink
        if self.text:
            cursor_x = px + 14 + it.get_width() + 2
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                pygame.draw.line(surface, CMD_BAR_TEXT,
                                 (cursor_x, input_y + 4),
                                 (cursor_x, input_y + 20))

        # Result message
        if self.result_msg and self.result_timer > 0:
            rc = CMD_BAR_RESULT_OK if self.result_ok else CMD_BAR_RESULT_ERR
            rt = self.font_sm.render(self.result_msg, True, rc)
            surface.blit(rt, (px + 12, py + 66))

        # Hint
        hint = self.font_sm.render(
            'Type "help" for a list of commands', True, GRAY)
        surface.blit(hint, (px + 12, py + BAR_HEIGHT - 20))
