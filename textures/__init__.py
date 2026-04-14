"""Procedural texture generation for all game assets.

Split into sub-modules by category.  ``TextureGenerator`` remains the
sole public class — consumers just ``from textures import TextureGenerator``.
"""
from typing import Dict, Callable

import pygame

from textures import tiles, mobs, items, buildings, effects


class TextureGenerator:
    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.cache: Dict[str, pygame.Surface] = {}

    def get(self, key: str) -> pygame.Surface:
        return self.cache[key]

    def _get(self, key: str, maker: Callable[[], pygame.Surface]) -> pygame.Surface:
        if key not in self.cache:
            self.cache[key] = maker()
        return self.cache[key]

    # ------------------------------------------------------------------
    # Master generator — call once after pygame.init()
    # ------------------------------------------------------------------
    def generate_all(self) -> None:
        # Player
        tiles.generate_player(self)
        # Mobs
        mobs.generate_slime(self)
        mobs.generate_skeleton(self)
        mobs.generate_wolf(self)
        mobs.generate_goblin(self)
        mobs.generate_ghost(self)
        mobs.generate_spider(self)
        mobs.generate_orc(self)
        mobs.generate_dark_knight(self)
        mobs.generate_zombie(self)
        mobs.generate_wraith(self)
        mobs.generate_troll(self)
        mobs.generate_skeleton_archer(self)
        mobs.generate_goblin_shaman(self)
        mobs.generate_boss_golem(self)
        mobs.generate_boss_lich(self)
        mobs.generate_boss_dragon(self)
        mobs.generate_boss_necromancer(self)
        mobs.generate_boss_troll_king(self)
        # Resources
        tiles.generate_tree(self)
        tiles.generate_rock(self)
        # Tiles
        tiles.generate_grass_tile(self)
        tiles.generate_dirt_tile(self)
        tiles.generate_sand_tile(self)
        tiles.generate_water_tile(self, 0)
        tiles.generate_stone_tile(self)
        tiles.generate_forest_tile(self)
        tiles.generate_cave_floor_tile(self)
        tiles.generate_cave_entrance_tile(self)
        tiles.generate_ore_node(self)
        tiles.generate_diamond_node(self)
        # Original items
        items.generate_item_wood(self)
        items.generate_item_stone(self)
        items.generate_item_stick(self)
        items.generate_item_berry(self)
        items.generate_item_axe(self)
        items.generate_item_sword(self)
        items.generate_item_torch(self)
        items.generate_item_campfire(self)
        items.generate_item_pie(self)
        items.generate_item_bandage(self)
        # New items
        items.generate_item_iron_sword(self)
        items.generate_item_spear(self)
        items.generate_item_bow(self)
        items.generate_item_arrow(self)
        items.generate_item_sling(self)
        items.generate_item_rock_ammo(self)
        items.generate_item_sling_bullet(self)
        items.generate_item_leather_armor(self)
        items.generate_item_wood_shield(self)
        items.generate_item_trap(self)
        items.generate_item_bed(self)
        # New items (phase 2)
        items.generate_item_iron(self)
        items.generate_item_cloth(self)
        items.generate_item_bone(self)
        items.generate_item_leather(self)
        items.generate_item_health_potion(self)
        items.generate_item_antidote(self)
        items.generate_item_iron_axe(self)
        items.generate_item_mace(self)
        items.generate_item_bone_club(self)
        items.generate_item_crossbow(self)
        items.generate_item_fire_arrow(self)
        items.generate_item_bolt(self)
        items.generate_item_iron_armor(self)
        items.generate_item_iron_shield(self)
        items.generate_item_spell_fireball(self)
        # Building items
        buildings.generate_item_wall(self)
        buildings.generate_item_stone_wall_b(self)
        buildings.generate_item_turret(self)
        buildings.generate_item_chest(self)
        buildings.generate_item_door(self)
        # Placed objects
        buildings.generate_campfire(self, True)
        buildings.generate_campfire(self, False)
        buildings.generate_torch_placed(self)
        buildings.generate_trap_placed(self)
        buildings.generate_bed_placed(self)
        buildings.generate_wall_placed(self)
        buildings.generate_stone_wall_placed(self)
        buildings.generate_turret_placed(self)
        buildings.generate_chest_placed(self)
        buildings.generate_cave_chest_placed(self)
        buildings.generate_door_placed(self)
        # Beacon and Stone Oven
        buildings.generate_item_beacon(self)
        buildings.generate_beacon_placed(self)
        buildings.generate_item_stone_oven(self)
        buildings.generate_stone_oven_placed(self, False)
        buildings.generate_stone_oven_placed(self, True)
        # Projectiles
        effects.generate_projectile_arrow(self)
        effects.generate_projectile_rock(self)
        effects.generate_projectile_bolt(self)
        effects.generate_projectile_fireball(self)
        effects.generate_projectile_enemy(self)
        # New spell / item textures
        items.generate_item_spell_heal(self)
        items.generate_item_spell_lightning(self)
        items.generate_item_spell_ice(self)
        items.generate_item_diamond(self)
        items.generate_item_gunpowder(self)
        items.generate_item_iron_ore(self)
        items.generate_item_bomb(self)
        items.generate_item_brilliant_diamond(self)
        items.generate_item_titanium_ore(self)
        items.generate_item_titanium_ingot(self)
        items.generate_item_titanium_axe(self)
        items.generate_item_diamond_axe(self)
        items.generate_item_greater_enchantment_table(self)
        items.generate_buff_spell_books(self)
        items.generate_tiered_spell_books(self)
        items.generate_stat_weapons(self)
        items.generate_stat_ranged(self)
        items.generate_stat_armors(self)
        items.generate_stat_turrets(self)
        effects.generate_projectile_lightning(self)
        effects.generate_projectile_ice(self)
        effects.generate_projectile_bomb(self)
        items.generate_item_hammer(self)
        # Enchantment system
        effects.generate_enchant_tomes(self)
        effects.generate_transfer_tomes(self)
        effects.generate_item_enchantment_table(self)
        effects.generate_enchantment_table_placed(self)

    # Delegate methods — support code that calls gen.generate_X() directly
    def generate_water_tile(self, frame: int = 0) -> pygame.Surface:
        return tiles.generate_water_tile(self, frame)
