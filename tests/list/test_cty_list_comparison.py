#
# tests/list/test_cty_list_comparison.py
#

import pytest

from pyvider.cty import CtyBool, CtyList, CtyNumber, CtyString


class TestCtyListComparison:
    """Advanced tests for the CtyList type to improve coverage."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())

    def test_equality_different_lengths(self) -> None:
        """Test equality with lists of different lengths."""
        # This tests line 327
        list1 = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b")]
        )
        list2 = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b"), CtyString(value="c")]
        )

        # Lists with different lengths should not be equal
        assert list1 != list2

    def test_equality_same_length_different_elements(self) -> None:
        """Test equality with lists of same length but different elements."""
        # This tests lines 331-332
        list1 = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b")]
        )
        list2 = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="c")]  # Different second element
        )

        # Lists with same length but different elements should not be equal
        assert list1 != list2

    def test_equal_same_element_type(self) -> None:
        """Test equality with same element type."""
        # Create another string list
        other_string_list = CtyList(element_type=CtyString())

        # Test equality
        assert self.string_list.equal(other_string_list)

    def test_equal_different_element_type(self) -> None:
        """Test equality with different element type."""
        # Test inequality
        assert not self.string_list.equal(self.number_list)

    def test_equal_non_list_type(self) -> None:
        """Test equality with non-list type."""
        # Create a CtyString
        string_type = CtyString()

        # Test inequality
        assert not self.string_list.equal(string_type)

    def test_list_equality_operator(self) -> None:
        """Test the __eq__ operator."""
        # Create two identical list types
        list1 = CtyList(element_type=CtyString())
        list2 = CtyList(element_type=CtyString())

        # Test equality
        assert list1 == list2

    def test_list_inequality_operator(self) -> None:
        """Test inequality with different element types."""
        # Test inequality
        assert self.string_list != self.number_list

# 🐍🏗️🧪
