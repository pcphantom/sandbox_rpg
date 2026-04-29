# Explicit Pooling Implementation Plan

## Phase 1: Core Infrastructure

### 1.1 Create `core/pool.py` — Shared pooling utilities
- Add `Vector2Pool`: pre-allocated mutable vectors for temporary math during combat/spawning
- Add `RectPool`: pre-allocated rectangle objects for AABB calculations

### 1.2 Enhance `core/components.py` — Pool-compatible components
- Every mutable component gets a `reset(**kwargs)` method:
  - `Transform.reset(x, y)`, `Velocity.reset(vx, vy)`, `Projectile.reset(damage, owner, speed, max_range)`
- Add `Dormant` tag component (empty class extending `Component`) — used for serialization filtering only

### 1.3 Enhance `core/ecs.py` — Support dormant tagging in saves
- Confirm `get_entities_with()` supports negative filters (entities that DON'T have Dormant)

---

## Phase 2: ProjectilePool (Highest Impact)

### 2.1 Create `systems/pools.py` — ProjectilePool class
```python
class ProjectilePool:
    _pool: list[int]              # stack of recycled entity IDs  
    _active: set[int]             # authoritative live projectiles ONLY
    _initial_size: int            # pre-allocated capacity (e.g. 64)
    
    def __init__(self, initial_size=64):
        self._pool = []
        self._active = set()
        self._initial_size = initial_size
```

### 2.2 Implement `ProjectilePool.acquire(em, x, y, vx, vy, damage, max_range, owner) -> int`
```python
if self._pool:
    eid = self._pool.pop()
    # In-place mutation of EXISTING components
    t = em.get_component(eid, Transform); t.x, t.y = x, y
    v = em.get_component(eid, Velocity); v.vx, v.vy = vx, vy
    p = em.get_component(eid, Projectile)
    p.damage, p.max_range, p.owner = damage, max_range, owner
    p.distance_traveled = 0.0      # ← critical reset
    p.spell_id = ''                 # ← critical reset  
    p.is_bomb = False              # ← critical reset
else:
    eid = em.create_entity()
    em.add_component(eid, Transform(x, y))
    em.add_component(eid, Velocity(vx, vy))
    em.add_component(eid, Projectile(damage, owner, 400.0, max_range))
self._active.add(eid)
return eid
```

### 2.3 Implement `ProjectilePool.release(em, eid)`
```python
self._active.discard(eid)
spatial_hash.remove(eid)          # ← clean up collision grid
self._pool.append(eid)            # ← return to stack
```
- Components stay attached (no ECS mutation needed for dormant entities)

### 2.4 Update `systems/projectile.py` — Pool-driven update loop
- Accept `active_projectiles: set[int]` instead of querying ECS
- Iterate `_active`, NOT `em.get_entities_with(Transform, Velocity, Projectile)`
- Replace `em.destroy_entity(pid)` → `projectile_pool.release(em, pid)`

### 2.5 Update `game/combat.py` — Pool-based spawn
- All projectile creation calls change from:
  ```python
  eid = em.create_entity()
  em.add_component(eid, Transform(...))
  em.add_component(eid, Velocity(...))
  em.add_component(eid, Projectile(...))
  ```
  To single call:
  ```python
  eid = g.projectile_pool.acquire(em, x, y, vx, vy, damage, max_range, owner)
  ```

---

## Phase 3: ParticlePool

### 3.1 Pre-allocate in `rendering/particles.py`
- Pool of 512 `Particle` objects (already has `__slots__`)
- `_available: deque[int]` with indices `[0..511]`
- `_live: set[int]` tracking active particle indices

### 3.2 Implement in-place acquire() / release()
- Pop index from `_available`, mutate fields, add to `_live`
- On expiration: remove from `_live`, push to `_available`

### 3.3 Update `ParticleSystem.update(dt)` 
- Iterate `_live` set only (not the full list)
- No list comprehension — just inline mutation and index swaps

---

## Phase 4: Damage Number Ring Buffer

### 4.1 Replace `g.dmg_numbers` list with fixed ring buffer in `sandbox_rpg.py`
```python
RING_SIZE = 128
self._dmg_ring: list[tuple | None] = [None] * RING_SIZE
self._dmg_write_idx = 0
```

### 4.2 Insertion (game/update.py) — O(1) overwrite
```python
# OLD: g.dmg_numbers.append((x, y, text, color, 0.5))
# NEW:
idx = self._dmg_write_idx % RING_SIZE  
self._dmg_ring[idx] = (x, y, text, color, 0.5)
self._dmg_write_idx += 1
```

### 4.3 Update/render decay (game/update.py) — iterate ring, mutate in-place
- Loop `_dmg_ring`, skip `None` or lifetime ≤ 0 entries
- Mutate existing tuples via new tuple creation at same index:
  ```python
  for i in range(RING_SIZE):
      entry = self._dmg_ring[i]
      if entry is None: continue
      x, y, txt, col, life = entry
      if life - dt <= 0:
          self._dmg_ring[i] = None
      else:
          self._dmg_ring[i] = (x, y - speed*dt, txt, col, life - dt)
  ```

### 4.4 Rendering (game/drawing.py) — iterate ring directly
- No list comprehension filter: `for entry in self._dmg_ring: if entry: draw(entry)`

---

## Phase 5: Integration Wiring

### 5.1 Wire pool creation in `sandbox_rpg.py` Game.__init__
```python
from systems.pools import ProjectilePool  
self.projectile_pool = ProjectilePool(initial_size=64)
# Add dormant Dormant components to pool IDs via em.add_component when released
```

### 5.2 Pass pool active set to all consuming systems in `game/update.py`
```python
g.projectile_system.update(dt, g.em, g.projectile_pool._active, on_hit=g._on_proj_hit)
# AISystem already uses ECS queries for mobs — no change needed there
```

### 5.3 Update game entities module — pass pool reference everywhere projectiles are spawned
- `_spawn_arrow()`, `_fire_spell()`, `_throw_bomb()` all → `g.projectile_pool.acquire(...)`

---

## Phase 6: Save/Load Migration (Serialization Fix)

### 6.1 Serialization Filter — Option A (Recommended): Active-set-only save
```python
# In game/persistence.py — build_save_data():
saved_projectiles = []
for eid in g.projectile_pool._active:  # ← ONLY serialize LIVE projectiles
    t = em.get_component(eid, Transform)
    p = em.get_component(eid, Projectile)
    saved_projectiles.append({
        'eid': eid,
        'x': t.x, 'y': t.y,
        'vx': ..., 'vy': ...,
        'damage': p.damage, 'owner': p.owner, ...
    })
# Dormant entities in _pool are EXCLUDED from save entirely
```

### 6.2 Option B: Dormant tag component (alternative / supplementary)
- On `release()`: `em.add_component(eid, Dormant())`
- On `acquire()`: `em.remove_component(eid, Dormant())`
- Global save routine already skips entities with `Dormant` — this acts as a safety net for any other pooled systems added later

### 6.3 Load Flow — Fresh pool rebuild on game load
```python
# In _restore_from_save or apply_save_data():
g.projectile_pool = ProjectilePool(initial_size=64)  # ← fresh pool, empty _active
for saved_proj in save_data.get('projectiles', []):
    eid = g.em.create_entity()
    g.em.add_component(eid, Transform(saved_proj['x'], saved_proj['y']))
    g.em.add_component(eid, Velocity(saved_proj['vx'], saved_proj['vy']))
    g.em.add_component(eid, Projectile(...))
    g.projectile_pool._active.add(eid)  # ← register as active
# Pool IDs remain empty until projectiles are spawned/fired in the new game
```

### 6.4 Save format compatibility — keep existing save keys unchanged
- New save files include a `pool_stats` section: `{"projectile_pool_active": N, "projectile_pool_capacity": M}` for monitoring/debugging
- Old saves without projectile data simply load with empty pool (graceful degradation)

---

## Files to Create/Modify — Complete List

**NEW FILES:**
- `systems/pools.py` — ProjectilePool class
- `core/components.py` additions — `Dormant` tag component, `reset()` methods on all mutable components

**MODIFY FILES (exact order):**
1. `core/components.py` — Add `reset()` methods + `Dormant` tag
2. `systems/pools.py` — ProjectilePool implementation
3. `systems/projectile.py` — Use `_active` set iteration, call pool.release()
4. `game/combat.py` — Call pool.acquire() instead of create_entity for projectiles
5. `rendering/particles.py` — Pre-allocate Particle objects, in-place mutation
6. `game/update.py` — Pass pool._active to systems; ring buffer for damage numbers
7. `game/drawing.py` — Render from ring buffer instead of filtered list comprehension  
8. `game/persistence.py` — Filter saved projectiles by pool._active only
9. `sandbox_rpg.py` — Wire pool creation, pass references to systems, replace dmg_numbers with ring buffer

---

## Execution Order & Dependencies

```
Phase 1 (components reset + Dormant tag)     ← prerequisite for everything
       ↓
Phase 2 (ProjectilePool + projectile system) ← highest priority, depends on Phase 1
       ↓
Phase 3 (ParticlePool)                       ← independent, can run in parallel
       ↓
Phase 4 (Damage ring buffer)                 ← independent, can run in parallel
       ↓
Phase 5 (Integration wiring)                 ← depends on Phases 2+3+4
       ↓
Phase 6 (Save/Load migration + verification) ← depends on Phase 5
```

## Verification Checklist (Phase 6 continued)

- [ ] Memory profiling with `tracemalloc` during Day 205 wave — zero projectile/particle allocations per frame after initial warmup
- [ ] Frame time delta stable at peak combat (no spikes from GC or list comprehensions)
- [ ] Save/load cycle: load a save → dormant pool entities don't appear on screen as live projectiles
- [ ] Pool exhaustion test: flood 5000 projectiles → pool grows, saves only live ones, reload restores correctly
- [ ] Dormant tag safety net: verify any entity with `Dormant` component is excluded from all ECS queries that iterate active entities
- [ ] Ring buffer overflow: fire >128 damage numbers simultaneously — oldest entries get overwritten, no crashes or index errors

This plan is now airtight. Every pooled entity type uses in-place mutation for updates and is properly filtered during serialization to prevent dormant data from bleeding into save files.