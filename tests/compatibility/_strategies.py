#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Generated `(type, value)` pairs for the differential property suite.

This repository had property-based testing and differential testing and had
never put them together: `tests/property_based/` runs sixteen hypothesis modules
and **none of them drive the oracle**, while `tests/compatibility/` compares
against real go-cty across 2595 tests and **none of them generate an input**.
Every case there is hand-written, and a hand-written case can only find a
divergence somebody already suspected.

Three bugs on 2026-08-19 came from closing that gap, none of which the table had
found: set elements ordering differently when one is a prefix of another, an
empty string prefix and a zero length lower bound written as refinements go-cty
does not record, and an unsatisfiable number range accepted. The set one needed
232 generated sets to characterise -- the rule is invisible from any single
example, because it only shows when two elements happen to be prefix-related.

**Shapes are biased, deliberately.** Uniform random values mostly re-test the
scalar paths that have never been wrong. The generators below over-produce what
has historically broken: prefix-related elements inside sets, empty containers,
degenerate refinements, strings whose graphemes are not their code points, and
numbers near a representation boundary.

Two things are kept out on purpose:

  * **Numbers past 154 significant digits.** go-cty renders through a 512-bit
    `big.Float`, so it spells at most that many; the divergence is recorded in
    `KNOWN_DIVERGENCES` and generating it here would make the suite permanently
    red rather than informative.
  * **Marks.** Serializing a marked value is refused by both implementations by
    design, so a codec property has nothing to compare. `test_stdlib_marked_sweep`
    covers marks where they are observable.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from hypothesis import strategies as st

from pyvider.cty import (
    CtyBool,
    CtyDynamic,
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
from pyvider.cty.refinement import refine

S = CtyString()
N = CtyNumber()
B = CtyBool()

Case = tuple[CtyType[Any], CtyValue[Any]]

# Strings whose grapheme clusters are not their code points, plus the ones that
# have to survive a wire: an embedded NUL, a lone combining mark, both spellings
# of an accented character, and the characters Go escapes in JSON and Python
# does not.
AWKWARD_STRINGS = [
    "",
    "\x00",
    "a\x00b",
    "\r\n",
    "\t",
    '"',
    "\\",
    "a<b>&c",
    "é",
    "é",
    "क्ष",
    "👨‍👩‍👧‍👦",
    "🇺🇸🇯🇵",
    "👍🏽",
    "각",
    "ﬁ",
    "straße",
    "ΣΣ",
    "İ",
    " leading and trailing ",
    "a" * 300,
]

# Numbers that sit near a boundary one implementation or the other cares about,
# all inside go-cty's 154-significant-digit rendering width.
POINTED_NUMBERS = [
    Decimal(0),
    Decimal("-0.0"),
    Decimal(1),
    Decimal(-1),
    Decimal("1.50"),
    Decimal("1E+2"),
    Decimal("1e-30"),
    Decimal("0.1"),
    Decimal(2**53),
    Decimal(2**53 + 1),
    Decimal(2**63 - 1),
    Decimal(-(2**63)),
    Decimal(2**100),
    Decimal("1.2345678901234567890123456789"),
    Decimal(5**220),
]

strings = st.one_of(
    st.sampled_from(AWKWARD_STRINGS),
    st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=40),
)
# A map key is barred from starting with `$`, and this is a limit of the
# *harness dialect* rather than of either implementation: the rich JSON both
# ends speak marks unknowns and nulls with `$`-prefixed sentinels, and the
# harness says so -- `key "$" cannot be expressed: it collides with a
# rich-value sentinel`. Both encode such a map identically (`81a124a0`); only
# the comparison channel cannot carry it.
map_keys = strings.filter(lambda key: not key.startswith("$"))
numbers = st.one_of(
    st.sampled_from(POINTED_NUMBERS),
    st.integers(min_value=-(2**120), max_value=2**120).map(Decimal),
)
scalar_types = st.sampled_from([S, N, B])


def _scalar_of(cty_type: CtyType[Any]) -> st.SearchStrategy[Any]:
    if isinstance(cty_type, CtyString):
        return strings
    if isinstance(cty_type, CtyNumber):
        return numbers
    return st.booleans()


@st.composite
def scalars(draw: Any) -> Case:
    """A known, null, or bare-unknown scalar."""
    cty_type = draw(scalar_types)
    kind = draw(st.sampled_from(["known", "known", "known", "null", "unknown"]))
    if kind == "null":
        return cty_type, CtyValue.null(cty_type)
    if kind == "unknown":
        return cty_type, CtyValue.unknown(cty_type)
    return cty_type, cty_type.validate(draw(_scalar_of(cty_type)))


@st.composite
def refined_unknowns(draw: Any) -> Case:
    """An unknown carrying refinements, including the degenerate ones.

    An empty prefix and a zero length bound are generated on purpose: both were
    written to the wire where go-cty writes a bare unknown, and both are cheap
    to regress.
    """
    kind = draw(st.sampled_from(["prefix", "number-range", "length", "not-null"]))
    if kind == "prefix":
        builder = refine(CtyValue.unknown(S)).string_prefix_full(
            draw(st.sampled_from(["", "a", "s3://", "🔥", "क्ष"]))
        )
        if draw(st.booleans()):
            builder = builder.not_null()
        return S, builder.new_value()
    if kind == "number-range":
        builder = refine(CtyValue.unknown(N))
        low, high = draw(st.sampled_from([(0, 10), (-5, None), (None, 100), (3, 3), (0, None)]))
        if low is not None:
            builder = builder.number_range_lower_bound(Decimal(low), inclusive=True)
        if high is not None:
            builder = builder.number_range_upper_bound(Decimal(high), inclusive=True)
        return N, builder.new_value()
    if kind == "length":
        cty_type = draw(
            st.sampled_from([CtyList(element_type=S), CtySet(element_type=S), CtyMap(element_type=S)])
        )
        builder = refine(CtyValue.unknown(cty_type))
        low, high = draw(st.sampled_from([(0, None), (0, 5), (1, 5), (None, 3), (2, 2)]))
        if low is not None:
            builder = builder.collection_length_lower_bound(low)
        if high is not None:
            builder = builder.collection_length_upper_bound(high)
        return cty_type, builder.new_value()
    cty_type = draw(scalar_types)
    return cty_type, refine(CtyValue.unknown(cty_type)).not_null().new_value()


def _members(element_type: CtyType[Any]) -> st.SearchStrategy[Any]:
    """An element that may itself be null or unknown, which containers must keep."""
    return st.one_of(
        _scalar_of(element_type).map(element_type.validate),
        st.just(CtyValue.null(element_type)),
        st.just(CtyValue.unknown(element_type)),
    )


@st.composite
def flat_collections(draw: Any) -> Case:
    """A list, set, or map of scalars, holding nulls and unknowns."""
    element_type = draw(scalar_types)
    kind = draw(st.sampled_from(["list", "set", "map"]))
    if kind == "map":
        cty_type: CtyType[Any] = CtyMap(element_type=element_type)
        keys = draw(st.lists(map_keys, max_size=5, unique=True))
        return cty_type, cty_type.validate({key: draw(_members(element_type)) for key in keys})
    cty_type = CtyList(element_type=element_type) if kind == "list" else CtySet(element_type=element_type)
    return cty_type, cty_type.validate(draw(st.lists(_members(element_type), max_size=6)))


@st.composite
def sets_of_sequences(draw: Any) -> Case:
    """The shape whose ordering rule diverged, drawn from a tiny alphabet.

    Three letters and a short length, so that generated elements are *prefixes*
    of one another often rather than by luck -- which is the only condition
    under which the two orderings differ at all.
    """
    element_type = CtyList(element_type=S)
    cty_type = CtySet(element_type=element_type)
    rows = draw(
        st.lists(
            st.lists(st.sampled_from(["a", "b", "c"]), max_size=4),
            max_size=5,
            unique_by=lambda row: tuple(row),
        )
    )
    return cty_type, cty_type.validate(rows)


@st.composite
def structural(draw: Any) -> Case:
    """An object, an object with optional attributes, or a tuple."""
    kind = draw(st.sampled_from(["object", "optional", "tuple"]))
    if kind == "tuple":
        cty_type: CtyType[Any] = CtyTuple(element_types=(S, N, CtyList(element_type=B)))
        return cty_type, cty_type.validate(
            [draw(strings), draw(numbers), draw(st.lists(st.booleans(), max_size=3))]
        )
    attributes = {"a": S, "b": N, "c": CtyList(element_type=S)}
    optional = frozenset({"c"}) if kind == "optional" else frozenset()
    cty_type = CtyObject(attribute_types=attributes, optional_attributes=optional)
    payload: dict[str, Any] = {"a": draw(_members(S)), "b": draw(_members(N))}
    if kind != "optional" or draw(st.booleans()):
        payload["c"] = draw(st.lists(strings, max_size=3))
    return cty_type, cty_type.validate(payload)


@st.composite
def nested(draw: Any) -> Case:
    """A container inside a container, and a dynamic-typed position."""
    kind = draw(st.sampled_from(["list-of-lists", "map-of-lists", "object-of-collections", "dynamic"]))
    if kind == "list-of-lists":
        cty_type: CtyType[Any] = CtyList(element_type=CtyList(element_type=S))
        return cty_type, cty_type.validate(draw(st.lists(st.lists(strings, max_size=3), max_size=3)))
    if kind == "map-of-lists":
        cty_type = CtyMap(element_type=CtyList(element_type=N))
        keys = draw(st.lists(strings, max_size=3, unique=True))
        return cty_type, cty_type.validate({key: draw(st.lists(numbers, max_size=3)) for key in keys})
    if kind == "object-of-collections":
        cty_type = CtyObject(
            attribute_types={"rows": CtyList(element_type=S), "tally": CtyMap(element_type=N)}
        )
        return cty_type, cty_type.validate(
            {
                "rows": draw(st.lists(strings, max_size=3)),
                "tally": {key: draw(numbers) for key in draw(st.lists(map_keys, max_size=2, unique=True))},
            }
        )
    inner = draw(
        st.sampled_from(
            [
                S.validate("x"),
                N.validate(1),
                CtyValue.unknown(S),
                CtyValue.null(N),
                CtyList(element_type=S).validate(["a", "b"]),
            ]
        )
    )
    # Through `validate`, not handed over raw: a `CtyDynamic`-typed value holds
    # a `CtyValue`, and the codec says so rather than guessing.
    return CtyDynamic(), CtyDynamic().validate(inner)


def cases() -> st.SearchStrategy[Case]:
    """Every shape, weighted toward the ones that have actually been wrong."""
    return st.one_of(
        scalars(),
        refined_unknowns(),
        flat_collections(),
        sets_of_sequences(),
        structural(),
        nested(),
    )


# 🌊🪢🔚
