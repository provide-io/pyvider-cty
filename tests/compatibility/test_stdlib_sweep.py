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

import base64
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
    CtyType,
    CtyValue,
)
from pyvider.cty.codec import cty_to_msgpack
from pyvider.cty.functions import STDLIB
from pyvider.cty.types import BytesCapsule

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


def lb(v: list[bool]) -> Arg:
    return CtyList(element_type=CtyBool()).validate(v), {"type": ["list", "bool"], "value": v}


def mp(v: dict[str, str]) -> Arg:
    return CtyMap(element_type=CtyString()).validate(v), {"type": ["map", "string"], "value": v}


def se(v: list[str]) -> Arg:
    return CtySet(element_type=CtyString()).validate(v), {"type": ["set", "string"], "value": v}


def sb(v: list[bool]) -> Arg:
    return CtySet(element_type=CtyBool()).validate(v), {"type": ["set", "bool"], "value": v}


def sn(v: list[Any]) -> Arg:
    return CtySet(element_type=CtyNumber()).validate(v), {"type": ["set", "number"], "value": v}


def mn(v: dict[str, Any]) -> Arg:
    return CtyMap(element_type=CtyNumber()).validate(v), {"type": ["map", "number"], "value": v}


def ob(v: dict[str, str]) -> Arg:
    object_type = CtyObject(attribute_types=dict.fromkeys(v, CtyString()))
    return object_type.validate(v), {"type": ["object", dict.fromkeys(v, "string")], "value": v}


def by(v: bytes) -> Arg:
    """A Bytes capsule buffer, carried to the harness as base64.

    JSON has no byte-string literal and go-cty refuses to marshal a capsule
    type at all, so base64 is the only spelling both ends can agree on.
    """
    return BytesCapsule.validate(v), {"type": "bytes", "value": base64.b64encode(v).decode()}


def nul(spec: Any, cty_type: CtyType[Any]) -> Arg:
    """A typed null. Distinct from unknown, and the two are answered differently."""
    return CtyValue.null(cty_type), {"type": spec, "null": True}


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
    ("not", [bl(False)]),
    ("and", [bl(True), bl(False)]),
    ("and", [bl(True), bl(True)]),
    ("and", [bl(False), bl(False)]),
    ("or", [bl(True), bl(False)]),
    ("or", [bl(False), bl(False)]),
    ("or", [bl(True), bl(True)]),
    # collections
    ("distinct", [ls(["a", "a", "b"])]),
    ("compact", [ls(["a", "", "b"])]),
    ("concat", [ls(["a"]), ls(["b"])]),
    ("concat", [ls(["a"]), ln([1])]),
    ("concat", [ls(["a"]), lb([True])]),
    ("concat", [ln([1]), lb([True])]),
    ("concat", [ls(["a"]), nul(["list", "string"], CtyList(element_type=CtyString()))]),
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
    ("setunion", [se(["a"])]),
    ("setunion", [se([]), se([])]),
    ("setunion", [se(["a"]), se(["a"])]),
    ("setunion", [se(["a"]), sb([True])]),
    ("setunion", [se(["a"]), sn([1])]),
    ("setintersection", [se(["a", "b"]), se(["b"])]),
    ("setintersection", [se(["a"]), se(["b"])]),
    ("setsubtract", [se(["a", "b"]), se(["b"])]),
    ("setsubtract", [se(["a"]), se(["a"])]),
    ("setsymmetricdifference", [se(["a", "b"]), se(["b", "c"])]),
    ("setsymmetricdifference", [se(["a"]), se(["a"])]),
    ("setsymmetricdifference", [se([]), se(["a"])]),
    ("setsymmetricdifference", [se(["a"]), se(["b"]), se(["c"])]),
    ("sethaselement", [se(["a", "b"]), st("a")]),
    ("sethaselement", [se(["a", "b"]), st("z")]),
    ("sethaselement", [se([]), st("a")]),
    ("setproduct", [se(["a"]), se(["x"])]),
    ("setproduct", [se(["a", "b"]), se(["x", "y"])]),
    ("setproduct", [se(["a"]), se([])]),
    ("setproduct", [ls(["a", "b"]), ls(["x"])]),
    ("setproduct", [se(["a"])]),
    ("flatten", [ls(["a"])]),
    ("chunklist", [ls(["a", "b", "c"]), nm(2)]),
    ("length", [ls(["a", "b"])]),
    ("coalesce", [st(""), st("b")]),
    ("coalescelist", [ls([]), ls(["a"])]),
    ("range", [nm(3)]),
    ("range", [nm(-3)]),
    ("range", [nm(0)]),
    ("range", [nm(1), nm(5)]),
    ("range", [nm(5), nm(1)]),
    ("range", [nm(1), nm(5), nm(2)]),
    ("range", [nm(5), nm(1), nm(-2)]),
    ("range", [nm(0), nm("1"), nm("0.25")]),
    ("range", [nm(1), nm(5), nm(-1)]),
    ("range", [nm(0), nm(2000)]),
    ("range", [nm(0), nm(10), nm(0)]),
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
    # format
    ("format", [st("%s"), st("hi")]),
    ("format", [st("%q"), st('a"b')]),
    ("format", [st("%v"), st("hi")]),
    ("format", [st("%v"), nm(42)]),
    ("format", [st("%v"), nm("0.00001")]),
    ("format", [st("%#v"), nm("0.00001")]),
    ("format", [st("%#v"), ls(["a", "b"])]),
    ("format", [st("%t"), bl(True)]),
    ("format", [st("%d"), nm(42)]),
    ("format", [st("%d"), nm("1.5")]),
    ("format", [st("%b"), nm(5)]),
    ("format", [st("%o"), nm(64)]),
    ("format", [st("%x"), nm(255)]),
    ("format", [st("%X"), nm(255)]),
    ("format", [st("%e"), nm(42)]),
    ("format", [st("%E"), nm("0.00001")]),
    ("format", [st("%f"), nm("3.14159")]),
    ("format", [st("%g"), nm("0.00001")]),
    ("format", [st("%G"), nm("1e21")]),
    ("format", [st("%5s|"), st("ab")]),
    ("format", [st("%-5s|"), st("ab")]),
    ("format", [st("%.2s"), st("hello")]),
    ("format", [st("%05d"), nm(42)]),
    ("format", [st("%+d"), nm(42)]),
    ("format", [st("%08.2f"), nm(-42)]),
    ("format", [st("%.3e"), nm(0)]),
    ("format", [st("%.5g"), nm("0.00001")]),
    ("format", [st("100%%")]),
    ("format", [st("a%sb"), st("x")]),
    ("format", [st("%s%s"), st("a"), st("b")]),
    ("format", [st("%[2]s%[1]s"), st("a"), st("b")]),
    ("format", [st("%s"), st("a"), st("b")]),
    ("format", [st("hi"), st("a")]),
    ("format", [st("%s%s"), st("a")]),
    ("format", [st("%z"), st("a")]),
    ("format", [st("%5s|"), st("\U0001f468\u200d\U0001f469\u200d\U0001f467")]),
    ("format", [st("%.1s"), st("\U0001f468\u200d\U0001f469\u200d\U0001f467")]),
    ("format", [st("%d"), st("nope")]),
    ("format", [st("%s"), nul("string", CtyString())]),
    ("format", [st("%v"), nul("string", CtyString())]),
    ("formatlist", [st("%s"), ls(["a", "b"])]),
    ("formatlist", [st("%s-%s"), ls(["a", "b"]), st("x")]),
    ("formatlist", [st("%s%s"), ls(["a", "b"]), ls(["1", "2"])]),
    ("formatlist", [st("%s%s"), ls(["a", "b"]), ls(["1"])]),
    ("formatlist", [st("%s"), ls([])]),
    ("formatlist", [st("%s"), st("a")]),
    ("formatlist", [st("hi")]),
    ("formatlist", [st("<%s>"), se(["a", "b"])]),
    # bytes
    ("byteslen", [by(b"hello world")]),
    ("byteslen", [by(b"")]),
    ("bytesslice", [by(b"hello world"), nm(0), nm(11)]),
    ("bytesslice", [by(b"hello world"), nm(0), nm(0)]),
    ("bytesslice", [by(b"hello world"), nm(1), nm(3)]),
    ("bytesslice", [by(b"hello world"), nm(6), nm(5)]),
    ("bytesslice", [by(b"hello world"), nm(9), nm(5)]),
    ("bytesslice", [by(b"hello world"), nm(-1), nm(2)]),
    ("bytesslice", [by(b"hello world"), nm(1), nm(-2)]),
    # conversion
    ("tostring", [st("a")]),
    ("tostring", [nm(1)]),
    ("tostring", [nm("1.5")]),
    ("tostring", [bl(True)]),
    ("tostring", [bl(False)]),
    ("tostring", [ls(["a"])]),
    ("tostring", [nul("string", CtyString())]),
    ("tonumber", [nm(1)]),
    ("tonumber", [st("1.5")]),
    ("tonumber", [st("abc")]),
    ("tonumber", [bl(True)]),
    ("tonumber", [ls(["a"])]),
    ("tonumber", [nul("number", CtyNumber())]),
    ("tostring", [nm("1e2")]),
    ("tostring", [nm("1e-7")]),
    ("tostring", [nm("1.50")]),
    ("tobool", [bl(True)]),
    ("tobool", [st("true")]),
    ("tobool", [st("false")]),
    ("tobool", [st("yes")]),
    ("tobool", [st("TRUE")]),
    ("tobool", [st("True")]),
    ("tobool", [st("1")]),
    ("tobool", [st("0")]),
    ("tobool", [nm(1)]),
    ("tobool", [nul("bool", CtyBool())]),
    ("setproduct", [se(["a"]), ls(["x"])]),
    ("setproduct", [ls(["a", "b"]), ls(["x", "y"])]),
]

# Divergences that are real, reproduced, and not yet fixed. Strict xfails, so
# that fixing one turns its entry red and forces it out of this list. Each entry
# is a case id and why it is still here.
KNOWN_DIVERGENCES: dict[str, str] = {
    # go-cty measures `format`'s width and precision in *grapheme clusters*;
    # this measures code points. NFC normalization at construction hides the
    # difference for anything with a precomposed form, so it takes a cluster
    # that has none to see it -- and there it matters: `%.1s` of a ZWJ family
    # emoji truncates to the whole emoji there and to the first person in it
    # here, which is a different picture rather than a shorter string. The
    # same UAX#29 decision `strlen` waits on.
    "format(%5s|,\U0001f468\u200d\U0001f469\u200d\U0001f467)": (
        "width is measured in grapheme clusters there, code points here"
    ),
    "format(%.1s,\U0001f468\u200d\U0001f469\u200d\U0001f467)": (
        "precision is measured in grapheme clusters there, code points here"
    ),
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


# Functions the oracle exposes that this sweep does not drive, and why. Every
# one of them is unported; nothing implemented here belongs in this list.
UNSWEPT: dict[str, str] = {
    "assertnotnull": "not ported",
    "strlen": "not ported -- blocked on UAX#29 grapheme segmentation",
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
            if reported.get("null"):
                return "null", reported.get("type")
            return "ok", (reported.get("type"), reported.get("value"))
    raise AssertionError(f"{func}: harness produced no result: {completed.stderr.decode()[-400:]}")


def _our_result(func: str, values: list[CtyValue[Any]]) -> tuple[str, Any]:
    """The same answer from this package, routed through the wire.

    Compared as msgpack rather than read off the value, so what is checked is
    what would actually reach Terraform.
    """
    implementation = STDLIB.get(func)
    if implementation is None:
        return "missing", None
    try:
        result = implementation(*values)
    except Exception as exc:  # noqa: BLE001 - any refusal is "error" for this comparison
        return "error", f"{type(exc).__name__}: {exc}"
    if result.is_unknown:
        return "unknown", None
    if result.is_null:
        return "null", result.type._to_wire_json()
    if result.type.equal(BytesCapsule):
        # A capsule has no wire form on either side -- go-cty refuses to
        # marshal a capsule type at all -- so the harness carries the buffer as
        # base64 and this does the same. That compares the buffers, rather than
        # two different ways of declining to encode them.
        return "ok", ("bytes", base64.b64encode(result.value).decode())
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


@pytest.mark.parametrize(("func", "args"), CASES, ids=[_case_id(func, args) for func, args in CASES])
def test_a_null_argument_is_answered_the_same_way(func: str, args: list[Arg]) -> None:
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
        if ours[0] == "missing":
            pytest.skip(f"{func} is not exported by pyvider-cty")

        where = f"{func} with argument {position} null"
        assert ours[0] == theirs[0], (
            f"{where}: go-cty {theirs[0]} ({theirs[1]}), pyvider {ours[0]} ({ours[1]})"
        )
        if theirs[0] == "ok":
            assert ours[1] == theirs[1], f"{where}: go-cty {theirs[1]}, pyvider {ours[1]}"


def test_the_known_divergence_list_is_not_stale() -> None:
    """Every entry must name a case that still exists.

    A stale entry silently stops covering anything, which is the failure mode
    this whole file exists to catch in the library itself.
    """
    ids = {_case_id(func, args) for func, args in CASES}

    assert not (KNOWN_DIVERGENCES.keys() - ids), (
        f"KNOWN_DIVERGENCES names cases that no longer exist: {KNOWN_DIVERGENCES.keys() - ids}"
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
        [_soup_go(), "cty", "functions"], capture_output=True, check=True
    )
    exposed = set(json.loads(completed.stdout.decode()))
    covered = {func for func, _args in CASES}

    assert not covered - exposed, f"sweep drives what the oracle does not expose: {covered - exposed}"
    assert exposed - covered == set(UNSWEPT), (
        f"exposed but unswept and unexplained: {sorted(exposed - covered - set(UNSWEPT))}; "
        f"explained but no longer unswept: {sorted(set(UNSWEPT) - (exposed - covered))}"
    )


# 🌊🪢🔚
