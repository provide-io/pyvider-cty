#
# SPDX-FileCopyrightText: Copyright (c) provide.io llc. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

"""Test suite for collection creation/manipulation functions (element, coalescelist, compact, chunklist, lookup, merge, zipmap, concat, slice, length)."""

import pytest

from pyvider.cty import (
    CtyBool,
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
from pyvider.cty.functions import (
    chunklist,
    coalescelist,
    compact,
    concat,
    element,
    length,
    lookup,
    merge,
    slice,
    zipmap,
)


class TestElement:
    def test_element_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert element(lst, CtyNumber().validate(1)).raw_value == "b"
        assert element(lst, CtyNumber().validate(3)).raw_value == "a"

    def test_element_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "b", "c"))
        assert element(t, CtyNumber().validate(1)).raw_value == "b"
        assert element(t, CtyNumber().validate(3)).raw_value == "a"

    def test_element_refuses_a_null_and_defers_an_unknown(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        with pytest.raises(CtyFunctionError):
            element(CtyValue.null(CtyList(element_type=CtyString())), CtyNumber().validate(0))
        assert element(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyNumber().validate(0),
        ).is_unknown
        with pytest.raises(CtyFunctionError):
            element(lst, CtyValue.null(CtyNumber()))
        assert element(lst, CtyValue.unknown(CtyNumber())).is_unknown

    def test_element_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            element(CtyString().validate("a"), CtyNumber().validate(0))

    def test_element_empty_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate([])
        with pytest.raises(CtyFunctionError, match="cannot use element function with an empty list"):
            element(lst, CtyNumber().validate(0))


class TestCoalesceList:
    def test_coalescelist_first_valid(self) -> None:
        l1 = CtyList(element_type=CtyString()).validate(["a"])
        l2 = CtyList(element_type=CtyString()).validate(["b"])
        assert coalescelist(l1, l2).raw_value == ["a"]

    def test_coalescelist_second_valid(self) -> None:
        l1 = CtyList(element_type=CtyString()).validate([])
        l2 = CtyList(element_type=CtyString()).validate(["b"])
        assert coalescelist(l1, l2).raw_value == ["b"]

    def test_coalescelist_with_refuses_a_null(self) -> None:
        l1 = CtyValue.null(CtyList(element_type=CtyString()))
        l2 = CtyList(element_type=CtyString()).validate(["b"])
        assert coalescelist(l1, l2).raw_value == ["b"]

    def test_coalescelist_with_unknown(self) -> None:
        l1 = CtyValue.unknown(CtyList(element_type=CtyString()))
        l2 = CtyList(element_type=CtyString()).validate(["b"])
        assert coalescelist(l1, l2).is_unknown

    def test_coalescelist_no_valid(self) -> None:
        l1 = CtyList(element_type=CtyString()).validate([])
        l2 = CtyList(element_type=CtyString()).validate([])
        with pytest.raises(CtyFunctionError, match="no non-empty list or tuple found"):
            coalescelist(l1, l2)


class TestCompact:
    def test_compact_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "", "b"])
        assert compact(lst).raw_value == ["a", "b"]

    def test_compact_set(self) -> None:
        s = CtySet(element_type=CtyString()).validate({"a", "", "b"})
        assert sorted(compact(s).raw_value) == ["a", "b"]

    def test_compact_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "", "b"))
        assert compact(t).raw_value == ["a", "b"]

    def test_compact_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            compact(CtyValue.null(CtyList(element_type=CtyString())))
        assert compact(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_compact_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            compact(CtyString().validate("a"))

    def test_compact_wrong_element_type(self) -> None:
        lst = CtyList(element_type=CtyNumber()).validate([1, 2])
        with pytest.raises(CtyFunctionError):
            compact(lst)


class TestChunklist:
    def test_chunklist_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d", "e"])
        assert chunklist(lst, CtyNumber().validate(2)).raw_value == [
            ["a", "b"],
            ["c", "d"],
            ["e"],
        ]

    def test_chunklist_tuple(self) -> None:
        t = CtyTuple(
            element_types=(
                CtyString(),
                CtyString(),
                CtyString(),
                CtyString(),
                CtyString(),
            )
        ).validate(("a", "b", "c", "d", "e"))

        chunked_list = chunklist(t, CtyNumber().validate(2))

        # The result is a CtyList where each element is a CtyTuple
        # We need to convert the inner CtyValues to raw Python types for comparison
        raw_result = [[el.raw_value for el in chunk.value] for chunk in chunked_list.value]

        assert raw_result == [
            ["a", "b"],
            ["c", "d"],
            ["e"],
        ]

    def test_chunklist_refuses_a_null_and_defers_an_unknown(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d", "e"])
        with pytest.raises(CtyFunctionError):
            chunklist(CtyValue.null(CtyList(element_type=CtyString())), CtyNumber().validate(2))
        assert chunklist(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyNumber().validate(2),
        ).is_unknown
        with pytest.raises(CtyFunctionError):
            chunklist(lst, CtyValue.null(CtyNumber()))
        assert chunklist(lst, CtyValue.unknown(CtyNumber())).is_unknown

    def test_chunklist_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            chunklist(CtyString().validate("hello"), CtyNumber().validate(2))
        with pytest.raises(CtyFunctionError):
            chunklist(
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyString().validate("2"),
            )

    def test_chunklist_invalid_size(self) -> None:
        """Zero is legal -- go-cty reads it as one chunk holding everything."""
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d", "e"])
        with pytest.raises(CtyFunctionError, match="must be positive"):
            chunklist(lst, CtyNumber().validate(-1))


class TestLookup:
    def test_lookup_map_found(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert lookup(m, CtyString().validate("a"), CtyString().validate("default")).raw_value == "x"

    def test_lookup_map_not_found(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert lookup(m, CtyString().validate("b"), CtyString().validate("default")).raw_value == "default"

    def test_lookup_object_found(self) -> None:
        o = CtyObject({"a": CtyString()}).validate({"a": "x"})
        assert lookup(o, CtyString().validate("a"), CtyString().validate("default")).raw_value == "x"

    def test_lookup_object_not_found(self) -> None:
        o = CtyObject({"a": CtyString()}).validate({"a": "x"})
        assert lookup(o, CtyString().validate("b"), CtyString().validate("default")).raw_value == "default"

    def test_lookup_refuses_a_null_and_defers_an_unknown(self) -> None:
        """A null map used to fall through to the default, which is a value.

        go-cty refuses the argument instead: a null map is not an empty map,
        and answering "not found" for it invents a fact.
        """
        default = CtyString().validate("default")

        for null_position in (
            (CtyValue.null(CtyMap(element_type=CtyString())), CtyString().validate("a"), default),
            (
                CtyMap(element_type=CtyString()).validate({"a": "x"}),
                CtyValue.null(CtyString()),
                default,
            ),
        ):
            with pytest.raises(CtyFunctionError):
                lookup(*null_position)

        assert lookup(
            CtyValue.unknown(CtyMap(element_type=CtyString())),
            CtyString().validate("a"),
            default,
        ).is_unknown

    def test_lookup_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            lookup(
                CtyString().validate("a"),
                CtyString().validate("a"),
                CtyString().validate("a"),
            )


class TestMerge:
    def test_merge_maps(self) -> None:
        m1 = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        m2 = CtyMap(element_type=CtyString()).validate({"b": "z", "c": "w"})
        assert merge(m1, m2).raw_value == {"a": "x", "b": "z", "c": "w"}

    def test_merge_objects(self) -> None:
        o1 = CtyObject({"a": CtyString(), "b": CtyString()}).validate({"a": "x", "b": "y"})
        o2 = CtyObject({"b": CtyString(), "c": CtyString()}).validate({"b": "z", "c": "w"})
        assert merge(o1, o2).raw_value == {"a": "x", "b": "z", "c": "w"}

    def test_merge_mixed(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        o = CtyObject({"b": CtyString(), "c": CtyString()}).validate({"b": "z", "c": "w"})
        assert merge(m, o).raw_value == {"a": "x", "b": "z", "c": "w"}

    def test_merge_with_refuses_a_null_and_defers_an_unknown(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert merge(m, CtyValue.null(CtyMap(element_type=CtyString()))).raw_value == {"a": "x"}
        assert merge(m, CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_merge_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            merge(CtyString().validate("a"), CtyMap(element_type=CtyString()).validate({}))


class TestZipmap:
    def test_zipmap(self) -> None:
        keys = CtyList(element_type=CtyString()).validate(["a", "b"])
        values = CtyList(element_type=CtyNumber()).validate([1, 2])
        assert zipmap(keys, values).raw_value == {"a": 1, "b": 2}

    def test_zipmap_refuses_a_null_and_defers_an_unknown(self) -> None:
        """A null list used to zip to an empty map, silently losing the other
        list's entries."""
        keys = CtyList(element_type=CtyString()).validate(["a", "b"])
        values = CtyList(element_type=CtyNumber()).validate([1, 2])

        with pytest.raises(CtyFunctionError):
            zipmap(keys, CtyValue.null(CtyList(element_type=CtyNumber())))
        with pytest.raises(CtyFunctionError):
            zipmap(CtyValue.null(CtyList(element_type=CtyString())), values)

        assert zipmap(keys, CtyValue.unknown(CtyList(element_type=CtyNumber()))).is_unknown
        assert zipmap(CtyValue.unknown(CtyList(element_type=CtyString())), values).is_unknown

    def test_zipmap_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            zipmap(
                CtyString().validate("a"),
                CtyList(element_type=CtyNumber()).validate([]),
            )

    def test_zipmap_different_lengths(self) -> None:
        keys = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        values = CtyList(element_type=CtyNumber()).validate([1, 2])
        assert zipmap(keys, values).raw_value == {"a": 1, "b": 2}


class TestSliceConcat:
    def test_slice_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert slice(lst, CtyNumber().validate(1), CtyNumber().validate(3)).raw_value == [
            "b",
            "c",
        ]

    def test_slice_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "b", "c"))
        assert slice(t, CtyNumber().validate(1), CtyNumber().validate(3)).raw_value == [
            "b",
            "c",
        ]

    def test_slice_refuses_a_null_and_defers_an_unknown(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        zero, one = CtyNumber().validate(0), CtyNumber().validate(1)

        for arguments in (
            (CtyValue.null(CtyList(element_type=CtyString())), zero, one),
            (lst, CtyValue.null(CtyNumber()), one),
            (lst, zero, CtyValue.null(CtyNumber())),
        ):
            with pytest.raises(CtyFunctionError):
                slice(*arguments)

        assert slice(CtyValue.unknown(CtyList(element_type=CtyString())), zero, one).is_unknown
        assert slice(lst, CtyValue.unknown(CtyNumber()), one).is_unknown
        assert slice(lst, zero, CtyValue.unknown(CtyNumber())).is_unknown

    def test_slice_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            slice(
                CtyString().validate("hello"),
                CtyNumber().validate(0),
                CtyNumber().validate(1),
            )
        with pytest.raises(CtyFunctionError):
            slice(
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyString().validate("0"),
                CtyNumber().validate(1),
            )
        with pytest.raises(CtyFunctionError):
            slice(
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyNumber().validate(0),
                CtyString().validate("1"),
            )

    def test_concat_lists(self) -> None:
        l1 = CtyList(element_type=CtyString()).validate(["a", "b"])
        l2 = CtyList(element_type=CtyString()).validate(["c", "d"])
        assert concat(l1, l2).raw_value == ["a", "b", "c", "d"]

    def test_concat_tuples(self) -> None:
        """A tuple in, a tuple out -- go-cty only returns a list when every
        argument is a list whose element types unify."""
        t1 = CtyTuple(element_types=(CtyString(), CtyString())).validate(("a", "b"))
        t2 = CtyTuple(element_types=(CtyString(), CtyString())).validate(("c", "d"))

        result = concat(t1, t2)

        assert isinstance(result.type, CtyTuple)
        assert result.raw_value == ("a", "b", "c", "d")

    def test_concat_mixed(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])
        t = CtyTuple(element_types=(CtyString(), CtyString())).validate(("c", "d"))

        result = concat(lst, t)

        assert isinstance(result.type, CtyTuple)
        assert result.raw_value == ("a", "b", "c", "d")

    def test_concat_refuses_a_null_argument(self) -> None:
        """This used to skip nulls silently, so the result had fewer elements
        than the arguments described. go-cty refuses the call."""
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])

        with pytest.raises(CtyFunctionError):
            concat(lst, CtyValue.null(CtyList(element_type=CtyString())))

    def test_concat_with_an_unknown_list_keeps_the_element_type(self) -> None:
        """The type is settled by the argument types even when the contents
        are not, so it does not collapse to `list(dynamic)`."""
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])

        result = concat(lst, CtyValue.unknown(CtyList(element_type=CtyString())))

        assert result.is_unknown
        assert result.type.equal(CtyList(element_type=CtyString()))

    def test_concat_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            concat(
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyString().validate("b"),
            )

    def test_concat_requires_an_argument(self) -> None:
        with pytest.raises(CtyFunctionError):
            concat()

    def test_concat_widens_element_types_that_unify(self) -> None:
        """`list(string)` + `list(number)` is a `list(string)`, not a
        `list(dynamic)` holding the originals: the element types unify, and the
        elements are converted rather than merely collected."""
        l1 = CtyList(element_type=CtyString()).validate(["a"])
        l2 = CtyList(element_type=CtyNumber()).validate([1])

        result = concat(l1, l2)

        assert result.type.equal(CtyList(element_type=CtyString()))
        assert result.raw_value == ["a", "1"]

    def test_concat_falls_back_to_a_tuple_when_the_elements_do_not_unify(self) -> None:
        """Only a tuple can carry a different type per position."""
        result = concat(
            CtyList(element_type=CtyNumber()).validate([1]),
            CtyList(element_type=CtyBool()).validate([True]),
        )

        assert result.type.equal(CtyTuple(element_types=(CtyNumber(), CtyBool())))


class TestLength:
    def test_length_list(self) -> None:
        lst = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert length(lst).raw_value == 2

    def test_length_set(self) -> None:
        s = CtySet(element_type=CtyString()).validate({"a", "b"})
        assert length(s).raw_value == 2

    def test_length_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString())).validate(("a", "b"))
        assert length(t).raw_value == 2

    def test_length_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        assert length(m).raw_value == 2

    def test_length_string_is_refused(self) -> None:
        """go-cty's `length` is collections-only; counting a string is
        `strlen`'s job. Pinned properly in test_gocty_stdlib_parity.py."""
        with pytest.raises(CtyFunctionError):
            length(CtyString().validate("hello"))

    def test_length_refuses_a_null_and_defers_an_unknown(self) -> None:
        with pytest.raises(CtyFunctionError):
            length(CtyValue.null(CtyList(element_type=CtyString())))
        assert length(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_length_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            length(CtyNumber().validate(123))


# 🌊🪢🔚
