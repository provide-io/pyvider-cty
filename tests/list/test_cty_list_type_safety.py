#
# tests/list/test_cty_list_type_safety.py
#

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyNumber,
    CtyString,
)


class TestCtyListTypeSafety:
    """Advanced tests for the CtyList type to improve coverage."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())
        self.nested_list = CtyList(element_type=CtyList(element_type=CtyNumber()))

    def test_usable_as_same_type(self) -> None:
        """Test usable_as with same type."""
        # Create another string list
        other_string_list = CtyList(element_type=CtyString())

        # needs to be
        assert self.string_list.usable_as(other_string_list)

    def test_string_representation(self) -> None:
        """Test string representation of CtyList."""
        # Create a list type
        list_type = CtyList(element_type=CtyString())

        # Test string representation
        assert str(list_type) == "list(CtyString)"

    def test_usable_as_different_type(self) -> None:
        """Test usable_as with different type."""
        # Test non-usability
        assert not self.string_list.usable_as(self.number_list)

# 🐍🏗️🧪
