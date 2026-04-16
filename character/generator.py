"""Character generator screen — customize appearance before starting a new game.

CharacterData holds all customization indices (serializable).
CharacterGenerator is the full-screen UI for the customization screen.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any
import random

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GRAY, DARK_GRAY, GREEN, RED, CYAN,
    UI_BG_MAIN_MENU, UI_BG_BUTTON_HOVER, UI_BG_BUTTON_NORMAL,
    UI_BORDER_NORMAL, UI_BORDER_PANEL,
)
from character.layers import (
    compose_character,
    SKIN_COLORS, HAIR_COLORS, SHIRT_COLORS, PANTS_COLORS,
    HAIR_STYLES, SHIRT_STYLES, PANTS_STYLES,
    SHOE_STYLES, SHOE_COLORS, ACCESSORY_STYLES,
)


# ======================================================================
# CHARACTER DATA — serializable customization state
# ======================================================================

class CharacterData:
    """Stores the player's character customization choices."""

    def __init__(self) -> None:
        self.skin_color_idx: int = 0
        self.hair_style_idx: int = 0
        self.hair_color_idx: int = 0
        self.shirt_style_idx: int = 0
        self.shirt_color_idx: int = 0
        self.pants_style_idx: int = 0
        self.pants_color_idx: int = 0
        self.shoe_style_idx: int = 0
        self.shoe_color_idx: int = 0
        self.accessory_idx: int = 0
        self.show_equipment: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'skin_color_idx': self.skin_color_idx,
            'hair_style_idx': self.hair_style_idx,
            'hair_color_idx': self.hair_color_idx,
            'shirt_style_idx': self.shirt_style_idx,
            'shirt_color_idx': self.shirt_color_idx,
            'pants_style_idx': self.pants_style_idx,
            'pants_color_idx': self.pants_color_idx,
            'shoe_style_idx': self.shoe_style_idx,
            'shoe_color_idx': self.shoe_color_idx,
            'accessory_idx': self.accessory_idx,
            'show_equipment': self.show_equipment,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self.skin_color_idx = data.get('skin_color_idx', 0)
        self.hair_style_idx = data.get('hair_style_idx', 0)
        self.hair_color_idx = data.get('hair_color_idx', 0)
        self.shirt_style_idx = data.get('shirt_style_idx', 0)
        self.shirt_color_idx = data.get('shirt_color_idx', 0)
        self.pants_style_idx = data.get('pants_style_idx', 0)
        self.pants_color_idx = data.get('pants_color_idx', 0)
        self.shoe_style_idx = data.get('shoe_style_idx', 0)
        self.shoe_color_idx = data.get('shoe_color_idx', 0)
        self.accessory_idx = data.get('accessory_idx', 0)
        self.show_equipment = data.get('show_equipment', True)

    def build_sprite(self, weapon_id: str = '',
                     shield_id: str = '') -> pygame.Surface:
        """Build the character sprite from current customization choices."""
        return compose_character(
            skin_color=SKIN_COLORS[self.skin_color_idx % len(SKIN_COLORS)],
            hair_style=HAIR_STYLES[self.hair_style_idx % len(HAIR_STYLES)],
            hair_color=HAIR_COLORS[self.hair_color_idx % len(HAIR_COLORS)],
            shirt_style=SHIRT_STYLES[self.shirt_style_idx % len(SHIRT_STYLES)],
            shirt_color=SHIRT_COLORS[self.shirt_color_idx % len(SHIRT_COLORS)],
            pants_style=PANTS_STYLES[self.pants_style_idx % len(PANTS_STYLES)],
            pants_color=PANTS_COLORS[self.pants_color_idx % len(PANTS_COLORS)],
            shoe_style=SHOE_STYLES[self.shoe_style_idx % len(SHOE_STYLES)],
            shoe_color=SHOE_COLORS[self.shoe_color_idx % len(SHOE_COLORS)],
            accessory=ACCESSORY_STYLES[self.accessory_idx % len(ACCESSORY_STYLES)],
            weapon_id=weapon_id,
            shield_id=shield_id,
            show_equipment=self.show_equipment,
        )


# ======================================================================
# CHARACTER GENERATOR UI
# ======================================================================

# Option row definitions: (label, attr_name, palette_or_list)
_OPTIONS = [
    ('Skin Color',  'skin_color_idx',  SKIN_COLORS),
    ('Hair Style',  'hair_style_idx',  HAIR_STYLES),
    ('Hair Color',  'hair_color_idx',  HAIR_COLORS),
    ('Shirt Style', 'shirt_style_idx', SHIRT_STYLES),
    ('Shirt Color', 'shirt_color_idx', SHIRT_COLORS),
    ('Pants Style', 'pants_style_idx', PANTS_STYLES),
    ('Pants Color', 'pants_color_idx', PANTS_COLORS),
    ('Shoe Style',  'shoe_style_idx',  SHOE_STYLES),
    ('Shoe Color',  'shoe_color_idx',  SHOE_COLORS),
    ('Accessory',   'accessory_idx',   ACCESSORY_STYLES),
]

# Arrow button size
_ARROW_W = 28
_ARROW_H = 28
_ROW_H = 36
_PREVIEW_SCALE = 4
_OPTION_LABEL_GAP = 12
_OPTION_CONTROL_GAP = 12
_OPTION_SWATCH_W = 60
_OPTION_VALUE_PADDING_X = 6


class CharacterGenerator:
    """Full-screen character customization UI."""

    def __init__(self) -> None:
        self._font = pygame.font.SysFont('consolas', 16)
        self._font_sm = pygame.font.SysFont('consolas', 13)
        self._font_lg = pygame.font.SysFont('consolas', 22, bold=True)
        self._option_label_width = max(
            self._font.size(f"{label}:")[0] for label, _attr, _palette in _OPTIONS
        )
        widest_text_value = max(
            (
                self._font.size(value.title())[0]
                for _label, _attr, palette in _OPTIONS
                for value in palette
                if not isinstance(value, tuple)
            ),
            default=0,
        )
        self._option_value_width = max(_OPTION_SWATCH_W, widest_text_value) + (
            _OPTION_VALUE_PADDING_X * 2
        )
        self._preview_weapon: bool = True  # toggle in preview
        # Set to True when opened for a legacy save migration
        self._is_legacy_migration: bool = False

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def draw(self, g: 'Game') -> None:
        screen = g.screen
        cd = g.char_data
        screen.fill(UI_BG_MAIN_MENU)
        mx, my = pygame.mouse.get_pos()

        # Title
        title = self._font_lg.render("Character Creation", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))

        # Panel background
        pw, ph = 500, 500
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 60
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((20, 20, 35, 240))
        screen.blit(bg, (px, py))
        pygame.draw.rect(screen, UI_BORDER_PANEL,
                         (px, py, pw, ph), 2, border_radius=10)

        # Preview area (right side of panel)
        preview_x = px + pw - 130
        preview_y = py + 30
        preview_w = 24 * _PREVIEW_SCALE
        preview_h = 32 * _PREVIEW_SCALE
        # Build preview sprite
        weapon = 'iron_sword' if self._preview_weapon else ''
        shield = 'wood_shield' if self._preview_weapon else ''
        sprite = cd.build_sprite(weapon, shield)
        scaled = pygame.transform.scale(sprite, (preview_w, preview_h))
        # Preview frame
        pygame.draw.rect(screen, (30, 30, 50),
                         (preview_x - 4, preview_y - 4,
                          preview_w + 8, preview_h + 8),
                         border_radius=4)
        pygame.draw.rect(screen, UI_BORDER_PANEL,
                         (preview_x - 4, preview_y - 4,
                          preview_w + 8, preview_h + 8),
                         1, border_radius=4)
        screen.blit(scaled, (preview_x, preview_y))

        # Equipment toggle below preview
        eq_y = preview_y + preview_h + 12
        eq_label = self._font_sm.render("Preview Equipment", True, GRAY)
        screen.blit(eq_label, (preview_x - 4, eq_y))
        eq_btn_r = pygame.Rect(preview_x + 30, eq_y + 16, 40, 20)
        eq_on = self._preview_weapon
        btn_color = GREEN if eq_on else RED
        pygame.draw.rect(screen, (40, 40, 60), eq_btn_r, border_radius=3)
        pygame.draw.rect(screen, btn_color, eq_btn_r, 1, border_radius=3)
        eq_txt = self._font_sm.render("On" if eq_on else "Off", True, btn_color)
        screen.blit(eq_txt, (eq_btn_r.centerx - eq_txt.get_width() // 2,
                             eq_btn_r.centery - eq_txt.get_height() // 2))

        # Show equipment on character toggle
        se_y = eq_y + 42
        se_label = self._font_sm.render("Show Equip In-Game", True, GRAY)
        screen.blit(se_label, (preview_x - 4, se_y))
        se_btn_r = pygame.Rect(preview_x + 30, se_y + 16, 40, 20)
        se_on = cd.show_equipment
        se_color = GREEN if se_on else RED
        pygame.draw.rect(screen, (40, 40, 60), se_btn_r, border_radius=3)
        pygame.draw.rect(screen, se_color, se_btn_r, 1, border_radius=3)
        se_txt = self._font_sm.render("On" if se_on else "Off", True, se_color)
        screen.blit(se_txt, (se_btn_r.centerx - se_txt.get_width() // 2,
                             se_btn_r.centery - se_txt.get_height() // 2))

        # Randomize button
        rand_y = se_y + 46
        rand_btn_r = pygame.Rect(preview_x - 4, rand_y, preview_w + 8, 26)
        rand_hov = rand_btn_r.collidepoint(mx, my)
        pygame.draw.rect(screen,
                         (60, 60, 90) if rand_hov else (40, 40, 60),
                         rand_btn_r, border_radius=4)
        pygame.draw.rect(screen, CYAN if rand_hov else GRAY,
                         rand_btn_r, 1, border_radius=4)
        rand_txt = self._font_sm.render("Randomize", True,
                                        CYAN if rand_hov else WHITE)
        screen.blit(rand_txt,
                    (rand_btn_r.centerx - rand_txt.get_width() // 2,
                     rand_btn_r.centery - rand_txt.get_height() // 2))

        # Option rows (left side of panel)
        opt_x = px + 20
        opt_y = py + 30
        for label, attr, palette in _OPTIONS:
            self._draw_option_row(screen, mx, my, opt_x, opt_y,
                                  label, attr, palette, cd)
            opt_y += _ROW_H + 8

        # "Save and Start Game" button
        btn_label = ("Save and Continue" if self._is_legacy_migration
                     else "Save and Start Game")
        btn_w, btn_h = 240, 46
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        btn_y = py + ph + 20
        btn_r = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        hov = btn_r.collidepoint(mx, my)
        bc = UI_BG_BUTTON_HOVER if hov else UI_BG_BUTTON_NORMAL
        pygame.draw.rect(screen, bc, btn_r, border_radius=6)
        bd = GREEN if hov else UI_BORDER_NORMAL
        pygame.draw.rect(screen, bd, btn_r, 2, border_radius=6)
        bt = self._font.render(btn_label, True,
                               WHITE if hov else GRAY)
        screen.blit(bt, (btn_r.centerx - bt.get_width() // 2,
                         btn_r.centery - bt.get_height() // 2))

        g._present()

    def _get_option_row_rects(self, x: int, y: int) -> tuple[pygame.Rect,
                                                               pygame.Rect,
                                                               pygame.Rect]:
        """Return fixed row geometry so every option aligns to shared columns."""
        left_x = x + self._option_label_width + _OPTION_LABEL_GAP
        left_r = pygame.Rect(left_x, y + 4, _ARROW_W, _ARROW_H)
        value_r = pygame.Rect(
            left_r.right + _OPTION_CONTROL_GAP,
            y + 4,
            self._option_value_width,
            _ARROW_H,
        )
        right_r = pygame.Rect(
            value_r.right + _OPTION_CONTROL_GAP,
            y + 4,
            _ARROW_W,
            _ARROW_H,
        )
        return left_r, value_r, right_r

    def _draw_option_row(self, screen: pygame.Surface, mx: int, my: int,
                         x: int, y: int, label: str, attr: str,
                         palette: list, cd: CharacterData) -> None:
        """Draw one customization row: label  < value >"""
        idx = getattr(cd, attr)
        count = len(palette)

        # Label
        lt = self._font.render(label + ":", True, GRAY)
        screen.blit(lt, (x, y + 6))

        # Arrows and current value use a shared fixed layout.
        left_r, value_r, right_r = self._get_option_row_rects(x, y)

        # Left arrow
        lhov = left_r.collidepoint(mx, my)
        pygame.draw.rect(screen, (60, 60, 90) if lhov else (40, 40, 60),
                         left_r, border_radius=4)
        pygame.draw.rect(screen, CYAN if lhov else GRAY,
                         left_r, 1, border_radius=4)
        la = self._font.render("<", True, WHITE)
        screen.blit(la, (left_r.centerx - la.get_width() // 2,
                         left_r.centery - la.get_height() // 2))

        # Value display
        value = palette[idx % count]
        if isinstance(value, tuple):
            swatch_r = pygame.Rect(
                value_r.centerx - (_OPTION_SWATCH_W // 2),
                y + 6,
                _OPTION_SWATCH_W,
                _ARROW_H - 4,
            )
            pygame.draw.rect(screen, value, swatch_r, border_radius=3)
            pygame.draw.rect(screen, GRAY, swatch_r, 1, border_radius=3)
        else:
            vt = self._font.render(value.title(), True, WHITE)
            screen.blit(
                vt,
                (
                    value_r.centerx - vt.get_width() // 2,
                    value_r.centery - vt.get_height() // 2,
                ),
            )

        rhov = right_r.collidepoint(mx, my)
        pygame.draw.rect(screen, (60, 60, 90) if rhov else (40, 40, 60),
                         right_r, border_radius=4)
        pygame.draw.rect(screen, CYAN if rhov else GRAY,
                         right_r, 1, border_radius=4)
        ra = self._font.render(">", True, WHITE)
        screen.blit(ra, (right_r.centerx - ra.get_width() // 2,
                         right_r.centery - ra.get_height() // 2))

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_events(self, g: 'Game') -> None:
        cd = g.char_data
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                g.running = False
                continue
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and (event.mod & pygame.KMOD_ALT)):
                g._toggle_fullscreen()
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Back to main menu
                g.in_char_gen = False
                g.in_main_menu = True
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = g._scale_mouse_pos(event.pos)
                self._handle_click(g, mx, my)

    def _handle_click(self, g: 'Game', mx: int, my: int) -> None:
        cd = g.char_data

        pw, ph = 500, 500
        px = SCREEN_WIDTH // 2 - pw // 2
        py = 60
        preview_x = px + pw - 130
        preview_y = py + 30
        preview_w = 24 * _PREVIEW_SCALE
        preview_h = 32 * _PREVIEW_SCALE

        # Equipment preview toggle
        eq_y = preview_y + preview_h + 12
        eq_btn_r = pygame.Rect(preview_x + 30, eq_y + 16, 40, 20)
        if eq_btn_r.collidepoint(mx, my):
            self._preview_weapon = not self._preview_weapon
            return

        # Show equipment in-game toggle
        se_y = eq_y + 42
        se_btn_r = pygame.Rect(preview_x + 30, se_y + 16, 40, 20)
        if se_btn_r.collidepoint(mx, my):
            cd.show_equipment = not cd.show_equipment
            return

        # Randomize button
        rand_y = se_y + 46
        rand_btn_r = pygame.Rect(preview_x - 4, rand_y, preview_w + 8, 26)
        if rand_btn_r.collidepoint(mx, my):
            self._randomize(cd)
            return

        # Option row arrows
        opt_x = px + 20
        opt_y = py + 30
        for _label, attr, palette in _OPTIONS:
            count = len(palette)
            left_r, _value_r, right_r = self._get_option_row_rects(opt_x, opt_y)
            if left_r.collidepoint(mx, my):
                cur = getattr(cd, attr)
                setattr(cd, attr, (cur - 1) % count)
                return
            if right_r.collidepoint(mx, my):
                cur = getattr(cd, attr)
                setattr(cd, attr, (cur + 1) % count)
                return
            opt_y += _ROW_H + 8

        # "Save and Start Game" button
        btn_w, btn_h = 240, 46
        btn_x = SCREEN_WIDTH // 2 - btn_w // 2
        btn_y = py + ph + 20
        btn_r = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        if btn_r.collidepoint(mx, my):
            self._start_game(g)

    def _start_game(self, g: 'Game') -> None:
        """Finalize character and enter the game."""
        from core.components import Renderable, Equipment
        if not self._is_legacy_migration:
            g._full_restart()
        # Build sprite with current equipment if loading a save
        eq: Equipment = g.em.get_component(g.player_id, Equipment)
        weapon = eq.weapon or '' if eq else ''
        shield = eq.shield or '' if eq else ''
        sprite = g.char_data.build_sprite(weapon, shield)
        g.textures.cache['player'] = sprite
        pr: Renderable = g.em.get_component(g.player_id, Renderable)
        pr.surface = sprite
        g.in_char_gen = False
        if self._is_legacy_migration:
            # Returning to a loaded game — go to paused state
            g.paused = True
            self._is_legacy_migration = False
            g.music_manager.start(g.daynight.is_night())

    def _randomize(self, cd: 'CharacterData') -> None:
        """Randomize all character customization choices."""
        cd.skin_color_idx = random.randint(0, len(SKIN_COLORS) - 1)
        cd.hair_style_idx = random.randint(0, len(HAIR_STYLES) - 1)
        cd.hair_color_idx = random.randint(0, len(HAIR_COLORS) - 1)
        cd.shirt_style_idx = random.randint(0, len(SHIRT_STYLES) - 1)
        cd.shirt_color_idx = random.randint(0, len(SHIRT_COLORS) - 1)
        cd.pants_style_idx = random.randint(0, len(PANTS_STYLES) - 1)
        cd.pants_color_idx = random.randint(0, len(PANTS_COLORS) - 1)
        cd.shoe_style_idx = random.randint(0, len(SHOE_STYLES) - 1)
        cd.shoe_color_idx = random.randint(0, len(SHOE_COLORS) - 1)
        cd.accessory_idx = random.randint(0, len(ACCESSORY_STYLES) - 1)
