"""Cheat commands for the F12 run command bar.

All cheat commands are registered here. When cheats are enabled (via
``enable cheats`` in the command bar), these commands become available.
Non-cheat commands (like ``help``) work regardless of cheat status.
"""
from __future__ import annotations

import shlex

from typing import TYPE_CHECKING, Tuple, Optional, List

if TYPE_CHECKING:
    from sandbox_rpg import Game

import game_controller as gc


def execute_command(g: 'Game', raw: str) -> Tuple[bool, str]:
    """Parse and execute a command string.

    Returns ``(success, message)`` for display in the command bar.
    """
    try:
        parts = shlex.split(raw.strip())
    except ValueError as exc:
        return False, gc.MSG_CHEAT_INVALID_COMMAND_SYNTAX.format(error=exc)

    if not parts:
        return False, gc.MSG_CHEAT_NO_COMMAND_ENTERED

    cmd = parts[0].lower()
    normalized_raw = ' '.join(part.lower() for part in parts)

    # -- Always-available commands --
    if normalized_raw == "enable cheats":
        g.cheats_enabled = True
        g.has_cheated = True
        return True, gc.MSG_CHEAT_ENABLED

    if normalized_raw in ("disable cheats", "cheats disabled", "cheats off"):
        _disable_cheats(g)
        return True, gc.MSG_CHEAT_DISABLED

    if cmd == "help":
        return True, _help_text(g)

    # -- Cheat-gated commands below --
    if not g.cheats_enabled:
        return False, gc.MSG_CHEAT_NOT_ENABLED

    if cmd == "set" and len(parts) >= 3:
        return _cmd_set(g, parts[1].lower(), parts[2:])

    if cmd == "give":
        return _cmd_give(g, parts[1:])

    if cmd == "god":
        g.god_mode = not g.god_mode
        state = "ON" if g.god_mode else "OFF"
        return True, gc.MSG_CHEAT_GOD_MODE.format(state=state)

    if cmd == "heal":
        from core.components import Health
        ph = g.em.get_component(g.player_id, Health)
        ph.current = ph.maximum
        return True, gc.MSG_CHEAT_HEALED_TO_HP.format(hp=ph.maximum)

    if cmd == "kill":
        return _cmd_kill(g)

    if cmd == "autokill":
        return _cmd_autokill(g, parts[1:])

    if cmd == "timestop":
        return _cmd_timestop(g, parts[1:])

    if cmd == "timestart":
        return _cmd_timestart(g, parts[1:])

    if cmd == "levelup":
        return _cmd_levelup(g, parts[1] if len(parts) > 1 else "1")

    if cmd == "clear":
        return True, ""

    return False, gc.MSG_CHEAT_UNKNOWN_COMMAND.format(cmd=cmd)


def _help_text(g: 'Game') -> str:
    """Return a short help string."""
    if not g.cheats_enabled:
        return gc.MSG_CHEAT_HELP_DISABLED
    return gc.MSG_CHEAT_HELP_ENABLED


def _disable_cheats(g: 'Game') -> None:
    g.cheats_enabled = False
    g.god_mode = False
    g.autokill_enabled = False
    g.autokill_timer = 0.0
    g.daynight.start_time()
    g.daynight.reset_speed()
    g.show_cheat_help = False


def kill_all_enemies(g: 'Game') -> int:
    from core.components import AI, Health

    killed = 0
    for entity_id in list(g.em.get_entities_with(AI, Health)):
        health = g.em.get_component(entity_id, Health)
        if not health.is_alive():
            continue
        health.current = 0
        killed += 1
    return killed


def _normalize_item_query(text: str) -> str:
    return ''.join(ch for ch in text.lower() if ch.isalnum())


def _item_match_sort_key(item_id: str) -> tuple[str, str]:
    from data import ITEM_DATA

    return (ITEM_DATA[item_id][0].lower(), item_id)


def _find_item_matches(query: str) -> List[str]:
    from data import ITEM_DATA

    query = query.strip()
    if not query:
        return []

    query_lower = query.lower()
    query_normalized = _normalize_item_query(query)
    exact: list[str] = []
    prefix: list[str] = []
    contains: list[str] = []

    for item_id, data in ITEM_DATA.items():
        display_name = data[0]
        id_spaced = item_id.replace('_', ' ')
        candidates = (item_id.lower(), id_spaced.lower(), display_name.lower())
        normalized = (_normalize_item_query(item_id),
                      _normalize_item_query(display_name))
        if (query_lower in candidates
                or query_normalized in normalized):
            exact.append(item_id)
            continue
        if any(candidate.startswith(query_lower) for candidate in candidates):
            prefix.append(item_id)
            continue
        if any(candidate.startswith(query_normalized) for candidate in normalized):
            prefix.append(item_id)
            continue
        if (any(query_lower in candidate for candidate in candidates)
                or any(query_normalized in candidate for candidate in normalized)):
            contains.append(item_id)

    for bucket in (exact, prefix, contains):
        if bucket:
            return sorted(dict.fromkeys(bucket), key=_item_match_sort_key)
    return []


def _format_match_list(matches: List[str], max_items: int = 6) -> str:
    from data import ITEM_DATA

    labels = [ITEM_DATA[item_id][0] for item_id in matches[:max_items]]
    if len(matches) > max_items:
        labels.append('...')
    return ', '.join(labels)


def _split_give_args(args: List[str]) -> tuple[str, int]:
    if not args:
        return '', 1

    count = 1
    item_parts = args
    if len(args) > 1:
        try:
            count = max(1, int(args[-1]))
            item_parts = args[:-1]
        except ValueError:
            item_parts = args

    return ' '.join(item_parts).strip(), count


def _parse_give_spec(args: List[str]) -> tuple[Optional[dict], Optional[str]]:
    from core.item_metadata import (
        parse_level_token,
        resolve_enchant_type_token,
        resolve_rarity_token,
    )

    item_query, count = _split_give_args(args)
    if not item_query:
        return None, gc.MSG_CHEAT_GIVE_MISSING_ITEM

    tokens = item_query.split()
    consumed: set[int] = set()
    enchant: Optional[dict] = None
    rarity = 'common'
    enhancement_level: Optional[int] = None

    token_index = 0
    while token_index < len(tokens) - 1:
        enchant_type = resolve_enchant_type_token(tokens[token_index])
        enchant_level = parse_level_token(tokens[token_index + 1])
        if enchant_type and enchant_level is not None:
            if enchant is not None:
                return None, gc.MSG_CHEAT_GIVE_ONE_ENCHANT_ONLY
            enchant = {'type': enchant_type, 'level': enchant_level}
            consumed.update({token_index, token_index + 1})
            token_index += 2
            continue
        token_index += 1

    for token_index, token in enumerate(tokens):
        if token_index in consumed:
            continue
        resolved_rarity = resolve_rarity_token(token)
        if resolved_rarity is None:
            continue
        if rarity != 'common':
            return None, gc.MSG_CHEAT_GIVE_ONE_RARITY_ONLY
        rarity = resolved_rarity
        consumed.add(token_index)

    for token_index, token in enumerate(tokens):
        if token_index in consumed or not token.startswith('+'):
            continue
        resolved_level = parse_level_token(token)
        if resolved_level is None:
            return None, gc.MSG_CHEAT_GIVE_INVALID_ENHANCEMENT_TOKEN.format(
                token=token)
        if enhancement_level is not None:
            return None, gc.MSG_CHEAT_GIVE_ONE_ENHANCEMENT_ONLY
        enhancement_level = resolved_level
        consumed.add(token_index)

    item_indices = [token_index for token_index in range(len(tokens))
                    if token_index not in consumed]
    item_tokens = [tokens[token_index] for token_index in item_indices]
    if not item_tokens:
        return None, gc.MSG_CHEAT_GIVE_MISSING_ITEM_AFTER_METADATA

    return {
        'count': count,
        'tokens': tokens,
        'item_tokens': item_tokens,
        'item_indices': item_indices,
        'rarity': rarity,
        'enchant': enchant,
        'enhancement_level': enhancement_level,
    }, None


def _resolve_give_spec(spec: dict) -> tuple[Optional[dict], Optional[str]]:
    from core.item_metadata import (
        can_apply_enchant_to_item,
        set_item_enhancement_level,
    )
    from data import HAS_RARITY, ITEM_DATA

    item_query = ' '.join(spec['item_tokens']).strip()
    matches = _find_item_matches(item_query)
    if not matches:
        return None, gc.MSG_CHEAT_GIVE_UNKNOWN_ITEM.format(item_query=item_query)
    if len(matches) > 1:
        return None, gc.MSG_CHEAT_GIVE_AMBIGUOUS_ITEM.format(
            item_query=item_query,
            matches=_format_match_list(matches),
        )

    item_id = matches[0]
    enhancement_level = spec['enhancement_level']
    if enhancement_level is not None:
        enhanced_item_id = set_item_enhancement_level(item_id, enhancement_level)
        if not enhanced_item_id:
            return None, gc.MSG_CHEAT_GIVE_CANNOT_ENHANCE.format(
                name=ITEM_DATA[item_id][0],
                level=enhancement_level,
            )
        item_id = enhanced_item_id

    rarity = spec['rarity']
    if rarity != 'common' and not HAS_RARITY.get(item_id, False):
        return None, gc.MSG_CHEAT_GIVE_NO_RARITY_SUPPORT.format(
            name=ITEM_DATA[item_id][0])

    enchant = spec['enchant']
    if enchant and not can_apply_enchant_to_item(item_id, enchant['type']):
        return None, gc.MSG_CHEAT_GIVE_CANNOT_ENCHANT.format(
            name=ITEM_DATA[item_id][0],
            enchant_type=enchant['type'],
        )

    return {
        'item_id': item_id,
        'count': spec['count'],
        'enchant': enchant,
        'rarity': rarity,
    }, None


def _extract_autocomplete_spec(raw: str) -> tuple[Optional[dict], str]:
    spec, error = _parse_give_spec(raw.split())
    if spec is None:
        return None, error
    return spec, ''


def _build_autocomplete_text(spec: dict, item_id: str) -> str:
    tokens = spec['tokens']
    rebuilt_tokens: List[str] = []
    item_inserted = False
    item_index_set = set(spec['item_indices'])
    for token_index, token in enumerate(tokens):
        if token_index in item_index_set:
            if not item_inserted:
                rebuilt_tokens.append(item_id)
                item_inserted = True
            continue
        rebuilt_tokens.append(token)
    if not item_inserted:
        rebuilt_tokens.append(item_id)
    rebuilt = ' '.join(rebuilt_tokens)
    count = spec['count']
    if count != 1:
        rebuilt = f"{rebuilt} {count}"
    return f"give {rebuilt}".strip()


def _is_enhanced_variant(item_id: str) -> bool:
    from data import CAN_ENHANCE

    for base_id, can_enhance in CAN_ENHANCE.items():
        if (can_enhance and item_id.startswith(base_id + '_')
                and item_id[len(base_id) + 1:].isdigit()):
            return True
    return False


def _filter_autocomplete_matches(query: str, matches: List[str]) -> List[str]:
    if any(ch.isdigit() for ch in query) or '+' in query:
        return matches

    base_matches = [item_id for item_id in matches
                    if not _is_enhanced_variant(item_id)]
    return base_matches or matches


def autocomplete_command(g: 'Game', raw: str,
                         apply: bool = False) -> Tuple[str, str]:
    """Autocomplete the `give` command item argument.

    Returns ``(new_text, hint)``. If *apply* is False, ``new_text`` will be
    unchanged and only the preview hint is refreshed.
    """
    from data import ITEM_DATA

    stripped = raw.lstrip()
    if not stripped.lower().startswith('give'):
        return raw, ''

    remainder = stripped[4:].lstrip()
    if not remainder or raw.endswith(' '):
        return raw, gc.MSG_CHEAT_AUTOCOMPLETE_HINT

    spec, error = _parse_give_spec(remainder.split())
    if spec is None:
        return raw, '' if error.startswith('Missing item') else error

    query = ' '.join(spec['item_tokens']).strip()
    matches = _filter_autocomplete_matches(query, _find_item_matches(query))
    if not matches:
        return raw, ''

    if len(matches) == 1:
        item_id = matches[0]
        completed = _build_autocomplete_text(spec, item_id)
        hint = gc.MSG_CHEAT_AUTOCOMPLETE_GIVE_PREVIEW.format(
            name=ITEM_DATA[item_id][0])
        return (completed if apply else raw), hint

    return raw, gc.MSG_CHEAT_AUTOCOMPLETE_MATCHES.format(
        matches=_format_match_list(matches))


# ── set <stat> <value> ───────────────────────────────────────────────

def _cmd_set(g: 'Game', stat: str, args: list) -> Tuple[bool, str]:
    from core.components import Health, PlayerStats, Inventory

    ph = g.em.get_component(g.player_id, Health)
    ps = g.em.get_component(g.player_id, PlayerStats)

    try:
        val = int(args[0])
    except (ValueError, IndexError):
        return False, gc.MSG_CHEAT_SET_INVALID_VALUE

    if stat == "health" or stat == "hp":
        ph.current = max(1, min(val, ph.maximum))
        g.health_bar.set_value(ph.current)
        return True, gc.MSG_CHEAT_SET_HP.format(value=ph.current)

    if stat == "maxhp" or stat == "max_hp":
        ph.maximum = max(1, val)
        ph.current = min(ph.current, ph.maximum)
        g.health_bar.max_value = ph.maximum
        g.health_bar.set_value(ph.current)
        return True, gc.MSG_CHEAT_SET_MAX_HP.format(value=ph.maximum)

    if stat == "level":
        ps.level = max(1, val)
        return True, gc.MSG_CHEAT_SET_LEVEL.format(value=ps.level)

    if stat == "xp":
        ps.xp = max(0, val)
        g.xp_bar.set_value(ps.xp)
        return True, gc.MSG_CHEAT_SET_XP.format(value=ps.xp)

    if stat == "stat_points" or stat == "points":
        ps.stat_points = max(0, val)
        return True, gc.MSG_CHEAT_SET_STAT_POINTS.format(
            value=ps.stat_points)

    if stat == "strength" or stat == "str":
        ps.strength = max(1, val)
        return True, gc.MSG_CHEAT_SET_STRENGTH.format(value=ps.strength)

    if stat == "agility" or stat == "agi":
        ps.agility = max(1, val)
        return True, gc.MSG_CHEAT_SET_AGILITY.format(value=ps.agility)

    if stat == "vitality" or stat == "vit":
        ps.vitality = max(1, val)
        return True, gc.MSG_CHEAT_SET_VITALITY.format(value=ps.vitality)

    if stat == "luck":
        ps.luck = max(1, val)
        return True, gc.MSG_CHEAT_SET_LUCK.format(value=ps.luck)

    if stat == "kills":
        ps.kills = max(0, val)
        return True, gc.MSG_CHEAT_SET_KILLS.format(value=ps.kills)

    if stat == "day":
        g.daynight.day_number = max(1, val)
        return True, gc.MSG_CHEAT_SET_DAY.format(value=g.daynight.day_number)

    return False, gc.MSG_CHEAT_UNKNOWN_STAT.format(stat=stat)


# ── give <item_id> [count] ───────────────────────────────────────────

def _cmd_give(g: 'Game', args: List[str]) -> Tuple[bool, str]:
    from core.components import Inventory
    from core.item_presentation import build_item_presentation

    parsed_spec, error = _parse_give_spec(args)
    if parsed_spec is None:
        return False, error or gc.MSG_CHEAT_GIVE_INVALID_ITEM_SPEC
    resolved_spec, error = _resolve_give_spec(parsed_spec)
    if resolved_spec is None:
        return False, error or gc.MSG_CHEAT_GIVE_INVALID_ITEM_SPEC

    inv = g.em.get_component(g.player_id, Inventory)
    overflow = inv.add_item_enchanted(
        resolved_spec['item_id'],
        resolved_spec['enchant'],
        resolved_spec['count'],
        resolved_spec['rarity'],
    )
    placed_count = resolved_spec['count'] - overflow
    if placed_count <= 0:
        return False, gc.MSG_CHEAT_GIVE_INVENTORY_FULL

    presentation = build_item_presentation(
        resolved_spec['item_id'],
        resolved_spec['rarity'],
        resolved_spec['enchant'],
        placed_count,
        include_count=True,
    )
    rarity_suffix = ''
    if resolved_spec['rarity'] != 'common':
        rarity_suffix = f" ({resolved_spec['rarity'].title()})"
    if overflow > 0:
        return True, gc.MSG_CHEAT_GIVE_SUCCESS_PARTIAL.format(
            label=presentation['label'],
            rarity_suffix=rarity_suffix,
            overflow=overflow,
        )
    return True, gc.MSG_CHEAT_GIVE_SUCCESS.format(
        label=presentation['label'],
        rarity_suffix=rarity_suffix,
    )


# ── kill (all enemies) ───────────────────────────────────────────────

def _cmd_kill(g: 'Game') -> Tuple[bool, str]:
    killed = kill_all_enemies(g)
    return True, gc.MSG_CHEAT_KILLED_ENEMIES.format(count=killed)


def _cmd_autokill(g: 'Game', args: List[str]) -> Tuple[bool, str]:
    state_arg = args[0].lower() if args else ''
    if state_arg in ('on', 'true', '1'):
        g.autokill_enabled = True
    elif state_arg in ('off', 'false', '0'):
        g.autokill_enabled = False
    elif not state_arg:
        g.autokill_enabled = not g.autokill_enabled
    else:
        return False, gc.MSG_CHEAT_AUTOKILL_USAGE

    g.autokill_timer = 0.0
    state = 'ON' if g.autokill_enabled else 'OFF'
    return True, gc.MSG_CHEAT_AUTOKILL_STATE.format(state=state)


def _cmd_timestop(g: 'Game', args: List[str]) -> Tuple[bool, str]:
    if args:
        return False, gc.MSG_CHEAT_TIMESTOP_USAGE
    if g.daynight.is_time_stopped():
        return True, gc.MSG_CHEAT_TIME_ALREADY_STOPPED
    g.daynight.stop_time()
    return True, gc.MSG_CHEAT_TIME_STOPPED


def _cmd_timestart(g: 'Game', args: List[str]) -> Tuple[bool, str]:
    if args:
        return False, gc.MSG_CHEAT_TIMESTART_USAGE
    if not g.daynight.is_time_stopped():
        return True, gc.MSG_CHEAT_TIME_ALREADY_RUNNING
    g.daynight.start_time()
    g.daynight.reset_speed()
    return True, gc.MSG_CHEAT_TIME_RESTARTED


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
    return True, gc.MSG_CHEAT_LEVELUP_RESULT.format(
        amount=amount,
        level=ps.level,
        stat_points=amount * 3,
    )
