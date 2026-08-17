#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The sweep's missing population: one argument wholly unknown.

`test_stdlib_sweep.py` drives three shapes of argument and, until this module,
only three. Everything known; a *container* holding an unknown element, which is
the plan-time shape a resource attribute actually has; and each argument nulled
in turn. None of them is a wholly unknown argument, and that is the only
population that reaches the code go-cty runs *instead of* a function's
implementation: `Function.Call` short-circuits on an unknown it was not told to
accept, and on the way out applies the function's `RefineResult` callback to say
what is known about the answer anyway.

That callback is the whole point. go-cty's stdlib declares 75 of them, and the
difference between "unknown" and "unknown, and not null, and at least zero" is
one Terraform acts on: a refined unknown can be compared, counted and sometimes
decided without waiting for apply. A comparison that never drives a wholly
unknown argument never sees any of it, and this sweep never did: on the day this
module was written 251 of its 304 case rows disagreed, and nothing in the suite
could say so.

Split out of `test_stdlib_sweep.py` rather than added to it because that file is
already past the 500-line mark this repository keeps test files under. The
argument table is imported, not copied, so this population is exactly as broad as
the sweep itself and cannot drift away from it.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import CtyValue
from tests.compatibility.test_stdlib_sweep import (
    CASES,
    Arg,
    _case_id,
    _go_result,
    _our_result,
)

pytestmark = pytest.mark.compat


def _render_type(spec: Any) -> str:
    """The harness's JSON type spec without its quotes: `["list","string"]` -> `list(string)`."""
    match spec:
        case str():
            return spec
        case dict():
            return "{" + ",".join(f"{name}:{_render_type(item)}" for name, item in spec.items()) + "}"
        case [kind, element]:
            return f"{kind}({_render_type(element)})"
    raise AssertionError(f"no rendering for type spec {spec!r}")


def _unknown_case_id(func: str, args: list[Arg]) -> str:
    """The sweep's case id, with each argument's type spelled out after it.

    `_case_id` alone renders only the values, and for this population that is not
    enough to *name* a case. `tobool` is driven with both the string "1" and the
    number 1, which render identically, and go-cty answers a wholly unknown
    string with an unknown bool but a wholly unknown number with a refusal --
    five ids in the table collide this way. One id for two cases with opposite
    outcomes means one divergence entry covering both, and it is then wrong for
    one of them whichever reason it gives.
    """
    return f"{_case_id(func, args)} :: {','.join(_render_type(spec['type']) for _value, spec in args)}"


CASE_IDS = [_unknown_case_id(func, args) for func, args in CASES]


# Functions where *every* case row diverges at *every* argument position. Listed
# by name rather than case by case because that is the shape of the gap and the
# shape of the fix: a `RefineResult` is declared once per function, and the day
# one is declared here every row of that function turns XPASS-strict and this
# entry has to go. A function that becomes partly fixed forces the same edit,
# only into BY_CASE below.
#
# Empty. It held 65 names when this module was written -- effectively every
# function in the sweep -- and emptied as the migration onto go-cty's function
# framework landed. Both halves are kept because the next `RefineResult` written
# by hand instead of by the framework belongs in one of them.
BY_FUNCTION: dict[str, str] = {}

# Functions where only some rows diverge, named case by case. A blanket entry
# would mark the rows that already agree as expected failures, and they would
# then XPASS and fail -- so these have to be spelled out however long the list.
BY_CASE: dict[str, str] = {}

KNOWN_DIVERGENCES: dict[str, str] = {
    **{
        _unknown_case_id(func, args): reason
        for func, args in CASES
        if (reason := BY_FUNCTION.get(func)) is not None
    },
    **BY_CASE,
}


@pytest.mark.parametrize(("func", "args"), CASES, ids=CASE_IDS)
def test_a_wholly_unknown_argument_is_answered_the_same_way(func: str, args: list[Arg], request: Any) -> None:
    """Every argument of every case, replaced in turn by an unknown of its own type.

    The argument table is reused rather than hand-written, so this is exactly as
    broad as the sweep itself -- the same reason the nulled-argument test reuses
    it. What it adds is the population nothing else covers. An unknown *element*
    inside a known container leaves the container known, so a function still runs
    its implementation; a wholly unknown argument does not, and go-cty answers
    from `Function.Call` alone: the return type `returnTypeForValues` computed,
    plus whatever the function's `RefineResult` callback knows about a result it
    has not computed.

    The first run of this shape found 251 of 304 case rows disagreeing, and
    almost all of it was one thing missing: go-cty said "unknown, and definitely
    not null" where this package said "unknown". A refined unknown is not a
    courtesy -- Terraform can compare, count and sometimes decide on one without
    waiting for apply -- so answering less is answering differently, and the
    sweep called the two identical for as long as it compared only the *kind* of
    an unknown answer.

    That list is gone, spent on the migration onto go-cty's function framework,
    which is what it was written to specify. It emptied in two steps and the
    second is worth keeping: once every function refined its result, sixteen
    argument positions across six functions refined one go-cty leaves bare.
    `Function.Call` applies `RefineResult` only `if val.IsKnown() || val.Type()
    != cty.DynamicPseudoType` -- a value whose *type* is undecided cannot be
    promised anything, because the promise would have to hold for whatever type
    it turns out to be -- and `regex`, `csvdecode`, `concat`, `merge`, `flatten`
    and `coalescelist` all reach that state by their own route. The framework now
    gates on the result rather than on the arguments, and they agree.
    """
    case_id = _unknown_case_id(func, args)
    if case_id in KNOWN_DIVERGENCES:
        # A marker rather than pytest.xfail(), for the reason the sweep gives:
        # the body has to run for a fixed divergence to XPASS and, being strict,
        # fail. This list is the specification for the refinement work, so it has
        # to shrink as that work lands rather than quietly outlive it.
        request.node.add_marker(pytest.mark.xfail(reason=KNOWN_DIVERGENCES[case_id], strict=True))

    for position in range(len(args)):
        specs = [
            {"type": spec["type"], "unknown": True} if i == position else spec
            for i, (_value, spec) in enumerate(args)
        ]
        values = [
            CtyValue.unknown(value.type) if i == position else value for i, (value, _spec) in enumerate(args)
        ]

        theirs = _go_result(func, specs)
        ours = _our_result(func, values)

        where = f"{func} with argument {position} wholly unknown"
        assert ours[0] == theirs[0], (
            f"{where}: go-cty {theirs[0]} ({theirs[1]}), pyvider {ours[0]} ({ours[1]})"
        )
        if theirs[0] != "error":
            assert ours[1] == theirs[1], f"{where}: go-cty {theirs[1]}, pyvider {ours[1]}"
            assert ours[2] == theirs[2], f"{where} marks: go-cty {theirs[2]}, pyvider {ours[2]}"


def test_every_case_has_an_id_of_its_own() -> None:
    """No two rows may share an id, or one xfail entry would cover both.

    The guard is here rather than assumed because the sweep's own ids do collide
    -- five of them -- and a divergence list keyed on a colliding id is a list
    that says something untrue about one of the cases it names.
    """
    duplicated = sorted({case_id for case_id in CASE_IDS if CASE_IDS.count(case_id) > 1})

    assert not duplicated, f"case ids shared by more than one row: {duplicated}"


def test_the_known_divergence_list_is_not_stale() -> None:
    """Every entry must name something that still exists, and name it once.

    A stale entry silently stops covering anything, and a case named twice --
    once by its function and once by itself -- lets the second reason win without
    saying so.
    """
    ids = set(CASE_IDS)
    functions = {func for func, _args in CASES}

    assert not (BY_FUNCTION.keys() - functions), (
        f"BY_FUNCTION names functions the sweep no longer drives: {BY_FUNCTION.keys() - functions}"
    )
    assert not (BY_CASE.keys() - ids), (
        f"BY_CASE names cases that no longer exist: {sorted(BY_CASE.keys() - ids)}"
    )
    named_twice = sorted(
        _unknown_case_id(func, args)
        for func, args in CASES
        if func in BY_FUNCTION and _unknown_case_id(func, args) in BY_CASE
    )
    assert not named_twice, f"cases named by both BY_FUNCTION and BY_CASE: {named_twice}"


# 🌊🪢🔚
