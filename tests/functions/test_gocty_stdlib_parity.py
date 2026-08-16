#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""`indent`, `flatten`, `chunklist` and `length` must answer what go-cty answers.

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
  - `length` accepted a string, which go-cty refuses, and refused a dynamic,
    which go-cty accepts.
  - `values` returned a map's values in insertion order where go-cty sorts them
    by key, so `keys` and `values` no longer lined up. `zipmap(keys(m),
    values(m))` -- the standard way to rebuild a map -- silently paired every
    value with the wrong key. Both also returned the wrong *type* for an object
    input, where go-cty returns a tuple rather than a list.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyObject,
    CtySet,
    CtyString,
    CtyTuple,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import chunklist, flatten, indent, keys, length, values

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


class TestLength:
    """`LengthFunc` counts a *collection*, and only a collection.

    Its parameter is `DynamicPseudoType`, so the type check runs on the
    resolved type: a dynamic wrapping a list is counted, a dynamic wrapping a
    string is refused just as a bare string is. go-cty's own error text says
    "a list, a map or a tuple" and is stale -- the check names sets too, and
    the oracle counts one.
    """

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (CtyList(element_type=CtyString()).validate(["a", "b"]), 2),
            (CtySet(element_type=CtyString()).validate(["a", "b"]), 2),
            (CtyTuple(element_types=(CtyString(), CtyNumber())).validate(("a", 1)), 2),
            (CtyMap(element_type=CtyString()).validate({"a": "x"}), 1),
        ],
        ids=["list", "set", "tuple", "map"],
    )
    def test_every_collection_type_is_counted(self, value: CtyValue[Any], expected: int) -> None:
        assert length(value).value == expected

    def test_a_string_is_refused(self) -> None:
        """Was 5. go-cty refuses the call outright -- counting a string is
        `strlen`'s job, and it counts grapheme clusters rather than the code
        points this returned."""
        with pytest.raises(CtyFunctionError, match="collection"):
            length(s("hello"))

    def test_a_string_of_combining_characters_is_refused_too(self) -> None:
        """The reason the old answer was not merely differently-spelled: this
        returned 7, where go-cty's `strlen` would say 1 and Terraform's
        `length` says 1. It agreed with neither."""
        with pytest.raises(CtyFunctionError, match="collection"):
            length(s("👨‍👩‍👧‍👦"))

    def test_a_dynamic_wrapping_a_collection_is_counted(self) -> None:
        """Was refused. go-cty's parameter is `DynamicPseudoType`, so the
        wrapper is resolved before the type check rather than failing it."""
        assert length(CtyDynamic().validate(["a", "b"])).value == 2

    def test_a_dynamic_wrapping_a_string_is_still_refused(self) -> None:
        """Unwrapping is not a licence to count anything: the resolved type is
        what the check runs on."""
        with pytest.raises(CtyFunctionError, match="collection"):
            length(CtyDynamic().validate("hello"))

    def test_an_unknown_dynamic_is_unknown_rather_than_refused(self) -> None:
        """Nothing to unwrap and nothing to refuse: go-cty's type check lets
        `DynamicPseudoType` through precisely so this can stay undecided."""
        assert length(CtyValue.unknown(CtyDynamic())).is_unknown

    @pytest.mark.parametrize("bad", [CtyNumber().validate(1), CtyValue.unknown(CtyNumber())], ids=str)
    def test_a_non_collection_is_refused_known_or_not(self, bad: CtyValue[Any]) -> None:
        """An unknown *number* is still typed, so the check still decides."""
        with pytest.raises(CtyFunctionError, match="collection"):
            length(bad)

    def test_an_object_is_refused(self) -> None:
        """go-cty counts map and tuple but not object."""
        with pytest.raises(CtyFunctionError, match="collection"):
            length(CtyObject(attribute_types={"a": CtyString()}).validate({"a": "x"}))

    def test_a_null_collection_stays_unknown(self) -> None:
        """A deliberate hold-out, not an oversight. go-cty raises "argument
        must not be null" here. Turning that return into a raise is the same
        strictness change already deferred for `contains`, and the two should
        move together rather than one at a time.
        """
        assert length(CtyValue.null(CtyList(element_type=CtyString()))).is_unknown

    def test_an_unknown_collection_is_unknown(self) -> None:
        assert length(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown


class TestKeysAndValues:
    """Both iterate in lexicographic order by key, and both return a *tuple*
    for an object input.

    go-cty's guarantee is a property of the types rather than of these two
    functions: "cty guarantees that these types always iterate in key
    lexicographical order". `keys` already sorted; `values` did not, which is
    the whole of the bug -- two functions documented to correspond, that did
    not.
    """

    MIXED = CtyMap(element_type=CtyString()).validate({"b": "bee", "a": "ay", "c": "see"})

    def test_a_maps_values_come_back_in_key_order(self) -> None:
        """Was insertion order."""
        assert [v.value for v in values(self.MIXED).value] == ["ay", "bee", "see"]

    def test_a_maps_keys_come_back_in_order(self) -> None:
        assert [k.value for k in keys(self.MIXED).value] == ["a", "b", "c"]

    def test_keys_and_values_line_up(self) -> None:
        """The property that actually matters, and the one that was broken.

        `zipmap(keys(m), values(m))` is the ordinary way to rebuild a map, and
        with `values` unsorted it reassociated every entry -- silently, with a
        result that still type-checked and still looked like a map.
        """
        paired = dict(
            zip(
                [k.value for k in keys(self.MIXED).value],
                [v.value for v in values(self.MIXED).value],
                strict=True,
            )
        )

        assert paired == {"b": "bee", "a": "ay", "c": "see"}

    def test_a_maps_values_are_a_list_of_the_element_type(self) -> None:
        assert values(self.MIXED).type.equal(CtyList(element_type=CtyString()))

    def test_an_objects_values_are_a_tuple_ordered_by_attribute_name(self) -> None:
        """A tuple, because an object's attributes have differing types and a
        list would have to widen them to dynamic to hold them."""
        obj = CtyObject(attribute_types={"b": CtyString(), "a": CtyNumber()}).validate({"b": "bee", "a": 1})

        result = values(obj)

        assert result.type.equal(CtyTuple(element_types=(CtyNumber(), CtyString())))
        assert [v.value for v in result.value] == [1, "bee"]

    def test_an_objects_keys_are_a_tuple_of_strings(self) -> None:
        obj = CtyObject(attribute_types={"b": CtyString(), "a": CtyNumber()}).validate({"b": "bee", "a": 1})

        result = keys(obj)

        assert result.type.equal(CtyTuple(element_types=(CtyString(), CtyString())))
        assert [k.value for k in result.value] == ["a", "b"]

    def test_an_empty_object_gives_the_empty_tuple(self) -> None:
        empty = CtyObject(attribute_types={}).validate({})

        assert values(empty).type.equal(CtyTuple(element_types=()))
        assert keys(empty).type.equal(CtyTuple(element_types=()))

    def test_an_empty_map_gives_an_empty_list(self) -> None:
        empty = CtyMap(element_type=CtyString()).validate({})

        assert values(empty).type.equal(CtyList(element_type=CtyString()))
        assert list(values(empty).value) == []

    def test_sorting_is_by_code_point_rather_than_locale(self) -> None:
        """Go's `sort.Strings` is a byte-wise comparison, so uppercase sorts
        before lowercase. A locale-aware sort would disagree."""
        m = CtyMap(element_type=CtyString()).validate({"b": "1", "A": "2", "a": "3"})

        assert [k.value for k in keys(m).value] == ["A", "a", "b"]
        assert [v.value for v in values(m).value] == ["2", "3", "1"]

    @pytest.mark.parametrize("bad", [s("x"), CtyList(element_type=CtyString()).validate(["a"])], ids=str)
    def test_a_non_mapping_is_refused(self, bad: CtyValue[Any]) -> None:
        with pytest.raises(CtyFunctionError):
            values(bad)
        with pytest.raises(CtyFunctionError):
            keys(bad)

    @pytest.mark.parametrize("kind", ["null", "unknown"], ids=str)
    def test_a_null_or_unknown_mapping_yields_unknown(self, kind: str) -> None:
        m = CtyMap(element_type=CtyString())
        arg = CtyValue.null(m) if kind == "null" else CtyValue.unknown(m)

        assert values(arg).is_unknown
        assert keys(arg).is_unknown


# 🌊🪢🔚
