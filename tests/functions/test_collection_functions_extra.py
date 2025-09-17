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
from pyvider.cty.functions import (
    chunklist,
    coalescelist,
    compact,
    concat,
    contains,
    distinct,
    element,
    flatten,
    hasindex,
    index,
    keys,
    length,
    lookup,
    merge,
    reverse,
    slice,
    sort,
    values,
    zipmap,
)


class TestDistinct:
    def test_distinct_with_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "a"])
        assert distinct(l).raw_value == ["a", "b"]

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
        l = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["a"]])
        with pytest.raises(CtyFunctionError, match="not hashable"):
            distinct(l)

    def test_distinct_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            distinct(CtyString().validate("hello"))


class TestFlatten:
    def test_flatten_list_of_lists(self) -> None:
        l = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a", "b"], ["c"]])
        assert flatten(l).raw_value == ["a", "b", "c"]

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
        l = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                None,
                CtyList(element_type=CtyString()).validate(["b"]),
            ]
        )
        assert flatten(l).raw_value == ["a", "b"]

    def test_flatten_with_unknown_element(self) -> None:
        l = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyValue.unknown(CtyList(element_type=CtyString())),
            ]
        )
        assert flatten(l).is_unknown

    def test_flatten_with_non_list_element(self) -> None:
        l = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyString().validate("b"),
            ]
        )
        with pytest.raises(CtyFunctionError, match="all elements must be lists, sets, or tuples"):
            flatten(l)

    def test_flatten_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            flatten(CtyString().validate("hello"))

    def test_flatten_empty(self) -> None:
        l = CtyList(element_type=CtyList(element_type=CtyString())).validate([])
        assert flatten(l).raw_value == []

    def test_flatten_mixed_types(self) -> None:
        l = CtyList(element_type=CtyDynamic()).validate(
            [
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyList(element_type=CtyNumber()).validate([1]),
            ]
        )
        result = flatten(l)
        assert isinstance(result.type, CtyList)
        assert isinstance(result.type.element_type, CtyDynamic)
        assert result.raw_value == ["a", 1]


class TestContains:
    def test_contains_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert contains(l, CtyString().validate("a")).raw_value is True
        assert contains(l, CtyString().validate("c")).raw_value is False

    def test_contains_set(self) -> None:
        s = CtySet(element_type=CtyString()).validate({"a", "b"})
        assert contains(s, CtyString().validate("a")).raw_value is True
        assert contains(s, CtyString().validate("c")).raw_value is False

    def test_contains_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString())).validate(("a", "b"))
        assert contains(t, CtyString().validate("a")).raw_value is True
        assert contains(t, CtyString().validate("c")).raw_value is False

    def test_contains_null_unknown(self) -> None:
        CtyList(element_type=CtyString()).validate(["a", "b"])
        assert contains(CtyValue.null(CtyList(element_type=CtyString())), CtyString().validate("a")).is_unknown
        assert contains(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyString().validate("a"),
        ).is_unknown

    def test_contains_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            contains(CtyString().validate("a"), CtyString().validate("a"))


class TestKeysValues:
    def test_keys_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        assert keys(m).raw_value == ["a", "b"]

    def test_keys_object(self) -> None:
        o = CtyObject({"a": CtyString(), "b": CtyString()}).validate({"a": "x", "b": "y"})
        assert keys(o).raw_value == ["a", "b"]

    def test_keys_null_unknown(self) -> None:
        assert keys(CtyValue.null(CtyMap(element_type=CtyString()))).is_unknown
        assert keys(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_keys_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            keys(CtyString().validate("hello"))

    def test_values_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        assert values(m).raw_value == ["x", "y"]

    def test_values_object(self) -> None:
        o = CtyObject({"a": CtyString(), "b": CtyString()}).validate({"a": "x", "b": "y"})
        assert values(o).raw_value == ["x", "y"]

    def test_values_null_unknown(self) -> None:
        assert values(CtyValue.null(CtyMap(element_type=CtyString()))).is_unknown
        assert values(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_values_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            values(CtyString().validate("hello"))


class TestReverse:
    def test_reverse_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert reverse(l).raw_value == ["c", "b", "a"]

    def test_reverse_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "b", "c"))
        assert reverse(t).raw_value == ("c", "b", "a")

    def test_reverse_null_unknown(self) -> None:
        assert reverse(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert reverse(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_reverse_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            reverse(CtyString().validate("hello"))


class TestHasIndexIndex:
    def test_hasindex_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert hasindex(l, CtyNumber().validate(0)).raw_value is True
        assert hasindex(l, CtyNumber().validate(2)).raw_value is False
        assert hasindex(l, CtyString().validate("a")).raw_value is False

    def test_hasindex_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert hasindex(m, CtyString().validate("a")).raw_value is True
        assert hasindex(m, CtyString().validate("b")).raw_value is False
        assert hasindex(m, CtyNumber().validate(0)).raw_value is False

    def test_hasindex_null_unknown(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a"])
        assert (
            hasindex(
                CtyValue.null(CtyList(element_type=CtyString())),
                CtyNumber().validate(0),
            ).raw_value
            is False
        )
        assert hasindex(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyNumber().validate(0),
        ).is_unknown
        assert hasindex(l, CtyValue.null(CtyNumber())).raw_value is False
        assert hasindex(l, CtyValue.unknown(CtyNumber())).is_unknown

    def test_hasindex_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            hasindex(CtyString().validate("a"), CtyNumber().validate(0))

    def test_index_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert index(l, CtyNumber().validate(1)).raw_value == "b"

    def test_index_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert index(m, CtyString().validate("a")).raw_value == "x"

    def test_index_not_found(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a"])
        with pytest.raises(CtyFunctionError, match="key does not exist"):
            index(l, CtyNumber().validate(1))


class TestElement:
    def test_element_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert element(l, CtyNumber().validate(1)).raw_value == "b"
        assert element(l, CtyNumber().validate(3)).raw_value == "a"

    def test_element_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "b", "c"))
        assert element(t, CtyNumber().validate(1)).raw_value == "b"
        assert element(t, CtyNumber().validate(3)).raw_value == "a"

    def test_element_null_unknown(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert element(CtyValue.null(CtyList(element_type=CtyString())), CtyNumber().validate(0)).is_unknown
        assert element(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyNumber().validate(0),
        ).is_unknown
        assert element(l, CtyValue.null(CtyNumber())).is_unknown
        assert element(l, CtyValue.unknown(CtyNumber())).is_unknown

    def test_element_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            element(CtyString().validate("a"), CtyNumber().validate(0))

    def test_element_empty_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate([])
        with pytest.raises(CtyFunctionError, match="cannot use element function with an empty list"):
            element(l, CtyNumber().validate(0))


class TestCoalesceList:
    def test_coalescelist_first_valid(self) -> None:
        l1 = CtyList(element_type=CtyString()).validate(["a"])
        l2 = CtyList(element_type=CtyString()).validate(["b"])
        assert coalescelist(l1, l2).raw_value == ["a"]

    def test_coalescelist_second_valid(self) -> None:
        l1 = CtyList(element_type=CtyString()).validate([])
        l2 = CtyList(element_type=CtyString()).validate(["b"])
        assert coalescelist(l1, l2).raw_value == ["b"]

    def test_coalescelist_with_null(self) -> None:
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
        l = CtyList(element_type=CtyString()).validate(["a", "", "b"])
        assert compact(l).raw_value == ["a", "b"]

    def test_compact_set(self) -> None:
        s = CtySet(element_type=CtyString()).validate({"a", "", "b"})
        assert sorted(compact(s).raw_value) == ["a", "b"]

    def test_compact_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "", "b"))
        assert compact(t).raw_value == ["a", "b"]

    def test_compact_null_unknown(self) -> None:
        assert compact(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert compact(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_compact_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            compact(CtyString().validate("a"))

    def test_compact_wrong_element_type(self) -> None:
        l = CtyList(element_type=CtyNumber()).validate([1, 2])
        with pytest.raises(CtyFunctionError):
            compact(l)


class TestChunklist:
    def test_chunklist_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d", "e"])
        assert chunklist(l, CtyNumber().validate(2)).raw_value == [
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

    def test_chunklist_null_unknown(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d", "e"])
        assert chunklist(CtyValue.null(CtyList(element_type=CtyString())), CtyNumber().validate(2)).is_unknown
        assert chunklist(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyNumber().validate(2),
        ).is_unknown
        assert chunklist(l, CtyValue.null(CtyNumber())).is_unknown
        assert chunklist(l, CtyValue.unknown(CtyNumber())).is_unknown

    def test_chunklist_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            chunklist(CtyString().validate("hello"), CtyNumber().validate(2))
        with pytest.raises(CtyFunctionError):
            chunklist(
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyString().validate("2"),
            )

    def test_chunklist_invalid_size(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d", "e"])
        with pytest.raises(CtyFunctionError, match="size must be a positive number"):
            chunklist(l, CtyNumber().validate(0))


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

    def test_lookup_null_unknown(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        d = CtyString().validate("default")
        assert (
            lookup(
                CtyValue.null(CtyMap(element_type=CtyString())),
                CtyString().validate("a"),
                d,
            ).raw_value
            == "default"
        )
        assert lookup(
            CtyValue.unknown(CtyMap(element_type=CtyString())),
            CtyString().validate("a"),
            d,
        ).is_unknown
        assert lookup(m, CtyValue.null(CtyString()), d).raw_value == "default"
        assert lookup(m, CtyValue.unknown(CtyString()), d).is_unknown

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

    def test_merge_with_null_unknown(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x"})
        assert merge(m, CtyValue.null(CtyMap(element_type=CtyString()))).raw_value == {"a": "x"}
        assert merge(m, CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_merge_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            merge(CtyString().validate("a"), CtyMap(element_type=CtyString()).validate({}))


class TestSetProductZipmap:
    def test_zipmap(self) -> None:
        keys = CtyList(element_type=CtyString()).validate(["a", "b"])
        values = CtyList(element_type=CtyNumber()).validate([1, 2])
        assert zipmap(keys, values).raw_value == {"a": 1, "b": 2}

    def test_zipmap_null_unknown(self) -> None:
        keys = CtyList(element_type=CtyString()).validate(["a", "b"])
        values = CtyList(element_type=CtyNumber()).validate([1, 2])
        assert zipmap(keys, CtyValue.null(CtyList(element_type=CtyNumber()))).raw_value == {}
        assert zipmap(keys, CtyValue.unknown(CtyList(element_type=CtyNumber()))).is_unknown
        assert zipmap(CtyValue.null(CtyList(element_type=CtyString())), values).raw_value == {}
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


class TestSort:
    def test_sort_list_of_strings(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["c", "a", "b"])
        assert sort(l).raw_value == ["a", "b", "c"]

    def test_sort_list_of_numbers(self) -> None:
        l = CtyList(element_type=CtyNumber()).validate([3, 1, 2])
        assert sort(l).raw_value == [1, 2, 3]

    def test_sort_with_null_unknown(self) -> None:
        assert sort(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert sort(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_sort_with_null_element(self) -> None:
        l = CtyList(element_type=CtyDynamic()).validate(
            [CtyString().validate("a"), CtyValue.null(CtyString())]
        )
        with pytest.raises(CtyFunctionError, match="cannot sort list with null or unknown elements"):
            sort(l)

    def test_sort_with_unknown_element(self) -> None:
        l = CtyList(element_type=CtyDynamic()).validate(
            [CtyString().validate("a"), CtyValue.unknown(CtyString())]
        )
        with pytest.raises(CtyFunctionError, match="cannot sort list with null or unknown elements"):
            sort(l)

    def test_sort_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            sort(CtyString().validate("hello"))

    def test_sort_unsupported_element_type(self) -> None:
        l = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"]])
        with pytest.raises(CtyFunctionError, match="elements must be string, number, or bool"):
            sort(l)


class TestLength:
    def test_length_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert length(l).raw_value == 2

    def test_length_set(self) -> None:
        s = CtySet(element_type=CtyString()).validate({"a", "b"})
        assert length(s).raw_value == 2

    def test_length_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString())).validate(("a", "b"))
        assert length(t).raw_value == 2

    def test_length_map(self) -> None:
        m = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        assert length(m).raw_value == 2

    def test_length_string(self) -> None:
        s = CtyString().validate("hello")
        assert length(s).raw_value == 5

    def test_length_null_unknown(self) -> None:
        assert length(CtyValue.null(CtyList(element_type=CtyString()))).is_unknown
        assert length(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_length_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            length(CtyNumber().validate(123))


class TestSlice:
    def test_slice_list(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert slice(l, CtyNumber().validate(1), CtyNumber().validate(3)).raw_value == [
            "b",
            "c",
        ]

    def test_slice_tuple(self) -> None:
        t = CtyTuple(element_types=(CtyString(), CtyString(), CtyString())).validate(("a", "b", "c"))
        assert slice(t, CtyNumber().validate(1), CtyNumber().validate(3)).raw_value == [
            "b",
            "c",
        ]

    def test_slice_null_unknown(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert slice(
            CtyValue.null(CtyList(element_type=CtyString())),
            CtyNumber().validate(0),
            CtyNumber().validate(1),
        ).is_unknown
        assert slice(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyNumber().validate(0),
            CtyNumber().validate(1),
        ).is_unknown
        assert slice(l, CtyValue.null(CtyNumber()), CtyNumber().validate(1)).is_unknown
        assert slice(l, CtyValue.unknown(CtyNumber()), CtyNumber().validate(1)).is_unknown
        assert slice(l, CtyNumber().validate(0), CtyValue.null(CtyNumber())).is_unknown
        assert slice(l, CtyNumber().validate(0), CtyValue.unknown(CtyNumber())).is_unknown

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


class TestConcat:
    def test_concat_lists(self) -> None:
        l1 = CtyList(element_type=CtyString()).validate(["a", "b"])
        l2 = CtyList(element_type=CtyString()).validate(["c", "d"])
        assert concat(l1, l2).raw_value == ["a", "b", "c", "d"]

    def test_concat_tuples(self) -> None:
        t1 = CtyTuple(element_types=(CtyString(), CtyString())).validate(("a", "b"))
        t2 = CtyTuple(element_types=(CtyString(), CtyString())).validate(("c", "d"))
        assert concat(t1, t2).raw_value == ["a", "b", "c", "d"]

    def test_concat_mixed(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b"])
        t = CtyTuple(element_types=(CtyString(), CtyString())).validate(("c", "d"))
        assert concat(l, t).raw_value == ["a", "b", "c", "d"]

    def test_concat_with_null_unknown(self) -> None:
        l = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert concat(l, CtyValue.null(CtyList(element_type=CtyString()))).raw_value == [
            "a",
            "b",
        ]
        assert concat(l, CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_concat_wrong_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            concat(
                CtyList(element_type=CtyString()).validate(["a"]),
                CtyString().validate("b"),
            )

    def test_concat_empty(self) -> None:
        assert concat().raw_value == []

    def test_concat_mixed_types(self) -> None:
        l1 = CtyList(element_type=CtyString()).validate(["a"])
        l2 = CtyList(element_type=CtyNumber()).validate([1])
        result = concat(l1, l2)
        assert isinstance(result.type, CtyList)
        assert isinstance(result.type.element_type, CtyDynamic)
        assert result.raw_value == ["a", 1]
