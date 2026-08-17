#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The sweep's last missing population: one argument marked in turn.

Until 2026-08-17 not one of the 83 stdlib functions had ever been driven with a
marked argument against the live oracle. Mark behaviour was pinned by
hand-written tests citing go-cty's source -- correct as far as it went, but a
citation is a reading, and this branch's recurring lesson is that readings age.
The harness's value dialect can spell a mark at any depth (`{"$marks": [...],
"$value": ...}`), so the gap was never expressiveness; nothing had used it.

What this measures is the framework's whole mark policy at once: marks stripped
from parameters that do not declare `allow_marked`, the union re-applied to the
result, the implementation's own propagation where a parameter *does* declare
it, and the interaction with the unknown short-circuit -- which is where go-cty
drops a mark on the floor (`function.go:298` collects marks only from
non-`AllowMarked` parameters, and an unknown argument returns before the
implementation that would have carried them). Matching that exactly is the
point: a value this package keeps sensitive and Terraform does not is two
systems disagreeing about what is secret.

Marks are compared as the harness reports them -- the deep union, sorted --
because that is also how `Function.Call` itself treats them: nothing positional
survives a function call in go-cty either.

The argument table is imported, not copied, so this population is exactly as
broad as the sweep itself.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.compatibility.test_stdlib_sweep import (
    CASES,
    KNOWN_DIVERGENCES,
    Arg,
    _case_id,
    _go_result,
    _our_result,
)

pytestmark = pytest.mark.compat

MARK = "sensitive"

# Functions where every row diverges, with the reason. Strict xfails, same
# mechanism as the other populations: a fixed divergence turns its entry red.
BY_FUNCTION: dict[str, str] = {}

# Rows that diverge case by case.
BY_CASE: dict[str, str] = {}


def _marked_case_id(func: str, args: list[Arg]) -> str:
    return f"{_case_id(func, args)}//marked"


KNOWN_MARK_DIVERGENCES: dict[str, str] = {
    # A row that diverges on its known values diverges identically with one of
    # them marked -- unlike the unknown population, marking does not replace
    # the value that carries the divergence. Inherited so the six GB9c and
    # numeric-precision rows stay owned by the sweep's registry, not this one.
    **{
        _marked_case_id(func, args): KNOWN_DIVERGENCES[base_id]
        for func, args in CASES
        if (base_id := _case_id(func, args)) in KNOWN_DIVERGENCES
    },
    **{
        _marked_case_id(func, args): reason
        for func, args in CASES
        if (reason := BY_FUNCTION.get(func)) is not None
    },
    **BY_CASE,
}


def _marked_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """The same argument, marked, in the harness's dialect.

    A plain value wraps as `{"$marks": [...], "$value": ...}`. Arguments the
    table spells with the `null` or `unknown` flag have no `value` key to wrap,
    so they become the dialect's `$null` / `$unknown` sentinels inside the
    wrapper -- each pair of spellings builds the same Go value.
    """
    if spec.get("null"):
        return {"type": spec["type"], "value": {"$marks": [MARK], "$value": {"$null": True}}}
    if spec.get("unknown"):
        return {"type": spec["type"], "value": {"$marks": [MARK], "$value": {"$unknown": True}}}
    return {"type": spec["type"], "value": {"$marks": [MARK], "$value": spec["value"]}}


@pytest.mark.parametrize(("func", "args"), CASES, ids=[_case_id(func, args) for func, args in CASES])
def test_a_marked_argument_is_answered_the_same_way(func: str, args: list[Arg], request: Any) -> None:
    """Every argument of every case, marked in turn; kind, payload and marks."""
    case_id = _marked_case_id(func, args)
    if case_id in KNOWN_MARK_DIVERGENCES:
        request.node.add_marker(pytest.mark.xfail(reason=KNOWN_MARK_DIVERGENCES[case_id], strict=True))

    for position in range(len(args)):
        specs = [_marked_spec(spec) if i == position else spec for i, (_value, spec) in enumerate(args)]
        values = [
            value.with_marks({MARK}) if i == position else value for i, (value, _spec) in enumerate(args)
        ]

        theirs = _go_result(func, specs)
        ours = _our_result(func, values)

        where = f"{func} with argument {position} marked"
        assert ours[0] == theirs[0], (
            f"{where}: go-cty {theirs[0]} ({theirs[1]}), pyvider {ours[0]} ({ours[1]})"
        )
        if theirs[0] != "error":
            assert ours[1] == theirs[1], f"{where}: go-cty {theirs[1]}, pyvider {ours[1]}"
            assert ours[2] == theirs[2], f"{where} marks: go-cty {theirs[2]}, pyvider {ours[2]}"


# 🌊🪢🔚
