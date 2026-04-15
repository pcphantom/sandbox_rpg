# CONSTANTS.md — Global Constants & Data Reference

This document tracks all global constants, key variables, and data structures used across the codebase. **Must be read before making changes and updated when constants change.**

---

## Module Architecture

| Module | Purpose | Key Contents |
|--------|---------|-----------|
| `game_controller.py` | **Single source of truth** for ALL game tuning variables | ~450+ symbols, every constant in the game |
| `sandbox_rpg.py` | Game class, main loop, event/update routing | Game class (entry point) |
| **core/** | Core engine modules | |
| `core/constants.py` | Re-exports from `game_controller.py` + data modules | ~240 re-exported constants |
| `core/components.py` | ECS component definitions | 15 component types |
| `core/item_stack.py` | Centralised item identity, stacking, transfer, sort | normalize_rarity, items_match, add_to_slots, remove_from_slots, sort_slots, transfer_slot, transfer_all |
| `core/item_presentation.py` | Canonical item label + rarity styling helpers | get_base_item_display_name, get_item_upgrade_suffix, get_item_display_label, build_item_presentation |
| `core/item_metadata.py` | Shared item metadata helpers for cheats and loot | parse_level_token, resolve_enchant_type_token, resolve_rarity_token, can_apply_enchant_to_item, set_item_enhancement_level, roll_item_metadata |
| `core/ecs.py` | EntityManager | Core ECS, _query_cache for per-frame dedup |
| `core/spatial.py` | SpatialHash grid-based spatial index | spatial_hash singleton, SPATIAL_CELL_SIZE=128 |
| `core/utils.py` | Math/geometry helpers | clamp, lerp, hash_noise, fbm_noise |
| `core/camera.py` | Camera | Viewport tracking |
| `core/settings.py` | Display/audio settings | load_settings, save_settings |
| `core/music.py` | MusicManager | Background music |
| **game/** | Game logic modules | |
| `game/combat.py` | Combat mechanics, damage, spells, bombs (god mode check) | 16 functions |
| `game/drawing.py` | All rendering/drawing + cheats button/help overlay | 15 functions |
| `game/entities.py` | Entity creation, population, lifecycle | 12 functions |
| `game/interaction.py` | Interact, placement, crafting, sleep | 8 functions |
| `game/menus.py` | Main menu, options menu | 6 functions |
| `game/persistence.py` | Save/load orchestration (includes cheats_enabled and has_cheated) | 8 functions |
| `game/save_load.py` | Low-level save file I/O | File operations |
| `game/cheats.py` | Cheat commands for F12 command bar | execute_command, help, set, give, god, heal, kill, autokill, levelup, kill_all_enemies |
| **systems/** | ECS systems | |
| `systems/movement.py` | Movement — imports from `game_controller.py` | MovementSystem |
| `systems/physics.py` | Physics / collision | PhysicsSystem |
| `systems/render.py` | Render — imports from `game_controller.py` | RenderSystem |
| `systems/day_night.py` | Day/night cycle | DayNightCycle |
| `systems/ai.py` | AI behaviour — imports from `game_controller.py` | AISystem |
| `systems/projectile.py` | Projectiles — imports from `game_controller.py` | ProjectileSystem |
| `systems/trap.py` | Traps — imports from `game_controller.py` | TrapSystem |
| `systems/turret.py` | Turrets | TurretSystem |
| `systems/wave.py` | Enemy waves | WaveSystem |
| `systems/damage_calc.py` | Damage formulas (imports from data/stats) | calc_melee_damage, calc_ranged_damage, calc_damage_reduction |
| **core/** | Core ECS, components, constants, enhancement | |
| `core/enhancement.py` | Enhancement scaling — imports control vars from `game_controller.py` | WEAPON_BASES, RANGED_BASES, ARMOR_BASES, TURRET_ENHANCE_DAMAGE, TURRET_ENHANCE_HP, TURRET_ENHANCE_DR, ARMOR_VALUES, PROTECTION_DR_BONUS. ENHANCEMENT_COLORS import REMOVED (commented out in game_controller.py). |
| **data/** | Centralised game data/tuning | |
| `data/items.py` | Item re-exports from items/ | ITEM_DATA, ITEM_CATEGORIES, CAN_ENCHANT, CAN_ENHANCE, HAS_RARITY, HARVEST_TYPE, NON_STACKABLE_CATEGORIES |
| `data/crafting.py` | Crafting recipes | RECIPES |
| `data/combat.py` | Combat data — re-exports from `game_controller.py` | RANGED_DATA, AMMO_BONUS_DAMAGE, BOMB_DATA (ARMOR_VALUES re-exported from core.enhancement) |
| `data/mobs.py` | Mob definitions — boss glow colors from `game_controller.py` | MOB_DATA, WAVE_MOB_TIERS, WAVE_RANGED_MOBS, WAVE_BOSS_MOBS |
| `data/day_night.py` | Day/night timing — re-exports from `game_controller.py` | DAWN_BEGINS, DAY_BEGINS, DUSK_BEGINS, NIGHT_BEGINS, TIME_*, flash/banner vars, sleep vars, night damage vars |
| `data/stats.py` | Player stat tuning — re-exports from `game_controller.py` | AGI_SPEED_BONUS, STR_DAMAGE_MULT, CRIT_CHANCE_PER_LUCK, etc. |
| `data/day_events.py` | Spawn/wave tuning — re-exports from `game_controller.py` | MOB_RESPAWN_*, WAVE_*, INITIAL_MOB_SPAWNS, RESOURCE_RESPAWN_DAYS, CAVE_RESET_DAYS |
| `data/difficulty.py` | Difficulty profiles — re-exports from `game_controller.py` + helpers | DIFFICULTY_PROFILES, DIFFICULTY_MULTIPLIERS, get_profile |
| `data/quality.py` | Item quality/rarity — re-exports from `game_controller.py` + helpers | RARITY_TIERS, RARITY_COLORS, RARITY_MULTIPLIERS, RARITY_ELIGIBLE_CATEGORIES, QUALITY_COLORS, get_item_quality, get_item_color |
| **items/** | Modular item definitions with control flags | |
| `items/__init__.py` | Item aggregator — builds ITEM_DATA, ITEM_CATEGORIES, CAN_ENCHANT, CAN_ENHANCE, HAS_RARITY, HARVEST_TYPE, NON_STACKABLE_CATEGORIES from category modules | |
| `items/materials.py` | Material items (wood, stone, iron, etc.) | ITEMS list |
| `items/consumables.py` | Consumable items (berry, pie, bandage, etc.) | ITEMS list |
| `items/weapons.py` | Melee weapons (axe, sword, iron_sword, etc.) | ITEMS list |
| `items/ranged.py` | Ranged weapons (bow, crossbow, sling) | ITEMS list |
| `items/ammo.py` | Ammunition (arrow, bolt, rock_ammo, etc.) | ITEMS list |
| `items/armor.py` | Armor and shields | ITEMS list |
| `items/placeables.py` | Placeables (turret, wall, chest, etc.) | ITEMS list |
| `items/spells.py` | Spell books (all tiers) | ITEMS list |
| `items/tools.py` | Tools (hammer, pickaxes) | ITEMS list |
| `items/tomes.py` | Enchantment and transfer tomes | ITEMS list |
| `items/throwables.py` | Throwables (bomb) | ITEMS list |
| **world/** | World generation | |
| `world/generator.py` | Overworld terrain | World, WorldGenerator |
| `world/cave.py` | Cave interiors, daily regeneration | CaveData, generate_cave_interior, CaveData.regenerate() |
| **gui.py** | **DELETED** — replaced by ui/ package | *(see ui/ modules below)* |
| **ui/** | All GUI panels (modular) | |
| `ui/__init__.py` | Re-exports all UI classes | UIElement, ProgressBar, Tooltip, SplitDialog, DropConfirmDialog, InventoryGrid, CraftingPanel, PauseMenu, CharacterMenu, ChestUI, EnchantmentTableUI, StoneOvenUI, Minimap |
| `ui/elements.py` | UIElement, ProgressBar, Tooltip | Base widgets |
| `ui/split_dialog.py` | SplitDialog | Stack splitting |
| `ui/drop_confirm.py` | DropConfirmDialog | Drop item confirmation prompt |
| `ui/inventory.py` | InventoryGrid — hotbar cycling (hotbar_view_index), centred grid layout | Inventory panel with up/down arrows to cycle all active hotbars |
| `ui/crafting.py` | CraftingPanel | Crafting panel (420×dynamic) |
| `ui/pause_menu.py` | PauseMenu | Pause/save/load (460×440) — **DO NOT MODIFY dimensions or layout** |
| `ui/character_menu.py` | CharacterMenu | Stats + equip with dropdown (540×460) — **DO NOT MODIFY dimensions or layout** |
| `ui/chest.py` | ChestUI | Chest storage with stacking rules (620×320) — **DO NOT MODIFY dimensions** |
| `ui/enchantment_table.py` | EnchantmentTableUI | Enchantment table 3×3 grid |
| `ui/stone_oven.py` | StoneOvenUI | Stone oven 2×2 smelting/cooking interface |
| `ui/inventory_sort.py` | sort_inventory_slots | Inventory sorting (respects non-stackable rules) |
| `ui/minimap.py` | Minimap | Minimap drawing |
| `ui/command_bar.py` | F12 run command bar | CommandBar — text input overlay for running game commands; owns keyboard focus via `blocks_game_input()` while visible and supports `give` item autocomplete |
| `ui/rarity_display.py` | Rarity UI & slot helpers | draw_rarity_border (ONLY border), insert_rarity_tooltip, pick_up_rarity, place_rarity, swap_rarity. draw_enhancement_border is COMMENTED OUT. |
| `ui/action_bar.py` | Action bar system — draggable hotbar + extra bars | ActionBarManager (_return_bar_items, handle_close_click with inv param), ExtraActionBar, SECONDARY_HOTKEYS, SECONDARY_KEY_LABELS |
| **character/** | Character customization package | |
| `character/__init__.py` | Re-exports all character classes/data | CharacterData, CharacterGenerator, compose_character, palettes |
| `character/layers.py` | Layered sprite rendering — skin, hair, shirt, pants, weapon/shield overlays | compose_character, draw_skin, draw_hair, draw_shirt, draw_pants, draw_weapon_overlay, draw_shield_overlay, SKIN_COLORS, HAIR_COLORS, SHIRT_COLORS, PANTS_COLORS, HAIR_STYLES, SHIRT_STYLES, PANTS_STYLES |
| `character/generator.py` | Character data model + customization screen UI | CharacterData (to_dict/from_dict/build_sprite), CharacterGenerator (_start_game, _is_legacy_migration) |
| `character/legacy_save_migration.py` | **REMOVABLE** — Detects legacy saves missing character data | check_needs_migration(data) — *Delete once all legacy saves are migrated* |

> ⚠️ **UI LAYOUT PROTECTION**: Panel dimensions and element positions in `pause_menu.py`, `character_menu.py`, and `chest.py` must NEVER be changed without explicit user instruction. Modifying sizes, positions, or rearranging layout sections is strictly prohibited.
| **enchantments/** | Enchantment system | |
| `enchantments/effects.py` | Enchant types, prefixes, colours — imports from `game_controller.py` | ENCHANT_PREFIX, ENCHANT_COLORS, SPELL_TO_ENCHANT, get_enchant_display_prefix |
| `enchantments/recipes.py` | Enchant combine logic | try_combine |
| **drops/** | Loot tables | LOOT_TABLES, roll_loot, CAVE_CHEST_LOOT |
| **systems/** | Centralized game systems | |
| `systems/rarity.py` | Rarity stat application & drop rolling | apply_rarity, roll_rarity |
| `systems/damage_calc.py` | Damage/DR formulas | calc_melee_damage, calc_ranged_damage, calc_damage_reduction |
| **spells/** | Spell effect modules | SPELL_DATA, SPELL_RECHARGE, FIREBALL_SPELLS, HEAL_SPELLS, LIGHTNING_SPELLS, ICE_SPELLS, PROTECTION_SPELLS, REGEN_SPELLS, STRENGTH_SPELLS, LEVITATE_SPELLS, RETURN_SPELLS |
| **rendering/** | Rendering utilities | |
| `rendering/particles.py` | Particle effects | ParticleSystem |
| `textures.py` | Texture generation (root) | TextureGenerator |

---

## Item Control Flags (`items/` package)

Three per-item boolean flags centralize eligibility checks. All consumer modules read these instead of hardcoding category checks.

| Flag Dict | Purpose | Consumers |
|-----------|---------|-----------|
| `CAN_ENCHANT` | Item can receive enchantments at enchantment table | `enchantments/recipes.py: _is_equipment()` |
| `CAN_ENHANCE` | Item can be stat-enhanced (+1..+5) via tome | `enchantments/recipes.py: _get_base_item()`, `drops/__init__.py: _maybe_enhance()` |
| `HAS_RARITY` | Item can roll a rarity tier on drop | `systems/rarity.py: roll_rarity()`, `enchantments/recipes.py: _is_rarity_eligible()` |

### Default Flag Values by Category

| Category | can_enchant | can_enhance | has_rarity |
|----------|-------------|-------------|------------|
| material | False | False | False |
| consumable | False | False | False |
| weapon | True | varies* | True |
| ranged | True | False | True |
| ammo | False | False | False |
| armor / shield | True | varies* | True |
| placeable (turret) | True | True | True |
| placeable (others) | False | False | True |
| spell | False | False | False |
| tool | False | False | True |
| enchant_tome / transfer_tome | False | False | False |
| throwable | False | False | False |

*`can_enhance=True` for: iron_sword, iron_axe, mace, titanium_axe, diamond_axe, iron_pickaxe, titanium_pickaxe, diamond_pickaxe, iron_armor, iron_shield, turret

### Enhanced Item Flag Inheritance

Enhanced variants (e.g., `iron_sword_3`, `turret_5`) automatically inherit flags from their base item:
- `can_enchant` → same as base
- `can_enhance` → True (they are enhancement-level items)
- `has_rarity` → same as base

---

## Display Constants (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SCREEN_WIDTH` | 1280 | Window width in pixels |
| `SCREEN_HEIGHT` | 720 | Window height in pixels |
| `TILE_SIZE` | 32 | Size of one world tile in pixels |
| `WORLD_WIDTH` | 200 | World width in tiles |
| `WORLD_HEIGHT` | 150 | World height in tiles |
| `FPS` | 60 | Target frames per second |

## Colour Constants (`game_controller.py`)

| Constant | RGB Value | Usage |
|----------|-----------|-------|
| `BLACK` | (0, 0, 0) | Background fill |
| `WHITE` | (255, 255, 255) | General text |
| `YELLOW` | (255, 255, 80) | Level-up effects |
| `RED` | (255, 60, 60) | Damage, warnings |
| `GREEN` | (60, 220, 80) | Healing, valid placement |
| `CYAN` | (80, 200, 255) | XP, loot text |
| `GRAY` | (160, 160, 170) | Secondary text |
| `DARK_GRAY` | (80, 80, 90) | UI backgrounds |
| `ORANGE` | (255, 160, 60) | Turret fire, fireball |
| `PURPLE` | (160, 80, 200) | Boss/magic effects |
| `DARK_BROWN` | (60, 35, 15) | Wood textures |
| `LIGHT_BLUE` | (140, 200, 255) | Water accents |
| `DARK_GREEN` | (30, 80, 30) | Forest textures |

### UI Theme Colors (`game_controller.py`)

| Constant | RGBA Value | Usage |
|----------|------------|-------|
| `UI_BG_MAIN_MENU` | (15, 15, 30) | Main menu background |
| `UI_BG_PANEL` | (25, 25, 40, 230) | Standard panel background |
| `UI_BG_BUTTON_NORMAL` | (30, 30, 50) | Button normal state |
| `UI_BG_BUTTON_HOVER` | (50, 50, 75) | Button hover state |
| `UI_BG_BUTTON_SELECTED` | (80, 80, 120) | Button selected state |
| `UI_BORDER_NORMAL` | (100, 100, 130) | Standard border |
| `UI_BORDER_PANEL` | (140, 140, 170) | Panel border |
| `UI_BORDER_LIGHT` | (130, 130, 155) | Light panel border (inventory, crafting) |
| `UI_BORDER_DIALOG` | (160, 160, 200) | Dialog border (character menu, split dialog) |
| `UI_BORDER_BUTTON` | (160, 160, 180) | Action button border (split dialog) |
| `UI_TEXT_NORMAL` | (200, 200, 220) | Standard text |
| `UI_TEXT_MUTED` | (130, 130, 160) | Muted/secondary text |
| `UI_TEXT_HIGHLIGHT` | (200, 200, 240) | Highlighted text, selected borders |
| `UI_NOTIFICATION_TEXT` | (220, 220, 240) | Notification/item name text |

### UI Slot/Grid Colors (`game_controller.py`)

| Constant | RGB Value | Usage |
|----------|-----------|-------|
| `UI_SLOT_BG_NORMAL` | (45, 45, 60) | Inventory/pause slot background |
| `UI_SLOT_BG_SELECTED` | (80, 80, 110) | Selected slot background |
| `UI_SLOT_BG_HOVER` | (70, 70, 95) | Hovered slot in chest/enchant grids |
| `UI_SLOT_BORDER_NORMAL` | (100, 100, 120) | Slot border |
| `UI_SLOT_SEPARATOR` | (80, 80, 100) | Separator line (inventory hotbar/grid) |
| `UI_NAV_HOVER` | (70, 70, 100) | Nav button hover |
| `UI_NAV_NORMAL` | (50, 50, 70) | Nav button normal |
| `UI_SAVE_SLOT_SELECTED` | (70, 70, 110) | Save slot selected |
| `UI_SPLIT_BUTTON_NORMAL` | (55, 55, 75) | Split dialog button normal |
| `UI_ENCHANT_FALLBACK` | (200, 200, 200) | Fallback for unknown enchant/enhancement levels |

### UI Action Button Colors (`game_controller.py`)

| Constant | RGB Value | Usage |
|----------|-----------|-------|
| `UI_CONFIRM_BUTTON` | (60, 120, 60) | Confirm action |
| `UI_CANCEL_BUTTON` | (120, 60, 60) | Cancel action |
| `UI_STAT_BUTTON_HOVER` | (70, 110, 70) | Stat+ button hover |
| `UI_STAT_BUTTON_NORMAL` | (50, 80, 50) | Stat+ button normal |
| `UI_UNEQUIP_HOVER` | (110, 50, 50) | Unequip button hover |
| `UI_UNEQUIP_NORMAL` | (80, 40, 40) | Unequip button normal |
| `UI_EQUIP_HOVER` | (50, 80, 50) | Equip button hover |
| `UI_EQUIP_NORMAL` | (40, 60, 40) | Equip button normal |
| `UI_DROPDOWN_HOVER` | (55, 65, 95) | Dropdown row hover |
| `UI_DROPDOWN_NORMAL` | (35, 35, 55) | Dropdown row normal |

### Crafting Panel Colors (`game_controller.py`)

| Constant | RGB Value | Usage |
|----------|-----------|-------|
| `UI_CRAFT_CAN_NORMAL` | (60, 90, 60) | Craftable recipe normal |
| `UI_CRAFT_CAN_HOVER` | (80, 120, 80) | Craftable recipe hover |
| `UI_CRAFT_CAN_BORDER` | (100, 180, 100) | Craftable recipe border |
| `UI_CRAFT_CANNOT_NORMAL` | (55, 35, 35) | Non-craftable recipe normal |
| `UI_CRAFT_CANNOT_HOVER` | (75, 50, 50) | Non-craftable recipe hover |
| `UI_CRAFT_CANNOT_BORDER` | (140, 60, 60) | Non-craftable recipe border |

### Chest UI Colors (`game_controller.py`)

| Constant | RGBA Value | Usage |
|----------|------------|-------|
| `UI_CHEST_PANEL_BG` | (20, 20, 35, 240) | Chest panel background |
| `UI_CHEST_SLOT_BG_NORMAL` | (50, 50, 65) | Chest slot normal |
| `UI_CHEST_SLOT_BG_HOVER` | (70, 70, 95) | Chest slot hover |
| `UI_CHEST_SORT_HOVER` | (70, 100, 70) | Sort button hover |
| `UI_CHEST_SORT_NORMAL` | (50, 70, 50) | Sort button normal |
| `UI_CHEST_SORT_BORDER` | (100, 160, 100) | Sort button border |
| `UI_CHEST_MOVE_HOVER` | (100, 70, 70) | Move-all button hover |
| `UI_CHEST_MOVE_NORMAL` | (70, 50, 50) | Move-all button normal |
| `UI_CHEST_MOVE_BORDER` | (160, 100, 100) | Move-all button border |

### Enchantment Table UI Colors (`game_controller.py`)

| Constant | RGBA Value | Usage |
|----------|------------|-------|
| `UI_ENCHANT_PANEL_BG` | (20, 15, 30, 240) | Enchant panel background |
| `UI_ENCHANT_PANEL_BORDER` | (140, 100, 170) | Enchant panel border |
| `UI_ENCHANT_SLOT_BG_NORMAL` | (40, 30, 55) | Enchant grid slot normal |
| `UI_ENCHANT_SLOT_BG_HOVER` | (60, 45, 80) | Enchant grid slot hover |
| `UI_ENCHANT_SLOT_BORDER` | (120, 80, 160) | Enchant grid slot border |
| `UI_ENCHANT_COMBINE_ACTIVE` | (55, 95, 55) | Combine button active normal |
| `UI_ENCHANT_COMBINE_ACTIVE_HOVER` | (75, 130, 75) | Combine button active hover |
| `UI_ENCHANT_COMBINE_ACTIVE_BORDER` | (100, 200, 100) | Combine button active border |
| `UI_ENCHANT_COMBINE_INACTIVE` | (40, 40, 50) | Combine button inactive |
| `UI_ENCHANT_COMBINE_INACTIVE_BORDER` | (75, 75, 90) | Combine button inactive border |
| `UI_ENCHANT_DIVIDER` | (120, 80, 150) | Enchant panel divider |

### Death Screen / HUD Colors (`game_controller.py`)

| Constant | RGB Value | Usage |
|----------|-----------|-------|
| `DEATH_BUTTON_HOVER` | (60, 60, 90) | Death screen respawn button hover |
| `DEATH_BUTTON_NORMAL` | (40, 40, 60) | Death screen respawn button normal |
| `HUD_STATUS_TEXT` | (180, 210, 255) | HUD status line text |
| `HUD_RESOURCE_TEXT` | (200, 200, 210) | HUD resource counters |
| `SPELL_HELP_TEXT` | (255, 180, 80) | Spell targeting help text |
| `PLACEMENT_UPGRADE_BORDER` | (255, 200, 60) | Placement upgrade preview border |

### Command Bar (F12) Colors (`game_controller.py`)

| Constant | RGBA Value | Usage |
|----------|------------|-------|
| `CMD_BAR_BG` | (15, 15, 25, 230) | Command bar panel background |
| `CMD_BAR_BORDER` | (120, 120, 160) | Command bar panel border |
| `CMD_BAR_INPUT_BG` | (30, 30, 45) | Input field background |
| `CMD_BAR_INPUT_BORDER` | (100, 100, 140) | Input field border |
| `CMD_BAR_TEXT` | (220, 220, 240) | Input text color |
| `CMD_BAR_PLACEHOLDER` | (100, 100, 120) | Placeholder text color |
| `CMD_BAR_CLOSE_HOVER` | (160, 60, 60) | Close button hover |
| `CMD_BAR_CLOSE_NORMAL` | (100, 40, 40) | Close button normal |
| `CMD_BAR_RESULT_OK` | (100, 255, 100) | Success message color |
| `CMD_BAR_RESULT_ERR` | (255, 100, 100) | Error message color |

### Cheats Button & Help Overlay Colors (`game_controller.py`)

| Constant | RGBA Value | Usage |
|----------|------------|-------|
| `CHEAT_BTN_BG` | (40, 20, 60, 200) | Cheats button background |
| `CHEAT_BTN_BORDER` | (140, 80, 200) | Cheats button border |
| `CHEAT_BTN_HOVER` | (60, 30, 80, 220) | Cheats button hover |
| `CHEAT_BTN_TEXT` | (200, 150, 255) | Cheats button text |
| `CHEAT_HELP_BG` | (15, 10, 25, 235) | Cheat help overlay background |
| `CHEAT_HELP_BORDER` | (140, 80, 200) | Cheat help overlay border |
| `CHEAT_HELP_TEXT` | (200, 200, 220) | Cheat help overlay text |

### Enhancement Level Colors — COMMENTED OUT (`game_controller.py`)

These are preserved but inactive. Inner borders for enchantment/enhancement are disabled — rarity border is the ONLY item border.

```python
# ENHANCEMENT_COLOR_1 = (0, 200, 0)      # +1 green
# ENHANCEMENT_COLOR_2 = (80, 140, 255)    # +2 blue
# ENHANCEMENT_COLOR_3 = (180, 60, 255)    # +3 purple
# ENHANCEMENT_COLOR_4 = (255, 215, 0)     # +4 gold
# ENHANCEMENT_COLOR_5 = (255, 50, 50)     # +5 red
# ENHANCEMENT_COLORS = {1: ..., 2: ..., 3: ..., 4: ..., 5: ...}
```

## Tile Types (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `TILE_WATER` | 0 | Water terrain |
| `TILE_SAND` | 1 | Sand terrain |
| `TILE_GRASS` | 2 | Grass terrain |
| `TILE_DIRT` | 3 | Dirt terrain |
| `TILE_STONE_FLOOR` | 4 | Stone floor |
| `TILE_STONE_WALL` | 5 | Stone wall (impassable) |
| `TILE_FOREST` | 6 | Forest terrain |
| `TILE_CAVE_FLOOR` | 7 | Cave interior floor |
| `TILE_CAVE_ENTRANCE` | 8 | Cave entrance marker |

## Cave System (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `CAVE_COUNT` | 3 | Number of caves per map |
| `CAVE_WIDTH` | 60 | Cave interior width in tiles |
| `CAVE_HEIGHT` | 45 | Cave interior height in tiles |
| `CAVE_WALL_DENSITY` | 0.48 | Cellular automata initial wall chance |
| `CAVE_SMOOTH_PASSES` | 5 | CA smoothing iterations |
| `CAVE_MOB_TYPES` | ('skeleton', 'orc', 'dark_knight', 'troll', 'ghost', 'wraith') | Mobs that spawn in caves |
| `CAVE_MOB_COUNT` | 15 | Mobs per cave |
| `CAVE_BOSS_TYPES` | ('boss_golem', 'boss_lich', 'boss_dragon', 'boss_necromancer', 'boss_troll_king') | Cave boss mob types |
| `CAVE_ORE_COUNT` | 8 | Iron ore nodes per cave |
| `CAVE_DIAMOND_COUNT` | 3 | Diamond nodes per cave |
| `CAVE_HP_MULT` | 1.5 | Extra HP multiplier for cave mobs |
| `CAVE_DMG_MULT` | 1.3 | Extra damage multiplier for cave mobs |
| `CAVE_ENTRANCE_MIN_DIST` | 800.0 | Min px distance between cave entrances |

### Cave Regeneration (per difficulty)

Caves regenerate on a schedule controlled by `CAVE_RESET_DAYS` in `game_controller.py`:

| Difficulty | `CAVE_RESET_DAYS` | Behaviour |
|-----------|-------------------|-----------|
| Easy | 1 | Caves rebuild every day |
| Normal | 1 | Caves rebuild every day |
| Hard | 2 | Caves rebuild every 2 days |
| Hardcore | 3 | Caves rebuild every 3 days |

- `CaveData.regenerate(day_number)` rebuilds all cave interiors using `seed + day_number * 99991` as the seed, producing different layouts each day.
- `boss_alive` and `chest_looted` lists are reset so bosses and chests reappear.
- If the player is inside a cave when the day changes, they are automatically exited first.
- Cave entrances on the overworld remain in the same positions.
- Tracked via `Game._last_cave_reset_day` (saved/loaded).

### Cave Chest Behaviour

- Cave chests always spawn when the player enters a cave (unless already looted this regeneration cycle).
- They use a **gold-coloured** texture (`cave_chest_placed`) instead of the regular brown `chest_placed`.
- Cave chests do **NOT** have a `Building` component, so cave enemies will not attack them.
- Killing the boss is **not** required to open the chest.
- `chest_looted[cave_index]` is set to True when the player interacts with the chest.

### Cave Entity Protection

- **AI only attacks `Building` entities** — cave-spawned resources (ore, diamonds) and cave chests lack `Building`, so enemies ignore them.
- **Player cannot place items in caves** — `placement_confirm()` rejects if `g.in_cave >= 0`.
- **Save/load and structure snapshots** only capture entities with `Building` component.

## Save System (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SAVE_DIR` | `<project>/save/` | Directory for save files |
| `SAVE_SLOTS` | 4 | Total slots (0=quick, 1-3=manual) |
| `QUICK_SAVE_SLOT` | 0 | Quick save slot index |

## Inventory (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `HOTBAR_CAPACITY` | 6 | Number of dedicated hotbar slots (separate from inventory) |
| `INVENTORY_SLOTS_PER_PAGE` | 24 | Slots per inventory page |
| `INVENTORY_PAGES` | 4 | Number of inventory pages |
| `INVENTORY_COLS` | 6 | Columns in inventory grid |
| `INVENTORY_TOTAL_SLOTS` | 96 | Total main inventory capacity (24×4) |

### Chest vs Inventory Stacking Rules

**THIS IS INTENTIONAL — DO NOT "FIX" IT:**

Items that do **NOT** stack in the player inventory (books, weapons, armor, etc.) **DO** stack inside chests, as long as the items are *identical* — same `item_id`, same enchant dict, same enhancement level, and same rarity tier.

This lets the player compact their storage while the inventory keeps items separate for quick equip/swap.

- **Player inventory** (`core/components.py: Inventory`): Non-stackable items (weapons, armor, books, tomes) occupy one slot each, even if identical.
- **Chest storage** (`core/components.py: Storage`): Identical non-stackable items can stack. Identity is checked via `core/item_stack.items_match(id_a, enchant_a, rarity_a, id_b, enchant_b, rarity_b)`.
- **ChestUI** (`ui/chest.py`): Simply delegates to `Storage` component. Does not enforce stacking rules itself.
- **EnchantmentTableUI** (`ui/enchantment_table.py`): Always places exactly 1 item per table slot (NEVER stacks on the enchant table).

| Storage Type | Stacks Identical Non-Stackables? | Enforced By |
|-------------|--------------------------------|-------------|
| Player inventory | No | `Inventory.add_item_enchanted()` |
| Crafted chests | Yes (if items_match) | `Storage` component + `transfer_slot()` |
| Cave chests | Yes (loot drops) | `Storage` component |
| Enchant table | Never (always qty=1) | `EnchantmentTableUI.handle_event()` |

## Stat Scaling (`game_controller.py` → `data/stats.py` → `core/constants.py`)

Single source of truth for ALL stat effects. Change `game_controller.py` to tune stat balance.

### Strength

| Constant | Value | Purpose |
|----------|-------|---------|
| `STR_DAMAGE_MULT` | 2 | Damage bonus per Strength point |
| `BASE_MELEE_DAMAGE` | 5 | Base unarmed/melee damage |
| `BASE_MELEE_DAMAGE_MIN` | 5 | Minimum melee damage floor |
| `LEVEL_DAMAGE_MULT` | 2 | Bonus damage per level above 1 |

### Agility

| Constant | Value | Purpose |
|----------|-------|---------|
| `AGI_SPEED_BONUS` | 0.01 | Speed multiplier per AGI point (1% per point) |
| `AGI_SPEED_BONUS_CAP` | 1.0 | Max speed bonus from agility (+100% = 200% total speed) |
| `AGILITY_COOLDOWN_REDUCTION` | 0.002 | Melee cooldown reduction per AGI point |
| `AGI_RANGED_SPEED_BONUS` | 0.01 | Ranged attack speed bonus per AGI point (1% per point) |
| `AGI_RANGED_SPEED_BONUS_CAP` | 1.0 | Max ranged attack speed bonus (+100% = halves cooldown) |
| `AGI_RANGED_DAMAGE_MULT` | 2 | Ranged damage bonus per AGI point |
| `BASE_ATTACK_COOLDOWN` | 0.30 | Base melee attack cooldown |
| `MIN_ATTACK_COOLDOWN` | 0.15 | Minimum melee attack cooldown |
| `MIN_RANGED_COOLDOWN` | 0.2 | Minimum ranged attack cooldown |

### Vitality

| Constant | Value | Purpose |
|----------|-------|---------|
| `LEVEL_UP_BASE_HP` | 10 | Base HP increase per level |
| `VIT_HP_BONUS_PER_LEVEL` | 5 | Extra HP per VIT point on level up |
| `VITALITY_CAMPFIRE_BONUS_PER` | 1 | +1 campfire heal per this many VIT |

### Luck

| Constant | Value | Purpose |
|----------|-------|---------|
| `CRIT_CHANCE_PER_LUCK` | 0.01 | Crit chance per Luck point (1%) |
| `CRIT_DAMAGE_MULT` | 1.5 | Critical hit damage multiplier |
| `LUCK_HARVEST_CHANCE` | 0.005 | Extra harvest chance per Luck point |

### General

| Constant | Value | Purpose |
|----------|-------|---------|
| `STAT_POINTS_PER_LEVEL` | 3 | Stat points per level-up |
| `PLAYER_BASE_SPEED` | 100.0 | Base movement speed (px/s) |
| `MOVEMENT_ACCEL_MULT` | 10 | Movement acceleration responsiveness |
| `SPRITE_FLIP_THRESHOLD` | 5.0 | Velocity threshold for sprite flip |

## Sleep / Time Controls (`game_controller.py` → `data/day_night.py` → `core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SLEEP_DURATION` | 5.0 | Sleep animation duration (seconds) |
| `SLEEP_SPEED_MULT` | 12.0 | Time advancement multiplier while sleeping |
| `BED_INTERACT_RANGE` | 50.0 | Bed interaction range (px) |
| `TIME_SPEED_NORMAL` | 1.0 | Normal time speed multiplier |
| `NIGHT_SLEEP_SPEED_MULT` | 12.0 | Backward compat alias for SLEEP_SPEED_MULT |

## World Generation (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `ELEVATION_SCALE` | 0.045 | Perlin noise scale for elevation |
| `MOISTURE_SCALE` | 0.06 | Perlin noise scale for moisture |
| `MOISTURE_OFFSET` | 500.0 | Offset between elevation/moisture noise |
| `ELEVATION_OCTAVES` | 6 | Octaves for elevation noise |
| `MOISTURE_OCTAVES` | 4 | Octaves for moisture noise |

## Building System (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `WALL_HP` | 100 | Wood wall hit points |
| `TURRET_HP` | 80 | Turret hit points |
| `TURRET_RANGE` | 200.0 | Turret detection range |
| `TURRET_DAMAGE` | 8 | Turret damage per shot |
| `TURRET_COOLDOWN` | 1.5 | Turret fire cooldown |
| `CHEST_CAPACITY` | 96 | Chest storage slots |
| `REPAIR_RANGE` | 60.0 | Max distance to repair a structure with hammer |
| `CAMPFIRE_BASE_HEAL` | 2 | Base HP healed per tick near campfire |
| `CAMPFIRE_HEAL_RADIUS` | 120.0 | Proximity radius for campfire healing (px) |
| `CAMPFIRE_HEAL_INTERVAL` | 1.0 | Seconds between campfire heal ticks |
| `VITALITY_CAMPFIRE_BONUS_PER` | 1 | +1 heal per this many vitality points |
| `TRAP_HP` | 40 | Spike trap hit points |
| `BED_HP` | 80 | Bed hit points |
| `CAMPFIRE_HP` | 60 | Campfire hit points |
| `CHEST_HP_VALUE` | 60 | Chest hit points |
| `DOOR_HP` | 50 | Door hit points |
| `DOOR_COLLIDER_W` | 24 | Door collider width |
| `DOOR_COLLIDER_H` | 32 | Door collider height |
| `STONE_WALL_HP_MULT` | 1.5 | Stone wall HP multiplier (×WALL_HP) |
| `ENCHANT_TABLE_CAPACITY` | 9 | Enchantment table storage slots |
| `ENCHANT_TABLE_HP` | 60 | Enchantment table hit points |
| `CAMPFIRE_LIGHT_RADIUS` | 180 | Campfire light radius in px |
| `BEACON_LIGHT_RADIUS` | 720 | Beacon gameplay influence radius in px for AI / beacon-zone logic |
| `BEACON_VISUAL_LIGHT_RADIUS` | 320 | Beacon on-screen lighting radius in px so night remains visibly dark outside the beacon area |
| `STONE_OVEN_LIGHT_RADIUS` | 120 | Stone oven light radius (only when burning) |
| `BEACON_HP` | 120 | Beacon hit points |
| `BEACON_ATTRACT_RADIUS` | 1440.0 | Distance enemies start moving toward beacon at night |
| `BEACON_ATTRACT_SPEED_OUTSIDE` | 0.3 | Speed mult for enemies outside beacon light |
| `BEACON_ATTRACT_SPEED_INSIDE` | 0.5 | Speed mult for enemies inside beacon light |
| `STONE_OVEN_HP` | 80 | Stone oven hit points |
| `STONE_OVEN_SLOTS` | 4 | Number of slots in stone oven (2×2 grid) |
| `TORCH_LIGHT_RADIUS` | 120 | Placed torch light radius in px |

## Enhancement Scaling (`game_controller.py` → `core/enhancement.py`)

Single source of truth for all enhancement-level scaling. Control variables declared in `game_controller.py`, builder functions in `core/enhancement.py`. Turrets get BOTH offense (damage) AND defense (DR) bonuses.

### Control Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `OFFENSE_BONUS_PER_LEVEL` | 2 | +damage per enhancement level for melee weapons |
| `RANGED_OFFENSE_BONUS_PER_LEVEL` | 2 | +damage per enhancement level for ranged weapons |
| `DEFENSE_BONUS_PER_LEVEL` | 2 | +DR per enhancement level for armor/shields |
| `TURRET_OFFENSE_BONUS_PER_LEVEL` | 2 | +damage per enhancement level for turrets |
| `TURRET_DEFENSE_BONUS_PER_LEVEL` | 2 | +DR per enhancement level for turrets (mobs attacking) |
| `PROTECTION_DR_PER_LEVEL` | 2 | +DR per protection enchant level (stacks with above) |
| `ENHANCEMENT_COLORS` | {1:green,2:blue,3:purple,4:gold,5:red} | Color-coded borders for enhancement levels |

### Ranged Enhancement Damage

| Weapon | Base | +1 | +2 | +3 | +4 | +5 |
|--------|------|----|----|----|----|---- |
| Bow | 18 | 20 | 22 | 24 | 26 | 28 |
| Crossbow | 28 | 30 | 32 | 34 | 36 | 38 |
| Sling | 12 | 14 | 16 | 18 | 20 | 22 |

### Turret Enhancement Damage (`TURRET_ENHANCE_DAMAGE`)

| Level | 0 | 1 | 2 | 3 | 4 | 5 |
|-------|---|---|---|---|---|---|
| Damage | 8 | 10 | 12 | 14 | 16 | 18 |

### Turret Enhancement HP (`TURRET_ENHANCE_HP`)

| Level | 0 | 1 | 2 | 3 | 4 | 5 |
|-------|---|---|---|---|---|---|
| HP | 80 | 96 | 112 | 136 | 160 | 192 |

### Turret Enhancement DR (`TURRET_ENHANCE_DR`)

| Level | 0 | 1 | 2 | 3 | 4 | 5 |
|-------|---|---|---|---|---|---|
| DR | 0 | 2 | 4 | 6 | 8 | 10 |

### Turret Total DR Examples (Enhancement + Protection Enchant)

| Turret +5 | +5 only | +5 + Prot I | +5 + Prot III | +5 + Prot V |
|-----------|---------|-------------|---------------|-------------|
| Total DR | 10 | 12 | 16 | 20 |

## Wave System (`game_controller.py` → `data/day_events.py` → `core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `WAVE_START_NIGHT` | 1 | Night count before waves begin |
| `WAVE_BASE_COUNT` | 3 | Base enemies per wave |
| `WAVE_SCALE_PER_NIGHT` | 2 | Additional enemies per night |
| `WAVE_SPAWN_RADIUS` | 350.0 | Spawn distance from target |
| `WAVE_SPAWN_RADIUS_VARIANCE` | 100.0 | Spawn radius jitter for waves |
| `WAVE_DAY_BONUS_PER_DAY` | 1 | Bonus mobs per day on top of night scaling |
| `WAVE_SPAWN_INITIAL_INTERVAL` | 2.0 | Seconds between batches at start |
| `WAVE_SPAWN_MIN_INTERVAL` | 0.8 | Fastest possible spawn interval |
| `WAVE_INTERVAL_REDUCTION` | 0.1 | Seconds shaved per qualifying night |
| `WAVE_SPAWN_BATCH` | 3 | Mobs per batch tick |
| `WAVE_RANGED_MOB_CHANCE` | 0.25 | Chance a wave mob is ranged |

## Day/Night Timing (`game_controller.py` → `data/day_night.py` → `core/constants.py`)

All time-of-day values are set in `game_controller.py` as `(hour, minute)` tuples on a 24-hour clock.
Engine fractions (`TIME_*`) are auto-derived — never edit them directly.

### Cycle Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `DAY_LENGTH_BASE` | 960.0 | Full day-night cycle length (seconds). 16 real minutes = 1 game day |

### Period Schedule (24-hour clock)

| Period | Begins At | Variable | Engine Fraction |
|--------|-----------|----------|-----------------|
| Dawn | 05:17 | `DAWN_BEGINS = (5, 17)` | `TIME_NIGHT_END ≈ 0.2201` |
| Day | 07:12 | `DAY_BEGINS = (7, 12)` | `TIME_DAY_START = 0.3000` |
| Dusk | 16:48 | `DUSK_BEGINS = (16, 48)` | `TIME_DAY_END = 0.7000` |
| Night | 18:43 | `NIGHT_BEGINS = (18, 43)` | `TIME_NIGHT_START ≈ 0.7799` |

To change when a period starts, edit the `(hour, minute)` tuple in `game_controller.py`.

### Banner / Flash Constants

Each period transition shows a banner. The time each appears is the period threshold above.

| Constant | Value | Purpose |
|----------|-------|---------|
| `DAY_FLASH_TEXT` | "Day {day}" | Banner at DAY_BEGINS (07:12) |
| `DAY_FLASH_DURATION` | 3.0 | Seconds visible |
| `DAY_FLASH_FADE_DIVISOR` | 1.0 | Alpha = timer / this (lower = fades slower) |
| `DAY_FLASH_COLOR` | (255, 255, 200) | Banner text colour |
| `NIGHT_FLASH_TEXT` | "Night falls — Defend!" | Banner at NIGHT_BEGINS (18:43) |
| `NIGHT_FLASH_DURATION` | 2.5 | Seconds visible |
| `NIGHT_FLASH_FADE_DIVISOR` | 0.8 | Alpha control |
| `NIGHT_FLASH_COLOR` | (255, 120, 80) | Night warning colour |
| `DAWN_FLASH_TEXT` | "" | Banner at DAWN_BEGINS (empty = disabled) |
| `DAWN_FLASH_DURATION` | 2.0 | Seconds visible |
| `DAWN_FLASH_COLOR` | (255, 220, 150) | Dawn message colour |
| `DUSK_FLASH_TEXT` | "Dusk approaches..." | Banner at DUSK_BEGINS (16:48) |
| `DUSK_FLASH_DURATION` | 2.0 | Seconds visible |
| `DUSK_FLASH_COLOR` | (255, 180, 100) | Dusk message colour |
| `SLEEP_OVERLAY_TEXT` | "Sleeping... Zzz" | Sleeping overlay text |
| `SLEEP_OVERLAY_COLOR` | (180, 180, 255) | Sleeping overlay colour |
| `NIGHT_DARKNESS_THRESHOLD` | 0.5 | Darkness level above which night damage applies |

### AI Aggro (`systems.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `AGGRO_DISENGAGE_MULT` | 2.0 | Chase disengage range multiplier when aggroed |
| `AGGRO_BOSS_DISENGAGE_MULT` | 3.0 | Chase disengage multiplier for boss mobs |

### Day/Night Periods

| Period | Clock Time | Engine Range | Description |
|--------|-----------|--------------|-------------|
| Night | 00:00–05:17, 18:43–24:00 | 0.00–0.22, 0.78–1.00 | Dark, enemies deal night damage to unlit players |
| Dawn | 05:17–07:12 | 0.22–0.30 | Transition, lighting ramps up |
| Day | 07:12–16:48 | 0.30–0.70 | Full daylight |
| Dusk | 16:48–18:43 | 0.70–0.78 | "Dusk approaches..." warning displayed |

### Key Methods (`DayNightCycle` in `systems.py`)

| Method | Logic |
|--------|-------|
| `is_night()` | `t < TIME_NIGHT_END or t >= TIME_NIGHT_START` |
| `is_sleepable()` | `t < TIME_NIGHT_END or t >= TIME_DAY_END` (allows sleep during Dusk+Night) |
| `day_changed` | `bool` flag — True the frame day_number increments, False otherwise |

## Difficulty System (`game_controller.py` → `data/difficulty.py` → `core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `DIFFICULTY_EASY` | 0 | Easy difficulty index |
| `DIFFICULTY_NORMAL` | 1 | Normal difficulty index |
| `DIFFICULTY_HARD` | 2 | Hard difficulty index |
| `DIFFICULTY_HARDCORE` | 3 | Hardcore difficulty index |
| `DIFFICULTY_NAMES` | ("Easy", "Normal", "Hard", "Hardcore") | Display names |

### Difficulty Profiles (`DIFFICULTY_PROFILES`)

Full dict-based profiles with named keys. Access: `DIFFICULTY_PROFILES[level]['enemy_hp_mult']` or use `get_profile(level)`.

| Key | Easy | Normal | Hard | Hardcore | Purpose |
|-----|------|--------|------|----------|---------|
| `enemy_hp_mult` | 1.0 | 1.3 | 1.8 | 3.5 | Multiplier on mob base HP |
| `enemy_dmg_mult` | 1.0 | 1.3 | 1.8 | 3.0 | Multiplier on mob base damage |
| `enemy_hp_per_day` | 0.03 | 0.05 | 0.08 | 0.12 | Daily mob HP growth (HP *= 1 + day × this) |
| `enemy_dmg_per_day` | 0.02 | 0.05 | 0.08 | 0.10 | Daily mob DMG growth (DMG *= 1 + day × this) |
| `boss_hp_mult` | 1.0 | 1.0 | 1.3 | 2.0 | Boss HP multiplier (stacks with enemy_hp) |
| `boss_dmg_mult` | 1.0 | 1.0 | 1.2 | 1.5 | Boss damage multiplier (stacks with enemy_dmg) |
| `boss_hp_per_day` | 0.02 | 0.04 | 0.06 | 0.10 | Daily boss HP growth (on top of enemy growth) |
| `boss_dmg_per_day` | 0.01 | 0.03 | 0.05 | 0.08 | Daily boss DMG growth (on top of enemy growth) |
| `spawn_rate_mult` | 1.0 | 1.2 | 1.5 | 4.0 | Mob respawn frequency multiplier |
| `wave_count_mult` | 1.0 | 1.3 | 1.8 | 4.0 | Night wave mob count multiplier |
| `night_dmg_mult` | 1.0 | 1.0 | 1.5 | 2.0 | Night darkness damage multiplier |
| `night_dmg_per_day` | 0.0 | 0.5 | 1.0 | 2.0 | Flat night damage added per day |
| `night_dmg_tick_min` | 1 | 1 | 2 | 5 | Minimum night damage per tick (floor) |
| `night_dmg_tick_max` | 0 | 0 | 0 | 0 | Maximum night damage per tick (0 = no cap) |
| `xp_mult` | 1.0 | 1.0 | 1.2 | 1.5 | XP earned multiplier |
| `loot_luck_bonus` | 0.0 | 0.0 | 0.0 | 0.0 | Flat bonus to rarity roll weights |
| `night_damage_multiplier` | 1 | 2 | 3 | 4 | Enemy damage mult at night when NOT in light |

### Resource Respawn (`RESOURCE_RESPAWN_DAYS`)

Controls how often overworld trees and rocks replenish (per difficulty).

| Difficulty | Days | Behaviour |
|-----------|------|-----------|
| Easy | 3 | Every 3 days |
| Normal | 7 | Every 7 days |
| Hard | 14 | Every 14 days |
| Hardcore | 0 | Never — resources are finite |

Tracked via `Game._last_resource_respawn_day` (saved/loaded).
`game/entities.py: respawn_resources()` places new trees/rocks at seed-consistent positions, skipping tiles already occupied.

### Legacy Tuple Format (`DIFFICULTY_MULTIPLIERS`)

Backward-compatible: `(enemy_hp_mult, enemy_dmg_mult, spawn_rate_mult, wave_count_mult)` — derived from profiles.

| Difficulty | HP Mult | DMG Mult | Spawn Mult | Wave Mult |
|-----------|---------|----------|------------|-----------|
| Easy | 1.0 | 1.0 | 1.0 | 1.0 |
| Normal | 1.3 | 1.3 | 1.2 | 1.3 |
| Hard | 1.8 | 1.8 | 1.5 | 1.8 |
| Hardcore | 3.5 | 3.0 | 4.0 | 4.0 |

### Difficulty Profile Consumers

| Multiplier | Applied in | How |
|------------|-----------|-----|
| `enemy_hp_mult` / `enemy_hp_per_day` | `game/entities.py: create_mob()` | Scales HP: `base * enemy_hp_mult * (1 + days * enemy_hp_per_day)` |
| `enemy_dmg_mult` / `enemy_dmg_per_day` | `game/entities.py: create_mob()` | Scales DMG: `base * enemy_dmg_mult * (1 + days * enemy_dmg_per_day)` |
| `boss_hp_mult` / `boss_hp_per_day` | `game/entities.py: create_mob()` | Additional scale inside boss block (stacks with enemy growth) |
| `boss_dmg_mult` / `boss_dmg_per_day` | `game/entities.py: create_mob()` | Additional scale inside boss block |
| `spawn_rate_mult` | `sandbox_rpg.py` (respawn) | Divides `MOB_RESPAWN_INTERVAL` |
| `wave_count_mult` | `systems/wave.py` | Multiplies wave mob count |
| `night_dmg_mult` / `night_dmg_per_day` | `game/combat.py: night_damage()` | Multiplies + adds flat per-day to night damage |
| `night_dmg_tick_min` / `night_dmg_tick_max` | `game/combat.py: night_damage()` | Enforces min/max bounds on night tick damage |
| `xp_mult` | `game/entities.py: on_mob_killed()` | Multiplies XP before `check_level_up()` |
| `loot_luck_bonus` | Wired into `roll_rarity()` via `roll_loot(luck_bonus=)` | Multiplies non-common rarity weights by `(1 + luck_bonus)` |

## Mob Respawn (`game_controller.py` → `data/day_events.py` → `core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `MOB_RESPAWN_INTERVAL` | 4.0 | Seconds between natural mob respawns |
| `MOB_RESPAWN_MIN_DIST` | 300.0 | Minimum spawn distance from player (px) |
| `MOB_MAX_COUNT` | 80 | Max mobs alive at once |
| `MOB_RESPAWN_BATCH` | 3 | Mobs to spawn per respawn tick |

## Ranged Enemies (`game_controller.py` → `data/day_events.py` → `core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `RANGED_ENEMY_START_DAY` | 3 | Day after which ranged enemies appear |

## Placement Preview (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `PLACEMENT_PREVIEW_COLOR` | (60, 220, 80, 120) | Valid placement ghost color |
| `PLACEMENT_INVALID_COLOR` | (220, 60, 60, 120) | Invalid placement ghost color |

## Font Sizes (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `FONT_SIZE_MAIN` | 16 | Main UI font size |
| `FONT_SIZE_SM` | 13 | Small font size |
| `FONT_SIZE_LG` | 22 | Large font size |
| `FONT_SIZE_XL` | 48 | Extra-large font size |

## Player Constants (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `PLAYER_BASE_SPEED` | 100.0 | Base movement speed (px/s) |
| `PLAYER_FRICTION` | 0.82 | Movement friction factor (frame-rate-independent via `pow(friction, dt * FPS)` in MovementSystem) |
| `PLAYER_COLLIDER_W` | 20 | Player collider width |
| `PLAYER_COLLIDER_H` | 28 | Player collider height |
| `AGI_SPEED_BONUS` | 0.01 | Speed bonus per agility point (re-exported from data/stats.py) |
| `AGI_SPEED_BONUS_CAP` | 1.0 | Max speed bonus cap (re-exported from data/stats.py) |
| `MOVEMENT_ACCEL_MULT` | 10 | Movement acceleration multiplier |
| `SPRITE_FLIP_THRESHOLD` | 5.0 | Velocity threshold for sprite flip |
| `STARTING_WOOD` | 5 | Starting wood count |
| `STARTING_STONE` | 3 | Starting stone count |
| `PLAYER_TORCH_LIGHT_RADIUS` | 110 | Light radius when holding torch |

## Melee / Ranged Combat Tuning (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SPEAR_ATTACK_RANGE` | 65.0 | Spear attack range (px) |
| `WEAPON_ATTACK_RANGE` | 55.0 | Standard weapon attack range (px) |
| `UNARMED_ATTACK_RANGE` | 38.0 | Unarmed attack range (px) |
| `MELEE_KNOCKBACK_FORCE` | 200.0 | Knockback force from melee hits |
| `ATTACK_ANIM_DURATION` | 0.18 | Attack animation duration (seconds) |
| `INTERACT_COOLDOWN` | 0.25 | Interaction cooldown (seconds) |

## Contact / Projectile Damage (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `CONTACT_DAMAGE_RADIUS` | 28.0 | Contact damage detection radius |
| `PLAYER_HIT_INVULN` | 0.5 | Invulnerability after being hit (seconds) |
| `DAMAGE_FLASH_DURATION` | 0.15 | Damage flash visual duration |
| `HIT_SHAKE_AMOUNT` | 4.0 | Screen shake on melee hit |
| `HIT_SHAKE_DURATION` | 0.2 | Shake duration on melee hit |
| `ENEMY_PROJ_HIT_RADIUS` | 20.0 | Enemy projectile hit detection radius |
| `PROJ_SHAKE_AMOUNT` | 3.0 | Screen shake on projectile hit |
| `PROJ_SHAKE_DURATION` | 0.15 | Shake duration on projectile hit |

## Night Damage (`data/day_night.py`, re-exported via `constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `NIGHT_DAMAGE_BASE` | 2 | Starting HP per tick on day 1 |
| `NIGHT_DAMAGE_INCREASE` | 1 | Extra HP added per scaling step |
| `NIGHT_DAMAGE_INCREASE_FREQ` | 1 | Add INCREASE every N days |
| `NIGHT_DAMAGE_INTERVAL` | 3.0 | Seconds between night damage ticks |
| `LIGHT_SAFETY_RADIUS` | 200.0 | Safe radius around light sources |

Night damage formula: `(NIGHT_DAMAGE_BASE + NIGHT_DAMAGE_INCREASE * ((day - 1) // NIGHT_DAMAGE_INCREASE_FREQ)) * night_dmg_mult`
Fire enchant on equipped weapon (hotbar or equipment slot) counts as a light source.

## Interaction Ranges (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `INTERACT_RANGE` | 50.0 | General interaction range |
| `HARVEST_RANGE` | 50.0 | Resource harvesting range |
| `BED_INTERACT_RANGE` | 50.0 | Bed interaction range |
| `LUCK_HARVEST_CHANCE` | 0.005 | Per-luck-point bonus harvest chance (re-exported from data/stats.py) |

## Mob Spawning Tuning (`data/day_events.py`, re-exported via `constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `PER_DAY_SCALE_FACTOR` | 0.05 | Mob scaling per day elapsed |
| `MOB_SPAWN_ATTEMPTS` | 20 | Max spawn placement attempts |
| `GHOST_SPAWN_CHANCE` | 0.25 | Chance to spawn ghost at night |
| `NIGHT_MOB_SPAWN_CHANCE` | 0.4 | General night spawn chance |
| `DARK_KNIGHT_SPAWN_CHANCE` | 0.15 | Dark knight spawn chance |
| `FOREST_MOB_SPAWN_CHANCE` | 0.5 | Forest biome mob spawn chance |
| `DIRT_MOB_SPAWN_CHANCE` | 0.4 | Dirt biome mob spawn chance |
| `ORC_SPAWN_CHANCE` | 0.2 | Orc spawn chance on dirt |
| `GRASS_MOB_SPAWN_CHANCE` | 0.4 | Grass biome mob spawn chance |

## World Population (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `TREE_COUNT` | 350 | Trees on grass/dirt |
| `FOREST_TREE_COUNT` | 150 | Extra trees in forest |
| `ROCK_COUNT` | 200 | Rock nodes on map |

## Level Up (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `LEVEL_UP_BASE_HP` | 10 | Base HP increase per level |
| `VIT_HP_BONUS_PER_LEVEL` | 5 | Extra HP per vitality point on level up |

## HUD (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `NOTIFICATION_DURATION` | 2.5 | Notification display time (seconds) |
| `HUD_REFRESH_INTERVAL` | 0.5 | HUD text refresh interval |
| `DMG_NUMBER_FLOAT_SPEED` | 40.0 | Damage number float-up speed |
| `MOB_HP_BAR_W` | 28 | Mob HP bar width |
| `MOB_HP_BAR_H` | 4 | Mob HP bar height |
| `PLACEABLE_HP_BAR_W` | 28 | Placeable HP bar width |
| `PLACEABLE_HP_BAR_H` | 3 | Placeable HP bar height |
| `HOTBAR_SLOTS` | 6 | Number of hotbar slots |
| `HOTBAR_SLOT_SIZE` | 48 | Hotbar slot pixel size |
| `HOTBAR_SLOT_GAP` | 6 | Gap between hotbar slots |

### HUD Layout (`game/drawing.py`)
- HUD background box: (12, 10) size 250×88 → bottom at y=98
- HP text at (24, 17), XP at (24, 39), Resources at (20, 58), Day/Kills at (20, 74)
- Active buffs + spell cooldowns start at y=104 (below HUD box), 16px spacing per line
- Buffs and cooldowns NEVER overlap HUD info or each other

## Window Limits (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `MIN_WINDOW_WIDTH` | 640 | Minimum window width |
| `MIN_WINDOW_HEIGHT` | 480 | Minimum window height |

## Initial Mob Population (`data/day_events.py`, re-exported via `constants.py`)

Format: `(mob_type, required_tile, count)`

| Mob Type | Tile | Count |
|----------|------|-------|
| slime | TILE_GRASS | 25 |
| wolf | TILE_FOREST | 10 |
| spider | TILE_FOREST | 8 |
| goblin | TILE_DIRT | 5 |

---

## Mob Types (`items_data.py: MOB_DATA`)

| Mob Type | HP | Speed | Detection | Damage | XP | Solid | Ranged | Boss |
|----------|-----|-------|-----------|--------|-----|-------|--------|------|
| slime | 30 | 35 | 180 | 5 | 15 | Yes | No | No |
| skeleton | 60 | 50 | 220 | 10 | 35 | Yes | No | No |
| wolf | 40 | 65 | 160 | 8 | 25 | Yes | No | No |
| goblin | 50 | 45 | 200 | 12 | 40 | Yes | No | No |
| ghost | 35 | 40 | 250 | 6 | 50 | No | No | No |
| spider | 25 | 55 | 140 | 7 | 20 | Yes | No | No |
| orc | 90 | 38 | 180 | 16 | 60 | Yes | No | No |
| dark_knight | 120 | 42 | 200 | 20 | 80 | Yes | No | No |
| zombie | 70 | 30 | 160 | 14 | 35 | Yes | No | No |
| wraith | 55 | 52 | 280 | 10 | 55 | No | No | No |
| troll | 150 | 28 | 160 | 22 | 75 | Yes | No | No |
| skeleton_archer | 50 | 35 | 260 | 8 | 45 | Yes | Yes | No |
| goblin_shaman | 45 | 32 | 240 | 6 | 50 | Yes | Yes | No |
| boss_golem | 400 | 22 | 300 | 35 | 250 | Yes | No | Yes |
| boss_lich | 300 | 35 | 350 | 28 | 300 | Yes | Yes | Yes |
| boss_dragon | 500 | 30 | 350 | 40 | 350 | Yes | Yes | Yes |
| boss_necromancer | 280 | 38 | 320 | 24 | 280 | Yes | Yes | Yes |
| boss_troll_king | 600 | 20 | 280 | 45 | 400 | Yes | No | Yes |

### Ranged Mob Stats

| Mob Type | Ranged DMG | Range | Cooldown | Speed |
|----------|-----------|-------|----------|-------|
| skeleton_archer | 12 | 250.0 | 2.0 | 350.0 |
| goblin_shaman | 15 | 220.0 | 2.5 | 300.0 |
| boss_lich | 25 | 300.0 | 1.8 | 400.0 |
| boss_dragon | 35 | 320.0 | 1.5 | 450.0 |
| boss_necromancer | 20 | 280.0 | 2.0 | 350.0 |

### Boss Glow Colors

| Boss | Glow Color |
|------|-----------|
| boss_golem | (255, 60, 60) |
| boss_lich | (200, 60, 255) |
| boss_dragon | (255, 140, 30) |
| boss_necromancer | (60, 255, 80) |
| boss_troll_king | (80, 200, 60) |

## Wave Mob Tiers (`items_data.py`)

| Tier | Label | Mobs |
|------|-------|------|
| 0 | Easy | slime, spider |
| 1 | Medium | skeleton, wolf, goblin, zombie |
| 2 | Hard | orc, wraith |
| 3 | Elite | dark_knight, troll |

Ranged wave mobs (after Day 3): skeleton_archer, goblin_shaman
Boss wave mobs: boss_golem, boss_lich, boss_dragon, boss_necromancer, boss_troll_king

---

## Item IDs (`items_data.py: ITEM_DATA`)

Format: `(name, description, damage, harvest_bonus, heal, placeable)`

### Materials
| ID | Name | Notes |
|----|------|-------|
| wood | Wood | Basic building material |
| stone | Stone | Hard and durable |
| stick | Stick | 3 dmg weak weapon |
| iron | Iron Ingot | Smelted metal |
| cloth | Cloth | Woven fabric |
| bone | Bone | Dropped by skeletons |
| leather | Leather | Animal hide |
| diamond | Diamond | Precious gemstone (rare) |
| gunpowder | Gunpowder | Explosive powder |
| iron_ore | Iron Ore | Raw iron, found in caves |
| brilliant_diamond | Brilliant Diamond | Crafted from 9 diamonds |
| titanium_ore | Titanium Ore | Rare ore, found in caves |
| titanium_ingot | Titanium Ingot | Smelted titanium |

### Consumables
| ID | Name | Heal | Notes |
|----|------|------|-------|
| berry | Berry | 15 | [F] to eat |
| pie | Berry Pie | 40 | [F] to eat |
| bandage | Bandage | 25 | [F] to use |
| health_potion | Health Potion | 80 | [F] to drink |
| antidote | Antidote | 10 | Cures poison |

### Spell Books
| ID | Name |
|----|------|
| spell_fireball | Fireball Tome |
| spell_fireball_2 | Fireball II Tome |
| spell_fireball_3 | Fireball III Tome |
| spell_fireball_4 | Fireball IV Tome |
| spell_fireball_5 | Fireball V Tome |
| spell_heal | Heal Tome |
| spell_heal_2 | Heal II Tome |
| spell_heal_3 | Heal III Tome |
| spell_heal_4 | Heal IV Tome |
| spell_heal_5 | Heal V Tome |
| spell_lightning | Lightning Tome |
| spell_lightning_2 | Lightning II Tome |
| spell_lightning_3 | Lightning III Tome |
| spell_lightning_4 | Lightning IV Tome |
| spell_lightning_5 | Lightning V Tome |
| spell_ice | Ice Tome |
| spell_ice_2 | Ice II Tome |
| spell_ice_3 | Ice III Tome |
| spell_ice_4 | Ice IV Tome |
| spell_ice_5 | Ice V Tome |

### Melee Weapons
| ID | Name | Damage | Harvest Bonus | Harvest Type |
|----|------|--------|---------------|--------------|
| axe | Stone Axe | 12 | +2 | wood |
| sword | Wood Sword | 20 | 0 | all |
| iron_sword | Iron Sword | 30 | 0 | all |
| spear | Spear | 18 | 0 | all |
| iron_axe | Iron Axe | 22 | +4 | wood |
| mace | Iron Mace | 26 | 0 | all |
| bone_club | Bone Club | 14 | 0 | all |
| titanium_axe | Titanium Axe | 33 | +6 | wood |
| diamond_axe | Diamond Axe | 44 | +8 | wood |

### Tools
| ID | Name | Damage | Harvest Bonus | Harvest Type |
|----|------|--------|---------------|--------------|
| hammer | Hammer | 5 | 0 | all |
| pickaxe | Stone Pickaxe | 8 | +2 | stone |
| iron_pickaxe | Iron Pickaxe | 15 | +4 | stone |
| titanium_pickaxe | Titanium Pickaxe | 23 | +6 | stone |
| diamond_pickaxe | Diamond Pickaxe | 30 | +8 | stone |

### Enhanced Weapons (+1 to +5, generated from `core/enhancement.py`)

Control variable: `OFFENSE_BONUS_PER_LEVEL = 2` (+2 damage per enhancement level)

| Base | +1 DMG | +2 DMG | +3 DMG | +4 DMG | +5 DMG |
|------|--------|--------|--------|--------|--------|
| iron_sword (30) | 32 | 34 | 36 | 38 | 40 |
| iron_axe (22) | 24 | 26 | 28 | 30 | 32 |
| mace (26) | 28 | 30 | 32 | 34 | 36 |
| titanium_axe (33) | 35 | 37 | 39 | 41 | 43 |
| diamond_axe (44) | 46 | 48 | 50 | 52 | 54 |
| iron_pickaxe (15) | 17 | 19 | 21 | 23 | 25 |
| titanium_pickaxe (23) | 25 | 27 | 29 | 31 | 33 |
| diamond_pickaxe (30) | 32 | 34 | 36 | 38 | 40 |

IDs: `iron_sword_1`..`iron_sword_5`, `iron_axe_1`..`iron_axe_5`, `mace_1`..`mace_5`, `titanium_axe_1`..`titanium_axe_5`, `diamond_axe_1`..`diamond_axe_5`, `iron_pickaxe_1`..`iron_pickaxe_5`, `titanium_pickaxe_1`..`titanium_pickaxe_5`, `diamond_pickaxe_1`..`diamond_pickaxe_5`

### Ranged Weapons
| ID | Name | Damage | Range | Ammo | Speed | Cooldown |
|----|------|--------|-------|------|-------|----------|
| bow | Bow | 18 | 300.0 | arrow, fire_arrow | 400.0 | 0.6 |
| crossbow | Crossbow | 28 | 350.0 | bolt | 500.0 | 1.2 |
| sling | Sling | 12 | 250.0 | rock_ammo, sling_bullet | 350.0 | 0.5 |

### Ammunition
| ID | Name | Notes |
|----|------|-------|
| arrow | Arrow | Bow ammo |
| fire_arrow | Fire Arrow | +8 damage |
| bolt | Bolt | Crossbow ammo |
| rock_ammo | Rock Ammo | Sling ammo (rough) |
| sling_bullet | Sling Bullet | Sling ammo (+5 dmg) |

### Armor
| ID | Name | DR | Notes |
|----|------|----|-------|
| leather_armor | Leather Armor | 3 | Basic |
| iron_armor | Iron Armor | 6 | Strong |
| wood_shield | Wood Shield | — | Blocks some damage |
| iron_shield | Iron Shield | 4 | Sturdy metal |

### Enhanced Armor (+1 to +5 DR, generated from `core/enhancement.py`)

Control variable: `DEFENSE_BONUS_PER_LEVEL = 2` (+2 DR per enhancement level)

| Base | +1 DR | +2 DR | +3 DR | +4 DR | +5 DR |
|------|-------|-------|-------|-------|-------|
| iron_armor (6) | 8 | 10 | 12 | 14 | 16 |
| iron_shield (4) | 6 | 8 | 10 | 12 | 14 |

IDs: `iron_armor_1`..`iron_armor_5`, `iron_shield_1`..`iron_shield_5`

### Light Sources & Placeables
| ID | Name | Damage | Placeable |
|----|------|--------|-----------|
| torch | Torch | 5 | Yes |
| campfire | Campfire Kit | 0 | Yes |
| trap | Spike Trap | 0 | Yes |
| bed | Bed | 0 | Yes |
| wall | Wood Wall | 0 | Yes |
| stone_wall_b | Stone Wall | 0 | Yes |
| turret | Turret | 0 | Yes |
| chest | Chest | 0 | Yes |
| door | Door | 0 | Yes |
| enchantment_table | Enchantment Table | 0 | Yes |
| greater_enchantment_table | Greater Enchantment Table | 0 | Yes |
| beacon | Beacon | 0 | Yes |
| stone_oven | Stone Oven | 0 | Yes |

### Tools
| ID | Name | Damage | Notes |
|----|------|--------|-------|
| hammer | Hammer | 5 | Repair structures with [F] near damaged |

### Throwables
| ID | Name | Notes |
|----|------|-------|
| bomb | Bomb | Explodes on impact |

### Buff Spell Tomes
| ID | Name |
|----|------|
| spell_regen_1 | Regen I Tome |
| spell_regen_2 | Regen II Tome |
| spell_regen_3 | Regen III Tome |
| spell_regen_4 | Regen IV Tome |
| spell_regen_5 | Regen V Tome |
| spell_protection_1 | Protection I Tome |
| spell_protection_2 | Protection II Tome |
| spell_protection_3 | Protection III Tome |
| spell_protection_4 | Protection IV Tome |
| spell_protection_5 | Protection V Tome |
| spell_strength_1 | Strength I Tome |
| spell_strength_2 | Strength II Tome |
| spell_strength_3 | Strength III Tome |
| spell_strength_4 | Strength IV Tome |
| spell_strength_5 | Strength V Tome |

---

## Spell Data (`spells/: SPELL_DATA`)

### Offensive Spells
**Note**: All spell damage/heal/buff values scale with player level at 2% per level (`SPELL_LEVEL_SCALE_PERCENT`).
Projectile spells auto-target the nearest enemy within 80px of the crosshair click.
Projectile size and explosion effects scale with spell tier (I-V).

| Spell | Type | Damage | Heal | Radius | Speed | Range | Cooldown | Special |
|-------|------|--------|------|--------|-------|-------|----------|---------|
| spell_fireball | projectile | 60 | — | 80.0 | 350.0 | 400.0 | 3.0 | — |
| spell_fireball_2 | projectile | 90 | — | 100.0 | 380.0 | 450.0 | 2.5 | — |
| spell_fireball_3 | projectile | 130 | — | 120.0 | 420.0 | 500.0 | 2.0 | — |
| spell_fireball_4 | projectile | 180 | — | 140.0 | 460.0 | 550.0 | 1.6 | — |
| spell_fireball_5 | projectile | 240 | — | 160.0 | 500.0 | 600.0 | 1.2 | — |
| spell_heal | self | — | 50 | — | — | — | 3.0 | — |
| spell_heal_2 | self | — | 80 | — | — | — | 2.5 | — |
| spell_heal_3 | self | — | 120 | — | — | — | 2.0 | — |
| spell_heal_4 | self | — | 170 | — | — | — | 1.6 | — |
| spell_heal_5 | self | — | 230 | — | — | — | 1.2 | — |
| spell_lightning | projectile | 80 | — | 40.0 | 600.0 | 350.0 | 3.0 | — |
| spell_lightning_2 | projectile | 120 | — | 50.0 | 650.0 | 400.0 | 2.5 | — |
| spell_lightning_3 | projectile | 170 | — | 60.0 | 700.0 | 450.0 | 2.0 | — |
| spell_lightning_4 | projectile | 230 | — | 70.0 | 750.0 | 500.0 | 1.6 | — |
| spell_lightning_5 | projectile | 300 | — | 80.0 | 800.0 | 550.0 | 1.2 | — |
| spell_ice | projectile | 45 | — | 60.0 | 280.0 | 300.0 | 3.0 | slow 3s ×0.4 |
| spell_ice_2 | projectile | 70 | — | 70.0 | 310.0 | 350.0 | 2.5 | slow 4s ×0.3 |
| spell_ice_3 | projectile | 100 | — | 80.0 | 340.0 | 400.0 | 2.0 | slow 5s ×0.2 |
| spell_ice_4 | projectile | 140 | — | 90.0 | 370.0 | 450.0 | 1.6 | slow 6s ×0.15 |
| spell_ice_5 | projectile | 190 | — | 100.0 | 400.0 | 500.0 | 1.2 | slow 7s ×0.1 |

### Buff Spells
| ID | Effect | Level | Duration | Value | Cooldown |
|----|--------|-------|----------|-------|----------|
| spell_regen_1 | regen | 1 | 30.0s | 2 HP/sec | 5.0 |
| spell_regen_2 | regen | 2 | 30.0s | 4 HP/sec | 5.0 |
| spell_regen_3 | regen | 3 | 30.0s | 6 HP/sec | 5.0 |
| spell_regen_4 | regen | 4 | 30.0s | 9 HP/sec | 5.0 |
| spell_regen_5 | regen | 5 | 30.0s | 12 HP/sec | 5.0 |
| spell_protection_1 | protection | 1 | 60.0s | 2 DR | 5.0 |
| spell_protection_2 | protection | 2 | 75.0s | 4 DR | 5.0 |
| spell_protection_3 | protection | 3 | 90.0s | 6 DR | 5.0 |
| spell_protection_4 | protection | 4 | 105.0s | 9 DR | 5.0 |
| spell_protection_5 | protection | 5 | 120.0s | 12 DR | 5.0 |
| spell_strength_1 | strength | 1 | 60.0s | +3 DMG | 5.0 |
| spell_strength_2 | strength | 2 | 60.0s | +6 DMG | 5.0 |
| spell_strength_3 | strength | 3 | 60.0s | +10 DMG | 5.0 |
| spell_strength_4 | strength | 4 | 60.0s | +15 DMG | 5.0 |
| spell_strength_5 | strength | 5 | 60.0s | +20 DMG | 5.0 |
| spell_levitate_1 | levitate | 1 | 30.0s | on/off | 5.0 |
| spell_levitate_2 | levitate | 2 | 45.0s | on/off | 5.0 |
| spell_levitate_3 | levitate | 3 | 60.0s | on/off | 5.0 |
| spell_levitate_4 | levitate | 4 | 75.0s | on/off | 5.0 |
| spell_levitate_5 | levitate | 5 | 90.0s | on/off | 5.0 |

### Teleport Spells
| ID | Type | Cooldown | Effect |
|----|------|----------|--------|
| spell_return_1 | teleport_bed | 600.0 | Teleport to bed |
| spell_return_2 | teleport_bed | 480.0 | Teleport to bed |
| spell_return_3 | teleport_bed | 360.0 | Teleport to bed |
| spell_return_4 | teleport_bed | 240.0 | Teleport to bed |
| spell_return_5 | teleport_bed | 120.0 | Teleport to bed |

### Terrain Speed Modifiers
| Constant | Value | Tile |
|----------|-------|------|
| TERRAIN_SPEED_SAND | 0.7 | TILE_SAND |
| TERRAIN_SPEED_WATER | 0.5 | TILE_WATER |
| TERRAIN_SPEED_DIRT | 0.9 | TILE_DIRT |

## Bomb Data (`items_data.py: BOMB_DATA`)

| ID | Damage | Radius | Speed | Range | Fuse |
|----|--------|--------|-------|-------|------|
| bomb | 50 | 80.0 | 300.0 | 250.0 | 0.0 |

## Quality / Rarity System (`game_controller.py` → `data/quality.py`)

### Rarity Tiers

Rarity is a **per-slot attribute** independent of enhancement (+1..+5) and enchantment. It multiplies base stats of equipment items. All tier constants are declared in `game_controller.py`.

**CRITICAL**: `None` is NEVER a valid rarity value. All items always have a rarity; the baseline is `'common'`. The canonical normalisation function is `core.item_stack.normalize_rarity()` which maps falsy values → `'common'`. All stacking, sorting, transfer, save/load, and display code must go through this normalisation.

**Display Contract**: Rarity is styling and metadata, not part of the canonical item label. Visible item labels are built centrally in `core/item_presentation.py` as:
- effect prefix
- base item name
- upgrade suffix (`+N`)

Example: `Flaming V Iron Axe +5`

Rarity appears through colour, border, and the dedicated tooltip line `Rarity: <Tier>`.

| Tier | Color Constant | RGB | Stat Multiplier |
|------|---------------|-----|-----------------|
| common | `RARITY_COLOR_COMMON` | (255, 255, 255) | 1.0× (100%) |
| rare | `RARITY_COLOR_RARE` | (80, 140, 255) | 1.5× (150%) |
| epic | `RARITY_COLOR_EPIC` | (180, 60, 255) | 2.0× (200%) |
| legendary | `RARITY_COLOR_LEGENDARY` | (255, 215, 0) | 2.5× (250%) |
| mythic | `RARITY_COLOR_MYTHIC` | (255, 50, 50) | 3.0× (300%) |

### Derived Dicts (game_controller.py)

| Dict | Purpose |
|------|---------|
| `RARITY_COLORS` | Maps tier string → RGB tuple, built from individual color constants |
| `RARITY_MULTIPLIERS` | Maps tier string → stat multiplier |
| `RARITY_ELIGIBLE_CATEGORIES` | frozenset of categories that can bear rarity |

### Rarity Functions (`data/quality.py`)

| Function | Purpose |
|----------|---------|
| `get_rarity_color(rarity)` | Returns RGB tuple for tier (default White) |
| `get_rarity_multiplier(rarity)` | Returns float multiplier (default 1.0) |
| `next_rarity(rarity)` | Returns next tier or None if mythic |
| `get_item_color(item_id, rarity='common')` | Returns display color; rarity overrides intrinsic quality |

### Rarity Stat Effects

All stat applications centralised in `systems/rarity.py`:

| Function | Purpose |
|----------|---------|
| `apply_rarity(base, rarity)` | Returns `int(base * multiplier)`, no-op for common |
| `roll_rarity(item_id, is_boss, rng, luck_bonus=0.0)` | Rolls rarity tier for eligible items, `'common'` for non-eligible |

| System | Usage |
|--------|-------|
| Melee damage (`game/combat.py`) | `base = apply_rarity(base, rarity)` |
| Ranged damage (`game/combat.py`) | `base_ranged = apply_rarity(base_ranged, rarity)` |
| Armor DR (`systems/damage_calc.py`) | `base_dr = apply_rarity(base_dr, rarity)` |
| Shield DR (`systems/damage_calc.py`) | `base_dr = apply_rarity(base_dr, rarity)` |
| Placeable HP (`game/interaction.py`) | `Health(apply_rarity(HP, rarity))` for all placeable types |
| Drop rolling (`drops/__init__.py`) | `roll_rarity(item_id, is_boss, rng, luck_bonus)` |
| Cave chests (`game/entities.py`) | `roll_rarity(item_id, True, rng)` |

### Rarity UI Helpers (`ui/rarity_display.py`)

| Function | Purpose |
|----------|---------|
| `draw_rarity_border(surface, rect, rarity)` | Draws 2px colored border for non-common rarity |
| `insert_rarity_tooltip(lines, colors, rarity)` | Inserts "Rarity: {tier}" line at index 1 |
| `pick_up_rarity(inv, src, slot)` | Moves rarity from slot dict to held_rarity |
| `place_rarity(inv, dst, slot)` | Moves held_rarity into target dict |
| `swap_rarity(inv, target, slot)` | Swaps held_rarity with target dict entry |

### Enhancement Utility Functions (`core/enhancement.py`)

| Function | Purpose |
|----------|---------|
| `get_base_item_id(item_id)` | Strips _N suffix to get base item id (returns unchanged if not enhanced) |
| `get_enhancement_level(item_id)` | Returns enhancement level 0-5 from item_id suffix |
| `enhanced_ranged_damage(base_id, level)` | Returns total ranged weapon damage at enhancement level |
| `build_enhanced_ranged_items()` | Generates ITEM_DATA entries for ranged weapon +1..+5 variants |

### Centralised Item Stack Module (`core/item_stack.py`)

All item identity, stacking, sorting, and transfer logic lives here. Every container (Inventory, Storage, ChestUI) delegates to these functions.

| Function | Purpose |
|----------|---------|
| `normalize_rarity(rarity)` | `None`/`'common'` → `'common'`; others unchanged |
| `items_match(id_a, ench_a, rar_a, id_b, ench_b, rar_b)` | True if two items are identical for stacking |
| `make_stack_key(item_id, ench, rarity)` | Hashable key for grouping identical items |
| `add_to_slots(slots, enchants, rarities, capacity, item_id, enchant, rarity, count, non_stackable=False)` | Add items to any container dict, returns overflow |
| `remove_from_slots(slots, enchants, rarities, item_id, count, ...)` | Remove items from any container dict |
| `sort_slots(slots, enchants, rarities)` | Merge duplicate stacks and compact to contiguous indices |
| `transfer_slot(src_slots, src_ench, src_rar, slot, dst_slots, dst_ench, dst_rar, dst_cap)` | Atomic single-slot transfer between containers |
| `transfer_all(src_slots, src_ench, src_rar, dst_slots, dst_ench, dst_rar, dst_cap)` | Move all items from src to dst |

### Rarity Data Storage

| Location | Field | Type | Purpose |
|----------|-------|------|---------|
| `Inventory` | `slot_rarities` | Dict[int, str] | Main inv slot → rarity tier string |
| `Inventory` | `hotbar_rarities` | Dict[int, str] | Hotbar slot → rarity tier string |
| `Inventory` | `held_rarity` | Optional[str] | Rarity of currently held/dragged item |
| `Equipment` | `rarities` | Dict[str, str] | Equipped slot name → rarity tier string |
| `Storage` | `slot_rarities` | Dict[int, str] | Storage slot → rarity tier string |

### Rarity Save/Load (`game/persistence.py`)

| Save Key | Source |
|----------|--------|
| `inv_rarities` | `{str(k): v for k, v in inv.slot_rarities.items()}` |
| `hotbar_rarities` | `{str(k): v for k, v in inv.hotbar_rarities.items()}` |
| `eq_rarities` | `equipment.rarities` |
| `storage_rarities` | `{str(k): v for k, v in stor.slot_rarities.items()}` (per structure) |

### Rarity Drop Weights (`drops/common.py`)

**Normal Mobs:**

| Tier | Weight |
|------|--------|
| common | 70 |
| rare | 20 |
| epic | 8 |
| legendary | 1.5 |
| mythic | 0.5 |

**Boss Mobs & Cave Chests:**

| Tier | Weight |
|------|--------|
| common | 20 |
| rare | 30 |
| epic | 30 |
| legendary | 15 |
| mythic | 5 |

### Legacy Quality Colors (backward compat)
| Tier | Color | RGB |
|------|-------|-----|
| common | White | (255, 255, 255) |
| rare | Blue | (80, 140, 255) |
| epic | Purple | (180, 60, 255) |

### Rare Items (Blue — intrinsic display, non-equipment)
`iron_sword_1`, `iron_sword_2`, `iron_axe_1`, `iron_axe_2`, `mace_1`, `mace_2`, `iron_armor_1`, `iron_armor_2`, `iron_shield_1`, `iron_shield_2`, `diamond`, `ench_regen_1`, `ench_protection_1`, `ench_strength_1`, `enchant_tome_1`, `enchant_tome_2`

### Epic Items (Purple — intrinsic display, non-equipment)
`iron_sword_3`-`5`, `iron_axe_3`-`5`, `mace_3`-`5`, `iron_armor_3`-`5`, `iron_shield_3`-`5`, `spell_fireball`-`spell_fireball_5`, `spell_heal`-`spell_heal_5`, `spell_lightning`-`spell_lightning_5`, `spell_ice`-`spell_ice_5`, `spell_regen_2`-`5`, `spell_protection_2`-`5`, `spell_strength_2`-`5`, `enchant_tome_3`, `enchant_tome_4`, `enchant_tome_5`

---

## Recipes (`items_data.py: RECIPES`)

### Tools & Melee Weapons
| Result | Cost |
|--------|------|
| Hammer | wood×3, iron×2 |
| Stone Axe | wood×3, stone×2 |
| Wood Sword | wood×5, stick×2, stone×1 |
| Iron Axe | iron×3, wood×2 |
| Iron Sword | iron×4, wood×2 |
| Iron Mace | iron×5, wood×1 |
| Spear | stick×4, stone×2 |
| Bone Club | bone×3, stick×1 |
| Stone Pickaxe | wood×3, stone×3 |
| Iron Pickaxe | iron×3, wood×2 |
| Titanium Pickaxe | titanium_ingot×5, wood×2 |

### Ranged Weapons
| Result | Cost |
|--------|------|
| Bow | wood×5, stick×3 |
| Crossbow | wood×6, iron×3, stick×2 |
| Sling | stick×2, leather×1 |

### Ammunition
| Result | Cost |
|--------|------|
| Arrow ×5 | stick×2, stone×1 |
| Fire Arrow ×3 | arrow×3, torch×1 |
| Bolt ×5 | iron×1, stick×2 |
| Rock Ammo ×5 | stone×3 |
| Sling Bullet ×3 | stone×2, stick×1 |

### Armor
| Result | Cost |
|--------|------|
| Leather Armor | leather×4, stick×2 |
| Iron Armor | iron×6, leather×2 |
| Wood Shield | wood×6, stick×3 |
| Iron Shield | iron×4, wood×2 |

### Consumables
| Result | Cost |
|--------|------|
| Bandage | cloth×2, berry×1 |
| Health Potion | berry×8, stone×2, cloth×1 |
| Antidote | berry×3, bone×1 |

### Utility & Placeables
| Result | Cost |
|--------|------|
| Campfire | wood×5, stone×3 |
| Torch | wood×2, stick×1 |
| Spike Trap | stick×4, stone×3 |
| Bed | wood×8, cloth×3 |

### Buildings
| Result | Cost |
|--------|------|
| Wood Wall | wood×6 |
| Stone Wall | stone×8 |
| Turret | wood×8, stone×5, iron×3 |
| Chest | wood×8, iron×2 |
| Door | wood×4, iron×1 |
| Beacon | wood×25, stone×10 |
| Stone Oven | stone×8, wood×2 |
| Enchantment Table | iron×6, diamond×2, wood×4 |

### Gems & Advanced Materials
| Result | Cost |
|--------|------|
| Brilliant Diamond | diamond×9 |

### Stone Oven Fuel
| Fuel Item | Fuel Units per Item | Notes |
|-----------|--------------------:|-------|
| wood | 5 | Standard fuel |
| stick | 1 | Burns 5× faster than wood |

### Stone Oven Smelting Recipes
| Result | Ore Cost | Fuel Cost | Smelt Time |
|--------|----------|-----------|------------|
| Iron Ingot | iron_ore×1 | 10 fuel units | 10s |
| Titanium Ingot | titanium_ore×1 | 10 fuel units | 30s |

### Stone Oven Cooking Recipes
| Result | Ingredients | Fuel Cost | Cook Time |
|--------|-------------|-----------|-----------|
| Berry Pie | berry×5 | 5 fuel units | 8s |

### Stone Oven Valid Input Categories
Items whose category is `material`, `consumable`, or `ammo` may be placed in the oven.
Gear items (weapon, ranged, armor, shield, spell, tool, etc.) are rejected with "You don't want to burn that."

### Titanium & Diamond Gear
| Result | Cost |
|--------|------|
| Titanium Axe | titanium_ingot×5, wood×2 |
| Diamond Axe | titanium_axe×1, brilliant_diamond×8 |
| Greater Enchantment Table | brilliant_diamond×4, iron×8, wood×6 |

### Material Processing
| Result | Cost |
|--------|------|
| Sticks ×5 | wood×1 |
| Iron Ingot | stone×4, wood×2 |
| Cloth | stick×3, berry×1 |
| Leather | bone×2, berry×1 |

### Throwables
| Result | Cost |
|--------|------|
| Bomb ×1 | gunpowder×2, iron×1 |
| Bomb ×3 | gunpowder×5, iron×2 |

### Armor
leather_armor (3 DR), iron_armor (6 DR), wood_shield, iron_shield (4 DR)

### Placeables
torch, campfire, trap, bed, wall, stone_wall_b, turret, chest, door, enchantment_table

---

## Storage Component (`components.py: Storage`)

| Field | Type | Purpose |
|-------|------|---------|
| `capacity` | int | Max slots (96 for chests, 9 for enchant tables) |
| `slots` | Dict[int, (str, int)] | slot → (item_id, count) |
| `slot_enchantments` | Dict[int, Dict] | slot → {'type', 'level'} |
| `slot_rarities` | Dict[int, str] | slot → rarity string |

| Method | Purpose |
|--------|---------|
| `add_item(item_id, count)` | Stack by item_id only (no enchant/rarity awareness) |
| `add_item_enchanted(item_id, enchant, count, rarity)` | Stack only if item_id + enchant + rarity all match |
| `sort()` | Merge all duplicate stacks (same item + enchant + rarity) and compact slots |

## Inventory Component (`components.py: Inventory`)

| Field | Type | Purpose |
|-------|------|---------|
| `capacity` | int | Main inventory capacity (default 96) |
| `slots` | Dict[int, (str, int)] | Main inventory slots → (item_id, count) |
| `hotbar` | Dict[int, (str, int)] | 6 dedicated hotbar slots → (item_id, count) |
| `equipped_slot` | int | Currently selected hotbar slot (0-5) |
| `held_item` | Optional[(str, int)] | Item currently picked up via drag-drop |

`get_equipped()` returns the item in `hotbar[equipped_slot]`, NOT from `slots`.
`add_item()` stacks to hotbar first, then slots; new items go to first empty main slot. **Non-stackable categories** (weapon, ranged, armor, shield, spell, tool, enchantment) always get their own slot.
`remove_item()` removes from hotbar first, then slots.
`remove_from_hotbar_slot(slot, count)` removes specifically from a given hotbar slot index (used for turret placement to consume from the correct slot).
`count()` / `has()` check both hotbar and slots.

### Non-Stackable Categories (`items/items.py: NON_STACKABLE_CATEGORIES`)

Items in these categories always occupy their own slot (count = 1 each):
`weapon`, `ranged`, `armor`, `shield`, `spell`, `tool`, `enchantment`

### Stack Splitting (`ui/split_dialog.py: SplitDialog`)

Right-click a stack (count > 1) in the inventory to open a split dialog.
- Scroll wheel or +/- buttons adjust the split amount.
- Type a number for precise control.
- Press Enter or click Confirm to split; Esc or Cancel to close.
- Default split amount is half the stack.
- Right-clicking a chest stack uses the same dialog, but moves the chosen amount directly from the chest into the player inventory.

### Drop Item Confirm (`ui/drop_confirm.py: DropConfirmDialog`)

Left-click outside the inventory panel while holding an item opens a confirmation dialog.
- Shows the canonical item label plus count; rarity remains styling/metadata rather than part of the label text.
- Warns the item will be lost forever.
- "Yes, Drop" destroys the held item (clears `held_item`, `held_enchant`, `held_rarity`).
- "Cancel" or Esc closes the dialog; the item remains held.
- Enter confirms the drop.

### Inventory Sort (`ui/inventory_sort.py: sort_inventory_slots`)

Click the "Sort" button below the inventory page navigation to sort and compact inventory slots.
- Stackable items with matching identity (id + enchant + rarity) are merged.
- Non-stackable items (weapons, armor, etc.) keep one unit per slot and are never merged.
- Slots are compacted so there are no gaps, sorted alphabetically by item_id.

## Key Game State Fields (`sandbox_rpg.py: Game`)

| Field | Type | Purpose |
|-------|------|---------|
| `overworld_structures` | list | Snapshot of placed structures before entering cave |

---

## Key Files

| File | Purpose |
|------|---------|
| `sandbox_rpg.py` | Entry point, Game class, all game logic |
| `constants.py` | All game-wide constants |
| `utils.py` | Math helpers, noise functions |
| `ecs.py` | Entity Component System (EntityManager) |
| `components.py` | All component types (Transform, Health, AI, etc.) |
| `items_data.py` | Item data, categories, recipes, mob definitions |
| `world.py` | World generation, tile data |
| `camera.py` | Camera following, shake |
| `particles.py` | Particle system |
| `textures.py` | Procedural texture generation |
| `minimap.py` | Minimap rendering |
| `gui.py` | UI components (InventoryGrid, CraftingPanel, PauseMenu, etc.) |
| `systems.py` | Game systems (Movement, Physics, AI, DayNight, Wave, etc.) |
| `save_load.py` | Save/load with JSON serialization |

## Key Classes

| Class | File | Purpose |
|-------|------|---------|
| `Game` | sandbox_rpg.py | Main game class, orchestrates everything |
| `EntityManager` | ecs.py | ECS entity/component management |
| `DayNightCycle` | systems.py | Tracks time, day_number, darkness |
| `WaveSystem` | systems.py | Night wave spawning with difficulty |
| `AISystem` | systems.py | Mob AI (wander, chase, ranged, structure attack) |
| `TextureGenerator` | textures.py | Procedural sprite generation |

## AI Component Attributes (`components.py: AI`)

| Attribute | Type | Purpose |
|-----------|------|---------|
| `behavior` | str | "wander" |
| `mob_type` | str | Mob type key |
| `state` | str | "idle", "chase", "attack_structure" |
| `is_ranged` | bool | Whether mob uses ranged attacks |
| `ranged_damage` | int | Ranged attack damage |
| `ranged_range` | float | Ranged attack range |
| `ranged_cooldown` | float | Seconds between ranged shots |
| `ranged_speed` | float | Ranged projectile speed |
| `is_boss` | bool | Whether mob is a boss |
| `glow_color` | tuple/None | Boss glow RGB color |

---

## Data Modules (`data/` package)

Centralised tuning modules. All values are re-exported through `constants.py` for backward compatibility.

| File | Purpose |
|------|---------|
| `data/__init__.py` | Re-exports from submodules |
| `data/crafting.py` | All crafting recipes (migrated from `items/recipes.py`) |
| `data/day_night.py` | Cycle timing, period thresholds, banner text/colour, night damage, sleep |
| `data/day_events.py` | Waves, mob respawn, day-based progression, spawn chances, initial population |
| `enchantments/__init__.py` | Package re-exports for effects helpers + try_combine |
| `enchantments/effects.py` | Enchantment control variables, bonus helpers, display helpers |
| `enchantments/recipes.py` | try_combine() — enchantment table combine logic |

### Recipes (`data/crafting.py`)

Format: `{'name': str, 'cost': {item_id: amount}, 'gives': str, 'count': int}`
Count defaults to 1 if omitted. See full list in Recipes section below.

---

## Enchantment System

### Building Constants (`core/constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `ENCHANT_TABLE_CAPACITY` | 9 | Enchantment table storage slots (3×3 grid) |
| `ENCHANT_TABLE_HP` | 60 | Enchantment table hit points |

### Enchantment Items (`data/items.py`)

| ID | Name | Category | Notes |
|----|------|----------|-------|
| `enchant_tome_1` | Enchantment Tome I | enchantment | Enhances equipment +1 |
| `enchant_tome_2` | Enchantment Tome II | enchantment | Enhances equipment +2 |
| `enchant_tome_3` | Enchantment Tome III | enchantment | Enhances equipment +3 |
| `enchant_tome_4` | Enchantment Tome IV | enchantment | Enhances equipment +4 |
| `enchant_tome_5` | Enchantment Tome V | enchantment | Enhances equipment +5 |
| `enchant_transfer_tome` | Enchant Transfer Tome | transfer_tome | Transfer enchant between items |
| `enhance_transfer_tome` | Enhancement Transfer Tome | transfer_tome | Transfer enhancement between items |
| `superior_transfer_tome` | Superior Transfer Tome | transfer_tome | Transfer both enchant + enhancement |
| `disenchant_tome` | Disenchant Tome | transfer_tome | Remove enchant from item |
| `unenhance_tome` | Unenhance Tome | transfer_tome | Remove enhancement from item |
| `enchantment_table` | Enchantment Table | placeable | Crafted, placed in world |
| `greater_enchantment_table` | Greater Enchantment Table | placeable | Advanced enchanting, crafted |

### Transfer Tome Drop Sources (Boss-only)

| Boss | Tomes in Pool | Weights |
|------|--------------|---------|
| boss_golem | enchant_transfer (2), enhance_transfer (2), superior_transfer (1), disenchant (2), unenhance (2) |
| boss_lich | enchant_transfer (3), enhance_transfer (3), superior_transfer (1), disenchant (3), unenhance (3) |
| boss_dragon | enchant_transfer (3), enhance_transfer (3), superior_transfer (2), disenchant (3), unenhance (3) |
| boss_necromancer | enchant_transfer (3), enhance_transfer (3), superior_transfer (1), disenchant (3), unenhance (3) |
| boss_troll_king | enchant_transfer (3), enhance_transfer (3), superior_transfer (1), disenchant (3), unenhance (3) |

### Enchantment Table Recipe (`data/crafting.py`)

| Result | Cost |
|--------|------|
| Enchantment Table | iron×6, diamond×2, wood×4 |
| Greater Enchantment Table | brilliant_diamond×4, iron×8, wood×6 |

### Enchantment Types (`game_controller.py` → `enchantments/effects.py`)

All enchantment tuning constants are declared in `game_controller.py`, imported by `enchantments/effects.py`.

| Type | Applies To | Source | Effect |
|------|-----------|--------|--------|
| `fire` | weapon | spell_fireball + equipment | Bonus fire damage + light radius + fire particles on hit |
| `ice` | weapon | spell_ice + equipment | Bonus ice damage + slow enemies on hit |
| `lightning` | weapon | spell_lightning + equipment | Bonus lightning damage + arc to nearby mob on hit |
| `protection` | armor/shield | any spell + armor/shield | Bonus damage reduction |

### Enchantment Color Dict (`game_controller.py: ENCHANT_COLORS`)

| Key | Color Constant | RGB |
|-----|---------------|-----|
| `fire` | `ENCHANT_COLOR_FIRE` | (255, 120, 30) |
| `ice` | `ENCHANT_COLOR_ICE` | (100, 200, 255) |
| `lightning` | `ENCHANT_COLOR_LIGHTNING` | (180, 200, 255) |
| `protection` | `ENCHANT_COLOR_PROTECTION` | (80, 255, 120) |
| `regen` | `ENCHANT_COLOR_REGEN` | (50, 255, 50) |
| `strength` | `ENCHANT_COLOR_STRENGTH` | (255, 80, 80) |

### Enchantment Prefix Dict (`game_controller.py: ENCHANT_PREFIX`)

| Key | Prefix |
|-----|--------|
| `fire` | Flaming |
| `ice` | Frozen |
| `lightning` | Shocking |
| `protection` | Warded |
| `regen` | Regenerating |
| `strength` | Mighty |

### Spell-to-Enchant Mapping (`game_controller.py: SPELL_TO_ENCHANT`)

| Spell Prefix | Enchant Type |
|-------------|-------------|
| `spell_fireball` | fire |
| `spell_ice` | ice |
| `spell_lightning` | lightning |
| `spell_protection` | protection |
| `spell_regen` | regen |
| `spell_strength` | strength |

### Enchantment Bonus Damage (`game_controller.py: FIRE/ICE/LIGHTNING_BONUS_DAMAGE`)

| Level | Fire | Ice | Lightning |
|-------|------|-----|-----------|
| 1 | +5 | +3 | +6 |
| 2 | +10 | +7 | +12 |
| 3 | +18 | +12 | +20 |
| 4 | +28 | +19 | +30 |
| 5 | +40 | +28 | +42 |

### Fire Enchant Light Radius (`enchantments/effects.py: FIRE_LIGHT_RADIUS`)

| Level | Radius (px) |
|-------|-------------|
| 1 | 90 |
| 2 | 110 |
| 3 | 140 |

### Ice Enchant Slow (`enchantments/effects.py`)

| Level | Slow Factor | Duration (s) |
|-------|-------------|--------------|
| 1 | 0.4 | 2.0 |
| 2 | 0.3 | 3.0 |
| 3 | 0.2 | 4.0 |

### Lightning Arc (`enchantments/effects.py`)

| Level | Arc Radius (px) | Damage Fraction |
|-------|-----------------|-----------------|
| 1 | 100 | 0.3 |
| 2 | 140 | 0.4 |
| 3 | 180 | 0.5 |

### Protection Enchant DR (`core/enhancement.py: PROTECTION_DR_BONUS`)

Control variable: `PROTECTION_DR_PER_LEVEL = 2` (+2 DR per enchant level, stacks with armor/turret enhancement DR)

| Level | Bonus DR |
|-------|----------|
| 1 | +2 |
| 2 | +4 |
| 3 | +6 |
| 4 | +8 |
| 5 | +10 |

### Elemental Resistance (`enchantments/effects.py: ELEMENTAL_RESISTANCE`)

| Level | Resistance |
|-------|-----------|
| 1 | 15% |
| 2 | 25% |
| 3 | 40% |
| 4 | 55% |
| 5 | 70% |

### Enchant Display (`enchantments/effects.py`)

| Type | Prefix | Color RGB |
|------|--------|-----------|
| fire | Blazing | (255, 100, 30) |
| ice | Frozen | (100, 200, 255) |
| lightning | Charged | (255, 255, 80) |
| protection | Warded | (180, 180, 255) |

### Spell-to-Enchant Mapping (`enchantments/effects.py: SPELL_TO_ENCHANT`)

| Spell Book | Enchant Type |
|-----------|-------------|
| spell_fireball | fire |
| spell_ice | ice |
| spell_lightning | lightning |
| spell_protection | protection |

### Enhanceable Base Items (via `CAN_ENHANCE` flag)

> **Note**: The old `_ENHANCEABLE_BASES` set in recipes.py has been replaced by the `CAN_ENHANCE` flag dict from the `items/` package.

`iron_sword`, `iron_axe`, `mace`, `titanium_axe`, `diamond_axe`, `iron_pickaxe`, `titanium_pickaxe`, `diamond_pickaxe`, `iron_armor`, `iron_shield`, `turret`

### Combine Recipes (`enchantments/recipes.py: try_combine()`)

| # | Combination | Result |
|---|------------|--------|
| 1 | Tome + Equipment | Stat-enhanced item (+1..+5), preserves existing enchant |
| 2 | Spell Book + Equipment | Elemental enchant (replaces existing) |
| 3 | Tome + Spell Book + Equipment | Both stat enhancement and elemental enchant |
| 4 | 9 identical items (same id, enchant, rarity) | 1 item of next rarity tier (preserves enchant + enhancement) |
| 5 | (reserved) | |
| 6 | Enchant Transfer Tome + enchanted item + non-enchanted equip | Transfers enchant to target; source loses enchant |
| 7 | Enhancement Transfer Tome + enhanced item + non-enhanced equip | Transfers enhancement to target; source reverts to base |
| 8 | Superior Transfer Tome + source + blank target | Transfers both enchant and enhancement to target |
| 9 | Disenchant Tome + enchanted equip | Removes enchant, keeps item |
| 10 | Unenhance Tome + enhanced equip | Reverts to base item, removes enhancement |

### 9-Item Rarity Upgrade Rules
- All 9 slots must be filled with the **exact same item** (same item_id, enchant, rarity)
- Output: 1 copy of the item at the next rarity tier
- Preserves enchant and enhancement on the result
- Fails if items differ in any attribute or if already mythic tier

### Non-Stackable Categories (`data/items.py`)

Items in these categories always occupy their own slot (count = 1):
`weapon`, `ranged`, `armor`, `shield`, `spell`, `tool`, `enchantment`, `transfer_tome`

### Enchant Data Storage

| Location | Field | Type | Purpose |
|----------|-------|------|---------|
| `Inventory` | `slot_enchantments` | Dict[int, Dict] | Main inv slot → {'type','level'} |
| `Inventory` | `hotbar_enchantments` | Dict[int, Dict] | Hotbar slot → {'type','level'} |
| `Equipment` | `enchantments` | Dict[str, Dict] | Equipped slot name → {'type','level'} |
| `Storage` | `slot_enchantments` | Dict[int, Dict] | Storage slot → {'type','level'} |

### Quality Tiers for Tomes (`data/quality.py`)

| Tier | Items |
|------|-------|
| Rare (Blue) | `enchant_tome_1`, `enchant_tome_2` |
| Epic (Purple) | `enchant_tome_3`, `enchant_tome_4`, `enchant_tome_5` |

### Tome Drop Sources

| Mob/Source | Tomes | Weights |
|-----------|-------|---------|
| dark_knight | enchant_tome_1 (w:3), enchant_tome_2 (w:2), enchant_tome_3 (w:1) | Normal drops |
| troll | enchant_tome_1 (w:3), enchant_tome_2 (w:2) | Normal drops |
| goblin_shaman | enchant_tome_1 (w:2) | Ranged drops |
| boss_golem | enchant_tome_1 (w:5), enchant_tome_2 (w:4), enchant_tome_3 (w:3) | Boss drops |
| boss_lich | enchant_tome_3 (w:4), enchant_tome_4 (w:3), enchant_tome_5 (w:2) | Boss drops |
| boss_dragon | enchant_tome_3 (w:4), enchant_tome_4 (w:3), enchant_tome_5 (w:2) | Boss drops |
| boss_necromancer | enchant_tome_2 (w:4), enchant_tome_3 (w:3), enchant_tome_4 (w:2), enchant_tome_5 (w:1) | Boss drops |
| boss_troll_king | enchant_tome_2 (w:4), enchant_tome_3 (w:3), enchant_tome_4 (w:2), enchant_tome_5 (w:1) | Boss drops |
| Cave Chest | enchant_tome_2, enchant_tome_3, enchant_tome_4 | Rare pool |

---

## Drop System (`drops/` package)

Mob loot is data-driven via the `drops/` package. The old `MOB_DATA['drops']` keys have been removed.

### Module Structure

| File | Purpose |
|------|---------|
| `drops/__init__.py` | Merges all tables into `LOOT_TABLES`, exports `roll_loot()` |
| `drops/common.py` | Enhancement odds, enhanceable item lists, material/consumable pools |
| `drops/normal.py` | Loot tables for 11 normal enemies (`NORMAL_LOOT`) |
| `drops/ranged.py` | Loot tables for 2 ranged enemies (`RANGED_LOOT`) |
| `drops/bosses.py` | Loot tables for 5 bosses (`BOSS_LOOT`) + `CAVE_CHEST_LOOT` |

### Loot Table Format

| Key | Type | Purpose |
|-----|------|---------|
| `drop_chance` | float | Probability (0.0–1.0) that the mob drops anything |
| `min_items` | int | Minimum distinct item types rolled from pool |
| `max_items` | int | Maximum distinct item types rolled from pool |
| `pool` | list[(id, weight, min, max)] | Weighted item pool with count ranges |
| `guaranteed` | list[(id, min, max)] | Boss only — always dropped |
| `enhanced_chance` | float | Boss only — chance to upgrade one drop to +1..+5 |

### Enhancement Odds (`drops/common.py: ENHANCEMENT_ODDS`)

| Tier | Chance |
|------|--------|
| +1 | 45% |
| +2 | 30% |
| +3 | 15% |
| +4 | 7% |
| +5 | 3% |

### Cave Chest Loot (`drops/bosses.py: CAVE_CHEST_LOOT`)

| Key | Value | Purpose |
|-----|-------|---------|
| `base` | 5 guaranteed item types | Always placed in chest |
| `pool` | 50+ weighted `(item_id, weight, min, max)` tuples | Weapons, armor, shields, ranged, ammo, spells, tomes, consumables, materials (incl. titanium_ore) |
| `min_pool_rolls` | 3 | Minimum extra items from weighted pool |
| `max_pool_rolls` | 6 | Maximum extra items from weighted pool |
| `enhanced_chance` | 0.50 | Chance one pool item gets +1..+5 enhancement |

Pool items receive boss rarity weights (`RARITY_WEIGHTS_BOSS`). Enhancement tiers use `ENHANCEMENT_ODDS`. Population uses public `pick_weighted()` and `maybe_enhance()` from `drops/__init__.py`.

### Key Function: `roll_loot(table, rng=None, luck_bonus=0.0)`

Returns `list[(item_id, count, rarity_or_None)]` — 3-tuples. Checks `drop_chance`, adds `guaranteed` items, picks `min_items`–`max_items` from weighted pool (no duplicates), then optionally enhances one drop for bosses. Rarity-eligible equipment items get a rarity roll using boss weights (if `enhanced_chance > 0`) or normal weights.

---

## Command Bar & Cheat System

### F12 Command Bar (`ui/command_bar.py`)

Press **F12** to toggle a text input overlay. Type commands and press Enter to execute.

### Cheat Commands (`game/cheats.py`)

| Command | Requires Cheats | Description |
|---------|-----------------|-------------|
| `enable cheats` | No | Enables cheat mode (saved to save data) |
| `disable cheats` | No | Disables cheat mode and turns off timed cheat effects |
| `help` | No | Lists available commands |
| `set health <val>` | Yes | Set current HP |
| `set maxhp <val>` | Yes | Set max HP |
| `set level <val>` | Yes | Set player level |
| `set xp <val>` | Yes | Set XP |
| `set points <val>` | Yes | Set stat points |
| `set str <val>` | Yes | Set strength |
| `set agi <val>` | Yes | Set agility |
| `set vit <val>` | Yes | Set vitality |
| `set luck <val>` | Yes | Set luck |
| `set kills <val>` | Yes | Set kill count |
| `set day <val>` | Yes | Set day number |
| `give <item_id> [n]` | Yes | Give n plain items (default 1) |
| `give Regen V Mythic Turret +5 [n]` | Yes | Give fully-specified enchant/rarity/enhancement items |
| `god` | Yes | Toggle invincibility |
| `heal` | Yes | Full heal |
| `kill` | Yes | Kill all enemies |
| `autokill on|off` | Yes | Kill enemies every 1 second while enabled |
| `levelup [n]` | Yes | Level up n times (default 1) |

### Save Data Fields

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `cheats_enabled` | bool | false | Whether cheats are enabled |
| `has_cheated` | bool | false | Permanent flag that becomes true once cheats were ever enabled |

### Game State

| Attribute | Type | Description |
|-----------|------|-------------|
| `Game.cheats_enabled` | bool | Cheat mode active |
| `Game.has_cheated` | bool | Persistent save flag tracking whether cheats were ever enabled |
| `Game.god_mode` | bool | Invincibility (not saved) |
| `Game.autokill_enabled` | bool | Timed cheat toggle that kills enemies every 1 second |
| `Game.autokill_timer` | float | Accumulator for the autokill interval |
| `Game.show_cheat_help` | bool | Cheat help overlay visible |
| `Game.command_bar` | CommandBar | F12 command bar instance |

When `Game.command_bar.blocks_game_input()` is true, command text entry has exclusive keyboard focus. Global UI toggles (`I`, `C`, `P`, etc.), action-bar hotkeys, mouse-wheel hotbar cycling, and held-key gameplay actions (`WASD`, `E`, `R`, `Space`) must not react until the command bar closes. `give` accepts item ids or multi-word item names plus optional enchant level, rarity, and `+N` enhancement tokens. Example: `give Regen V Mythic Turret +5 2`. `Tab` autocompletes the item portion while preserving the metadata tokens already typed.

Loot metadata now also flows through `core/item_metadata.roll_item_metadata()`. Enemy-specific tables still decide what can drop; day count, elite tier, boss status, and item type now decide whether the drop also rolls rarity, enchant, and enhancement metadata.

---

## Border System — Clean Slate

**Rarity border is the ONLY item border.** All other borders (enchantment glow, enhancement inner ring, icon tier glow) have been removed.

- `draw_rarity_border()` in `ui/rarity_display.py` — draws 2px colored border for non-common rarity items
- `draw_enhancement_border()` — **COMMENTED OUT** (preserved for future use)
- `ENHANCEMENT_COLORS` dict — **COMMENTED OUT** in `game_controller.py`
- `ENHANCEMENT_COLOR_1` through `ENHANCEMENT_COLOR_5` — **COMMENTED OUT** in `game_controller.py`
- Tier glow borders on item icon textures — **REMOVED** from `textures/items.py` (`_generate_stat_weapon`, `generate_tiered_spell_books`)
- Enchant color fallback borders (drawn when no rarity but has enchant) — **REMOVED** from all UI modules

---

## New Enemy Types (added to data/mobs.py MOB_DATA)

### Tier 0 — Easy
| Mob Type | HP | Speed | Detection | Damage | XP | Notes |
|----------|-----|-------|-----------|--------|----|-------|
| `snake` | 20 | 60 | 120 | 6 | 18 | Fast, low HP |
| `kobold` | 28 | 50 | 160 | 6 | 22 | Small humanoid |

### Tier 2 — Hard
| Mob Type | HP | Speed | Detection | Damage | XP | Notes |
|----------|-----|-------|-----------|--------|----|-------|
| `hobgoblin` | 80 | 42 | 200 | 14 | 55 | Larger goblin |
| `bear` | 100 | 35 | 140 | 18 | 65 | Strong melee |
| `mephit_fire` | 45 | 55 | 220 | 12 | 50 | Ranged (fire) |
| `mephit_ice` | 45 | 55 | 220 | 10 | 50 | Ranged (ice) |
| `mephit_lightning` | 45 | 58 | 230 | 11 | 55 | Ranged (lightning) |

### Tier 3 — Elite
| Mob Type | HP | Speed | Detection | Damage | XP | Notes |
|----------|-----|-------|-----------|--------|----|-------|
| `ogre` | 180 | 24 | 160 | 28 | 90 | Large enemy |
| `ogre_mage` | 140 | 30 | 240 | 18 | 100 | Large, ranged |
| `golem` | 220 | 18 | 140 | 30 | 100 | Large, very slow |

### Tier 4 — Late Game
| Mob Type | HP | Speed | Detection | Damage | XP | Notes |
|----------|-----|-------|-----------|--------|----|-------|
| `centaur` | 110 | 55 | 280 | 15 | 85 | Fast ranged |

### Dragon Bosses (all Large)
| Mob Type | HP | Speed | Detection | Damage | XP | Boss | Glow |
|----------|-----|-------|-----------|--------|----|------|------|
| `dragon_red` | 500 | 32 | 350 | 40 | 300 | Yes | BOSS_GLOW_DRAGON_RED |
| `dragon_green` | 450 | 34 | 340 | 35 | 280 | Yes | BOSS_GLOW_DRAGON_GREEN |
| `dragon_black` | 550 | 30 | 360 | 42 | 320 | Yes | BOSS_GLOW_DRAGON_BLACK |
| `dragon_white` | 480 | 36 | 350 | 38 | 300 | Yes | BOSS_GLOW_DRAGON_WHITE |
| `shadow_dragon` | 800 | 28 | 400 | 55 | 500 | Yes | BOSS_GLOW_SHADOW_DRAGON |

### New Ranged Enemies
| Mob Type | Ranged Dmg | Range | Cooldown | Speed |
|----------|-----------|-------|----------|-------|
| `orc_archer` | 16 | 260 | 1.8s | 360 |
| `mephit_fire` | 14 | 200 | 2.0s | 320 |
| `mephit_ice` | 12 | 200 | 2.2s | 300 |
| `mephit_lightning` | 16 | 210 | 1.8s | 380 |
| `centaur` | 18 | 280 | 1.5s | 400 |

---

## New Game Controller Constants

### New Mob Colors (game_controller.py)
| Constant | RGB Value |
|----------|-----------|
| `MOB_COLOR_ORC_ARCHER` | (90, 110, 55) |
| `MOB_COLOR_HOBGOBLIN` | (120, 80, 50) |
| `MOB_COLOR_KOBOLD` | (140, 100, 60) |
| `MOB_COLOR_MEPHIT_FIRE` | (220, 80, 30) |
| `MOB_COLOR_MEPHIT_ICE` | (100, 180, 230) |
| `MOB_COLOR_MEPHIT_LIGHTNING` | (200, 200, 60) |
| `MOB_COLOR_OGRE` | (130, 110, 70) |
| `MOB_COLOR_OGRE_MAGE` | (110, 80, 140) |
| `MOB_COLOR_CENTAUR` | (140, 120, 80) |
| `MOB_COLOR_SNAKE` | (80, 140, 50) |
| `MOB_COLOR_BEAR` | (100, 70, 40) |
| `MOB_COLOR_GOLEM` | (150, 140, 130) |
| `MOB_COLOR_DRAGON_RED` | (200, 40, 30) |
| `MOB_COLOR_DRAGON_GREEN` | (40, 160, 50) |
| `MOB_COLOR_DRAGON_BLACK` | (30, 30, 40) |
| `MOB_COLOR_DRAGON_WHITE` | (220, 220, 240) |
| `MOB_COLOR_SHADOW_DRAGON` | (50, 20, 70) |

### New Boss Glow Colors
| Constant | RGB Value |
|----------|-----------|
| `BOSS_GLOW_DRAGON_RED` | (255, 80, 40) |
| `BOSS_GLOW_DRAGON_GREEN` | (60, 255, 60) |
| `BOSS_GLOW_DRAGON_BLACK` | (120, 60, 180) |
| `BOSS_GLOW_DRAGON_WHITE` | (200, 220, 255) |
| `BOSS_GLOW_SHADOW_DRAGON` | (160, 40, 220) |

### Elite Enemy Tier System
Elite enemies use a tiered system with silhouette-based neon glow outlines (not a box).
Each tier has a color and stat multipliers (HP, DMG, XP).

| Tier | Color | HP Mult | DMG Mult | XP Mult | RGB |
|------|-------|---------|----------|---------|-----|
| 1 (Blue) | Blue | 2× | 2× | 2× | (60, 140, 255) |
| 2 (Purple) | Purple | 3× | 3× | 3.5× | (180, 60, 255) |
| 3 (Gold) | Gold | 4× | 4× | 5× | (255, 200, 40) |
| 4 (Red) | Red | 5× | 5× | 8× | (255, 40, 40) |

| Constant | Value | Description |
|----------|-------|-------------|
| `ELITE_GLOW_EXPAND` | 2 | Outline expansion in px beyond sprite edge |
| `ELITE_GLOW_PULSE_SPEED` | 0.004 | Pulse animation speed |
| `ELITE_GLOW_ALPHA_MIN` | 100 | Minimum glow alpha |
| `ELITE_GLOW_ALPHA_MAX` | 200 | Maximum glow alpha |
| `ELITE_START_DAY` | 7 | No elites before this day |
| `ELITE_MAX_CHANCE` | 0.1 | Max spawn probability |

### Spell Level Scaling
| Constant | Value | Description |
|----------|-------|-------------|
| `SPELL_LEVEL_SCALE_PERCENT` | 0.02 | 2% per player level bonus to all spell effects |
| `SPELL_AUTO_TARGET_RADIUS` | 80.0 | Auto-target enemy within this radius of click |
| `SPELL_PROJ_SIZE` | {1:(12,12)..5:(22,22)} | Projectile size per spell tier |
| `SPELL_EXPLOSION_PARTICLES` | {1:10..5:30} | Explosion particle count per tier |
| `SPELL_EXPLOSION_RADIUS` | {1:50..5:110} | Visual explosion radius per tier |
| `PROJ_MOB_HIT_RADIUS` | 28.0 | Projectile→mob collision radius |

### Damage Resistance (Diminishing Returns)
Formula: `reduction% = DR / (DR + DR_HALF_VALUE)`, capped at `DR_MAX_PERCENT`.

| Constant | Value | Description |
|----------|-------|-------------|
| `DR_HALF_VALUE` | 100.0 | DR needed for 50% damage reduction |
| `DR_MAX_PERCENT` | 0.85 | Hard cap at 85% reduction |
| `DR_MIN_DAMAGE` | 1 | Minimum damage always dealt |

Example DR values at half=100:
- DR 10 → 9% reduction
- DR 50 → 33% reduction  
- DR 100 → 50% reduction
- DR 200 → 67% reduction
- DR 500 → 83% reduction

### Multi-Wave Night System
| Constant | Value | Description |
|----------|-------|-------------|
| `NIGHT_WAVE_COUNT` | {0:1, 1:3, 2:5, 3:10} | Waves per night by difficulty |
| `NIGHT_WAVE_SPACING_HOURS` | {0:0, 1:2, 2:1, 3:0.5} | Game hours between waves |

---

## Spawn Tables (data/mobs.py)

### Day Spawn Table (DAY_SPAWN_TABLE)
| Biome | Spawns |
|-------|--------|
| grass | slime, snake, kobold |
| forest | wolf, spider, bear, snake |
| dirt | goblin, kobold, hobgoblin, orc |

### Night Spawn Table (NIGHT_SPAWN_TABLE)
| Biome | Spawns |
|-------|--------|
| grass | skeleton, zombie, ghost, wraith |
| forest | wolf, spider, skeleton, ghost, wraith |
| dirt | dark_knight, orc, hobgoblin, skeleton, zombie |

### Undead Types (night-only on overworld)
`skeleton`, `zombie`, `ghost`, `wraith`, `skeleton_archer`

### Wave Mob Tiers (WAVE_MOB_TIERS) — 5 tiers now
| Tier | Enemies |
|------|---------|
| 0 | slime, spider, snake, kobold |
| 1 | skeleton, wolf, goblin, zombie, ghost |
| 2 | orc, wraith, hobgoblin, bear, mephit_fire/ice/lightning |
| 3 | dark_knight, troll, ogre, ogre_mage, golem |
| 4 | centaur, dragon_red/green/black/white |

---

## DraggableWindow System (ui/draggable.py)

All UI windows use `DraggableWindow` for drag, close (X), and resize support.

| UI Panel | DraggableWindow Title | Base Size |
|----------|----------------------|-----------|
| Inventory | "Inventory" | Dynamic |
| Crafting | "Crafting" | 420×501 |
| Character Menu | "Character" | 540×460 |
| Chest | "Chest" | 620×320 |
| Enchantment Table | "Enchantment Table" | 570×300 |
| Stone Oven | "Stone Oven" | 380×340 |
| Pause Menu | "Pause Menu" | 460×440 |

### DraggableWindow Features
- Title bar height: 22px
- Close button (X): upper right corner
- Resize handle: lower right corner (8×8)
- Minimum size: 120×80
- All UIs retain ESC-closes-all behavior
- Stone Oven opens left-aligned with inventory beside it

### AI Component (core/components.py) — New Attribute
| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `is_elite` | bool | False | Whether mob is an elite variant |

### Large Enemy Flag
Enemies with `'large': True` in MOB_DATA:
- `ogre`, `ogre_mage`, `golem`
- `dragon_red`, `dragon_green`, `dragon_black`, `dragon_white`, `shadow_dragon`

These use larger texture surfaces (36×48 for ogres/golems, 48×48 for dragons).

---

## Character Customization System (`character/` package)

### Sprite Composition
The player sprite is a 24×32 SRCALPHA surface composed of layered pixel art:
1. **Skin** (body shape: head, arms, legs) — `draw_skin(color)`
2. **Pants/shorts/skirt** — `draw_pants(style, color)`
3. **Shirt/tunic/vest/tank** — `draw_shirt(style, color)`
4. **Hair** — `draw_hair(style, color)`
5. **Weapon overlay** (right hand) — `draw_weapon_overlay(weapon_id)` — optional
6. **Shield overlay** (left hand) — `draw_shield_overlay(shield_id)` — optional

`compose_character()` blits all layers in order and returns the final sprite.

### CharacterData (serializable state)
| Field | Type | Default | Range |
|-------|------|---------|-------|
| `skin_color_idx` | int | 0 | 0–5 (SKIN_COLORS) |
| `hair_style_idx` | int | 0 | 0–5 (HAIR_STYLES: short, long, spiky, bald, ponytail, mohawk) |
| `hair_color_idx` | int | 0 | 0–7 (HAIR_COLORS) |
| `shirt_style_idx` | int | 0 | 0–2 (SHIRT_STYLES: tunic, vest, tank) |
| `shirt_color_idx` | int | 0 | 0–7 (SHIRT_COLORS) |
| `pants_style_idx` | int | 0 | 0–5 (PANTS_COLORS) / 0–2 (PANTS_STYLES: pants, shorts, skirt) |
| `pants_color_idx` | int | 0 | 0–5 (PANTS_COLORS) |
| `show_equipment` | bool | True | Whether weapon/shield show on sprite |

### Weapon Overlay Profiles
Each weapon_id is matched (first match wins) to a (weapon_type, handle_color, head_color) tuple:
| Match Key | Type | Handle Color | Head Color |
|-----------|------|-------------|------------|
| `iron_sword` | sword | (80,60,30) | (200,210,230) |
| `sword` | sword | (100,70,35) | (180,180,200) |
| `diamond_pickaxe` | pickaxe | (120,80,40) | (140,200,255) |
| `titanium_pickaxe` | pickaxe | (120,80,40) | (160,170,200) |
| `iron_pickaxe` | pickaxe | (120,80,40) | (170,170,190) |
| `pickaxe` | pickaxe | (120,80,40) | (160,160,170) |
| `diamond_axe` | axe | (120,80,40) | (140,200,255) |
| `titanium_axe` | axe | (120,80,40) | (160,170,200) |
| `iron_axe` | axe | (120,80,40) | (170,170,190) |
| `axe` | axe | (120,80,40) | (180,180,200) |
| `mace` | mace | (120,80,40) | (160,160,175) |
| `spear` | spear | (120,80,40) | (180,190,210) |
| `bone_club` | club | (200,195,180) | (230,225,210) |

### Shield Overlay Profiles
| Match Key | Fill Color | Border Color | Emblem Color |
|-----------|-----------|-------------|-------------|
| `iron_shield` | (160,160,180) | (120,120,135) | (200,205,220) |
| `wood_shield` | (130,91,30) | (80,60,40) | (180,180,200) |

### Game Integration
- `Game.char_data` — CharacterData instance, persisted in saves as `'character'` key
- `Game.char_gen_ui` — CharacterGenerator instance
- `Game.in_char_gen` — True when character creation screen is active
- `Game._rebuild_player_sprite()` — Rebuilds player texture from char_data + current equipment; called after equip/unequip changes and on save load
- `CharacterMenu.equipment_changed` — Flag set True on equip/unequip, checked in game/events.py to trigger sprite rebuild

### Legacy Save Migration (`character/legacy_save_migration.py`)
- **REMOVABLE MODULE** — exists only to handle saves created before character gen was added
- `check_needs_migration(data)` → True if save dict lacks `'character'` key
- When True, game routes player to character generator before resuming
- References: `game/menus.py` (load game handler), `character/generator.py` (`_is_legacy_migration` flag)

### UI Window System
- Opening one window (I/C/P) does NOT close other windows
- Only ESC closes all windows simultaneously
- Stone oven and enchantment table auto-open inventory alongside themselves
- Chest does NOT auto-open inventory (chest UI has its own built-in inventory panel)

### Performance Infrastructure

#### Spatial Hash (`core/spatial.py`)
- `SPATIAL_CELL_SIZE = 128` — Grid cell size in pixels (4 tiles), controls broadphase granularity
- `spatial_hash` — Module-level singleton instance used by all systems
- API: `insert(eid, x, y, w, h)`, `remove(eid)`, `update(eid, x, y, w, h)`, `query_radius(cx, cy, r)`, `query_rect(x, y, w, h)`, `clear()`
- All entity lifecycle events (create, destroy, move, load) must maintain spatial hash
- Systems use `query_radius()` / `query_rect()` instead of `get_entities_with()` for proximity checks

#### ECS Query Cache (`core/ecs.py`)
- `EntityManager._query_cache: dict[tuple[Type,...], list[int]]` — Per-frame cache of `get_entities_with` results
- Auto-invalidated on `create_entity`, `destroy_entity`, `add_component`, `remove_component`
- `clear_query_cache()` called at top of each update tick in `game/update.py`

#### Elite Outline Cache (`game/drawing.py`)
- `_elite_outline_cache: dict[(id(sprite), flip_x, tier), Surface]` — Cached mask→silhouette→8-dir stamp surfaces
- Cache key: `(id(rend.surface), rend.flip_x, ai_c.elite_tier)`
- Pulsing via `set_alpha()` — no per-frame surface regeneration

#### Light Surface Cache (`game/drawing.py`)
- `_light_surface_cache: dict[(radius, r, g, b), Surface]` — Cached concentric-ring light punch surfaces
- Cache key: `(radius, color[0], color[1], color[2])`
- Eliminates ~11 Surface allocations per light per frame during night
