#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The msgpack wire codec, compared byte for byte -- unknowns included.

`test_tofusoup_compat.py` already round-trips values through this codec, but it
builds them from plain JSON and so cannot express an unknown. That is precisely
what Terraform puts on the wire for an attribute it has not decided yet, and
since Terraform 1.6 those unknowns carry *refinements*: not null, this prefix,
at least this long. None of it was ever compared.

Two divergences came out of the first run, both invisible to a round trip
because go-cty reads this library's bytes back correctly:

  - a bare unknown was written as an empty ext payload, `c7 00 00`, where go-cty
    writes the fixext1 `d4 00 00` it calls "the most compact possible
    representation"
  - a refined number bound was written as raw UTF-8 *binary*, where go-cty
    encodes the bound through its ordinary number marshaller and writes 3 as an
    integer

Values agreed and bytes did not, which is the whole failure mode: Terraform
compares serialized state, so a difference no decoder notices is still a diff on
every plan.

A third was in the harness -- it built refinement bounds with a default-precision
`big.Float`, so a bound past 2^64 came back rounded and looked like this
library losing precision.
"""

from __future__ import annotations

import base64
import json
from typing import Any

import pytest

from pyvider.cty import (
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
from pyvider.cty.codec import cty_from_msgpack, cty_to_msgpack
from pyvider.cty.refinement import refine
from tests.compatibility._oracle import canonical, rich, run, type_spec

pytestmark = pytest.mark.compat

S = CtyString()
N = CtyNumber()
STRINGS = CtyList(element_type=S)
STRING_SET = CtySet(element_type=S)
STRING_MAP = CtyMap(element_type=S)
PAIR = CtyObject(attribute_types={"a": S, "b": N})
TUPLE = CtyTuple(element_types=(S, N))

UNKNOWN_STRING = CtyValue.unknown(S)
UNKNOWN_NUMBER = CtyValue.unknown(N)
UNKNOWN_LIST = CtyValue.unknown(STRINGS)

CASES: list[tuple[str, CtyType[Any], CtyValue[Any]]] = [
    ("a string", S, S.validate("x")),
    ("a null", S, CtyValue.null(S)),
    ("a number", N, N.validate(1)),
    ("a fraction", N, N.validate("1.5")),
    ("a number past 2**53", N, N.validate("9007199254740993")),
    # Unknowns, which is what this module exists for.
    ("a bare unknown", S, UNKNOWN_STRING),
    ("an unknown number", N, UNKNOWN_NUMBER),
    ("an unknown list", STRINGS, UNKNOWN_LIST),
    ("a not-null unknown", S, refine(UNKNOWN_STRING).not_null().new_value()),
    ("a prefixed unknown", S, refine(UNKNOWN_STRING).string_prefix("http").new_value()),
    ("a lower-bounded number", N, refine(UNKNOWN_NUMBER).number_range_lower_bound(3).new_value()),
    (
        "an exclusive lower bound",
        N,
        refine(UNKNOWN_NUMBER).number_range_lower_bound(3, inclusive=False).new_value(),
    ),
    ("both number bounds", N, refine(UNKNOWN_NUMBER).number_range_inclusive(1, 10).new_value()),
    ("a fractional bound", N, refine(UNKNOWN_NUMBER).number_range_lower_bound("1.5").new_value()),
    ("a bound past 2**64", N, refine(UNKNOWN_NUMBER).number_range_lower_bound(2**70).new_value()),
    ("a negative bound", N, refine(UNKNOWN_NUMBER).number_range_lower_bound(-5).new_value()),
    ("a length lower bound", STRINGS, refine(UNKNOWN_LIST).collection_length_lower_bound(2).new_value()),
    (
        "both length bounds",
        STRINGS,
        refine(UNKNOWN_LIST).collection_length_lower_bound(2).collection_length_upper_bound(5).new_value(),
    ),
    ("an exact length", STRINGS, refine(UNKNOWN_LIST).collection_length(3).new_value()),
    ("a not-null unknown collection", STRINGS, refine(UNKNOWN_LIST).not_null().new_value()),
    # Unknowns at depth.
    ("an unknown inside a list", STRINGS, STRINGS.validate(["a", UNKNOWN_STRING])),
    ("an unknown attribute", PAIR, PAIR.validate({"a": UNKNOWN_STRING, "b": 1})),
    ("an unknown tuple element", TUPLE, TUPLE.validate([UNKNOWN_STRING, 1])),
    ("an unknown map value", STRING_MAP, STRING_MAP.validate({"k": UNKNOWN_STRING})),
    (
        "a refined unknown inside a list",
        STRINGS,
        STRINGS.validate([refine(UNKNOWN_STRING).not_null().new_value()]),
    ),
    # An unknown's *position* is part of the bytes, so both orders are pinned.
    # Until 2026-08-17 neither of these could be expressed: the container took
    # its unknown-ness from the element and encoded as a bare `d4 00 00`, so
    # every case above was really testing a wholly unknown container and
    # agreeing with go-cty for the wrong reason.
    ("an unknown last in a list", STRINGS, STRINGS.validate(["a", UNKNOWN_STRING])),
    ("an unknown first in a list", STRINGS, STRINGS.validate([UNKNOWN_STRING, "a"])),
    ("a list of nothing but unknowns", STRINGS, STRINGS.validate([UNKNOWN_STRING, UNKNOWN_STRING])),
    (
        "an unknown nested two deep",
        CtyList(element_type=STRINGS),
        CtyList(element_type=STRINGS).validate([["a", UNKNOWN_STRING]]),
    ),
    # Sets are the hard case: go-cty keeps two unknowns as two distinct members
    # (`set_internals.go` -- unknowns are never equivalent to one another), and
    # orders knowns first, then unknowns, then nulls. A frozenset payload could
    # hold neither the multiplicity nor the order.
    ("a set holding one unknown", STRING_SET, STRING_SET.validate(["z", UNKNOWN_STRING])),
    ("a set holding two unknowns", STRING_SET, STRING_SET.validate([UNKNOWN_STRING, UNKNOWN_STRING])),
    (
        "a set holding a known, an unknown and a null",
        STRING_SET,
        STRING_SET.validate(["a", UNKNOWN_STRING, CtyValue.null(S)]),
    ),
    # Ordinary containers, so the unknown cases are not the only coverage here.
    ("a list", STRINGS, STRINGS.validate(["a", "b"])),
    ("a set", STRING_SET, STRING_SET.validate(["b", "a"])),
    ("a set holding a null", STRING_SET, STRING_SET.validate(["a", CtyValue.null(S)])),
    # Composite elements where one is a *prefix* of another. The only shape
    # whose set ordering ever disagreed with go-cty once the null rank was
    # fixed: a plain tuple comparison sorts a prefix first, go-cty sorts it
    # last, and only a byte comparison sees it. The empty element is the
    # extreme case, being a prefix of everything.
    (
        "a set of lists where one is a prefix of another",
        CtySet(element_type=CtyList(element_type=S)),
        CtySet(element_type=CtyList(element_type=S)).validate([["a"], ["a", "c"], ["b"]]),
    ),
    (
        "a set of lists holding an empty one",
        CtySet(element_type=CtyList(element_type=S)),
        CtySet(element_type=CtyList(element_type=S)).validate([["b"], [], ["a", "c"]]),
    ),
    (
        "a set of maps of differing size",
        CtySet(element_type=CtyMap(element_type=S)),
        CtySet(element_type=CtyMap(element_type=S)).validate([{"k": "b"}, {}, {"k": "a"}]),
    ),
    ("a map", STRING_MAP, STRING_MAP.validate({"b": "2", "a": "1"})),
    ("an object", PAIR, PAIR.validate({"a": "x", "b": 1})),
]

IDS = [case[0] for case in CASES]


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_the_encoded_bytes_are_identical(label: str, cty_type: CtyType[Any], value: CtyValue[Any]) -> None:
    theirs = run("cty", "msgpack", "encode", "--type", type_spec(cty_type), json.dumps(rich(value)))
    assert theirs["ok"], theirs

    here = base64.b64encode(cty_to_msgpack(value, cty_type)).decode()
    assert here == theirs["base64"], f"{label}: {theirs['hex']} there"


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_go_cty_reads_back_what_this_library_wrote(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    """The other half, and it is not implied by the first.

    Identical bytes mean go-cty must read them the same way -- but a codec can
    also write bytes go-cty accepts and reads as something else, which is the
    failure a round trip inside one implementation cannot see.
    """
    encoded = base64.b64encode(cty_to_msgpack(value, cty_type)).decode()

    theirs = run("cty", "msgpack", "decode", "--type", type_spec(cty_type), encoded)
    assert theirs["ok"], theirs

    assert canonical(theirs["value"]) == canonical(rich(value)), label


@pytest.mark.parametrize(("label", "cty_type", "value"), CASES, ids=IDS)
def test_this_library_reads_back_what_go_cty_wrote(
    label: str, cty_type: CtyType[Any], value: CtyValue[Any]
) -> None:
    theirs = run("cty", "msgpack", "encode", "--type", type_spec(cty_type), json.dumps(rich(value)))
    assert theirs["ok"], theirs

    decoded = cty_from_msgpack(base64.b64decode(theirs["base64"]), cty_type)

    assert canonical(rich(decoded)) == canonical(rich(value)), label


def test_a_long_string_prefix_is_truncated_the_same_way() -> None:
    """go-cty caps the prefix so the refinement blob stays under its own limit.

    The cut is followed by a safe-prefix trim, because truncating mid-cluster
    would leave a prefix a later character could combine with -- the one place
    where "make it shorter" and "keep it correct" are the same operation.
    """
    value = refine(CtyValue.unknown(S)).string_prefix("a" * 400).new_value()

    theirs = run("cty", "msgpack", "encode", "--type", type_spec(S), json.dumps(rich(value)))
    assert theirs["ok"], theirs

    assert base64.b64encode(cty_to_msgpack(value, S)).decode() == theirs["base64"]


# 🌊🪢🔚
