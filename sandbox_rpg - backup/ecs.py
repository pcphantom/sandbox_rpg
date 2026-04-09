"""Entity-Component-System core."""
from typing import Dict, Set, List, Any, Type


class EntityManager:
    def __init__(self) -> None:
        self._next_id: int = 1
        self._components: Dict[Type, Dict[int, Any]] = {}
        self._entities: Set[int] = set()

    def create_entity(self) -> int:
        eid = self._next_id
        self._next_id += 1
        self._entities.add(eid)
        return eid

    def destroy_entity(self, entity: int) -> None:
        self._entities.discard(entity)
        for cd in self._components.values():
            cd.pop(entity, None)

    def add_component(self, entity: int, comp: Any) -> None:
        ct = type(comp)
        if ct not in self._components:
            self._components[ct] = {}
        self._components[ct][entity] = comp

    def get_component(self, entity: int, ct: Type) -> Any:
        return self._components.get(ct, {}).get(entity)

    def has_component(self, entity: int, ct: Type) -> bool:
        return entity in self._components.get(ct, {})

    def remove_component(self, entity: int, ct: Type) -> None:
        if ct in self._components:
            self._components[ct].pop(entity, None)

    def get_entities_with(self, *cts: Type) -> List[int]:
        if not cts:
            return list(self._entities)
        sets = [set(self._components.get(c, {}).keys()) for c in cts]
        if not sets:
            return []
        r = sets[0]
        for s in sets[1:]:
            r = r.intersection(s)
        return list(r)

    @property
    def next_id(self) -> int:
        return self._next_id

    @next_id.setter
    def next_id(self, value: int) -> None:
        self._next_id = value
