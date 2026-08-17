#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`can_convert_unsafe` — go-cty's `GetConversionUnsafe` as a type-level predicate.

It exists because unification has to ask "could this be converted" without a
value in hand, and it is only useful if it answers for exactly the conversions
`convert` performs. A divergence either way is a real fault: unification would
propose a type nothing can reach, or refuse one that can.

So the load-bearing test here is the last one, which checks the two against each
other rather than checking either against a table written by hand.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import (
    CtyBool,
    CtyCapsule,
    CtyCapsuleWithOps,
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
from pyvider.cty.conversion import can_convert_unsafe, convert
from pyvider.cty.exceptions import CtyConversionError

S, N, B, D = CtyString(), CtyNumber(), CtyBool(), CtyDynamic()


def lst(element: CtyType[Any]) -> CtyType[Any]:
    return CtyList(element_type=element)


def st(element: CtyType[Any]) -> CtyType[Any]:
    return CtySet(element_type=element)


def mp(element: CtyType[Any]) -> CtyType[Any]:
    return CtyMap(element_type=element)


def tp(*elements: CtyType[Any]) -> CtyType[Any]:
    return CtyTuple(element_types=elements)


class _Payload:
    def __init__(self, value: object) -> None:
        self.value = value


@pytest.mark.parametrize(
    ("source", "target", "expected"),
    [
        # Dynamic converts both ways: it stands for a type not yet known.
        (S, D, True),
        (D, S, True),
        (S, S, True),
        # go-cty's primitive table, entire.
        (N, S, True),
        (B, S, True),
        (S, N, True),
        (S, B, True),
        (B, N, False),
        (N, B, False),
        # Collections convert when their elements do.
        (lst(N), lst(S), True),
        (lst(B), lst(N), False),
        (lst(S), st(S), True),
        (st(S), lst(S), True),
        (tp(N, B), lst(S), True),
        (tp(N, B), st(S), True),
        (lst(S), tp(S), False),
        (mp(N), mp(S), True),
        (lst(S), mp(S), False),
        # Tuples convert positionally, and only at matching lengths.
        (tp(N, B), tp(S, S), True),
        (tp(N), tp(S, S), False),
        (tp(N), tp(B), False),
        # An object is map-shaped once the per-attribute types agree.
        (CtyObject({"a": N}), mp(S), True),
        (CtyObject({"a": lst(S)}), mp(S), False),
        # And the other direction, which this table recorded as False from a
        # reading of go-cty's source. go-cty has `conversionMapToObject` and
        # allows it unsafely -- "we don't know if all the map keys will
        # correspond to object attributes" -- which the harness confirms.
        (mp(S), CtyObject({"a": S}), True),
        (mp(lst(S)), CtyObject({"a": S}), False),
        (mp(S), CtyObject({"a": S, "b": N}, optional_attributes=frozenset({"b"})), True),
        # Objects convert to a subset of themselves; this is what unification
        # deliberately does *not* use.
        (CtyObject({"a": S, "b": N}), CtyObject({"a": S}), True),
        (CtyObject({"a": S}), CtyObject({"a": S, "b": N}), False),
        (CtyObject({"a": S}), CtyObject({"a": S, "b": N}, optional_attributes={"b"}), True),
        (CtyObject({"a": B}), CtyObject({"a": N}), False),
        # Nothing crosses between a primitive and a collection.
        (S, lst(S), False),
        (lst(S), S, False),
    ],
    ids=str,
)
def test_the_table_matches_go_ctys(source: CtyType[Any], target: CtyType[Any], expected: bool) -> None:  # noqa: FBT001
    assert can_convert_unsafe(source, target) is expected


class TestCapsules:
    def test_a_capsule_with_a_converter_is_admitted_optimistically(self) -> None:
        """Whether it converts is the converter's decision, and that needs a value."""
        capsule = CtyCapsuleWithOps("WithOps", _Payload, convert_fn=lambda raw, ty: None)

        assert can_convert_unsafe(capsule, CtyString()) is True

    def test_a_capsule_without_a_converter_converts_to_nothing(self) -> None:
        assert can_convert_unsafe(CtyCapsuleWithOps("Bare", _Payload), CtyString()) is False

    def test_a_plain_capsule_converts_to_nothing(self) -> None:
        assert can_convert_unsafe(CtyCapsule("Plain", _Payload), CtyString()) is False

    def test_nothing_converts_to_a_capsule(self) -> None:
        assert can_convert_unsafe(CtyString(), CtyCapsule("Plain", _Payload)) is False


SAMPLES: dict[str, Any] = {"string": "1", "number": 1, "bool": True}


def _sample(cty_type: CtyType[Any]) -> CtyValue[Any]:
    """A value of the given type, built from primitives outwards."""
    if isinstance(cty_type, CtyList | CtySet):
        return cty_type.validate([_sample(cty_type.element_type).value])
    if isinstance(cty_type, CtyMap):
        # Keyed "a" so that a map can reach the object type in TYPES. A map
        # converts to an object by key, so a sample keyed anything else fails on
        # the *value* -- a legal outcome for an unsafe conversion, and one that
        # would leave this test unable to check the contract for that pair.
        return cty_type.validate({"a": _sample(cty_type.element_type).value})
    if isinstance(cty_type, CtyTuple):
        return cty_type.validate(tuple(_sample(element).value for element in cty_type.element_types))
    if isinstance(cty_type, CtyObject):
        return cty_type.validate(
            {name: _sample(attribute).value for name, attribute in cty_type.attribute_types.items()}
        )
    return cty_type.validate(SAMPLES[cty_type.ctype])


TYPES = [S, N, B, lst(S), lst(N), st(S), mp(S), mp(N), tp(S, N), CtyObject({"a": S})]


@pytest.mark.parametrize("source", TYPES, ids=str)
@pytest.mark.parametrize("target", TYPES, ids=str)
def test_the_predicate_agrees_with_what_convert_actually_does(
    source: CtyType[Any], target: CtyType[Any]
) -> None:
    """The contract, checked as a contract rather than as a table.

    "Unsafe" allows the conversion to fail on the *value* -- not every string is
    a number -- so a False here must mean `convert` refuses, while a True only
    promises that the types are not the obstacle. The sample values are chosen
    to convert, so in practice both directions hold.
    """
    value = _sample(source)
    permitted = can_convert_unsafe(source, target)

    try:
        converted = convert(value, target)
    except CtyConversionError:
        assert not permitted or source.equal(target), (
            f"can_convert_unsafe said {source} -> {target} was possible, and convert refused"
        )
        return

    assert permitted, f"convert performed {source} -> {target}, which can_convert_unsafe denied"
    assert converted.type.equal(target)


# 🌊🪢🔚
