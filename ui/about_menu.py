"""About menu — Game info, Index, Credits sub-menus."""
from __future__ import annotations
from typing import TYPE_CHECKING, List

import pygame

if TYPE_CHECKING:
    from sandbox_rpg import Game

from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, GRAY, DARK_GRAY, CYAN,
    UI_BG_MAIN_MENU, UI_BG_BUTTON_HOVER, UI_BG_BUTTON_NORMAL,
    UI_BORDER_NORMAL, UI_BORDER_PANEL,
    OPTIONS_BACK_HOVER, OPTIONS_BACK_NORMAL, OPTIONS_BACK_BORDER,
)


# ======================================================================
# CONTENT GENERATORS
# ======================================================================

def get_game_instructions() -> List[str]:
    """Return how-to-play text lines built from actual game data."""
    return [
        "=== CONTROLS ===",
        "",
        "WASD - Move",
        "Space - Attack (melee)",
        "E - Interact / Gather resources",
        "F - Use equipped item (spell, potion, etc.)",
        "R - Ranged attack (requires bow/crossbow + ammo)",
        "I - Open/close inventory",
        "C - Open/close crafting menu",
        "P - Open/close character stats",
        "1-6 - Select hotbar slot",
        "7,8,9,0,-,= - Select secondary action bar slot",
        "Mouse Wheel - Cycle hotbar",
        "F5 - Quick Save",
        "F9 - Quick Load",
        "F12 - Command console",
        "Esc - Pause / close menus",
        "R (in placement mode) - Rotate building",
        "",
        "=== GETTING STARTED ===",
        "",
        "You begin with some wood and stone. Gather resources",
        "by pressing E near trees, rocks, and other harvestable",
        "objects. Use the crafting menu (C) to turn raw materials",
        "into tools, weapons, and buildings.",
        "",
        "=== GATHERING ===",
        "",
        "Press E near resources to harvest them. Equipping an axe",
        "gives bonus wood when harvesting trees. Equipping a",
        "pickaxe gives bonus stone/ore when mining rocks. The game",
        "checks both your equipped weapon and your selected hotbar",
        "item, using the higher applicable bonus.",
        "",
        "=== COMBAT ===",
        "",
        "Space to melee attack. R to fire ranged weapons (bow,",
        "crossbow, sling) -- requires ammunition. Enemies become",
        "aggressive when you get close or attack them. Strength",
        "increases melee damage, Agility increases attack speed",
        "and movement.",
        "",
        "=== DAY/NIGHT CYCLE ===",
        "",
        "Daytime is safe for exploration. At night, enemies become",
        "more dangerous and attack in waves. Stay near light",
        "sources (campfires, torches) to avoid darkness damage.",
        "Sleep in a bed to skip the night.",
        "",
        "=== BUILDING ===",
        "",
        "Craft walls, doors, and turrets to defend your base.",
        "Place buildings by selecting them and clicking. Use R to",
        "rotate before placing. Turrets auto-attack nearby enemies.",
        "Repair damaged structures with a hammer.",
        "",
        "=== SPELLS ===",
        "",
        "Spell books are found as loot. Select a spell in your",
        "hotbar and press F to cast. Spells have cooldowns.",
        "- Fireball/Lightning/Ice Shard: Offensive targeted spells",
        "- Heal: Restores HP",
        "- Strength: Increases damage dealt",
        "- Protection: Reduces damage taken",
        "- Regen: Heals over time",
        "- Levitate: Ignore terrain speed penalties",
        "- Return: Teleport to your bed",
        "",
        "=== CAVES ===",
        "",
        "Find cave entrances on the overworld. Caves contain rare",
        "ores, diamonds, boss enemies, and treasure chests. Cave",
        "resources regenerate periodically.",
        "",
        "=== ENCHANTMENTS ===",
        "",
        "Build an Enchantment Table to enchant weapons and armor.",
        "Combine enchantment tomes to create and upgrade",
        "enchantments. Types: Fire, Ice, Lightning, Protection,",
        "Regen, Strength.",
        "",
        "=== DIFFICULTY ===",
        "",
        "Easy, Normal, Hard, Hardcore -- affects enemy HP, damage,",
        "wave scaling, and resource respawn rates. Difficulty is",
        "saved per game.",
    ]


def get_index_content() -> List[str]:
    """Return organized item/enemy index built from game data."""
    from data import ITEM_DATA, ITEM_CATEGORIES
    from data.mobs import MOB_DATA

    lines: List[str] = []
    lines.append("=== ITEMS ===")
    lines.append("")

    # Group items by category (skip enhanced variants like iron_sword_1)
    categories: dict = {}
    for item_id, (name, desc, dmg, harvest, heal, placeable) in ITEM_DATA.items():
        # Skip enhanced variants to keep the index clean
        if any(item_id.endswith(f'_{i}') for i in range(1, 6)):
            base = item_id.rsplit('_', 1)[0]
            if base in ITEM_DATA:
                continue
        cat = ITEM_CATEGORIES.get(item_id, 'other')
        categories.setdefault(cat, []).append(
            (item_id, name, desc, dmg, harvest, heal))

    cat_order = [
        'weapon', 'ranged', 'ammo', 'armor', 'shield', 'tool',
        'spell', 'consumable', 'material', 'placeable',
        'enchant_tome', 'transfer_tome', 'throwable',
    ]
    for cat in cat_order:
        if cat not in categories:
            continue
        lines.append(f"--- {cat.upper().replace('_', ' ')} ---")
        for item_id, name, desc, dmg, harvest, heal in sorted(
                categories[cat], key=lambda x: x[1]):
            stats = []
            if dmg > 0:
                stats.append(f"DMG:{dmg}")
            if harvest > 0:
                stats.append(f"Harvest:{harvest}")
            if heal > 0:
                stats.append(f"Heal:{heal}")
            stat_str = f"  ({', '.join(stats)})" if stats else ""
            lines.append(f"  {name}{stat_str}")
        lines.append("")

    lines.append("=== ENEMIES ===")
    lines.append("")
    for mob_id, data in sorted(MOB_DATA.items(), key=lambda x: x[1]['hp']):
        name = data.get('name', mob_id.replace('_', ' ').title())
        hp = data['hp']
        dmg = data['damage']
        xp = data['xp']
        boss = " [BOSS]" if data.get('boss', False) else ""
        lines.append(f"  {name}{boss}  HP:{hp}  DMG:{dmg}  XP:{xp}")

    return lines


# ======================================================================
# DRAWING
# ======================================================================

def draw_about_menu(g: 'Game') -> None:
    """Draw the main About screen with 4 sub-section buttons."""
    g.screen.fill(UI_BG_MAIN_MENU)
    mx, my = pygame.mouse.get_pos()

    pw, ph = 450, 360
    px = SCREEN_WIDTH // 2 - pw // 2
    py = SCREEN_HEIGHT // 2 - ph // 2

    bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
    bg.fill((20, 20, 35, 240))
    g.screen.blit(bg, (px, py))
    pygame.draw.rect(g.screen, UI_BORDER_PANEL,
                     (px, py, pw, ph), 2, border_radius=10)

    title = g.font_lg.render("About", True, WHITE)
    g.screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 16))

    # 2x2 grid of buttons
    btn_w, btn_h = 190, 50
    gap_x, gap_y = 20, 16
    grid_w = btn_w * 2 + gap_x
    grid_x = px + pw // 2 - grid_w // 2
    grid_y = py + 70

    buttons = [
        ('game', "Game"),
        ('index', "Index"),
        ('noobfragged', "NoobFragged Games"),
        ('credits', "Credits"),
    ]
    for i, (key, label) in enumerate(buttons):
        col = i % 2
        row = i // 2
        bx = grid_x + col * (btn_w + gap_x)
        by = grid_y + row * (btn_h + gap_y)
        r = pygame.Rect(bx, by, btn_w, btn_h)
        hov = r.collidepoint(mx, my)
        bc = UI_BG_BUTTON_HOVER if hov else UI_BG_BUTTON_NORMAL
        pygame.draw.rect(g.screen, bc, r, border_radius=6)
        bd = CYAN if hov else UI_BORDER_NORMAL
        pygame.draw.rect(g.screen, bd, r, 2, border_radius=6)
        lt = g.font.render(label, True, WHITE if hov else GRAY)
        g.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                           r.centery - lt.get_height() // 2))

    # Back button
    back_y = py + ph - 60
    back_r = pygame.Rect(px + pw // 2 - 80, back_y, 160, 40)
    hov = back_r.collidepoint(mx, my)
    bc = OPTIONS_BACK_HOVER if hov else OPTIONS_BACK_NORMAL
    pygame.draw.rect(g.screen, bc, back_r, border_radius=6)
    pygame.draw.rect(g.screen, OPTIONS_BACK_BORDER, back_r, 2,
                     border_radius=6)
    bt = g.font.render("Back  [Esc]", True, WHITE)
    g.screen.blit(bt, (back_r.centerx - bt.get_width() // 2,
                       back_r.centery - bt.get_height() // 2))

    g._present()


def draw_about_section(g: 'Game') -> None:
    """Draw the selected section content with scrollable text."""
    g.screen.fill(UI_BG_MAIN_MENU)
    mx, my = pygame.mouse.get_pos()

    section_titles = {
        'game': "How to Play",
        'index': "Item & Enemy Index",
        'noobfragged': "NoobFragged Games",
        'credits': "Credits",
    }

    pw, ph = 620, 500
    px = SCREEN_WIDTH // 2 - pw // 2
    py = SCREEN_HEIGHT // 2 - ph // 2

    bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
    bg.fill((20, 20, 35, 240))
    g.screen.blit(bg, (px, py))
    pygame.draw.rect(g.screen, UI_BORDER_PANEL,
                     (px, py, pw, ph), 2, border_radius=10)

    title_text = section_titles.get(g.about_section, "About")
    title = g.font_lg.render(title_text, True, WHITE)
    g.screen.blit(title, (px + pw // 2 - title.get_width() // 2, py + 12))

    # Get content lines
    if g.about_section == 'game':
        lines = get_game_instructions()
    elif g.about_section == 'index':
        lines = get_index_content()
    else:
        lines = ["", "Content coming soon..."]

    # Scrollable text area
    text_x = px + 20
    text_y_start = py + 46
    text_area_h = ph - 110
    line_h = 18

    max_visible = text_area_h // line_h
    max_scroll = max(0, len(lines) - max_visible)
    g.about_scroll = max(0, min(g.about_scroll, max_scroll))

    # Clip text to panel area
    clip_rect = pygame.Rect(px + 2, text_y_start, pw - 4, text_area_h)
    g.screen.set_clip(clip_rect)

    for i, line in enumerate(lines[g.about_scroll:]):
        ly = text_y_start + i * line_h
        if ly > text_y_start + text_area_h:
            break
        if line.startswith("==="):
            color = CYAN
            font = g.font
        elif line.startswith("---"):
            color = (180, 180, 80)
            font = g.font_sm
        else:
            color = GRAY
            font = g.font_sm
        surf = font.render(line, True, color)
        g.screen.blit(surf, (text_x, ly))

    g.screen.set_clip(None)

    # Scroll indicator
    if max_scroll > 0:
        bar_h = max(20, int(text_area_h * max_visible / len(lines)))
        bar_y = text_y_start + int(
            (text_area_h - bar_h) * g.about_scroll / max_scroll)
        pygame.draw.rect(g.screen, DARK_GRAY,
                         (px + pw - 14, bar_y, 8, bar_h),
                         border_radius=3)

    # Back button
    back_y = py + ph - 52
    back_r = pygame.Rect(px + pw // 2 - 80, back_y, 160, 40)
    hov = back_r.collidepoint(mx, my)
    bc = OPTIONS_BACK_HOVER if hov else OPTIONS_BACK_NORMAL
    pygame.draw.rect(g.screen, bc, back_r, border_radius=6)
    pygame.draw.rect(g.screen, OPTIONS_BACK_BORDER, back_r, 2,
                     border_radius=6)
    bt = g.font.render("Back  [Esc]", True, WHITE)
    g.screen.blit(bt, (back_r.centerx - bt.get_width() // 2,
                       back_r.centery - bt.get_height() // 2))

    g._present()


# ======================================================================
# EVENT HANDLING
# ======================================================================

def handle_about_events(g: 'Game') -> None:
    """Process events for both the About main screen and section views."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            g.running = False
            continue
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_RETURN
                    and (event.mod & pygame.KMOD_ALT)):
                g._toggle_fullscreen()
                continue
            if event.key == pygame.K_ESCAPE:
                if g.about_section:
                    g.about_section = ''
                    g.about_scroll = 0
                else:
                    g.in_about_menu = False
                    g.in_options_menu = True
                continue

        # Scroll in section view
        if g.about_section and event.type == pygame.MOUSEWHEEL:
            g.about_scroll -= event.y * 3
            g.about_scroll = max(0, g.about_scroll)
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = g._scale_mouse_pos(event.pos)

            if g.about_section:
                # Section view — only back button
                pw, ph = 620, 500
                px = SCREEN_WIDTH // 2 - pw // 2
                py_val = SCREEN_HEIGHT // 2 - ph // 2
                back_y = py_val + ph - 52
                back_r = pygame.Rect(px + pw // 2 - 80, back_y, 160, 40)
                if back_r.collidepoint(mx, my):
                    g.about_section = ''
                    g.about_scroll = 0
            else:
                # About main screen — 4 buttons + back
                pw, ph = 450, 360
                px = SCREEN_WIDTH // 2 - pw // 2
                py_val = SCREEN_HEIGHT // 2 - ph // 2

                btn_w, btn_h = 190, 50
                gap_x, gap_y = 20, 16
                grid_w = btn_w * 2 + gap_x
                grid_x = px + pw // 2 - grid_w // 2
                grid_y = py_val + 70

                buttons = [
                    ('game', "Game"),
                    ('index', "Index"),
                    ('noobfragged', "NoobFragged Games"),
                    ('credits', "Credits"),
                ]
                for i, (key, label) in enumerate(buttons):
                    col = i % 2
                    row = i // 2
                    bx = grid_x + col * (btn_w + gap_x)
                    by = grid_y + row * (btn_h + gap_y)
                    r = pygame.Rect(bx, by, btn_w, btn_h)
                    if r.collidepoint(mx, my):
                        g.about_section = key
                        g.about_scroll = 0
                        break

                # Back button
                back_y = py_val + ph - 60
                back_r = pygame.Rect(px + pw // 2 - 80, back_y, 160, 40)
                if back_r.collidepoint(mx, my):
                    g.in_about_menu = False
                    g.in_options_menu = True
