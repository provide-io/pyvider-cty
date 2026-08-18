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
from decimal import Decimal
import json
import subprocess  # nosec
from typing import Any

import msgpack
import pytest

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
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
from pyvider.cty.marks import unmark_deep
from pyvider.cty.refinement import refine
from pyvider.cty.types import BytesCapsule
from tests.compatibility._oracle import refinements as _refinements, soup_go

pytestmark = pytest.mark.compat

# One argument, written once, in both dialects: the pyvider value and the JSON
# the harness needs to build the same value in Go.
Arg = tuple[CtyValue[Any], dict[str, Any]]


def st(v: str) -> Arg:
    return CtyString().validate(v), {"type": "string", "value": v}


def nm(v: Any) -> Arg:
    return CtyNumber().validate(v), {"type": "number", "value": v}


def nm_inf(*, negative: bool = False) -> Arg:
    """An infinite number, through the harness's rich dialect.

    JSON has no spelling for one, so a plain `{"type":"number","value":...}`
    cannot carry it -- which was believed to mean the oracle could not express
    it at all, and the infinity work was checked against a hand-written Go
    program instead. It can: `$number` takes the text `big.Float.Text` produces,
    and the harness has round-tripped `Infinity` since its rich dialect landed.
    These rows replace that program.
    """
    text = "-Infinity" if negative else "Infinity"
    return CtyNumber().validate(Decimal(text)), {"type": "number", "value": {"$number": text}}


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


UK = {"$unknown": True}

# go-cty's `cty.DynamicVal`: a value whose *type* is still undecided, which is
# what every reference to an unresolved resource attribute looks like during
# planning. Distinct from the unknown population, which replaces an argument
# with an unknown of the argument's own declared type -- here the function's
# type callback cannot even see what kind of thing it will be handed.
DYNAMIC_UK: Arg = (CtyValue.unknown(CtyDynamic()), {"type": "dynamic", "unknown": True})


def st_uk(prefix: str) -> Arg:
    """An *unknown* string already known to start with `prefix`.

    The one row whose answer turns on a refinement travelling *into* a function
    rather than out of one. `strlen`'s implementation reads its argument's
    `StringPrefix` and refines the result's lower bound to the number of grapheme
    clusters in it, so a bare unknown answers `n >= 0` where this answers `n >= 3`
    -- and nothing else in the table can tell those two apart.

    `string_prefix_full`, not `string_prefix`. The harness builds its side with
    `StringPrefixFull` and stores the prefix as given; `string_prefix` matches
    go-cty's `StringPrefix`, which runs `SafeKnownPrefix` first and drops the last
    character in case the next one combines with it. Written the obvious way this
    row held "abc" in Go and "ab" here, and reported `n >= 3` against `n >= 2` as
    a divergence in `strlen` when the two sides had simply been handed different
    arguments.
    """
    return (
        refine(CtyValue.unknown(CtyString())).string_prefix_full(prefix).new_value(),
        {"type": "string", "value": {"$unknown": True, "$refine": {"string_prefix": prefix}}},
    )


def nm_uk(lower: tuple[str, bool] | None = None, upper: tuple[str, bool] | None = None) -> Arg:
    """An unknown number carrying range bounds, each `(bound, inclusive)`.

    Added 2026-08-17, when the coverage audit found `strlen` was the *only*
    function ever handed a refined unknown: the no-narrowing rule -- stdlib
    functions answer a bare not-null unknown however tightly the argument is
    bounded, because their parameters mostly do not admit unknowns at all --
    was pinned by hand-written tests citing go-cty's source, never measured.
    These builders make the claim measurable, and the comparison rows below
    measure the other half: go-cty's comparisons *do* consult the ranges
    (`value_ops.go:1367`), so `lessthan(unknown < 10, 20)` is known true.
    """
    builder = refine(CtyValue.unknown(CtyNumber()))
    spec: dict[str, Any] = {}
    if lower is not None:
        builder = builder.number_range_lower_bound(Decimal(lower[0]), inclusive=lower[1])
        spec["number_lower_bound"] = [lower[0], lower[1]]
    if upper is not None:
        builder = builder.number_range_upper_bound(Decimal(upper[0]), inclusive=upper[1])
        spec["number_upper_bound"] = [upper[0], upper[1]]
    return builder.new_value(), {"type": "number", "value": {"$unknown": True, "$refine": spec}}


def ln_uk_len(lower: int | None = None, upper: int | None = None) -> Arg:
    """An unknown list of strings whose *length* is bounded."""
    builder = refine(CtyValue.unknown(CtyList(element_type=CtyString())))
    spec: dict[str, Any] = {}
    if lower is not None:
        builder = builder.collection_length_lower_bound(lower)
        spec["collection_length_lower_bound"] = lower
    if upper is not None:
        builder = builder.collection_length_upper_bound(upper)
        spec["collection_length_upper_bound"] = upper
    return builder.new_value(), {
        "type": ["list", "string"],
        "value": {"$unknown": True, "$refine": spec},
    }


def ls_uk(*elements: Any) -> Arg:
    """A *known* list of strings holding one or more unknown elements.

    The plan-time shape, and until 2026-08-17 it could not be written: the list
    took its unknown-ness from the element and every function here was handed a
    wholly unknown argument instead. So the sweep's 83 functions had only ever
    been driven with arguments that were either entirely known or entirely not.
    """
    string_type = CtyString()
    values = [CtyValue.unknown(string_type) if element is UK else element for element in elements]
    return (
        CtyList(element_type=string_type).validate(values),
        {"type": ["list", "string"], "value": list(elements)},
    )


def se_uk(*elements: Any) -> Arg:
    """The same for a set, where the *count* is what an unknown puts in doubt."""
    string_type = CtyString()
    values = [CtyValue.unknown(string_type) if element is UK else element for element in elements]
    return (
        CtySet(element_type=string_type).validate(values),
        {"type": ["set", "string"], "value": list(elements)},
    )


# (function name, arguments). The id is derived, so adding a row is one line.
# Strings whose grapheme clusters are not their code points. Named because the
# literals are unreadable and the point of each is exactly which UAX#29 rule it
# exercises.
FAMILY = "\U0001f468‍\U0001f469‍\U0001f467‍\U0001f466"  # GB11, ZWJ sequence
FLAGS = "\U0001f1fa\U0001f1f8\U0001f1ef\U0001f1f5"  # GB12/GB13, two flags
THUMB_TONED = "\U0001f44d\U0001f3fd"  # GB9, skin-tone modifier
HANGUL_JAMO = "각"  # GB6/GB7/GB8, one syllable from three jamo
CONJUNCT = "क्ष"  # GB9c, and the one Unicode-version divergence

CASES: list[tuple[str, list[Arg]]] = [
    # strings
    ("upper", [st("héllo")]),
    ("lower", [st("HÉLLO")]),
    # Case mappings that are not one code point to one code point. `héllo` and
    # `HÉLLO` map 1:1 in both directions, so the sweep could not tell Go's simple
    # per-rune mapping from Python's full mapping: `str.upper()` expands ß to SS
    # and ﬁ to FI, `str.lower()` picks the final sigma for a trailing Σ, and
    # `İ`.lower() adds a combining dot. go-cty does none of those.
    ("upper", [st("straße")]),
    ("upper", [st("ﬁ")]),
    ("lower", [st("ΣΣ")]),
    ("lower", [st("İ")]),
    ("title", [st("a bc")]),
    ("title", [st("hEllo wOrld")]),
    ("strrev", [st("abc")]),
    ("strrev", [st("héllo")]),
    ("chomp", [st("a\n")]),
    ("chomp", [st("a\r\n")]),
    ("trimspace", [st("  a  ")]),
    ("trimspace", [st("\t a \n")]),
    ("trim", [st("xxaxx"), st("x")]),
    ("trim", [st("abc"), st("z")]),
    ("trimprefix", [st("abc"), st("a")]),
    ("trimprefix", [st("abc"), st("z")]),
    ("trimsuffix", [st("abc"), st("c")]),
    ("trimsuffix", [st("abc"), st("z")]),
    ("replace", [st("aaa"), st("a"), st("b")]),
    ("replace", [st("abc"), st(""), st("-")]),
    ("split", [st(","), st("a,b")]),
    ("split", [st(","), st("")]),
    ("join", [st(","), ls(["a", "b"])]),
    ("join", [st(","), ls([])]),
    ("substr", [st("abcdef"), nm(1), nm(3)]),
    ("substr", [st("abcdef"), nm(1), nm(-1)]),
    ("substr", [st("héllo"), nm(0), nm(2)]),
    # A negative offset counts from the end, and a zero length reached that way
    # means "the rest" rather than "nothing" -- both were refused outright here
    # until the grapheme work went through go-cty's algorithm line by line.
    ("substr", [st("abcdef"), nm(-3), nm(2)]),
    ("substr", [st("abcdef"), nm(-3), nm(0)]),
    ("substr", [st("abcdef"), nm(-100), nm(2)]),
    ("substr", [st("abcdef"), nm(0), nm(0)]),
    ("substr", [st("abcdef"), nm(6), nm(1)]),
    ("substr", [st("abcdef"), nm(2), nm(10)]),
    ("indent", [nm(2), st("a\nb")]),
    ("indent", [nm(0), st("a\nb")]),
    ("assertnotnull", [st("x")]),
    ("assertnotnull", [nm(1)]),
    # Grapheme clusters. `héllo` proves nothing about segmentation -- it
    # NFC-composes to one code point per character, which is why four functions
    # measured in code points for as long as they did. These do not compose.
    ("strlen", [st("abc")]),
    ("strlen", [st(FAMILY)]),
    ("strlen", [st(f"ab{FAMILY}cd")]),
    ("strlen", [st(FLAGS)]),
    ("strlen", [st(THUMB_TONED)]),
    ("strlen", [st(HANGUL_JAMO)]),
    ("strlen", [st(CONJUNCT)]),
    ("strlen", [st("")]),
    ("strlen", [st_uk("abc")]),
    ("strrev", [st(f"ab{FAMILY}cd")]),
    ("strrev", [st(FLAGS)]),
    ("strrev", [st(CONJUNCT)]),
    ("substr", [st(f"{FAMILY}xy"), nm(0), nm(1)]),
    ("substr", [st(f"{FAMILY}xy"), nm(1), nm(1)]),
    ("substr", [st(CONJUNCT), nm(0), nm(1)]),
    ("format", [st("%5s|"), st(FAMILY)]),
    ("format", [st("%-5s|"), st(FAMILY)]),
    ("format", [st("%.1s"), st(FAMILY)]),
    ("format", [st("%.1s"), st(CONJUNCT)]),
    ("format", [st("%q"), st(FAMILY)]),
    ("format", [st("%q"), st("héllo")]),
    # Literal text *before* the first verb. These rows agree trivially when
    # everything is known -- what they exist for is the unknown population,
    # where the deferred result is refined with the template's literal prefix
    # and `SafeKnownPrefix` decides whether the trailing delimiter survives
    # (`ctystrings/prefix.go:140` keeps it; until 2026-08-17 this package
    # dropped it, and no row could see the difference).
    ("format", [st("hi %s"), st("x")]),
    ("format", [st("id-%s"), st("x")]),
    ("format", [st("ab%s"), st("x")]),
    # regexp
    ("regex", [st("a(b)c"), st("abc")]),
    ("regex", [st("a(b)c"), st("zzz")]),
    ("regexall", [st("a(b)"), st("abab")]),
    ("regexall", [st("x"), st("y")]),
    ("regexreplace", [st("-ab-axxb-"), st("a(x*)b"), st("${1}W")]),
    ("regexreplace", [st("-ab-axxb-"), st("a(x*)b"), st("$1W")]),
    # numbers
    ("abs", [nm(-3)]),
    ("abs", [nm("3.5")]),
    ("ceil", [nm("1.2")]),
    ("ceil", [nm("-1.2")]),
    ("floor", [nm("1.8")]),
    ("floor", [nm("-1.8")]),
    ("signum", [nm(-5)]),
    ("signum", [nm(0)]),
    ("int", [nm("3.9")]),
    ("int", [nm("-3.9")]),
    ("add", [nm(1), nm(2)]),
    ("add", [nm("1.5"), nm("2.25")]),
    ("subtract", [nm(5), nm(2)]),
    ("subtract", [nm(2), nm(5)]),
    ("multiply", [nm(3), nm(4)]),
    ("multiply", [nm(-3), nm(4)]),
    ("divide", [nm(7), nm(2)]),
    ("divide", [nm(1), nm(3)]),
    ("modulo", [nm(7), nm(3)]),
    ("modulo", [nm(-7), nm(3)]),
    ("negate", [nm(3)]),
    ("negate", [nm(0)]),
    ("pow", [nm(2), nm(10)]),
    ("pow", [nm(2), nm("0.5")]),
    # go-cty computes `pow` in float64, so its answer carries that type's
    # rounding, its overflow to an infinity and its range refusal.
    ("pow", [nm("1.1"), nm(2)]),
    ("pow", [nm(10), nm(308)]),
    ("pow", [nm(10), nm(400)]),
    ("pow", [nm(10), nm(1000000)]),
    ("pow", [nm(10), nm(-1000000)]),
    ("pow", [nm(0), nm(0)]),
    ("pow", [nm(0), nm(-1)]),
    ("pow", [nm(-8), nm("0.5")]),
    ("pow", [nm("-0.0"), nm(-1)]),
    ("log", [nm(8), nm(2)]),
    ("max", [nm(1), nm(5)]),
    ("max", [nm(-1), nm(-5)]),
    ("max", [nm(1), nm(2), nm(3)]),
    ("min", [nm(1), nm(5)]),
    ("min", [nm(-1), nm(-5)]),
    ("min", [nm(1), nm(2), nm(3)]),
    ("parseint", [st("ff"), nm(16)]),
    ("parseint", [st("-10"), nm(10)]),
    # comparison and logic. Both boolean outcomes for every operator: until
    # 2026-08-17 each had exactly one row, all of them answering true, so a
    # comparison that always answered true would have swept clean.
    ("equal", [st("a"), st("a")]),
    ("equal", [st("a"), st("b")]),
    ("equal", [nm(1), nm("1.0")]),
    ("notequal", [st("a"), st("b")]),
    ("notequal", [st("a"), st("a")]),
    ("greaterthan", [nm(2), nm(1)]),
    ("greaterthan", [nm(1), nm(2)]),
    ("greaterthanorequalto", [nm(1), nm(1)]),
    ("greaterthanorequalto", [nm(1), nm(2)]),
    ("lessthan", [nm(1), nm(2)]),
    ("lessthan", [nm(2), nm(1)]),
    ("lessthanorequalto", [nm(1), nm(1)]),
    ("lessthanorequalto", [nm(2), nm(1)]),
    # Refined unknowns travelling *into* a function. The comparisons consult
    # the ranges and can answer while the value stays unknown; the arithmetic
    # and min/max rows pin the opposite -- however tight the bounds, functions
    # whose parameters do not admit an unknown answer a bare not-null unknown,
    # because go-cty's bound arithmetic lives on Value's operators, not here.
    ("lessthan", [nm_uk(upper=("10", False)), nm(20)]),
    ("lessthan", [nm_uk(lower=("10", True), upper=("20", True)), nm(15)]),
    ("greaterthan", [nm_uk(lower=("100", False)), nm(50)]),
    ("max", [nm_uk(upper=("10", False)), nm(20)]),
    ("min", [nm_uk(lower=("100", False)), nm(50)]),
    ("add", [nm_uk(lower=("0", False)), nm_uk(lower=("0", False))]),
    ("length", [ln_uk_len(3, 3)]),
    ("length", [ln_uk_len(1, 5)]),
    ("length", [ln_uk_len(2, None)]),
    ("coalescelist", [ln_uk_len(1, None), ls(["b"])]),
    # `cty.DynamicVal` at each interesting shape: unary, variadic-first,
    # collection position, index position, a type-callback that must unify it.
    # go-cty stops checking arguments at the first inexactly-typed one and the
    # framework port had this wrong for twenty functions, found by review
    # rather than by a row -- these are the rows that would have found it.
    ("not", [DYNAMIC_UK]),
    ("length", [DYNAMIC_UK]),
    ("coalesce", [DYNAMIC_UK, st("b")]),
    ("concat", [DYNAMIC_UK, ls(["b"])]),
    ("jsonencode", [DYNAMIC_UK]),
    ("format", [st("%s!"), DYNAMIC_UK]),
    ("equal", [DYNAMIC_UK, st("a")]),
    ("merge", [mp({"a": "1"}), DYNAMIC_UK]),
    ("element", [DYNAMIC_UK, nm(0)]),
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
    ("index", [ls(["a", "b"]), st("z")]),
    ("hasindex", [ls(["a"]), nm(0)]),
    ("hasindex", [ls(["a"]), nm(9)]),
    # A key `big.Float.Int64()` cannot read exactly names no position, so it is
    # a False rather than a truncation. `index` then refuses it.
    ("hasindex", [ls(["a", "b", "c"]), nm(1.5)]),
    ("hasindex", [ls(["a", "b", "c"]), nm(-1)]),
    ("hasindex", [ls(["a", "b", "c"]), nm(1e30)]),
    ("index", [ls(["a", "b", "c"]), nm(1.5)]),
    ("index", [ls(["a", "b", "c"]), nm(1)]),
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
    # The empty collection, for every function whose answer's *shape* turns on
    # it. Until 2026-08-17 sixteen collection functions had never been handed
    # one: the interesting part is usually the result type -- an empty result
    # still has to name an element type, and the two implementations derive it
    # by different routes.
    ("distinct", [ls([])]),
    ("compact", [ls([])]),
    ("concat", [ls([]), ls([])]),
    ("contains", [ls([]), st("a")]),
    ("element", [ls([]), nm(0)]),
    ("flatten", [ls([])]),
    ("length", [ls([])]),
    ("lookup", [mp({}), st("a"), st("z")]),
    ("reverselist", [ls([])]),
    ("setintersection", [se([]), se([])]),
    ("setsubtract", [se([]), se(["a"])]),
    ("slice", [ls([]), nm(0), nm(0)]),
    ("sort", [ls([])]),
    ("zipmap", [ls([]), ls([])]),
    ("chunklist", [ls([]), nm(2)]),
    # Containers holding an unknown element. Every row below was unreachable
    # until 2026-08-17 -- the container collapsed to a wholly unknown value on
    # construction, so these functions had never been driven with the ordinary
    # plan-time shape at all. A list's length is decided by its own structure;
    # a set's is not, because an unknown element may still resolve to a value
    # equal to another member, so go-cty answers with bounds rather than a count.
    ("length", [ls_uk("a", UK)]),
    ("length", [se_uk("z", UK)]),
    ("length", [se_uk(UK, UK)]),
    ("length", [se_uk(UK)]),
    ("length", [se_uk("a", "b", UK)]),
    ("contains", [ls_uk("a", UK), st("a")]),
    ("contains", [ls_uk("a", UK), st("zzz")]),
    ("contains", [se_uk("z", UK), st("z")]),
    ("contains", [se_uk("z", UK), st("zzz")]),
    ("distinct", [ls_uk("a", UK)]),
    ("distinct", [ls_uk(UK, UK)]),
    ("compact", [ls_uk("a", UK)]),
    ("join", [st("-"), ls_uk("a", UK)]),
    ("jsonencode", [ls_uk("a", UK)]),
    ("keys", [mp({"a": "1"})]),
    ("reverselist", [ls_uk("a", UK)]),
    ("concat", [ls_uk("a", UK), ls(["b"])]),
    ("slice", [ls_uk("a", UK), nm(0), nm(1)]),
    ("element", [ls_uk("a", UK), nm(0)]),
    ("element", [ls_uk("a", UK), nm(1)]),
    ("flatten", [ls_uk("a", UK)]),
    ("coalescelist", [ls_uk("a", UK), ls(["b"])]),
    ("chunklist", [ls_uk("a", UK), nm(1)]),
    ("zipmap", [ls(["a", "b"]), ls_uk("z", UK)]),
    ("setunion", [se_uk("z", UK), se(["q"])]),
    ("setintersection", [se_uk("z", UK), se(["z", "q"])]),
    ("sort", [ls_uk("a", UK)]),
    ("formatlist", [st("%s!"), ls_uk("a", UK)]),
    # A set holding an unknown element has an undecided *length* -- the unknown
    # may coalesce with a member -- so go-cty defers the whole list where a
    # list-typed argument only defers the affected rows. Both shapes measured
    # as divergences on 2026-08-17.
    ("formatlist", [st("<%s>"), se_uk("z", UK)]),
    ("formatlist", [st("%s%s"), ls_uk("a", UK), ls(["x", "y"])]),
    ("coalesce", [st(""), st("b")]),
    ("coalesce", [st("a"), st("b")]),
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
    # jsonencode had four cases here, and its only known-value list case was
    # ["a"] -- a single element, which cannot show a separator. Go writes
    # `["a","b"]` and Python `["a", "b"]`; go sorts object keys and escapes
    # `<`, `>`, `&` while leaving non-ASCII alone, and Python does the reverse
    # on both. Every one of those lands in state and is compared as text.
    ("jsonencode", [ls(["a", "b"])]),
    ("jsonencode", [ob({"b": "x", "a": "y"})]),
    ("jsonencode", [mp({"z": "1", "a": "2"})]),
    ("jsonencode", [st("a<b>&c")]),
    ("jsonencode", [st("héllo")]),
    ("jsonencode", [st('a"b\\c')]),
    ("jsonencode", [nm("0.00001")]),
    ("jsonencode", [nm("1e21")]),
    ("jsonencode", [bl(True)]),
    ("jsonencode", [ln(["1", "2"])]),
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
    # The ends of the range, where Go's time.Time keeps going and Python's
    # datetime stops. Recorded divergences, not agreements -- see KNOWN_DIVERGENCES.
    ("timeadd", [st("9999-12-31T23:59:59Z"), st("1h")]),
    ("timeadd", [st("0001-01-01T00:00:00Z"), st("-1s")]),
    # The duration overflow boundary, where the two *do* agree: Go's
    # time.Duration is int64 nanoseconds, and this package's parser enforces the
    # same limit rather than inheriting timedelta's much wider one.
    ("timeadd", [st("2026-01-01T00:00:00Z"), st("2560000h")]),
    ("timeadd", [st("2026-01-01T00:00:00Z"), st("2570000h")]),
    ("formatdate", [st("YYYY-MM-DD"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("EEEE, DD MMMM YYYY hh:mm:ss ZZZZ"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("HH:mm aa Z"), st("2020-11-22T13:04:05-08:00")]),
    ("formatdate", [st("'it''s' YYYY"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("YYY"), st("2020-01-02T03:04:05Z")]),
    # A Go reference layout, which go-cty returns as literal text and this
    # package refuses. The one place it declines something go-cty answers --
    # see KNOWN_DIVERGENCES for why. The quoted form is the escape, and agrees.
    ("formatdate", [st("2006-01-02"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("'2006-01-02'"), st("2020-01-02T03:04:05Z")]),
    ("formatdate", [st("2006"), st("2020-01-02T03:04:05Z")]),
    # An infinite number through every verb that renders one. go-cty spells it
    # `+Inf` -- `big.Float.Text`'s answer -- where `str(Decimal)` says
    # "Infinity", and the float verbs drop the zero flag for it while `%v` and
    # `%s` keep it, because only the former delegate to Go's own fmt.
    ("format", [st("%v"), nm_inf()]),
    ("format", [st("%f"), nm_inf()]),
    ("format", [st("%e"), nm_inf()]),
    ("format", [st("%g"), nm_inf()]),
    ("format", [st("%s"), nm_inf()]),
    ("format", [st("%08.2f"), nm_inf()]),
    ("format", [st("%08v"), nm_inf()]),
    ("format", [st("%10.2f"), nm_inf()]),
    ("format", [st("% f"), nm_inf()]),
    ("format", [st("%v"), nm_inf(negative=True)]),
    ("format", [st("%f"), nm_inf(negative=True)]),
    ("format", [st("% f"), nm_inf(negative=True)]),
    ("format", [st("%d"), nm_inf()]),
    ("format", [st("%#v"), nm_inf()]),
    ("formatdate", [st("YYYY"), st("2020-01-02 03:04:05Z")]),
    # format
    ("format", [st("%s"), st("hi")]),
    ("format", [st("%q"), st('a"b')]),
    ("format", [st("%v"), st("hi")]),
    ("format", [st("%v"), nm(42)]),
    # %v is the default verb and picks between %e and %f on a threshold Go fixes
    # at 6 regardless of how many digits it is about to print. Deriving it from
    # the value's own significant digits rendered every round number
    # exponentially -- 10 as "1e+01" -- and 1234567 non-exponentially.
    ("format", [st("%v"), nm(10)]),
    ("format", [st("%v"), nm(100)]),
    ("format", [st("%v"), nm(1500)]),
    ("format", [st("%v"), nm(250000)]),
    ("format", [st("%v"), nm(1234567)]),
    ("format", [st("%v"), nm(12345678)]),
    # Integer flags: precision and the alternate form were parsed and never
    # read, and `-` did not cancel zero-padding, so %-05d of 42 gave "42000".
    ("format", [st("%-05d"), nm(42)]),
    ("format", [st("%0-5d"), nm(42)]),
    ("format", [st("%-08d"), nm(42)]),
    ("format", [st("%.5d"), nm(42)]),
    ("format", [st("%05.2d"), nm(42)]),
    ("format", [st("%.5x"), nm(42)]),
    ("format", [st("%-05x"), nm(255)]),
    ("format", [st("%#x"), nm(42)]),
    ("format", [st("%#X"), nm(255)]),
    ("format", [st("%#o"), nm(42)]),
    ("format", [st("%#b"), nm(42)]),
    ("format", [st("%10t"), bl(True)]),
    ("format", [st("%-10t"), bl(False)]),
    ("format", [st("%v"), nm("0.00001")]),
    ("format", [st("%#v"), nm("0.00001")]),
    ("format", [st("%#v"), ls(["a", "b"])]),
    ("format", [st("%v"), ln(["0.00001"])]),
    ("format", [st("%v"), mp({"z": "1", "a": "2"})]),
    ("format", [st("%v"), ob({"b": "2", "a": "1"})]),
    ("format", [st("%v"), se(["b", "a"])]),
    ("format", [st("%.1e"), nm("9.99")]),
    ("format", [st("%+.1f"), nm("1.5")]),
    ("format", [st("% .1f"), nm("1.5")]),
    ("format", [st("%.0g"), nm(123)]),
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
            reported = json.loads(line)
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
