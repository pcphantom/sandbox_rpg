# sandbox_rpg.py — Sandbox Survival RPG (Modular Edition)
# Python 3.10+ | pygame 2.5+
"""Entry point.  All game logic lives in dedicated modules."""
import pygame
import random
import sys
from typing import List, Tuple, Dict, Optional, Any

pygame.init()
pygame.font.init()

# -- project imports (order matters: constants first) ----------------------
from core.constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT,
    FPS, DIFFICULTY_EASY,
    FONT_SIZE_MAIN, FONT_SIZE_SM, FONT_SIZE_LG, FONT_SIZE_XL,
    NOTIFICATION_DURATION, MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT,
    HUD_HP_BAR_FG, HUD_HP_BAR_BG, HUD_XP_BAR_FG, HUD_XP_BAR_BG,
)
from core.utils import clamp
from core.ecs import EntityManager
from core.components import (
    Transform, Health, Inventory, AI, PlayerStats, Projectile, Turret,
)
from data import DAY_LENGTH_BASE
from world import World, WorldGenerator
from world.cave import CaveData
from core.camera import Camera
from rendering.particles import ParticleSystem
from textures import TextureGenerator
from ui.minimap import Minimap
from systems import (
    MovementSystem, PhysicsSystem, RenderSystem, DayNightCycle,
    AISystem, ProjectileSystem, TrapSystem, TurretSystem, WaveSystem,
)
from ui import (
    ProgressBar, Tooltip, InventoryGrid, CraftingPanel, PauseMenu,
    CharacterMenu, ChestUI, EnchantmentTableUI, StoneOvenUI,
)
from core.settings import (
    load_settings, save_settings,
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
    DISPLAY_WINDOWED, DISPLAY_FULLSCREEN, DISPLAY_BORDERLESS,
)
from core.music import MusicManager
from ui.command_bar import CommandBar
from game import combat as game_combat
from game import drawing as game_drawing
from game import entities as game_entities
from game import interaction as game_interaction
from game import menus as game_menus
from game import persistence as game_persistence
from game import events as game_events
from game import update as game_update

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

        # Day-based respawn tracking (must be set before _populate_world)
        self._last_resource_respawn_day: int = 1
        self._last_cave_reset_day: int = 1
        # Harvested overworld resource grid positions (cleared on respawn day)
        self.harvested_resources: set = set()
        # Cave entity snapshots: cave_index -> list of entity dicts
        # Persists cave state between entries/exits so caves don't reset
        self.cave_snapshots: Dict[int, list] = {}

        self._populate_world()

        # UI state
        self.show_inventory = False
        self.show_crafting = False
        self.show_character = False
        self.show_chest = False
        self.active_chest: Optional[int] = None
        self.show_enchant_table = False
        self.active_enchant_table: Optional[int] = None
        self.show_stone_oven = False
        self.active_stone_oven: Optional[int] = None
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
        self.stone_oven_ui = StoneOvenUI(self.textures)

        self.health_bar = ProgressBar(
            pygame.Rect(20, 16, 200, 18), 100, HUD_HP_BAR_FG, HUD_HP_BAR_BG)
        self.xp_bar = ProgressBar(
            pygame.Rect(20, 38, 200, 12), 50, HUD_XP_BAR_FG, HUD_XP_BAR_BG)
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

        # Command bar (F12) and cheats
        self.command_bar = CommandBar()
        self.cheats_enabled: bool = False
        self.god_mode: bool = False
        self.show_cheat_help: bool = False

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
        # Populate cave — restore snapshot if exists, otherwise fresh populate
        if cave_index in self.cave_snapshots:
            game_entities.restore_cave_snapshot(self, cave_index,
                                                self.cave_snapshots[cave_index])
        else:
            self._populate_cave(cave_index)
        self.cave_teleport_cd = 1.5
        self._notify(f"Entered cave {cave_index + 1}...")

    def _exit_cave(self) -> None:
        """Teleport player back to overworld."""
        cave_index = self.in_cave
        # Snapshot cave entities before destroying them
        self.cave_snapshots[cave_index] = game_entities.snapshot_cave_entities(self)
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
        game_events.handle_events(self)

    # ======================================================================
    # UPDATE
    # ======================================================================
    def _update(self, dt: float) -> None:
        game_update.update(self, dt)

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
        self.harvested_resources.clear()
        self.cave_snapshots.clear()
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
        self.show_stone_oven = False
        self.active_stone_oven = None
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
            # Snapshot cave state before leaving
            self.cave_snapshots[cave_index] = game_entities.snapshot_cave_entities(self)
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
