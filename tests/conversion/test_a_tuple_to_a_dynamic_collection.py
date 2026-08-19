#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Converting a tuple to a collection whose element type is `dynamic`.

`dynamic` in a *target* element position does not mean "anything goes". go-cty
reads it as "find a single type every element can convert to"
(`convert/conversion_collection.go:277`, `conversionTupleToList`) and refuses
when there is no such type:

  * an empty tuple converts to an empty collection whatever the element type is;
  * otherwise the tuple's element types are **unified**, and no common type is a
    refusal;
  * and if that unification is itself `dynamic`, it only stands when every
    element type was already `dynamic` -- a `dynamic` arrived at by unification
    is not a type every element converts to.

`can_convert_unsafe` asked the question per element instead, and
`can_convert_unsafe(anything, dynamic)` is yes, so **every** tuple converted.
The visible consequence was one layer up: `unify` reads this answer back, so
`unify(tuple(list(string), number), list(dynamic))` was `list(dynamic)` where
go-cty finds no common type at all -- `concat` and `flatten` succeeding here on
arguments real Terraform rejects.

Found 2026-08-19 by sweeping `unify` against the live oracle, which had never
been compared. The differential cases are in
`tests/compatibility/test_unify_oracle.py`; these run without a Go toolchain and
state the conversion rule directly.
"""

from __future__ import annotations

from typing import Any

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyType,
)
from pyvider.cty.conversion import unify
from pyvider.cty.conversion.explicit import can_convert_unsafe

S, N, D = CtyString(), CtyNumber(), CtyDynamic()
LIST_OF_DYNAMIC = CtyList(element_type=D)
SET_OF_DYNAMIC = CtySet(element_type=D)


class TestWhatTheRuleRefuses:
    def test_a_tuple_whose_elements_have_no_common_type(self) -> None:
        """`list(string)` and `number` unify to nothing, so the tuple converts to nothing."""
        source = CtyTuple(element_types=(CtyList(element_type=S), N))

        assert not can_convert_unsafe(source, LIST_OF_DYNAMIC)
        assert not can_convert_unsafe(source, SET_OF_DYNAMIC)

    def test_the_same_tuple_is_refused_by_unify(self) -> None:
        """The layer that made it visible: no common type, not `list(dynamic)`."""
        source = CtyTuple(element_types=(CtyList(element_type=S), N))

        assert unify([source, LIST_OF_DYNAMIC]) is None

    def test_a_unification_that_lands_on_dynamic_needs_every_element_dynamic(self) -> None:
        """A `dynamic` reached *by unifying* is not a type every element converts to."""
        mixed = CtyTuple(element_types=(D, CtyList(element_type=S)))

        assert not can_convert_unsafe(mixed, LIST_OF_DYNAMIC)


class TestWhatTheRuleStillAllows:
    """The rule has to stay narrow: it refuses on unifiability, not on `dynamic`."""

    def test_an_empty_tuple_converts_to_an_empty_collection(self) -> None:
        assert can_convert_unsafe(CtyTuple(element_types=()), LIST_OF_DYNAMIC)

    def test_elements_with_a_common_type_convert(self) -> None:
        """`string` and `number` unify to `string`, so this is `list(string)`."""
        source = CtyTuple(element_types=(S, N))

        assert can_convert_unsafe(source, LIST_OF_DYNAMIC)
        assert unify([source, LIST_OF_DYNAMIC]) == CtyList(element_type=S)

    def test_an_all_dynamic_tuple_converts(self) -> None:
        assert can_convert_unsafe(CtyTuple(element_types=(D, D)), LIST_OF_DYNAMIC)

    @pytest.mark.parametrize(
        ("label", "target"),
        [("concrete element", CtyList(element_type=S)), ("set target", CtySet(element_type=S))],
    )
    def test_a_concrete_target_element_is_unchanged(self, label: str, target: CtyType[Any]) -> None:
        """Only a `dynamic` target element takes the unification path."""
        assert can_convert_unsafe(CtyTuple(element_types=(S, S)), target), label
        assert not can_convert_unsafe(CtyTuple(element_types=(CtyList(element_type=S), N)), target), label


# 🌊🪢🔚
