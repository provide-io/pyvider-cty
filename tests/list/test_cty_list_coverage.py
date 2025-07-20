import pytest
from pyvider.cty.types.collections.list import CtyList
from pyvider.cty.types import CtyString, CtyNumber, CtyDynamic
from pyvider.cty.values import CtyValue
from pyvider.cty.exceptions import CtyListValidationError

def test_attrs_post_init_invalid_element_type():
    with pytest.raises(CtyListValidationError):
        CtyList(element_type="not_a_type")

def test_validate_none():
    list_type = CtyList(element_type=CtyString())
    assert list_type.validate(None).is_null

def test_validate_with_set():
    list_type = CtyList(element_type=CtyNumber())
    value = {1, 2, 3}
    result = list_type.validate(value)
    assert isinstance(result.value, tuple)
    assert sorted([v.value for v in result.value]) == [1, 2, 3]

def test_validate_null_element_in_list():
    list_type = CtyList(element_type=CtyString())
    with pytest.raises(CtyListValidationError, match="List elements cannot be null"):
        list_type.validate(["a", None, "c"])

def test_element_at_on_non_cty_list_value():
    list_type = CtyList(element_type=CtyString())
    with pytest.raises(CtyListValidationError, match="Expected CtyValue with CtyList type"):
        list_type.element_at(CtyValue(CtyNumber(), 1), 0)

def test_element_at_on_non_list_internal_value():
    list_type = CtyList(element_type=CtyString())
    # Manually create a CtyValue with an inconsistent internal value
    inconsistent_value = CtyValue(list_type, value="not a list")
    with pytest.raises(CtyListValidationError, match="Internal error: CtyValue of CtyList type does not wrap a list/tuple"):
        list_type.element_at(inconsistent_value, 0)
