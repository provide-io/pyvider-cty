#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The values stdlib arguments are drawn from, and the region they stay inside.

`_strategies` generates values for the *codec* properties, where the question is
whether two implementations spell the same value the same way. This generates
values to be *arguments*, where the question is whether two implementations
compute the same answer -- and the two want different pools, because a function
can diverge on an input the codecs agree about.

**The region.** Everything here is drawn from the region where the two number
models agree by construction. go-cty holds a number in a 512-bit `big.Float` and
this package holds a `Decimal`, so the two agree exactly on integers and on
binary fractions that fit that width, and disagree in the last digits everywhere
else -- `multiply(0.1, 0.1)` is go-cty's 0.010000...0001 against this package's
0.01, which is neither implementation being wrong. That divergence is recorded
against `divide(1,3)` in the sweep's `KNOWN_DIVERGENCES` and closed as a
decision; generating into it would make this suite permanently red instead of
informative. So integers stay under forty digits, fractions are sixteenths, and
the infinities -- which both models hold exactly -- are in.

Three more exclusions, each one a divergence that is recorded elsewhere:

  * **The Indic conjunct.** `क्ष` is one grapheme cluster under Unicode 15.1 and
    later and two under 15.0, which is what the oracle's `go-textseg` build has.
    Four sweep rows pin it; generating it would re-report it on every string
    function that counts clusters.
  * **NaN.** Both codecs refuse it now, so a function answering one would raise
    out of the comparison rather than diverge from go-cty. `test_non_finite_numbers`
    holds that boundary.
  * **Marks.** `test_stdlib_marked_sweep` drives them across the whole argument
    table already, and a mark has no wire form to compare.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from hypothesis import strategies as st

from pyvider.cty import (
    CtyBool,
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
from pyvider.cty.types import BytesCapsule

S, N, B = CtyString(), CtyNumber(), CtyBool()

# Strings that have historically carried information through a function
# differently on the two sides: graphemes that are not code points, both
# spellings of an accented character, the case-mapping oddities, and the
# characters one language's JSON escapes and the other's does not.
AWKWARD_STRINGS = [
    "",
    " ",
    "a",
    "\x00",
    "\r\n",
    "\t",
    '"',
    "\\",
    "a<b>&c",
    "é",
    "é",
    "👨‍👩‍👧‍👦",
    "🇺🇸🇯🇵",
    "👍🏽",
    "각",
    "ﬁ",
    "straße",
    "ΣΣ",
    "İ",
    " padded ",
    "a,b,c",
    "one two three",
    "x" * 60,
]

strings = st.one_of(
    st.sampled_from(AWKWARD_STRINGS),
    st.text(alphabet=st.characters(blacklist_categories=("Cs",)), max_size=24),
)

# A map key cannot start with `$`: the harness dialect marks unknowns and nulls
# with `$`-prefixed sentinels and refuses a map that collides with one. A limit
# of the comparison channel, not of either implementation -- see `_strategies`.
map_keys = strings.filter(lambda key: not key.startswith("$"))

# An attribute name for a generated object. Kept plain, because an object type
# is spelled into the harness as a type as well as a value and the point of the
# generator is the *shape* rather than the naming.
attribute_names = st.sampled_from(["a", "b", "c", "name", "count"])

# Numbers at a boundary one implementation or the other has cared about, all
# integers or exact binary fractions, all inside the width both models hold.
POINTED_NUMBERS = [
    Decimal(0),
    Decimal("-0.0"),
    Decimal(1),
    Decimal(-1),
    Decimal("0.5"),
    Decimal("-0.5"),
    Decimal("1.5"),
    Decimal(2**53),
    Decimal(2**53 + 1),
    Decimal(2**63 - 1),
    Decimal(-(2**63)),
    Decimal(2**100 + 1),
    Decimal("Infinity"),
    Decimal("-Infinity"),
]

# Forty digits is about 133 bits, so a sum stays exact and a product of two of
# them is still well inside the 512 both models hold exactly.
integers = st.integers(min_value=-(10**40), max_value=10**40).map(Decimal)
# Sixteenths: an exact binary fraction, so both models hold it and every sum,
# difference and product of two of them exactly.
fractions = st.integers(min_value=-2048, max_value=2048).map(lambda i: Decimal(i) / 16)

numbers = st.one_of(st.sampled_from(POINTED_NUMBERS), integers, fractions)

# An index or a length. Negative and past-the-end on purpose: the interesting
# question about `element`, `slice` and `substr` is what they do at the edges,
# and both implementations should refuse or wrap the same way.
indices = st.integers(min_value=-4, max_value=9).map(Decimal)
# A count that a function will build a collection out of, kept small so that
# `range` and `setproduct` cannot generate something enormous.
sizes = st.integers(min_value=-2, max_value=5).map(Decimal)

byte_buffers = st.binary(max_size=16)

scalar_types: st.SearchStrategy[CtyType[Any]] = st.sampled_from([S, N, B])


def scalar_payload(cty_type: CtyType[Any]) -> st.SearchStrategy[Any]:
    """The raw Python payload for a scalar of `cty_type`."""
    if isinstance(cty_type, CtyString):
        return strings
    if isinstance(cty_type, CtyNumber):
        return numbers
    return st.booleans()


def scalars(cty_type: CtyType[Any] | None = None) -> st.SearchStrategy[CtyValue[Any]]:
    """A known scalar value, of a given type or of any of the three."""
    if cty_type is not None:
        return scalar_payload(cty_type).map(cty_type.validate)
    return scalar_types.flatmap(lambda t: scalar_payload(t).map(t.validate))


def members(element_type: CtyType[Any], *, unknowns: bool = True) -> st.SearchStrategy[CtyValue[Any]]:
    """An element that may itself be null or unknown.

    Both are the ordinary plan-time shape -- a list one of whose elements is not
    yet computed -- and until the sweep grew `ls_uk` no function here had ever
    been handed one.
    """
    known = scalar_payload(element_type).map(element_type.validate)
    if not unknowns:
        return st.one_of(known, st.just(CtyValue.null(element_type)))
    return st.one_of(
        known,
        known,
        st.just(CtyValue.null(element_type)),
        st.just(CtyValue.unknown(element_type)),
    )


@st.composite
def lists(
    draw: Any, element_type: CtyType[Any] | None = None, *, unknowns: bool = True, max_size: int = 4
) -> CtyValue[Any]:
    element_type = element_type if element_type is not None else draw(scalar_types)
    return CtyList(element_type=element_type).validate(
        draw(st.lists(members(element_type, unknowns=unknowns), max_size=max_size))
    )


@st.composite
def sets(
    draw: Any, element_type: CtyType[Any] | None = None, *, unknowns: bool = True, max_size: int = 4
) -> CtyValue[Any]:
    element_type = element_type if element_type is not None else draw(scalar_types)
    return CtySet(element_type=element_type).validate(
        draw(st.lists(members(element_type, unknowns=unknowns), max_size=max_size))
    )


@st.composite
def maps(
    draw: Any, element_type: CtyType[Any] | None = None, *, unknowns: bool = True, max_size: int = 3
) -> CtyValue[Any]:
    element_type = element_type if element_type is not None else draw(scalar_types)
    keys = draw(st.lists(map_keys, max_size=max_size, unique=True))
    return CtyMap(element_type=element_type).validate(
        {key: draw(members(element_type, unknowns=unknowns)) for key in keys}
    )


@st.composite
def tuples(draw: Any, *, unknowns: bool = True, max_size: int = 3) -> CtyValue[Any]:
    element_types = draw(st.lists(scalar_types, max_size=max_size))
    return CtyTuple(element_types=tuple(element_types)).validate(
        [draw(members(element_type, unknowns=unknowns)) for element_type in element_types]
    )


@st.composite
def objects(draw: Any, *, unknowns: bool = True, max_size: int = 3) -> CtyValue[Any]:
    names = draw(st.lists(attribute_names, max_size=max_size, unique=True))
    attribute_types = {name: draw(scalar_types) for name in names}
    return CtyObject(attribute_types=attribute_types).validate(
        {name: draw(members(cty_type, unknowns=unknowns)) for name, cty_type in attribute_types.items()}
    )


def sequences(element_type: CtyType[Any] | None = None) -> st.SearchStrategy[CtyValue[Any]]:
    """Something a collection function will index into: list, set or tuple."""
    if element_type is not None:
        return st.one_of(lists(element_type), sets(element_type))
    return st.one_of(lists(), sets(), tuples())


def mappings() -> st.SearchStrategy[CtyValue[Any]]:
    """Something with keys: a map or an object."""
    return st.one_of(maps(), objects())


def collections(*, unknowns: bool = True) -> st.SearchStrategy[CtyValue[Any]]:
    return st.one_of(
        lists(unknowns=unknowns),
        sets(unknowns=unknowns),
        maps(unknowns=unknowns),
        tuples(unknowns=unknowns),
        objects(unknowns=unknowns),
    )


def bytes_values() -> st.SearchStrategy[CtyValue[Any]]:
    return byte_buffers.map(BytesCapsule.validate)


def any_value() -> st.SearchStrategy[CtyValue[Any]]:
    """Anything a caller could pass to a `dynamic` parameter.

    Weighted toward the concrete over the absent: a null or an unknown argument
    is answered before the implementation runs for most parameters, so a pool
    made mostly of those would drive the framework rather than the function.
    The null and unknown *populations* have sweeps of their own.
    """
    return st.one_of(
        scalars(),
        scalars(),
        collections(),
        collections(),
        bytes_values(),
        scalar_types.map(CtyValue.null),
        scalar_types.map(CtyValue.unknown),
    )


# 🌊🪢🔚
