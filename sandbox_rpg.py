# sandbox_rpg.py — Sandbox Survival RPG (Modular Edition)
# Python 3.10+ | pygame 2.5+
"""Entry point.  All game logic lives in dedicated modules."""
import pygame
import random
import math
import sys
from typing import List, Tuple, Dict, Optional, Any

pygame.init()
pygame.font.init()

# -- project imports (order matters: constants first) ----------------------
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT,
    FPS, BLACK, WHITE, YELLOW, RED, GREEN, CYAN, GRAY, ORANGE, DARK_GRAY,
    PURPLE, LIGHT_BLUE,
    TILE_WATER, TILE_GRASS, TILE_DIRT, TILE_SAND, TILE_STONE_FLOOR,
    TILE_STONE_WALL, TILE_FOREST, TILE_CAVE_FLOOR, TILE_CAVE_ENTRANCE,
    QUICK_SAVE_SLOT, INVENTORY_TOTAL_SLOTS,
    MIN_ATTACK_COOLDOWN, BASE_ATTACK_COOLDOWN, AGILITY_COOLDOWN_REDUCTION,
    WALL_HP, TURRET_HP, TURRET_RANGE, TURRET_DAMAGE, TURRET_COOLDOWN,
    CHEST_CAPACITY,
    CAMPFIRE_BASE_HEAL, CAMPFIRE_HEAL_RADIUS, CAMPFIRE_HEAL_INTERVAL,
    VITALITY_CAMPFIRE_BONUS_PER,
    DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD, DIFFICULTY_HARDCORE,
    DIFFICULTY_NAMES, DIFFICULTY_MULTIPLIERS,
    PLACEMENT_PREVIEW_COLOR, PLACEMENT_INVALID_COLOR,
    CAVE_MOB_TYPES, CAVE_MOB_COUNT, CAVE_BOSS_TYPES,
    CAVE_ORE_COUNT, CAVE_DIAMOND_COUNT,
    CAVE_HP_MULT, CAVE_DMG_MULT,
    FONT_SIZE_MAIN, FONT_SIZE_SM, FONT_SIZE_LG, FONT_SIZE_XL,
    PLAYER_BASE_SPEED, PLAYER_FRICTION, PLAYER_COLLIDER_W, PLAYER_COLLIDER_H,
    AGI_SPEED_BONUS, AGI_SPEED_BONUS_CAP,
    MOVEMENT_ACCEL_MULT, SPRITE_FLIP_THRESHOLD,
    STARTING_WOOD, STARTING_STONE, PLAYER_TORCH_LIGHT_RADIUS,
    BASE_MELEE_DAMAGE, SPEAR_ATTACK_RANGE, WEAPON_ATTACK_RANGE,
    UNARMED_ATTACK_RANGE, CRIT_CHANCE_PER_LUCK, CRIT_DAMAGE_MULT,
    MELEE_KNOCKBACK_FORCE, ATTACK_ANIM_DURATION, INTERACT_COOLDOWN,
    MIN_RANGED_COOLDOWN,
    CONTACT_DAMAGE_RADIUS, PLAYER_HIT_INVULN, DAMAGE_FLASH_DURATION,
    HIT_SHAKE_AMOUNT, HIT_SHAKE_DURATION,
    ENEMY_PROJ_HIT_RADIUS, PROJ_SHAKE_AMOUNT, PROJ_SHAKE_DURATION,
    INTERACT_RANGE, HARVEST_RANGE, BED_INTERACT_RANGE, LUCK_HARVEST_CHANCE,
    TREE_COUNT, FOREST_TREE_COUNT, ROCK_COUNT,
    TRAP_HP, BED_HP, CAMPFIRE_HP, CHEST_HP_VALUE, DOOR_HP,
    DOOR_COLLIDER_W, DOOR_COLLIDER_H, STONE_WALL_HP_MULT,
    CAMPFIRE_LIGHT_RADIUS, TORCH_LIGHT_RADIUS,
    LEVEL_UP_BASE_HP, VIT_HP_BONUS_PER_LEVEL,
    NOTIFICATION_DURATION, HUD_REFRESH_INTERVAL, DMG_NUMBER_FLOAT_SPEED,
    MOB_HP_BAR_W, MOB_HP_BAR_H, PLACEABLE_HP_BAR_W, PLACEABLE_HP_BAR_H,
    HOTBAR_SLOTS, HOTBAR_SLOT_SIZE, HOTBAR_SLOT_GAP,
    MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
)
from core.utils import clamp, lerp
from core.ecs import EntityManager
from core.components import (
    Transform, Velocity, Renderable, Collider, Health, Inventory,
    LightSource, AI, PlayerStats, Equipment, Projectile, Placeable,
    Storage, Turret, Building,
)
from data import (
    ITEM_DATA, ITEM_CATEGORIES, RECIPES, RANGED_DATA, AMMO_BONUS_DAMAGE,
    ARMOR_VALUES, MOB_DATA, WAVE_MOB_TIERS, WAVE_RANGED_MOBS,
    WAVE_BOSS_MOBS, SPELL_DATA, SPELL_RECHARGE, BOMB_DATA,
    get_item_color,
    # day/night & event constants (split from core.constants during reorg)
    DAY_LENGTH_BASE, NIGHT_SLEEP_SPEED_MULT,
    WAVE_SPAWN_RADIUS,
    MOB_RESPAWN_INTERVAL, MOB_RESPAWN_MIN_DIST, MOB_MAX_COUNT,
    MOB_RESPAWN_BATCH, RANGED_ENEMY_START_DAY,
    PER_DAY_SCALE_FACTOR, MOB_SPAWN_ATTEMPTS,
    GHOST_SPAWN_CHANCE, NIGHT_MOB_SPAWN_CHANCE, DARK_KNIGHT_SPAWN_CHANCE,
    FOREST_MOB_SPAWN_CHANCE, DIRT_MOB_SPAWN_CHANCE, ORC_SPAWN_CHANCE,
    GRASS_MOB_SPAWN_CHANCE, WAVE_SPAWN_RADIUS_VARIANCE, WAVE_RANGED_MOB_CHANCE,
    INITIAL_MOB_SPAWNS,
)
from world import World, WorldGenerator
from world.cave import CaveData
from core.camera import Camera
from rendering.particles import ParticleSystem
from textures import TextureGenerator
from ui.minimap import Minimap
from systems import (
    MovementSystem, PhysicsSystem, RenderSystem, DayNightCycle,
    AISystem, ProjectileSystem, TrapSystem, TurretSystem, WaveSystem,
    calc_melee_damage, calc_ranged_damage, calc_damage_reduction,
)
from gui import (
    ProgressBar, Tooltip, InventoryGrid, CraftingPanel, PauseMenu,
    CharacterMenu, ChestUI, EnchantmentTableUI,
)
from core.settings import (
    load_settings, save_settings,
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
    DISPLAY_WINDOWED, DISPLAY_FULLSCREEN, DISPLAY_BORDERLESS,
    DISPLAY_MODE_NAMES, RESOLUTION_PRESETS,
)
from game import save_load
from core.music import MusicManager
from game import combat as game_combat
from game import drawing as game_drawing
from game import entities as game_entities
from game import interaction as game_interaction
from game import menus as game_menus
from game import persistence as game_persistence

# ==========================================================================
# GAME
# ==========================================================================

class Game:
    def __init__(self, difficulty: int = DIFFICULTY_EASY) -> None:
        # Load persisted settings
        self.settings = load_settings()

        # Display setup — render at fixed internal res, scale to window
        self.display_mode: int = self.settings.get(
            'display_mode', DISPLAY_WINDOWED)
        self.window_w: int = self.settings.get('resolution_w', SCREEN_WIDTH)
        self.window_h: int = self.settings.get('resolution_h', SCREEN_HEIGHT)
        self._display = self._create_display()
        # Internal render surface (all game code draws here)
        self.screen = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        pygame.display.set_caption("Sandbox Survival RPG")

        # Letterbox state (computed in _present / _calc_letterbox)
        self._lb_scale: float = 1.0
        self._lb_ox: int = 0
        self._lb_oy: int = 0
        self._calc_letterbox()

        # Override pygame.mouse.get_pos to return internal coordinates
        self._original_mouse_get_pos = pygame.mouse.get_pos
        _game_ref = self
        def _scaled_mouse_get_pos() -> Tuple[int, int]:
            wx, wy = _game_ref._original_mouse_get_pos()
            s = max(0.001, _game_ref._lb_scale)
            ix = int((wx - _game_ref._lb_ox) / s)
            iy = int((wy - _game_ref._lb_oy) / s)
            return (int(clamp(ix, 0, INTERNAL_WIDTH - 1)),
                    int(clamp(iy, 0, INTERNAL_HEIGHT - 1)))
        pygame.mouse.get_pos = _scaled_mouse_get_pos

        self.clock = pygame.time.Clock()
        self.running = True
        self.dead = False
        self.paused = False
        self.seed = random.randint(0, 2**31 - 1)
        self.difficulty = self.settings.get('difficulty', difficulty)
        self.in_main_menu = True
        self.in_options_menu = False
        self.options_source: str = 'main'  # 'main' or 'pause'

        # Fonts
        self.font = pygame.font.SysFont('consolas', FONT_SIZE_MAIN)
        self.font_sm = pygame.font.SysFont('consolas', FONT_SIZE_SM)
        self.font_lg = pygame.font.SysFont('consolas', FONT_SIZE_LG, bold=True)
        self.font_xl = pygame.font.SysFont('consolas', FONT_SIZE_XL, bold=True)

        # Textures
        self.textures = TextureGenerator(seed=self.seed)
        self.textures.generate_all()

        # World
        self.world_gen = WorldGenerator(seed=self.seed)
        self.world = self.world_gen.generate(WORLD_WIDTH, WORLD_HEIGHT)

        # Caves — generates entrances on overworld + interiors
        self.caves = CaveData(self.seed, self.world)
        self.in_cave: int = -1  # -1 = overworld, 0..N = cave index
        self.overworld: Optional[World] = None  # snapshot while in cave
        self.cave_entities: List[int] = []  # entity IDs created for current cave
        self.cave_teleport_cd: float = 0.0  # cooldown to prevent teleport loop
        self.overworld_structures: list = []  # snapshot of structures when entering cave

        # ECS + systems
        self.em = EntityManager()
        self.movement = MovementSystem()
        self.physics = PhysicsSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.renderer = RenderSystem(self.screen)
        self.daynight = DayNightCycle(day_length=DAY_LENGTH_BASE)
        self.ai_system = AISystem()
        self.projectile_system = ProjectileSystem()
        self.trap_system = TrapSystem()
        self.turret_system = TurretSystem()
        self.wave_system = WaveSystem(difficulty=self.difficulty)
        self.camera = Camera()
        self.particles = ParticleSystem()

        # Player
        self.player_id = self._create_player()
        self._populate_world()

        # UI state
        self.show_inventory = False
        self.show_crafting = False
        self.show_character = False
        self.show_chest = False
        self.active_chest: Optional[int] = None
        self.show_enchant_table = False
        self.active_enchant_table: Optional[int] = None
        self.tooltip = Tooltip()

        # Placement preview mode
        self.placement_mode = False
        self.placement_item: Optional[str] = None
        self.placement_valid = True
        self.placement_rotation = 0  # 0=right, 1=down, 2=left, 3=up (90° CW per step)
        self.placement_rarity: str = 'common'
        self.placement_enchant: Optional[dict] = None
        self.placement_slot: Optional[int] = None

        # Spell targeting mode
        self.spell_targeting = False
        self.spell_item: Optional[str] = None
        self.spell_cooldowns: Dict[str, float] = {}  # spell_id -> remaining seconds
        # Active spell buffs: effect_name -> (level, value, remaining_time)
        self.active_buffs: Dict[str, Tuple[int, float, float]] = {}
        self.buff_regen_accum: float = 0.0  # accumulator for regen tick
        self.armor_regen_accum: float = 0.0  # accumulator for armor regen enchant
        # Pending mob speed restores: [(entity_id, original_speed, remaining_time)]
        self.speed_restores: List[Tuple[int, float, float]] = []

        inv_comp: Inventory = self.em.get_component(self.player_id, Inventory)
        self.inventory_ui = InventoryGrid(
            pygame.Rect(SCREEN_WIDTH // 2 - 195,
                        SCREEN_HEIGHT // 2 - 210, 390, 400),
            inv_comp, self.textures)
        self.crafting_ui = CraftingPanel(self.textures)
        self.pause_menu = PauseMenu()
        self.character_menu = CharacterMenu(self.textures)
        self.chest_ui = ChestUI(self.textures)
        self.enchant_table_ui = EnchantmentTableUI(self.textures)

        self.health_bar = ProgressBar(
            pygame.Rect(20, 16, 200, 18), 100, (210, 50, 50), (40, 15, 15))
        self.xp_bar = ProgressBar(
            pygame.Rect(20, 38, 200, 12), 50, (70, 160, 255), (20, 30, 50))
        self.minimap = Minimap()

        # Timers / cooldowns
        self.interact_cd = 0.0
        self.attack_cd = 0.0
        self.attack_anim = 0.0
        self.ranged_cd = 0.0
        self.player_hit_cd = 0.0
        self.damage_flash = 0.0
        self.mob_spawn_timer = 0.0
        self.campfire_heal_timer = 0.0
        self.night_dmg_timer = 0.0
        self.survival_timer = 0.0
        self.sleeping = False
        self.sleep_timer = 0.0

        self.dmg_numbers: List[Tuple[float, float, str,
                                     Tuple[int, int, int], float]] = []
        self.notification: str = ""
        self.notification_timer: float = 0.0

        # Music
        self.music_manager = MusicManager(self.settings)

    # -- helpers -----------------------------------------------------------
    def _return_held_item(self) -> None:
        """Return any held item from drag-drop back to inventory."""
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        if inv.held_item:
            item_id, count = inv.held_item
            inv.add_item_enchanted(
                item_id, inv.held_enchant, count, inv.held_rarity)
            inv.held_item = None
            inv.held_enchant = None
            inv.held_rarity = 'common'

    def _notify(self, msg: str, duration: float = NOTIFICATION_DURATION) -> None:
        self.notification = msg
        self.notification_timer = duration

    def _create_display(self) -> pygame.Surface:
        """Create or recreate the pygame display for current settings."""
        if self.display_mode == DISPLAY_FULLSCREEN:
            return pygame.display.set_mode(
                (self.window_w, self.window_h), pygame.FULLSCREEN)
        elif self.display_mode == DISPLAY_BORDERLESS:
            info = pygame.display.Info()
            self.window_w = info.current_w
            self.window_h = info.current_h
            return pygame.display.set_mode(
                (self.window_w, self.window_h), pygame.NOFRAME)
        else:
            return pygame.display.set_mode(
                (self.window_w, self.window_h), pygame.RESIZABLE)

    def _apply_display_settings(self) -> None:
        """Recreate display and persist settings."""
        self._display = self._create_display()
        self.settings['display_mode'] = self.display_mode
        self.settings['resolution_w'] = self.window_w
        self.settings['resolution_h'] = self.window_h
        save_settings(self.settings)

    def _toggle_fullscreen(self) -> None:
        """Toggle between windowed and fullscreen (Alt+Enter)."""
        if self.display_mode == DISPLAY_FULLSCREEN:
            self.display_mode = DISPLAY_WINDOWED
            self.window_w = self.settings.get('resolution_w', SCREEN_WIDTH)
            self.window_h = self.settings.get('resolution_h', SCREEN_HEIGHT)
        else:
            self.display_mode = DISPLAY_FULLSCREEN
            info = pygame.display.Info()
            self.window_w = info.current_w
            self.window_h = info.current_h
        self._apply_display_settings()

    def _calc_letterbox(self) -> None:
        """Recompute letterbox scale + offsets for current window size."""
        ww = max(1, self.window_w)
        wh = max(1, self.window_h)
        sx = ww / INTERNAL_WIDTH
        sy = wh / INTERNAL_HEIGHT
        self._lb_scale = min(sx, sy)
        sw = int(INTERNAL_WIDTH * self._lb_scale)
        sh = int(INTERNAL_HEIGHT * self._lb_scale)
        self._lb_ox = (ww - sw) // 2
        self._lb_oy = (wh - sh) // 2

    def _scale_mouse_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert actual window mouse pos to internal surface coords."""
        wx, wy = pos
        s = max(0.001, self._lb_scale)
        ix = int((wx - self._lb_ox) / s)
        iy = int((wy - self._lb_oy) / s)
        return (int(clamp(ix, 0, INTERNAL_WIDTH - 1)),
                int(clamp(iy, 0, INTERNAL_HEIGHT - 1)))

    def _present(self) -> None:
        """Scale internal surface to window with letterboxing and flip."""
        self._calc_letterbox()
        self._display.fill((0, 0, 0))
        sw = int(INTERNAL_WIDTH * self._lb_scale)
        sh = int(INTERNAL_HEIGHT * self._lb_scale)
        if sw == INTERNAL_WIDTH and sh == INTERNAL_HEIGHT:
            self._display.blit(self.screen, (self._lb_ox, self._lb_oy))
        else:
            scaled = pygame.transform.scale(self.screen, (sw, sh))
            self._display.blit(scaled, (self._lb_ox, self._lb_oy))
        pygame.display.flip()

    # ======================================================================
    # ENTITY CREATION
    # ======================================================================
    def _create_player(self) -> int:
        return game_entities.create_player(self)

    def _create_mob(self, x: float, y: float, mob_type: str) -> int:
        return game_entities.create_mob(self, x, y, mob_type)

    def _populate_world(self) -> None:
        game_entities.populate_world(self)

    def _spawn_mob(self) -> None:
        game_entities.spawn_mob(self)

    def _spawn_wave_mobs(self, count: int, tier: int,
                         include_ranged: bool = False,
                         include_boss: bool = False) -> None:
        game_entities.spawn_wave_mobs(self, count, tier, include_ranged, include_boss)

    def _check_cave_teleport(self, pt: Transform) -> None:
        """Check if player is standing on a cave entrance/exit and teleport."""
        if self.cave_teleport_cd > 0:
            return
        if self.in_cave < 0:
            # On overworld — check for entrance
            idx = self.caves.entrance_at(pt.x, pt.y)
            if idx is not None:
                self._enter_cave(idx)
        else:
            # Inside cave — check for exit
            if self.caves.at_exit(self.in_cave, pt.x, pt.y):
                self._exit_cave()

    def _enter_cave(self, cave_index: int) -> None:
        """Teleport player into cave interior."""
        # Save overworld reference
        self.overworld = self.world
        # Snapshot player-placed structures so they survive cave transition
        self.overworld_structures = game_entities.snapshot_structures(self)
        # Destroy non-player entities from overworld (we'll repopulate on exit)
        self._destroy_non_player_entities()
        # Swap to cave world
        self.world = self.caves.interiors[cave_index]
        self.in_cave = cave_index
        # Update physics bounds for smaller cave
        self.physics = PhysicsSystem(self.world.width, self.world.height)
        self.camera.set_bounds(self.world.width, self.world.height)
        # Place player near exit
        exp, eyp = self.caves.get_exit_pixel(cave_index)
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pt.x = exp
        pt.y = eyp - TILE_SIZE  # slightly above exit
        self.camera.follow(pt.x, pt.y)
        self.camera.snap()
        # Populate cave
        self._populate_cave(cave_index)
        self.cave_teleport_cd = 1.5
        self._notify(f"Entered cave {cave_index + 1}...")

    def _exit_cave(self) -> None:
        """Teleport player back to overworld."""
        cave_index = self.in_cave
        # Destroy cave entities
        self._destroy_non_player_entities()
        self.cave_entities.clear()
        # Restore overworld
        assert self.overworld is not None
        self.world = self.overworld
        self.overworld = None
        self.in_cave = -1
        # Restore physics bounds
        self.physics = PhysicsSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.camera.set_bounds(WORLD_WIDTH, WORLD_HEIGHT)
        # Place player at cave entrance on overworld
        epx, epy = self.caves.get_entrance_pixel(cave_index)
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pt.x = epx
        pt.y = epy + TILE_SIZE  # slightly below entrance
        self.camera.follow(pt.x, pt.y)
        self.camera.snap()
        # Repopulate overworld
        self._populate_world()
        # Restore player-placed structures that were saved on cave entry
        game_entities.restore_structures(self, self.overworld_structures)
        self.overworld_structures = []
        self.cave_teleport_cd = 1.5
        self._notify("Returned to the surface.")

    def _populate_cave(self, cave_index: int) -> None:
        game_entities.populate_cave(self, cave_index)

    def _create_cave_mob(self, x: float, y: float, mob_type: str) -> int:
        return game_entities.create_cave_mob(self, x, y, mob_type)

    def _create_cave_resource(self, x: float, y: float,
                              texture_key: str, drop_item: str) -> int:
        return game_entities.create_cave_resource(self, x, y, texture_key, drop_item)

    def _create_cave_chest(self, x: float, y: float,
                           cave_index: int, rng: random.Random) -> int:
        return game_entities.create_cave_chest(self, x, y, cave_index, rng)

    def _destroy_non_player_entities(self) -> None:
        game_entities.destroy_non_player_entities(self)

    def run(self) -> None:
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)  # Cap at 50ms to prevent velocity spikes
            # Handle global display events
            self._process_display_events()
            if self.in_options_menu:
                self._handle_options_events()
                self._draw_options_menu()
            elif self.in_main_menu:
                self._handle_main_menu_events()
                self._draw_main_menu()
            elif not self.dead and not self.paused:
                self._handle_events()
                self._update(dt)
                self._render()
            else:
                self._handle_events()
                # Animate particles & dmg numbers even while paused/dead
                self.particles.update(dt)
                self.dmg_numbers = [
                    (x, y - 40 * dt, t, c, l - dt)
                    for x, y, t, c, l in self.dmg_numbers if l - dt > 0
                ]
                self._render()
        pygame.quit()
        sys.exit()

    def _process_display_events(self) -> None:
        """Peek at event queue for resize / Alt+Enter without consuming."""
        for event in pygame.event.get(
                [pygame.VIDEORESIZE, pygame.VIDEOEXPOSE]):
            if event.type == pygame.VIDEORESIZE:
                if self.display_mode == DISPLAY_WINDOWED:
                    self.window_w = max(MIN_WINDOW_WIDTH, event.w)
                    self.window_h = max(MIN_WINDOW_HEIGHT, event.h)
                    self._display = pygame.display.set_mode(
                        (self.window_w, self.window_h), pygame.RESIZABLE)

    def _handle_main_menu_events(self) -> None:
        game_menus.handle_main_menu_events(self)

    def _draw_main_menu(self) -> None:
        game_menus.draw_main_menu(self)

    def _handle_options_events(self) -> None:
        game_menus.handle_options_events(self)

    def _close_options(self) -> None:
        game_menus.close_options(self)

    def _open_options_from_pause(self) -> None:
        game_menus.open_options_from_pause(self)

    def _draw_options_menu(self) -> None:
        game_menus.draw_options_menu(self)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # Alt+Enter fullscreen toggle (works in all states)
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and (event.mod & pygame.KMOD_ALT)):
                self._toggle_fullscreen()
                continue

            # Scale mouse positions from window coords to internal coords
            if hasattr(event, 'pos'):
                event.pos = self._scale_mouse_pos(event.pos)

            # --- Dead state ---
            if self.dead:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F9:
                        self._quick_load()
                    elif event.key == pygame.K_q:
                        self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check death screen buttons
                    mx, my = event.pos
                    btn_w = 200
                    bx = SCREEN_WIDTH // 2 - btn_w // 2
                    # Quick Load button
                    if pygame.Rect(bx, SCREEN_HEIGHT // 2 + 10, btn_w, 36).collidepoint(mx, my):
                        self._quick_load()
                    # Load Save button
                    elif pygame.Rect(bx, SCREEN_HEIGHT // 2 + 56, btn_w, 36).collidepoint(mx, my):
                        self.paused = True
                        self.dead = False
                    # Restart button
                    elif pygame.Rect(bx, SCREEN_HEIGHT // 2 + 102, btn_w, 36).collidepoint(mx, my):
                        self._full_restart()
                continue

            # --- Pause menu ---
            if self.paused:
                self.pause_menu.handle_event(
                    event,
                    save_cb=self._save_to_slot,
                    load_cb=self._load_from_slot,
                    delete_cb=self._delete_slot,
                    resume_cb=self._resume,
                    quit_cb=self._quit,
                    options_cb=self._open_options_from_pause,
                )
                continue

            # --- Global hotkeys ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.placement_mode:
                        self.placement_mode = False
                        self.placement_item = None
                        self.placement_rarity = 'common'
                        self.placement_enchant = None
                        self.placement_slot = None
                    elif self.spell_targeting:
                        self.spell_targeting = False
                        self.spell_item = None
                    elif (self.show_inventory or self.show_crafting
                            or self.show_character or self.show_chest
                            or self.show_enchant_table):
                        self._return_held_item()
                        self.show_inventory = False
                        self.show_crafting = False
                        self.show_character = False
                        self.show_chest = False
                        self.active_chest = None
                        self.chest_ui.split_dialog.close()
                        self.show_enchant_table = False
                        self.active_enchant_table = None
                    else:
                        self.paused = True
                    continue
                if event.key == pygame.K_i:
                    if self.show_inventory:
                        self._return_held_item()
                    self.show_inventory = not self.show_inventory
                    self.show_crafting = False
                    self.show_character = False
                    self.show_chest = False
                    self.active_chest = None
                    self.show_enchant_table = False
                    self.active_enchant_table = None
                    continue
                if event.key == pygame.K_c:
                    self._return_held_item()
                    self.show_crafting = not self.show_crafting
                    self.show_inventory = False
                    self.show_character = False
                    self.show_chest = False
                    self.active_chest = None
                    self.show_enchant_table = False
                    self.active_enchant_table = None
                    continue
                if event.key == pygame.K_p:
                    self._return_held_item()
                    self.show_character = not self.show_character
                    self.show_inventory = False
                    self.show_crafting = False
                    self.show_chest = False
                    self.active_chest = None
                    self.show_enchant_table = False
                    self.active_enchant_table = None
                    continue
                if event.key == pygame.K_f:
                    self._use_equipped_item()
                    continue
                if event.key == pygame.K_F5:
                    self._quick_save()
                    continue
                if event.key == pygame.K_F9:
                    self._quick_load()
                    continue

                # Number keys 1-6 → hotbar
                inv = self.em.get_component(self.player_id, Inventory)
                for n in range(1, 7):
                    if event.key == getattr(pygame, f'K_{n}'):
                        inv.equipped_slot = n - 1

            # Mouse-wheel for hotbar (only when no overlay menus are open)
            if event.type == pygame.MOUSEWHEEL:
                if (not self.placement_mode and not self.spell_targeting
                        and not self.show_inventory and not self.show_crafting
                        and not self.show_character and not self.show_chest
                        and not self.show_enchant_table):
                    inv = self.em.get_component(self.player_id, Inventory)
                    inv.equipped_slot = (inv.equipped_slot - event.y) % 6

            # Placement mode rotation
            if self.placement_mode and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.placement_rotation = (self.placement_rotation + 1) % 4
                    continue

            # Placement mode click
            if self.placement_mode and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._placement_confirm()
                    continue
                elif event.button == 3:
                    self.placement_mode = False
                    self.placement_item = None
                    self.placement_rarity = 'common'
                    self.placement_enchant = None
                    self.placement_slot = None
                    continue

            # Spell targeting click
            if self.spell_targeting and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._spell_cast_at_mouse()
                    continue
                elif event.button == 3:
                    self.spell_targeting = False
                    self.spell_item = None
                    continue

            # Overlay event handling
            if self.show_chest and self.active_chest is not None:
                stor = self.em.get_component(self.active_chest, Storage)
                if stor:
                    is_cave = not self.em.has_component(
                        self.active_chest, Building)
                    self.chest_ui.handle_event(
                        event, stor,
                        self.em.get_component(self.player_id, Inventory),
                        is_cave_chest=is_cave)
            if self.show_enchant_table and self.active_enchant_table is not None:
                stor = self.em.get_component(self.active_enchant_table, Storage)
                if stor:
                    self.enchant_table_ui.handle_event(
                        event, stor,
                        self.em.get_component(self.player_id, Inventory))
            if self.show_inventory:
                self.inventory_ui.handle_event(event)
            if self.show_crafting:
                self.crafting_ui.handle_event(
                    event,
                    self.em.get_component(self.player_id, Inventory),
                    self._craft)
            if self.show_character:
                self.character_menu.handle_event(
                    event,
                    self.em.get_component(self.player_id, PlayerStats),
                    self.em.get_component(self.player_id, Equipment),
                    self.em.get_component(self.player_id, Inventory),
                )

    # ======================================================================
    # UPDATE
    # ======================================================================
    def _update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        pv: Velocity = self.em.get_component(self.player_id, Velocity)
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pr: Renderable = self.em.get_component(self.player_id, Renderable)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)

        # Movement (AGI speed bonus with cap)
        agi_bonus = min(AGI_SPEED_BONUS_CAP, ps.agility * AGI_SPEED_BONUS)
        base_speed = PLAYER_BASE_SPEED * (1.0 + agi_bonus)
        if keys[pygame.K_w]:
            pv.vy -= base_speed * dt * MOVEMENT_ACCEL_MULT
        if keys[pygame.K_s]:
            pv.vy += base_speed * dt * MOVEMENT_ACCEL_MULT
        if keys[pygame.K_a]:
            pv.vx -= base_speed * dt * MOVEMENT_ACCEL_MULT
        if keys[pygame.K_d]:
            pv.vx += base_speed * dt * MOVEMENT_ACCEL_MULT
        if pv.vx < -SPRITE_FLIP_THRESHOLD:
            pr.flip_x = True
        elif pv.vx > SPRITE_FLIP_THRESHOLD:
            pr.flip_x = False

        # Systems tick
        self.movement.update(dt, self.em)
        self.physics.update(dt, self.em, self.world)
        self.ai_system.update(dt, self.em, self.player_id,
                              on_ranged_fire=self._on_enemy_ranged_fire)
        self.projectile_system.update(dt, self.em, on_hit=self._on_proj_hit)
        self.trap_system.update(dt, self.em, on_hit=self._on_trap_hit)
        self.turret_system.update(dt, self.em, on_fire=self._on_turret_fire)
        self.daynight.update(dt)

        # Cave daily regeneration — rebuild caves when a new day starts
        if self.daynight.day_changed:
            if self.in_cave >= 0:
                self._exit_cave()
            self.caves.regenerate(self.daynight.day_number)

        self.music_manager.update(self.daynight.is_night())
        self.camera.follow(pt.x, pt.y)
        self.camera.update(dt)
        self.particles.update(dt)

        # Cave teleport check
        self._check_cave_teleport(pt)

        # Wave system — disabled inside caves
        if self.in_cave < 0:
            wave_req = self.wave_system.update(
                dt, self.daynight.is_night(), self.daynight.day_number)
            if wave_req:
                self._spawn_wave_mobs(
                    wave_req['count'], wave_req['tier'],
                    include_ranged=wave_req.get('ranged', False),
                    include_boss=wave_req.get('boss', False))
                if self.wave_system.wave_spawned <= wave_req['count']:
                    self._notify("Defend yourself!", 2.5)

        # Sleeping (bed mechanic) — only speeds night while on bed
        if self.sleeping:
            self.sleep_timer -= dt
            if self.sleep_timer <= 0 or not self.daynight.is_night():
                self.sleeping = False
                self.daynight.reset_speed()
                self._notify("You wake up refreshed.")

        # Cooldowns
        self.interact_cd = max(0, self.interact_cd - dt)
        self.attack_cd = max(0, self.attack_cd - dt)
        self.attack_anim = max(0, self.attack_anim - dt)
        self.ranged_cd = max(0, self.ranged_cd - dt)
        self.player_hit_cd = max(0, self.player_hit_cd - dt)
        self.damage_flash = max(0, self.damage_flash - dt)
        self.notification_timer = max(0, self.notification_timer - dt)
        self.cave_teleport_cd = max(0, self.cave_teleport_cd - dt)

        # Spell cooldowns
        expired_spells = [k for k, v in self.spell_cooldowns.items()
                          if v - dt <= 0]
        for k in expired_spells:
            del self.spell_cooldowns[k]
        for k in list(self.spell_cooldowns):
            self.spell_cooldowns[k] -= dt

        # Spell buff ticking
        expired_buffs = []
        for effect, (level, value, remaining) in self.active_buffs.items():
            remaining -= dt
            if remaining <= 0:
                expired_buffs.append(effect)
            else:
                self.active_buffs[effect] = (level, value, remaining)
        for effect in expired_buffs:
            del self.active_buffs[effect]
            self._notify(f"{effect.title()} buff expired.")
        # Regen buff: heal 'value' HP per second
        if 'regen' in self.active_buffs:
            _, regen_val, _ = self.active_buffs['regen']
            self.buff_regen_accum += dt
            if self.buff_regen_accum >= 1.0:
                self.buff_regen_accum -= 1.0
                ph_r: Health = self.em.get_component(self.player_id, Health)
                if ph_r.current < ph_r.maximum:
                    ph_r.heal(int(regen_val))
                    self.health_bar.set_value(ph_r.current)
                    self.dmg_numbers.append(
                        (pt.x, pt.y - 20, f'+{int(regen_val)}', GREEN, 0.5))
        else:
            self.buff_regen_accum = 0.0

        # Armor regen enchant: passive HP/sec while regen-enchanted armor is equipped
        eq_regen: Equipment = self.em.get_component(self.player_id, Equipment)
        armor_ench = eq_regen.enchantments.get('armor')
        from enchantments.effects import get_enchant_regen_rate
        armor_regen_rate = get_enchant_regen_rate(armor_ench)
        if armor_regen_rate > 0:
            self.armor_regen_accum += dt
            if self.armor_regen_accum >= 1.0:
                self.armor_regen_accum -= 1.0
                ph_ar: Health = self.em.get_component(self.player_id, Health)
                if ph_ar.current < ph_ar.maximum:
                    ph_ar.heal(armor_regen_rate)
                    self.health_bar.set_value(ph_ar.current)
                    self.dmg_numbers.append(
                        (pt.x, pt.y - 24, f'+{armor_regen_rate}', (50, 255, 50), 0.5))
        else:
            self.armor_regen_accum = 0.0

        # Ice slow speed restores
        self._tick_speed_restores(dt)

        # Melee attack
        if keys[pygame.K_SPACE] and self.attack_cd == 0:
            self._attack()
            cd = max(MIN_ATTACK_COOLDOWN,
                     BASE_ATTACK_COOLDOWN - ps.agility * AGILITY_COOLDOWN_REDUCTION)
            self.attack_cd = cd
            self.attack_anim = ATTACK_ANIM_DURATION

        # Ranged attack (R key)
        if keys[pygame.K_r] and self.ranged_cd == 0:
            self._ranged_attack()

        # Interact
        if keys[pygame.K_e] and self.interact_cd == 0:
            self._interact()
            self.interact_cd = INTERACT_COOLDOWN

        # Damage numbers decay
        self.dmg_numbers = [
            (x, y - DMG_NUMBER_FLOAT_SPEED * dt, t, c, l - dt)
            for x, y, t, c, l in self.dmg_numbers if l - dt > 0
        ]

        # Kill dead mobs
        for eid in list(self.em.get_entities_with(Health, AI)):
            h: Health = self.em.get_component(eid, Health)
            if not h.is_alive():
                self._on_mob_killed(eid)

        # Kill dead placeables
        for eid in list(self.em.get_entities_with(Health, Placeable)):
            if self.em.has_component(eid, AI):
                continue
            h = self.em.get_component(eid, Health)
            if not h.is_alive():
                td = self.em.get_component(eid, Transform)
                self.particles.emit(td.x + 10, td.y + 10, 8, GRAY, 40, 0.3)
                if self.active_chest == eid:
                    self.show_chest = False
                    self.active_chest = None
                    self.chest_ui.split_dialog.close()
                if self.active_enchant_table == eid:
                    self.show_enchant_table = False
                    self.active_enchant_table = None
                self.em.destroy_entity(eid)

        # Mob contact damage
        self._check_contact_damage(pt)

        # Enemy projectile damage to player
        self._check_enemy_projectile_damage(pt)

        # Campfire healing
        self._campfire_heal(dt, pt)

        # Night damage
        self._night_damage(dt, pt)

        # Mob respawning — disabled inside caves
        if self.in_cave < 0:
            self.mob_spawn_timer += dt
            _, _, spawn_mult, _ = DIFFICULTY_MULTIPLIERS.get(
                self.difficulty, (1.0, 1.0, 1.0, 1.0))
            respawn_interval = MOB_RESPAWN_INTERVAL / spawn_mult
            if self.mob_spawn_timer > respawn_interval:
                self.mob_spawn_timer = 0.0
                mob_count = len(self.em.get_entities_with(AI))
                if mob_count < MOB_MAX_COUNT:
                    # Spawn a batch when population is low
                    batch = min(MOB_RESPAWN_BATCH, MOB_MAX_COUNT - mob_count)
                    for _ in range(batch):
                        self._spawn_mob()

        # HUD refresh
        self.survival_timer += dt
        if self.survival_timer > HUD_REFRESH_INTERVAL:
            self.survival_timer = 0.0
            ph: Health = self.em.get_component(self.player_id, Health)
            self.health_bar.max_value = ph.maximum
            self.health_bar.set_value(ph.current)
            self.xp_bar.max_value = ps.xp_to_next
            self.xp_bar.set_value(ps.xp)

    # ======================================================================
    # ACTIONS
    # ======================================================================
    def _get_attack_damage(self) -> int:
        return game_combat.get_attack_damage(self)

    def _get_attack_range(self) -> float:
        return game_combat.get_attack_range(self)

    def _attack(self) -> None:
        game_combat.attack(self)

    def _ranged_attack(self) -> None:
        game_combat.ranged_attack(self)

    def _on_proj_hit(self, target_eid: int, damage: int,
                     proj_t: Transform, proj: Optional[Projectile] = None) -> None:
        game_combat.on_proj_hit(self, target_eid, damage, proj_t, proj)

    def _schedule_speed_restore(self, eid: int, original_speed: float,
                                duration: float) -> None:
        game_combat.schedule_speed_restore(self, eid, original_speed, duration)

    def _tick_speed_restores(self, dt: float) -> None:
        game_combat.tick_speed_restores(self, dt)

    def _on_trap_hit(self, target_eid: int, damage: int,
                     trap_t: Transform) -> None:
        game_combat.on_trap_hit(self, target_eid, damage, trap_t)

    def _on_turret_fire(self, target_eid: int, damage: int,
                        turret_t: Transform, target_t: Transform,
                        enchant: Optional[dict] = None, arc_mobs: Optional[list] = None,
                        ice_slow_data: Optional[tuple] = None) -> None:
        game_combat.on_turret_fire(self, target_eid, damage, turret_t, target_t,
                                   enchant, arc_mobs, ice_slow_data)

    def _on_enemy_ranged_fire(self, mob_eid: int, mob_t: Transform,
                               player_t: Transform) -> None:
        game_combat.on_enemy_ranged_fire(self, mob_eid, mob_t, player_t)

    def _get_placement_tiles(self, tx: int, ty: int) -> List[Tuple[int, int]]:
        return game_interaction.get_placement_tiles(self, tx, ty)

    def _find_building_at_tiles(self, tiles: list) -> int:
        return game_interaction.find_building_at_tiles(self, tiles)

    def _placement_confirm(self) -> None:
        game_interaction.placement_confirm(self)

    def _spell_cast_at_mouse(self) -> None:
        game_combat.spell_cast_at_mouse(self)

    def _throw_bomb(self, bdata: dict) -> None:
        game_combat.throw_bomb(self, bdata)

    def _full_restart(self) -> None:
        """Reset game completely for death restart."""
        # Remove all entities
        for eid in list(self.em._entities):
            self.em.destroy_entity(eid)
        # New seed for fresh map
        self.seed = random.randint(0, 2**31 - 1)
        self.world_gen = WorldGenerator(seed=self.seed)
        self.world = self.world_gen.generate(WORLD_WIDTH, WORLD_HEIGHT)
        # Reset cave state
        self.caves = CaveData(self.seed, self.world)
        self.in_cave = -1
        self.overworld = None
        self.cave_entities.clear()
        # Restore physics for overworld
        self.physics = PhysicsSystem(WORLD_WIDTH, WORLD_HEIGHT)
        self.player_id = self._create_player()
        self._populate_world()
        self.daynight = DayNightCycle(day_length=DAY_LENGTH_BASE)
        self.wave_system = WaveSystem(difficulty=self.difficulty)
        self.dead = False
        self.paused = False
        self.sleeping = False
        self.placement_mode = False
        self.placement_item = None
        self.placement_rarity = 'common'
        self.placement_enchant = None
        self.placement_slot = None
        self.spell_targeting = False
        self.spell_item = None
        self.show_inventory = False
        self.show_crafting = False
        self.show_character = False
        self.show_chest = False
        self.active_chest = None
        self.show_enchant_table = False
        self.active_enchant_table = None
        self.spell_cooldowns.clear()
        self.active_buffs.clear()
        self.speed_restores.clear()
        self.buff_regen_accum = 0.0
        self.armor_regen_accum = 0.0
        self.cave_teleport_cd = 0.0
        inv_comp = self.em.get_component(self.player_id, Inventory)
        self.inventory_ui = InventoryGrid(
            pygame.Rect(SCREEN_WIDTH // 2 - 195,
                        SCREEN_HEIGHT // 2 - 210, 390, 400),
            inv_comp, self.textures)
        ph = self.em.get_component(self.player_id, Health)
        self.health_bar.max_value = ph.maximum
        self.health_bar.set_value(ph.current)
        ps = self.em.get_component(self.player_id, PlayerStats)
        self.xp_bar.max_value = ps.xp_to_next
        self.xp_bar.set_value(ps.xp)
        self.music_manager.start(self.daynight.is_night())
        self._notify("New game started.")

    def _interact(self) -> None:
        game_interaction.interact(self)

    def _use_equipped_item(self) -> None:
        game_interaction.use_equipped_item(self)

    def _place_item(self, item_id: str,
                    px: Optional[float] = None,
                    py: Optional[float] = None,
                    rotation: int = 0) -> None:
        game_interaction.place_item(self, item_id, px, py, rotation)

    def _craft(self, recipe: Dict[str, Any]) -> None:
        game_interaction.craft(self, recipe)

    def _on_mob_killed(self, eid: int) -> None:
        game_entities.on_mob_killed(self, eid)

    def _check_level_up(self, xp: int) -> None:
        game_entities.check_level_up(self, xp)

    def _check_contact_damage(self, pt: Transform) -> None:
        game_combat.check_contact_damage(self, pt)

    def _check_enemy_projectile_damage(self, pt: Transform) -> None:
        game_combat.check_enemy_projectile_damage(self, pt)

    def _campfire_heal(self, dt: float, pt: Transform) -> None:
        game_combat.campfire_heal(self, dt, pt)

    def _night_damage(self, dt: float, pt: Transform) -> None:
        game_combat.night_damage(self, dt, pt)

    def _respawn(self) -> None:
        self.dead = False
        pt: Transform = self.em.get_component(self.player_id, Transform)
        # If player dies in a cave, exit to overworld first
        if self.in_cave >= 0:
            cave_index = self.in_cave
            self._destroy_non_player_entities()
            self.cave_entities.clear()
            assert self.overworld is not None
            self.world = self.overworld
            self.overworld = None
            self.in_cave = -1
            self.physics = PhysicsSystem(WORLD_WIDTH, WORLD_HEIGHT)
            self.camera.set_bounds(WORLD_WIDTH, WORLD_HEIGHT)
            self._populate_world()
            # Respawn at cave entrance
            epx, epy = self.caves.get_entrance_pixel(cave_index)
            pt.x, pt.y = epx, epy + TILE_SIZE
        else:
            sx, sy = WorldGenerator.find_spawn(self.world)
            pt.x, pt.y = sx, sy
        ph: Health = self.em.get_component(self.player_id, Health)
        ph.current = ph.maximum
        self.health_bar.set_value(ph.current)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        for slot in list(inv.slots.keys()):
            item_id, count = inv.slots[slot]
            if count > 1:
                inv.slots[slot] = (item_id, max(1, count // 2))
            else:
                del inv.slots[slot]
                inv.slot_enchantments.pop(slot, None)
                inv.slot_rarities.pop(slot, 'common')
        self.camera.follow(pt.x, pt.y)
        self.camera.snap()
        self._notify("Respawned! You lost some items.")

    # ======================================================================
    # BED / SLEEP
    # ======================================================================
    def _try_sleep(self) -> None:
        game_interaction.try_sleep(self)

    def _build_save_data(self) -> Dict[str, Any]:
        return game_persistence.build_save_data(self)

    def _apply_save_data(self, data: Dict[str, Any]) -> None:
        game_persistence.apply_save_data(self, data)

    def _restore_structure(self, struct: Dict[str, Any]) -> None:
        game_persistence.restore_structure(self, struct)

    def _quick_save(self) -> None:
        game_persistence.quick_save(self)

    def _quick_load(self) -> None:
        game_persistence.quick_load(self)

    def _save_to_slot(self, slot: int) -> None:
        game_persistence.save_to_slot(self, slot)

    def _load_from_slot(self, slot: int) -> None:
        game_persistence.load_from_slot(self, slot)

    def _delete_slot(self, slot: int) -> None:
        game_persistence.delete_slot(self, slot)

    def _resume(self) -> None:
        self.paused = False

    def _quit(self) -> None:
        self.running = False

    # ======================================================================
    # RENDER
    # ======================================================================
    def _render(self) -> None:
        game_drawing.render(self)

    def _draw_world(self) -> None:
        game_drawing.draw_world(self)

    def _draw_lighting(self) -> None:
        game_drawing.draw_lighting(self)

    def _draw_mob_health_bars(self) -> None:
        game_drawing.draw_mob_health_bars(self)

    def _draw_placeable_health_bars(self) -> None:
        game_drawing.draw_placeable_health_bars(self)

    def _draw_attack_arc(self) -> None:
        game_drawing.draw_attack_arc(self)

    def _draw_damage_numbers(self) -> None:
        game_drawing.draw_damage_numbers(self)

    def _draw_hotbar(self) -> None:
        game_drawing.draw_hotbar(self)

    def _draw_hud(self) -> None:
        game_drawing.draw_hud(self)

    def _draw_death_screen(self) -> None:
        game_drawing.draw_death_screen(self)

    def _draw_placement_preview(self) -> None:
        game_drawing.draw_placement_preview(self)

    def _draw_spell_targeting(self) -> None:
        game_drawing.draw_spell_targeting(self)

    def _draw_boss_glow(self) -> None:
        game_drawing.draw_boss_glow(self)

if __name__ == "__main__":
    Game().run()
