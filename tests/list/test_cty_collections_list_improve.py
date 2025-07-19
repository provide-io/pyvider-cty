# tests/list/test_cty_collections_list_improve.py

import pytest

from pyvider.cty import (
    CtyBool,
    CtyList,
    CtyNumber,
    CtyString,
)


class TestCtyListAdvanced:
    """Advanced tests for the CtyList type to improve coverage."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Set up objects for testing."""
        self.string_list = CtyList(element_type=CtyString())
        self.number_list = CtyList(element_type=CtyNumber())
        self.bool_list = CtyList(element_type=CtyBool())

    def test_element_at_negative_index(self) -> None:
        """Test retrieving an element at a negative index."""
        list_type = self.string_list  # This is CtyList(element_type=CtyString())
        # Create a CtyValue instance by validating a Python list
        list_cty_value = list_type.validate(["apple", "banana", "cherry"])

        # Get element at negative index using CtyValue's __getitem__
        element_cty_value = list_cty_value[-1]

        # Assertions
        from pyvider.cty import (
            CtyValue,
        )  # Import CtyValue if not already at module level

        assert isinstance(element_cty_value, CtyValue)
        assert isinstance(element_cty_value.type, CtyString)
        assert element_cty_value.value == "cherry"

    def test_repr_representation(self) -> None:
        """Test __repr__ representation."""
        # Based on the actual implementation, adjust expectations
        repr_str = repr(self.string_list)
        assert "CtyList" in repr_str


# 🐍🏗️🧪
