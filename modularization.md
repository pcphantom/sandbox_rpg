# Extreme Modularization Plan

This document outlines the full plan for migrating all declared control variables to `game_controller.py` and reducing every script to under 1,000 lines through extreme modularization.

---

## Guiding Principles

1. **game_controller.py** contains ONLY declared variables — no logic, no functions, no classes.
2. **No color, numeric tuning value, or control variable should be declared in more than one place.** Every script imports from `game_controller.py`.
3. **No regular script should exceed 1,000 lines.** Files that do must be split by responsibility.
4. **No functionality changes.** This is a pure refactor — every behavior must remain identical.
5. **Signal Up, Call Down** architecture is maintained throughout.
6. **DRY / SOLID / KISS / YAGNI** strictly enforced per CLAUDE.md.

---

## Current State: Files Over 1,000 Lines (Must Be Split)

| File | Lines | Action Required |
|------|-------|-----------------|
| `textures.py` | 2,499 | Split into `textures/` package by texture category |
| `gui.py` | 2,189 | Already has `ui/` package — remove this legacy monolith |
| `sandbox_rpg.py` | 1,189 | Extract remaining inline logic into game/ modules |

---

## Current State: All Files with Variables to Migrate

The following files contain module-level declared variables that belong in `game_controller.py`. Each will be refactored to import from `game_controller.py` instead of declaring locally.

### Core Module (`core/`)
| File | Lines | Variables to Migrate |
|------|-------|---------------------|
| `core/constants.py` | 237 | ALL color constants, tile types, world dimensions, screen settings, font sizes, combat ranges, building stats, inventory config, hotbar config, HUD config — **every constant** |
| `core/settings.py` | 66 | `DISPLAY_WINDOWED/FULLSCREEN/BORDERLESS`, `DISPLAY_MODE_NAMES`, `RESOLUTION_PRESETS`, `DEFAULTS` dict values |
| `core/enhancement.py` | 303 | `OFFENSE_BONUS_PER_LEVEL`, `DEFENSE_BONUS_PER_LEVEL`, `ENHANCEMENT_COLORS`, `WEAPON_BASES`, `RANGED_BASES`, `ARMOR_BASES`, `TURRET_BASE_*`, `TURRET_HP_TABLE` |
| `core/components.py` | 290 | Default values in component `__init__` params (light color, AI ranges, turret stats) — reference `game_controller` defaults |
| `core/music.py` | 79 | `CROSSFADE_MS` |
| `core/camera.py` | 47 | Camera lerp factor (0.12) |

### Data Module (`data/`)
| File | Lines | Variables to Migrate |
|------|-------|---------------------|
| `data/day_night.py` | 103 | ALL variables — this entire file's purpose is subsumed by the "Day / Night Controls" section of `game_controller.py` |
| `data/day_events.py` | 108 | ALL variables — wave system, mob respawn, spawn chances, initial population |
| `data/difficulty.py` | 93 | `DIFFICULTY_*` constants and `DIFFICULTY_PROFILES` |
| `data/stats.py` | 98 | ALL stat tuning constants (strength, agility, vitality, luck) |
| `data/quality.py` | 144 | `RARITY_TIERS`, `RARITY_COLORS`, `RARITY_MULTIPLIERS`, `RARITY_ELIGIBLE_CATEGORIES` |
| `data/combat.py` | 32 | `RANGED_DATA`, `AMMO_BONUS_DAMAGE`, `BOMB_DATA` |
| `data/mobs.py` | 112 | Mob glow colors (boss_golem glow, boss_lich glow, etc.) |

### Systems Module (`systems/`)
| File | Lines | Variables to Migrate |
|------|-------|---------------------|
| `systems/ai.py` | 186 | ALL 17 AI behavior constants (chase, wander, ranged, stuck detection) |
| `systems/projectile.py` | 52 | `PROJ_MOB_HIT_RADIUS` |
| `systems/render.py` | 33 | `RENDER_CULL_MARGIN` |
| `systems/movement.py` | 25 | `VELOCITY_DEADZONE` |
| `systems/trap.py` | 48 | `TRAP_TRIGGER_RADIUS`, `TRAP_SELF_DAMAGE`, `TRAP_DAMAGE`, `TRAP_COOLDOWN` |

### Enchantments Module (`enchantments/`)
| File | Lines | Variables to Migrate |
|------|-------|---------------------|
| `enchantments/effects.py` | 212 | ALL enchantment scaling tables (fire/ice/lightning damage, slow, arc radius), `ENCHANT_COLORS`, `ENCHANT_PREFIX` |

### Drops Module (`drops/`)
| File | Lines | Variables to Migrate |
|------|-------|---------------------|
| `drops/common.py` | 49 | `ENHANCEMENT_ODDS`, `RARITY_WEIGHTS_NORMAL`, `RARITY_WEIGHTS_BOSS` |

### Spells Module (`spells/`)
| File | Lines | Variables to Migrate |
|------|-------|---------------------|
| `spells/__init__.py` | 35 | `SPELL_RECHARGE` |

### Game Module (`game/`)
| File | Lines | Inline Colors/Magic Numbers to Migrate |
|------|-------|----------------------------------------|
| `game/drawing.py` | 797 | ~40 inline color tuples, health bar colors, HUD overlay colors, period colors |
| `game/combat.py` | 663 | 6 inline color tuples (fire/ice/lightning particles, campfire/torch light) |
| `game/interaction.py` | 603 | 3 inline color tuples, light source values |
| `game/entities.py` | 483 | 15 mob body color tuples, boss glow color |
| `game/persistence.py` | 408 | Light source colors, building HP defaults |
| `game/menus.py` | 377 | ~16 inline UI theme color tuples |

### UI Module (`ui/`)
| File | Lines | Inline Colors to Migrate |
|------|-------|--------------------------|
| `ui/inventory.py` | 323 | 11 color tuples |
| `ui/character_menu.py` | 399 | 9 color tuples |
| `ui/pause_menu.py` | 148 | 8 color tuples |
| `ui/split_dialog.py` | 177 | 7 color tuples |
| `ui/crafting.py` | 104 | 7 color tuples |
| `ui/elements.py` | 96 | 4 color tuples |
| `ui/minimap.py` | 89 | `TILE_COLORS` dict, `MAP_PX`, `VIEW_RADIUS` |
| `ui/rarity_display.py` | 88 | 1 color tuple |

### Root Files
| File | Lines | Action |
|------|-------|--------|
| `gui.py` | 2,189 | **DELETE** — this is a legacy monolith; all functionality exists in `ui/` package |
| `textures.py` | 2,499 | Split into `textures/` package (see Step 7) |
| `sandbox_rpg.py` | 1,189 | Extract remaining inline logic (see Step 8) |

---

## Implementation Steps (Clustered by Priority)

### Step 1: Foundation — Wire Up `game_controller.py` to `core/`
**Files:** `core/constants.py`, `core/settings.py`
**What:** Make `core/constants.py` re-export everything from `game_controller.py` instead of declaring locally. This ensures ALL existing imports (`from core.constants import X`) continue to work without touching every consumer file. Update `core/settings.py` to import display mode constants from `game_controller`.
**Risk:** Low — purely additive, backwards compatible via re-export.
**Test:** Run full game, verify all imports resolve.

### Step 2: Day/Night & Day Events — Full Migration
**Files:** `data/day_night.py`, `data/day_events.py`, `systems/day_night.py`
**What:** Replace all local variable declarations in `data/day_night.py` and `data/day_events.py` with imports from `game_controller.py`. These files become thin re-export layers or are reduced to just their docstrings + imports. `systems/day_night.py` already imports from `data/day_night.py` — the chain now flows: `game_controller` → `data/day_night` → `systems/day_night`.
**Risk:** Low — these files are already well-organized data-only modules.

### Step 3: Difficulty & Stats — Full Migration
**Files:** `data/difficulty.py`, `data/stats.py`
**What:** Move difficulty profiles and stat tuning constants to import from `game_controller.py`. These data files keep their helper functions (e.g., `get_profile()`) but all numeric values come from the controller.
**Risk:** Low — data-only modules with no complex logic.

### Step 4: Combat & Rarity Data — Full Migration
**Files:** `data/combat.py`, `data/quality.py`, `data/mobs.py` (boss glow colors only)
**What:** Migrate ranged weapon data, bomb data, rarity colors/tiers/multipliers, and boss glow colors. `data/quality.py` keeps its `RARITY_COLORS` dict but builds it from `game_controller` color constants. `data/mobs.py` references `game_controller` glow colors instead of inline tuples.
**Risk:** Low — straightforward value replacement.

### Step 5: Systems Module — Full Migration
**Files:** `systems/ai.py`, `systems/projectile.py`, `systems/render.py`, `systems/movement.py`, `systems/trap.py`
**What:** Replace all 17+ module-level AI constants and system constants with imports from `game_controller.py`. These files already have clean constant declarations at the top — just change declarations to imports.
**Risk:** Low — mechanical find-and-replace.

### Step 6: Enchantments & Drops — Full Migration
**Files:** `enchantments/effects.py`, `drops/common.py`, `spells/__init__.py`
**What:** Move all enchantment scaling tables, enchant colors, enhancement odds, and rarity weights to import from `game_controller.py`. `enchantments/effects.py` keeps its `ENCHANT_EFFECTS` builder logic but sources all numeric tables from the controller.
**Risk:** Low — these are already pure data declarations.

### Step 7: Enhancement Module — Full Migration
**Files:** `core/enhancement.py`, `core/components.py`, `core/music.py`, `core/camera.py`
**What:** Migrate enhancement bonuses, weapon/armor/turret bases, default component values, crossfade timing, and camera lerp. `core/enhancement.py` keeps its builder functions but all base values come from `game_controller`.
**Risk:** Low — values only, logic untouched.

### Step 8: Game Module — Inline Color Extraction
**Files:** `game/drawing.py`, `game/combat.py`, `game/interaction.py`, `game/entities.py`, `game/persistence.py`, `game/menus.py`
**What:** Replace ALL inline color tuples and magic numbers with named imports from `game_controller.py`. This is the largest step — `game/drawing.py` alone has ~40 inline colors. Every `(R, G, B)` tuple gets replaced with a named constant.
**Risk:** Medium — many individual replacements, each must be verified visually.
**Approach:** Do one file at a time, test after each.

### Step 9: UI Module — Inline Color Extraction
**Files:** `ui/inventory.py`, `ui/character_menu.py`, `ui/pause_menu.py`, `ui/crafting.py`, `ui/split_dialog.py`, `ui/elements.py`, `ui/minimap.py`, `ui/rarity_display.py`
**What:** Same as Step 8 — replace all inline color tuples with `game_controller` imports. The UI module has many repeated theme colors (panel backgrounds, borders, text colors) that should all reference the centralized UI theme constants.
**Risk:** Medium — many replacements but UI is testable.

### Step 10: Kill the Legacy Monolith — `gui.py`
**Files:** `gui.py`
**What:** Verify that ALL classes and functionality in `gui.py` (2,189 lines) already exist in the `ui/` package. If so, delete `gui.py` entirely. If any classes are still imported from `gui.py` by other files, update those imports to point to `ui/`.
**Risk:** Medium — must verify no remaining imports reference `gui.py`.
**Approach:** `grep -r "from gui import\|import gui" .` to find all references, update them, then delete.

### Step 11: Split `textures.py` (2,499 lines) → `textures/` Package ✅
**Files:** `textures.py` → `textures/__init__.py`, `textures/tiles.py`, `textures/mobs.py`, `textures/items.py`, `textures/buildings.py`, `textures/effects.py`
**What:** Broke the monolithic texture generator into a package organized by texture category. Each sub-module contains standalone functions (taking `gen` parameter) for one category. The `__init__.py` re-exports `TextureGenerator` with `generate_all()` for backwards compatibility. Verified 187 texture keys match exactly between old and new.

### Step 12: Trim `sandbox_rpg.py` (1,204 lines) Below 1,000 ✅
**Files:** `sandbox_rpg.py` → `game/events.py`, `game/update.py`
**What:** Extracted `_handle_events()` (196 lines) to `game/events.py` and `_update()` (228 lines) to `game/update.py`. Cleaned up unused imports. Final size: 734 lines.

### Step 13: Verification Pass ✅
**What:** After all migrations:
1. ✅ `wc -l` on every `.py` file — no file exceeds 1,000 lines except `game_controller.py` (1,021 — the single source of truth).
2. ✅ Zero remaining inline color tuples in `game/`, `ui/`, `spells/`, or `sandbox_rpg.py`.
3. ✅ All 35 spell tier colors centralized in `game_controller.py`.
4. ✅ Full game test — all 187 textures, all 35 spells, all UI components verified.
5. ✅ All module imports successful.

---

## Variable Migration Tracking

### Colors: Current Duplication Map

The following colors appear in **multiple files** and MUST be centralized:

| Color | Current Locations | game_controller Name |
|-------|------------------|---------------------|
| `(255, 120, 30)` | game/combat.py, game/drawing.py, game/interaction.py, enchantments/effects.py, spells/fireball.py | `ENCHANT_COLOR_FIRE` / `PARTICLE_COLOR_FIRE` |
| `(100, 200, 255)` | game/combat.py, enchantments/effects.py, spells/ice.py | `ENCHANT_COLOR_ICE` / `PARTICLE_COLOR_ICE` |
| `(180, 200, 255)` | game/combat.py, enchantments/effects.py, spells/lightning.py | `ENCHANT_COLOR_LIGHTNING` / `PARTICLE_COLOR_LIGHTNING_ARC` |
| `(255, 160, 80)` | game/combat.py, game/persistence.py, game/interaction.py | `LIGHT_COLOR_CAMPFIRE` |
| `(255, 180, 60)` | game/drawing.py, game/persistence.py, game/interaction.py | `LIGHT_COLOR_TORCH` |
| `(200, 200, 210)` | game/entities.py (skeleton + skeleton_archer) | `MOB_COLOR_SKELETON` |
| `(255, 60, 60)` | game/entities.py, core/constants.py (RED) | `RED` / `BOSS_GLOW_DEFAULT` |
| `(80, 140, 255)` | data/quality.py, core/enhancement.py | `RARITY_COLOR_RARE` / `ENHANCEMENT_COLOR_2` |
| `(180, 60, 255)` | data/quality.py, core/enhancement.py | `RARITY_COLOR_EPIC` / `ENHANCEMENT_COLOR_3` |
| `(255, 215, 0)` | data/quality.py, core/enhancement.py | `RARITY_COLOR_LEGENDARY` / `ENHANCEMENT_COLOR_4` |
| `(255, 50, 50)` | data/quality.py, core/enhancement.py | `RARITY_COLOR_MYTHIC` / `ENHANCEMENT_COLOR_5` |
| `(30, 30, 50)` | game/menus.py, game/drawing.py, ui/pause_menu.py | `UI_BG_BUTTON_NORMAL` |
| `(50, 50, 75)` | game/menus.py, game/drawing.py | `UI_BG_BUTTON_HOVER` |
| `(100, 100, 130)` | game/menus.py, ui/pause_menu.py | `UI_BORDER_NORMAL` |
| `(140, 140, 170)` | game/menus.py, game/drawing.py, ui/pause_menu.py | `UI_BORDER_PANEL` |
| `(130, 130, 160)` | ui/inventory.py, ui/elements.py, ui/split_dialog.py, ui/character_menu.py | `UI_TEXT_MUTED` |
| `(200, 200, 240)` | game/drawing.py, ui/inventory.py, ui/pause_menu.py | `UI_TEXT_HIGHLIGHT` |

---

## Architecture After Modularization

```
game_controller.py          ← ALL declared variables (the one source of truth)
    │
    ├── core/constants.py   ← Re-exports from game_controller (backwards compat)
    ├── core/settings.py    ← Imports display constants from game_controller
    ├── core/enhancement.py ← Builder functions using game_controller values
    ├── core/components.py  ← Default params reference game_controller
    ├── core/camera.py      ← Imports CAMERA_LERP_FACTOR
    ├── core/music.py       ← Imports CROSSFADE_MS
    │
    ├── data/day_night.py   ← Thin re-export or just imports
    ├── data/day_events.py  ← Thin re-export or just imports
    ├── data/difficulty.py  ← get_profile() + imports
    ├── data/stats.py       ← Thin re-export or just imports
    ├── data/quality.py     ← Builds RARITY_COLORS dict from game_controller colors
    ├── data/combat.py      ← Imports ranged/bomb data
    ├── data/mobs.py        ← MOB_DATA with glow colors from game_controller
    │
    ├── systems/ai.py       ← Imports all AI constants
    ├── systems/trap.py     ← Imports trap constants
    ├── systems/*.py        ← Each imports its constants
    │
    ├── enchantments/effects.py ← Imports scaling tables + colors
    ├── drops/common.py     ← Imports odds/weights
    ├── spells/__init__.py  ← Imports SPELL_RECHARGE
    │
    ├── game/*.py           ← All colors from game_controller
    ├── ui/*.py             ← All colors from game_controller
    │
    ├── textures/           ← Package (split from textures.py)
    │   ├── __init__.py     ← TextureGenerator class + generate_all()
    │   ├── tiles.py        ← Player, resource, terrain tiles
    │   ├── mobs.py         ← All 18 mob textures
    │   ├── items.py        ← All ~52 item textures
    │   ├── buildings.py    ← Building items + placed objects
    │   └── effects.py      ← Projectiles + enchantment textures
    │
    └── sandbox_rpg.py      ← Entry point, < 1000 lines
```

---

## Priority Order Summary

| Step | Scope | Difficulty | Files Affected |
|------|-------|-----------|----------------|
| **1** | Foundation (core/constants re-export) | Easy | 2 | ✅ |
| **2** | Day/Night + Day Events | Easy | 3 | ✅ |
| **3** | Difficulty + Stats | Easy | 2 | ✅ |
| **4** | Combat Data + Rarity + Mob Colors | Easy | 3 | ✅ |
| **5** | Systems (AI, trap, movement, etc.) | Easy | 5 | ✅ |
| **6** | Enchantments + Drops + Spells | Easy | 3 | ✅ |
| **7** | Enhancement + Components + Music + Camera | Easy | 4 | ✅ |
| **8** | Game module inline colors | Medium | 6 | ✅ |
| **9** | UI module inline colors | Medium | 8 | ✅ |
| **10** | Delete legacy `gui.py` | Medium | 1+ | ✅ |
| **11** | Split `textures.py` → package | High | 7+ new files | ✅ |
| **12** | Trim `sandbox_rpg.py` < 1000 lines | Medium | 2-3 | ✅ |
| **13** | Verification pass | Easy | All | ✅ |
