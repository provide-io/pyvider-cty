#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The argument builders the stdlib sweep is written in.

Split out of `test_stdlib_sweep.py`, which was over twice this repository's
500-line ceiling for a test file. Nothing here drives anything: it is the
vocabulary the case tables in `_sweep_cases_scalar` and `_sweep_cases_collection`
are written in, and each builder produces one argument in both dialects at once
so the two implementations cannot be handed different values.
"""

from __future__ import annotations

import base64
from decimal import Decimal
from typing import Any

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
from pyvider.cty.refinement import refine
from pyvider.cty.types import BytesCapsule

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

# 🌊🪢🔚
