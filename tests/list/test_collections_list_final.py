#
# tests/list/test_collections_list_final.py
#

from typing import Never

import pytest

from pyvider.cty import (
    CtyList,
    CtyNumber,
    CtyString,
)
from pyvider.cty.exceptions import CtyListValidationError


class TestFinalCoverage:
    """Tests specifically targeting the final uncovered lines."""

    def test_line_319_index_out_of_bounds(self) -> None:
        """Test out-of-bounds indexing."""
        # Create a list type
        list_obj = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b")]
        )

        # Access via __getitem__ with invalid index
        with pytest.raises(IndexError) as exc:
            list_obj[10]  # This should hit line 319

        # Check for the standard Python error message
        assert "list index out of range" in str(exc.value)

    def test_append_validation_failure(self) -> None:
        """Test exception handling in append method (lines 165-168)."""
        # Create a number list
        number_list = CtyList(element_type=CtyNumber())

        # Try to append a string (which will fail number validation)
        with pytest.raises(CtyListValidationError) as exc:
            number_list.append("not a number")

        # Verify the correct error message
        assert "Failed to append item" in str(exc.value)

    def test_getitem_special_cases(self) -> None:
        """Test special indexing cases to cover line 319."""
        # Create a list with some elements
        list_obj = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b")]
        )

        # Different ways to access elements to hit all code branches

        # Try normal access
        item = list_obj[0]
        assert isinstance(item, CtyString)
        assert item.value == "a"

        # Try with very large negative index that will wrap around
        # This should execute different code path than the regular index
        # out of bounds we've already tested
        with pytest.raises(IndexError):
            list_obj[-100]

    def test_complex_append_failure(self) -> None:
        """Test append with a more complex validation failure."""
        # Create a special validator that will fail in a specific way
        class FailingStringType(CtyString):
            def validate(self, value) -> Never:
                raise ValueError("Custom validation error")

        # Create a list with our failing validator
        string_list = CtyList(element_type=FailingStringType())

        # Now try to append, which should hit the exception handler
        with pytest.raises(CtyListValidationError) as exc:
            string_list.append("test")

        assert "Failed to append item" in str(exc.value)
        assert "Custom validation error" in str(exc.value)

    def test_getitem_invalid_index_types(self) -> None:
        """Test __getitem__ with invalid index types."""
        list_obj = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b")]
        )

        # Try different index types that might trigger different code paths
        with pytest.raises(TypeError):
            list_obj["not an index"]  # String index

        with pytest.raises(TypeError):
            list_obj[None]  # None as index

    def test_line_319_direct_indexing(self) -> None:
        """Test to directly hit line 319 in __getitem__."""
        # Create a list
        list_obj = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b")]
        )

        # Test normal indexing to confirm functionality
        assert isinstance(list_obj[0], CtyString)
        assert list_obj[0].value == "a"

        # Try accessing with an invalid index
        # This should hit line 319 when the index is out of bounds
        # We need to try different ways to trigger all code paths
        with pytest.raises(IndexError):
            # This alternative syntax might take a different code path
            _ = list_obj.__getitem__(10)

    def test_getitem_alternative_cases(self) -> None:
        """Test slice syntax variations."""
        # Create a list
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

        # Try slicing with step and no end parameter
        sliced = list_obj[::2]  # Should get elements at indices 0, 2, 4

        assert isinstance(sliced, CtyList)
        assert len(sliced.value) == 3
        assert [item.value for item in sliced.value] == ["a", "c", "e"]

    def test_getitem_unusual_indices(self) -> None:
        """Test more unusual indexing scenarios."""
        # Create a list with single element
        list_obj = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a")]
        )

        # Test boundary conditions
        assert list_obj[0].value == "a"  # First element

        with pytest.raises(IndexError):
            list_obj[1]  # Just beyond end

        # Try special slice cases with single element list
        empty_slice = list_obj[1:]  # Should be empty slice
        assert isinstance(empty_slice, CtyList)
        assert len(empty_slice.value) == 0

# 🐍🏗️🧪
