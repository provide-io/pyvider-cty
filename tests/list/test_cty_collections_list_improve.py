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
        # Create a CtyList with CtyString values
        validated = CtyList(
            element_type=CtyString(),
            value=[
                CtyString(value="apple"),
                CtyString(value="banana"),
                CtyString(value="cherry"),
            ],
        )

        # Get element at negative index
        element = self.string_list.element_at(validated, -1)

        # Assertions
        assert isinstance(element, CtyString)
        assert element.value == "cherry"

    def test_repr_representation(self) -> None:
        """Test __repr__ representation."""
        # Based on the actual implementation, adjust expectations
        repr_str = repr(self.string_list)
        assert "CtyList" in repr_str


# 🐍🏗️🧪
