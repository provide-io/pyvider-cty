#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""The paths `convert` and `unify` take when there is no answer.

Refusals are the half of a conversion layer that is easiest to leave untested
and worst to get wrong: a conversion that quietly succeeds where it should fail
produces a well-typed value that is not what the caller asked for, and nothing
downstream can tell. Several of the divergences on this branch were exactly
that shape.
"""

from __future__ import annotations

from typing import Any

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
    CtyTuple,
    CtyType,
    CtyValue,
)
from pyvider.cty.conversion import convert
from pyvider.cty.conversion.unify import unify
from pyvider.cty.exceptions import CtyConversionError

S, N, B = CtyString(), CtyNumber(), CtyBool()


class TestConvertRefusals:
    @pytest.mark.parametrize("absent", [CtyValue.null(S), CtyValue.unknown(S)], ids=["null", "unknown"])
    def test_an_absent_value_still_has_to_be_convertible(self, absent: CtyValue[Any]) -> None:
        """Nullness is not part of a cty type.

        `convert` used to return a null of the target type for *any* target, so
        `tostring(null_of_list)` produced a null string. A null list is no more
        a string than a populated one. Found by the null sweep.
        """
        with pytest.raises(CtyConversionError):
            convert(CtyValue.null(CtyList(element_type=S)), S)
        with pytest.raises(CtyConversionError):
            convert(CtyValue.unknown(CtyList(element_type=S)), S)

        # ...and one that *is* convertible still passes through.
        assert convert(absent, CtyString()).type.equal(S)

    def test_a_sequence_of_the_wrong_length_is_not_a_tuple(self) -> None:
        """A tuple type fixes its arity, so there is nothing to convert into."""
        source = CtyList(element_type=S).validate(["a", "b", "c"])

        with pytest.raises(CtyConversionError):
            convert(source, CtyTuple(element_types=(S, S)))

    def test_a_sequence_of_the_right_length_converts_positionally(self) -> None:
        source = CtyList(element_type=N).validate([1, 2])

        converted = convert(source, CtyTuple(element_types=(S, S)))

        assert converted.raw_value == ("1", "2")

    def test_an_object_whose_payload_is_not_a_dict_is_refused(self) -> None:
        malformed = CtyValue(CtyObject({"a": S}), "not a dict")

        with pytest.raises(CtyConversionError):
            convert(malformed, CtyMap(element_type=S))

    def test_an_object_converts_to_a_map_its_attributes_all_reach(self) -> None:
        source = CtyObject({"a": N, "b": N}).validate({"a": 1, "b": 2})

        converted = convert(source, CtyMap(element_type=S))

        assert converted.raw_value == {"a": "1", "b": "2"}


class TestUnifyRefusals:
    """`None` is an answer, and it is the one callers most need to distinguish."""

    @pytest.mark.parametrize(
        "types",
        [
            [N, B],
            [CtyList(element_type=N), CtyList(element_type=B)],
            [CtySet(element_type=N), CtySet(element_type=B)],
            [CtyMap(element_type=N), CtyMap(element_type=B)],
            [CtyObject({"a": N}), CtyObject({"b": B})],
            [CtyObject({"a": N}), CtyObject({"a": B})],
            [CtyTuple(element_types=(N,)), CtyTuple(element_types=(B,))],
            [CtyTuple(element_types=(N,)), CtyTuple(element_types=(B, B))],
            [CtyTuple(element_types=(N,)), CtyList(element_type=B)],
            [S, CtyList(element_type=S)],
            [CtyObject({"a": S}), CtyTuple(element_types=(S,))],
            [CtyMap(element_type=S), CtyList(element_type=S)],
        ],
        ids=str,
    )
    def test_types_with_nothing_in_common_unify_to_nothing(self, types: list[CtyType[Any]]) -> None:
        assert unify(types) is None

    def test_a_dynamic_among_collections_defers_the_whole_answer(self) -> None:
        """Which path unification takes once it resolves cannot be predicted."""
        for group in (
            [CtyList(element_type=S), CtyDynamic()],
            [CtyMap(element_type=S), CtyDynamic()],
            [CtySet(element_type=S), CtyDynamic()],
            [CtyObject({"a": S}), CtyDynamic()],
            [CtyTuple(element_types=(S,)), CtyDynamic()],
        ):
            assert isinstance(unify(group), CtyDynamic), group

    def test_an_object_and_a_map_whose_members_disagree_unify_to_nothing(self) -> None:
        assert unify([CtyObject({"a": B}), CtyMap(element_type=N)]) is None

    def test_a_tuple_and_a_list_whose_members_disagree_unify_to_nothing(self) -> None:
        assert unify([CtyTuple(element_types=(B, B)), CtyList(element_type=N)]) is None


# 🌊🪢🔚
