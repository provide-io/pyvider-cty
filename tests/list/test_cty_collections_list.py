# tests/list/test_cty_collections_list.py

import pytest

from pyvider.cty.exceptions import ValidationError
from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyTuple

# --------------------------------
# Test: CtyList Validation
# --------------------------------

def test_ctylist_validate_success():
    """Test successful validation of a simple string list."""
    string_list = CtyList(element_type=CtyString())
    validated = string_list.validate(["apple", "banana", "cherry"])
    
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    
    # Test that the values are CtyString objects
    assert len(validated.value) == 3
    for item in validated.value:
        assert isinstance(item, CtyString)
    
    # Test access through indexing - should get CtyString objects
    assert isinstance(validated[0], CtyString)
    assert validated[0].value == "apple"
    assert isinstance(validated[1], CtyString)
    assert validated[1].value == "banana"
    assert isinstance(validated[2], CtyString)
    assert validated[2].value == "cherry"


def test_ctylist_validate_failure():
    """Test validation failure with mixed types."""
    string_list = CtyList(element_type=CtyString())
    
    # Second element is a number, not a string
    with pytest.raises(ValidationError, match="CtyList validation failed:\nItem 1:"):
        string_list.validate(["apple", 123, "cherry"])


def test_ctylist_validate_nested_lists():
    """Test validation of nested lists."""
    # Create a list of lists of strings
    nested_list = CtyList(element_type=CtyList(element_type=CtyString()))
    validated = nested_list.validate([["one", "two"], ["three"]])
    
    # Test that we get back a CtyList of CtyLists
    assert isinstance(validated, CtyList)
    assert len(validated.value) == 2
    
    # Test that the inner lists are CtyLists
    assert isinstance(validated[0], CtyList)
    assert isinstance(validated[1], CtyList)
    
    # Test that the inner list elements are CtyString objects
    assert len(validated[0].value) == 2
    assert isinstance(validated[0][0], CtyString)
    assert validated[0][0].value == "one"
    assert isinstance(validated[0][1], CtyString)
    assert validated[0][1].value == "two"
    
    assert len(validated[1].value) == 1
    assert isinstance(validated[1][0], CtyString)
    assert validated[1][0].value == "three"
    
    # Test nested validation failure
    with pytest.raises(ValidationError):
        nested_list.validate([["one", 2], ["three"]])


def test_ctylist_validate_empty_list():
    """Test validation of an empty list."""
    string_list = CtyList(element_type=CtyString())
    validated = string_list.validate([])
    
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    
    # Test that the value is an empty list
    assert validated.value == []
    
    # Test that the length is 0
    assert len(validated) == 0


def test_ctylist_validate_none():
    """Test validation of None, which should raise an error."""
    string_list = CtyList(element_type=CtyString())
    
    # None should raise an error, not return an empty list
    with pytest.raises(ValidationError, match="Cannot validate None as a list"):
        string_list.validate(None)


# --------------------------------
# Test: CtyList with Invalid Configurations
# --------------------------------

def test_ctylist_invalid_element_type():
    """Test constructor with invalid element_type."""
    with pytest.raises(ValidationError, match="Expected CtyType for element_type"):
        CtyList(element_type="invalid")  # Non-CtyType passed


def test_ctylist_invalid_structure():
    """Test validation with non-list structure."""
    list_of_numbers = CtyList(element_type=CtyNumber())
    with pytest.raises(ValidationError, match="Expected list or tuple"):
        list_of_numbers.validate("not_a_list")  # String is not a valid list


# --------------------------------
# Test: Nested List with None (Should Fail)
# --------------------------------

def test_ctylist_validate_none_in_list():
    """Test validation with None element in list."""
    string_list = CtyList(element_type=CtyString())
    
    # None element should cause validation failure
    with pytest.raises(ValidationError, match="CtyList validation failed:\nItem 0:"):
        string_list.validate([None, "value"])


# --------------------------------
# Test: Large List Validation
# --------------------------------

def test_ctylist_large_list():
    """Test validation of a large list."""
    large_list = CtyList(element_type=CtyString())
    data = ["item"] * 1000
    validated = large_list.validate(data)
    
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    
    # Test that the length is correct
    assert len(validated) == 1000
    
    # Test that all elements are CtyString objects with value "item"
    for item in validated.value:
        assert isinstance(item, CtyString)
        assert item.value == "item"


# --------------------------------
# Test: Dynamic Schema (Nested Lists)
# --------------------------------

def test_ctylist_dynamic_schema():
    """Test validation with dynamically nested structure."""
    dynamic_list = CtyList(element_type=CtyList(element_type=CtyString()))
    validated = dynamic_list.validate([["one", "two"], ["three"]])
    
    # Test that we get back a CtyList
    assert isinstance(validated, CtyList)
    
    # Test that the first element is a CtyList with CtyString values
    assert isinstance(validated[0], CtyList)
    assert len(validated[0].value) == 2
    assert isinstance(validated[0][0], CtyString)
    assert validated[0][0].value == "one"
    assert isinstance(validated[0][1], CtyString)
    assert validated[0][1].value == "two"
    
    # Test that the second element is a CtyList with a CtyString value
    assert isinstance(validated[1], CtyList)
    assert len(validated[1].value) == 1
    assert isinstance(validated[1][0], CtyString)
    assert validated[1][0].value == "three"


# --------------------------------
# Test: CtyList Methods
# --------------------------------

def test_ctylist_len():
    """Test the __len__ method."""
    # Create a CtyList with CtyString values
    list_obj = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="a"), CtyString(value="b"), CtyString(value="c")]
    )
    assert len(list_obj) == 3


def test_ctylist_getitem():
    """Test the __getitem__ method."""
    # Create a CtyList with CtyString values
    list_obj = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="a"), CtyString(value="b"), CtyString(value="c")]
    )
    
    # Test indexing - should get CtyString objects
    assert isinstance(list_obj[0], CtyString)
    assert list_obj[0].value == "a"
    assert isinstance(list_obj[1], CtyString)
    assert list_obj[1].value == "b"
    assert isinstance(list_obj[2], CtyString)
    assert list_obj[2].value == "c"


def test_ctylist_iter():
    """Test the __iter__ method."""
    # Create a CtyList with CtyString values
    list_obj = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="a"), CtyString(value="b"), CtyString(value="c")]
    )
    
    # Test iteration - should get CtyString objects
    items = []
    for item in list_obj:
        assert isinstance(item, CtyString)
        items.append(item.value)
    
    assert items == ["a", "b", "c"]


def test_ctylist_slice():
    """Test slicing a CtyList."""
    # Create a CtyList with CtyString values
    list_obj = CtyList(
        element_type=CtyString(),
        value=[
            CtyString(value="a"),
            CtyString(value="b"),
            CtyString(value="c"),
            CtyString(value="d"),
            CtyString(value="e")
        ]
    )
    
    # Test using __getitem__ with slice
    sliced = list_obj[1:4]
    assert isinstance(sliced, CtyList)
    assert len(sliced.value) == 3
    assert sliced[0].value == "b"
    assert sliced[1].value == "c"
    assert sliced[2].value == "d"
    
    # Test using slice method
    sliced = list_obj.slice(1, 4)
    assert isinstance(sliced, CtyList)
    assert len(sliced.value) == 3
    assert sliced[0].value == "b"
    assert sliced[1].value == "c"
    assert sliced[2].value == "d"


def test_ctylist_element_at():
    """Test the element_at method."""
    # Create a CtyList with CtyString values
    list_obj = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="a"), CtyString(value="b"), CtyString(value="c")]
    )
    
    # Test element_at with CtyList
    element = list_obj.element_at(list_obj, 1)
    assert isinstance(element, CtyString)
    assert element.value == "b"
    
    # Test element_at with raw list
    raw_list = [CtyString(value="a"), CtyString(value="b"), CtyString(value="c")]
    element = list_obj.element_at(raw_list, 1)
    assert isinstance(element, CtyString)
    assert element.value == "b"


def test_ctylist_append():
    """Test the append method."""
    # Create a CtyList with CtyString values
    list_obj = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="a"), CtyString(value="b")]
    )
    
    # Append a new item
    new_list = list_obj.append("c")
    
    # Test that we get back a new CtyList
    assert isinstance(new_list, CtyList)
    assert new_list is not list_obj
    
    # Test that the new list has the additional item
    assert len(new_list.value) == 3
    assert new_list[0].value == "a"
    assert new_list[1].value == "b"
    assert new_list[2].value == "c"
    
    # Test that the original list is unchanged
    assert len(list_obj.value) == 2
    assert list_obj[0].value == "a"
    assert list_obj[1].value == "b"


def test_ctylist_concat():
    """Test the concat method."""
    # Create two CtyLists with CtyString values
    list1 = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="a"), CtyString(value="b")]
    )
    list2 = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="c"), CtyString(value="d")]
    )
    
    # Concatenate the lists
    result = list1.concat(list2)
    
    # Test that we get back a new CtyList
    assert isinstance(result, CtyList)
    assert result is not list1
    assert result is not list2
    
    # Test that the result has all items
    assert len(result.value) == 4
    assert result[0].value == "a"
    assert result[1].value == "b"
    assert result[2].value == "c"
    assert result[3].value == "d"
    
    # Test that the original lists are unchanged
    assert len(list1.value) == 2
    assert list1[0].value == "a"
    assert list1[1].value == "b"
    
    assert len(list2.value) == 2
    assert list2[0].value == "c"
    assert list2[1].value == "d"
    
    # Test with incompatible element types
    number_list = CtyList(element_type=CtyNumber(), value=[])
    with pytest.raises(ValidationError):
        list1.concat(number_list)


def test_ctylist_contains():
    """Test the contains method."""
    # Create a CtyList with CtyString values
    list_obj = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="a"), CtyString(value="b"), CtyString(value="c")]
    )
    
    # Test contains with valid values
    assert list_obj.contains("a") is True
    assert list_obj.contains("d") is False
    
    # Test contains with invalid type (should return False, not raise exception)
    assert list_obj.contains(123) is False
