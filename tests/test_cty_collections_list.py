import pytest

from pyvider.exceptions import PyviderError, ValidationError
from pyvider.cty.collections import TFList
from pyvider.cty.primitives import TFNumber, TFString

# --------------------------------
# Test: TFList Validation
# --------------------------------

def test_tflist_validate_success():
    string_list = TFList(element_type=TFString())
    validated = string_list.validate(["apple", "banana", "cherry"])
    assert validated == ["apple", "banana", "cherry"]

def test_tflist_validate_failure():
    string_list = TFList(element_type=TFString())
    with pytest.raises(ValidationError, match="Invalid element at index 1"):
        string_list.validate(["apple", 123, "cherry"])  # Second element is invalid


def test_tflist_validate_nested_lists():
    nested_list = TFList(element_type=TFList(element_type=TFString()))
    validated = nested_list.validate([["one", "two"], ["three"]])
    assert validated == [["one", "two"], ["three"]]

    with pytest.raises(ValidationError, match="Invalid element at index 0"):
        nested_list.validate([["one", 2], ["three"]])


def test_tflist_validate_empty_list():
    string_list = TFList(element_type=TFString())
    validated = string_list.validate([])
    assert validated == []


def test_tflist_validate_none():
    string_list = TFList(element_type=TFString())
    validated = string_list.validate(None)
    assert validated == []


# --------------------------------
# Test: TFList with Invalid Configurations
# --------------------------------

def test_tflist_invalid_element_type():
    with pytest.raises(PyviderError, match="Expected TFType for element_type"):
        TFList(element_type="invalid")  # Non-TFType passed


def test_tflist_invalid_structure():
    list_of_numbers = TFList(element_type=TFNumber())
    with pytest.raises(PyviderError):
        list_of_numbers.validate("not_a_list")  # Entire structure must be list


# --------------------------------
# Test: Nested List with None (Should Fail)
# --------------------------------

def test_tflist_validate_none_in_list():
    string_list = TFList(element_type=TFString())
    with pytest.raises(ValidationError, match="Invalid element at index 0"):
        string_list.validate([None, "value"])


# --------------------------------
# Test: Large List Validation
# --------------------------------

def test_tflist_large_list():
    large_list = TFList(element_type=TFString())
    validated = large_list.validate(["item"] * 1000)
    assert len(validated) == 1000


# --------------------------------
# Test: Dynamic Schema (Nested Lists)
# --------------------------------

def test_tflist_dynamic_schema():
    dynamic_list = TFList(element_type=TFList(TFString()))
    validated = dynamic_list.validate([["one", "two"], ["three"]])
    assert validated == [["one", "two"], ["three"]]
