#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`cty_to_native` orders a set by `_canonical_sort_key`, as it says it does.

The sort ran over the *already-converted natives* rather than the elements:

    results[val_id] = sorted(
        [results[id(item)] for item in set_val],
        key=lambda v: v._canonical_sort_key() if isinstance(v, CtyValue) else repr(v),
    )

By that point every member is a plain `int`, `str` or `dict`, so the
`isinstance(v, CtyValue)` branch was unreachable and every set came out ordered
by `repr`. That is lexicographic, so `{10, 2, 9}` converted to `[10, 2, 9]` and
a set of numbers came out in an order no reader would predict -- while the
comment above it named the canonical order this package uses everywhere else,
including on the wire.
"""

from __future__ import annotations

from decimal import Decimal

from pyvider.cty import CtyNumber, CtySet, CtyString
from pyvider.cty.conversion import cty_to_native
from pyvider.cty.values import CtyValue


def test_numbers_come_out_in_numeric_order() -> None:
    """The case `repr` gets wrong: "10" sorts before "2" and 10 does not."""
    value = CtySet(element_type=CtyNumber()).validate([10, 2, 9])

    assert cty_to_native(value) == [Decimal(2), Decimal(9), Decimal(10)]


def test_negative_numbers_sort_below_zero() -> None:
    """`repr` puts every "-" first regardless of magnitude."""
    value = CtySet(element_type=CtyNumber()).validate([-2, -10, 1])

    assert cty_to_native(value) == [Decimal(-10), Decimal(-2), Decimal(1)]


def test_the_order_is_the_one_the_wire_uses() -> None:
    """The whole point of naming a canonical order is that it is the same one.

    `_canonical_sort_key` is what `CtySet.validate` de-duplicates with and what
    the msgpack and JSON codecs serialize in, so a native conversion that
    ordered differently gave a Python caller a different answer from the one
    Terraform sees.
    """
    value = CtySet(element_type=CtyNumber()).validate([10, 2, 9])
    elements = sorted(value.value, key=lambda element: element._canonical_sort_key())

    assert cty_to_native(value) == [element.value for element in elements]


def test_strings_still_come_out_in_order() -> None:
    value = CtySet(element_type=CtyString()).validate(["b", "a", "c"])

    assert cty_to_native(value) == ["a", "b", "c"]


def test_a_set_holding_a_null_puts_it_last() -> None:
    """`_canonical_sort_key` ranks known 0, unknown 1, null 2 -- go-cty's order."""
    value = CtySet(element_type=CtyString()).validate([CtyValue.null(CtyString()), "a"])

    assert cty_to_native(value) == ["a", None]


def test_nested_sets_are_ordered_at_every_level() -> None:
    """The recursive case: the inner sets are ordered too, and the outer by them.

    `[[2, 10], [3]]` rather than `[[3], [2, 10]]`: an element's key carries its
    members, so a two-element set ranks before a one-element set whose member is
    larger. That is what go-cty's own wire encoding of this value contains,
    checked against v1.19.0:

        soup-go cty msgpack encode --type '["set",["set","number"]]' '[[10,2],[3]]'
        -> [[2, 10], [3]]
    """
    inner = CtySet(element_type=CtyNumber())
    value = CtySet(element_type=inner).validate([[10, 2], [3]])

    assert cty_to_native(value) == [[Decimal(2), Decimal(10)], [Decimal(3)]]


# 🐍🏗️🔚
