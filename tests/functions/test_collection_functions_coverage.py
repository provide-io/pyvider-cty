import pytest
from pyvider.cty.functions.collection_functions import flatten, concat
from pyvider.cty.values import CtyValue
from pyvider.cty.types import CtyString, CtyNumber, CtyList, CtyTuple, CtyDynamic
from pyvider.cty.exceptions import CtyFunctionError

def test_flatten_with_mixed_types():
    list_type = CtyList(element_type=CtyList(element_type=CtyString()))
    value = list_type.validate([["a", "b"], ["c", 1]])
    with pytest.raises(CtyFunctionError):
        flatten(value)

def test_flatten_with_empty_list():
    list_type = CtyList(element_type=CtyList(element_type=CtyString()))
    value = list_type.validate([[]])
    result = flatten(value)
    assert result.type.equal(CtyList(element_type=CtyDynamic()))
    assert result.value == tuple()

def test_concat_with_mixed_types():
    list1 = CtyList(element_type=CtyString()).validate(["a", "b"])
    list2 = CtyList(element_type=CtyNumber()).validate([1, 2])
    result = concat(list1, list2)
    assert result.type.equal(CtyList(element_type=CtyDynamic()))
    assert len(result.value) == 4
