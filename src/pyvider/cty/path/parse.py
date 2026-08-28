#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Parsing the string form `CtyPath.string()` emits.

`CtyPath.string()` has always been able to render a path as `rule[0].port` or
`tags['a']`. Nothing could read one back, so every caller that accepted a
hand-written path grew its own parser -- and a parser without a type cannot
tell a set element from a map key, because both are spelled `['a']`. Given the
type, it can: `KeyStep` is what a map and a set accept, `IndexStep` is what a
list and a tuple accept, and no type accepts both.

That makes the round trip exact rather than approximate:

    CtyPath.parse(p.string(), within=t) == p     for any p valid in t
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pyvider.cty.exceptions import AttributePathError

if TYPE_CHECKING:
    from pyvider.cty.path.base import CtyPath, PathStep
    from pyvider.cty.types import CtyType

# What `string()` renders for the empty path. Parsed back to the empty path so
# the round trip holds at the root as well.
ROOT_LITERAL = "(root)"

_QUOTES = ("'", '"')


def _read_bracket(text: str, start: int) -> tuple[object, int]:
    """Read one `[...]` beginning at `start`. Returns its content and the index after `]`."""
    end = text.find("]", start)
    if end == -1:
        raise AttributePathError(f"Unterminated '[' at position {start} in {text!r}")
    inner = text[start + 1 : end]
    if not inner:
        raise AttributePathError(f"Empty '[]' at position {start} in {text!r}")
    if inner[0] in _QUOTES:
        if len(inner) < 2 or inner[-1] != inner[0]:
            raise AttributePathError(f"Unbalanced quotes in {inner!r} at position {start} in {text!r}")
        return inner[1:-1], end + 1
    try:
        return int(inner), end + 1
    except ValueError:
        raise AttributePathError(
            f"Bracket contents {inner!r} at position {start} in {text!r} are neither "
            "an integer index nor a quoted key"
        ) from None


def _read_name(text: str, start: int) -> tuple[str, int]:
    """Read an attribute name beginning at `start`, up to the next `.` or `[`."""
    end = start
    while end < len(text) and text[end] not in ".[":
        end += 1
    return text[start:end], end


def tokenize(path_str: str) -> list[tuple[str, Any]]:
    """Split a path string into ("attr", name) and ("bracket", int | str) tokens.

    Strict by design: the whole string is consumed or it raises. The regex this
    replaces used `finditer`, which skipped anything it could not match, so a
    malformed path silently became a shorter valid-looking one.
    """
    if not path_str or path_str == ROOT_LITERAL:
        return []

    tokens: list[tuple[str, Any]] = []
    i = 0
    # A leading name has no dot; `string()` strips it so `size_gb` round-trips.
    if path_str[0] not in ".[":
        name, i = _read_name(path_str, 0)
        tokens.append(("attr", name))

    while i < len(path_str):
        char = path_str[i]
        if char == ".":
            name, i = _read_name(path_str, i + 1)
            tokens.append(("attr", name))
        elif char == "[":
            content, i = _read_bracket(path_str, i)
            tokens.append(("bracket", content))
        else:  # pragma: no cover - _read_name consumes everything else
            raise AttributePathError(f"Unexpected {char!r} at position {i} in {path_str!r}")
    return tokens


def _bracket_step(content: object, vtype: CtyType[Any] | None) -> PathStep:
    """Choose IndexStep or KeyStep for a `[...]` token.

    Without a type this is the syntax's own guess and a set element is
    indistinguishable from a map key. With one it is decided: a list or tuple
    takes an index, a map or set takes a key.
    """
    from pyvider.cty.path.base import IndexStep, KeyStep
    from pyvider.cty.types.collections import CtyList, CtyMap, CtySet
    from pyvider.cty.types.structural import CtyTuple

    if vtype is not None:
        if isinstance(vtype, CtyList | CtyTuple):
            if not isinstance(content, int):
                raise AttributePathError(
                    f"{vtype.__class__.__name__} is indexed by integer, not by {content!r}"
                )
            return IndexStep(content)
        if isinstance(vtype, CtyMap | CtySet):
            return KeyStep(content)
        # Anything else (dynamic included) falls through to the syntactic
        # reading; the step's own apply_type reports the mismatch, with the
        # message it already words for that type.
    return IndexStep(content) if isinstance(content, int) else KeyStep(content)


def parse_path(path_str: str, within: CtyType[Any] | None = None) -> CtyPath:
    """Build a CtyPath from `path_str`, resolved against `within` when given."""
    from pyvider.cty.path.base import CtyPath, GetAttrStep

    steps: list[PathStep] = []
    current = within
    for kind, value in tokenize(path_str):
        step: PathStep = GetAttrStep(value) if kind == "attr" else _bracket_step(value, current)
        if current is not None:
            try:
                current = step.apply_type(current)
            except AttributePathError as exc:
                position = len(steps) + 1
                raise AttributePathError(f"Error at step {position} ({step}) in {path_str!r}: {exc}") from exc
        steps.append(step)
    return CtyPath(tuple(steps))


# 🌊🪢🔚
