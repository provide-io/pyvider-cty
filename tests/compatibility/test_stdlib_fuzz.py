#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Generated arguments for every stdlib function, answered by real go-cty.

The last surface no generated input had ever reached. `test_stdlib_sweep` drives
all 83 functions against 444 hand-written argument rows -- an average of five
each, with 31 functions holding two or fewer and `log` holding one -- and a
hand-written row can only find a divergence somebody already suspected. Every
divergence found on 2026-08-19 came from pointing generated inputs at a surface
that had only ever seen chosen ones: seventeen in `unify`, and set ordering,
vacuous refinements, the dynamic envelope and NaN in the codecs.

`SIGNATURES` is what makes this cheap. Each function declares its parameters,
its variadic one and its null/unknown/dynamic policy, so for half the surface
the argument list is *derived* rather than written; the other half declares a
`dynamic` parameter and gets a shaped plan in `_fuzz_plans`. Either way the
values are generated, and the same generated value drives both implementations,
so the two cannot be handed different arguments by a mistake in this file.

**There is no known-divergence list here, on purpose.** A generated case has no
stable id to key one by, so an accepted divergence has to be excluded from
*generation* instead -- and each exclusion is written down where the generator
makes it, with the sweep row that pins the divergence it avoids. The rule that
keeps that honest is the coverage guard at the bottom: a plan that generates
nothing a function will answer fails, so narrowing a generator until it stops
finding anything is not a way to make this suite pass.

**What is compared is the value, not the bytes**, and that is a different
question from the one `test_stdlib_sweep` asks. The harness reports a result
through `ctyjson.Marshal`, so go's side of a comparison is JSON while this
package's is msgpack -- and the two codecs make different choices about the same
number. The sweep reads that asymmetry as a divergence, which is right for the
432 rows it holds and wrong for a generator: `abs(2**63)` reports as go's JSON
integer against this package's msgpack *text*, while the two write byte-identical
msgpack. That is the comparison channel inventing a divergence, and it shrank
four functions onto the same non-bug on this suite's first run. So both answers
are normalised with `canonical` before comparing, and where go-cty falls back to
msgpack -- a container holding an unknown, which JSON cannot express -- the two
encodings are compared as bytes, which is exact.

Nothing is lost by that division: `test_differential_properties` compares the
msgpack of generated *values* in both directions, so the byte question is asked
where it can be answered for both sides, and the one function whose bytes
genuinely differ (`pow`, whose float64-derived answer go-cty writes as a float64
and this package writes as text) is pinned by a sweep row.
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any

from hypothesis import HealthCheck, given, settings, strategies as st
import pytest

from pyvider.cty import CtyValue
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.functions import SIGNATURES, STDLIB
from pyvider.cty.marks import unmark_deep
from pyvider.cty.types import BytesCapsule
from tests.compatibility._fuzz_plans import DERIVED, PLANS, arguments_for
from tests.compatibility._oracle import canonical, refinements, rich, type_spec
from tests.compatibility.test_stdlib_sweep import reported

pytestmark = pytest.mark.compat

FUNCTIONS = sorted(SIGNATURES)


def _examples(default: int) -> int:
    """`PYVIDER_COMPAT_EXAMPLES=200 make compat` widens every function at once.

    The committed default is one subprocess per example per function, which is
    what keeps the whole differential suite in the seconds it is today. Finding
    a *new* divergence generally means running wider than a regression guard
    needs to.
    """
    override = os.environ.get("PYVIDER_COMPAT_EXAMPLES")
    return max(1, int(override)) if override else default


EXAMPLES = _examples(20)
# Draws per function in the coverage guard below, and the loop stops at the
# first answer, so a healthy plan costs one harness call.
#
# Forty rather than six, and each from a **fresh** strategy. `example()` fills a
# pool once per strategy object and then samples it, so repeated draws from the
# module-level plan objects are correlated -- which is how `concat` failed this
# guard once on a plan that answers most of the time. A fresh strategy per draw
# makes them independent.
#
# The count is high because it is nearly free: the loop stops at the first
# answer, so a healthy plan costs one harness call and only a genuinely broken
# one pays for all forty. Measured across all 83 plans, the least likely to
# answer is `tobool` at three draws in ten, which puts a false failure at
# 0.7**40 -- about one run in a million.
COVERAGE_DRAWS = 40


def _spec(value: CtyValue[Any]) -> dict[str, Any]:
    """One argument in the harness's dialect, carrying its own concrete type.

    `rich` rather than the flat `"null"`/`"unknown"` flags, because those can
    only speak about a whole argument: a list holding one unknown element is the
    ordinary plan-time shape and the flags cannot spell it. The type travels
    explicitly for the same reason `dynamic_arg` exists -- JSON infers a *tuple*
    from an array, so an inferred list would be a different argument.
    """
    return {"type": json.loads(type_spec(value.type)), "value": rich(value)}


def _describe(func: str, args: list[CtyValue[Any]]) -> str:
    """A failing call, spelled so it can be replayed against the harness."""
    rendered = " ".join(json.dumps(_spec(value)) for value in args)
    return f"soup-go cty call {func} {rendered}"


Answer = tuple[str, Any, list[str]]


def _theirs(func: str, args: list[CtyValue[Any]]) -> Answer:
    """go-cty's answer as (kind, payload, marks).

    `bytes` is its own kind rather than a flavour of `ok`: it means go-cty
    answered something `ctyjson.Marshal` cannot spell -- a container holding an
    unknown -- and that answer can only be compared as an encoding.
    """
    answer = reported(func, [_spec(value) for value in args])
    marks = sorted(answer.get("marks") or [])
    if not answer.get("ok"):
        return "error", answer.get("error", ""), marks
    if answer.get("unknown"):
        return "unknown", (answer.get("type"), canonical(answer.get("refine") or {})), marks
    if answer.get("null"):
        return "null", answer.get("type"), marks
    if "msgpack" in answer:
        return "bytes", (answer.get("type"), base64.b64decode(answer["msgpack"]).hex()), marks
    return "ok", (answer.get("type"), canonical(answer.get("value"))), marks


def _ours(func: str, args: list[CtyValue[Any]], *, as_bytes: bool) -> Answer:
    """The same call answered here, spelled the way go-cty spelled its own."""
    try:
        marked = STDLIB[func](*args)
    except Exception as exc:  # noqa: BLE001 - any refusal is "error" for this comparison
        return "error", f"{type(exc).__name__}: {exc}", []
    result, mark_set = unmark_deep(marked)
    marks = sorted(mark if isinstance(mark, str) else str(mark) for mark in mark_set)
    # A capsule has no wire spelling on either side -- go-cty refuses to marshal
    # one at all -- so both ends name it the way the harness does.
    wire_type = "bytes" if result.type.equal(BytesCapsule) else result.type._to_wire_json()
    if result.is_unknown:
        return "unknown", (wire_type, canonical(refinements(result))), marks
    if result.is_null:
        return "null", wire_type, marks
    if result.type.equal(BytesCapsule):
        return "ok", ("bytes", base64.b64encode(result.value).decode()), marks
    if as_bytes:
        return "bytes", (wire_type, cty_to_msgpack(result, result.type).hex()), marks
    return "ok", (wire_type, canonical(rich(result))), marks


def _compare(func: str, args: list[CtyValue[Any]]) -> None:
    """One generated call, asked of both implementations.

    Both refusing counts as agreement -- the messages differ between a Go and a
    Python implementation and pinning their wording would test translation
    rather than behaviour. Everything else is compared in full: the kind of
    answer, the value, and the marks.
    """
    theirs = _theirs(func, args)
    ours = _ours(func, args, as_bytes=theirs[0] == "bytes")
    where = _describe(func, args)

    assert ours[0] == theirs[0], f"{where}\n  go-cty {theirs[0]} ({theirs[1]}), pyvider {ours[0]} ({ours[1]})"
    if theirs[0] != "error":
        assert ours[1] == theirs[1], f"{where}\n  go-cty {theirs[1]!r}, pyvider {ours[1]!r}"
        assert ours[2] == theirs[2], f"{where}\n  marks: go-cty {theirs[2]}, pyvider {ours[2]}"


@pytest.mark.parametrize("func", FUNCTIONS)
@settings(max_examples=EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(data=st.data())
def test_a_generated_call_is_answered_the_same_way(func: str, data: st.DataObject) -> None:
    """Every function, on arguments neither implementation chose."""
    _compare(func, data.draw(arguments_for(func), label="arguments"))


def _fresh(strategy: Any) -> Any:
    """A distinct strategy object drawing from the same plan.

    `example()` fills a pool once **per strategy object** and then samples it,
    and the plans are module-level, so twelve draws from one of them are twelve
    samples of one pool rather than twelve independent draws. Mapping through
    the identity is the cheapest way to get a new object with exactly the same
    distribution, and it is what makes the count below mean what it says.
    """
    return strategy.map(lambda drawn: drawn)


@pytest.mark.filterwarnings("ignore::hypothesis.errors.NonInteractiveExampleWarning")
def test_every_plan_reaches_the_function_it_plans_for() -> None:
    """Coverage, measured rather than assumed.

    A generator that only ever produces arguments go-cty refuses would make this
    whole module pass while testing nothing about any function -- which is the
    exact failure the sweep's own coverage guard exists to catch, and the reason
    narrowing a plan is not a way out of a divergence. Every plan has to produce
    at least one call go-cty actually answers.

    Drawn with `example()` rather than under `@given`, which is the one place in
    this suite that is right. Inside `@given` hypothesis hands out its *minimal*
    values first, and the minimum of most of these plans is degenerate -- an
    empty list to `element`, an empty string to `tonumber` -- so ten plans that
    reach their function perfectly well reported as never reaching it. What this
    test asks is whether the plan's population contains an answerable call, and
    a random sample is the way to ask that.
    """
    silent = []
    for func in FUNCTIONS:
        answered = any(
            _theirs(func, _fresh(arguments_for(func)).example())[0] != "error" for _ in range(COVERAGE_DRAWS)
        )
        if not answered:
            silent.append(func)

    assert not silent, f"these plans never produced a call go-cty would answer: {silent}"


def test_every_function_is_planned_for() -> None:
    """No function may fall off this suite by being added to another one."""
    unplanned = set(SIGNATURES) - set(PLANS) - set(DERIVED)

    assert not unplanned, unplanned
    assert not (set(PLANS) - set(SIGNATURES)), (
        f"plans for functions that do not exist: {set(PLANS) - set(SIGNATURES)}"
    )


# 🌊🪢🔚
