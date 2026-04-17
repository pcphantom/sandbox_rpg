"""Entity-Component-System core."""
from typing import Dict, Set, List, Any, Tuple, Type


class EntityManager:
    def __init__(self) -> None:
        self._next_id: int = 1
        self._components: Dict[Type, Dict[int, Any]] = {}
        self._entities: Set[int] = set()
        # Per-frame query cache — call clear_query_cache() once per tick.
        self._query_cache: Dict[Tuple[Type, ...], List[int]] = {}

    def clear_query_cache(self) -> None:
        """Invalidate the per-frame query cache.  Call at the start of each tick."""
        if self._query_cache:
            self._query_cache.clear()

    def create_entity(self) -> int:
        eid = self._next_id
        self._next_id += 1
        self._entities.add(eid)
        self._query_cache.clear()
        return eid

    def destroy_entity(self, entity: int) -> None:
        self._entities.discard(entity)
        for cd in self._components.values():
            cd.pop(entity, None)
        self._query_cache.clear()

    def add_component(self, entity: int, comp: Any) -> None:
        ct = type(comp)
        if ct not in self._components:
            self._components[ct] = {}
        self._components[ct][entity] = comp
        self._query_cache.clear()

    def get_component(self, entity: int, ct: Type) -> Any:
        return self._components.get(ct, {}).get(entity)

    def has_component(self, entity: int, ct: Type) -> bool:
        return entity in self._components.get(ct, {})

    def remove_component(self, entity: int, ct: Type) -> None:
        if ct in self._components:
            self._components[ct].pop(entity, None)
            self._query_cache.clear()

    def get_entities_with(self, *cts: Type) -> List[int]:
        if not cts:
            return list(self._entities)
        key = cts
        cached = self._query_cache.get(key)
        if cached is not None:
            return list(cached)
        sets = [set(self._components.get(c, {}).keys()) for c in cts]
        if not sets:
            self._query_cache[key] = []
            return []
        r = sets[0]
        for s in sets[1:]:
            r = r.intersection(s)
        result = list(r)
        self._query_cache[key] = result
        return list(result)

    @property
    def next_id(self) -> int:
        return self._next_id

    @next_id.setter
    def next_id(self, value: int) -> None:
        self._next_id = value
