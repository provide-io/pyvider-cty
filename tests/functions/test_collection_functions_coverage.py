from pyvider.cty.functions.collection_functions import concat, flatten
from pyvider.cty.types import CtyDynamic, CtyList, CtyNumber, CtyString


def test_flatten_with_mixed_types() -> None:
    list_type = CtyList(element_type=CtyDynamic())
    value = list_type.validate([["a", "b"], [1, 2]])
    result = flatten(value)
    assert result.type.equal(CtyList(element_type=CtyDynamic()))
    assert len(result.value) == 4


def test_flatten_with_empty_list() -> None:
    list_type = CtyList(element_type=CtyList(element_type=CtyString()))
    value = list_type.validate([[]])
    result = flatten(value)
    assert result.type.equal(CtyList(element_type=CtyDynamic()))
    assert result.value == tuple()


def test_concat_with_mixed_types() -> None:
    list1 = CtyList(element_type=CtyString()).validate(["a", "b"])
    list2 = CtyList(element_type=CtyNumber()).validate([1, 2])
    result = concat(list1, list2)
    assert result.type.equal(CtyList(element_type=CtyDynamic()))
    assert len(result.value) == 4
