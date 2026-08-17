#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
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

    def test_distinct_with_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            distinct(CtyValue.null(CtyList(element_type=CtyString())))
        assert distinct(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_distinct_de_duplicates_container_elements(self) -> None:
        """A list of lists de-duplicates like anything else.

        This asserted a "not hashable" refusal until 2026-08-17, when
        `CtyValue.__hash__` started hashing containers. go-cty never had the
        restriction to begin with: `DistinctFunc` de-duplicates through
        `appendIfMissing`, which compares with the three-valued `Equal`
        (`stdlib/collection.go:1434`) and has no notion of a hashable element.
        Two equal inner lists are one value, so one of them goes.
        """
        lst = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["a"]])

        assert distinct(lst).raw_value == [["a"]]

    def test_distinct_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            distinct(CtyString().validate("hello"))


class TestFlatten:
    """`flatten` returns a tuple, so `raw_value` is a tuple too.

    See tests/functions/test_gocty_stdlib_parity.py for the go-cty behaviour
    these follow, and why a list was the wrong return type.
    """

    def test_flatten_list_of_lists(self) -> None:
        lst = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a", "b"], ["c"]])
        assert flatten(lst).raw_value == ("a", "b", "c")

    def test_flatten_tuple_of_lists(self) -> None:
        t = CtyTuple(
            element_types=(
                CtyList(element_type=CtyString()),
                CtyList(element_type=CtyString()),
            )
        ).validate([["a", "b"], ["c"]])
        assert flatten(t).raw_value == ("a", "b", "c")

    def test_flatten_with_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            flatten(CtyValue.null(CtyList(element_type=CtyDynamic())))
        assert flatten(CtyValue.unknown(CtyList(element_type=CtyDynamic()))).is_unknown

    def test_flatten_with_null_element(self) -> None:
        """A null is a value, and go-cty keeps it. Dropping it shortened the result."""
        lst = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                None,
                CtyList(element_type=CtyString()).validate(["b"]),
            ]
        )
        assert flatten(lst).raw_value == ("a", None, "b")

    def test_flatten_with_unknown_element(self) -> None:
        lst = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyValue.unknown(CtyList(element_type=CtyString())),
            ]
        )
        assert flatten(lst).is_unknown

    def test_flatten_with_non_list_element(self) -> None:
        """go-cty passes a non-sequence element through instead of refusing."""
        lst = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyString().validate("b"),
            ]
        )
        assert flatten(lst).raw_value == ("a", "b")

    def test_flatten_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            flatten(CtyString().validate("hello"))

    def test_flatten_empty(self) -> None:
        lst = CtyList(element_type=CtyList(element_type=CtyString())).validate([])
        assert flatten(lst).raw_value == ()

    def test_flatten_mixed_types(self) -> None:
        """A tuple carries each element's own type, so nothing widens to dynamic."""
        lst = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyList(element_type=CtyNumber()).validate([1]),
            ]
        )
        result = flatten(lst)
        assert result.type.equal(CtyTuple(element_types=(CtyString(), CtyNumber())))
        assert result.raw_value == ("a", 1)


class TestReverse:
    def test_reverse_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert reverse(lst).raw_value == ["c", "b", "a"]

    def test_reverse_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "b", "c"))
        assert reverse(t).raw_value == ("c", "b", "a")

    def test_reverse_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            reverse(CtyValue.null(CtyList(element_type=CtyString())))
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

    def test_sort_with_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            sort(CtyValue.null(CtyList(element_type=CtyString())))
        assert sort(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_sort_with_null_element(self) -> None:
        lst = CtyList(element_type=CtyDynamic()).validate(
            [CtyString().validate("a"), CtyValue.null(CtyString())]
        )
        with pytest.raises(CtyFunctionError, match="cannot sort list with null or unknown elements"):
            sort(lst)

    def test_sort_with_unknown_element(self) -> None:
        """An unknown element defers the ordering; it does not refuse it.

        This asserted a refusal until 2026-08-17, when a list stopped taking its
        unknown-ness from its elements and the case became reachable at all.
        go-cty's `SortFunc` answers with a list of the same length whose
        elements are all unknown -- the ordering is undecided, so every position
        is, and it discards even the elements it knows. Verified against go-cty:
        `sort(["a", unknown])` is `cty.ListVal([unknown, unknown])`.

        A *null* element is still an error, and that is the distinction this
        used to miss by treating the two alike.
        """
        lst = CtyList(element_type=CtyDynamic()).validate(
            [CtyString().validate("a"), CtyValue.unknown(CtyString())]
        )

        result = sort(lst)

        assert not result.is_unknown
        assert len(result.value) == 2
        assert all(element.is_unknown for element in result.value)

    def test_sort_with_null_element_still_refuses(self) -> None:
        """The other half of the distinction above, so it cannot regress."""
        lst = CtyList(element_type=CtyString()).validate(["a", CtyValue.null(CtyString())])

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
