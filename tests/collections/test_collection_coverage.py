import pytest
from decimal import Decimal
from pyvider.cty import (
    CtyString, CtyNumber, CtyBool, CtyList, CtyMap, CtySet, CtyTuple, CtyObject, CtyDynamic,
    CtyValue
)
from pyvider.cty.exceptions import CtyListValidationError, CtyMapValidationError, CtySetValidationError, CtyValidationError, CtyTypeMismatchError

# --- CtyList Validation Error Coverage ---

def test_list_validate_none_input():
    list_type = CtyList(element_type=CtyString())
    with pytest.raises(CtyListValidationError, match="Input to CtyList.validate cannot be None"):
        list_type.validate(None)

def test_list_validate_non_iterable_input():
    list_type = CtyList(element_type=CtyString())
    with pytest.raises(CtyListValidationError, match="Expected list, tuple, or CtyValue list, got int"):
        list_type.validate(123)

def test_list_validate_ctyvalue_wrong_type():
    list_type = CtyList(element_type=CtyString())
    map_value = CtyMap(key_type=CtyString(), value_type=CtyString()).validate({})
    with pytest.raises(CtyListValidationError, match="Input CtyValue is not of a list type, got CtyMap"):
        list_type.validate(map_value)

def test_list_validate_ctyvalue_incompatible_element_type():
    list_type_string = CtyList(element_type=CtyString())
    list_value_number = CtyList(element_type=CtyNumber()).validate([1, 2])
    with pytest.raises(CtyListValidationError, match="Input CtyValue has incompatible list element type: list\\(number\\) vs list\\(string\\)"):
        list_type_string.validate(list_value_number)

def test_list_validate_element_validation_error():
    list_type = CtyList(element_type=CtyNumber())
    with pytest.raises(CtyListValidationError) as excinfo:
        list_type.validate([1, "not-a-number", 3])
    assert "Item 1 ('not-a-number'): Value of type str cannot be converted to a number." in str(excinfo.value)

# --- CtyMap Validation Error Coverage ---

def test_map_validate_non_dict_input():
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    with pytest.raises(CtyMapValidationError, match="Input must be a dictionary, got list"):
        map_type.validate([1, 2, 3])

def test_map_validate_ctyvalue_wrong_type():
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    list_value = CtyList(element_type=CtyString()).validate(["a"])
    with pytest.raises(CtyMapValidationError, match="Input CtyValue has type list, expected compatible map type."):
        map_type.validate(list_value)

def test_map_validate_ctyvalue_incompatible_key_type():
    map_type_str_key = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    map_val_num_key_type = CtyMap(key_type=CtyNumber(), value_type=CtyNumber())
    map_value_num_key = map_val_num_key_type.validate({1:10})

    with pytest.raises(CtyMapValidationError, match="Input CtyValue map type map\\(number\\) is not compatible with target type map\\(string\\)"):
        map_type_str_key.validate(map_value_num_key)

def test_map_validate_ctyvalue_incompatible_value_type():
    map_type_num_val = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    map_value_str_val = CtyMap(key_type=CtyString(), value_type=CtyString()).validate({"key": "value"})
    with pytest.raises(CtyMapValidationError, match="Input CtyValue map type map\\(string\\) is not compatible with target type map\\(number\\)"):
        map_type_num_val.validate(map_value_str_val)

def test_map_validate_key_validation_error():
    map_type = CtyMap(key_type=CtyNumber(), value_type=CtyString()) # Expects numeric keys
    with pytest.raises(CtyMapValidationError) as excinfo:
        map_type.validate({"not-a-number-key": "value"})
    assert "Invalid key-value pair ('not-a-number-key': 'value'): Value of type str cannot be converted to a number." in str(excinfo.value)

def test_map_validate_value_validation_error():
    map_type = CtyMap(key_type=CtyString(), value_type=CtyNumber())
    with pytest.raises(CtyMapValidationError) as excinfo:
        map_type.validate({"key1": 1, "key2": "not-a-number"})
    assert "Invalid key-value pair ('key2': 'not-a-number'): Value of type str cannot be converted to a number." in str(excinfo.value)

def test_map_validate_null_key():
    map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
    with pytest.raises(CtyMapValidationError) as excinfo:
        map_type.validate({None: "value"}) # Raw None key
    assert "Invalid key None: Map keys cannot be null or unknown." in str(excinfo.value)

# --- CtySet Validation Error Coverage ---

def test_set_validate_none_input_direct():
    set_type = CtySet(element_type=CtyString())
    with pytest.raises(CtySetValidationError, match="Expected a Python set/frozenset .* got NoneType"):
         set_type.validate(None)

def test_set_validate_non_iterable_input():
    set_type = CtySet(element_type=CtyString())
    with pytest.raises(CtySetValidationError, match="Expected a Python set/frozenset .* got int"):
        set_type.validate(123)

def test_set_validate_ctyvalue_wrong_type():
    set_type = CtySet(element_type=CtyString())
    map_value = CtyMap(key_type=CtyString(), value_type=CtyString()).validate({})
    with pytest.raises(CtySetValidationError, match="Expected a Python set/frozenset .* got dict"):
        set_type.validate(map_value)

def test_set_validate_ctyvalue_incompatible_element_type():
    set_type_string = CtySet(element_type=CtyString())
    set_value_number = CtySet(element_type=CtyNumber()).validate({1, 2})
    with pytest.raises(CtySetValidationError) as excinfo:
        set_type_string.validate(set_value_number)
    # Error message will be about element validation. Order in set is not guaranteed.
    assert "Value of type Decimal cannot be converted to a string" in str(excinfo.value)


def test_set_validate_element_validation_error():
    set_type = CtySet(element_type=CtyNumber())
    with pytest.raises(CtySetValidationError) as excinfo:
        set_type.validate({1, "not-a-number", 3})
    assert "Value of type str cannot be converted to a number" in str(excinfo.value)

def test_set_validate_unhashable_in_list_input():
    set_type = CtySet(element_type=CtyList(CtyString())) # Set of lists
    with pytest.raises(CtySetValidationError, match="Input list/tuple could not be converted to set"):
        set_type.validate([ ["a"], ["b"], ["a"] ])

def test_set_constructor_invalid_element_type():
    with pytest.raises(CtySetValidationError, match="Expected CtyType for element_type, got str"):
        CtySet(element_type="not-a-ctytype") # type: ignore

# --- Constructor Error Coverage for other collections ---

def test_map_constructor_invalid_key_type():
    with pytest.raises(CtyMapValidationError, match="key_type must be a CtyType instance"):
        CtyMap(key_type="not-cty", value_type=CtyString()) # type: ignore

def test_map_constructor_invalid_value_type():
    with pytest.raises(CtyMapValidationError, match="value_type must be a CtyType instance"):
        CtyMap(key_type=CtyString(), value_type="not-cty") # type: ignore

def test_map_constructor_non_primitive_key_type():
    with pytest.raises(CtyMapValidationError, match="Map key_type must be a primitive type or CtyDynamic"):
        CtyMap(key_type=CtyList(CtyString()), value_type=CtyString())

def test_list_constructor_invalid_element_type():
    with pytest.raises(CtyListValidationError, match="Expected CtyType for element_type, got str"):
        CtyList(element_type="not-a-ctytype") # type: ignore

# --- Method Error Coverage (element_at, get) ---

@pytest.fixture
def cty_list_fixture() -> CtyList:
    return CtyList(element_type=CtyString())

@pytest.fixture
def cty_map_fixture() -> CtyMap:
    return CtyMap(key_type=CtyString(), value_type=CtyNumber())

def test_list_element_at_non_ctyvalue_container(cty_list_fixture):
    with pytest.raises(CtyListValidationError, match="Expected CtyValue\\[CtyList\\], got list"):
        cty_list_fixture.element_at(["a","b"], 0)

def test_list_element_at_wrong_ctyvalue_type_container(cty_list_fixture, cty_map_string_to_number_val):
    with pytest.raises(CtyListValidationError, match="Expected CtyValue with CtyList type, got CtyValue with CtyMap"):
        cty_list_fixture.element_at(cty_map_string_to_number_val, 0)

def test_list_element_at_null_container():
    list_type = CtyList(element_type=CtyString())
    null_list_val = CtyValue.null(list_type)
    with pytest.raises(IndexError, match="Cannot access element at index 0 in a null list"):
        list_type.element_at(null_list_val, 0)

def test_list_element_at_internal_value_not_list():
    list_type = CtyList(element_type=CtyString())
    # Create a CtyValue that claims to be CtyList but wraps a non-list
    # This requires bypassing normal construction if it prevents such states.
    bad_val = CtyValue(vtype=list_type, value="not a list") # This should ideally be caught by CtyValue itself or list_type.validate
    # If validate was called on "not a list" for list_type, it would fail earlier.
    # This test is for element_at assuming such a CtyValue exists.
    with pytest.raises(CtyListValidationError, match="Internal error: CtyValue of CtyList type does not wrap a list/tuple"):
        list_type.element_at(bad_val, 0)

def test_map_get_non_ctyvalue_container(cty_map_fixture):
    with pytest.raises(CtyTypeMismatchError, match="get operation called on non-map CtyValue or non-CtyValue: dict"):
        cty_map_fixture.get({"one":1}, "one")

def test_map_get_wrong_ctyvalue_type_container(cty_map_fixture, cty_list_of_strings_val):
    with pytest.raises(CtyTypeMismatchError, match="get operation called on non-map CtyValue or non-CtyValue"):
        cty_map_fixture.get(cty_list_of_strings_val, "key")

def test_map_get_key_validation_error_in_get(cty_map_fixture, cty_map_string_to_number_val):
    # Map expects string keys. Try to get with an int key.
    with pytest.raises(CtyValidationError, match="Value of type int cannot be converted to a string."): # Error from CtyString().validate(123)
        cty_map_fixture.get(cty_map_string_to_number_val, 123)

def test_map_get_null_key_in_get(cty_map_fixture, cty_map_string_to_number_val):
    # CtyMap.get should handle null key and return default or null value_type
    result = cty_map_fixture.get(cty_map_string_to_number_val, CtyValue.null(CtyString()))
    assert result.is_null
    assert result.type == cty_map_fixture.value_type

def test_map_get_unknown_key_in_get(cty_map_fixture, cty_map_string_to_number_val):
    result = cty_map_fixture.get(cty_map_string_to_number_val, CtyValue.unknown(CtyString()))
    assert result.is_null # Current CtyMap.get behavior for unknown keys
    assert result.type == cty_map_fixture.value_type

def test_map_get_internal_value_not_dict():
    map_type = CtyMap(key_type=CtyString(), value_type=CtyString())
    bad_map_val = CtyValue(vtype=map_type, value="not a dict")
    # CtyMap.get will attempt to use .value which is "not a dict"
    # This should lead to it returning the default (null of value_type)
    result = map_type.get(bad_map_val, "anykey")
    assert result.is_null
    assert result.type == map_type.value_type
