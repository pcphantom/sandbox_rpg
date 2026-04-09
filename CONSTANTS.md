# CONSTANTS.md — Global Constants & Data Reference

This document tracks all global constants, key variables, and data structures used across the codebase. **Must be read before making changes and updated when constants change.**

---

## Display Constants (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SCREEN_WIDTH` | 1280 | Window width in pixels |
| `SCREEN_HEIGHT` | 720 | Window height in pixels |
| `TILE_SIZE` | 32 | Size of one world tile in pixels |
| `WORLD_WIDTH` | 200 | World width in tiles |
| `WORLD_HEIGHT` | 150 | World height in tiles |
| `FPS` | 60 | Target frames per second |

## Colour Constants (`constants.py`)

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

## Tile Types (`constants.py`)

| Constant | Value |
|----------|-------|
| `TILE_WATER` | 0 |
| `TILE_SAND` | 1 |
| `TILE_GRASS` | 2 |
| `TILE_DIRT` | 3 |
| `TILE_STONE_FLOOR` | 4 |
| `TILE_STONE_WALL` | 5 |
| `TILE_FOREST` | 6 |

## Save System (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SAVE_DIR` | `<project>/save/` | Directory for save files |
| `SAVE_SLOTS` | 4 | Total slots (0=quick, 1-3=manual) |
| `QUICK_SAVE_SLOT` | 0 | Quick save slot index |

## Inventory (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `INVENTORY_SLOTS_PER_PAGE` | 24 | Slots per inventory page |
| `INVENTORY_PAGES` | 4 | Number of inventory pages |
| `INVENTORY_COLS` | 6 | Columns in inventory grid |
| `INVENTORY_TOTAL_SLOTS` | 96 | Total inventory capacity |

## Combat (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `MIN_ATTACK_COOLDOWN` | 0.15 | Minimum attack cooldown (seconds) |
| `BASE_ATTACK_COOLDOWN` | 0.30 | Base attack cooldown |
| `AGILITY_COOLDOWN_REDUCTION` | 0.02 | Cooldown reduction per AGI point |
| `STAT_POINTS_PER_LEVEL` | 3 | Stat points gained per level |

## Sleep (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `SLEEP_DURATION` | 5.0 | Sleep duration in seconds |
| `SLEEP_TIME_MULTIPLIER` | 12.0 | Legacy sleep time multiplier |

## Building System (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `WALL_HP` | 100 | Wood wall hit points |
| `TURRET_HP` | 80 | Turret hit points |
| `TURRET_RANGE` | 200.0 | Turret detection range |
| `TURRET_DAMAGE` | 8 | Turret damage per shot |
| `TURRET_COOLDOWN` | 1.5 | Turret fire cooldown |
| `CHEST_CAPACITY` | 24 | Chest storage slots |

## Wave System (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `WAVE_START_NIGHT` | 3 | Night count before waves begin |
| `WAVE_BASE_COUNT` | 3 | Base enemies per wave |
| `WAVE_SCALE_PER_NIGHT` | 2 | Additional enemies per night |
| `WAVE_SPAWN_RADIUS` | 350.0 | Spawn distance from target |

## Day/Night Timing (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `DAY_LENGTH_BASE` | 960.0 | Full day-night cycle length (seconds). 4x slower than original 240.0 |
| `NIGHT_SLEEP_SPEED_MULT` | 12.0 | Time multiplier when sleeping on bed at night |

## Difficulty System (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `DIFFICULTY_EASY` | 0 | Easy difficulty index |
| `DIFFICULTY_NORMAL` | 1 | Normal difficulty index |
| `DIFFICULTY_HARD` | 2 | Hard difficulty index |
| `DIFFICULTY_HARDCORE` | 3 | Hardcore difficulty index |
| `DIFFICULTY_NAMES` | ("Easy", "Normal", "Hard", "Hardcore") | Display names |

### Difficulty Multipliers (`DIFFICULTY_MULTIPLIERS`)

Format: `(enemy_hp_mult, enemy_dmg_mult, spawn_rate_mult, wave_count_mult)`

| Difficulty | HP Mult | DMG Mult | Spawn Mult | Wave Mult |
|-----------|---------|----------|------------|-----------|
| Easy | 1.0 | 1.0 | 1.0 | 1.0 |
| Normal | 1.3 | 1.3 | 1.2 | 1.3 |
| Hard | 1.8 | 1.8 | 1.5 | 1.8 |
| Hardcore | 2.5 | 2.5 | 2.0 | 2.5 |

## Mob Respawn (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `MOB_RESPAWN_INTERVAL` | 8.0 | Seconds between natural mob respawns |
| `RANGED_ENEMY_START_DAY` | 3 | Day after which ranged enemies appear |

## Placement Preview (`constants.py`)

| Constant | Value | Purpose |
|----------|-------|---------|
| `PLACEMENT_PREVIEW_COLOR` | (60, 220, 80, 120) | Valid placement ghost color |
| `PLACEMENT_INVALID_COLOR` | (220, 60, 60, 120) | Invalid placement ghost color |

---

## Mob Types (`items_data.py: MOB_DATA`)

| Mob Type | HP | Speed | Detection | Damage | XP | Ranged | Boss |
|----------|-----|-------|-----------|--------|-----|--------|------|
| slime | 30 | 35 | 180 | 5 | 15 | No | No |
| skeleton | 60 | 50 | 220 | 10 | 35 | No | No |
| wolf | 40 | 65 | 160 | 8 | 25 | No | No |
| goblin | 50 | 45 | 200 | 12 | 40 | No | No |
| ghost | 35 | 40 | 250 | 6 | 50 | No | No |
| spider | 25 | 55 | 140 | 7 | 20 | No | No |
| orc | 90 | 38 | 180 | 16 | 60 | No | No |
| dark_knight | 120 | 42 | 200 | 20 | 80 | No | No |
| zombie | 70 | 30 | 160 | 14 | 35 | No | No |
| wraith | 55 | 52 | 280 | 10 | 55 | No | No |
| troll | 150 | 28 | 160 | 22 | 75 | No | No |
| skeleton_archer | 50 | 35 | 260 | 8 | 45 | Yes | No |
| goblin_shaman | 45 | 32 | 240 | 6 | 50 | Yes | No |
| boss_golem | 400 | 22 | 300 | 35 | 250 | No | Yes |
| boss_lich | 300 | 35 | 350 | 28 | 300 | Yes | Yes |

## Wave Mob Tiers (`items_data.py`)

| Tier | Mobs |
|------|------|
| 0 (Easy) | slime, spider |
| 1 (Medium) | skeleton, wolf, goblin, zombie |
| 2 (Hard) | orc, wraith |
| 3 (Boss-tier) | dark_knight, troll |

Ranged wave mobs: skeleton_archer, goblin_shaman (after Day 3)
Boss wave mobs: boss_golem, boss_lich

## Item IDs (`items_data.py: ITEM_DATA`)

### Materials
wood, stone, stick, iron, cloth, bone, leather

### Consumables
berry (15hp), pie (40hp), bandage (25hp), health_potion (80hp), antidote (10hp)

### Spell Books
spell_fireball — Fireball Tome (60 damage, 80 radius, 350 speed, 400 range)

### Melee Weapons
axe (12dmg), sword (20dmg), iron_sword (30dmg), spear (18dmg), iron_axe (22dmg), mace (26dmg), bone_club (14dmg)

### Ranged Weapons
bow, crossbow, sling

### Ammo
arrow, fire_arrow, bolt, rock_ammo, sling_bullet

### Armor
leather_armor (3 DR), iron_armor (6 DR), wood_shield, iron_shield (4 DR)

### Placeables
torch, campfire, trap, bed, wall, stone_wall_b, turret, chest, door

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
