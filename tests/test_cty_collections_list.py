import pytest

from pyvider.cty.exceptions import PyviderError, ValidationError
from pyvider.cty import CtyNumber, CtyString, CtyList

# --------------------------------
# Test: CtyList Validation
# --------------------------------

def test_CtyList_validate_success():
    string_list = CtyList(element_type=CtyString())
    validated = string_list.validate(["apple", "banana", "cherry"])
    assert validated == ["apple", "banana", "cherry"]

def test_CtyList_validate_failure():
    string_list = CtyList(element_type=CtyString())
    with pytest.raises(ValidationError, match="Invalid element at index 1"):
        string_list.validate(["apple", 123, "cherry"])  # Second element is invalid


def test_CtyList_validate_nested_lists():
    nested_list = CtyList(element_type=CtyList(element_type=CtyString()))
    validated = nested_list.validate([["one", "two"], ["three"]])
    assert validated == [["one", "two"], ["three"]]

    with pytest.raises(ValidationError, match="Invalid element at index 0"):
        nested_list.validate([["one", 2], ["three"]])


def test_CtyList_validate_empty_list():
    string_list = CtyList(element_type=CtyString())
    validated = string_list.validate([])
    assert validated == []


def test_CtyList_validate_none():
    string_list = CtyList(element_type=CtyString())
    validated = string_list.validate(None)
    assert validated == []


# --------------------------------
# Test: CtyList with Invalid Configurations
# --------------------------------

def test_CtyList_invalid_element_type():
    with pytest.raises(PyviderError, match="Expected CtyType for element_type"):
        CtyList(element_type="invalid")  # Non-CtyType passed


def test_CtyList_invalid_structure():
    list_of_numbers = CtyList(element_type=CtyNumber())
    with pytest.raises(PyviderError):
        list_of_numbers.validate("not_a_list")  # Entire structure must be list


# --------------------------------
# Test: Nested List with None (Should Fail)
# --------------------------------

def test_CtyList_validate_none_in_list():
    string_list = CtyList(element_type=CtyString())
    with pytest.raises(ValidationError, match="Invalid element at index 0"):
        string_list.validate([None, "value"])


# --------------------------------
# Test: Large List Validation
# --------------------------------

def test_CtyList_large_list():
    large_list = CtyList(element_type=CtyString())
    validated = large_list.validate(["item"] * 1000)
    assert len(validated) == 1000


# --------------------------------
# Test: Dynamic Schema (Nested Lists)
# --------------------------------

def test_CtyList_dynamic_schema():
    dynamic_list = CtyList(element_type=CtyList(CtyString()))
    validated = dynamic_list.validate([["one", "two"], ["three"]])
    assert validated == [["one", "two"], ["three"]]
