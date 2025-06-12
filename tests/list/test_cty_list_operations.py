#
# tests/list/test_cty_list_operations.py
#

import pytest

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty import (
    CtyValue,
    CtyBool,
    CtyList,
    CtyNumber,
    CtyString,
    CtyTuple,
)

class TestCtyListOperations:
    """Tests for CtyList operations with consistent type-based return values."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())

    def test_cty_list_access_methods(self):
        """Test list access methods with direct element access."""
        # Create a CtyList with validated values
        validated = self.string_list.validate([
            "a", "b", "c", "d", "e"
        ])

        # Initialize the list with the validated values
        list_obj = CtyList(
            element_type=CtyString(),
            value=validated.value
        )

        # Test direct indexing - should get a CtyValue
        element = list_obj[2]
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyString)
        assert element.value == "c"

        # Test element_at method
        element = list_obj.element_at(list_obj, 2)
        assert isinstance(element, CtyValue)
        assert isinstance(element.type, CtyString)
        assert element.value == "c"

        # Test slicing with steps
        sliced = list_obj[::2]  # Should get indices 0, 2, 4
        assert isinstance(sliced, CtyList)
        assert len(sliced.value) == 3
        assert [item.value for item in sliced.value] == ["a", "c", "e"]

    def test_cty_list_concat(self):
        """Test concatenation of lists returning a new CtyList."""
        # Create two CtyLists with validated values
        list1_values = self.string_list.validate(["a", "b"])
        list2_values = self.string_list.validate(["c", "d"])
        
        # Create list objects with the validated values
        list1 = CtyList(
            element_type=CtyString(),
            value=list1_values.value
        )
        list2 = CtyList(
            element_type=CtyString(),
            value=list2_values.value
        )

        # Test concat method
        result = list1.concat(list2)
        assert isinstance(result, CtyList)
        
        # Check that elements are CtyValue objects
        assert len(result.value) == 4
        assert all(isinstance(item, CtyValue) for item in result.value)
        assert [item.value for item in result.value] == ["a", "b", "c", "d"]

        # Test that original lists are unchanged
        assert len(list1.value) == 2
        assert [item.value for item in list1.value] == ["a", "b"]
        assert len(list2.value) == 2
        assert [item.value for item in list2.value] == ["c", "d"]

        # Test with incompatible element types
        number_list = CtyList(element_type=CtyNumber(), value=[])
        with pytest.raises(CtyListValidationError):
            list1.concat(number_list)

    def test_cty_list_append(self):
        """Test append operation returning a new CtyList."""
        # Create a list with string values
        validated = self.string_list.validate(["a", "b"])
        list_obj = CtyList(
            element_type=CtyString(),
            value=validated.value
        )
        
        # Append a new item
        new_list = list_obj.append("c")
        
        # Test that we get a new CtyList
        assert isinstance(new_list, CtyList)
        assert new_list is not list_obj
        
        # Test that the new list has the additional item
        assert len(new_list.value) == 3
        assert [item.value for item in new_list.value] == ["a", "b", "c"]
        
        # Test that the original list is unchanged
        assert len(list_obj.value) == 2
        assert [item.value for item in list_obj.value] == ["a", "b"]

    def test_cty_list_contains(self):
        """Test the contains method."""
        # Create a CtyList with string values
        validated = self.string_list.validate(["a", "b", "c"])
        list_obj = CtyList(
            element_type=CtyString(),
            value=validated.value
        )
        
        # Test contains with valid values
        assert list_obj.contains("a") is True
        assert list_obj.contains("d") is False
        
        # Test contains with invalid type (should return False, not raise)
        assert list_obj.contains(123) is False

def test_cty_list_len():
    """Test the __len__ method."""
    # Create a CtyList with CtyString values
    validated = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
    list_obj = CtyList(
        element_type=CtyString(),
        value=validated.value
    )
    assert len(list_obj) == 3

def test_cty_list_getitem():
    """Test the __getitem__ method."""
    # Create a CtyList with CtyString values
    validated = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
    list_obj = CtyList(
        element_type=CtyString(),
        value=validated.value
    )

    # Test indexing - should get CtyValue objects
    assert isinstance(list_obj[0], CtyValue)
    assert list_obj[0].value == "a"
    assert isinstance(list_obj[1], CtyValue)
    assert list_obj[1].value == "b"
    assert isinstance(list_obj[2], CtyValue)
    assert list_obj[2].value == "c"

def test_cty_list_iter():
    """Test the __iter__ method."""
    # Create a CtyList with CtyString values
    validated = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
    list_obj = CtyList(
        element_type=CtyString(),
        value=validated.value
    )

    # Test iteration - should get CtyValue objects
    items = []
    for item in list_obj:
        assert isinstance(item, CtyValue)
        items.append(item.value)

    assert items == ["a", "b", "c"]

def test_cty_list_slice():
    """Test slicing a CtyList."""
    # Create a CtyList with CtyString values
    validated = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d", "e"])
    list_obj = CtyList(
        element_type=CtyString(),
        value=validated.value
    )

    # Test slicing with __getitem__
    sliced = list_obj[1:4]
    # Expect a CtyList
    assert isinstance(sliced, CtyList)
    assert len(sliced.value) == 3
    assert [item.value for item in sliced.value] == ["b", "c", "d"]

    # Test using slice method
    sliced = list_obj.slice(1, 4)
    assert isinstance(sliced, CtyList)
    assert len(sliced.value) == 3
    assert [item.value for item in sliced.value] == ["b", "c", "d"]

def test_cty_list_element_at():
    """Test the element_at method."""
    # Create a CtyList with CtyString values
    validated = CtyList(element_type=CtyString()).validate(["a", "b", "c"])
    list_obj = CtyList(
        element_type=CtyString(),
        value=validated.value
    )

    # Test element_at with CtyList
    element = list_obj.element_at(list_obj, 1)
    assert isinstance(element, CtyValue)
    assert element.value == "b"

    # Test element_at with raw list containing CtyValue objects
    raw_list = list_obj.value
    element = list_obj.element_at(raw_list, 1)
    assert isinstance(element, CtyValue)
    assert element.value == "b"


def test_alternative_slice_syntax():
    """Test slice syntax variations."""
    # Create a list with validated values
    validated = CtyList(element_type=CtyString()).validate(["a", "b", "c", "d", "e"])
    list_obj = CtyList(
        element_type=CtyString(),
        value=validated.value
    )

    # Try slicing with step and no end parameter
    sliced = list_obj[::2]  # Should get elements at indices 0, 2, 4
    assert isinstance(sliced, CtyList)
    assert len(sliced.value) == 3
    assert [item.value for item in sliced.value] == ["a", "c", "e"]

def test_cty_list_append():
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

# 🐍🏗️🧪
