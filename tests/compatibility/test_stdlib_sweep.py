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
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess  # nosec
from typing import Any

import msgpack
import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyValue,
)
from pyvider.cty.codec import cty_to_msgpack
import pyvider.cty.functions as F

pytestmark = pytest.mark.compat

# One argument, written once, in both dialects: the pyvider value and the JSON
# the harness needs to build the same value in Go.
Arg = tuple[CtyValue[Any], dict[str, Any]]


def st(v: str) -> Arg:
    return CtyString().validate(v), {"type": "string", "value": v}


def nm(v: Any) -> Arg:
    return CtyNumber().validate(v), {"type": "number", "value": v}


def bl(v: bool) -> Arg:  # noqa: FBT001
    return CtyBool().validate(v), {"type": "bool", "value": v}


def ls(v: list[str]) -> Arg:
    return CtyList(element_type=CtyString()).validate(v), {"type": ["list", "string"], "value": v}


def ln(v: list[Any]) -> Arg:
    return CtyList(element_type=CtyNumber()).validate(v), {"type": ["list", "number"], "value": v}


def mp(v: dict[str, str]) -> Arg:
    return CtyMap(element_type=CtyString()).validate(v), {"type": ["map", "string"], "value": v}


def se(v: list[str]) -> Arg:
    return CtySet(element_type=CtyString()).validate(v), {"type": ["set", "string"], "value": v}


def mn(v: dict[str, Any]) -> Arg:
    return CtyMap(element_type=CtyNumber()).validate(v), {"type": ["map", "number"], "value": v}


def ob(v: dict[str, str]) -> Arg:
    object_type = CtyObject(attribute_types=dict.fromkeys(v, CtyString()))
    return object_type.validate(v), {"type": ["object", dict.fromkeys(v, "string")], "value": v}


# (function name, arguments). The id is derived, so adding a row is one line.
CASES: list[tuple[str, list[Arg]]] = [
    # strings
    ("upper", [st("héllo")]),
    ("lower", [st("HÉLLO")]),
    ("title", [st("a bc")]),
    ("strrev", [st("abc")]),
    ("strrev", [st("héllo")]),
    ("chomp", [st("a\n")]),
    ("chomp", [st("a\r\n")]),
    ("trimspace", [st("  a  ")]),
    ("trim", [st("xxaxx"), st("x")]),
    ("trimprefix", [st("abc"), st("a")]),
    ("trimprefix", [st("abc"), st("z")]),
    ("trimsuffix", [st("abc"), st("c")]),
    ("replace", [st("aaa"), st("a"), st("b")]),
    ("replace", [st("abc"), st(""), st("-")]),
    ("split", [st(","), st("a,b")]),
    ("split", [st(","), st("")]),
    ("join", [st(","), ls(["a", "b"])]),
    ("join", [st(","), ls([])]),
    ("substr", [st("abcdef"), nm(1), nm(3)]),
    ("substr", [st("abcdef"), nm(1), nm(-1)]),
    ("substr", [st("héllo"), nm(0), nm(2)]),
    ("indent", [nm(2), st("a\nb")]),
    # regexp
    ("regex", [st("a(b)c"), st("abc")]),
    ("regexall", [st("a(b)"), st("abab")]),
    ("regexreplace", [st("-ab-axxb-"), st("a(x*)b"), st("${1}W")]),
    ("regexreplace", [st("-ab-axxb-"), st("a(x*)b"), st("$1W")]),
    # numbers
    ("abs", [nm(-3)]),
    ("ceil", [nm("1.2")]),
    ("ceil", [nm("-1.2")]),
    ("floor", [nm("1.8")]),
    ("floor", [nm("-1.8")]),
    ("signum", [nm(-5)]),
    ("signum", [nm(0)]),
    ("int", [nm("3.9")]),
    ("int", [nm("-3.9")]),
    ("add", [nm(1), nm(2)]),
    ("subtract", [nm(5), nm(2)]),
    ("multiply", [nm(3), nm(4)]),
    ("divide", [nm(7), nm(2)]),
    ("divide", [nm(1), nm(3)]),
    ("modulo", [nm(7), nm(3)]),
    ("modulo", [nm(-7), nm(3)]),
    ("negate", [nm(3)]),
    ("pow", [nm(2), nm(10)]),
    ("pow", [nm(2), nm("0.5")]),
    ("log", [nm(8), nm(2)]),
    ("max", [nm(1), nm(5)]),
    ("min", [nm(1), nm(5)]),
    ("parseint", [st("ff"), nm(16)]),
    ("parseint", [st("-10"), nm(10)]),
    # comparison and logic
    ("equal", [st("a"), st("a")]),
    ("notequal", [st("a"), st("b")]),
    ("greaterthan", [nm(2), nm(1)]),
    ("greaterthanorequalto", [nm(1), nm(1)]),
    ("lessthan", [nm(1), nm(2)]),
    ("lessthanorequalto", [nm(1), nm(1)]),
    ("not", [bl(True)]),
    ("and", [bl(True), bl(False)]),
    ("or", [bl(True), bl(False)]),
    # collections
    ("distinct", [ls(["a", "a", "b"])]),
    ("compact", [ls(["a", "", "b"])]),
    ("concat", [ls(["a"]), ls(["b"])]),
    ("contains", [ls(["a"]), st("a")]),
    ("contains", [ls(["a"]), st("z")]),
    ("element", [ls(["a", "b"]), nm(1)]),
    ("element", [ls(["a", "b"]), nm(3)]),
    ("index", [ls(["a", "b"]), st("b")]),
    ("hasindex", [ls(["a"]), nm(0)]),
    ("hasindex", [ls(["a"]), nm(9)]),
    ("keys", [mp({"b": "1", "a": "2"})]),
    ("values", [mp({"b": "1", "a": "2"})]),
    ("values", [mp({})]),
    ("lookup", [mp({"a": "1"}), st("a"), st("z")]),
    ("lookup", [mp({"a": "1"}), st("q"), st("z")]),
    ("merge", [mp({"a": "1"}), mp({"b": "2"})]),
    ("merge", [mp({"a": "1"}), mp({"a": "2"})]),
    ("merge", [ob({"a": "1"}), ob({"b": "2"})]),
    ("merge", [mp({"a": "1"}), ob({"b": "2"})]),
    ("merge", [mp({"a": "1"}), mn({"b": 2})]),
    ("merge", [mp({})]),
    ("reverselist", [ls(["a", "b"])]),
    ("sort", [ls(["b", "a", "C"])]),
    ("slice", [ls(["a", "b", "c"]), nm(1), nm(3)]),
    ("zipmap", [ls(["a", "b"]), ls(["1", "2"])]),
    ("setunion", [se(["a"]), se(["b"])]),
    ("setintersection", [se(["a", "b"]), se(["b"])]),
    ("setsubtract", [se(["a", "b"]), se(["b"])]),
    ("flatten", [ls(["a"])]),
    ("chunklist", [ls(["a", "b", "c"]), nm(2)]),
    ("length", [ls(["a", "b"])]),
    ("coalesce", [st(""), st("b")]),
    ("coalescelist", [ls([]), ls(["a"])]),
    ("range", [nm(3)]),
    ("range", [nm(1), nm(5), nm(2)]),
    # encoding and time
    ("jsonencode", [ls(["a"])]),
    ("jsonencode", [nm(1)]),
    ("jsondecode", [st('{"a":1}')]),
    ("jsondecode", [st("[1,2]")]),
    ("jsondecode", [st('[1,"a",true]')]),
    ("jsondecode", [st('{"a":{"b":[1,{"c":true}]}}')]),
    ("jsondecode", [st('{"a":null}')]),
    ("jsondecode", [st("null")]),
    ("jsondecode", [st("{}")]),
    ("csvdecode", [st("a,b\n1,2")]),
    ("csvdecode", [st("a,b\n1,2\n3,4")]),
    ("csvdecode", [st("a,b")]),
    ("csvdecode", [st("a,a\n1,2")]),
    ("csvdecode", [st("a,b\n1")]),
    ("timeadd", [st("2020-01-01T00:00:00Z"), st("1h")]),
    ("timeadd", [st("2020-01-01T00:00:00+02:00"), st("1h30m")]),
    ("timeadd", [st("2020-01-01T00:00:00Z"), st("-2h5m")]),
    ("timeadd", [st("2020-01-01T00:00:00Z"), st("not a duration")]),
    ("formatdate", [st("YYYY-MM-DD"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("EEEE, DD MMMM YYYY hh:mm:ss ZZZZ"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("HH:mm aa Z"), st("2020-11-22T13:04:05-08:00")]),
    ("formatdate", [st("'it''s' YYYY"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("YYY"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("YYYY"), st("2020-01-02 03:04:05Z")]),
]

# Divergences that are real, reproduced, and not yet fixed. Strict xfails, so
# that fixing one turns its entry red and forces it out of this list. Each entry
# is a case id and why it is still here.
KNOWN_DIVERGENCES: dict[str, str] = {
    # The numeric precision model differs, and in both directions. go-cty holds
    # a number in a 512-bit big.Float, so a non-terminating quotient comes back
    # with 155 significant digits against Decimal's 28-digit default context --
    # but its transcendental functions run in float64 first, so `pow(2, 0.5)`
    # comes back with 17, and there this package is the *more* accurate of the
    # two. Neither is a wrong answer; they are different models. Matching go-cty
    # means reproducing its float64 step, which is a decision, not a fix.
    "divide(1,3)": "numeric precision model: go-cty big.Float 155 digits, Decimal 28",
    "pow(2,0.5)": "numeric precision model: go-cty computes in float64, Decimal is more precise",
}

# go-cty's name for a function, and this package's name for the same function.
# The two diverge systematically -- `max` is exported as `max_fn` to dodge the
# Python builtin, comparisons are spelled in snake_case -- so without this map
# the sweep skips fourteen functions while reporting that it covered them.
# That the public API does not use Terraform's own function names is a separate
# parity question, recorded in the tracker rather than settled here.
NAME_MAP = {
    "abs": "abs_fn",
    "ceil": "ceil_fn",
    "floor": "floor_fn",
    "int": "int_fn",
    "log": "log_fn",
    "max": "max_fn",
    "min": "min_fn",
    "parseint": "parseint_fn",
    "pow": "pow_fn",
    "signum": "signum_fn",
    "notequal": "not_equal",
    "greaterthan": "greater_than",
    "greaterthanorequalto": "greater_than_or_equal_to",
    "lessthan": "less_than",
    "lessthanorequalto": "less_than_or_equal_to",
    "reverselist": "reverse",
}


def _case_id(func: str, args: list[Arg]) -> str:
    rendered = ",".join(str(spec.get("value")) for _value, spec in args)
    return f"{func}({rendered})"


def _soup_go() -> str:
    candidate = os.environ.get("SOUP_GO_BIN") or shutil.which("soup-go") or "/tmp/soup-go"  # nosec
    if not Path(candidate).exists():
        pytest.skip(f"soup-go harness not found at {candidate}; set SOUP_GO_BIN.")
    return candidate


def _go_result(func: str, specs: list[dict[str, Any]]) -> tuple[str, Any]:
    """go-cty's answer as (kind, payload): ok / unknown / error."""
    completed = subprocess.run(  # nosec
        [_soup_go(), "cty", "call", func, *[json.dumps(spec) for spec in specs]],
        capture_output=True,
        check=False,
    )
    for line in completed.stdout.decode().splitlines():
        if line.startswith("{"):
            reported = json.loads(line)
            if not reported.get("ok"):
                return "error", reported.get("error", "")
            if reported.get("unknown"):
                return "unknown", None
            return "ok", (reported.get("type"), reported.get("value"))
    raise AssertionError(f"{func}: harness produced no result: {completed.stderr.decode()[-400:]}")


def _our_result(func: str, values: list[CtyValue[Any]]) -> tuple[str, Any]:
    """The same answer from this package, routed through the wire.

    Compared as msgpack rather than read off the value, so what is checked is
    what would actually reach Terraform.
    """
    implementation = getattr(F, NAME_MAP.get(func, func), None)
    if implementation is None:
        return "missing", None
    try:
        result = implementation(*values)
    except Exception as exc:  # noqa: BLE001 - any refusal is "error" for this comparison
        return "error", f"{type(exc).__name__}: {exc}"
    if result.is_unknown:
        return "unknown", None
    return "ok", (
        result.type._to_wire_json(),
        msgpack.unpackb(cty_to_msgpack(result, result.type), strict_map_key=False),
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

    if ours[0] == "missing":
        pytest.skip(f"{func} is not exported by pyvider-cty")

    assert ours[0] == theirs[0], f"{case_id}: go-cty {theirs[0]} ({theirs[1]}), pyvider {ours[0]} ({ours[1]})"
    if theirs[0] == "ok":
        assert ours[1] == theirs[1], f"{case_id}: go-cty {theirs[1]}, pyvider {ours[1]}"


def test_the_known_divergence_list_is_not_stale() -> None:
    """Every entry must name a case that still exists.

    A stale entry silently stops covering anything, which is the failure mode
    this whole file exists to catch in the library itself.
    """
    ids = {_case_id(func, args) for func, args in CASES}

    assert not (KNOWN_DIVERGENCES.keys() - ids), (
        f"KNOWN_DIVERGENCES names cases that no longer exist: {KNOWN_DIVERGENCES.keys() - ids}"
    )


def test_the_sweep_covers_most_of_what_the_oracle_exposes() -> None:
    """A guard on coverage, not on behaviour.

    The sweep is only worth anything if it is broad, and breadth is exactly the
    property that decays quietly as functions are added.
    """
    covered = {func for func, _args in CASES}

    assert len(covered) >= 55, f"sweep covers only {len(covered)} functions"


# 🌊🪢🔚
