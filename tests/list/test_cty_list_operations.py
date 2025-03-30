#
# tests/list/test_cty_list_operations.py
#

import pytest

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString, CtyTuple


class TestCtyListOperations:
    """Advanced tests for the CtyList type to improve coverage."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())

    def test_list_access_methods(self):
        """Test advanced list access methods."""
        # Create a CtyList with CtyString values
        self.string_list = CtyList(
            element_type=CtyString(),
            value=[
                CtyString(value="a"),
                CtyString(value="b"),
                CtyString(value="c"),
                CtyString(value="d"),
                CtyString(value="e")
            ]
        )

        # Test slicing
        sliced = self.string_list[1:4]
        assert isinstance(sliced, CtyList)
        assert len(sliced.value) == 3
        assert all(isinstance(item, CtyString) for item in sliced.value)
        assert [item.value for item in sliced.value] == ["b", "c", "d"]

        # Test slice method
        sliced = self.string_list.slice(1, 4)
        assert isinstance(sliced, CtyList)
        assert len(sliced.value) == 3
        assert all(isinstance(item, CtyString) for item in sliced.value)
        assert [item.value for item in sliced.value] == ["b", "c", "d"]

        # Test negative slicing
        sliced = self.string_list[-3:]
        assert isinstance(sliced, CtyList)
        assert len(sliced.value) == 3
        assert all(isinstance(item, CtyString) for item in sliced.value)
        assert [item.value for item in sliced.value] == ["c", "d", "e"]

    def test_list_concat_method(self):
        """Test concatenation of lists."""
        # Create two CtyLists with CtyString values
        list1 = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b")]
        )
        list2 = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="c"), CtyString(value="d")]
        )

        # Test concat method
        result = list1.concat(list2)
        assert isinstance(result, CtyList)
        assert len(result.value) == 4
        assert all(isinstance(item, CtyString) for item in result.value)
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

    def test_list_contains_method(self):
        """Test the contains method."""
        # Create a CtyList with CtyString values
        self.string_list = CtyList(
            element_type=CtyString(),
            value=[
                CtyString(value="a"),
                CtyString(value="b"),
                CtyString(value="c")
            ]
        )

        # Test contains with valid values
        assert self.string_list.contains("a") is True
        assert self.string_list.contains("d") is False

        # Test contains with invalid type (should return False, not raise)
        assert self.string_list.contains(123) is False

def test_cty_list_len():
    """Test the __len__ method."""
    # Create a CtyList with CtyString values
    list_obj = CtyList(
        element_type=CtyString(),
        value=[CtyString(value="a"), CtyString(value="b"), CtyString(value="c")]
    )
    assert len(list_obj) == 3

def test_cty_list_getitem():
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

def test_cty_list_iter():
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

def test_cty_list_slice():
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

def test_cty_list_element_at():
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

def test_cty_list_concat():
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
    with pytest.raises(CtyListValidationError):
        list1.concat(number_list)

def test_cty_list_contains():
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

# 🐍🏗️🧪
