"""Spells package — collects all per-spell modules into a unified SPELL_DATA dict.

Usage:
    from spells import SPELL_DATA
"""
from typing import Dict, Any

from spells.fireball import FIREBALL_SPELLS
from spells.heal import HEAL_SPELLS
from spells.lightning import LIGHTNING_SPELLS
from spells.ice import ICE_SPELLS
from spells.protection import PROTECTION_SPELLS
from spells.regen import REGEN_SPELLS
from spells.strength import STRENGTH_SPELLS
from game_controller import SPELL_RECHARGE                           # noqa: F401

# -- All spells (offensive, heal, and buff) ------------------------------------
SPELL_DATA: Dict[str, Dict[str, Any]] = {}
SPELL_DATA.update(FIREBALL_SPELLS)
SPELL_DATA.update(HEAL_SPELLS)
SPELL_DATA.update(LIGHTNING_SPELLS)
SPELL_DATA.update(ICE_SPELLS)
SPELL_DATA.update(PROTECTION_SPELLS)
SPELL_DATA.update(REGEN_SPELLS)
SPELL_DATA.update(STRENGTH_SPELLS)

__all__ = [
    'SPELL_DATA', 'SPELL_RECHARGE',
    'FIREBALL_SPELLS', 'HEAL_SPELLS', 'LIGHTNING_SPELLS', 'ICE_SPELLS',
    'PROTECTION_SPELLS', 'REGEN_SPELLS', 'STRENGTH_SPELLS',
]
