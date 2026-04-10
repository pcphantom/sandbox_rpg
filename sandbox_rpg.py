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
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, WORLD_WIDTH, WORLD_HEIGHT,
    FPS, BLACK, WHITE, YELLOW, RED, GREEN, CYAN, GRAY, ORANGE, DARK_GRAY,
    PURPLE,
    TILE_WATER, TILE_GRASS, TILE_DIRT, TILE_SAND, TILE_STONE_FLOOR,
    TILE_STONE_WALL, TILE_FOREST, QUICK_SAVE_SLOT, INVENTORY_TOTAL_SLOTS,
    MIN_ATTACK_COOLDOWN, BASE_ATTACK_COOLDOWN, AGILITY_COOLDOWN_REDUCTION,
    SLEEP_DURATION, SLEEP_TIME_MULTIPLIER,
    WALL_HP, TURRET_HP, TURRET_RANGE, TURRET_DAMAGE, TURRET_COOLDOWN,
    CHEST_CAPACITY, WAVE_SPAWN_RADIUS,
    DAY_LENGTH_BASE, NIGHT_SLEEP_SPEED_MULT,
    DIFFICULTY_EASY, DIFFICULTY_NORMAL, DIFFICULTY_HARD, DIFFICULTY_HARDCORE,
    DIFFICULTY_NAMES, DIFFICULTY_MULTIPLIERS,
    MOB_RESPAWN_INTERVAL, RANGED_ENEMY_START_DAY,
    PLACEMENT_PREVIEW_COLOR, PLACEMENT_INVALID_COLOR,
)
from utils import clamp, lerp
from ecs import EntityManager
from components import (
    Transform, Velocity, Renderable, Collider, Health, Inventory,
    LightSource, AI, PlayerStats, Equipment, Projectile, Placeable,
    Storage, Turret, Building,
)
from items_data import (
    ITEM_DATA, ITEM_CATEGORIES, RECIPES, RANGED_DATA, AMMO_BONUS_DAMAGE,
    ARMOR_VALUES, MOB_DATA, WAVE_MOB_TIERS, WAVE_RANGED_MOBS,
    WAVE_BOSS_MOBS, SPELL_DATA,
)
from world import World, WorldGenerator
from camera import Camera
from particles import ParticleSystem
from textures import TextureGenerator
from minimap import Minimap
from systems import (
    MovementSystem, PhysicsSystem, RenderSystem, DayNightCycle,
    AISystem, ProjectileSystem, TrapSystem, TurretSystem, WaveSystem,
    calc_melee_damage, calc_ranged_damage, calc_damage_reduction,
)
from gui import (
    ProgressBar, Tooltip, InventoryGrid, CraftingPanel, PauseMenu,
    CharacterMenu, ChestUI,
)
from settings import (
    load_settings, save_settings,
    INTERNAL_WIDTH, INTERNAL_HEIGHT,
    DISPLAY_WINDOWED, DISPLAY_FULLSCREEN, DISPLAY_BORDERLESS,
    DISPLAY_MODE_NAMES, RESOLUTION_PRESETS,
)
import save_load
from music import MusicManager

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

        # Override pygame.mouse.get_pos to return internal coordinates
        self._original_mouse_get_pos = pygame.mouse.get_pos
        _game_ref = self
        def _scaled_mouse_get_pos() -> Tuple[int, int]:
            wx, wy = _game_ref._original_mouse_get_pos()
            sw = max(1, _game_ref.window_w)
            sh = max(1, _game_ref.window_h)
            return (int(wx * INTERNAL_WIDTH / sw),
                    int(wy * INTERNAL_HEIGHT / sh))
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
        self.font = pygame.font.SysFont('consolas', 16)
        self.font_sm = pygame.font.SysFont('consolas', 13)
        self.font_lg = pygame.font.SysFont('consolas', 22, bold=True)
        self.font_xl = pygame.font.SysFont('consolas', 48, bold=True)

        # Textures
        self.textures = TextureGenerator(seed=self.seed)
        self.textures.generate_all()

        # World
        self.world_gen = WorldGenerator(seed=self.seed)
        self.world = self.world_gen.generate(WORLD_WIDTH, WORLD_HEIGHT)

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
        self.tooltip = Tooltip()

        # Placement preview mode
        self.placement_mode = False
        self.placement_item: Optional[str] = None
        self.placement_valid = True
        self.placement_rotation = 0  # 0=right, 1=down, 2=left, 3=up (90° CW per step)

        # Spell targeting mode
        self.spell_targeting = False
        self.spell_item: Optional[str] = None

        inv_comp: Inventory = self.em.get_component(self.player_id, Inventory)
        self.inventory_ui = InventoryGrid(
            pygame.Rect(SCREEN_WIDTH // 2 - 195,
                        SCREEN_HEIGHT // 2 - 180, 390, 340),
            inv_comp, self.textures)
        self.crafting_ui = CraftingPanel(self.textures)
        self.pause_menu = PauseMenu()
        self.character_menu = CharacterMenu(self.textures)
        self.chest_ui = ChestUI(self.textures)

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
    def _notify(self, msg: str, duration: float = 2.5) -> None:
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

    def _scale_mouse_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Convert actual window mouse pos to internal surface coords."""
        wx, wy = pos
        ix = int(wx * INTERNAL_WIDTH / max(1, self.window_w))
        iy = int(wy * INTERNAL_HEIGHT / max(1, self.window_h))
        return (int(clamp(ix, 0, INTERNAL_WIDTH - 1)),
                int(clamp(iy, 0, INTERNAL_HEIGHT - 1)))

    def _present(self) -> None:
        """Scale internal surface to window and flip."""
        if (self.window_w == INTERNAL_WIDTH
                and self.window_h == INTERNAL_HEIGHT):
            self._display.blit(self.screen, (0, 0))
        else:
            scaled = pygame.transform.scale(
                self.screen, (self.window_w, self.window_h))
            self._display.blit(scaled, (0, 0))
        pygame.display.flip()

    # ======================================================================
    # ENTITY CREATION
    # ======================================================================
    def _create_player(self) -> int:
        eid = self.em.create_entity()
        sx, sy = WorldGenerator.find_spawn(self.world)
        self.em.add_component(eid, Transform(sx, sy, 1))
        self.em.add_component(eid, Velocity(0, 0, 0.82))
        self.em.add_component(eid, Renderable(
            self.textures.get('player'), layer=5))
        self.em.add_component(eid, Collider(20, 28, True))
        self.em.add_component(eid, Health(100))
        self.em.add_component(eid, Inventory(INVENTORY_TOTAL_SLOTS))
        self.em.add_component(eid, PlayerStats())
        self.em.add_component(eid, Equipment())
        inv: Inventory = self.em.get_component(eid, Inventory)
        inv.add_item('wood', 5)
        inv.add_item('stone', 3)
        return eid

    def _create_mob(self, x: float, y: float, mob_type: str) -> int:
        data = MOB_DATA[mob_type]
        tex_key = mob_type
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(x, y))
        self.em.add_component(eid, Velocity(
            random.uniform(-20, 20), random.uniform(-20, 20), 0.9))
        self.em.add_component(eid, Renderable(
            self.textures.get(tex_key), layer=3))
        surf = self.textures.get(tex_key)
        self.em.add_component(eid, Collider(
            surf.get_width(), surf.get_height(), data['solid']))
        # Apply difficulty multipliers
        hp_mult, dmg_mult, _, _ = DIFFICULTY_MULTIPLIERS.get(
            self.difficulty, (1.0, 1.0, 1.0, 1.0))
        # Per-day scaling: +5% hp/dmg per day
        day_scale = 1.0 + max(0, (self.daynight.day_number - 1)) * 0.05
        scaled_hp = int(data['hp'] * hp_mult * day_scale)
        scaled_dmg = int(data['damage'] * dmg_mult * day_scale)
        self.em.add_component(eid, Health(scaled_hp))
        mob_ai = AI('wander', mob_type)
        mob_ai.speed = data['speed']
        mob_ai.detection_range = data['detection']
        mob_ai.contact_damage = scaled_dmg
        mob_ai.xp_value = data['xp']
        # Ranged enemy setup
        if data.get('ranged', False):
            mob_ai.is_ranged = True
            mob_ai.ranged_damage = int(data.get('ranged_damage', 10) * dmg_mult * day_scale)
            mob_ai.ranged_range = data.get('ranged_range', 200.0)
            mob_ai.ranged_cooldown = data.get('ranged_cooldown', 2.0)
            mob_ai.ranged_speed = data.get('ranged_speed', 350.0)
        # Boss setup
        if data.get('boss', False):
            mob_ai.is_boss = True
            mob_ai.glow_color = data.get('glow_color', (255, 60, 60))
        self.em.add_component(eid, mob_ai)
        return eid

    def _populate_world(self) -> None:
        rng = random.Random(self.seed + 12345)
        # Trees — denser in forest/grass biomes
        for _ in range(350):
            x = rng.randint(5, WORLD_WIDTH - 5)
            y = rng.randint(5, WORLD_HEIGHT - 5)
            tile = self.world.get_tile(x, y)
            if tile in (TILE_GRASS, TILE_FOREST):
                eid = self.em.create_entity()
                self.em.add_component(eid, Transform(
                    x * TILE_SIZE + 8, y * TILE_SIZE - 16))
                self.em.add_component(eid, Renderable(
                    self.textures.get('tree'), layer=2))
                self.em.add_component(eid, Collider(24, 32, True))
        # Extra trees in forest
        for _ in range(150):
            x = rng.randint(5, WORLD_WIDTH - 5)
            y = rng.randint(5, WORLD_HEIGHT - 5)
            if self.world.get_tile(x, y) == TILE_FOREST:
                eid = self.em.create_entity()
                self.em.add_component(eid, Transform(
                    x * TILE_SIZE + 8, y * TILE_SIZE - 16))
                self.em.add_component(eid, Renderable(
                    self.textures.get('tree'), layer=2))
                self.em.add_component(eid, Collider(24, 32, True))
        # Rocks
        for _ in range(200):
            x = rng.randint(5, WORLD_WIDTH - 5)
            y = rng.randint(5, WORLD_HEIGHT - 5)
            if self.world.get_tile(x, y) in (TILE_GRASS, TILE_DIRT,
                                              TILE_STONE_FLOOR, TILE_FOREST):
                eid = self.em.create_entity()
                self.em.add_component(eid, Transform(
                    x * TILE_SIZE + 4, y * TILE_SIZE + 6))
                self.em.add_component(eid, Renderable(
                    self.textures.get('rock'), layer=1))
                self.em.add_component(eid, Collider(26, 18, True))
        # Initial mobs — diverse mix
        mob_spawns = [
            ('slime', TILE_GRASS, 25),
            ('wolf', TILE_FOREST, 10),
            ('spider', TILE_FOREST, 8),
            ('goblin', TILE_DIRT, 5),
        ]
        for mob_type, biome, count in mob_spawns:
            for _ in range(count):
                x = rng.randint(5, WORLD_WIDTH - 5)
                y = rng.randint(5, WORLD_HEIGHT - 5)
                tile = self.world.get_tile(x, y)
                if tile == biome or (biome == TILE_GRASS and tile == TILE_FOREST):
                    self._create_mob(x * TILE_SIZE + 8, y * TILE_SIZE + 8,
                                     mob_type)

    def _spawn_mob(self) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        for _ in range(20):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
            wx, wy = x * TILE_SIZE, y * TILE_SIZE
            if math.hypot(wx - pt.x, wy - pt.y) < 400:
                continue
            if self.world.is_solid(x, y):
                continue
            tile = self.world.get_tile(x, y)
            is_night = self.daynight.is_night()
            # Choose mob type based on biome & time
            if is_night and random.random() < 0.25:
                mob = 'ghost'
            elif is_night and random.random() < 0.4:
                mob = 'dark_knight' if random.random() < 0.15 else 'skeleton'
            elif tile == TILE_FOREST and random.random() < 0.5:
                mob = random.choice(['wolf', 'spider'])
            elif tile in (TILE_DIRT, TILE_STONE_FLOOR) and random.random() < 0.4:
                mob = 'orc' if random.random() < 0.2 else 'goblin'
            elif tile == TILE_GRASS and random.random() < 0.4:
                mob = 'wolf'
            else:
                mob = 'slime'
            self._create_mob(wx, wy, mob)
            return

    def _spawn_wave_mobs(self, count: int, tier: int,
                         include_ranged: bool = False,
                         include_boss: bool = False) -> None:
        """Spawn wave mobs near player buildings (or player if no buildings)."""
        pt: Transform = self.em.get_component(self.player_id, Transform)
        target_x, target_y = pt.x, pt.y
        buildings = self.em.get_entities_with(Transform, Building)
        if buildings:
            b_eid = random.choice(buildings)
            bt = self.em.get_component(b_eid, Transform)
            target_x, target_y = bt.x, bt.y

        available: list[str] = []
        for t in range(min(tier + 1, len(WAVE_MOB_TIERS))):
            available.extend(WAVE_MOB_TIERS[t])

        for i in range(count):
            angle = random.uniform(0, math.tau)
            dist = WAVE_SPAWN_RADIUS + random.uniform(0, 100)
            wx = target_x + math.cos(angle) * dist
            wy = target_y + math.sin(angle) * dist
            wx = clamp(wx, TILE_SIZE * 2, (WORLD_WIDTH - 2) * TILE_SIZE)
            wy = clamp(wy, TILE_SIZE * 2, (WORLD_HEIGHT - 2) * TILE_SIZE)

            # Boss spawn on the designated mob
            if include_boss and i == 0:
                mob_type = random.choice(WAVE_BOSS_MOBS)
            elif include_ranged and random.random() < 0.25:
                mob_type = random.choice(WAVE_RANGED_MOBS)
            else:
                mob_type = random.choice(available)
            self._create_mob(wx, wy, mob_type)

    # ======================================================================
    # MAIN LOOP
    # ======================================================================
    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
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
                    self.window_w = max(640, event.w)
                    self.window_h = max(480, event.h)
                    self._display = pygame.display.set_mode(
                        (self.window_w, self.window_h), pygame.RESIZABLE)

    def _handle_main_menu_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            # Alt+Enter fullscreen toggle
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and (event.mod & pygame.KMOD_ALT)):
                self._toggle_fullscreen()
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.in_main_menu = False
                    self.music_manager.start(self.daynight.is_night())
                elif event.key == pygame.K_q:
                    self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = self._scale_mouse_pos(event.pos)
                btn_w, btn_h = 220, 44
                bx = SCREEN_WIDTH // 2 - btn_w // 2
                # Start Game button
                start_y = 300
                if pygame.Rect(bx, start_y, btn_w, btn_h).collidepoint(mx, my):
                    self.in_main_menu = False
                    self.music_manager.start(self.daynight.is_night())
                # Load Game button — auto-load quick save if available
                load_y = start_y + 60
                if pygame.Rect(bx, load_y, btn_w, btn_h).collidepoint(mx, my):
                    data = save_load.load_game(QUICK_SAVE_SLOT)
                    if data:
                        self.in_main_menu = False
                        self._apply_save_data(data)
                        self._notify("Loaded quick save!")
                        self.music_manager.start(self.daynight.is_night())
                    else:
                        self._notify("No saved game found!")
                # Options button
                opts_y = load_y + 60
                if pygame.Rect(bx, opts_y, btn_w, btn_h).collidepoint(mx, my):
                    self.in_options_menu = True
                    self.options_source = 'main'
                # Quit button
                quit_y = opts_y + 60
                if pygame.Rect(bx, quit_y, btn_w, btn_h).collidepoint(mx, my):
                    self.running = False

    def _draw_main_menu(self) -> None:
        self.screen.fill((15, 15, 30))
        title = self.font_xl.render("Sandbox Survival RPG", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

        diff_name = DIFFICULTY_NAMES[self.difficulty]
        diff_colors = [GREEN, YELLOW, ORANGE, RED]
        sub = self.font.render(f"Difficulty: {diff_name}", True,
                               diff_colors[self.difficulty])
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 240))

        mx, my = pygame.mouse.get_pos()
        btn_w, btn_h = 220, 44
        bx = SCREEN_WIDTH // 2 - btn_w // 2

        buttons = [
            (300, "Start Game", GREEN),
            (360, "Load Game", CYAN),
            (420, "Options", GRAY),
            (480, "Quit", RED),
        ]
        for by, label, color in buttons:
            r = pygame.Rect(bx, by, btn_w, btn_h)
            hov = r.collidepoint(mx, my)
            bc = (50, 50, 75) if hov else (30, 30, 50)
            pygame.draw.rect(self.screen, bc, r, border_radius=6)
            bd = color if hov else (100, 100, 130)
            pygame.draw.rect(self.screen, bd, r, 2, border_radius=6)
            lt = self.font_lg.render(label, True, WHITE if hov else GRAY)
            self.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                                  r.centery - lt.get_height() // 2))

        hint = self.font_sm.render("Press ENTER to start  |  Q to quit", True, GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                SCREEN_HEIGHT - 60))
        self._present()

    # ======================================================================
    # OPTIONS MENU
    # ======================================================================
    def _handle_options_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._close_options()
                    continue
                if (event.key == pygame.K_RETURN
                        and (event.mod & pygame.KMOD_ALT)):
                    self._toggle_fullscreen()
                    continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = self._scale_mouse_pos(event.pos)
                pw, ph = 450, 560
                px = SCREEN_WIDTH // 2 - pw // 2
                py = SCREEN_HEIGHT // 2 - ph // 2

                # Difficulty buttons
                diff_y = py + 60
                btn_w, btn_h = 100, 32
                total_w = len(DIFFICULTY_NAMES) * (btn_w + 8) - 8
                diff_bx = px + pw // 2 - total_w // 2
                for i, name in enumerate(DIFFICULTY_NAMES):
                    r = pygame.Rect(
                        diff_bx + i * (btn_w + 8), diff_y, btn_w, btn_h)
                    if r.collidepoint(mx, my):
                        self.difficulty = i
                        self.wave_system.difficulty = i
                        self.settings['difficulty'] = i
                        save_settings(self.settings)

                # Display mode buttons
                mode_y = diff_y + 70
                modes = [
                    (DISPLAY_WINDOWED, "Windowed"),
                    (DISPLAY_FULLSCREEN, "Fullscreen"),
                    (DISPLAY_BORDERLESS, "Borderless"),
                ]
                mode_bw = 130
                mode_total = len(modes) * (mode_bw + 8) - 8
                mode_bx = px + pw // 2 - mode_total // 2
                for i, (mode_id, label) in enumerate(modes):
                    r = pygame.Rect(
                        mode_bx + i * (mode_bw + 8), mode_y, mode_bw, btn_h)
                    if r.collidepoint(mx, my):
                        self.display_mode = mode_id
                        if mode_id == DISPLAY_BORDERLESS:
                            info = pygame.display.Info()
                            self.window_w = info.current_w
                            self.window_h = info.current_h
                        elif mode_id == DISPLAY_FULLSCREEN:
                            info = pygame.display.Info()
                            self.window_w = info.current_w
                            self.window_h = info.current_h
                        self._apply_display_settings()

                # Resolution presets
                res_y = mode_y + 70
                res_bw = 120
                for i, (rw, rh) in enumerate(RESOLUTION_PRESETS):
                    row = i // 3
                    col = i % 3
                    rx = px + 30 + col * (res_bw + 12)
                    ry = res_y + row * 38
                    r = pygame.Rect(rx, ry, res_bw, 30)
                    if r.collidepoint(mx, my):
                        self.window_w = rw
                        self.window_h = rh
                        if self.display_mode != DISPLAY_BORDERLESS:
                            self._apply_display_settings()

                # Music toggle
                music_y = res_y + 90
                btn_h = 32
                for i, (enabled, label) in enumerate(
                        [(True, "On"), (False, "Off")]):
                    r = pygame.Rect(
                        px + 100 + i * 78, music_y, 70, btn_h)
                    if r.collidepoint(mx, my):
                        self.music_manager.set_enabled(enabled)
                        self.settings['music_enabled'] = enabled
                        save_settings(self.settings)

                # Volume slider
                vol_y = music_y + 40
                slider_x = px + 100
                slider_w = 300
                slider_r = pygame.Rect(
                    slider_x, vol_y + 8, slider_w, 16)
                if slider_r.collidepoint(mx, my):
                    vol = (mx - slider_x) / slider_w
                    vol = max(0.0, min(1.0, vol))
                    self.music_manager.set_volume(vol)
                    self.settings['music_volume'] = round(vol, 2)
                    save_settings(self.settings)

                # Back button
                back_y = py + ph - 60
                back_r = pygame.Rect(px + pw // 2 - 80, back_y, 160, 40)
                if back_r.collidepoint(mx, my):
                    self._close_options()

    def _close_options(self) -> None:
        self.in_options_menu = False
        if self.options_source == 'pause':
            self.paused = True

    def _open_options_from_pause(self) -> None:
        self.paused = False
        self.in_options_menu = True
        self.options_source = 'pause'

    def _draw_options_menu(self) -> None:
        self.screen.fill((15, 15, 30))
        mx, my = pygame.mouse.get_pos()
        pw, ph = 450, 560
        px = SCREEN_WIDTH // 2 - pw // 2
        py = SCREEN_HEIGHT // 2 - ph // 2
        bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        bg.fill((20, 20, 35, 240))
        self.screen.blit(bg, (px, py))
        pygame.draw.rect(self.screen, (140, 140, 170),
                         (px, py, pw, ph), 2, border_radius=10)

        title = self.font_lg.render("Options", True, WHITE)
        self.screen.blit(title,
                         (px + pw // 2 - title.get_width() // 2, py + 16))

        # --- Difficulty ---
        diff_label = self.font.render("Difficulty:", True, GRAY)
        self.screen.blit(diff_label, (px + 20, py + 46))
        diff_y = py + 60
        diff_colors = [GREEN, YELLOW, ORANGE, RED]
        btn_w, btn_h = 100, 32
        total_w = len(DIFFICULTY_NAMES) * (btn_w + 8) - 8
        diff_bx = px + pw // 2 - total_w // 2
        for i, name in enumerate(DIFFICULTY_NAMES):
            r = pygame.Rect(diff_bx + i * (btn_w + 8), diff_y, btn_w, btn_h)
            sel = i == self.difficulty
            hov = r.collidepoint(mx, my)
            bc = (80, 80, 120) if sel else (50, 50, 75) if hov else (30, 30, 50)
            pygame.draw.rect(self.screen, bc, r, border_radius=5)
            bd = diff_colors[i] if sel else (100, 100, 130)
            pygame.draw.rect(self.screen, bd, r, 2, border_radius=5)
            lt = self.font_sm.render(name, True,
                                     diff_colors[i] if sel else WHITE)
            self.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                                  r.centery - lt.get_height() // 2))

        # --- Display Mode ---
        mode_label = self.font.render("Display Mode:", True, GRAY)
        self.screen.blit(mode_label, (px + 20, py + 106))
        mode_y = diff_y + 70
        modes = [
            (DISPLAY_WINDOWED, "Windowed"),
            (DISPLAY_FULLSCREEN, "Fullscreen"),
            (DISPLAY_BORDERLESS, "Borderless"),
        ]
        mode_bw = 130
        mode_total = len(modes) * (mode_bw + 8) - 8
        mode_bx = px + pw // 2 - mode_total // 2
        for i, (mode_id, label) in enumerate(modes):
            r = pygame.Rect(mode_bx + i * (mode_bw + 8), mode_y,
                            mode_bw, btn_h)
            sel = mode_id == self.display_mode
            hov = r.collidepoint(mx, my)
            bc = (80, 80, 120) if sel else (50, 50, 75) if hov else (30, 30, 50)
            pygame.draw.rect(self.screen, bc, r, border_radius=5)
            bd = CYAN if sel else (100, 100, 130)
            pygame.draw.rect(self.screen, bd, r, 2, border_radius=5)
            lt = self.font_sm.render(label, True, WHITE if sel else GRAY)
            self.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                                  r.centery - lt.get_height() // 2))

        # --- Resolution ---
        res_label = self.font.render("Resolution:", True, GRAY)
        self.screen.blit(res_label, (px + 20, py + 176))
        res_y = mode_y + 70
        res_bw = 120
        for i, (rw, rh) in enumerate(RESOLUTION_PRESETS):
            row = i // 3
            col = i % 3
            rx = px + 30 + col * (res_bw + 12)
            ry = res_y + row * 38
            r = pygame.Rect(rx, ry, res_bw, 30)
            sel = (rw == self.window_w and rh == self.window_h)
            hov = r.collidepoint(mx, my)
            bc = (80, 80, 120) if sel else (50, 50, 75) if hov else (30, 30, 50)
            pygame.draw.rect(self.screen, bc, r, border_radius=4)
            bd = GREEN if sel else (100, 100, 130)
            pygame.draw.rect(self.screen, bd, r, 2, border_radius=4)
            lt = self.font_sm.render(f"{rw}x{rh}", True,
                                     WHITE if sel else GRAY)
            self.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                                  r.centery - lt.get_height() // 2))

        # --- Music ---
        music_y = res_y + 90
        music_label = self.font.render("Music:", True, GRAY)
        self.screen.blit(music_label, (px + 20, music_y + 4))
        for i, (enabled, label) in enumerate([(True, "On"), (False, "Off")]):
            r = pygame.Rect(px + 100 + i * 78, music_y, 70, btn_h)
            sel = self.music_manager.enabled == enabled
            hov = r.collidepoint(mx, my)
            bc = (80, 80, 120) if sel else (50, 50, 75) if hov else (30, 30, 50)
            pygame.draw.rect(self.screen, bc, r, border_radius=5)
            bd = GREEN if sel and enabled else RED if sel else (100, 100, 130)
            pygame.draw.rect(self.screen, bd, r, 2, border_radius=5)
            lt = self.font_sm.render(label, True, WHITE if sel else GRAY)
            self.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                                  r.centery - lt.get_height() // 2))

        # Volume slider
        vol_y = music_y + 40
        vol_label = self.font.render("Volume:", True, GRAY)
        self.screen.blit(vol_label, (px + 20, vol_y + 4))
        slider_x = px + 100
        slider_w = 300
        pygame.draw.rect(self.screen, (30, 30, 50),
                         (slider_x, vol_y + 8, slider_w, 16),
                         border_radius=4)
        fill_w = int(slider_w * self.music_manager.volume)
        if fill_w > 0:
            pygame.draw.rect(self.screen, (70, 160, 255),
                             (slider_x, vol_y + 8, fill_w, 16),
                             border_radius=4)
        pygame.draw.rect(self.screen, (100, 100, 130),
                         (slider_x, vol_y + 8, slider_w, 16), 2,
                         border_radius=4)
        pct = self.font_sm.render(
            f"{int(self.music_manager.volume * 100)}%", True, WHITE)
        self.screen.blit(pct, (slider_x + slider_w + 10, vol_y + 8))

        # Current info
        cur_info = self.font_sm.render(
            f"Current: {self.window_w}x{self.window_h}  "
            f"{DISPLAY_MODE_NAMES.get(self.display_mode, '?')}",
            True, (160, 160, 190))
        self.screen.blit(cur_info,
                         (px + pw // 2 - cur_info.get_width() // 2,
                          py + ph - 100))

        # --- Back Button ---
        back_y = py + ph - 60
        back_r = pygame.Rect(px + pw // 2 - 80, back_y, 160, 40)
        hov = back_r.collidepoint(mx, my)
        bc = (60, 70, 100) if hov else (40, 45, 65)
        pygame.draw.rect(self.screen, bc, back_r, border_radius=6)
        pygame.draw.rect(self.screen, (130, 130, 160), back_r, 2,
                         border_radius=6)
        bt = self.font.render("Back  [Esc]", True, WHITE)
        self.screen.blit(bt, (back_r.centerx - bt.get_width() // 2,
                              back_r.centery - bt.get_height() // 2))

        hint = self.font_sm.render("Alt+Enter toggles fullscreen", True,
                                   DARK_GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                                SCREEN_HEIGHT - 40))
        self._present()

    # ======================================================================
    # EVENTS
    # ======================================================================
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
                    elif self.spell_targeting:
                        self.spell_targeting = False
                        self.spell_item = None
                    elif (self.show_inventory or self.show_crafting
                            or self.show_character or self.show_chest):
                        self.show_inventory = False
                        self.show_crafting = False
                        self.show_character = False
                        self.show_chest = False
                        self.active_chest = None
                    else:
                        self.paused = True
                    continue
                if event.key == pygame.K_i:
                    self.show_inventory = not self.show_inventory
                    self.show_crafting = False
                    self.show_character = False
                    self.show_chest = False
                    self.active_chest = None
                    continue
                if event.key == pygame.K_c:
                    self.show_crafting = not self.show_crafting
                    self.show_inventory = False
                    self.show_character = False
                    self.show_chest = False
                    self.active_chest = None
                    continue
                if event.key == pygame.K_p:
                    self.show_character = not self.show_character
                    self.show_inventory = False
                    self.show_crafting = False
                    self.show_chest = False
                    self.active_chest = None
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

            # Mouse-wheel for hotbar
            if event.type == pygame.MOUSEWHEEL:
                if not self.placement_mode and not self.spell_targeting:
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
                    self.chest_ui.handle_event(
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

        # Movement (AGI speed bonus)
        base_speed = 180.0 * (1.0 + ps.agility * 0.05)
        if keys[pygame.K_w]:
            pv.vy -= base_speed * dt * 10
        if keys[pygame.K_s]:
            pv.vy += base_speed * dt * 10
        if keys[pygame.K_a]:
            pv.vx -= base_speed * dt * 10
        if keys[pygame.K_d]:
            pv.vx += base_speed * dt * 10
        if pv.vx < -5:
            pr.flip_x = True
        elif pv.vx > 5:
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
        self.music_manager.update(self.daynight.is_night())
        self.camera.follow(pt.x, pt.y)
        self.camera.update(dt)
        self.particles.update(dt)

        # Wave system
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

        # Melee attack
        if keys[pygame.K_SPACE] and self.attack_cd == 0:
            self._attack()
            cd = max(MIN_ATTACK_COOLDOWN,
                     BASE_ATTACK_COOLDOWN - ps.agility * AGILITY_COOLDOWN_REDUCTION)
            self.attack_cd = cd
            self.attack_anim = 0.18

        # Ranged attack (R key)
        if keys[pygame.K_r] and self.ranged_cd == 0:
            self._ranged_attack()

        # Interact
        if keys[pygame.K_e] and self.interact_cd == 0:
            self._interact()
            self.interact_cd = 0.25

        # Damage numbers decay
        self.dmg_numbers = [
            (x, y - 40 * dt, t, c, l - dt)
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
                self.em.destroy_entity(eid)

        # Mob contact damage
        self._check_contact_damage(pt)

        # Enemy projectile damage to player
        self._check_enemy_projectile_damage(pt)

        # Campfire healing
        self._campfire_heal(dt, pt)

        # Night damage
        self._night_damage(dt, pt)

        # Mob respawning
        self.mob_spawn_timer += dt
        _, _, spawn_mult, _ = DIFFICULTY_MULTIPLIERS.get(
            self.difficulty, (1.0, 1.0, 1.0, 1.0))
        respawn_interval = MOB_RESPAWN_INTERVAL / spawn_mult
        if self.mob_spawn_timer > respawn_interval:
            self.mob_spawn_timer = 0.0
            if len(self.em.get_entities_with(AI)) < 60:
                self._spawn_mob()

        # HUD refresh
        self.survival_timer += dt
        if self.survival_timer > 0.5:
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
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        eq = self.em.get_component(self.player_id, Equipment)
        # Prefer equipped weapon over hotbar
        weapon = eq.weapon if eq and eq.weapon else inv.get_equipped()
        base = 5
        if weapon and weapon in ITEM_DATA and ITEM_DATA[weapon][2] > 0:
            base = ITEM_DATA[weapon][2]
        return calc_melee_damage(base, ps, eq)

    def _get_attack_range(self) -> float:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        eq = self.em.get_component(self.player_id, Equipment)
        weapon = eq.weapon if eq and eq.weapon else inv.get_equipped()
        if weapon == 'spear':
            return 65.0
        if weapon and weapon in ITEM_DATA and ITEM_DATA[weapon][2] > 0:
            return 55.0
        return 38.0

    def _attack(self) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        px, py = pt.x + 10, pt.y + 14
        rng = self._get_attack_range()
        dmg = self._get_attack_damage()
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        is_crit = random.random() < ps.luck * 0.02
        if is_crit:
            dmg = int(dmg * 1.5)
        for eid in self.em.get_entities_with(Transform, Health, AI):
            t: Transform = self.em.get_component(eid, Transform)
            dist = math.hypot(t.x - px, t.y - py)
            if dist < rng:
                h: Health = self.em.get_component(eid, Health)
                h.damage(dmg)
                v_mob = self.em.get_component(eid, Velocity)
                if v_mob and dist > 1:
                    dx, dy = t.x - px, t.y - py
                    v_mob.vx += (dx / dist) * 200
                    v_mob.vy += (dy / dist) * 200
                if is_crit:
                    self.dmg_numbers.append(
                        (t.x, t.y - 16, f'{dmg} CRIT!', ORANGE, 1.0))
                    self.particles.emit(
                        t.x + 12, t.y + 10, 10, ORANGE, 60, 0.4)
                else:
                    self.dmg_numbers.append(
                        (t.x, t.y - 16, str(dmg), YELLOW, 0.8))
                    self.particles.emit(
                        t.x + 12, t.y + 10, 6, YELLOW, 50, 0.3)

    def _ranged_attack(self) -> None:
        eq: Equipment = self.em.get_component(self.player_id, Equipment)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        if not eq or not eq.ranged:
            self._notify("No ranged weapon equipped!")
            return
        rdata = RANGED_DATA.get(eq.ranged)
        if not rdata:
            return
        # Find ammo
        ammo_id = eq.ammo
        if not ammo_id or not inv.has(ammo_id):
            # Try to find any compatible ammo
            ammo_id = None
            for a in rdata['ammo']:
                if inv.has(a):
                    ammo_id = a
                    break
        if not ammo_id:
            self._notify("No ammo!")
            return

        inv.remove_item(ammo_id, 1)
        bonus = AMMO_BONUS_DAMAGE.get(ammo_id, 0)
        dmg = calc_ranged_damage(rdata['damage'], bonus, ps)

        pt: Transform = self.em.get_component(self.player_id, Transform)
        pr: Renderable = self.em.get_component(self.player_id, Renderable)
        # Direction: face direction
        dx = -1.0 if pr.flip_x else 1.0
        dy = 0.0

        # Try to aim at nearest mob in range
        best_eid, best_dist = None, rdata['range']
        for eid in self.em.get_entities_with(Transform, Health, AI):
            mt = self.em.get_component(eid, Transform)
            d = math.hypot(mt.x - pt.x, mt.y - pt.y)
            if d < best_dist:
                best_dist = d
                best_eid = eid
        if best_eid is not None:
            mt = self.em.get_component(best_eid, Transform)
            ddx, ddy = mt.x - pt.x, mt.y - pt.y
            mag = math.hypot(ddx, ddy)
            if mag > 0:
                dx, dy = ddx / mag, ddy / mag

        # Create projectile
        pid = self.em.create_entity()
        self.em.add_component(pid, Transform(pt.x + 10, pt.y + 14))
        self.em.add_component(pid, Velocity(
            dx * rdata['speed'], dy * rdata['speed'], 1.0))
        proj_tex = ('proj_arrow' if eq.ranged == 'bow'
                    else 'proj_bolt' if eq.ranged == 'crossbow'
                    else 'proj_rock')
        self.em.add_component(pid, Renderable(
            self.textures.get(proj_tex), layer=4))
        self.em.add_component(pid, Collider(8, 8, False))
        self.em.add_component(pid, Projectile(
            dmg, self.player_id, rdata['speed'], rdata['range']))

        cd = max(0.2, rdata['cooldown'] - ps.agility * 0.02)
        self.ranged_cd = cd

    def _on_proj_hit(self, target_eid: int, damage: int,
                     proj_t: Transform) -> None:
        self.dmg_numbers.append(
            (proj_t.x, proj_t.y - 16, str(damage), CYAN, 0.8))
        self.particles.emit(proj_t.x, proj_t.y, 5, CYAN, 40, 0.3)

    def _on_trap_hit(self, target_eid: int, damage: int,
                     trap_t: Transform) -> None:
        self.dmg_numbers.append(
            (trap_t.x, trap_t.y - 16, str(damage), RED, 0.8))
        self.particles.emit(trap_t.x, trap_t.y, 5, RED, 40, 0.3)

    def _on_turret_fire(self, target_eid: int, damage: int,
                        turret_t: Transform, target_t: Transform) -> None:
        self.dmg_numbers.append(
            (target_t.x, target_t.y - 16, str(damage), ORANGE, 0.8))
        self.particles.emit(turret_t.x + 16, turret_t.y + 8, 4, ORANGE, 60, 0.2)
        self.particles.emit(target_t.x, target_t.y, 3, RED, 40, 0.2)

    def _on_enemy_ranged_fire(self, mob_eid: int, mob_t: Transform,
                               player_t: Transform) -> None:
        """Called by AISystem when a ranged enemy fires a projectile."""
        mob_ai = self.em.get_component(mob_eid, AI)
        if not mob_ai:
            return
        dx = player_t.x - mob_t.x
        dy = player_t.y - mob_t.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        dx /= dist
        dy /= dist
        pid = self.em.create_entity()
        self.em.add_component(pid, Transform(mob_t.x + 12, mob_t.y + 12))
        self.em.add_component(pid, Velocity(
            dx * mob_ai.ranged_speed, dy * mob_ai.ranged_speed, 1.0))
        self.em.add_component(pid, Renderable(
            self.textures.get('proj_enemy'), layer=4))
        self.em.add_component(pid, Collider(8, 8, False))
        # Enemy projectiles target the player — we use negative owner
        proj = Projectile(mob_ai.ranged_damage, mob_eid,
                          mob_ai.ranged_speed, mob_ai.ranged_range)
        self.em.add_component(pid, proj)
        self.particles.emit(mob_t.x + 12, mob_t.y + 10, 3, RED, 40, 0.2)

    def _get_placement_tiles(self, tx: int, ty: int) -> List[Tuple[int, int]]:
        """Return list of (tile_x, tile_y) occupied by the current placement."""
        if self.placement_item == 'bed':
            # Bed is 2 tiles: rotation 0=right, 1=down, 2=left, 3=up
            offsets = [(0, 0)]
            r = self.placement_rotation % 4
            if r == 0:
                offsets.append((1, 0))
            elif r == 1:
                offsets.append((0, 1))
            elif r == 2:
                offsets.append((-1, 0))
            else:
                offsets.append((0, -1))
            return [(tx + dx, ty + dy) for dx, dy in offsets]
        return [(tx, ty)]

    # Wall-type item ids that support upgrade/replace
    _WALL_ITEM_IDS = {'wall', 'stone_wall_b'}

    def _find_building_at_tiles(self, tiles: list) -> int:
        """Return entity id of a Building occupying any of the given tiles, or 0."""
        for bid in self.em.get_entities_with(Transform, Building, Health):
            bt: Transform = self.em.get_component(bid, Transform)
            bc = self.em.get_component(bid, Collider) if self.em.has_component(bid, Collider) else None
            bw = bc.width if bc else TILE_SIZE
            bh = bc.height if bc else TILE_SIZE
            btx = int(bt.x // TILE_SIZE)
            bty = int(bt.y // TILE_SIZE)
            btx2 = int((bt.x + bw - 1) // TILE_SIZE)
            bty2 = int((bt.y + bh - 1) // TILE_SIZE)
            for ttx, tty in tiles:
                if btx <= ttx <= btx2 and bty <= tty <= bty2:
                    return bid
        return 0

    def _placement_confirm(self) -> None:
        """Place the item at the mouse cursor position in the world."""
        if not self.placement_mode or not self.placement_item:
            return
        mx, my = pygame.mouse.get_pos()
        world_x = mx + self.camera.x
        world_y = my + self.camera.y
        # Snap to tile grid
        tx = int(world_x // TILE_SIZE)
        ty = int(world_y // TILE_SIZE)
        # Check all tiles for multi-tile items
        tiles = self._get_placement_tiles(tx, ty)
        for ttx, tty in tiles:
            if self.world.is_solid(ttx, tty):
                self._notify("Can't place here!")
                return

        # Check for existing building at target tiles
        existing_bid = self._find_building_at_tiles(tiles)
        if existing_bid:
            # Allow wall upgrades: replacing one wall type with another
            existing_placeable = self.em.get_component(existing_bid, Placeable)
            if (self.placement_item in self._WALL_ITEM_IDS
                    and existing_placeable
                    and existing_placeable.item_type in self._WALL_ITEM_IDS):
                if existing_placeable.item_type == self.placement_item:
                    self._notify("Same wall type already here!")
                    return
                # Return old wall to inventory and destroy old entity
                inv_check: Inventory = self.em.get_component(
                    self.player_id, Inventory)
                if not inv_check.has(self.placement_item):
                    self.placement_mode = False
                    self.placement_item = None
                    self._notify("No more items to place!")
                    return
                inv_check.add_item(existing_placeable.item_type, 1)
                old_name = ITEM_DATA[existing_placeable.item_type][0]
                td = self.em.get_component(existing_bid, Transform)
                self.particles.emit(td.x + 10, td.y + 10, 6, GRAY, 40, 0.3)
                self.em.destroy_entity(existing_bid)
                inv_check.remove_item(self.placement_item, 1)
                # Use top-left tile as anchor
                min_tx = min(t[0] for t in tiles)
                min_ty = min(t[1] for t in tiles)
                place_x = min_tx * TILE_SIZE
                place_y = min_ty * TILE_SIZE
                self._place_item(self.placement_item, place_x, place_y,
                                 rotation=self.placement_rotation)
                new_name = ITEM_DATA[self.placement_item][0]
                self._notify(f"Replaced {old_name} with {new_name}")
                if not inv_check.has(self.placement_item):
                    self.placement_mode = False
                    self.placement_item = None
                return
            else:
                self._notify("Can't place here!")
                return

        # Use top-left tile as anchor
        min_tx = min(t[0] for t in tiles)
        min_ty = min(t[1] for t in tiles)
        place_x = min_tx * TILE_SIZE
        place_y = min_ty * TILE_SIZE
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        if not inv.has(self.placement_item):
            self.placement_mode = False
            self.placement_item = None
            self._notify("No more items to place!")
            return
        inv.remove_item(self.placement_item, 1)
        self._place_item(self.placement_item, place_x, place_y,
                         rotation=self.placement_rotation)
        self._notify(f"Placed {ITEM_DATA[self.placement_item][0]}")
        # If player has more of this item, stay in placement mode
        if not inv.has(self.placement_item):
            self.placement_mode = False
            self.placement_item = None

    def _spell_cast_at_mouse(self) -> None:
        """Cast spell at mouse target position."""
        if not self.spell_targeting or not self.spell_item:
            return
        sdata = SPELL_DATA.get(self.spell_item)
        if not sdata:
            self.spell_targeting = False
            self.spell_item = None
            return
        mx, my = pygame.mouse.get_pos()
        target_x = mx + self.camera.x
        target_y = my + self.camera.y
        pt: Transform = self.em.get_component(self.player_id, Transform)
        dx = target_x - pt.x
        dy = target_y - pt.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        dx /= dist
        dy /= dist
        # Create fireball projectile
        pid = self.em.create_entity()
        self.em.add_component(pid, Transform(pt.x + 10, pt.y + 14))
        self.em.add_component(pid, Velocity(
            dx * sdata['speed'], dy * sdata['speed'], 1.0))
        self.em.add_component(pid, Renderable(
            self.textures.get('proj_fireball'), layer=4))
        self.em.add_component(pid, Collider(12, 12, False))
        self.em.add_component(pid, Projectile(
            sdata['damage'], self.player_id, sdata['speed'], sdata['range']))
        self.particles.emit(pt.x + 10, pt.y + 14, 8, sdata['color'], 60, 0.3)
        self._notify(f"Cast {sdata['name']}!")
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        inv.remove_item(self.spell_item, 1)
        self.spell_targeting = False
        self.spell_item = None

    def _full_restart(self) -> None:
        """Reset game completely for death restart."""
        # Remove all entities
        for eid in list(self.em._entities):
            self.em.destroy_entity(eid)
        # New seed for fresh map
        self.seed = random.randint(0, 2**31 - 1)
        self.world_gen = WorldGenerator(seed=self.seed)
        self.world = self.world_gen.generate(WORLD_WIDTH, WORLD_HEIGHT)
        self.player_id = self._create_player()
        self._populate_world()
        self.daynight = DayNightCycle(day_length=DAY_LENGTH_BASE)
        self.wave_system = WaveSystem(difficulty=self.difficulty)
        self.dead = False
        self.paused = False
        self.sleeping = False
        self.placement_mode = False
        self.placement_item = None
        self.spell_targeting = False
        self.spell_item = None
        self.show_inventory = False
        self.show_crafting = False
        self.show_character = False
        self.show_chest = False
        self.active_chest = None
        inv_comp = self.em.get_component(self.player_id, Inventory)
        self.inventory_ui = InventoryGrid(
            pygame.Rect(SCREEN_WIDTH // 2 - 195,
                        SCREEN_HEIGHT // 2 - 180, 390, 340),
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
        pt: Transform = self.em.get_component(self.player_id, Transform)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        px, py = pt.x + 10, pt.y + 14

        # Check for nearby chest interaction
        for eid in self.em.get_entities_with(Transform, Storage):
            ct = self.em.get_component(eid, Transform)
            if math.hypot(ct.x - px, ct.y - py) < 50:
                self.show_chest = True
                self.active_chest = eid
                self.show_inventory = False
                self.show_crafting = False
                self.show_character = False
                return

        nearest: Optional[int] = None
        nearest_dist = 50.0
        for eid in self.em.get_entities_with(Transform, Renderable):
            if eid == self.player_id or self.em.has_component(eid, AI):
                continue
            if self.em.has_component(eid, Placeable):
                continue
            t: Transform = self.em.get_component(eid, Transform)
            r: Renderable = self.em.get_component(eid, Renderable)
            if r.surface in (self.textures.get('tree'),
                             self.textures.get('rock')):
                d = math.hypot(t.x - px, t.y - py)
                if d < nearest_dist:
                    nearest = eid
                    nearest_dist = d
        if nearest is not None:
            r = self.em.get_component(nearest, Renderable)
            eq: Equipment = self.em.get_component(self.player_id, Equipment)
            eq_item = eq.weapon if eq and eq.weapon else inv.get_equipped()
            bonus = (ITEM_DATA[eq_item][3]
                     if eq_item and eq_item in ITEM_DATA else 0)
            ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
            luck_bonus = 1 if random.random() < ps.luck * 0.10 else 0
            if r.surface == self.textures.get('tree'):
                inv.add_item('wood', random.randint(2, 4) + bonus + luck_bonus)
                inv.add_item('stick', 1)
                th = self.em.get_component(nearest, Transform)
                self.particles.emit(th.x + 20, th.y + 30, 8,
                                    (80, 50, 30), 40, 0.3)
            else:
                inv.add_item('stone', random.randint(2, 3) + bonus + luck_bonus)
                th = self.em.get_component(nearest, Transform)
                self.particles.emit(th.x + 14, th.y + 10, 8,
                                    GRAY, 40, 0.3)
            self.em.destroy_entity(nearest)

    def _use_equipped_item(self) -> None:
        # First check: interact with nearby bed to sleep
        pt_check: Transform = self.em.get_component(self.player_id, Transform)
        for eid in self.em.get_entities_with(Transform, Placeable):
            pl: Placeable = self.em.get_component(eid, Placeable)
            if pl.item_type == 'bed':
                bt: Transform = self.em.get_component(eid, Transform)
                if math.hypot(bt.x - pt_check.x, bt.y - pt_check.y) < 50:
                    self._try_sleep()
                    return

        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        eq_id = inv.get_equipped()
        if not eq_id or eq_id not in ITEM_DATA:
            return
        data = ITEM_DATA[eq_id]
        heal = data[4]
        placeable = data[5]
        pt: Transform = self.em.get_component(self.player_id, Transform)

        # Spell items: enter targeting mode
        cat = ITEM_CATEGORIES.get(eq_id, '')
        if cat == 'spell' and eq_id in SPELL_DATA:
            self.spell_targeting = True
            self.spell_item = eq_id
            self._notify("Click target to cast spell. ESC/Right-click to cancel.")
            return

        if heal > 0:
            ph: Health = self.em.get_component(self.player_id, Health)
            if ph.current >= ph.maximum:
                self._notify("Already at full health!")
                return
            ph.heal(heal)
            inv.remove_item(eq_id, 1)
            self.health_bar.set_value(ph.current)
            self.dmg_numbers.append(
                (pt.x, pt.y - 20, f'+{heal}', GREEN, 0.8))
            self.particles.emit(pt.x + 10, pt.y + 14, 8, GREEN, 40, 0.4)
            self._notify(f"Used {data[0]} (+{heal} HP)")
        elif placeable:
            # Enter placement preview mode
            self.placement_mode = True
            self.placement_item = eq_id
            self.placement_rotation = 0
            hint = f"Click to place {data[0]}."
            if eq_id == 'bed':
                hint += " R to rotate."
            hint += " ESC/Right-click to cancel."
            self._notify(hint)

    def _place_item(self, item_id: str,
                    px: Optional[float] = None,
                    py: Optional[float] = None,
                    rotation: int = 0) -> None:
        if px is None or py is None:
            pt: Transform = self.em.get_component(self.player_id, Transform)
            pr: Renderable = self.em.get_component(self.player_id, Renderable)
            offset_x = -30 if pr.flip_x else 30
            px, py = pt.x + offset_x, pt.y + 20
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(px, py))
        self.em.add_component(eid, Placeable(item_id, rotation=rotation))

        if item_id == 'campfire':
            self.em.add_component(eid, Renderable(
                self.textures.get('campfire_True'), layer=2))
            self.em.add_component(eid, LightSource(180, (255, 160, 80), 1.0))
            self.em.add_component(eid, Health(60))
        elif item_id == 'torch':
            self.em.add_component(eid, Renderable(
                self.textures.get('torch_placed'), layer=2))
            self.em.add_component(eid, LightSource(120, (255, 180, 60), 0.8))
            self.em.add_component(eid, Health(30))
        elif item_id == 'trap':
            self.em.add_component(eid, Renderable(
                self.textures.get('trap_placed'), layer=1))
            self.em.add_component(eid, Health(40))
        elif item_id == 'bed':
            tex = self.textures.get('bed_placed')
            if rotation % 4 != 0:
                tex = pygame.transform.rotate(tex, -90 * (rotation % 4))
            self.em.add_component(eid, Renderable(tex, layer=1))
            self.em.add_component(eid, Health(80))
        elif item_id == 'wall':
            self.em.add_component(eid, Renderable(
                self.textures.get('wall_placed'), layer=2))
            self.em.add_component(eid, Collider(32, 32, True))
            self.em.add_component(eid, Health(WALL_HP))
            self.em.add_component(eid, Building('wall'))
        elif item_id == 'stone_wall_b':
            self.em.add_component(eid, Renderable(
                self.textures.get('stone_wall_placed'), layer=2))
            self.em.add_component(eid, Collider(32, 32, True))
            self.em.add_component(eid, Health(int(WALL_HP * 1.5)))
            self.em.add_component(eid, Building('stone_wall'))
        elif item_id == 'turret':
            self.em.add_component(eid, Renderable(
                self.textures.get('turret_placed'), layer=2))
            self.em.add_component(eid, Collider(32, 32, True))
            self.em.add_component(eid, Health(TURRET_HP))
            self.em.add_component(eid, Turret(TURRET_DAMAGE, TURRET_RANGE, TURRET_COOLDOWN))
            self.em.add_component(eid, Building('turret'))
        elif item_id == 'chest':
            self.em.add_component(eid, Renderable(
                self.textures.get('chest_placed'), layer=1))
            self.em.add_component(eid, Health(60))
            self.em.add_component(eid, Storage(CHEST_CAPACITY))
            self.em.add_component(eid, Building('chest'))
        elif item_id == 'door':
            self.em.add_component(eid, Renderable(
                self.textures.get('door_placed'), layer=2))
            self.em.add_component(eid, Health(50))
            self.em.add_component(eid, Collider(24, 32, True))
            self.em.add_component(eid, Building('door'))

    def _craft(self, recipe: Dict[str, Any]) -> None:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        for item, cost in recipe['cost'].items():
            if not inv.has(item, cost):
                self._notify("Not enough materials!")
                return
        for item, cost in recipe['cost'].items():
            inv.remove_item(item, cost)
        count = recipe.get('count', 1)
        inv.add_item(recipe['gives'], count)
        self._notify(f"Crafted {recipe['name']}!")
        pt: Transform = self.em.get_component(self.player_id, Transform)
        self.particles.emit(pt.x + 10, pt.y + 14, 10, CYAN, 50, 0.4)

    def _on_mob_killed(self, eid: int) -> None:
        td: Transform = self.em.get_component(eid, Transform)
        mob_ai: AI = self.em.get_component(eid, AI)
        pinv: Inventory = self.em.get_component(self.player_id, Inventory)

        data = MOB_DATA.get(mob_ai.mob_type, {})
        drops = data.get('drops', [])
        for item_id, lo, hi in drops:
            amt = random.randint(lo, hi)
            if amt > 0:
                pinv.add_item(item_id, amt)
        if drops:
            self.dmg_numbers.append((td.x, td.y - 10, '+Loot', CYAN, 1.2))

        # Particles based on mob type
        mob_colors = {
            'slime': (50, 200, 70), 'skeleton': (200, 200, 210),
            'wolf': (100, 100, 100), 'goblin': (80, 140, 60),
            'ghost': (180, 180, 220), 'spider': (60, 40, 30),
            'orc': (80, 100, 50), 'dark_knight': (40, 40, 50),
            'zombie': (100, 140, 80), 'wraith': (140, 80, 180),
            'troll': (80, 120, 60), 'skeleton_archer': (200, 200, 210),
            'goblin_shaman': (100, 60, 160),
            'boss_golem': (180, 80, 60), 'boss_lich': (120, 60, 180),
        }
        color = mob_colors.get(mob_ai.mob_type, GRAY)
        self.particles.emit(td.x + 12, td.y + 10, 15, color, 80, 0.5)

        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        ps.kills += 1
        self._check_level_up(mob_ai.xp_value)
        self.em.destroy_entity(eid)

    def _check_level_up(self, xp: int) -> None:
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        if ps.add_xp(xp):
            ph: Health = self.em.get_component(self.player_id, Health)
            # VIT gives extra HP on level up
            ph.maximum += 10 + ps.vitality * 5
            ph.current = ph.maximum
            self.health_bar.max_value = ph.maximum
            self.health_bar.set_value(ph.current)
            pt: Transform = self.em.get_component(self.player_id, Transform)
            self.dmg_numbers.append(
                (pt.x, pt.y - 30, f'LEVEL {ps.level}!', CYAN, 2.0))
            self.particles.emit(pt.x + 10, pt.y + 14, 25, YELLOW, 100, 0.8)
            self.particles.emit(pt.x + 10, pt.y + 14, 25, CYAN, 80, 0.6)
            self._notify(f"Level Up! Level {ps.level}  (+3 stat points)")

    def _check_contact_damage(self, pt: Transform) -> None:
        if self.player_hit_cd > 0:
            return
        eq: Equipment = self.em.get_component(self.player_id, Equipment)
        dmg_red = calc_damage_reduction(eq)
        for eid in self.em.get_entities_with(Transform, AI):
            t: Transform = self.em.get_component(eid, Transform)
            ai_c: AI = self.em.get_component(eid, AI)
            dist = math.hypot(t.x - pt.x, t.y - pt.y)
            if dist < 28:
                ph: Health = self.em.get_component(self.player_id, Health)
                raw = ai_c.contact_damage
                dmg = max(1, raw - dmg_red)
                ph.damage(dmg)
                self.health_bar.set_value(ph.current)
                self.player_hit_cd = 0.5
                self.damage_flash = 0.15
                self.camera.shake(4.0, 0.2)
                self.particles.emit(pt.x + 10, pt.y + 14, 8, RED, 60, 0.4)
                self.dmg_numbers.append(
                    (pt.x, pt.y - 16, str(dmg), RED, 0.8))
                if not ph.is_alive():
                    self.dead = True
                    self.dmg_numbers.append(
                        (pt.x, pt.y - 30, 'YOU DIED', RED, 2.5))
                break

    def _check_enemy_projectile_damage(self, pt: Transform) -> None:
        """Check if enemy projectiles hit the player."""
        eq: Equipment = self.em.get_component(self.player_id, Equipment)
        dmg_red = calc_damage_reduction(eq)
        to_remove = []
        for pid in self.em.get_entities_with(Transform, Projectile):
            proj = self.em.get_component(pid, Projectile)
            if proj.owner == self.player_id:
                continue
            proj_t = self.em.get_component(pid, Transform)
            dist = math.hypot(proj_t.x - pt.x - 10, proj_t.y - pt.y - 14)
            if dist < 20:
                ph: Health = self.em.get_component(self.player_id, Health)
                dmg = max(1, proj.damage - dmg_red)
                ph.damage(dmg)
                self.health_bar.set_value(ph.current)
                self.damage_flash = 0.15
                self.camera.shake(3.0, 0.15)
                self.particles.emit(pt.x + 10, pt.y + 14, 5, RED, 40, 0.3)
                self.dmg_numbers.append(
                    (pt.x, pt.y - 16, str(dmg), RED, 0.8))
                to_remove.append(pid)
                if not ph.is_alive():
                    self.dead = True
                    self.dmg_numbers.append(
                        (pt.x, pt.y - 30, 'YOU DIED', RED, 2.5))
                break
        for pid in to_remove:
            self.em.destroy_entity(pid)

    def _campfire_heal(self, dt: float, pt: Transform) -> None:
        self.campfire_heal_timer += dt
        if self.campfire_heal_timer < 1.0:
            return
        self.campfire_heal_timer = 0.0
        ph: Health = self.em.get_component(self.player_id, Health)
        if ph.current >= ph.maximum:
            return
        for eid in self.em.get_entities_with(Transform, Placeable):
            pl: Placeable = self.em.get_component(eid, Placeable)
            if pl.item_type == 'campfire':
                t2: Transform = self.em.get_component(eid, Transform)
                if math.hypot(t2.x - pt.x, t2.y - pt.y) < 120:
                    amt = 3
                    ph.heal(amt)
                    self.health_bar.set_value(ph.current)
                    self.dmg_numbers.append(
                        (pt.x, pt.y - 20, f'+{amt}', GREEN, 0.6))
                    break

    def _night_damage(self, dt: float, pt: Transform) -> None:
        darkness = self.daynight.get_darkness()
        if darkness <= 0.5:
            self.night_dmg_timer = 0.0
            return
        self.night_dmg_timer += dt
        if self.night_dmg_timer < 3.0:
            return
        self.night_dmg_timer = 0.0
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        near_light = (inv.get_equipped() == 'torch' and inv.has('torch'))
        if not near_light:
            for eid in self.em.get_entities_with(Transform, LightSource):
                t3: Transform = self.em.get_component(eid, Transform)
                if math.hypot(t3.x - pt.x, t3.y - pt.y) < 200:
                    near_light = True
                    break
        if near_light:
            return
        ph: Health = self.em.get_component(self.player_id, Health)
        ph.damage(3)
        self.health_bar.set_value(ph.current)
        self.damage_flash = 0.1
        self.dmg_numbers.append((pt.x, pt.y - 20, '3', RED, 0.8))
        if not ph.is_alive():
            self.dead = True

    def _respawn(self) -> None:
        self.dead = False
        pt: Transform = self.em.get_component(self.player_id, Transform)
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
        self._notify("Respawned! You lost some items.")

    # ======================================================================
    # BED / SLEEP
    # ======================================================================
    def _try_sleep(self) -> None:
        if not self.daynight.is_night():
            self._notify("You can only sleep at night!")
            return
        pt: Transform = self.em.get_component(self.player_id, Transform)
        for eid in self.em.get_entities_with(Transform, Placeable):
            pl: Placeable = self.em.get_component(eid, Placeable)
            if pl.item_type == 'bed':
                bt: Transform = self.em.get_component(eid, Transform)
                if math.hypot(bt.x - pt.x, bt.y - pt.y) < 50:
                    self.sleeping = True
                    self.sleep_timer = SLEEP_DURATION
                    self.daynight.set_speed(NIGHT_SLEEP_SPEED_MULT)
                    self._notify("Sleeping...")
                    return
        self._notify("No bed nearby!")

    # ======================================================================
    # SAVE / LOAD
    # ======================================================================
    def _build_save_data(self) -> Dict[str, Any]:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        ph: Health = self.em.get_component(self.player_id, Health)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        eq: Equipment = self.em.get_component(self.player_id, Equipment)
        inv_data = {str(s): [iid, c] for s, (iid, c) in inv.slots.items()}

        # Save placed structures
        structures: list[dict[str, Any]] = []
        for eid in self.em.get_entities_with(Transform, Placeable):
            if self.em.has_component(eid, AI):
                continue
            pl = self.em.get_component(eid, Placeable)
            t = self.em.get_component(eid, Transform)
            h = self.em.get_component(eid, Health)
            struct_data: Dict[str, Any] = {
                'type': pl.item_type,
                'x': t.x, 'y': t.y,
                'hp': h.current if h else 0,
                'max_hp': h.maximum if h else 0,
                'rotation': pl.rotation,
            }
            stor = self.em.get_component(eid, Storage)
            if stor:
                struct_data['storage'] = {str(s): [iid, c]
                                          for s, (iid, c) in stor.slots.items()}
            structures.append(struct_data)

        return {
            'seed': self.seed,
            'px': pt.x, 'py': pt.y,
            'hp': ph.current, 'max_hp': ph.maximum,
            'level': ps.level, 'xp': ps.xp, 'kills': ps.kills,
            'xp_to_next': ps.xp_to_next,
            'stat_points': ps.stat_points,
            'strength': ps.strength, 'agility': ps.agility,
            'vitality': ps.vitality, 'luck': ps.luck,
            'inventory': inv_data, 'equipped': inv.equipped_slot,
            'eq_weapon': eq.weapon, 'eq_armor': eq.armor,
            'eq_shield': eq.shield, 'eq_ranged': eq.ranged,
            'eq_ammo': eq.ammo,
            'day_time': self.daynight.time,
            'day_number': self.daynight.day_number,
            'was_day': self.daynight._was_day,
            'night_count': self.wave_system.night_count,
            'difficulty': self.difficulty,
            'structures': structures,
        }

    def _apply_save_data(self, data: Dict[str, Any]) -> None:
        # Restore seed and regenerate world from it
        saved_seed = data.get('seed', self.seed)
        if saved_seed != self.seed:
            self.seed = saved_seed
            self.world_gen = WorldGenerator(seed=self.seed)
        self.world = self.world_gen.generate(WORLD_WIDTH, WORLD_HEIGHT)

        # Destroy all entities except player, then repopulate world
        for eid in list(self.em._entities):
            if eid != self.player_id:
                self.em.destroy_entity(eid)
        self._populate_world()

        pt: Transform = self.em.get_component(self.player_id, Transform)
        ph: Health = self.em.get_component(self.player_id, Health)
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        eq: Equipment = self.em.get_component(self.player_id, Equipment)
        pt.x = data['px']; pt.y = data['py']
        ph.current = data['hp']; ph.maximum = data['max_hp']
        ps.level = data['level']; ps.xp = data['xp']
        ps.kills = data['kills']; ps.xp_to_next = data['xp_to_next']
        ps.stat_points = data.get('stat_points', 0)
        ps.strength = data.get('strength', 1)
        ps.agility = data.get('agility', 1)
        ps.vitality = data.get('vitality', 1)
        ps.luck = data.get('luck', data.get('dexterity', 1))
        inv.slots.clear()
        for s_str, (iid, c) in data['inventory'].items():
            inv.slots[int(s_str)] = (iid, c)
        inv.equipped_slot = data.get('equipped', 0)
        eq.weapon = data.get('eq_weapon')
        eq.armor = data.get('eq_armor')
        eq.shield = data.get('eq_shield')
        eq.ranged = data.get('eq_ranged')
        eq.ammo = data.get('eq_ammo')
        self.daynight.time = data.get('day_time', 0.3)
        self.daynight.day_number = data.get('day_number', 1)
        # Restore _was_day to prevent spurious day/night transitions on load
        is_day_now = 0.30 <= self.daynight.time < 0.70
        self.daynight._was_day = data.get('was_day', is_day_now)
        self.daynight._day_flash_timer = 0.0
        self.daynight._night_flash_timer = 0.0
        self.wave_system.night_count = data.get('night_count', 0)
        self.wave_system.was_night = not is_day_now
        self.difficulty = data.get('difficulty', DIFFICULTY_EASY)
        self.wave_system.difficulty = self.difficulty
        self.health_bar.max_value = ph.maximum
        self.health_bar.set_value(ph.current)
        self.xp_bar.max_value = ps.xp_to_next
        self.xp_bar.set_value(ps.xp)
        self.dead = False
        # Reset sleeping state
        self.sleeping = False
        self.sleep_timer = 0.0
        self.daynight.reset_speed()

        # Restore saved structures
        for struct in data.get('structures', []):
            self._restore_structure(struct)

    def _restore_structure(self, struct: Dict[str, Any]) -> None:
        """Recreate a placed structure from save data."""
        item_id = struct['type']
        rotation = struct.get('rotation', 0)
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(struct['x'], struct['y']))
        self.em.add_component(eid, Placeable(item_id, rotation=rotation))

        if item_id == 'campfire':
            self.em.add_component(eid, Renderable(
                self.textures.get('campfire_True'), layer=2))
            self.em.add_component(eid, LightSource(180, (255, 160, 80), 1.0))
            h = Health(struct.get('max_hp', 60))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
        elif item_id == 'torch':
            self.em.add_component(eid, Renderable(
                self.textures.get('torch_placed'), layer=2))
            self.em.add_component(eid, LightSource(120, (255, 180, 60), 0.8))
            h = Health(struct.get('max_hp', 30))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
        elif item_id == 'trap':
            self.em.add_component(eid, Renderable(
                self.textures.get('trap_placed'), layer=1))
            h = Health(struct.get('max_hp', 40))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
        elif item_id == 'bed':
            tex = self.textures.get('bed_placed')
            if rotation % 4 != 0:
                tex = pygame.transform.rotate(tex, -90 * (rotation % 4))
            self.em.add_component(eid, Renderable(tex, layer=1))
            h = Health(struct.get('max_hp', 80))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
        elif item_id == 'wall':
            self.em.add_component(eid, Renderable(
                self.textures.get('wall_placed'), layer=2))
            self.em.add_component(eid, Collider(32, 32, True))
            h = Health(struct.get('max_hp', WALL_HP))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
            self.em.add_component(eid, Building('wall'))
        elif item_id == 'stone_wall_b':
            self.em.add_component(eid, Renderable(
                self.textures.get('stone_wall_placed'), layer=2))
            self.em.add_component(eid, Collider(32, 32, True))
            h = Health(struct.get('max_hp', int(WALL_HP * 1.5)))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
            self.em.add_component(eid, Building('stone_wall'))
        elif item_id == 'turret':
            self.em.add_component(eid, Renderable(
                self.textures.get('turret_placed'), layer=2))
            self.em.add_component(eid, Collider(32, 32, True))
            h = Health(struct.get('max_hp', TURRET_HP))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
            self.em.add_component(eid, Turret(TURRET_DAMAGE, TURRET_RANGE, TURRET_COOLDOWN))
            self.em.add_component(eid, Building('turret'))
        elif item_id == 'chest':
            self.em.add_component(eid, Renderable(
                self.textures.get('chest_placed'), layer=1))
            h = Health(struct.get('max_hp', 60))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
            stor = Storage(CHEST_CAPACITY)
            for s_str, (iid, c) in struct.get('storage', {}).items():
                stor.slots[int(s_str)] = (iid, c)
            self.em.add_component(eid, stor)
            self.em.add_component(eid, Building('chest'))
        elif item_id == 'door':
            self.em.add_component(eid, Renderable(
                self.textures.get('door_placed'), layer=2))
            h = Health(struct.get('max_hp', 50))
            h.current = struct.get('hp', h.maximum)
            self.em.add_component(eid, h)
            self.em.add_component(eid, Collider(24, 32, True))
            self.em.add_component(eid, Building('door'))

    def _quick_save(self) -> None:
        if save_load.save_game(QUICK_SAVE_SLOT, self._build_save_data()):
            self._notify("Quick Saved!")
        else:
            self._notify("Save failed!")

    def _quick_load(self) -> None:
        data = save_load.load_game(QUICK_SAVE_SLOT)
        if not data:
            self._notify("No quick save found!")
            return
        self._apply_save_data(data)
        self._notify("Quick Loaded!")

    def _save_to_slot(self, slot: int) -> None:
        if save_load.save_game(slot, self._build_save_data()):
            self._notify(f"Saved to slot {slot}!")
        else:
            self._notify("Save failed!")

    def _load_from_slot(self, slot: int) -> None:
        data = save_load.load_game(slot)
        if not data:
            self._notify(f"Slot {slot} is empty!")
            return
        self._apply_save_data(data)
        self.paused = False
        self._notify(f"Loaded slot {slot}!")

    def _delete_slot(self, slot: int) -> None:
        save_load.delete_save(slot)
        self._notify(f"Deleted slot {slot}.")

    def _resume(self) -> None:
        self.paused = False

    def _quit(self) -> None:
        self.running = False

    # ======================================================================
    # RENDER
    # ======================================================================
    def _render(self) -> None:
        self.screen.fill(BLACK)
        self.tooltip.clear()
        self._draw_world()
        self.renderer.update(self.em, self.camera)
        self._draw_boss_glow()
        self._draw_mob_health_bars()
        self._draw_placeable_health_bars()
        if self.attack_anim > 0:
            self._draw_attack_arc()
        self.particles.draw(self.screen, self.camera.x, self.camera.y)
        self._draw_damage_numbers()
        self._draw_lighting()
        if self.damage_flash > 0:
            fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(80 * (self.damage_flash / 0.15))
            fs.fill((255, 0, 0, min(255, alpha)))
            self.screen.blit(fs, (0, 0))
        # Placement preview
        if self.placement_mode and self.placement_item:
            self._draw_placement_preview()
        # Spell targeting cursor
        if self.spell_targeting:
            self._draw_spell_targeting()
        self._draw_hud()
        self._draw_hotbar()

        # Minimap — gather mob positions
        mob_pos = []
        for eid in self.em.get_entities_with(Transform, AI):
            mt = self.em.get_component(eid, Transform)
            mob_pos.append((mt.x, mt.y))
        build_pos = []
        for eid in self.em.get_entities_with(Transform, Building):
            bt = self.em.get_component(eid, Transform)
            build_pos.append((bt.x, bt.y))
        pt: Transform = self.em.get_component(self.player_id, Transform)
        self.minimap.draw(self.screen, self.world, pt.x, pt.y,
                          mob_pos, build_pos)

        # Overlays
        if self.show_chest and self.active_chest is not None:
            stor = self.em.get_component(self.active_chest, Storage)
            if stor:
                self.chest_ui.draw(
                    self.screen, stor,
                    self.em.get_component(self.player_id, Inventory),
                    self.tooltip)
        if self.show_inventory:
            self.inventory_ui.draw(self.screen, self.tooltip)
        if self.show_crafting:
            self.crafting_ui.draw(
                self.screen,
                self.em.get_component(self.player_id, Inventory),
                self.tooltip)
        if self.show_character:
            self.character_menu.draw(
                self.screen,
                self.em.get_component(self.player_id, PlayerStats),
                self.em.get_component(self.player_id, Equipment),
                self.em.get_component(self.player_id, Health),
                self.em.get_component(self.player_id, Inventory),
                self.tooltip)
        if self.paused:
            self.pause_menu.draw(self.screen, save_load.list_slots())
        if self.notification_timer > 0:
            alpha = min(1.0, self.notification_timer / 0.5)
            ns = self.font.render(self.notification, True,
                                  (220, 220, 240))
            nbg = pygame.Surface((ns.get_width() + 20, ns.get_height() + 8),
                                 pygame.SRCALPHA)
            nbg.fill((10, 10, 20, int(180 * alpha)))
            nx = SCREEN_WIDTH // 2 - ns.get_width() // 2
            ny = SCREEN_HEIGHT // 2 + 120
            self.screen.blit(nbg, (nx - 10, ny - 4))
            self.screen.blit(ns, (nx, ny))
        self.tooltip.draw(self.screen)
        if self.dead:
            self._draw_death_screen()

        # Sleeping overlay
        if self.sleeping:
            ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 30, 140))
            self.screen.blit(ov, (0, 0))
            zt = self.font_lg.render("Sleeping... Zzz", True, (180, 180, 255))
            self.screen.blit(zt, (SCREEN_WIDTH // 2 - zt.get_width() // 2,
                                  SCREEN_HEIGHT // 2 - 20))

        # Day number flash
        if self.daynight._day_flash_timer > 0:
            alpha = min(1.0, self.daynight._day_flash_timer / 1.0)
            dt_text = self.font_xl.render(
                f"Day {self.daynight.day_number}", True,
                (255, 255, 200))
            dt_text.set_alpha(int(255 * alpha))
            self.screen.blit(dt_text,
                             (SCREEN_WIDTH // 2 - dt_text.get_width() // 2,
                              SCREEN_HEIGHT // 4))

        # Night warning flash
        if self.daynight._night_flash_timer > 0:
            alpha = min(1.0, self.daynight._night_flash_timer / 0.8)
            nt = self.font_lg.render("Night falls — Defend!", True,
                                     (255, 120, 80))
            nt.set_alpha(int(255 * alpha))
            self.screen.blit(nt,
                             (SCREEN_WIDTH // 2 - nt.get_width() // 2,
                              SCREEN_HEIGHT // 4 + 60))

        self._present()

    # -- world tiles -------------------------------------------------------
    def _draw_world(self) -> None:
        sx_start = max(0, int(self.camera.x // TILE_SIZE) - 1)
        sx_end = min(self.world.width,
                     int((self.camera.x + SCREEN_WIDTH) // TILE_SIZE) + 2)
        sy_start = max(0, int(self.camera.y // TILE_SIZE) - 1)
        sy_end = min(self.world.height,
                     int((self.camera.y + SCREEN_HEIGHT) // TILE_SIZE) + 2)
        tile_surfs = {
            TILE_WATER: self.textures.get('water_0'),
            TILE_SAND: self.textures.get('sand'),
            TILE_GRASS: self.textures.get('grass'),
            TILE_DIRT: self.textures.get('dirt'),
            TILE_STONE_FLOOR: self.textures.get('stone'),
            TILE_STONE_WALL: self.textures.get('stone'),
            TILE_FOREST: self.textures.get('forest'),
        }
        default_surf = self.textures.get('grass')
        for x in range(sx_start, sx_end):
            for y in range(sy_start, sy_end):
                tile = self.world.get_tile(x, y)
                scx = int(x * TILE_SIZE - self.camera.x)
                scy = int(y * TILE_SIZE - self.camera.y)
                self.screen.blit(tile_surfs.get(tile, default_surf),
                                 (scx, scy))
                if tile == TILE_STONE_WALL:
                    pygame.draw.rect(self.screen, (50, 50, 60),
                                     (scx, scy, TILE_SIZE, TILE_SIZE))
                    pygame.draw.rect(self.screen, (30, 30, 40),
                                     (scx, scy, TILE_SIZE, TILE_SIZE), 2)

    # -- lighting ----------------------------------------------------------
    def _draw_lighting(self) -> None:
        darkness = self.daynight.get_darkness()
        lights = self.em.get_entities_with(Transform, LightSource)
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        has_torch = inv.get_equipped() == 'torch' and inv.has('torch')
        if darkness < 0.05 and not lights and not has_torch:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                                 pygame.SRCALPHA)
        base_alpha = int(darkness * 210)
        overlay.fill((5, 5, 20, base_alpha))

        def punch_light(sx: int, sy: int, radius: int,
                        color: Tuple[int, int, int]) -> None:
            for r in range(radius, 15, -18):
                ts = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                a = int(30 * (r / radius))
                pygame.draw.circle(
                    ts, (color[0], color[1], color[2], max(1, a)), (r, r), r)
                overlay.blit(ts, (sx - r, sy - r),
                             special_flags=pygame.BLEND_RGBA_SUB)

        for eid in lights:
            t: Transform = self.em.get_component(eid, Transform)
            ls: LightSource = self.em.get_component(eid, LightSource)
            lx = int(t.x - self.camera.x + 12)
            ly = int(t.y - self.camera.y + 12)
            punch_light(lx, ly, ls.radius, ls.color)

        if has_torch:
            pt: Transform = self.em.get_component(self.player_id, Transform)
            lx = int(pt.x - self.camera.x + 10)
            ly = int(pt.y - self.camera.y + 14)
            punch_light(lx, ly, 110, (255, 180, 60))

        self.screen.blit(overlay, (0, 0))

    # -- health bars -------------------------------------------------------
    def _draw_mob_health_bars(self) -> None:
        for eid in self.em.get_entities_with(Transform, Health, AI):
            t: Transform = self.em.get_component(eid, Transform)
            h: Health = self.em.get_component(eid, Health)
            if h.current >= h.maximum:
                continue
            sx = int(t.x - self.camera.x)
            sy = int(t.y - self.camera.y - 8)
            pygame.draw.rect(self.screen, (40, 10, 10), (sx, sy, 28, 4))
            fill = int(28 * h.current / h.maximum)
            pygame.draw.rect(self.screen, (220, 40, 40), (sx, sy, fill, 4))

    def _draw_placeable_health_bars(self) -> None:
        for eid in self.em.get_entities_with(Transform, Health, Placeable):
            if self.em.has_component(eid, AI):
                continue
            t: Transform = self.em.get_component(eid, Transform)
            h: Health = self.em.get_component(eid, Health)
            if h.current >= h.maximum:
                continue
            sx = int(t.x - self.camera.x)
            sy = int(t.y - self.camera.y - 6)
            pygame.draw.rect(self.screen, (40, 30, 10), (sx, sy, 28, 3))
            fill = int(28 * h.current / h.maximum)
            pygame.draw.rect(self.screen, (200, 160, 40), (sx, sy, fill, 3))

    # -- attack arc --------------------------------------------------------
    def _draw_attack_arc(self) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pr: Renderable = self.em.get_component(self.player_id, Renderable)
        cx = int(pt.x - self.camera.x + 10)
        cy = int(pt.y - self.camera.y + 14)
        d = -1 if pr.flip_x else 1
        ax = cx + d * 20
        alpha = int(200 * (self.attack_anim / 0.18))
        arc = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.arc(arc, (255, 255, 200, alpha),
                        pygame.Rect(0, 0, 40, 40),
                        -0.8 if d > 0 else 2.3,
                        0.8 if d > 0 else 3.9, 3)
        self.screen.blit(arc, (ax - 20, cy - 20))

    # -- floating damage numbers -------------------------------------------
    def _draw_damage_numbers(self) -> None:
        for x, y, txt, color, ttl in self.dmg_numbers:
            sx = int(x - self.camera.x)
            sy = int(y - self.camera.y)
            bold = (txt.startswith('+') or txt.startswith('LEVEL')
                    or txt == 'YOU DIED')
            f = self.font_lg if bold else self.font
            surf = f.render(txt, True, color)
            self.screen.blit(surf, (sx - surf.get_width() // 2, sy))

    # -- hotbar ------------------------------------------------------------
    def _draw_hotbar(self) -> None:
        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        slots = 6; ss = 48; gap = 6
        tw = slots * ss + (slots - 1) * gap
        bx = SCREEN_WIDTH // 2 - tw // 2
        by = SCREEN_HEIGHT - ss - 14
        mx, my = pygame.mouse.get_pos()

        # Background strip
        bg = pygame.Surface((tw + 16, ss + 12), pygame.SRCALPHA)
        bg.fill((15, 15, 25, 180))
        self.screen.blit(bg, (bx - 8, by - 6))
        pygame.draw.rect(self.screen, (100, 100, 130),
                         (bx - 8, by - 6, tw + 16, ss + 12), 1, border_radius=6)

        for i in range(slots):
            x = bx + i * (ss + gap)
            rect = pygame.Rect(x, by, ss, ss)
            sel = i == inv.equipped_slot
            bg_c = (80, 80, 115) if sel else (30, 30, 48)
            pygame.draw.rect(self.screen, bg_c, rect, border_radius=5)
            bd = (200, 200, 240) if sel else (90, 90, 110)
            pygame.draw.rect(self.screen, bd, rect, 2, border_radius=5)
            ns = self.font_sm.render(str(i + 1), True, (170, 170, 190))
            self.screen.blit(ns, (x + 3, by + 2))
            if i in inv.slots:
                item_id, count = inv.slots[i]
                icon = self.textures.cache.get(f'item_{item_id}')
                if icon:
                    self.screen.blit(
                        pygame.transform.scale(icon, (32, 32)),
                        (x + 8, by + 8))
                if count > 1:
                    cs = self.font_sm.render(str(count), True, WHITE)
                    self.screen.blit(
                        cs, (x + ss - cs.get_width() - 3,
                             by + ss - cs.get_height() - 2))
                if rect.collidepoint(mx, my) and item_id in ITEM_DATA:
                    d = ITEM_DATA[item_id]
                    self.tooltip.show([d[0], d[1]], (mx, my))
        eq_item = inv.get_equipped()
        if eq_item and eq_item in ITEM_DATA:
            nt = self.font.render(ITEM_DATA[eq_item][0], True, (220, 220, 240))
            self.screen.blit(nt, (SCREEN_WIDTH // 2 - nt.get_width() // 2,
                                  by - 22))

    # -- HUD ---------------------------------------------------------------
    def _draw_hud(self) -> None:
        # Background for HUD area
        hud_bg = pygame.Surface((230, 70), pygame.SRCALPHA)
        hud_bg.fill((10, 10, 20, 150))
        self.screen.blit(hud_bg, (12, 10))

        self.health_bar.draw(self.screen)
        ph: Health = self.em.get_component(self.player_id, Health)
        ht = self.font_sm.render(f"HP {ph.current}/{ph.maximum}", True, WHITE)
        self.screen.blit(ht, (24, 17))

        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        self.xp_bar.draw(self.screen)
        xt = self.font_sm.render(
            f"Lv.{ps.level}  XP {ps.xp}/{ps.xp_to_next}", True,
            (180, 210, 255))
        self.screen.blit(xt, (24, 39))

        inv: Inventory = self.em.get_component(self.player_id, Inventory)
        res = (f"Wood:{inv.count('wood')}  Stone:{inv.count('stone')}"
               f"  Iron:{inv.count('iron')}  Kills:{ps.kills}")
        self.screen.blit(self.font_sm.render(res, True, (200, 200, 210)),
                         (20, 58))

        # Time of day + Day number
        period = self.daynight.get_period_name()
        period_colors = {'Day': (255, 255, 200), 'Dawn': (255, 200, 140),
                         'Dusk': (200, 140, 180), 'Night': (140, 140, 220)}
        pc = period_colors.get(period, WHITE)
        # Background for top-right HUD area
        tr_bg = pygame.Surface((200, 55), pygame.SRCALPHA)
        tr_bg.fill((10, 10, 20, 150))
        self.screen.blit(tr_bg, (SCREEN_WIDTH - 210, 8))
        day_str = f"Day {self.daynight.day_number}  {period}"
        self.screen.blit(self.font.render(day_str, True, pc),
                         (SCREEN_WIDTH - 200, 14))
        t_str = (f"{int(self.daynight.time * 24):02d}"
                 f":{int((self.daynight.time * 1440) % 60):02d}")
        diff_name = DIFFICULTY_NAMES[self.difficulty] if 0 <= self.difficulty < len(DIFFICULTY_NAMES) else "?"
        self.screen.blit(self.font_sm.render(
            f"{t_str}   [{diff_name}]", True, GRAY),
            (SCREEN_WIDTH - 200, 36))

        # Wave info — simplified, no numbers
        if self.wave_system.wave_active:
            wave_txt = "DEFEND!"
            wt = self.font.render(wave_txt, True, RED)
            wbg = pygame.Surface((wt.get_width() + 16, wt.get_height() + 6),
                                 pygame.SRCALPHA)
            wbg.fill((40, 10, 10, 180))
            wx = SCREEN_WIDTH // 2 - wt.get_width() // 2
            self.screen.blit(wbg, (wx - 8, 8))
            self.screen.blit(wt, (wx, 11))

        # Warnings
        if 0.2 < self.daynight.get_darkness() < 0.55:
            wt = self.font.render("Night approaches... find light!",
                                  True, (255, 200, 80))
            self.screen.blit(
                wt, (SCREEN_WIDTH // 2 - wt.get_width() // 2, 70))
        pt: Transform = self.em.get_component(self.player_id, Transform)
        tx, ty = pt.x / TILE_SIZE, pt.y / TILE_SIZE
        if (tx < 4 or tx > WORLD_WIDTH - 4
                or ty < 4 or ty > WORLD_HEIGHT - 4):
            et = self.font.render("~ Edge of the World ~", True,
                                  (170, 170, 200))
            self.screen.blit(
                et, (SCREEN_WIDTH // 2 - et.get_width() // 2, 94))

        # Controls hint — bottom-left vertical list
        if not (self.show_inventory or self.show_crafting
                or self.show_character or self.show_chest
                or self.paused):
            controls = [
                "WASD  Move",
                "Space Attack",
                "R     Ranged",
                "E     Harvest",
                "F     Use Item",
                "I     Inventory",
                "C     Crafting",
                "P     Stats",
                "Esc   Menu",
            ]
            line_h = 15
            ctrl_x = 14
            ctrl_y = SCREEN_HEIGHT - len(controls) * line_h - 80
            bg_w = 120
            bg_h = len(controls) * line_h + 6
            ctrl_bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
            ctrl_bg.fill((10, 10, 20, 120))
            self.screen.blit(ctrl_bg, (ctrl_x - 4, ctrl_y - 3))
            for i, line in enumerate(controls):
                cs = self.font_sm.render(line, True, (130, 130, 150))
                self.screen.blit(cs, (ctrl_x, ctrl_y + i * line_h))

        # Contextual bed prompt
        if not self.sleeping and self.daynight.is_night():
            pt_bed: Transform = self.em.get_component(self.player_id, Transform)
            for eid in self.em.get_entities_with(Transform, Placeable):
                pl = self.em.get_component(eid, Placeable)
                if pl.item_type == 'bed':
                    bt = self.em.get_component(eid, Transform)
                    if math.hypot(bt.x - pt_bed.x, bt.y - pt_bed.y) < 50:
                        bed_txt = self.font.render(
                            "Press F to Sleep", True, (180, 180, 255))
                        bed_bg = pygame.Surface(
                            (bed_txt.get_width() + 16,
                             bed_txt.get_height() + 8), pygame.SRCALPHA)
                        bed_bg.fill((10, 10, 30, 160))
                        bx = SCREEN_WIDTH // 2 - bed_txt.get_width() // 2
                        by = SCREEN_HEIGHT // 2 + 60
                        self.screen.blit(bed_bg, (bx - 8, by - 4))
                        self.screen.blit(bed_txt, (bx, by))
                        break

    # -- death screen ------------------------------------------------------
    def _draw_death_screen(self) -> None:
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        dt_text = self.font_xl.render("YOU DIED", True, RED)
        self.screen.blit(
            dt_text, (SCREEN_WIDTH // 2 - dt_text.get_width() // 2,
                      SCREEN_HEIGHT // 2 - 100))
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        st = self.font.render(
            f"Day {self.daynight.day_number}  |  Level {ps.level}  |  "
            f"{ps.kills} Kills", True, WHITE)
        self.screen.blit(
            st, (SCREEN_WIDTH // 2 - st.get_width() // 2,
                 SCREEN_HEIGHT // 2 - 30))

        # Buttons
        mx, my = pygame.mouse.get_pos()
        btn_w = 200
        bx = SCREEN_WIDTH // 2 - btn_w // 2
        buttons = [
            (SCREEN_HEIGHT // 2 + 10, "Quick Load [F9]"),
            (SCREEN_HEIGHT // 2 + 56, "Load Save..."),
            (SCREEN_HEIGHT // 2 + 102, "Restart"),
        ]
        for by, label in buttons:
            r = pygame.Rect(bx, by, btn_w, 36)
            hov = r.collidepoint(mx, my)
            bc = (60, 60, 90) if hov else (40, 40, 60)
            pygame.draw.rect(self.screen, bc, r, border_radius=5)
            pygame.draw.rect(self.screen, GRAY, r, 1, border_radius=5)
            lt = self.font.render(label, True, WHITE)
            self.screen.blit(lt, (r.centerx - lt.get_width() // 2,
                                  r.centery - lt.get_height() // 2))

        quit_hint = self.font_sm.render("Press Q to quit", True, GRAY)
        self.screen.blit(quit_hint,
                         (SCREEN_WIDTH // 2 - quit_hint.get_width() // 2,
                          SCREEN_HEIGHT // 2 + 160))

    # -- placement preview -------------------------------------------------
    def _draw_placement_preview(self) -> None:
        mx, my = pygame.mouse.get_pos()
        world_x = mx + self.camera.x
        world_y = my + self.camera.y
        tx = int(world_x // TILE_SIZE)
        ty = int(world_y // TILE_SIZE)

        # Get all tiles this placement occupies
        tiles = self._get_placement_tiles(tx, ty)
        terrain_ok = all(
            not self.world.is_solid(ttx, tty) for ttx, tty in tiles)

        # Check for existing building — allow wall upgrades
        existing_bid = self._find_building_at_tiles(tiles) if terrain_ok else 0
        is_upgrade = False
        if existing_bid and terrain_ok:
            ep = self.em.get_component(existing_bid, Placeable)
            if (self.placement_item in self._WALL_ITEM_IDS
                    and ep and ep.item_type in self._WALL_ITEM_IDS
                    and ep.item_type != self.placement_item):
                is_upgrade = True

        all_valid = terrain_ok and (not existing_bid or is_upgrade)

        # Draw ghost for each occupied tile
        for ttx, tty in tiles:
            tsx = int(ttx * TILE_SIZE - self.camera.x)
            tsy = int(tty * TILE_SIZE - self.camera.y)
            if is_upgrade:
                color = (255, 200, 60, 120)  # yellow-ish for upgrade
                bd_color = (255, 200, 60)
            elif all_valid:
                color = PLACEMENT_PREVIEW_COLOR
                bd_color = (60, 220, 80)
            else:
                color = PLACEMENT_INVALID_COLOR
                bd_color = (220, 60, 60)
            ghost = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            ghost.fill(color)
            self.screen.blit(ghost, (tsx, tsy))
            pygame.draw.rect(self.screen, bd_color,
                             (tsx, tsy, TILE_SIZE, TILE_SIZE), 2)

        # Draw the actual item texture over the ghost tiles
        if self.placement_item:
            tex_key = None
            for k in [f'{self.placement_item}_placed',
                      f'campfire_True',
                      f'item_{self.placement_item}']:
                if k in self.textures.cache:
                    tex_key = k
                    break
            if tex_key:
                icon = self.textures.get(tex_key)
                # Compute bounding box of all tiles
                min_tx = min(t[0] for t in tiles)
                min_ty = min(t[1] for t in tiles)
                max_tx = max(t[0] for t in tiles)
                max_ty = max(t[1] for t in tiles)
                pw = (max_tx - min_tx + 1) * TILE_SIZE
                ph = (max_ty - min_ty + 1) * TILE_SIZE
                bsx = int(min_tx * TILE_SIZE - self.camera.x)
                bsy = int(min_ty * TILE_SIZE - self.camera.y)
                # Rotate texture for multi-tile items
                rot = self.placement_rotation % 4
                if rot != 0 and self.placement_item == 'bed':
                    icon = pygame.transform.rotate(icon, -90 * rot)
                scaled = pygame.transform.scale(icon, (pw, ph))
                scaled.set_alpha(140)
                self.screen.blit(scaled, (bsx, bsy))

        # Hint text
        hint_parts = ["Click to place"]
        if self.placement_item == 'bed':
            hint_parts.append("R to rotate")
        hint_parts.append("ESC/Right-click to cancel")
        hint = self.font_sm.render(
            " | ".join(hint_parts), True, WHITE)
        self.screen.blit(hint,
                         (SCREEN_WIDTH // 2 - hint.get_width() // 2, 40))

    # -- spell targeting ---------------------------------------------------
    def _draw_spell_targeting(self) -> None:
        mx, my = pygame.mouse.get_pos()
        # Targeting crosshair
        pygame.draw.circle(self.screen, (255, 120, 30), (mx, my), 16, 2)
        pygame.draw.line(self.screen, (255, 120, 30), (mx - 20, my), (mx + 20, my), 1)
        pygame.draw.line(self.screen, (255, 120, 30), (mx, my - 20), (mx, my + 20), 1)
        hint = self.font_sm.render(
            "Click to cast | ESC/Right-click to cancel", True, (255, 180, 80))
        self.screen.blit(hint,
                         (SCREEN_WIDTH // 2 - hint.get_width() // 2, 40))

    # -- boss glow ---------------------------------------------------------
    def _draw_boss_glow(self) -> None:
        for eid in self.em.get_entities_with(Transform, AI):
            ai_c = self.em.get_component(eid, AI)
            if not ai_c.is_boss or not ai_c.glow_color:
                continue
            t = self.em.get_component(eid, Transform)
            sx = int(t.x - self.camera.x + 14)
            sy = int(t.y - self.camera.y + 14)
            # Pulsing glow
            pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.005)
            radius = int(40 * pulse)
            glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            r, g, b = ai_c.glow_color
            pygame.draw.circle(glow_surf, (r, g, b, int(60 * pulse)),
                               (radius, radius), radius)
            self.screen.blit(glow_surf, (sx - radius, sy - radius),
                             special_flags=pygame.BLEND_RGBA_ADD)


# ==========================================================================
if __name__ == "__main__":
    Game().run()
