import pytest

from pyvider.cty.exceptions import CtyListValidationError
from pyvider.cty import (
    CtyValue,
    CtyList,
    CtyNumber,
    CtyString,
)

from pyvider.cty import CtyString, CtyNumber, CtyList

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

    # Tests for slice method

    def test_slice_default_end(self, string_list):
        """Test slice with default end parameter."""
        # This will test line 187: end = len(self.value)
        result = string_list.slice(2)

        # Should get elements from index 2 to end
        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert len(result.value) == 3
        assert [item.value for item in result.value] == ["c", "d", "e"]

    def test_slice_negative_indices(self, string_list):
        """Test slice with negative indices."""
        # This tests lines 191 and 193 (converting negative indices)
        result = string_list.slice(-3, -1)

        assert isinstance(result, CtyValue)
        assert isinstance(result.type, CtyList)
        assert len(result.value) == 2
        assert [item.value for item in result.value] == ["c", "d"]

    def test_slice_start_out_of_bounds_negative(self, string_list):
        """Test slice with start index too negative."""
        # This tests lines 197-199
        with pytest.raises(IndexError) as exc:
            string_list.slice(-10, 3)

        assert "Start index" in str(exc.value)
        assert "out of bounds" in str(exc.value)

    def test_slice_start_out_of_bounds_positive(self, string_list):
        """Test slice with start index too large."""
        # This tests lines 197-199 again but with positive index
        with pytest.raises(IndexError) as exc:
            string_list.slice(10, 12)

        assert "Start index" in str(exc.value)
        assert "out of bounds" in str(exc.value)

    def test_slice_end_out_of_bounds(self, string_list):
        """Test slice with end index out of bounds."""
        # This tests lines 202-204
        with pytest.raises(IndexError) as exc:
            string_list.slice(2, 10)

        assert "End index" in str(exc.value)
        assert "out of bounds" in str(exc.value)

    def test_slice_end_less_than_start(self, string_list):
        """Test slice with end index less than start index."""
        # This also tests lines 202-204
        with pytest.raises(IndexError) as exc:
            string_list.slice(3, 2)

        assert "End index" in str(exc.value)
        assert "out of bounds" in str(exc.value)

    # Tests for concat method

    def test_concat_with_invalid_container(self, string_list):
        """Test concat with invalid container."""
        # This tests lines 228-230
        with pytest.raises(CtyListValidationError) as exc:
            string_list.concat("not a list")

        assert "Expected CtyList" in str(exc.value)


    def test_element_at_out_of_bounds(self):
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
