#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The soup-go harness, and the value dialect both implementations speak.

Three test modules had each grown their own copy of "find the binary", which is
the shape of divergence this repository keeps finding: the copies agreed today
and nothing made them agree tomorrow. They now share this one.

The rest of the module is the bridge that makes the non-stdlib half of go-cty
comparable at all. `cty call` can only say "unknown", "null" or "marked" about a
whole value, which is enough for a function's answer and not enough for
`UnknownAsNull`, `MarkWithPaths` or a refined unknown -- all of which exist
precisely to talk about depth. `rich()` writes a pyvider value in the harness's
richer dialect, and `canonical()` normalises both sides' numbers so a comparison
is comparing values rather than spellings.

Numbers travel as `{"$number": "<digits>"}` in this direction. A JSON float
would round through a float64 and lose precision above 2**53, which would make
the two implementations disagree about an argument neither of them chose.
"""

from __future__ import annotations

import base64
from decimal import Decimal
from functools import lru_cache
import json
import os
from pathlib import Path
import shutil
import subprocess  # nosec
from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyCapsule,
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.conversion import encode_cty_type_to_wire_json
from pyvider.cty.types import BytesCapsule
from pyvider.cty.values.markers import RefinedUnknownValue

__all__ = ["canonical", "dynamic_arg", "refinements", "rich", "run", "soup_go", "type_spec"]


REQUIRED_COMMANDS = frozenset(
    {
        # The stdlib oracle.
        "call",
        "functions",
        "unify",
        # The cty package itself, which no stdlib call reaches.
        "rich",
        "unknown-as-null",
        "marks",
        "conformance",
        "json",
        "range",
        "safe-known-prefix",
        "convert-value",
        "walk",
        "transform",
        "msgpack",
        "equals",
    }
)
"""Every `soup-go cty` subcommand this suite drives.

Doubles as the index of which go-cty surfaces are compared here at all: a
feature with no command in this list is a feature nothing checks.
"""


@lru_cache(maxsize=8)
def _commands(binary: str) -> frozenset[str]:
    """The `cty` subcommands a binary exposes, read from its own help output."""
    completed = subprocess.run(  # nosec
        [binary, "cty", "--help"], capture_output=True, text=True, check=False
    )
    found: set[str] = set()
    listing = False
    for line in completed.stdout.splitlines():
        if line.startswith("Available Commands:"):
            listing = True
            continue
        if listing:
            if not line.strip():
                break
            found.add(line.split()[0])
    return frozenset(found)


def soup_go() -> str:
    """The harness binary, or skip. Never silently passes without it.

    A binary that is *present but too old* fails rather than skips. That is the
    difference between "nothing was checked and it said so" and "something was
    checked against last week's go-cty" -- and the second has already happened
    here: `/tmp/soup-go` is the last-resort default, a developer running pytest
    directly picks it up, and a day-old copy answered "unknown function" to two
    thirds of the sweep while the suite reported a clean run.
    """
    candidate = os.environ.get("SOUP_GO_BIN") or shutil.which("soup-go") or "/tmp/soup-go"  # nosec
    if not Path(candidate).exists():
        pytest.skip(
            f"soup-go harness not found at {candidate}. Build it from "
            "tofusoup/src/tofusoup/harness/go/soup-go, or set SOUP_GO_BIN."
        )

    missing = sorted(REQUIRED_COMMANDS - _commands(candidate))
    if missing:
        raise AssertionError(
            f"the soup-go harness at {candidate} is out of date: it has no {', '.join(missing)}. "
            "Rebuild it from tofusoup/src/tofusoup/harness/go/soup-go, or point SOUP_GO_BIN at a "
            "current build. `make compat` rebuilds it for you."
        )
    return candidate


def run(*args: str) -> dict[str, Any]:
    """Run one harness command and parse its single JSON object.

    A non-zero exit is a failure here rather than a comparison result: the
    commands report go-cty's own refusals in the JSON as `ok: false`, so a
    process that died instead means the harness was misused or is broken, and
    reading that as "the implementations disagree" would point at the wrong
    code.
    """
    completed = subprocess.run(  # nosec
        [soup_go(), *args], capture_output=True, text=True, check=False
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"harness exited {completed.returncode} for {args!r}:\n{completed.stderr.strip()}"
        )
    try:
        # parse_int as well as parse_float: length bounds reach maxint, and a
        # number that arrives as a float has already lost the argument.
        return json.loads(completed.stdout, parse_float=Decimal, parse_int=Decimal)
    except json.JSONDecodeError as exc:  # pragma: no cover - a broken harness
        raise AssertionError(f"harness produced no JSON for {args!r}: {completed.stdout!r}") from exc


def type_spec(cty_type: CtyType[Any]) -> str:
    """A pyvider type in the harness's JSON type dialect.

    Delegates to the wire encoder rather than re-deriving the spelling, so a
    test writes its type once and both implementations are handed the same one.
    """
    if cty_type.equal(BytesCapsule):
        # A capsule type has no JSON spelling of its own; the harness accepts
        # this name for the one capsule both sides know about.
        return json.dumps("bytes")
    return json.dumps(encode_cty_type_to_wire_json(cty_type))


def rich(value: CtyValue[Any]) -> Any:
    """A pyvider value in the harness's rich dialect."""
    if value.marks:
        # unmark() returns the value *and* the marks it removed, so the value
        # is the first half of the pair rather than the whole answer.
        unmarked, marks = value.unmark()
        return {"$marks": sorted(str(mark) for mark in marks), "$value": rich(unmarked)}
    if value.is_unknown:
        payload: dict[str, Any] = {"$unknown": True}
        refined = refinements(value)
        if refined:
            payload["$refine"] = refined
        return payload
    if value.is_null:
        return {"$null": True}
    return _rich_known(value)


def dynamic_arg(value: CtyValue[Any]) -> Any:
    """A value for a position whose declared type is `dynamic`.

    The concrete type has to travel with it. Sent as a plain rich value, the
    harness infers a type from the JSON -- and JSON infers a *tuple* from an
    array -- so a list arrived as a tuple and the operation under test was
    handed a different value from the one the test wrote.
    """
    inner = value.value if isinstance(value.type, CtyDynamic) and isinstance(value.value, CtyValue) else value
    return {"$dynamic": {"type": json.loads(type_spec(inner.type)), "value": rich(inner)}}


def _rich_known(value: CtyValue[Any]) -> Any:
    cty_type = value.type
    match cty_type:
        case CtyDynamic():
            inner = value.value
            return rich(inner) if isinstance(inner, CtyValue) else inner
        case CtyString():
            return str(value.value)
        case CtyBool():
            return bool(value.value)
        case CtyNumber():
            return {"$number": _number_text(value.value)}
        case CtyList() | CtyTuple():
            return [rich(element) for element in value.value]
        case CtySet():
            # Sorted the way the codec sorts, because that order is the answer:
            # a set's element order reaches the wire and go-cty's iteration
            # order is what the harness reports back.
            elements = sorted(value.value, key=lambda element: element._canonical_sort_key())
            return [rich(element) for element in elements]
        case CtyMap() | CtyObject():
            return {name: rich(element) for name, element in value.value.items()}
        case CtyCapsule() if cty_type.equal(BytesCapsule):
            return {"$bytes": base64.b64encode(value.value).decode()}
    raise AssertionError(f"no rich encoding for {cty_type}")


def _number_text(number: Any) -> str:
    """Exact digits, never an exponent.

    `format(d, "f")` is what keeps 1E+2 and 100 the same argument on both sides.
    """
    decimal = Decimal(str(number))
    if decimal.is_infinite():
        return "Infinity" if decimal > 0 else "-Infinity"
    return format(decimal, "f")


def _bound_text(number: Any) -> str:
    """A number bound's digits the way Go's `Text('f', -1)` writes them.

    `_number_text` keeps whatever trailing zeros a Decimal carries, which is
    right for a *value* -- the wire transmits what was written -- and wrong for
    a bound, where the harness has already reduced 1.50 to 1.5 and the two would
    compare unequal while describing the same bound.
    """
    return format(Decimal(str(number)).normalize(), "f")


GO_MAXINT = 2**63 - 1
"""`math.MaxInt` on the 64-bit builds the harness is compiled for.

An unrefined unknown collection in go-cty already reports this as its length
upper bound, so the harness treats it as "no bound" and omits it.
"""


def refinements(value: CtyValue[Any]) -> dict[str, Any]:
    """What is known about an unknown, in the harness's spelling.

    Public because the stdlib sweep needs it too: an unknown answer is only
    comparable with go-cty's if the refinements come with it.

    Normalised towards the harness rather than the other way round. The harness
    reads go-cty's own `Value.Range()`, so its spelling *is* go-cty's answer and
    ours is the side that has to match. Three differences between this and
    `encodeRefinements` were spellings rather than facts, and all three are
    settled here:

      * a length lower bound of 0, and an upper bound of maxint, are what an
        unrefined unknown collection already says. `encodeRefinements` omits
        both (`lower != 0`, `upper != math.MaxInt`), so emitting them would
        report as a refinement something go-cty does not consider one.
      * an infinite number bound is the absence of a bound, and is omitted
        there too (`!bound.AsBigFloat().IsInf()`).
      * a bound's digits come from Go's `Text('f', -1)`, the shortest form that
        round-trips. See `_bound_text`.

    Nothing else is smoothed over. `is_known_null: true` in particular stays as
    it is: go-cty cannot produce it, because refining an unknown as null yields
    an actual null value, so this saying it would be a difference in behaviour
    rather than in spelling and is exactly what the comparison should catch.
    """
    raw = value.value
    if not isinstance(raw, RefinedUnknownValue):
        return {}
    out: dict[str, Any] = {}
    if raw.is_known_null is not None:
        out["is_known_null"] = raw.is_known_null
    if raw.string_prefix:
        out["string_prefix"] = raw.string_prefix
    for key, bound in (
        ("number_lower_bound", raw.number_lower_bound),
        ("number_upper_bound", raw.number_upper_bound),
    ):
        if bound is None or Decimal(str(bound[0])).is_infinite():
            continue
        out[key] = [_bound_text(bound[0]), bound[1]]
    if raw.collection_length_lower_bound not in (None, 0):
        out["collection_length_lower_bound"] = raw.collection_length_lower_bound
    if raw.collection_length_upper_bound not in (None, GO_MAXINT):
        out["collection_length_upper_bound"] = raw.collection_length_upper_bound
    return out


def canonical(payload: Any) -> Any:
    """Both spellings of a number become a Decimal.

    The harness writes numbers as JSON tokens and `rich()` writes them as
    `{"$number": ...}`, which are the same number written two ways. Without
    this, every comparison would fail on the spelling and none of them would be
    about behaviour.
    """
    match payload:
        case bool():
            return payload
        case {"$number": str() as text}:
            return Decimal(text)
        case dict():
            return {key: canonical(item) for key, item in payload.items()}
        case list():
            return [canonical(item) for item in payload]
        case Decimal() | int() | float():
            return Decimal(str(payload))
    return payload


# 🌊🪢🔚
