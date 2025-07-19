import pytest
from pyvider.cty import CtyList, CtySet, CtyTuple, CtyString, CtyNumber, CtyValue, CtyDynamic, CtyMap
from pyvider.cty.functions import distinct, flatten, sort, length, slice, concat, contains, keys, values
from pyvider.cty.exceptions import CtyFunctionError

class TestCollectionFunctions:
    def test_distinct_list_primitives(self):
        list_val = CtyList(element_type=CtyString()).validate(["a", "b", "a", "c"])
        result = distinct(list_val)
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_flatten_list_of_lists_primitives(self):
        list_val = CtyList(element_type=CtyList(element_type=CtyString())).validate([["a"], ["b", "c"]])
        result = flatten(list_val)
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_sort_primitives(self):
        list_val = CtyList(element_type=CtyString()).validate(["c", "a", "b"])
        result = sort(list_val)
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_length(self):
        assert length(CtyList(element_type=CtyString()).validate(["a", "b", "c"])).value == 3
        assert length(CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})).value == 2

    def test_slice(self):
        list_val = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d"])
        result = slice(list_val, CtyNumber().validate(1), CtyNumber().validate(3))
        assert [v.value for v in result.value] == ["b", "c"]

    def test_concat(self):
        list1 = CtyList(element_type=CtyString()).validate(["a", "b"])
        list2 = CtyList(element_type=CtyString()).validate(["c", "d"])
        result = concat(list1, list2)
        assert [v.value for v in result.value] == ["a", "b", "c", "d"]

    def test_contains(self):
        list_val = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
        assert contains(list_val, CtyString().validate("b")).value is True
        assert contains(list_val, CtyString().validate("d")).value is False

    def test_keys(self):
        map_val = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        result = keys(map_val)
        assert sorted([v.value for v in result.value]) == ["a", "b"]

    def test_values(self):
        map_val = CtyMap(element_type=CtyString()).validate({"a": "x", "b": "y"})
        result = values(map_val)
        assert sorted([v.value for v in result.value]) == ["x", "y"]
