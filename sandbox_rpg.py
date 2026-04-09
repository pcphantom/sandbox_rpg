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
    TILE_WATER, TILE_GRASS, TILE_DIRT, TILE_SAND, TILE_STONE_FLOOR,
    TILE_STONE_WALL, TILE_FOREST, QUICK_SAVE_SLOT, INVENTORY_TOTAL_SLOTS,
    MIN_ATTACK_COOLDOWN, BASE_ATTACK_COOLDOWN, AGILITY_COOLDOWN_REDUCTION,
    SLEEP_DURATION, SLEEP_TIME_MULTIPLIER,
    WALL_HP, TURRET_HP, TURRET_RANGE, TURRET_DAMAGE, TURRET_COOLDOWN,
    CHEST_CAPACITY, WAVE_SPAWN_RADIUS,
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
    ARMOR_VALUES, MOB_DATA, WAVE_MOB_TIERS,
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
import save_load

# ==========================================================================
# GAME
# ==========================================================================

class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sandbox Survival RPG")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dead = False
        self.paused = False
        self.seed = 42

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
        self.daynight = DayNightCycle(day_length=240.0)
        self.ai_system = AISystem()
        self.projectile_system = ProjectileSystem()
        self.trap_system = TrapSystem()
        self.turret_system = TurretSystem()
        self.wave_system = WaveSystem()
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

    # -- helpers -----------------------------------------------------------
    def _notify(self, msg: str, duration: float = 2.5) -> None:
        self.notification = msg
        self.notification_timer = duration

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
        self.em.add_component(eid, Health(data['hp']))
        mob_ai = AI('wander', mob_type)
        mob_ai.speed = data['speed']
        mob_ai.detection_range = data['detection']
        mob_ai.contact_damage = data['damage']
        mob_ai.xp_value = data['xp']
        self.em.add_component(eid, mob_ai)
        return eid

    def _populate_world(self) -> None:
        # Trees — denser in forest/grass biomes
        for _ in range(350):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
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
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
            if self.world.get_tile(x, y) == TILE_FOREST:
                eid = self.em.create_entity()
                self.em.add_component(eid, Transform(
                    x * TILE_SIZE + 8, y * TILE_SIZE - 16))
                self.em.add_component(eid, Renderable(
                    self.textures.get('tree'), layer=2))
                self.em.add_component(eid, Collider(24, 32, True))
        # Rocks
        for _ in range(200):
            x = random.randint(5, WORLD_WIDTH - 5)
            y = random.randint(5, WORLD_HEIGHT - 5)
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
                x = random.randint(5, WORLD_WIDTH - 5)
                y = random.randint(5, WORLD_HEIGHT - 5)
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

    def _spawn_wave_mobs(self, count: int, tier: int) -> None:
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

        for _ in range(count):
            angle = random.uniform(0, math.tau)
            dist = WAVE_SPAWN_RADIUS + random.uniform(0, 100)
            wx = target_x + math.cos(angle) * dist
            wy = target_y + math.sin(angle) * dist
            wx = clamp(wx, TILE_SIZE * 2, (WORLD_WIDTH - 2) * TILE_SIZE)
            wy = clamp(wy, TILE_SIZE * 2, (WORLD_HEIGHT - 2) * TILE_SIZE)
            mob_type = random.choice(available)
            self._create_mob(wx, wy, mob_type)

    # ======================================================================
    # MAIN LOOP
    # ======================================================================
    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            if not self.dead and not self.paused:
                self._update(dt)
            else:
                # Animate particles & dmg numbers even while paused/dead
                self.particles.update(dt)
                self.dmg_numbers = [
                    (x, y - 40 * dt, t, c, l - dt)
                    for x, y, t, c, l in self.dmg_numbers if l - dt > 0
                ]
            self._render()
        pygame.quit()
        sys.exit()

    # ======================================================================
    # EVENTS
    # ======================================================================
    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # --- Dead state ---
            if self.dead:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self._respawn()
                    elif event.key == pygame.K_q:
                        self.running = False
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
                )
                continue

            # --- Global hotkeys ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if (self.show_inventory or self.show_crafting
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
                inv = self.em.get_component(self.player_id, Inventory)
                inv.equipped_slot = (inv.equipped_slot - event.y) % 6

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
        self.ai_system.update(dt, self.em, self.player_id)
        self.projectile_system.update(dt, self.em, on_hit=self._on_proj_hit)
        self.trap_system.update(dt, self.em, on_hit=self._on_trap_hit)
        self.turret_system.update(dt, self.em, on_fire=self._on_turret_fire)
        self.daynight.update(dt)
        self.camera.follow(pt.x, pt.y)
        self.camera.update(dt)
        self.particles.update(dt)

        # Wave system
        wave_req = self.wave_system.update(dt, self.daynight.is_night())
        if wave_req:
            self._spawn_wave_mobs(wave_req['count'], wave_req['tier'])
            if self.wave_system.wave_spawned <= wave_req['count']:
                self._notify(f"Wave {self.wave_system.night_count}! Defend yourself!", 3.0)

        # Sleeping (bed mechanic)
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

        # Campfire healing
        self._campfire_heal(dt, pt)

        # Night damage
        self._night_damage(dt, pt)

        # Mob respawning
        self.mob_spawn_timer += dt
        if self.mob_spawn_timer > 15.0:
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
                self.dmg_numbers.append((t.x, t.y - 16, str(dmg), YELLOW, 0.8))
                self.particles.emit(t.x + 12, t.y + 10, 6, YELLOW, 50, 0.3)

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

        cd = max(0.2, rdata['cooldown'] - ps.dexterity * 0.02)
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
            eq_item = inv.get_equipped()
            bonus = (ITEM_DATA[eq_item][3]
                     if eq_item and eq_item in ITEM_DATA else 0)
            if r.surface == self.textures.get('tree'):
                inv.add_item('wood', random.randint(2, 4) + bonus)
                inv.add_item('stick', 1)
                th = self.em.get_component(nearest, Transform)
                self.particles.emit(th.x + 20, th.y + 30, 8,
                                    (80, 50, 30), 40, 0.3)
            else:
                inv.add_item('stone', random.randint(2, 3) + bonus)
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
            self._place_item(eq_id)
            inv.remove_item(eq_id, 1)
            self._notify(f"Placed {data[0]}")

    def _place_item(self, item_id: str) -> None:
        pt: Transform = self.em.get_component(self.player_id, Transform)
        pr: Renderable = self.em.get_component(self.player_id, Renderable)
        offset_x = -30 if pr.flip_x else 30
        eid = self.em.create_entity()
        px, py = pt.x + offset_x, pt.y + 20
        self.em.add_component(eid, Transform(px, py))
        self.em.add_component(eid, Placeable(item_id))

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
            self.em.add_component(eid, Renderable(
                self.textures.get('bed_placed'), layer=1))
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
                    self.daynight.set_speed(SLEEP_TIME_MULTIPLIER)
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
            'vitality': ps.vitality, 'dexterity': ps.dexterity,
            'inventory': inv_data, 'equipped': inv.equipped_slot,
            'eq_weapon': eq.weapon, 'eq_armor': eq.armor,
            'eq_shield': eq.shield, 'eq_ranged': eq.ranged,
            'eq_ammo': eq.ammo,
            'day_time': self.daynight.time,
            'night_count': self.wave_system.night_count,
            'structures': structures,
        }

    def _apply_save_data(self, data: Dict[str, Any]) -> None:
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
        ps.dexterity = data.get('dexterity', 1)
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
        self.wave_system.night_count = data.get('night_count', 0)
        self.health_bar.max_value = ph.maximum
        self.health_bar.set_value(ph.current)
        self.xp_bar.max_value = ps.xp_to_next
        self.xp_bar.set_value(ps.xp)
        self.dead = False

        # Restore structures
        for eid in list(self.em.get_entities_with(Placeable)):
            if not self.em.has_component(eid, AI):
                self.em.destroy_entity(eid)
        for struct in data.get('structures', []):
            self._restore_structure(struct)

    def _restore_structure(self, struct: Dict[str, Any]) -> None:
        """Recreate a placed structure from save data."""
        item_id = struct['type']
        eid = self.em.create_entity()
        self.em.add_component(eid, Transform(struct['x'], struct['y']))
        self.em.add_component(eid, Placeable(item_id))

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
            self.em.add_component(eid, Renderable(
                self.textures.get('bed_placed'), layer=1))
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
        save_load.save_game(QUICK_SAVE_SLOT, self._build_save_data())
        self._notify("Quick Saved!")

    def _quick_load(self) -> None:
        data = save_load.load_game(QUICK_SAVE_SLOT)
        if not data:
            self._notify("No quick save found!")
            return
        self._apply_save_data(data)
        self._notify("Quick Loaded!")

    def _save_to_slot(self, slot: int) -> None:
        save_load.save_game(slot, self._build_save_data())
        self._notify(f"Saved to slot {slot}!")

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
        self._draw_mob_health_bars()
        self._draw_placeable_health_bars()
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

        pygame.display.flip()

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

        # Time of day
        period = self.daynight.get_period_name()
        period_colors = {'Day': (255, 255, 200), 'Dawn': (255, 200, 140),
                         'Dusk': (200, 140, 180), 'Night': (140, 140, 220)}
        pc = period_colors.get(period, WHITE)
        self.screen.blit(self.font.render(period, True, pc),
                         (SCREEN_WIDTH - 195, 16))
        t_str = (f"{int(self.daynight.time * 24):02d}"
                 f":{int((self.daynight.time * 1440) % 60):02d}")
        self.screen.blit(self.font_sm.render(t_str, True, GRAY),
                         (SCREEN_WIDTH - 195, 36))

        # Wave info
        if self.wave_system.wave_active:
            wave_txt = f"WAVE {self.wave_system.night_count}  ({self.wave_system.wave_spawned}/{self.wave_system.wave_target})"
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

        # Controls hint
        ctrl = ("WASD:Move  Space:Attack  R:Ranged  E:Harvest/Chest  F:Use  "
                "I:Inv  C:Craft  P:Stats  Esc:Pause")
        ctrl_bg = pygame.Surface((len(ctrl) * 7 + 10, 18), pygame.SRCALPHA)
        ctrl_bg.fill((10, 10, 20, 140))
        self.screen.blit(ctrl_bg, (15, SCREEN_HEIGHT - 84))
        self.screen.blit(self.font_sm.render(ctrl, True, (140, 140, 160)),
                         (20, SCREEN_HEIGHT - 82))

    # -- death screen ------------------------------------------------------
    def _draw_death_screen(self) -> None:
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 180))
        self.screen.blit(ov, (0, 0))
        dt_text = self.font_xl.render("YOU DIED", True, RED)
        self.screen.blit(
            dt_text, (SCREEN_WIDTH // 2 - dt_text.get_width() // 2,
                      SCREEN_HEIGHT // 2 - 80))
        ht = self.font.render("Press [R] to Respawn  |  [Q] to Quit",
                              True, GRAY)
        self.screen.blit(
            ht, (SCREEN_WIDTH // 2 - ht.get_width() // 2,
                 SCREEN_HEIGHT // 2))
        ps: PlayerStats = self.em.get_component(self.player_id, PlayerStats)
        st = self.font.render(
            f"Level {ps.level}  |  {ps.kills} Kills", True, WHITE)
        self.screen.blit(
            st, (SCREEN_WIDTH // 2 - st.get_width() // 2,
                 SCREEN_HEIGHT // 2 + 40))


# ==========================================================================
if __name__ == "__main__":
    Game().run()
