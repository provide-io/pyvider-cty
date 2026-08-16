#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`indent`, `flatten` and `chunklist` must answer what go-cty answers.

Every expectation was taken from running real go-cty through the soup-go
oracle, not from reading its source. What these pin, all divergent before:

  - `indent` took a prefix *string* where go-cty takes a *number* of spaces,
    and indented the first line, which go-cty deliberately does not.
  - `flatten` returned a list with a unified element type; go-cty returns a
    tuple. It also flattened one level where go-cty recurses, dropped null
    elements that go-cty keeps, and raised on a non-sequence element that
    go-cty passes straight through.
  - `chunklist` erased the element type to dynamic, and rejected a size of 0
    that go-cty accepts as "one chunk holding everything".
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

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
from pyvider.cty.functions import chunklist, flatten, indent

STRS = CtyList(element_type=CtyString())


def s(text: str) -> CtyValue[Any]:
    return CtyString().validate(text)


def n(num: int | str) -> CtyValue[Any]:
    return CtyNumber().validate(num)


class TestIndent:
    """`strings.Replace(data, "\\n", "\\n"+pad, -1)` -- go-cty's whole implementation.

    The first line is left alone on purpose: `indent` exists to line a
    multi-line value up underneath something already written on the first line.
    """

    def test_a_number_of_spaces_is_added_after_each_newline(self) -> None:
        assert indent(n(2), s("a\nb")).value == "a\n  b"

    def test_the_first_line_is_not_indented(self) -> None:
        assert indent(n(4), s("first\nsecond")).value == "first\n    second"

    def test_a_string_without_newlines_is_unchanged(self) -> None:
        assert indent(n(2), s("abc")).value == "abc"

    def test_an_empty_string_stays_empty(self) -> None:
        """Not the padding on its own: there is no newline to follow."""
        assert indent(n(2), s("")).value == ""

    def test_a_trailing_newline_is_followed_by_padding(self) -> None:
        assert indent(n(2), s("a\n")).value == "a\n  "

    def test_a_carriage_return_is_not_a_line_break(self) -> None:
        """Only "\\n" is replaced, so CRLF keeps its CR ahead of the padding."""
        assert indent(n(2), s("a\r\nb")).value == "a\r\n  b"

    def test_zero_spaces_changes_nothing(self) -> None:
        assert indent(n(0), s("a\nb")).value == "a\nb"

    def test_a_fractional_count_is_rejected(self) -> None:
        with pytest.raises(CtyFunctionError, match="whole number"):
            indent(n("1.5"), s("a\nb"))

    @pytest.mark.parametrize("count", ["Infinity", "-Infinity", "NaN", str(2**70)], ids=str)
    def test_a_count_that_is_not_a_usable_integer_is_rejected(self, count: str) -> None:
        """go-cty reads this into a Go `int` and refuses anything that will not
        fit. Here the same values would reach `int(Decimal("Infinity"))`, which
        raises `OverflowError`, or be accepted and then used -- long enough for
        2**70 to try to build a 10^21-character string."""
        with pytest.raises(CtyFunctionError, match="whole number"):
            indent(CtyNumber().validate(Decimal(count)), s("a\nb"))

    def test_a_negative_count_is_rejected(self) -> None:
        """A deliberate divergence: go-cty panics here, recovering it as an
        opaque error carrying a Go stack trace. Refusing cleanly is the same
        outcome for a caller without reproducing the crash."""
        with pytest.raises(CtyFunctionError, match="negative"):
            indent(n(-1), s("a\nb"))

    def test_the_arguments_are_a_number_then_a_string(self) -> None:
        with pytest.raises(CtyFunctionError):
            indent(s("  "), s("a\nb"))
        with pytest.raises(CtyFunctionError):
            indent(n(2), n(2))

    @pytest.mark.parametrize(
        ("spaces", "text"),
        [
            (CtyValue.null(CtyNumber()), s("a")),
            (n(2), CtyValue.null(CtyString())),
            (CtyValue.unknown(CtyNumber()), s("a")),
            (n(2), CtyValue.unknown(CtyString())),
        ],
    )
    def test_a_null_or_unknown_argument_yields_unknown(
        self, spaces: CtyValue[Any], text: CtyValue[Any]
    ) -> None:
        assert indent(spaces, text).is_unknown


class TestFlatten:
    """go-cty's `FlattenFunc` returns a *tuple*, and recurses.

    A tuple can hold elements of differing types, so flattening a mixture does
    not have to widen anything to dynamic the way a list would.
    """

    def test_a_list_of_lists_flattens_to_a_tuple(self) -> None:
        result = flatten(CtyList(element_type=STRS).validate([["a"], ["b", "c"]]))

        assert result.type.equal(CtyTuple(element_types=(CtyString(),) * 3))
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_an_empty_sequence_flattens_to_the_empty_tuple(self) -> None:
        result = flatten(CtyList(element_type=STRS).validate([]))

        assert result.type.equal(CtyTuple(element_types=()))
        assert list(result.value) == []

    def test_nesting_is_flattened_all_the_way_down(self) -> None:
        """One level was not enough: go-cty's `flattener` calls itself."""
        inner = CtyTuple(element_types=(CtyString(),))
        middle = CtyTuple(element_types=(inner,))
        outer = CtyTuple(element_types=(middle,))

        result = flatten(outer.validate([[["a"]]]))

        assert result.type.equal(CtyTuple(element_types=(CtyString(),)))
        assert [v.value for v in result.value] == ["a"]

    def test_an_element_that_is_not_a_sequence_passes_through(self) -> None:
        """go-cty appends it unchanged rather than refusing the whole call."""
        source = CtyTuple(element_types=(CtyString(), STRS))

        result = flatten(source.validate(["a", ["b"]]))

        assert result.type.equal(CtyTuple(element_types=(CtyString(), CtyString())))
        assert [v.value for v in result.value] == ["a", "b"]

    def test_a_null_element_is_kept(self) -> None:
        """Dropping it silently shortened the result."""
        source = CtyTuple(element_types=(CtyString(), STRS))

        result = flatten(source.validate([None, ["b"]]))

        assert len(result.value) == 2
        assert result.value[0].is_null
        assert result.value[1].value == "b"

    def test_a_null_sequence_element_is_kept_rather_than_descended_into(self) -> None:
        source = CtyTuple(element_types=(STRS, STRS))

        result = flatten(source.validate([None, ["b"]]))

        assert result.type.equal(CtyTuple(element_types=(STRS, CtyString())))
        assert result.value[0].is_null

    def test_elements_of_different_types_keep_their_own_types(self) -> None:
        source = CtyTuple(element_types=(STRS, CtyList(element_type=CtyNumber())))

        result = flatten(source.validate([["a"], [1]]))

        assert result.type.equal(CtyTuple(element_types=(CtyString(), CtyNumber())))

    def test_a_nested_set_is_descended_into(self) -> None:
        """A set is a sequence for flattening, and gets a stable order.

        The input is a tuple holding a set rather than a set holding lists,
        because this package cannot build the latter -- a CtyValue with a list
        payload is unhashable, so `CtySet(element_type=list(string))` raises.
        That is a separate go-cty gap, not this one.
        """
        source = CtyTuple(element_types=(CtySet(element_type=CtyString()),))

        result = flatten(source.validate([["a", "b"]]))

        assert result.type.equal(CtyTuple(element_types=(CtyString(), CtyString())))
        assert sorted(v.value for v in result.value) == ["a", "b"]

    def test_an_unknown_sequence_element_makes_the_result_unknown(self) -> None:
        source = CtyList(element_type=STRS).validate([CtyValue.unknown(STRS)])

        assert flatten(source).is_unknown

    def test_a_non_sequence_input_raises(self) -> None:
        with pytest.raises(CtyFunctionError, match="lists, sets and tuples"):
            flatten(s("hello"))

    def test_a_null_or_unknown_input_passes_through(self) -> None:
        assert flatten(CtyValue.null(CtyList(element_type=CtyDynamic()))).is_null
        assert flatten(CtyValue.unknown(CtyList(element_type=CtyDynamic()))).is_unknown


class TestChunklist:
    """`cty.List(args[0].Type())` -- the chunk type is the input's own type."""

    def test_the_element_type_is_preserved(self) -> None:
        result = chunklist(STRS.validate(["a", "b", "c"]), n(2))

        assert result.type.equal(CtyList(element_type=STRS))
        assert [[e.value for e in c.value] for c in result.value] == [["a", "b"], ["c"]]

    def test_a_numeric_element_type_is_preserved_too(self) -> None:
        source = CtyList(element_type=CtyNumber())

        result = chunklist(source.validate([1, 2, 3]), n(2))

        assert result.type.equal(CtyList(element_type=source))

    def test_a_size_of_zero_gives_one_chunk_holding_everything(self) -> None:
        """go-cty documents this: "if size is 0, returns a list made of the
        initial list". Refusing it was stricter than the implementation."""
        result = chunklist(STRS.validate(["a", "b", "c"]), n(0))

        assert [[e.value for e in c.value] for c in result.value] == [["a", "b", "c"]]

    def test_a_negative_size_is_rejected(self) -> None:
        with pytest.raises(CtyFunctionError, match="must be positive"):
            chunklist(STRS.validate(["a", "b"]), n(-1))

    def test_a_fractional_size_is_rejected(self) -> None:
        with pytest.raises(CtyFunctionError, match="whole number"):
            chunklist(STRS.validate(["a", "b"]), n("1.5"))

    @pytest.mark.parametrize("size", ["Infinity", "NaN", str(2**70)], ids=str)
    def test_a_size_that_is_not_a_usable_integer_is_rejected(self, size: str) -> None:
        with pytest.raises(CtyFunctionError, match="whole number"):
            chunklist(STRS.validate(["a", "b"]), CtyNumber().validate(Decimal(size)))

    def test_an_empty_list_gives_an_empty_list_of_chunks(self) -> None:
        result = chunklist(STRS.validate([]), n(2))

        assert result.type.equal(CtyList(element_type=STRS))
        assert list(result.value) == []

    def test_a_size_larger_than_the_list_gives_a_single_chunk(self) -> None:
        result = chunklist(STRS.validate(["a"]), n(5))

        assert [[e.value for e in c.value] for c in result.value] == [["a"]]

    def test_a_tuple_input_unifies_its_element_types(self) -> None:
        """A deliberate superset: go-cty's parameter is `list(dynamic)`, which
        its conversion layer refuses a tuple for. Accepting one costs nothing
        and breaks nobody, so long as the chunk type is the unified type rather
        than dynamic."""
        source = CtyTuple(element_types=(CtyString(), CtyString(), CtyString()))

        result = chunklist(source.validate(["a", "b", "c"]), n(2))

        assert result.type.equal(CtyList(element_type=STRS))

    def test_a_wrong_type_raises(self) -> None:
        with pytest.raises(CtyFunctionError):
            chunklist(s("hello"), n(2))
        with pytest.raises(CtyFunctionError):
            chunklist(STRS.validate(["a"]), s("2"))

    @pytest.mark.parametrize(
        ("collection", "size"),
        [
            (CtyValue.null(STRS), n(2)),
            (CtyValue.unknown(STRS), n(2)),
            (STRS.validate(["a"]), CtyValue.null(CtyNumber())),
            (STRS.validate(["a"]), CtyValue.unknown(CtyNumber())),
        ],
    )
    def test_a_null_or_unknown_argument_yields_unknown(
        self, collection: CtyValue[Any], size: CtyValue[Any]
    ) -> None:
        assert chunklist(collection, size).is_unknown


# 🌊🪢🔚
