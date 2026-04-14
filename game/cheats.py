"""Cheat commands for the F12 run command bar.

All cheat commands are registered here. When cheats are enabled (via
``enable cheats`` in the command bar), these commands become available.
Non-cheat commands (like ``help``) work regardless of cheat status.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from sandbox_rpg import Game


def execute_command(g: 'Game', raw: str) -> Tuple[bool, str]:
    """Parse and execute a command string.

    Returns ``(success, message)`` for display in the command bar.
    """
    parts = raw.strip().split()
    if not parts:
        return False, "No command entered."

    cmd = parts[0].lower()

    # -- Always-available commands --
    if raw.strip().lower() == "enable cheats":
        g.cheats_enabled = True
        return True, "Cheats enabled! Press the button below the minimap."

    if cmd == "help":
        return True, _help_text(g)

    # -- Cheat-gated commands below --
    if not g.cheats_enabled:
        return False, "Cheats are not enabled. Type: enable cheats"

    if cmd == "set" and len(parts) >= 3:
        return _cmd_set(g, parts[1].lower(), parts[2:])

    if cmd == "give" and len(parts) >= 2:
        return _cmd_give(g, parts[1], parts[2] if len(parts) > 2 else "1")

    if cmd == "god":
        g.god_mode = not g.god_mode
        state = "ON" if g.god_mode else "OFF"
        return True, f"God mode {state}"

    if cmd == "heal":
        from core.components import Health
        ph = g.em.get_component(g.player_id, Health)
        ph.current = ph.maximum
        return True, f"Healed to {ph.maximum} HP"

    if cmd == "kill":
        return _cmd_kill(g)

    if cmd == "levelup":
        return _cmd_levelup(g, parts[1] if len(parts) > 1 else "1")

    if cmd == "clear":
        return True, ""

    return False, f"Unknown command: {cmd}. Type help for a list."


def _help_text(g: 'Game') -> str:
    """Return a short help string."""
    if not g.cheats_enabled:
        return "enable cheats | help"
    return ("set <stat> <val> | give <item> [n] | god | heal | "
            "kill | levelup [n] | help")


# ── set <stat> <value> ───────────────────────────────────────────────

def _cmd_set(g: 'Game', stat: str, args: list) -> Tuple[bool, str]:
    from core.components import Health, PlayerStats, Inventory

    ph = g.em.get_component(g.player_id, Health)
    ps = g.em.get_component(g.player_id, PlayerStats)

    try:
        val = int(args[0])
    except (ValueError, IndexError):
        return False, f"Invalid value: {args[0]}"

    if stat == "health" or stat == "hp":
        ph.current = max(1, min(val, ph.maximum))
        g.health_bar.set_value(ph.current)
        return True, f"HP set to {ph.current}"

    if stat == "maxhp" or stat == "max_hp":
        ph.maximum = max(1, val)
        ph.current = min(ph.current, ph.maximum)
        g.health_bar.max_value = ph.maximum
        g.health_bar.set_value(ph.current)
        return True, f"Max HP set to {ph.maximum}"

    if stat == "level":
        ps.level = max(1, val)
        return True, f"Level set to {ps.level}"

    if stat == "xp":
        ps.xp = max(0, val)
        g.xp_bar.set_value(ps.xp)
        return True, f"XP set to {ps.xp}"

    if stat == "stat_points" or stat == "points":
        ps.stat_points = max(0, val)
        return True, f"Stat points set to {ps.stat_points}"

    if stat == "strength" or stat == "str":
        ps.strength = max(1, val)
        return True, f"Strength set to {ps.strength}"

    if stat == "agility" or stat == "agi":
        ps.agility = max(1, val)
        return True, f"Agility set to {ps.agility}"

    if stat == "vitality" or stat == "vit":
        ps.vitality = max(1, val)
        return True, f"Vitality set to {ps.vitality}"

    if stat == "luck":
        ps.luck = max(1, val)
        return True, f"Luck set to {ps.luck}"

    if stat == "kills":
        ps.kills = max(0, val)
        return True, f"Kills set to {ps.kills}"

    if stat == "day":
        g.daynight.day_number = max(1, val)
        return True, f"Day set to {g.daynight.day_number}"

    return False, f"Unknown stat: {stat}"


# ── give <item_id> [count] ───────────────────────────────────────────

def _cmd_give(g: 'Game', item_id: str, count_str: str) -> Tuple[bool, str]:
    from core.components import Inventory
    from data import ITEM_DATA

    try:
        count = max(1, int(count_str))
    except ValueError:
        return False, f"Invalid count: {count_str}"

    if item_id not in ITEM_DATA:
        return False, f"Unknown item: {item_id}"

    inv = g.em.get_component(g.player_id, Inventory)
    inv.add_item(item_id, count)
    name = ITEM_DATA[item_id][0]
    return True, f"Gave {count}x {name}"


# ── kill (all enemies) ───────────────────────────────────────────────

def _cmd_kill(g: 'Game') -> Tuple[bool, str]:
    from core.components import AI, Health as H, Transform
    killed = 0
    for eid in list(g.em.get_entities_with(AI, H)):
        if eid == g.player_id:
            continue
        h = g.em.get_component(eid, H)
        h.current = 0
        killed += 1
    return True, f"Killed {killed} enemies"


# ── levelup [amount] ─────────────────────────────────────────────────

def _cmd_levelup(g: 'Game', amount_str: str) -> Tuple[bool, str]:
    from core.components import PlayerStats
    ps = g.em.get_component(g.player_id, PlayerStats)
    try:
        amount = max(1, int(amount_str))
    except ValueError:
        amount = 1
    for _ in range(amount):
        ps.level += 1
        ps.stat_points += 3
    return True, f"Leveled up {amount}x → Lv.{ps.level} (+{amount * 3} stat points)"
