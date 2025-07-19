import pytest

from pyvider.cty import (
    CtyDynamic,
    CtyList,
    CtyMap,
    CtyNumber,
    CtyString,
    CtyValue,
)
from pyvider.cty.exceptions import CtyFunctionError
from pyvider.cty.functions import (
    concat,
    contains,
    distinct,
    flatten,
    keys,
    length,
    slice,
    sort,
    values,
)


class TestCollectionFunctions:
    def test_distinct_list_primitives(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b", "a", "c"])
        result = distinct(list_val)
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_distinct_null_unknown(self) -> None:
        assert distinct(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert distinct(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_distinct_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            distinct(CtyString().validate("not a collection"))

    def test_distinct_unhashable(self) -> None:
        list_val = CtyList(element_type=CtyMap(element_type=CtyString())).validate(
            [{"a": "b"}]
        )
        with pytest.raises(CtyFunctionError):
            distinct(list_val)

    def test_flatten_list_of_lists_primitives(self) -> None:
        list_val = CtyList(element_type=CtyList(element_type=CtyString())).validate(
            [["a"], ["b", "c"]]
        )
        result = flatten(list_val)
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_flatten_null_unknown(self) -> None:
        assert flatten(
            CtyValue.null(CtyList(element_type=CtyList(element_type=CtyString())))
        ).is_null
        assert flatten(
            CtyValue.unknown(CtyList(element_type=CtyList(element_type=CtyString())))
        ).is_unknown

    def test_flatten_with_null_elements(self) -> None:
        list_val = CtyList(element_type=CtyDynamic()).validate([["a"], None, ["b"]])
        result = flatten(list_val)
        assert [v.value for v in result.value] == ["a", "b"]

    def test_flatten_with_unknown_elements(self) -> None:
        list_val = CtyList(element_type=CtyList(element_type=CtyString())).validate(
            [["a"], CtyValue.unknown(CtyList(element_type=CtyString()))]
        )
        assert flatten(list_val).is_unknown

    def test_flatten_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            flatten(CtyString().validate("not a collection"))

    def test_flatten_invalid_element_type(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b"])
        with pytest.raises(CtyFunctionError):
            flatten(list_val)

    def test_sort_primitives(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["c", "a", "b"])
        result = sort(list_val)
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_sort_null_unknown(self) -> None:
        assert sort(CtyValue.null(CtyList(element_type=CtyString()))).is_null
        assert sort(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_sort_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            sort(CtyString().validate("not a collection"))

    def test_sort_unsupported_element_type(self) -> None:
        list_val = CtyList(element_type=CtyMap(element_type=CtyString())).validate(
            [{"a": "b"}]
        )
        with pytest.raises(CtyFunctionError):
            sort(list_val)

    def test_sort_with_null_element(self) -> None:
        list_val = CtyList(element_type=CtyDynamic()).validate(["a", None, "c"])
        with pytest.raises(CtyFunctionError):
            sort(list_val)

    def test_sort_with_unknown_element(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(
            ["a", CtyValue.unknown(CtyString()), "c"]
        )
        with pytest.raises(CtyFunctionError):
            sort(list_val)

    def test_length(self) -> None:
        assert (
            length(CtyList(element_type=CtyString()).validate(["a", "b", "c"])).value
            == 3
        )
        assert (
            length(
                CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
            ).value
            == 2
        )

    def test_length_null_unknown(self) -> None:
        assert length(CtyValue.null(CtyList(element_type=CtyString()))).is_unknown
        assert length(CtyValue.unknown(CtyList(element_type=CtyString()))).is_unknown

    def test_length_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            length(CtyString().validate("no length"))

    def test_slice(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d"])
        result = slice(list_val, CtyNumber().validate(1), CtyNumber().validate(3))
        assert [v.value for v in result.value] == ["b", "c"]

    def test_slice_null_unknown(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d"])
        assert slice(
            CtyValue.null(CtyList(element_type=CtyString())),
            CtyNumber().validate(1),
            CtyNumber().validate(3),
        ).is_unknown
        assert slice(
            list_val, CtyValue.null(CtyNumber()), CtyNumber().validate(3)
        ).is_unknown
        assert slice(
            list_val, CtyNumber().validate(1), CtyValue.null(CtyNumber())
        ).is_unknown

    def test_slice_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            slice(
                CtyString().validate("a"),
                CtyNumber().validate(0),
                CtyNumber().validate(1),
            )
        with pytest.raises(CtyFunctionError):
            slice(
                CtyList(element_type=CtyString()).validate([]),
                CtyString().validate("a"),
                CtyNumber().validate(1),
            )

    def test_concat(self) -> None:
        list1 = CtyList(element_type=CtyString()).validate(["a", "b"])
        list2 = CtyList(element_type=CtyString()).validate(["c", "d"])
        result = concat(list1, list2)
        assert [v.value for v in result.value] == ["a", "b", "c", "d"]

    def test_concat_null_unknown(self) -> None:
        list1 = CtyList(element_type=CtyString()).validate(["a", "b"])
        assert concat(
            list1, CtyValue.null(CtyList(element_type=CtyString()))
        ).is_unknown
        assert concat(
            list1, CtyValue.unknown(CtyList(element_type=CtyString()))
        ).is_unknown

    def test_concat_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            concat(
                CtyList(element_type=CtyString()).validate([]),
                CtyString().validate("a"),
            )

    def test_contains(self) -> None:
        list_val = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert contains(list_val, CtyString().validate("b")).value is True
        assert contains(list_val, CtyString().validate("d")).value is False

    def test_contains_null_unknown(self) -> None:
        CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert contains(
            CtyValue.null(CtyList(element_type=CtyString())), CtyString().validate("a")
        ).is_unknown
        assert contains(
            CtyValue.unknown(CtyList(element_type=CtyString())),
            CtyString().validate("a"),
        ).is_unknown

    def test_contains_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            contains(CtyString().validate("a"), CtyString().validate("a"))

    def test_keys(self) -> None:
        map_val = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        result = keys(map_val)
        assert sorted([v.value for v in result.value]) == ["a", "b"]

    def test_keys_null_unknown(self) -> None:
        assert keys(CtyValue.null(CtyMap(element_type=CtyString()))).is_unknown
        assert keys(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_keys_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            keys(CtyString().validate("a"))

    def test_values(self) -> None:
        map_val = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        result = values(map_val)
        assert sorted([v.value for v in result.value]) == ["x", "y"]

    def test_values_null_unknown(self) -> None:
        assert values(CtyValue.null(CtyMap(element_type=CtyString()))).is_unknown
        assert values(CtyValue.unknown(CtyMap(element_type=CtyString()))).is_unknown

    def test_values_invalid_type(self) -> None:
        with pytest.raises(CtyFunctionError):
            values(CtyString().validate("a"))
