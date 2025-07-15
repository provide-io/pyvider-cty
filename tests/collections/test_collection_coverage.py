import pytest
from pyvider.cty import CtyString, CtyNumber, CtyList, CtyMap
from pyvider.cty.exceptions import CtyListValidationError, CtyMapValidationError, InvalidTypeError

def test_list_validate_ctyvalue_wrong_type():
    list_type = CtyList(element_type=CtyString())
    map_value = CtyMap(element_type=CtyString()).validate({})
    with pytest.raises(CtyListValidationError):
        list_type.validate(map_value)

def test_map_validate_non_dict_input():
    map_type = CtyMap(element_type=CtyNumber())
    with pytest.raises(CtyMapValidationError):
        map_type.validate([1, 2, 3])

def test_map_constructor_validation():
    with pytest.raises(InvalidTypeError):
        CtyMap(element_type="not a type")
