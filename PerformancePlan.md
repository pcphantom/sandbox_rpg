# Performance Improvement Plan

## Executive Summary

This plan targets **CPU-bound bottlenecks** in the per-frame update and render loops.
Every change preserves identical gameplay, visuals, and feel — zero reduction to quality or experience.

The codebase currently has **~45 `get_entities_with` calls per frame** across systems, many of which are nested O(N×M) loops scanning every entity. With 50+ mobs, 30+ buildings, and 100+ total entities, these dominate frame time.

---

## Bottleneck Analysis

### Hot Path: Per-Frame Call Chain (from `game/update.py`)

```
update(dt)
 ├── movement.update()          → 1× get_entities_with(Transform, Velocity)
 ├── physics.update()           → 2× get_entities_with (rebuild ALL building rects every frame)
 ├── ai_system.update()         → 5× get_entities_with (nested: per-mob scans buildings + lights)
 ├── projectile_system.update() → 2× get_entities_with (nested: per-projectile scans all mobs)
 ├── trap_system.update()       → 2× get_entities_with (nested: per-trap scans all mobs)
 ├── turret_system.update()     → 3× get_entities_with (nested: per-turret scans all mobs)
 ├── _check_contact_damage()    → 1× get_entities_with (all mobs)
 ├── _check_enemy_projectile()  → 1× get_entities_with (all projectiles)
 ├── _campfire_heal()           → 1× get_entities_with (all placeables)
 ├── _night_damage()            → 1× get_entities_with (all lights)
 └── kill-dead loops            → 2× get_entities_with
```

### Hot Path: Per-Frame Render Chain (from `game/drawing.py`)

```
render()
 ├── draw_world()               → tile loop (already culled — fine)
 ├── draw_elite_outlines()      → 1× all AI + per-elite: mask + 8-direction stamp (EXPENSIVE)
 ├── renderer.update()          → 1× all Renderable + full sort every frame
 ├── draw_boss_glow()           → 1× all AI
 ├── draw_mob_health_bars()     → 1× all (Health, AI)
 ├── draw_placeable_health_bars()→ 1× all (Health, Placeable)
 ├── draw_lighting()            → 1× all LightSource + nested concentric-circle surfaces
 ├── minimap                    → 2× all AI + all Building (positions only)
 ├── bed prompt                 → 1× all Placeable
 └── repair prompt              → 1× all (Placeable, Health)
```

### Specific Bottleneck Details

| # | Location | Issue | Complexity | Impact |
|---|----------|-------|-----------|--------|
| 1 | `ai.py:88-98` | Every wandering mob scans ALL buildings to find nearest target | O(mobs × buildings) | **HIGH** |
| 2 | `ai.py:30-55` | `_find_blocking_wall` scans ALL solid colliders per stuck mob | O(stuck_mobs × entities) | **MED** |
| 3 | `ai.py:126` | Light-source scan for structure night damage per attacking mob | O(attacking_mobs × lights) | **MED** |
| 4 | `physics.py:40-51` | `_rebuild_building_rects` iterates ALL (Transform, Collider) every frame | O(N) per frame, N=all collidable | **HIGH** |
| 5 | `turret.py:55` | Each turret scans ALL mobs to find nearest target | O(turrets × mobs) | **HIGH** |
| 6 | `turret.py:89` | Lightning arc scans ALL mobs per turret shot | O(mobs) per shot | **LOW** |
| 7 | `projectile.py:35` | Each player projectile scans ALL mobs for collision | O(projectiles × mobs) | **MED** |
| 8 | `trap.py:33` | Each trap scans ALL mobs for proximity | O(traps × mobs) | **MED** |
| 9 | `combat.py:108` | Melee attack scans ALL mobs | O(mobs) | **LOW** |
| 10 | `combat.py:242` | Ranged auto-aim scans ALL mobs | O(mobs) | **LOW** |
| 11 | `combat.py:382` | `_find_nearest_enemy` scans ALL mobs | O(mobs) | **LOW** |
| 12 | `combat.py:616,768` | Light safety checks scan ALL lights | O(lights) | **LOW** |
| 13 | `render.py:18` | Full `.sort()` of ALL renderable entities every frame | O(N log N) | **MED** |
| 14 | `drawing.py:807-869` | Elite outlines: mask → silhouette → 8-dir stamp per elite per frame | O(elites × expand²) | **HIGH** |
| 15 | `drawing.py:252-260` | Lighting: creates temporary Surfaces in nested loop per light | O(lights × rings) | **MED** |
| 16 | `drawing.py:91-97` | Minimap iterates all AI + all Building separately | O(mobs + buildings) | **LOW** |
| 17 | `ecs.py:38-47` | `get_entities_with` builds set intersections every call; same queries repeated | O(component_sets) | **MED** |

---

## Implementation Plan

### Phase 1: Spatial Hash (Highest Impact)

**What:** A grid-based spatial index that maps entity positions to cells, enabling O(1) proximity queries instead of O(N) linear scans.

**File:** `core/spatial.py`

**Design:**
- `SpatialHash` class with configurable cell size (default 128px = 4 tiles)
- Methods: `insert(eid, x, y, w, h)`, `remove(eid)`, `update(eid, x, y, w, h)`, `query_radius(x, y, radius)`, `query_rect(x, y, w, h)`
- Internal dict: `cell (int, int) → set[int]` mapping grid cells to entity IDs
- Reverse lookup: `eid → set[(int, int)]` for O(1) removal/update
- Module-level singleton instance for global access

**Integration points (insert/remove):**
- `game/entities.py` — mob spawning, resource creation, populate_world, cave entities
- `game/interaction.py` — place_item (building creation), demolish/harvest (destroy_entity)
- `game/update.py` — kill-dead mob/placeable loops (destroy)
- `game/persistence.py` — restore_structure (load), _destroy_non_player_entities
- `systems/movement.py` — update position in hash after movement (only for moving entities)

**Integration points (query):**
- `systems/ai.py` — structure targeting (nearest Building within detection_range), blocking wall check
- `systems/physics.py` — replace `_rebuild_building_rects` with spatial query per moving entity
- `systems/turret.py` — nearest mob within fire_range
- `systems/trap.py` — mobs within trigger radius
- `systems/projectile.py` — mobs within hit radius
- `game/combat.py` — melee range, ranged auto-aim, contact damage, bomb AoE, campfire healing, light checks

**Expected gains:**
- Structure targeting: O(mobs × buildings) → O(mobs × ~4 cells)
- Turret targeting: O(turrets × mobs) → O(turrets × ~4 cells)
- Physics building check: O(N rebuild + M check) → O(movers × ~4 cells)
- Net: ~60-80% reduction in entity-scanning CPU time during combat-heavy scenarios

#### Checklist

- [ ] Create `core/spatial.py` with `SpatialHash` class and module-level instance
- [ ] Add position-update hook in `systems/movement.py` (update hash for moved entities)
- [ ] Integrate insert calls in `game/entities.py` (spawn_mob, populate_world, create_cave_entities)
- [ ] Integrate insert calls in `game/interaction.py` (place_item)
- [ ] Integrate remove calls in `game/update.py` (kill-dead loops), `game/interaction.py` (harvest/demolish)
- [ ] Integrate remove calls in `game/entities.py` (destroy_non_player_entities)
- [ ] Integrate remove calls in `game/persistence.py` (entity destruction on load)
- [ ] Refactor `systems/ai.py` to use spatial hash for structure targeting and blocking-wall check
- [ ] Refactor `systems/physics.py` to use spatial hash instead of `_rebuild_building_rects`
- [ ] Refactor `systems/turret.py` to use spatial hash for nearest-mob search
- [ ] Refactor `systems/trap.py` to use spatial hash for mob proximity
- [ ] Refactor `systems/projectile.py` to use spatial hash for collision detection
- [ ] Refactor `game/combat.py` proximity functions (melee, ranged aim, contact, campfire, AoE, light checks)

---

### Phase 2: ECS Query Cache (Medium Impact)

**What:** Cache `get_entities_with` results per frame so identical queries don't recompute set intersections.

**Design:**
- Add a `_query_cache: dict[tuple[Type, ...], list[int]]` to `EntityManager`
- On `get_entities_with`, check cache first; populate on miss
- Invalidate cache on `create_entity`, `destroy_entity`, `add_component`, `remove_component`
- Alternative: manual invalidation via `em.clear_query_cache()` called once per frame start

**Why this matters:**
- `(Transform, Health, AI)` is queried **10+ times per frame** (ai, turret, trap, projectile, combat melee/ranged/bomb/spell/contact)
- `(Transform, Collider)` is queried **3 times** (physics, ai blocking)
- `(Transform, Placeable)` is queried **4+ times** (trap, drawing, interaction)
- Each call does N set intersections + list conversion

**Expected gains:**
- ~30-40% reduction in ECS overhead (repeated intersection work eliminated)
- Most benefit during combat with many entities

#### Checklist

- [ ] Add `_query_cache` dict and cache-check logic to `EntityManager.get_entities_with`
- [ ] Add cache invalidation to `create_entity`, `destroy_entity`, `add_component`, `remove_component`
- [ ] (Optional) Add `clear_query_cache()` method for manual per-frame invalidation if auto-invalidation proves too aggressive

---

### Phase 3: Render Sort Optimization (Medium Impact)

**What:** Avoid full-sorting all renderable entities every frame when the order hasn't changed.

**Design:**
- Track a `_render_dirty` flag on the RenderSystem
- Set dirty when entities are created/destroyed or when Y positions change significantly
- Use insertion sort (nearly O(N) on mostly-sorted data) instead of Timsort when not dirty
- Alternative: maintain a pre-sorted list and use bisect-insort for additions

**Simpler approach:** Since Timsort is already adaptive (O(N) on sorted data), the main win is **avoiding the lambda key function overhead**. Pre-compute sort keys:
- Cache `(layer, y)` tuples and sort those, avoiding repeated `get_component` calls in the sort key
- This alone removes 2× `get_component` calls per comparison (O(N log N) comparisons)

#### Checklist

- [ ] Pre-compute sort keys as `(layer, y, eid)` tuples before sorting
- [ ] Apply off-screen culling BEFORE sorting (reduce N for sort)
- [ ] (Optional) Track render-order dirty flag to skip sort entirely when nothing moved

---

### Phase 4: Elite Outline Surface Caching (High Impact on Visual Frames)

**What:** Cache the expensive mask → silhouette → 8-direction-stamp pipeline for elite mobs.

**Current cost per elite per frame:**
1. `pygame.mask.from_surface(sprite)` — pixel-level mask extraction
2. `mask.to_surface(...)` — create RGBA silhouette
3. Create `outline_surf` (new Surface allocation)
4. 8× `expand` directional blits — 8-24 blits per elite

**Design:**
- Cache outline surface per `(sprite_surface_id, flip_x, tier, expand)` key
- Only regenerate when sprite changes (e.g., flip direction)
- Apply pulsing alpha via `set_alpha()` on the cached surface instead of regenerating with per-pixel alpha
- Store cache on the AI component or in a module-level dict keyed by entity ID

**Expected gains:**
- ~90% reduction in elite outline rendering cost (mask+stamp work eliminated)
- Significant during wave attacks with multiple elites

#### Checklist

- [ ] Add module-level outline cache dict in `game/drawing.py`
- [ ] Cache outline surfaces keyed by `(id(sprite), flip_x, tier)`
- [ ] Use `set_alpha()` for pulsing instead of regenerating the surface
- [ ] Invalidate cache entry when sprite or flip state changes

---

### Phase 5: Lighting Surface Pre-computation (Medium Impact)

**What:** Pre-compute the concentric-circle "light punch" surfaces instead of creating them every frame.

**Current cost per frame during night:**
- For EACH light source: nested loop from `radius` down to `15` in steps of `18`
- Each iteration: `pygame.Surface(...)` allocation + `pygame.draw.circle` + `overlay.blit`
- A light with radius 200 → ~11 temporary surfaces created and blitted per light per frame

**Design:**
- Pre-compute a set of light-punch surfaces for each unique `(radius, color)` pair
- Store in a module-level cache dict
- On draw, just blit the cached composite surface

**Expected gains:**
- ~70% reduction in lighting render cost during night
- Eliminates surface allocation churn

#### Checklist

- [ ] Create light-punch surface cache keyed by `(radius, color_tuple)`
- [ ] Pre-compose all concentric rings into a single cached surface per light config
- [ ] Blit cached surface instead of running the ring loop each frame
- [ ] Invalidate/rebuild only when a new light type is encountered

---

### Phase 6: Drawing Pass Consolidation (Low-Medium Impact)

**What:** Combine multiple per-frame iterations over the same entity sets into single passes.

**Current redundancy in `render()` chain:**
- `draw_elite_outlines()` iterates ALL `(Transform, AI)` → filters elites
- `draw_boss_glow()` iterates ALL `(Transform, AI)` → filters bosses
- `draw_mob_health_bars()` iterates ALL `(Transform, Health, AI)` → filters damaged
- Minimap iterates ALL `(Transform, AI)` for positions

These are **4 separate full scans** of the mob list per frame.

**Design:**
- Single `for eid in mobs:` loop that handles: elite outline, boss glow, health bar, and minimap position collection
- Classify each mob once, then dispatch to the appropriate draw function
- Off-screen culling applied once at the top of the combined loop

**Expected gains:**
- ~50% reduction in render-side entity iteration overhead
- Reduces `get_component` calls by 3× for mob-related rendering

#### Checklist

- [ ] Create unified `draw_mob_overlays(g)` function combining elite outlines, boss glow, mob health bars, and minimap mob collection
- [ ] Apply screen-space culling once at the top of the loop
- [ ] Replace the 4 separate draw calls in `render()` with the single combined call
- [ ] Ensure draw ORDER is preserved (outlines before sprites, glow after sprites, bars on top)

---

### Phase 7: Physics Building Cache (Medium Impact, Partially Covered by Phase 1)

**What:** Stop rebuilding the building-rects list every frame.

**Current:** `_rebuild_building_rects()` iterates ALL `(Transform, Collider)` entities, checks `solid`, checks no `Velocity`, and appends to a list — **every single frame**.

**Design (if spatial hash is implemented):**
- Replace `_building_rects` with spatial hash queries per moving entity
- Query only the cells around the entity's current + proposed position
- Buildings don't move, so their spatial hash entries are stable

**Design (standalone, if spatial hash is deferred):**
- Only rebuild when a building is added/removed (dirty flag)
- Set dirty flag in `place_item()`, `destroy_entity()` for buildings
- Skip rebuild when flag is clean

#### Checklist

- [ ] If Phase 1 done: replace `_entity_blocked` with spatial hash query
- [ ] If Phase 1 deferred: add dirty flag, rebuild only on building add/remove
- [ ] Remove the per-frame `_rebuild_building_rects` call

---

## Implementation Order & Dependencies

```
Phase 1 (Spatial Hash)  ←── highest impact, foundational
  ↓
Phase 2 (ECS Query Cache) ←── independent, can be done in parallel
  ↓
Phase 7 (Physics Cache) ←── depends on Phase 1 OR standalone
  ↓
Phase 3 (Render Sort) ←── independent
  ↓
Phase 4 (Elite Cache) ←── independent, high visual perf impact
  ↓
Phase 5 (Light Cache) ←── independent
  ↓
Phase 6 (Draw Consolidation) ←── depends on Phase 4 being done
```

**Recommended execution order:** 1 → 2 → 7 → 4 → 5 → 3 → 6

Phases 2, 3, 4, and 5 are fully independent and could be done in any order.
Phase 7 should follow Phase 1 (it uses the spatial hash).
Phase 6 should follow Phase 4 (it consolidates the elite drawing that Phase 4 caches).

---

## Risk Assessment

| Phase | Risk | Mitigation |
|-------|------|------------|
| 1 - Spatial Hash | Entities not properly inserted/removed → invisible or immortal mobs | Unit test: spawn mob → verify in hash → kill → verify removed |
| 1 - Spatial Hash | Cell size too large → queries return too many results | Benchmark with cell sizes 64, 128, 256; default 128 |
| 2 - Query Cache | Stale cache → missing/phantom entities | Invalidate on ALL mutation operations; assert cache correctness in debug |
| 3 - Render Sort | Skipping sort → visual z-order glitches | Only skip when truly clean; fallback to full sort if unsure |
| 4 - Elite Cache | Stale outline when sprite changes → visual artifact | Key cache on surface identity + flip state; invalidate conservatively |
| 5 - Light Cache | Wrong radius cached → lighting artifacts | Key on exact (radius, color) tuple |
| 6 - Draw Consolidation | Draw order wrong → outlines on top of sprites | Careful ordering: collect data in single pass, draw in correct order |

---

## Validation Strategy

1. **Before any changes:** Run the game headless to establish baseline (no errors/warnings)
2. **After each phase:** Run headless test to verify no regressions
3. **Visual verification:** Spot-check that elite outlines, boss glows, lighting, health bars all look identical
4. **Performance verification:** Add optional FPS counter / frame-time logging to confirm gains
5. **Save/load verification:** Ensure spatial hash is rebuilt correctly after loading a save

---

## Notes

- All changes are **internal optimizations** — no gameplay, balancing, UI, or visual changes
- The spatial hash is the single highest-impact change; it eliminates the dominant O(N²) patterns
- ECS query caching provides broad benefit since the same component queries are repeated extensively
- Surface caching (elite outlines, lighting) eliminates per-frame allocation churn that stresses the GC
- The existing off-screen culling in `render.py` and `drawing.py` is well-implemented and should be preserved
- The particle system (`rendering/particles.py`) already uses `__slots__` and is reasonably efficient
- The world tile rendering (`draw_world`) already uses camera-based culling — no changes needed
