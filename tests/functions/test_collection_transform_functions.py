#
# SPDX-FileCopyrightText: Copyright (c) 2025 provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for collection transformation functions (distinct, flatten, reverse, sort, etc.)."""

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyNumber,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import distinct, flatten, reverse, sort


class TestDistinct:
    def test_distinct_with_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "a"])
        assert distinct(lst).raw_value == ["a", "b"]

    def test_distinct_with_set(self) -> None:
        s = CtySet(element_type=CtyNumber()).validate({1, 2})
        assert sorted(distinct(s).raw_value) == [1, 2]

    def test_distinct_with_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "b", "a"))
        assert distinct(t).raw_value == ["a", "b"]

    def test_distinct_with_null_unknown(self) -> None:
        assert distinct(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert distinct(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_distinct_with_unhashable(self) -> None:
        lst = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["a"]])
        with pytest.raises(CtyFunctionError, match="not hashable"):
            distinct(lst)

    def test_distinct_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            distinct(CtyString().validate("hello"))


class TestFlatten:
    def test_flatten_list_of_lists(self) -> None:
        lst = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a", "b"], ["c"]])
        assert flatten(lst).raw_value == ["a", "b", "c"]

    def test_flatten_tuple_of_lists(self) -> None:
        t = CtyTuple(
            element_types=(
                CtyList(element_type=CtyString()),
                CtyList(element_type=CtyString()),
            )
        ).validate([["a", "b"], ["c"]])
        assert flatten(t).raw_value == ["a", "b", "c"]

    def test_flatten_with_null_unknown(self) -> None:
        assert flatten(CtyValue.null(CtyList(element_type=CtyDynamic()))).is_null
        assert flatten(CtyValue.unknown(CtyList(element_type=CtyDynamic()))).is_unknown

    def test_flatten_with_null_element(self) -> None:
        lst = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                None,
                CtyList(element_type=CtyString()).validate(["b"]),
            ]
        )
        assert flatten(lst).raw_value == ["a", "b"]

    def test_flatten_with_unknown_element(self) -> None:
        lst = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyValue.unknown(CtyList(element_type=CtyString())),
            ]
        )
        assert flatten(lst).is_unknown

    def test_flatten_with_non_list_element(self) -> None:
        lst = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyString().validate("b"),
            ]
        )
        with pytest.raises(CtyFunctionError, match="all elements must be lists, sets, or tuples"):
            flatten(lst)

    def test_flatten_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            flatten(CtyString().validate("hello"))

    def test_flatten_empty(self) -> None:
        lst = CtyList(element_type=CtyList(element_type=CtyString())).validate([])
        assert flatten(lst).raw_value == []

    def test_flatten_mixed_types(self) -> None:
        lst = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyList(element_type=CtyNumber()).validate([1]),
            ]
        )
        result = flatten(lst)
        assert isinstance(result.type, CtyList)
        assert isinstance(result.type.element_type, CtyDynamic)
        assert result.raw_value == ["a", 1]


class TestReverse:
    def test_reverse_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert reverse(lst).raw_value == ["c", "b", "a"]

    def test_reverse_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "b", "c"))
        assert reverse(t).raw_value == ("c", "b", "a")

    def test_reverse_null_unknown(self) -> None:
        assert reverse(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert reverse(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_reverse_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            reverse(CtyString().validate("hello"))


class TestSort:
    def test_sort_list_of_strings(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["c", "a", "b"])
        assert sort(lst).raw_value == ["a", "b", "c"]

    def test_sort_list_of_numbers(self) -> None:
        lst = CtyList(element_type=CtyNumber()).validate([3, 1, 2])
        assert sort(lst).raw_value == [1, 2, 3]

    def test_sort_with_null_unknown(self) -> None:
        assert sort(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert sort(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_sort_with_null_element(self) -> None:
        lst = CtyList(element_type=CtyDynamic()).validate(
            [CtyString().validate("a"), CtyValue.null(CtyString())]
        )
        with pytest.raises(CtyFunctionError, match="cannot sort list with null or unknown elements"):
            sort(lst)

    def test_sort_with_unknown_element(self) -> None:
        lst = CtyList(element_type=CtyDynamic()).validate(
            [CtyString().validate("a"), CtyValue.unknown(CtyString())]
        )
        with pytest.raises(CtyFunctionError, match="cannot sort list with null or unknown elements"):
            sort(lst)

    def test_sort_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            sort(CtyString().validate("hello"))

    def test_sort_unsupported_element_type(self) -> None:
        lst = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"]])
        with pytest.raises(CtyFunctionError, match="elements must be string, number, or bool"):
            sort(lst)


# 🌊🪢🔚
