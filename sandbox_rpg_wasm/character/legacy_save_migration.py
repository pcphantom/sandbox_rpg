"""Legacy save migration — detect saves missing character customization data.

==========================================================================
REMOVABLE MODULE — This file exists solely to handle save files created
before the character generation feature was added.  Once there is no
chance of such legacy saves existing, this entire file can be safely
deleted and all imports / calls to it removed.  Search for
``legacy_save_migration`` across the codebase to find all references.
==========================================================================

The only public function is ``check_needs_migration(data)`` which returns
True when the save dict has no ``'character'`` key, meaning the player
has never gone through character creation for this save.
"""
from typing import Any, Dict


def check_needs_migration(data: Dict[str, Any]) -> bool:
    """Return True if *data* is a save dict that predates character gen.

    Parameters
    ----------
    data : dict
        The save-game dictionary as returned by ``save_load.load_game()``.

    Returns
    -------
    bool
        ``True`` when the save lacks a ``'character'`` key, indicating
        the player should be routed through the character generator
        before resuming play.
    """
    if not data:
        return False
    return 'character' not in data
