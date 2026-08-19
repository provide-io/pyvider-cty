#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Every stdlib function the oracle exposes, compared against real go-cty.

`test_stdlib_oracle.py` pins specific behaviours a fix established, one
hand-written case at a time. This is the other shape: one compact table, broad
rather than deep, whose job is to *find* divergences rather than to hold known
ones in place.

It exists because that is how the last two were found. An external reviewer
caught `regexreplace` by looking past the branch diff at code the parity work
had never touched; a throwaway sweep in the same spirit then turned up six more
in 46 calls, including `values` returning a map's values in insertion order
where `keys` returned them sorted -- so `zipmap(keys(m), values(m))` silently
paired every value with the wrong key.

Each case is written once and drives both implementations, so the two cannot
drift apart in the test itself. Divergences that are known and not yet fixed
are listed in `KNOWN_DIVERGENCES` as strict xfails: fixing one makes its entry
fail, which is what forces the list to shrink rather than rot.

The table itself lives next door. It had grown to twice this repository's
500-line ceiling for a test file, and it is data rather than driver: the
argument builders are in `_sweep_args`, the rows in `_sweep_cases_scalar` and
`_sweep_cases_collection`. Adding a row is still one line, in whichever of the
two halves it belongs to.
"""

from __future__ import annotations

import base64
from decimal import Decimal
import json
import subprocess  # nosec
from typing import Any

import msgpack
import pytest

from pyvider.cty import CtyValue
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.functions import STDLIB
from pyvider.cty.marks import unmark_deep
from pyvider.cty.types import BytesCapsule
from tests.compatibility._oracle import refinements as _refinements, soup_go
from tests.compatibility._sweep_args import Arg
from tests.compatibility._sweep_cases_collection import COLLECTION_CASES
from tests.compatibility._sweep_cases_scalar import SCALAR_CASES

pytestmark = pytest.mark.compat

CASES: list[tuple[str, list[Arg]]] = [*SCALAR_CASES, *COLLECTION_CASES]


# Divergences that are real, reproduced, and not yet fixed. Strict xfails, so
# that fixing one turns its entry red and forces it out of this list. Each entry
# is a case id and why it is still here.
KNOWN_DIVERGENCES: dict[str, str] = {
    # The Unicode versions differ, and this is the one string in the sweep where
    # that is observable. GB9c -- the Indic conjunct rule, which holds
    # `Consonant Linker Consonant` together as one cluster -- was added in
    # Unicode 15.1. This package's tables are 16.0.0, so `\u0915\u094d\u0937` is one character
    # here. go-cty's `cty/internal/graphemes` selects `go-textseg` v15 or v17 by
    # *Go toolchain version*, and the oracle is built with go1.26, which takes
    # the `!go1.27` branch and therefore v15 -- Unicode 15.0, before GB9c. So it
    # answers two.
    #
    # Deliberately not matched. 15.0 is the outlier: 15.1, 16 and 17 all have
    # GB9c, and go-cty already carries the v17 that agrees with us. Implementing
    # a superseded rule set to match one build of the oracle would bake in
    # something we would have to take back out. These entries are strict xfails,
    # so rebuilding the oracle on go1.27 makes them XPASS and forces them out --
    # which is the correct end state arriving on its own.
    "strlen(\u0915\u094d\u0937)": "GB9c: Unicode 16.0.0 here, 15.0 in the oracle's go-textseg v15",
    "strrev(\u0915\u094d\u0937)": "GB9c: Unicode 16.0.0 here, 15.0 in the oracle's go-textseg v15",
    "substr(\u0915\u094d\u0937,0,1)": "GB9c: Unicode 16.0.0 here, 15.0 in the oracle's go-textseg v15",
    "format(%.1s,\u0915\u094d\u0937)": "GB9c: Unicode 16.0.0 here, 15.0 in the oracle's go-textseg v15",
    # The numeric precision model differs where go-cty computes in a big.Float:
    # a non-terminating quotient comes back with 155 significant digits against
    # Decimal's 28-digit default context. Neither is a wrong answer.
    #
    # **Closed as a decision on 2026-08-18, not left open.** Matching it is a
    # representation change rather than a precision setting -- go-cty's answer
    # ends ...335 because it is a 512-bit *binary* float printed exactly, and a
    # decimal division ends ...333 at any precision -- so it costs a new
    # dependency and a rewrite of CtyValue's payload. Measured the same day:
    # nothing in the workspace consumes this function, and pyvider-components
    # implements its own `divide` rather than delegating. Reopen on evidence of
    # a real provider being bitten.
    #
    # `pow(2, 0.5)` used to sit here on the same reasoning and did not belong.
    # go-cty computes `pow` in float64, so its 17 digits are not a rounder
    # version of the answer this package gave -- they *are* the answer, and being
    # more precise than it was a different function. `pow` is transcribed through
    # float64 now, and the rows above pin the three ways that changes things.
    "divide(1,3)": "numeric precision model: go-cty big.Float 155 digits, Decimal 28",
    # The *width* half of the same representation gap, and it is not about
    # computing anything. go-cty renders a number with `big.Float.Text('f', -1)`
    # -- the shortest decimal that reads back as the same 512-bit float -- so it
    # can spell floor(512 * log10 2) = 154 significant digits and writes zeros
    # past them. A Decimal spells every digit it holds.
    #
    # Measured 2026-08-19, and the boundary is exact: 5**220 is 154 significant
    # digits and agrees, 5**221 is 155 and is the first that cannot. Magnitude
    # is not what decides it -- 10**500 is 501 digits, one of them significant,
    # and agrees. Renders through the same route as `tostring` here: `convert`,
    # `format("%s")`, `jsonencode` and the cty/json codec.
    #
    # Same closed decision as `divide` above: matching it means holding numbers
    # as a 512-bit binary float rather than a Decimal. Until 2026-08-19 the
    # threshold was **28** digits rather than 154, which was a genuine bug --
    # `2**100` reached Terraform state as ...205000 -- and that half is fixed.
    "tostring(29673649205499371085853882092381116106940518230062328019624312471340650720765034871978496661785667500290711353088009272216396539079141803085803985595703125)": (
        "number width: go-cty's 512-bit big.Float spells 154 significant digits, Decimal spells all 155"
    ),
    # The calendar range. Go's time.Time runs to year 292277026596; Python's
    # datetime stops at 9999, so go-cty answers 10000-01-01T00:59:59Z where this
    # refuses. Accepted as a divergence 2026-08-18 rather than fixed: matching it
    # means replacing datetime with an integer nanosecond count plus civil
    # calendar conversion, and no Terraform expression can reach the boundary --
    # `timestamp()` cannot produce a year near it.
    #
    # The *shape* of the refusal was fixed. datetime signals the boundary with
    # OverflowError, which is not a CtyError, so it escaped the taxonomy as a
    # CtyFunctionPanicError; it is an ordinary CtyFunctionError now.
    #
    # Strict, so replacing datetime later forces these entries out rather than
    # leaving a stale note behind.
    # The one deliberate refusal of something go-cty answers, and the reasoning
    # is about which failure a caller can act on. `formatdate("2006-01-02", ts)`
    # returns the string "2006-01-02" there: not an error, not a date, and
    # shaped exactly like the answer the caller wanted -- the worst of the
    # forty-three breaking changes in 0.5.0, since a test asserting "the output
    # looks like a date" passes and the wrong value reaches Terraform state.
    # Every other silent break in that list either raises or produces visibly
    # wrong output. Strict, so removing the refusal forces this entry out.
    "formatdate(2006-01-02,2020-01-02T03:04:05Z)": (
        "deliberate: a Go reference layout is refused here and returned as literal text there"
    ),
    "timeadd(9999-12-31T23:59:59Z,1h)": "calendar range: Go's time.Time runs past year 9999, datetime does not",
    "timeadd(0001-01-01T00:00:00Z,-1s)": "calendar range: Go's time.Time runs before year 1, datetime does not",
    # Two divergences left by transcribing `pow` through float64, neither of them
    # about `pow`.
    #
    # The first is a *spelling* gap in the wire codec, and the digits now agree:
    # both sides answer 1.4142135623730951. go-cty holds that as a big.Float of
    # precision 53 built by `SetFloat64`, so `Float64()` is exact and msgpack
    # writes a float64 (`msgpack/marshal.go:92`). This package holds the shortest
    # decimal that names the same float, which is not *exactly* that float, so
    # the codec correctly declines the float64 branch and writes the text. Both
    # spellings are right about the number and only one is right about the bytes.
    # Fixing it means recording that a number came from a float64 computation,
    # which is a change to how every number is stored -- and the naive version,
    # comparing against `str(float(d))`, is the bug the comment at
    # `codec.py:296` exists to prevent.
    #
    # **Confirmed at the byte level on 2026-08-19**, against go-cty v1.19.0
    # directly rather than through this harness, because the harness cannot
    # express it: `cty msgpack encode` parses its argument with
    # `big.ParseFloat(text, 10, 512, ...)`, so asking it to encode the *text*
    # "1.4142135623730951" builds a precision-512 float whose `Float64()` is
    # inexact and which therefore marshals as text, agreeing with this package
    # and hiding the gap. go-cty's own `stdlib.Pow` result is a precision-**53**
    # float built by `SetFloat64`: `Float64()` is Exact and msgpack writes
    # `cb3ff6a09e667f3bcd`, nine bytes, against this package's nineteen bytes of
    # text. Same number, different wire.
    "pow(2,0.5)": "wire spelling: go-cty writes a float64-derived number as a float64, this writes its text",
    "pow(1.1,2)": "wire spelling: go-cty writes a float64-derived number as a float64, this writes its text",
    # The second will not be fixed. Go's `math.Pow` is a pure-Go implementation
    # and is not correctly rounded; the platform libm behind Python's `math.pow`
    # is. At 10^308 they are three ULPs apart -- Go answers the float whose
    # shortest spelling is 1.0000000000000006e+308, and this answers the one
    # nearest to 10^308. Reproducing Go's rounding error is not parity worth
    # having, and the row stays so the difference is recorded rather than found
    # again.
    "pow(10,308)": "Go's math.Pow is not correctly rounded; the platform libm behind math.pow is",
}

# The same, for the nulled-argument population. A list of its own rather than a
# share of the one above, because the two populations disagree about different
# cases: `contains` with an unknown element answered a refined unknown correctly
# for one and not the other, and one shared list would have marked a case xfail
# in the population where it passes -- which, being strict, fails.
#
# Empty, and kept: four `contains` entries lived here for the afternoon it took
# the refinement migration to reach that function, and the next unknown-payload
# divergence in this population has somewhere to go.
KNOWN_NULL_DIVERGENCES: dict[str, str] = {}


# Functions the oracle exposes that this sweep does not drive, and why. Every
# one of them is unported; nothing implemented here belongs in this list.
UNSWEPT: dict[str, str] = {}


def _case_id(func: str, args: list[Arg]) -> str:
    rendered = ",".join(str(spec.get("value")) for _value, spec in args)
    return f"{func}({rendered})"


def _go_result(func: str, specs: list[dict[str, Any]]) -> tuple[str, Any, list[str]]:
    """go-cty's answer as (kind, payload, marks): ok / unknown / error.

    Marks are the deep union, sorted -- the harness runs `UnmarkDeep` on the
    result and reports what it collected, which is also how `Function.Call`
    itself treats marks, so nothing positional is lost that go-cty would keep.
    """
    completed = subprocess.run(  # nosec
        [soup_go(), "cty", "call", func, *[json.dumps(spec) for spec in specs]],
        capture_output=True,
        check=False,
    )
    for line in completed.stdout.decode().splitlines():
        if line.startswith("{"):
            # `parse_float=Decimal`, for the reason `_oracle.run` already does
            # it: a plain `json.loads` turns every non-integer go-cty answer
            # into a Python float, so go's 155-digit `divide(1, 3)` arrived here
            # as 0.3333333333333333. That does not only weaken the comparison,
            # it can *invent agreement* -- a go answer of
            # 0.1000000000000000055511151231257827 truncates to exactly the 0.1
            # this package would return. Integers were always safe, Python's
            # being arbitrary precision, which is why nothing noticed.
            reported = json.loads(line, parse_float=Decimal)
            marks = sorted(reported.get("marks") or [])
            if not reported.get("ok"):
                return "error", reported.get("error", ""), marks
            if reported.get("unknown"):
                # The type and the refinements come with it. Comparing "unknown"
                # against "unknown" only established that both sides declined to
                # answer, not that they declined knowing the same things -- and
                # go-cty's refinements are load-bearing, so an answer refined to
                # [1, 2] and a bare unknown are different answers that this
                # sweep used to call identical. The type is here for the same
                # reason: `flatten` deferring as list(string) and deferring as
                # dynamic are different answers to a Terraform plan.
                return "unknown", (reported.get("type"), reported.get("refine") or {}), marks
            if reported.get("null"):
                return "null", reported.get("type"), marks
            if "msgpack" in reported:
                # A result the JSON codec cannot express -- a container holding
                # an unknown element. Compared as wire bytes, which is the
                # stricter comparison anyway and the one Terraform makes.
                return (
                    "ok",
                    (
                        reported.get("type"),
                        msgpack.unpackb(base64.b64decode(reported["msgpack"]), strict_map_key=False),
                    ),
                    marks,
                )
            return "ok", (reported.get("type"), reported.get("value")), marks
    raise AssertionError(f"{func}: harness produced no result: {completed.stderr.decode()[-400:]}")


def _our_result(func: str, values: list[CtyValue[Any]]) -> tuple[str, Any, list[str]]:
    """The same answer from this package, routed through the wire.

    Compared as msgpack rather than read off the value, so what is checked is
    what would actually reach Terraform. Marks are collected the way the
    harness collects them -- the deep union, sorted -- and the payload is
    spelled from the unmarked view, since a mark has no wire form.
    """
    # A case row for an unregistered name is a fault in this file, not a
    # coverage decision: until 2026-08-17 this returned a "missing" sentinel
    # that every caller turned into pytest.skip(), so dropping a function from
    # STDLIB while leaving its rows here would have skipped every one of them
    # and read as a cleaner run, not a broken one.
    assert func in STDLIB, f"{func} is in CASES but not registered in STDLIB"
    implementation = STDLIB[func]
    try:
        marked = implementation(*values)
    except Exception as exc:  # noqa: BLE001 - any refusal is "error" for this comparison
        return "error", f"{type(exc).__name__}: {exc}", []
    result, mark_set = unmark_deep(marked)
    marks = sorted(mark if isinstance(mark, str) else str(mark) for mark in mark_set)
    # A capsule type has no wire spelling on either side, so both ends name it
    # the way the harness does rather than each inventing an answer.
    wire_type = "bytes" if result.type.equal(BytesCapsule) else result.type._to_wire_json()
    if result.is_unknown:
        return "unknown", (wire_type, _refinements(result)), marks
    if result.is_null:
        return "null", wire_type, marks
    if result.type.equal(BytesCapsule):
        # A capsule has no wire form on either side -- go-cty refuses to
        # marshal a capsule type at all -- so the harness carries the buffer as
        # base64 and this does the same. That compares the buffers, rather than
        # two different ways of declining to encode them.
        return "ok", ("bytes", base64.b64encode(result.value).decode()), marks
    return (
        "ok",
        (
            result.type._to_wire_json(),
            msgpack.unpackb(cty_to_msgpack(result, result.type), strict_map_key=False),
        ),
        marks,
    )


@pytest.mark.parametrize(("func", "args"), CASES, ids=[_case_id(func, args) for func, args in CASES])
def test_the_two_implementations_answer_the_same(func: str, args: list[Arg], request: Any) -> None:
    """Same call, same result type and value.

    Both refusing counts as agreement: the messages differ between a Go and a
    Python implementation, and demanding they match would pin wording rather
    than behaviour. Both answering *unknown* likewise.
    """
    case_id = _case_id(func, args)
    if case_id in KNOWN_DIVERGENCES:
        # A marker rather than pytest.xfail(), which aborts the test then and
        # there: the body has to actually run for a fixed divergence to XPASS
        # and, being strict, fail. Calling pytest.xfail() here would have made
        # KNOWN_DIVERGENCES exactly the kind of list that rots unnoticed that
        # it exists to prevent.
        request.node.add_marker(pytest.mark.xfail(reason=KNOWN_DIVERGENCES[case_id], strict=True))

    theirs = _go_result(func, [spec for _value, spec in args])
    ours = _our_result(func, [value for value, _spec in args])

    assert ours[0] == theirs[0], f"{case_id}: go-cty {theirs[0]} ({theirs[1]}), pyvider {ours[0]} ({ours[1]})"
    if theirs[0] != "error":
        # Every kind but `error` carries a payload worth comparing, and until
        # 2026-08-17 only `ok` was compared -- so every unknown answer counted
        # as equal to every other unknown answer, and so did every null. That is
        # the fault this file exists to catch, sitting in this file.
        assert ours[1] == theirs[1], f"{case_id}: go-cty {theirs[1]}, pyvider {ours[1]}"
        assert ours[2] == theirs[2], f"{case_id} marks: go-cty {theirs[2]}, pyvider {ours[2]}"


@pytest.mark.parametrize(("func", "args"), CASES, ids=[_case_id(func, args) for func, args in CASES])
def test_a_null_argument_is_answered_the_same_way(func: str, args: list[Arg], request: Any) -> None:
    """Every argument of every case, nulled in turn.

    The argument table is reused rather than hand-written, so this is exactly as
    broad as the sweep itself -- which is the point. A one-off run of this shape
    found **109 of 138 argument positions disagreeing**, every one of them
    go-cty raising where this package did something else: unknown in 69 of them,
    a *computed result* in 21 (`lookup` on a null map returned its default,
    `max(null, 5)` returned 5), and a null in 19.

    All of it was one fault repeated: the hand-rolled guard
    `if x.is_null or x.is_unknown: return unknown` treats a null as an unknown.
    They are not the same. An unknown is a value nobody knows yet; a null is a
    value that is definitely absent, and computing with it invents a fact.
    """
    case_id = _case_id(func, args)
    if case_id in KNOWN_NULL_DIVERGENCES:
        request.node.add_marker(pytest.mark.xfail(reason=KNOWN_NULL_DIVERGENCES[case_id], strict=True))

    for position in range(len(args)):
        specs = [
            {"type": spec["type"], "null": True} if i == position else spec
            for i, (_value, spec) in enumerate(args)
        ]
        values = [
            CtyValue.null(value.type) if i == position else value for i, (value, _spec) in enumerate(args)
        ]

        theirs = _go_result(func, specs)
        ours = _our_result(func, values)

        where = f"{func} with argument {position} null"
        assert ours[0] == theirs[0], (
            f"{where}: go-cty {theirs[0]} ({theirs[1]}), pyvider {ours[0]} ({ours[1]})"
        )
        if theirs[0] != "error":
            assert ours[1] == theirs[1], f"{where}: go-cty {theirs[1]}, pyvider {ours[1]}"
            assert ours[2] == theirs[2], f"{where} marks: go-cty {theirs[2]}, pyvider {ours[2]}"


def test_the_known_divergence_list_is_not_stale() -> None:
    """Every entry must name a case that still exists.

    A stale entry silently stops covering anything, which is the failure mode
    this whole file exists to catch in the library itself.
    """
    ids = {_case_id(func, args) for func, args in CASES}

    assert not (KNOWN_DIVERGENCES.keys() - ids), (
        f"KNOWN_DIVERGENCES names cases that no longer exist: {KNOWN_DIVERGENCES.keys() - ids}"
    )
    assert not (KNOWN_NULL_DIVERGENCES.keys() - ids), (
        f"KNOWN_NULL_DIVERGENCES names cases that no longer exist: {KNOWN_NULL_DIVERGENCES.keys() - ids}"
    )


def test_the_sweep_drives_every_function_the_oracle_exposes() -> None:
    """A guard on coverage, not on behaviour.

    Measured against the oracle's own surface rather than against a threshold
    typed in here. A threshold is coverage reported against the wrong
    denominator, which is the bug this file exists to catch in the library --
    and it was live in this very test: it asserted "at least 70 functions" while
    the harness reached 74 of go-cty's 83, so seven implemented functions had no
    differential verification at all and nothing here could say so.
    """
    completed = subprocess.run(  # nosec
        [soup_go(), "cty", "functions"], capture_output=True, check=True
    )
    exposed = set(json.loads(completed.stdout.decode()))
    covered = {func for func, _args in CASES}

    assert not covered - exposed, f"sweep drives what the oracle does not expose: {covered - exposed}"
    assert exposed - covered == set(UNSWEPT), (
        f"exposed but unswept and unexplained: {sorted(exposed - covered - set(UNSWEPT))}; "
        f"explained but no longer unswept: {sorted(set(UNSWEPT) - (exposed - covered))}"
    )


# 🌊🪢🔚
