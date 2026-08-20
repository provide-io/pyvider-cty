#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The traversal surfaces' shared vocabulary: paths, visits, and the rewrites.

`test_walk_oracle` and `test_mark_paths_oracle` had each grown their own copy of
"a pyvider path step in the harness's structural form", and the copies had
already drifted -- one normalised a map key's number and the other left it to
the call site. That is the same divergence-by-copy `_oracle.py` was made to end
for "find the binary", so these live in one place too, and
`test_traversal_properties` generates against exactly the vocabulary the
table-driven modules use.

`transform` cannot take a function over a command line, so both sides implement
the same two rewrites by name. That is a real constraint on what can be checked
and it is stated rather than worked around: the comparison is of *how the
traversal rebuilds*, with the rewrite held fixed.
"""

from __future__ import annotations

from decimal import Decimal
import json
from typing import Any

from pyvider.cty import CtyDynamic, CtyString, CtyType, CtyValue
from pyvider.cty._unicode.case import simple_upper
from pyvider.cty.conversion.explicit import _without_optional
from pyvider.cty.path import GetAttrStep, IndexStep, KeyStep
from tests.compatibility._oracle import canonical, dynamic_arg, rich, run, type_spec

__all__ = [
    "REWRITES",
    "implied_type",
    "mark_paths_here",
    "ordered",
    "payload",
    "step_form",
    "subject",
    "traversal_answer",
    "visit_form",
]


def step_form(step: Any) -> Any:
    """One pyvider path step in the harness's structural form.

    Structural rather than a display string: go-cty spells a map key as an index
    step holding a string and this library has a distinct `KeyStep`, so comparing
    the two renderings would compare spelling conventions instead of locations.
    """
    match step:
        case GetAttrStep(name=name):
            return {"attr": name}
        case IndexStep(index=index):
            return {"index": Decimal(index)}
        case KeyStep(key=key):
            return {"index": canonical(rich(key)) if isinstance(key, CtyValue) else key}
    raise AssertionError(f"no structural form for {step!r}")


def implied_type(cty_type: CtyType[Any]) -> Any:
    """A type as go-cty's `ImpliedType()` spells it: no optional attributes.

    Optionality is a property of a type used as a *constraint*, and go-cty drops
    it when a value is built -- everything crossing the provider protocol is
    marshalled with `ImpliedType()`, which strips optional attributes
    recursively, so the type a provider receives has none at all. This library
    keeps the record on the type object, so an un-stripped comparison asks
    go-cty about something its values cannot carry, and every generated object
    with an optional attribute read as a divergence in the result type.
    """
    return json.loads(type_spec(_without_optional(cty_type)))


def visit_form(path: Any, value: CtyValue[Any]) -> dict[str, Any]:
    """One visit -- where the walk was, what it found, and at what type."""
    return {
        "path": [step_form(step) for step in path.steps],
        "value": canonical(rich(value)),
        "type": implied_type(value.type),
    }


def payload(cty_type: CtyType[Any], value: CtyValue[Any]) -> str:
    """One value as the harness reads it, at the type the caller declared.

    A `dynamic` position has to carry its concrete type explicitly: the harness
    infers the type from the JSON, and JSON infers a *tuple* from an array, so a
    `list(string)` would arrive as `tuple(string, string)` and the traversal
    under test would be handed a different value from the one generated.
    """
    if isinstance(cty_type, CtyDynamic):
        return json.dumps(dynamic_arg(value))
    return json.dumps(rich(value))


def subject(cty_type: CtyType[Any], value: CtyValue[Any]) -> CtyValue[Any]:
    """The value the harness is actually traversing, on this side too.

    `DynamicPseudoType` is a type *constraint* in go-cty and never survives into
    a value: a dynamic position holds a concrete `cty.String`, and go-cty's walk
    reports that concrete type at the root. This library keeps a wrapper instead,
    so a dynamic position can carry its own type across the wire, and `payload`
    below unwraps it before sending -- which means the harness is handed the
    inner value while an un-unwrapped comparison would traverse the outer one.
    Comparing those is comparing two different values, and it read as a
    divergence in the root visit's type on this suite's first run.

    Only the envelope is removed; the traversal underneath is compared in full.
    """
    if isinstance(cty_type, CtyDynamic) and isinstance(value.value, CtyValue):
        return value.value
    return value


def traversal_answer(
    command: str, cty_type: CtyType[Any], value: CtyValue[Any], *extra: str
) -> dict[str, Any]:
    """go-cty's answer for one traversal command, or a failure with its reason."""
    result = run("cty", command, "--type", type_spec(cty_type), payload(cty_type, value), *extra)
    assert result["ok"], result
    return result


def ordered(entries: Any) -> list[str]:
    """Entries as sorted, key-order-independent strings.

    Comparing the dicts directly compares their key insertion order, which is a
    property of how each side happened to build them and not of where the marks
    were found.
    """
    return sorted(json.dumps(entry, sort_keys=True, default=str) for entry in entries)


def mark_paths_here(value: CtyValue[Any]) -> list[str]:
    """Where this library says the marks are, in the harness's vocabulary."""
    from pyvider.cty.mark_paths import unmark_deep_with_paths

    _, found = unmark_deep_with_paths(value)
    return ordered(
        {
            "path": [step_form(step) for step in path.steps],
            "marks": sorted(str(mark) for mark in marks),
        }
        for path, marks in found.items()
    )


def _upper(_path: Any, value: CtyValue[Any]) -> CtyValue[Any]:
    """Uppercase a known, non-null string, keeping its marks.

    `simple_upper`, not `str.upper()`. Go's `strings.ToUpper` maps one code
    point at a time and Python's applies full case mapping, so `\ufb01` -- the
    `fi` ligature -- is left alone there and expands to `FI` here. This rewrite
    used `str.upper()` and the difference was invisible for as long as the cases
    were hand-written, because nobody writes a ligature into a table. The
    generated population produced one on its first wide run, and it read as a
    `transform` divergence when `transform` was doing its job: the library's own
    `upper` has always gone through `simple_upper`.
    """
    if not isinstance(value.type, CtyString) or value.is_null or value.is_unknown:
        return value
    return CtyString().validate(simple_upper(str(value.value))).with_marks(value.marks)


def _unknown_to_null(_path: Any, value: CtyValue[Any]) -> CtyValue[Any]:
    if not value.is_unknown:
        return value
    return CtyValue.null(value.type).with_marks(value.marks)


REWRITES = {"upper": _upper, "unknown-to-null": _unknown_to_null}


# 🌊🪢🔚
