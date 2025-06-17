import pytest

from pyvider.cty import (
    CtyList,
    CtyString,
)
from pyvider.cty.exceptions import CtyListValidationError


class TestCtyListCoverage:
    """Tests specifically targeting uncovered lines in CtyList."""

    @pytest.fixture
    def string_list(self):
        """Create a string list with values for testing."""
        return CtyList(
            element_type=CtyString(),
            value=[
                CtyString(value="a"),
                CtyString(value="b"),
                CtyString(value="c"),
                CtyString(value="d"),
                CtyString(value="e")
            ]
        )

    @pytest.fixture
    def empty_string_list(self):
        """Create an empty string list for testing."""
        return CtyList(element_type=CtyString(), value=[])

    @pytest.mark.asyncio
    async def test_slice_default_end(self, string_list) -> None:
        """Test slice with default end parameter."""
        # This will test line 187: end = len(self.value)
        result = string_list.slice(2)

        # Should get elements from index 2 to end
        assert isinstance(result, CtyList)
        assert len(result.value) == 3
        assert [item.value for item in result.value] == ["c", "d", "e"]

    @pytest.mark.asyncio
    async def test_slice_negative_indices(self, string_list) -> None:
        """Test slice with negative indices."""
        # This tests lines 191 and 193 (converting negative indices)
        result = string_list.slice(-3, -1)

        assert isinstance(result, CtyList)
        assert len(result.value) == 2
        assert [item.value for item in result.value] == ["c", "d"]


    @pytest.mark.asyncio
    async def test_concat_with_invalid_container(self, string_list) -> None:
        """Test concat with invalid container."""
        # This tests lines 228-230
        with pytest.raises(CtyListValidationError) as exc:
            string_list.concat("not a list")

        assert "Expected CtyList" in str(exc.value)


    @pytest.mark.asyncio
    async def test_element_at_out_of_bounds(self) -> None:
        """Test element_at with index out of bounds."""
        # Create a CtyList with CtyString values
        list_obj = CtyList(
            element_type=CtyString(),
            value=[CtyString(value="a"), CtyString(value="b")]
        )

        # This tests the error raised in element_at method
        with pytest.raises(IndexError) as exc:
            list_obj.element_at(list_obj, 5)

        assert "Index out of bounds" in str(exc.value)
