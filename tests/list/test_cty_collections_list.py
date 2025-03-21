
# tests/list/test_cty_collections_list.py

import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyTuple

# --------------------------------
# Test: CtyList Validation
# --------------------------------

def test_ctylist_validate_success():
    string_list = CtyList(element_type=CtyString())
    validated = string_list.validate(["apple", "banana", "cherry"])
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    # Test that the values are correct
    assert validated.value == ["apple", "banana", "cherry"]
    # Test access through the list interface
    assert validated[0] == "apple"
    assert validated[1] == "banana"
    assert validated[2] == "cherry"

def test_ctylist_validate_failure():
    string_list = CtyList(element_type=CtyString())
    with pytest.raises(ValidationError, match="CtyList validation failed:\nItem 1"):
        string_list.validate(["apple", 123, "cherry"])  # Second element is invalid


def test_ctylist_validate_nested_lists():
    nested_list = CtyList(element_type=CtyList(element_type=CtyString()))
    validated = nested_list.validate([["one", "two"], ["three"]])
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    # Test that the values are CtyList objects containing the correct values
    assert isinstance(validated[0], CtyList)
    assert isinstance(validated[1], CtyList)
    assert validated[0].value == ["one", "two"]
    assert validated[1].value == ["three"]

    with pytest.raises(ValidationError):
        nested_list.validate([["one", 2], ["three"]])


def test_ctylist_validate_empty_list():
    string_list = CtyList(element_type=CtyString())
    validated = string_list.validate([])
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    # Test that the value is an empty list
    assert validated.value == []
    # Test that the length is 0
    assert len(validated) == 0


def test_ctylist_validate_none():
    string_list = CtyList(element_type=CtyString())
    validated = string_list.validate(None)
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    # Test that the value is an empty list
    assert validated.value == []
    # Test that the length is 0
    assert len(validated) == 0


# --------------------------------
# Test: CtyList with Invalid Configurations
# --------------------------------

def test_ctylist_invalid_element_type():
    with pytest.raises(ValidationError, match="Expected CtyType for element_type"):
        CtyList(element_type="invalid")  # Non-CtyType passed


def test_ctylist_invalid_structure():
    list_of_numbers = CtyList(element_type=CtyNumber())
    with pytest.raises(ValidationError):
        list_of_numbers.validate("not_a_list")  # Entire structure must be list


# --------------------------------
# Test: Nested List with None (Should Fail)
# --------------------------------

def test_ctylist_validate_none_in_list():
    string_list = CtyList(element_type=CtyString())
    with pytest.raises(ValidationError, match="CtyList validation failed:\nItem 0"):
        string_list.validate([None, "value"])


# --------------------------------
# Test: Large List Validation
# --------------------------------

def test_ctylist_large_list():
    large_list = CtyList(element_type=CtyString())
    data = ["item"] * 1000
    validated = large_list.validate(data)
    # Test that the length is correct
    assert len(validated) == 1000
    # Test that all elements are "item"
    assert all(item == "item" for item in validated)


# --------------------------------
# Test: Dynamic Schema (Nested Lists)
# --------------------------------

def test_ctylist_dynamic_schema():
    dynamic_list = CtyList(element_type=CtyList(element_type=CtyString()))
    validated = dynamic_list.validate([["one", "two"], ["three"]])
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    # Test that the first element is a CtyList with values ["one", "two"]
    assert isinstance(validated[0], CtyList)
    assert validated[0].value == ["one", "two"]
    # Test that the second element is a CtyList with values ["three"]
    assert isinstance(validated[1], CtyList)
    assert validated[1].value == ["three"]


# --------------------------------
# Test: CtyList Methods
# --------------------------------

def test_ctylist_len():
    """Test the __len__ method"""
    list_obj = CtyList(element_type=CtyString(), value=["a", "b", "c"])
    assert len(list_obj) == 3


def test_ctylist_getitem():
    """Test the __getitem__ method"""
    list_obj = CtyList(element_type=CtyString(), value=["a", "b", "c"])
    assert list_obj[0] == "a"
    assert list_obj[1] == "b"
    assert list_obj[2] == "c"


def test_ctylist_iter():
    """Test the __iter__ method"""
    list_obj = CtyList(element_type=CtyString(), value=["a", "b", "c"])
    items = []
    for item in list_obj:
        items.append(item)
    assert items == ["a", "b", "c"]


def test_ctylist_slice():
    """Test slicing a CtyList"""
    list_obj = CtyList(element_type=CtyString(), value=["a", "b", "c", "d", "e"])
    # Test using __getitem__ with slice
    sliced = list_obj[1:4]
    assert isinstance(sliced, CtyList)
    assert sliced.value == ["b", "c", "d"]
    # Test using slice method
    sliced = list_obj.slice(1, 4)
    assert isinstance(sliced, CtyList)
    assert sliced.value == ["b", "c", "d"]


def test_ctylist_element_at():
    """Test the element_at method"""
    list_obj = CtyList(element_type=CtyString(), value=["a", "b", "c"])
    assert list_obj.element_at(list_obj, 1) == "b"
    # Also test with a raw list
    assert list_obj.element_at(["a", "b", "c"], 1) == "b"


def test_ctylist_append():
    """Test the append method"""
    list_obj = CtyList(element_type=CtyString(), value=["a", "b"])
    new_list = list_obj.append("c")
    assert isinstance(new_list, CtyList)
    assert new_list.value == ["a", "b", "c"]
    # Original list should be unchanged
    assert list_obj.value == ["a", "b"]


def test_ctylist_concat():
    """Test the concat method"""
    list1 = CtyList(element_type=CtyString(), value=["a", "b"])
    list2 = CtyList(element_type=CtyString(), value=["c", "d"])
    result = list1.concat(list2)
    assert isinstance(result, CtyList)
    assert result.value == ["a", "b", "c", "d"]
    # Original lists should be unchanged
    assert list1.value == ["a", "b"]
    assert list2.value == ["c", "d"]


def test_ctylist_contains():
    """Test the contains method"""
    list_obj = CtyList(element_type=CtyString(), value=["a", "b", "c"])
    assert list_obj.contains("a") is True
    assert list_obj.contains("d") is False
    # Invalid type should return False, not raise exception
    assert list_obj.contains(123) is False
