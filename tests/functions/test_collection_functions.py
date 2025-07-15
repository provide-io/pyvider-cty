import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyList, CtySet, CtyTuple, CtyDynamic, CtyString, CtyNumber, CtyBool,
    CtyValue, CtyObject
)
from pyvider.cty.functions.collection_functions import distinct, flatten, sort
from pyvider.cty.exceptions import CtyFunctionError

class TestCollectionFunctions:
    def test_distinct_list_primitives(self):
        list_type = CtyList(element_type=CtyString())
        input_val = list_type.validate(["a", "b", "a", "c", "b"])
        result = distinct(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equal(CtyString())
        assert [v.value for v in result.value] == ["a", "b", "c"]

    def test_flatten_list_of_lists_primitives(self):
        list_of_lists_type = CtyList(element_type=CtyList(element_type=CtyNumber()))
        input_val = list_of_lists_type.validate([[1, 2], [3], [], [4, 5]])
        result = flatten(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equal(CtyNumber())
        assert [v.value for v in result.value] == [Decimal("1"), Decimal("2"), Decimal("3"), Decimal("4"), Decimal("5")]

    def test_sort_primitives(self):
        list_type = CtyList(element_type=CtyString())
        input_val = list_type.validate(["c", "a", "b"])
        result = sort(input_val)
        assert isinstance(result.type, CtyList)
        assert result.type.element_type.equal(CtyString())
        assert [v.value for v in result.value] == ["a", "b", "c"]
